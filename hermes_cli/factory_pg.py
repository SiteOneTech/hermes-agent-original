"""PostgreSQL-backed Factory progress API for Agent Core DB.

This is the canonical runtime backend for the SitioUno Software Factory. Do not
route production Factory work to SQLite.
"""
from __future__ import annotations

import posixpath
import re
import subprocess
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

from hermes_cli import agent_core_sql as sql
from hermes_cli import factory_contracts
from hermes_cli.factory_catalog import DEFAULT_LANES, FACTORY_AGENTS, VALID_METHODS, slugify

G1_BLOCKING_DOCUMENTS = (
    "FACTORY_INTAKE.md",
    "REQUIREMENTS_ANALYSIS.md",
    "PATTERN_ANALYSIS.md",
    "ASSUMPTIONS_AND_OPEN_QUESTIONS.md",
    "PRD.md",
    "ADRS.md",
    "METHODOLOGY_PLAN.md",
    "TECHNICAL_BLUEPRINT.md",
    "SPRINT_PLAN.md",
    "TASK_GRAPH.md",
    "TRACKER.md",
    "DOCUMENTATION_INDEX.md",
    "QA_GATES.md",
    "SECURITY_GATES.md",
)
LIFECYCLE_DOCUMENTS = (
    "QA_REPORT.md",
    "SECURITY_REVIEW.md",
    "QUALITY_REVIEW.md",
    "DELIVERY_REPORT.md",
    "CHANGELOG.md",
    "CHANGE_RECORDS.md",
    "RETROSPECTIVE.md",
)
PM_PROJECTION_DOCUMENTS = (
    "NOTION_UPDATE.md",
)
FACTORY_REQUIRED_DOCS = G1_BLOCKING_DOCUMENTS
FACTORY_DOCUMENT_DEFINITIONS = (
    *((name, "g1_required") for name in G1_BLOCKING_DOCUMENTS),
    *((name, "lifecycle") for name in LIFECYCLE_DOCUMENTS),
    *((name, "pm_projection") for name in PM_PROJECTION_DOCUMENTS),
)
CRITICAL_RISK_LEVELS = {"critical", "high"}
RECONCILIATION_TASK_SPECS: dict[str, dict[str, Any]] = {
    "missing_repository_strategy": {
        "title": "G0 — Repository Strategy Gate: classify project repo/worktree path",
        "phase": "planning",
        "owner": "factory-orchestrator",
        "reviewer": "architecture-reviewer",
        "engine": "zeus",
        "priority": 5,
        "acceptance": [
            "Factory DB project metadata contains repo_strategy with repo_scope, work_intent, primary repo, branch_prefix, and per-deliverable worktree policy.",
            "If Jean says this is Zeus functionality, the project uses a branch/worktree in SiteOneTech/hermes-agent-original.",
            "If Jean says this is a new project, the strategy explicitly authorizes or records the new product repo.",
            "If the work modifies an existing project, the strategy points to that existing repo and opens branches there instead of starting from zero.",
        ],
    },
    "missing_notion_project": {
        "title": "R0 — Reconciliation: create or link Factory Notion PM tracker",
        "phase": "documentation",
        "owner": "factory-reporter",
        "reviewer": "factory-orchestrator",
        "engine": "zeus",
        "priority": 10,
        "acceptance": [
            "Project-specific Notion PM page exists from the Factory template and links to canonical repo documentation.",
            "Factory DB project metadata includes notion_tracker_page_id or notion_tracker_url for the human PM projection.",
            "Notion remains human reporting only; Factory DB + repo Markdown docs stay the agents' source of truth.",
            "Every increment closure is reflected post-action in the Notion page before the project is considered sequentially current.",
        ],
    },
    "notion_pm_projection_warning": {
        "title": "PM — Legacy projection warning: reconcile to required Factory Notion reporting surface",
        "phase": "reporting",
        "owner": "factory-reporter",
        "reviewer": "factory-orchestrator",
        "engine": "zeus",
        "priority": 900,
        "acceptance": [
            "Legacy optional Notion warning is migrated into the required missing_notion_project reconciliation path.",
            "Factory DB and repo artifacts remain the canonical source of truth.",
            "Notion is mandatory human PM projection, not an agent source of truth.",
        ],
    },
    "missing_project_artifact_dir": {
        "title": "R1 — Reconciliation: restore project-local Factory artifact directory",
        "phase": "documentation",
        "owner": "factory-reporter",
        "reviewer": "factory-orchestrator",
        "engine": "zeus",
        "priority": 20,
        "acceptance": [
            "Project-local artifact directory exists under the project repo and matches project metadata.",
            "Directory ownership and source-of-truth notes are recorded in DOCUMENTATION_INDEX.md or equivalent.",
        ],
    },
    "missing_required_docs": {
        "title": "R2 — Reconciliation: complete required Factory methodology documentation",
        "phase": "documentation",
        "owner": "factory-reporter",
        "reviewer": "factory-orchestrator",
        "engine": "zeus",
        "priority": 30,
        "acceptance": [
            "Required project-local Factory docs exist, unless Jean explicitly authorized a document exception for this project.",
            "PRD, ADRs, sprint plan, task graph, QA/security gates, tracker, and delivery report are reconciled against Factory DB.",
        ],
    },
    "docs_not_indexed": {
        "title": "R2b — Reconciliation: update DOCUMENTATION_INDEX.md",
        "phase": "documentation",
        "owner": "factory-reporter",
        "reviewer": "factory-orchestrator",
        "engine": "zeus",
        "priority": 35,
        "acceptance": [
            "DOCUMENTATION_INDEX.md lists every required project-local Factory artifact path.",
            "The documentation index is generated from real artifact files, not only filename guesses.",
            "Builder context points at DOCUMENTATION_INDEX.md before implementation starts.",
        ],
    },
    "uncommitted_project_artifacts": {
        "title": "R2c — Reconciliation: commit project-local Factory artifacts",
        "phase": "documentation",
        "owner": "factory-reporter",
        "reviewer": "factory-orchestrator",
        "engine": "zeus",
        "priority": 37,
        "acceptance": [
            "Project-local Factory artifacts have a git commit checkpoint, unless Jean explicitly authorized a project-specific exception.",
            "Factory DB metadata or gate evidence records the commit SHA used as the source-of-truth checkpoint.",
            "Untracked or modified methodology docs are not treated as completed delivery evidence.",
        ],
    },
    "missing_task_graph": {
        "title": "R3 — Reconciliation: rebuild canonical Factory task graph",
        "phase": "planning",
        "owner": "implementation-planner",
        "reviewer": "factory-orchestrator",
        "engine": "zeus",
        "priority": 40,
        "acceptance": [
            "Factory DB contains pending implementation/QA/security/delivery tasks that cover the remaining objective.",
            "Task graph is derived from project artifacts and deliverable evidence, not from UI state alone.",
            "Each generated task has owner, reviewer, phase, acceptance criteria, and evidence requirements.",
        ],
    },
    "missing_mandatory_factory_phases": {
        "title": "R3b — Reconciliation: enforce canonical Factory phase contract",
        "phase": "planning",
        "owner": "implementation-planner",
        "reviewer": "factory-orchestrator",
        "engine": "zeus",
        "priority": 45,
        "acceptance": [
            "Runnable/UI deliverables have explicit planning, implementation, independent review, QA, sandbox deploy, post-sandbox verification, and delivery reporting tasks.",
            "UI deliverables include a qa-verifier task requiring Playwright or equivalent browser evidence with desktop/mobile screenshots and console checks.",
            "Sandbox deploy tasks target Zeus-authorized sandbox surfaces, not production, unless Jean explicitly authorized production scope.",
        ],
    },
    "pending_effective_gates": {
        "title": "R4 — Reconciliation: resolve stale or pending effective Factory gates",
        "phase": "review",
        "owner": "factory-orchestrator",
        "reviewer": "quality-reviewer",
        "engine": "zeus",
        "priority": 50,
        "acceptance": [
            "Every effective pending gate is either passed, failed with rework, or waived with a recorded reason.",
            "Old superseded gate rows do not block the current project status.",
        ],
    },
    "deliverable_unverified": {
        "title": "R5 — Reconciliation: verify deliverable completion and close delivery gate",
        "phase": "delivery",
        "owner": "qa-verifier",
        "reviewer": "factory-orchestrator",
        "engine": "zeus",
        "priority": 60,
        "acceptance": [
            "Deliverable evidence is checked against PRD, task graph, tests/builds, and local artifacts.",
            "Delivery gate is recorded as passed, failed with rework, or waived with a human/admin reason.",
            "Project is not marked completed from prose alone.",
        ],
    },
}
TERMINAL_TASK_STATUSES = factory_contracts.TERMINAL_TASK_STATUSES
IN_FLIGHT_TASK_STATUSES = factory_contracts.IN_FLIGHT_TASK_STATUSES
ACTIVE_TASK_STATUSES = factory_contracts.ACTIVE_TASK_STATUSES
DISPATCHABLE_PROJECT_STATUSES = factory_contracts.DISPATCHABLE_PROJECT_STATUSES
TERMINAL_GATE_STATUSES = factory_contracts.TERMINAL_GATE_STATUSES
BLOCKER_ACTION_CATEGORIES = {"auto_resolvable", "technical_rework", "human_question_required", "stale_orphan_state"}
DELIVERY_HOLD_STATUS = factory_contracts.ProjectStatus.DELIVERY_HOLD.value
MANUAL_ATTENTION_STATUS = factory_contracts.ProjectStatus.MANUAL_ATTENTION.value
CONDITION_HOLD_STATUSES = {DELIVERY_HOLD_STATUS, "hold", "on_hold"}
TERMINAL_PROJECT_STATUSES = {
    factory_contracts.ProjectStatus.COMPLETED.value,
    factory_contracts.ProjectStatus.ACCEPTED.value,
    factory_contracts.ProjectStatus.CANCELLED.value,
    factory_contracts.ProjectStatus.SUPERSEDED.value,
    "closed",
}
RESUME_RUNNABLE_TASK_STATUSES = factory_contracts.RUNNABLE_TASK_STATUSES | {"ready", "todo"}
SUPERVISOR_TECHNICAL_REWORK_MAX_RETRIES = 2
MANUAL_TAKEOVER_DEFAULT_TTL_MINUTES = 180
MANUAL_TAKEOVER_MAX_TTL_MINUTES = 24 * 60
BLOCKED_ALERT_DEFAULT_MINUTES = 60
CLAIMED_NULL_ALERT_ROUNDS = 3
_BLOCKER_TECHNICAL_KEYWORDS = (
    "error", "exception", "traceback", "crash", "timeout", "fail", "failed", "failing", "import error",
    "syntax error", "typeerror", "attributeerror", "test failed", "pytest", "bug", "regression", "rework",
)
_BLOCKER_HUMAN_KEYWORDS = (
    "human decision", "decisión humana", "jean debe", "jean needs", "owner decision", "business decision",
    "legal approval", "customer approval", "api key", "token", "password", "credential", "secret", "2fa", "mfa",
    "access denied", "permission denied", "403", "401", "billing", "payment method",
)
_BLOCKER_AUTO_KEYWORDS = (
    "run pytest", "run tests", "correr pytest", "correr tests", "aprobación para correr", "approval to run",
    "implementación o cierre administrativo", "administrative closure", "gate passed", "already passed",
)
_SCHEMA_READY = False


def _user() -> str:
    return sql.runtime_env().get("FACTORY_DB_RUNTIME_USER", "factory_runtime")


def _admin_user() -> str:
    return sql.runtime_env().get("AGENT_DB_ADMIN_USER", "agent_admin")


def _q(v: Any) -> str:
    return sql.quote_literal(v)


def _j(v: Any) -> str:
    return sql.quote_jsonb(v)


def _normalize(row: dict[str, Any]) -> dict[str, Any]:
    data = dict(row)
    metadata = data.get("metadata")
    if metadata is None:
        data["metadata"] = {}
    if "owner_profile" in data and "owner_agent_id" not in data:
        data["owner_agent_id"] = data.get("owner_profile")
    if "reviewer_profile" in data and "reviewer_agent_id" not in data:
        data["reviewer_agent_id"] = data.get("reviewer_profile")
    if "timestamp" in data and "created_at" not in data:
        data["created_at"] = data.get("timestamp")
    if "profile_name" in data and not data.get("display_name"):
        data["display_name"] = data.get("profile_name")
    if data.get("status") == "active" and "active" not in data:
        data["active"] = 1
    return data


def _normalize_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [_normalize(row) for row in rows]


def available() -> bool:
    if not sql.enabled():
        return False
    try:
        sql.psql("SELECT 1;", user=_user())
        return True
    except Exception:
        return False


def ensure_runtime_schema() -> None:
    """Ensure orchestration runtime tables/columns exist.

    Migrations normally create these objects. This guard keeps the autonomous
    cron path safe after deploy/restart when a runtime DB is slightly behind.
    """

    global _SCHEMA_READY
    if _SCHEMA_READY:
        return
    ddl = Path(__file__).resolve().parents[1] / "db" / "modules" / "factory" / "000003_orchestration_runtime.sql"
    if ddl.exists():
        sql.psql(ddl.read_text(encoding="utf-8"), user=_admin_user())
    _SCHEMA_READY = True


def seed_agents() -> None:
    ensure_runtime_schema()
    values = []
    for agent_id, display_name, role, engine, toolsets, skills, greenlights in FACTORY_AGENTS:
        values.append(
            f"({_q(agent_id)}, {_q(agent_id)}, {_q(display_name)}, {_q(role)}, {_q(engine)}, {_j({'toolsets': toolsets, 'skills': skills, 'greenlight_required': greenlights})})"
        )
    active_ids = ", ".join(_q(agent[0]) for agent in FACTORY_AGENTS)
    sql.psql(
        """
        INSERT INTO factory.agents (agent_id, profile_name, display_name, role, preferred_engine, metadata)
        VALUES """ + ",\n".join(values) + """
        ON CONFLICT (agent_id) DO UPDATE SET
          profile_name = EXCLUDED.profile_name,
          display_name = EXCLUDED.display_name,
          role = EXCLUDED.role,
          preferred_engine = EXCLUDED.preferred_engine,
          metadata = EXCLUDED.metadata,
          status = 'active',
          updated_at = now();
        UPDATE factory.agents
        SET status = 'retired', updated_at = now()
        WHERE agent_id IN ('olga-openhands')
          AND agent_id NOT IN (""" + active_ids + """)
          AND status = 'active';
        """,
        user=_user(),
    )


def list_agents() -> list[dict[str, Any]]:
    seed_agents()
    return _normalize_rows(
        sql.rows(
            "SELECT agent_id, profile_name, display_name, role, status, preferred_engine, metadata, created_at, updated_at FROM factory.agents WHERE status = 'active' ORDER BY agent_id",
            user=_user(),
        )
    )


def create_project(name: str, *, project_id: Optional[str] = None, repo_path: Optional[str] = None, repo_remote: Optional[str] = None, base_branch: Optional[str] = None, human_owner: Optional[str] = None, summary: Optional[str] = None, risk_level: str = "medium", autonomy_level: int = 3, methodology: str = "hybrid", create_default_lanes: bool = True, repo_scope: Optional[str] = None, work_intent: Optional[str] = None, metadata: Optional[dict[str, Any]] = None, **_: Any) -> dict[str, Any]:
    seed_agents()
    pid = project_id or slugify(name)
    meta = {"source_of_truth": "agent_core_postgres", "artifact_dir": f"factory/projects/{pid}", **(metadata or {})}
    strategy = factory_contracts.build_repository_strategy(
        project_id=pid,
        project_name=name,
        repo_scope=repo_scope,
        work_intent=work_intent,
        repo_path=repo_path,
        repo_remote=repo_remote,
        base_branch=base_branch,
        metadata=meta,
    )
    meta["repo_strategy"] = strategy
    meta["repo_scope"] = strategy.get("repo_scope")
    meta["work_intent"] = strategy.get("work_intent")
    repo_path = repo_path or strategy.get("primary_repo_path") or None
    repo_remote = repo_remote or strategy.get("primary_repo_remote") or None
    base_branch = base_branch or strategy.get("base_branch") or None
    sql.psql(f"""
        INSERT INTO factory.projects (project_id, name, repo_path, repo_remote, base_branch, status, autonomy_level, methodology, risk_level, human_owner, summary, metadata, started_at, updated_at)
        VALUES ({_q(pid)}, {_q(name)}, {_q(repo_path)}, {_q(repo_remote)}, {_q(base_branch)}, 'intake', {int(autonomy_level)}, {_q(methodology)}, {_q(risk_level)}, {_q(human_owner)}, {_q(summary)}, {_j(meta)}, now(), now())
        ON CONFLICT (project_id) DO UPDATE SET
          name=EXCLUDED.name, repo_path=COALESCE(EXCLUDED.repo_path, factory.projects.repo_path), repo_remote=COALESCE(EXCLUDED.repo_remote, factory.projects.repo_remote), base_branch=COALESCE(EXCLUDED.base_branch, factory.projects.base_branch),
          autonomy_level=EXCLUDED.autonomy_level, methodology=EXCLUDED.methodology, risk_level=EXCLUDED.risk_level,
          human_owner=EXCLUDED.human_owner, summary=EXCLUDED.summary,
          metadata=factory.projects.metadata || EXCLUDED.metadata,
          updated_at=now();
        INSERT INTO factory.events(project_id, actor, event_type, message, metadata)
        VALUES ({_q(pid)}, 'factory-orchestrator', 'project_created', {_q(f'Factory project {pid} initialized')}, {_j({'methodology': methodology, 'source_of_truth': 'agent_core_postgres', 'repo_strategy': strategy})});
    """, user=_user())
    lanes = []
    if create_default_lanes:
        for _suffix, lane_name, method in DEFAULT_LANES:
            lanes.append(create_lane(pid, lane_name, method))
    return {"project_id": pid, "lanes": lanes, "repo_strategy": strategy}


def create_lane(project_id: str, name: str, methodology: str, *, lane_id: Optional[str] = None, kanban_board: Optional[str] = None, branch: Optional[str] = None, worktree_path: Optional[str] = None, metadata: Optional[dict[str, Any]] = None, **_: Any) -> dict[str, Any]:
    ensure_runtime_schema()
    if methodology not in VALID_METHODS:
        raise ValueError(f"unknown methodology {methodology!r}; expected one of {sorted(VALID_METHODS)}")
    suffix = "zeus" if methodology == "zeus_native" else "bmad" if methodology == "bmad_hybrid" else slugify(methodology)
    lid = lane_id or f"{project_id}-{suffix}"
    branch_value = branch or f"factory/{project_id}/{suffix}"
    meta = {"execution_surface": "factory", **(metadata or {})}
    if kanban_board:
        # Explicitly recorded as an exception; Factory DB remains canonical.
        meta["execution_surface"] = "kanban_bridge"
        meta["kanban_board"] = kanban_board
    sql.psql(f"""
        INSERT INTO factory.lanes (lane_id, project_id, name, methodology, branch, worktree_path, status, metadata, created_at, updated_at)
        VALUES ({_q(lid)}, {_q(project_id)}, {_q(name)}, {_q(methodology)}, {_q(branch_value)}, {_q(worktree_path)}, 'planned', {_j(meta)}, now(), now())
        ON CONFLICT (lane_id) DO UPDATE SET name=EXCLUDED.name, methodology=EXCLUDED.methodology, branch=EXCLUDED.branch, worktree_path=EXCLUDED.worktree_path, metadata=factory.lanes.metadata || EXCLUDED.metadata, updated_at=now();
        INSERT INTO factory.events(project_id, lane_id, actor, event_type, message, metadata)
        VALUES ({_q(project_id)}, {_q(lid)}, 'factory-orchestrator', 'lane_created', {_q(f'Lane {lid} initialized')}, {_j({'methodology': methodology, 'execution_surface': meta['execution_surface'], 'branch': branch_value})});
    """, user=_user())
    result = {"lane_id": lid, "project_id": project_id, "methodology": methodology, "execution_surface": meta["execution_surface"], "branch": branch_value}
    if kanban_board:
        result["kanban_board"] = kanban_board
    return result


def _next_increment_key(project_id: str, priority: int, title: str, metadata: Optional[dict[str, Any]]) -> str:
    if metadata and metadata.get("increment_key"):
        return str(metadata["increment_key"])
    return f"inc-{int(priority):03d}-{slugify(title)[:32]}"


def create_task(project_id: str, title: str, *, lane_id: Optional[str] = None, kanban_id: Optional[str] = None, description: Optional[str] = None, phase: str = "planning", status: str = "todo", owner_agent_id: Optional[str] = None, reviewer_agent_id: Optional[str] = None, engine: str = "zeus", priority: int = 100, acceptance_criteria: Optional[list[str]] = None, dependencies: Optional[list[str]] = None, branch: Optional[str] = None, worktree_path: Optional[str] = None, metadata: Optional[dict[str, Any]] = None, **_: Any) -> dict[str, Any]:
    ensure_runtime_schema()
    base = f"{project_id}-{slugify(title)[:40]}"
    existing = sql.rows(f"SELECT task_id FROM factory.tasks WHERE task_id LIKE {_q(base + '%')} ORDER BY task_id", user=_user())
    taken = {r['task_id'] for r in existing}
    task_id = base
    n = 2
    while task_id in taken:
        task_id = f"{base}-{n}"
        n += 1
    increment_key = _next_increment_key(project_id, priority, title, metadata)
    project = _project(project_id)
    derived_branch, derived_worktree, strategy = _task_branch_and_worktree(project, increment_key)
    branch_value = branch or derived_branch
    worktree_value = worktree_path or derived_worktree
    meta = {"source": "factory_task_create", "repo_strategy_status": strategy.get("status"), **(metadata or {})}
    sql.psql(f"""
        INSERT INTO factory.tasks (task_id, project_id, lane_id, kanban_id, title, description, phase, status, owner_profile, reviewer_profile, engine, priority, dependencies, branch, worktree_path, acceptance_criteria, evidence_required, evidence_status, risk_level, metadata, increment_key, increment_order, created_at, updated_at)
        VALUES ({_q(task_id)}, {_q(project_id)}, {_q(lane_id)}, {_q(kanban_id)}, {_q(title)}, {_q(description)}, {_q(phase)}, {_q(status)}, {_q(owner_agent_id)}, {_q(reviewer_agent_id)}, {_q(engine)}, {int(priority)}, {_j(dependencies or [])}, {_q(branch_value)}, {_q(worktree_value)}, {_j(acceptance_criteria or [])}, true, 'missing', 'medium', {_j(meta)}, {_q(increment_key)}, {int(priority)}, now(), now());
        INSERT INTO factory.events(project_id, lane_id, task_id, actor, event_type, message, metadata)
        VALUES ({_q(project_id)}, {_q(lane_id)}, {_q(task_id)}, 'factory-orchestrator', 'task_created', {_q(f'Task {task_id} created')}, {_j({'engine': engine, 'owner': owner_agent_id, 'kanban_id': kanban_id, 'increment_key': increment_key, 'branch': branch_value, 'worktree_path': worktree_value})});
    """, user=_user())
    return {"task_id": task_id, "project_id": project_id, "lane_id": lane_id, "increment_key": increment_key, "branch": branch_value, "worktree_path": worktree_value}


def _project(project_id: str) -> dict[str, Any] | None:
    row = sql.one(f"SELECT * FROM factory.projects WHERE project_id={_q(project_id)}", user=_user())
    return _normalize(row) if row else None


def _tasks(project_id: str) -> list[dict[str, Any]]:
    return _normalize_rows(sql.rows(f"SELECT * FROM factory.tasks WHERE project_id={_q(project_id)} ORDER BY priority, created_at", user=_user()))


def _latest_gate_rows(project_id: str) -> list[dict[str, Any]]:
    """Latest effective stage gate per gate_type for a project.

    Gate rows are an audit log. Older ``pending`` or ``failed`` rows must not
    keep a project blocked after a later authoritative stage decision exists.
    """

    return _normalize_rows(sql.rows(
        f"""
        SELECT DISTINCT ON (gate_type) *
        FROM factory.gates
        WHERE project_id={_q(project_id)}
        ORDER BY gate_type, timestamp DESC, gate_id DESC
        """,
        user=_user(),
    ))


def _active_pending_gates(project_id: str) -> list[dict[str, Any]]:
    return [gate for gate in _latest_gate_rows(project_id) if str(gate.get("status") or "") == "pending"]


def _metadata(row: dict[str, Any]) -> dict[str, Any]:
    value = row.get("metadata")
    return value if isinstance(value, dict) else {}


def _metadata_bool(metadata: dict[str, Any], key: str) -> bool:
    value = metadata.get(key)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "required", "mandatory"}
    return bool(value)


_UI_DELIVERABLE_TYPES = {
    "ui",
    "web",
    "website",
    "landing_page",
    "frontend",
    "web_app",
    "browser_app",
    "dashboard",
    "spa",
}
_RUNNABLE_DELIVERABLE_TYPES = _UI_DELIVERABLE_TYPES | {"api", "backend", "service", "app", "worker", "integration"}
_DEFAULT_AUTHORIZED_SANDBOX_HOSTS = ("kidu.app", "*.kidu.app")


def _metadata_text_values(metadata: dict[str, Any], *keys: str) -> set[str]:
    values: set[str] = set()
    for key in keys:
        value = metadata.get(key)
        if isinstance(value, str):
            values.add(value.strip().lower().replace("-", "_"))
        elif isinstance(value, (list, tuple, set)):
            for item in value:
                if isinstance(item, str):
                    values.add(item.strip().lower().replace("-", "_"))
    return {value for value in values if value}


def _project_requires_ui_delivery(project: dict[str, Any]) -> bool:
    metadata = _metadata(project)
    if any(_metadata_bool(metadata, key) for key in ("ui_deliverable", "requires_ui_qa", "browser_deliverable", "frontend_deliverable")):
        return True
    deliverable_types = _metadata_text_values(metadata, "deliverable_type", "deliverable_types", "project_type", "surface", "surfaces")
    return bool(deliverable_types & _UI_DELIVERABLE_TYPES)


def _project_requires_sandbox_delivery(project: dict[str, Any]) -> bool:
    metadata = _metadata(project)
    if _project_requires_ui_delivery(project):
        return True
    if any(_metadata_bool(metadata, key) for key in ("runnable_deliverable", "sandbox_required", "requires_sandbox_delivery")):
        return True
    if str(metadata.get("delivery_target") or "").strip().lower().replace("-", "_") == "sandbox":
        return True
    deliverable_types = _metadata_text_values(metadata, "deliverable_type", "deliverable_types", "project_type", "surface", "surfaces")
    return bool(deliverable_types & _RUNNABLE_DELIVERABLE_TYPES)


def _task_text(task: dict[str, Any]) -> str:
    fields = ("task_id", "title", "description", "phase", "owner_profile", "reviewer_profile", "engine")
    return "\n".join(str(task.get(key) or "") for key in fields).lower()


def _task_counts_for_phase_contract(task: dict[str, Any]) -> bool:
    return str(task.get("status") or "") not in {"cancelled", "superseded"}


def _task_satisfies_mandatory_category(task: dict[str, Any], category: str) -> bool:
    if not _task_counts_for_phase_contract(task):
        return False
    phase = str(task.get("phase") or "").lower().replace("-", "_")
    owner = str(task.get("owner_profile") or task.get("owner_agent_id") or "").lower()
    reviewer = str(task.get("reviewer_profile") or task.get("reviewer_agent_id") or "").lower()
    text = _task_text(task)
    if category == "planning":
        return owner == "implementation-planner" and (
            phase in {"planning", "documentation", "docs", "architecture", "research"}
            or any(term in text for term in ("prd", "adr", "sprint plan", "task graph", "technical blueprint"))
        )
    if category == "implementation":
        return owner in {"claude-builder", "claude-deepseek-builder", "codex-builder", "openhands-builder", "claude-code-builder"} and phase == "implementation"
    if category == "quality_review":
        return owner == "quality-reviewer" and phase in {"review", "quality_review", "quality"}
    if category == "security_review":
        return owner == "security-reviewer" and phase == "security"
    if category == "qa_verification":
        return owner == "qa-verifier" and phase == "qa" and any(term in text for term in ("qa", "smoke", "test gate", "verification"))
    if category == "ui_qa_verification":
        return owner == "qa-verifier" and phase == "qa" and any(term in text for term in ("playwright", "browser", "screenshot", "console", "visual", "mobile", "desktop"))
    if category == "sandbox_deploy":
        return owner == "devops-release" and phase in {"delivery", "deploy", "deployment", "release"} and any(term in text for term in ("sandbox", "deploy", "docker compose", "caddy", "preview url", "public url"))
    if category == "post_sandbox_verification":
        return owner == "qa-verifier" and phase in {"qa", "delivery"} and any(term in text for term in ("post-sandbox", "post sandbox", "post-deploy", "post deploy", "public sandbox", "sandbox url", "live sandbox")) and any(term in text for term in ("playwright", "browser", "smoke", "console", "screenshot", "api", "health", "endpoint", "curl", "http", "status"))
    if category == "delivery_report":
        return owner == "factory-reporter" and phase in {"delivery", "reporting", "documentation"} and any(term in text for term in ("delivery report", "delivery gate", "gate closure", "qa_report", "qa report"))
    return False


def _mandatory_phase_categories(project: dict[str, Any]) -> list[str]:
    if not _project_requires_sandbox_delivery(project):
        return []
    metadata = _metadata(project)
    categories = ["planning", "implementation", "quality_review"]
    categories.append("ui_qa_verification" if _project_requires_ui_delivery(project) else "qa_verification")
    if _metadata_bool(metadata, "security_required"):
        categories.append("security_review")
    categories.extend(["sandbox_deploy", "post_sandbox_verification", "delivery_report"])
    return categories


def _missing_mandatory_phase_categories(project: dict[str, Any], tasks: list[dict[str, Any]]) -> list[str]:
    """Return mandatory categories not covered by distinct Factory tasks.

    The contract requires explicit phases, not one keyword-stuffed task that
    pretends to cover planning, build, QA, deploy, post-sandbox verification,
    and report at once. Use bipartite matching so coverage is order-independent:
    if a post-sandbox task appears before a normal QA task, the matcher can
    still assign each category to a distinct task.
    """

    categories = _mandatory_phase_categories(project)
    task_keys: dict[int, str] = {
        index: f"{task.get('task_id') or task.get('id') or 'task'}:{index}"
        for index, task in enumerate(tasks)
    }
    candidates: dict[str, list[str]] = {
        category: [
            task_keys[index]
            for index, task in enumerate(tasks)
            if _task_satisfies_mandatory_category(task, category)
        ]
        for category in categories
    }
    task_to_category: dict[str, str] = {}

    def _try_match(category: str, seen_tasks: set[str]) -> bool:
        for task_key in candidates.get(category, []):
            if task_key in seen_tasks:
                continue
            seen_tasks.add(task_key)
            previous_category = task_to_category.get(task_key)
            if previous_category is None or _try_match(previous_category, seen_tasks):
                task_to_category[task_key] = category
                return True
        return False

    for category in categories:
        _try_match(category, set())

    matched_categories = set(task_to_category.values())
    return [category for category in categories if category not in matched_categories]


def _authorized_sandbox_hosts(metadata: dict[str, Any]) -> list[str]:
    raw_hosts = metadata.get("authorized_sandbox_hosts") or metadata.get("sandbox_authorized_hosts") or metadata.get("allowed_sandbox_hosts")
    hosts: list[str] = []
    custom_authorized_by = (
        metadata.get("authorized_sandbox_hosts_authorized_by")
        or metadata.get("sandbox_authorized_hosts_authorized_by")
        or metadata.get("allowed_sandbox_hosts_authorized_by")
        or metadata.get("sandbox_host_authorized_by")
    )
    custom_authorization_reason = (
        metadata.get("authorized_sandbox_hosts_reason")
        or metadata.get("sandbox_authorized_hosts_reason")
        or metadata.get("allowed_sandbox_hosts_reason")
        or metadata.get("sandbox_host_authorization_reason")
    )
    custom_hosts_authorized = bool(custom_authorized_by and str(custom_authorization_reason or "").strip())
    if custom_hosts_authorized and isinstance(raw_hosts, str):
        hosts.extend(part.strip().lower() for part in raw_hosts.split(",") if part.strip())
    elif custom_hosts_authorized and isinstance(raw_hosts, (list, tuple, set)):
        hosts.extend(str(part).strip().lower() for part in raw_hosts if str(part).strip())
    for host in _DEFAULT_AUTHORIZED_SANDBOX_HOSTS:
        if host not in hosts:
            hosts.append(host)
    return hosts


def _host_matches_authorized_sandbox(host: str, authorized_hosts: list[str]) -> bool:
    clean = host.strip().lower().split(":", 1)[0]
    for allowed in authorized_hosts:
        allowed = allowed.strip().lower()
        if allowed.startswith("*."):
            suffix = allowed[1:]
            if clean.endswith(suffix) and clean != suffix.lstrip("."):
                return True
        elif clean == allowed:
            return True
    return False


def _delivery_url_from_evidence(evidence: dict[str, Any]) -> str:
    for key in ("sandbox_url", "preview_url", "public_url", "delivery_url"):
        value = evidence.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _evidence_url_from_keys(evidence: dict[str, Any], *keys: str) -> str:
    for key in keys:
        extracted = _evidence_url_from_value(evidence.get(key))
        if extracted:
            return extracted
    return ""


def _evidence_urls_by_key(evidence: dict[str, Any], *keys: str) -> dict[str, str]:
    urls: dict[str, str] = {}
    for key in keys:
        value = evidence.get(key)
        extracted = _evidence_url_from_value(value)
        if extracted:
            urls[key] = extracted
    return urls


def _evidence_url_from_value(value: Any) -> str:
    if isinstance(value, str) and value.strip().lower().startswith(("http://", "https://")):
        return value.strip()
    if isinstance(value, dict):
        for nested_key in ("url", "href", "target", "target_url", "checked_url", "health_url", "endpoint"):
            nested = value.get(nested_key)
            if isinstance(nested, str) and nested.strip().lower().startswith(("http://", "https://")):
                return nested.strip()
    return ""


def _url_host(value: str) -> str:
    parsed = urlparse(value or "")
    return parsed.netloc.lower().split(":", 1)[0]


def _same_url_host(a: str, b: str) -> bool:
    return bool(_url_host(a) and _url_host(a) == _url_host(b))


def _evidence_status_passed(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value == 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "passed", "pass", "ok", "success", "succeeded", "clean", "done"}
    if isinstance(value, dict):
        for key in ("errors", "error_count", "console_errors", "critical_errors"):
            if key in value:
                try:
                    if int(value.get(key) or 0) > 0:
                        return False
                except (TypeError, ValueError):
                    return False
        return any(_evidence_status_passed(value.get(key)) for key in ("passed", "status", "result", "state", "ok"))
    return False


def _non_empty_path(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, dict):
        return any(_non_empty_path(value.get(key)) for key in ("path", "url", "file", "artifact"))
    return False


def _path_string(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        for key in ("path", "file", "artifact", "url"):
            item = value.get(key)
            if isinstance(item, str) and item.strip():
                return item.strip()
    return ""


def _authorized_project_sandbox_root(project: dict[str, Any]) -> str:
    project_id = str(project.get("project_id") or "").strip() or "<project>"
    return f"/srv/factory/projects/{project_id}"


def _path_under_root(path: str, root: str) -> bool:
    if not path.strip() or not root.strip():
        return False
    clean = posixpath.normpath(path.strip())
    root_clean = posixpath.normpath(root.strip())
    if not clean.startswith("/") or not root_clean.startswith("/"):
        return False
    return clean == root_clean or clean.startswith(root_clean + "/")


def _evidence_path_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, dict):
        values: list[str] = []
        for item in value.values():
            values.extend(_evidence_path_strings(item))
        return values
    if isinstance(value, (list, tuple, set)):
        values: list[str] = []
        for item in value:
            values.extend(_evidence_path_strings(item))
        return values
    return []


def _evidence_paths_present(evidence: dict[str, Any]) -> bool:
    value = evidence.get("evidence_paths") or evidence.get("artifacts")
    return bool(_evidence_path_strings(value))


def _missing_ui_evidence_path_labels(evidence: dict[str, Any]) -> list[str]:
    paths = _evidence_path_strings(evidence.get("evidence_paths") or evidence.get("artifacts"))
    lowered = [path.lower() for path in paths]
    desktop = str(_screenshot_evidence_path(evidence, "desktop") or "").strip().lower()
    mobile = str(_screenshot_evidence_path(evidence, "mobile") or "").strip().lower()
    qa_report = str(evidence.get("qa_report_path") or evidence.get("qa_report") or evidence.get("QA_REPORT.md") or "").strip()
    qa_report_lower = qa_report.lower()
    missing: list[str] = []
    if not desktop or not any(path == desktop or "desktop" in path for path in lowered):
        missing.append("desktop_screenshot")
    if not mobile or not any(path == mobile or "mobile" in path for path in lowered):
        missing.append("mobile_screenshot")
    if not qa_report_lower or not any(path == qa_report_lower or "qa_report.md" in path for path in lowered):
        missing.append("QA_REPORT.md")
    return missing


def _console_error_check_passed(evidence: dict[str, Any]) -> bool:
    if "console_error_check" in evidence:
        return _evidence_status_passed(evidence.get("console_error_check"))
    for key in ("console_errors", "console_error_count", "browser_console_errors"):
        if key in evidence:
            try:
                return int(evidence.get(key) or 0) == 0
            except (TypeError, ValueError):
                return False
    return False


def _screenshot_evidence_path(evidence: dict[str, Any], viewport: str) -> Any:
    direct = evidence.get(f"{viewport}_screenshot")
    if direct:
        return direct
    screenshots = evidence.get("screenshots")
    if isinstance(screenshots, dict):
        return screenshots.get(viewport)
    return None


def _delivery_evidence_findings(project: dict[str, Any], evidence: dict[str, Any]) -> list[str]:
    metadata = _metadata(project)
    findings: list[str] = []
    requires_sandbox = _project_requires_sandbox_delivery(project)
    requires_ui = _project_requires_ui_delivery(project)
    if not requires_sandbox and not requires_ui:
        return findings

    sandbox_url = _delivery_url_from_evidence(evidence)
    if not sandbox_url:
        findings.append("sandbox_url public authorized sandbox URL is required")
    else:
        parsed = urlparse(sandbox_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            findings.append("sandbox_url must be an http(s) public authorized sandbox URL")
        elif not _host_matches_authorized_sandbox(parsed.netloc, _authorized_sandbox_hosts(metadata)):
            findings.append("sandbox_url must use an authorized sandbox host (*.kidu.app by default)")

    if requires_sandbox:
        sandbox_root = _authorized_project_sandbox_root(project)
        deploy_path = _path_string(evidence.get("sandbox_deploy_path") or evidence.get("deploy_path"))
        compose_path = _path_string(evidence.get("docker_compose_path") or evidence.get("compose_path"))
        public_check_urls = _evidence_urls_by_key(
            evidence,
            "health_url",
            "api_smoke_url",
            "api_health_smoke_url",
            "sandbox_public_smoke_url",
            "public_url_smoke_url",
            "sandbox_smoke_url",
            "public_smoke_url",
        )
        smoke_status_url_keys = {
            "sandbox_public_smoke": ("sandbox_public_smoke_url", "public_smoke_url", "sandbox_smoke_url"),
            "public_url_smoke": ("public_url_smoke_url", "public_smoke_url"),
            "sandbox_smoke": ("sandbox_smoke_url", "public_smoke_url"),
            "health_check": ("health_url",),
            "api_smoke": ("api_smoke_url",),
            "api_health_smoke": ("api_health_smoke_url", "health_url"),
        }
        passed_public_smokes = 0
        for status_key, url_keys in smoke_status_url_keys.items():
            if not _evidence_status_passed(evidence.get(status_key)):
                continue
            passed_public_smokes += 1
            if status_key == "api_smoke":
                status_url = _evidence_url_from_keys(evidence, *url_keys)
            else:
                status_url = _evidence_url_from_value(evidence.get(status_key)) or _evidence_url_from_keys(evidence, *url_keys)
            if not status_url:
                findings.append(f"{status_key} evidence must include a public same-host URL")
            else:
                public_check_urls.setdefault(f"{status_key}_url", status_url)
        if not passed_public_smokes:
            findings.append("sandbox_public_smoke/public_url_smoke must be passed against the public sandbox URL")
        if sandbox_url:
            for key, value in public_check_urls.items():
                if not _same_url_host(value, sandbox_url):
                    findings.append(f"{key} must target the same public sandbox host as sandbox_url")
        if not deploy_path:
            findings.append(f"sandbox_deploy_path under {sandbox_root} is required")
        elif not _path_under_root(deploy_path, sandbox_root):
            findings.append(f"sandbox_deploy_path must be under authorized sandbox root {sandbox_root}")
        if not compose_path:
            findings.append("docker_compose_path is required for runnable sandbox delivery unless explicitly waived")
        elif not _path_under_root(compose_path, sandbox_root):
            findings.append(f"docker_compose_path must be under authorized sandbox root {sandbox_root}")
        elif Path(compose_path).name not in {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}:
            findings.append("docker_compose_path must point to a Docker Compose file")

    if requires_ui:
        playwright_passed = _evidence_status_passed(evidence.get("playwright_smoke"))
        browser_passed = _evidence_status_passed(evidence.get("browser_smoke"))
        playwright_url = _evidence_url_from_keys(evidence, "playwright_url")
        browser_url = _evidence_url_from_keys(evidence, "browser_smoke_url", "verified_url", "validated_url", "qa_url")
        for key, value in _evidence_urls_by_key(evidence, "playwright_url", "browser_smoke_url", "verified_url", "validated_url", "qa_url").items():
            if sandbox_url and not _same_url_host(value, sandbox_url):
                findings.append(f"{key} must target the same public sandbox host as sandbox_url")
        if not (playwright_url or browser_url):
            findings.append("playwright_url/browser_smoke_url for the public sandbox URL is required")
        if playwright_passed and not playwright_url:
            findings.append("playwright_smoke evidence must include playwright_url on the public sandbox host")
        if browser_passed and not browser_url:
            findings.append("browser_smoke evidence must include browser_smoke_url/verified_url on the public sandbox host")
        if not (playwright_passed or browser_passed):
            findings.append("playwright_smoke or equivalent browser_smoke must be passed")
        if not _non_empty_path(_screenshot_evidence_path(evidence, "desktop")):
            findings.append("desktop_screenshot evidence path is required")
        if not _non_empty_path(_screenshot_evidence_path(evidence, "mobile")):
            findings.append("mobile_screenshot evidence path is required")
        if not _console_error_check_passed(evidence):
            findings.append("console_error_check must be present and clean")
        if not _evidence_status_passed(evidence.get("core_flow_interaction") or evidence.get("core_flow_result")):
            findings.append("core_flow_interaction must be passed")
        qa_report = evidence.get("qa_report_path") or evidence.get("qa_report") or evidence.get("QA_REPORT.md")
        if not (_non_empty_path(qa_report) and "QA_REPORT.md" in str(qa_report)):
            findings.append("QA_REPORT.md path is required")
        missing_path_labels = _missing_ui_evidence_path_labels(evidence)
        if missing_path_labels:
            findings.append("evidence_paths must include " + ", ".join(missing_path_labels))
        if not _evidence_paths_present(evidence):
            findings.append("evidence_paths must list screenshots, QA report, and other verification artifacts")
    return findings


def _waiver_explicitly_authorized(metadata: dict[str, Any], waiver_key: str) -> bool:
    """Return True only for a project-specific waiver Jean authorized.

    Suppressor booleans such as ``notion_waived`` and
    ``required_docs_waived`` explain historical drift, but they must not mute
    canonical Factory readiness unless an explicit human authorization is
    attached to that project.
    """

    if not metadata.get(waiver_key):
        return False
    authorizer = (
        metadata.get(f"{waiver_key}_authorized_by")
        or metadata.get("waiver_authorized_by")
        or metadata.get("waivers_authorized_by")
    )
    reason = (
        metadata.get(f"{waiver_key}_reason")
        or metadata.get("waiver_reason")
        or metadata.get("waiver_authorization_reason")
    )
    return bool(authorizer and reason)


def _any_explicit_waiver(metadata: dict[str, Any], *waiver_keys: str) -> bool:
    return any(_waiver_explicitly_authorized(metadata, key) for key in waiver_keys)


def _has_unauthorized_completion_waivers(metadata: dict[str, Any]) -> bool:
    waiver_keys = ("notion_waived", "tracker_waived", "required_docs_waived")
    return any(metadata.get(key) and not _waiver_explicitly_authorized(metadata, key) for key in waiver_keys)


def _required_docs_explicitly_waived(metadata: dict[str, Any]) -> bool:
    if _waiver_explicitly_authorized(metadata, "required_docs_waived"):
        return True
    waivers = metadata.get("required_doc_waivers")
    if not waivers:
        return False
    authorizer = metadata.get("required_doc_waivers_authorized_by") or metadata.get("waiver_authorized_by")
    reason = metadata.get("required_doc_waivers_reason") or metadata.get("waiver_reason")
    return bool(authorizer and reason)


def _repository_strategy(project: dict[str, Any]) -> dict[str, Any]:
    return factory_contracts.repository_strategy_from_project(project)


def _repository_strategy_complete(project: dict[str, Any]) -> bool:
    return factory_contracts.repository_strategy_is_complete(_repository_strategy(project))


def _task_increment_key(project_id: str, priority: int, title: str, metadata: Optional[dict[str, Any]]) -> str:
    return _next_increment_key(project_id, priority, title, metadata)


def _task_branch_and_worktree(project: dict[str, Any] | None, increment_key: str) -> tuple[str | None, str | None, dict[str, Any]]:
    if not project:
        return None, None, {}
    strategy = _repository_strategy(project)
    if not factory_contracts.repository_strategy_is_complete(strategy):
        return None, None, strategy
    project_id = str(project.get("project_id") or "")
    branch = factory_contracts.increment_branch_name(project_id, increment_key, strategy)
    worktree = factory_contracts.increment_worktree_path(project_id, increment_key, strategy)
    return branch or None, worktree or None, strategy


def _all_open_work_is_reconciliation(tasks: list[dict[str, Any]]) -> bool:
    open_tasks = [task for task in tasks if str(task.get("status") or "") not in TERMINAL_TASK_STATUSES]
    return bool(open_tasks) and all(_is_reconciliation_task(task) for task in open_tasks)


def _all_blocked_work_is_documentation_hold(tasks: list[dict[str, Any]]) -> bool:
    blocked_statuses = {"blocked", "review_pending_human"}
    blocking_tasks = [task for task in tasks if str(task.get("status") or "") in blocked_statuses]
    if not blocking_tasks:
        return False
    documentation_phases = {"documentation", "docs", "pm", "reporting"}
    for task in blocking_tasks:
        phase = str(task.get("phase") or "").lower()
        if phase not in documentation_phases and not _is_reconciliation_task(task):
            return False
    return True


def _project_artifact_dir(project: dict[str, Any]) -> tuple[Path | None, str]:
    project_id = str(project.get("project_id") or "")
    metadata = _metadata(project)
    artifact_dir = str(metadata.get("artifact_dir") or f"factory/projects/{project_id}")
    repo_path = str(project.get("repo_path") or "").strip()
    if not repo_path:
        return None, artifact_dir
    return Path(repo_path).expanduser() / artifact_dir, artifact_dir


def _docs_missing_from_documentation_index(factory_dir: Path, required_docs: tuple[str, ...] = FACTORY_REQUIRED_DOCS) -> list[str]:
    """Return required docs not referenced by the project documentation index.

    The repo-first Factory contract treats ``DOCUMENTATION_INDEX.md`` as the
    builder entry point. A file existing on disk is not enough; builders and
    reviewers need the index to enumerate every canonical artifact path.
    """

    index_path = factory_dir / "DOCUMENTATION_INDEX.md"
    try:
        index_text = index_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return list(required_docs)
    return [name for name in required_docs if name not in index_text]


def _documentation_index_text(factory_dir: Path | None) -> str:
    if factory_dir is None:
        return ""
    try:
        return (factory_dir / "DOCUMENTATION_INDEX.md").read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _documentation_index_line(index_text: str, file_name: str) -> str:
    for line in index_text.splitlines():
        if file_name in line:
            return line
    return ""


def _project_document_metadata(project: dict[str, Any], file_name: str) -> dict[str, Any]:
    metadata = _metadata(project)
    docs = metadata.get("document_status") or metadata.get("documents") or metadata.get("factory_documents")
    if isinstance(docs, dict):
        value = docs.get(file_name)
        return value if isinstance(value, dict) else {}
    return {}


def _git_status_by_file(repo_path: str, artifact_dir: str) -> dict[str, str] | None:
    repo = Path(repo_path).expanduser() if repo_path else None
    if not repo or not repo.exists():
        return None
    try:
        probe = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--is-inside-work-tree"],
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
        if probe.returncode != 0 or probe.stdout.strip() != "true":
            return None
        status = subprocess.run(
            ["git", "-C", str(repo), "status", "--porcelain", "--", artifact_dir],
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
    except Exception:
        return None
    if status.returncode != 0:
        return None
    result: dict[str, str] = {}
    prefix = str(artifact_dir).strip("/") + "/"
    for raw in status.stdout.splitlines():
        if not raw.strip():
            continue
        state = raw[:2].strip() or raw[:2]
        path = raw[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        if path.startswith(prefix):
            result[Path(path).name] = state
    return result


def _document_flag_from_text(metadata: dict[str, Any], index_line: str, file_text: str, flag: str) -> bool:
    value = metadata.get(flag)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "y", "1", "passed", "validated", "reviewed", "approved"}
    text = (index_line + "\n" + file_text[:2000]).lower()
    if re.search(rf"\b(not|no|pending|todo|tbd|unvalidated|unreviewed)\b[^\n]{{0,40}}\b{re.escape(flag)}\b", text):
        return False
    if flag == "validated":
        return bool(re.search(r"\b(validated|validado|validation)\b\s*[:=\-]\s*(yes|true|passed|ok|validated)", text) or re.search(r"\bstatus\b\s*[:=\-]\s*validated\b", text))
    if flag == "reviewed":
        return bool(
            re.search(r"\b(reviewed|revisado)\b\s*[:=\-]\s*(yes|true|passed|ok|reviewed)", text)
            or re.search(r"\b(reviewed by|reviewer|approved by|jean-approved)\b\s*[:=\-]?\s*[a-z0-9]", text)
            or re.search(r"\bstatus\b\s*[:=\-]\s*(reviewed|approved)\b", text)
        )
    return False


def project_document_status(project: dict[str, Any]) -> list[dict[str, Any]]:
    """Return first-class per-file Factory document readiness state.

    G1 documents are blocking source-of-truth artifacts for implementation
    dispatch. Lifecycle and PM projection docs are exposed for UI/reporting but
    are not implementation blockers by default.
    """

    factory_dir, artifact_dir = _project_artifact_dir(project)
    repo_path = str(project.get("repo_path") or "").strip()
    index_text = _documentation_index_text(factory_dir)
    git_state = _git_status_by_file(repo_path, artifact_dir) if repo_path else None
    statuses: list[dict[str, Any]] = []
    seen: set[str] = set()
    for file_name, category in FACTORY_DOCUMENT_DEFINITIONS:
        if file_name in seen:
            continue
        seen.add(file_name)
        path = factory_dir / file_name if factory_dir is not None else None
        exists = bool(path and path.is_file())
        try:
            file_text = path.read_text(encoding="utf-8", errors="replace") if exists and path is not None else ""
        except Exception:
            file_text = ""
        index_line = _documentation_index_line(index_text, file_name)
        indexed = bool(index_line)
        committed = bool(exists and git_state is not None and file_name not in git_state)
        doc_meta = _project_document_metadata(project, file_name)
        validated = _document_flag_from_text(doc_meta, index_line, file_text, "validated")
        reviewed = _document_flag_from_text(doc_meta, index_line, file_text, "reviewed")
        owner = doc_meta.get("owner") or doc_meta.get("owner_profile")
        reviewer = doc_meta.get("reviewer") or doc_meta.get("reviewer_profile")
        blocking = category == "g1_required" and not (exists and indexed and committed and validated and reviewed)
        statuses.append({
            "file_name": file_name,
            "path": f"{artifact_dir.rstrip('/')}/{file_name}",
            "category": category,
            "exists": exists,
            "indexed": indexed,
            "committed": committed,
            "validated": validated,
            "reviewed": reviewed,
            "blocking": blocking,
            "owner": owner,
            "reviewer": reviewer,
            "git_status": git_state.get(file_name) if git_state is not None else "unverified",
        })
    return statuses


def _g1_document_blockers(project: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in project_document_status(project) if row.get("category") == "g1_required" and row.get("blocking")]


def _repo_commit_explicitly_waived(metadata: dict[str, Any]) -> bool:
    return _any_explicit_waiver(
        metadata,
        "repo_commit_waived",
        "commit_checkpoint_waived",
        "uncommitted_artifacts_waived",
    )


def _uncommitted_project_artifacts(repo_path: Path, artifact_dir: str) -> list[str]:
    """Return git porcelain rows for uncommitted project-local artifacts.

    If the repo is unavailable or not a git worktree, return an empty list so the
    reconciler does not turn filesystem errors into false blockers. Git-backed
    Factory repos, however, must leave no modified/untracked project artifacts
    before critical readiness/delivery closure.
    """

    repo = Path(repo_path).expanduser()
    if not repo.exists():
        return []
    try:
        probe = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--is-inside-work-tree"],
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
        if probe.returncode != 0 or probe.stdout.strip() != "true":
            return []
        status = subprocess.run(
            ["git", "-C", str(repo), "status", "--porcelain", "--", artifact_dir],
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
    except Exception:
        return []
    if status.returncode != 0:
        return []
    return [line for line in status.stdout.splitlines() if line.strip()]


def _is_reconciliation_task(task: dict[str, Any]) -> bool:
    metadata = _metadata(task)
    if metadata.get("factory_reconciliation_task") or metadata.get("reconciliation_anomaly"):
        return True
    text = "\n".join(str(task.get(key) or "") for key in ("task_id", "title", "description", "phase")).lower()
    return "reconciliation" in text or "reconciliación" in text


def _task_covers_reconciliation_anomaly(task: dict[str, Any], code: str) -> bool:
    if str(task.get("status") or "") in TERMINAL_TASK_STATUSES:
        return False
    metadata = _metadata(task)
    if metadata.get("reconciliation_anomaly") == code:
        return True
    text = "\n".join(str(task.get(key) or "") for key in ("task_id", "title", "description", "phase")).lower()
    if code == "missing_repository_strategy":
        return "repository strategy" in text or "repo strategy" in text or "g0" in text or "branch" in text or "worktree" in text
    if code == "missing_notion_project":
        return "pm tracker" in text or "tracker metadata" in text or "notion_required" in text or "required notion" in text
    if code == "notion_pm_projection_warning":
        return "pm projection" in text or "executive visibility" in text or "reporting surface" in text
    if code == "missing_project_artifact_dir":
        return "artifact" in text or "documentation" in text or "documentación" in text
    if code == "missing_required_docs":
        return any(term in text for term in ("documentation", "documentación", "docs", "tracker", "delivery report"))
    if code == "docs_not_indexed":
        return "documentation_index" in text or "documentation index" in text or "índice" in text or "indexed" in text
    if code == "uncommitted_project_artifacts":
        return "commit" in text or "uncommitted" in text or "git" in text or "checkpoint" in text
    if code == "missing_task_graph":
        return "task graph" in text or "task-graph" in text or "canonical task" in text or "task graph recovery" in text
    if code == "missing_mandatory_factory_phases":
        if not _is_reconciliation_task(task):
            return False
        return "mandatory phase" in text or "phase contract" in text or "canonical factory phase" in text or "playwright" in text or "sandbox deploy" in text
    if code == "pending_effective_gates":
        return str(task.get("phase") or "").lower() in {"review", "qa", "security"} or "gate" in text
    if code == "deliverable_unverified":
        return str(task.get("phase") or "").lower() in {"delivery", "qa", "security"} or any(term in text for term in ("delivery", "deliverable", "qa", "security review"))
    return False


def _latest_gate_statuses(gates: list[dict[str, Any]]) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for gate in gates:
        gate_type = str(gate.get("gate_type") or "").strip()
        if gate_type and gate_type not in statuses:
            statuses[gate_type] = str(gate.get("status") or "").strip()
    return statuses


def _notion_projection_issue(metadata: dict[str, Any]) -> str | None:
    tracker_ok = bool(
        metadata.get("notion_tracker_url")
        or metadata.get("notion_tracker_page_id")
        or _any_explicit_waiver(metadata, "notion_waived", "tracker_waived")
    )
    if not tracker_ok:
        return "missing"
    if any(_metadata_bool(metadata, key) for key in ("notion_projection_stale", "notion_tracker_stale", "notion_stale")):
        return "stale"
    return None


def reconciliation_findings(project: dict[str, Any], tasks: list[dict[str, Any]], pending_gates: list[dict[str, Any]], gates: Optional[list[dict[str, Any]]] = None) -> list[dict[str, Any]]:
    """Return deterministic project-completeness anomalies for Factory reconciliation.

    This is intentionally objective: it inspects Factory DB state, project-local
    artifact paths, Notion tracker metadata, gates, and task graph shape. It does
    not ask a worker to decide whether an incomplete project is implementation or
    administrative closure; it creates recovery work that can be executed if the
    project is resumed.
    """

    metadata = _metadata(project)
    if (
        str(project.get("status") or "") in {"completed", "accepted"}
        and not metadata.get("force_reconcile_completed")
        and not _has_unauthorized_completion_waivers(metadata)
    ):
        return []

    findings: list[dict[str, Any]] = []

    def add(code: str, message: str, **metadata: Any) -> None:
        if code not in RECONCILIATION_TASK_SPECS:
            raise ValueError(f"unknown reconciliation anomaly code: {code}")
        findings.append({"code": code, "message": message, "metadata": metadata})

    factory_dir, artifact_dir = _project_artifact_dir(project)
    strategy = _repository_strategy(project)
    if not factory_contracts.repository_strategy_is_complete(strategy):
        add(
            "missing_repository_strategy",
            "Missing or incomplete G0 Repository Strategy Gate metadata",
            missing_fields=strategy.get("missing_fields") or ["repo_scope"],
            repo_strategy=strategy,
        )
    notion_issue = _notion_projection_issue(metadata)
    if notion_issue:
        add(
            "missing_notion_project",
            f"Required human Notion PM projection is {notion_issue}; Factory DB + repo Markdown docs remain agent source of truth",
            notion_issue=notion_issue,
            notion_role="human_pm_projection_not_agent_truth",
            canonical_agent_truth="factory_db_plus_repo_markdown_docs",
            timing="template_page_before_visibility_and_increment_closures_post_action",
        )

    if factory_dir is None or not factory_dir.is_dir():
        add("missing_project_artifact_dir", f"Missing project-local Factory artifact directory: {artifact_dir}", artifact_dir=artifact_dir)
        missing_docs = list(FACTORY_REQUIRED_DOCS)
    else:
        missing_docs = [name for name in FACTORY_REQUIRED_DOCS if not (factory_dir / name).is_file()]
    if missing_docs and not _required_docs_explicitly_waived(metadata):
        add("missing_required_docs", "Missing required Factory methodology documents", missing_docs=missing_docs, artifact_dir=artifact_dir)
    elif factory_dir is not None and factory_dir.is_dir():
        missing_from_index = _docs_missing_from_documentation_index(factory_dir)
        if missing_from_index and not _required_docs_explicitly_waived(metadata):
            add(
                "docs_not_indexed",
                "Required Factory methodology documents are missing from DOCUMENTATION_INDEX.md",
                missing_from_index=missing_from_index,
                artifact_dir=artifact_dir,
            )

    repo_path = str(project.get("repo_path") or "").strip()
    if repo_path and factory_dir is not None and factory_dir.is_dir() and not _repo_commit_explicitly_waived(metadata):
        uncommitted_paths = _uncommitted_project_artifacts(Path(repo_path), artifact_dir)
        if uncommitted_paths:
            add(
                "uncommitted_project_artifacts",
                "Project-local Factory artifacts have uncommitted git changes",
                uncommitted_paths=uncommitted_paths,
                artifact_dir=artifact_dir,
            )

    non_reconciliation_tasks = [task for task in tasks if not _is_reconciliation_task(task)]
    if not non_reconciliation_tasks:
        add("missing_task_graph", "Factory DB has no canonical non-reconciliation task graph for this project")
    missing_phase_categories = _missing_mandatory_phase_categories(project, non_reconciliation_tasks)
    has_phase_reconciliation_coverage = any(_task_covers_reconciliation_anomaly(task, "missing_mandatory_factory_phases") for task in tasks)
    if missing_phase_categories and not has_phase_reconciliation_coverage:
        add(
            "missing_mandatory_factory_phases",
            "Factory task graph is missing mandatory canonical phases for runnable/UI sandbox delivery",
            missing_categories=missing_phase_categories,
            required_categories=_mandatory_phase_categories(project),
            contract="planning -> implementation -> independent review -> QA/browser -> authorized sandbox deploy -> post-sandbox browser/API verification -> delivery report",
        )

    if pending_gates:
        add(
            "pending_effective_gates",
            "Project has effective pending gates that must be resolved",
            pending_gates=[gate.get("gate_type") for gate in pending_gates],
        )

    latest_gate_status = _latest_gate_statuses(gates or [])
    delivery_passed = latest_gate_status.get("delivery") == "passed" or latest_gate_status.get("critical_readiness") == "passed"
    has_delivery_coverage = any(_task_covers_reconciliation_anomaly(task, "deliverable_unverified") for task in tasks)
    if not delivery_passed and not has_delivery_coverage:
        add("deliverable_unverified", "No passed delivery/critical readiness gate or pending delivery verification task exists")

    return findings


def ensure_reconciliation_tasks(project: dict[str, Any], findings: list[dict[str, Any]], tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ensure_runtime_schema()
    project_id = str(project.get("project_id") or "")
    created: list[dict[str, Any]] = []
    statements: list[str] = []
    terminal = ",".join(_q(status) for status in TERMINAL_TASK_STATUSES)
    for finding in findings:
        code = str(finding.get("code") or "")
        if not code or any(_task_covers_reconciliation_anomaly(task, code) for task in tasks):
            continue
        spec = RECONCILIATION_TASK_SPECS[code]
        task_id = f"{project_id}-reconcile-{code.replace('_', '-')}"
        metadata = {
            "source": "factory_reconciler",
            "factory_reconciliation_task": True,
            "reconciliation_anomaly": code,
            "finding": finding,
        }
        description = (
            f"Deterministic reconciliation task generated because: {finding.get('message')}.\n\n"
            "Do not close the project manually from UI state. Inspect Factory DB, project-local artifacts, Notion metadata, gates, and deliverable evidence; then record gates/evidence canonically."
        )
        reopen_note = f"\n\n[factory-reconciler] Reopened because the canonical anomaly recurred: {code}."
        statements.append(
            f"""
            INSERT INTO factory.tasks (
              task_id, project_id, lane_id, title, description, phase, status,
              owner_profile, reviewer_profile, engine, priority, dependencies,
              acceptance_criteria, evidence_required, evidence_status, risk_level,
              metadata, increment_key, increment_order, created_at, updated_at
            )
            VALUES (
              {_q(task_id)}, {_q(project_id)}, (SELECT lane_id FROM factory.lanes WHERE project_id={_q(project_id)} ORDER BY created_at, lane_id LIMIT 1),
              {_q(spec['title'])}, {_q(description)}, {_q(spec['phase'])}, 'todo',
              {_q(spec['owner'])}, {_q(spec['reviewer'])}, {_q(spec['engine'])}, {int(spec['priority'])}, '[]'::jsonb,
              {_j(spec['acceptance'])}, true, 'missing', {_q(str(project.get('risk_level') or 'medium'))},
              {_j(metadata)}, {_q('reconcile-' + code)}, {int(spec['priority'])}, now(), now()
            )
            ON CONFLICT (task_id) DO UPDATE SET
              status=CASE WHEN factory.tasks.status IN ({terminal}) THEN 'todo' ELSE factory.tasks.status END,
              evidence_status=CASE WHEN factory.tasks.status IN ({terminal}) THEN 'missing' ELSE factory.tasks.evidence_status END,
              result_summary=CASE
                WHEN factory.tasks.status IN ({terminal}) THEN COALESCE(factory.tasks.result_summary, '') || {_q(reopen_note)}
                ELSE factory.tasks.result_summary
              END,
              description=EXCLUDED.description,
              acceptance_criteria=EXCLUDED.acceptance_criteria,
              metadata=factory.tasks.metadata || EXCLUDED.metadata || {_j({'reopened_by': 'factory_reconciler', 'reopen_reason': 'canonical_anomaly_recurred'})},
              updated_at=now();
            INSERT INTO factory.events(project_id, lane_id, task_id, actor, event_type, message, metadata)
            VALUES ({_q(project_id)}, (SELECT lane_id FROM factory.lanes WHERE project_id={_q(project_id)} ORDER BY created_at, lane_id LIMIT 1), {_q(task_id)}, 'factory-reconciler', 'reconciliation_task_ensured', {_q(f'Reconciliation task ensured for anomaly {code}')}, {_j({'task_id': task_id, 'reconciliation_anomaly': code})});
            """
        )
        created.append({"task_id": task_id, "code": code})
    if statements:
        sql.psql("\n".join(statements), user=_user())
    return created


def cancel_resolved_reconciliation_tasks(project: dict[str, Any], findings: list[dict[str, Any]], tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Cancel open reconciliation tasks once their canonical anomaly is gone.

    Reconciliation tasks are recovery work, not permanent backlog. If the current
    deterministic findings no longer include the task's anomaly, leaving the row
    in ``todo`` makes a project appear planned/active even though there is no
    defect left to resolve. This reducer records the resolution and lets the
    normal reconciler compute terminal project status from the refreshed task set.
    """

    ensure_runtime_schema()
    project_id = str(project.get("project_id") or "")
    active_codes = {str(finding.get("code") or "") for finding in findings if finding.get("code")}
    resolved: list[dict[str, Any]] = []
    for task in tasks:
        if str(task.get("status") or "") in TERMINAL_TASK_STATUSES:
            continue
        anomaly = _task_reconciliation_anomaly(task)
        if not anomaly:
            continue
        code, source = anomaly
        if code in active_codes:
            continue
        resolved.append({"task_id": str(task.get("task_id") or ""), "code": code, "source": source})
    resolved = [item for item in resolved if item["task_id"]]
    if not resolved:
        return []

    terminal = ",".join(_q(status) for status in TERMINAL_TASK_STATUSES)
    task_ids = ",".join(_q(item["task_id"]) for item in resolved)
    note = "\n\n[factory-reconciler] Reconciliation anomaly resolved; task auto-cancelled."
    sql.psql(
        f"""
        WITH cancelled AS (
          UPDATE factory.tasks
          SET status='cancelled',
              evidence_status='not_required',
              result_summary=COALESCE(result_summary, '') || {_q(note)},
              metadata = metadata || {_j({'cancelled_by': 'factory_reconciler', 'cancel_reason': 'resolved_reconciliation_anomaly'})},
              updated_at=now()
          WHERE project_id={_q(project_id)}
            AND task_id IN ({task_ids})
            AND status NOT IN ({terminal})
          RETURNING project_id, lane_id, task_id, metadata
        )
        INSERT INTO factory.events(project_id, lane_id, task_id, actor, event_type, message, metadata)
        SELECT project_id, lane_id, task_id, 'factory-reconciler', 'resolved_reconciliation_task_cancelled',
               'Resolved reconciliation task auto-cancelled',
               jsonb_build_object('task_id', task_id, 'reconciliation_anomaly', metadata->>'reconciliation_anomaly')
        FROM cancelled;
        """,
        user=_user(),
    )
    return resolved


def critical_readiness_findings(project_id: str, *, gate_evidence: Optional[dict[str, Any]] = None) -> list[str]:
    project = _project(project_id)
    if not project:
        return [f"project {project_id} is not visible in Agent Core Postgres"]
    risk = str(project.get("risk_level") or "").lower()
    critical_project = risk in CRITICAL_RISK_LEVELS

    findings: list[str] = []
    raw_metadata = project.get("metadata")
    metadata: dict[str, Any] = raw_metadata if isinstance(raw_metadata, dict) else {}
    repo_path = str(project.get("repo_path") or "").strip()
    artifact_dir = metadata.get("artifact_dir") or f"factory/projects/{project_id}"
    factory_dir = Path(repo_path).expanduser() / str(artifact_dir) if repo_path else None

    if critical_project:
        notion_issue = _notion_projection_issue(metadata)
        strategy = _repository_strategy(project)
        if not factory_contracts.repository_strategy_is_complete(strategy):
            missing = ", ".join(strategy.get("missing_fields") or ["repo_scope"])
            findings.append(f"missing G0 repository strategy metadata: {missing}")
        if notion_issue:
            findings.append(f"required Notion PM tracker is {notion_issue}")

        if not factory_dir or not factory_dir.is_dir():
            findings.append(f"missing project-local factory documentation directory: {artifact_dir}")
        else:
            document_blockers = [] if _required_docs_explicitly_waived(metadata) else _g1_document_blockers(project)
            if document_blockers:
                findings.append(
                    "g1 documentary readiness blockers: "
                    + ", ".join(f"{row['file_name']}({','.join(key for key in ('exists', 'indexed', 'committed', 'validated', 'reviewed') if not row.get(key))})" for row in document_blockers)
                )
            if repo_path and not _repo_commit_explicitly_waived(metadata):
                uncommitted_paths = _uncommitted_project_artifacts(Path(repo_path), str(artifact_dir))
                if uncommitted_paths:
                    findings.append("uncommitted project-local factory artifacts: " + ", ".join(uncommitted_paths))

        self_approved = sql.rows(
            f"""
            SELECT task_id, title, owner_profile, reviewer_profile
            FROM factory.tasks
            WHERE project_id={_q(project_id)}
              AND owner_profile IS NOT NULL
              AND owner_profile = reviewer_profile
            ORDER BY task_id
            """,
            user=_user(),
        )
        if self_approved:
            findings.append(f"{len(self_approved)} task(s) have no independent reviewer")
        if metadata.get("dashboard_visible") is False:
            findings.append("project is explicitly hidden from dashboard")

    if gate_evidence is not None:
        findings.extend(_delivery_evidence_findings(project, gate_evidence))
    return findings


def _document_status_snapshot(project_id: str) -> dict[str, Any]:
    """Return delivery-gate evidence proving G1 doc readiness at decision time."""

    project = _project(project_id)
    if not project:
        return {"available": False, "project_id": project_id, "reason": "project_not_found"}
    statuses = project_document_status(project)
    blockers = [row for row in statuses if row.get("category") == "g1_required" and row.get("blocking")]
    return {
        "available": True,
        "project_id": project_id,
        "docs_ready": not blockers,
        "document_count": len(statuses),
        "g1_document_count": sum(1 for row in statuses if row.get("category") == "g1_required"),
        "blocking_count": len(blockers),
        "blocking_documents": [row.get("file_name") for row in blockers],
        "documents": statuses,
    }


def record_gate(project_id: str, gate_type: str, status: str, *, lane_id: Optional[str] = None, task_id: Optional[str] = None, reviewer: Optional[str] = None, evidence: Optional[dict[str, Any]] = None, notes: Optional[str] = None, **_: Any) -> dict[str, Any]:
    ensure_runtime_schema()
    gate = str(gate_type or "").strip()
    state = str(status or "").strip()
    gate_evidence = dict(evidence or {})
    if gate in {"delivery", "critical_readiness"}:
        gate_evidence.setdefault("document_status_snapshot", _document_status_snapshot(project_id))
    if gate in {"delivery", "critical_readiness"} and state == "passed":
        blockers = critical_readiness_findings(project_id, gate_evidence=gate_evidence)
        if blockers:
            raise ValueError("critical readiness gate blocked: " + "; ".join(blockers))

    row = sql.statement_one(f"""
      INSERT INTO factory.gates (project_id, lane_id, task_id, gate_type, status, reviewer, evidence, notes, timestamp)
      VALUES ({_q(project_id)}, {_q(lane_id)}, {_q(task_id)}, {_q(gate)}, {_q(state)}, {_q(reviewer)}, {_j(gate_evidence)}, {_q(notes)}, now())
      RETURNING gate_id, project_id, status, timestamp
    """, user=_user())
    gate_id = row["gate_id"] if row else None
    if gate_id and state in TERMINAL_GATE_STATUSES:
        sql.psql(
            f"""
            UPDATE factory.gates
            SET status='superseded',
                evidence = evidence || {_j({'superseded_by_gate_id': gate_id, 'superseded_by_status': state})}
            WHERE project_id={_q(project_id)}
              AND gate_type={_q(gate)}
              AND status='pending'
              AND gate_id <> {int(gate_id)}
              AND timestamp <= (SELECT timestamp FROM factory.gates WHERE gate_id={int(gate_id)});
            """,
            user=_user(),
        )
    sql.psql(f"INSERT INTO factory.events(project_id, lane_id, task_id, actor, event_type, message, metadata) VALUES ({_q(project_id)}, {_q(lane_id)}, {_q(task_id)}, {_q(reviewer or 'factory-orchestrator')}, {_q('gate_' + state)}, {_q(f'{gate} gate {state}')}, {_j({'gate_id': gate_id})});", user=_user())
    reconcile_project(project_id)
    return {"gate_id": gate_id, "project_id": project_id, "status": state}


def update_project_metadata(project_id: str, metadata: dict[str, Any]) -> None:
    ensure_runtime_schema()
    sql.psql(
        f"UPDATE factory.projects SET metadata = metadata || {_j(metadata)}, updated_at = now() WHERE project_id={_q(project_id)};",
        user=_user(),
    )


_NOTION_PAGE_ID_RE = re.compile(r"^[0-9a-fA-F]{32}$|^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def _normalize_notion_page_id(page_id: str) -> str:
    compact = page_id.replace("-", "").lower()
    return f"{compact[:8]}-{compact[8:12]}-{compact[12:16]}-{compact[16:20]}-{compact[20:]}"


def _validate_notion_tracker_metadata(*, page_id: str | None, url: str | None, page_title: str | None = None) -> dict[str, Any]:
    """Validate canonical project-specific Notion tracker metadata.

    Factory DB is the source of truth; this validates the DB metadata written by
    the Notion side-effect path and returns the exact fields used by reconciler
    readback. A shared template URL is not enough: at least one project-specific
    page identifier or URL is required.
    """

    clean_page_id = str(page_id or "").strip()
    clean_url = str(url or "").strip()
    if not clean_page_id and not clean_url:
        raise ValueError("notion tracker page_id or url is required")
    if clean_page_id and not _NOTION_PAGE_ID_RE.match(clean_page_id):
        raise ValueError("notion tracker page_id must be a 32-char or UUID hex Notion page id")
    if clean_url and not (clean_url.startswith("https://") or clean_url.startswith("http://")):
        raise ValueError("notion tracker url must be http(s)")
    metadata: dict[str, Any] = {
        "notion_tracker_linked_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "notion_tracker_source": "hermes factory project link-notion",
    }
    if clean_page_id:
        metadata["notion_tracker_page_id"] = _normalize_notion_page_id(clean_page_id)
    if clean_url:
        metadata["notion_tracker_url"] = clean_url
    if page_title and str(page_title).strip():
        metadata["notion_tracker_title"] = str(page_title).strip()
    return metadata


def link_notion_tracker(
    project_id: str,
    *,
    page_id: str | None = None,
    url: str | None = None,
    page_title: str | None = None,
    actor: str = "factory-reporter",
) -> dict[str, Any]:
    """Canonical Factory DB write/readback path for a project Notion PM tracker."""

    ensure_runtime_schema()
    pid = str(project_id or "").strip()
    if not pid:
        raise ValueError("project_id is required")
    if not _project(pid):
        raise ValueError(f"Factory project not found: {pid}")
    actor_name = str(actor or "factory-reporter").strip() or "factory-reporter"
    metadata = _validate_notion_tracker_metadata(page_id=page_id, url=url, page_title=page_title)
    metadata["notion_tracker_linked_by"] = actor_name
    sql.psql(
        f"""
        UPDATE factory.projects
        SET metadata = metadata || {_j(metadata)}, updated_at=now()
        WHERE project_id={_q(pid)};
        INSERT INTO factory.events(project_id, actor, event_type, message, metadata)
        VALUES ({_q(pid)}, {_q(actor_name)}, 'notion_tracker_linked', 'Project-specific Notion PM tracker linked and readback requested', {_j(metadata)});
        """,
        user=_user(),
    )
    readback_row = sql.one(f"SELECT metadata FROM factory.projects WHERE project_id={_q(pid)}", user=_user()) or {}
    readback = readback_row.get("metadata") if isinstance(readback_row, dict) and isinstance(readback_row.get("metadata"), dict) else {}
    expected_page = metadata.get("notion_tracker_page_id")
    expected_url = metadata.get("notion_tracker_url")
    if expected_page and readback.get("notion_tracker_page_id") != expected_page:
        raise ValueError("notion tracker metadata readback mismatch: page_id not persisted")
    if expected_url and readback.get("notion_tracker_url") != expected_url:
        raise ValueError("notion tracker metadata readback mismatch: url not persisted")
    reconcile = reconcile_project(pid)
    return {
        "action": "link-notion",
        "project_id": pid,
        "readback": {
            "notion_tracker_page_id": readback.get("notion_tracker_page_id"),
            "notion_tracker_url": readback.get("notion_tracker_url"),
            "notion_tracker_title": readback.get("notion_tracker_title"),
        },
        "reconcile": reconcile,
    }


def _notion_increment_closure_checkpoint(
    *,
    task_id: str,
    project_id: str,
    lane_id: Any,
    status: str,
    summary: str,
    evidence: dict[str, Any],
    actor: str,
    queued: bool = True,
) -> dict[str, Any]:
    return {
        "queued": queued,
        "notion_role": "human_pm_projection_not_agent_truth",
        "timing": "post_action_increment_closure",
        "event_type": "notion_increment_closure_checkpoint" if queued else "notion_increment_closure_synced",
        "source": "factory_task_close",
        "project_id": project_id,
        "lane_id": lane_id,
        "task_id": task_id,
        "status": status,
        "summary": summary,
        "evidence": evidence,
        "closed_by": actor,
        "canonical_pre_action_docs": "Factory DB + repo Markdown docs are the agent source of truth; Notion is the post-action human PM projection.",
        "notion_sync_required": queued,
    }


def _task_close_completes_notion_sync(task_id: str, evidence: dict[str, Any]) -> bool:
    """Return True when the task being closed is the Notion projection repair itself.

    Normal increment closures must mark the PM projection stale so the reporter
    updates Notion after action. The reconciliation/reporting task that performs
    that sync is different: closing it must clear the stale flag, otherwise
    `close_task()` immediately recreates the same reconciliation anomaly.
    """

    if evidence.get("notion_sync_completed") is True:
        return True
    if "reconcile-missing-notion" not in str(task_id or ""):
        return False
    return any(
        evidence.get(key)
        for key in (
            "notion_tracker_page_id",
            "notion_tracker_url",
            "notion_page_id",
            "notion_page",
            "notion_url",
        )
    )


def close_task(
    task_id: str,
    *,
    status: str = "done",
    result_summary: str,
    evidence: Optional[dict[str, Any]] = None,
    actor: str = "factory-orchestrator",
    reconcile: bool = True,
) -> dict[str, Any]:
    """Canonically close a Factory task/increment with auditable evidence."""

    ensure_runtime_schema()
    tid = str(task_id or "").strip()
    if not tid:
        raise ValueError("task_id is required")
    final_status = str(status or "done").strip().lower()
    if final_status not in TERMINAL_TASK_STATUSES:
        raise ValueError(f"unsupported terminal task status: {status}")
    summary = str(result_summary or "").strip()
    if not summary:
        raise ValueError("result_summary is required")
    actor_name = str(actor or "factory-orchestrator").strip() or "factory-orchestrator"
    evidence_payload = dict(evidence or {})
    evidence_state = "not_required" if final_status in {"cancelled", "superseded"} else "present"
    run_status = "cancelled" if final_status in {"cancelled", "superseded"} else "succeeded"
    metadata = {
        "closed_by": actor_name,
        "closure_source": "factory_task_close",
        "task_close_status": final_status,
        "evidence": evidence_payload,
    }
    row = sql.statement_one(
        f"""
        UPDATE factory.tasks
        SET status={_q(final_status)},
            evidence_status={_q(evidence_state)},
            result_summary={_q(summary)},
            finished_at=now(),
            metadata = metadata || {_j(metadata)},
            updated_at=now()
        WHERE task_id={_q(tid)}
        RETURNING project_id, lane_id, task_id, status
        """,
        user=_user(),
    )
    if not row:
        raise ValueError(f"Factory task not found: {tid}")
    project_id = str(row.get("project_id") or "")
    lane_id = row.get("lane_id")
    notion_sync_completed = _task_close_completes_notion_sync(tid, evidence_payload)
    notion_checkpoint = _notion_increment_closure_checkpoint(
        task_id=tid,
        project_id=project_id,
        lane_id=lane_id,
        status=final_status,
        summary=summary,
        evidence=evidence_payload,
        actor=actor_name,
        queued=not notion_sync_completed,
    )
    if notion_sync_completed:
        synced_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        project_notion_metadata = {
            "notion_projection_stale": False,
            "notion_sync_required": False,
            "notion_last_increment_closure_synced_at": synced_at,
            "notion_tracker_last_synced_at": synced_at,
            "notion_last_increment_closure": notion_checkpoint,
        }
        notion_event_type = "notion_increment_closure_synced"
        notion_event_message = f"Post-action Notion PM projection synced by {tid}"
    else:
        project_notion_metadata = {
            "notion_projection_stale": True,
            "notion_sync_required": True,
            "notion_last_increment_closure": notion_checkpoint,
        }
        notion_event_type = "notion_increment_closure_checkpoint"
        notion_event_message = f"Post-action Notion PM projection checkpoint queued for {tid}"
    sql.psql(
        f"""
        UPDATE factory.task_runs
        SET status={_q(run_status)},
            finished_at=now(),
            heartbeat_at=now(),
            output_summary={_q(summary)},
            evidence = evidence || {_j(evidence_payload)},
            metadata = metadata || {_j({'closed_by': actor_name, 'closure_source': 'factory_task_close'})}
        WHERE task_id={_q(tid)}
          AND status IN ('queued','running');

        UPDATE factory.projects
        SET metadata = metadata || {_j(project_notion_metadata)},
            updated_at=now()
        WHERE project_id={_q(project_id)};

        INSERT INTO factory.events(project_id, lane_id, task_id, actor, event_type, message, metadata)
        VALUES ({_q(project_id)}, {_q(lane_id)}, {_q(tid)}, {_q(actor_name)}, 'task_closed', {_q(f'Task {tid} closed as {final_status}')}, {_j({'status': final_status, 'evidence': evidence_payload, 'result_summary': summary})});

        INSERT INTO factory.events(project_id, lane_id, task_id, actor, event_type, message, metadata)
        VALUES ({_q(project_id)}, {_q(lane_id)}, {_q(tid)}, {_q(actor_name)}, {_q(notion_event_type)}, {_q(notion_event_message)}, {_j(notion_checkpoint)});
        """,
        user=_user(),
    )
    reconciled = reconcile_project(project_id) if reconcile and project_id else None
    return {
        "action": "task_close",
        "project_id": project_id,
        "task_id": tid,
        "status": final_status,
        "evidence_status": evidence_state,
        "notion_post_action": notion_checkpoint,
        "reconcile": reconciled,
    }


def close_project(
    project_id: str,
    *,
    reason: str,
    closure_type: str = "administrative",
    superseded_by_project_id: Optional[str] = None,
    actor: str = "factory-orchestrator",
) -> dict[str, Any]:
    """Canonically close a Factory project without pretending it delivered product work.

    This is the administrative/supersession path for legacy, duplicate, deferred,
    or absorbed projects. It intentionally does not enable autonomy. Open tasks are
    cancelled with evidence marked not required, lanes and project are completed,
    and a closure gate/event preserve why the project is no longer runnable.
    """

    ensure_runtime_schema()
    pid = str(project_id or "").strip()
    if not pid:
        raise ValueError("project_id is required")
    reason_text = str(reason or "").strip()
    if not reason_text:
        raise ValueError("closure reason is required")
    kind = str(closure_type or "administrative").strip().lower().replace("-", "_")
    allowed = {"administrative", "superseded", "deferred", "duplicate", "cancelled"}
    if kind not in allowed:
        raise ValueError(f"unsupported closure_type: {closure_type}")
    final_status = factory_contracts.ProjectStatus.COMPLETED.value if kind != "cancelled" else factory_contracts.ProjectStatus.CANCELLED.value
    closed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    closure_metadata = {
        "administrative_closure": True,
        "closure_type": kind,
        "closure_reason": reason_text,
        "closed_by": actor,
        "closed_at": closed_at,
        "delivery_claim": "administrative_closure_not_product_delivery",
        "autonomous_enabled": False,
        "reconciliation_required": False,
        "reconciliation_anomalies": [],
    }
    if superseded_by_project_id:
        closure_metadata["superseded_by_project_id"] = superseded_by_project_id
        closure_metadata["absorbed_into_project_id"] = superseded_by_project_id
    active_runs = sql.rows(
        f"SELECT run_id FROM factory.task_runs WHERE project_id={_q(pid)} AND status IN ('queued','running') ORDER BY started_at",
        user=_user(),
    )
    monitor_evidence = {
        "monitor_evidence": "project_closure_finalized_active_runs",
        "stale_task_runs_cancelled": [str(row.get("run_id")) for row in active_runs],
        "active_run_count_before_close": len(active_runs),
    }
    closure_metadata["monitor_evidence"] = monitor_evidence
    terminal_tasks = ",".join(_q(status) for status in TERMINAL_TASK_STATUSES)
    event_payload = dict(closure_metadata)
    gate_row = sql.statement_one(
        f"""
        INSERT INTO factory.gates (project_id, gate_type, status, reviewer, evidence, notes, timestamp)
        VALUES ({_q(pid)}, 'closure', 'passed', {_q(actor)}, {_j(event_payload)}, {_q(reason_text)}, now())
        RETURNING gate_id
        """,
        user=_user(),
    )
    gate_id = gate_row.get("gate_id") if gate_row else None
    sql.psql(
        f"""
        UPDATE factory.tasks
        SET status='cancelled',
            evidence_status='not_required',
            result_summary={_q('Cancelled by canonical project closure: ' + reason_text)},
            metadata = metadata || {_j({'administrative_closure': True, 'closure_type': kind, 'closure_reason': reason_text, 'superseded_by_project_id': superseded_by_project_id})},
            updated_at=now()
        WHERE project_id={_q(pid)}
          AND status NOT IN ({terminal_tasks});

        UPDATE factory.task_runs
        SET status='cancelled',
            finished_at=now(),
            heartbeat_at=now(),
            output_summary={_q('Cancelled by canonical project closure: ' + reason_text)},
            metadata = metadata || {_j({'closed_by': actor, 'closure_source': 'factory_project_close', **monitor_evidence})}
        WHERE project_id={_q(pid)}
          AND status IN ('queued','running');

        UPDATE factory.lanes
        SET status='completed', updated_at=now()
        WHERE project_id={_q(pid)};

        UPDATE factory.projects
        SET status={_q(final_status)},
            autonomous_enabled=false,
            paused_at=NULL,
            metadata = metadata || {_j(closure_metadata)},
            last_reconciled_at=now(),
            updated_at=now()
        WHERE project_id={_q(pid)};

        INSERT INTO factory.events(project_id, actor, event_type, message, metadata)
        VALUES ({_q(pid)}, {_q(actor)}, 'project_closed', {_q('Factory project closed by canonical administrative closure')}, {_j({'gate_id': gate_id, **event_payload})});

        INSERT INTO factory.events(project_id, actor, event_type, message, metadata)
        VALUES ({_q(pid)}, {_q(actor)}, 'gate_passed', 'closure gate passed', {_j({'gate_id': gate_id, 'gate_type': 'closure'})});
        """,
        user=_user(),
    )
    return {
        "action": "close",
        "project_id": pid,
        "status": final_status,
        "closure_type": kind,
        "superseded_by_project_id": superseded_by_project_id,
        "gate_id": gate_id,
    }


def _status_counts(tasks: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for task in tasks:
        status = str(task.get("status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
    return counts


def _project_autonomous_enabled(project: dict[str, Any], metadata: dict[str, Any] | None = None) -> bool:
    metadata = metadata if metadata is not None else _metadata(project)
    return bool(project.get("autonomous_enabled") or metadata.get("autonomous_enabled"))


def _project_status_forces_autonomy_off(status: str | None) -> bool:
    status_value = str(status or "").lower()
    return status_value in TERMINAL_PROJECT_STATUSES or status_value == MANUAL_ATTENTION_STATUS


def _project_reconcile_forces_autonomy_off(old_status: str | None, new_status: str | None) -> bool:
    return _project_status_forces_autonomy_off(old_status) or _project_status_forces_autonomy_off(new_status)


def _should_auto_resume_after_reconcile(old_status: str | None, new_status: str | None) -> bool:
    return str(new_status or "").lower() == "completed" and str(old_status or "").lower() != "completed"


def _has_runnable_autonomous_work(tasks: list[dict[str, Any]]) -> bool:
    runnable_statuses = {"todo", "ready", "rework"} | IN_FLIGHT_TASK_STATUSES
    return any(str(task.get("status") or "") in runnable_statuses for task in tasks)


def _has_active_increment(tasks: list[dict[str, Any]]) -> bool:
    return any(str(t.get("status") or "") in ACTIVE_TASK_STATUSES for t in tasks)


def _has_in_flight_increment(tasks: list[dict[str, Any]]) -> bool:
    """Return True when a task has a worker/reviewer currently in flight.

    A task in ``rework`` is an active increment for project status and for
    blocking later increments, but it is also runnable: the orchestrator must be
    able to hand it back to the owner. Treating rework as in-flight makes it an
    absorbing state with no autonomous recovery path.
    """

    return any(str(t.get("status") or "") in IN_FLIGHT_TASK_STATUSES for t in tasks)


def _next_runnable_task(project_id: str) -> dict[str, Any] | None:
    tasks = _tasks(project_id)
    if _has_active_increment(tasks):
        return None
    terminal = ",".join(_q(s) for s in TERMINAL_TASK_STATUSES)
    candidates = sql.rows(
        f"""
        SELECT * FROM factory.tasks
        WHERE project_id={_q(project_id)}
          AND status IN ('todo', 'ready')
          AND NOT EXISTS (
            SELECT 1 FROM jsonb_array_elements_text(factory.tasks.dependencies) dep
            WHERE dep NOT IN (SELECT task_id FROM factory.tasks WHERE project_id={_q(project_id)} AND status IN ({terminal}))
          )
        ORDER BY priority, created_at
        LIMIT 1
        """,
        user=_user(),
    )
    return _normalize(candidates[0]) if candidates else None


def reconcile_project(project_id: str) -> dict[str, Any]:
    ensure_runtime_schema()
    tasks = _tasks(project_id)
    project = _project(project_id)
    if not project:
        raise ValueError(f"Factory project not found: {project_id}")
    metadata = _metadata(project)
    pending_gates = _active_pending_gates(project_id)
    latest_gates = _latest_gate_rows(project_id)
    findings = reconciliation_findings(project, tasks, pending_gates, latest_gates)
    created_reconciliation_tasks = ensure_reconciliation_tasks(project, findings, tasks) if findings else []
    cancelled_reconciliation_tasks = cancel_resolved_reconciliation_tasks(project, findings, tasks)
    if created_reconciliation_tasks or cancelled_reconciliation_tasks:
        tasks = _tasks(project_id)
    counts = _status_counts(tasks)
    active_runs = sql.rows(f"SELECT run_id FROM factory.task_runs WHERE project_id={_q(project_id)} AND status IN ('queued','running')", user=_user())
    if str(project.get("status") or "") == MANUAL_ATTENTION_STATUS or metadata.get("manual_attention_required"):
        new_status = MANUAL_ATTENTION_STATUS
    elif str(project.get("status")) == "paused" or metadata.get("autonomous_enabled") is False and project.get("paused_at"):
        new_status = "paused"
    elif active_runs or any(status in counts for status in ACTIVE_TASK_STATUSES):
        new_status = "active"
    elif _project_autonomous_enabled(project, metadata) and _has_runnable_autonomous_work(tasks):
        # A documentation/delivery hold can coexist with runnable reconciliation
        # tasks.  While autonomy is enabled, keep the project dispatchable until
        # those tasks are actually claimed and resolved; only then can it become
        # a true delivery_hold waiting on Jean/UI or external documentation.
        new_status = "active"
    elif any(status in counts for status in ("blocked", "review_pending_human")):
        new_status = DELIVERY_HOLD_STATUS if _all_blocked_work_is_documentation_hold(tasks) else "blocked"
    elif tasks and not any(str(t.get("status") or "") not in TERMINAL_TASK_STATUSES for t in tasks) and not pending_gates and not findings:
        new_status = DELIVERY_HOLD_STATUS if metadata.get("closure_pending_human_ui") else "completed"
    elif findings and _all_open_work_is_reconciliation(tasks) and not active_runs:
        # Documentation/PM reconciliation must keep the project visibly open,
        # but it is not a technical blocker and should not present as a blocked
        # engineering increment. Jean can close it explicitly from the UI once
        # the document side-effect is generated/reconciled.
        new_status = DELIVERY_HOLD_STATUS
    elif findings:
        # Incomplete projects should not remain "active" solely because the
        # autonomous flag is true. Planned + autonomous_enabled=true is still
        # claimable by the orchestrator tick, but the UI no longer shows an
        # active project with no canonical recovery work.
        new_status = "planned"
    elif metadata.get("autonomous_enabled"):
        new_status = "active"
    elif tasks:
        new_status = "planned" if str(project.get("status") or "") not in {"active", "blocked"} else str(project.get("status"))
    else:
        new_status = "intake"
    finding_codes = [str(finding.get("code")) for finding in findings]
    force_autonomy_off = _project_reconcile_forces_autonomy_off(str(project.get("status") or ""), new_status)
    reconcile_metadata = {'reconciliation_required': bool(findings), 'reconciliation_anomalies': finding_codes}
    if force_autonomy_off:
        reconcile_metadata.update({
            'autonomous_enabled': False,
            'autonomy_disabled_reason': f'project_status_{new_status}',
        })
    autonomous_sql = "false" if force_autonomy_off else "autonomous_enabled"
    sql.psql(
        f"""
        UPDATE factory.projects
        SET status={_q(new_status)},
            autonomous_enabled={autonomous_sql},
            metadata = metadata || {_j(reconcile_metadata)},
            last_reconciled_at=now(), updated_at=now()
        WHERE project_id={_q(project_id)};
        UPDATE factory.lanes
        SET status = CASE WHEN { _q(new_status) } IN ('active','completed','blocked','manual_attention','paused','planned','intake','delivery_hold') THEN { _q(new_status) } ELSE status END,
            updated_at=now()
        WHERE project_id={_q(project_id)};
        INSERT INTO factory.events(project_id, actor, event_type, message, metadata)
        VALUES ({_q(project_id)}, 'factory-reconciler', 'project_reconciled', {_q(f'Project reconciled as {new_status}')}, {_j({'task_counts': counts, 'pending_gates': len(pending_gates), 'active_runs': len(active_runs), 'anomalies': finding_codes, 'reconciliation_tasks_created': created_reconciliation_tasks, 'reconciliation_tasks_cancelled': cancelled_reconciliation_tasks, 'autonomy_disabled': force_autonomy_off})});
        """,
        user=_user(),
    )
    auto_resumed = _auto_resume_next_guard_queued_project(project_id) if _should_auto_resume_after_reconcile(str(project.get("status") or ""), new_status) else None
    return {
        "project_id": project_id,
        "status": new_status,
        "task_counts": counts,
        "pending_gates": len(pending_gates),
        "active_runs": len(active_runs),
        "anomalies": finding_codes,
        "reconciliation_tasks_created": len(created_reconciliation_tasks),
        "reconciliation_tasks_cancelled": len(cancelled_reconciliation_tasks),
        "auto_resumed_project_id": auto_resumed.get("project_id") if auto_resumed else None,
    }


def _pause_other_autonomous_projects(active_project_id: str) -> list[dict[str, Any]]:
    """Pause runnable autonomous sibling projects when one project is resumed.

    Jean's current Factory operating mode is single-project autonomy: one
    project may be dispatchable at a time while the methodology is being
    hardened.  Projects paused by this guard are explicitly marked as a queue so
    the orchestrator may resume one later after the active project completes.
    Delivery/hold/completed/cancelled projects are intentionally not touched.
    """

    ensure_runtime_schema()
    paused = _normalize_rows(sql.json_query(
        f"""
        WITH updated AS (
            UPDATE factory.projects
            SET status='paused',
                autonomous_enabled=false,
                paused_at=now(),
                metadata = metadata || {_j({
                    'autonomous_enabled': False,
                    'paused_by_single_active_guard': True,
                    'single_active_guard_queue': True,
                    'single_active_guard_paused_for': active_project_id,
                })},
                updated_at=now()
            WHERE project_id<>{_q(active_project_id)}
              AND autonomous_enabled IS TRUE
              AND status IN ('active','planned','intake','blocked')
            RETURNING project_id
        ), lane_update AS (
            UPDATE factory.lanes l
            SET status='paused', updated_at=now()
            FROM updated u
            WHERE l.project_id=u.project_id
              AND l.status IN ('active','planned','intake','blocked')
            RETURNING l.project_id
        ), event_insert AS (
            INSERT INTO factory.events(project_id, actor, event_type, message, metadata)
            SELECT project_id, 'factory-orchestrator', 'single_active_guard_pause',
                   'Paused by single-active Factory guard while another project was resumed',
                   {_j({'active_project_id': active_project_id, 'queued_for_auto_resume': True})}
            FROM updated
            RETURNING 1
        )
        SELECT COALESCE(jsonb_agg(to_jsonb(updated)), '[]'::jsonb)::text FROM updated;
        """,
        user=_user(),
    ) or [])
    return paused


def _auto_resume_next_guard_queued_project(completed_project_id: str) -> dict[str, Any] | None:
    """Resume the next project queued by the single-active guard after completion.

    Only projects explicitly paused by `_pause_other_autonomous_projects` are
    eligible. Each candidate must pass the same resume preflight as the UI/CLI;
    a blocked/manual project must not steal the autonomous slot while the next
    runnable project waits behind it.
    """

    ensure_runtime_schema()
    rows = sql.rows(
        f"""
        SELECT project_id
        FROM factory.projects
        WHERE project_id<>{_q(completed_project_id)}
          AND status='paused'
          AND COALESCE((metadata->>'paused_by_single_active_guard')::boolean, false) IS TRUE
          AND COALESCE((metadata->>'single_active_guard_queue')::boolean, false) IS TRUE
        ORDER BY updated_at, started_at, project_id
        LIMIT 10
        """,
        user=_user(),
    )
    for row in rows:
        next_project_id = str(row["project_id"])
        result = control_action(next_project_id, "resume")
        if result.get("resume_blocked") or result.get("dispatch_allowed") is False:
            sql.psql(
                f"""
                INSERT INTO factory.events(project_id, actor, event_type, message, metadata)
                VALUES ({_q(completed_project_id)}, 'factory-orchestrator', 'single_active_guard_auto_resume_skipped',
                        {_q(f'Skipped queued Factory project {next_project_id}; resume preflight blocked')},
                        {_j({'candidate_project_id': next_project_id, 'resume_blocked_reason': result.get('resume_blocked_reason')})});
                """,
                user=_user(),
            )
            continue
        sql.psql(
            f"""
            INSERT INTO factory.events(project_id, actor, event_type, message, metadata)
            VALUES ({_q(completed_project_id)}, 'factory-orchestrator', 'single_active_guard_auto_resume_next',
                    {_q(f'Auto-resumed queued Factory project {next_project_id} after active project completion')},
                    {_j({'resumed_project_id': next_project_id})});
            """,
            user=_user(),
        )
        return result
    return None


def resume_project(project_id: str) -> dict[str, Any]:
    ensure_runtime_schema()
    sql.psql(
        f"""
        UPDATE factory.projects
        SET status='active', autonomous_enabled=true, paused_at=NULL,
            metadata = (metadata || {_j({'autonomous_enabled': True, 'autonomy_mode': 'incremental_single_active'})})
                - 'paused_by_single_active_guard'
                - 'single_active_guard_queue'
                - 'single_active_guard_paused_for'
                - 'manual_attention_required'
                - 'manual_attention_reason'
                - 'manual_attention_blockers',
            updated_at=now()
        WHERE project_id={_q(project_id)};
        UPDATE factory.lanes SET status='active', updated_at=now() WHERE project_id={_q(project_id)} AND status IN ('planned','paused','intake','manual_attention');
        INSERT INTO factory.events(project_id, actor, event_type, message, metadata)
        VALUES ({_q(project_id)}, 'factory-orchestrator', 'autonomous_resume', 'Autonomous Factory execution resumed', {_j({'single_active_increment': True, 'single_active_project_guard': True})});
        """,
        user=_user(),
    )
    paused_siblings = _pause_other_autonomous_projects(project_id)
    next_task = _next_runnable_task(project_id)
    if next_task:
        sql.psql(
            f"UPDATE factory.tasks SET status='ready', updated_at=now() WHERE task_id={_q(next_task['task_id'])} AND status='todo';",
            user=_user(),
        )
    result = reconcile_project(project_id)
    result["next_task_id"] = next_task.get("task_id") if next_task else None
    result["paused_sibling_projects"] = [str(row.get("project_id")) for row in paused_siblings]
    return result


def pause_project(project_id: str, *, reason: str = "user_paused") -> dict[str, Any]:
    ensure_runtime_schema()
    pause_metadata = {
        "autonomous_enabled": False,
        "manual_pause": True,
        "pause_kind": "user_decision",
        "pause_reason": reason,
        "paused_by": "factory-orchestrator",
        "reactivation_policy": "resolve_state_preflight_before_dispatch",
    }
    sql.psql(
        f"""
        UPDATE factory.projects
        SET status='paused', autonomous_enabled=false, paused_at=now(),
            metadata = (metadata || {_j(pause_metadata)})
                - 'paused_by_single_active_guard'
                - 'single_active_guard_queue'
                - 'single_active_guard_paused_for',
            updated_at=now()
        WHERE project_id={_q(project_id)};
        UPDATE factory.lanes SET status='paused', updated_at=now() WHERE project_id={_q(project_id)} AND status='active';
        INSERT INTO factory.events(project_id, actor, event_type, message, metadata)
        VALUES ({_q(project_id)}, 'factory-orchestrator', 'autonomous_pause', 'Autonomous Factory execution paused by user/operator decision', {_j(pause_metadata)});
        """,
        user=_user(),
    )
    return {"project_id": project_id, "status": "paused", "pause_kind": "user_decision", "pause_reason": reason}


def _task_blocker_text(task: dict[str, Any]) -> str:
    return "\n".join(str(task.get(key) or "") for key in ("title", "description", "result_summary")).lower()


def _parse_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if not value:
        return None
    try:
        text = str(value).replace("Z", "+00:00")
        parsed = datetime.fromisoformat(text)
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _age_minutes(value: Any, *, now: datetime | None = None) -> float | None:
    parsed = _parse_datetime(value)
    if not parsed:
        return None
    current = now or datetime.now(timezone.utc)
    return max(0.0, (current - parsed).total_seconds() / 60.0)


def _manual_takeover_dispatch_filter(project_alias: str = "p") -> str:
    """SQL predicate that excludes projects held by an active manual takeover lease."""

    alias = project_alias.strip() or "p"
    return (
        "NOT ("
        f"{alias}.metadata ? 'manual_takeover_lease' "
        f"AND NULLIF({alias}.metadata->'manual_takeover_lease'->>'expires_at', '') IS NOT NULL "
        f"AND (NULLIF({alias}.metadata->'manual_takeover_lease'->>'expires_at', ''))::timestamptz > now()"
        ")"
    )


def _manual_takeover_lease_active(lease: Any) -> dict[str, Any] | None:
    if not isinstance(lease, dict) or not lease:
        return None
    expires_at = _parse_datetime(lease.get("expires_at"))
    # Missing/unparseable expiry is treated as active to fail closed rather than
    # letting an autonomous worker collide with a human/editor session.
    if expires_at is None:
        return lease
    if expires_at <= datetime.now(timezone.utc):
        return None
    return lease


def cleanup_stale_manual_takeover_leases(project_id: Optional[str] = None) -> list[dict[str, Any]]:
    """Release expired manual takeover leases so they cannot become absorbing state."""

    ensure_runtime_schema()
    project_filter = "" if not project_id else f"AND p.project_id={_q(project_id)}"
    released = _normalize_rows(sql.json_query(
        f"""
        WITH stale AS (
            SELECT p.project_id, p.metadata->'manual_takeover_lease' AS lease
            FROM factory.projects p
            WHERE p.metadata ? 'manual_takeover_lease'
              AND NULLIF(p.metadata->'manual_takeover_lease'->>'expires_at', '') IS NOT NULL
              AND (NULLIF(p.metadata->'manual_takeover_lease'->>'expires_at', ''))::timestamptz <= now()
              {project_filter}
        ), updated AS (
            UPDATE factory.projects p
            SET metadata = (p.metadata - 'manual_takeover_lease')
                || jsonb_build_object(
                    'last_manual_takeover_release',
                    jsonb_build_object('released_by', 'factory-monitor', 'release_reason', 'expired', 'released_at', now())
                ),
                updated_at=now()
            FROM stale
            WHERE p.project_id=stale.project_id
            RETURNING p.project_id, stale.lease
        )
        SELECT COALESCE(jsonb_agg(to_jsonb(updated)), '[]'::jsonb)::text FROM updated;
        """,
        user=_user(),
    ) or [])
    if released:
        values = ",\n".join(
            f"({_q(row.get('project_id'))}, 'factory-monitor', 'manual_takeover_released', {_q('Expired manual takeover lease released')}, {_j({'lease': row.get('lease'), 'release_reason': 'expired'})})"
            for row in released
        )
        sql.psql(
            "INSERT INTO factory.events(project_id, actor, event_type, message, metadata) VALUES\n"
            + values
            + ";",
            user=_user(),
        )
    return released


def active_manual_takeover_lease(project_id: str) -> dict[str, Any] | None:
    cleanup_stale_manual_takeover_leases(project_id)
    project = _project(project_id)
    metadata = project.get("metadata") if isinstance(project, dict) else {}
    lease = metadata.get("manual_takeover_lease") if isinstance(metadata, dict) else None
    return _manual_takeover_lease_active(lease)


def acquire_manual_takeover_lease(
    project_id: str,
    *,
    holder: str = "factory-orchestrator",
    reason: str = "manual_takeover",
    ttl_minutes: int = MANUAL_TAKEOVER_DEFAULT_TTL_MINUTES,
    worktree_path: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Acquire a project-level single-writer lease for manual/operator work."""

    ensure_runtime_schema()
    cleanup_stale_manual_takeover_leases(project_id)
    active = active_manual_takeover_lease(project_id)
    holder_value = str(holder or "factory-orchestrator").strip() or "factory-orchestrator"
    if active and str(active.get("holder") or "") != holder_value:
        return {"project_id": project_id, "acquired": False, "lease": active, "blocked_reason": "manual_takeover_active"}
    ttl = max(1, min(int(ttl_minutes or MANUAL_TAKEOVER_DEFAULT_TTL_MINUTES), MANUAL_TAKEOVER_MAX_TTL_MINUTES))
    now = datetime.now(timezone.utc)
    lease = {
        "kind": "manual_takeover",
        "holder": holder_value,
        "reason": str(reason or "manual_takeover"),
        "worktree_path": worktree_path,
        "session_id": session_id,
        "acquired_at": now.isoformat().replace("+00:00", "Z"),
        "expires_at": (now + timedelta(minutes=ttl)).isoformat().replace("+00:00", "Z"),
        "ttl_minutes": ttl,
    }
    sql.psql(
        f"""
        UPDATE factory.projects
        SET metadata = metadata || {_j({'manual_takeover_lease': lease, 'single_writer_guard': 'manual_takeover_lease'})},
            updated_at=now()
        WHERE project_id={_q(project_id)};
        INSERT INTO factory.events(project_id, actor, event_type, message, metadata)
        VALUES ({_q(project_id)}, {_q(holder_value)}, 'manual_takeover_acquired', {_q('Manual takeover lease acquired; autonomous dispatch is blocked for this project')}, {_j({'lease': lease})});
        """,
        user=_user(),
    )
    return {"project_id": project_id, "acquired": True, "lease": lease}


def release_manual_takeover_lease(
    project_id: str,
    *,
    holder: str = "factory-orchestrator",
    reason: str = "manual_takeover_complete",
) -> dict[str, Any]:
    """Release a project manual takeover lease through the canonical Factory DB path."""

    ensure_runtime_schema()
    holder_value = str(holder or "factory-orchestrator").strip() or "factory-orchestrator"
    release_metadata = {
        "released_by": holder_value,
        "release_reason": str(reason or "manual_takeover_complete"),
        "released_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    sql.psql(
        f"""
        UPDATE factory.projects
        SET metadata = (metadata - 'manual_takeover_lease') || {_j({'last_manual_takeover_release': release_metadata})},
            updated_at=now()
        WHERE project_id={_q(project_id)};
        INSERT INTO factory.events(project_id, actor, event_type, message, metadata)
        VALUES ({_q(project_id)}, {_q(holder_value)}, 'manual_takeover_released', {_q('Manual takeover lease released; autonomous dispatch may resume after preflight')}, {_j(release_metadata)});
        """,
        user=_user(),
    )
    return {"project_id": project_id, "released": True, "release": release_metadata}


def _active_run_task_ids(payload: dict[str, Any]) -> set[str]:
    return {
        str(run.get("task_id"))
        for run in payload.get("task_runs", [])
        if str(run.get("status") or "") in {"queued", "running"} and run.get("task_id")
    }


def _latest_gate_status_map_from_payload(payload: dict[str, Any]) -> dict[str, str]:
    return {
        str(gate_type).lower(): str(status).lower()
        for gate_type, status in _latest_gate_statuses(payload.get("gates", [])).items()
    }


def _mentions_resolved_gate(task: dict[str, Any], gate_statuses: dict[str, str]) -> bool:
    text = _task_blocker_text(task)
    blocker_terms = ("pending", "pendiente", "blocked", "blocker", "bloque", "espera", "requiere")
    if not any(term in text for term in blocker_terms):
        return False
    mentioned = [gate_type for gate_type in gate_statuses if gate_type and gate_type in text]
    return bool(mentioned) and all(gate_statuses.get(gate_type) == "passed" for gate_type in mentioned)


def classify_factory_blocker(task: dict[str, Any], *, payload: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """Classify a blocked/stuck Factory task into the runtime action taxonomy."""

    payload = payload or {}
    text = _task_blocker_text(task)
    status_value = str(task.get("status") or "")
    task_id = str(task.get("task_id") or "")
    active_task_ids = _active_run_task_ids(payload)
    gate_statuses = _latest_gate_status_map_from_payload(payload)

    if status_value in {"claimed", "running", "in_progress", "review_running"} and task_id not in active_task_ids:
        action_category = "stale_orphan_state"
        blocker_category = "runtime_state"
        recommended_action = "repair_orphan_inflight_state"
        requires_human = False
    elif _mentions_resolved_gate(task, gate_statuses) or any(keyword in text for keyword in _BLOCKER_AUTO_KEYWORDS):
        action_category = "auto_resolvable"
        blocker_category = "resolved_gate_or_routine_decision"
        recommended_action = "run_orchestrator_unblock_or_record_gate"
        requires_human = False
    elif any(keyword in text for keyword in _BLOCKER_HUMAN_KEYWORDS):
        action_category = "human_question_required"
        blocker_category = "external_or_owner_decision"
        recommended_action = "create_human_question_and_notify_owner"
        requires_human = True
    elif any(keyword in text for keyword in _BLOCKER_TECHNICAL_KEYWORDS):
        action_category = "technical_rework"
        blocker_category = "technical"
        recommended_action = "delegate_to_programming_worker_for_rework"
        requires_human = False
    else:
        action_category = "technical_rework" if status_value == "blocked" else "auto_resolvable"
        blocker_category = "unclassified"
        recommended_action = "delegate_to_programming_worker_for_rework" if status_value == "blocked" else "run_orchestrator_tick"
        requires_human = False

    alert_key = f"factory:{task.get('project_id')}:{task_id}:{action_category}"
    return {
        "task_id": task_id,
        "project_id": task.get("project_id"),
        "lane_id": task.get("lane_id"),
        "title": task.get("title"),
        "status": status_value,
        "blocker_category": blocker_category,
        "action_category": action_category,
        "recommended_action": recommended_action,
        "requires_human": requires_human,
        "alert_key": alert_key,
        "updated_at": task.get("updated_at"),
        "result_summary": task.get("result_summary"),
    }


def classify_factory_blockers(payload: Optional[dict[str, Any]] = None, *, project_id: Optional[str] = None) -> list[dict[str, Any]]:
    """Return action classifications for blocked tasks and orphan in-flight rows."""

    payload = payload or status(project_id)
    active_task_ids = _active_run_task_ids(payload)
    classified: list[dict[str, Any]] = []
    seen: set[str] = set()
    for task in payload.get("tasks", []):
        if project_id and task.get("project_id") != project_id:
            continue
        task_id = str(task.get("task_id") or "")
        status_value = str(task.get("status") or "")
        is_blocked = status_value == "blocked"
        is_orphan = status_value in {"claimed", "running", "in_progress", "review_running"} and task_id not in active_task_ids
        if not (is_blocked or is_orphan) or task_id in seen:
            continue
        seen.add(task_id)
        classified.append(classify_factory_blocker(task, payload=payload))
    return classified


def record_factory_blocker_actions(classified: Optional[list[dict[str, Any]]] = None, *, payload: Optional[dict[str, Any]] = None, create_questions: bool = True) -> dict[str, Any]:
    """Persist blocker classifications and create human questions when unavoidable."""

    ensure_runtime_schema()
    payload = payload or status()
    classified = classified if classified is not None else classify_factory_blockers(payload)
    events_recorded = 0
    questions_created = 0
    for item in classified:
        task_id = str(item.get("task_id") or "")
        project_id = str(item.get("project_id") or "")
        if not task_id or not project_id:
            continue
        compact = {
            "action_category": item.get("action_category"),
            "blocker_category": item.get("blocker_category"),
            "recommended_action": item.get("recommended_action"),
            "requires_human": item.get("requires_human"),
            "alert_key": item.get("alert_key"),
        }
        sql.psql(
            f"""
            UPDATE factory.tasks
            SET metadata = metadata || {_j({'last_blocker_classification': compact})}, updated_at=updated_at
            WHERE task_id={_q(task_id)};
            INSERT INTO factory.events(project_id, lane_id, task_id, actor, event_type, message, metadata)
            SELECT {_q(project_id)}, {_q(item.get('lane_id'))}, {_q(task_id)}, 'factory-blocker-detector', 'blocker_classified',
                   {_q('Factory blocker classified as ' + str(item.get('action_category')))}, {_j(compact)}
            WHERE NOT EXISTS (
              SELECT 1 FROM factory.events
              WHERE task_id={_q(task_id)}
                AND event_type='blocker_classified'
                AND metadata->>'alert_key'={_q(item.get('alert_key'))}
                AND timestamp > now() - interval '60 minutes'
            );
            """,
            user=_user(),
        )
        events_recorded += 1
        if create_questions and item.get("requires_human"):
            question_id = "hq-" + uuid.uuid5(uuid.NAMESPACE_URL, f"factory:{task_id}:human-question").hex[:16]
            question = (
                f"Factory project {project_id} requires a human decision for task {task_id}: "
                f"{item.get('title') or 'blocked task'}. Recommended action: {item.get('recommended_action')}."
            )
            before = sql.one(
                f"SELECT question_id FROM factory.human_questions WHERE question_id={_q(question_id)} OR (task_id={_q(task_id)} AND status='pending')",
                user=_user(),
            )
            sql.psql(
                f"""
                INSERT INTO factory.human_questions(question_id, project_id, task_id, severity, question, options, asked_via, status, metadata)
                VALUES ({_q(question_id)}, {_q(project_id)}, {_q(task_id)}, 'high', {_q(question)}, '[]'::jsonb, 'factory_watchdog', 'pending', {_j({'alert_key': item.get('alert_key'), 'classification': compact})})
                ON CONFLICT (question_id) DO NOTHING;
                INSERT INTO factory.events(project_id, lane_id, task_id, actor, event_type, message, metadata)
                SELECT {_q(project_id)}, {_q(item.get('lane_id'))}, {_q(task_id)}, 'factory-blocker-detector', 'human_question_created', {_q('Created human question for indispensable Factory blocker')}, {_j({'question_id': question_id, 'alert_key': item.get('alert_key')})}
                WHERE NOT EXISTS (
                  SELECT 1 FROM factory.events
                  WHERE task_id={_q(task_id)} AND event_type='human_question_created' AND metadata->>'question_id'={_q(question_id)}
                );
                """,
                user=_user(),
            )
            if not before:
                questions_created += 1
    return {"classified": len(classified), "events_recorded": events_recorded, "questions_created": questions_created}


def _task_retry_count(task: dict[str, Any]) -> int:
    try:
        return int(task.get("retry_count") or 0)
    except (TypeError, ValueError):
        return 0


def _supervisor_requeue_technical_blockers(
    project_id: str,
    classified: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
    *,
    max_retries: int = SUPERVISOR_TECHNICAL_REWORK_MAX_RETRIES,
) -> dict[str, Any]:
    """Turn technical blocked tasks back into executable rework when safe.

    A blocked autonomous project with technical blockers and no active run is an
    absorbing state unless the supervisor converts the classifier decision into a
    concrete Factory task transition. Keep retries bounded so a definitive
    blocker eventually becomes manual attention instead of monopolizing the
    single-active slot forever.
    """

    tasks_by_id = {str(task.get("task_id") or ""): task for task in tasks}
    requeued: list[dict[str, Any]] = []
    exhausted: list[dict[str, Any]] = []
    for item in classified:
        if item.get("action_category") != "technical_rework":
            continue
        task_id = str(item.get("task_id") or "")
        task = tasks_by_id.get(task_id)
        if not task or str(task.get("status") or "") != "blocked":
            continue
        retry_count = _task_retry_count(task)
        if retry_count >= max_retries:
            exhausted.append({"task_id": task_id, "retry_count": retry_count, "max_retries": max_retries})
            continue
        summary = str(task.get("result_summary") or "").rstrip()
        rework_note = (
            "\n\n[factory-supervisor] Bloqueo técnico reabierto como rework automático "
            f"(intento {retry_count + 1}/{max_retries}). El proyecto no requiere a Jean todavía; "
            "el worker debe corregir la causa raíz y cerrar con evidencia."
        )
        sql.psql(
            f"""
            UPDATE factory.tasks
            SET status='rework',
                result_summary={_q((summary + rework_note).strip())},
                metadata = metadata || {_j({'supervisor_rework': True, 'supervisor_rework_reason': item.get('blocker_category'), 'supervisor_rework_attempt': retry_count + 1, 'supervisor_rework_max_retries': max_retries})},
                updated_at=now()
            WHERE task_id={_q(task_id)} AND status='blocked';
            INSERT INTO factory.events(project_id, lane_id, task_id, actor, event_type, message, metadata)
            VALUES ({_q(project_id)}, {_q(task.get('lane_id'))}, {_q(task_id)}, 'factory-supervisor', 'technical_blocker_requeued',
                    {_q('Supervisor converted technical blocker into runnable rework')},
                    {_j({'retry_count': retry_count, 'max_retries': max_retries, 'classification': item})});
            """,
            user=_user(),
        )
        requeued.append({"task_id": task_id, "retry_count": retry_count, "next_status": "rework"})
    return {"requeued": requeued, "exhausted": exhausted}


def mark_project_manual_attention(project_id: str, *, reason: str, blockers: list[dict[str, Any]]) -> dict[str, Any]:
    """Move a project out of the autonomous slot when it truly needs a person."""

    ensure_runtime_schema()
    compact_blockers = [
        {
            "task_id": blocker.get("task_id"),
            "action_category": blocker.get("action_category"),
            "requires_human": blocker.get("requires_human"),
            "recommended_action": blocker.get("recommended_action"),
        }
        for blocker in blockers[:10]
    ]
    metadata = {
        "autonomous_enabled": False,
        "manual_attention_required": True,
        "manual_attention_reason": reason,
        "manual_attention_blockers": compact_blockers,
        "pause_kind": "manual_attention_required",
        "reactivation_policy": "resolve_state_preflight_before_dispatch",
    }
    sql.psql(
        f"""
        UPDATE factory.projects
        SET status='manual_attention', autonomous_enabled=false, paused_at=now(),
            metadata = (metadata || {_j(metadata)})
                - 'paused_by_single_active_guard'
                - 'single_active_guard_queue'
                - 'single_active_guard_paused_for',
            updated_at=now()
        WHERE project_id={_q(project_id)};
        UPDATE factory.lanes
        SET status='manual_attention', updated_at=now()
        WHERE project_id={_q(project_id)} AND status IN ('active','planned','intake','blocked','delivery_hold','paused');
        INSERT INTO factory.events(project_id, actor, event_type, message, metadata)
        VALUES ({_q(project_id)}, 'factory-supervisor', 'manual_attention_required',
                {_q('Factory supervisor moved project out of autonomous slot because it needs manual attention')},
                {_j(metadata)});
        """,
        user=_user(),
    )
    return {"project_id": project_id, "status": MANUAL_ATTENTION_STATUS, "reason": reason, "blockers": compact_blockers}


def factory_watchdog_alerts(payload: Optional[dict[str, Any]] = None, *, blocked_minutes: int = BLOCKED_ALERT_DEFAULT_MINUTES, claimed_null_rounds: int = 0, project_id: Optional[str] = None) -> list[dict[str, Any]]:
    """Compute deterministic Factory watchdog alerts for dashboard/cron."""

    payload = payload or status(project_id)
    now = datetime.now(timezone.utc)
    projects = {str(project.get("project_id")): project for project in payload.get("projects", [])}
    tasks_by_project: dict[str, list[dict[str, Any]]] = {}
    for task in payload.get("tasks", []):
        if project_id and task.get("project_id") != project_id:
            continue
        tasks_by_project.setdefault(str(task.get("project_id")), []).append(task)
    pending_questions_by_project: dict[str, int] = {}
    for question in payload.get("human_questions", []):
        if str(question.get("status") or "") == "pending":
            pid = str(question.get("project_id") or "")
            pending_questions_by_project[pid] = pending_questions_by_project.get(pid, 0) + 1

    alerts: list[dict[str, Any]] = []
    for pid, project in projects.items():
        if project_id and pid != project_id:
            continue
        if not project.get("autonomous_enabled"):
            continue
        ptasks = tasks_by_project.get(pid, [])
        blocked_tasks = [task for task in ptasks if str(task.get("status") or "") == "blocked"]
        if str(project.get("status") or "") == "blocked" and blocked_tasks:
            ages = [age for age in (_age_minutes(task.get("updated_at") or task.get("created_at"), now=now) for task in blocked_tasks) if age is not None]
            max_age = max(ages) if ages else None
            if max_age is not None and max_age >= blocked_minutes:
                alerts.append({
                    "alert_key": f"factory:{pid}:blocked>{blocked_minutes}m",
                    "alert_type": "autonomous_project_blocked_too_long",
                    "severity": "high",
                    "project_id": pid,
                    "message": f"Autonomous Factory project {pid} has been blocked for {int(max_age)} minutes.",
                    "age_minutes": max_age,
                    "blocked_tasks": [task.get("task_id") for task in blocked_tasks],
                })
            if pending_questions_by_project.get(pid, 0) == 0:
                alerts.append({
                    "alert_key": f"factory:{pid}:blocked-without-human-question",
                    "alert_type": "blocked_without_human_question",
                    "severity": "medium",
                    "project_id": pid,
                    "message": f"Factory project {pid} has blocked tasks but no pending human question; Zeus must auto-resolve or create one.",
                    "blocked_tasks": [task.get("task_id") for task in blocked_tasks],
                })
        if str(project.get("status") or "") == DELIVERY_HOLD_STATUS and blocked_tasks and pending_questions_by_project.get(pid, 0) == 0:
            alerts.append({
                "alert_key": f"factory:{pid}:delivery-hold-autoresolvable-blocked-work",
                "alert_type": "delivery_hold_autoresolvable_blocked_work",
                "severity": "high",
                "project_id": pid,
                "invariant": factory_contracts.FactoryInvariant.RED_DELIVERY_HOLD_WITH_BLOCKED_WORK.value,
                "message": f"Autonomous Factory project {pid} is in delivery_hold with blocked work and no human question; supervisor must repair or escalate.",
                "blocked_tasks": [task.get("task_id") for task in blocked_tasks],
                "recommended_action": "supervisor_repair_then_force_tick",
            })

    for item in classify_factory_blockers(payload, project_id=project_id):
        if item.get("action_category") == "stale_orphan_state":
            alerts.append({
                "alert_key": item.get("alert_key"),
                "alert_type": "orphan_inflight_without_active_run",
                "severity": "high",
                "project_id": item.get("project_id"),
                "task_id": item.get("task_id"),
                "message": f"Task {item.get('task_id')} is {item.get('status')} without an active task_run.",
                "recommended_action": item.get("recommended_action"),
            })
    if claimed_null_rounds >= CLAIMED_NULL_ALERT_ROUNDS and _claimed_null_alert_expected(payload, project_id=project_id):
        alerts.append({
            "alert_key": "factory:cron:claimed-null-repeated",
            "alert_type": "cron_claimed_null_repeated",
            "severity": "medium",
            "project_id": project_id,
            "message": f"Factory cron returned claimed=null for {claimed_null_rounds} consecutive rounds while runnable autonomous work exists.",
            "claimed_null_rounds": claimed_null_rounds,
        })
    return alerts


def _payload_has_claimable_task(project_id: str, tasks: list[dict[str, Any]]) -> bool:
    """Mirror the dependency semantics used by ``_next_runnable_task``.

    The watchdog runs from a status payload, not directly from SQL. Counting
    every ``todo`` row as runnable creates false positives when the only open
    work is behind a blocked dependency. The cron claimed-null alert should fire
    only when a task is actually claimable by the dispatcher: status todo/ready
    and all declared dependencies are terminal.
    """

    project_tasks = [task for task in tasks if str(task.get("project_id") or "") == project_id]
    terminal_task_ids = {
        str(task.get("task_id") or "")
        for task in project_tasks
        if str(task.get("status") or "") in TERMINAL_TASK_STATUSES
    }
    for task in project_tasks:
        if str(task.get("status") or "") not in {"todo", "ready"}:
            continue
        dependencies = task.get("dependencies") or []
        if isinstance(dependencies, str):
            dependencies = [dependencies]
        if not isinstance(dependencies, list):
            dependencies = []
        if all(str(dep) in terminal_task_ids for dep in dependencies):
            return True
    return False


def _claimed_null_alert_expected(payload: dict[str, Any], *, project_id: Optional[str] = None) -> bool:
    """Return True only when claimed=null is suspicious, not simply idle.

    A cron tick that claims no work is healthy when there are no autonomous
    projects with dependency-ready tasks, or while a run is already active.
    Alert only when the dispatcher should have been able to claim work.
    """

    projects = {
        str(project.get("project_id")): project
        for project in payload.get("projects", [])
        if not project_id or str(project.get("project_id")) == project_id
    }
    if not projects:
        return False
    active_run_projects = {
        str(run.get("project_id"))
        for run in payload.get("task_runs", [])
        if str(run.get("status") or "") in {"queued", "running"}
    }
    payload_tasks = payload.get("tasks", [])
    tasks = payload_tasks if isinstance(payload_tasks, list) else []
    for pid, project in projects.items():
        if not project.get("autonomous_enabled"):
            continue
        if str(project.get("status") or "") not in DISPATCHABLE_PROJECT_STATUSES:
            continue
        if pid in active_run_projects:
            continue
        if _payload_has_claimable_task(pid, tasks):
            return True
    return False


def _task_reconciliation_anomaly(task: dict[str, Any]) -> tuple[str, str] | None:
    metadata = _metadata(task)
    code = str(metadata.get("reconciliation_anomaly") or "").strip()
    if code:
        return code, "structured_reconciliation_metadata"
    text = "\n".join(str(task.get(key) or "") for key in ("task_id", "title", "description", "phase", "result_summary")).lower()
    for candidate in RECONCILIATION_TASK_SPECS:
        if candidate in text or candidate.replace("_", "-") in text:
            return candidate, "legacy_reconciliation_text"
    return None


def _resolved_reconciliation_anomaly(project: dict[str, Any] | None, task: dict[str, Any]) -> tuple[str, str] | None:
    """Return ``(anomaly_code, source)`` when a blocked task is now resolved.

    Reconciliation blockers are structured state, not prose.  Each supported
    anomaly has a deterministic resolution condition so `delivery_hold` cannot
    become an absorbing state after the underlying metadata/docs/gate issue was
    already fixed. Legacy blocker prose is recognized only for known anomaly
    codes and is migrated forward when reopened.
    """

    if not project:
        return None
    anomaly = _task_reconciliation_anomaly(task)
    if not anomaly:
        return None
    code, source = anomaly

    project_metadata = _metadata(project)
    if code == "missing_repository_strategy":
        return (code, source) if _repository_strategy_complete(project) else None
    if code == "missing_notion_project":
        return (code, source) if _notion_projection_issue(project_metadata) is None else None
    if code == "notion_pm_projection_warning":
        # Legacy optional-warning tasks should not keep projects in an absorbing
        # reporting state. The current reconciler will create the required
        # missing_notion_project task whenever the Notion PM projection is absent
        # or stale.
        return code, source

    factory_dir, artifact_dir = _project_artifact_dir(project)
    if code == "missing_project_artifact_dir":
        return (code, source) if factory_dir is not None and factory_dir.is_dir() else None

    if code == "missing_required_docs":
        if _required_docs_explicitly_waived(project_metadata):
            return code, source
        if factory_dir is not None and factory_dir.is_dir() and all((factory_dir / name).is_file() for name in FACTORY_REQUIRED_DOCS):
            return code, source
        return None

    if code == "docs_not_indexed":
        if _required_docs_explicitly_waived(project_metadata):
            return code, source
        if factory_dir is not None and factory_dir.is_dir() and not _docs_missing_from_documentation_index(factory_dir):
            return code, source
        return None

    if code == "uncommitted_project_artifacts":
        if _repo_commit_explicitly_waived(project_metadata):
            return code, source
        repo_path = str(project.get("repo_path") or "").strip()
        if repo_path and factory_dir is not None and factory_dir.is_dir() and not _uncommitted_project_artifacts(Path(repo_path), artifact_dir):
            return code, source
        return None

    if code == "pending_effective_gates":
        return (code, source) if not _active_pending_gates(str(project.get("project_id") or "")) else None

    if code == "deliverable_unverified":
        latest_gate_status = _latest_gate_statuses(_latest_gate_rows(str(project.get("project_id") or "")))
        if latest_gate_status.get("delivery") == "passed" or latest_gate_status.get("critical_readiness") == "passed":
            return code, source
        return None

    return None


def clear_resolved_blockers(project_id: str) -> dict[str, Any]:
    """Reopen blocked tasks whose recorded blocker is already resolved.

    The resolver handles two canonical blocker sources:
    1. structured reconciliation anomalies with objective resolution conditions;
    2. legacy prose blockers that explicitly wait on a gate now passed.

    Reopened tasks move to ``review_ready`` rather than self-approved; the
    assigned reviewer still has to close the gate/evidence path.
    """

    ensure_runtime_schema()
    project = _project(project_id)
    effective = {
        str(gate.get("gate_type") or "").lower(): str(gate.get("status") or "").lower()
        for gate in _latest_gate_rows(project_id)
    }
    blocked = [task for task in _tasks(project_id) if str(task.get("status") or "") == "blocked"]
    reopened: list[dict[str, Any]] = []
    blocker_terms = ("pending", "pendiente", "blocked", "blocker", "bloque", "espera", "requiere")
    for task in blocked:
        resolved_anomaly = _resolved_reconciliation_anomaly(project, task)
        if resolved_anomaly:
            resolved_code, resolved_source = resolved_anomaly
            summary = str(task.get("result_summary") or "").rstrip()
            unblock_note = (
                "\n\n[factory-orchestrator] Bloqueo de reconciliación resuelto: "
                + resolved_code
                + " ya no viola la condición canónica. Tarea reabierta para review; no auto-aprobada."
            )
            sql.psql(
                f"""
                UPDATE factory.tasks
                SET status='review_ready',
                    evidence_status=CASE WHEN evidence_status='missing' THEN 'present' ELSE evidence_status END,
                    result_summary={_q((summary + unblock_note).strip())},
                    metadata = metadata || {_j({'unblocked_by': 'factory-orchestrator', 'unblock_reason': 'resolved_reconciliation_anomaly', 'resolved_anomaly': resolved_code, 'blocker_source': resolved_source, 'reconciliation_anomaly': resolved_code})},
                    updated_at=now()
                WHERE task_id={_q(task['task_id'])};
                INSERT INTO factory.events(project_id, lane_id, task_id, actor, event_type, message, metadata)
                VALUES ({_q(project_id)}, {_q(task.get('lane_id'))}, {_q(task['task_id'])}, 'factory-orchestrator', 'blocker_resolved', {_q('Resolved structured reconciliation blocker and reopened task for review')}, {_j({'resolved_anomaly': resolved_code, 'source': resolved_source})});
                """,
                user=_user(),
            )
            reopened.append({"task_id": task["task_id"], "resolved_anomaly": resolved_code, "source": resolved_source})
            continue

        text = "\n".join(
            str(task.get(key) or "") for key in ("title", "description", "result_summary")
        ).lower()
        if not any(term in text for term in blocker_terms):
            continue
        mentioned_gates = [
            gate_type
            for gate_type in effective
            if gate_type and gate_type in text
        ]
        if not mentioned_gates:
            continue
        unresolved_gates = [gate_type for gate_type in mentioned_gates if effective.get(gate_type) != "passed"]
        if unresolved_gates:
            continue
        resolved_gates = mentioned_gates
        summary = str(task.get("result_summary") or "").rstrip()
        unblock_note = (
            "\n\n[factory-orchestrator] Bloqueo de gate resuelto: "
            + ", ".join(sorted(resolved_gates))
            + " ya está passed en el gate efectivo. Tarea reabierta para review; no auto-aprobada."
        )
        sql.psql(
            f"""
            UPDATE factory.tasks
            SET status='review_ready',
                evidence_status=CASE WHEN evidence_status='missing' THEN 'present' ELSE evidence_status END,
                result_summary={_q((summary + unblock_note).strip())},
                metadata = metadata || {_j({'unblocked_by': 'factory-orchestrator', 'unblock_reason': 'resolved_gate_blocker', 'resolved_gates': sorted(resolved_gates)})},
                updated_at=now()
            WHERE task_id={_q(task['task_id'])};
            INSERT INTO factory.events(project_id, lane_id, task_id, actor, event_type, message, metadata)
            VALUES ({_q(project_id)}, {_q(task.get('lane_id'))}, {_q(task['task_id'])}, 'factory-orchestrator', 'blocker_resolved', {_q('Resolved stale gate blocker and reopened task for review')}, {_j({'resolved_gates': sorted(resolved_gates)})});
            """,
            user=_user(),
        )
        reopened.append({"task_id": task["task_id"], "resolved_gates": sorted(resolved_gates)})
    reconciled = reconcile_project(project_id)
    return {"project_id": project_id, "reopened": reopened, **reconciled}


def claim_next_review(project_id: Optional[str] = None, *, worker: str = "factory-reviewer-dispatch") -> dict[str, Any] | None:
    ensure_runtime_schema()
    cleanup_stale_manual_takeover_leases(project_id)
    project_filter = f"AND p.project_id={_q(project_id)}" if project_id else ""
    manual_takeover_filter = _manual_takeover_dispatch_filter("p")
    row = sql.statement_one(
        f"""
        UPDATE factory.tasks t
        SET status='review_running', claimed_by={_q(worker)}, claimed_at=now(), lease_until=now() + interval '30 minutes', updated_at=now()
        FROM factory.projects p
        WHERE t.project_id=p.project_id
          AND p.autonomous_enabled IS TRUE
          AND p.status IN ('active','planned','intake','blocked')
          AND {manual_takeover_filter}
          AND t.status='review_ready'
          {project_filter}
          AND NOT EXISTS (
            SELECT 1 FROM factory.task_runs r
            WHERE r.project_id=t.project_id AND r.status IN ('queued','running')
          )
          AND t.task_id = (
            SELECT t2.task_id
            FROM factory.tasks t2
            WHERE t2.project_id=t.project_id AND t2.status='review_ready'
            ORDER BY t2.priority, t2.created_at
            LIMIT 1
          )
        RETURNING t.*
        """,
        user=_user(),
    )
    if not row:
        return None
    normalized = _normalize(row)
    run_id = f"run-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    reviewer_profile = normalized.get("reviewer_profile") or normalized.get("reviewer_agent_id") or "quality-reviewer"
    sql.psql(
        f"""
        INSERT INTO factory.task_runs(run_id, task_id, project_id, lane_id, worker_profile, reviewer_profile, engine, status, started_at, heartbeat_at, metadata)
        VALUES ({_q(run_id)}, {_q(normalized['task_id'])}, {_q(normalized['project_id'])}, {_q(normalized.get('lane_id'))}, {_q(reviewer_profile)}, {_q(reviewer_profile)}, {_q(normalized.get('engine'))}, 'queued', now(), now(), {_j({'claimed_by': worker, 'run_type': 'review'})});
        INSERT INTO factory.events(project_id, lane_id, task_id, actor, event_type, message, metadata)
        VALUES ({_q(normalized['project_id'])}, {_q(normalized.get('lane_id'))}, {_q(normalized['task_id'])}, {_q(worker)}, 'review_claimed', {_q(f"Task {normalized['task_id']} claimed for review by {reviewer_profile}")}, {_j({'run_id': run_id, 'worker_profile': reviewer_profile, 'run_type': 'review'})});
        """,
        user=_user(),
    )
    return {"run_id": run_id, "task": normalized, "worker_profile": reviewer_profile, "run_type": "review"}


def claim_next_rework(project_id: Optional[str] = None, *, worker: str = "factory-dispatcher") -> dict[str, Any] | None:
    """Claim the oldest rework task for its original owner.

    Review failure should not be terminal and should not require Jean/Zeus to
    manually flip the row back to ``todo``. ``rework`` blocks later increments,
    but it is itself runnable by the owner with the reviewer findings carried in
    ``result_summary``.
    """

    ensure_runtime_schema()
    cleanup_stale_manual_takeover_leases(project_id)
    project_filter = f"AND p.project_id={_q(project_id)}" if project_id else ""
    manual_takeover_filter = _manual_takeover_dispatch_filter("p")
    in_flight = ",".join(_q(status) for status in IN_FLIGHT_TASK_STATUSES)
    row = sql.statement_one(
        f"""
        UPDATE factory.tasks t
        SET status='claimed',
            claimed_by={_q(worker)},
            claimed_at=now(),
            lease_until=now() + interval '30 minutes',
            retry_count=COALESCE(retry_count, 0) + 1,
            updated_at=now()
        FROM factory.projects p
        WHERE t.project_id=p.project_id
          AND p.autonomous_enabled IS TRUE
          AND p.status IN ('active','planned','intake','blocked')
          AND {manual_takeover_filter}
          AND t.status='rework'
          {project_filter}
          AND NOT EXISTS (
            SELECT 1 FROM factory.task_runs r
            WHERE r.project_id=t.project_id AND r.status IN ('queued','running')
          )
          AND NOT EXISTS (
            SELECT 1 FROM factory.tasks t_busy
            WHERE t_busy.project_id=t.project_id AND t_busy.status IN ({in_flight})
          )
          AND t.task_id = (
            SELECT t2.task_id
            FROM factory.tasks t2
            WHERE t2.project_id=t.project_id AND t2.status='rework'
            ORDER BY t2.priority, t2.updated_at, t2.created_at
            LIMIT 1
          )
        RETURNING t.*
        """,
        user=_user(),
    )
    if not row:
        return None
    normalized = _normalize(row)
    run_id = f"run-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    worker_profile = normalized.get("owner_profile") or normalized.get("owner_agent_id") or "factory-orchestrator"
    sql.psql(
        f"""
        INSERT INTO factory.task_runs(run_id, task_id, project_id, lane_id, worker_profile, reviewer_profile, engine, status, started_at, heartbeat_at, metadata)
        VALUES ({_q(run_id)}, {_q(normalized['task_id'])}, {_q(normalized['project_id'])}, {_q(normalized.get('lane_id'))}, {_q(worker_profile)}, {_q(normalized.get('reviewer_profile'))}, {_q(normalized.get('engine'))}, 'queued', now(), now(), {_j({'claimed_by': worker, 'run_type': 'rework', 'previous_status': 'rework'})});
        INSERT INTO factory.events(project_id, lane_id, task_id, actor, event_type, message, metadata)
        VALUES ({_q(normalized['project_id'])}, {_q(normalized.get('lane_id'))}, {_q(normalized['task_id'])}, {_q(worker)}, 'rework_claimed', {_q(f"Task {normalized['task_id']} claimed for rework by {worker_profile}")}, {_j({'run_id': run_id, 'worker_profile': worker_profile, 'run_type': 'rework'})});
        """,
        user=_user(),
    )
    return {"run_id": run_id, "task": normalized, "worker_profile": worker_profile, "run_type": "rework"}


def _dispatch_docs_first_waived(metadata: dict[str, Any]) -> bool:
    """Return True only for an explicit Jean-authorized docs/Notion dispatch waiver."""

    if not metadata.get("docs_first_dispatch_waived"):
        return False
    authorizer = str(metadata.get("docs_first_dispatch_waived_authorized_by") or "").strip().lower()
    reason = str(metadata.get("docs_first_dispatch_waived_reason") or "").strip()
    return authorizer in {"jean", "jean garcía", "jean garcia"} and bool(reason)


def _is_runtime_bootstrap_repair_task(task: dict[str, Any]) -> bool:
    metadata = _metadata(task)
    if metadata.get("control_plane_bootstrap") or metadata.get("runtime_bootstrap_repair"):
        return True
    text = "\n".join(str(task.get(key) or "") for key in ("task_id", "title", "description", "phase")).lower()
    return (
        "control-plane" in text
        or "control plane" in text
        or "docs/notion" in text
        or "notion control" in text
        or "link-notion" in text
    )


def _is_implementation_dispatch_task(task: dict[str, Any]) -> bool:
    phase = str(task.get("phase") or "").lower()
    text = "\n".join(str(task.get(key) or "") for key in ("task_id", "title", "description", "engine")).lower()
    return phase == "implementation" or any(term in text for term in ("implementation", "implement", "builder", "claude-code"))


def _dispatch_preflight_blockers(
    task: dict[str, Any],
    *,
    docs_ready: bool,
    notion_ready: bool,
    notion_required: bool = False,
    docs_first_waived: bool = False,
) -> list[str]:
    """Return docs-first blockers for a candidate implementation dispatch."""

    if not _is_implementation_dispatch_task(task):
        return []
    if _is_reconciliation_task(task) or _is_runtime_bootstrap_repair_task(task) or docs_first_waived:
        return []
    blockers: list[str] = []
    if not docs_ready:
        blockers.append("missing_or_unindexed_docs")
    if not notion_ready:
        blockers.append("missing_notion_tracker")
    return blockers


def _project_docs_notion_preflight(project: dict[str, Any], tasks: list[dict[str, Any]], pending_gates: list[dict[str, Any]], gates: list[dict[str, Any]]) -> tuple[bool, bool, bool, bool]:
    metadata = _metadata(project)
    findings = reconciliation_findings(project, tasks, pending_gates, gates)
    codes = {str(finding.get("code") or "") for finding in findings}
    docs_ready = not bool(_g1_document_blockers(project)) and "missing_project_artifact_dir" not in codes
    notion_ready = _notion_projection_issue(metadata) is None
    return docs_ready, notion_ready, _metadata_bool(metadata, "notion_required"), _dispatch_docs_first_waived(metadata)


def _record_dispatch_preflight_denied(project_id: str, task: dict[str, Any], blockers: list[str], *, worker: str) -> None:
    sql.psql(
        f"""
        INSERT INTO factory.events(project_id, lane_id, task_id, actor, event_type, message, metadata)
        VALUES ({_q(project_id)}, {_q(task.get('lane_id'))}, {_q(task.get('task_id'))}, {_q(worker)}, 'dispatch_preflight_denied',
                'Implementation dispatch denied until Factory docs/index/Notion gates are ready',
                {_j({'blockers': blockers, 'runtime_contract': 'docs_first_factory_dispatch'})});
        """,
        user=_user(),
    )


def claim_next_task(project_id: Optional[str] = None, *, worker: str = "factory-dispatcher") -> dict[str, Any] | None:
    ensure_runtime_schema()
    cleanup_stale_manual_takeover_leases(project_id)
    project_filter = f"AND p.project_id={_q(project_id)}" if project_id else ""
    manual_takeover_filter = _manual_takeover_dispatch_filter("p")
    projects = sql.rows(
        f"""
        SELECT p.project_id
        FROM factory.projects p
        WHERE p.autonomous_enabled IS TRUE
          AND p.status IN ('active','planned','intake','blocked')
          AND {manual_takeover_filter}
          {project_filter}
        ORDER BY p.updated_at, p.started_at
        """,
        user=_user(),
    )
    for project in projects:
        pid = project["project_id"]
        tasks = _tasks(pid)
        if _has_active_increment(tasks):
            continue
        task = _next_runnable_task(pid)
        if not task:
            reconcile_project(pid)
            continue
        full_project = _project(pid) or {"project_id": pid, "metadata": {}}
        docs_ready, notion_ready, notion_required, docs_first_waived = _project_docs_notion_preflight(
            full_project,
            tasks,
            _active_pending_gates(pid),
            _latest_gate_rows(pid),
        )
        preflight_blockers = _dispatch_preflight_blockers(
            task,
            docs_ready=docs_ready,
            notion_ready=notion_ready,
            notion_required=notion_required,
            docs_first_waived=docs_first_waived,
        )
        if preflight_blockers:
            ensure_reconciliation_tasks(
                full_project,
                reconciliation_findings(full_project, tasks, _active_pending_gates(pid), _latest_gate_rows(pid)),
                tasks,
            )
            _record_dispatch_preflight_denied(pid, task, preflight_blockers, worker=worker)
            reconcile_project(pid)
            continue
        run_id = f"run-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        worker_profile = task.get("owner_profile") or task.get("owner_agent_id") or "factory-orchestrator"
        row = sql.statement_one(
            f"""
            UPDATE factory.tasks
            SET status='claimed', claimed_by={_q(worker)}, claimed_at=now(), lease_until=now() + interval '30 minutes', updated_at=now()
            WHERE task_id={_q(task['task_id'])} AND status IN ('todo','ready')
            RETURNING *
            """,
            user=_user(),
        )
        if not row:
            continue
        sql.psql(
            f"""
            INSERT INTO factory.task_runs(run_id, task_id, project_id, lane_id, worker_profile, reviewer_profile, engine, status, started_at, heartbeat_at, metadata)
            VALUES ({_q(run_id)}, {_q(row['task_id'])}, {_q(row['project_id'])}, {_q(row.get('lane_id'))}, {_q(worker_profile)}, {_q(row.get('reviewer_profile'))}, {_q(row.get('engine'))}, 'queued', now(), now(), {_j({'claimed_by': worker})});
            INSERT INTO factory.events(project_id, lane_id, task_id, actor, event_type, message, metadata)
            VALUES ({_q(row['project_id'])}, {_q(row.get('lane_id'))}, {_q(row['task_id'])}, {_q(worker)}, 'task_claimed', {_q(f"Task {row['task_id']} claimed for {worker_profile}")}, {_j({'run_id': run_id, 'worker_profile': worker_profile})});
            """,
            user=_user(),
        )
        return {"run_id": run_id, "task": _normalize(row), "worker_profile": worker_profile}
    return None


def mark_run_spawned(run_id: str, *, process_id: int, log_path: str, prompt_path: str) -> None:
    ensure_runtime_schema()
    sql.psql(
        f"""
        UPDATE factory.task_runs
        SET status='running', process_id={int(process_id)}, log_path={_q(log_path)}, prompt_path={_q(prompt_path)}, heartbeat_at=now()
        WHERE run_id={_q(run_id)};
        UPDATE factory.tasks
        SET status='running', last_heartbeat_at=now(), updated_at=now()
        WHERE task_id=(SELECT task_id FROM factory.task_runs WHERE run_id={_q(run_id)});
        """,
        user=_user(),
    )


_SEMANTIC_DONE_MARKERS = ("STATE: DONE", "STATE:DONE")
_SEMANTIC_BLOCKED_MARKERS = ("STATE: BLOCKED", "STATE:BLOCKED")
_SEMANTIC_IN_PROGRESS_MARKERS = ("STATE: IN_PROGRESS", "STATE:IN_PROGRESS")
_SEMANTIC_MARKERS = _SEMANTIC_DONE_MARKERS + _SEMANTIC_BLOCKED_MARKERS + _SEMANTIC_IN_PROGRESS_MARKERS


def _final_semantic_state(text: str) -> Optional[str]:
    # Returns 'done', 'blocked', 'in_progress', or None for the LAST semantic
    # marker in `text`. Historical STATE markers embedded in the prompt or in a
    # prior result_summary must never override the final assistant marker.
    last_done = max(text.rfind(marker) for marker in _SEMANTIC_DONE_MARKERS)
    last_blocked = max(text.rfind(marker) for marker in _SEMANTIC_BLOCKED_MARKERS)
    last_in_progress = max(text.rfind(marker) for marker in _SEMANTIC_IN_PROGRESS_MARKERS)
    candidates = [(last_done, "done"), (last_blocked, "blocked"), (last_in_progress, "in_progress")]
    index, state = max(candidates, key=lambda item: item[0])
    return None if index == -1 else state


def _read_worker_output_summary(log_path: str | Path, *, tail_chars: int = 4000) -> str:
    try:
        text = Path(log_path).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return "Worker log unreadable"
    tail = text[-tail_chars:]
    # Identify the FINAL semantic marker line. Earlier markers (e.g. the prompt
    # embedding a previous result_summary with STATE: BLOCKED) must not be
    # promoted to the summary as if they were the current outcome.
    final_marker_line: str | None = None
    for line in text.splitlines():
        if any(marker in line for marker in _SEMANTIC_MARKERS):
            final_marker_line = line.strip()[-500:]
    if final_marker_line and final_marker_line not in tail:
        return "Final semantic state marker:\n" + final_marker_line + "\n\nLog tail:\n" + tail
    return tail


def _effective_exit_code(exit_code: int, output_summary: str) -> int:
    # Agents may exit 0 after producing a final blocked/rework report, or exit
    # non-zero after producing a final DONE. The FINAL semantic marker wins
    # over the process exit, but earlier historical markers (prompt context,
    # previous result_summary echoes) must not be allowed to mask it.
    state = _final_semantic_state(output_summary)
    if state == "blocked":
        return exit_code if exit_code != 0 else 1
    if state == "in_progress":
        return exit_code if exit_code != 0 else 1
    if state == "done":
        return 0
    return exit_code


def mark_run_finished(run_id: str, *, exit_code: int, output_summary: str = "") -> None:
    ensure_runtime_schema()
    effective_exit_code = _effective_exit_code(exit_code, output_summary)
    run_row = _normalize(sql.one(f"SELECT metadata FROM factory.task_runs WHERE run_id={_q(run_id)}", user=_user()) or {})
    metadata_value = run_row.get("metadata")
    metadata: dict[str, Any] = metadata_value if isinstance(metadata_value, dict) else {}
    run_type = str(metadata.get("run_type") or "implementation")
    if run_type == "review":
        status_value = "done" if effective_exit_code == 0 else "rework"
        evidence_status = "present"
    else:
        status_value = "review_ready" if effective_exit_code == 0 else "blocked"
        evidence_status = "present" if effective_exit_code == 0 else "missing"
    run_status = "succeeded" if effective_exit_code == 0 else "failed"
    sql.psql(
        f"""
        UPDATE factory.task_runs
        SET status={_q(run_status)}, exit_code={int(effective_exit_code)}, finished_at=now(), output_summary={_q(output_summary)}, heartbeat_at=now()
        WHERE run_id={_q(run_id)};
        UPDATE factory.tasks
        SET status={_q(status_value)}, evidence_status={_q(evidence_status)}, result_summary={_q(output_summary)}, finished_at=CASE WHEN {int(effective_exit_code)} = 0 THEN now() ELSE finished_at END, updated_at=now()
        WHERE task_id=(SELECT task_id FROM factory.task_runs WHERE run_id={_q(run_id)});
        """,
        user=_user(),
    )
    row = sql.one(f"SELECT project_id FROM factory.task_runs WHERE run_id={_q(run_id)}", user=_user())
    if row:
        reconcile_project(row["project_id"])


def _repair_orphan_in_flight_tasks(project_id: Optional[str] = None) -> list[dict[str, Any]]:
    """Reopen in-flight task rows that no longer have an active run.

    A task in ``review_running``/``running``/``claimed`` without a queued or
    running ``factory.task_runs`` row is an impossible state: no worker can
    finish it and the dispatcher treats it as active forever.  Keep the repair
    conservative: only rows with **no** active run are reset.  Live long-running
    workers remain untouched even if their lease is old.
    """

    ensure_runtime_schema()
    project_filter = "" if not project_id else f"AND t.project_id={_q(project_id)}"
    active_run_filter = """
        NOT EXISTS (
            SELECT 1 FROM factory.task_runs r
            WHERE r.task_id=t.task_id
              AND r.project_id=t.project_id
              AND r.status IN ('queued','running')
        )
    """
    review_rows = _normalize_rows(sql.json_query(
        f"""
        WITH updated AS (
            UPDATE factory.tasks t
            SET status='review_ready',
                metadata = metadata || {_j({'orphan_repaired_by': 'factory-monitor', 'orphan_repair_reason': 'review_running_without_active_run'})},
                updated_at=now()
            WHERE t.status='review_running'
              {project_filter}
              AND {active_run_filter}
            RETURNING t.project_id, t.lane_id, t.task_id, t.status
        )
        SELECT COALESCE(jsonb_agg(to_jsonb(updated)), '[]'::jsonb)::text FROM updated;
        """,
        user=_user(),
    ) or [])
    worker_rows = _normalize_rows(sql.json_query(
        f"""
        WITH updated AS (
            UPDATE factory.tasks t
            SET status='ready',
                metadata = metadata || {_j({'orphan_repaired_by': 'factory-monitor', 'orphan_repair_reason': 'worker_in_flight_without_active_run'})},
                updated_at=now()
            WHERE t.status IN ('claimed','running','in_progress')
              {project_filter}
              AND {active_run_filter}
            RETURNING t.project_id, t.lane_id, t.task_id, t.status
        )
        SELECT COALESCE(jsonb_agg(to_jsonb(updated)), '[]'::jsonb)::text FROM updated;
        """,
        user=_user(),
    ) or [])
    repaired = review_rows + worker_rows
    if repaired:
        values = ",\n".join(
            f"({_q(row.get('project_id'))}, {_q(row.get('lane_id'))}, {_q(row.get('task_id'))}, 'factory-monitor', 'orphan_inflight_repaired', {_q('Reopened orphan in-flight task with no active run')}, {_j({'new_status': row.get('status')})})"
            for row in repaired
        )
        sql.psql(
            "INSERT INTO factory.events(project_id, lane_id, task_id, actor, event_type, message, metadata) VALUES\n"
            + values
            + ";",
            user=_user(),
        )
    return repaired


def monitor_runs() -> dict[str, Any]:
    ensure_runtime_schema()
    running = _normalize_rows(sql.rows("SELECT * FROM factory.task_runs WHERE status='running' ORDER BY started_at", user=_user()))
    checked = 0
    finished = 0
    for run in running:
        checked += 1
        metadata = run.get("metadata") if isinstance(run.get("metadata"), dict) else {}
        exit_path = metadata.get("exit_path")
        if not exit_path:
            continue
        path = Path(str(exit_path)).expanduser()
        if not path.exists():
            continue
        try:
            exit_code = int(path.read_text(encoding="utf-8").strip() or "1")
        except Exception:
            exit_code = 1
        log_path = str(run.get("log_path") or "")
        summary = ""
        if log_path and Path(log_path).exists():
            summary = _read_worker_output_summary(log_path)
        mark_run_finished(run["run_id"], exit_code=exit_code, output_summary=summary)
        finished += 1
    repaired = _repair_orphan_in_flight_tasks()
    return {"checked": checked, "finished": finished, "orphan_inflight_repaired": len(repaired)}


def update_run_metadata(run_id: str, metadata: dict[str, Any]) -> None:
    ensure_runtime_schema()
    sql.psql(
        f"UPDATE factory.task_runs SET metadata=metadata || {_j(metadata)}, heartbeat_at=now() WHERE run_id={_q(run_id)};",
        user=_user(),
    )


def supervisor_health_check(project_id: str, *, repair: bool = True) -> dict[str, Any]:
    """L2 Factory supervisor: detect invariant violations and perform safe repairs.

    The supervisor is the structural loop behind dashboard actions and cron ticks:
    if an autonomous project is in a static/blocked state but Zeus can infer a
    safe deterministic repair, the runtime should perform that repair itself or
    return a precise human escalation instead of waiting for Jean to ping Zeus.
    """

    ensure_runtime_schema()
    project = _project(project_id)
    if not project:
        return {"project_id": project_id, "health": "red", "violations": [{"invariant": "project_not_found"}], "repairs": []}

    tasks = _tasks(project_id)
    active_runs = _normalize_rows(sql.rows(
        f"SELECT run_id, task_id, status FROM factory.task_runs WHERE project_id={_q(project_id)} AND status IN ('queued','running')",
        user=_user(),
    ))
    pending_questions = _normalize_rows(sql.rows(
        f"SELECT question_id, task_id, status FROM factory.human_questions WHERE project_id={_q(project_id)} AND status IN ('pending','open')",
        user=_user(),
    ))
    blocked_tasks = [task for task in tasks if str(task.get("status") or "") == "blocked"]
    autonomous = _project_autonomous_enabled(project)
    violations: list[dict[str, Any]] = []
    repairs: list[dict[str, Any]] = []

    payload = {
        "projects": [project],
        "tasks": tasks,
        "task_runs": active_runs,
        "gates": [],
        "human_questions": pending_questions,
    }
    no_runnable_work = not _has_runnable_autonomous_work(tasks)
    blocked_without_runtime = autonomous and blocked_tasks and not active_runs and no_runnable_work
    delivery_hold_blocked = str(project.get("status") or "") == DELIVERY_HOLD_STATUS and blocked_without_runtime
    autonomous_blocked = str(project.get("status") or "") == "blocked" and blocked_without_runtime

    if delivery_hold_blocked or autonomous_blocked:
        invariant = (
            factory_contracts.FactoryInvariant.RED_DELIVERY_HOLD_WITH_BLOCKED_WORK.value
            if delivery_hold_blocked
            else factory_contracts.FactoryInvariant.RED_AUTONOMOUS_WITHOUT_RUNNABLE_WORK_OR_QUESTION.value
        )
        violations.append({
            "invariant": invariant,
            "project_id": project_id,
            "blocked_tasks": [task.get("task_id") for task in blocked_tasks],
            "expected_runtime_action": "repair_requeue_or_manual_attention",
        })
        if repair:
            unblocked = clear_resolved_blockers(project_id)
            repairs.append({"operation": "clear_resolved_blockers", "result": unblocked})
            tasks = _tasks(project_id)
            blocked_tasks = [task for task in tasks if str(task.get("status") or "") == "blocked"]
            payload["tasks"] = tasks
            classified = classify_factory_blockers(payload, project_id=project_id)
            blocker_actions = record_factory_blocker_actions(classified, payload=payload, create_questions=True)
            repairs.append({"operation": "record_factory_blocker_actions", "result": blocker_actions})
            if pending_questions:
                manual = mark_project_manual_attention(project_id, reason="pending_human_question", blockers=classified)
                repairs.append({"operation": "mark_project_manual_attention", "result": manual})
            else:
                human_blockers = [item for item in classified if item.get("requires_human")]
                requeue = _supervisor_requeue_technical_blockers(project_id, classified, tasks)
                if requeue.get("requeued"):
                    repairs.append({"operation": "supervisor_requeue_technical_blockers", "result": requeue})
                if human_blockers or (requeue.get("exhausted") and not requeue.get("requeued")):
                    manual_reason = "human_question_required" if human_blockers else "technical_rework_retries_exhausted"
                    manual = mark_project_manual_attention(project_id, reason=manual_reason, blockers=human_blockers or classified)
                    repairs.append({"operation": "mark_project_manual_attention", "result": manual})

    health = "green"
    if violations and not repairs:
        health = "red"
    elif violations:
        health = "yellow"
    return {"project_id": project_id, "health": health, "violations": violations, "repairs": repairs}


def _preflight_task_count(preflight: dict[str, Any], statuses: set[str]) -> int:
    counts = preflight.get("task_counts") if isinstance(preflight.get("task_counts"), dict) else {}
    total = 0
    for status in statuses:
        try:
            total += int(counts.get(status, 0) or 0)
        except (TypeError, ValueError):
            continue
    return total


def _resume_preflight_blocker(preflight: dict[str, Any]) -> str | None:
    if preflight.get("manual_takeover_lease"):
        return "manual_takeover_active"
    status_value = str(preflight.get("status") or "").lower()
    if status_value in TERMINAL_PROJECT_STATUSES:
        return f"terminal_{status_value}"
    runnable_count = _preflight_task_count(preflight, RESUME_RUNNABLE_TASK_STATUSES)
    if status_value == MANUAL_ATTENTION_STATUS and runnable_count <= 0:
        return "manual_attention_without_runnable_work"
    if status_value in {"hold", "on_hold"}:
        return "condition_hold"
    if status_value == DELIVERY_HOLD_STATUS and runnable_count <= 0:
        return "delivery_hold_without_runnable_work"
    if status_value == "blocked" and runnable_count <= 0:
        return "blocked_without_runnable_work"
    if status_value == "paused" and _preflight_task_count(preflight, {"blocked"}) > 0 and runnable_count <= 0:
        return "blocked_without_runnable_work"
    return None


def resolve_project_state(project_id: str) -> dict[str, Any]:
    """Canonical user-facing resolve action for Factory project state.

    This is the deterministic control-plane operation behind the dashboard's
    single "Resolver estado" button. It intentionally combines the old
    "reconcile" and "unblock" buttons: finish/repair stale runs, clear resolved
    blockers, recompute status, run the supervisor repair pass, and persist
    blocker classifications/human questions when the remaining condition really
    needs a person.
    """

    monitor = monitor_runs()
    unblocked = clear_resolved_blockers(project_id)
    reconciled = reconcile_project(project_id)
    supervisor = supervisor_health_check(project_id, repair=True)
    if supervisor.get("repairs"):
        reconciled = reconcile_project(project_id)
    payload = status(project_id)
    project_rows = payload.get("projects") or []
    project_meta = project_rows[0].get("metadata") if project_rows and isinstance(project_rows[0].get("metadata"), dict) else {}
    manual_takeover_lease = _manual_takeover_lease_active(project_meta.get("manual_takeover_lease")) if isinstance(project_meta, dict) else None
    classified = classify_factory_blockers(payload, project_id=project_id)
    blocker_actions = record_factory_blocker_actions(classified, payload=payload, create_questions=True)
    return {
        "action": "resolve-state",
        "project_id": project_id,
        **reconciled,
        "manual_takeover_lease": manual_takeover_lease,
        "monitor": monitor,
        "unblocked": unblocked,
        "supervisor": supervisor,
        "blockers": classified,
        "blocker_actions": blocker_actions,
    }


def force_tick(project_id: Optional[str] = None) -> dict[str, Any]:
    ensure_runtime_schema()
    monitor = monitor_runs()
    if project_id:
        unblock_targets = [project_id]
    else:
        unblock_targets = [
            row["project_id"]
            for row in sql.rows(
                "SELECT project_id FROM factory.projects WHERE status='blocked' OR autonomous_enabled IS TRUE ORDER BY updated_at",
                user=_user(),
            )
        ]
    unblocked = []
    for target in unblock_targets:
        result = clear_resolved_blockers(target)
        if result.get("reopened"):
            unblocked.append({"project_id": target, "reopened": result.get("reopened")})
    if project_id:
        reconciled = [reconcile_project(project_id)]
    else:
        reconciled = [reconcile_project(row["project_id"]) for row in sql.rows("SELECT project_id FROM factory.projects ORDER BY updated_at", user=_user())]
    claimed = claim_next_review(project_id, worker="factory-force-tick")
    if not claimed:
        claimed = claim_next_rework(project_id, worker="factory-force-tick")
    if not claimed:
        claimed = claim_next_task(project_id, worker="factory-force-tick")
    return {"monitor": monitor, "unblocked": unblocked, "reconciled": reconciled, "claimed": claimed}


def normalize_project_action(action: str) -> str:
    """Map legacy dashboard/API/CLI action names to the canonical control action."""

    normalized = str(action or "").strip().lower().replace("_", "-")
    aliases = {
        "resolve-state": "resolve-state",
        "resolve": "resolve-state",
        "resolve-blockers": "resolve-state",
        "resolver-estado": "resolve-state",
        "resolver-bloqueos": "resolve-state",
        # Legacy controls remain accepted but converge on the canonical action.
        "reconcile": "resolve-state",
        "unblock": "resolve-state",
        "resume": "resume",
        "pause": "pause",
        "tick": "tick",
    }
    return aliases.get(normalized, normalized)


def control_action(project_id: str, action: str) -> dict[str, Any]:
    canonical_action = normalize_project_action(action)
    if canonical_action == "resume":
        preflight = resolve_project_state(project_id)
        blocked_reason = _resume_preflight_blocker(preflight)
        if blocked_reason:
            return {
                "action": "resume",
                "project_id": project_id,
                "status": preflight.get("status"),
                "resume_blocked": True,
                "resume_blocked_reason": blocked_reason,
                "dispatch_allowed": False,
                "preflight": preflight,
            }
        resumed = resume_project(project_id)
        supervisor = supervisor_health_check(project_id, repair=True)
        return {"action": "resume", **resumed, "resume_blocked": False, "dispatch_allowed": True, "preflight": preflight, "supervisor": supervisor}
    if canonical_action == "pause":
        return {"action": "pause", **pause_project(project_id)}
    if canonical_action == "resolve-state":
        return resolve_project_state(project_id)
    if canonical_action == "tick":
        return {"action": "tick", **force_tick(project_id)}
    raise ValueError(f"Unsupported factory action: {action}")


def status(project_id: Optional[str] = None, **_: Any) -> dict[str, Any]:
    ensure_runtime_schema()
    where = "" if not project_id else f"WHERE project_id={_q(project_id)}"
    filter_expr = "TRUE" if not project_id else f"project_id={_q(project_id)}"
    projects = _normalize_rows(sql.rows(f"SELECT * FROM factory.projects {where} ORDER BY updated_at DESC", user=_user()))
    lanes = _normalize_rows(sql.rows(f"SELECT *, COALESCE(metadata->>'execution_surface', 'factory') AS execution_surface FROM factory.lanes WHERE {filter_expr} ORDER BY project_id, lane_id", user=_user()))
    tasks = _normalize_rows(sql.rows(f"SELECT * FROM factory.tasks WHERE {filter_expr} ORDER BY project_id, priority, created_at", user=_user()))
    for task in tasks:
        task.pop("kanban_id", None)
    gates = _normalize_rows(sql.rows(f"SELECT * FROM factory.gates WHERE {filter_expr} ORDER BY timestamp DESC LIMIT 300", user=_user()))
    events = _normalize_rows(sql.rows(f"SELECT * FROM factory.events WHERE {filter_expr} ORDER BY timestamp DESC LIMIT 300", user=_user()))
    artifacts = _normalize_rows(sql.rows(f"SELECT * FROM factory.artifacts WHERE {filter_expr} ORDER BY created_at DESC LIMIT 300", user=_user()))
    task_runs = _normalize_rows(sql.rows(f"SELECT * FROM factory.task_runs WHERE {filter_expr} ORDER BY started_at DESC LIMIT 300", user=_user()))
    human_questions = _normalize_rows(sql.rows(f"SELECT * FROM factory.human_questions WHERE {filter_expr} ORDER BY created_at DESC LIMIT 100", user=_user()))
    agents = list_agents()
    for project in projects:
        project["document_status"] = project_document_status(project)
    payload = {
        "db_backend": "agent_core_postgres",
        "database": sql.runtime_env().get("AGENT_DB_NAME", "zeus_agent"),
        "db_path": f"agent_core_postgres:{sql.runtime_env().get('AGENT_DB_NAME', 'zeus_agent')}.factory",
        "projects": projects,
        "lanes": lanes,
        "tasks": tasks,
        "gates": gates,
        "events": events,
        "artifacts": artifacts,
        "task_runs": task_runs,
        "human_questions": human_questions,
        "agents": agents,
    }
    payload["alerts"] = factory_watchdog_alerts(payload, project_id=project_id)
    return payload

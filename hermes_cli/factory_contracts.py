"""Closed runtime contracts for the SitioUno Software Factory.

The Factory runtime stores status values as text in Agent Core Postgres for
backward compatibility, but code should treat them as a closed finite-state
contract.  This module centralizes those values so watchdogs, reconciler,
dispatcher, and dashboard actions do not drift into incompatible string sets.
"""
from __future__ import annotations

import re
from enum import Enum
from pathlib import Path
from typing import Any


class _StrEnum(str, Enum):
    """Portable string enum with JSON/SQL friendly values."""

    def __str__(self) -> str:  # pragma: no cover - trivial convenience
        return self.value


class ProjectStatus(_StrEnum):
    INTAKE = "intake"
    PLANNED = "planned"
    ACTIVE = "active"
    BLOCKED = "blocked"
    MANUAL_ATTENTION = "manual_attention"
    PAUSED = "paused"
    DELIVERY_HOLD = "delivery_hold"
    COMPLETED = "completed"
    ACCEPTED = "accepted"
    CANCELLED = "cancelled"
    SUPERSEDED = "superseded"


class TaskStatus(_StrEnum):
    TODO = "todo"
    READY = "ready"
    CLAIMED = "claimed"
    RUNNING = "running"
    IN_PROGRESS = "in_progress"
    REVIEW_READY = "review_ready"
    REVIEW_RUNNING = "review_running"
    REVIEW_PENDING_HUMAN = "review_pending_human"
    QA_READY = "qa_ready"
    REWORK = "rework"
    BLOCKED = "blocked"
    DONE = "done"
    VERIFIED = "verified"
    ACCEPTED = "accepted"
    CANCELLED = "cancelled"
    SUPERSEDED = "superseded"


class RunStatus(_StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    STALE = "stale"


class GateStatus(_StrEnum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    WAIVED = "waived"


class FactoryInvariant(_StrEnum):
    RED_DELIVERY_HOLD_WITH_BLOCKED_WORK = "RED_DELIVERY_HOLD_WITH_BLOCKED_WORK"
    RED_AUTONOMOUS_WITHOUT_RUNNABLE_WORK_OR_QUESTION = "RED_AUTONOMOUS_WITHOUT_RUNNABLE_WORK_OR_QUESTION"
    RED_ORPHAN_INFLIGHT_WITHOUT_ACTIVE_RUN = "RED_ORPHAN_INFLIGHT_WITHOUT_ACTIVE_RUN"


class RepositoryScope(_StrEnum):
    ZEUS_ONLY = "zeus_only"
    ZEUS_THEN_RUNTIME = "zeus_then_runtime"
    RUNTIME_ONLY = "runtime_only"
    EXISTING_PROJECT_CHANGE = "existing_project_change"
    NEW_PRODUCT_REPO = "new_product_repo"
    DOCS_OR_RESEARCH_ONLY = "docs_or_research_only"


class WorkIntent(_StrEnum):
    CREATE_NEW_PROJECT = "create_new_project"
    ADD_FUNCTIONALITY = "add_functionality"
    MODIFY_EXISTING_PROJECT = "modify_existing_project"
    MAINTAIN_EXISTING_PROJECT = "maintain_existing_project"
    DOCS_RESEARCH = "docs_research"


TERMINAL_TASK_STATUSES = {
    TaskStatus.DONE.value,
    TaskStatus.VERIFIED.value,
    TaskStatus.ACCEPTED.value,
    TaskStatus.CANCELLED.value,
    TaskStatus.SUPERSEDED.value,
}

IN_FLIGHT_TASK_STATUSES = {
    TaskStatus.CLAIMED.value,
    TaskStatus.RUNNING.value,
    TaskStatus.IN_PROGRESS.value,
    TaskStatus.REVIEW_READY.value,
    TaskStatus.REVIEW_RUNNING.value,
    TaskStatus.QA_READY.value,
}

RUNNABLE_TASK_STATUSES = {
    TaskStatus.TODO.value,
    TaskStatus.READY.value,
    TaskStatus.REWORK.value,
    TaskStatus.REVIEW_READY.value,
}

ACTIVE_TASK_STATUSES = IN_FLIGHT_TASK_STATUSES | {TaskStatus.REWORK.value}

DISPATCHABLE_PROJECT_STATUSES = {
    ProjectStatus.ACTIVE.value,
    ProjectStatus.PLANNED.value,
    ProjectStatus.INTAKE.value,
    ProjectStatus.BLOCKED.value,
}

TERMINAL_GATE_STATUSES = {
    GateStatus.PASSED.value,
    GateStatus.FAILED.value,
    GateStatus.WAIVED.value,
}


REPOSITORY_SCOPE_ALIASES = {
    "client_product_repo": RepositoryScope.NEW_PRODUCT_REPO.value,
    "client_new_repo": RepositoryScope.NEW_PRODUCT_REPO.value,
    "new_repo": RepositoryScope.NEW_PRODUCT_REPO.value,
    "new_project": RepositoryScope.NEW_PRODUCT_REPO.value,
    "project_new": RepositoryScope.NEW_PRODUCT_REPO.value,
    "existing_product_repo": RepositoryScope.EXISTING_PROJECT_CHANGE.value,
    "existing_repo": RepositoryScope.EXISTING_PROJECT_CHANGE.value,
    "modify_existing_repo": RepositoryScope.EXISTING_PROJECT_CHANGE.value,
    "maintain_existing_repo": RepositoryScope.EXISTING_PROJECT_CHANGE.value,
    "zeus_functionality": RepositoryScope.ZEUS_ONLY.value,
    "zeus_admin": RepositoryScope.ZEUS_ONLY.value,
    "agent_product_capability": RepositoryScope.ZEUS_THEN_RUNTIME.value,
    "commercial_runtime": RepositoryScope.RUNTIME_ONLY.value,
    "runtime": RepositoryScope.RUNTIME_ONLY.value,
    "docs_only": RepositoryScope.DOCS_OR_RESEARCH_ONLY.value,
    "research_only": RepositoryScope.DOCS_OR_RESEARCH_ONLY.value,
}

WORK_INTENT_ALIASES = {
    "create": WorkIntent.CREATE_NEW_PROJECT.value,
    "new": WorkIntent.CREATE_NEW_PROJECT.value,
    "new_project": WorkIntent.CREATE_NEW_PROJECT.value,
    "feature": WorkIntent.ADD_FUNCTIONALITY.value,
    "new_functionality": WorkIntent.ADD_FUNCTIONALITY.value,
    "functionality": WorkIntent.ADD_FUNCTIONALITY.value,
    "modify": WorkIntent.MODIFY_EXISTING_PROJECT.value,
    "change": WorkIntent.MODIFY_EXISTING_PROJECT.value,
    "update_existing": WorkIntent.MODIFY_EXISTING_PROJECT.value,
    "maintenance": WorkIntent.MAINTAIN_EXISTING_PROJECT.value,
    "maintain": WorkIntent.MAINTAIN_EXISTING_PROJECT.value,
    "research": WorkIntent.DOCS_RESEARCH.value,
    "docs": WorkIntent.DOCS_RESEARCH.value,
}

CANONICAL_REPOSITORIES: dict[str, dict[str, str]] = {
    RepositoryScope.ZEUS_ONLY.value: {
        "repo": "SiteOneTech/hermes-agent-original",
        "remote": "https://github.com/SiteOneTech/hermes-agent-original",
        "path": "/home/jean/Projects/hermes-agent-original",
    },
    RepositoryScope.ZEUS_THEN_RUNTIME.value: {
        "repo": "SiteOneTech/hermes-agent-original",
        "remote": "https://github.com/SiteOneTech/hermes-agent-original",
        "path": "/home/jean/Projects/hermes-agent-original",
        "propagation_repo": "SiteOneTech/sitiouno-agent-runtime",
        "propagation_remote": "https://github.com/SiteOneTech/sitiouno-agent-runtime",
        "propagation_path": "/home/jean/Projects/sitiouno-agent-runtime",
    },
    RepositoryScope.RUNTIME_ONLY.value: {
        "repo": "SiteOneTech/sitiouno-agent-runtime",
        "remote": "https://github.com/SiteOneTech/sitiouno-agent-runtime",
        "path": "/home/jean/Projects/sitiouno-agent-runtime",
    },
}

REPOSITORY_SCOPE_LABELS = {
    RepositoryScope.ZEUS_ONLY.value: "Funcionalidad interna de Zeus",
    RepositoryScope.ZEUS_THEN_RUNTIME.value: "Funcionalidad de agente heredable",
    RepositoryScope.RUNTIME_ONLY.value: "Funcionalidad directa del runtime heredado",
    RepositoryScope.EXISTING_PROJECT_CHANGE.value: "Modificar proyecto existente",
    RepositoryScope.NEW_PRODUCT_REPO.value: "Crear proyecto/repositorio nuevo",
    RepositoryScope.DOCS_OR_RESEARCH_ONLY.value: "Documentación o investigación sin repo de código",
}

REPOSITORY_SCOPE_SUMMARIES = {
    RepositoryScope.ZEUS_ONLY.value: "Abrir rama/worktree dentro del fork principal de Zeus; no crear repo nuevo ni propagar al runtime.",
    RepositoryScope.ZEUS_THEN_RUNTIME.value: "Validar primero en Zeus y abrir tarea/PR de propagación al runtime heredado antes del cierre completo.",
    RepositoryScope.RUNTIME_ONLY.value: "Abrir rama/worktree directamente en el runtime heredado; no tocar superficies admin de Zeus.",
    RepositoryScope.EXISTING_PROJECT_CHANGE.value: "Abrir rama/worktree en el repo existente del producto; no arrancar de cero ni crear repo nuevo.",
    RepositoryScope.NEW_PRODUCT_REPO.value: "Crear/usar repo de producto independiente porque el usuario pidió proyecto nuevo o hay lifecycle propio.",
    RepositoryScope.DOCS_OR_RESEARCH_ONLY.value: "No crear repo de código; mantener evidencia en docs/wiki/Notion según corresponda.",
}


def is_terminal_task_status(status: str | None) -> bool:
    return str(status or "") in TERMINAL_TASK_STATUSES


def is_runnable_task_status(status: str | None) -> bool:
    return str(status or "") in RUNNABLE_TASK_STATUSES


def is_in_flight_task_status(status: str | None) -> bool:
    return str(status or "") in IN_FLIGHT_TASK_STATUSES


def _metadata_dict(metadata: dict[str, Any] | None) -> dict[str, Any]:
    return metadata if isinstance(metadata, dict) else {}


def _strategy_dict(metadata: dict[str, Any]) -> dict[str, Any]:
    value = metadata.get("repo_strategy")
    return value if isinstance(value, dict) else {}


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _slug(value: Any) -> str:
    text = _clean(value).lower()
    text = re.sub(r"[^a-z0-9._/-]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-/.")
    return text or "increment"


def normalize_repository_scope(value: Any) -> str | None:
    raw = _clean(value).lower().replace("-", "_").replace(" ", "_")
    if not raw:
        return None
    raw = REPOSITORY_SCOPE_ALIASES.get(raw, raw)
    valid = {scope.value for scope in RepositoryScope}
    return raw if raw in valid else None


def normalize_work_intent(value: Any, repo_scope: str | None = None) -> str:
    raw = _clean(value).lower().replace("-", "_").replace(" ", "_")
    raw = WORK_INTENT_ALIASES.get(raw, raw)
    valid = {intent.value for intent in WorkIntent}
    if raw in valid:
        return raw
    if repo_scope == RepositoryScope.NEW_PRODUCT_REPO.value:
        return WorkIntent.CREATE_NEW_PROJECT.value
    if repo_scope == RepositoryScope.EXISTING_PROJECT_CHANGE.value:
        return WorkIntent.MODIFY_EXISTING_PROJECT.value
    if repo_scope == RepositoryScope.DOCS_OR_RESEARCH_ONLY.value:
        return WorkIntent.DOCS_RESEARCH.value
    return WorkIntent.ADD_FUNCTIONALITY.value


def normalize_repo_remote(remote: Any) -> str:
    value = _clean(remote)
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value.removeprefix("git@github.com:")
    if value.endswith(".git"):
        value = value[:-4]
    return value


def repository_name_from_remote(remote: Any) -> str:
    value = normalize_repo_remote(remote)
    if value.startswith("https://github.com/"):
        return value.removeprefix("https://github.com/").strip("/")
    return ""


def github_repo_web_url(remote: Any) -> str:
    value = normalize_repo_remote(remote)
    return value if value.startswith("https://github.com/") else ""


def github_branch_url(remote: Any, branch: Any) -> str:
    repo = github_repo_web_url(remote)
    branch_value = _clean(branch)
    if not repo or not branch_value:
        return ""
    return f"{repo}/tree/{branch_value}"


def github_blob_url(remote: Any, branch: Any, relative_path: Any) -> str:
    repo = github_repo_web_url(remote)
    branch_value = _clean(branch)
    rel = _clean(relative_path).strip("/")
    if not repo or not branch_value or not rel:
        return ""
    return f"{repo}/blob/{branch_value}/{rel}"


def default_worktree_root(repo_path: Any) -> str:
    value = _clean(repo_path)
    if not value:
        return ""
    return str(Path(value).expanduser().parent / ".worktrees")


def increment_branch_name(project_id: str, increment_key: str, strategy: dict[str, Any] | None = None) -> str:
    strategy = strategy if isinstance(strategy, dict) else {}
    prefix = _clean(strategy.get("branch_prefix")) or f"factory/{_slug(project_id)}/"
    if not prefix.endswith("/"):
        prefix += "/"
    return prefix + _slug(increment_key)


def increment_worktree_path(project_id: str, increment_key: str, strategy: dict[str, Any] | None = None) -> str:
    strategy = strategy if isinstance(strategy, dict) else {}
    root = _clean(strategy.get("worktree_root")) or default_worktree_root(strategy.get("primary_repo_path"))
    if not root:
        return ""
    return str(Path(root).expanduser() / _slug(project_id) / _slug(increment_key))


def build_repository_strategy(
    *,
    project_id: str,
    project_name: str | None = None,
    repo_scope: str | None = None,
    work_intent: str | None = None,
    repo_path: str | None = None,
    repo_remote: str | None = None,
    base_branch: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Normalize G0 Repository Strategy Gate metadata for a Factory project.

    The gate encodes Jean's canonical workflow: if the request is Zeus
    functionality, use the Zeus fork; if it is a new project, create/use a new
    product repo; if it modifies an existing product, branch that existing repo;
    every deliverable then gets its own branch/worktree.
    """

    metadata = _metadata_dict(metadata)
    existing = _strategy_dict(metadata)
    raw_scope = repo_scope or existing.get("repo_scope") or metadata.get("repo_scope") or metadata.get("repository_scope")
    scope = normalize_repository_scope(raw_scope)
    missing_fields: list[str] = []
    if not scope:
        missing_fields.append("repo_scope")

    intent = normalize_work_intent(work_intent or existing.get("work_intent") or metadata.get("work_intent"), scope)
    canonical = CANONICAL_REPOSITORIES.get(scope or "", {})
    primary_remote = normalize_repo_remote(
        repo_remote or existing.get("primary_repo_remote") or metadata.get("primary_repo_remote") or canonical.get("remote")
    )
    primary_path = _clean(repo_path or existing.get("primary_repo_path") or metadata.get("primary_repo_path") or canonical.get("path"))
    primary_repo = _clean(existing.get("primary_repo") or metadata.get("primary_repo") or canonical.get("repo") or repository_name_from_remote(primary_remote))
    branch_base = _clean(base_branch or existing.get("base_branch") or metadata.get("base_branch")) or "main"
    branch_prefix = _clean(existing.get("branch_prefix") or metadata.get("branch_prefix")) or f"factory/{_slug(project_id)}/"
    if not branch_prefix.endswith("/"):
        branch_prefix += "/"
    worktree_root = _clean(existing.get("worktree_root") or metadata.get("worktree_root")) or default_worktree_root(primary_path)
    standalone_repo_required = bool(scope == RepositoryScope.NEW_PRODUCT_REPO.value)
    propagation_required = bool(scope == RepositoryScope.ZEUS_THEN_RUNTIME.value)

    if scope in {
        RepositoryScope.ZEUS_ONLY.value,
        RepositoryScope.ZEUS_THEN_RUNTIME.value,
        RepositoryScope.RUNTIME_ONLY.value,
        RepositoryScope.EXISTING_PROJECT_CHANGE.value,
    }:
        if not primary_repo and not primary_remote:
            missing_fields.append("primary_repo")
        if not primary_path and not primary_remote:
            missing_fields.append("primary_repo_path_or_remote")
    if scope == RepositoryScope.EXISTING_PROJECT_CHANGE.value and not (primary_path or primary_remote):
        missing_fields.append("existing_project_repo")
    if scope == RepositoryScope.NEW_PRODUCT_REPO.value:
        approval = existing.get("new_repo_approval") or metadata.get("new_repo_approval") or metadata.get("new_repo_approved_by")
        if not approval and not (primary_repo or primary_remote):
            missing_fields.append("new_repo_approval_or_repo")

    status = "missing" if missing_fields else "passed"
    propagation_repo = _clean(existing.get("propagation_repo") or metadata.get("propagation_repo") or canonical.get("propagation_repo"))
    propagation_remote = normalize_repo_remote(existing.get("propagation_remote") or metadata.get("propagation_remote") or canonical.get("propagation_remote"))
    links = {
        "repo_url": github_repo_web_url(primary_remote),
        "base_branch_url": github_branch_url(primary_remote, branch_base),
        "propagation_repo_url": github_repo_web_url(propagation_remote),
    }
    return {
        "status": status,
        "gate": "G0 Repository Strategy Gate",
        "project_id": _clean(project_id),
        "project_name": _clean(project_name),
        "repo_scope": scope,
        "work_intent": intent,
        "decision_label": REPOSITORY_SCOPE_LABELS.get(scope or "", "Estrategia de repositorio pendiente"),
        "decision_summary": REPOSITORY_SCOPE_SUMMARIES.get(scope or "", "La Factory debe decidir si esto es Zeus, runtime, repo existente, proyecto nuevo o solo documentación antes de organizar tareas."),
        "primary_repo": primary_repo,
        "primary_repo_remote": primary_remote,
        "primary_repo_path": primary_path,
        "base_branch": branch_base,
        "branch_prefix": branch_prefix,
        "worktree_root": worktree_root,
        "worktree_policy": "per_deliverable",
        "standalone_repo_required": standalone_repo_required,
        "new_repo_approval_required": standalone_repo_required,
        "new_repo_approval": existing.get("new_repo_approval") or metadata.get("new_repo_approval") or metadata.get("new_repo_approved_by"),
        "propagation_required": propagation_required,
        "propagation_repo": propagation_repo,
        "propagation_remote": propagation_remote,
        "missing_fields": sorted(set(missing_fields)),
        "links": {key: value for key, value in links.items() if value},
    }


def repository_strategy_from_project(project: dict[str, Any]) -> dict[str, Any]:
    metadata = _metadata_dict(project.get("metadata") if isinstance(project, dict) else None)
    return build_repository_strategy(
        project_id=_clean(project.get("project_id")) if isinstance(project, dict) else "",
        project_name=_clean(project.get("name")) if isinstance(project, dict) else "",
        repo_path=_clean(project.get("repo_path")) if isinstance(project, dict) else "",
        repo_remote=_clean(project.get("repo_remote")) if isinstance(project, dict) else "",
        base_branch=_clean(project.get("base_branch")) if isinstance(project, dict) else "",
        metadata=metadata,
    )


def repository_strategy_is_complete(strategy: dict[str, Any] | None) -> bool:
    return bool(isinstance(strategy, dict) and strategy.get("status") == "passed" and strategy.get("repo_scope") and not strategy.get("missing_fields"))

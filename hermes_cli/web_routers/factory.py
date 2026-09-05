"""Factory dashboard routes: the SitioUno Software Factory status surface.

Read-only projections over the factory control-plane backend (projects, tasks, gates, events,
artifacts, agents, findings) plus the handoff/Notion publishing actions the dashboard triggers.
Helpers stay module-local; ``hermes_cli.web_server`` re-exports them so
``web_server.<name>`` keeps resolving for callers and tests.
"""

import asyncio
import json
import logging
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException

from hermes_cli import factory_contracts
from hermes_cli.config import load_env

# Same logger the handlers used before extraction (identical logger object).
_log = logging.getLogger("hermes_cli.web_server")
router = APIRouter()


# ---------------------------------------------------------------------------
# Factory dashboard — read-only status surface for SitioUno Software Factory.
# ---------------------------------------------------------------------------

_FACTORY_REQUIRED_DOCS = (
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

_FACTORY_DONE_STATUSES = {"done", "completed", "verified", "accepted", "cancelled", "superseded"}
_FACTORY_OPEN_STATUSES = {"todo", "ready", "in_progress", "blocked", "review_pending_human"}


def _factory_json_load(value: Any, fallback: Any) -> Any:
    if value in (None, ""):
        return fallback
    try:
        return json.loads(value)
    except Exception:
        return fallback


def _factory_counts(rows: List[Dict[str, Any]], key: str = "status") -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for row in rows:
        status = str(row.get(key) or "unknown")
        counts[status] = counts.get(status, 0) + 1
    return counts


def _factory_gate_created_at(gate: Dict[str, Any]) -> str:
    return str(gate.get("created_at") or gate.get("timestamp") or "")


def _factory_sort_gates_desc(gates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        gates,
        key=lambda gate: (_factory_gate_created_at(gate), int(gate.get("gate_id") or 0)),
        reverse=True,
    )


def _factory_effective_gates(gates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return the latest project-stage gate for each gate type.

    Factory keeps gate rows as an audit log: a stage can have an early
    ``pending`` row, a failed rework row, and then a later ``passed`` row.  The
    dashboard and reconcilers must reason from the latest stage decision rather
    than treating all historical pending/failed rows as live blockers.
    """

    latest_by_type: dict[str, Dict[str, Any]] = {}
    for gate in _factory_sort_gates_desc(gates):
        gate_type = str(gate.get("gate_type") or "").strip()
        if not gate_type or gate_type in latest_by_type:
            continue
        latest_by_type[gate_type] = gate
    return _factory_sort_gates_desc(list(latest_by_type.values()))


def _factory_project_artifact_dir(project: Dict[str, Any]) -> Path | None:
    repo_path = str(project.get("repo_path") or "").strip()
    if not repo_path:
        return None
    project_id = str(project.get("project_id") or "").strip()
    metadata = _factory_project_metadata(project)
    raw_dir = str(metadata.get("artifact_dir") or "").strip()
    relative = raw_dir or f"factory/projects/{project_id}"
    return Path(repo_path).expanduser() / relative


def _factory_repo_web_base(project: Dict[str, Any]) -> str:
    """Return a browser-openable repository URL when the project remote is GitHub."""

    remote = str(project.get("repo_remote") or "").strip()
    if not remote:
        return ""
    if remote.startswith("git@github.com:"):
        remote = "https://github.com/" + remote.removeprefix("git@github.com:")
    if remote.endswith(".git"):
        remote = remote[:-4]
    if remote.startswith("https://github.com/"):
        return remote
    return ""


def _factory_doc_external_url(project: Dict[str, Any], path: Path) -> str:
    """Create a direct web link for a project-local document when possible."""

    repo_base = _factory_repo_web_base(project)
    repo_path = str(project.get("repo_path") or "").strip()
    if not repo_base or not repo_path:
        return ""
    try:
        rel = path.resolve().relative_to(Path(repo_path).expanduser().resolve()).as_posix()
    except Exception:
        return ""
    branch = str(project.get("base_branch") or "main").strip() or "main"
    branch_slug = urllib.parse.quote(branch, safe="")
    rel_slug = urllib.parse.quote(rel, safe="/")
    return f"{repo_base}/blob/{branch_slug}/{rel_slug}"


def _factory_repository_strategy_card(project: Dict[str, Any], tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    strategy = factory_contracts.repository_strategy_from_project(project)
    current_task = (tasks or [None])[0] if tasks else None
    branch = str((current_task or {}).get("branch") or "").strip()
    worktree_path = str((current_task or {}).get("worktree_path") or "").strip()
    repo_remote = str(strategy.get("primary_repo_remote") or project.get("repo_remote") or "").strip()
    base_branch = str(strategy.get("base_branch") or project.get("base_branch") or "main").strip() or "main"
    branch_url = factory_contracts.github_branch_url(repo_remote, branch) if branch else ""
    return {
        "gate": strategy.get("gate") or "G0 Repository Strategy Gate",
        "status": strategy.get("status") or "missing",
        "repo_scope": strategy.get("repo_scope"),
        "work_intent": strategy.get("work_intent"),
        "decision_label": strategy.get("decision_label"),
        "decision_summary": strategy.get("decision_summary"),
        "primary_repo": strategy.get("primary_repo"),
        "primary_repo_remote": repo_remote,
        "primary_repo_path": strategy.get("primary_repo_path") or project.get("repo_path"),
        "base_branch": base_branch,
        "branch_prefix": strategy.get("branch_prefix"),
        "branch": branch,
        "worktree_path": worktree_path,
        "worktree_policy": strategy.get("worktree_policy") or "per_deliverable",
        "standalone_repo_required": bool(strategy.get("standalone_repo_required")),
        "propagation_required": bool(strategy.get("propagation_required")),
        "missing_fields": strategy.get("missing_fields") or [],
        "links": strategy.get("links") or {},
        "repo_url": (strategy.get("links") or {}).get("repo_url") or factory_contracts.github_repo_web_url(repo_remote),
        "base_branch_url": (strategy.get("links") or {}).get("base_branch_url") or factory_contracts.github_branch_url(repo_remote, base_branch),
        "branch_url": branch_url,
    }


def _factory_markdown_link(label: str, url: str) -> str:
    clean_label = str(label or "").replace("[", "\\[").replace("]", "\\]").strip() or "link"
    clean_url = str(url or "").strip()
    if not clean_url:
        return f"`{clean_label}`"
    return f"[{clean_label}]({clean_url})"


def _factory_doc_inventory(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    base = _factory_project_artifact_dir(project)
    backend_status = project.get("document_status") if isinstance(project.get("document_status"), list) else []
    if backend_status:
        docs: list[dict[str, Any]] = []
        for row in backend_status:
            name = str(row.get("file_name") or row.get("name") or "").strip()
            rel_path = str(row.get("path") or name).strip()
            path = Path(rel_path)
            if base is not None and not path.is_absolute():
                artifact_dir_name = base.name
                parts = path.parts
                if artifact_dir_name in parts:
                    path = Path(str(project.get("repo_path") or "")) / path
                else:
                    path = base / name
            exists = bool(row.get("exists"))
            try:
                size = path.stat().st_size if exists and path.exists() else 0
            except Exception:
                size = 0
            docs.append({
                "name": name,
                "file_name": name,
                "path": rel_path,
                "url": _factory_doc_external_url(project, path) if exists else "",
                "exists": exists,
                "size": size,
                "category": row.get("category"),
                "indexed": bool(row.get("indexed")),
                "committed": bool(row.get("committed")),
                "validated": bool(row.get("validated")),
                "reviewed": bool(row.get("reviewed")),
                "blocking": bool(row.get("blocking")),
                "owner": row.get("owner"),
                "reviewer": row.get("reviewer"),
                "git_status": row.get("git_status"),
            })
        return docs
    if base is None:
        return []
    docs = []
    for name in _FACTORY_REQUIRED_DOCS:
        path = base / name
        try:
            exists = path.is_file()
            size = path.stat().st_size if exists else 0
        except Exception:
            exists = False
            size = 0
        docs.append({
            "name": name,
            "file_name": name,
            "path": str(path),
            "url": _factory_doc_external_url(project, path) if exists else "",
            "exists": exists,
            "size": size,
            "category": "g1_required",
            "indexed": exists,
            "committed": exists,
            "validated": False,
            "reviewed": False,
            "blocking": not exists,
            "owner": None,
            "reviewer": None,
            "git_status": None,
        })
    return docs


def _factory_project_metadata(project: Dict[str, Any]) -> Dict[str, Any]:
    raw = project.get("metadata")
    if raw is None:
        raw = project.get("metadata_json")
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        parsed = _factory_json_load(raw, {})
        return parsed if isinstance(parsed, dict) else {}
    return {}


def _factory_notion_page_url(page_id: str) -> str:
    compact = page_id.replace("-", "")
    return f"https://www.notion.so/{compact}" if compact else ""


def _factory_project_notion(project: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """Return the real project Notion tracker, not the shared template link."""

    metadata = _factory_project_metadata(project)
    url = ""
    for key in (
        "notion_tracker_url",
        "notion_project_url",
        "notion_page_url",
        "notion_url",
    ):
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            url = value.strip()
            break

    page_id = ""
    for key in (
        "notion_tracker_page_id",
        "notion_project_page_id",
        "notion_page_id",
    ):
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            page_id = value.strip()
            break

    if not url and page_id:
        url = _factory_notion_page_url(page_id)
    if not url and not page_id:
        return None
    return {"url": url, "page_id": page_id}


def _factory_notion_template(project: Dict[str, Any]) -> Optional[Dict[str, str]]:
    metadata = _factory_project_metadata(project)
    url = str(metadata.get("notion_template_url") or "").strip()
    page_id = str(metadata.get("notion_template_page_id") or "").strip()
    if not url and page_id:
        url = _factory_notion_page_url(page_id)
    if not url and not page_id:
        return None
    return {"url": url, "page_id": page_id}


def _factory_utc_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _factory_project_dashboard(
    project: Dict[str, Any],
    tasks: List[Dict[str, Any]],
    gates: List[Dict[str, Any]],
    events: List[Dict[str, Any]],
    task_runs: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    project_id = str(project.get("project_id") or "")
    project_tasks = [row for row in tasks if row.get("project_id") == project_id]
    project_gates = _factory_sort_gates_desc([row for row in gates if row.get("project_id") == project_id])
    effective_gates = _factory_effective_gates(project_gates)
    project_events = [row for row in events if row.get("project_id") == project_id]
    project_runs = [row for row in (task_runs or []) if row.get("project_id") == project_id]
    open_tasks = [
        task for task in project_tasks if str(task.get("status") or "") not in _FACTORY_DONE_STATUSES
    ]
    blocked_tasks = [task for task in project_tasks if str(task.get("status") or "") == "blocked"]
    review_tasks = [
        task for task in project_tasks if str(task.get("status") or "") == "review_pending_human"
    ]
    missing_evidence = [
        task for task in project_tasks if str(task.get("evidence_status") or "") == "missing"
    ]
    self_approved = [
        task
        for task in project_tasks
        if task.get("owner_agent_id")
        and task.get("owner_agent_id") == task.get("reviewer_agent_id")
    ]
    failed_gates = [gate for gate in effective_gates if str(gate.get("status") or "") == "failed"]
    pending_gates = [gate for gate in effective_gates if str(gate.get("status") or "") == "pending"]
    docs = _factory_doc_inventory(project)
    missing_docs = [doc for doc in docs if not doc.get("exists")]
    g1_blocking_docs = [doc for doc in docs if doc.get("category") == "g1_required" and doc.get("blocking")]
    missing_notion = _factory_project_notion(project) is None
    repo_strategy_card = _factory_repository_strategy_card(project, project_tasks)
    missing_repo_strategy = repo_strategy_card.get("status") != "passed"

    latest_open = sorted(open_tasks, key=lambda r: str(r.get("updated_at") or ""), reverse=True)
    latest_any = sorted(project_tasks, key=lambda r: str(r.get("updated_at") or ""), reverse=True)
    current_task = (latest_open or latest_any or [None])[0]

    summary_lines: list[str] = []
    if current_task:
        status = current_task.get("status") or "unknown"
        summary_lines.append(f"Última tarea relevante: {current_task.get('title')} ({status}).")
    if open_tasks:
        summary_lines.append(f"Hay {len(open_tasks)} tarea(s) abiertas; {len(review_tasks)} en revisión humana.")
    else:
        summary_lines.append("No hay tareas operativas abiertas en Factory DB para este proyecto.")
    if effective_gates:
        passed = sum(1 for gate in effective_gates if str(gate.get("status") or "") == "passed")
        summary_lines.append(
            f"Gates efectivos: {passed}/{len(effective_gates)} pasados "
            f"(histórico: {len(project_gates)} registros)."
        )
    if self_approved:
        summary_lines.append(
            f"{len(self_approved)} tarea(s) tienen mismo owner/reviewer; requiere revisión independiente."
        )
    if g1_blocking_docs:
        summary_lines.append(f"G1 documental bloqueado: {len(g1_blocking_docs)} documento(s) no están listos.")
    elif docs:
        summary_lines.append("G1 documental listo: todos los documentos requeridos existen, están indexados, commiteados, validados y revisados.")
    if missing_docs:
        summary_lines.append(f"Faltan {len(missing_docs)} documento(s) factory requeridos en el repo.")
    if missing_notion:
        summary_lines.append("Falta página Notion PM del proyecto; debe generarse desde la plantilla Factory.")
    if missing_repo_strategy:
        summary_lines.append("Falta decisión G0 de repositorio: Zeus, runtime, repo existente, repo nuevo o docs/research.")

    findings: list[dict[str, Any]] = []
    if self_approved:
        findings.append(
            {
                "severity": "warning",
                "code": "self_approval",
                "title": "Separación de roles incompleta",
                "message": "Hay tareas donde owner y reviewer son el mismo agente.",
                "count": len(self_approved),
            }
        )
    if missing_evidence:
        findings.append(
            {
                "severity": "warning",
                "code": "missing_evidence",
                "title": "Evidencia incompleta",
                "message": "Algunas tareas aún no tienen evidencia verificada.",
                "count": len(missing_evidence),
            }
        )
    if failed_gates:
        findings.append(
            {
                "severity": "destructive",
                "code": "failed_gates",
                "title": "Gates fallidos",
                "message": "Existen gates con status failed.",
                "count": len(failed_gates),
            }
        )
    if pending_gates:
        findings.append(
            {
                "severity": "warning",
                "code": "pending_gates",
                "title": "Gates pendientes",
                "message": "Existen gates sin cerrar.",
                "count": len(pending_gates),
            }
        )
    if g1_blocking_docs:
        findings.append(
            {
                "severity": "warning",
                "code": "g1_documentary_readiness_blockers",
                "title": "G1 Documentary Readiness bloqueado",
                "message": "Hay documentos G1 que no están listos para implementación: deben existir, estar indexados, commiteados, validados y revisados.",
                "count": len(g1_blocking_docs),
            }
        )
    if missing_docs:
        findings.append(
            {
                "severity": "warning",
                "code": "missing_factory_docs",
                "title": "Documentación Factory incompleta",
                "message": "Faltan documentos mínimos en factory/ para metodología completa.",
                "count": len(missing_docs),
            }
        )
    if missing_notion:
        findings.append(
            {
                "severity": "warning",
                "code": "missing_notion_project",
                "title": "Notion PM faltante",
                "message": "El proyecto no tiene página Notion propia; solo una plantilla no cuenta como documentación PM.",
                "count": 1,
            }
        )
    if missing_repo_strategy:
        findings.append(
            {
                "severity": "warning",
                "code": "missing_repository_strategy",
                "title": "G0 Repository Strategy Gate faltante",
                "message": "Antes de arrancar o retomar, Factory debe decidir si trabaja en Zeus, runtime, un repo existente, un repo nuevo o solo docs/research.",
                "count": 1,
            }
        )

    active_runs = [run for run in project_runs if str(run.get("status") or "") in {"queued", "running"}]
    active_run = sorted(active_runs, key=lambda r: str(r.get("heartbeat_at") or r.get("started_at") or ""), reverse=True)[0] if active_runs else None
    project_status = str(project.get("status") or "").lower()
    static_project_statuses = {"blocked", "cancelled", "closed", "completed", "delivery_hold", "hold", "on_hold", "paused"}
    workflow_stage = "running" if active_run else "blocked" if blocked_tasks else "review" if review_tasks else "planned" if open_tasks else "completed"
    workflow_operative = bool(active_run or project.get("autonomous_enabled")) and project_status not in static_project_statuses
    workflow = {
        "operative": workflow_operative,
        "stage": workflow_stage,
        "worker": (active_run or {}).get("worker_profile") if active_run else None,
        "heartbeat_at": (active_run or {}).get("heartbeat_at") if active_run else None,
        "current_task_id": (current_task or {}).get("task_id") if current_task else None,
        "single_active_increment": True,
    }

    return {
        "task_counts": _factory_counts(project_tasks),
        "gate_counts": _factory_counts(project_gates),
        "effective_gate_counts": _factory_counts(effective_gates),
        "open_task_count": len(open_tasks),
        "blocked_task_count": len(blocked_tasks),
        "blocked_tasks": blocked_tasks,
        "review_task_count": len(review_tasks),
        "missing_evidence_count": len(missing_evidence),
        "self_approved_task_count": len(self_approved),
        "latest_event": project_events[0] if project_events else None,
        "current_task": current_task,
        "active_run": active_run,
        "effective_gates": effective_gates,
        "recent_runs": sorted(project_runs, key=lambda r: str(r.get("started_at") or ""), reverse=True)[:5],
        "workflow": workflow,
        "repo_strategy_card": repo_strategy_card,
        "required_docs": docs,
        "document_status": docs,
        "g1_blocking_documents": g1_blocking_docs,
        "g1_blocking_count": len(g1_blocking_docs),
        "missing_required_docs": missing_docs,
        "findings": findings,
        "quick_status": " ".join(summary_lines),
    }


@router.get("/api/factory/status")
async def get_factory_dashboard(project_id: Optional[str] = None, force: bool = False):
    """Read-only Factory dashboard payload from the canonical Factory backend."""
    try:
        from hermes_cli import factory_backend

        backend = factory_backend.get_backend()
        force_refresh: dict[str, Any] | None = None
        if force:
            initial = backend.status(project_id)
            monitor = backend.monitor_runs() if hasattr(backend, "monitor_runs") else {}
            reconciled: list[dict[str, Any]] = []
            project_ids = [str(row.get("project_id")) for row in initial.get("projects", []) if row.get("project_id")]
            for pid in project_ids:
                if hasattr(backend, "reconcile_project"):
                    reconciled.append(backend.reconcile_project(pid))
            force_refresh = {"monitor": monitor, "reconciled": reconciled}
        payload = backend.status(project_id)
        projects = payload.get("projects", [])
        lanes = payload.get("lanes", [])
        tasks = payload.get("tasks", [])
        gates = _factory_sort_gates_desc(payload.get("gates", []))
        events = payload.get("events", [])
        artifacts = payload.get("artifacts", [])
        task_runs = payload.get("task_runs", [])
        human_questions = payload.get("human_questions", [])
        agents = payload.get("agents", [])
        db_backend = payload.get("db_backend", "agent_core_postgres")
        db_path = payload.get("db_path", "agent_core_postgres:zeus_agent.factory")

        for lane in lanes:
            metadata_raw = lane.get("metadata")
            metadata: Dict[str, Any] = metadata_raw if isinstance(metadata_raw, dict) else {}
            execution_surface = lane.get("execution_surface") or metadata.get("execution_surface") or "factory"
            lane["execution_surface"] = execution_surface
            if execution_surface != "kanban_bridge":
                lane.pop("kanban_board", None)
                metadata.pop("kanban_board", None)
        for task in tasks:
            task.pop("kanban_id", None)

        project_dashboards = {
            str(project.get("project_id")): _factory_project_dashboard(
                project,
                tasks,
                gates,
                events,
                task_runs,
            )
            for project in projects
        }
        for project in projects:
            project["dashboard"] = project_dashboards.get(str(project.get("project_id")))

        findings = [
            finding
            for dashboard in project_dashboards.values()
            for finding in dashboard.get("findings", [])
        ]
        counts = {
            "projects": len(projects),
            "lanes": len(lanes),
            "tasks": len(tasks),
            "gates": len(gates),
            "events": len(events),
            "artifacts": len(artifacts),
            "agents": len(agents),
            "task_runs": len(task_runs),
            "human_questions": len(human_questions),
            "open_tasks": sum(d.get("open_task_count", 0) for d in project_dashboards.values()),
            "active_runs": sum(1 for run in task_runs if str(run.get("status") or "") in {"queued", "running"}),
            "findings": len(findings),
        }
        return {
            "db_backend": db_backend,
            "db_path": db_path,
            "server_time": _factory_utc_now(),
            "force_refresh": force_refresh,
            "projects": projects,
            "lanes": lanes,
            "tasks": tasks,
            "gates": gates,
            "events": events,
            "artifacts": artifacts,
            "task_runs": task_runs,
            "human_questions": human_questions,
            "agents": agents,
            "counts": counts,
            "findings": findings,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Factory dashboard failed: {exc}") from exc


def _factory_handoff_prompt(payload: Dict[str, Any], project: Dict[str, Any]) -> str:
    project_id = str(project.get("project_id") or "")
    dashboard = project.get("dashboard") or {}
    tasks = [task for task in payload.get("tasks", []) if task.get("project_id") == project_id]
    gates = [gate for gate in payload.get("gates", []) if gate.get("project_id") == project_id]
    notion = _factory_project_notion(project)
    template = _factory_notion_template(project)
    findings = dashboard.get("findings") or []
    open_tasks = [task for task in tasks if str(task.get("status") or "") not in _FACTORY_DONE_STATUSES]
    recent_tasks = sorted(tasks, key=lambda row: str(row.get("updated_at") or row.get("created_at") or ""), reverse=True)[:8]

    task_lines = [
        f"- {task.get('task_id')}: {task.get('title')} [{task.get('status')}] owner={task.get('owner_agent_id') or task.get('owner_profile') or '—'}"
        for task in recent_tasks
    ]
    finding_lines = [f"- {f.get('code')}: {f.get('message')}" for f in findings]

    return "\n".join(
        [
            "Retomar proyecto Factory desde Dashboard.",
            "",
            f"Proyecto: {project.get('name')} ({project_id})",
            f"Status Factory DB: {project.get('status')} · metodología: {project.get('methodology')} · riesgo: {project.get('risk_level')}",
            f"Repo: {project.get('repo_path') or '—'}",
            f"Notion PM: {notion['url'] if notion else 'ANOMALÍA: falta página Notion propia del proyecto'}",
            f"Plantilla Notion: {template['url'] if template else '—'}",
            f"Resumen rápido DB: {dashboard.get('quick_status') or '—'}",
            f"Tareas abiertas: {len(open_tasks)} · Gates registrados: {len(gates)}",
            "",
            "Tareas recientes:",
            *(task_lines or ["- —"]),
            "",
            "Anomalías detectadas:",
            *(finding_lines or ["- Ninguna detectada por Factory DB."]),
            "",
            "Instrucción para Zeus:",
            "1. Carga/usa el skill software-factory-orchestration y trata Factory DB como fuente operativa de verdad.",
            "2. No le pidas al usuario repetir contexto: verifica en vivo `hermes factory status --json` para este project_id, revisa repo/factory/ y Notion si existe.",
            "3. Si el status es intake o faltan docs/Notion/gates, preséntalo como deuda metodológica real, no como proyecto cerrado.",
            "4. Entrega un resumen breve del estado verificado y pregunta a Jean cómo quiere continuar este proyecto.",
        ]
    )


def _factory_markdown_cell(value: Any) -> str:
    text = str(value or "—").replace("\n", " ").replace("|", "\\|").strip()
    return text or "—"


def _factory_notion_markdown(payload: Dict[str, Any], project: Dict[str, Any]) -> str:
    project_id = str(project.get("project_id") or "")
    dashboard = project.get("dashboard") or {}
    tasks = [task for task in payload.get("tasks", []) if task.get("project_id") == project_id]
    gates = [gate for gate in payload.get("gates", []) if gate.get("project_id") == project_id]
    events = [event for event in payload.get("events", []) if event.get("project_id") == project_id]
    task_runs = [run for run in payload.get("task_runs", []) if run.get("project_id") == project_id]
    findings = dashboard.get("findings") or []
    docs = dashboard.get("required_docs") or []
    repo_base = _factory_repo_web_base(project)
    repo_link = _factory_markdown_link(repo_base or str(project.get("repo_path") or "Repo"), repo_base)
    metadata = _factory_project_metadata(project)
    runtime_url = str(metadata.get("runtime_url") or metadata.get("preview_url") or metadata.get("sandbox_url") or "").strip()
    task_rows = sorted(tasks, key=lambda row: (int(row.get("priority") or 999), str(row.get("updated_at") or "")))[:25]
    gate_rows = gates[:25]
    event_rows = sorted(events, key=lambda row: str(row.get("created_at") or ""), reverse=True)[:12]
    run_rows = sorted(task_runs, key=lambda row: str(row.get("started_at") or ""), reverse=True)[:10]
    current_task = dashboard.get("current_task") or {}
    active_run = dashboard.get("active_run") or {}

    def task_metadata(row: Dict[str, Any]) -> Dict[str, Any]:
        raw = row.get("metadata")
        if isinstance(raw, dict):
            return raw
        parsed = _factory_json_load(raw, {}) if isinstance(raw, str) else {}
        return parsed if isinstance(parsed, dict) else {}

    def sort_int(value: Any, default: int = 999_999) -> int:
        try:
            return int(value)
        except Exception:
            return default

    terminal_increment_rows = [
        task
        for task in tasks
        if str(task.get("status") or "").lower() in _FACTORY_DONE_STATUSES
        and (
            task.get("increment_key")
            or task.get("increment_order") is not None
            or task_metadata(task).get("closure_source") == "factory_task_close"
        )
    ]
    terminal_increment_rows = sorted(
        terminal_increment_rows,
        key=lambda task: (
            sort_int(task.get("increment_order"), sort_int(task.get("priority"))),
            str(task.get("finished_at") or task.get("updated_at") or task.get("task_id") or ""),
        ),
    )[:40]

    task_table = ["| ID | Tarea | Estado | Owner | Evidencia |", "|---|---|---|---|---|"]
    task_table.extend(
        "| "
        + " | ".join(
            [
                _factory_markdown_cell(task.get("task_id")),
                _factory_markdown_cell(task.get("title")),
                _factory_markdown_cell(task.get("status")),
                _factory_markdown_cell(task.get("owner_agent_id") or task.get("owner_profile")),
                _factory_markdown_cell(task.get("evidence_status")),
            ]
        )
        + " |"
        for task in task_rows
    )
    if len(task_table) == 2:
        task_table.append("| — | — | — | — | — |")

    gate_table = ["| Gate | Estado | Reviewer | Fecha |", "|---|---|---|---|"]
    gate_table.extend(
        "| "
        + " | ".join(
            [
                _factory_markdown_cell(gate.get("gate_type")),
                _factory_markdown_cell(gate.get("status")),
                _factory_markdown_cell(gate.get("reviewer")),
                _factory_markdown_cell(gate.get("created_at") or gate.get("timestamp")),
            ]
        )
        + " |"
        for gate in gate_rows
    )
    if len(gate_table) == 2:
        gate_table.append("| — | — | — | — |")

    docs_ready = sum(1 for doc in docs if doc.get("exists"))
    executive_table = [
        "| Área | Señal | Lectura ejecutiva |",
        "|---|---:|---|",
        f"| Status DB | `{_factory_markdown_cell(project.get('status'))}` | {_factory_markdown_cell(dashboard.get('quick_status') or 'Sin resumen DB.')} |",
        f"| Tareas abiertas | {_factory_markdown_cell(dashboard.get('open_task_count'))} | blocked={_factory_markdown_cell(dashboard.get('blocked_task_count'))} · revisión humana={_factory_markdown_cell(dashboard.get('review_task_count'))} |",
        f"| Gates | {_factory_markdown_cell((dashboard.get('effective_gate_counts') or dashboard.get('gate_counts') or {}).get('passed', 0))} passed | failed={_factory_markdown_cell((dashboard.get('effective_gate_counts') or dashboard.get('gate_counts') or {}).get('failed', 0))} · pending={_factory_markdown_cell((dashboard.get('effective_gate_counts') or dashboard.get('gate_counts') or {}).get('pending', 0))} |",
        f"| Docs Factory | {docs_ready}/{len(docs)} | Cada doc existente debe abrir desde link directo. |",
        f"| Run activo | `{_factory_markdown_cell(active_run.get('status'))}` | worker={_factory_markdown_cell(active_run.get('worker_profile'))} · task={_factory_markdown_cell(active_run.get('task_id'))} |",
    ]

    quick_links = [
        f"- **Repo:** {repo_link}",
        f"- **Worktree local:** `{project.get('repo_path') or '—'}`",
        f"- **Branch base:** `{project.get('base_branch') or 'main'}`",
        f"- **Runtime / preview:** {_factory_markdown_link(runtime_url, runtime_url) if runtime_url else '—'}",
        "- **Factory DB:** Agent Core Postgres `factory.*`",
    ]

    doc_table = ["| Documento | Estado | Abrir | Tamaño |", "|---|---|---|---:|"]
    for doc in docs:
        name = str(doc.get("name") or "—")
        exists = bool(doc.get("exists"))
        url = str(doc.get("url") or "").strip()
        location = _factory_markdown_link(name, url) if exists and url else f"`{doc.get('path') or name}`"
        try:
            size = int(doc.get("size") or 0)
        except Exception:
            size = 0
        size_label = "—" if size <= 0 else f"{size / 1024:.1f} KB"
        doc_table.append(
            "| "
            + " | ".join(
                [
                    _factory_markdown_cell(name),
                    "✅ current" if exists else "⚠️ missing",
                    location,
                    _factory_markdown_cell(size_label),
                ]
            )
            + " |"
        )
    if len(doc_table) == 2:
        doc_table.append("| — | — | — | — |")

    closure_table = ["| Secuencia | Incremento | Tarea | Cierre post-acción | Evidencia |", "|---:|---|---|---|---|"]
    for task in terminal_increment_rows:
        metadata = task_metadata(task)
        evidence = metadata.get("evidence") if isinstance(metadata.get("evidence"), dict) else {}
        evidence_bits: list[str] = []
        if isinstance(evidence, dict):
            for key in ("commit", "pr", "tests", "artifact", "artifact_path", "url"):
                value = evidence.get(key)
                if value:
                    evidence_bits.append(f"{key}={value}")
        sequence = task.get("increment_order") if task.get("increment_order") is not None else task.get("priority")
        increment = task.get("increment_key") or task.get("task_id") or "—"
        summary = task.get("result_summary") or metadata.get("summary") or "—"
        closed_at = task.get("finished_at") or task.get("updated_at") or "—"
        closure_table.append(
            "| "
            + " | ".join(
                [
                    _factory_markdown_cell(sequence),
                    _factory_markdown_cell(increment),
                    _factory_markdown_cell(task.get("title") or task.get("task_id")),
                    _factory_markdown_cell(f"{closed_at} · {summary}"),
                    _factory_markdown_cell("; ".join(evidence_bits) or task.get("evidence_status") or "—"),
                ]
            )
            + " |"
        )
    if len(closure_table) == 2:
        closure_table.append("| — | — | — | — | — |")

    event_table = ["| Fecha | Actor | Evento | Mensaje |", "|---|---|---|---|"]
    event_table.extend(
        "| "
        + " | ".join(
            [
                _factory_markdown_cell(event.get("created_at")),
                _factory_markdown_cell(event.get("actor")),
                _factory_markdown_cell(event.get("event_type")),
                _factory_markdown_cell(event.get("message")),
            ]
        )
        + " |"
        for event in event_rows
    )
    if len(event_table) == 2:
        event_table.append("| — | — | — | — |")

    run_table = ["| Run | Task | Worker | Estado | Inicio | Evidencia |", "|---|---|---|---|---|---|"]
    run_table.extend(
        "| "
        + " | ".join(
            [
                _factory_markdown_cell(run.get("run_id")),
                _factory_markdown_cell(run.get("task_id")),
                _factory_markdown_cell(run.get("worker_profile")),
                _factory_markdown_cell(run.get("status")),
                _factory_markdown_cell(run.get("started_at")),
                _factory_markdown_cell(run.get("log_path") or run.get("prompt_path") or "—"),
            ]
        )
        + " |"
        for run in run_rows
    )
    if len(run_table) == 2:
        run_table.append("| — | — | — | — | — | — |")

    current_task_lines = [
        f"- **Tarea actual/relevante:** `{current_task.get('task_id') or '—'}` — {current_task.get('title') or '—'}",
        f"- **Estado tarea:** `{current_task.get('status') or '—'}` · owner={current_task.get('owner_agent_id') or current_task.get('owner_profile') or '—'} · reviewer={current_task.get('reviewer_agent_id') or current_task.get('reviewer_profile') or '—'}",
        f"- **Run activo:** `{active_run.get('run_id') or '—'}` · status={active_run.get('status') or '—'} · evidence={active_run.get('log_path') or active_run.get('prompt_path') or '—'}",
    ]
    finding_lines = [f"- **{finding.get('code')}** · {finding.get('severity', 'info')} — {finding.get('message')}" for finding in findings] or ["- ✅ Ninguna anomalía detectada por Factory DB en este snapshot."]

    return "\n".join(
        [
            f"# 🏭 {project.get('name')} — Factory PM",
            "",
            f"Última sincronización: **{_factory_utc_now()}** · Fuente operativa: **Agent Core Postgres `factory.*`**",
            "",
            "<callout icon=\"🎯\" color=\"blue_bg\">",
            "\tTablero humano de PM: estado ejecutivo, bitácora, gates y links para abrir documentos. La verdad operativa sigue en Factory DB + repo + evidencia de runtime.",
            "</callout>",
            "",
            "<table_of_contents color=\"gray\"/>",
            "",
            "## 1. Snapshot ejecutivo",
            "",
            f"**Project ID:** `{project_id}` · **Status:** `{project.get('status')}` · **Metodología:** `{project.get('methodology')}` · **Riesgo:** `{project.get('risk_level')}`",
            "",
            *executive_table,
            "",
            "## 2. Abrir rápido",
            "",
            *quick_links,
            "",
            "## 3. Document Hub — links directos",
            "",
            "Cada documento existente debe ser clickeable desde esta tabla. Si un link falta, el proyecto necesita metadata de repo/remoto o publicación de artifacts.",
            "",
            *doc_table,
            "",
            "## 4. Estado operativo actual",
            "",
            *current_task_lines,
            "",
            "## 5. Task graph / backlog visible",
            "",
            *task_table,
            "",
            "## 6. Gates efectivos",
            "",
            *gate_table,
            "",
            "## 7. Cierres secuenciales de incrementos",
            "",
            "Cada cierre se registra post-acción: los agentes trabajan con los documentos canónicos pre-acción en repo/Factory DB, y Notion queda como vista humana secuencial del avance.",
            "",
            *closure_table,
            "",
            "## 8. Bitácora ejecutiva",
            "",
            "Registro reciente de eventos Factory. Esto debe sentirse como log de proyecto, no como plantilla vacía.",
            "",
            *event_table,
            "",
            "## 9. Runs / workers recientes",
            "",
            *run_table,
            "",
            "## 10. Anomalías y deuda metodológica",
            "",
            *finding_lines,
            "",
            "## 11. Próximos pasos / supervisión humana",
            "",
            "- [ ] Verificar estado live en Factory DB antes de retomar ejecución.",
            "- [ ] Resolver gates failed/pending antes de marcar cierre.",
            "- [ ] Crear o linkear cualquier doc missing antes del cierre.",
            "- [ ] Actualizar esta página al cierre de sprint o cuando cambie un blocker real.",
            "",
            "## 12. Retrospectiva / metodología",
            "",
            "- Qué funcionó:",
            "- Qué produjo deriva:",
            "- Qué regla se debe incorporar a la Factory:",
        ]
    )


def _notion_api_key() -> str:
    return (load_env().get("NOTION_API_KEY") or os.environ.get("NOTION_API_KEY") or "").strip()


def _notion_request(method: str, path: str, api_key: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        f"https://api.notion.com/v1/{path.lstrip('/')}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Notion-Version": "2025-09-03",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Notion API {exc.code}: {detail}") from exc


_FACTORY_NOTION_MARKDOWN_LINK_RE = re.compile(r"\[([^\]\n]+)\]\((https?://[^)\s]+)\)")


def _factory_notion_rich_text(text: str) -> list[dict[str, Any]]:
    """Convert inline Markdown links into Notion rich_text chunks."""

    chunks: list[dict[str, Any]] = []
    cursor = 0
    for match in _FACTORY_NOTION_MARKDOWN_LINK_RE.finditer(text):
        if match.start() > cursor:
            chunks.append({"type": "text", "text": {"content": text[cursor:match.start()]}})
        label = match.group(1).strip() or match.group(2)
        url = match.group(2).strip()
        chunks.append({"type": "text", "text": {"content": label, "link": {"url": url}}, "href": url})
        cursor = match.end()
    if cursor < len(text):
        chunks.append({"type": "text", "text": {"content": text[cursor:]}})
    return chunks or [{"type": "text", "text": {"content": " "}}]


def _factory_notion_blocks(markdown: str, *, limit: int = 240) -> list[dict[str, Any]]:
    """Convert a Markdown status snapshot into simple Notion paragraph/code blocks."""

    blocks: list[dict[str, Any]] = []
    current_code: list[str] = []
    in_code = False
    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if line.strip().startswith("```"):
            if in_code:
                text = "\n".join(current_code).strip() or " "
                blocks.append({"object": "block", "type": "code", "code": {"language": "plain text", "rich_text": [{"type": "text", "text": {"content": text[:1900]}}]}})
                current_code = []
            in_code = not in_code
            continue
        if in_code:
            current_code.append(line)
            continue
        text = line.strip() or " "
        block_type = "heading_2" if text.startswith("## ") else "heading_3" if text.startswith("### ") else "paragraph"
        clean = text.removeprefix("### ").removeprefix("## ")[:1900]
        blocks.append({"object": "block", "type": block_type, block_type: {"rich_text": _factory_notion_rich_text(clean)}})
        if len(blocks) >= limit:
            break
    return blocks or [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Factory status synced."}}]}}]


def _factory_append_notion_page_children(page_id: str, blocks: list[dict[str, Any]], api_key: str, *, chunk_size: int = 100) -> None:
    """Append blocks using Notion's 100-children request limit."""

    for start in range(0, len(blocks), chunk_size):
        chunk = blocks[start:start + chunk_size]
        if chunk:
            _notion_request("PATCH", f"blocks/{page_id}/children", api_key, {"children": chunk})


def _factory_replace_notion_page_children(page_id: str, markdown: str, api_key: str) -> None:
    """Replace generated Factory PM page content using official Notion block APIs.

    Notion's public REST API accepts page creation with ``children`` and updates
    through ``blocks/{page_id}/children``. It does not expose a stable
    ``pages/{id}/markdown`` endpoint, so the dashboard keeps the link-first
    Markdown renderer but converts it to blocks before writing.
    """

    cursor = ""
    while True:
        path = f"blocks/{page_id}/children?page_size=100"
        if cursor:
            path += f"&start_cursor={urllib.parse.quote(cursor, safe='')}"
        children = _notion_request("GET", path, api_key)
        for block in children.get("results") or []:
            if not isinstance(block, dict):
                continue
            block_id = str(block.get("id") or "").strip()
            block_type = str(block.get("type") or "").strip()
            if block_id and block_type not in {"child_page", "child_database"}:
                _notion_request("PATCH", f"blocks/{block_id}", api_key, {"archived": True})
        if not children.get("has_more") or not children.get("next_cursor"):
            break
        cursor = str(children.get("next_cursor") or "")
    _factory_append_notion_page_children(page_id, _factory_notion_blocks(markdown), api_key)


def _notion_page_title(page: Dict[str, Any]) -> str:
    props = page.get("properties") if isinstance(page, dict) else None
    if not isinstance(props, dict):
        return ""
    chunks: list[str] = []
    for prop in props.values():
        if not isinstance(prop, dict):
            continue
        for rich in prop.get("title") or []:
            if isinstance(rich, dict):
                chunks.append(str(rich.get("plain_text") or rich.get("text", {}).get("content") or ""))
    return "".join(chunks).strip()


def _factory_notion_parent_page_id(project: Dict[str, Any], api_key: str) -> str:
    metadata = _factory_project_metadata(project)
    for key in ("notion_parent_page_id", "notion_factory_root_page_id", "notion_root_page_id"):
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    template = _factory_notion_template(project)
    if template and template.get("page_id"):
        page = _notion_request("GET", f"pages/{template['page_id']}", api_key)
        parent = page.get("parent") if isinstance(page, dict) else None
        if isinstance(parent, dict) and parent.get("type") == "page_id" and parent.get("page_id"):
            return str(parent["page_id"])

    search = _notion_request(
        "POST",
        "search",
        api_key,
        {"query": "Software Factory — Reportes Ejecutivos", "filter": {"property": "object", "value": "page"}},
    )
    for page in search.get("results") or []:
        title = _notion_page_title(page).lower()
        if "software factory" in title and "reportes ejecutivos" in title:
            return str(page.get("id") or "")
    return ""


def _factory_update_project_metadata(project_id: str, metadata: Dict[str, Any]) -> None:
    from hermes_cli import factory_backend

    backend = factory_backend.get_backend()
    if not hasattr(backend, "update_project_metadata"):
        raise HTTPException(status_code=500, detail="Canonical Factory backend cannot update project metadata")
    backend.update_project_metadata(project_id, metadata)  # type: ignore[attr-defined]
    try:
        from hermes_cli import factory_pg

        factory_pg.sql.psql(
            "INSERT INTO factory.events(project_id, actor, event_type, message, metadata) "
            f"VALUES ({factory_pg._q(project_id)}, 'factory-reporter', 'notion_documented', "
            f"{factory_pg._q('Project Notion PM metadata updated')}, {factory_pg._j(metadata)});",
            user=factory_pg._user(),
        )
    except Exception:
        _log.warning("Factory Notion metadata updated but event insert failed", exc_info=True)


@router.get("/api/factory/projects/{project_id}/handoff")
async def get_factory_project_handoff(project_id: str):
    payload = await get_factory_dashboard(project_id=project_id)
    projects = payload.get("projects", [])
    if not projects:
        raise HTTPException(status_code=404, detail=f"Factory project not found: {project_id}")
    project = projects[0]
    return {
        "ok": True,
        "project_id": project_id,
        "prompt": _factory_handoff_prompt(payload, project),
    }


@router.post("/api/factory/projects/{project_id}/actions/{action}")
async def run_factory_project_action(project_id: str, action: str):
    """Deterministic project control action.

    These buttons change Factory DB state or run one orchestrator tick. They are
    intentionally separate from the chat handoff; opening chat is not what makes
    a project autonomous.
    """

    action_aliases = {
        "resume": "resume",
        "pause": "pause",
        "tick": "tick",
        "resolve-state": "resolve-state",
        "resolve": "resolve-state",
        "reconcile": "resolve-state",
        "unblock": "resolve-state",
    }
    canonical_action = action_aliases.get(action)
    if not canonical_action:
        raise HTTPException(status_code=400, detail=f"Unsupported Factory action: {action}")
    try:
        if canonical_action in {"tick", "resume"}:
            resume_result = None
            if canonical_action == "resume":
                from hermes_cli import factory_backend

                backend = factory_backend.get_backend()
                resume_result = backend.control_action(project_id, "resume")
                if resume_result.get("resume_blocked") or resume_result.get("dispatch_allowed") is False:
                    return {"ok": True, "project_id": project_id, **resume_result, "tick": None, "claimed": None}
            from hermes_cli import factory as factory_cli

            result = factory_cli._run_orchestrator_script(project_id)
            if resume_result is not None:
                return {"ok": True, "project_id": project_id, **resume_result, "tick": result, "claimed": result.get("claimed")}
            return {"ok": True, "project_id": project_id, "action": canonical_action, **result}

        from hermes_cli import factory_backend

        backend = factory_backend.get_backend()
        result = backend.control_action(project_id, canonical_action)
        return {"ok": True, "project_id": project_id, **result}
    except Exception as exc:
        _log.exception("Factory action failed for %s/%s", project_id, action)
        raise HTTPException(status_code=500, detail=f"Factory action failed: {exc}") from exc


@router.post("/api/factory/projects/{project_id}/notion/sync")
async def sync_factory_project_notion(project_id: str):
    """Record/update the human PM documentation checkpoint in Notion metadata.

    Notion is the human reporting layer; Factory DB remains canonical. If the
    project page does not exist yet, create it first through the existing Notion
    endpoint. If it exists, record a sprint/increment sync event and metadata so
    dashboard status reflects the latest documentation checkpoint.
    """

    payload = await get_factory_dashboard(project_id=project_id)
    projects = payload.get("projects", [])
    if not projects:
        raise HTTPException(status_code=404, detail=f"Factory project not found: {project_id}")
    project = projects[0]
    existing = _factory_project_notion(project)
    if not existing or not existing.get("url"):
        created = await create_factory_project_notion(project_id)
        return {**created, "synced": True}

    metadata = {
        "notion_role": "human_pm_reporting_not_agent_truth",
        "notion_tracker_last_synced_at": _factory_utc_now(),
        "notion_tracker_last_sync_summary": (project.get("dashboard") or {}).get("quick_status") or "Factory dashboard synced",
        "notion_projection_stale": False,
        "notion_sync_required": False,
        "notion_last_increment_closure_synced_at": _factory_utc_now(),
    }
    api_key = _notion_api_key()
    page_id = str(existing.get("page_id") or "").strip()
    if api_key and page_id:
        markdown = _factory_notion_markdown(payload, project)
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, _factory_replace_notion_page_children, page_id, markdown, api_key)
    _factory_update_project_metadata(project_id, metadata)
    return {
        "ok": True,
        "created": False,
        "synced": True,
        "project_id": project_id,
        "page_id": existing.get("page_id"),
        "url": existing.get("url"),
    }


@router.post("/api/factory/projects/{project_id}/notion")
async def create_factory_project_notion(project_id: str):
    payload = await get_factory_dashboard(project_id=project_id)
    projects = payload.get("projects", [])
    if not projects:
        raise HTTPException(status_code=404, detail=f"Factory project not found: {project_id}")
    project = projects[0]

    existing = _factory_project_notion(project)
    if existing and existing.get("url"):
        return {
            "ok": True,
            "created": False,
            "project_id": project_id,
            "page_id": existing.get("page_id"),
            "url": existing.get("url"),
        }

    api_key = _notion_api_key()
    if not api_key:
        raise HTTPException(status_code=400, detail="NOTION_API_KEY is not configured")

    try:
        loop = asyncio.get_running_loop()
        parent_id = await loop.run_in_executor(None, _factory_notion_parent_page_id, project, api_key)
        if not parent_id:
            raise RuntimeError("Could not resolve the Factory Notion root page")
        title = f"🏭 {project.get('name') or project_id} — Factory PM"
        markdown = _factory_notion_markdown(payload, project)
        blocks = _factory_notion_blocks(markdown)
        page = await loop.run_in_executor(
            None,
            lambda: _notion_request(
                "POST",
                "pages",
                api_key,
                {
                    "parent": {"page_id": parent_id},
                    "properties": {"title": [{"text": {"content": title[:180]}}]},
                    "children": blocks[:100],
                },
            ),
        )
        created_page_id = str(page.get("id") or "").strip()
        if created_page_id and len(blocks) > 100:
            await loop.run_in_executor(None, _factory_append_notion_page_children, created_page_id, blocks[100:], api_key)
    except HTTPException:
        raise
    except Exception as exc:
        _log.exception("Factory Notion generation failed for %s", project_id)
        raise HTTPException(status_code=502, detail=f"Notion generation failed: {exc}") from exc

    page_id = str(page.get("id") or "").strip()
    url = str(page.get("url") or "").strip() or _factory_notion_page_url(page_id)
    metadata = {
        "notion_role": "human_pm_reporting_not_agent_truth",
        "notion_tracker_page_id": page_id,
        "notion_tracker_url": url,
        "notion_tracker_created_at": _factory_utc_now(),
        "notion_tracker_last_synced_at": _factory_utc_now(),
        "notion_projection_stale": False,
        "notion_sync_required": False,
        "notion_parent_page_id": parent_id,
    }
    _factory_update_project_metadata(project_id, metadata)
    return {
        "ok": True,
        "created": True,
        "project_id": project_id,
        "page_id": page_id,
        "url": url,
    }


async def _factory_dashboard_slice(key: str, project_id: Optional[str] = None) -> Dict[str, Any]:
    payload = await get_factory_dashboard(project_id=project_id)
    return {
        "db_backend": payload.get("db_backend"),
        "db_path": payload.get("db_path"),
        "project_id": project_id,
        key: payload.get(key, []),
        "counts": payload.get("counts", {}),
    }


@router.get("/api/factory/projects")
async def get_factory_projects(project_id: Optional[str] = None):
    return await _factory_dashboard_slice("projects", project_id=project_id)


@router.get("/api/factory/tasks")
async def get_factory_tasks(project_id: Optional[str] = None):
    return await _factory_dashboard_slice("tasks", project_id=project_id)


@router.get("/api/factory/gates")
async def get_factory_gates(project_id: Optional[str] = None):
    return await _factory_dashboard_slice("gates", project_id=project_id)


@router.get("/api/factory/events")
async def get_factory_events(project_id: Optional[str] = None):
    return await _factory_dashboard_slice("events", project_id=project_id)


@router.get("/api/factory/artifacts")
async def get_factory_artifacts(project_id: Optional[str] = None):
    return await _factory_dashboard_slice("artifacts", project_id=project_id)


@router.get("/api/factory/agents")
async def get_factory_agents(project_id: Optional[str] = None):
    return await _factory_dashboard_slice("agents", project_id=project_id)


@router.get("/api/factory/kanban-boards")
async def get_factory_kanban_boards(project_id: Optional[str] = None):
    raise HTTPException(
        status_code=410,
        detail=(
            "Kanban is a separate orchestration surface. Use the Kanban plugin/API "
            "directly; Factory endpoints do not project Kanban boards."
        ),
    )


@router.get("/api/factory/findings")
async def get_factory_findings(project_id: Optional[str] = None):
    return await _factory_dashboard_slice("findings", project_id=project_id)

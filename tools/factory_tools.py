"""Agent tools for the SitioUno Software Factory progress DB."""
from __future__ import annotations

import json
from typing import Any

from tools.registry import registry, tool_error


def _factory_backend():
    from hermes_cli import factory_backend

    return factory_backend.get_backend()


def _ok(**fields: Any) -> str:
    return json.dumps({"ok": True, **fields}, ensure_ascii=False, sort_keys=True)


def _check_factory_mode() -> bool:
    # Factory tools are safe enough for explicit toolset use. They are not in
    # the default core toolset; profiles opt into the ``factory`` toolset.
    return True


def _handle_factory_project_create(args: dict, **_kwargs) -> str:
    try:
        db = _factory_backend()
        result = db.create_project(
            str(args.get("name") or "").strip(),
            project_id=args.get("project_id") or None,
            repo_path=args.get("repo_path") or None,
            repo_remote=args.get("repo_remote") or None,
            base_branch=args.get("base_branch") or None,
            human_owner=args.get("human_owner") or "Jean García",
            summary=args.get("summary") or None,
            risk_level=args.get("risk_level") or "medium",
            autonomy_level=int(args.get("autonomy_level") or 3),
            create_default_lanes=bool(args.get("create_default_lanes", True)),
            repo_scope=args.get("repo_scope") or None,
            work_intent=args.get("work_intent") or None,
            metadata={"source": "factory_project_create tool"},
        )
        return _ok(**result)
    except Exception as exc:
        return tool_error(str(exc))


def _handle_factory_lane_create(args: dict, **_kwargs) -> str:
    try:
        db = _factory_backend()
        result = db.create_lane(
            str(args.get("project_id") or "").strip(),
            str(args.get("name") or "").strip(),
            str(args.get("methodology") or "").strip(),
            lane_id=args.get("lane_id") or None,
            branch=args.get("branch") or None,
            worktree_path=args.get("worktree_path") or None,
        )
        return _ok(**result)
    except Exception as exc:
        return tool_error(str(exc))


def _handle_factory_task_create(args: dict, **_kwargs) -> str:
    try:
        db = _factory_backend()
        result = db.create_task(
            str(args.get("project_id") or "").strip(),
            str(args.get("title") or "").strip(),
            lane_id=args.get("lane_id") or None,
            description=args.get("description") or None,
            phase=args.get("phase") or "planning",
            owner_agent_id=args.get("owner_agent_id") or None,
            reviewer_agent_id=args.get("reviewer_agent_id") or None,
            engine=args.get("engine") or "zeus",
            priority=int(args.get("priority") or 100),
            acceptance_criteria=args.get("acceptance_criteria") or [],
            branch=args.get("branch") or None,
            worktree_path=args.get("worktree_path") or None,
            metadata={"source": "factory_task_create tool"},
        )
        return _ok(**result)
    except Exception as exc:
        return tool_error(str(exc))


def _handle_factory_gate_record(args: dict, **_kwargs) -> str:
    try:
        db = _factory_backend()
        result = db.record_gate(
            str(args.get("project_id") or "").strip(),
            str(args.get("gate_type") or "").strip(),
            str(args.get("status") or "pending").strip(),
            lane_id=args.get("lane_id") or None,
            task_id=args.get("task_id") or None,
            reviewer=args.get("reviewer") or None,
            notes=args.get("notes") or None,
            evidence=args.get("evidence") or {},
        )
        return _ok(**result)
    except Exception as exc:
        return tool_error(str(exc))


def _handle_factory_status(args: dict, **_kwargs) -> str:
    try:
        db = _factory_backend()
        return _ok(**db.status(args.get("project_id") or None))
    except Exception as exc:
        return tool_error(str(exc))


_PROJECT_CREATE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "factory_project_create",
        "description": "Create or update a SitioUno Software Factory project and optional default Zeus/BMAD lanes.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "project_id": {"type": "string"},
                "repo_path": {"type": "string"},
                "repo_remote": {"type": "string"},
                "base_branch": {"type": "string"},
                "human_owner": {"type": "string"},
                "summary": {"type": "string"},
                "risk_level": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                "autonomy_level": {"type": "integer"},
                "repo_scope": {"type": "string", "enum": ["zeus_only", "zeus_then_runtime", "runtime_only", "existing_project_change", "new_product_repo", "docs_or_research_only"], "description": "Canonical G0 routing. Use zeus_only for Zeus-only improvements, zeus_then_runtime for features inherited by runtime agents, existing_project_change to modify an existing product repo, new_product_repo only when Jean asked for a new project/repo."},
                "work_intent": {"type": "string", "enum": ["create_new_project", "add_functionality", "modify_existing_project", "maintain_existing_project", "docs_research"]},
                "create_default_lanes": {"type": "boolean"},
            },
            "required": ["name"],
        },
    },
}

_LANE_CREATE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "factory_lane_create",
        "description": "Create or update a factory method lane (hybrid by default unless Jean explicitly requests zeus_native, bmad_hybrid, or dual_lane). Factory lanes do not create Kanban boards/cards.",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {"type": "string"},
                "name": {"type": "string"},
                "methodology": {"type": "string", "enum": ["zeus_native", "bmad_hybrid", "hybrid", "dual_lane"]},
                "lane_id": {"type": "string"},
                "branch": {"type": "string"},
                "worktree_path": {"type": "string"},
            },
            "required": ["project_id", "name", "methodology"],
        },
    },
}

_TASK_CREATE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "factory_task_create",
        "description": "Create a factory progress task with owner, reviewer, engine, and acceptance criteria.",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {"type": "string"},
                "title": {"type": "string"},
                "lane_id": {"type": "string"},
                "description": {"type": "string"},
                "phase": {"type": "string"},
                "owner_agent_id": {"type": "string"},
                "reviewer_agent_id": {"type": "string"},
                "engine": {"type": "string"},
                "priority": {"type": "integer"},
                "branch": {"type": "string", "description": "Override derived per-deliverable branch. Normally omit so Factory derives from G0 repo_strategy."},
                "worktree_path": {"type": "string", "description": "Override derived isolated per-deliverable worktree. Normally omit so Factory derives from G0 repo_strategy."},
                "acceptance_criteria": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["project_id", "title"],
        },
    },
}

_GATE_RECORD_SCHEMA = {
    "type": "function",
    "function": {
        "name": "factory_gate_record",
        "description": "Record a factory gate result with reviewer notes and evidence.",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {"type": "string"},
                "gate_type": {"type": "string", "enum": ["intake", "functional", "architecture", "planning", "implementation", "spec", "quality", "test", "security", "delivery", "critical_readiness"]},
                "status": {"type": "string", "enum": ["pending", "passed", "failed", "waived"]},
                "lane_id": {"type": "string"},
                "task_id": {"type": "string"},
                "reviewer": {"type": "string"},
                "notes": {"type": "string"},
                "evidence": {"type": "object"},
            },
            "required": ["project_id", "gate_type", "status"],
        },
    },
}

_STATUS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "factory_status",
        "description": "Read current SitioUno Software Factory projects, lanes, tasks, and gates from the progress DB.",
        "parameters": {
            "type": "object",
            "properties": {"project_id": {"type": "string"}},
        },
    },
}

registry.register(name="factory_project_create", toolset="factory", schema=_PROJECT_CREATE_SCHEMA, handler=_handle_factory_project_create, check_fn=_check_factory_mode, emoji="🏭")
registry.register(name="factory_lane_create", toolset="factory", schema=_LANE_CREATE_SCHEMA, handler=_handle_factory_lane_create, check_fn=_check_factory_mode, emoji="🏭")
registry.register(name="factory_task_create", toolset="factory", schema=_TASK_CREATE_SCHEMA, handler=_handle_factory_task_create, check_fn=_check_factory_mode, emoji="🏭")
registry.register(name="factory_gate_record", toolset="factory", schema=_GATE_RECORD_SCHEMA, handler=_handle_factory_gate_record, check_fn=_check_factory_mode, emoji="🏭")
registry.register(name="factory_status", toolset="factory", schema=_STATUS_SCHEMA, handler=_handle_factory_status, check_fn=_check_factory_mode, emoji="🏭")

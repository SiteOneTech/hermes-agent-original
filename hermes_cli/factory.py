"""CLI surface for SitioUno Software Factory."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from hermes_cli import factory_backend
from hermes_cli.factory_catalog import VALID_METHODS


def _backend(args: argparse.Namespace):
    return factory_backend.get_backend()


def _annotate_status_payload_source(
    payload: Any,
    source_root: Path,
    *,
    delegated_from: Path | None = None,
) -> Any:
    if not isinstance(payload, dict):
        return payload
    payload["factory_cli_source_root"] = str(source_root)
    payload["factory_status_source_root"] = str(source_root)
    payload["factory_status_delegated"] = delegated_from is not None
    if delegated_from is not None:
        payload["factory_status_delegated_from_source_root"] = str(delegated_from)
    else:
        payload.pop("factory_status_delegated_from_source_root", None)
    return payload


def _status_payload(args: argparse.Namespace) -> dict[str, Any]:
    backend = _backend(args)
    payload = backend.status(getattr(args, "project_id", None))
    try:
        source_root = _running_factory_source_root()
    except RuntimeError:
        return payload
    return _annotate_status_payload_source(payload, source_root)


def _print_status_subprocess_output(
    proc: subprocess.CompletedProcess[str],
    *,
    args: argparse.Namespace,
    source_root: Path,
    delegated_from: Path,
) -> None:
    if getattr(args, "json", False) and (proc.stdout or "").strip():
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError:
            payload = None
        if isinstance(payload, dict):
            _print_json(_annotate_status_payload_source(payload, source_root, delegated_from=delegated_from))
            if proc.stderr:
                print(proc.stderr, end="", file=sys.stderr)
            return
    if proc.stdout:
        print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)


def _print_json(payload: Any) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _lane_surface(lane: dict[str, Any]) -> str:
    return str(lane.get("execution_surface") or "factory")


def cmd_init(args: argparse.Namespace) -> int:
    backend = _backend(args)
    backend.seed_agents()
    print("✓ Factory backend ready: Agent Core Postgres (canonical, SQLite disabled)")
    return 0


def cmd_agents(args: argparse.Namespace) -> int:
    backend = _backend(args)
    agents = backend.list_agents()
    if args.json:
        return _print_json({"agents": agents})
    for agent in agents:
        print(f"{agent['agent_id']}: {agent['role']} [{agent.get('preferred_engine') or 'zeus'}]")
    return 0


def cmd_project_create(args: argparse.Namespace) -> int:
    backend = _backend(args)
    result = backend.create_project(
        args.name,
        project_id=args.project_id,
        repo_path=args.repo_path,
        repo_remote=args.repo_remote,
        base_branch=args.base_branch,
        human_owner=args.human_owner,
        summary=args.summary,
        risk_level=args.risk_level,
        autonomy_level=args.autonomy_level,
        methodology=args.methodology,
        create_default_lanes=not args.no_default_lanes,
        repo_scope=getattr(args, "repo_scope", None),
        work_intent=getattr(args, "work_intent", None),
        metadata={"source": "hermes factory project create"},
    )
    if args.json:
        return _print_json(result)
    print(f"✓ Project {result['project_id']} ready")
    for lane in result.get("lanes", []):
        print(f"  - lane {lane['lane_id']} ({lane['methodology']}) surface={_lane_surface(lane)} branch={lane['branch']}")
    return 0


def cmd_lane_create(args: argparse.Namespace) -> int:
    backend = _backend(args)
    result = backend.create_lane(
        args.project_id,
        args.name,
        args.methodology,
        lane_id=args.lane_id,
        kanban_board=args.kanban_board,
        branch=args.branch,
        worktree_path=args.worktree_path,
    )
    if args.json:
        return _print_json(result)
    print(f"✓ Lane {result['lane_id']} ready ({result['methodology']})")
    print(f"  surface={_lane_surface(result)} branch={result['branch']}")
    return 0


def cmd_task_create(args: argparse.Namespace) -> int:
    backend = _backend(args)
    result = backend.create_task(
        args.project_id,
        args.title,
        lane_id=args.lane_id,
        description=args.description,
        phase=args.phase,
        owner_agent_id=args.owner,
        reviewer_agent_id=args.reviewer,
        engine=args.engine,
        priority=args.priority,
        acceptance_criteria=args.acceptance or [],
        branch=args.branch,
        worktree_path=args.worktree_path,
    )
    if args.json:
        return _print_json(result)
    print(f"✓ Task {result['task_id']} created")
    return 0


def cmd_task_close(args: argparse.Namespace) -> int:
    backend = _backend(args)
    try:
        evidence = json.loads(args.evidence_json) if args.evidence_json else {}
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid --evidence-json: {exc}") from exc
    if not isinstance(evidence, dict):
        raise ValueError("--evidence-json must decode to a JSON object")
    result = backend.close_task(
        args.task_id,
        status=args.status,
        result_summary=args.summary,
        evidence=evidence,
        actor=args.actor,
        reconcile=not args.no_reconcile,
    )
    if args.json:
        return _print_json(result)
    print(f"✓ Task {args.task_id}: closed as {result.get('status')}")
    return 0


def cmd_gate_record(args: argparse.Namespace) -> int:
    backend = _backend(args)
    result = backend.record_gate(
        args.project_id,
        args.gate_type,
        args.status,
        lane_id=args.lane_id,
        task_id=args.task_id,
        reviewer=args.reviewer,
        notes=args.notes,
        evidence={"source": "hermes factory gate record"},
    )
    if args.json:
        return _print_json(result)
    print(f"✓ Gate {result['gate_id']} recorded: {args.gate_type}={args.status}")
    return 0


def cmd_project_close(args: argparse.Namespace) -> int:
    backend = _backend(args)
    result = backend.close_project(
        args.project_id,
        reason=args.reason,
        closure_type=args.closure_type,
        superseded_by_project_id=args.superseded_by_project_id,
        actor=args.actor,
    )
    if args.json:
        return _print_json(result)
    print(f"✓ Project {args.project_id}: closed as {result.get('status')} ({result.get('closure_type')})")
    return 0


def cmd_project_reopen(args: argparse.Namespace) -> int:
    backend = _backend(args)
    result = backend.reopen_project(
        args.project_id,
        reason=args.reason,
        actor=args.actor,
        continuation_of=getattr(args, "continuation_of", None),
    )
    if args.json:
        return _print_json(result)
    if result.get("reopen_blocked"):
        print(f"✗ Project {args.project_id}: reopen blocked ({result.get('reason')})")
        return 1
    print(f"✓ Project {args.project_id}: reopened canonically ({result.get('status')})")
    return 0


def cmd_project_link_notion(args: argparse.Namespace) -> int:
    backend = _backend(args)
    result = backend.link_notion_tracker(
        args.project_id,
        page_id=args.page_id,
        url=args.url,
        page_title=getattr(args, "page_title", None),
        actor=args.actor,
    )
    if args.json:
        return _print_json(result)
    readback = result.get("readback") if isinstance(result.get("readback"), dict) else {}
    print(f"✓ Project {args.project_id}: Notion tracker linked")
    if readback.get("notion_tracker_page_id"):
        print(f"  page_id={readback.get('notion_tracker_page_id')}")
    if readback.get("notion_tracker_url"):
        print(f"  url={readback.get('notion_tracker_url')}")
    return 0


def cmd_project_takeover(args: argparse.Namespace) -> int:
    backend = _backend(args)
    result = backend.acquire_manual_takeover_lease(
        args.project_id,
        holder=args.holder,
        reason=args.reason,
        ttl_minutes=args.ttl_minutes,
        worktree_path=args.worktree_path,
        session_id=args.session_id,
    )
    if args.json:
        return _print_json(result)
    if result.get("acquired"):
        print(f"✓ Project {args.project_id}: manual takeover lease acquired by {args.holder}")
    else:
        print(f"✗ Project {args.project_id}: manual takeover blocked by active lease")
    return 0


def cmd_project_release_takeover(args: argparse.Namespace) -> int:
    backend = _backend(args)
    result = backend.release_manual_takeover_lease(
        args.project_id,
        holder=args.holder,
        reason=args.reason,
    )
    if args.json:
        return _print_json(result)
    print(f"✓ Project {args.project_id}: manual takeover lease released by {args.holder}")
    return 0


def cmd_project_declare_successor(args: argparse.Namespace) -> int:
    backend = _backend(args)
    authorization = {
        "authorized_by": args.actor,
        "reason": args.reason,
        "allow_auto_resume": bool(args.allow_auto_resume),
    }
    result = backend.declare_project_succession(
        args.project_id,
        args.successor_project_id,
        authorization=authorization,
        declared_by=args.actor,
        metadata={"declared_via": "hermes factory project declare-successor"},
    )
    if args.json:
        return _print_json(result)
    print(f"✓ Project succession declared: {args.project_id} -> {args.successor_project_id}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    delegated = _delegated_status_from_cwd_source(args)
    if delegated is not None:
        return delegated
    payload = _status_payload(args)
    if args.json:
        return _print_json(payload)
    print(f"Factory DB: Agent Core Postgres/{payload.get('database', 'zeus_agent')}.factory (canonical; SQLite disabled)")
    print(f"Projects: {len(payload['projects'])} | Lanes: {len(payload['lanes'])} | Tasks: {len(payload['tasks'])} | Gates: {len(payload['gates'])} | Runs: {len(payload.get('task_runs', []))}")
    for project in payload["projects"]:
        print(f"- {project['project_id']}: {project['name']} [{project['status']}] risk={project['risk_level']}")
        for lane in [item for item in payload["lanes"] if item["project_id"] == project["project_id"]]:
            print(f"    lane {lane['lane_id']} {lane['methodology']} surface={_lane_surface(lane)}")
    return 0


def _running_factory_source_root() -> Path:
    factory_file = Path(__file__).resolve()
    if factory_file.name != "factory.py" or factory_file.parent.name != "hermes_cli":
        raise RuntimeError(f"Factory tick source provenance malformed: {factory_file}")
    return factory_file.parents[1]


def _factory_source_root_is_complete(source_root: Path) -> bool:
    return all(
        (source_root / rel_path).is_file()
        for rel_path in (
            Path("hermes_cli") / "main.py",
            Path("hermes_cli") / "factory.py",
            Path("hermes_cli") / "factory_pg.py",
            Path("scripts") / "factory" / "factory_orchestrator_tick.py",
        )
    )


def _find_cwd_factory_source_root() -> Path | None:
    try:
        cwd = Path.cwd().resolve()
    except Exception:
        return None
    for candidate in (cwd, *cwd.parents):
        if _factory_source_root_is_complete(candidate):
            return candidate
    return None


def _same_source_root(left: Path, right: Path) -> bool:
    try:
        return left.resolve() == right.resolve()
    except Exception:
        return os.path.realpath(str(left)) == os.path.realpath(str(right))


def _preferred_cwd_source_root(running_source_root: Path) -> Path | None:
    if os.environ.get("HERMES_FACTORY_SOURCE_DELEGATED") == "1":
        return None
    cwd_source_root = _find_cwd_factory_source_root()
    if cwd_source_root is None or _same_source_root(cwd_source_root, running_source_root):
        return None
    return cwd_source_root


def _source_env(source_root: Path, *, project_id: str | None = None) -> dict[str, str]:
    env = {**os.environ}
    pythonpath = str(source_root)
    if env.get("PYTHONPATH"):
        pythonpath = f"{pythonpath}{os.pathsep}{env['PYTHONPATH']}"
    env["PYTHONPATH"] = pythonpath
    if project_id:
        env["FACTORY_TICK_PROJECT_ID"] = project_id
    return env


def _delegated_status_from_cwd_source(args: argparse.Namespace) -> int | None:
    try:
        running_source_root = _running_factory_source_root()
    except RuntimeError:
        return None
    source_root = _preferred_cwd_source_root(running_source_root)
    if source_root is None:
        return None
    argv = [sys.executable, "-m", "hermes_cli.main", "factory", "status"]
    project_id = getattr(args, "project_id", None)
    if project_id:
        argv.append(str(project_id))
    if getattr(args, "json", False):
        argv.append("--json")
    env = _source_env(source_root)
    env["HERMES_FACTORY_SOURCE_DELEGATED"] = "1"
    proc = subprocess.run(
        argv,
        cwd=str(source_root),
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=180,
    )
    _print_status_subprocess_output(
        proc,
        args=args,
        source_root=source_root,
        delegated_from=running_source_root,
    )
    return proc.returncode


def _resolve_orchestrator_script() -> tuple[Path, Path]:
    running_source_root = _running_factory_source_root()
    running_script = running_source_root / "scripts" / "factory" / "factory_orchestrator_tick.py"
    if not running_script.is_file():
        raise RuntimeError(f"Factory orchestrator script not found in running Hermes source: {running_script}")
    source_root = _preferred_cwd_source_root(running_source_root) or running_source_root
    script = source_root / "scripts" / "factory" / "factory_orchestrator_tick.py"
    if not script.is_file():
        raise RuntimeError(f"Factory orchestrator script not found in running Hermes source: {script}")
    return script, source_root


def _run_orchestrator_script(project_id: str | None = None) -> dict[str, Any]:
    script, source_root = _resolve_orchestrator_script()
    env = _source_env(source_root, project_id=project_id)
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(source_root),
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=180,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"tick exited {proc.returncode}")
    try:
        payload = json.loads(proc.stdout or "{}")
        if isinstance(payload, dict):
            payload.setdefault("factory_cli_source_root", str(source_root))
            payload.setdefault("factory_orchestrator_script", str(script))
        return payload
    except Exception:
        return {"raw_output": proc.stdout, "factory_cli_source_root": str(source_root), "factory_orchestrator_script": str(script)}


def cmd_project_action(args: argparse.Namespace) -> int:
    backend = _backend(args)
    action_map = {
        "resume": "resume",
        "pause": "pause",
        "technical-hold": "technical-hold",
        "tick": "tick",
        "resolve-state": "resolve-state",
        "resolve": "resolve-state",
        "reconcile": "resolve-state",
        "unblock": "resolve-state",
    }
    if args.factory_project_command == "tick":
        result = {"action": "tick", **_run_orchestrator_script(args.project_id)}
    elif args.factory_project_command == "resume":
        resumed = backend.control_action(args.project_id, "resume")
        if resumed.get("resume_blocked"):
            result = resumed
        else:
            tick = _run_orchestrator_script(args.project_id)
            result = {**resumed, "tick": tick, "claimed": tick.get("claimed")}
    elif args.factory_project_command == "pause":
        result = backend.control_action(
            args.project_id,
            "pause",
            reason=args.reason,
            actor=args.actor,
            origin=args.origin,
        )
    elif args.factory_project_command == "technical-hold":
        result = backend.control_action(
            args.project_id,
            "technical-hold",
            reason=args.reason,
            actor=args.actor,
            hold_kind=args.hold_kind,
        )
    else:
        result = backend.control_action(args.project_id, action_map[args.factory_project_command])
    if args.json:
        return _print_json(result)
    print(f"✓ Project {args.project_id}: {result.get('action')} -> {result.get('status') or 'ok'}")
    return 0


def cmd_worker_dispatch(args: argparse.Namespace) -> int:
    result = _run_orchestrator_script(args.project_id)
    if args.json:
        return _print_json(result)
    claimed = result.get("claimed")
    spawned = result.get("spawned_worker")
    print(f"✓ Factory tick: claimed={claimed.get('run_id') if isinstance(claimed, dict) else 'none'} spawned={spawned.get('pid') if isinstance(spawned, dict) else 'none'} monitored={result.get('monitor', {})}")
    return 0


def factory_command(args: argparse.Namespace) -> int:
    command = getattr(args, "factory_command", None)
    if command == "init":
        return cmd_init(args)
    if command == "agents":
        return cmd_agents(args)
    if command == "project":
        sub = getattr(args, "factory_project_command", None)
        if sub == "create":
            return cmd_project_create(args)
        if sub == "close":
            return cmd_project_close(args)
        if sub in {"reopen", "continue"}:
            return cmd_project_reopen(args)
        if sub == "link-notion":
            return cmd_project_link_notion(args)
        if sub == "takeover":
            return cmd_project_takeover(args)
        if sub == "release-takeover":
            return cmd_project_release_takeover(args)
        if sub == "declare-successor":
            return cmd_project_declare_successor(args)
        if sub in {"resume", "pause", "technical-hold", "tick", "resolve-state", "resolve", "reconcile", "unblock"}:
            return cmd_project_action(args)
    if command == "lane" and getattr(args, "factory_lane_command", None) == "create":
        return cmd_lane_create(args)
    if command == "task":
        sub = getattr(args, "factory_task_command", None)
        if sub == "create":
            return cmd_task_create(args)
        if sub == "close":
            return cmd_task_close(args)
    if command == "gate" and getattr(args, "factory_gate_command", None) == "record":
        return cmd_gate_record(args)
    if command == "worker" and getattr(args, "factory_worker_command", None) == "dispatch":
        return cmd_worker_dispatch(args)
    if command == "status":
        return cmd_status(args)
    return cmd_status(args)


def add_parser(subparsers) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "factory",
        help="SitioUno Software Factory orchestration state",
        description="Manage factory projects, lanes, tasks, gates, agents, and autonomous progress in Agent Core Postgres.",
    )
    parser.set_defaults(func=factory_command)
    subs = parser.add_subparsers(dest="factory_command")

    init = subs.add_parser("init", help="Verify Postgres Factory DB and seed agent roster")
    init.set_defaults(func=factory_command)

    agents = subs.add_parser("agents", help="List seeded factory agents")
    agents.add_argument("--json", action="store_true", help="Emit JSON")
    agents.set_defaults(func=factory_command)

    status = subs.add_parser("status", help="Show factory status")
    status.add_argument("project_id", nargs="?", help="Optional project id filter")
    status.add_argument("--json", action="store_true", help="Emit JSON")
    status.set_defaults(func=factory_command)

    project = subs.add_parser("project", help="Manage factory projects")
    project_sub = project.add_subparsers(dest="factory_project_command")
    project_create = project_sub.add_parser("create", help="Create/update a project and default method lanes")
    project_create.add_argument("name")
    project_create.add_argument("--project-id")
    project_create.add_argument("--repo-path")
    project_create.add_argument("--repo-remote")
    project_create.add_argument("--base-branch")
    project_create.add_argument("--repo-scope", choices=["zeus_only", "zeus_then_runtime", "runtime_only", "existing_project_change", "new_product_repo", "docs_or_research_only"], help="G0 repository strategy: Zeus, runtime, existing repo, new repo, or docs/research")
    project_create.add_argument("--work-intent", choices=["create_new_project", "add_functionality", "modify_existing_project", "maintain_existing_project", "docs_research"], help="G0 work intent for canonical routing")
    project_create.add_argument("--human-owner", default="Jean García")
    project_create.add_argument("--summary")
    project_create.add_argument("--risk-level", default="medium", choices=["low", "medium", "high", "critical"])
    project_create.add_argument("--autonomy-level", type=int, default=3)
    project_create.add_argument("--methodology", default="hybrid", choices=sorted(VALID_METHODS))
    project_create.add_argument("--no-default-lanes", action="store_true")
    project_create.add_argument("--json", action="store_true")
    project_create.set_defaults(func=factory_command)

    project_close = project_sub.add_parser("close", help="Canonically close/supersede a Factory project without enabling autonomy")
    project_close.add_argument("project_id")
    project_close.add_argument("--reason", required=True, help="Human-readable closure reason recorded in Factory DB")
    project_close.add_argument("--closure-type", default="administrative", choices=["administrative", "superseded", "deferred", "duplicate", "cancelled"])
    project_close.add_argument("--superseded-by-project-id")
    project_close.add_argument("--actor", default="factory-orchestrator")
    project_close.add_argument("--json", action="store_true")
    project_close.set_defaults(func=factory_command)

    project_reopen = project_sub.add_parser("reopen", aliases=["continue"], help="Canonically reopen/continue a terminal project without creating a detached successor")
    project_reopen.add_argument("project_id")
    project_reopen.add_argument("--reason", required=True, help="Evidence-backed continuation reason recorded in Factory DB")
    project_reopen.add_argument("--actor", default="factory-orchestrator")
    project_reopen.add_argument("--continuation-of", help="Optional lineage/predecessor project id")
    project_reopen.add_argument("--json", action="store_true")
    project_reopen.set_defaults(func=factory_command)

    project_link_notion = project_sub.add_parser("link-notion", help="Write/readback canonical project-specific Notion PM tracker metadata")
    project_link_notion.add_argument("project_id")
    project_link_notion.add_argument("--page-id", help="Notion page UUID or 32-char page id")
    project_link_notion.add_argument("--url", help="Notion tracker URL")
    project_link_notion.add_argument("--page-title", help="Human-readable Notion page title")
    project_link_notion.add_argument("--actor", default="factory-reporter")
    project_link_notion.add_argument("--json", action="store_true")
    project_link_notion.set_defaults(func=factory_command)

    project_takeover = project_sub.add_parser("takeover", help="Acquire a manual/operator single-writer lease that blocks autonomous dispatch")
    project_takeover.add_argument("project_id")
    project_takeover.add_argument("--holder", default="factory-orchestrator")
    project_takeover.add_argument("--reason", default="manual_takeover")
    project_takeover.add_argument("--ttl-minutes", type=int, default=180)
    project_takeover.add_argument("--worktree-path")
    project_takeover.add_argument("--session-id")
    project_takeover.add_argument("--json", action="store_true")
    project_takeover.set_defaults(func=factory_command)

    project_release_takeover = project_sub.add_parser("release-takeover", help="Release a manual/operator single-writer lease")
    project_release_takeover.add_argument("project_id")
    project_release_takeover.add_argument("--holder", default="factory-orchestrator")
    project_release_takeover.add_argument("--reason", default="manual_takeover_complete")
    project_release_takeover.add_argument("--json", action="store_true")
    project_release_takeover.set_defaults(func=factory_command)

    project_declare_successor = project_sub.add_parser(
        "declare-successor",
        help="Persist Jean-authorized predecessor→successor activation; the global tick evaluates and dispatches it",
    )
    project_declare_successor.add_argument("project_id", help="Completed/integrated predecessor project id")
    project_declare_successor.add_argument("successor_project_id", help="Paused successor project id")
    project_declare_successor.add_argument("--actor", required=True, help="Jean authority recorded in immutable succession metadata")
    project_declare_successor.add_argument("--reason", required=True, help="Why this successor may resume autonomously")
    project_declare_successor.add_argument("--allow-auto-resume", action="store_true", help="Explicitly authorize this one automatic successor activation")
    project_declare_successor.add_argument("--json", action="store_true")
    project_declare_successor.set_defaults(func=factory_command)

    project_pause = project_sub.add_parser("pause", help="Pause autonomy by explicit human/operator authority with audited provenance")
    project_pause.add_argument("project_id")
    project_pause.add_argument("--reason", required=True, help="Explicit human/operator reason for the manual pause")
    project_pause.add_argument("--actor", required=True, help="Human/operator identity; Factory system actors are rejected")
    project_pause.add_argument("--origin", required=True, help="Auditable request origin, such as the operator terminal or reviewed ticket")
    project_pause.add_argument("--json", action="store_true")
    project_pause.set_defaults(func=factory_command)

    project_technical_hold = project_sub.add_parser("technical-hold", help="Record a supervisable technical/dependency hold without disabling autonomy")
    project_technical_hold.add_argument("project_id")
    project_technical_hold.add_argument("--reason", required=True, help="Concrete technical/dependency condition")
    project_technical_hold.add_argument("--actor", required=True, help="Actor recording the technical/dependency hold")
    project_technical_hold.add_argument("--hold-kind", required=True, choices=["technical", "dependency"])
    project_technical_hold.add_argument("--json", action="store_true")
    project_technical_hold.set_defaults(func=factory_command)

    for action, help_text in {
        "resume": "Run resolve-state preflight, then enable autonomous incremental execution when dispatchable",
        "tick": "Force one deterministic orchestrator/dispatcher tick",
        "resolve-state": "Canonical resolve action: reconcile, repair resolved blockers, and classify holds/questions",
        "resolve": "Legacy alias for resolve-state",
        "reconcile": "Legacy alias for resolve-state",
        "unblock": "Legacy alias for resolve-state",
    }.items():
        sub = project_sub.add_parser(action, help=help_text)
        sub.add_argument("project_id")
        sub.add_argument("--json", action="store_true")
        sub.set_defaults(func=factory_command)

    lane = subs.add_parser("lane", help="Manage method lanes")
    lane_sub = lane.add_subparsers(dest="factory_lane_command")
    lane_create = lane_sub.add_parser("create", help="Create/update a lane")
    lane_create.add_argument("project_id")
    lane_create.add_argument("name")
    lane_create.add_argument("--methodology", required=True, choices=sorted(VALID_METHODS))
    lane_create.add_argument("--lane-id")
    lane_create.add_argument("--kanban-board", help="Explicit temporary Kanban bridge board. Omit for normal Factory lanes.")
    lane_create.add_argument("--branch")
    lane_create.add_argument("--worktree-path")
    lane_create.add_argument("--json", action="store_true")
    lane_create.set_defaults(func=factory_command)

    task = subs.add_parser("task", help="Manage factory tasks")
    task_sub = task.add_subparsers(dest="factory_task_command")
    task_create = task_sub.add_parser("create", help="Create a task/increment in the Factory DB")
    task_create.add_argument("project_id")
    task_create.add_argument("title")
    task_create.add_argument("--lane-id")
    task_create.add_argument("--description")
    task_create.add_argument("--phase", default="planning")
    task_create.add_argument("--owner")
    task_create.add_argument("--reviewer")
    task_create.add_argument("--engine", default="zeus")
    task_create.add_argument("--priority", type=int, default=100)
    task_create.add_argument("--branch", help="Override derived per-deliverable branch")
    task_create.add_argument("--worktree-path", help="Override derived isolated per-deliverable worktree")
    task_create.add_argument("--acceptance", action="append", help="Acceptance criterion; repeatable")
    task_create.add_argument("--json", action="store_true")
    task_create.set_defaults(func=factory_command)

    task_close = task_sub.add_parser("close", help="Close a task/increment with canonical evidence")
    task_close.add_argument("task_id")
    task_close.add_argument("--status", default="done", choices=["done", "verified", "accepted", "cancelled", "superseded"])
    task_close.add_argument("--summary", required=True, help="Evidence-backed result summary for the task")
    task_close.add_argument("--evidence-json", default="{}", help="JSON object with evidence such as commit, tests, artifact paths")
    task_close.add_argument("--actor", default="factory-orchestrator")
    task_close.add_argument("--no-reconcile", action="store_true", help="Do not immediately reconcile the parent project")
    task_close.add_argument("--json", action="store_true")
    task_close.set_defaults(func=factory_command)

    gate = subs.add_parser("gate", help="Record factory gates")
    gate_sub = gate.add_subparsers(dest="factory_gate_command")
    gate_record = gate_sub.add_parser("record", help="Record a gate result")
    gate_record.add_argument("project_id")
    gate_record.add_argument("gate_type", choices=["intake", "functional", "architecture", "planning", "implementation", "spec", "quality", "test", "security", "delivery", "critical_readiness"])
    gate_record.add_argument("status", choices=["pending", "passed", "failed", "waived"])
    gate_record.add_argument("--lane-id")
    gate_record.add_argument("--task-id")
    gate_record.add_argument("--reviewer")
    gate_record.add_argument("--notes")
    gate_record.add_argument("--json", action="store_true")
    gate_record.set_defaults(func=factory_command)

    worker = subs.add_parser("worker", help="Deterministic Factory worker controls")
    worker_sub = worker.add_subparsers(dest="factory_worker_command")
    dispatch = worker_sub.add_parser("dispatch", help="Run one generic status-driven Factory dispatch tick")
    dispatch.add_argument("project_id", nargs="?")
    dispatch.add_argument("--json", action="store_true")
    dispatch.set_defaults(func=factory_command)

    return parser

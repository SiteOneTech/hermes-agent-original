#!/usr/bin/env python3
"""Canonical Factory Orchestrator Tick.

Generic status-driven cron script: reads Agent Core Postgres Factory DB, monitors
running task runs, reconciles project state, claims at most one next increment
per project, and spawns the assigned Hermes worker with fresh context. No
project-specific routing and no SQLite fallback.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
if REPO.exists() and str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _home() -> Path:
    from hermes_constants import get_hermes_home

    return get_hermes_home()


def _watchdog_state_path() -> Path:
    return _home() / "factory" / "watchdog_state.json"


def _read_watchdog_state() -> dict[str, Any]:
    path = _watchdog_state_path()
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except Exception:
        return {}


def _write_watchdog_state(state: dict[str, Any]) -> None:
    path = _watchdog_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _gate_ts(gate: dict[str, Any]) -> tuple[str, int]:
    return (str(gate.get("created_at") or gate.get("timestamp") or ""), int(gate.get("gate_id") or 0))


def _effective_gates(gates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for gate in sorted(gates, key=_gate_ts, reverse=True):
        gate_type = str(gate.get("gate_type") or "").strip()
        if gate_type and gate_type not in latest:
            latest[gate_type] = gate
    return sorted(latest.values(), key=_gate_ts, reverse=True)


def _canonical_doc_lines(project: dict[str, Any], task: dict[str, Any]) -> list[str]:
    """Summarize the G1 documentation pack the spawned worker must read."""

    project_id = str(project.get("project_id") or task.get("project_id") or "")
    work_root = str(task.get("worktree_path") or project.get("repo_path") or "").strip()
    artifact_dir = "factory/projects/" + project_id if project_id else "factory/projects/<project_id>"
    metadata_raw = project.get("metadata")
    metadata = metadata_raw if isinstance(metadata_raw, dict) else {}
    artifact_value = metadata.get("artifact_dir")
    if isinstance(artifact_value, str) and artifact_value.strip():
        artifact_dir = artifact_value.strip()
    statuses = project.get("document_status") if isinstance(project.get("document_status"), list) else []
    entrypoint = f"{artifact_dir.rstrip('/')}/DOCUMENTATION_INDEX.md"
    if work_root:
        entrypoint = str(Path(work_root).expanduser() / entrypoint)
    lines = [
        "- Skill operativo común: `factory-agent-operating-canon` (obligatorio para todos los roles Factory).",
        f"- Entrada documental obligatoria: {entrypoint}",
        "- Antes de implementar o revisar, lee DOCUMENTATION_INDEX.md y los G1 docs que apliquen a tu fase; cita los paths usados en tu evidencia final.",
    ]
    if not statuses:
        lines.append("- document_status no vino en el payload; si la tarea no es de bootstrap/reconciliación, bloquea y pide reconciliación G1.")
        return lines
    blockers = [row for row in statuses if row.get("category") == "g1_required" and row.get("blocking")]
    lines.append(f"- G1 readiness: {len(statuses) - len(blockers)}/{len(statuses)} documentos sin blocker; blockers={len(blockers)}.")
    for row in [r for r in statuses if r.get("category") == "g1_required"][:20]:
        missing = [key for key in ("exists", "indexed", "committed", "validated", "reviewed") if not row.get(key)]
        state = "READY" if not missing else "BLOCKED missing=" + ",".join(missing)
        path = str(row.get("path") or row.get("file_name") or "")
        if work_root and path and not Path(path).is_absolute():
            path = str(Path(work_root).expanduser() / path)
        lines.append(f"  - {row.get('file_name')}: {state} path={path}")
    return lines


def _task_prompt(payload: dict[str, Any], claim: dict[str, Any]) -> str:
    task = claim["task"]
    run_type = str(claim.get("run_type") or "implementation")
    is_review = run_type == "review"
    project_id = task["project_id"]
    project = next((p for p in payload.get("projects", []) if p.get("project_id") == project_id), {})
    project_meta = project.get("metadata") if isinstance(project.get("metadata"), dict) else {}
    repo_strategy = project_meta.get("repo_strategy") if isinstance(project_meta.get("repo_strategy"), dict) else {}
    related_tasks = [t for t in payload.get("tasks", []) if t.get("project_id") == project_id]
    gates = _effective_gates([g for g in payload.get("gates", []) if g.get("project_id") == project_id])[:20]
    doc_lines = _canonical_doc_lines(project, task)
    return "\n".join(
        [
            "Eres un worker del SitioUno Software Factory. Ejecuta SOLO el incremento asignado y deja evidencia verificable." if not is_review else "Eres un reviewer del SitioUno Software Factory. Revisa SOLO el incremento asignado y decide si puede cerrarse.",
            "Fuente de verdad: Agent Core Postgres schema factory.*. Notion es solo reporte humano.",
            "Regla de eficiencia: no abras otro incremento; cierra este con evidencia, pruebas y resumen." if not is_review else "Regla de review: valida evidencia, artifacts y criterios. Si pasa, termina con STATE: DONE; si falla, termina con STATE: BLOCKED y razones/rework.",
            "",
            f"Proyecto: {project.get('name')} ({project_id})",
            f"G0 Repository Strategy: {repo_strategy.get('decision_label') or '—'} [{repo_strategy.get('repo_scope') or 'missing'} / {repo_strategy.get('work_intent') or '—'}]",
            f"G0 Decision: {repo_strategy.get('decision_summary') or '—'}",
            f"Repo raíz: {repo_strategy.get('primary_repo_path') or project.get('repo_path') or '—'}",
            f"Repo remoto: {repo_strategy.get('primary_repo_remote') or project.get('repo_remote') or '—'}",
            f"Base branch: {repo_strategy.get('base_branch') or project.get('base_branch') or 'main'}",
            f"Rama asignada del entregable: {task.get('branch') or '—'}",
            f"Worktree aislado asignado: {task.get('worktree_path') or '—'}",
            f"Tarea: {task.get('title')} ({task.get('task_id')})",
            f"Tipo de run: {run_type}",
            f"Fase: {task.get('phase')} · Engine: {task.get('engine')} · Run: {claim.get('run_id')}",
            f"Estado actual: {task.get('status') or '—'}",
            f"Descripción: {task.get('description') or '—'}",
            f"Acceptance criteria: {json.dumps(task.get('acceptance_criteria') or [], ensure_ascii=False)}",
            f"Dependencias: {json.dumps(task.get('dependencies') or [], ensure_ascii=False)}",
            "",
            "Documentación canónica / G1 Documentary Readiness:",
            *doc_lines,
            "",
            "Resumen/evidencia previa/rework:",
            str(task.get("result_summary") or "—")[-4000:],
            "",
            "Tareas del proyecto:",
            *[f"- {t.get('task_id')}: {t.get('title')} [{t.get('status')}] branch={t.get('branch') or '—'}" for t in related_tasks[:30]],
            "",
            "Gates recientes:",
            *[f"- {g.get('gate_type')}: {g.get('status')} reviewer={g.get('reviewer') or '—'}" for g in gates],
            "",
            "Reglas duras de seguridad/runtime:",
            "- Trabaja en el worktree aislado asignado; no modifiques el checkout principal ni otra rama del proyecto.",
            "- Cada entregable debe quedar en su rama/worktree propia y tener commit cuando el scope implique cambios de código/docs.",
            "- Si el repo remoto está aprobado, empuja la rama asignada después de validación local y evidencia. Cuando la política de gate/review del entregable lo permita, mantén la rama base/main al día con merge + push incremental; no acumules todo para el final.",
            "- No hagas deploy ni cambies credenciales salvo que la tarea lo pida explícitamente y el scope/gate lo permita.",
            "- No instales paquetes con pip/uv/apt/npm/pnpm ni modifiques entornos para resolver una tarea documental; si falta una dependencia, reporta BLOCKER.",
            "- No hagas escrituras directas a factory.* con psql/psycopg2/scripts ad-hoc. Para Factory DB usa solo `hermes factory status` y `hermes factory gate record`.",
            "- No escribas scripts temporales dentro del repo/proyecto salvo que sean artifacts requeridos; si creas un helper temporal, bórralo antes de terminar.",
            "",
            "Entrega obligatoria:",
            "1. Implementa/documenta exactamente el incremento.",
            "2. Ejecuta pruebas o verificaciones reales si aplica.",
            "3. Actualiza artifacts project-locales bajo factory/projects/<project_id>/ cuando toque planificación/QA/docs.",
            "4. Registra evidencia vía herramientas Factory si están disponibles; si no, deja resumen final con paths/comandos/resultados.",
            "5. Si necesitas decisión humana, formula UNA pregunta clara y bloquea solo lo necesario; sigue con tareas independientes si el alcance lo permite.",
        ]
    )


def _prepare_worktree(payload: dict[str, Any], claim: dict[str, Any]) -> dict[str, Any]:
    """Create/verify the isolated per-deliverable git worktree for the claimed task."""

    task = claim.get("task") or {}
    project_id = str(task.get("project_id") or "")
    project = next((p for p in payload.get("projects", []) if p.get("project_id") == project_id), {})
    project_meta = project.get("metadata") if isinstance(project.get("metadata"), dict) else {}
    strategy = project_meta.get("repo_strategy") if isinstance(project_meta.get("repo_strategy"), dict) else {}
    repo_raw = str(strategy.get("primary_repo_path") or project.get("repo_path") or "").strip()
    worktree_raw = str(task.get("worktree_path") or "").strip()
    repo_path = Path(repo_raw).expanduser()
    worktree_path = Path(worktree_raw).expanduser()
    branch = str(task.get("branch") or "").strip()
    base_branch = str(strategy.get("base_branch") or project.get("base_branch") or "main").strip() or "main"
    if not repo_raw or not branch or not worktree_raw:
        return {"ready": False, "reason": "missing_repo_branch_or_worktree", "cwd": repo_raw or None}
    if not repo_path.exists():
        return {"ready": False, "reason": "repo_path_missing", "repo_path": str(repo_path), "cwd": str(repo_path)}
    probe = subprocess.run(["git", "-C", str(repo_path), "rev-parse", "--is-inside-work-tree"], text=True, capture_output=True, timeout=10, check=False)
    if probe.returncode != 0:
        return {"ready": False, "reason": "repo_path_not_git", "repo_path": str(repo_path), "stderr": probe.stderr[-500:], "cwd": str(repo_path)}
    if worktree_path.exists():
        wt_probe = subprocess.run(["git", "-C", str(worktree_path), "rev-parse", "--is-inside-work-tree"], text=True, capture_output=True, timeout=10, check=False)
        if wt_probe.returncode == 0:
            return {"ready": True, "reason": "worktree_exists", "repo_path": str(repo_path), "branch": branch, "worktree_path": str(worktree_path), "cwd": str(worktree_path)}
        return {"ready": False, "reason": "worktree_path_exists_not_git", "repo_path": str(repo_path), "worktree_path": str(worktree_path), "cwd": str(repo_path)}
    worktree_path.parent.mkdir(parents=True, exist_ok=True)
    add = subprocess.run(
        ["git", "-C", str(repo_path), "worktree", "add", "-B", branch, str(worktree_path), base_branch],
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    if add.returncode != 0:
        return {"ready": False, "reason": "git_worktree_add_failed", "repo_path": str(repo_path), "branch": branch, "worktree_path": str(worktree_path), "stdout": add.stdout[-500:], "stderr": add.stderr[-500:], "cwd": str(repo_path)}
    return {"ready": True, "reason": "worktree_created", "repo_path": str(repo_path), "branch": branch, "worktree_path": str(worktree_path), "cwd": str(worktree_path)}


def _spawn_worker(db: Any, payload: dict[str, Any], claim: dict[str, Any]) -> dict[str, Any]:
    run_id = claim["run_id"]
    worker = str(claim.get("worker_profile") or "factory-orchestrator")
    base = _home() / "factory" / "runs" / run_id
    base.mkdir(parents=True, exist_ok=True)
    prompt_path = base / "prompt.md"
    log_path = base / "worker.log"
    exit_path = base / "exit_code.txt"
    worktree_state = _prepare_worktree(payload, claim)
    prompt = _task_prompt(payload, claim) + "\n\nPreparación runtime de worktree:\n" + json.dumps(worktree_state, ensure_ascii=False, indent=2)
    prompt_path.write_text(prompt, encoding="utf-8")

    wrapper = "\n".join(
        [
            "import pathlib, subprocess, sys",
            f"prompt = pathlib.Path({str(prompt_path)!r}).read_text(encoding='utf-8')",
            f"log_path = pathlib.Path({str(log_path)!r})",
            f"exit_path = pathlib.Path({str(exit_path)!r})",
            "with log_path.open('w', encoding='utf-8', errors='replace') as log:",
            f"    proc = subprocess.run(['hermes', '--profile', {worker!r}, 'chat', '-q', prompt], stdout=log, stderr=subprocess.STDOUT, text=True)",
            "exit_path.write_text(str(proc.returncode), encoding='utf-8')",
        ]
    )
    # Detach stdio from the cron runner.  Cron captures stdout/stderr with
    # pipes; if the spawned worker inherits those FDs, subprocess.communicate()
    # in the cron runner waits for the worker to exit and the tick appears to
    # time out even though the parent script already returned.
    cwd_value = worktree_state.get("cwd") if isinstance(worktree_state, dict) else None
    cwd_path = str(cwd_value) if cwd_value and Path(str(cwd_value)).exists() else None
    proc = subprocess.Popen(
        [sys.executable, "-c", wrapper],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=cwd_path,
        start_new_session=True,
        close_fds=True,
    )
    db.mark_run_spawned(run_id, process_id=proc.pid, log_path=str(log_path), prompt_path=str(prompt_path))
    db.update_run_metadata(run_id, {"exit_path": str(exit_path), "spawned_by": "factory_orchestrator_tick", "worktree_preparation": worktree_state, "worker_cwd": cwd_path})
    return {"run_id": run_id, "worker_profile": worker, "pid": proc.pid, "log_path": str(log_path), "prompt_path": str(prompt_path), "worktree_preparation": worktree_state, "worker_cwd": cwd_path}


def main() -> None:
    try:
        from hermes_cli import factory_backend, factory_pg

        db = factory_backend.get_backend()
        project_id = os.environ.get("FACTORY_TICK_PROJECT_ID") or None
        supervisor = []
        if hasattr(db, "supervisor_health_check"):
            before = db.status(project_id)
            if project_id:
                supervisor_targets = [project_id]
            else:
                supervisor_targets = [
                    str(project.get("project_id"))
                    for project in before.get("projects", [])
                    if project.get("autonomous_enabled") or str(project.get("status") or "") in {"blocked", "delivery_hold"}
                ]
            for target in supervisor_targets:
                result = db.supervisor_health_check(target, repair=True)
                if result.get("violations") or result.get("repairs"):
                    supervisor.append(result)
        tick = db.force_tick(project_id)
        spawned = None
        if tick.get("claimed"):
            # Build the worker prompt from post-claim state.  Using the pre-tick
            # snapshot makes task lists and gate state stale (e.g. F3 still
            # shown as running while F4 has just been claimed), which confuses
            # autonomous workers and reviewers.
            prompt_payload = db.status(project_id)
            spawned = _spawn_worker(db, prompt_payload, tick["claimed"])
        after = db.status()
        state = _read_watchdog_state()
        claimed_null_rounds = 0 if tick.get("claimed") else int(state.get("claimed_null_rounds") or 0) + 1
        state["claimed_null_rounds"] = claimed_null_rounds
        state["last_tick_at"] = _now()
        _write_watchdog_state(state)
        alerts = factory_pg.factory_watchdog_alerts(after, claimed_null_rounds=claimed_null_rounds, project_id=project_id)
        report = {
            "job": "factory_orchestrator_tick",
            "db_backend": after.get("db_backend"),
            "timestamp": _now(),
            "monitor": tick.get("monitor"),
            "supervisor": supervisor,
            "unblocked": tick.get("unblocked"),
            "reconciled": tick.get("reconciled"),
            "claimed": tick.get("claimed"),
            "spawned_worker": spawned,
            "claimed_null_rounds": claimed_null_rounds,
            "alerts": alerts,
            "counts": {
                "projects": len(after.get("projects", [])),
                "tasks": len(after.get("tasks", [])),
                "active_runs": len([r for r in after.get("task_runs", []) if str(r.get("status")) in {"queued", "running"}]),
            },
            "needs_attention": bool(spawned or tick.get("claimed") or alerts),
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
    except Exception as exc:
        print(json.dumps({"job": "factory_orchestrator_tick", "error": str(exc), "timestamp": _now()}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()

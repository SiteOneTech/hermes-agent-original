#!/usr/bin/env python3
"""Factory watchdog and autonomous repair launcher.

Script-only cron target. It stays silent when there are no human-required
conditions. Deterministic checks compute workflow alerts and progress
fingerprints; repairable conditions launch an autonomous Hermes reasoning
supervisor with a prepared prompt and audit files. Jean is notified only when the
reasoning supervisor explicitly reports ``SUPERVISOR_STATUS: NEEDS_HUMAN`` or
when the repair machinery itself fails repeatedly.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psutil

REPO = Path(__file__).resolve().parents[2]
if REPO.exists() and str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

SUPERVISOR_STATUSES = {"RESOLVED", "NO_ACTION", "NEEDS_HUMAN", "FAILED"}
AUTOREPAIR_ALERT_TYPES = {
    "autonomous_project_blocked_too_long",
    "blocked_without_human_question",
    "delivery_hold_autoresolvable_blocked_work",
    "orphan_inflight_without_active_run",
    "cron_claimed_null_repeated",
    "factory_progress_stalled",
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso_now() -> str:
    return _now().isoformat().replace("+00:00", "Z")


def _home() -> Path:
    from hermes_constants import get_hermes_home

    return get_hermes_home()


def _state_path() -> Path:
    override = os.environ.get("FACTORY_WATCHDOG_STATE_PATH")
    if override:
        return Path(override).expanduser()
    return _home() / "factory" / "watchdog_alert_state.json"


def _progress_state_path() -> Path:
    override = os.environ.get("FACTORY_PROGRESS_STATE_PATH")
    if override:
        return Path(override).expanduser()
    return _home() / "factory" / "watchdog_progress_state.json"


def _supervisor_runs_dir() -> Path:
    override = os.environ.get("FACTORY_SUPERVISOR_RUNS_DIR")
    if override:
        return Path(override).expanduser()
    return _home() / "factory" / "watchdog_supervisor_runs"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except Exception:
        return {}


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _parse_dt(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _unsuppressed(alerts: list[dict[str, Any]], state: dict[str, Any], suppress_minutes: int) -> list[dict[str, Any]]:
    sent = state.setdefault("sent", {})
    now = _now()
    out: list[dict[str, Any]] = []
    for alert in alerts:
        key = str(alert.get("alert_key") or alert.get("alert_type") or "unknown")
        try:
            alert_suppress_minutes = int(alert.get("suppress_minutes") or suppress_minutes)
        except Exception:
            alert_suppress_minutes = suppress_minutes
        last_sent = _parse_dt(sent.get(key))
        if not last_sent:
            legacy_prefixes = alert.get("legacy_alert_key_prefixes")
            if isinstance(legacy_prefixes, list):
                legacy_times = [
                    parsed
                    for sent_key, sent_value in sent.items()
                    if any(str(sent_key).startswith(str(prefix)) for prefix in legacy_prefixes)
                    for parsed in [_parse_dt(sent_value)]
                    if parsed
                ]
                if legacy_times:
                    last_sent = max(legacy_times)
        if last_sent and (now - last_sent).total_seconds() < alert_suppress_minutes * 60:
            continue
        sent[key] = now.isoformat().replace("+00:00", "Z")
        out.append(alert)
    return out


def _render(alerts: list[dict[str, Any]]) -> str:
    lines = ["🏭 Factory supervisor — Jean action required", ""]
    for alert in alerts:
        lines.append(f"- {alert.get('alert_type')} · {alert.get('severity')}")
        if alert.get("project_id"):
            lines.append(f"  - Proyecto: {alert.get('project_id')}")
        if alert.get("task_id"):
            lines.append(f"  - Tarea: {alert.get('task_id')}")
        lines.append(f"  - {alert.get('message')}")
        if alert.get("same_rounds") is not None:
            lines.append(f"  - Rondas sin progreso medible: {alert.get('same_rounds')}")
        if alert.get("progress_fingerprint"):
            lines.append(f"  - Fingerprint: {str(alert.get('progress_fingerprint'))[:16]}")
        if alert.get("supervisor_run_id"):
            lines.append(f"  - Supervisor run: {alert.get('supervisor_run_id')}")
        if alert.get("supervisor_output_path"):
            lines.append(f"  - Log: {alert.get('supervisor_output_path')}")
        if alert.get("jean_question"):
            lines.append(f"  - Pregunta para Jean: {alert.get('jean_question')}")
    lines.append("")
    lines.append("No se enviará ruido periódico: el watchdog intenta reparar primero. Esta notificación significa que el supervisor razonador pidió una decisión humana o la autorreparación falló repetidamente.")
    return "\n".join(lines)


def _task_counts(tasks: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for task in tasks:
        status = str(task.get("status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
    return counts


def _safe_git(repo_path: Path, args: list[str]) -> str:
    if not repo_path.exists():
        return ""
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_path), *args],
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
    except Exception:
        return ""
    return (proc.stdout or "").strip() if proc.returncode == 0 else ""


def _artifact_signature(repo_path: Path, artifact_dir: str) -> dict[str, Any]:
    root = repo_path / artifact_dir if repo_path.exists() else Path()
    if not root.exists() or not root.is_dir():
        return {"exists": False}
    file_count = 0
    total_size = 0
    max_mtime = 0.0
    latest_path = ""
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            stat = path.stat()
        except OSError:
            continue
        file_count += 1
        total_size += int(stat.st_size)
        if stat.st_mtime >= max_mtime:
            max_mtime = stat.st_mtime
            latest_path = str(path.relative_to(root))
    return {
        "exists": True,
        "file_count": file_count,
        "total_size": total_size,
        "latest_mtime": int(max_mtime),
        "latest_file": latest_path,
    }


def _run_file_signature(run: dict[str, Any]) -> dict[str, Any]:
    log_path = Path(str(run.get("log_path") or "")).expanduser() if run.get("log_path") else None
    metadata = run.get("metadata") if isinstance(run.get("metadata"), dict) else {}
    exit_path = Path(str(metadata.get("exit_path"))).expanduser() if metadata.get("exit_path") else None
    out: dict[str, Any] = {
        "run_id": run.get("run_id"),
        "task_id": run.get("task_id"),
        "status": run.get("status"),
    }
    if log_path and log_path.exists():
        try:
            stat = log_path.stat()
            out.update({"log_size": int(stat.st_size), "log_mtime": int(stat.st_mtime)})
        except OSError:
            pass
    if exit_path:
        out["exit_exists"] = exit_path.exists()
    return out


def _project_progress_snapshot(payload: dict[str, Any], project: dict[str, Any]) -> dict[str, Any]:
    pid = str(project.get("project_id") or "")
    tasks = [task for task in payload.get("tasks", []) if str(task.get("project_id") or "") == pid]
    runs = [run for run in payload.get("task_runs", []) if str(run.get("project_id") or "") == pid]
    gates = [gate for gate in payload.get("gates", []) if str(gate.get("project_id") or "") == pid]
    active_runs = [run for run in runs if str(run.get("status") or "") in {"queued", "running"}]
    metadata = project.get("metadata") if isinstance(project.get("metadata"), dict) else {}
    repo_path = Path(str(project.get("repo_path") or "")).expanduser()
    artifact_dir = str(metadata.get("artifact_dir") or f"factory/projects/{pid}")
    head = _safe_git(repo_path, ["rev-parse", "HEAD"])
    dirty = _safe_git(repo_path, ["status", "--short", "--", artifact_dir])
    latest_run = max(
        (str(run.get("finished_at") or run.get("started_at") or ""), str(run.get("run_id") or "")) for run in runs
    ) if runs else ("", "")
    latest_gate = max(
        (str(gate.get("timestamp") or gate.get("created_at") or ""), int(gate.get("gate_id") or 0)) for gate in gates
    ) if gates else ("", 0)
    return {
        "project_id": pid,
        "project_status": project.get("status"),
        "autonomous_enabled": bool(project.get("autonomous_enabled")),
        "task_counts": _task_counts(tasks),
        "active_runs": [_run_file_signature(run) for run in active_runs],
        "latest_run": latest_run,
        "latest_gate": latest_gate,
        "repo_head": head,
        "repo_dirty_factory_lines": len([line for line in dirty.splitlines() if line.strip()]),
        "repo_dirty_factory_sample": dirty.splitlines()[:10],
        "artifact_signature": _artifact_signature(repo_path, artifact_dir),
    }


def _project_has_open_or_active_work(payload: dict[str, Any], pid: str) -> bool:
    for run in payload.get("task_runs", []):
        if str(run.get("project_id") or "") == pid and str(run.get("status") or "") in {"queued", "running"}:
            return True
    open_statuses = {"todo", "ready", "rework", "blocked", "claimed", "running", "in_progress", "review_ready", "review_running"}
    for task in payload.get("tasks", []):
        if str(task.get("project_id") or "") == pid and str(task.get("status") or "") in open_statuses:
            return True
    return False


def _progress_stall_alerts(payload: dict[str, Any], state: dict[str, Any]) -> list[dict[str, Any]]:
    threshold = int(os.environ.get("FACTORY_PROGRESS_STALLED_ROUNDS", "3"))
    projects_state = state.setdefault("projects", {})
    alerts: list[dict[str, Any]] = []
    for project in payload.get("projects", []):
        pid = str(project.get("project_id") or "")
        if not pid or not project.get("autonomous_enabled"):
            continue
        if str(project.get("status") or "") not in {"active", "blocked", "delivery_hold"}:
            continue
        if not _project_has_open_or_active_work(payload, pid):
            continue
        snapshot = _project_progress_snapshot(payload, project)
        fingerprint = hashlib.sha256(json.dumps(snapshot, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
        previous = projects_state.get(pid) if isinstance(projects_state.get(pid), dict) else {}
        same_rounds = int(previous.get("same_rounds") or 0) + 1 if previous.get("fingerprint") == fingerprint else 0
        projects_state[pid] = {
            "fingerprint": fingerprint,
            "same_rounds": same_rounds,
            "last_checked_at": _iso_now(),
            "snapshot": snapshot,
        }
        if same_rounds >= threshold:
            alerts.append({
                "alert_key": f"factory:{pid}:progress-stalled:{fingerprint[:12]}",
                "alert_type": "factory_progress_stalled",
                "severity": "high",
                "project_id": pid,
                "message": f"Factory project {pid} has shown no measurable progress for {same_rounds} watchdog rounds.",
                "same_rounds": same_rounds,
                "progress_fingerprint": fingerprint,
                "progress_snapshot": snapshot,
                "supervisor_action": "launch_reasoning_supervisor",
            })
    return alerts


def _project_scoped_payload(payload: dict[str, Any], project_id: str | None) -> dict[str, Any]:
    if not project_id:
        return payload
    scoped: dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, list):
            scoped[key] = [
                item for item in value
                if not isinstance(item, dict) or str(item.get("project_id") or project_id) == project_id
            ]
        else:
            scoped[key] = value
    return scoped


def _supervisor_group_key(alerts: list[dict[str, Any]]) -> str:
    project_id = next((str(alert.get("project_id")) for alert in alerts if alert.get("project_id")), "global")
    safe_project = re.sub(r"[^a-zA-Z0-9_.-]+", "-", project_id)[:80] or "global"
    return safe_project


def _supervisor_fingerprint(alerts: list[dict[str, Any]], payload: dict[str, Any]) -> str:
    relevant = {
        "alerts": alerts,
        "project_payload": _project_scoped_payload(payload, next((str(a.get("project_id")) for a in alerts if a.get("project_id")), None)),
    }
    return hashlib.sha256(json.dumps(relevant, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()


def _hermes_bin() -> str:
    override = os.environ.get("FACTORY_SUPERVISOR_HERMES_BIN")
    if override:
        return override
    repo_bin = REPO / "venv" / "bin" / "hermes"
    if repo_bin.exists():
        return str(repo_bin)
    found = shutil.which("hermes")
    if found:
        return found
    raise RuntimeError("Cannot launch Factory reasoning supervisor: hermes binary not found")


def _build_supervisor_prompt(group_id: str, alerts: list[dict[str, Any]], payload: dict[str, Any]) -> str:
    project_id = next((str(alert.get("project_id")) for alert in alerts if alert.get("project_id")), None)
    context_payload = _project_scoped_payload(payload, project_id)
    context_json = json.dumps(
        {
            "triggered_at": _iso_now(),
            "group_id": group_id,
            "project_id": project_id,
            "alerts": alerts,
            "factory_status_payload": context_payload,
        },
        ensure_ascii=False,
        indent=2,
        default=str,
    )
    return textwrap.dedent(
        f"""
        [Workspace::v1: /home/jean/Projects/hermes-agent-original]
        Eres Zeus actuando como SUPERVISOR AUTÓNOMO del Software Factory de SitioUno.

        El watchdog determinístico detectó una condición reparable. Jean NO quiere recibir alertas repetidas para esto: debes razonar, inspeccionar estado real, reparar lo que sea canónico y solo pedir intervención humana si realmente hay una decisión de negocio/producto, credencial física, acceso externo, pago, llamada a terceros, o algo que no puedas resolver con herramientas.

        REGLAS DURAS:
        - No respondas con un plan sin actuar. Usa herramientas reales.
        - Sigue systematic-debugging: diagnostica raíz antes de cambiar.
        - Puedes operar el control-plane Factory: leer status, logs, runs, DB, corregir estados huérfanos, relanzar tick, resolver blockers canónicos, ajustar perfiles/herramientas de Factory si la raíz es runtime/config.
        - No hagas trabajo de producto manual fuera del Factory salvo que sea estrictamente reparación del runtime/control-plane. El producto debe seguir fluyendo por tareas Factory.
        - Notion está desactivado/no-bloqueante para Factory hasta que Jean lo reactive explícitamente.
        - Si una tarea está parada por falta de tool/skill/perfil, corrige la configuración canónica del perfil o la matriz, verifica, y deja evidencia.
        - Si hay una pregunta humana pendiente o una decisión real de Jean, no inventes: deja una pregunta concreta.
        - Antes de cerrar, verifica con comandos reales que el bloqueo o estancamiento cambió, o explica por qué no pudo cambiar.

        CONTEXTO DETERMINÍSTICO DEL WATCHDOG:
        ```json
        {context_json}
        ```

        FORMATO FINAL OBLIGATORIO — las últimas líneas deben incluir exactamente una de estas:
        SUPERVISOR_STATUS: RESOLVED
        SUPERVISOR_STATUS: NO_ACTION
        SUPERVISOR_STATUS: NEEDS_HUMAN
        SUPERVISOR_STATUS: FAILED

        También incluye:
        SUPERVISOR_SUMMARY: <una línea concreta con lo que hiciste/verificaste>

        Si y solo si usas NEEDS_HUMAN, incluye:
        JEAN_QUESTION: <pregunta exacta y accionable para Jean>
        """
    ).strip()


def _is_pid_running(pid: Any) -> bool:
    try:
        pid_int = int(pid)
    except Exception:
        return False
    return pid_int > 0 and psutil.pid_exists(pid_int)


def _parse_supervisor_output(text: str) -> dict[str, str | None]:
    status: str | None = None
    summary: str | None = None
    jean_question: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        upper = stripped.upper()
        if upper.startswith("SUPERVISOR_STATUS:"):
            candidate = stripped.split(":", 1)[1].strip().split()[0].upper() if ":" in stripped else ""
            if candidate in SUPERVISOR_STATUSES:
                status = candidate
        elif upper.startswith("SUPERVISOR_SUMMARY:"):
            summary = stripped.split(":", 1)[1].strip() if ":" in stripped else ""
        elif upper.startswith("JEAN_QUESTION:"):
            jean_question = stripped.split(":", 1)[1].strip() if ":" in stripped else ""
    return {"status": status, "summary": summary, "jean_question": jean_question}


def _read_exit_code(path: Path | None) -> int | None:
    if not path or not path.exists():
        return None
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except Exception:
        return None


def _completion_alert(group_id: str, entry: dict[str, Any]) -> dict[str, Any] | None:
    status = str(entry.get("status") or "")
    exit_code = entry.get("exit_code")
    failure_threshold = int(os.environ.get("FACTORY_SUPERVISOR_FAILURE_ALERTS", "5"))
    if status in {"RESOLVED", "NO_ACTION"}:
        return None
    if status == "NEEDS_HUMAN":
        return {
            "alert_key": f"factory:supervisor:{group_id}:{entry.get('run_id')}:needs-human",
            "alert_type": "factory_reasoning_supervisor_needs_human",
            "severity": "high",
            "project_id": entry.get("project_id"),
            "message": entry.get("summary") or "Factory reasoning supervisor needs Jean input.",
            "jean_question": entry.get("jean_question") or "Supervisor requested Jean input but did not provide a question; inspect the run log.",
            "supervisor_run_id": entry.get("run_id"),
            "supervisor_output_path": entry.get("output_path"),
        }
    if status == "FAILED" or (exit_code is not None and int(exit_code) != 0):
        failures = int(entry.get("failure_count") or 1)
        if failures < failure_threshold:
            return None
        return {
            "alert_key": f"factory:supervisor:{group_id}:failed",
            "alert_type": "factory_reasoning_supervisor_failed",
            "severity": "high",
            "project_id": entry.get("project_id"),
            "message": f"Factory reasoning supervisor failed {failures} time(s) while trying to auto-repair; inspect log before asking Jean for product decisions.",
            "supervisor_run_id": entry.get("run_id"),
            "supervisor_output_path": entry.get("output_path"),
            "suppress_minutes": int(os.environ.get("FACTORY_SUPERVISOR_FAILURE_NOTIFY_COOLDOWN_MINUTES", "360")),
            "legacy_alert_key_prefixes": [f"factory:supervisor:{group_id}:fsup-"],
        }
    return None


def _refresh_supervisor_runs(state: dict[str, Any]) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    runs = state.setdefault("supervisor_runs", {})
    for group_id, entry in list(runs.items()):
        if not isinstance(entry, dict):
            continue
        if entry.get("completed_notified"):
            continue
        if entry.get("status") in SUPERVISOR_STATUSES:
            alert = _completion_alert(group_id, entry)
            if alert:
                alerts.append(alert)
            entry["completed_notified"] = True
            continue
        if _is_pid_running(entry.get("pid")):
            continue
        output_path = Path(str(entry.get("output_path") or "")) if entry.get("output_path") else None
        exit_path = Path(str(entry.get("exit_path") or "")) if entry.get("exit_path") else None
        output_text = ""
        if output_path and output_path.exists():
            try:
                output_text = output_path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                output_text = ""
        parsed = _parse_supervisor_output(output_text)
        exit_code = _read_exit_code(exit_path)
        status = parsed.get("status") or ("FAILED" if exit_code not in (0, None) else "FAILED")
        previous_failures = int(entry.get("failure_count") or 0)
        entry.update({
            "status": status,
            "summary": parsed.get("summary"),
            "jean_question": parsed.get("jean_question"),
            "exit_code": exit_code,
            "completed_at": _iso_now(),
        })
        if status == "FAILED":
            entry["failure_count"] = previous_failures + 1
        alert = _completion_alert(group_id, entry)
        if alert:
            alerts.append(alert)
        entry["completed_notified"] = True
    return alerts


def _supervisor_recently_launched(entry: dict[str, Any], fingerprint: str) -> bool:
    if entry.get("fingerprint") != fingerprint:
        return False
    if _is_pid_running(entry.get("pid")):
        return True
    if entry.get("status") == "NEEDS_HUMAN":
        return True
    launched_at = _parse_dt(entry.get("started_at"))
    cooldown = int(os.environ.get("FACTORY_SUPERVISOR_REPAIR_COOLDOWN_MINUTES", "30"))
    if launched_at and (_now() - launched_at).total_seconds() < cooldown * 60:
        return True
    return False


def _write_supervisor_runner(run_dir: Path, prompt_path: Path, output_path: Path, exit_path: Path) -> Path:
    profile = os.environ.get("FACTORY_SUPERVISOR_PROFILE", "default")
    toolsets = os.environ.get("FACTORY_SUPERVISOR_TOOLSETS", "terminal,file,factory,cronjob,session_search,skills,web")
    skills = os.environ.get("FACTORY_SUPERVISOR_SKILLS", "software-factory-orchestration,systematic-debugging,hermes-agent")
    hermes = _hermes_bin()
    supervisor_query = (
        "Lee y sigue exactamente el prompt/contexto del supervisor Factory guardado en "
        f"{prompt_path}. Usa la herramienta read_file para cargarlo completo antes de actuar. "
        "No le preguntes a Jean salvo que ese prompt y la evidencia demuestren una decisión humana real."
    )
    runner = run_dir / "run_supervisor.sh"
    runner.write_text(
        "#!/usr/bin/env bash\n"
        "set +e\n"
        f"cd {shlex_quote(str(REPO))}\n"
        f"{shlex_quote(hermes)} --profile {shlex_quote(profile)} chat -Q --source factory_watchdog_supervisor --max-turns 90 -t {shlex_quote(toolsets)} -s {shlex_quote(skills)} -q {shlex_quote(supervisor_query)} > {shlex_quote(str(output_path))} 2>&1\n"
        "code=$?\n"
        f"printf '%s\n' \"$code\" > {shlex_quote(str(exit_path))}\n"
        "exit $code\n",
        encoding="utf-8",
    )
    runner.chmod(0o700)
    return runner


def shlex_quote(value: str) -> str:
    import shlex

    return shlex.quote(value)


def _launch_reasoning_supervisor(group_id: str, alerts: list[dict[str, Any]], payload: dict[str, Any], state: dict[str, Any]) -> None:
    if os.environ.get("FACTORY_AUTOREPAIR_ENABLED", "1").strip().lower() in {"0", "false", "no", "off"}:
        return
    runs = state.setdefault("supervisor_runs", {})
    fingerprint = _supervisor_fingerprint(alerts, payload)
    existing = runs.get(group_id) if isinstance(runs.get(group_id), dict) else {}
    if _supervisor_recently_launched(existing, fingerprint):
        return

    project_id = next((str(alert.get("project_id")) for alert in alerts if alert.get("project_id")), None)
    run_id = f"fsup-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{group_id}-{fingerprint[:8]}"
    run_dir = _supervisor_runs_dir() / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = run_dir / "prompt.md"
    output_path = run_dir / "output.log"
    exit_path = run_dir / "exit_code.txt"
    prompt_path.write_text(_build_supervisor_prompt(group_id, alerts, payload), encoding="utf-8")
    runner = _write_supervisor_runner(run_dir, prompt_path, output_path, exit_path)
    proc = subprocess.Popen(
        ["bash", str(runner)],
        cwd=str(REPO),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    runs[group_id] = {
        "run_id": run_id,
        "project_id": project_id,
        "fingerprint": fingerprint,
        "alert_types": [alert.get("alert_type") for alert in alerts],
        "alert_keys": [alert.get("alert_key") for alert in alerts],
        "pid": proc.pid,
        "started_at": _iso_now(),
        "prompt_path": str(prompt_path),
        "output_path": str(output_path),
        "exit_path": str(exit_path),
        "runner_path": str(runner),
        "status": "running",
        "failure_count": int(existing.get("failure_count") or 0),
    }


def _alert_requires_direct_human(alert: dict[str, Any]) -> bool:
    if alert.get("requires_human") is True:
        return True
    alert_type = str(alert.get("alert_type") or "")
    return alert_type in {"human_question_pending", "factory_reasoning_supervisor_needs_human"}


def _route_repairable_alerts(alerts: list[dict[str, Any]], payload: dict[str, Any], state: dict[str, Any]) -> list[dict[str, Any]]:
    human_alerts = _refresh_supervisor_runs(state)
    grouped: dict[str, list[dict[str, Any]]] = {}
    for alert in alerts:
        if _alert_requires_direct_human(alert) or str(alert.get("alert_type") or "") not in AUTOREPAIR_ALERT_TYPES:
            human_alerts.append(alert)
            continue
        grouped.setdefault(_supervisor_group_key([alert]), []).append(alert)
    for group_id, group_alerts in grouped.items():
        _launch_reasoning_supervisor(group_id, group_alerts, payload, state)
    return human_alerts


def main() -> None:
    from hermes_cli import factory_backend, factory_pg

    threshold = int(os.environ.get("FACTORY_BLOCKED_ALERT_MINUTES", "60"))
    suppress = int(os.environ.get("FACTORY_ALERT_SUPPRESS_MINUTES", "60"))
    tick_state = _read_json(_home() / "factory" / "watchdog_state.json")
    claimed_null_rounds = int(tick_state.get("claimed_null_rounds") or 0)
    db = factory_backend.get_backend()
    payload = db.status()
    classified = factory_pg.classify_factory_blockers(payload)
    factory_pg.record_factory_blocker_actions(classified, payload=payload)
    payload = db.status()
    alerts = factory_pg.factory_watchdog_alerts(payload, blocked_minutes=threshold, claimed_null_rounds=claimed_null_rounds)
    progress_state_path = _progress_state_path()
    progress_state = _read_json(progress_state_path)
    alerts.extend(_progress_stall_alerts(payload, progress_state))
    _write_json(progress_state_path, progress_state)
    state_path = _state_path()
    state = _read_json(state_path)
    human_alerts = _route_repairable_alerts(alerts, payload, state)
    send = _unsuppressed(human_alerts, state, suppress)
    state["last_checked_at"] = _iso_now()
    state["last_alert_count"] = len(alerts)
    state["last_human_alert_count"] = len(human_alerts)
    _write_json(state_path, state)
    if send:
        print(_render(send))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"🏭 Factory watchdog error: {exc}")
        sys.exit(1)

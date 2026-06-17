#!/usr/bin/env python3
"""Factory watchdog notifier.

Script-only cron target. It stays silent when there are no unsuppressed alerts;
non-empty stdout is a concise human-facing alert suitable for origin/Telegram
delivery.

The watchdog is deterministic. It does not implement product work. It computes
objective workflow alerts and progress fingerprints; when progress stalls, it
alerts Zeus/Jean with enough evidence for a reasoning supervisor to inspect and
repair the root cause.
"""
from __future__ import annotations

import hashlib
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


def _now() -> datetime:
    return datetime.now(timezone.utc)


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
        last_sent = _parse_dt(sent.get(key))
        if last_sent and (now - last_sent).total_seconds() < suppress_minutes * 60:
            continue
        sent[key] = now.isoformat().replace("+00:00", "Z")
        out.append(alert)
    return out


def _render(alerts: list[dict[str, Any]]) -> str:
    lines = ["🏭 Factory watchdog — acción requerida", ""]
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
        if alert.get("recommended_action"):
            lines.append(f"  - Acción: {alert.get('recommended_action')}")
    lines.append("")
    lines.append("Zeus debe resolver automáticamente los casos rutinarios. Si esta alerta llegó a Jean, es porque el watchdog detectó un bloqueo persistente, una pregunta humana pendiente, una anomalía de runtime o estancamiento determinístico sin progreso medible.")
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
            "last_checked_at": _now().isoformat().replace("+00:00", "Z"),
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
                "recommended_action": "invoke_zeus_reasoning_supervisor_with_snapshot_and_repair_root_cause",
            })
    return alerts


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
    send = _unsuppressed(alerts, state, suppress)
    state["last_checked_at"] = _now().isoformat().replace("+00:00", "Z")
    state["last_alert_count"] = len(alerts)
    _write_json(state_path, state)
    if send:
        print(_render(send))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"🏭 Factory watchdog error: {exc}")
        sys.exit(1)

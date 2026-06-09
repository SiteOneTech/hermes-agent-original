#!/usr/bin/env python3
"""Factory watchdog notifier.

Script-only cron target. It stays silent when there are no unsuppressed alerts;
non-empty stdout is a concise human-facing alert suitable for origin/Telegram
delivery.
"""
from __future__ import annotations

import json
import os
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
        if alert.get("recommended_action"):
            lines.append(f"  - Acción: {alert.get('recommended_action')}")
    lines.append("")
    lines.append("Zeus debe resolver automáticamente los casos rutinarios. Si esta alerta llegó a Jean, es porque el watchdog detectó un bloqueo persistente, una pregunta humana pendiente o una anomalía de runtime.")
    return "\n".join(lines)


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

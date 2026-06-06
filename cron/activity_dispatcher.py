"""Deterministic Activity reminder dispatcher.

This module is intentionally script-friendly: it reads Agent Core Postgres state,
returns notification-ready JSON, and writes auditable Activity events without
relying on chat/session memory. It does not send messages by itself; delivery
adapters can consume the returned outputs.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from hermes_cli import agent_core_sql as sql
from tools import activity_tool


_ACTIVE_STATUSES = "('planned','open','waiting','snoozed')"


def _ok(**fields: Any) -> str:
    return json.dumps({"ok": True, **fields}, ensure_ascii=False, sort_keys=True)


def _err(exc: Exception | str) -> str:
    return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, sort_keys=True)


def _limit(value: Any, default: int = 50, maximum: int = 500) -> int:
    try:
        n = int(value if value is not None else default)
    except Exception:
        n = default
    return max(1, min(maximum, n))


def _owner_clause(owner_id: str | None, *, alias: str = "a") -> str:
    if not owner_id:
        return ""
    return f"AND {alias}.owner_id={sql.quote_literal(owner_id)}"


def _scan_id() -> str:
    return datetime.now(timezone.utc).replace(second=0, microsecond=0).isoformat()


def _event(activity_id: str | None, event_type: str, output: dict[str, Any], scan_id: str) -> dict[str, Any] | None:
    idempotency_key = f"activity-dispatcher:{scan_id}:{event_type}:{activity_id or output.get('rule_id') or output.get('recurrence_rule_id') or output.get('source_id')}"
    return activity_tool._event(
        activity_id,
        event_type,
        new=output,
        side_effect={"dispatcher": "cron.activity_dispatcher", "scan_id": scan_id, "notification_ready": True},
        source="schedule",
        source_ref="activity_dispatcher",
        idempotency_key=idempotency_key,
        result_status="recorded",
    )


def _activity_output(row: dict[str, Any], *, bucket: str) -> dict[str, Any]:
    return {
        "source": "activity",
        "bucket": bucket,
        "activity_id": row.get("activity_id"),
        "title": row.get("title"),
        "activity_type": row.get("activity_type"),
        "owner_id": row.get("owner_id"),
        "due_at": row.get("due_at"),
        "channel": "none",
        "action_status": "notification_ready",
        "audit_event_type": "reminder_due",
    }


def _reminder_output(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "source": "reminder_rule",
        "bucket": "reminder_due",
        "activity_id": row.get("activity_id"),
        "rule_id": row.get("reminder_rule_id"),
        "title": row.get("title"),
        "owner_id": row.get("owner_id"),
        "next_fire_at": row.get("next_fire_at"),
        "channel": row.get("channel") or "none",
        "action_status": "notification_ready",
        "audit_event_type": "reminder_dispatched",
    }


def _recurrence_output(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "source": "recurrence_rule",
        "bucket": "recurrence_due",
        "activity_id": row.get("activity_id"),
        "recurrence_rule_id": row.get("recurrence_rule_id"),
        "title": row.get("title"),
        "owner_id": row.get("owner_id"),
        "dtstart": row.get("dtstart"),
        "rrule": row.get("rrule"),
        "channel": "none",
        "action_status": "notification_ready",
        "audit_event_type": "recurrence_materialized",
    }


def run_dispatcher_scan(owner_id: str | None = None, limit: int = 50, dry_run: bool = False) -> str:
    """Return notification-ready due/reminder outputs and audited event evidence.

    The dispatcher is intentionally deterministic and read-model friendly:
    - due activities: active activities due within the next hour or overdue;
    - reminder rules: enabled rules whose next_fire_at has arrived;
    - recurrence rules: enabled rules in the next 24h window, surfaced for a
      future materializer without creating calendar events or activities here.
    """
    try:
        bounded = _limit(limit)
        scan_id = _scan_id()
        owner = _owner_clause(owner_id)
        due_rows = sql.rows(
            f"""
            SELECT * FROM activity.activities a
            WHERE a.status IN {_ACTIVE_STATUSES}
              {owner}
              AND a.due_at IS NOT NULL
              AND a.due_at <= now() + interval '1 hour'
            ORDER BY a.due_at ASC
            LIMIT {bounded}
            """,
            user=activity_tool._user(),
        )
        reminder_rows = sql.rows(
            f"""
            SELECT r.*, a.title, a.owner_id, a.activity_type, a.due_at
            FROM activity.reminder_rules r
            JOIN activity.activities a ON a.activity_id=r.activity_id
            WHERE r.enabled=true
              {_owner_clause(owner_id, alias='a')}
              AND r.next_fire_at IS NOT NULL
              AND r.next_fire_at <= now()
            ORDER BY r.next_fire_at ASC
            LIMIT {bounded}
            """,
            user=activity_tool._user(),
        )
        recurrence_rows = sql.rows(
            f"""
            SELECT rr.*, a.title, a.owner_id, a.activity_type
            FROM activity.recurrence_rules rr
            JOIN activity.activities a ON a.activity_id=rr.activity_id
            WHERE rr.enabled=true
              {_owner_clause(owner_id, alias='a')}
              AND (rr.dtstart IS NULL OR rr.dtstart <= now() + interval '24 hours')
              AND (rr.until_at IS NULL OR rr.until_at >= now())
            ORDER BY COALESCE(rr.dtstart, now()) ASC
            LIMIT {bounded}
            """,
            user=activity_tool._user(),
        )

        outputs = [_activity_output(row, bucket="due_or_upcoming") for row in due_rows]
        outputs.extend(_reminder_output(row) for row in reminder_rows)
        outputs.extend(_recurrence_output(row) for row in recurrence_rows)

        audit_events = []
        if not dry_run:
            for output in outputs:
                audit_events.append(_event(output.get("activity_id"), output["audit_event_type"], output, scan_id))

        return _ok(
            status="notification_ready" if outputs else "idle",
            scan_id=scan_id,
            owner_id=owner_id,
            count=len(outputs),
            outputs=outputs,
            audit={"dry_run": bool(dry_run), "event_count": len(audit_events), "events": audit_events},
            evidence={"db_backend": "agent_core_postgres", "script": "cron.activity_dispatcher", "limit": bounded},
        )
    except Exception as exc:
        return _err(exc)


if __name__ == "__main__":
    print(run_dispatcher_scan())

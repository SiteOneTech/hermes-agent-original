"""Agent-native Activity / Follow-up tools backed by Agent Core DB.

The Activity Core is the universal layer for follow-ups, reminders, tasks,
next-actions, plans, and timeline evidence. Handlers return JSON strings for
Hermes tool calls and build SQL exclusively through Agent Core SQL quoting
helpers so model-provided text cannot become executable SQL fragments.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from typing import Any

from hermes_cli import agent_core_sql as sql
from tools import calendar_tool
from tools.registry import registry, tool_error


ACTIVITY_TYPES = {"task", "follow_up", "reminder", "call", "meeting", "email", "message", "note", "document", "approval", "custom"}
ACTIVITY_STATUSES = {"planned", "open", "waiting", "snoozed", "done", "cancelled"}
ACTIVITY_PRIORITIES = {"low", "normal", "high", "urgent"}
ACTIVITY_SOURCES = {"manual", "agent", "crm", "calendar", "email", "whatsapp", "telegram", "webhook", "schedule", "import", "test"}
LINK_TARGET_TYPES = {"contact", "organization", "opportunity", "project", "document", "quote", "invoice", "interaction", "calendar_event", "external_ref", "activity", "plan", "custom"}
LINK_RELATIONSHIPS = {"primary", "context", "participant", "derived_from", "next_after", "blocks", "blocked_by", "calendar_event", "duplicate_of", "merged_into", "legacy_follow_up", "source_ref"}
PLAN_STATUSES = {"draft", "active", "paused", "archived"}
RUN_STATUSES = {"active", "paused", "completed", "cancelled"}
STEP_STATUSES = {"pending", "suggested", "created", "skipped", "done", "cancelled"}


def _ok(**fields: Any) -> str:
    return json.dumps({"ok": True, **fields}, ensure_ascii=False, sort_keys=True)


def _err(exc: Exception | str) -> str:
    return tool_error(str(exc))


def _check_activity() -> bool:
    try:
        if not sql.enabled():
            return False
        sql.psql("SELECT 1;", user=_user())
        return True
    except Exception:
        return False


def _user() -> str:
    return sql.runtime_env().get("ACTIVITY_DB_RUNTIME_USER", "activity_runtime")


def _q(value: Any) -> str:
    return sql.quote_literal(value)


def _j(value: Any) -> str:
    return sql.quote_jsonb(value)


def _slug(prefix: str, value: str) -> str:
    return f"{prefix}_{sql.slugify(value)}"


def _stable_id(prefix: str, *parts: Any) -> str:
    material = "|".join(str(p or "") for p in parts)
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def _limit(value: Any, default: int = 20, maximum: int = 100) -> int:
    try:
        n = int(value or default)
    except Exception:
        n = default
    return max(1, min(maximum, n))


def _non_negative_int(value: Any, default: int = 0, maximum: int = 31_536_000) -> int:
    try:
        n = int(value if value is not None else default)
    except Exception:
        n = default
    return max(0, min(maximum, n))


def _offset(value: Any) -> int:
    try:
        n = int(value or 0)
    except Exception:
        n = 0
    return max(0, n)


def _required(args: dict[str, Any], field: str) -> str:
    value = str(args.get(field) or "").strip()
    if not value:
        raise ValueError(f"{field} is required")
    return value


def _enum(value: Any, allowed: set[str], field: str, default: str | None = None) -> str:
    text = str(value or default or "").strip()
    if not text:
        raise ValueError(f"{field} is required")
    if text not in allowed:
        raise ValueError(f"{field} must be one of: {', '.join(sorted(allowed))}")
    return text


def _maybe_json_obj(value: Any, field: str) -> dict[str, Any]:
    if value is None or value == "":
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    return value


def _maybe_json_array(value: Any, field: str) -> list[Any]:
    if value is None or value == "":
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field} must be an array")
    return value


def _event(activity_id: str | None, event_type: str, *, previous: dict[str, Any] | None = None, new: dict[str, Any] | None = None, side_effect: dict[str, Any] | None = None, source: str | None = None, source_ref: str | None = None, idempotency_key: str | None = None, result_status: str = "recorded", error: str | None = None) -> dict[str, Any] | None:
    return sql.statement_one(f"""
      INSERT INTO activity.activity_events (activity_id, event_type, source, source_ref, idempotency_key, previous_state, new_state, side_effect, result_status, error)
      VALUES ({_q(activity_id)}, {_q(event_type)}, {_q(source)}, {_q(source_ref)}, {_q(idempotency_key)}, {_j(previous or {})}, {_j(new or {})}, {_j(side_effect or {})}, {_q(result_status)}, {_q(error)})
      ON CONFLICT (idempotency_key) WHERE idempotency_key IS NOT NULL DO UPDATE SET new_state=EXCLUDED.new_state, side_effect=EXCLUDED.side_effect, result_status=EXCLUDED.result_status, error=EXCLUDED.error
      RETURNING *
    """, user=_user())


def _handle_activity_status() -> str:
    try:
        counts = sql.one("""
          SELECT
            (SELECT count(*) FROM activity.activities) AS activities,
            (SELECT count(*) FROM activity.activities WHERE status IN ('planned','open','waiting','snoozed')) AS active,
            (SELECT count(*) FROM activity.activities WHERE status='done') AS done,
            (SELECT count(*) FROM activity.activities WHERE status='cancelled') AS cancelled,
            (SELECT count(*) FROM activity.activity_links) AS links,
            (SELECT count(*) FROM activity.reminder_rules WHERE enabled=true) AS enabled_reminder_rules,
            (SELECT count(*) FROM activity.activity_plans WHERE status='active') AS active_plans,
            (SELECT count(*) FROM activity.activity_events) AS events
        """, user=_user())
        return _ok(db_backend="agent_core_postgres", counts=counts)
    except Exception as exc:
        return _err(exc)


def _handle_activity_upsert(args: dict, **_kwargs) -> str:
    try:
        title = _required(args, "title")
        activity_type = _enum(args.get("activity_type"), ACTIVITY_TYPES, "activity_type", "follow_up")
        status = _enum(args.get("status"), ACTIVITY_STATUSES, "status", "open")
        priority = _enum(args.get("priority"), ACTIVITY_PRIORITIES, "priority", "normal")
        source = _enum(args.get("source"), ACTIVITY_SOURCES, "source", "agent")
        evidence = _maybe_json_obj(args.get("evidence"), "evidence")
        participants = _maybe_json_array(args.get("participants"), "participants")
        metadata = _maybe_json_obj(args.get("metadata"), "metadata")
        activity_id = args.get("activity_id") or _stable_id("act", activity_type, title, args.get("due_at"), args.get("owner_id") or "zeus", args.get("source_ref"))
        dedupe_key = args.get("dedupe_key") or metadata.get("dedupe_key")
        source_ref = args.get("source_ref")
        if not dedupe_key and source_ref:
            dedupe_key = _stable_id("dedupe", source, source_ref, activity_type)
        conflict_target = "(activity_id)" if not dedupe_key else "(dedupe_key) WHERE dedupe_key IS NOT NULL"
        row = sql.statement_one(f"""
          INSERT INTO activity.activities (
            activity_id, activity_type, title, description, status, priority, owner_id, assignee_id,
            due_at, start_at, end_at, source, source_ref, source_hash, dedupe_key, confidence,
            evidence, participants, metadata, created_at, updated_at
          ) VALUES (
            {_q(activity_id)}, {_q(activity_type)}, {_q(title)}, {_q(args.get('description'))}, {_q(status)}, {_q(priority)}, {_q(args.get('owner_id') or 'zeus')}, {_q(args.get('assignee_id'))},
            {_q(args.get('due_at'))}::timestamptz, {_q(args.get('start_at'))}::timestamptz, {_q(args.get('end_at'))}::timestamptz, {_q(source)}, {_q(source_ref)}, {_q(args.get('source_hash'))}, {_q(dedupe_key)}, {_q(args.get('confidence'))}::numeric,
            {_j(evidence)}, {_j(participants)}, {_j(metadata)}, now(), now()
          )
          ON CONFLICT {conflict_target} DO UPDATE SET
            activity_type=EXCLUDED.activity_type, title=EXCLUDED.title, description=EXCLUDED.description,
            status=EXCLUDED.status, priority=EXCLUDED.priority, owner_id=EXCLUDED.owner_id,
            assignee_id=EXCLUDED.assignee_id, due_at=EXCLUDED.due_at, start_at=EXCLUDED.start_at,
            end_at=EXCLUDED.end_at, source=EXCLUDED.source, source_ref=EXCLUDED.source_ref,
            source_hash=EXCLUDED.source_hash, dedupe_key=EXCLUDED.dedupe_key,
            confidence=EXCLUDED.confidence, evidence=EXCLUDED.evidence,
            participants=EXCLUDED.participants, metadata=EXCLUDED.metadata, updated_at=now()
          RETURNING *
        """, user=_user())
        operation = "upserted"
        if row:
            _event(row.get("activity_id"), "updated" if row.get("created_at") != row.get("updated_at") else "created", new=row, source=source, source_ref=source_ref)
        return _ok(activity=row, activity_id=(row or {}).get("activity_id", activity_id), operation=operation, dedupe_key=dedupe_key, evidence={"source": source, "source_ref": source_ref})
    except Exception as exc:
        return _err(exc)


def _due_clause(filter_name: str | None, alias: str = "a") -> str:
    p = f"{alias}."
    name = str(filter_name or "").strip().lower()
    active = f"{p}status IN ('planned','open','waiting','snoozed')"
    if name in {"due", "today"}:
        return f"{active} AND {p}due_at IS NOT NULL AND {p}due_at >= date_trunc('day', now()) AND {p}due_at < date_trunc('day', now()) + interval '1 day'"
    if name == "upcoming":
        return f"{active} AND {p}due_at IS NOT NULL AND {p}due_at >= now() AND {p}due_at <= now() + interval '7 days'"
    if name == "overdue":
        return f"{active} AND {p}due_at IS NOT NULL AND {p}due_at < now()"
    if name == "waiting":
        return f"{p}status = 'waiting'"
    if name == "snoozed":
        return f"{p}status = 'snoozed'"
    if name == "resurfaced":
        return f"{p}status = 'snoozed' AND {p}snoozed_until IS NOT NULL AND {p}snoozed_until <= now()"
    return "TRUE"


def _handle_activity_list(args: dict, **_kwargs) -> str:
    try:
        limit = _limit(args.get("limit"), maximum=200)
        offset = _offset(args.get("offset"))
        where = [_due_clause(args.get("due_filter"))]
        for field in ("owner_id", "status", "activity_type", "priority", "source", "assignee_id", "dedupe_key"):
            if args.get(field):
                where.append(f"a.{field}={_q(args.get(field))}")
        if args.get("query"):
            pattern = f"%{args.get('query')}%"
            where.append(f"(a.title ILIKE {_q(pattern)} OR a.description ILIKE {_q(pattern)})")
        if args.get("target_type") and args.get("target_id"):
            where.append(f"EXISTS (SELECT 1 FROM activity.activity_links l WHERE l.activity_id=a.activity_id AND l.target_type={_q(args.get('target_type'))} AND l.target_id={_q(args.get('target_id'))})")
        condition = " AND ".join(where)
        rows = sql.rows(f"""
          SELECT a.* FROM activity.activities a
          WHERE {condition}
          ORDER BY COALESCE(a.due_at, a.updated_at) ASC, a.updated_at DESC
          LIMIT {limit} OFFSET {offset}
        """, user=_user())
        return _ok(activities=rows, count=len(rows), due_filter=args.get("due_filter"), limit=limit, offset=offset)
    except Exception as exc:
        return _err(exc)


def _status_update(args: dict, status: str, event_type: str, *, set_sql: str = "", note_field: str | None = None) -> str:
    aid = _required(args, "activity_id")
    note = args.get(note_field) if note_field else None
    metadata_patch = {note_field: note} if note_field and note else {}
    row = sql.statement_one(f"""
      UPDATE activity.activities
      SET status={_q(status)}, updated_at=now(){set_sql},
          metadata = metadata || {_j(metadata_patch)}
      WHERE activity_id={_q(aid)}
      RETURNING *
    """, user=_user())
    if not row:
        raise ValueError("activity not found")
    ev = _event(row.get("activity_id"), event_type, new=row, side_effect=metadata_patch)
    return _ok(activity=row, activity_id=row.get("activity_id"), status=row.get("status"), event=ev)


def _handle_activity_complete(args: dict, **_kwargs) -> str:
    try:
        return _status_update(args, "done", "completed", set_sql=", completed_at=now(), cancelled_at=NULL, snoozed_until=NULL", note_field="completion_note")
    except Exception as exc:
        return _err(exc)


def _handle_activity_snooze(args: dict, **_kwargs) -> str:
    try:
        snoozed_until = _required(args, "snoozed_until")
        return _status_update(args, "snoozed", "snoozed", set_sql=f", snoozed_until={_q(snoozed_until)}::timestamptz", note_field="snooze_reason")
    except Exception as exc:
        return _err(exc)


def _handle_activity_reschedule(args: dict, **_kwargs) -> str:
    try:
        aid = _required(args, "activity_id")
        due_at = _required(args, "due_at")
        row = sql.statement_one(f"""
          UPDATE activity.activities
          SET due_at={_q(due_at)}::timestamptz, status=CASE WHEN status='cancelled' THEN status ELSE 'open' END,
              snoozed_until=NULL, updated_at=now(), metadata=metadata || {_j({'reschedule_reason': args.get('reschedule_reason')} if args.get('reschedule_reason') else {})}
          WHERE activity_id={_q(aid)}
          RETURNING *
        """, user=_user())
        if not row:
            raise ValueError("activity not found")
        ev = _event(row.get("activity_id"), "rescheduled", new=row, side_effect={"due_at": due_at})
        return _ok(activity=row, activity_id=row.get("activity_id"), due_at=row.get("due_at"), event=ev)
    except Exception as exc:
        return _err(exc)


def _handle_activity_cancel(args: dict, **_kwargs) -> str:
    try:
        return _status_update(args, "cancelled", "cancelled", set_sql=", cancelled_at=now(), snoozed_until=NULL", note_field="cancel_reason")
    except Exception as exc:
        return _err(exc)


def _handle_activity_link(args: dict, **_kwargs) -> str:
    try:
        aid = _required(args, "activity_id")
        target_type = _enum(args.get("target_type"), LINK_TARGET_TYPES, "target_type")
        target_id = _required(args, "target_id")
        relationship_type = _enum(args.get("relationship_type"), LINK_RELATIONSHIPS, "relationship_type", "context")
        metadata = _maybe_json_obj(args.get("metadata"), "metadata")
        row = sql.statement_one(f"""
          INSERT INTO activity.activity_links (activity_id, target_type, target_id, relationship_type, target_schema, target_table, provider, external_type, external_id, external_url, metadata)
          VALUES ({_q(aid)}, {_q(target_type)}, {_q(target_id)}, {_q(relationship_type)}, {_q(args.get('target_schema'))}, {_q(args.get('target_table'))}, {_q(args.get('provider'))}, {_q(args.get('external_type'))}, {_q(args.get('external_id'))}, {_q(args.get('external_url'))}, {_j(metadata)})
          ON CONFLICT (activity_id, target_type, target_id, relationship_type)
          DO UPDATE SET target_schema=EXCLUDED.target_schema, target_table=EXCLUDED.target_table, provider=EXCLUDED.provider, external_type=EXCLUDED.external_type, external_id=EXCLUDED.external_id, external_url=EXCLUDED.external_url, metadata=EXCLUDED.metadata
          RETURNING *
        """, user=_user())
        ev = _event(aid, "linked", new=row, side_effect={"target_type": target_type, "target_id": target_id, "relationship_type": relationship_type})
        return _ok(link=row, activity_link_id=(row or {}).get("activity_link_id"), activity_id=aid, event=ev)
    except Exception as exc:
        return _err(exc)


def _handle_activity_unlink(args: dict, **_kwargs) -> str:
    try:
        aid = _required(args, "activity_id")
        target_type = _enum(args.get("target_type"), LINK_TARGET_TYPES, "target_type")
        target_id = _required(args, "target_id")
        relationship_type = _enum(args.get("relationship_type"), LINK_RELATIONSHIPS, "relationship_type", "context")
        row = sql.statement_one(f"""
          DELETE FROM activity.activity_links
          WHERE activity_id={_q(aid)} AND target_type={_q(target_type)} AND target_id={_q(target_id)} AND relationship_type={_q(relationship_type)}
          RETURNING *
        """, user=_user())
        ev = _event(aid, "unlinked", previous=row or {}, side_effect={"target_type": target_type, "target_id": target_id, "relationship_type": relationship_type})
        return _ok(unlinked=bool(row), link=row, activity_id=aid, event=ev)
    except Exception as exc:
        return _err(exc)


def _handle_activity_timeline(args: dict, **_kwargs) -> str:
    try:
        limit = _limit(args.get("limit"), default=50, maximum=200)
        target_type = args.get("target_type")
        target_id = args.get("target_id")
        aid = args.get("activity_id")
        if not aid and not (target_type and target_id):
            raise ValueError("activity_id or target_type + target_id is required")
        if aid:
            activity_condition = f"a.activity_id={_q(aid)}"
            link_condition = f"l.activity_id={_q(aid)}"
            event_condition = f"e.activity_id={_q(aid)}"
        else:
            activity_condition = f"EXISTS (SELECT 1 FROM activity.activity_links l WHERE l.activity_id=a.activity_id AND l.target_type={_q(target_type)} AND l.target_id={_q(target_id)})"
            link_condition = f"l.target_type={_q(target_type)} AND l.target_id={_q(target_id)}"
            event_condition = f"EXISTS (SELECT 1 FROM activity.activity_links l WHERE l.activity_id=e.activity_id AND l.target_type={_q(target_type)} AND l.target_id={_q(target_id)})"
        activities = sql.rows(f"SELECT a.* FROM activity.activities a WHERE {activity_condition} ORDER BY COALESCE(a.due_at, a.updated_at) DESC LIMIT {limit}", user=_user())
        links = sql.rows(f"SELECT l.* FROM activity.activity_links l WHERE {link_condition} ORDER BY l.created_at DESC LIMIT {limit}", user=_user())
        events = sql.rows(f"SELECT e.* FROM activity.activity_events e WHERE {event_condition} ORDER BY e.created_at DESC LIMIT {limit}", user=_user())
        return _ok(activities=activities, links=links, events=events, target={"activity_id": aid, "target_type": target_type, "target_id": target_id})
    except Exception as exc:
        return _err(exc)


def _to_utc_datetime(value: Any, field: str) -> datetime:
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value or "").strip()
        if not text:
            raise ValueError(f"{field} is required")
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _timestamp_ms(value: Any, field: str) -> int:
    return int(_to_utc_datetime(value, field).timestamp() * 1000)


def _duration_minutes(start_at: Any, end_at: Any, explicit: Any = None) -> int:
    if explicit is not None and explicit != "":
        minutes = int(explicit)
    else:
        delta = _to_utc_datetime(end_at, "end_at") - _to_utc_datetime(start_at, "start_at")
        minutes = int(delta.total_seconds() // 60)
    if minutes <= 0:
        raise ValueError("duration_minutes must be positive")
    return minutes


def _json_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _calendar_required(activity: dict[str, Any], args: dict[str, Any]) -> bool:
    metadata = _json_dict(activity.get("metadata"))
    return bool(
        args.get("calendar_required")
        or metadata.get("calendar_required")
        or metadata.get("time_block_required")
        or activity.get("activity_type") in {"meeting", "call"}
    )


def _extract_calendar_event_id(result: dict[str, Any]) -> str | None:
    candidates: list[Any] = [result.get("event_id"), result.get("eventId"), result.get("id")]
    data = result.get("data")
    if isinstance(data, dict):
        candidates.extend([data.get("event_id"), data.get("eventId"), data.get("id")])
        event = data.get("event")
        if isinstance(event, dict):
            candidates.extend([event.get("event_id"), event.get("eventId"), event.get("id")])
    elif isinstance(data, list) and data and isinstance(data[0], dict):
        candidates.extend([data[0].get("event_id"), data[0].get("eventId"), data[0].get("id")])
    for candidate in candidates:
        if candidate:
            return str(candidate)
    return None


def _handle_activity_to_calendar_event(args: dict, **_kwargs) -> str:
    try:
        aid = _required(args, "activity_id")
        activity = sql.statement_one(f"SELECT * FROM activity.activities WHERE activity_id={_q(aid)}", user=_user())
        if not activity:
            raise ValueError("activity not found")
        if not _calendar_required(activity, args):
            ev = _event(aid, "calendar_requested", new={"calendar_required": False}, result_status="skipped", side_effect={"reason": "activity does not require calendar blocking"})
            return _ok(activity_id=aid, calendar_event_id=None, status="skipped", event=ev, evidence={"calendar_required": False})

        actor_id = _required(args, "actor_id")
        calendar_id = _required(args, "calendar_id")
        start_at = args.get("start_at") or activity.get("start_at") or activity.get("due_at")
        end_at = args.get("end_at") or activity.get("end_at")
        duration = _duration_minutes(start_at, end_at, args.get("duration_minutes"))
        start_ts = int(args.get("start_ts") or _timestamp_ms(start_at, "start_at"))
        activity_metadata = _json_dict(activity.get("metadata"))
        bridge_metadata = {
            **_json_dict(args.get("metadata")),
            "activity_id": aid,
            "activity_type": activity.get("activity_type"),
            "source": "activity_core",
            "title": args.get("title") or activity.get("title"),
        }
        if activity.get("participants"):
            bridge_metadata["participants"] = activity.get("participants")

        _event(aid, "calendar_requested", new={"actor_id": actor_id, "calendar_id": calendar_id, "start_ts": start_ts, "duration_minutes": duration}, result_status="pending")
        if args.get("block_time") or activity_metadata.get("block_time") or activity_metadata.get("time_block_required"):
            result = calendar_tool.calendar_block_time(
                actor_id=actor_id,
                calendar_id=calendar_id,
                start_ts=start_ts,
                duration_minutes=duration,
                reason=args.get("reason") or activity.get("title"),
                metadata=bridge_metadata,
            )
        else:
            result = calendar_tool.calendar_create_event(
                actor_id=actor_id,
                calendar_id=calendar_id,
                start_ts=start_ts,
                duration_minutes=duration,
                busy=bool(args.get("busy", True)),
                metadata=bridge_metadata,
                service_id=args.get("service_id"),
                reminders=args.get("reminders"),
                recurrence=args.get("recurrence"),
            )

        calendar_event_id = _extract_calendar_event_id(result)
        if result.get("success") and calendar_event_id:
            link_payload = {
                "activity_id": aid,
                "target_type": "calendar_event",
                "target_id": calendar_event_id,
                "relationship_type": "calendar_event",
                "provider": args.get("provider") or "calendar_tool",
                "external_type": "calendar_event",
                "external_id": calendar_event_id,
                "external_url": args.get("external_url"),
                "metadata": {"calendar_id": calendar_id, "actor_id": actor_id, "status": result.get("status")},
            }
            link = json.loads(_handle_activity_link(link_payload))
            ev = _event(aid, "calendar_linked", new={"calendar_event_id": calendar_event_id, "calendar_id": calendar_id}, side_effect={"calendar_result": result, "link": link}, result_status="succeeded", source="calendar", source_ref=calendar_event_id)
            return _ok(activity_id=aid, calendar_event_id=calendar_event_id, status="created", calendar_result=result, link=link, event=ev)

        error = result.get("error") or result
        ev = _event(aid, "calendar_failed", new={"calendar_event_id": calendar_event_id}, side_effect={"calendar_result": result}, result_status="failed", error=json.dumps(error, ensure_ascii=False, sort_keys=True))
        return _ok(activity_id=aid, calendar_event_id=None, status="retryable", calendar_result=result, event=ev, error=error)
    except Exception as exc:
        return _err(exc)


def activity_to_calendar_event(**kwargs: Any) -> str:
    """Public deterministic wrapper for bridge smoke tests and scripts."""
    return _handle_activity_to_calendar_event(kwargs)


def _handle_activity_dispatcher_scan(args: dict, **_kwargs) -> str:
    """Expose the deterministic dispatcher through the activity toolset.

    Keep the Hermes tool handler aligned with ``cron.activity_dispatcher`` so
    chat-triggered scans, cron jobs, and future scheduler wrappers share one
    audited implementation. Import lazily to avoid the module cycle:
    cron.activity_dispatcher -> tools.activity_tool.
    """
    try:
        from cron import activity_dispatcher

        return activity_dispatcher.run_dispatcher_scan(
            owner_id=args.get("owner_id"),
            limit=_limit(args.get("limit"), default=50, maximum=500),
            dry_run=bool(args.get("dry_run", False)),
        )
    except Exception as exc:
        return _err(exc)


def _handle_activity_plan_create(args: dict, **_kwargs) -> str:
    try:
        name = _required(args, "name")
        steps = args.get("steps") or []
        if not isinstance(steps, list):
            raise ValueError("steps must be an array")
        plan_id = args.get("plan_id") or _stable_id("aplan", name, args.get("owner_id") or "zeus")
        status = _enum(args.get("status"), PLAN_STATUSES, "status", "active")
        metadata = _maybe_json_obj(args.get("metadata"), "metadata")
        validated_steps = []
        for index, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                raise ValueError("each step must be an object")
            title_template = str(step.get("title_template") or step.get("title") or "").strip()
            if not title_template:
                raise ValueError("step title_template is required")
            activity_type = _enum(step.get("activity_type"), ACTIVITY_TYPES, "activity_type", "follow_up")
            default_priority = _enum(step.get("default_priority") or step.get("priority"), ACTIVITY_PRIORITIES, "default_priority", "normal")
            step_id = step.get("plan_step_id") or _stable_id("apstep", plan_id, index, title_template)
            validated_steps.append((index, step, step_id, title_template, activity_type, default_priority))
        plan = sql.statement_one(f"""
          INSERT INTO activity.activity_plans (plan_id, name, description, status, scope, owner_id, metadata, created_at, updated_at)
          VALUES ({_q(plan_id)}, {_q(name)}, {_q(args.get('description'))}, {_q(status)}, {_q(args.get('scope'))}, {_q(args.get('owner_id') or 'zeus')}, {_j(metadata)}, now(), now())
          ON CONFLICT (plan_id) DO UPDATE SET name=EXCLUDED.name, description=EXCLUDED.description, status=EXCLUDED.status, scope=EXCLUDED.scope, owner_id=EXCLUDED.owner_id, metadata=EXCLUDED.metadata, updated_at=now()
          RETURNING *
        """, user=_user())
        sql.psql(f"DELETE FROM activity.activity_plan_steps WHERE plan_id={_q(plan_id)};", user=_user())
        saved_steps = []
        for index, step, step_id, title_template, activity_type, default_priority in validated_steps:
            saved_steps.append(sql.statement_one(f"""
              INSERT INTO activity.activity_plan_steps (plan_step_id, plan_id, step_order, activity_type, title_template, description_template, default_priority, relative_to, offset_seconds, auto_create, requires_confirmation, metadata)
              VALUES ({_q(step_id)}, {_q(plan_id)}, {index}, {_q(activity_type)}, {_q(title_template)}, {_q(step.get('description_template') or step.get('description'))}, {_q(default_priority)}, {_q(step.get('relative_to') or 'plan_start')}, {_non_negative_int(step.get('offset_seconds'), default=0, maximum=31_536_000)}, {_q(bool(step.get('auto_create')))}, {_q(bool(step.get('requires_confirmation')))}, {_j(step.get('metadata') or {})})
              RETURNING *
            """, user=_user()))
        _event(None, "plan_applied", new={"plan_id": plan_id, "step_count": len(saved_steps)}, source=args.get("source"), source_ref=args.get("source_ref"))
        return _ok(plan=plan, plan_id=plan_id, steps=saved_steps, step_count=len(saved_steps))
    except Exception as exc:
        return _err(exc)


def _render_template(template: str, context: dict[str, Any]) -> str:
    rendered = template
    for key, value in context.items():
        rendered = rendered.replace("{{" + key + "}}", str(value or ""))
    return rendered


def _handle_activity_plan_apply(args: dict, **_kwargs) -> str:
    try:
        plan_id = _required(args, "plan_id")
        target_type = _required(args, "target_type")
        target_id = _required(args, "target_id")
        target_name = args.get("target_name") or target_id
        run_id = args.get("plan_run_id") or _stable_id("aprun", plan_id, target_type, target_id, datetime.now(timezone.utc).isoformat())
        status = _enum(args.get("status"), RUN_STATUSES, "status", "active")
        metadata = _maybe_json_obj(args.get("metadata"), "metadata")
        run = sql.statement_one(f"""
          INSERT INTO activity.activity_plan_runs (plan_run_id, plan_id, status, owner_id, target_type, target_id, metadata)
          VALUES ({_q(run_id)}, {_q(plan_id)}, {_q(status)}, {_q(args.get('owner_id') or 'zeus')}, {_q(target_type)}, {_q(target_id)}, {_j(metadata)})
          RETURNING *
        """, user=_user())
        steps = sql.rows(f"SELECT * FROM activity.activity_plan_steps WHERE plan_id={_q(plan_id)} ORDER BY step_order ASC", user=_user())
        saved = []
        created = []
        base_due = args.get("start_at") or datetime.now(timezone.utc).isoformat()
        for step in steps:
            step_status = "suggested"
            activity_id = None
            offset_seconds = int(step.get("offset_seconds") or 0)
            due_at = (_to_utc_datetime(base_due, "start_at") + timedelta(seconds=offset_seconds)).isoformat()
            due_at_expr = f"({_q(base_due)}::timestamptz + ({offset_seconds} * interval '1 second'))"
            step_metadata = _json_dict(step.get("metadata"))
            activity_metadata = {
                **step_metadata,
                "plan_id": plan_id,
                "plan_run_id": run_id,
                "plan_step_id": step.get("plan_step_id"),
                "target_type": target_type,
                "target_id": target_id,
            }
            if step.get("auto_create") or args.get("create_activities"):
                title = _render_template(step.get("title_template") or "Follow up {{target_name}}", {"target_name": target_name, "target_id": target_id, "target_type": target_type})
                description = _render_template(step.get("description_template") or "", {"target_name": target_name, "target_id": target_id, "target_type": target_type}) or None
                act_payload = json.loads(_handle_activity_upsert({"activity_type": step.get("activity_type"), "title": title, "description": description, "priority": step.get("default_priority"), "owner_id": args.get("owner_id") or "zeus", "assignee_id": step_metadata.get("default_assignee_id"), "due_at": due_at, "source": "agent", "metadata": activity_metadata}))
                if act_payload.get("ok"):
                    activity_id = act_payload.get("activity_id")
                    created.append(act_payload.get("activity"))
                    step_status = "created"
            run_step_id = _stable_id("aprunstep", run_id, step.get("plan_step_id"))
            saved.append(sql.statement_one(f"""
              INSERT INTO activity.activity_plan_run_steps (plan_run_step_id, plan_run_id, plan_step_id, activity_id, status, due_at, metadata)
              VALUES ({_q(run_step_id)}, {_q(run_id)}, {_q(step.get('plan_step_id'))}, {_q(activity_id)}, {_q(step_status)}, {due_at_expr}, {_j({})})
              ON CONFLICT (plan_run_id, plan_step_id) DO UPDATE SET activity_id=EXCLUDED.activity_id, status=EXCLUDED.status, due_at=EXCLUDED.due_at, metadata=EXCLUDED.metadata
              RETURNING *
            """, user=_user()))
        _event(None, "plan_applied", new={"plan_id": plan_id, "plan_run_id": run_id, "target_type": target_type, "target_id": target_id, "created": len(created)})
        return _ok(plan_run=run, plan_run_id=run_id, run_steps=saved, created_activities=created, next_actions=[s for s in saved if s and s.get("status") in {"pending", "suggested", "created"}])
    except Exception as exc:
        return _err(exc)


def _handle_activity_next_actions(args: dict, **_kwargs) -> str:
    try:
        limit = _limit(args.get("limit"), default=20, maximum=100)
        owner = args.get("owner_id") or "zeus"
        linked = sql.rows(f"""
          SELECT nxt.* FROM activity.activity_links l
          JOIN activity.activities cur ON cur.activity_id=l.activity_id
          JOIN activity.activities nxt ON nxt.activity_id=l.target_id
          WHERE l.target_type='activity' AND l.relationship_type='next_after'
            AND cur.status='done' AND nxt.status IN ('planned','open','waiting','snoozed')
            AND nxt.owner_id={_q(owner)}
          ORDER BY COALESCE(nxt.due_at, nxt.updated_at) ASC
          LIMIT {limit}
        """, user=_user())
        run_steps = sql.rows(f"""
          SELECT rs.*, s.title_template, s.activity_type, r.target_type, r.target_id
          FROM activity.activity_plan_run_steps rs
          JOIN activity.activity_plan_steps s ON s.plan_step_id=rs.plan_step_id
          JOIN activity.activity_plan_runs r ON r.plan_run_id=rs.plan_run_id
          WHERE r.owner_id={_q(owner)} AND r.status='active' AND rs.status IN ('pending','suggested')
          ORDER BY rs.due_at ASC NULLS LAST
          LIMIT {limit}
        """, user=_user())
        return _ok(next_actions={"linked_activities": linked, "plan_steps": run_steps}, count=len(linked) + len(run_steps), owner_id=owner)
    except Exception as exc:
        return _err(exc)


def _parse_relative_datetime(text: str) -> str | None:
    lower = text.lower()
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    if "tomorrow" in lower or "mañana" in lower:
        base = now + timedelta(days=1)
    elif "today" in lower or "hoy" in lower:
        base = now
    else:
        return None
    match = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", lower)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2) or 0)
        ampm = match.group(3)
        if ampm == "pm" and hour < 12:
            hour += 12
        if ampm == "am" and hour == 12:
            hour = 0
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            base = base.replace(hour=hour, minute=minute)
    return base.isoformat()


def _detect_one(text: str) -> dict[str, Any]:
    lower = text.lower()
    if re.search(r"\b(call|llamar|llama)\b", lower):
        activity_type = "call"
    elif re.search(r"\b(remind|recordar|recu[eé]rdame)\b", lower):
        activity_type = "reminder"
    elif re.search(r"\b(email|correo|write|escribir)\b", lower):
        activity_type = "email"
    else:
        activity_type = "follow_up"
    title = re.sub(r"\s+", " ", text.strip())[:140] or "Detected follow-up"
    return {
        "activity_type": activity_type,
        "title": title,
        "due_at": _parse_relative_datetime(text),
        "confidence": 0.72,
        "evidence": {"detector": "regex-v1", "text_excerpt": text[:240]},
    }


def _handle_activity_detect(args: dict, **_kwargs) -> str:
    try:
        text = _required(args, "text")
        suggestions = [_detect_one(text)]
        if not args.get("persist"):
            return _ok(detected_activities=suggestions, persisted=[])
        persisted = []
        for suggestion in suggestions:
            payload = {**suggestion, "source": args.get("source") or "agent", "source_ref": args.get("source_ref"), "owner_id": args.get("owner_id") or "zeus", "metadata": {"detected_from_text": True}}
            result = json.loads(_handle_activity_upsert(payload))
            persisted.append(result)
            if result.get("ok"):
                _event(result.get("activity_id"), "detection_persisted", new=suggestion, source=payload["source"], source_ref=payload.get("source_ref"))
        return _ok(detected_activities=suggestions, persisted=persisted)
    except Exception as exc:
        return _err(exc)


# ---------------------------------------------------------------------------
# Tool schemas / registration
# ---------------------------------------------------------------------------

def _schema(name: str, description: str, props: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    return {"type": "function", "function": {"name": name, "description": description, "parameters": {"type": "object", "properties": props, "required": required or []}}}


def _meta_props() -> dict[str, Any]:
    return {
        "metadata": {"type": "object", "description": "Optional JSON metadata for tenant-neutral evidence, labels, business_id, source_channel, and workflow hints."},
        "evidence": {"type": "object", "description": "Optional JSON evidence for why this activity exists."},
    }


_ACTIVITY_PROPS = {
    "activity_id": {"type": "string"}, "activity_type": {"type": "string", "enum": sorted(ACTIVITY_TYPES)}, "title": {"type": "string"},
    "description": {"type": "string"}, "status": {"type": "string", "enum": sorted(ACTIVITY_STATUSES)}, "priority": {"type": "string", "enum": sorted(ACTIVITY_PRIORITIES)},
    "owner_id": {"type": "string"}, "assignee_id": {"type": "string"}, "due_at": {"type": "string"}, "start_at": {"type": "string"}, "end_at": {"type": "string"},
    "source": {"type": "string", "enum": sorted(ACTIVITY_SOURCES)}, "source_ref": {"type": "string"}, "source_hash": {"type": "string"}, "dedupe_key": {"type": "string"},
    "confidence": {"type": "number"}, "participants": {"type": "array"}, **_meta_props(),
}

_LINK_PROPS = {
    "activity_id": {"type": "string"}, "target_type": {"type": "string", "enum": sorted(LINK_TARGET_TYPES)}, "target_id": {"type": "string"},
    "relationship_type": {"type": "string", "enum": sorted(LINK_RELATIONSHIPS)}, "target_schema": {"type": "string"}, "target_table": {"type": "string"},
    "provider": {"type": "string"}, "external_type": {"type": "string"}, "external_id": {"type": "string"}, "external_url": {"type": "string"},
    "metadata": {"type": "object"},
}

registry.register(name="activity_status", toolset="activity", schema=_schema("activity_status", "Return Activity Core row counts and Agent Core DB backend evidence.", {}), handler=lambda args, **_kw: _handle_activity_status(), check_fn=_check_activity, emoji="⏰")
registry.register(name="activity_upsert", toolset="activity", schema=_schema("activity_upsert", "Create or update a universal activity/follow-up/reminder/task. Returns actionable activity_id and evidence.", _ACTIVITY_PROPS, ["title"]), handler=_handle_activity_upsert, check_fn=_check_activity, emoji="⏰")
registry.register(name="activity_list", toolset="activity", schema=_schema("activity_list", "List activities by due/upcoming/overdue/today/waiting/snoozed/resurfaced, target link, owner, status, priority, source, or query.", {"owner_id": {"type": "string"}, "status": {"type": "string"}, "activity_type": {"type": "string"}, "priority": {"type": "string"}, "source": {"type": "string"}, "assignee_id": {"type": "string"}, "due_filter": {"type": "string", "enum": ["due", "today", "upcoming", "overdue", "waiting", "snoozed", "resurfaced"]}, "target_type": {"type": "string"}, "target_id": {"type": "string"}, "query": {"type": "string"}, "limit": {"type": "integer"}, "offset": {"type": "integer"}}), handler=_handle_activity_list, check_fn=_check_activity, emoji="⏰")
registry.register(name="activity_complete", toolset="activity", schema=_schema("activity_complete", "Mark an activity complete and write completion evidence.", {"activity_id": {"type": "string"}, "completion_note": {"type": "string"}}, ["activity_id"]), handler=_handle_activity_complete, check_fn=_check_activity, emoji="⏰")
registry.register(name="activity_snooze", toolset="activity", schema=_schema("activity_snooze", "Snooze an activity until a timestamp.", {"activity_id": {"type": "string"}, "snoozed_until": {"type": "string"}, "snooze_reason": {"type": "string"}}, ["activity_id", "snoozed_until"]), handler=_handle_activity_snooze, check_fn=_check_activity, emoji="⏰")
registry.register(name="activity_reschedule", toolset="activity", schema=_schema("activity_reschedule", "Reschedule an activity due_at timestamp and return updated row/evidence.", {"activity_id": {"type": "string"}, "due_at": {"type": "string"}, "reschedule_reason": {"type": "string"}}, ["activity_id", "due_at"]), handler=_handle_activity_reschedule, check_fn=_check_activity, emoji="⏰")
registry.register(name="activity_cancel", toolset="activity", schema=_schema("activity_cancel", "Cancel an activity and write cancellation evidence.", {"activity_id": {"type": "string"}, "cancel_reason": {"type": "string"}}, ["activity_id"]), handler=_handle_activity_cancel, check_fn=_check_activity, emoji="⏰")
registry.register(name="activity_link", toolset="activity", schema=_schema("activity_link", "Link an activity to contact/org/opportunity/project/document/calendar/external/activity targets.", _LINK_PROPS, ["activity_id", "target_type", "target_id"]), handler=_handle_activity_link, check_fn=_check_activity, emoji="⏰")
registry.register(name="activity_unlink", toolset="activity", schema=_schema("activity_unlink", "Remove a link between an activity and a target.", {"activity_id": {"type": "string"}, "target_type": {"type": "string"}, "target_id": {"type": "string"}, "relationship_type": {"type": "string"}}, ["activity_id", "target_type", "target_id"]), handler=_handle_activity_unlink, check_fn=_check_activity, emoji="⏰")
registry.register(name="activity_timeline", toolset="activity", schema=_schema("activity_timeline", "Return activities, links, and audit events for an activity or linked target.", {"activity_id": {"type": "string"}, "target_type": {"type": "string"}, "target_id": {"type": "string"}, "limit": {"type": "integer"}}), handler=_handle_activity_timeline, check_fn=_check_activity, emoji="⏰")
registry.register(name="activity_to_calendar_event", toolset="activity", schema=_schema("activity_to_calendar_event", "Create or update a Calendar Core event/block only when an activity requires time blocking, then link activity ↔ calendar_event with audit evidence. Non-calendar reminders are skipped.", {"activity_id": {"type": "string"}, "actor_id": {"type": "string"}, "calendar_id": {"type": "string"}, "start_at": {"type": "string"}, "end_at": {"type": "string"}, "start_ts": {"type": "integer"}, "duration_minutes": {"type": "integer"}, "calendar_required": {"type": "boolean"}, "block_time": {"type": "boolean"}, "busy": {"type": "boolean"}, "reason": {"type": "string"}, "provider": {"type": "string"}, "service_id": {"type": "string"}, "external_url": {"type": "string"}, "reminders": {"type": "array", "items": {"type": "object"}}, "recurrence": {"type": "object"}, "metadata": {"type": "object"}}, ["activity_id"]), handler=_handle_activity_to_calendar_event, check_fn=_check_activity, emoji="📅")
registry.register(name="activity_dispatcher_scan", toolset="activity", schema=_schema("activity_dispatcher_scan", "Run the deterministic Activity reminder dispatcher and return notification-ready outputs with audit evidence unless dry_run=true.", {"owner_id": {"type": "string"}, "limit": {"type": "integer"}, "dry_run": {"type": "boolean"}}), handler=_handle_activity_dispatcher_scan, check_fn=_check_activity, emoji="⏰")
registry.register(name="activity_plan_create", toolset="activity", schema=_schema("activity_plan_create", "Create or replace an activity plan with ordered steps.", {"plan_id": {"type": "string"}, "name": {"type": "string"}, "description": {"type": "string"}, "status": {"type": "string"}, "scope": {"type": "string"}, "owner_id": {"type": "string"}, "steps": {"type": "array", "items": {"type": "object"}}, "metadata": {"type": "object"}, "source": {"type": "string"}, "source_ref": {"type": "string"}}, ["name"]), handler=_handle_activity_plan_create, check_fn=_check_activity, emoji="⏰")
registry.register(name="activity_plan_apply", toolset="activity", schema=_schema("activity_plan_apply", "Apply an activity plan to a target and optionally create activities from auto-create steps.", {"plan_id": {"type": "string"}, "plan_run_id": {"type": "string"}, "target_type": {"type": "string"}, "target_id": {"type": "string"}, "target_name": {"type": "string"}, "owner_id": {"type": "string"}, "start_at": {"type": "string"}, "create_activities": {"type": "boolean"}, "status": {"type": "string"}, "metadata": {"type": "object"}}, ["plan_id", "target_type", "target_id"]), handler=_handle_activity_plan_apply, check_fn=_check_activity, emoji="⏰")
registry.register(name="activity_next_actions", toolset="activity", schema=_schema("activity_next_actions", "Return next actions from completed activity chains and active plan run steps.", {"owner_id": {"type": "string"}, "limit": {"type": "integer"}}), handler=_handle_activity_next_actions, check_fn=_check_activity, emoji="⏰")
registry.register(name="activity_detect", toolset="activity", schema=_schema("activity_detect", "Detect follow-up/reminder/activity suggestions from text. Preview by default; set persist=true to create activities.", {"text": {"type": "string"}, "persist": {"type": "boolean"}, "owner_id": {"type": "string"}, "source": {"type": "string"}, "source_ref": {"type": "string"}}, ["text"]), handler=_handle_activity_detect, check_fn=_check_activity, emoji="⏰")

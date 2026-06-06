"""Activity plan, chaining, recurrence, and quick-capture helpers.

This module keeps the F7 next-action engine importable as a small focused
surface while reusing ``tools.activity_tool`` for the audited Activity Core SQL
handlers and registry entries. It intentionally does not add a new runtime
package: recurrence expansion is implemented with Python stdlib for DAILY,
WEEKLY, and MONTHLY RRULE subsets used by the Factory task.
"""
from __future__ import annotations

import calendar
import json
import re
from datetime import datetime, timedelta, timezone
from typing import Any

from tools import activity_tool
from tools.registry import registry

_WEEKDAYS = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}
_WEEKDAY_NAMES = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
    "lunes": 0,
    "martes": 1,
    "miercoles": 2,
    "miércoles": 2,
    "jueves": 3,
    "viernes": 4,
    "sabado": 5,
    "sábado": 5,
    "domingo": 6,
}


def _ok(**fields: Any) -> str:
    return json.dumps({"ok": True, **fields}, ensure_ascii=False, sort_keys=True)


def _err(exc: Exception | str) -> str:
    return activity_tool._err(exc)  # Reuse tool_error JSON shape.


def _parse_dt(value: Any, field: str = "from_date") -> datetime:
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value or "").strip()
        if not text:
            raise ValueError(f"{field} is required")
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
            text = f"{text}T00:00:00+00:00"
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _parse_time(lower: str) -> tuple[int, int] | None:
    match = re.search(r"\b(?:at|a las|alas)?\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", lower)
    if not match:
        return None
    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    ampm = match.group(3)
    if ampm == "pm" and hour < 12:
        hour += 12
    if ampm == "am" and hour == 12:
        hour = 0
    if 0 <= hour <= 23 and 0 <= minute <= 59:
        return hour, minute
    return None


def _next_weekday(reference: datetime, weekday: int) -> datetime:
    days = (weekday - reference.weekday()) % 7
    if days == 0:
        days = 7
    return reference + timedelta(days=days)


def _parse_due_at(text: str, reference_now: Any = None) -> tuple[str | None, list[str]]:
    lower = text.lower()
    ref = _parse_dt(reference_now or datetime.now(timezone.utc), "reference_now").replace(second=0, microsecond=0)
    uncertainty: list[str] = []
    base: datetime | None = None

    if re.search(r"\b(tomorrow|mañana)\b", lower):
        base = ref + timedelta(days=1)
    elif re.search(r"\b(today|hoy)\b", lower):
        base = ref
    else:
        for name, weekday in _WEEKDAY_NAMES.items():
            if re.search(rf"\bnext\s+{re.escape(name)}\b", lower) or re.search(rf"\bpr[oó]ximo\s+{re.escape(name)}\b", lower):
                base = _next_weekday(ref, weekday)
                break

    time_part = _parse_time(lower)
    if base and time_part:
        base = base.replace(hour=time_part[0], minute=time_part[1])
    elif base:
        uncertainty.append("time_uncertain")
    elif re.search(r"\b(soon|pronto|cuando puedas|when you can)\b", lower):
        uncertainty.append("due_at_uncertain")

    return (base.isoformat() if base else None), uncertainty


def _detect_type(text: str) -> str:
    lower = text.lower()
    if re.search(r"\b(call|llamar|llama)\b", lower):
        return "call"
    if re.search(r"\b(remind|recordar|recu[eé]rdame)\b", lower):
        return "reminder"
    if re.search(r"\b(email|correo|write|escribir)\b", lower):
        return "email"
    return "follow_up"


def _extract_refs_and_labels(text: str) -> tuple[list[dict[str, str]], list[str]]:
    refs: list[dict[str, str]] = []
    labels: list[str] = []
    seen_refs: set[tuple[str, str]] = set()
    seen_labels: set[str] = set()

    for raw in re.findall(r"@([\w.-]+)", text, flags=re.UNICODE):
        target_id = raw.strip(".,;:!?")
        key = ("contact", target_id.lower())
        if target_id and key not in seen_refs:
            refs.append({"target_type": "contact", "target_id": target_id.lower()})
            seen_refs.add(key)

    # Lightweight person-reference inference for common quick-capture phrases
    # such as "call John" and "follow up with Ana". Keep it conservative and
    # single-token so ambiguous free text stays in the uncertainty bucket rather
    # than becoming fabricated CRM data.
    for raw in re.findall(r"\b(?:call|llamar|follow up with|follow-up with|with|con)\s+([A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÑáéíóúñ.-]+)", text):
        target_id = raw.strip(".,;:!?")
        key = ("contact", target_id.lower())
        if target_id and key not in seen_refs:
            refs.append({"target_type": "contact", "target_id": target_id.lower()})
            seen_refs.add(key)

    for raw in re.findall(r"#([\w.-]+)", text, flags=re.UNICODE):
        token = raw.strip(".,;:!?")
        if not token:
            continue
        if token[:1].isupper():
            key = ("project", token)
            if key not in seen_refs:
                refs.append({"target_type": "project", "target_id": token})
                seen_refs.add(key)
        else:
            label = token.lower()
            if label not in seen_labels:
                labels.append(label)
                seen_labels.add(label)
    return refs, labels


def _detect_recurrence(text: str) -> dict[str, Any] | None:
    lower = text.lower()
    if re.search(r"\b(every|cada)\s+(day|día|dia|daily)\b", lower):
        return {"rrule": "FREQ=DAILY", "source_text": "every day"}
    if re.search(r"\b(every|cada)\s+(week|semana|weekly)\b", lower):
        return {"rrule": "FREQ=WEEKLY", "source_text": "every week"}
    if re.search(r"\b(every|cada)\s+(month|mes|monthly)\b", lower):
        return {"rrule": "FREQ=MONTHLY", "source_text": "every month"}
    return None


def activity_plan_create(**kwargs: Any) -> str:
    """Create or replace a reusable activity plan.

    Accepts both F7 task vocabulary (``plan_name``, ``relative_after_days``,
    ``priority``) and the lower-level Activity Core vocabulary.
    """
    try:
        steps = []
        for step in kwargs.get("steps") or []:
            normalized = dict(step)
            if "title_template" not in normalized and "title" in normalized:
                normalized["title_template"] = normalized["title"]
            if "default_priority" not in normalized and "priority" in normalized:
                normalized["default_priority"] = normalized["priority"]
            if "offset_seconds" not in normalized and "relative_after_days" in normalized:
                normalized["offset_seconds"] = int(normalized.get("relative_after_days") or 0) * 86_400
            metadata = dict(normalized.get("metadata") or {})
            if normalized.get("default_assignee_id"):
                metadata["default_assignee_id"] = normalized["default_assignee_id"]
            if normalized.get("assignee_id"):
                metadata["default_assignee_id"] = normalized["assignee_id"]
            if normalized.get("labels"):
                metadata["labels"] = normalized["labels"]
            normalized["metadata"] = metadata
            steps.append(normalized)

        return activity_tool._handle_activity_plan_create({
            "plan_id": kwargs.get("plan_id"),
            "name": kwargs.get("plan_name") or kwargs.get("name"),
            "description": kwargs.get("description"),
            "status": kwargs.get("status"),
            "scope": kwargs.get("scope"),
            "owner_id": kwargs.get("owner_id"),
            "steps": steps,
            "metadata": kwargs.get("metadata") or {},
            "source": kwargs.get("source"),
            "source_ref": kwargs.get("source_ref"),
        })
    except Exception as exc:
        return _err(exc)


def activity_plan_apply(**kwargs: Any) -> str:
    """Apply a plan to a target and create/suggest run steps."""
    return activity_tool._handle_activity_plan_apply({**kwargs, "create_activities": kwargs.get("create_activities", True)})


def activity_next_actions(**kwargs: Any) -> str:
    """Return currently actionable chained activities and plan run steps."""
    return activity_tool._handle_activity_next_actions(kwargs)


def activity_complete_with_next_actions(**kwargs: Any) -> str:
    """Complete an activity and include immediate next-action suggestions.

    This is the chaining helper for UI/agent flows that want completion plus the
    next suggested action in one deterministic response. It suggests; creation
    is governed by the plan step/run config already stored by ``plan_apply``.
    """
    try:
        completion = json.loads(activity_tool._handle_activity_complete(kwargs))
        if not completion.get("ok"):
            return json.dumps(completion, ensure_ascii=False, sort_keys=True)
        next_actions = json.loads(activity_tool._handle_activity_next_actions({
            "owner_id": kwargs.get("owner_id") or "zeus",
            "limit": kwargs.get("limit") or 20,
        }))
        return _ok(completion=completion, next_actions=next_actions.get("next_actions", {}), count=next_actions.get("count", 0))
    except Exception as exc:
        return _err(exc)


def activity_detect_from_text(**kwargs: Any) -> str:
    """Parse a quick-capture text/message/email payload into activity suggestions.

    The parser is intentionally conservative: uncertain dates are returned as
    ``due_at=None`` with explicit uncertainty markers instead of fabricating a
    timestamp.
    """
    try:
        text = str(kwargs.get("text") or kwargs.get("message") or kwargs.get("subject") or "").strip()
        if not text and isinstance(kwargs.get("email"), dict):
            email = kwargs["email"]
            text = " ".join(str(email.get(k) or "") for k in ("subject", "body", "from"))
        if not text:
            raise ValueError("text is required")

        due_at, uncertainty = _parse_due_at(text, kwargs.get("reference_now"))
        refs, labels = _extract_refs_and_labels(text)
        recurrence = _detect_recurrence(text)
        suggestion = {
            "activity_type": _detect_type(text),
            "title": re.sub(r"\s+", " ", text)[:140],
            "due_at": due_at,
            "parsed_datetime": due_at,
            "recurrence": recurrence,
            "refs": refs,
            "labels": labels,
            "confidence": 0.84 if due_at else 0.62,
            "uncertainty": uncertainty,
            "evidence": {"detector": "quick-capture-v1", "text_excerpt": text[:240]},
        }
        if not due_at and "due_at_uncertain" not in suggestion["uncertainty"]:
            suggestion["uncertainty"].append("due_at_missing")

        persisted = []
        if kwargs.get("persist"):
            metadata = {
                "quick_capture": True,
                "refs": refs,
                "labels": labels,
                "recurrence": recurrence,
                "uncertainty": suggestion["uncertainty"],
            }
            result = json.loads(activity_tool._handle_activity_upsert({
                "activity_type": suggestion["activity_type"],
                "title": suggestion["title"],
                "due_at": due_at,
                "owner_id": kwargs.get("owner_id") or "zeus",
                "source": kwargs.get("source") or "agent",
                "source_ref": kwargs.get("source_ref"),
                "confidence": suggestion["confidence"],
                "evidence": suggestion["evidence"],
                "metadata": metadata,
            }))
            persisted.append(result)
        return _ok(detected_activities=[suggestion], persisted=persisted)
    except Exception as exc:
        return _err(exc)


def _parse_rrule(rrule_text: str) -> dict[str, str]:
    parts: dict[str, str] = {}
    for item in str(rrule_text or "").split(";"):
        if not item:
            continue
        if "=" not in item:
            raise ValueError(f"invalid RRULE part: {item}")
        key, value = item.split("=", 1)
        parts[key.upper()] = value.upper()
    if parts.get("FREQ") not in {"DAILY", "WEEKLY", "MONTHLY"}:
        raise ValueError("rrule_text must include FREQ=DAILY, FREQ=WEEKLY, or FREQ=MONTHLY")
    return parts


def _add_month(dt: datetime) -> datetime:
    month = dt.month + 1
    year = dt.year
    if month > 12:
        month = 1
        year += 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def activity_recurrence_expand(**kwargs: Any) -> str:
    """Expand a small RFC 5545 RRULE subset to ordered ISO timestamps."""
    try:
        rrule_text = kwargs.get("rrule_text") or kwargs.get("rrule")
        if not rrule_text and kwargs.get("rule_id"):
            row = activity_tool.sql.statement_one(
                f"SELECT * FROM activity.recurrence_rules WHERE recurrence_rule_id={activity_tool._q(kwargs.get('rule_id'))}",
                user=activity_tool._user(),
            )
            if not row:
                raise ValueError("recurrence rule not found")
            rrule_text = row.get("rrule")
            kwargs.setdefault("from_date", row.get("dtstart") or row.get("next_occurrence_at"))
            kwargs.setdefault("count", row.get("count_limit") or 10)
        rule = _parse_rrule(str(rrule_text or ""))
        start = _parse_dt(kwargs.get("from_date") or kwargs.get("dtstart"), "from_date")
        limit = max(1, min(366, int(kwargs.get("count") or rule.get("COUNT") or 10)))
        instances: list[datetime] = []

        if rule["FREQ"] == "DAILY":
            current = start
            while len(instances) < limit:
                instances.append(current)
                current += timedelta(days=1)
        elif rule["FREQ"] == "WEEKLY":
            bydays = [_WEEKDAYS[d] for d in rule.get("BYDAY", "").split(",") if d in _WEEKDAYS]
            if not bydays:
                bydays = [start.weekday()]
            current = start
            while len(instances) < limit:
                if current.weekday() in bydays and current >= start:
                    instances.append(current)
                current += timedelta(days=1)
        else:
            current = start
            while len(instances) < limit:
                instances.append(current)
                current = _add_month(current)

        output = [dt.isoformat() for dt in instances]
        return _ok(instances=output, rrule_text=rrule_text, count=len(output))
    except Exception as exc:
        return _err(exc)


# Backwards-compatible names from the F7 task graph.
activity_quick_capture = activity_detect_from_text


# Hermes tool registrations for the F7-only helper surfaces. The core plan
# create/apply/next-actions tools remain registered in activity_tool.py.
registry.register(
    name="activity_complete_with_next_actions",
    toolset="activity",
    schema=activity_tool._schema(
        "activity_complete_with_next_actions",
        "Mark an activity complete and return chained/plan next-action suggestions.",
        {"activity_id": {"type": "string"}, "owner_id": {"type": "string"}, "limit": {"type": "integer"}, "completion_note": {"type": "string"}},
        ["activity_id"],
    ),
    handler=lambda args, **_kw: activity_complete_with_next_actions(**args),
    check_fn=activity_tool._check_activity,
    emoji="⏰",
)
registry.register(
    name="activity_detect_from_text",
    toolset="activity",
    schema=activity_tool._schema(
        "activity_detect_from_text",
        "Quick-capture parser for text/message/email payloads. Extracts due dates, recurrence, refs, labels and uncertainty markers.",
        {"text": {"type": "string"}, "message": {"type": "string"}, "email": {"type": "object"}, "reference_now": {"type": "string"}, "persist": {"type": "boolean"}, "owner_id": {"type": "string"}, "source": {"type": "string"}, "source_ref": {"type": "string"}},
        [],
    ),
    handler=lambda args, **_kw: activity_detect_from_text(**args),
    check_fn=activity_tool._check_activity,
    emoji="⏰",
)
registry.register(
    name="activity_recurrence_expand",
    toolset="activity",
    schema=activity_tool._schema(
        "activity_recurrence_expand",
        "Expand recurrence rules for DAILY/WEEKLY/MONTHLY RRULE subsets into ordered ISO timestamps.",
        {"rule_id": {"type": "string"}, "rrule_text": {"type": "string"}, "rrule": {"type": "string"}, "from_date": {"type": "string"}, "dtstart": {"type": "string"}, "count": {"type": "integer"}},
        [],
    ),
    handler=lambda args, **_kw: activity_recurrence_expand(**args),
    check_fn=activity_tool._check_activity,
    emoji="⏰",
)

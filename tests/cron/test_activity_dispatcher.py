import json

from cron import activity_dispatcher


def _payload(raw: str) -> dict:
    return json.loads(raw)


def test_dispatcher_scan_returns_notification_ready_outputs_and_audits(monkeypatch):
    queries: list[str] = []
    events: list[tuple] = []

    def fake_rows(statement: str, **_kwargs):
        queries.append(statement)
        if "FROM activity.activities" in statement:
            return [
                {"activity_id": "act-due", "title": "Call Ana", "due_at": "2026-06-10T10:00:00+00:00", "owner_id": "zeus", "activity_type": "call"}
            ]
        if "FROM activity.reminder_rules" in statement:
            return [
                {"reminder_rule_id": "rule-1", "activity_id": "act-rem", "title": "Pay rent", "next_fire_at": "2026-06-10T09:00:00+00:00", "channel": "telegram", "owner_id": "zeus"}
            ]
        if "FROM activity.recurrence_rules" in statement:
            return []
        raise AssertionError(f"unexpected query: {statement}")

    monkeypatch.setattr(activity_dispatcher.sql, "rows", fake_rows)
    monkeypatch.setattr(activity_dispatcher.activity_tool, "_event", lambda *args, **kwargs: events.append((args, kwargs)) or {"event_id": len(events)})

    payload = _payload(activity_dispatcher.run_dispatcher_scan(owner_id="zeus", limit=10))

    assert payload["ok"] is True
    assert payload["status"] == "notification_ready"
    assert payload["count"] == 2
    assert payload["outputs"][0]["action_status"] == "notification_ready"
    assert payload["outputs"][1]["channel"] == "telegram"
    assert any("owner_id='zeus'" in query for query in queries)
    assert any(call[0][1] == "reminder_due" for call in events)
    assert any(call[0][1] == "reminder_dispatched" for call in events)


def test_dispatcher_scan_dry_run_does_not_write_audit_events(monkeypatch):
    monkeypatch.setattr(activity_dispatcher.sql, "rows", lambda *_args, **_kwargs: [{"activity_id": "act-1", "title": "Due", "due_at": "now", "owner_id": "zeus"}])

    def fail_event(*_args, **_kwargs):
        raise AssertionError("dry_run must not write audit events")

    monkeypatch.setattr(activity_dispatcher.activity_tool, "_event", fail_event)

    payload = _payload(activity_dispatcher.run_dispatcher_scan(dry_run=True, limit=1))

    assert payload["ok"] is True
    assert payload["audit"]["dry_run"] is True

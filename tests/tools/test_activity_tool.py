import json

from tools import activity_tool


def _payload(raw: str) -> dict:
    return json.loads(raw)


def test_activity_upsert_requires_title_before_db_query(monkeypatch):
    def fail_db(*_args, **_kwargs):
        raise AssertionError("database should not be queried when required fields are missing")

    monkeypatch.setattr(activity_tool.sql, "statement_one", fail_db)

    payload = _payload(activity_tool._handle_activity_upsert({"activity_type": "follow_up"}))

    assert payload["error"] == "title is required"


def test_activity_link_requires_target_id_before_db_query(monkeypatch):
    def fail_db(*_args, **_kwargs):
        raise AssertionError("database should not be queried when required fields are missing")

    monkeypatch.setattr(activity_tool.sql, "statement_one", fail_db)

    payload = _payload(activity_tool._handle_activity_link({"activity_id": "act_1", "target_type": "contact"}))

    assert payload["error"] == "target_id is required"


def test_activity_plan_create_validates_step_title_before_db_query(monkeypatch):
    def fail_db(*_args, **_kwargs):
        raise AssertionError("database should not be queried when required plan step fields are missing")

    monkeypatch.setattr(activity_tool.sql, "statement_one", fail_db)
    monkeypatch.setattr(activity_tool.sql, "psql", fail_db)

    payload = _payload(activity_tool._handle_activity_plan_create({"name": "VIP onboarding", "steps": [{}]}))

    assert payload["error"] == "step title_template is required"


def test_activity_limit_rejects_sql_fragments():
    assert activity_tool._limit("5; DROP TABLE activity.activities") == 20


def test_activity_upsert_uses_quoted_literals_for_sql_safety(monkeypatch):
    statements: list[str] = []

    def capture(statement: str, **_kwargs):
        statements.append(statement)
        return {"activity_id": "act_safe", "title": "Call O'Reilly", "created_at": "now", "updated_at": "now"}

    monkeypatch.setattr(activity_tool.sql, "statement_one", capture)
    monkeypatch.setattr(activity_tool.sql, "psql", lambda *_args, **_kwargs: None)

    payload = _payload(activity_tool._handle_activity_upsert({"title": "Call O'Reilly; DROP TABLE activity.activities;--"}))

    assert payload["ok"] is True
    assert "O''Reilly" in statements[0]
    assert "DROP TABLE" in statements[0]
    assert "Call O'Reilly" not in statements[0]


def test_activity_status_update_quotes_activity_id(monkeypatch):
    statements: list[str] = []

    def capture(statement: str, **_kwargs):
        statements.append(statement)
        return {"activity_id": "act_1", "status": "done", "updated_at": "now"}

    monkeypatch.setattr(activity_tool.sql, "statement_one", capture)
    monkeypatch.setattr(activity_tool, "_event", lambda *_args, **_kwargs: None)

    payload = _payload(activity_tool._handle_activity_complete({"activity_id": "act_1'; DROP SCHEMA activity;--"}))

    assert payload["ok"] is True
    assert "act_1''; DROP SCHEMA activity;--" in statements[0]


def test_activity_detection_returns_actionable_suggestion_without_db_write(monkeypatch):
    def fail_db(*_args, **_kwargs):
        raise AssertionError("detection preview must not write to the database")

    monkeypatch.setattr(activity_tool.sql, "statement_one", fail_db)

    payload = _payload(activity_tool._handle_activity_detect({"text": "Call John tomorrow at 3pm about the contract"}))

    assert payload["ok"] is True
    assert payload["detected_activities"]
    assert payload["detected_activities"][0]["activity_type"] in {"call", "follow_up", "task"}
    assert payload["detected_activities"][0]["title"]


def test_activity_to_calendar_event_skips_non_calendar_reminders(monkeypatch):
    def fake_statement(statement: str, **_kwargs):
        assert "FROM activity.activities" in statement
        return {
            "activity_id": "act-reminder",
            "activity_type": "reminder",
            "title": "Pay rent",
            "start_at": None,
            "end_at": None,
            "metadata": {},
            "participants": [],
        }

    def fail_calendar(*_args, **_kwargs):
        raise AssertionError("non-calendar reminders must not create calendar events")

    monkeypatch.setattr(activity_tool.sql, "statement_one", fake_statement)
    monkeypatch.setattr(activity_tool.calendar_tool, "calendar_create_event", fail_calendar)
    monkeypatch.setattr(activity_tool, "_event", lambda *_args, **_kwargs: {"event_id": 1})

    payload = _payload(activity_tool._handle_activity_to_calendar_event({"activity_id": "act-reminder"}))

    assert payload["ok"] is True
    assert payload["status"] == "skipped"
    assert payload["calendar_event_id"] is None


def test_activity_to_calendar_event_creates_event_and_calendar_link(monkeypatch):
    statements: list[str] = []
    events: list[tuple] = []

    def fake_statement(statement: str, **_kwargs):
        statements.append(statement)
        if "FROM activity.activities" in statement:
            return {
                "activity_id": "act-call",
                "activity_type": "call",
                "title": "Call Ana",
                "start_at": "2026-06-10T10:00:00+00:00",
                "end_at": "2026-06-10T10:30:00+00:00",
                "metadata": {},
                "participants": [{"name": "Ana"}],
            }
        if "INSERT INTO activity.activity_links" in statement:
            return {"activity_link_id": 7, "target_id": "evt-123", "relationship_type": "calendar_event"}
        raise AssertionError(f"unexpected SQL: {statement}")

    def fake_calendar_create_event(**kwargs):
        assert kwargs["actor_id"] == "actor-1"
        assert kwargs["calendar_id"] == "cal-1"
        assert kwargs["start_ts"] == 1781085600000
        assert kwargs["duration_minutes"] == 30
        assert kwargs["metadata"]["activity_id"] == "act-call"
        return {"success": True, "status": 201, "data": {"id": "evt-123"}}

    monkeypatch.setattr(activity_tool.sql, "statement_one", fake_statement)
    monkeypatch.setattr(activity_tool.calendar_tool, "calendar_create_event", fake_calendar_create_event)
    monkeypatch.setattr(activity_tool, "_event", lambda *args, **kwargs: events.append((args, kwargs)) or {"event_id": len(events)})

    payload = _payload(activity_tool._handle_activity_to_calendar_event({"activity_id": "act-call", "actor_id": "actor-1", "calendar_id": "cal-1"}))

    assert payload["ok"] is True
    assert payload["status"] == "created"
    assert payload["calendar_event_id"] == "evt-123"
    assert any("INSERT INTO activity.activity_links" in s for s in statements)
    assert any(call[0][1] == "calendar_linked" for call in events)


def test_activity_to_calendar_event_records_retryable_failure(monkeypatch):
    events: list[tuple] = []

    def fake_statement(statement: str, **_kwargs):
        if "FROM activity.activities" in statement:
            return {
                "activity_id": "act-meeting",
                "activity_type": "meeting",
                "title": "Planning",
                "start_at": "2026-06-10T10:00:00+00:00",
                "end_at": "2026-06-10T10:30:00+00:00",
                "metadata": {},
                "participants": [],
            }
        return None

    monkeypatch.setattr(activity_tool.sql, "statement_one", fake_statement)
    monkeypatch.setattr(activity_tool.calendar_tool, "calendar_create_event", lambda **_kwargs: {"success": False, "status": 503, "error": "calendar down"})
    monkeypatch.setattr(activity_tool, "_event", lambda *args, **kwargs: events.append((args, kwargs)) or {"event_id": len(events)})

    payload = _payload(activity_tool._handle_activity_to_calendar_event({"activity_id": "act-meeting", "actor_id": "actor-1", "calendar_id": "cal-1"}))

    assert payload["ok"] is True
    assert payload["status"] == "retryable"
    assert payload["calendar_event_id"] is None
    assert any(call[0][1] == "calendar_failed" and call[1]["result_status"] == "failed" for call in events)


def test_activity_dispatcher_scan_tool_delegates_to_deterministic_dispatcher(monkeypatch):
    from cron import activity_dispatcher

    calls: list[dict] = []

    def fake_dispatcher(**kwargs):
        calls.append(kwargs)
        return json.dumps({
            "ok": True,
            "status": "notification_ready",
            "outputs": [{"action_status": "notification_ready"}],
            "audit": {"dry_run": kwargs["dry_run"], "event_count": 0},
            "evidence": {"script": "cron.activity_dispatcher"},
        })

    monkeypatch.setattr(activity_dispatcher, "run_dispatcher_scan", fake_dispatcher)

    payload = _payload(activity_tool._handle_activity_dispatcher_scan({"owner_id": "zeus", "limit": 999, "dry_run": True}))

    assert payload["ok"] is True
    assert payload["status"] == "notification_ready"
    assert payload["outputs"][0]["action_status"] == "notification_ready"
    assert payload["audit"]["dry_run"] is True
    assert calls == [{"owner_id": "zeus", "limit": 500, "dry_run": True}]


def test_activity_list_filters_by_dedupe_key(monkeypatch):
    statements: list[str] = []

    def fake_rows(statement: str, **_kwargs):
        statements.append(statement)
        if "a.dedupe_key='dedupe-target'" not in statement:
            return [{"activity_id": "act-wrong", "dedupe_key": "dedupe-other"}]
        return [{"activity_id": "act-right", "dedupe_key": "dedupe-target"}]

    monkeypatch.setattr(activity_tool.sql, "rows", fake_rows)

    payload = _payload(activity_tool._handle_activity_list({"dedupe_key": "dedupe-target", "limit": 1}))

    assert payload["ok"] is True
    assert payload["activities"] == [{"activity_id": "act-right", "dedupe_key": "dedupe-target"}]
    assert statements, "activity_list did not query the database"
    assert "a.dedupe_key='dedupe-target'" in statements[0]


def test_toolset_registration_is_explicit_and_not_in_core_defaults():
    import toolsets

    activity_tools = set(toolsets.TOOLSETS["activity"]["tools"])

    assert "activity_upsert" in activity_tools
    assert "activity_list" in activity_tools
    assert "activity_complete" in activity_tools
    assert "activity_snooze" in activity_tools
    assert "activity_reschedule" in activity_tools
    assert "activity_cancel" in activity_tools
    assert "activity_timeline" in activity_tools
    assert "activity_to_calendar_event" in activity_tools
    assert "activity_plan_create" in activity_tools
    assert "activity_plan_apply" in activity_tools
    assert "activity_next_actions" in activity_tools
    assert "activity_complete_with_next_actions" in activity_tools
    assert "activity_detect" in activity_tools
    assert "activity_detect_from_text" in activity_tools
    assert "activity_recurrence_expand" in activity_tools
    assert "activity_upsert" not in toolsets._HERMES_CORE_TOOLS

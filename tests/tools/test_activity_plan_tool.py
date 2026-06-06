import json

from tools import activity_plan_tool


def _payload(raw):
    return json.loads(raw) if isinstance(raw, str) else raw


def test_activity_plan_create_accepts_reusable_steps_and_assignment_defaults(monkeypatch):
    statements = []

    def fake_statement(statement: str, **_kwargs):
        statements.append(statement)
        if "INSERT INTO activity.activity_plans" in statement:
            return {"plan_id": "plan-vip", "name": "VIP onboarding", "owner_id": "owner-1"}
        if "INSERT INTO activity.activity_plan_steps" in statement:
            return {"plan_step_id": "step-1", "default_priority": "high", "metadata": {"default_assignee_id": "sales-1"}}
        if "INSERT INTO activity.activity_events" in statement:
            return {"event_id": 1}
        raise AssertionError(f"unexpected SQL: {statement}")

    monkeypatch.setattr(activity_plan_tool.activity_tool.sql, "statement_one", fake_statement)
    monkeypatch.setattr(activity_plan_tool.activity_tool.sql, "psql", lambda *_args, **_kwargs: None)

    payload = _payload(activity_plan_tool.activity_plan_create(
        plan_id="plan-vip",
        plan_name="VIP onboarding",
        description="Reusable sequence",
        owner_id="owner-1",
        steps=[{
            "title": "Call {{target_name}}",
            "relative_after_days": 2,
            "activity_type": "call",
            "priority": "high",
            "default_assignee_id": "sales-1",
            "auto_create": True,
        }],
    ))

    assert payload["ok"] is True
    assert payload["plan_id"] == "plan-vip"
    assert "172800" in "\n".join(statements)
    assert "sales-1" in "\n".join(statements)


def test_activity_plan_apply_creates_activities_with_step_due_dates(monkeypatch):
    rows_calls = []
    statements = []

    def fake_statement(statement: str, **_kwargs):
        statements.append(statement)
        if "INSERT INTO activity.activity_plan_runs" in statement:
            return {"plan_run_id": "run-1", "owner_id": "owner-1"}
        if "INSERT INTO activity.activities" in statement:
            assert "2026-06-03T09:00:00+00:00" in statement
            return {"activity_id": "act-1", "title": "Call Acme", "due_at": "2026-06-03T09:00:00+00:00"}
        if "INSERT INTO activity.activity_plan_run_steps" in statement:
            return {"plan_run_step_id": "rs-1", "activity_id": "act-1", "status": "created"}
        if "INSERT INTO activity.activity_events" in statement:
            return {"event_id": 2}
        raise AssertionError(f"unexpected SQL: {statement}")

    def fake_rows(statement: str, **_kwargs):
        rows_calls.append(statement)
        return [{
            "plan_step_id": "step-1",
            "activity_type": "call",
            "title_template": "Call {{target_name}}",
            "description_template": "Intro call",
            "default_priority": "high",
            "offset_seconds": 172800,
            "auto_create": True,
            "metadata": {"default_assignee_id": "sales-1", "labels": ["vip"]},
        }]

    monkeypatch.setattr(activity_plan_tool.activity_tool.sql, "statement_one", fake_statement)
    monkeypatch.setattr(activity_plan_tool.activity_tool.sql, "rows", fake_rows)

    payload = _payload(activity_plan_tool.activity_plan_apply(
        plan_id="plan-vip",
        plan_run_id="run-1",
        target_type="organization",
        target_id="org-1",
        target_name="Acme",
        owner_id="owner-1",
        start_at="2026-06-01T09:00:00+00:00",
    ))

    assert payload["ok"] is True
    assert payload["plan_run_id"] == "run-1"
    assert payload["created_activities"][0]["activity_id"] == "act-1"
    assert "172800 * interval '1 second'" in "\n".join(statements)
    assert "sales-1" in "\n".join(statements)


def test_activity_complete_can_return_plan_and_chain_next_actions(monkeypatch):
    def fake_status_update(args, status, event_type, **_kwargs):
        assert status == "done"
        return json.dumps({"ok": True, "activity_id": args["activity_id"], "status": status})

    def fake_rows(statement: str, **_kwargs):
        if "activity.activity_links" in statement:
            return [{"activity_id": "act-next", "title": "Send proposal", "due_at": "2026-06-02T09:00:00+00:00"}]
        if "activity.activity_plan_run_steps" in statement:
            return [{"plan_run_step_id": "rs-2", "title_template": "Follow up {{target_name}}", "status": "suggested"}]
        raise AssertionError(f"unexpected SQL: {statement}")

    monkeypatch.setattr(activity_plan_tool.activity_tool, "_status_update", fake_status_update)
    monkeypatch.setattr(activity_plan_tool.activity_tool.sql, "rows", fake_rows)

    payload = _payload(activity_plan_tool.activity_complete_with_next_actions(activity_id="act-current", owner_id="owner-1"))

    assert payload["ok"] is True
    assert payload["completion"]["status"] == "done"
    assert payload["next_actions"]["linked_activities"][0]["activity_id"] == "act-next"
    assert payload["next_actions"]["plan_steps"][0]["status"] == "suggested"


def test_activity_detect_from_text_extracts_due_recurrence_refs_labels_and_uncertainty():
    payload = _payload(activity_plan_tool.activity_detect_from_text(
        text="Follow up with @ana about #Qrovia next Friday at 3pm every week #vip #renewal",
        reference_now="2026-06-01T10:00:00+00:00",
    ))

    detected = payload["detected_activities"][0]
    assert payload["ok"] is True
    assert detected["activity_type"] == "follow_up"
    assert detected["due_at"].startswith("2026-06-05T15:00:00")
    assert detected["recurrence"]["rrule"] == "FREQ=WEEKLY"
    assert {"target_type": "contact", "target_id": "ana"} in detected["refs"]
    assert {"target_type": "project", "target_id": "Qrovia"} in detected["refs"]
    assert "vip" in detected["labels"] and "renewal" in detected["labels"]
    assert detected["uncertainty"] == []


def test_activity_detect_from_text_reports_uncertain_due_date():
    payload = _payload(activity_plan_tool.activity_detect_from_text(
        text="Remind me soon to check invoice #finance",
        reference_now="2026-06-01T10:00:00+00:00",
    ))

    detected = payload["detected_activities"][0]
    assert detected["due_at"] is None
    assert "due_at_uncertain" in detected["uncertainty"]
    assert "finance" in detected["labels"]


def test_activity_recurrence_expand_supports_daily_weekly_monthly_ordered():
    weekly = _payload(activity_plan_tool.activity_recurrence_expand(
        rrule_text="FREQ=WEEKLY;BYDAY=MO,WE,FR;COUNT=5",
        from_date="2026-06-01T09:00:00+00:00",
        count=5,
    ))
    monthly = _payload(activity_plan_tool.activity_recurrence_expand(
        rrule_text="FREQ=MONTHLY;COUNT=2",
        from_date="2026-01-31T09:00:00+00:00",
        count=2,
    ))

    assert weekly["ok"] is True
    assert weekly["instances"] == [
        "2026-06-01T09:00:00+00:00",
        "2026-06-03T09:00:00+00:00",
        "2026-06-05T09:00:00+00:00",
        "2026-06-08T09:00:00+00:00",
        "2026-06-10T09:00:00+00:00",
    ]
    assert monthly["instances"] == [
        "2026-01-31T09:00:00+00:00",
        "2026-02-28T09:00:00+00:00",
    ]

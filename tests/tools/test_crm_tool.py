import json

from tools import crm_tool


def test_quote_totals_computes_subtotal_tax_and_total():
    subtotal, tax_amount, total = crm_tool._quote_totals([
        {"quantity": 2, "unit_price": 100, "tax_rate": 0.1},
        {"quantity": 1, "unit_price": 50, "tax_rate": 0},
    ])

    assert subtotal == 250
    assert tax_amount == 20
    assert total == 270


def test_twenty_request_reports_unconfigured_without_network(monkeypatch):
    monkeypatch.setattr(crm_tool.sql, "runtime_env", lambda: {})
    monkeypatch.delenv("TWENTY_BASE_URL", raising=False)
    monkeypatch.delenv("TWENTY_API_KEY", raising=False)

    result = crm_tool._twenty_request("GET", "/rest/companies")

    assert result["ok"] is False
    assert result["configured"] is False
    assert "TWENTY_BASE_URL" in result["error"]


def test_twenty_sync_validates_local_id_before_db_query():
    payload = json.loads(crm_tool._handle_twenty_sync({"local_type": "organization"}))

    assert payload["error"] == "local_id is required"


def test_num_rejects_sql_fragments():
    try:
        crm_tool._num("1; DROP TABLE crm.contacts")
    except ValueError as exc:
        assert "Invalid numeric value" in str(exc)
    else:
        raise AssertionError("expected numeric validation failure")


def test_toolset_exports_expanded_crm_tools():
    import toolsets

    crm_tools = set(toolsets.TOOLSETS["crm"]["tools"])

    assert "crm_contact_social_upsert" in crm_tools
    assert "crm_opportunity_upsert" in crm_tools
    assert "crm_product_upsert" in crm_tools
    assert "crm_quote_create" in crm_tools
    assert "crm_invoice_create" in crm_tools
    assert "crm_relationship_upsert" in crm_tools
    assert "crm_customer_timeline" in crm_tools
    assert "crm_twenty_sync" in crm_tools


def test_contact_social_upsert_validates_required_params():
    payload = json.loads(crm_tool._handle_contact_social_upsert({}))

    assert payload["error"] == "contact_id and platform are required"


def test_contact_upsert_accepts_structured_social_profiles(monkeypatch):
    captured_sql = []

    def fake_statement_one(sql: str, user: str = "") -> dict:
        captured_sql.append(sql)
        if "crm.contact_social_profiles" in sql:
            return {
                "social_profile_id": "social-telegram-sample",
                "contact_id": "contact-sample",
                "platform": "telegram",
                "handle": "@samplecontact",
                "external_id": "123456789",
                "display_name": "Sample Contact",
            }
        return {
            "contact_id": "contact-sample",
            "full_name": "Sample Contact",
            "email": "sample@example.com",
            "metadata": {},
        }

    monkeypatch.setattr(crm_tool.sql, "statement_one", fake_statement_one)
    monkeypatch.setattr(crm_tool.sql, "psql", lambda *a, **kw: None)

    payload = json.loads(crm_tool._handle_contact_upsert({
        "contact_id": "contact-sample",
        "full_name": "Sample Contact",
        "email": "sample@example.com",
        "social_profiles": [{
            "platform": "telegram",
            "handle": "@samplecontact",
            "external_id": "123456789",
            "display_name": "Sample Contact",
        }],
    }))

    assert payload["ok"] is True
    assert payload["social_profiles"][0]["platform"] == "telegram"
    assert any("crm.contact_social_profiles" in statement for statement in captured_sql)


# ---------------------------------------------------------------------------
# F8: CRM compatibility bridge — follow_up_create → activity layer
# ---------------------------------------------------------------------------


def test_follow_up_create_validates_required_params():
    """due_at and summary are required."""
    payload = json.loads(crm_tool._handle_follow_up_create({}))

    assert payload["error"] == "due_at and summary are required"


def test_follow_up_create_creates_activity_and_link_when_sql_succeeds(monkeypatch):
    """After INSERT into crm.follow_ups, _handle_follow_up_create must also
    create an activity in activity.activities and a link with relationship_type
    'legacy_follow_up'."""
    import hashlib

    fake_follow_up = {
        "follow_up_id": "fu-abc-123",
        "organization_id": None,
        "contact_id": "contact-1",
        "opportunity_id": None,
        "due_at": "2026-06-15T10:00:00Z",
        "summary": "Call John about proposal",
        "status": "open",
        "priority": "normal",
        "assignee": "zeus",
        "metadata": {},
    }

    def fake_statement_one(sql: str, user: str = "") -> dict:
        return dict(fake_follow_up)

    captured_calls = {"activity_upsert": None, "activity_links": [], "activity_link_count": 0}

    def fake_activity_upsert(args: dict, **_kwargs) -> str:
        captured_calls["activity_upsert"] = dict(args)
        return json.dumps({"ok": True, "activity_id": "act-crm-bridge-1"})

    def fake_activity_link(args: dict, **_kwargs) -> str:
        captured_calls["activity_links"].append(dict(args))
        captured_calls["activity_link_count"] += 1
        return json.dumps({"ok": True, "link": {"activity_link_id": f"link-{captured_calls['activity_link_count']}"}})

    monkeypatch.setattr(crm_tool.sql, "statement_one", fake_statement_one)
    monkeypatch.setattr(crm_tool.sql, "psql", lambda *a, **kw: None)
    monkeypatch.setattr(crm_tool.sql, "rows", lambda *a, **kw: [])
    monkeypatch.setattr(crm_tool.sql, "one", lambda *a, **kw: None)

    # Monkeypatch the activity_tool module-level handlers
    import tools.activity_tool as at

    monkeypatch.setattr(at, "_handle_activity_upsert", fake_activity_upsert)
    monkeypatch.setattr(at, "_handle_activity_link", fake_activity_link)

    payload = json.loads(crm_tool._handle_follow_up_create({
        "contact_id": "contact-1",
        "due_at": "2026-06-15T10:00:00Z",
        "summary": "Call John about proposal",
        "assignee": "zeus",
        "priority": "normal",
        "status": "open",
    }))

    assert payload["ok"] is True
    assert payload["follow_up"] == fake_follow_up
    assert payload["activity_id"] == "act-crm-bridge-1"
    assert payload["operation"] == "created"
    assert "dedupe_key" in payload
    assert payload["dedupe_key"].startswith("crm_fu_")

    # Verify activity_upsert was called with correct bridge params
    act_call = captured_calls["activity_upsert"]
    assert act_call is not None, "activity_upsert was never called"
    assert act_call["source"] == "crm"
    assert act_call["dedupe_key"] == payload["dedupe_key"]
    assert act_call["activity_type"] == "follow_up"
    assert act_call["title"] == "Call John about proposal"

    # Verify activity_link was called with legacy_follow_up relationship
    assert len(captured_calls["activity_links"]) >= 1, "activity_link was never called"
    legacy_link = captured_calls["activity_links"][0]
    assert legacy_link["relationship_type"] == "legacy_follow_up"
    assert legacy_link["target_schema"] == "crm"
    assert legacy_link["target_table"] == "follow_ups"

    # Verify CRM entity links were also created so timeline can find the activity
    assert len(captured_calls["activity_links"]) >= 2, (
        f"Expected at least 2 activity_link calls (legacy + contact), "
        f"got {len(captured_calls['activity_links'])}"
    )
    contact_link = captured_calls["activity_links"][1]
    assert contact_link["target_type"] == "contact"
    assert contact_link["target_id"] == "contact-1"
    assert contact_link["relationship_type"] == "context"


def test_customer_timeline_includes_activities_when_activity_tool_available(monkeypatch):
    """crm_customer_timeline must include activity-layer activities linked to
    the CRM entity via activity_timeline."""
    from tools import crm_tool

    def fake_statement_one(*a, **kw):
        return {"follow_up_id": "fu-1", "summary": "test"}

    def fake_rows(sql: str, user: str = "") -> list:
        return [{"interaction_id": "i-1", "summary": "test interaction"}]

    monkeypatch.setattr(crm_tool.sql, "statement_one", fake_statement_one)
    monkeypatch.setattr(crm_tool.sql, "psql", lambda *a, **kw: None)
    monkeypatch.setattr(crm_tool.sql, "rows", fake_rows)
    monkeypatch.setattr(crm_tool.sql, "one", lambda *a, **kw: None)

    import tools.activity_tool as at

    def fake_timeline(args: dict, **_kwargs) -> str:
        return json.dumps({
            "ok": True,
            "activities": [{"activity_id": "act-crm-1", "title": "Call from timeline", "source": "crm"}],
            "links": [],
            "events": [],
        })

    monkeypatch.setattr(at, "_handle_activity_timeline", fake_timeline)

    payload = json.loads(crm_tool._handle_customer_timeline({
        "contact_id": "contact-1",
        "limit": 10,
    }))

    assert payload["ok"] is True
    assert len(payload["activities"]) > 0
    assert payload["activities"][0]["activity_id"] == "act-crm-1"
    assert payload["activities"][0]["source"] == "crm"
    assert len(payload["interactions"]) > 0


def test_stable_id_is_deterministic():
    """Same inputs always produce the same stable_id."""
    a = crm_tool._stable_id("crm_fu", "org-1", "follow up", "2026-06-15T10:00:00Z")
    b = crm_tool._stable_id("crm_fu", "org-1", "follow up", "2026-06-15T10:00:00Z")
    assert a == b
    assert a.startswith("crm_fu_")
    assert len(a) > len("crm_fu_")


def test_stable_id_differs_for_different_inputs():
    """Different inputs produce different stable_ids."""
    a = crm_tool._stable_id("crm_fu", "contact-1", "Call John", "2026-06-15")
    b = crm_tool._stable_id("crm_fu", "contact-2", "Call John", "2026-06-15")
    assert a != b


def test_follow_up_dedupe_key_helper():
    """_follow_up_dedupe_key produces a deterministic key from args."""
    key_a = crm_tool._follow_up_dedupe_key({
        "organization_id": "org-1",
        "contact_id": "contact-1",
        "opportunity_id": None,
        "summary": "Follow up on quote",
        "due_at": "2026-07-01T10:00:00Z",
    })
    key_b = crm_tool._follow_up_dedupe_key({
        "organization_id": "org-1",
        "contact_id": "contact-1",
        "opportunity_id": None,
        "summary": "Follow up on quote",
        "due_at": "2026-07-01T10:00:00Z",
    })
    assert key_a == key_b
    assert key_a.startswith("crm_fu_")


# ---------------------------------------------------------------------------
# F8 rework: no-duplicate follow-ups via dedupe_key lookup
# ---------------------------------------------------------------------------


def test_find_activity_by_dedupe_uses_activity_list_dedupe_filter(monkeypatch):
    statements: list[str] = []

    def fake_rows(statement: str, **_kwargs):
        statements.append(statement)
        if "a.dedupe_key='dedupe-target'" not in statement:
            return [{"activity_id": "act-wrong", "dedupe_key": "dedupe-other"}]
        return [{"activity_id": "act-right", "dedupe_key": "dedupe-target"}]

    import tools.activity_tool as at

    monkeypatch.setattr(at.sql, "rows", fake_rows)

    assert crm_tool._find_activity_by_dedupe("dedupe-target") == "act-right"
    assert statements, "activity_list did not query the database"
    assert "a.dedupe_key='dedupe-target'" in statements[0]


def test_follow_up_create_second_call_returns_existing(monkeypatch):
    """Calling crm_follow_up_create twice with identical args must NOT create a
    duplicate. The second call must detect the existing row via dedupe_key in
    metadata and return operation='exists'."""
    dedupe_key = crm_tool._follow_up_dedupe_key({
        "organization_id": "org-dup-1",
        "contact_id": "contact-dup-1",
        "summary": "Duplicate test",
        "due_at": "2026-07-15T14:00:00Z",
    })

    call_count = {"statement_one": 0, "one": 0}

    def fake_statement_one(sql: str, user: str = "") -> dict:
        call_count["statement_one"] += 1
        return {
            "follow_up_id": "fu-dup-1",
            "organization_id": "org-dup-1",
            "contact_id": "contact-dup-1",
            "opportunity_id": None,
            "due_at": "2026-07-15T14:00:00Z",
            "summary": "Duplicate test",
            "status": "open",
            "priority": "normal",
            "assignee": "zeus",
            "metadata": {"dedupe_key": dedupe_key},
        }

    call_sequence = {"first": True}

    def fake_one(sql: str, user: str = "") -> dict | None:
        call_count["one"] += 1
        # First call → no existing row found (dedupe check returns None)
        # Second call → existing row found
        if call_sequence["first"]:
            call_sequence["first"] = False
            return None
        return {
            "follow_up_id": "fu-dup-1",
            "organization_id": "org-dup-1",
            "contact_id": "contact-dup-1",
            "opportunity_id": None,
            "due_at": "2026-07-15T14:00:00Z",
            "summary": "Duplicate test",
            "status": "open",
            "priority": "normal",
            "assignee": "zeus",
            "metadata": {"dedupe_key": dedupe_key},
        }

    monkeypatch.setattr(crm_tool.sql, "statement_one", fake_statement_one)
    monkeypatch.setattr(crm_tool.sql, "one", fake_one)
    monkeypatch.setattr(crm_tool.sql, "psql", lambda *a, **kw: None)

    # Mock activity_tool handlers for hermetic tests (no real DB needed)
    import tools.activity_tool as at

    def fake_activity_upsert(args: dict, **_kwargs) -> str:
        return json.dumps({"ok": True, "activity_id": "act-dup-1"})

    def fake_activity_link(args: dict, **_kwargs) -> str:
        return json.dumps({"ok": True, "link": {"activity_link_id": "link-dup-1"}})

    def fake_activity_list(args: dict, **_kwargs) -> str:
        return json.dumps({
            "ok": True,
            "activities": [{"activity_id": "act-dup-existing", "title": "Duplicate test"}],
            "count": 1,
        })

    monkeypatch.setattr(at, "_handle_activity_upsert", fake_activity_upsert)
    monkeypatch.setattr(at, "_handle_activity_link", fake_activity_link)
    monkeypatch.setattr(at, "_handle_activity_list", fake_activity_list)

    args = {
        "organization_id": "org-dup-1",
        "contact_id": "contact-dup-1",
        "due_at": "2026-07-15T14:00:00Z",
        "summary": "Duplicate test",
        "assignee": "zeus",
        "priority": "normal",
        "status": "open",
    }

    # First call — should create
    first = json.loads(crm_tool._handle_follow_up_create(args))
    assert first["ok"] is True
    assert first["operation"] == "created"
    assert first["follow_up"]["follow_up_id"] == "fu-dup-1"

    # Reset call counter to count second invocation cleanly
    call_count["statement_one"] = 0
    call_count["one"] = 0
    call_sequence["first"] = False  # fake_one will return the existing row

    # Second call — should detect existing, return operation='exists'
    second = json.loads(crm_tool._handle_follow_up_create(args))
    assert second["ok"] is True
    assert second["operation"] == "exists"
    # statement_one should NOT have been called (no INSERT on dedupe hit)
    assert call_count["statement_one"] == 0, (
        f"Expected 0 INSERTs on second call, got {call_count['statement_one']}"
    )
    # Follow-up ID matches the existing row
    assert second["follow_up"]["follow_up_id"] == "fu-dup-1"
    # activity_id must be provided for the 'exists' path (looked up via dedupe_key)
    assert second["activity_id"] is not None, (
        "Expected a non-None activity_id when existing follow-up is found, "
        "because _find_activity_by_dedupe should return the existing activity_id"
    )
    assert second["activity_id"] == "act-dup-existing"


def test_interaction_record_deduplicates_follow_up(monkeypatch):
    """Calling crm_interaction_record twice with the same follow_up_at/
    follow_up_summary must NOT create duplicate follow_ups. The existing
    follow_up should be returned with follow_up_operation='exists'."""
    dedupe_key = crm_tool._follow_up_dedupe_key({
        "organization_id": "org-ir-1",
        "contact_id": "contact-ir-1",
        "summary": "Follow up on meeting",
        "due_at": "2026-08-01T09:00:00Z",
    })

    call_state = {"statement_one_calls": 0, "one_calls": 0, "first_call": True}

    def fake_statement_one(sql: str, user: str = "") -> dict:
        call_state["statement_one_calls"] += 1
        if "crm.interactions" in sql:
            return {"interaction_id": "int-dup-1", "summary": "Meeting happened"}
        # crm.follow_ups INSERT
        return {
            "follow_up_id": "fu-ir-1",
            "organization_id": "org-ir-1",
            "contact_id": "contact-ir-1",
            "opportunity_id": None,
            "due_at": "2026-08-01T09:00:00Z",
            "summary": "Follow up on meeting",
            "priority": "high",
            "assignee": "zeus",
            "metadata": {"source_interaction_id": "int-dup-1", "dedupe_key": dedupe_key},
        }

    def fake_one(sql: str, user: str = "") -> dict | None:
        call_state["one_calls"] += 1
        if call_state["first_call"]:
            call_state["first_call"] = False
            return None
        return {
            "follow_up_id": "fu-ir-1",
            "organization_id": "org-ir-1",
            "contact_id": "contact-ir-1",
            "opportunity_id": None,
            "due_at": "2026-08-01T09:00:00Z",
            "summary": "Follow up on meeting",
            "priority": "high",
            "assignee": "zeus",
            "metadata": {"source_interaction_id": "int-dup-1", "dedupe_key": dedupe_key},
        }

    monkeypatch.setattr(crm_tool.sql, "statement_one", fake_statement_one)
    monkeypatch.setattr(crm_tool.sql, "one", fake_one)
    monkeypatch.setattr(crm_tool.sql, "psql", lambda *a, **kw: None)

    args = {
        "organization_id": "org-ir-1",
        "contact_id": "contact-ir-1",
        "summary": "Meeting happened",
        "channel": "call",
        "actor": "zeus",
        "follow_up_at": "2026-08-01T09:00:00Z",
        "follow_up_summary": "Follow up on meeting",
        "follow_up_priority": "high",
    }

    # First call — creates interaction + follow_up
    first = json.loads(crm_tool._handle_interaction_record(args))
    assert first["ok"] is True
    assert first["follow_up_operation"] == "created"
    assert first["follow_up"]["follow_up_id"] == "fu-ir-1"

    # Reset state for second call (first_call=False)
    prev_count = call_state["statement_one_calls"]
    call_state["first_call"] = False

    # Second call — creates interaction (new one each time) but follow_up
    # should detect existing and return operation='exists'
    second = json.loads(crm_tool._handle_interaction_record(args))
    assert second["ok"] is True
    assert second["follow_up_operation"] == "exists"

    # The follow_up INSERT should NOT have been called on second invocation
    follow_up_inserts = call_state["statement_one_calls"] - prev_count
    assert follow_up_inserts <= 1, (
        f"Expected at most 1 statement_one on second call (interaction INSERT), "
        f"got {follow_up_inserts}"
    )
    assert second["follow_up"]["follow_up_id"] == "fu-ir-1"


def test_two_different_follow_ups_both_get_created(monkeypatch):
    """Different follow_up inputs (different summary) must each create their
    own follow_up — dedupe must not block unrelated follow-ups."""
    insert_count = {"follow_ups": 0}
    captured_sqls = []

    def fake_one(sql: str, user: str = "") -> dict | None:
        """Return None for any dedupe_key — no existing row."""
        return None

    def fake_statement_one(sql: str, user: str = "") -> dict:
        if "INSERT INTO crm.follow_ups" in sql:
            insert_count["follow_ups"] += 1
            captured_sqls.append(sql[:120])
        return {"follow_up_id": f"fu-{insert_count['follow_ups'] or 1}", "summary": "x"}

    monkeypatch.setattr(crm_tool.sql, "statement_one", fake_statement_one)
    monkeypatch.setattr(crm_tool.sql, "one", fake_one)
    monkeypatch.setattr(crm_tool.sql, "psql", lambda *a, **kw: None)
    monkeypatch.setattr(crm_tool.sql, "rows", lambda *a, **kw: [])

    first = json.loads(crm_tool._handle_follow_up_create({
        "contact_id": "c-1", "due_at": "2026-09-01T10:00:00Z", "summary": "Call A",
    }))
    assert first["ok"] is True
    assert first["operation"] == "created"

    second = json.loads(crm_tool._handle_follow_up_create({
        "contact_id": "c-1", "due_at": "2026-09-02T10:00:00Z", "summary": "Call B",
    }))
    assert second["ok"] is True
    assert second["operation"] == "created"
    assert second["follow_up"]["follow_up_id"] != first["follow_up"]["follow_up_id"]
    # Each create produced exactly one CRM follow_ups INSERT (two total)
    assert insert_count["follow_ups"] == 2, (
        f"Expected 2 follow_ups INSERTs, got {insert_count['follow_ups']}.\n"
        f"Captured SQLs: {captured_sqls}"
    )

import json

import model_tools
import toolsets
from tools import agent_management_tool
from tools.registry import invalidate_check_fn_cache, registry


def test_onboarding_start_requires_post_payment_authorization_before_db():
    payload = json.loads(agent_management_tool._handle_onboarding_start({"client_name": "Acme"}))

    assert payload["error"] == "deploy_authorized_by is required"


def test_onboarding_payload_rejects_secret_like_keys():
    payload = json.loads(agent_management_tool._handle_onboarding_start({
        "client_name": "Acme",
        "payment_received": True,
        "deploy_authorized_by": "jean",
        "initial_form_data": {"channels": {"api_key": "should-not-be-stored"}},
    }))

    assert "secret-like field" in payload["error"]
    assert "Infisical" in payload["error"]


def test_onboarding_start_requires_boolean_payment_received_true():
    for value in (False, "false", "0", 1):
        payload = json.loads(agent_management_tool._handle_onboarding_start({
            "client_name": "Acme",
            "payment_received": value,
            "deploy_authorized_by": "jean",
        }))
        assert payload["error"] == "payment_received=true is required before onboarding"


def test_redact_session_row_redacts_scalar_secret_like_text():
    row = agent_management_tool._redact_session_row({
        "session_id": "onb-1",
        "payment_reference": "Authorization: Bearer abc.def.ghi",
        "form_data": {},
    })

    assert row is not None
    assert row["payment_reference"] == f"authorization={agent_management_tool.REDACTED_REFERENCE}"


def test_onboarding_report_redacts_secret_like_existing_data():
    report = agent_management_tool._build_onboarding_report(
        {"session_id": "onb-1", "client_name": "Ana", "agent_class": "generic_smb"},
        {
            "business": {"name": "Acme", "description": "password=hunter2", "country": "US"},
            "owner": {"name": "Ana", "primary_channel": "WhatsApp"},
            "proposal_feedback": {"liked": "speed", "buying_reason": "follow-up"},
            "operations": {"current_process": "manual", "top_pain_points": ["quotes"]},
            "agent_expectations": {"main_jobs": ["reply leads"]},
            "channels": {"access_token": "never echo"},
        },
    )

    raw = report["raw_form_data"]
    assert raw["business"]["description"] == f"password={agent_management_tool.REDACTED_REFERENCE}"
    assert raw["channels"]["access_token"] == agent_management_tool.REDACTED_FIELD


def test_onboarding_redacts_bearer_token_text_formats():
    assert agent_management_tool._redact_secret_like_text(
        "Authorization: Bearer abc.def.ghi"
    ) == f"authorization={agent_management_tool.REDACTED_REFERENCE}"
    assert agent_management_tool._redact_secret_like_text(
        "usa Bearer abcdefgh123456 para conectar"
    ) == f"usa bearer {agent_management_tool.REDACTED_REFERENCE} para conectar"


def test_merge_form_data_preserves_existing_nested_answers():
    existing = {
        "business": {"name": "Acme", "description": "Cleaning company"},
        "proposal_feedback": {"liked": "WhatsApp automation"},
    }
    patch = {
        "business": {"description": "Residential cleaning company", "country": "US"},
        "operations": {"current_process": "Manual follow-up"},
    }

    merged = agent_management_tool._merge_form_data(existing, patch)

    assert merged["business"]["name"] == "Acme"
    assert merged["business"]["description"] == "Residential cleaning company"
    assert merged["business"]["country"] == "US"
    assert merged["proposal_feedback"]["liked"] == "WhatsApp automation"
    assert merged["operations"]["current_process"] == "Manual follow-up"


def test_start_reopen_uses_deep_merged_form_for_next_prompt(monkeypatch):
    existing = {
        "session_id": "onb-acme",
        "agent_class": "generic_smb",
        "payment_reference": "old-payment",
        "source_channel": "whatsapp",
        "form_data": {"business": {"name": "Acme", "description": "Existing description"}},
        "metadata": {"labels": ["existing"]},
    }
    captured = {}

    monkeypatch.setattr(agent_management_tool.sql, "one", lambda *args, **kwargs: existing)

    def fake_statement_one(*args, **kwargs):
        merged = agent_management_tool._merge_form_data(
            existing["form_data"],
            {"business": {"country": "US"}},
        )
        captured["form_data"] = merged
        return {**existing, "form_data": merged}

    monkeypatch.setattr(agent_management_tool.sql, "statement_one", fake_statement_one)
    monkeypatch.setattr(agent_management_tool.sql, "runtime_env", lambda: {"AGENT_MANAGEMENT_DB_RUNTIME_USER": "agent_management_runtime"})

    payload = json.loads(agent_management_tool._handle_onboarding_start({
        "session_id": "onb-acme",
        "client_name": "Acme",
        "payment_received": True,
        "deploy_authorized_by": "jean",
        "source_channel": "whatsapp",
        "initial_form_data": {"business": {"country": "US"}},
    }))

    assert payload["ok"] is True
    assert captured["form_data"]["business"]["description"] == "Existing description"
    assert captured["form_data"]["business"]["country"] == "US"
    assert payload["next_prompt"]["next_field"] == "owner.name"


def test_next_prompt_targets_first_missing_required_field():
    form_data = {"business": {"name": "Acme Cleaning"}}

    prompt = agent_management_tool._compose_next_prompt(form_data, channel="whatsapp")

    assert prompt["complete"] is False
    assert prompt["next_field"] == "business.description"
    assert "Sophie" in prompt["speaker"]
    assert "qué hace" in prompt["customer_prompt"].lower()


def test_report_generation_contains_zeus_build_sections():
    form_data = {
        "business": {"name": "Acme Cleaning", "description": "Residential cleaning in Miami", "country": "US"},
        "owner": {"name": "Ana", "primary_channel": "WhatsApp"},
        "proposal_feedback": {"liked": "La automatización de cotizaciones", "buying_reason": "Responder más rápido"},
        "operations": {"current_process": "Manual WhatsApp", "top_pain_points": ["follow-up", "quotes"]},
        "agent_expectations": {"main_jobs": ["responder leads", "cotizar", "agendar"]},
    }

    report = agent_management_tool._build_onboarding_report(
        {"session_id": "onb-1", "client_name": "Ana", "agent_class": "cleaning_business"},
        form_data,
    )

    assert report["status"] == "ready_for_zeus_build_review"
    assert report["zeus_build_brief"]["client_business"] == "Acme Cleaning"
    assert "La automatización" in report["commercial_context"]["what_client_liked"]
    assert "responder leads" in report["desired_agent_behavior"]["main_jobs"]
    assert "configure_runtime_agent" in report["recommended_build_sequence"]


def test_actuation_plan_guides_customer_without_human_dependency():
    plan = agent_management_tool._build_actuation_plan(
        {"session_id": "onb-1", "client_name": "Ana", "agent_class": "cleaning_business"},
        {"agent_expectations": {"main_jobs": ["cotizar", "agendar"]}},
    )

    assert plan["human_intervention_policy"] == "agent_first_escalate_only_on_exception"
    assert any(step["owner_agent"] == "Sophie Onboarding" for step in plan["phases"])
    assert any(step["owner_agent"] == "Customer Success Agent" for step in plan["phases"])


def test_toolset_exports_agent_management_onboarding_tools():
    tools = set(toolsets.TOOLSETS["agent_management"]["tools"])

    assert "agent_mgmt_onboarding_start" in tools
    assert "agent_mgmt_onboarding_form_update" in tools
    assert "agent_mgmt_onboarding_next_prompt" in tools
    assert "agent_mgmt_onboarding_report_generate" in tools
    assert "agent_mgmt_actuation_plan_generate" in tools


def test_model_tool_definitions_expose_flat_function_schema():
    originals = {}
    for name in toolsets.TOOLSETS["agent_management"]["tools"]:
        entry = registry.get_entry(name)
        assert entry is not None
        originals[name] = entry.check_fn
        entry.check_fn = lambda: True
    invalidate_check_fn_cache()
    try:
        definitions = model_tools.get_tool_definitions(enabled_toolsets=["agent_management"], quiet_mode=False)
    finally:
        for name, original in originals.items():
            entry = registry.get_entry(name)
            assert entry is not None
            entry.check_fn = original
        invalidate_check_fn_cache()

    by_name = {definition["function"]["name"]: definition for definition in definitions}
    start = by_name["agent_mgmt_onboarding_start"]["function"]
    assert "function" not in start
    assert start["parameters"]["type"] == "object"
    assert "payment_received" in start["parameters"]["required"]
    assert "deploy_authorized_by" in start["parameters"]["required"]

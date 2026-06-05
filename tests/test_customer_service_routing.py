from pathlib import Path

from gateway.config import Platform, PlatformConfig
from gateway.session import SessionSource
from gateway.run import (
    _customer_service_prompt,
    _customer_service_route,
    _customer_service_skills_prompt,
    _customer_service_toolsets,
    _source_matches_customer_service_owner,
    _source_should_use_customer_service,
)
from gateway.platforms.whatsapp import WhatsAppAdapter
from toolsets import resolve_toolset


def _external_whatsapp_source() -> SessionSource:
    return SessionSource(
        platform=Platform.WHATSAPP,
        chat_id="15550000002@s.whatsapp.net",
        user_id="15550000002@s.whatsapp.net",
    )


def test_customer_service_routes_non_owner_whatsapp_to_sophie_toolset(monkeypatch):
    monkeypatch.delenv("WHATSAPP_ALLOWED_USERS", raising=False)
    cfg = {
        "customer_service": {
            "enabled": True,
            "channels": ["whatsapp", "email"],
            "owner_users": {"whatsapp": ["15550000001"]},
        }
    }
    source = _external_whatsapp_source()

    assert _source_should_use_customer_service(source, cfg) is True
    assert _customer_service_toolsets(cfg) == ["customer_service"]
    prompt = _customer_service_prompt(cfg)
    assert "Sophie de SitioUno" in prompt
    assert "customer_intent_raise" in prompt
    assert "Perfecto, ya tomé nota de tu solicitud" in prompt


def test_customer_service_ignores_unsafe_configured_toolsets(caplog):
    cfg = {"customer_service": {"toolsets": ["customer_service", "terminal", "file", "calendar"]}}

    assert _customer_service_toolsets(cfg) == ["customer_service"]
    assert "Ignoring unsafe customer_service.toolsets" in caplog.text


def test_customer_service_toolset_is_restricted_to_safe_crm_and_intent_raise():
    resolved = set(resolve_toolset("customer_service"))

    assert "customer_intent_raise" in resolved
    assert "crm_contact_upsert" in resolved
    assert "crm_interaction_record" in resolved
    assert "crm_follow_up_create" in resolved
    assert "crm_customer_timeline" in resolved
    assert "crm_search" in resolved
    assert "crm_organization_upsert" not in resolved
    assert "crm_opportunity_upsert" not in resolved
    assert "sales_quote_create" not in resolved
    assert "sales_customer_workspace_create" not in resolved
    assert "calendar_create_event" not in resolved
    assert "calendar_update_event" not in resolved
    assert "crm_quote_create" not in resolved
    assert "crm_invoice_create" not in resolved
    assert "crm_product_upsert" not in resolved
    assert "crm_twenty_raw_request" not in resolved
    assert "crm_twenty_sync" not in resolved
    assert "terminal" not in resolved
    assert "cronjob" not in resolved
    assert "delegate_task" not in resolved


def test_customer_intents_supervisor_toolset_excludes_raise_only_surface():
    resolved = set(resolve_toolset("customer_intents"))

    assert "customer_intent_list" in resolved
    assert "customer_intent_update" in resolved
    assert "customer_intent_raise" not in resolved


def test_customer_service_route_fails_closed_without_isolated_profile(monkeypatch, tmp_path):
    from hermes_cli import profiles as profiles_mod

    monkeypatch.delenv("WHATSAPP_ALLOWED_USERS", raising=False)
    monkeypatch.setattr(profiles_mod, "_get_profiles_root", lambda: tmp_path)
    cfg = {"customer_service": {"enabled": True, "owner_users": {"whatsapp": ["15550000001"]}}}

    route = _customer_service_route(_external_whatsapp_source(), cfg)

    assert route.enabled is False
    assert "missing customer-service profile" in route.error


def test_customer_service_route_loads_isolated_profile_skill(monkeypatch, tmp_path):
    from hermes_cli import profiles as profiles_mod

    monkeypatch.delenv("WHATSAPP_ALLOWED_USERS", raising=False)
    monkeypatch.setattr(profiles_mod, "_get_profiles_root", lambda: tmp_path)
    profile = tmp_path / "sophie-atc"
    (profile / "skills/customer-service/sophie-atc").mkdir(parents=True)
    (profile / "SOUL.md").write_text("# Sophie", encoding="utf-8")
    (profile / "skills/customer-service/sophie-atc/SKILL.md").write_text(
        "---\nname: sophie-atc\n---\n# Playbook\nEscala solicitudes reales.",
        encoding="utf-8",
    )
    cfg = {"customer_service": {"enabled": True, "owner_users": {"whatsapp": ["15550000001"]}}}

    route = _customer_service_route(_external_whatsapp_source(), cfg)

    assert route.enabled is True
    assert route.profile_name == "sophie-atc"
    assert route.profile_home == profile
    assert route.toolsets == ["customer_service"]
    assert route.skills == ["sophie-atc"]
    skill_prompt = _customer_service_skills_prompt(route)
    assert "Playbook" in skill_prompt
    assert "name: sophie-atc" not in skill_prompt
    assert "auto-loaded" in skill_prompt


def test_customer_service_keeps_owner_whatsapp_on_operator_route(monkeypatch):
    monkeypatch.delenv("WHATSAPP_ALLOWED_USERS", raising=False)
    cfg = {
        "customer_service": {
            "enabled": True,
            "channels": ["whatsapp", "email"],
            "owner_users": {"whatsapp": ["15550000001"]},
        }
    }
    source = SessionSource(
        platform=Platform.WHATSAPP,
        chat_id="15550000001@s.whatsapp.net",
        user_id="15550000001@s.whatsapp.net",
    )

    assert _source_matches_customer_service_owner(source, cfg) is True
    assert _source_should_use_customer_service(source, cfg) is False


def test_customer_service_routes_non_owner_email_to_sophie():
    cfg = {
        "customer_service": {
            "enabled": True,
            "channels": ["whatsapp", "email"],
            "owner_users": {"email": ["owner@example.com"]},
        }
    }
    source = SessionSource(
        platform=Platform.EMAIL,
        chat_id="cliente@example.com",
        user_id="cliente@example.com",
    )

    assert _source_should_use_customer_service(source, cfg) is True


def test_whatsapp_dynamic_allowed_users_pass_python_gateway_allowlist(tmp_path):
    session_dir = tmp_path / "session"
    session_dir.mkdir()
    (session_dir / "dynamic-allowed-users.json").write_text('["15550000002"]', encoding="utf-8")

    config = PlatformConfig(extra={"session_path": str(session_dir), "dm_policy": "allowlist"})
    adapter = WhatsAppAdapter(config)

    assert adapter._is_dm_allowed("15550000002@s.whatsapp.net") is True
    assert adapter._is_dm_allowed("15550000003@s.whatsapp.net") is False

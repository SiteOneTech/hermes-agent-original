from hermes_cli import agent_core_sql
from scripts import agent_core_db, agent_core_roles
import toolsets


def test_signature_module_is_in_agent_core_migration_runner():
    assert agent_core_db.DEFAULTS["AGENT_SIGNATURE_DB_NAME"] == "zeus_agent"
    spec = agent_core_db.MODULES["signature"]
    assert spec["database_env"] == "AGENT_SIGNATURE_DB_NAME"
    assert spec["migrations"].name == "signature"


def test_signature_runtime_secrets_and_roles_are_wired():
    assert agent_core_sql.DEFAULTS["SIGNATURE_DB_RUNTIME_USER"] == "signature_runtime"
    env = {"SIGNATURE_DATABASE_URL": "postgresql://signature_runtime:samplepw@127.0.0.1:55430/zeus_agent"}
    agent_core_sql._fill_passwords_from_urls(env)
    assert env["SIGNATURE_DB_RUNTIME_PASSWORD"] == "samplepw"

    assert agent_core_roles.DEFAULTS["SIGNATURE_DB_RUNTIME_USER"] == "signature_runtime"
    assert "SIGNATURE_DB_RUNTIME_PASSWORD" not in agent_core_roles.SECRET_KEYS


def test_signature_toolset_lists_full_canonical_v2_surface():
    tools = set(toolsets.resolve_toolset("signature"))
    assert {
        "signature_status",
        "signature_template_upsert",
        "signature_request_create",
        "signature_request_get",
        "signature_event_record",
        "signature_approval_hash_create",
        "signature_delivery_receipt_record",
        "signature_reminder_policy_upsert",
        "signature_reminder_attempt_record",
        "signature_followup_due",
        "signature_completed_pdf_record",
        "signature_final_copies_send",
        "signature_dashboard_metrics",
    } <= tools

from pathlib import Path

from scripts import agent_core_db


REPO_ROOT = Path(__file__).resolve().parents[1]
SIGNATURE_DIR = REPO_ROOT / "db" / "modules" / "signature"
V2_SQL = SIGNATURE_DIR / "000002_signature_v2_schema.sql"


def _sql() -> str:
    return V2_SQL.read_text(encoding="utf-8").lower()


def test_signature_module_is_registered_with_migration_runner() -> None:
    assert "signature" in agent_core_db.MODULES
    spec = agent_core_db.MODULES["signature"]
    assert spec["database_env"] == "AGENT_SIGNATURE_DB_NAME"
    assert Path(spec["migrations"]).name == "signature"


def test_signature_v2_migration_defines_normalized_tables_and_views() -> None:
    sql = _sql()
    required_objects = [
        "create table if not exists signature.template_versions",
        "create table if not exists signature.field_placements",
        "create table if not exists signature.field_values",
        "create table if not exists signature.comments",
        "create table if not exists signature.reminder_policies",
        "create table if not exists signature.reminder_attempts",
        "create table if not exists signature.delivery_receipts",
        "create table if not exists signature.metric_snapshots",
        "create or replace view signature.request_metrics",
        "create or replace view signature.dashboard_metrics",
    ]
    for object_sql in required_objects:
        assert object_sql in sql


def test_signature_v2_migration_links_templates_requests_submitters_and_artifacts() -> None:
    sql = _sql()
    required_constraints = [
        "references signature.templates(template_id)",
        "references signature.template_versions(template_version_id)",
        "references signature.field_placements(field_id)",
        "references signature.document_requests(request_id)",
        "references signature.submitters(submitter_id)",
        "references signature.attachments(attachment_id)",
    ]
    for constraint in required_constraints:
        assert constraint in sql

    assert "add column if not exists template_version_id" in sql
    assert "add column if not exists decline_blocks" in sql


def test_signature_v2_migration_includes_runtime_grants_and_default_privileges() -> None:
    sql = _sql()
    assert "grant usage on schema signature to signature_runtime, agent_runtime" in sql
    assert "grant select, insert, update, delete on all tables in schema signature to signature_runtime" in sql
    assert "grant select on all tables in schema signature to agent_runtime" in sql
    assert "grant usage, select on all sequences in schema signature to signature_runtime" in sql
    assert "alter default privileges in schema signature grant select, insert, update, delete on tables to signature_runtime" in sql
    assert "alter default privileges in schema signature grant select on tables to agent_runtime" in sql


def test_signature_v2_migration_adds_query_indexes_for_dashboard_and_workers() -> None:
    sql = _sql()
    required_indexes = [
        "idx_signature_template_versions_template",
        "idx_signature_field_placements_version_role",
        "idx_signature_field_values_request_submitter",
        "idx_signature_comments_request_field",
        "idx_signature_reminder_policies_next_due",
        "idx_signature_reminder_attempts_policy_due",
        "idx_signature_delivery_receipts_request_kind",
        "idx_signature_metric_snapshots_captured",
    ]
    for index_name in required_indexes:
        assert index_name in sql

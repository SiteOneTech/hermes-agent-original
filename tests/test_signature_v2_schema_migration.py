import os
import shutil
import subprocess
import uuid
from collections.abc import Generator
from pathlib import Path

import pytest

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


@pytest.fixture()
def migrated_signature_database() -> Generator[str, None, None]:
    if not shutil.which("docker"):
        pytest.skip("docker CLI is required for PostgreSQL semantic migration smoke")
    if os.getenv("HERMES_SKIP_DOCKER_POSTGRES_TESTS") == "1":
        pytest.skip("PostgreSQL semantic migration smoke disabled by environment")

    database = f"signature_v2_test_{uuid.uuid4().hex[:12]}"
    _psql("postgres", f'CREATE DATABASE "{database}";')
    try:
        for path in sorted((REPO_ROOT / "db" / "agent-core").glob("*.sql")):
            _psql_file(database, path)
        for path in sorted(SIGNATURE_DIR.glob("*.sql")):
            _psql_file(database, path)
        yield database
    finally:
        _psql("postgres", f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{database}';
            DROP DATABASE IF EXISTS "{database}";
        """)


def _psql(database: str, sql: str) -> str:
    proc = subprocess.run(
        [
            "docker",
            "exec",
            "-i",
            "agent-postgres",
            "psql",
            "-X",
            "-q",
            "-t",
            "-A",
            "-v",
            "ON_ERROR_STOP=1",
            "-U",
            "agent_admin",
            "-d",
            database,
        ],
        input=sql,
        text=True,
        check=True,
        capture_output=True,
    )
    return proc.stdout.strip()


def _psql_file(database: str, path: Path) -> None:
    _psql(database, path.read_text(encoding="utf-8"))


def test_signature_v2_migration_semantics_allow_started_submitter_status(
    migrated_signature_database: str,
) -> None:
    _psql(
        migrated_signature_database,
        """
        INSERT INTO signature.templates(template_id, name) VALUES ('tpl_started', 'Started status');
        INSERT INTO signature.document_requests(request_id, template_id, title)
        VALUES ('req_started', 'tpl_started', 'Started request');
        INSERT INTO signature.submitters(
          submitter_id, request_id, role, slug, token_hash_sha256, status
        ) VALUES (
          'sub_started', 'req_started', 'signer', 'slug_started', 'hash_started', 'started'
        );
        """,
    )
    status = _psql(
        migrated_signature_database,
        "SELECT status FROM signature.submitters WHERE submitter_id = 'sub_started';",
    )
    assert status == "started"


def test_signature_v2_request_metrics_do_not_multiply_join_counts(
    migrated_signature_database: str,
) -> None:
    _psql(
        migrated_signature_database,
        """
        INSERT INTO signature.templates(template_id, name) VALUES ('tpl_metrics', 'Metrics');
        INSERT INTO signature.template_versions(
          template_version_id, template_id, version_number, status
        ) VALUES ('tv_metrics', 'tpl_metrics', 1, 'active');
        INSERT INTO signature.document_requests(
          request_id, template_id, template_version_id, title, status, sent_at, completed_at
        ) VALUES (
          'req_metrics', 'tpl_metrics', 'tv_metrics', 'Metrics request', 'completed',
          now() - interval '2 hours', now()
        );
        INSERT INTO signature.submitters(
          submitter_id, request_id, role, slug, token_hash_sha256, status, required
        ) VALUES
          ('sub_required_done', 'req_metrics', 'signer', 'slug_done', 'hash_done', 'signed', true),
          ('sub_required_pending', 'req_metrics', 'approver', 'slug_pending', 'hash_pending', 'sent', true),
          ('sub_viewer', 'req_metrics', 'viewer', 'slug_viewer', 'hash_viewer', 'sent', false);
        INSERT INTO signature.reminder_policies(reminder_policy_id, request_id, channel)
        VALUES ('rp_metrics', 'req_metrics', 'email');
        INSERT INTO signature.reminder_attempts(
          reminder_attempt_id, reminder_policy_id, request_id, attempt_number, channel, status
        ) VALUES
          ('ra_sent', 'rp_metrics', 'req_metrics', 1, 'email', 'sent'),
          ('ra_delivered', 'rp_metrics', 'req_metrics', 2, 'email', 'delivered'),
          ('ra_failed', 'rp_metrics', 'req_metrics', 3, 'email', 'failed');
        INSERT INTO signature.delivery_receipts(
          delivery_receipt_id, request_id, submitter_id, kind, channel, status
        ) VALUES
          ('dr_final_sent', 'req_metrics', 'sub_required_done', 'final_copy', 'email', 'sent'),
          ('dr_final_delivered', 'req_metrics', 'sub_required_pending', 'final_copy', 'email', 'delivered'),
          ('dr_invitation', 'req_metrics', 'sub_viewer', 'invitation', 'email', 'sent');
        """,
    )
    metrics = _psql(
        migrated_signature_database,
        """
        SELECT concat_ws(',',
          required_submitters,
          completed_required_submitters,
          pending_submitters,
          declined_submitters,
          reminders_sent,
          reminder_failures,
          final_copy_receipts
        )
        FROM signature.request_metrics
        WHERE request_id = 'req_metrics';
        """,
    )
    assert metrics == "2,1,2,0,2,1,2"


def test_signature_v2_runtime_grants_are_applied_to_new_objects(
    migrated_signature_database: str,
) -> None:
    grant_summary = _psql(
        migrated_signature_database,
        """
        SELECT concat_ws(',', grantee, table_name, string_agg(privilege_type, '+' ORDER BY privilege_type))
        FROM information_schema.role_table_grants
        WHERE table_schema = 'signature'
          AND table_name IN ('template_versions', 'field_placements', 'request_metrics')
          AND grantee IN ('signature_runtime', 'agent_runtime')
        GROUP BY grantee, table_name
        ORDER BY grantee, table_name;
        """,
    ).splitlines()
    assert "agent_runtime,field_placements,SELECT" in grant_summary
    assert "agent_runtime,request_metrics,SELECT" in grant_summary
    assert "agent_runtime,template_versions,SELECT" in grant_summary
    assert "signature_runtime,field_placements,DELETE+INSERT+SELECT+UPDATE" in grant_summary
    assert any(
        row.startswith("signature_runtime,request_metrics,") and "SELECT" in row
        for row in grant_summary
    )
    assert "signature_runtime,template_versions,DELETE+INSERT+SELECT+UPDATE" in grant_summary

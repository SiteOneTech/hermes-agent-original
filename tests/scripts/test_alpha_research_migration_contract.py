from __future__ import annotations

import json
import os
import subprocess
import uuid
from pathlib import Path

import pytest

from scripts import agent_core_db


EXPECTED_ALPHA_RESEARCH_TABLES = {
    "research_programs",
    "source_registry",
    "source_policy_revisions",
    "evidence_items",
    "research_cycles",
    "alpha_cards",
    "alpha_card_evidence",
    "alpha_lineage",
    "research_reviews",
    "experiment_result_refs",
    "inert_handoff_packages",
    "runtime_readiness",
}

FORBIDDEN_ALPHA_RESEARCH_TERMS = (
    "session",
    "message",
    "collaboration",
    "vonash",
    "magnus",
    "vaos",
    "broker",
    "trading",
    "risk",
    "paper",
    "live",
    "recipient",
    "transport",
    "token",
)

EXPECTED_HANDOFF_PAYLOAD_KEYS = {
    "schema_version",
    "classification_scope",
    "validation_state",
    "not_investment_advice",
    "advisory_disclaimer",
    "authority_scope",
    "dispatch_state",
    "program_id",
    "cycle_id",
    "card_ids",
    "evidence_ids",
    "prepared_at",
}

PROHIBITED_HANDOFF_PAYLOAD_FIELDS = (
    "validated_alpha",
    "investment_advice",
    "recommendation",
    "strategy_approved",
    "promotion",
    "order",
    "risk",
    "paper_activation",
    "live_activation",
    "deployment",
    "action",
    "recipient",
    "transport",
    "url",
    "token",
)


def _agent_postgres_available() -> bool:
    proc = subprocess.run(
        ["docker", "inspect", "-f", "{{.State.Running}}", "agent-postgres"],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    return proc.returncode == 0 and proc.stdout.strip() == "true"


def _psql(
    database: str,
    sql: str,
    *,
    user: str = "agent_admin",
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
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
            user,
            "-d",
            database,
        ],
        input=sql,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=check,
    )


@pytest.fixture(scope="module")
def migrated_alpha_research_database():
    if not _agent_postgres_available():
        pytest.skip("agent-postgres container is not running")

    database = f"alr020_payload_{uuid.uuid4().hex[:12]}"
    env = {
        **os.environ,
        "AGENT_DB_ADMIN_USER": "agent_admin",
        "AGENT_DB_NAME": database,
        "AGENT_ALPHA_RESEARCH_DB_NAME": database,
    }

    agent_core_db.ensure_database(env, database)
    try:
        agent_core_db.apply_module(env, "agent_core")
        agent_core_db.apply_module(env, "alpha_research")
        yield database
    finally:
        agent_core_db.psql(
            env,
            "postgres",
            "SELECT pg_terminate_backend(pid) "
            "FROM pg_stat_activity "
            f"WHERE datname = {agent_core_db.quote_literal(database)} "
            "AND pid <> pg_backend_pid();",
            check=False,
        )
        agent_core_db.psql(
            env,
            "postgres",
            f"DROP DATABASE IF EXISTS {agent_core_db.quote_ident(database)};",
            check=False,
        )


def _create_runtime_program(database: str) -> str:
    proc = _psql(
        database,
        f"""
        INSERT INTO alpha_research.research_programs(name, universe)
        VALUES ('payload contract behavior {uuid.uuid4()}', 'local research universe')
        RETURNING program_id;
        """,
        user="alpha_research_runtime",
    )
    return proc.stdout.strip()


def _insert_handoff(
    database: str,
    program_id: str,
    payload: str | None = None,
    prepared_at: str | None = None,
) -> subprocess.CompletedProcess[str]:
    payload_sql = "DEFAULT" if payload is None else f"$payload${payload}$payload$::jsonb"
    prepared_at_column = ", prepared_at" if prepared_at is not None else ""
    prepared_at_value = (
        f", $prepared_at${prepared_at}$prepared_at$::timestamptz"
        if prepared_at is not None
        else ""
    )
    return _psql(
        database,
        f"""
        INSERT INTO alpha_research.inert_handoff_packages(
          program_id,
          card_ids,
          payload{prepared_at_column}
        )
        VALUES (
          '{program_id}'::uuid,
          ARRAY['00000000-0000-0000-0000-000000000001']::uuid[],
          {payload_sql}{prepared_at_value}
        )
        RETURNING payload::text;
        """,
        user="alpha_research_runtime",
        check=False,
    )


def _insert_handoff_row(database: str, program_id: str) -> dict[str, object]:
    proc = _psql(
        database,
        f"""
        INSERT INTO alpha_research.inert_handoff_packages(program_id, card_ids)
        VALUES (
          '{program_id}'::uuid,
          ARRAY['00000000-0000-0000-0000-000000000001']::uuid[]
        )
        RETURNING jsonb_build_object(
          'handoff_id', handoff_id,
          'payload', payload
        )::text;
        """,
        user="alpha_research_runtime",
    )
    return json.loads(proc.stdout)


def test_alpha_research_module_registers_private_local_schema_contract():
    spec = agent_core_db.MODULES["alpha_research"]

    assert agent_core_db.DEFAULTS["AGENT_ALPHA_RESEARCH_DB_NAME"] == "zeus_agent"
    assert spec["database_env"] == "AGENT_ALPHA_RESEARCH_DB_NAME"
    assert spec["migrations"].name == "alpha_research"

    contract = spec["contract"]
    assert contract["schema"] == "alpha_research"
    assert set(contract["tables"]) == EXPECTED_ALPHA_RESEARCH_TABLES
    assert contract["author_role"] == "alpha_research_runtime"
    assert contract["reviewer_role"] == "alpha_research_reviewer"
    assert contract["source_classes"] == (
        "local_normalized_batch",
        "manual_reference_metadata",
        "licensed_local_document",
    )
    assert contract["classification"] == {
        "classification_scope": "research_only",
        "validation_state": "unvalidated",
        "not_investment_advice": True,
        "advisory_disclaimer": "Research only; unvalidated; not investment advice.",
    }
    assert contract["external_authority"] == ()

    contract_words = {
        name.lower()
        for value in contract.values()
        for name in (value if isinstance(value, tuple) else (value,))
        if isinstance(name, str)
    }
    assert not any(
        forbidden in name
        for name in contract_words
        for forbidden in FORBIDDEN_ALPHA_RESEARCH_TERMS
    )


def test_alpha_research_module_migrates_through_shared_agent_core_runner(monkeypatch):
    calls: list[tuple[str, str | Path]] = []

    def fake_ensure_database(env, database):
        calls.append(("ensure_database", database))

    def fake_ensure_migration_ledger(env, database):
        calls.append(("ensure_migration_ledger", database))

    def fake_migration_applied(env, database, module, version):
        calls.append(("migration_applied", f"{database}:{module}:{version}"))
        return False

    def fake_psql_file(env, database, path):
        calls.append(("psql_file", path.relative_to(agent_core_db.REPO_ROOT)))

    def fake_record_migration(env, database, module, version, checksum):
        assert len(checksum) == 64
        calls.append(("record_migration", f"{database}:{module}:{version}"))

    monkeypatch.setattr(agent_core_db, "ensure_database", fake_ensure_database)
    monkeypatch.setattr(agent_core_db, "ensure_migration_ledger", fake_ensure_migration_ledger)
    monkeypatch.setattr(agent_core_db, "migration_applied", fake_migration_applied)
    monkeypatch.setattr(agent_core_db, "psql_file", fake_psql_file)
    monkeypatch.setattr(agent_core_db, "record_migration", fake_record_migration)

    agent_core_db.apply_module(
        {
            "AGENT_ALPHA_RESEARCH_DB_NAME": "zeus_agent",
        },
        "alpha_research",
    )

    assert calls[:2] == [
        ("ensure_database", "zeus_agent"),
        ("ensure_migration_ledger", "zeus_agent"),
    ]
    assert (
        "psql_file",
        Path("db/modules/alpha_research/000001_alpha_research_schema.sql"),
    ) in calls
    assert (
        "psql_file",
        Path("db/modules/alpha_research/000002_inert_handoff_payload_contract.sql"),
    ) in calls
    assert ("record_migration", "zeus_agent:alpha_research:000001") in calls
    assert ("record_migration", "zeus_agent:alpha_research:000002") in calls

    psql_000001 = calls.index(
        (
            "psql_file",
            Path("db/modules/alpha_research/000001_alpha_research_schema.sql"),
        )
    )
    record_000001 = calls.index(("record_migration", "zeus_agent:alpha_research:000001"))
    psql_000002 = calls.index(
        (
            "psql_file",
            Path("db/modules/alpha_research/000002_inert_handoff_payload_contract.sql"),
        )
    )
    record_000002 = calls.index(("record_migration", "zeus_agent:alpha_research:000002"))
    assert psql_000001 < record_000001 < psql_000002 < record_000002


def test_inert_handoff_payload_is_canonicalized_by_database(migrated_alpha_research_database):
    program_id = _create_runtime_program(migrated_alpha_research_database)

    proc = _insert_handoff(migrated_alpha_research_database, program_id)

    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert set(payload) == EXPECTED_HANDOFF_PAYLOAD_KEYS
    assert payload["schema_version"] == "alpha_research/v1"
    assert payload["classification_scope"] == "research_only"
    assert payload["validation_state"] == "unvalidated"
    assert payload["not_investment_advice"] is True
    assert (
        payload["advisory_disclaimer"]
        == "Research only; unvalidated; not investment advice."
    )
    assert payload["authority_scope"] == "research_only"
    assert payload["dispatch_state"] == "not_dispatched"
    assert payload["program_id"] == program_id
    assert payload["cycle_id"] is None
    assert payload["card_ids"] == ["00000000-0000-0000-0000-000000000001"]
    assert payload["evidence_ids"] == []
    assert isinstance(payload["prepared_at"], str)
    assert "recipient" not in payload
    assert "transport" not in payload
    assert "token" not in payload
    assert "url" not in payload


@pytest.mark.parametrize("field", PROHIBITED_HANDOFF_PAYLOAD_FIELDS)
def test_inert_handoff_payload_rejects_operational_fields(
    migrated_alpha_research_database,
    field,
):
    program_id = _create_runtime_program(migrated_alpha_research_database)

    proc = _insert_handoff(
        migrated_alpha_research_database,
        program_id,
        json.dumps({field: "blocked"}),
    )

    assert proc.returncode != 0
    assert "alpha_research_handoff_payload_prohibited_field" in proc.stderr
    assert "blocked" not in proc.stderr


def test_inert_handoff_payload_rejects_unknown_fields(migrated_alpha_research_database):
    program_id = _create_runtime_program(migrated_alpha_research_database)

    proc = _insert_handoff(
        migrated_alpha_research_database,
        program_id,
        json.dumps({"freeform_next_step": "blocked"}),
    )

    assert proc.returncode != 0
    assert "alpha_research_handoff_payload_unknown_field" in proc.stderr
    assert "blocked" not in proc.stderr


@pytest.mark.parametrize("payload", ("null", "[]", '"text"'))
def test_inert_handoff_payload_rejects_non_object_payloads(
    migrated_alpha_research_database,
    payload,
):
    program_id = _create_runtime_program(migrated_alpha_research_database)

    proc = _insert_handoff(migrated_alpha_research_database, program_id, payload)

    assert proc.returncode != 0
    assert "alpha_research_handoff_payload_object_required" in proc.stderr


def test_inert_handoff_payload_rejects_allowed_key_with_operational_value(
    migrated_alpha_research_database,
):
    program_id = _create_runtime_program(migrated_alpha_research_database)
    canonical = json.loads(_insert_handoff(migrated_alpha_research_database, program_id).stdout)
    canonical["authority_scope"] = "paper_activation"

    proc = _insert_handoff(
        migrated_alpha_research_database,
        program_id,
        json.dumps(canonical),
        prepared_at=canonical["prepared_at"],
    )

    assert proc.returncode != 0
    assert "alpha_research_handoff_payload_invalid" in proc.stderr
    assert "paper_activation" not in proc.stderr


def test_inert_handoff_payload_accepts_exact_canonical_payload(
    migrated_alpha_research_database,
):
    program_id = _create_runtime_program(migrated_alpha_research_database)
    canonical = json.loads(_insert_handoff(migrated_alpha_research_database, program_id).stdout)

    proc = _insert_handoff(
        migrated_alpha_research_database,
        program_id,
        json.dumps(canonical),
        prepared_at=canonical["prepared_at"],
    )

    assert proc.returncode == 0, proc.stderr
    assert json.loads(proc.stdout) == canonical


def test_inert_handoff_payload_cannot_be_mutated_after_insert(
    migrated_alpha_research_database,
):
    program_id = _create_runtime_program(migrated_alpha_research_database)
    row = _insert_handoff_row(migrated_alpha_research_database, program_id)

    update_proc = _psql(
        migrated_alpha_research_database,
        f"""
        UPDATE alpha_research.inert_handoff_packages
        SET payload = '{{"recipient":"blocked"}}'::jsonb
        WHERE handoff_id = '{row["handoff_id"]}'::uuid;
        """,
        user="agent_admin",
        check=False,
    )
    payload_proc = _psql(
        migrated_alpha_research_database,
        f"""
        SELECT payload::text
        FROM alpha_research.inert_handoff_packages
        WHERE handoff_id = '{row["handoff_id"]}'::uuid;
        """,
        user="alpha_research_runtime",
    )

    assert update_proc.returncode != 0
    assert "alpha_research_handoff_payload_immutable" in update_proc.stderr
    assert "blocked" not in update_proc.stderr
    assert json.loads(payload_proc.stdout) == row["payload"]

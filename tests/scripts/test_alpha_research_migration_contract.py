from __future__ import annotations

from pathlib import Path

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
    assert ("record_migration", "zeus_agent:alpha_research:000001") in calls

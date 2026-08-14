from __future__ import annotations

import subprocess
import sys

from scripts import agent_core_db


def test_agent_core_db_migrate_can_target_factory_module_and_verify(monkeypatch):
    calls: list[tuple[str, object]] = []
    env = {
        "AGENT_DB_NAME": "zeus_agent",
        "AGENT_CALENDAR_DB_NAME": "nettu_calendar",
        "AGENT_CRM_DB_NAME": "zeus_agent",
        "AGENT_FITNESS_DB_NAME": "zeus_agent",
        "AGENT_SIGNATURE_DB_NAME": "zeus_agent",
        "AGENT_AGENT_MANAGEMENT_DB_NAME": "zeus_agent",
    }

    monkeypatch.setattr(agent_core_db, "runtime_env", lambda: env)
    monkeypatch.setattr(
        agent_core_db,
        "compose",
        lambda _env, args: calls.append(("compose", tuple(args)))
        or subprocess.CompletedProcess(args, 0, stdout="", stderr=""),
    )
    monkeypatch.setattr(agent_core_db, "ensure_database", lambda _env, database: calls.append(("ensure_database", database)))
    monkeypatch.setattr(agent_core_db, "apply_module", lambda _env, module: calls.append(("apply_module", module)))
    monkeypatch.setattr(agent_core_db, "verify_module", lambda _env, module: calls.append(("verify_module", module)), raising=False)
    monkeypatch.setattr(sys, "argv", ["agent_core_db.py", "migrate", "--module", "factory"])

    agent_core_db.main()

    assert ("apply_module", "factory") in calls
    assert ("verify_module", "factory") in calls
    assert ("apply_module", "agent_core") not in calls


def test_factory_module_apply_applies_000004_once_and_then_skips_idempotently(monkeypatch):
    env = {"AGENT_DB_NAME": "zeus_agent"}
    applied_versions = {"000001", "000002", "000003"}
    applied_files: list[str] = []

    monkeypatch.setattr(agent_core_db, "ensure_database", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(agent_core_db, "ensure_migration_ledger", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        agent_core_db,
        "migration_applied",
        lambda _env, _database, module, version: module == "factory" and version in applied_versions,
    )

    def fake_psql_file(_env, _database, path):
        applied_files.append(path.name)

    def fake_record_migration(_env, _database, module, version, _checksum):
        assert module == "factory"
        applied_versions.add(version)

    monkeypatch.setattr(agent_core_db, "psql_file", fake_psql_file)
    monkeypatch.setattr(agent_core_db, "record_migration", fake_record_migration)

    agent_core_db.apply_module(env, "factory")
    agent_core_db.apply_module(env, "factory")

    assert applied_files == ["000004_successor_control.sql"]


def test_verify_factory_module_checks_successor_control_privileges(monkeypatch):
    captured: dict[str, str] = {}
    env = {"AGENT_DB_NAME": "zeus_agent", "FACTORY_DB_RUNTIME_USER": "factory_runtime"}

    def fake_psql(_env, database, sql, **_kwargs):
        captured["database"] = database
        captured["sql"] = sql
        return subprocess.CompletedProcess(
            ["psql"],
            0,
            stdout="\n".join(
                [
                    "factory:000004|ok",
                    "factory.runtime_leases|ok",
                    "factory.project_successions|ok",
                    "factory.runtime_leases:factory_runtime:write|ok",
                    "factory.project_successions:factory_runtime:write|ok",
                    "factory.project_successions_succession_id_seq:factory_runtime|ok",
                ]
            )
            + "\n",
            stderr="",
        )

    monkeypatch.setattr(agent_core_db, "psql", fake_psql)

    result = agent_core_db.verify_module(env, "factory")

    assert result["ready"] is True
    assert captured["database"] == "zeus_agent"
    assert "agent_core.schema_migrations" in captured["sql"]
    assert "000004" in captured["sql"]
    assert "factory.runtime_leases" in captured["sql"]
    assert "factory.project_successions" in captured["sql"]
    assert "has_table_privilege" in captured["sql"]
    assert "factory_runtime" in captured["sql"]
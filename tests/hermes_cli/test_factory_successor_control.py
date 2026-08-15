"""Regression tests for FRE-025 successor activation and global control lease."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts import agent_core_db
from hermes_cli import factory_pg


ROOT = Path(__file__).resolve().parents[2]


def _project(project_id: str, *, status: str = "completed", autonomous: bool = False, metadata: dict | None = None) -> dict:
    return {
        "project_id": project_id,
        "status": status,
        "autonomous_enabled": autonomous,
        "metadata": metadata or {},
    }


def _succession(*, allow_auto_resume: bool = True) -> dict:
    return {
        "predecessor_project_id": "factory-runtime",
        "successor_project_id": "alpha",
        "status": "declared",
        "declared_at": "2026-08-12T22:00:00Z",
        "authorization_metadata": {
            "authorized_by": "jean",
            "reason": "Factory green then research-only Alpha",
            "allow_auto_resume": allow_auto_resume,
        },
    }


def test_successor_control_migration_is_discovered_as_a_new_factory_version():
    versions = [
        agent_core_db.migration_version(path)
        for path in sorted((ROOT / "db/modules/factory").glob("*.sql"))
    ]

    assert "000004" in versions
    assert "000005" in versions
    assert agent_core_db.MODULES["factory"]["migrations"] == ROOT / "db/modules/factory"
    assert agent_core_db.migration_version(ROOT / "db/modules/factory/000004_successor_control.sql") == "000004"
    assert agent_core_db.migration_version(ROOT / "db/modules/factory/000005_document_dispatch_readiness_serialization.sql") == "000005"


def test_factory_runtime_requires_000005_readiness_serialization_migration(monkeypatch):
    assert factory_pg.REQUIRED_FACTORY_MIGRATION_VERSION == "000005"

    captured: dict[str, str] = {}

    class FakeSql:
        @staticmethod
        def rows(query, **_kwargs):
            captured["query"] = query
            return [{
                "migration_000005_applied": True,
                "runtime_leases_exists": True,
                "project_successions_exists": True,
                "readiness_guard_trigger_exists": True,
                "runtime_leases_write_ok": True,
                "project_successions_write_ok": True,
                "project_successions_sequence_ok": True,
            }]

        @staticmethod
        def quote_literal(value):
            return "'" + str(value).replace("'", "''") + "'"

        @staticmethod
        def runtime_env():
            return {"FACTORY_DB_RUNTIME_USER": "factory_runtime"}

    monkeypatch.setattr(factory_pg, "sql", FakeSql)
    monkeypatch.setattr(factory_pg, "_SCHEMA_READY", False)

    assert factory_pg.factory_migration_readiness()["ready"] is True
    assert "000005" in captured["query"]
    assert "factory_projects_document_dispatch_readiness_guard" in captured["query"]


def test_force_tick_fails_closed_when_factory_readiness_serialization_migration_is_missing(monkeypatch):
    calls: list[tuple[str, str, str | None]] = []

    class FakeSql:
        @staticmethod
        def rows(query, **kwargs):
            calls.append(("rows", query, kwargs.get("user")))
            assert kwargs.get("user") == "factory_runtime"
            assert "agent_core.schema_migrations" in query
            assert "000005" in query
            assert "factory_projects_document_dispatch_readiness_guard" in query
            assert "factory.runtime_leases" in query
            assert "factory.project_successions" in query
            return [
                {
                    "migration_000005_applied": False,
                    "runtime_leases_exists": False,
                    "project_successions_exists": False,
                    "readiness_guard_trigger_exists": False,
                    "runtime_leases_write_ok": False,
                    "project_successions_write_ok": False,
                    "project_successions_sequence_ok": False,
                }
            ]

        @staticmethod
        def statement_one(query, **kwargs):
            calls.append(("statement_one", query, kwargs.get("user")))
            raise subprocess.CalledProcessError(
                3,
                ["psql"],
                stderr='ERROR: relation "factory.runtime_leases" does not exist',
            )

        @staticmethod
        def psql(query, **kwargs):
            calls.append(("psql", query, kwargs.get("user")))
            return subprocess.CompletedProcess(["psql"], 0, stdout="", stderr="")

        @staticmethod
        def runtime_env():
            return {"FACTORY_DB_RUNTIME_USER": "factory_runtime"}

        @staticmethod
        def quote_literal(value):
            return "'" + str(value).replace("'", "''") + "'"

        @staticmethod
        def quote_jsonb(_value):
            return "'{}'::jsonb"

    def fail_if_reached(*_args, **_kwargs):
        raise AssertionError("claim/spawn path must not run when Factory 000005 is missing")

    monkeypatch.setattr(factory_pg, "sql", FakeSql)
    monkeypatch.setattr(factory_pg, "_SCHEMA_READY", False)
    monkeypatch.setattr(factory_pg, "monitor_runs", fail_if_reached)
    monkeypatch.setattr(factory_pg, "claim_next_review", fail_if_reached)
    monkeypatch.setattr(factory_pg, "claim_next_task", fail_if_reached)
    monkeypatch.setattr(factory_pg, "claim_next_rework", fail_if_reached)

    with pytest.raises(RuntimeError) as exc:
        factory_pg.force_tick(holder="tick-missing-000005")

    message = str(exc.value)
    assert "Factory migration readiness failed" in message
    assert "000005" in message
    assert "scripts/agent_core_db.py migrate --module factory" in message
    assert [call[0] for call in calls] == ["rows"]


def test_declared_successor_persists_authorization_metadata_contract(monkeypatch):
    statements: list[str] = []

    class FakeSql:
        @staticmethod
        def statement_one(query, **_kwargs):
            statements.append(query)
            return {"succession_id": 42}

        @staticmethod
        def psql(query, **_kwargs):
            statements.append(query)

        @staticmethod
        def quote_literal(value):
            return "'" + str(value).replace("'", "''") + "'"

        @staticmethod
        def quote_jsonb(value):
            import json

            return "'" + json.dumps(value).replace("'", "''") + "'::jsonb"

        @staticmethod
        def runtime_env():
            return {}

    monkeypatch.setattr(factory_pg, "sql", FakeSql)
    monkeypatch.setattr(factory_pg, "ensure_runtime_schema", lambda: None)
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: {"project_id": project_id})

    result = factory_pg.declare_project_succession(
        "factory-runtime",
        "alpha",
        authorization={
            "authorized_by": "Jean",
            "reason": "Factory green then research-only Alpha",
            "allow_auto_resume": True,
        },
        declared_by="Jean",
    )

    assert result["succession_id"] == 42
    joined = "\n".join(statements)
    assert "INSERT INTO factory.project_successions" in joined
    assert "authorization_metadata" in joined
    assert "project_succession_declared" in joined


def test_successor_activation_requires_integrated_predecessor_and_no_unapproved_manual_pause(monkeypatch):
    predecessor = _project("factory-runtime")
    successor = _project("alpha", status="paused", metadata={"manual_pause": True})
    monkeypatch.setattr(factory_pg, "_source_increment_integration_blockers", lambda *_args: [{"task_id": "fre-025"}])

    blockers = factory_pg._successor_activation_blockers(
        _succession(),
        predecessor,
        successor,
        predecessor_tasks=[{"task_id": "fre-025", "status": "done"}],
        successor_tasks=[{"task_id": "alr-020", "status": "todo"}],
        pending_human_questions=[],
        active_autonomous_project_ids=[],
    )
    assert "predecessor_source_delivery_unverified" in blockers

    monkeypatch.setattr(factory_pg, "_source_increment_integration_blockers", lambda *_args: [])
    blockers = factory_pg._successor_activation_blockers(
        _succession(allow_auto_resume=False),
        predecessor,
        successor,
        predecessor_tasks=[],
        successor_tasks=[{"task_id": "alr-020", "status": "todo"}],
        pending_human_questions=[],
        active_autonomous_project_ids=[],
    )
    assert "successor_manual_pause_after_succession_declaration" in blockers


def test_successor_activation_allows_only_explicit_jean_authorized_research_resume(monkeypatch):
    monkeypatch.setattr(factory_pg, "_source_increment_integration_blockers", lambda *_args: [])
    blockers = factory_pg._successor_activation_blockers(
        _succession(allow_auto_resume=True),
        _project("factory-runtime"),
        _project("alpha", status="paused", metadata={"manual_pause": True, "manual_pause_recorded_at": "2026-08-12T21:00:00Z"}),
        predecessor_tasks=[],
        successor_tasks=[{"task_id": "alr-020", "status": "todo"}],
        pending_human_questions=[],
        active_autonomous_project_ids=[],
    )

    assert blockers == []



def test_successor_activation_never_overrides_human_pause_after_declaration(monkeypatch):
    monkeypatch.setattr(factory_pg, "_source_increment_integration_blockers", lambda *_args: [])
    blockers = factory_pg._successor_activation_blockers(
        _succession(),
        _project("factory-runtime"),
        _project("alpha", status="paused", metadata={"manual_pause": True, "manual_pause_recorded_at": "2026-08-12T23:00:00Z"}),
        predecessor_tasks=[],
        successor_tasks=[{"task_id": "alr-020", "status": "todo"}],
        pending_human_questions=[],
        active_autonomous_project_ids=[],
    )

    assert blockers == ["successor_manual_pause_after_succession_declaration"]


def test_successor_activation_blocks_human_question_manual_attention_and_other_active_slot(monkeypatch):
    monkeypatch.setattr(factory_pg, "_source_increment_integration_blockers", lambda *_args: [])
    blockers = factory_pg._successor_activation_blockers(
        _succession(),
        _project("factory-runtime"),
        _project("alpha", status="manual_attention", metadata={"manual_attention_required": True}),
        predecessor_tasks=[],
        successor_tasks=[{"task_id": "alr-020", "status": "todo"}],
        pending_human_questions=[{"question_id": "q-1", "status": "pending"}],
        active_autonomous_project_ids=["another-project"],
    )

    assert set(blockers) == {
        "successor_manual_attention_required",
        "successor_pending_human_question",
        "single_active_slot_occupied:another-project",
    }


def test_global_lease_acquire_is_atomic_and_expiry_safe(monkeypatch):
    class FakeSql:
        calls: list[str] = []

        @classmethod
        def statement_one(cls, query, **_kwargs):
            cls.calls.append(query)
            return {"lease_key": "factory-control-plane", "holder": "tick-a", "acquired": True}

        @staticmethod
        def quote_literal(value):
            return "'" + str(value).replace("'", "''") + "'"

        @staticmethod
        def quote_jsonb(value):
            return "'{}'::jsonb"

        @staticmethod
        def runtime_env():
            return {}

    monkeypatch.setattr(factory_pg, "sql", FakeSql)
    monkeypatch.setattr(factory_pg, "ensure_runtime_schema", lambda: None)

    result = factory_pg.acquire_global_control_plane_lease("tick-a", ttl_seconds=90)

    assert result["acquired"] is True
    query = "\n".join(FakeSql.calls)
    assert "INSERT INTO factory.runtime_leases" in query
    assert "ON CONFLICT (lease_key)" in query
    assert "expires_at <= now()" in query


def test_force_tick_releases_retained_global_lease_when_tick_raises(monkeypatch):
    released: list[str] = []
    monkeypatch.setattr(factory_pg, "ensure_runtime_schema", lambda: None)
    monkeypatch.setattr(factory_pg, "acquire_global_control_plane_lease", lambda *_args, **_kwargs: {"acquired": True})
    monkeypatch.setattr(factory_pg, "release_global_control_plane_lease", lambda holder: released.append(holder))
    monkeypatch.setattr(factory_pg, "monitor_runs", lambda: (_ for _ in ()).throw(RuntimeError("transient db failure")))

    import pytest
    with pytest.raises(RuntimeError, match="transient db failure"):
        factory_pg.force_tick(holder="tick-a", retain_lease=True)

    assert released == ["tick-a"]


def test_force_tick_skips_when_global_control_lease_is_held(monkeypatch):
    monkeypatch.setattr(factory_pg, "ensure_runtime_schema", lambda: None)
    monkeypatch.setattr(
        factory_pg,
        "acquire_global_control_plane_lease",
        lambda _holder, ttl_seconds=0: {"acquired": False, "holder": "other-tick", "lease_key": "factory-control-plane"},
    )

    result = factory_pg.force_tick(holder="this-tick")

    assert result["skipped"] is True
    assert result["reason"] == "global_control_plane_lease_held"


def test_global_lease_release_expires_the_callers_lease_without_delete_permission(monkeypatch):
    statements: list[str] = []

    class FakeSql:
        @staticmethod
        def psql(query, **_kwargs):
            statements.append(query)

        @staticmethod
        def quote_literal(value):
            return "'" + str(value).replace("'", "''") + "'"

        @staticmethod
        def runtime_env():
            return {}

    monkeypatch.setattr(factory_pg, "sql", FakeSql)

    factory_pg.release_global_control_plane_lease("tick-a")

    query = "\n".join(statements)
    assert "UPDATE factory.runtime_leases" in query
    assert "expires_at=now()" in query
    assert "DELETE FROM factory.runtime_leases" not in query

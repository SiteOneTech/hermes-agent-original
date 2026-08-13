"""Regression tests for FRE-025 successor activation and global control lease."""
from __future__ import annotations

from pathlib import Path

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
    assert agent_core_db.MODULES["factory"]["migrations"] == ROOT / "db/modules/factory"
    assert agent_core_db.migration_version(ROOT / "db/modules/factory/000004_successor_control.sql") == "000004"


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

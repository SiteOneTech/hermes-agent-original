"""Regression tests for canonical Factory project continuation/reopen."""
from __future__ import annotations

import json

from hermes_cli import factory_pg


class FakeSql:
    def __init__(self) -> None:
        self.statements: list[str] = []
        self.one_results: list[dict | None] = []
        self.rows_results: list[list[dict]] = []
        self.statement_one_results: list[dict | None] = []
        self.json_query_results: list[list[dict]] = []

    def psql(self, sql, *, user=None, **_):
        self.statements.append(sql)
        return None

    def one(self, sql, *, user=None, **_):
        self.statements.append(sql)
        return self.one_results.pop(0) if self.one_results else None

    def rows(self, sql, *, user=None, **_):
        self.statements.append(sql)
        return self.rows_results.pop(0) if self.rows_results else []

    def statement_one(self, sql, *, user=None, **_):
        self.statements.append(sql)
        return self.statement_one_results.pop(0) if self.statement_one_results else None

    def json_query(self, sql, *, user=None, **_):
        self.statements.append(sql)
        return self.json_query_results.pop(0) if self.json_query_results else []

    @staticmethod
    def quote_literal(value):
        return "NULL" if value is None else "'" + str(value).replace("'", "''") + "'"

    @staticmethod
    def quote_jsonb(value):
        return "'" + json.dumps(value if value is not None else {}, sort_keys=True) + "'::jsonb"

    @staticmethod
    def runtime_env():
        return {"AGENT_DB_NAME": "zeus_agent"}


def _completed_lineage_project(project_id: str = "factory-runtime-evolution") -> dict:
    return {
        "project_id": project_id,
        "name": "Factory Runtime Evolution",
        "status": "completed",
        "autonomous_enabled": False,
        "repo_path": "/repo",
        "base_branch": "main",
        "metadata": {
            "lineage": "factory-runtime-evolution",
            "artifact_dir": "factory/projects/factory-runtime-evolution",
            "repo_strategy": {
                "status": "passed",
                "repo_scope": "zeus_only",
                "work_intent": "maintain_existing_project",
                "primary_repo": "SiteOneTech/hermes-agent-original",
                "primary_repo_path": "/repo",
                "base_branch": "main",
                "branch_prefix": "factory/factory-runtime-evolution/",
                "missing_fields": [],
            },
        },
    }


def test_completed_lineage_project_reopens_to_active_with_gate(monkeypatch):
    fake = FakeSql()
    fake.statement_one_results = [{"gate_id": 777}]
    monkeypatch.setattr(factory_pg, "sql", fake)
    monkeypatch.setattr(factory_pg, "ensure_runtime_schema", lambda: None)
    monkeypatch.setattr(factory_pg, "_project", _completed_lineage_project)
    monkeypatch.setattr(factory_pg, "_g1_document_blockers", lambda project: [])

    result = factory_pg.reopen_project(
        "factory-runtime-evolution",
        reason="Continue Factory runtime control-plane work in the canonical project",
        actor="factory-orchestrator",
    )

    assert result["action"] == "reopen"
    assert result["status"] == "active"
    assert result["gate_id"] == 777
    joined = "\n".join(fake.statements)
    assert "'reopen', 'passed'" in joined
    assert "project_reopened" in joined
    assert "continuation_of" in joined
    assert "autonomous_enabled=true" in joined
    assert "project_created" not in joined


def test_reopen_preflight_fails_closed_on_missing_docs_or_strategy(monkeypatch):
    fake = FakeSql()
    project = _completed_lineage_project()
    project["metadata"]["repo_strategy"] = {"status": "missing", "missing_fields": ["repo_scope"]}
    monkeypatch.setattr(factory_pg, "sql", fake)
    monkeypatch.setattr(factory_pg, "ensure_runtime_schema", lambda: None)
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: project)
    monkeypatch.setattr(factory_pg, "_g1_document_blockers", lambda project: [{"file_name": "PRD.md"}])

    result = factory_pg.reopen_project(
        "factory-runtime-evolution",
        reason="Continue Factory runtime control-plane work in the canonical project",
    )

    assert result["reopen_blocked"] is True
    assert "missing G0 repository strategy" in "; ".join(result["preflight_findings"])
    assert "g1 documentary readiness blockers" in "; ".join(result["preflight_findings"])
    joined = "\n".join(fake.statements)
    assert "project_reopen_preflight_failed" in joined
    assert "autonomous_enabled=true" not in joined
    assert "project_reopened" not in joined


def test_cancelled_project_reopen_requires_jean_approval(monkeypatch):
    fake = FakeSql()
    project = _completed_lineage_project()
    project["status"] = "cancelled"
    monkeypatch.setattr(factory_pg, "sql", fake)
    monkeypatch.setattr(factory_pg, "ensure_runtime_schema", lambda: None)
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: project)
    monkeypatch.setattr(factory_pg, "_g1_document_blockers", lambda project: [])

    result = factory_pg.reopen_project(
        "factory-runtime-evolution",
        reason="Continue Factory runtime control-plane work in the canonical project",
    )

    assert result["reopen_blocked"] is True
    assert "jean_approval_required_for_cancelled_reopen" in result["preflight_findings"]
    joined = "\n".join(fake.statements)
    assert "project_reopen_preflight_failed" in joined
    assert "autonomous_enabled=true" not in joined


def test_project_create_suggests_reopen_instead_of_detached_successor(monkeypatch):
    fake = FakeSql()
    fake.one_results = [{"project_id": "factory-runtime-evolution", "status": "completed", "metadata": {"lineage": "factory-runtime-evolution"}}]
    monkeypatch.setattr(factory_pg, "sql", fake)
    monkeypatch.setattr(factory_pg, "ensure_runtime_schema", lambda: None)

    result = factory_pg.create_project(
        "Factory Runtime Evolution — Continuation",
        project_id="factory-runtime-evolution-continuation",
        repo_scope="zeus_only",
        work_intent="maintain_existing_project",
        create_default_lanes=False,
        metadata={"continuation_of": "factory-runtime-evolution"},
    )

    assert result["suggest"] == "reopen"
    assert result["project_id"] == "factory-runtime-evolution"
    assert result["requested_project_id"] == "factory-runtime-evolution-continuation"
    joined = "\n".join(fake.statements)
    assert "project_created" not in joined
    assert "factory-runtime-evolution-continuation" in joined

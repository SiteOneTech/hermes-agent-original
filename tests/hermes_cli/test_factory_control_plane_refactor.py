"""Regression tests for INC-0001 Factory runtime docs/Notion control-plane refactor."""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

from hermes_cli import factory, factory_catalog, factory_pg


class FakeSql:
    def __init__(self) -> None:
        self.statements: list[str] = []
        self.one_results: list[dict | None] = []
        self.statement_one_results: list[dict | None] = []
        self.rows_results: list[list[dict]] = []

    def psql(self, sql, *, user=None, **_):
        self.statements.append(sql)
        return None

    def one(self, sql, *, user=None, **_):
        self.statements.append(sql)
        return self.one_results.pop(0) if self.one_results else None

    def statement_one(self, sql, *, user=None, **_):
        self.statements.append(sql)
        return self.statement_one_results.pop(0) if self.statement_one_results else None

    def rows(self, sql, *, user=None, **_):
        self.statements.append(sql)
        return self.rows_results.pop(0) if self.rows_results else []

    def json_query(self, sql, *, user=None, **_):
        self.statements.append(sql)
        return []

    @staticmethod
    def quote_literal(value):
        return "NULL" if value is None else "'" + str(value).replace("'", "''") + "'"

    @staticmethod
    def quote_jsonb(value):
        return "'" + json.dumps(value if value is not None else {}, sort_keys=True) + "'::jsonb"

    @staticmethod
    def runtime_env():
        return {"AGENT_DB_NAME": "zeus_agent"}


@pytest.fixture(autouse=True)
def disabled_notion_workflow(monkeypatch):
    monkeypatch.delenv("FACTORY_NOTION_WORKFLOW_ENABLED", raising=False)


@pytest.fixture
def fake_sql(monkeypatch):
    fake = FakeSql()
    monkeypatch.setattr(factory_pg, "sql", fake)
    monkeypatch.setattr(factory_pg, "ensure_runtime_schema", lambda: None)
    monkeypatch.setattr(factory_pg, "reconcile_project", lambda pid: {"project_id": pid, "status": "active"})
    return fake


def test_notion_tracker_schema_validation_rejects_empty_and_bad_input():
    with pytest.raises(ValueError):
        factory_pg._validate_notion_tracker_metadata(page_id=None, url=None)
    with pytest.raises(ValueError):
        factory_pg._validate_notion_tracker_metadata(page_id="not-hex", url=None)
    with pytest.raises(ValueError):
        factory_pg._validate_notion_tracker_metadata(page_id=None, url="ftp://example.com/x")


def test_notion_tracker_schema_validation_accepts_funnel_core_evidence():
    meta = factory_pg._validate_notion_tracker_metadata(
        page_id="37a37b39-cad6-8146-b9f2-e1fdf0bdf727",
        url="https://app.notion.com/p/Funnel-Core-CRM-Sales-Workflow-Factory-PM-37a37b39cad68146b9f2e1fdf0bdf727",
    )
    assert meta["notion_tracker_page_id"] == "37a37b39-cad6-8146-b9f2-e1fdf0bdf727"
    assert meta["notion_tracker_url"].startswith("https://app.notion.com/")


def test_link_notion_tracker_writes_metadata_reads_back_and_audits(fake_sql):
    fake_sql.one_results = [
        {"project_id": "demo", "status": "active", "metadata": {}},
        {"metadata": {
            "notion_tracker_page_id": "37a37b39-cad6-8146-b9f2-e1fdf0bdf727",
            "notion_tracker_url": "https://app.notion.com/p/x-37a37b39cad68146b9f2e1fdf0bdf727",
        }},
    ]
    result = factory_pg.link_notion_tracker(
        "demo",
        page_id="37a37b39-cad6-8146-b9f2-e1fdf0bdf727",
        url="https://app.notion.com/p/x-37a37b39cad68146b9f2e1fdf0bdf727",
        actor="jean",
    )
    assert result["action"] == "link-notion"
    assert result["readback"]["notion_tracker_page_id"] == "37a37b39-cad6-8146-b9f2-e1fdf0bdf727"
    joined = "\n".join(fake_sql.statements)
    assert "notion_tracker_page_id" in joined
    assert "notion_tracker_linked" in joined


def test_link_notion_tracker_raises_on_readback_mismatch(fake_sql):
    fake_sql.one_results = [
        {"project_id": "demo", "status": "active", "metadata": {}},
        {"metadata": {}},
    ]
    with pytest.raises(ValueError, match="readback"):
        factory_pg.link_notion_tracker("demo", page_id="37a37b39cad68146b9f2e1fdf0bdf727", url=None)


def test_missing_notion_is_not_a_factory_reconciliation_blocker_by_default(monkeypatch):
    monkeypatch.setattr(factory_pg, "_project_artifact_dir", lambda project: (None, "factory/projects/funnel-core-crm-workflow"))
    project_missing = {"project_id": "funnel-core-crm-workflow", "status": "active", "metadata": {}}
    findings = factory_pg.reconciliation_findings(project_missing, tasks=[{"task_id": "t1", "status": "todo"}], pending_gates=[])
    codes = {f["code"] for f in findings}
    assert "missing_notion_project" not in codes
    assert "notion_pm_projection_warning" not in codes


def test_missing_notion_is_not_blocking_even_when_legacy_required_flag_is_set(monkeypatch):
    monkeypatch.setattr(factory_pg, "_project_artifact_dir", lambda project: (None, "factory/projects/funnel-core-crm-workflow"))
    project_missing = {"project_id": "funnel-core-crm-workflow", "status": "active", "metadata": {"notion_required": True}}
    findings = factory_pg.reconciliation_findings(project_missing, tasks=[{"task_id": "t1", "status": "todo"}], pending_gates=[])
    codes = {f["code"] for f in findings}
    assert "missing_notion_project" not in codes
    assert "notion_pm_projection_warning" not in codes


def test_notion_required_string_false_remains_non_blocking(monkeypatch):
    monkeypatch.setattr(factory_pg, "_project_artifact_dir", lambda project: (None, "factory/projects/funnel-core-crm-workflow"))
    project_missing = {"project_id": "funnel-core-crm-workflow", "status": "active", "metadata": {"notion_required": "false"}}
    findings = factory_pg.reconciliation_findings(project_missing, tasks=[{"task_id": "t1", "status": "todo"}], pending_gates=[])
    codes = {f["code"] for f in findings}
    assert "missing_notion_project" not in codes
    assert "notion_pm_projection_warning" not in codes


def test_stale_notion_string_false_is_not_treated_as_stale(monkeypatch):
    monkeypatch.setattr(factory_pg, "_project_artifact_dir", lambda project: (None, "factory/projects/funnel-core-crm-workflow"))
    project_linked = {
        "project_id": "funnel-core-crm-workflow",
        "status": "active",
        "metadata": {
            "notion_tracker_page_id": "37a37b39-cad6-8146-b9f2-e1fdf0bdf727",
            "notion_projection_stale": "false",
        },
    }
    findings = factory_pg.reconciliation_findings(project_linked, tasks=[{"task_id": "t1", "status": "todo"}], pending_gates=[])
    assert not any(f["code"] in {"missing_notion_project", "notion_pm_projection_warning"} for f in findings)


def test_legacy_missing_notion_blocker_resolves_when_workflow_disabled():
    project = {"project_id": "demo", "status": "active", "metadata": {}}
    task = {
        "task_id": "demo-missing-notion",
        "status": "blocked",
        "metadata": {"reconciliation_anomaly": "missing_notion_project"},
    }
    assert factory_pg._resolved_reconciliation_anomaly(project, task) == ("missing_notion_project", "structured_reconciliation_metadata")


def test_legacy_projection_warning_resolves_because_missing_notion_is_now_required():
    project = {"project_id": "demo", "status": "active", "metadata": {}}
    task = {
        "task_id": "demo-notion-warning",
        "status": "blocked",
        "metadata": {"reconciliation_anomaly": "notion_pm_projection_warning"},
    }
    assert factory_pg._resolved_reconciliation_anomaly(project, task) == ("notion_pm_projection_warning", "structured_reconciliation_metadata")


def test_notion_projection_warning_task_does_not_cover_required_notion_blocker():
    task = {
        "task_id": "demo-reconcile-notion-pm-projection-warning",
        "title": "PM — Projection warning: update Factory Notion reporting surface",
        "description": "Missing or stale Notion PM projection is reported for executive visibility.",
        "phase": "reporting",
        "status": "todo",
    }
    assert factory_pg._task_covers_reconciliation_anomaly(task, "notion_pm_projection_warning") is True
    assert factory_pg._task_covers_reconciliation_anomaly(task, "missing_notion_project") is False


def test_stale_notion_metadata_is_not_a_factory_reconciliation_blocker(monkeypatch):
    monkeypatch.setattr(factory_pg, "_project_artifact_dir", lambda project: (None, "factory/projects/funnel-core-crm-workflow"))
    project_stale = {
        "project_id": "funnel-core-crm-workflow",
        "status": "active",
        "metadata": {
            "notion_tracker_page_id": "37a37b39-cad6-8146-b9f2-e1fdf0bdf727",
            "notion_projection_stale": True,
        },
    }
    findings = factory_pg.reconciliation_findings(project_stale, tasks=[{"task_id": "t1", "status": "todo"}], pending_gates=[])
    assert not any(f["code"] == "missing_notion_project" for f in findings)


def test_linked_notion_metadata_satisfies_reconciler_for_funnel_core(monkeypatch):
    monkeypatch.setattr(factory_pg, "_project_artifact_dir", lambda project: (None, "factory/projects/funnel-core-crm-workflow"))
    project_linked = {
        "project_id": "funnel-core-crm-workflow",
        "status": "active",
        "metadata": {
            "notion_tracker_page_id": "37a37b39-cad6-8146-b9f2-e1fdf0bdf727",
            "notion_tracker_url": "https://app.notion.com/p/x-37a37b39cad68146b9f2e1fdf0bdf727",
        },
    }
    findings_linked = factory_pg.reconciliation_findings(project_linked, tasks=[{"task_id": "t1", "status": "todo"}], pending_gates=[])
    assert not any(f["code"] in {"missing_notion_project", "notion_pm_projection_warning"} for f in findings_linked)


def test_critical_readiness_ignores_missing_notion_while_workflow_disabled(fake_sql, monkeypatch, tmp_path):
    factory_dir = tmp_path / "factory" / "projects" / "demo"
    factory_dir.mkdir(parents=True)
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: {
        "project_id": project_id,
        "repo_path": str(tmp_path),
        "risk_level": "high",
        "metadata": {
            "artifact_dir": "factory/projects/demo",
            "repo_strategy": {
                "repo_scope": "zeus_only",
                "work_intent": "maintain_existing_project",
                "primary_repo": "/repo",
                "base_branch": "main",
                "branch_prefix": "factory/demo",
            },
            "required_docs_waived": True,
            "required_docs_waived_authorized_by": "Jean",
            "required_docs_waived_reason": "unit test isolates Notion gate semantics",
            "repo_commit_waived": True,
            "repo_commit_waived_authorized_by": "Jean",
            "repo_commit_waived_reason": "unit test isolates Notion gate semantics",
        },
    })
    fake_sql.rows_results = [[]]
    assert not any("Notion" in finding for finding in factory_pg.critical_readiness_findings("demo"))


def test_critical_readiness_ignores_missing_notion_even_when_required_flag_is_set(fake_sql, monkeypatch, tmp_path):
    factory_dir = tmp_path / "factory" / "projects" / "demo"
    factory_dir.mkdir(parents=True)
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: {
        "project_id": project_id,
        "repo_path": str(tmp_path),
        "risk_level": "high",
        "metadata": {
            "artifact_dir": "factory/projects/demo",
            "notion_required": True,
            "repo_strategy": {
                "repo_scope": "zeus_only",
                "work_intent": "maintain_existing_project",
                "primary_repo": "/repo",
                "base_branch": "main",
                "branch_prefix": "factory/demo",
            },
            "required_docs_waived": True,
            "required_docs_waived_authorized_by": "Jean",
            "required_docs_waived_reason": "unit test isolates Notion gate semantics",
            "repo_commit_waived": True,
            "repo_commit_waived_authorized_by": "Jean",
            "repo_commit_waived_reason": "unit test isolates Notion gate semantics",
        },
    })
    fake_sql.rows_results = [[]]
    assert not any("Notion" in finding for finding in factory_pg.critical_readiness_findings("demo"))


def _commit_factory_docs(repo):
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "factory@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Factory Test"], cwd=repo, check=True)
    subprocess.run(["git", "add", "factory"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "docs"], cwd=repo, check=True, capture_output=True, text=True)


def test_cli_link_notion_uses_backend(monkeypatch, capsys):
    calls = {}

    class FakeBackend:
        @staticmethod
        def link_notion_tracker(project_id, **kwargs):
            calls["project_id"] = project_id
            calls["kwargs"] = kwargs
            return {"action": "link-notion", "project_id": project_id, "readback": kwargs}

    monkeypatch.setattr("hermes_cli.factory_backend.get_backend", lambda: FakeBackend)
    args = argparse.Namespace(
        project_id="demo",
        page_id="37a37b39cad68146b9f2e1fdf0bdf727",
        url="https://app.notion.com/p/x",
        page_title="Demo PM",
        actor="jean",
        json=True,
    )
    assert factory.cmd_project_link_notion(args) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["project_id"] == "demo"
    assert calls["kwargs"]["page_id"] == "37a37b39cad68146b9f2e1fdf0bdf727"


def test_dispatch_preflight_blocks_product_execution_without_docs():
    cases = [
        {"task_id": "demo-impl", "phase": "implementation", "status": "todo", "metadata": {}},
        {"task_id": "demo-qa", "phase": "qa-security", "title": "Tests Playwright QA and security review", "status": "todo", "metadata": {}},
        {"task_id": "demo-deploy", "phase": "delivery", "title": "Sandbox deployment on Kidu", "status": "todo", "metadata": {}},
        {"task_id": "demo-report", "phase": "delivery-report", "title": "Delivery report", "status": "todo", "metadata": {}},
    ]
    for task in cases:
        blockers = factory_pg._dispatch_preflight_blockers(task, docs_ready=False, notion_ready=False)
        assert "missing_or_unindexed_docs" in blockers, task
        assert "missing_notion_tracker" not in blockers


def test_dispatch_preflight_allows_g1_document_tasks_to_repair_docs():
    task = {"task_id": "demo-g1-prd", "phase": "G1-product", "title": "Product requirements", "status": "todo", "metadata": {}}
    assert factory_pg._dispatch_preflight_blockers(task, docs_ready=False, notion_ready=False) == []


def test_dispatch_preflight_does_not_block_on_notion_by_default():
    task = {"task_id": "demo-impl", "phase": "implementation", "status": "todo", "metadata": {}}
    assert factory_pg._dispatch_preflight_blockers(task, docs_ready=True, notion_ready=False, notion_required=False) == []
    assert factory_pg._dispatch_preflight_blockers(task, docs_ready=True, notion_ready=False, notion_required=True) == []


def test_dispatch_preflight_allows_when_docs_and_notion_ready():
    task = {"task_id": "demo-impl", "phase": "implementation", "status": "todo", "metadata": {}}
    assert factory_pg._dispatch_preflight_blockers(task, docs_ready=True, notion_ready=True) == []


def test_document_status_distinguishes_g1_lifecycle_and_pm_projection(tmp_path):
    factory_dir = tmp_path / "factory" / "projects" / "demo"
    factory_dir.mkdir(parents=True)
    for name in factory_pg.G1_BLOCKING_DOCUMENTS:
        (factory_dir / name).write_text(f"# {name}\nvalidated: yes\nreviewed: yes\n", encoding="utf-8")
    (factory_dir / "QA_REPORT.md").write_text("# QA\n", encoding="utf-8")
    (factory_dir / "NOTION_UPDATE.md").write_text("# Notion\n", encoding="utf-8")
    index_text = "\n".join(
        f"- `{name}` — status: validated; reviewed by factory-orchestrator" for name in factory_pg.G1_BLOCKING_DOCUMENTS
    )
    index_text += "\n- `QA_REPORT.md` — lifecycle report\n- `NOTION_UPDATE.md` — PM projection\n"
    (factory_dir / "DOCUMENTATION_INDEX.md").write_text(index_text, encoding="utf-8")
    _commit_factory_docs(tmp_path)

    statuses = factory_pg.project_document_status(
        {"project_id": "demo", "repo_path": str(tmp_path), "metadata": {"artifact_dir": "factory/projects/demo"}}
    )

    by_name = {row["file_name"]: row for row in statuses}
    assert by_name["PRD.md"]["category"] == "g1_required"
    assert by_name["PRD.md"]["blocking"] is False
    assert by_name["QA_REPORT.md"]["category"] == "lifecycle"
    assert by_name["QA_REPORT.md"]["blocking"] is False
    assert by_name["NOTION_UPDATE.md"]["category"] == "pm_projection"
    assert by_name["NOTION_UPDATE.md"]["blocking"] is False


def test_document_status_detects_missing_from_index_as_g1_blocker(tmp_path):
    factory_dir = tmp_path / "factory" / "projects" / "demo"
    factory_dir.mkdir(parents=True)
    for name in factory_pg.G1_BLOCKING_DOCUMENTS:
        (factory_dir / name).write_text(f"# {name}\nvalidated: yes\nreviewed: yes\n", encoding="utf-8")
    (factory_dir / "DOCUMENTATION_INDEX.md").write_text("- `DOCUMENTATION_INDEX.md` — validated; reviewed\n", encoding="utf-8")
    _commit_factory_docs(tmp_path)

    statuses = factory_pg.project_document_status(
        {"project_id": "demo", "repo_path": str(tmp_path), "metadata": {"artifact_dir": "factory/projects/demo"}}
    )
    prd = next(row for row in statuses if row["file_name"] == "PRD.md")
    assert prd["exists"] is True
    assert prd["indexed"] is False
    assert prd["blocking"] is True


def test_document_status_marks_uncommitted_g1_doc_blocking(tmp_path):
    repo = tmp_path
    factory_dir = repo / "factory" / "projects" / "demo"
    factory_dir.mkdir(parents=True)
    for name in factory_pg.G1_BLOCKING_DOCUMENTS:
        (factory_dir / name).write_text(f"# {name}\nvalidated: yes\nreviewed: yes\n", encoding="utf-8")
    (factory_dir / "DOCUMENTATION_INDEX.md").write_text(
        "\n".join(f"- `{name}` — validated; reviewed" for name in factory_pg.G1_BLOCKING_DOCUMENTS),
        encoding="utf-8",
    )
    _commit_factory_docs(repo)
    (factory_dir / "PRD.md").write_text("# PRD\nvalidated: yes\nreviewed: yes\nchanged\n", encoding="utf-8")

    statuses = factory_pg.project_document_status(
        {"project_id": "demo", "repo_path": str(repo), "metadata": {"artifact_dir": "factory/projects/demo"}}
    )
    prd = next(row for row in statuses if row["file_name"] == "PRD.md")
    assert prd["committed"] is False
    assert prd["blocking"] is True


def test_document_status_marks_missing_g1_file_blocking(tmp_path):
    factory_dir = tmp_path / "factory" / "projects" / "demo"
    factory_dir.mkdir(parents=True)
    (factory_dir / "DOCUMENTATION_INDEX.md").write_text(
        "\n".join(f"- `{name}` — status: validated; reviewed by qa" for name in factory_pg.G1_BLOCKING_DOCUMENTS),
        encoding="utf-8",
    )
    _commit_factory_docs(tmp_path)

    statuses = factory_pg.project_document_status(
        {"project_id": "demo", "repo_path": str(tmp_path), "metadata": {"artifact_dir": "factory/projects/demo"}}
    )
    prd = next(row for row in statuses if row["file_name"] == "PRD.md")
    assert prd["exists"] is False
    assert prd["blocking"] is True


def test_document_status_does_not_treat_negated_review_words_as_reviewed(tmp_path):
    factory_dir = tmp_path / "factory" / "projects" / "demo"
    factory_dir.mkdir(parents=True)
    for name in factory_pg.G1_BLOCKING_DOCUMENTS:
        (factory_dir / name).write_text(f"# {name}\nvalidated: yes\nnot reviewed yet\n", encoding="utf-8")
    (factory_dir / "DOCUMENTATION_INDEX.md").write_text(
        "\n".join(f"- `{name}` — validated: yes; not reviewed yet" for name in factory_pg.G1_BLOCKING_DOCUMENTS),
        encoding="utf-8",
    )
    _commit_factory_docs(tmp_path)

    statuses = factory_pg.project_document_status(
        {"project_id": "demo", "repo_path": str(tmp_path), "metadata": {"artifact_dir": "factory/projects/demo"}}
    )
    prd = next(row for row in statuses if row["file_name"] == "PRD.md")
    assert prd["validated"] is True
    assert prd["reviewed"] is False
    assert prd["blocking"] is True


def test_reconciler_creates_task_for_unvalidated_required_docs(tmp_path):
    factory_dir = tmp_path / "factory" / "projects" / "demo"
    factory_dir.mkdir(parents=True)
    for name in factory_pg.G1_BLOCKING_DOCUMENTS:
        (factory_dir / name).write_text(f"# {name}\nvalidated: yes\nnot reviewed yet\n", encoding="utf-8")
    (factory_dir / "DOCUMENTATION_INDEX.md").write_text(
        "\n".join(f"- `{name}` — validated: yes; not reviewed yet" for name in factory_pg.G1_BLOCKING_DOCUMENTS),
        encoding="utf-8",
    )
    _commit_factory_docs(tmp_path)
    project = {"project_id": "demo", "repo_path": str(tmp_path), "metadata": {"artifact_dir": "factory/projects/demo"}}

    findings = factory_pg.reconciliation_findings(project, tasks=[{"task_id": "demo-t1", "status": "todo"}], pending_gates=[])

    finding = next(row for row in findings if row["code"] == "unvalidated_required_docs")
    assert "PRD.md" in finding["metadata"]["blocking_documents"]


def test_status_payload_includes_document_status(fake_sql, monkeypatch):
    fake_sql.rows_results = [
        [{"project_id": "demo", "status": "active", "repo_path": None, "metadata": {}}],
        [], [], [], [], [], [], [], [],
    ]
    monkeypatch.setattr(factory_pg, "list_agents", lambda: [])
    monkeypatch.setattr(factory_pg, "factory_watchdog_alerts", lambda payload, project_id=None: [])
    monkeypatch.setattr(factory_pg, "project_document_status", lambda project: [{"file_name": "PRD.md", "category": "g1_required"}])

    payload = factory_pg.status("demo")
    assert payload["projects"][0]["document_status"] == [{"file_name": "PRD.md", "category": "g1_required"}]


def test_record_delivery_gate_persists_document_status_snapshot(fake_sql, monkeypatch):
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: {"project_id": project_id, "risk_level": "medium", "repo_path": None, "metadata": {}})
    monkeypatch.setattr(factory_pg, "project_document_status", lambda project: [
        {"file_name": "PRD.md", "category": "g1_required", "blocking": False},
        {"file_name": "QA_REPORT.md", "category": "lifecycle", "blocking": False},
    ])
    fake_sql.statement_one_results = [{"gate_id": 42, "project_id": "demo", "status": "passed", "timestamp": "now"}]

    result = factory_pg.record_gate("demo", "delivery", "passed", reviewer="qa", evidence={"tests": "passed"})

    assert result["gate_id"] == 42
    joined = "\n".join(fake_sql.statements)
    assert "document_status_snapshot" in joined
    assert "blocking_count" in joined
    assert "PRD.md" in joined


def test_factory_catalog_assigns_common_operating_canon_to_all_agents():
    for agent in factory_catalog.FACTORY_AGENTS:
        skills = agent[5]
        assert skills[0] == factory_catalog.FACTORY_CANONICAL_SKILL


def test_orchestrator_prompt_injects_g1_docs_and_common_skill():
    script = Path(__file__).resolve().parents[2] / "scripts" / "factory" / "factory_orchestrator_tick.py"
    spec = importlib.util.spec_from_file_location("factory_orchestrator_tick_test", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    payload = {
        "projects": [{
            "project_id": "demo",
            "name": "Demo",
            "repo_path": "/repo",
            "metadata": {"artifact_dir": "factory/projects/demo"},
            "document_status": [
                {"file_name": "DOCUMENTATION_INDEX.md", "path": "factory/projects/demo/DOCUMENTATION_INDEX.md", "category": "g1_required", "blocking": False, "exists": True, "indexed": True, "committed": True, "validated": True, "reviewed": True},
                {"file_name": "PRD.md", "path": "factory/projects/demo/PRD.md", "category": "g1_required", "blocking": False, "exists": True, "indexed": True, "committed": True, "validated": True, "reviewed": True},
            ],
        }],
        "tasks": [],
        "gates": [],
    }
    claim = {"run_id": "run-1", "run_type": "implementation", "task": {"project_id": "demo", "task_id": "t1", "title": "Implement", "phase": "implementation", "engine": "codex", "worktree_path": "/repo/.worktrees/demo/t1"}}

    prompt = module._task_prompt(payload, claim)

    assert "factory-agent-operating-canon" in prompt
    assert "DOCUMENTATION_INDEX.md" in prompt
    assert "G1 readiness" in prompt
    assert "/repo/.worktrees/demo/t1/factory/projects/demo/PRD.md" in prompt


def test_orchestrator_prompt_injects_ui_sandbox_delivery_contract():
    script = Path(__file__).resolve().parents[2] / "scripts" / "factory" / "factory_orchestrator_tick.py"
    spec = importlib.util.spec_from_file_location("factory_orchestrator_tick_ui_contract_test", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    payload = {
        "projects": [{
            "project_id": "demo",
            "name": "Demo UI",
            "repo_path": "/repo",
            "metadata": {"artifact_dir": "factory/projects/demo", "ui_deliverable": True, "delivery_target": "sandbox"},
            "document_status": [],
        }],
        "tasks": [],
        "gates": [],
    }
    claim = {"run_id": "run-1", "run_type": "implementation", "task": {"project_id": "demo", "task_id": "t1", "title": "QA UI", "phase": "qa", "owner_profile": "qa-verifier", "engine": "zeus", "worktree_path": "/repo/.worktrees/demo/t1"}}

    prompt = module._task_prompt(payload, claim)

    assert "Factory entrega en sandbox funcional" in prompt
    assert "kidu.app" in prompt
    assert "Playwright o browser smoke" in prompt
    assert "desktop screenshot" in prompt
    assert "mobile screenshot" in prompt
    assert "console_error_check" in prompt
    assert "QA_REPORT.md" in prompt
    assert "contexto de DB no confiable" in prompt


def test_dispatch_preflight_exempts_reconciliation_tasks():
    task = {"task_id": "demo-reconcile-missing-notion-project", "phase": "documentation", "status": "todo",
            "metadata": {"factory_reconciliation_task": True, "reconciliation_anomaly": "missing_notion_project"}}
    assert factory_pg._dispatch_preflight_blockers(task, docs_ready=False, notion_ready=False) == []


def test_dispatch_preflight_exempts_control_plane_bootstrap_repair():
    task = {"task_id": "inc-0001-control-plane", "phase": "implementation", "status": "todo",
            "metadata": {"control_plane_bootstrap": True}}
    assert factory_pg._dispatch_preflight_blockers(task, docs_ready=False, notion_ready=False) == []


def test_dispatch_preflight_respects_explicit_jean_waiver():
    task = {"task_id": "demo-impl", "phase": "implementation", "status": "todo", "metadata": {}}
    assert factory_pg._dispatch_preflight_blockers(task, docs_ready=False, notion_ready=False, docs_first_waived=True) == []


def test_dispatch_docs_first_waived_requires_authorizer_and_reason():
    assert factory_pg._dispatch_docs_first_waived({"docs_first_dispatch_waived": True}) is False
    assert factory_pg._dispatch_docs_first_waived({
        "docs_first_dispatch_waived": True,
        "docs_first_dispatch_waived_authorized_by": "Jean",
        "docs_first_dispatch_waived_reason": "runtime bootstrap repair",
    }) is True


def test_resume_preflight_blocks_blocked_project_without_runnable_work():
    preflight = {
        "status": "blocked",
        "task_counts": {
            "blocked": 3,
            "done": 40,
        },
    }

    assert factory_pg._resume_preflight_blocker(preflight) == "blocked_without_runnable_work"


def test_resume_preflight_blocks_paused_project_with_only_blocked_work():
    preflight = {
        "status": "paused",
        "task_counts": {
            "blocked": 3,
            "done": 40,
        },
    }

    assert factory_pg._resume_preflight_blocker(preflight) == "blocked_without_runnable_work"


def test_resume_preflight_allows_blocked_project_with_runnable_rework():
    preflight = {
        "status": "blocked",
        "task_counts": {
            "blocked": 1,
            "rework": 1,
        },
    }

    assert factory_pg._resume_preflight_blocker(preflight) is None


def test_supervisor_requeues_technical_blocker_before_manual_attention(fake_sql, monkeypatch):
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: {
        "project_id": project_id,
        "status": "blocked",
        "autonomous_enabled": True,
        "metadata": {"autonomous_enabled": True},
    })
    monkeypatch.setattr(factory_pg, "_tasks", lambda project_id: [
        {
            "project_id": project_id,
            "lane_id": "demo-lane",
            "task_id": "demo-blocked-tech",
            "title": "Fix failing UI QA",
            "status": "blocked",
            "retry_count": 0,
            "result_summary": "STATE: BLOCKED — tests failed with regression",
            "metadata": {},
        }
    ])
    fake_sql.rows_results = [[], []]

    result = factory_pg.supervisor_health_check("demo", repair=True)

    assert result["health"] == "yellow"
    assert result["violations"][0]["invariant"] == "RED_AUTONOMOUS_WITHOUT_RUNNABLE_WORK_OR_QUESTION"
    assert any(repair["operation"] == "supervisor_requeue_technical_blockers" for repair in result["repairs"])
    joined = "\n".join(fake_sql.statements)
    assert "SET status='rework'" in joined
    assert "manual_attention" not in joined


def test_supervisor_moves_exhausted_blocker_to_manual_attention(fake_sql, monkeypatch):
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: {
        "project_id": project_id,
        "status": "blocked",
        "autonomous_enabled": True,
        "metadata": {"autonomous_enabled": True},
    })
    monkeypatch.setattr(factory_pg, "_tasks", lambda project_id: [
        {
            "project_id": project_id,
            "lane_id": "demo-lane",
            "task_id": "demo-blocked-tech",
            "title": "Fix failing UI QA",
            "status": "blocked",
            "retry_count": factory_pg.SUPERVISOR_TECHNICAL_REWORK_MAX_RETRIES,
            "result_summary": "STATE: BLOCKED — repeated regression after rework",
            "metadata": {},
        }
    ])
    fake_sql.rows_results = [[], []]

    result = factory_pg.supervisor_health_check("demo", repair=True)

    assert result["health"] == "yellow"
    assert any(repair["operation"] == "mark_project_manual_attention" for repair in result["repairs"])
    joined = "\n".join(fake_sql.statements)
    assert "status='manual_attention'" in joined
    assert "autonomous_enabled=false" in joined


def test_supervisor_moves_existing_human_question_to_manual_attention(fake_sql, monkeypatch):
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: {
        "project_id": project_id,
        "status": "blocked",
        "autonomous_enabled": True,
        "metadata": {"autonomous_enabled": True},
    })
    monkeypatch.setattr(factory_pg, "_tasks", lambda project_id: [
        {
            "project_id": project_id,
            "lane_id": "demo-lane",
            "task_id": "demo-blocked-human",
            "title": "Needs owner decision",
            "status": "blocked",
            "retry_count": 0,
            "result_summary": "STATE: BLOCKED — owner decision required",
            "metadata": {},
        }
    ])
    fake_sql.rows_results = [[], [{"question_id": "hq-demo", "task_id": "demo-blocked-human", "status": "pending"}], []]

    result = factory_pg.supervisor_health_check("demo", repair=True)

    assert result["health"] == "yellow"
    assert any(repair["operation"] == "mark_project_manual_attention" for repair in result["repairs"])
    joined = "\n".join(fake_sql.statements)
    assert "status='manual_attention'" in joined
    assert "autonomous_enabled=false" in joined
    assert "pending_human_question" in joined
    assert "SET status='rework'" not in joined


def test_terminal_and_manual_attention_statuses_disable_autonomy():
    assert factory_pg._project_status_forces_autonomy_off("completed") is True
    assert factory_pg._project_status_forces_autonomy_off("accepted") is True
    assert factory_pg._project_status_forces_autonomy_off("manual_attention") is True
    assert factory_pg._project_status_forces_autonomy_off("active") is False
    assert factory_pg._project_reconcile_forces_autonomy_off("completed", "active") is True
    assert factory_pg._project_reconcile_forces_autonomy_off("active", "completed") is True
    assert factory_pg._project_reconcile_forces_autonomy_off("active", "blocked") is False


def test_resume_preflight_allows_manual_attention_only_with_runnable_work():
    assert factory_pg._resume_preflight_blocker({
        "status": "manual_attention",
        "task_counts": {"rework": 1},
    }) is None
    assert factory_pg._resume_preflight_blocker({
        "status": "manual_attention",
        "task_counts": {"blocked": 1},
    }) == "manual_attention_without_runnable_work"


def test_auto_resume_only_fires_on_new_completion_transition():
    assert factory_pg._should_auto_resume_after_reconcile("active", "completed") is True
    assert factory_pg._should_auto_resume_after_reconcile("blocked", "completed") is True
    assert factory_pg._should_auto_resume_after_reconcile("completed", "completed") is False
    assert factory_pg._should_auto_resume_after_reconcile("paused", "active") is False


def test_reconcile_preserves_manual_attention_and_forces_autonomy_off(monkeypatch):
    fake = FakeSql()
    monkeypatch.setattr(factory_pg, "sql", fake)
    monkeypatch.setattr(factory_pg, "ensure_runtime_schema", lambda: None)
    monkeypatch.setattr(factory_pg, "_tasks", lambda project_id: [
        {"project_id": project_id, "task_id": "demo-blocked", "status": "blocked"}
    ])
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: {
        "project_id": project_id,
        "status": "manual_attention",
        "autonomous_enabled": True,
        "paused_at": "2026-06-17T00:00:00Z",
        "metadata": {"manual_attention_required": True, "autonomous_enabled": True},
    })
    monkeypatch.setattr(factory_pg, "_active_pending_gates", lambda project_id: [])
    monkeypatch.setattr(factory_pg, "_latest_gate_rows", lambda project_id: [])
    monkeypatch.setattr(factory_pg, "reconciliation_findings", lambda project, tasks, pending, gates: [])
    monkeypatch.setattr(factory_pg, "ensure_reconciliation_tasks", lambda project, findings, tasks: [])
    monkeypatch.setattr(factory_pg, "cancel_resolved_reconciliation_tasks", lambda project, findings, tasks: [])
    fake.rows_results = [[]]

    result = factory_pg.reconcile_project("demo")

    assert result["status"] == "manual_attention"
    joined = "\n".join(fake.statements)
    assert "status='manual_attention'" in joined
    assert "autonomous_enabled=false" in joined
    assert "project_status_manual_attention" in joined


def test_close_project_cancels_active_runs_and_records_monitor_evidence(fake_sql):
    fake_sql.rows_results = [[{"run_id": "run-1"}, {"run_id": "run-2"}]]
    fake_sql.statement_one_results = [{"gate_id": 99}]
    result = factory_pg.close_project("demo", reason="superseded by refactor", closure_type="superseded")
    assert result["status"] in {"completed", "cancelled"}
    joined = "\n".join(fake_sql.statements)
    assert "factory.task_runs" in joined
    assert "'cancelled'" in joined
    assert "stale_task_runs_cancelled" in joined
    assert "monitor_evidence" in joined


def test_close_task_does_not_queue_notion_increment_checkpoint_when_workflow_disabled(fake_sql):
    fake_sql.statement_one_results = [
        {"project_id": "demo", "lane_id": "lane-1", "task_id": "demo-inc-0001", "status": "done"}
    ]

    result = factory_pg.close_task(
        "demo-inc-0001",
        status="done",
        result_summary="Implemented the first production increment.",
        evidence={"commit": "abc123", "tests": "passed"},
        actor="codex-builder",
        reconcile=False,
    )

    assert result["notion_post_action"]["disabled"] is True
    assert result["notion_post_action"]["notion_sync_required"] is False
    joined = "\n".join(fake_sql.statements)
    assert "task_closed" in joined
    assert "notion_increment_closure_checkpoint" not in joined
    assert "human_pm_projection_not_agent_truth" not in joined
    assert '"notion_workflow_disabled": true' in joined
    assert '"notion_sync_required": false' in joined


def test_close_task_keeps_notion_disabled_even_for_legacy_notion_reconciliation_task(fake_sql):
    fake_sql.statement_one_results = [
        {
            "project_id": "demo",
            "lane_id": "lane-1",
            "task_id": "demo-reconcile-missing-notion-project",
            "status": "done",
        }
    ]

    result = factory_pg.close_task(
        "demo-reconcile-missing-notion-project",
        status="done",
        result_summary="Legacy Notion PM projection task closed after workflow was disabled.",
        evidence={"notion_sync_completed": True, "notion_tracker_page_id": "37e37b39-cad6-812e-a750-f19285329717"},
        actor="factory-reporter",
        reconcile=False,
    )

    assert result["notion_post_action"]["disabled"] is True
    joined = "\n".join(fake_sql.statements)
    assert '"notion_projection_stale": false' in joined
    assert '"notion_sync_required": false' in joined
    assert "notion_increment_closure_checkpoint" not in joined
    assert "notion_increment_closure_synced" not in joined


def test_factory_notion_markdown_includes_sequential_post_action_increment_closures():
    from hermes_cli import web_server

    project = {
        "project_id": "demo",
        "name": "Demo Factory Project",
        "status": "active",
        "methodology": "hybrid",
        "risk_level": "medium",
        "repo_path": "/repo/demo",
        "base_branch": "main",
        "metadata": {"artifact_dir": "factory/projects/demo"},
        "dashboard": {"quick_status": "Dos incrementos cerrados.", "required_docs": []},
    }
    payload = {
        "tasks": [
            {
                "project_id": "demo",
                "task_id": "demo-inc-0002",
                "title": "Second increment",
                "status": "done",
                "owner_profile": "claude-code-builder",
                "priority": 20,
                "increment_key": "INC-0002",
                "increment_order": 2,
                "result_summary": "Second increment delivered.",
                "evidence_status": "present",
                "finished_at": "2026-06-13T11:00:00Z",
                "metadata": {"closure_source": "factory_task_close", "evidence": {"commit": "def456"}},
            },
            {
                "project_id": "demo",
                "task_id": "demo-inc-0001",
                "title": "First increment",
                "status": "done",
                "owner_profile": "codex-builder",
                "priority": 10,
                "increment_key": "INC-0001",
                "increment_order": 1,
                "result_summary": "First increment delivered.",
                "evidence_status": "present",
                "finished_at": "2026-06-13T10:00:00Z",
                "metadata": {"closure_source": "factory_task_close", "evidence": {"commit": "abc123"}},
            },
        ],
        "gates": [],
        "events": [],
        "task_runs": [],
    }

    markdown = web_server._factory_notion_markdown(payload, project)

    assert "## 7. Cierres secuenciales de incrementos" in markdown
    assert "post-acción" in markdown
    assert markdown.index("INC-0001") < markdown.index("INC-0002")
    assert "First increment delivered." in markdown
    assert "Second increment delivered." in markdown
    assert "Fuente operativa: **Agent Core Postgres `factory.*`**" in markdown


def test_factory_notion_blocks_do_not_truncate_late_increment_closure_section():
    from hermes_cli import web_server

    markdown = "\n".join(
        [f"prelude line {idx}" for idx in range(120)]
        + [
            "## 7. Cierres secuenciales de incrementos",
            "Cada cierre se registra post-acción.",
            "| 1 | INC-0001 | First increment | done | commit=abc123 |",
        ]
    )
    blocks = web_server._factory_notion_blocks(markdown)
    rendered_parts = []
    for block in blocks:
        block_type = block.get("type")
        if not isinstance(block_type, str):
            continue
        rich_text = block.get(block_type, {}).get("rich_text", [])
        rendered_parts.append(
            "".join(chunk.get("plain_text") or chunk.get("text", {}).get("content", "") for chunk in rich_text)
        )
    rendered = "\n".join(rendered_parts)

    assert "Cierres secuenciales de incrementos" in rendered
    assert "INC-0001" in rendered


def test_final_semantic_state_ignores_historical_markers():
    text = "prompt context: previous run said STATE: BLOCKED\n...work...\nFINAL: STATE: DONE"
    assert factory_pg._final_semantic_state(text) == "done"


def test_final_semantic_state_detects_ambiguous_in_progress():
    text = "...lots of work...\nSTATE: IN_PROGRESS"
    assert factory_pg._final_semantic_state(text) == "in_progress"


def test_effective_exit_code_treats_final_in_progress_as_failure():
    assert factory_pg._effective_exit_code(0, "work\nSTATE: IN_PROGRESS") != 0


def test_effective_exit_code_final_done_overrides_nonzero_exit():
    assert factory_pg._effective_exit_code(1, "STATE: BLOCKED earlier\nSTATE: DONE") == 0


def test_effective_exit_code_final_blocked_forces_failure():
    assert factory_pg._effective_exit_code(0, "STATE: DONE earlier\nSTATE: BLOCKED") != 0

def _ui_project(tmp_path=None):
    metadata = {
        "ui_deliverable": True,
        "runnable_deliverable": True,
        "delivery_target": "sandbox",
        "notion_tracker_page_id": "37a37b39-cad6-8146-b9f2-e1fdf0bdf727",
        "repo_strategy": {
            "repo_scope": "zeus_only",
            "work_intent": "maintain_existing_project",
            "primary_repo": "/repo",
            "base_branch": "main",
            "branch_prefix": "factory/demo",
        },
        "required_docs_waived": True,
        "required_docs_waived_authorized_by": "Jean",
        "required_docs_waived_reason": "unit test isolates UI delivery contract",
        "repo_commit_waived": True,
        "repo_commit_waived_authorized_by": "Jean",
        "repo_commit_waived_reason": "unit test isolates UI delivery contract",
    }
    if tmp_path is not None:
        metadata["artifact_dir"] = "factory/projects/demo"
    return {
        "project_id": "demo",
        "repo_path": str(tmp_path) if tmp_path is not None else "/repo",
        "risk_level": "medium",
        "metadata": metadata,
    }


def _complete_ui_delivery_evidence():
    return {
        "sandbox_url": "https://demo.kidu.app/",
        "sandbox_deploy_path": "/srv/factory/projects/demo",
        "docker_compose_path": "/srv/factory/projects/demo/docker-compose.yml",
        "health_url": "https://demo.kidu.app/health",
        "sandbox_public_smoke": "passed",
        "public_smoke_url": "https://demo.kidu.app/health",
        "browser_smoke_url": "https://demo.kidu.app/",
        "playwright_url": "https://demo.kidu.app/",
        "playwright_smoke": "passed",
        "browser_smoke": "passed",
        "desktop_screenshot": "factory/projects/demo/evidence/desktop.png",
        "mobile_screenshot": "factory/projects/demo/evidence/mobile.png",
        "console_error_check": {"status": "passed", "errors": 0},
        "core_flow_interaction": "passed",
        "qa_report_path": "factory/projects/demo/QA_REPORT.md",
        "evidence_paths": [
            "factory/projects/demo/evidence/desktop.png",
            "factory/projects/demo/evidence/mobile.png",
            "factory/projects/demo/QA_REPORT.md",
        ],
    }


def test_ui_delivery_gate_blocks_without_required_sandbox_playwright_evidence(fake_sql, monkeypatch):
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: _ui_project())
    fake_sql.rows_results = [[]]
    fake_sql.statement_one_results = [{"gate_id": 43, "project_id": "demo", "status": "passed", "timestamp": "now"}]

    with pytest.raises(ValueError) as exc:
        factory_pg.record_gate("demo", "delivery", "passed", reviewer="qa", evidence={"tests": "passed"})

    message = str(exc.value)
    assert "sandbox_url" in message
    assert "sandbox_public_smoke" in message
    assert "browser_smoke_url" in message
    assert "playwright_smoke" in message
    assert "desktop_screenshot" in message
    assert "mobile_screenshot" in message
    assert "console_error_check" in message
    assert "core_flow_interaction" in message
    assert "QA_REPORT.md" in message
    assert "evidence_paths" in message


def test_ui_delivery_gate_rejects_non_authorized_sandbox_url(fake_sql, monkeypatch):
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: _ui_project())
    fake_sql.rows_results = [[]]
    evidence = _complete_ui_delivery_evidence()
    evidence["sandbox_url"] = "https://example.com/demo"

    with pytest.raises(ValueError, match="authorized sandbox"):
        factory_pg.record_gate("demo", "delivery", "passed", reviewer="qa", evidence=evidence)


def test_ui_delivery_gate_passes_with_complete_authorized_sandbox_playwright_evidence(fake_sql, monkeypatch):
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: _ui_project())
    fake_sql.rows_results = [[]]
    fake_sql.statement_one_results = [{"gate_id": 44, "project_id": "demo", "status": "passed", "timestamp": "now"}]

    result = factory_pg.record_gate("demo", "delivery", "passed", reviewer="qa", evidence=_complete_ui_delivery_evidence())

    assert result["gate_id"] == 44
    joined = "\n".join(fake_sql.statements)
    assert "demo.kidu.app" in joined
    assert "desktop.png" in joined
    assert "mobile.png" in joined


def test_reconciliation_requires_canonical_ui_phase_contract(monkeypatch):
    monkeypatch.setattr(factory_pg, "_project_artifact_dir", lambda project: (None, "factory/projects/demo"))
    project = _ui_project()
    tasks = [
        {"task_id": "demo-impl", "title": "Implement UI", "phase": "implementation", "status": "todo", "owner_profile": "codex-builder"},
    ]

    findings = factory_pg.reconciliation_findings(project, tasks=tasks, pending_gates=[], gates=[])

    finding = next(f for f in findings if f["code"] == "missing_mandatory_factory_phases")
    missing = set(finding["metadata"]["missing_categories"])
    assert {"planning", "quality_review", "ui_qa_verification", "sandbox_deploy", "post_sandbox_verification", "delivery_report"}.issubset(missing)


def test_reconciliation_accepts_canonical_ui_phase_contract(monkeypatch):
    monkeypatch.setattr(factory_pg, "_project_artifact_dir", lambda project: (None, "factory/projects/demo"))
    project = _ui_project()
    tasks = [
        {"task_id": "demo-plan", "title": "Finalize PRD ADR sprint task graph", "phase": "planning", "status": "done", "owner_profile": "implementation-planner"},
        {"task_id": "demo-impl", "title": "Implement UI", "phase": "implementation", "status": "done", "owner_profile": "codex-builder", "reviewer_profile": "quality-reviewer"},
        {"task_id": "demo-review", "title": "Independent quality review", "phase": "review", "status": "done", "owner_profile": "quality-reviewer"},
        {"task_id": "demo-ui-qa", "title": "Playwright browser QA with desktop/mobile screenshots", "phase": "qa", "status": "done", "owner_profile": "qa-verifier"},
        {"task_id": "demo-deploy", "title": "Deploy to authorized Kidu sandbox", "phase": "delivery", "status": "done", "owner_profile": "devops-release"},
        {"task_id": "demo-post-sandbox-qa", "title": "Post-sandbox Playwright browser smoke against public sandbox URL with console screenshots", "phase": "qa", "status": "done", "owner_profile": "qa-verifier"},
        {"task_id": "demo-report", "title": "Delivery report and gate closure", "phase": "delivery", "status": "done", "owner_profile": "factory-reporter"},
    ]

    findings = factory_pg.reconciliation_findings(project, tasks=tasks, pending_gates=[], gates=[])

    assert not any(f["code"] == "missing_mandatory_factory_phases" for f in findings)


def test_reconciliation_accepts_claude_deepseek_builder_as_implementation(monkeypatch):
    monkeypatch.setattr(factory_pg, "_project_artifact_dir", lambda project: (None, "factory/projects/demo"))
    project = _ui_project()
    tasks = [
        {"task_id": "demo-plan", "title": "PRD ADR sprint task graph", "phase": "planning", "status": "done", "owner_profile": "implementation-planner"},
        {"task_id": "demo-impl", "title": "Implement UI", "phase": "implementation", "status": "done", "owner_profile": "claude-deepseek-builder"},
        {"task_id": "demo-review", "title": "Independent quality review", "phase": "review", "status": "done", "owner_profile": "quality-reviewer"},
        {"task_id": "demo-ui-qa", "title": "Playwright browser QA with desktop/mobile screenshots", "phase": "qa", "status": "done", "owner_profile": "qa-verifier"},
        {"task_id": "demo-deploy", "title": "Deploy to authorized Kidu sandbox", "phase": "delivery", "status": "done", "owner_profile": "devops-release"},
        {"task_id": "demo-post-sandbox-qa", "title": "Post-sandbox Playwright browser smoke against public sandbox URL with console screenshots", "phase": "qa", "status": "done", "owner_profile": "qa-verifier"},
        {"task_id": "demo-report", "title": "Delivery report and gate closure", "phase": "delivery", "status": "done", "owner_profile": "factory-reporter"},
    ]

    findings = factory_pg.reconciliation_findings(project, tasks=tasks, pending_gates=[], gates=[])

    assert not any(f["code"] == "missing_mandatory_factory_phases" for f in findings)


def test_phase_contract_requires_distinct_ui_qa_and_post_sandbox_tasks(monkeypatch):
    monkeypatch.setattr(factory_pg, "_project_artifact_dir", lambda project: (None, "factory/projects/demo"))
    project = _ui_project()
    tasks = [
        {"task_id": "demo-plan", "title": "PRD ADR sprint task graph", "phase": "planning", "status": "done", "owner_profile": "implementation-planner"},
        {"task_id": "demo-impl", "title": "Implement UI", "phase": "implementation", "status": "done", "owner_profile": "codex-builder"},
        {"task_id": "demo-review", "title": "Independent quality review", "phase": "review", "status": "done", "owner_profile": "quality-reviewer"},
        {"task_id": "demo-deploy", "title": "Deploy to authorized Kidu sandbox", "phase": "delivery", "status": "done", "owner_profile": "devops-release"},
        {"task_id": "demo-post-sandbox-qa", "title": "Post-sandbox Playwright browser smoke against public sandbox URL with console screenshots", "phase": "qa", "status": "done", "owner_profile": "qa-verifier"},
        {"task_id": "demo-report", "title": "Delivery report and gate closure", "phase": "delivery", "status": "done", "owner_profile": "factory-reporter"},
    ]

    findings = factory_pg.reconciliation_findings(project, tasks=tasks, pending_gates=[], gates=[])

    finding = next(f for f in findings if f["code"] == "missing_mandatory_factory_phases")
    assert "post_sandbox_verification" in set(finding["metadata"]["missing_categories"])


def test_phase_contract_distinct_qa_tasks_are_order_independent(monkeypatch):
    monkeypatch.setattr(factory_pg, "_project_artifact_dir", lambda project: (None, "factory/projects/demo"))
    project = _ui_project()
    tasks = [
        {"task_id": "demo-plan", "title": "PRD ADR sprint task graph", "phase": "planning", "status": "done", "owner_profile": "implementation-planner"},
        {"task_id": "demo-impl", "title": "Implement UI", "phase": "implementation", "status": "done", "owner_profile": "codex-builder"},
        {"task_id": "demo-review", "title": "Independent quality review", "phase": "review", "status": "done", "owner_profile": "quality-reviewer"},
        {"task_id": "demo-deploy", "title": "Deploy to authorized Kidu sandbox", "phase": "delivery", "status": "done", "owner_profile": "devops-release"},
        {"task_id": "demo-post-sandbox-qa", "title": "Post-sandbox Playwright browser smoke against public sandbox URL with console screenshots", "phase": "qa", "status": "done", "owner_profile": "qa-verifier"},
        {"task_id": "demo-ui-qa", "title": "Playwright browser QA with desktop/mobile screenshots", "phase": "qa", "status": "done", "owner_profile": "qa-verifier"},
        {"task_id": "demo-report", "title": "Delivery report and gate closure", "phase": "delivery", "status": "done", "owner_profile": "factory-reporter"},
    ]

    findings = factory_pg.reconciliation_findings(project, tasks=tasks, pending_gates=[], gates=[])

    assert not any(f["code"] == "missing_mandatory_factory_phases" for f in findings)


def test_phase_reconciliation_not_suppressed_by_regular_playwright_task(monkeypatch):
    monkeypatch.setattr(factory_pg, "_project_artifact_dir", lambda project: (None, "factory/projects/demo"))
    project = _ui_project()
    tasks = [
        {"task_id": "demo-impl", "title": "Implement UI", "phase": "implementation", "status": "todo", "owner_profile": "codex-builder"},
        {"task_id": "demo-ui-qa", "title": "Playwright QA smoke", "phase": "qa", "status": "todo", "owner_profile": "qa-verifier"},
    ]

    findings = factory_pg.reconciliation_findings(project, tasks=tasks, pending_gates=[], gates=[])

    finding = next(f for f in findings if f["code"] == "missing_mandatory_factory_phases")
    missing = set(finding["metadata"]["missing_categories"])
    assert {"planning", "quality_review", "sandbox_deploy", "post_sandbox_verification", "delivery_report"}.issubset(missing)


def test_phase_contract_rejects_keyword_stuffed_planner_task(monkeypatch):
    monkeypatch.setattr(factory_pg, "_project_artifact_dir", lambda project: (None, "factory/projects/demo"))
    project = _ui_project()
    tasks = [
        {
            "task_id": "demo-all-in-one",
            "title": "PRD ADR implementation independent review Playwright browser screenshot console sandbox deploy delivery report",
            "phase": "planning",
            "status": "done",
            "owner_profile": "implementation-planner",
        },
    ]

    findings = factory_pg.reconciliation_findings(project, tasks=tasks, pending_gates=[], gates=[])

    finding = next(f for f in findings if f["code"] == "missing_mandatory_factory_phases")
    missing = set(finding["metadata"]["missing_categories"])
    assert {"implementation", "quality_review", "ui_qa_verification", "sandbox_deploy", "post_sandbox_verification", "delivery_report"}.issubset(missing)


def test_ui_delivery_gate_requires_public_url_smoke_and_same_browser_host(fake_sql, monkeypatch):
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: _ui_project())
    fake_sql.rows_results = [[]]
    evidence = _complete_ui_delivery_evidence()
    evidence.pop("sandbox_public_smoke")
    evidence.pop("browser_smoke_url")
    evidence["playwright_url"] = "https://other.kidu.app/"

    with pytest.raises(ValueError) as exc:
        factory_pg.record_gate("demo", "delivery", "passed", reviewer="qa", evidence=evidence)

    message = str(exc.value)
    assert "sandbox_public_smoke" in message
    assert "same public sandbox host" in message


def test_ui_delivery_gate_rejects_unpaired_passed_browser_smoke_url(fake_sql, monkeypatch):
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: _ui_project())
    fake_sql.rows_results = [[]]
    evidence = _complete_ui_delivery_evidence()
    evidence["playwright_smoke"] = "failed"
    evidence["playwright_url"] = "https://demo.kidu.app/"
    evidence["browser_smoke"] = "passed"
    evidence["browser_smoke_url"] = "https://example.com/"

    with pytest.raises(ValueError) as exc:
        factory_pg.record_gate("demo", "delivery", "passed", reviewer="qa", evidence=evidence)

    message = str(exc.value)
    assert "browser_smoke_url" in message
    assert "same public sandbox host" in message


def test_reconciliation_accepts_api_post_sandbox_verification(monkeypatch):
    monkeypatch.setattr(factory_pg, "_project_artifact_dir", lambda project: (None, "factory/projects/api-demo"))
    project = {
        "project_id": "api-demo",
        "repo_path": "/repo",
        "risk_level": "medium",
        "metadata": {"runnable_deliverable": True, "delivery_target": "sandbox", "deliverable_type": "api"},
    }
    tasks = [
        {"task_id": "plan", "title": "PRD ADR sprint task graph", "phase": "planning", "status": "done", "owner_profile": "implementation-planner"},
        {"task_id": "impl", "title": "Implement API", "phase": "implementation", "status": "done", "owner_profile": "codex-builder"},
        {"task_id": "review", "title": "Quality review", "phase": "review", "status": "done", "owner_profile": "quality-reviewer"},
        {"task_id": "qa", "title": "QA smoke verification", "phase": "qa", "status": "done", "owner_profile": "qa-verifier"},
        {"task_id": "deploy", "title": "Deploy API to authorized sandbox", "phase": "delivery", "status": "done", "owner_profile": "devops-release"},
        {"task_id": "post", "title": "Post-sandbox API health endpoint HTTP status smoke against public sandbox URL", "phase": "qa", "status": "done", "owner_profile": "qa-verifier"},
        {"task_id": "report", "title": "Delivery report and gate closure", "phase": "delivery", "status": "done", "owner_profile": "factory-reporter"},
    ]

    findings = factory_pg.reconciliation_findings(project, tasks=tasks, pending_gates=[], gates=[])

    assert not any(f["code"] == "missing_mandatory_factory_phases" for f in findings)


def test_delivery_gate_requires_health_url_same_host_for_health_check(fake_sql, monkeypatch):
    project = _ui_project()
    project["metadata"]["ui_deliverable"] = False
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: project)
    fake_sql.rows_results = [[]]
    evidence = {
        "sandbox_url": "https://demo.kidu.app/",
        "sandbox_deploy_path": "/srv/factory/projects/demo",
        "docker_compose_path": "/srv/factory/projects/demo/docker-compose.yml",
        "health_check": "passed",
        "health_url": "https://example.com/health",
    }

    with pytest.raises(ValueError) as exc:
        factory_pg.record_gate("demo", "delivery", "passed", reviewer="qa", evidence=evidence)

    message = str(exc.value)
    assert "health_url" in message
    assert "same public sandbox host" in message


def test_delivery_gate_rejects_public_smoke_without_explicit_url(fake_sql, monkeypatch):
    project = _ui_project()
    project["metadata"]["ui_deliverable"] = False
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: project)
    fake_sql.rows_results = [[]]
    evidence = {
        "sandbox_url": "https://demo.kidu.app/",
        "sandbox_deploy_path": "/srv/factory/projects/demo",
        "docker_compose_path": "/srv/factory/projects/demo/docker-compose.yml",
        "sandbox_public_smoke": "passed",
    }

    with pytest.raises(ValueError) as exc:
        factory_pg.record_gate("demo", "delivery", "passed", reviewer="qa", evidence=evidence)

    assert "sandbox_public_smoke evidence must include" in str(exc.value)


def test_delivery_gate_rejects_api_smoke_without_explicit_url(fake_sql, monkeypatch):
    project = _ui_project()
    project["metadata"]["ui_deliverable"] = False
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: project)
    fake_sql.rows_results = [[]]
    evidence = {
        "sandbox_url": "https://demo.kidu.app/",
        "sandbox_deploy_path": "/srv/factory/projects/demo",
        "docker_compose_path": "/srv/factory/projects/demo/docker-compose.yml",
        "health_check": "passed",
        "health_url": "https://demo.kidu.app/health",
        "api_smoke": "passed",
    }

    with pytest.raises(ValueError) as exc:
        factory_pg.record_gate("demo", "delivery", "passed", reviewer="qa", evidence=evidence)

    assert "api_smoke evidence must include" in str(exc.value)


def test_delivery_gate_rejects_nested_api_smoke_url_without_explicit_api_smoke_url(fake_sql, monkeypatch):
    project = _ui_project()
    project["metadata"]["ui_deliverable"] = False
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: project)
    fake_sql.rows_results = [[]]
    evidence = {
        "sandbox_url": "https://demo.kidu.app/",
        "sandbox_deploy_path": "/srv/factory/projects/demo",
        "docker_compose_path": "/srv/factory/projects/demo/docker-compose.yml",
        "health_check": "passed",
        "health_url": "https://demo.kidu.app/health",
        "api_smoke": {"status": "passed", "url": "https://demo.kidu.app/api/health"},
    }

    with pytest.raises(ValueError) as exc:
        factory_pg.record_gate("demo", "delivery", "passed", reviewer="qa", evidence=evidence)

    assert "api_smoke evidence must include" in str(exc.value)


def test_delivery_gate_rejects_nested_public_smoke_url_on_wrong_host(fake_sql, monkeypatch):
    project = _ui_project()
    project["metadata"]["ui_deliverable"] = False
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: project)
    fake_sql.rows_results = [[]]
    evidence = {
        "sandbox_url": "https://demo.kidu.app/",
        "sandbox_deploy_path": "/srv/factory/projects/demo",
        "docker_compose_path": "/srv/factory/projects/demo/docker-compose.yml",
        "sandbox_public_smoke": {"status": "passed", "url": "https://example.com/health"},
    }

    with pytest.raises(ValueError) as exc:
        factory_pg.record_gate("demo", "delivery", "passed", reviewer="qa", evidence=evidence)

    message = str(exc.value)
    assert "sandbox_public_smoke_url" in message
    assert "same public sandbox host" in message


def test_ui_delivery_gate_ignores_custom_sandbox_host_without_explicit_authorization(fake_sql, monkeypatch):
    project = _ui_project()
    project["metadata"]["authorized_sandbox_hosts"] = ["example.com"]
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: project)
    fake_sql.rows_results = [[]]
    evidence = _complete_ui_delivery_evidence()
    evidence["sandbox_url"] = "https://example.com/demo"

    with pytest.raises(ValueError, match="authorized sandbox"):
        factory_pg.record_gate("demo", "delivery", "passed", reviewer="qa", evidence=evidence)


def test_ui_delivery_gate_blocks_sandbox_paths_outside_authorized_project_root(fake_sql, monkeypatch):
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: _ui_project())
    fake_sql.rows_results = [[]]
    evidence = _complete_ui_delivery_evidence()
    evidence["sandbox_deploy_path"] = "/var/www/prod"
    evidence["docker_compose_path"] = "/etc/docker-compose.yml"

    with pytest.raises(ValueError) as exc:
        factory_pg.record_gate("demo", "delivery", "passed", reviewer="qa", evidence=evidence)

    message = str(exc.value)
    assert "/srv/factory/projects/demo" in message
    assert "docker_compose_path" in message


def test_ui_delivery_gate_requires_evidence_paths_cover_desktop_mobile_and_qa_report(fake_sql, monkeypatch):
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: _ui_project())
    fake_sql.rows_results = [[]]
    evidence = _complete_ui_delivery_evidence()
    evidence["evidence_paths"] = ["factory/projects/demo/evidence/desktop.png"]

    with pytest.raises(ValueError) as exc:
        factory_pg.record_gate("demo", "delivery", "passed", reviewer="qa", evidence=evidence)

    message = str(exc.value)
    assert "evidence_paths" in message
    assert "mobile_screenshot" in message
    assert "QA_REPORT.md" in message

def test_ui_delivery_gate_blocks_path_traversal_outside_authorized_project_root(fake_sql, monkeypatch):
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: _ui_project())
    fake_sql.rows_results = [[]]
    evidence = _complete_ui_delivery_evidence()
    evidence["sandbox_deploy_path"] = "/srv/factory/projects/demo/../../prod"
    evidence["docker_compose_path"] = "/srv/factory/projects/demo/../../prod/docker-compose.yml"

    with pytest.raises(ValueError) as exc:
        factory_pg.record_gate("demo", "delivery", "passed", reviewer="qa", evidence=evidence)

    assert "/srv/factory/projects/demo" in str(exc.value)

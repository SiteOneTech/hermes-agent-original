"""Regression tests for INC-0001 Factory runtime docs/Notion control-plane refactor."""
from __future__ import annotations

import argparse
import json
import subprocess

import pytest

from hermes_cli import factory, factory_pg


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


def test_linked_notion_metadata_satisfies_reconciler_for_funnel_core(monkeypatch):
    monkeypatch.setattr(factory_pg, "_project_artifact_dir", lambda project: (None, "factory/projects/funnel-core-crm-workflow"))
    project_missing = {"project_id": "funnel-core-crm-workflow", "status": "active", "metadata": {}}
    findings = factory_pg.reconciliation_findings(project_missing, tasks=[{"task_id": "t1", "status": "todo"}], pending_gates=[])
    assert any(f["code"] == "missing_notion_project" for f in findings)

    project_linked = {
        "project_id": "funnel-core-crm-workflow",
        "status": "active",
        "metadata": {
            "notion_tracker_page_id": "37a37b39-cad6-8146-b9f2-e1fdf0bdf727",
            "notion_tracker_url": "https://app.notion.com/p/x-37a37b39cad68146b9f2e1fdf0bdf727",
        },
    }
    findings_linked = factory_pg.reconciliation_findings(project_linked, tasks=[{"task_id": "t1", "status": "todo"}], pending_gates=[])
    assert not any(f["code"] == "missing_notion_project" for f in findings_linked)


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


def test_dispatch_preflight_blocks_implementation_without_docs_or_notion():
    task = {"task_id": "demo-impl", "phase": "implementation", "status": "todo", "metadata": {}}
    blockers = factory_pg._dispatch_preflight_blockers(task, docs_ready=False, notion_ready=False)
    assert "missing_or_unindexed_docs" in blockers
    assert "missing_notion_tracker" not in blockers


def test_dispatch_preflight_allows_docs_ready_when_notion_missing_by_default():
    task = {"task_id": "demo-impl", "phase": "implementation", "status": "todo", "metadata": {}}
    assert factory_pg._dispatch_preflight_blockers(task, docs_ready=True, notion_ready=False) == []


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

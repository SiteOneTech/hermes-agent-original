from __future__ import annotations

import subprocess

import pytest

from hermes_cli import factory_pg


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
        import json

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
    monkeypatch.setattr(factory_pg, "notion_workflow_enabled", lambda: False)
    return fake


def test_close_task_integrates_increment_before_terminal_status(fake_sql, monkeypatch):
    calls: list[tuple[str, str]] = []

    def integrate(task_id: str, *, actor: str, final_status: str):
        calls.append((task_id, final_status))
        return {
            "increment_integration_required": True,
            "increment_integration_status": "integrated",
            "increment_base_branch": "main",
            "increment_base_commit_after": "abc123",
        }

    monkeypatch.setattr(factory_pg, "_integrate_increment_to_base", integrate)
    fake_sql.statement_one_results = [{"project_id": "demo", "lane_id": "lane", "task_id": "task-1", "status": "done"}]

    result = factory_pg.close_task("task-1", result_summary="QA passed", evidence={"tests": "passed"}, actor="qa")

    assert calls == [("task-1", "done")]
    assert result["status"] == "done"
    joined = "\n".join(fake_sql.statements)
    assert "increment_integration" in joined
    assert "task_closed" in joined


def test_close_task_refuses_done_when_increment_integration_fails(fake_sql, monkeypatch):
    def integrate(*_, **__):
        raise factory_pg.IncrementIntegrationError("merge conflict")

    monkeypatch.setattr(factory_pg, "_integrate_increment_to_base", integrate)

    with pytest.raises(ValueError, match="increment integration failed"):
        factory_pg.close_task("task-1", result_summary="QA passed", evidence={}, actor="qa")

    joined = "\n".join(fake_sql.statements)
    assert "SET status='done'" not in joined
    assert "task_closed" not in joined


def test_mark_run_finished_review_success_merges_before_done(fake_sql, monkeypatch):
    calls: list[str] = []

    def integrate(task_id: str, *, actor: str, final_status: str):
        calls.append(task_id)
        return {
            "increment_integration_required": True,
            "increment_integration_status": "integrated",
            "increment_base_branch": "main",
        }

    monkeypatch.setattr(factory_pg, "_integrate_increment_to_base", integrate)
    fake_sql.one_results = [
        {"task_id": "task-1", "metadata": {"run_type": "review"}},
        {"project_id": "demo"},
    ]

    factory_pg.mark_run_finished("run-1", exit_code=0, output_summary="STATE: DONE")

    assert calls == ["task-1"]
    joined = "\n".join(fake_sql.statements)
    assert "SET status='succeeded'" in joined
    assert "SET status='done'" in joined
    assert "Increment integration completed" in joined


def test_mark_run_finished_review_success_reworks_when_merge_fails(fake_sql, monkeypatch):
    def integrate(*_, **__):
        raise factory_pg.IncrementIntegrationError("push rejected")

    monkeypatch.setattr(factory_pg, "_integrate_increment_to_base", integrate)
    fake_sql.one_results = [
        {"task_id": "task-1", "metadata": {"run_type": "review"}},
        {"project_id": "demo"},
    ]

    factory_pg.mark_run_finished("run-1", exit_code=0, output_summary="STATE: DONE")

    joined = "\n".join(fake_sql.statements)
    assert "SET status='failed'" in joined
    assert "SET status='rework'" in joined
    assert "Increment integration failed before terminal close" in joined


def test_passed_task_gate_requires_increment_integration(fake_sql, monkeypatch):
    calls: list[str] = []

    def integrate(task_id: str, *, actor: str, final_status: str):
        calls.append(task_id)
        return {"increment_integration_required": True, "increment_integration_status": "integrated"}

    monkeypatch.setattr(factory_pg, "_integrate_increment_to_base", integrate)
    fake_sql.statement_one_results = [{"gate_id": 42, "project_id": "demo", "status": "passed", "timestamp": "now"}]

    result = factory_pg.record_gate("demo", "review", "passed", task_id="task-1", reviewer="qa", evidence={})

    assert calls == ["task-1"]
    assert result["gate_id"] == 42
    assert "increment_integration" in "\n".join(fake_sql.statements)


def test_next_runnable_task_blocks_dependency_not_integrated(fake_sql, monkeypatch):
    dep = {
        "project_id": "demo",
        "task_id": "task-1",
        "status": "done",
        "branch": "factory/demo/task-1",
        "worktree_path": "/tmp/worktrees/task-1",
        "metadata": {},
    }
    candidate = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-2",
        "status": "todo",
        "dependencies": ["task-1"],
    }
    fake_sql.rows_results = [[dep, candidate], [candidate]]
    fake_sql.one_results = [{"project_id": "demo", "metadata": {}}]
    monkeypatch.setattr(factory_pg, "_dependency_increment_integrated", lambda dep_task, project: False)

    assert factory_pg._next_runnable_task("demo") is None
    assert "increment_dependency_integration_blocked" in "\n".join(fake_sql.statements)


def test_next_runnable_task_prioritizes_doc_repair_over_product_rework(fake_sql, monkeypatch):
    rework = {"project_id": "demo", "task_id": "task-qa", "status": "rework", "phase": "qa-security", "dependencies": []}
    doc_repair = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "demo-reconcile-unvalidated-required-docs",
        "status": "todo",
        "phase": "documentation",
        "dependencies": [],
        "metadata": {"factory_reconciliation_task": True, "reconciliation_anomaly": "unvalidated_required_docs"},
    }
    delivery = {"project_id": "demo", "lane_id": "lane", "task_id": "task-delivery", "status": "todo", "phase": "delivery", "dependencies": []}
    fake_sql.rows_results = [[rework, doc_repair, delivery], [delivery, doc_repair]]
    fake_sql.one_results = [{"project_id": "demo", "metadata": {}}]

    result = factory_pg._next_runnable_task("demo")

    assert result["task_id"] == "demo-reconcile-unvalidated-required-docs"


def _git(path, *args):
    return subprocess.run(["git", "-C", str(path), *args], text=True, capture_output=True, check=True)


def test_integrate_increment_to_base_merges_and_pushes_real_git_repo(fake_sql, monkeypatch, tmp_path):
    origin = tmp_path / "origin.git"
    repo = tmp_path / "repo"
    worktree = tmp_path / "worktrees" / "task-1"
    subprocess.run(["git", "init", "--bare", str(origin)], text=True, capture_output=True, check=True)
    subprocess.run(["git", "clone", str(origin), str(repo)], text=True, capture_output=True, check=True)
    _git(repo, "config", "user.email", "factory@example.test")
    _git(repo, "config", "user.name", "Factory Test")
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "base")
    _git(repo, "branch", "-M", "main")
    _git(repo, "push", "origin", "main")
    _git(repo, "checkout", "-b", "factory/demo/task-1")
    (repo / "feature.txt").write_text("feature\n", encoding="utf-8")
    _git(repo, "add", "feature.txt")
    _git(repo, "commit", "-m", "feature")
    _git(repo, "push", "origin", "factory/demo/task-1")
    feature_commit = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _git(repo, "checkout", "main")

    task = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-1",
        "status": "review_ready",
        "branch": "factory/demo/task-1",
        "worktree_path": str(worktree),
        "metadata": {},
    }
    project = {
        "project_id": "demo",
        "repo_path": str(repo),
        "base_branch": "main",
        "metadata": {"repo_strategy": {"primary_repo_path": str(repo), "base_branch": "main"}},
    }
    fake_sql.one_results = [task]
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: project)

    evidence = factory_pg._integrate_increment_to_base("task-1", actor="qa", final_status="done")

    _git(repo, "fetch", "origin", "main")
    subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", feature_commit, "origin/main"], check=True)
    assert evidence["increment_integration_status"] == "integrated"
    assert evidence["increment_integration_method"] == "merge_no_ff_push_origin"
    assert "increment_integrated" in "\n".join(fake_sql.statements)

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


def test_claim_next_task_claims_docs_repair_before_preflight_denied_product(fake_sql, monkeypatch):
    product = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "demo-impl",
        "status": "todo",
        "phase": "implementation",
        "priority": 20,
        "dependencies": [],
        "metadata": {},
    }
    doc_repair = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "demo-reconcile-unvalidated-required-docs",
        "status": "todo",
        "phase": "documentation",
        "priority": 36,
        "dependencies": [],
        "metadata": {"factory_reconciliation_task": True, "reconciliation_anomaly": "unvalidated_required_docs"},
    }
    tasks = [product, doc_repair]
    project = {"project_id": "demo", "status": "active", "autonomous_enabled": True, "metadata": {}}
    fake_sql.rows_results = [[{"project_id": "demo"}], [product, doc_repair]]
    fake_sql.statement_one_results = [{**doc_repair, "status": "claimed"}]
    monkeypatch.setattr(factory_pg, "_tasks", lambda project_id: tasks)
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: project)
    monkeypatch.setattr(factory_pg, "_active_pending_gates", lambda project_id: [])
    monkeypatch.setattr(factory_pg, "_latest_gate_rows", lambda project_id: [])
    monkeypatch.setattr(
        factory_pg,
        "_project_docs_notion_preflight",
        lambda project_arg, tasks_arg, pending_arg, gates_arg: (False, True, False, False),
    )

    result = factory_pg.claim_next_task("demo", worker="factory-force-tick")

    assert result is not None
    assert result["task"]["task_id"] == "demo-reconcile-unvalidated-required-docs"
    joined = "\n".join(fake_sql.statements)
    assert "Task demo-reconcile-unvalidated-required-docs claimed" in joined
    assert "dispatch_preflight_denied" not in joined


def test_claim_next_task_claims_g1_recovery_despite_unresolved_validation_history(fake_sql, monkeypatch):
    validation_history = {
        "project_id": "demo",
        "task_id": "demo-quality-review",
        "status": "todo",
        "phase": "quality_review",
        "title": "Independent quality review",
        "owner_profile": "quality-reviewer",
        "dependencies": [],
        "metadata": {},
    }
    recovery = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "demo-r2f4-g1-recovery",
        "status": "todo",
        "phase": "g1_recovery",
        "priority": 10,
        "title": "Repair terminal run reconciliation after resolved G1 recovery cancellation",
        "description": "Finalize only this G1 recovery path; delivery remains blocked.",
        "owner_profile": "codex-builder",
        "reviewer_profile": "quality-reviewer",
        "dependencies": [],
        "metadata": {},
    }
    tasks = [validation_history, recovery]
    project = {"project_id": "demo", "status": "active", "autonomous_enabled": True, "metadata": {}}
    fake_sql.rows_results = [[{"project_id": "demo"}], [recovery]]
    fake_sql.statement_one_results = [{**recovery, "status": "claimed"}]
    monkeypatch.setattr(factory_pg, "_tasks", lambda project_id: tasks)
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: project)
    monkeypatch.setattr(factory_pg, "_active_pending_gates", lambda project_id: [])
    monkeypatch.setattr(factory_pg, "_latest_gate_rows", lambda project_id: [])
    monkeypatch.setattr(
        factory_pg,
        "_project_docs_notion_preflight",
        lambda project_arg, tasks_arg, pending_arg, gates_arg: (False, True, False, False),
    )

    result = factory_pg.claim_next_task("demo", worker="factory-force-tick")

    assert result is not None
    assert result["task"]["task_id"] == "demo-r2f4-g1-recovery"
    joined = "\n".join(fake_sql.statements)
    assert "Task demo-r2f4-g1-recovery claimed" in joined
    assert joined.count("INSERT INTO factory.task_runs") == 1
    assert "unresolved_validation_tasks" not in joined


def test_reconciler_requeues_technical_docs_repair_blocked_without_human_decision(fake_sql):
    project = {
        "project_id": "demo",
        "repo_path": "/repo",
        "risk_level": "medium",
        "metadata": {
            "repo_strategy": {
                "primary_repo_path": "/repo",
                "branch_prefix": "factory/demo/",
                "worktree_root": "/worktrees",
            },
            "g1_documentation_checkout": {
                "branch": "factory/demo/inc-010-g1-review",
                "path": "/worktrees/demo/inc-010-g1-review",
            },
        },
    }
    finding = {
        "code": "unvalidated_required_docs",
        "message": "Required Factory methodology documents are present but not fully validated/reviewed",
        "metadata": {"blocking_documents": ["PRD.md"]},
    }
    repair = {
        "project_id": "demo",
        "task_id": "demo-reconcile-unvalidated-required-docs",
        "status": "blocked",
        "retry_count": 0,
        "max_retries": 2,
        "metadata": {
            "factory_reconciliation_task": True,
            "reconciliation_anomaly": "unvalidated_required_docs",
            "last_blocker_classification": {
                "action_category": "technical_rework",
                "requires_human": False,
            },
        },
    }
    fake_sql.one_results = [{"task_id": "demo-reconcile-unvalidated-required-docs"}]

    changes = factory_pg.ensure_reconciliation_tasks(project, [finding], [repair])

    assert changes == [{
        "task_id": "demo-reconcile-unvalidated-required-docs",
        "code": "unvalidated_required_docs",
        "action": "requeued",
    }]
    joined = "\n".join(fake_sql.statements)
    assert "status='rework'" in joined
    assert "reconciliation_task_requeued" in joined
    assert "claimed_by=NULL" in joined
    assert "branch='factory/demo/inc-010-g1-review'" in joined
    assert "worktree_path='/worktrees/demo/inc-010-g1-review'" in joined
    assert "NOT EXISTS (" in joined
    assert "FROM factory.task_runs active_run" in joined


def test_reconciler_does_not_report_requeue_when_atomic_update_loses_race(fake_sql):
    project = {
        "project_id": "demo",
        "repo_path": "/repo",
        "risk_level": "medium",
        "metadata": {
            "repo_strategy": {
                "primary_repo_path": "/repo",
                "branch_prefix": "factory/demo/",
                "worktree_root": "/worktrees",
            },
            "g1_documentation_checkout": {
                "branch": "factory/demo/inc-010-g1-review",
                "path": "/worktrees/demo/inc-010-g1-review",
            },
        },
    }
    finding = {"code": "unvalidated_required_docs", "message": "docs require review", "metadata": {}}
    repair = {
        "project_id": "demo",
        "task_id": "demo-reconcile-unvalidated-required-docs",
        "status": "blocked",
        "retry_count": 0,
        "max_retries": 2,
        "metadata": {
            "factory_reconciliation_task": True,
            "reconciliation_anomaly": "unvalidated_required_docs",
            "last_blocker_classification": {
                "action_category": "technical_rework",
                "requires_human": False,
            },
        },
    }
    fake_sql.one_results = [None]

    changes = factory_pg.ensure_reconciliation_tasks(project, [finding], [repair])

    assert changes == []
    assert "recorded_event AS" in "\n".join(fake_sql.statements)


def test_reconciler_does_not_requeue_without_complete_g0_assignment(fake_sql):
    project = {
        "project_id": "demo",
        "risk_level": "medium",
        "metadata": {
            "repo_strategy": {
                "status": "missing",
                "branch_prefix": "factory/demo/",
                "worktree_root": "/worktrees",
            },
        },
    }
    finding = {
        "code": "unvalidated_required_docs",
        "message": "Required Factory methodology documents are present but not fully validated/reviewed",
        "metadata": {"blocking_documents": ["PRD.md"]},
    }
    repair = {
        "project_id": "demo",
        "task_id": "demo-reconcile-unvalidated-required-docs",
        "status": "blocked",
        "retry_count": 0,
        "max_retries": 2,
        "metadata": {
            "factory_reconciliation_task": True,
            "reconciliation_anomaly": "unvalidated_required_docs",
            "last_blocker_classification": {
                "action_category": "technical_rework",
                "requires_human": False,
            },
        },
    }

    changes = factory_pg.ensure_reconciliation_tasks(project, [finding], [repair])

    assert changes == []
    assert "status='rework'" not in "\n".join(fake_sql.statements)


def test_reconciler_does_not_requeue_conflicting_full_assignment(fake_sql):
    project = {
        "project_id": "demo",
        "repo_path": "/repo",
        "risk_level": "medium",
        "metadata": {
            "repo_strategy": {
                "primary_repo_path": "/repo",
                "branch_prefix": "factory/demo/",
                "worktree_root": "/worktrees",
            },
            "g1_documentation_checkout": {
                "branch": "factory/demo/inc-010-g1-review",
                "path": "/worktrees/demo/inc-010-g1-review",
            },
        },
    }
    finding = {
        "code": "unvalidated_required_docs",
        "message": "Required Factory methodology documents are present but not fully validated/reviewed",
        "metadata": {"blocking_documents": ["PRD.md"]},
    }
    repair = {
        "project_id": "demo",
        "task_id": "demo-reconcile-unvalidated-required-docs",
        "status": "blocked",
        "branch": "factory/demo/inc-099-unrelated",
        "worktree_path": "/worktrees/demo/inc-099-unrelated",
        "retry_count": 0,
        "max_retries": 2,
        "metadata": {
            "factory_reconciliation_task": True,
            "reconciliation_anomaly": "unvalidated_required_docs",
            "last_blocker_classification": {
                "action_category": "technical_rework",
                "requires_human": False,
            },
        },
    }
    fake_sql.one_results = [{"task_id": "demo-reconcile-unvalidated-required-docs"}]

    changes = factory_pg.ensure_reconciliation_tasks(project, [finding], [repair])

    assert changes == []
    assert "status='rework'" not in "\n".join(fake_sql.statements)


def test_claimed_null_predicate_ignores_docs_blocked_product_without_repair():
    payload = {
        "projects": [
            {
                "project_id": "demo",
                "status": "active",
                "autonomous_enabled": True,
                "document_status": [{"category": "g1_required", "blocking": True}],
            }
        ],
        "tasks": [
            {
                "project_id": "demo",
                "task_id": "demo-impl",
                "status": "todo",
                "phase": "implementation",
                "dependencies": [],
            }
        ],
        "task_runs": [],
    }

    assert factory_pg._claimed_null_alert_expected(payload, project_id="demo") is False


def test_claimed_null_predicate_sees_docs_repair_as_claimable():
    payload = {
        "projects": [
            {
                "project_id": "demo",
                "status": "active",
                "autonomous_enabled": True,
                "document_status": [{"category": "g1_required", "blocking": True}],
            }
        ],
        "tasks": [
            {
                "project_id": "demo",
                "task_id": "demo-impl",
                "status": "todo",
                "phase": "implementation",
                "dependencies": [],
            },
            {
                "project_id": "demo",
                "task_id": "demo-reconcile-unvalidated-required-docs",
                "status": "todo",
                "phase": "documentation",
                "dependencies": [],
                "metadata": {"factory_reconciliation_task": True, "reconciliation_anomaly": "unvalidated_required_docs"},
            },
        ],
        "task_runs": [],
    }

    assert factory_pg._claimed_null_alert_expected(payload, project_id="demo") is True


def test_claim_next_task_keeps_priority_order_when_docs_ready(fake_sql, monkeypatch):
    product = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "demo-impl",
        "status": "todo",
        "phase": "implementation",
        "priority": 20,
        "dependencies": [],
        "metadata": {},
    }
    doc_repair = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "demo-reconcile-unvalidated-required-docs",
        "status": "todo",
        "phase": "documentation",
        "priority": 36,
        "dependencies": [],
        "metadata": {"factory_reconciliation_task": True, "reconciliation_anomaly": "unvalidated_required_docs"},
    }
    tasks = [product, doc_repair]
    project = {"project_id": "demo", "status": "active", "autonomous_enabled": True, "metadata": {}}
    fake_sql.rows_results = [[{"project_id": "demo"}], [product, doc_repair]]
    fake_sql.statement_one_results = [{**product, "status": "claimed"}]
    monkeypatch.setattr(factory_pg, "_tasks", lambda project_id: tasks)
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: project)
    monkeypatch.setattr(factory_pg, "_active_pending_gates", lambda project_id: [])
    monkeypatch.setattr(factory_pg, "_latest_gate_rows", lambda project_id: [])
    monkeypatch.setattr(
        factory_pg,
        "_project_docs_notion_preflight",
        lambda project_arg, tasks_arg, pending_arg, gates_arg: (True, True, False, False),
    )

    result = factory_pg.claim_next_task("demo", worker="factory-force-tick")

    assert result is not None
    assert result["task"]["task_id"] == "demo-impl"


def _source_task(*, metadata=None, phase="implementation"):
    return {
        "project_id": "demo",
        "task_id": "task-source",
        "title": "Control-plane source increment",
        "description": "Implement control plane source changes",
        "phase": phase,
        "status": "done",
        "branch": "factory/demo/task-source",
        "worktree_path": "/tmp/factory-demo-task-source",
        "metadata": metadata or {},
    }


def _source_project(*, status="completed"):
    return {
        "project_id": "demo",
        "status": status,
        "repo_path": "/tmp/factory-demo-repo",
        "base_branch": "main",
        "metadata": {
            "repo_strategy": {
                "primary_repo_path": "/tmp/factory-demo-repo",
                "base_branch": "main",
            }
        },
    }


def test_runtime_bootstrap_repair_exemption_requires_structured_jean_authorization():
    text_only = _source_task()
    unapproved = _source_task(metadata={"runtime_bootstrap_repair": True})
    authorized = _source_task(metadata={
        "runtime_bootstrap_repair": True,
        "runtime_bootstrap_repair_authorized_by": "Jean García",
        "runtime_bootstrap_repair_authorization_reason": "Canonical Factory control-plane recovery",
    })

    assert factory_pg._is_runtime_bootstrap_repair_task(text_only) is False
    assert factory_pg._is_runtime_bootstrap_repair_task(unapproved) is False
    assert factory_pg._is_runtime_bootstrap_repair_task(authorized) is True
    assert factory_pg._increment_integration_required(text_only, _source_project(status="active"), "done") is True
    assert factory_pg._increment_integration_required(unapproved, _source_project(status="active"), "done") is True
    assert factory_pg._increment_integration_required(authorized, _source_project(status="active"), "done") is False


def test_reconciliation_finds_completed_source_increment_without_verified_base_integration():
    findings = factory_pg.reconciliation_findings(
        _source_project(),
        tasks=[_source_task(metadata={"increment_integration_status": "integrated"})],
        pending_gates=[],
        gates=[],
    )

    finding = next(item for item in findings if item["code"] == "source_increment_not_integrated")
    assert finding["metadata"]["task_ids"] == ["task-source"]
    assert finding["metadata"]["base_branch"] == "main"


def test_delivery_readiness_blocks_unintegrated_positive_terminal_source_task(monkeypatch):
    project = _source_project(status="active")
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: project)
    monkeypatch.setattr(factory_pg, "_tasks", lambda project_id: [_source_task()])
    monkeypatch.setattr(factory_pg, "_delivery_evidence_findings", lambda project_arg, evidence: [])

    findings = factory_pg.critical_readiness_findings("demo", gate_evidence={"tests": "passed"})

    assert any("task-source" in finding and "origin/main" in finding for finding in findings)


def test_reconciliation_rejects_metadata_claimed_integration_when_git_containment_fails(monkeypatch):
    claimed_integrated = _source_task(metadata={
        "increment_integration_status": "integrated",
        "increment_branch": "factory/demo/task-source",
        "increment_branch_commit": "abc123",
        "increment_base_branch": "main",
        "increment_base_commit_after": "def456",
    })
    monkeypatch.setattr(factory_pg, "_source_increment_is_contained_in_origin", lambda *args, **kwargs: False)

    findings = factory_pg.reconciliation_findings(
        _source_project(),
        tasks=[claimed_integrated],
        pending_gates=[],
        gates=[],
    )

    assert any(item["code"] == "source_increment_not_integrated" for item in findings)


def test_reconciliation_accepts_verified_git_containment_or_jean_waiver(monkeypatch):
    integrated = _source_task(metadata={
        "increment_integration_status": "integrated",
        "increment_branch": "factory/demo/task-source",
        "increment_branch_commit": "abc123",
        "increment_base_branch": "main",
        "increment_base_commit_after": "def456",
    })
    waived = _source_task(metadata={
        "increment_integration_waived": True,
        "increment_integration_waived_authorized_by": "Jean García",
        "increment_integration_waived_reason": "PR-first independent review remains open",
    })
    monkeypatch.setattr(factory_pg, "_refresh_source_increment_origin_base", lambda *args, **kwargs: True)
    monkeypatch.setattr(factory_pg, "_source_increment_is_contained_in_origin", lambda *args, **kwargs: True)

    for task in (integrated, waived):
        findings = factory_pg.reconciliation_findings(
            _source_project(),
            tasks=[task],
            pending_gates=[],
            gates=[],
        )
        assert not any(item["code"] == "source_increment_not_integrated" for item in findings)


def test_reconciliation_refreshes_origin_once_for_multiple_source_increments(monkeypatch, tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    project = _source_project()
    project["repo_path"] = str(repo)
    project["metadata"]["repo_strategy"]["primary_repo_path"] = str(repo)
    tasks = []
    for suffix in ("one", "two"):
        branch = f"factory/demo/task-{suffix}"
        task = _source_task(metadata={
            "increment_integration_status": "integrated",
            "increment_branch": branch,
            "increment_branch_commit": f"source-{suffix}",
            "increment_base_branch": "main",
            "increment_base_commit_after": "base-commit",
        })
        task["task_id"] = f"task-{suffix}"
        task["branch"] = branch
        tasks.append(task)

    calls = []

    def run_git(repo_path, args, *, timeout):
        calls.append((repo_path, args, timeout))
        if args[:3] == ["fetch", "origin", "main"]:
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")
        if args[:2] == ["rev-parse", "--verify"]:
            return subprocess.CompletedProcess(args, 0, stdout="commit\n", stderr="")
        if args[:2] == ["merge-base", "--is-ancestor"]:
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")
        raise AssertionError(f"unexpected git command: {args}")

    monkeypatch.setattr(factory_pg, "_run_git", run_git)

    assert factory_pg._source_increment_integration_blockers(project, tasks) == []
    fetches = [args for _, args, _ in calls if args[:3] == ["fetch", "origin", "main"]]
    comparisons = [args for _, args, _ in calls if args[:2] == ["merge-base", "--is-ancestor"]]
    assert fetches == [["fetch", "origin", "main"]]
    assert len(comparisons) == 2


def test_reconciliation_keeps_legitimate_non_source_and_reconciliation_tasks_working():
    docs_task = _source_task(phase="documentation")
    docs_task["branch"] = "main"
    reconciliation_task = _source_task(metadata={
        "factory_reconciliation_task": True,
        "reconciliation_anomaly": "missing_required_docs",
    })

    findings = factory_pg.reconciliation_findings(
        _source_project(),
        tasks=[docs_task, reconciliation_task],
        pending_gates=[],
        gates=[],
    )

    assert not any(item["code"] == "source_increment_not_integrated" for item in findings)


def test_source_integration_blocker_prevents_completion_auto_resume():
    assert factory_pg._should_auto_resume_after_reconcile(
        "active",
        "completed",
        completion_blockers=["source_increment_not_integrated"],
    ) is False


def _git(path, *args):
    return subprocess.run(["git", "-C", str(path), *args], text=True, capture_output=True, check=True)


def test_factory_git_commands_disable_interactive_prompts(monkeypatch, tmp_path):
    captured = {}

    def run(command, **kwargs):
        captured["command"] = command
        captured.update(kwargs)
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(factory_pg.subprocess, "run", run)

    factory_pg._run_git(tmp_path, ["fetch", "origin", "main"], timeout=17)

    assert captured["command"] == ["git", "-C", str(tmp_path), "fetch", "origin", "main"]
    assert captured["timeout"] == 17
    assert captured["env"]["GIT_TERMINAL_PROMPT"] == "0"


def test_source_integration_requires_current_origin_base_ancestry(tmp_path):
    origin = tmp_path / "origin.git"
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "--bare", str(origin)], text=True, capture_output=True, check=True)
    subprocess.run(["git", "clone", str(origin), str(repo)], text=True, capture_output=True, check=True)
    _git(repo, "config", "user.email", "factory@example.test")
    _git(repo, "config", "user.name", "Factory Test")
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "base")
    _git(repo, "branch", "-M", "main")
    _git(repo, "push", "origin", "main")
    _git(repo, "checkout", "-b", "factory/demo/task-source")
    (repo / "feature.txt").write_text("feature\n", encoding="utf-8")
    _git(repo, "add", "feature.txt")
    _git(repo, "commit", "-m", "feature")
    source_commit = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _git(repo, "push", "origin", "factory/demo/task-source")

    task = _source_task(metadata={
        "increment_integration_status": "integrated",
        "increment_branch": "factory/demo/task-source",
        "increment_branch_commit": source_commit,
        "increment_base_branch": "main",
        "increment_base_commit_after": _git(repo, "rev-parse", "main").stdout.strip(),
    })
    project = _source_project()
    project["repo_path"] = str(repo)
    project["metadata"]["repo_strategy"]["primary_repo_path"] = str(repo)

    assert factory_pg._source_increment_is_contained_in_origin(
        task, project, branch=task["branch"], base_branch="main"
    ) is False

    _git(repo, "checkout", "main")
    _git(repo, "merge", "--no-ff", "factory/demo/task-source", "-m", "merge feature")
    _git(repo, "push", "origin", "main")
    _git(repo, "branch", "-D", "factory/demo/task-source")
    _git(repo, "push", "origin", "--delete", "factory/demo/task-source")

    assert factory_pg._source_increment_is_contained_in_origin(
        task, project, branch=task["branch"], base_branch="main"
    ) is True


def test_integrate_increment_to_base_rejects_dirty_worktree_before_gate(fake_sql, monkeypatch, tmp_path):
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
    _git(repo, "worktree", "add", "-b", "factory/demo/task-1", str(worktree), "main")
    (worktree / "feature.txt").write_text("uncommitted feature\n", encoding="utf-8")

    task = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-1",
        "status": "claimed",
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

    with pytest.raises(factory_pg.IncrementIntegrationError, match="uncommitted changes"):
        factory_pg._integrate_increment_to_base("task-1", actor="qa", final_status="done")


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
    _git(repo, "worktree", "add", str(worktree), "factory/demo/task-1")

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

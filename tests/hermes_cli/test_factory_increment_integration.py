from __future__ import annotations

import subprocess

import pytest

from hermes_cli import factory_pg

_ORIGINAL_RECONCILE_PROJECT = factory_pg.reconcile_project
_BASE_CURRENT = "a" * 40
_BASE_OLD = "b" * 40


class FakeSql:
    def __init__(self) -> None:
        self.statements: list[str] = []
        self.one_results: list[dict | None] = []
        self.statement_one_results: list[dict | None] = []
        self.rows_results: list[list[dict]] = []
        self.json_query_results: list[list[dict]] = []

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
        return self.json_query_results.pop(0) if self.json_query_results else []

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


def test_close_task_respects_project_auto_integration_forbidden_without_increment_event(fake_sql, monkeypatch):
    task = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-1",
        "status": "review_ready",
        "branch": "factory/demo/task-1",
        "worktree_path": "/tmp/factory-demo-task-1",
        "metadata": {},
    }
    project = {
        "project_id": "demo",
        "repo_path": "/tmp/factory-demo-repo",
        "base_branch": "main",
        "metadata": {
            "factory_auto_integration_forbidden": True,
            "repo_strategy": {"primary_repo_path": "/tmp/factory-demo-repo", "base_branch": "main"},
        },
    }
    fake_sql.one_results = [task]
    fake_sql.statement_one_results = [{"project_id": "demo", "lane_id": "lane", "task_id": "task-1", "status": "done"}]
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: project)
    calls: list[list[str]] = []

    def record_git(_repo_path, args, *, timeout=120):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    monkeypatch.setattr(factory_pg, "_run_git", record_git)

    result = factory_pg.close_task("task-1", result_summary="QA passed", evidence={}, actor="qa", reconcile=False)

    assert result["status"] == "done"
    assert calls == []
    joined = "\n".join(fake_sql.statements)
    assert "task_closed" in joined
    assert "increment_integrated" not in joined
    assert "merge_no_ff_push_origin" not in joined


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
        {"gate_id": 42, "gate_type": "quality", "reviewer": "quality-reviewer"},
        {"project_id": "demo"},
    ]

    factory_pg.mark_run_finished(
        "run-1",
        exit_code=0,
        output_summary="Reviewed exact candidate SHA abc1234; gate_id 42 passed.\nSTATE: DONE",
    )

    assert calls == ["task-1"]
    joined = "\n".join(fake_sql.statements)
    assert "SET status='succeeded'" in joined
    assert "SET status='done'" in joined
    assert "Increment integration completed" in joined


def test_mark_run_finished_review_success_requires_task_bound_gate(fake_sql, monkeypatch):
    calls: list[str] = []

    def integrate(task_id: str, *, actor: str, final_status: str):
        calls.append(task_id)
        return {"increment_integration_required": True, "increment_integration_status": "integrated"}

    monkeypatch.setattr(factory_pg, "_integrate_increment_to_base", integrate)
    fake_sql.one_results = [
        {"task_id": "task-1", "metadata": {"run_type": "review"}},
        None,
        {"project_id": "demo"},
    ]

    factory_pg.mark_run_finished(
        "run-1",
        exit_code=0,
        output_summary="Reviewed exact candidate SHA abc1234, but no task-bound Factory gate was recorded.\nSTATE: DONE",
    )

    assert calls == []
    joined = "\n".join(fake_sql.statements)
    assert "SET status='failed'" in joined
    assert "SET status='review_ready'" in joined
    assert "SET status='done'" not in joined
    assert "review_success_without_task_bound_passed_gate" in joined
    assert "review_run_failed" in joined


def test_mark_run_finished_review_success_reworks_when_merge_fails(fake_sql, monkeypatch):
    def integrate(*_, **__):
        raise factory_pg.IncrementIntegrationError("push rejected")

    monkeypatch.setattr(factory_pg, "_integrate_increment_to_base", integrate)
    fake_sql.one_results = [
        {"task_id": "task-1", "metadata": {"run_type": "review"}},
        {"gate_id": 42, "gate_type": "quality", "reviewer": "quality-reviewer"},
        {"project_id": "demo"},
    ]

    factory_pg.mark_run_finished(
        "run-1",
        exit_code=0,
        output_summary="Reviewed exact candidate SHA abc1234; gate_id 42 passed.\nSTATE: DONE",
    )

    joined = "\n".join(fake_sql.statements)
    assert "SET status='failed'" in joined
    assert "SET status='rework'" in joined
    assert "Increment integration failed before terminal close" in joined


def test_mark_run_finished_failed_review_runtime_failure_requeues_review(fake_sql, monkeypatch):
    calls: list[str] = []

    def integrate(task_id: str, *, actor: str, final_status: str):
        calls.append(task_id)
        return {"increment_integration_required": True, "increment_integration_status": "integrated"}

    monkeypatch.setattr(factory_pg, "_integrate_increment_to_base", integrate)
    fake_sql.one_results = [
        {"task_id": "task-1", "metadata": {"run_type": "review"}},
        {"project_id": "demo"},
    ]
    output = (
        "STATE: DONE; si falla, termina con STATE: BLOCKED y razones/rework.\n"
        "RateLimitError [HTTP 429]: Token Plan usage limit reached.\n"
        "API call failed after 3 retries."
    )

    factory_pg.mark_run_finished("run-1", exit_code=1, output_summary=output)

    assert calls == []
    joined = "\n".join(fake_sql.statements)
    assert "SET status='failed'" in joined
    assert "SET status='review_ready'" in joined
    assert "SET status='done'" not in joined
    assert "review_run_failed" in joined
    assert "HTTP 429" in joined


def test_mark_run_finished_review_429_log_cannot_close_even_when_exit_zero(fake_sql, monkeypatch):
    calls: list[str] = []

    def integrate(task_id: str, *, actor: str, final_status: str):
        calls.append(task_id)
        return {"increment_integration_required": True, "increment_integration_status": "integrated"}

    monkeypatch.setattr(factory_pg, "_integrate_increment_to_base", integrate)
    fake_sql.one_results = [
        {"task_id": "task-1", "metadata": {"run_type": "review"}},
        {"project_id": "demo"},
    ]
    output = (
        "Final semantic state marker:\n"
        "STATE: DONE; si falla, termina con STATE: BLOCKED y razones/rework.\n\n"
        "⚠️  API call failed (attempt 1/3): RateLimitError [HTTP 429]\n"
        "❌ Rate limited after 3 retries — HTTP 429: Token Plan usage limit reached.\n"
        "API call failed after 3 retries: HTTP 429: Token Plan usage limit reached.\n"
        "Messages:       1 (1 user, 0 tool calls)\n"
    )

    factory_pg.mark_run_finished("run-1", exit_code=0, output_summary=output)

    assert calls == []
    joined = "\n".join(fake_sql.statements)
    assert "SET status='failed'" in joined
    assert "SET status='review_ready'" in joined
    assert "SET status='done'" not in joined
    assert "review_output_contains_runtime_failure" in joined
    assert "RateLimitError" in joined


def test_mark_run_finished_review_generic_http_429_requeues_even_with_task_gate(fake_sql, monkeypatch):
    calls: list[str] = []

    def integrate(task_id: str, *, actor: str, final_status: str):
        calls.append(task_id)
        return {"increment_integration_required": True, "increment_integration_status": "integrated"}

    monkeypatch.setattr(factory_pg, "_integrate_increment_to_base", integrate)
    fake_sql.one_results = [
        {"task_id": "task-1", "metadata": {"run_type": "review"}},
        {"gate_id": 7, "gate_type": "security", "reviewer": "security-reviewer"},
        {"project_id": "demo"},
    ]
    output = (
        "Independent review transcript\n"
        "STATE: DONE\n"
        "Provider response: HTTP 429 Too Many Requests\n"
    )

    factory_pg.mark_run_finished("run-1", exit_code=0, output_summary=output)

    assert calls == []
    joined = "\n".join(fake_sql.statements)
    assert "SET status='failed'" in joined
    assert "SET status='review_ready'" in joined
    assert "SET status='done'" not in joined
    assert "review_output_contains_runtime_failure" in joined
    assert "HTTP 429 Too Many Requests" in joined


def test_mark_run_finished_review_can_document_429_condition_with_task_gate(fake_sql, monkeypatch):
    calls: list[str] = []

    def integrate(task_id: str, *, actor: str, final_status: str):
        calls.append(task_id)
        return {"increment_integration_required": True, "increment_integration_status": "integrated"}

    monkeypatch.setattr(factory_pg, "_integrate_increment_to_base", integrate)
    fake_sql.one_results = [
        {"task_id": "task-1", "metadata": {"run_type": "review"}},
        {"gate_id": 7, "gate_type": "security", "reviewer": "security-reviewer"},
        {"project_id": "demo"},
    ]
    output = (
        "Independent security review for exact SHA abc1234 passed.\n"
        "The review explicitly checked the R2dc regression where a prior "
        "`API call failed after 3 retries: HTTP 429 / Too Many Requests` "
        "transcript must be requeued instead of accepted as review evidence.\n"
        "No provider/runtime failure occurred during this review run.\n"
        "STATE: DONE\n"
    )

    factory_pg.mark_run_finished("run-1", exit_code=0, output_summary=output)

    assert calls == ["task-1"]
    joined = "\n".join(fake_sql.statements)
    assert "SET status='succeeded'" in joined
    assert "SET status='done'" in joined
    assert "review_output_contains_runtime_failure" not in joined
    assert "Review terminal success rejected" not in joined


def test_mark_run_finished_review_prompt_only_marker_requeues_even_with_task_gate(fake_sql, monkeypatch):
    calls: list[str] = []

    def integrate(task_id: str, *, actor: str, final_status: str):
        calls.append(task_id)
        return {"increment_integration_required": True, "increment_integration_status": "integrated"}

    monkeypatch.setattr(factory_pg, "_integrate_increment_to_base", integrate)
    fake_sql.one_results = [
        {"task_id": "task-1", "metadata": {"run_type": "review"}},
        {"gate_id": 7, "gate_type": "security", "reviewer": "security-reviewer"},
        {"project_id": "demo"},
    ]

    factory_pg.mark_run_finished(
        "run-1",
        exit_code=0,
        output_summary="Final semantic state marker:\nSTATE: DONE\n",
    )

    assert calls == []
    joined = "\n".join(fake_sql.statements)
    assert "SET status='failed'" in joined
    assert "SET status='review_ready'" in joined
    assert "SET status='done'" not in joined
    assert "prompt_only_reviewer_output" in joined


def test_reconcile_project_recovers_false_terminalized_review_run(fake_sql, monkeypatch):
    project = {"project_id": "demo", "status": "active", "metadata": {"repo_strategy": {"repo_scope": "zeus_only", "work_intent": "add_functionality", "primary_repo": "demo/repo", "primary_repo_path": "/tmp/demo", "primary_repo_remote": "https://example.test/demo.git", "base_branch": "main", "branch_prefix": "factory/demo", "worktree_policy": "isolated"}}}
    task = {"project_id": "demo", "task_id": "task-1", "status": "done", "title": "Reviewed task", "phase": "documentation", "owner_profile": "codex-builder", "reviewer_profile": "quality-reviewer", "metadata": {}}
    fake_sql.json_query_results = [[
        {
            "project_id": "demo",
            "lane_id": "lane",
            "task_id": "task-1",
            "run_id": "run-review",
            "task_status": "done",
            "increment_base_commit_after": _BASE_CURRENT,
            "output_summary": "STATE: DONE\nRateLimitError [HTTP 429]\nAPI call failed after 3 retries\nMessages:       1 (1 user, 0 tool calls)",
            "has_task_bound_passed_review_gate": False,
        }
    ]]
    monkeypatch.setattr(factory_pg, "_configured_base_ref_readback", lambda project: {"accepted": True, "base_commit": _BASE_CURRENT})
    monkeypatch.setattr(factory_pg, "_tasks", lambda project_id: [task])
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: project)
    monkeypatch.setattr(factory_pg, "_active_pending_gates", lambda project_id: [])
    monkeypatch.setattr(factory_pg, "_latest_gate_rows", lambda project_id: [])
    monkeypatch.setattr(factory_pg, "reconciliation_findings", lambda *args, **kwargs: [])
    monkeypatch.setattr(factory_pg, "ensure_reconciliation_tasks", lambda *args, **kwargs: [])
    monkeypatch.setattr(factory_pg, "cancel_resolved_reconciliation_tasks", lambda *args, **kwargs: [])
    monkeypatch.setattr(factory_pg, "_stale_g1_projection_metadata_keys", lambda *args, **kwargs: [])

    result = _ORIGINAL_RECONCILE_PROJECT("demo")

    assert result["false_review_terminalization_recoveries"] == 1
    joined = "\n".join(fake_sql.statements)
    assert "SET status='review_ready'" in joined
    assert "false_review_terminalization_recovered" in joined
    assert "review_output_contains_runtime_failure" in joined
    assert "SET status='done'" not in joined


def test_recover_false_terminal_review_skips_prior_recovered_run_but_reopens_later_run(fake_sql, monkeypatch):
    project = {"project_id": "demo", "metadata": {}}
    fake_sql.json_query_results = [[
        {
            "project_id": "demo",
            "lane_id": "lane",
            "task_id": "task-1",
            "run_id": "run-old-review",
            "task_status": "done",
            "increment_base_commit_after": _BASE_CURRENT,
            "output_summary": "STATE: DONE\nRateLimitError [HTTP 429]",
            "has_task_bound_passed_review_gate": False,
            "recovered_run_id": "run-old-review",
        },
        {
            "project_id": "demo",
            "lane_id": "lane",
            "task_id": "task-1",
            "run_id": "run-new-review",
            "task_status": "done",
            "increment_base_commit_after": _BASE_CURRENT,
            "output_summary": "STATE: DONE\nProvider response: HTTP 429 Too Many Requests",
            "has_task_bound_passed_review_gate": True,
            "recovered_run_id": "run-old-review",
        },
    ]]
    monkeypatch.setattr(factory_pg, "_configured_base_ref_readback", lambda project: {"accepted": True, "base_commit": _BASE_CURRENT})

    recovered = factory_pg._recover_false_terminalized_review_runs("demo", project=project)

    assert [row["run_id"] for row in recovered] == ["run-new-review"]
    joined = "\n".join(fake_sql.statements)
    assert "run-old-review" not in joined.split("run-new-review")[0]
    assert "SET status='review_ready'" in joined
    assert "review_output_contains_runtime_failure" in joined


def test_false_terminal_review_recovery_is_bounded_to_current_base(fake_sql, monkeypatch):
    project = {"project_id": "demo", "metadata": {}}
    fake_sql.json_query_results = [[
        {
            "project_id": "demo",
            "lane_id": "lane",
            "task_id": "task-old",
            "run_id": "run-old-review",
            "task_status": "done",
            "increment_base_commit_after": _BASE_OLD,
            "output_summary": "STATE: DONE\nRateLimitError [HTTP 429]",
            "has_task_bound_passed_review_gate": False,
        }
    ]]
    monkeypatch.setattr(factory_pg, "_configured_base_ref_readback", lambda project: {"accepted": True, "base_commit": _BASE_CURRENT})

    recovered = factory_pg._recover_false_terminalized_review_runs("demo", project=project)

    assert recovered == []
    joined = "\n".join(fake_sql.statements)
    assert "SET status='review_ready'" not in joined


def test_reconcile_project_revokes_unscoped_out_of_scope_false_terminal_recovery(fake_sql, monkeypatch):
    project = {"project_id": "demo", "status": "active", "metadata": {}}
    task = {"project_id": "demo", "task_id": "task-old", "status": "review_ready", "title": "Historical task", "phase": "documentation", "metadata": {"false_review_terminalization_recovered": True}}
    fake_sql.json_query_results = [
        [],
        [],
        [
            {
                "project_id": "demo",
                "lane_id": "lane",
                "task_id": "task-old",
                "run_id": "run-old-review",
                "previous_status": "done",
                "increment_base_commit_after": _BASE_OLD,
                "result_summary": "False review terminalization recovered by Factory reconcile",
            }
        ],
    ]
    monkeypatch.setattr(factory_pg, "_configured_base_ref_readback", lambda project: {"accepted": True, "base_commit": _BASE_CURRENT})
    monkeypatch.setattr(factory_pg, "_tasks", lambda project_id: [task])
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: project)
    monkeypatch.setattr(factory_pg, "_active_pending_gates", lambda project_id: [])
    monkeypatch.setattr(factory_pg, "_latest_gate_rows", lambda project_id: [])
    monkeypatch.setattr(factory_pg, "reconciliation_findings", lambda *args, **kwargs: [])
    monkeypatch.setattr(factory_pg, "ensure_reconciliation_tasks", lambda *args, **kwargs: [])
    monkeypatch.setattr(factory_pg, "cancel_resolved_reconciliation_tasks", lambda *args, **kwargs: [])
    monkeypatch.setattr(factory_pg, "_stale_g1_projection_metadata_keys", lambda *args, **kwargs: [])

    result = _ORIGINAL_RECONCILE_PROJECT("demo")

    assert result["false_review_terminalization_recovery_revocations"] == 1
    joined = "\n".join(fake_sql.statements)
    assert "false_review_terminalization_recovery_revoked" in joined
    assert "SET status='done'" in joined
    assert _BASE_OLD in joined
    assert _BASE_CURRENT in joined


def test_reconcile_project_scopes_current_unscoped_false_terminal_recovery(fake_sql, monkeypatch):
    project = {"project_id": "demo", "status": "active", "metadata": {}}
    task = {"project_id": "demo", "task_id": "task-current", "status": "review_ready", "title": "Current false review", "phase": "documentation", "metadata": {"false_review_terminalization_recovered": True}}
    fake_sql.json_query_results = [
        [],
        [
            {
                "project_id": "demo",
                "lane_id": "lane",
                "task_id": "task-current",
                "run_id": "run-current-review",
                "increment_base_commit_after": _BASE_CURRENT,
            }
        ],
        [],
    ]
    monkeypatch.setattr(factory_pg, "_configured_base_ref_readback", lambda project: {"accepted": True, "base_commit": _BASE_CURRENT})
    monkeypatch.setattr(factory_pg, "_tasks", lambda project_id: [task])
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: project)
    monkeypatch.setattr(factory_pg, "_active_pending_gates", lambda project_id: [])
    monkeypatch.setattr(factory_pg, "_latest_gate_rows", lambda project_id: [])
    monkeypatch.setattr(factory_pg, "reconciliation_findings", lambda *args, **kwargs: [])
    monkeypatch.setattr(factory_pg, "ensure_reconciliation_tasks", lambda *args, **kwargs: [])
    monkeypatch.setattr(factory_pg, "cancel_resolved_reconciliation_tasks", lambda *args, **kwargs: [])
    monkeypatch.setattr(factory_pg, "_stale_g1_projection_metadata_keys", lambda *args, **kwargs: [])

    result = _ORIGINAL_RECONCILE_PROJECT("demo")

    assert result["false_review_terminalization_recovery_scopes"] == 1
    joined = "\n".join(fake_sql.statements)
    assert "false_review_terminalization_recovery_scoped" in joined
    assert "current_configured_base_terminalization" in joined
    assert _BASE_CURRENT in joined


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
    monkeypatch.setattr(factory_pg, "_source_increment_is_contained_in_origin", lambda *args, **kwargs: True)

    for task in (integrated, waived):
        findings = factory_pg.reconciliation_findings(
            _source_project(),
            tasks=[task],
            pending_gates=[],
            gates=[],
        )
        assert not any(item["code"] == "source_increment_not_integrated" for item in findings)


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


def _source_delivery_metadata(
    candidate_commit: str,
    *,
    replacement_for: str = "task-old",
    pr_state: str = "merged",
    qa_guardian: bool = True,
    qa_guardian_evidence=None,
    pr_head_commit: str | None = None,
) -> dict:
    source_delivery = {
        "status": "accepted",
        "candidate_commit": candidate_commit,
        "pr_first_policy": True,
        "pr": {
            "url": "https://github.com/SiteOneTech/hermes-agent-original/pull/123",
            "state": pr_state,
            "head_commit": pr_head_commit or candidate_commit,
            "base_branch": "main",
            "mergeable_state": "clean",
        },
    }
    if qa_guardian:
        source_delivery["qa_guardian_evidence"] = (
            qa_guardian_evidence
            if qa_guardian_evidence is not None
            else {
                "status": "passed",
                "candidate_commit": candidate_commit,
                "reviewer": "qa-verifier",
            }
        )
    return {
        "replacement_for_task": replacement_for,
        "source_delivery": source_delivery,
    }


def _make_source_delivery_repo(tmp_path, *, merged_to_base: bool) -> tuple[dict, dict, str]:
    origin = tmp_path / "origin.git"
    repo = tmp_path / "repo"
    worktree = tmp_path / "worktrees" / "task-replacement"
    branch = "factory/demo/task-replacement"
    subprocess.run(["git", "init", "--bare", str(origin)], text=True, capture_output=True, check=True)
    subprocess.run(["git", "clone", str(origin), str(repo)], text=True, capture_output=True, check=True)
    _git(repo, "config", "user.email", "factory@example.test")
    _git(repo, "config", "user.name", "Factory Test")
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "base")
    _git(repo, "branch", "-M", "main")
    _git(repo, "push", "origin", "main")
    _git(repo, "checkout", "-b", branch)
    (repo / "feature.txt").write_text("replacement source\n", encoding="utf-8")
    _git(repo, "add", "feature.txt")
    _git(repo, "commit", "-m", "replacement source")
    feature_commit = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _git(repo, "push", "origin", branch)
    _git(repo, "checkout", "main")
    if merged_to_base:
        _git(repo, "merge", "--no-ff", branch, "-m", "merge replacement source")
        _git(repo, "push", "origin", "main")
    _git(repo, "worktree", "add", str(worktree), branch)
    project = {
        "project_id": "demo",
        "repo_path": str(repo),
        "base_branch": "main",
        "metadata": {"repo_strategy": {"primary_repo_path": str(repo), "base_branch": "main"}},
    }
    replacement = {
        "project_id": "demo",
        "task_id": "task-replacement",
        "status": "done",
        "branch": branch,
        "worktree_path": str(worktree),
        "metadata": _source_delivery_metadata(feature_commit),
    }
    return project, replacement, feature_commit


_BASE_ALIAS_OR_PSEUDO_REFS = (
    "main",
    "origin/main",
    "refs/heads/main",
    "refs/remotes/origin/main",
    "HEAD",
    "FETCH_HEAD",
    "ORIG_HEAD",
    "MERGE_HEAD",
    "origin/HEAD",
    "refs/remotes/origin/HEAD",
)

_UNSAFE_BASE_BRANCHES = (
    "",
    "--upload-pack=touch /tmp/factory-pwned",
    "HEAD",
    "FETCH_HEAD",
    "ORIG_HEAD",
    "MERGE_HEAD",
    "origin/HEAD",
    "refs/remotes/origin/HEAD",
    "main..evil",
    "bad branch",
)


def _project_with_base_branch(project: dict, base_branch: str) -> dict:
    project = dict(project)
    metadata = dict(project.get("metadata") or {})
    strategy = dict(metadata.get("repo_strategy") or {})
    project["base_branch"] = base_branch
    strategy["base_branch"] = base_branch
    metadata["repo_strategy"] = strategy
    project["metadata"] = metadata
    return project


def test_next_runnable_task_blocks_cancelled_dependency_without_replacement(fake_sql):
    dep = {"project_id": "demo", "task_id": "task-old", "status": "cancelled", "metadata": {}}
    candidate = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-downstream",
        "status": "todo",
        "dependencies": ["task-old"],
    }
    fake_sql.rows_results = [[dep, candidate], [candidate]]
    fake_sql.one_results = [{"project_id": "demo", "metadata": {}}]

    assert factory_pg._next_runnable_task("demo") is None
    joined = "\n".join(fake_sql.statements)
    assert "increment_dependency_integration_blocked" in joined
    assert "unreplaced_negative_terminal" in joined


def test_candidate_dependencies_integrated_blocks_missing_dependency_task(fake_sql):
    candidate = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-downstream",
        "status": "todo",
        "dependencies": ["task-missing"],
    }

    assert factory_pg._candidate_dependencies_integrated("demo", candidate, [candidate], {"project_id": "demo", "metadata": {}}) is False
    joined = "\n".join(fake_sql.statements)
    assert "increment_dependency_integration_blocked" in joined
    assert "missing_dependency_task" in joined


def test_has_claimable_autonomous_work_ignores_superseded_dependency_without_replacement():
    tasks = [
        {"task_id": "task-old", "status": "superseded", "metadata": {}},
        {"task_id": "task-downstream", "status": "todo", "dependencies": ["task-old"]},
    ]

    assert factory_pg._has_claimable_autonomous_work(tasks) is False


def test_candidate_dependencies_integrated_blocks_nonterminal_replacement(fake_sql):
    dep = {"project_id": "demo", "task_id": "task-old", "status": "superseded", "metadata": {"replacement_task_id": "task-replacement"}}
    replacement = {
        "project_id": "demo",
        "task_id": "task-replacement",
        "status": "review_ready",
        "metadata": {"replacement_for_task": "task-old"},
    }
    candidate = {"project_id": "demo", "lane_id": "lane", "task_id": "task-downstream", "status": "todo", "dependencies": ["task-old"]}

    assert factory_pg._candidate_dependencies_integrated("demo", candidate, [dep, replacement, candidate], {"project_id": "demo", "metadata": {}}) is False
    joined = "\n".join(fake_sql.statements)
    assert "replacement_nonterminal" in joined


def test_candidate_dependencies_integrated_blocks_mismatched_replacement(fake_sql):
    dep = {"project_id": "demo", "task_id": "task-old", "status": "superseded", "metadata": {"replacement_task_id": "task-replacement"}}
    replacement = {
        "project_id": "demo",
        "task_id": "task-replacement",
        "status": "done",
        "metadata": {"replacement_for_task": "another-task"},
    }
    candidate = {"project_id": "demo", "lane_id": "lane", "task_id": "task-downstream", "status": "todo", "dependencies": ["task-old"]}

    assert factory_pg._candidate_dependencies_integrated("demo", candidate, [dep, replacement, candidate], {"project_id": "demo", "metadata": {}}) is False
    joined = "\n".join(fake_sql.statements)
    assert "replacement_mismatch" in joined


def test_candidate_dependencies_integrated_blocks_unbound_replacement(fake_sql):
    dep = {"project_id": "demo", "task_id": "task-old", "status": "superseded", "metadata": {"replacement_task_id": "task-replacement"}}
    replacement = {
        "project_id": "demo",
        "task_id": "task-replacement",
        "status": "done",
        "metadata": {},
    }
    candidate = {"project_id": "demo", "lane_id": "lane", "task_id": "task-downstream", "status": "todo", "dependencies": ["task-old"]}

    assert factory_pg._candidate_dependencies_integrated("demo", candidate, [dep, replacement, candidate], {"project_id": "demo", "metadata": {}}) is False
    joined = "\n".join(fake_sql.statements)
    assert "replacement_unbound" in joined


def test_candidate_dependencies_integrated_blocks_replacement_cycle(fake_sql):
    dep = {"project_id": "demo", "task_id": "task-old", "status": "superseded", "metadata": {"replacement_task_id": "task-replacement"}}
    replacement = {
        "project_id": "demo",
        "task_id": "task-replacement",
        "status": "superseded",
        "metadata": {"replacement_task_id": "task-old", "replacement_for_task": "task-old"},
    }
    candidate = {"project_id": "demo", "lane_id": "lane", "task_id": "task-downstream", "status": "todo", "dependencies": ["task-old"]}

    assert factory_pg._candidate_dependencies_integrated("demo", candidate, [dep, replacement, candidate], {"project_id": "demo", "metadata": {}}) is False
    joined = "\n".join(fake_sql.statements)
    assert "replacement_cycle" in joined


def test_next_runnable_task_blocks_superseded_dependency_replacement_pr_open_not_in_base(fake_sql, tmp_path):
    project, replacement, feature_commit = _make_source_delivery_repo(tmp_path, merged_to_base=False)
    replacement["metadata"] = _source_delivery_metadata(feature_commit, pr_state="open")
    dep = {
        "project_id": "demo",
        "task_id": "task-old",
        "status": "superseded",
        "metadata": {"replacement_task_id": "task-replacement"},
    }
    candidate = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-downstream",
        "status": "todo",
        "dependencies": ["task-old"],
    }
    fake_sql.rows_results = [[dep, replacement, candidate], [candidate]]
    fake_sql.one_results = [project]

    assert factory_pg._next_runnable_task("demo") is None
    joined = "\n".join(fake_sql.statements)
    assert "increment_dependency_integration_blocked" in joined
    assert "pr_open" in joined
    assert "source_not_in_base" in joined


def test_next_runnable_task_blocks_replacement_source_delivery_without_branch(fake_sql, tmp_path):
    project, replacement, _feature_commit = _make_source_delivery_repo(tmp_path, merged_to_base=True)
    replacement.pop("branch")
    dep = {
        "project_id": "demo",
        "task_id": "task-old",
        "status": "superseded",
        "metadata": {"replacement_task_id": "task-replacement"},
    }
    candidate = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-downstream",
        "status": "todo",
        "dependencies": ["task-old"],
    }
    fake_sql.rows_results = [[dep, replacement, candidate], [candidate]]
    fake_sql.one_results = [project]

    assert factory_pg._next_runnable_task("demo") is None
    joined = "\n".join(fake_sql.statements)
    assert "increment_dependency_integration_blocked" in joined
    assert "unverified_branch_metadata" in joined


def test_next_runnable_task_blocks_replacement_source_delivery_without_worktree(fake_sql, tmp_path):
    project, replacement, _feature_commit = _make_source_delivery_repo(tmp_path, merged_to_base=True)
    replacement.pop("worktree_path")
    dep = {
        "project_id": "demo",
        "task_id": "task-old",
        "status": "superseded",
        "metadata": {"replacement_task_id": "task-replacement"},
    }
    candidate = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-downstream",
        "status": "todo",
        "dependencies": ["task-old"],
    }
    fake_sql.rows_results = [[dep, replacement, candidate], [candidate]]
    fake_sql.one_results = [project]

    assert factory_pg._next_runnable_task("demo") is None
    joined = "\n".join(fake_sql.statements)
    assert "increment_dependency_integration_blocked" in joined
    assert "unverified_branch_metadata" in joined


def test_next_runnable_task_blocks_replacement_source_delivery_on_base_branch(fake_sql, tmp_path):
    project, replacement, _feature_commit = _make_source_delivery_repo(tmp_path, merged_to_base=True)
    replacement["branch"] = "main"
    dep = {
        "project_id": "demo",
        "task_id": "task-old",
        "status": "superseded",
        "metadata": {"replacement_task_id": "task-replacement"},
    }
    candidate = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-downstream",
        "status": "todo",
        "dependencies": ["task-old"],
    }
    fake_sql.rows_results = [[dep, replacement, candidate], [candidate]]
    fake_sql.one_results = [project]

    assert factory_pg._next_runnable_task("demo") is None
    joined = "\n".join(fake_sql.statements)
    assert "increment_dependency_integration_blocked" in joined
    assert "unverified_branch_metadata" in joined


def test_next_runnable_task_blocks_replacement_source_delivery_without_pr_even_without_policy(fake_sql, tmp_path):
    project, replacement, feature_commit = _make_source_delivery_repo(tmp_path, merged_to_base=True)
    metadata = _source_delivery_metadata(feature_commit)
    metadata["source_delivery"].pop("pr_first_policy")
    metadata["source_delivery"].pop("pr")
    replacement["metadata"] = metadata
    dep = {
        "project_id": "demo",
        "task_id": "task-old",
        "status": "superseded",
        "metadata": {"replacement_task_id": "task-replacement"},
    }
    candidate = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-downstream",
        "status": "todo",
        "dependencies": ["task-old"],
    }
    fake_sql.rows_results = [[dep, replacement, candidate], [candidate]]
    fake_sql.one_results = [project]

    assert factory_pg._next_runnable_task("demo") is None
    joined = "\n".join(fake_sql.statements)
    assert "pr_missing" in joined


def test_next_runnable_task_blocks_contradictory_source_delivery_acceptance(fake_sql, tmp_path):
    project, replacement, feature_commit = _make_source_delivery_repo(tmp_path, merged_to_base=True)
    metadata = _source_delivery_metadata(feature_commit)
    metadata["source_delivery"]["accepted"] = True
    metadata["source_delivery"]["status"] = "rejected"
    replacement["metadata"] = metadata
    dep = {
        "project_id": "demo",
        "task_id": "task-old",
        "status": "superseded",
        "metadata": {"replacement_task_id": "task-replacement"},
    }
    candidate = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-downstream",
        "status": "todo",
        "dependencies": ["task-old"],
    }
    fake_sql.rows_results = [[dep, replacement, candidate], [candidate]]
    fake_sql.one_results = [project]

    assert factory_pg._next_runnable_task("demo") is None
    joined = "\n".join(fake_sql.statements)
    assert "source_delivery_contract_not_accepted" in joined


def test_next_runnable_task_dispatches_superseded_dependency_accepted_replacement(fake_sql, tmp_path):
    project, replacement, _feature_commit = _make_source_delivery_repo(tmp_path, merged_to_base=True)
    dep = {
        "project_id": "demo",
        "task_id": "task-old",
        "status": "superseded",
        "metadata": {"replacement_task_id": "task-replacement"},
    }
    candidate = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-downstream",
        "status": "todo",
        "dependencies": ["task-old"],
    }
    fake_sql.rows_results = [[dep, replacement, candidate], [candidate]]
    fake_sql.one_results = [project]

    result = factory_pg._next_runnable_task("demo")

    assert result is not None
    assert result["task_id"] == "task-downstream"


def test_next_runnable_task_blocks_replacement_without_qa_guardian_evidence(fake_sql, tmp_path):
    project, replacement, feature_commit = _make_source_delivery_repo(tmp_path, merged_to_base=True)
    replacement["metadata"] = _source_delivery_metadata(feature_commit, qa_guardian=False)
    dep = {
        "project_id": "demo",
        "task_id": "task-old",
        "status": "superseded",
        "metadata": {"replacement_task_id": "task-replacement"},
    }
    candidate = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-downstream",
        "status": "todo",
        "dependencies": ["task-old"],
    }
    fake_sql.rows_results = [[dep, replacement, candidate], [candidate]]
    fake_sql.one_results = [project]

    assert factory_pg._next_runnable_task("demo") is None
    joined = "\n".join(fake_sql.statements)
    assert "qa_guardian_evidence_missing" in joined


def test_next_runnable_task_blocks_scalar_qa_guardian_evidence(fake_sql, tmp_path):
    project, replacement, feature_commit = _make_source_delivery_repo(tmp_path, merged_to_base=True)
    replacement["metadata"] = _source_delivery_metadata(feature_commit, qa_guardian_evidence=True)
    dep = {
        "project_id": "demo",
        "task_id": "task-old",
        "status": "superseded",
        "metadata": {"replacement_task_id": "task-replacement"},
    }
    candidate = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-downstream",
        "status": "todo",
        "dependencies": ["task-old"],
    }
    fake_sql.rows_results = [[dep, replacement, candidate], [candidate]]
    fake_sql.one_results = [project]

    assert factory_pg._next_runnable_task("demo") is None
    joined = "\n".join(fake_sql.statements)
    assert "qa_guardian_evidence_missing" in joined


def test_next_runnable_task_blocks_qa_guardian_evidence_without_commit(fake_sql, tmp_path):
    project, replacement, feature_commit = _make_source_delivery_repo(tmp_path, merged_to_base=True)
    replacement["metadata"] = _source_delivery_metadata(feature_commit, qa_guardian_evidence={"status": "passed"})
    dep = {
        "project_id": "demo",
        "task_id": "task-old",
        "status": "superseded",
        "metadata": {"replacement_task_id": "task-replacement"},
    }
    candidate = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-downstream",
        "status": "todo",
        "dependencies": ["task-old"],
    }
    fake_sql.rows_results = [[dep, replacement, candidate], [candidate]]
    fake_sql.one_results = [project]

    assert factory_pg._next_runnable_task("demo") is None
    joined = "\n".join(fake_sql.statements)
    assert "qa_guardian_candidate_missing" in joined


def test_next_runnable_task_blocks_qa_guardian_commit_mismatch(fake_sql, tmp_path):
    project, replacement, feature_commit = _make_source_delivery_repo(tmp_path, merged_to_base=True)
    replacement["metadata"] = _source_delivery_metadata(
        feature_commit,
        qa_guardian_evidence={"status": "passed", "candidate_commit": "deadbeef"},
    )
    dep = {
        "project_id": "demo",
        "task_id": "task-old",
        "status": "superseded",
        "metadata": {"replacement_task_id": "task-replacement"},
    }
    candidate = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-downstream",
        "status": "todo",
        "dependencies": ["task-old"],
    }
    fake_sql.rows_results = [[dep, replacement, candidate], [candidate]]
    fake_sql.one_results = [project]

    assert factory_pg._next_runnable_task("demo") is None
    joined = "\n".join(fake_sql.statements)
    assert "qa_guardian_candidate_mismatch" in joined


def test_next_runnable_task_accepts_qa_guardian_commit_bound_evidence(fake_sql, tmp_path):
    project, replacement, feature_commit = _make_source_delivery_repo(tmp_path, merged_to_base=True)
    replacement["metadata"] = _source_delivery_metadata(
        feature_commit,
        qa_guardian_evidence={"status": "accepted", "commit_sha": feature_commit, "reviewer": "qa-verifier"},
    )
    dep = {
        "project_id": "demo",
        "task_id": "task-old",
        "status": "superseded",
        "metadata": {"replacement_task_id": "task-replacement"},
    }
    candidate = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-downstream",
        "status": "todo",
        "dependencies": ["task-old"],
    }
    fake_sql.rows_results = [[dep, replacement, candidate], [candidate]]
    fake_sql.one_results = [project]

    result = factory_pg._next_runnable_task("demo")

    assert result is not None
    assert result["task_id"] == "task-downstream"


def test_next_runnable_task_blocks_wrong_head_replacement_pr(fake_sql, tmp_path):
    project, replacement, feature_commit = _make_source_delivery_repo(tmp_path, merged_to_base=True)
    replacement["metadata"] = _source_delivery_metadata(feature_commit, pr_head_commit="deadbeef")
    dep = {
        "project_id": "demo",
        "task_id": "task-old",
        "status": "superseded",
        "metadata": {"replacement_task_id": "task-replacement"},
    }
    candidate = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-downstream",
        "status": "todo",
        "dependencies": ["task-old"],
    }
    fake_sql.rows_results = [[dep, replacement, candidate], [candidate]]
    fake_sql.one_results = [project]

    assert factory_pg._next_runnable_task("demo") is None
    joined = "\n".join(fake_sql.statements)
    assert "pr_head_mismatch" in joined


def test_next_runnable_task_blocks_string_false_merged_replacement_pr(fake_sql, tmp_path):
    project, replacement, feature_commit = _make_source_delivery_repo(tmp_path, merged_to_base=True)
    metadata = _source_delivery_metadata(feature_commit, pr_state="open")
    metadata["source_delivery"]["pr"]["merged"] = "false"
    replacement["metadata"] = metadata
    dep = {
        "project_id": "demo",
        "task_id": "task-old",
        "status": "superseded",
        "metadata": {"replacement_task_id": "task-replacement"},
    }
    candidate = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-downstream",
        "status": "todo",
        "dependencies": ["task-old"],
    }
    fake_sql.rows_results = [[dep, replacement, candidate], [candidate]]
    fake_sql.one_results = [project]

    assert factory_pg._next_runnable_task("demo") is None
    joined = "\n".join(fake_sql.statements)
    assert "pr_open" in joined


@pytest.mark.parametrize("explicit_merged", [False, "false"])
def test_next_runnable_task_blocks_contradictory_merged_state_replacement_pr(fake_sql, tmp_path, explicit_merged):
    project, replacement, feature_commit = _make_source_delivery_repo(tmp_path, merged_to_base=True)
    metadata = _source_delivery_metadata(feature_commit, pr_state="merged")
    metadata["source_delivery"]["pr"]["merged"] = explicit_merged
    replacement["metadata"] = metadata
    dep = {
        "project_id": "demo",
        "task_id": "task-old",
        "status": "superseded",
        "metadata": {"replacement_task_id": "task-replacement"},
    }
    candidate = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-downstream",
        "status": "todo",
        "dependencies": ["task-old"],
    }
    fake_sql.rows_results = [[dep, replacement, candidate], [candidate]]
    fake_sql.one_results = [project]

    assert factory_pg._next_runnable_task("demo") is None
    joined = "\n".join(fake_sql.statements)
    assert "pr_contradictory" in joined


def test_next_runnable_task_blocks_replacement_pr_without_head_commit(fake_sql, tmp_path):
    project, replacement, feature_commit = _make_source_delivery_repo(tmp_path, merged_to_base=True)
    metadata = _source_delivery_metadata(feature_commit)
    metadata["source_delivery"]["pr"].pop("head_commit")
    replacement["metadata"] = metadata
    dep = {
        "project_id": "demo",
        "task_id": "task-old",
        "status": "superseded",
        "metadata": {"replacement_task_id": "task-replacement"},
    }
    candidate = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-downstream",
        "status": "todo",
        "dependencies": ["task-old"],
    }
    fake_sql.rows_results = [[dep, replacement, candidate], [candidate]]
    fake_sql.one_results = [project]

    assert factory_pg._next_runnable_task("demo") is None
    joined = "\n".join(fake_sql.statements)
    assert "pr_head_missing" in joined


def test_next_runnable_task_blocks_replacement_pr_without_base_branch(fake_sql, tmp_path):
    project, replacement, feature_commit = _make_source_delivery_repo(tmp_path, merged_to_base=True)
    metadata = _source_delivery_metadata(feature_commit)
    metadata["source_delivery"]["pr"].pop("base_branch")
    replacement["metadata"] = metadata
    dep = {
        "project_id": "demo",
        "task_id": "task-old",
        "status": "superseded",
        "metadata": {"replacement_task_id": "task-replacement"},
    }
    candidate = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-downstream",
        "status": "todo",
        "dependencies": ["task-old"],
    }
    fake_sql.rows_results = [[dep, replacement, candidate], [candidate]]
    fake_sql.one_results = [project]

    assert factory_pg._next_runnable_task("demo") is None
    joined = "\n".join(fake_sql.statements)
    assert "pr_base_missing" in joined


def test_next_runnable_task_blocks_replacement_pr_without_clean_evidence(fake_sql, tmp_path):
    project, replacement, feature_commit = _make_source_delivery_repo(tmp_path, merged_to_base=True)
    metadata = _source_delivery_metadata(feature_commit)
    metadata["source_delivery"]["pr"].pop("mergeable_state")
    replacement["metadata"] = metadata
    dep = {
        "project_id": "demo",
        "task_id": "task-old",
        "status": "superseded",
        "metadata": {"replacement_task_id": "task-replacement"},
    }
    candidate = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-downstream",
        "status": "todo",
        "dependencies": ["task-old"],
    }
    fake_sql.rows_results = [[dep, replacement, candidate], [candidate]]
    fake_sql.one_results = [project]

    assert factory_pg._next_runnable_task("demo") is None
    joined = "\n".join(fake_sql.statements)
    assert "pr_clean_missing" in joined


def test_next_runnable_task_blocks_missing_replacement_pr(fake_sql, tmp_path):
    project, replacement, feature_commit = _make_source_delivery_repo(tmp_path, merged_to_base=True)
    metadata = _source_delivery_metadata(feature_commit)
    metadata["source_delivery"].pop("pr")
    replacement["metadata"] = metadata
    dep = {
        "project_id": "demo",
        "task_id": "task-old",
        "status": "superseded",
        "metadata": {"replacement_task_id": "task-replacement"},
    }
    candidate = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-downstream",
        "status": "todo",
        "dependencies": ["task-old"],
    }
    fake_sql.rows_results = [[dep, replacement, candidate], [candidate]]
    fake_sql.one_results = [project]

    assert factory_pg._next_runnable_task("demo") is None
    joined = "\n".join(fake_sql.statements)
    assert "pr_missing" in joined


def test_next_runnable_task_blocks_dirty_replacement_pr(fake_sql, tmp_path):
    project, replacement, feature_commit = _make_source_delivery_repo(tmp_path, merged_to_base=True)
    metadata = _source_delivery_metadata(feature_commit)
    metadata["source_delivery"]["pr"]["mergeable_state"] = "dirty"
    replacement["metadata"] = metadata
    dep = {
        "project_id": "demo",
        "task_id": "task-old",
        "status": "superseded",
        "metadata": {"replacement_task_id": "task-replacement"},
    }
    candidate = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-downstream",
        "status": "todo",
        "dependencies": ["task-old"],
    }
    fake_sql.rows_results = [[dep, replacement, candidate], [candidate]]
    fake_sql.one_results = [project]

    assert factory_pg._next_runnable_task("demo") is None
    joined = "\n".join(fake_sql.statements)
    assert "pr_dirty" in joined


def test_dependency_increment_blockers_rejects_option_like_branch_before_fetch(fake_sql, monkeypatch, tmp_path):
    repo = tmp_path / "repo"
    worktree = tmp_path / "worktree"
    repo.mkdir()
    worktree.mkdir()
    task = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-replacement",
        "status": "done",
        "branch": "--upload-pack=touch /tmp/factory-pwned",
        "worktree_path": str(worktree),
        "metadata": _source_delivery_metadata("abc123"),
    }
    project = {
        "project_id": "demo",
        "repo_path": str(repo),
        "base_branch": "main",
        "metadata": {"repo_strategy": {"primary_repo_path": str(repo), "base_branch": "main"}},
    }
    calls: list[list[str]] = []

    def record_git(_repo_path, args, *, timeout=120):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    monkeypatch.setattr(factory_pg, "_run_git", record_git)

    assert factory_pg._dependency_increment_blockers(task, project) == ["unverified_branch_metadata"]
    assert not any("--upload-pack" in " ".join(args) for args in calls)


@pytest.mark.parametrize("base_branch", _UNSAFE_BASE_BRANCHES)
def test_dependency_increment_blockers_rejects_unsafe_base_branch_before_fetch(fake_sql, monkeypatch, tmp_path, base_branch):
    repo = tmp_path / "repo"
    worktree = tmp_path / "worktree"
    repo.mkdir()
    worktree.mkdir()
    task = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-replacement",
        "status": "done",
        "branch": "factory/demo/task-replacement",
        "worktree_path": str(worktree),
        "metadata": _source_delivery_metadata("abc123"),
    }
    project = _project_with_base_branch(
        {
            "project_id": "demo",
            "repo_path": str(repo),
            "metadata": {"repo_strategy": {"primary_repo_path": str(repo), "base_branch": "main"}},
        },
        base_branch,
    )
    calls: list[list[str]] = []

    def record_git(_repo_path, args, *, timeout=120):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    monkeypatch.setattr(factory_pg, "_run_git", record_git)

    assert factory_pg._dependency_increment_blockers(task, project) == ["unverified_base_branch_metadata"]
    assert calls == []


def test_dependency_increment_blockers_accepts_main_base_branch(fake_sql, tmp_path):
    project, replacement, _feature_commit = _make_source_delivery_repo(tmp_path, merged_to_base=True)

    assert factory_pg._dependency_increment_blockers(replacement, project) == []


@pytest.mark.parametrize("branch", _BASE_ALIAS_OR_PSEUDO_REFS)
def test_dependency_increment_blockers_rejects_base_alias_and_pseudoref_before_fetch(fake_sql, monkeypatch, tmp_path, branch):
    repo = tmp_path / "repo"
    worktree = tmp_path / "worktree"
    repo.mkdir()
    worktree.mkdir()
    task = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-replacement",
        "status": "done",
        "branch": branch,
        "worktree_path": str(worktree),
        "metadata": _source_delivery_metadata("abc123"),
    }
    project = {
        "project_id": "demo",
        "repo_path": str(repo),
        "base_branch": "main",
        "metadata": {"repo_strategy": {"primary_repo_path": str(repo), "base_branch": "main"}},
    }
    calls: list[list[str]] = []

    def record_git(_repo_path, args, *, timeout=120):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    monkeypatch.setattr(factory_pg, "_run_git", record_git)

    assert factory_pg._dependency_increment_blockers(task, project) == ["unverified_branch_metadata"]
    assert calls == []


@pytest.mark.parametrize("branch", _BASE_ALIAS_OR_PSEUDO_REFS)
def test_increment_integration_required_rejects_base_alias_and_pseudoref(branch):
    task = {
        "project_id": "demo",
        "task_id": "task-1",
        "status": "review_ready",
        "branch": branch,
        "worktree_path": "/tmp/factory-worktree",
        "metadata": {},
    }
    project = {
        "project_id": "demo",
        "repo_path": "/tmp/factory-repo",
        "base_branch": "main",
        "metadata": {"repo_strategy": {"primary_repo_path": "/tmp/factory-repo", "base_branch": "main"}},
    }

    assert factory_pg._increment_integration_required(task, project, "done") is False


@pytest.mark.parametrize("base_branch", _UNSAFE_BASE_BRANCHES)
def test_increment_integration_required_rejects_unsafe_base_branch(base_branch):
    task = {
        "project_id": "demo",
        "task_id": "task-1",
        "status": "review_ready",
        "branch": "factory/demo/task-1",
        "worktree_path": "/tmp/factory-worktree",
        "metadata": {},
    }
    project = _project_with_base_branch(
        {
            "project_id": "demo",
            "repo_path": "/tmp/factory-repo",
            "metadata": {"repo_strategy": {"primary_repo_path": "/tmp/factory-repo", "base_branch": "main"}},
        },
        base_branch,
    )

    assert factory_pg._increment_integration_required(task, project, "done") is False


@pytest.mark.parametrize("base_branch", _UNSAFE_BASE_BRANCHES)
def test_integrate_increment_to_base_rejects_unsafe_base_branch_before_git(fake_sql, monkeypatch, tmp_path, base_branch):
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    task = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-1",
        "status": "review_ready",
        "branch": "factory/demo/task-1",
        "worktree_path": str(worktree),
        "metadata": {},
    }
    project = _project_with_base_branch(
        {
            "project_id": "demo",
            "repo_path": str(tmp_path / "repo"),
            "metadata": {"repo_strategy": {"primary_repo_path": str(tmp_path / "repo"), "base_branch": "main"}},
        },
        base_branch,
    )
    fake_sql.one_results = [task]
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: project)
    calls: list[list[str]] = []

    def record_git(_repo_path, args, *, timeout=120):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    monkeypatch.setattr(factory_pg, "_run_git", record_git)

    with pytest.raises(factory_pg.IncrementIntegrationError, match="unverified base branch metadata"):
        factory_pg._integrate_increment_to_base("task-1", actor="qa", final_status="done")
    assert calls == []


@pytest.mark.parametrize("branch", _BASE_ALIAS_OR_PSEUDO_REFS)
def test_integrate_increment_to_base_rejects_base_alias_and_pseudoref_before_git(fake_sql, monkeypatch, tmp_path, branch):
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    task = {
        "project_id": "demo",
        "lane_id": "lane",
        "task_id": "task-1",
        "status": "review_ready",
        "branch": branch,
        "worktree_path": str(worktree),
        "metadata": {},
    }
    project = {
        "project_id": "demo",
        "repo_path": str(tmp_path / "repo"),
        "base_branch": "main",
        "metadata": {"repo_strategy": {"primary_repo_path": str(tmp_path / "repo"), "base_branch": "main"}},
    }
    fake_sql.one_results = [task]
    monkeypatch.setattr(factory_pg, "_project", lambda project_id: project)
    calls: list[list[str]] = []

    def record_git(_repo_path, args, *, timeout=120):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    monkeypatch.setattr(factory_pg, "_run_git", record_git)

    with pytest.raises(factory_pg.IncrementIntegrationError, match="unverified branch metadata"):
        factory_pg._integrate_increment_to_base("task-1", actor="qa", final_status="done")
    assert calls == []


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

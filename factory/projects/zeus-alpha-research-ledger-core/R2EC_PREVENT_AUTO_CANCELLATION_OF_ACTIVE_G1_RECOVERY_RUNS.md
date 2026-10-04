---
document_type: active_g1_recovery_auto_cancellation_guard
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2ec-prevent-auto-cancellation-of-active
run_id: run-1788345466-f118b673
phase: g1_recovery
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending
owner: codex-builder
base_ref: origin/main
base_sha: a7e3a54f7ee54e27b4fbdc7ffa2e6808ece0f872
branch: factory/zeus-alpha-research-ledger-core/inc-101-r2ec-prevent-auto-cancellation-o
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-101-r2ec-prevent-auto-cancellation-o
created_at: 2026-09-02T10:46:21Z
---

# R2ec — prevent auto-cancellation of active G1 recovery runs

## Scope and boundary

R2ec is a bounded Factory control-plane reconciliation repair. It changes only:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_control_plane_refactor.py`
- project-local Factory evidence under `factory/projects/zeus-alpha-research-ledger-core/`

No Alpha Ledger product/runtime code, provider/model/auth config, database migration, tool registration, scheduler, deployment, credential access, messaging connector, external runtime, primary checkout mutation, reviewed G1 frontmatter mutation, direct SQL, merge, Vonash, Magnus, VAOS, RAG/KB, broker, trading, risk, paper/live activation, or external-system operation is authorized or performed by this increment.

Factory DB interaction for this run stayed on canonical Factory CLI surfaces: sanctioned `factory status`, `factory project resolve-state`, and final `factory gate record` evidence only. No ad-hoc `psql`/driver writes were used.

## G1 documents read before implementation

The required documentation entrypoint and applicable G1/project docs read for this increment were:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`

The assignment prompt's G1 snapshot named 10 `missing=reviewed` blockers. Canonical current-source status readbacks from this assigned worktree report 14/14 required G1 rows non-blocking; the blocker snapshot remains stale projection/audit context for this control-plane repair.

## RED reproduction

Command:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k test_reconcile_project_preserves_active_reconciliation_run_when_anomaly_clears -v`

Pre-fix result:

- Exit `1`.
- Focused regression failed at `assert result["reconciliation_tasks_cancelled"] == 0` with `assert 1 == 0`.
- The fixture reproduced a G1 recovery reconciliation task in `status=running` with a live `factory.task_runs` row in `status=running`, PR #151/candidate SHA/gate evidence in metadata, and cleared current `reconciliation_findings=[]`. The pre-fix reconciler still appended the `[factory-reconciler] Reconciliation anomaly resolved; task auto-cancelled` path and cancelled the task while leaving the run active.

## Implementation summary

`cancel_resolved_reconciliation_tasks()` now checks `factory.task_runs` for queued/running rows bound to candidate reconciliation task IDs before emitting the auto-cancel update. Any resolved reconciliation task with a live queued/running run is filtered out of the cancellation set, preserving the task row, run row, result summary, PR-first candidate metadata, and gate evidence until the worker reaches a supported terminal path such as `mark_run_finished()` / `close_task()`.

Resolved reconciliation tasks with no live run remain eligible for the existing auto-cancel cleanup, so stale unworked reconciliation backlog can still clear once the canonical anomaly is gone.

## GREEN validation

Focused GREEN:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k test_reconcile_project_preserves_active_reconciliation_run_when_anomaly_clears -v`

Result: 1 selected test passed, 0 failed.

Related Factory control-plane regression set:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_orchestrator_tick.py`

Result: 3 files, 331 tests passed, 0 failed.

Diff hygiene:

`git diff --check`

Result: exit 0, no whitespace errors.

## Canonical status/readback evidence

Final current-source status after commit:

`/home/jean/Projects/hermes-agent-original/venv/bin/python -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2ec-status-final.json`

Readback summary:

- `/tmp/r2ec-status-final.json` size: 4,867,174 bytes.
- `db_backend=agent_core_postgres`.
- Project status: `active`.
- Source root: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-101-r2ec-prevent-auto-cancellation-o`.
- Active metadata `reconciliation_anomalies=[]`.
- Current required G1 rows: `g1_required=14`, `blockers=0`.
- Active runs: 1, this R2ec run `run-1788345466-f118b673` on task `zeus-alpha-research-ledger-core-r2ec-prevent-auto-cancellation-of-active` (`status=running`, PID 3360617).
- Focused task coherence: R2ec task is `status=running`, `evidence_status=missing`, and the bound run is `status=running`; the historical R2ea task is no longer represented as an active run and reads back as `status=review_ready`, `evidence_status=present`.

Final canonical resolve-state after commit:

`/home/jean/Projects/hermes-agent-original/venv/bin/python -m hermes_cli.main factory project resolve-state zeus-alpha-research-ledger-core --json > /tmp/r2ec-resolve-state-final.json`

Readback summary:

- `/tmp/r2ec-resolve-state-final.json` size: 69,804 bytes.
- `action=resolve-state`, `project_id=zeus-alpha-research-ledger-core`, `status=active`.
- `active_runs=1`.
- `reconciliation_tasks_cancelled=0`.
- `anomalies=[]`.
- `monitor={"checked":1,"expired_queued_runs_recovered":0,"finalized_dead_without_exit":0,"finalized_from_stale_semantic_marker":0,"finished":0,"orphan_inflight_repaired":0}`.
- `supervisor={"health":"green","project_id":"zeus-alpha-research-ledger-core","repairs":[],"violations":[]}`.

Intermediate pre-final readback had still exposed the historical R2ea cancelled-task/running-run pair that triggered this rework; the final canonical status above no longer reports that pair as active. This R2ec repair is still intentionally non-retroactive: it prevents future auto-cancellation of live reconciliation runs and leaves any already-finished/failed historical rows to their canonical run finalization or independent review path.

## Delivery and review handoff

R2ec remains PR-first. This artifact is implementation evidence only and is `reviewed: pending` until a distinct reviewer performs independent exact-SHA review of the final pushed PR head. This worker must not self-approve, merge, deploy, write direct SQL, mutate primary checkout, force-push/rewrite unrelated refs, execute external runtimes, or dispatch ALR product/trading work.

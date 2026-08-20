---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2dz-docs-first-dispatcher-recovery-for-
phase: documentation
status: implemented_pending_pr_review
validated: yes
reviewed: pending
worker_profile: codex-builder
engine: codex
branch: factory/zeus-alpha-research-ledger-core/inc-001-r2dz-docs-first-dispatcher-recov
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2dz-docs-first-dispatcher-recov
---

# R2dz — docs-first dispatcher recovery for documentation task selection

## Scope and boundary

R2dz is a bounded Factory control-plane repair. It changes only Factory dispatcher classification/selection code, focused regression tests, and project-local evidence under `factory/projects/zeus-alpha-research-ledger-core/`.

This increment does not implement ALR product/runtime logic, deploy, mutate the primary checkout, write direct SQL, change credentials, call external runtimes, or authorize Vonash/Magnus/VAOS/RAG/KB/broker/trading/risk/paper/live activity.

## Canonical G1 inputs read

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DL_G1_DOCUMENTATION_DISPATCH_VALIDATOR_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DH_DOCS_FIRST_CURRENT_BASE_G1_REVIEW_STATE_DISPATCH_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DI_DOCS_FIRST_FAIL_CLOSED_REVIEW_TERMINALIZATION_AND_DISPATCH_REPAIR.md`

## RED reproduction

Command:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k docs_first_dispatch_selects_documentation_recovery_before_review_ready_and_product_work -v --tb=short
```

Observed RED before repair: `1 failed, 157 deselected`; assertion failed because `_next_runnable_task(...)` returned `None` instead of the dependency-ready documentation recovery row. The fixture reproduced the claimed-null loop with:

- `review_ready` downstream quality-review work present;
- higher-priority product implementation work present;
- `docs_ready=false` preflight tuple;
- a dependency-ready `phase=documentation` recovery task.

## Repair summary

- Added `_is_docs_first_recovery_task()` so docs-first recovery eligibility is driven by stable phase values (`documentation`, `docs`, `g0*`, `g1*`) and explicit Factory metadata flags rather than broad prose such as `quality review`, `security`, or `finalized` appearing in descriptions.
- `review_ready` and `qa_ready` are no longer treated as live in-flight worker statuses inside `_has_in_flight_increment`; they remain deferred validation queues that block product work.
- `_next_runnable_task()` now skips non-docs-first candidates while deferred review/QA queues exist, but still selects documentation/reconciliation repair candidates before product, review, QA, security, delivery, or handoff work.
- `claim_next_task()` uses the narrower live-worker predicate so docs/reconciliation repair rows are not hidden by queued review/QA rows.
- `force_tick()` attempts task dispatch before review dispatch. The task path itself falls through to review when no documentation/reconciliation repair candidate is eligible, preserving fail-closed product gating.

## GREEN validation

Focused GREEN:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k docs_first_dispatch_selects_documentation_recovery_before_review_ready_and_product_work -v --tb=short
```

Result: `1 tests passed, 0 failed`.

Related regression GREEN:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'docs_first_dispatch_selects_documentation_recovery_before_review_ready_and_product_work or validation_readiness_allows_dependency_ready_documentation_recovery_with_historical_finalized_wording or dispatch_validation_readiness_does_not_deadlock_deploy_prerequisite or dispatch_preflight_blocks_product_execution_without_docs' -v --tb=short
```

Result: `4 tests passed, 0 failed`.

Broader Factory control-plane GREEN:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_increment_integration.py -v
```

Result: `3 files, 304 tests passed, 0 failed`.

Whitespace validation:

```bash
git diff --check
```

Result: exit `0`.

## Canonical Factory CLI evidence

Status before/after code was read only through the approved Factory CLI:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2dz-status-before.json
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2dz-status-after-code.json
```

After-code readback highlights:

- `db_backend=agent_core_postgres`.
- R2dz task status: `running`.
- R2dz phase: `documentation`.
- R2dz owner/engine: `codex-builder` / `codex`.
- R2dz branch/worktree: `factory/zeus-alpha-research-ledger-core/inc-001-r2dz-docs-first-dispatcher-recov` / `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2dz-docs-first-dispatcher-recov`.
- R2dz `claimed_by=factory-force-tick`.
- R2dz task run: `run-1787232398-bcd2ee36`, status `running`, worker `codex-builder`, engine `codex`, started `2026-08-20T13:26:38.993929+00:00`.

Forced tick evidence:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory project tick zeus-alpha-research-ledger-core --json > /tmp/r2dz-forced-tick-after-code.json
```

Result:

- CLI exited `0`.
- `db_backend=agent_core_postgres`.
- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2dz-docs-first-dispatcher-recov`.
- `factory_orchestrator_script=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2dz-docs-first-dispatcher-recov/scripts/factory/factory_orchestrator_tick.py`.
- `factory_project_action_delegated=false`.
- `claimed=null`, `spawned_worker=null`, with `counts.active_runs=1`.

Source-backed explanation: the forced tick did not spawn a second worker because the canonical DB already had this R2dz documentation worker running. The same status readback shows the active documentation task was claimed by `factory-force-tick` and is running under run `run-1787232398-bcd2ee36`.

## Delivery status

Delivery remains PR-first. The final Zeus-signed commit SHA, PR URL, and independent review result must be recorded after the branch is pushed and the `agent:zeus` PR is opened. This artifact itself is not a merge, deployment, task-status mutation, or self-approval.

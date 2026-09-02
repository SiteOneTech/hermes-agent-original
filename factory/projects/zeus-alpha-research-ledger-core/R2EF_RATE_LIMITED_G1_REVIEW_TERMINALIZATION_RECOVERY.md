---
title: R2ef rate-limited G1 review terminalization recovery
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2ef-repair-rate-limited-g1-review-termi
phase: g1_recovery
owner_profile: codex-builder
reviewer_profile: quality-reviewer
status: implementation_ready_for_pr_first_review
candidate_code_sha: 7e67f40385212ec3e3aa1df8372e0b7de16ca71d
base_sha: d8194b268807ef2bb701b6d3f4302967a9e5e5be
branch: factory/zeus-alpha-research-ledger-core/inc-105-r2ef-repair-rate-limited-g1-revi
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-105-r2ef-repair-rate-limited-g1-revi
factory_db_source_of_truth: Agent Core Postgres factory.* via Factory CLI
reviewed: pending
pull_request: https://github.com/SiteOneTech/hermes-agent-original/pull/161
---

# R2ef — rate-limited G1 review terminalization recovery

## Scope

Bounded Factory control-plane repair only. This increment changes Factory scheduler/reconciler behavior and hermetic tests. It does not change Alpha Ledger product/runtime, credentials, deploy, messaging, trading/risk, paper/live execution, or the primary checkout.

## Canonical inputs read

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DB_CURRENT_ORIGIN_G1_REVIEWED_STATE_PR_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DC_BOUNDED_G1_REVIEWED_STATE_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R5_FAIL_CLOSED_REVIEW_TERMINALIZATION_RECOVERY.md`

## RED reproduction

Focused hermetic RED test added:

- `tests/hermes_cli/test_factory_increment_integration.py::test_force_tick_recovers_failed_rate_limited_g1_review_and_dispatches_retry`

The RED case models the exact failure class with structured task/run/gate state:

- same-project task in `phase=g1_recovery`
- task is already positive-terminal `done`
- latest independent review run has `run_type=review`, `status=failed`, `exit_code=1`
- output contains three MiniMax HTTP 429 retry failures
- there is no task-bound passed quality gate
- ten required G1 documents are blocking
- normal product/ALR/QA/security/delivery candidates are present but fail closed

Before the repair, the recovery SQL only considered `review` runs with `status=succeeded` and `exit_code=0`, so this failed review run was invisible to reconciliation and forced tick could strand recovery with `claimed=null`.

## GREEN repair

Implementation changed:

- `hermes_cli/factory_pg.py` around `_recover_false_terminalized_review_runs()`

The reconciler now considers the latest task-bound independent review run when it is either:

1. a positive-zero process that still contains runtime-failure evidence, or
2. a failed process with non-zero review exit state and no task-bound passed review gate.

For failed review runs, Python logic requires `_review_runtime_failure_reason(output_summary)` to be present before reopening the terminal task. This preserves the explicit state contract: task/run/gate state controls eligibility, and title/status prose cannot make a failed/rate-limited review terminalize as done.

The recovery writes structured metadata:

- `false_review_terminalization_run_id`
- `false_review_terminalization_recovered_at`
- `false_review_terminalization_recovered_by`
- `false_review_terminalization_reason`
- `review_failure_reason`
- `review_requeue_reason`
- `runtime_contract=review_success_requires_nonempty_runtime_output_and_task_bound_passed_gate`

After recovery, the scheduler can claim the eligible same-project `g1_recovery` / documentation-review task while product, ALR, QA/security, and delivery candidates remain blocked by dispatch preflight.

## Test evidence

All focused tests were run through `scripts/run_tests.sh` with the approved wrapper and no package installs:

- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py`
  - Result: exit 0
  - Summary: 1 file, 148 tests passed, 0 failed in 9.2s
  - Log: `/tmp/r2ef-test-increment.log`
- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py`
  - Result: exit 0
  - Summary: 1 file, 161 tests passed, 0 failed in 11.7s
  - Log: `/tmp/r2ef-test-control-plane.log`

`git diff --check` returned exit 0 before the code commit.

## Factory CLI readbacks

No direct SQL, psql, psycopg2, ad-hoc DB script, credential change, merge, deploy, product execution, messaging, or trading/risk/paper/live action was used.

Readbacks captured with the sanctioned Factory CLI path and summarized with local JSON tooling:

- `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2ef-status-after-code.json`
  - `project_id=zeus-alpha-research-ledger-core`
  - `project.status=active`
  - `autonomous_enabled=true`
  - `doc_blockers=0` at this readback
  - `metadata.reconciliation_anomalies=[]`
  - R2ef task before live tick readback: `status=running`, `phase=g1_recovery`, `owner_profile=codex-builder`, assigned branch matched.
- `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory project resolve-state zeus-alpha-research-ledger-core --json > /tmp/r2ef-resolve-after-kill.json`
  - `active_runs=1`
  - `unresolved_validation_tasks_count=0`
  - `unvalidated_required_docs_count=0`
  - `blockers_count=14`
  - `status=active`
  - `claimed=null`
- `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory project tick zeus-alpha-research-ledger-core --json > /tmp/r2ef-forced-tick-after-code.json`
  - Readback showed `false_review_terminalization_recoveries=0` on the current canonical DB state because G1 document blockers were already cleared at readback time.
  - The tick claimed/spawned the separate R2df-R39 task (`run-1788377626-6fea556b`, worker pid 2686376). This was outside the requested single-increment scope; I immediately terminated the spawned worker process and did not continue that increment.
- `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2ef-status-after-kill.json`
  - `active_runs=2`
  - R2ef task readback after the live tick/reconcile side effect: `status=cancelled`
  - R2df-R39 task readback: `status=running` until monitor reconciliation records the terminated worker failure.

The hermetic tests above are the acceptance evidence for the red-G1 dispatch class. The live DB no longer presented the original ten-document blocker state at the time of this run, so the live tick readback cannot reproduce the historical `unvalidated_required_docs` state without unsafe/manual DB mutation.

## Delivery status

Code candidate SHA: `7e67f40385212ec3e3aa1df8372e0b7de16ca71d`.
PR-first delivery readback: `https://github.com/SiteOneTech/hermes-agent-original/pull/161` was opened against `main`; readback showed head `9dcad29af33d7cecccf7284b2ea3ba1600c3a1d9`, state `OPEN`, merge state `CLEAN`, and no independent review decision yet.

Factory gate readback from `/tmp/r2ef-status-after-gates.json`:

- Gate `1184`: `implementation` / `passed`, reviewer `codex-builder`, task-bound to `zeus-alpha-research-ledger-core-r2ef-repair-rate-limited-g1-review-termi`.
- Gate `1185`: `test` / `passed`, reviewer `codex-builder`, task-bound to `zeus-alpha-research-ledger-core-r2ef-repair-rate-limited-g1-review-termi`.

This artifact records the code candidate SHA. The final branch head after adding this evidence file cannot self-embed its own SHA; the final PR/gate/readback should be treated as the exact SHA source for independent quality review.

Remaining PR-first step:

1. obtain independent exact-SHA quality review by a reviewer different from `codex-builder`
2. no merge/deploy until explicit approved review path passes

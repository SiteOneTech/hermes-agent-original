---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2f1-current-origin-g1-document-status-p
phase: g1_recovery
status: implemented_pending_independent_review
validated: yes
reviewed: pending_independent_review
owner: codex-builder
run_id: run-1788430467-02737685
---

# R2f1 — current-origin G1 document-status projection repair

## Scope

This increment is limited to the Factory control plane and tests for the Zeus Alpha Research Ledger Core Factory project. It does not modify ledger product behavior, runtime deployment, credentials, messaging, trading/risk, paper/live activation, or production state.

## Root cause reproduced

The stale projection class is a mismatch between current git document evidence and persisted/documentary Factory projection rows:

- The current configured origin/base document rows can prove every required G1 document is reviewed.
- Persisted metadata projections such as `document_status`, `documents`, or `factory_documents` can still carry old G1 rows with `reviewed=false` / `blocking=true`.
- Readback/reconciliation must clear those stale projection keys only after current G1 rows are clean; genuinely red G1 remains fail-closed.

## RED evidence

Command run from the assigned isolated worktree with the approved test wrapper and existing primary venv Python:

`scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k status_projection_discards_persisted_stale_g1_rows_when_current_origin_reviewed -v --tb=long`

Result before production fix: failed as expected. The new regression test showed current configured-base G1 rows were non-blocking and `reviewed=True`, but `metadata.document_status` still remained present with stale `reviewed=False` rows.

## Repair

Changed `hermes_cli/factory_pg.py` so stale persisted G1 document projections are detected and cleared when the current configured-base document-status projection is green:

- `metadata.document_status`
- `metadata.documents`
- `metadata.factory_documents`

The repair is intentionally bounded. It only marks those metadata projection keys stale when they contain G1 rows with blocking/false/missing validated or reviewed state, and only clears them after current G1 rows are clean. It preserves fail-closed behavior for genuinely red G1 and runtime/product dispatch, including primary-checkout identity blockers.

## GREEN evidence

Commands run from the assigned isolated worktree:

1. `scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k status_projection_discards_persisted_stale_g1_rows_when_current_origin_reviewed -v --tb=long`
   - Result: 1 selected test passed, 0 failed.

2. `scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_increment_integration.py -k 'status_projection_discards_persisted_stale_g1_rows_when_current_origin_reviewed or document_status_uses_configured_origin_base_when_primary_checkout_stale or document_status_rejects_stale_primary_even_when_primary_docs_are_ready or status_prefers_configured_base_source_when_invoked_from_stale_primary_root or g1_recovery_metadata_keeps_validation_and_reporting_work_fail_closed or force_tick_uses_explicit_g1_recovery_metadata_before_review_when_docs_red or claim_next_task_claims_r2df_r23_phase_g1_recovery_before_validation_deadlock or claim_next_task_primary_runtime_rejection_routes_g1_recovery_before_product' -v --tb=short`
   - Result: 8 selected tests passed, 0 failed.

3. `scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -v --tb=short`
   - Result: 162 tests passed, 0 failed.

4. `git diff --check`
   - Result: passed; no whitespace errors reported.

## Factory readback evidence

Approved Factory status command run from the assigned isolated worktree:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`

Readback summary captured in `/tmp/r2f1-status-after-current.json`:

- `db_backend=agent_core_postgres`
- `project_status=active autonomy=true`
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-104-r2f1-current-origin-g1-document`
- `factory_status_delegated=false`
- `g1_total=14`
- `g1_blocking=0`
- `g1_sources=configured_base_ref`
- `metadata_anomalies=`
- `active_runs=0`

Resolve-state/tick were not executed here because this worker's hard runtime rule limits Factory DB operations to the approved `factory status` and `factory gate record` commands. The exact source-backed technical cause is therefore recorded as: current worktree status readback is already green for G1 and has no active runs, while invoking the old primary checkout still reports stale `unvalidated_required_docs`; this code change prevents that stale persisted-row projection class after merge/review without mutating the primary checkout.

## Delivery boundary

This is PR-first only. Required follow-up after push: open a PR labeled `agent:zeus`, request/obtain independent exact-SHA review, and do not merge/deploy/activate from this worker.

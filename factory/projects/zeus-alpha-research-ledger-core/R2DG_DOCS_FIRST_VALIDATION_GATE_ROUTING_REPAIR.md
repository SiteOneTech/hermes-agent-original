---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2dg-docs-first-validation-gate-routing-
phase: documentation
status: implemented
validated: yes
reviewed: pending_independent_quality_review
owner: codex-builder
reviewer: quality-reviewer
base_commit: 0c0cb6517d62b5402fe06b1939856aa9b1a18392
branch: factory/zeus-alpha-research-ledger-core/inc-000-r2dg-docs-first-validation-gate
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-000-r2dg-docs-first-validation-gate
---

# R2dg — docs-first validation-gate routing repair

## Scope

Bounded Factory control-plane repair for the R2df docs-first routing deadlock. The change is confined to:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_increment_integration.py`
- this project-local evidence artifact

No product/runtime code, direct SQL, primary checkout mutation, deploy, credential, messaging, broker, trading, risk, paper/live, Vonash, Magnus, VAOS, or RAG/KB path is touched.

## Canonical reproduction evidence

Commands were executed from the assigned worktree with the canonical Hermes CLI wrapper in `/home/jean/Projects/hermes-agent-original/venv/bin/hermes`.

1. Status readback before/after code:
   - Command: `/home/jean/Projects/hermes-agent-original/venv/bin/hermes factory status zeus-alpha-research-ledger-core --json`
   - Evidence files: `/tmp/r2dg-status-before.json` and `/tmp/r2dg-status-after-code.json`
   - Readback: `db_backend=agent_core_postgres`, project `active`, autonomy `true`, G1 required blockers `10`, active `reconciliation_anomalies=["unvalidated_required_docs"]`.
   - Current assigned run is active after claim: `run-1787321309-2bf71dd5` for this R2dg repair task. The immediately preceding canonical status events preserve the no-worker-dispatch failure that selected R2df and rejected it before this repair was claimed.

2. Exact stale dispatch path in status events:
   - Event `210803`, `2026-08-21T14:05:03.049565+00:00`, `dispatch_preflight_denied`, task `zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation`, actor `factory-dispatcher`.
   - Blockers include `unresolved_validation_tasks` plus downstream validation rows: R2cy-R1 quality review `ready`, ALR-061 `todo`, ALR-062 `todo`, ALR-063 `todo`, ALR-070 `todo`, and stale superseded historical validation rows.
   - Event `210809`, `2026-08-21T14:08:29.592463+00:00`, then claims this R2dg repair task, confirming the R2df denial happened immediately before the assigned run became active.

3. Resolve-state readback:
   - Command: `/home/jean/Projects/hermes-agent-original/venv/bin/hermes factory project resolve-state zeus-alpha-research-ledger-core --json`
   - Evidence file: `/tmp/r2dg-resolve-state-before.json`
   - Readback: action `resolve-state`, project `active`, anomalies `['unvalidated_required_docs']`, supervisor health `green`, with existing blocked reconciliation rows preserved.

4. Tick readback during this run:
   - Command: `/home/jean/Projects/hermes-agent-original/venv/bin/hermes factory project tick zeus-alpha-research-ledger-core --json`
   - Evidence file: `/tmp/r2dg-tick-before.json`
   - Readback: `claimed=null`, `active_runs=1`, where the active run is this R2dg worker. This explains why live tick cannot create a second no-active-run reproduction after the task has already been claimed; status event `210803` remains the canonical source-backed classifier reproduction.

## Root cause

`_candidate_requires_validation_readiness_before_dispatch()` treated terminal words such as `final gate` and `gate closure` as sufficient evidence that a candidate was final delivery/reporting work. A docs-first documentation/control-plane recovery can legitimately quote those words while describing the broken run it is repairing. When such a task was not explicitly classified as docs/reconciliation recovery, it was held behind unresolved downstream ALR validation rows, creating a circular G1-red validation dependency.

A second part of the same classifier path was that `_is_docs_first_gated_dispatch_task()` only exempted validation-review repairs, not all docs-first repair dispatch tasks. Implementation-run/control-plane repair rows with `codex`/builder fields could therefore still look like product execution to the docs-first preflight sorter.

## Repair

- Added `_is_validation_readiness_terminal_dispatch_task()` so validation readiness uses explicit phase/owner classification for final delivery/reporting (`delivery`, `release`, `final`, `final_report`, `factory-reporter`, `devops-release`) instead of broad terminal-word matching alone.
- Extended `_is_docs_first_repair_dispatch_task()` to classify dependency-ready docs-first repair intent from documentation/G1 signals plus repair/recovery/routing/control-plane/provenance signals, without calling the product-gating matcher recursively.
- Changed `_is_docs_first_gated_dispatch_task()` to exempt the full docs-first repair classifier, not only validation-review repairs.

Result: documentation/reconciliation recovery can be selected before downstream validation rows, while product implementation and final delivery/reporting remain fail-closed.

## RED/GREEN evidence

RED first:

- Command: `scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k docs_first_validation_gate_repair -v`
- Initial result: failed as expected, `assert result is not None` failed because the R2dg-style docs-first validation-gate repair was not claimable and product preflight denial won.

GREEN focused tests:

- Command: `scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k docs_first_validation_gate_repair -v`
- Result after fix: `1 tests passed, 0 failed`.

- Command: `scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_orchestrator_tick.py`
- Result: `156 tests passed, 0 failed`.

- Command: `scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'dispatch_validation_readiness or validation_readiness_allows_dependency' -v`
- Result: `2 tests passed, 0 failed`; this covers deploy-prerequisite/final-report fail-closed behavior and dependency-ready documentation recovery.

- Command: `git diff --check`
- Result: exit `0`.

A broader optional run including all of `tests/hermes_cli/test_factory_control_plane_refactor.py` still has three unrelated existing failures in stale G1 projection tests (`test_unvalidated_required_docs_reconciliation_resolves_from_current_document_status`, `test_reconcile_clears_stale_g1_checkout_projection_when_current_docs_nonblocking`, `test_status_projection_uses_origin_base_not_stale_head_or_task_metadata`). Those failures are outside this increment's touched classifier path and were not changed here.

## Delivery status

This candidate is ready for a Zeus-signed non-draft `agent:zeus` PR from the assigned branch. The PR must record the final pushed candidate SHA and request independent exact-SHA quality review; this worker does not self-approve and does not merge.

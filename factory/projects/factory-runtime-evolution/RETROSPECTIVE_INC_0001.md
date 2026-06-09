# INC-0001 Retrospective — Delivery-hold autoresolvable blocker

## Incident fingerprint

- Project observed: `agent-core-followup-reminders`
- Symptom: `delivery_hold` + `autonomous_enabled=true` + blocked reconciliation/delivery task + no active run + no human question.
- UI action: `Poner autónomo` wrote `autonomous_resume`, but reconcile returned the project to `delivery_hold` and the tick produced `claimed=null`.
- Factory invariant violated: `RED_DELIVERY_HOLD_WITH_BLOCKED_WORK`.

## Root cause

The runtime had sensors but no action authority for this state:

1. `clear_resolved_blockers()` only understood legacy gate-text blockers.
2. Structured reconciliation blockers such as `missing_notion_project` were stored in task metadata but had no resolver.
3. `delivery_hold` was treated as a static state even when the blocker had become objectively resolved.
4. The dashboard resume action only resumed/reconciled; it did not run supervisor repair + force tick + return a diagnostic.

## Reference Patterns Consulted

Reference: n8n
Local file(s):
- `/home/jean/reference-repos/factory-workflow-patterns/n8n/packages/workflow/src/execution-status.ts`
- `/home/jean/reference-repos/factory-workflow-patterns/n8n/packages/@n8n/task-runner/src/task-state.ts`
- `/home/jean/reference-repos/factory-workflow-patterns/n8n/packages/cli/src/active-executions.ts`
Commit: `0db6a4b7d82c`
Pattern borrowed: closed runtime statuses, explicit task lifecycle, active execution discipline, conditional repair instead of silent idle.
Factory invariant affected: `RED_DELIVERY_HOLD_WITH_BLOCKED_WORK`.
Test proving it:
- `tests/hermes_cli/test_factory_canonical_runtime.py::test_factory_contracts_define_runtime_invariants`
- `tests/hermes_cli/test_factory_canonical_runtime.py::test_factory_force_tick_reopens_and_claims_autoresolved_delivery_hold_reconciliation_blocker`
- `tests/hermes_cli/test_factory_canonical_runtime.py::test_factory_control_resume_runs_supervisor_and_force_tick`
- `tests/hermes_cli/test_factory_canonical_runtime.py::test_factory_watchdog_alerts_flags_delivery_hold_autoresolvable_without_human_question`

Reference: Prefect
Local file(s):
- `/home/jean/reference-repos/factory-workflow-patterns/prefect/src/prefect/server/schemas/states.py`
- `/home/jean/reference-repos/factory-workflow-patterns/prefect/src/prefect/server/models/flow_run_states.py`
Commit: `db66b14dbaea`
Pattern borrowed: server/runtime-owned state transitions with metadata, rather than worker prose deciding final state.
Factory invariant affected: structured resolver transitions blocked reconciliation tasks to `review_ready` rather than marking them done.

## Structural fix implemented

- Added `hermes_cli/factory_contracts.py` with closed enums/helpers for project/task/run/gate status and runtime invariants.
- Extended `factory_pg.clear_resolved_blockers()` to resolve structured reconciliation anomalies using deterministic conditions.
- Added L2 `supervisor_health_check(project_id, repair=True)` for invariant detection and safe repair.
- Hardened `control_action(..., "resume")` so `Poner autónomo` now runs resume + supervisor + force tick and returns `claimed`/diagnostic data.
- Added `delivery_hold_autoresolvable_blocked_work` watchdog alert with invariant and recommended action.
- Updated active runtime cron scripts so the orchestrator tick runs supervisor repair before force tick and the daily report includes supervisor/watchdog findings.

## Verification log

- RED verified: focused tests failed before implementation because `factory_contracts` was missing and `force_tick()` did not reopen the blocker.
- GREEN verified: focused tests pass after implementation.
- Full focused file verified: `python3 -m pytest tests/hermes_cli/test_factory_canonical_runtime.py -q` -> `31 passed`.

## Residual / next increments

- INC-0002 should promote more of the runtime status strings to `factory_contracts` and add transition-level tests.
- INC-0003 should introduce a typed operation reducer for Factory state mutations, inspired by n8n `operations-processor.ts`.
- INC-0004 should make L3 daily retrospective create/update Factory Runtime Evolution increments automatically from repeated incident fingerprints.

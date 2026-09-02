# R2d6 — repair recurrent G1 recovery self-denial by unresolved validation history

## Scope

This evidence is project-local for `zeus-alpha-research-ledger-core` and records only the bounded Factory control-plane repair requested for R2d6. It does not change Alpha Ledger product code, runtime dispatch, credentials, deploy targets, trading/risk behavior, paper/live activation, or the primary checkout.

Assigned branch/worktree:

- Branch: `factory/zeus-alpha-research-ledger-core/inc-102-r2d6-repair-recurrent-g1-recover`
- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-102-r2d6-repair-recurrent-g1-recover`
- Base at start of repair: `origin/main` = `63a866d57bda6a1258de6c93d0f244316f298828`; `HEAD` = same; merge-base = same; ahead/behind = `0 0`.

## Root cause

The docs-first dispatch preflight already allowed some phase-explicit G1/documentation recovery tasks to bypass validation-readiness history. The recurring gap was that task phase could also be carried in structured metadata (`task_phase`, `factory_phase`, `dispatch_phase`, `recovery_phase`, or metadata `phase`) while the persisted task row still had a generic implementation phase. In that shape, the dispatcher evaluated the candidate as normal implementation/final-gate work, hit `_validation_task_readiness_findings()`, and denied it because historical validation rows were unresolved.

The denial was self-referential for control-plane recovery: the eligible same-project G1/documentation recovery path was the work required to make red G1 dispatchable again, but it was denied solely due historical validation rows. Product/QA/security/delivery/runtime work must still fail closed while red G1.

## Repair

Implementation in `hermes_cli/factory_pg.py` adds structured phase-signal resolution for G1/documentation recovery routing:

- Normalize explicit task phase from the task row and from metadata keys `dispatch_phase`, `factory_phase`, `phase`, `recovery_phase`, and `task_phase`.
- Use those phase signals in `_has_explicit_g1_or_documentation_recovery_scope()` and `_is_explicit_g1_recovery_task()`.
- Preserve existing product/runtime/reporting/QA/security fail-closed guards, including metadata-scoped product/runtime/direct-SQL/external work.

## RED/GREEN evidence

Focused RED test added in `tests/hermes_cli/test_factory_increment_integration.py`:

- `test_claim_next_task_uses_metadata_phase_for_g1_recovery_before_validation_history`

It reproduces an active project with no active run, `unvalidated_required_docs`, historical blocked/superseded validation rows, a ready R2cy-style review row, downstream ALR validation work, and an eligible same-project candidate whose database phase is generic implementation but whose metadata explicitly says `task_phase=g1_recovery`. Before the repair, the candidate was denied by unresolved validation history. After the repair, it is claimed and no dispatch-preflight denial is recorded for it.

Additional fail-closed regression coverage extends `test_g1_recovery_metadata_scope_keeps_product_runtime_and_external_work_fail_closed` with a metadata-phase product candidate (`ALR-020 product implementation`) so metadata `task_phase=g1_recovery` cannot bypass product gating.

Commands executed from the assigned worktree:

- RED command before implementation:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 HERMES_TEST_WORKERS=1 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'metadata_phase_for_g1_recovery_before_validation_history' -v --tb=short`
  Result: exit 1, focused test failed as expected.

- Focused GREEN:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 HERMES_TEST_WORKERS=1 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'metadata_phase_for_g1_recovery_before_validation_history' -v --tb=short`
  Result: 1 test passed, 0 failed.

- Focused GREEN plus fail-closed product metadata regression:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 HERMES_TEST_WORKERS=1 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'metadata_phase_for_g1_recovery_before_validation_history or g1_recovery_metadata_scope_keeps_product_runtime_and_external_work_fail_closed' -v --tb=short`
  Result: 2 tests passed, 0 failed.

- Related Factory scheduler/control-plane suite:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 HERMES_TEST_WORKERS=1 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_control_plane_refactor.py`
  Result: 300 tests passed, 0 failed.

- Orchestrator/cron Factory tick-control suite:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 HERMES_TEST_WORKERS=1 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_cron_control_plane.py`
  Result: 39 tests passed, 0 failed.

## Canonical Agent Core Factory readback

Canonical status was read via the approved Factory CLI only:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2d6-status-final.json`

Readback summary from `/tmp/r2d6-status-final.json` after recording the implementation gate:

- `db_backend`: `agent_core_postgres`
- project `zeus-alpha-research-ledger-core`: `status=active`, `autonomous_enabled=true`
- `reconciliation_anomalies`: `[]`
- current R2d6 task: `status=running`, `phase=g1_recovery`, `owner_profile=codex-builder`
- implementation gate `1149`: `passed`, reviewer `codex-builder`, task `zeus-alpha-research-ledger-core-r2d6-repair-recurrent-g1-recovery-self-d`
- latest historical denial evidence still includes events `259216`–`259219` with `unresolved_validation_tasks` blockers, plus event `259221` correctly failing closed for `R2cy-R1` with `missing_or_unindexed_docs`.

The earlier post-code/pre-gate snapshot `/tmp/r2d6-status-after.json` recorded the source-backed live limitation as `reconciliation_anomalies=["source_increment_not_integrated"]`. The final approved-CLI readback after the implementation gate records clean project reconciliation metadata; this still does not authorize live worker dispatch or merge.

No live `factory worker dispatch`, direct SQL, product execution, deploy, external runtime, messaging, primary mutation, merge, or activation was executed. Because runtime dispatch was explicitly out of scope, the claim/spawn proof is limited to hermetic tests plus canonical status/gate readback, pending independent exact-SHA review and integration.

## Delivery boundary

Delivery is PR-first only. The branch must be pushed and reviewed independently at the exact final SHA before any merge or runtime dispatch. This evidence document is not an approval gate and does not authorize production, external runtime, product, QA, delivery, trading/risk, paper/live, deploy, credential, direct-SQL, or primary-checkout actions.

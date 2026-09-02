# R2db — repair explicit G1 recovery dispatch starvation

## Scope

This is bounded Factory control-plane evidence for project `zeus-alpha-research-ledger-core` and task `zeus-alpha-research-ledger-core-r2db-repair-explicit-g1-recovery-dispatc` only.

Assigned delivery identity:

- Branch: `factory/zeus-alpha-research-ledger-core/inc-116-r2db-repair-explicit-g1-recovery`
- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-116-r2db-repair-explicit-g1-recovery`
- Base at start of repair: `origin/main` = `a7e3a54f7ee54e27b4fbdc7ffa2e6808ece0f872`; `HEAD` = same; merge-base = same; ahead/behind = `0 0`.
- Run: `run-1788355136-e74f4efc`
- Phase: `g1_recovery`
- Engine: `codex`

This change does not modify Alpha Ledger product behavior, deployment paths, credentials, runtime connectors, primary checkout state, direct SQL state, messaging, trading/risk behavior, or paper/live execution.

## Canonical docs consulted

Required and applicable G1/Factory docs read before implementation:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R43_G1_RECOVERY_SELECTION_STARVATION_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2D6_REPAIR_RECURRENT_G1_RECOVERY_SELF_DENIAL.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DB_CURRENT_ORIGIN_G1_REVIEWED_STATE_PR_RECOVERY.md`

## Root cause

The explicit G1 recovery classifier already required a structured phase/metadata signal before bypassing validation-readiness history. The remaining starvation shape is narrower: a legitimate `phase=g1_recovery` Factory control-plane candidate can document that downstream ALR/product/QA/delivery/runtime work must stay fail-closed while G1 is red. That fail-closed prose can still contain product/runtime scope tokens such as `ALR-020`, `product implementation`, `deploy`, `external runtime`, `direct SQL`, `trading`, `risk`, or `paper/live`.

Before this repair, `_text_without_negative_dispatch_guardrails()` stripped explicit `no`/`must not` guardrail sentences, but it did not strip fail-closed/blocked/gated/denied guardrail sentences. As a result, a phase-explicit G1 recovery task could be misclassified as product/runtime dispatch, then denied by docs-first/validation-readiness preflight. That reproduces the starvation class shown by Agent Core events `260456`-`260460`: zero active runs, red G1 projection/anomaly, explicit G1 candidates denied, and forced tick unable to claim/spawn a recovery worker until a later bounded R2db task was created and claimed.

## Repair

Implementation in `hermes_cli/factory_pg.py` is intentionally small:

- Extend `_text_without_negative_dispatch_guardrails()` so product/runtime words that occur only inside fail-closed, blocked, gated, or denied guardrail chunks are not treated as positive product/runtime scope.
- Keep explicit phase/metadata checks unchanged: G1/documentation recovery eligibility still requires `phase=g1_recovery`, G0/G1/documentation/planning phase, or structured recovery metadata.
- Keep product/runtime/QA/security/delivery/reporting candidates fail-closed while G1 is red; the guardrail stripping only prevents negative control-plane evidence from becoming a false positive product scope.

## RED/GREEN evidence

Focused RED test added in `tests/hermes_cli/test_factory_increment_integration.py`:

- `test_force_tick_claims_r2db_g1_recovery_with_fail_closed_product_guardrail_when_docs_red`

The test reproduces the exact starvation shape hermetically:

- project active/autonomous;
- zero active task runs in the status payload;
- ten required G1 document rows are `exists=true`, `indexed=true`, `committed=true`, `validated=true`, `reviewed=false`, `blocking=true`, `missing=["reviewed"]`;
- active project metadata carries `reconciliation_anomalies=["unvalidated_required_docs"]`;
- an exact R2cy-style `review_ready` quality review is present;
- downstream ALR product, QA, and delivery candidates are ready;
- the bounded R2db task is `phase=g1_recovery` and documents that ALR/product/QA/delivery/runtime work must remain fail-closed.

Before the implementation change, the new focused test failed (exit 1) because `force_tick()` did not claim the explicit G1 recovery task. After the repair, it claims the R2db G1 recovery candidate and never records an `unresolved_validation_tasks` denial for that candidate; direct preflight assertions still return `missing_or_unindexed_docs` for R2cy review, product, QA, and delivery rows.

Commands executed from the assigned worktree:

- RED before implementation:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 HERMES_TEST_WORKERS=1 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k r2db_g1_recovery_with_fail_closed_product_guardrail_when_docs_red -v --tb=short`
  Result: exit 1, focused regression failed as expected.

- Focused GREEN:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 HERMES_TEST_WORKERS=1 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k r2db_g1_recovery_with_fail_closed_product_guardrail_when_docs_red -v --tb=short`
  Result: exit 0, focused regression passed.

- Related Factory scheduler/control-plane suite:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 HERMES_TEST_WORKERS=1 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_control_plane_refactor.py -v --tb=short`
  Result: exit 0; 307 tests passed, 0 failed.

- Orchestrator tick suite:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 HERMES_TEST_WORKERS=1 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -v --tb=short`
  Result: exit 0; 24 tests passed, 0 failed.

- Diff whitespace check:
  `git diff --check`
  Result: exit 0.

## Canonical Agent Core Factory readback

Approved status command only; no direct SQL was used:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2db-inc116-status-after-code.json`

Summary from `/tmp/r2db-inc116-status-after-code.json`:

- `db_backend=agent_core_postgres`
- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-116-r2db-repair-explicit-g1-recovery`
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-116-r2db-repair-explicit-g1-recovery`
- project `zeus-alpha-research-ledger-core`: `status=active`, `autonomous_enabled=true`
- active project metadata after the R2db claim reports `reconciliation_anomalies=[]`
- G1 required rows in the current status projection: `14` total, `0` blocking
- active run readback: `run-1788355136-e74f4efc`, `status=running`, task `zeus-alpha-research-ledger-core-r2db-repair-explicit-g1-recovery-dispatc`, `worker_profile=codex-builder`, `spawned_by=factory_orchestrator_tick`, `claimed_by=factory-force-tick`
- current R2db task readback: `status=running`, `phase=g1_recovery`, `priority=-116`, owner `codex-builder`, engine `codex`
- historical resolve-state/anomaly readback events: `260455`, `260461`, `260463`, and `260464` all recorded `active_runs=0` and `anomalies=["unvalidated_required_docs"]` before the R2db task was claimed.
- historical tick/dispatch readback events: `260456`, `260457`, and `260458` denied R2df G1 recovery candidates with `unresolved_validation_tasks`; `260460` denied R2cy-R1 with `missing_or_unindexed_docs`; `260465` records the current R2db `task_claimed` with `run_id=run-1788355136-e74f4efc`; `260466` records the follow-up reconciliation with `active_runs=1`.

The live status readback shows the current assigned R2db worker already running. This evidence does not invoke a new live `factory project tick` from this worker because the hard DB-action allowlist for this run permits only `factory status` and `factory gate record`; hermetic tests provide the claim/spawn regression proof for the fixed scheduler path.

## Delivery boundary

Delivery remains PR-first only. The final candidate SHA must be recorded after commit/push in the PR and Factory gate evidence, followed by independent exact-SHA quality review. This evidence document does not authorize merge, deploy, direct SQL, primary-checkout mutation, credential change, external runtime, messaging, product execution, trading/risk action, paper/live activation, or external dispatch.

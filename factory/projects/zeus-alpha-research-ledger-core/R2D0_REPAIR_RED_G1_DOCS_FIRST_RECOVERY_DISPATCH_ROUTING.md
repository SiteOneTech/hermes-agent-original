---
document_type: r2d0_repair_red_g1_docs_first_recovery_dispatch_routing
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2d0-repair-red-g1-docs-first-recovery-d
run_id: run-1787271960-5ecf821b
phase: g1_recovery
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending_independent_exact_sha_quality_review
owner: claude-builder
base_ref: origin/main
base_sha: 96f0ecd0a5f17d88a513cf986e5e92edadcbbd40
branch: factory/zeus-alpha-research-ledger-core/inc-000-r2d0-repair-red-g1-docs-first-re
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-000-r2d0-repair-red-g1-docs-first-re
created_at: 2026-08-21
---

# R2d0 — repair red-G1 docs-first recovery dispatch routing

## Scope and boundary

R2d0 is a bounded Factory control-plane recovery for the docs-first dispatch deadlock in `zeus-alpha-research-ledger-core`.

Changed scope is limited to:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_control_plane_refactor.py`
- `tests/hermes_cli/test_factory_increment_integration.py`
- `factory/projects/zeus-alpha-research-ledger-core/R2D0_REPAIR_RED_G1_DOCS_FIRST_RECOVERY_DISPATCH_ROUTING.md`
- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md` evidence index entry

No Alpha Ledger product/runtime implementation, ledger runtime propagation, deploy, credentials, direct SQL, messaging, broker/trading/risk/paper/live path, primary-checkout mutation, merge, or external writes are authorized or performed by this increment.

## Canonical documents read before implementation

The required project entrypoint and phase evidence read for this task were:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`

The canonical source of truth for operational state remains Agent Core Postgres `factory.*`; project-local Markdown is evidence/provenance only.

## Worktree identity

Captured before implementation evidence update:

- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-000-r2d0-repair-red-g1-docs-first-re`
- Branch: `factory/zeus-alpha-research-ledger-core/inc-000-r2d0-repair-red-g1-docs-first-re`
- Remote: `https://github.com/SiteOneTech/hermes-agent-original.git`
- `git rev-parse HEAD`: `96f0ecd0a5f17d88a513cf986e5e92edadcbbd40`
- `git rev-parse origin/main`: `96f0ecd0a5f17d88a513cf986e5e92edadcbbd40`
- `git merge-base HEAD origin/main`: `96f0ecd0a5f17d88a513cf986e5e92edadcbbd40`

## Canonical Factory readback and reproduction

Read-only canonical primary-runtime status command:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2d0-status-primary-stale.json`

Readback summary:

- Output size: `4,167,417` bytes
- `db_backend=agent_core_postgres`
- Project status: `active`
- Active metadata: `reconciliation_anomalies=["unvalidated_required_docs"]`
- G1 required rows: `14`
- Blocking rows: `10`
- `reviewed=false` rows: `10`
- Exact `reviewed=false` files: `FACTORY_INTAKE.md`, `REQUIREMENTS_ANALYSIS.md`, `PATTERN_ANALYSIS.md`, `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, `PRD.md`, `ADRS.md`, `METHODOLOGY_PLAN.md`, `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`, `SECURITY_GATES.md`

Assigned-worktree status command:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2d0-status-after.json`

Assigned-worktree readback summary:

- `db_backend=agent_core_postgres`
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-000-r2d0-repair-red-g1-docs-first-re`
- `factory_status_delegated=false`
- G1 required rows: `14`
- Blocking rows: `0`

Event evidence in the same status payload reproduced the dispatcher denial class:

- `dispatch_preflight_denied` event `208429` for `zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation` with `runtime_contract=docs_first_factory_product_execution_dispatch` and validation blockers.
- `dispatch_preflight_denied` event `208430` for `zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re` with `blockers=["missing_or_unindexed_docs"]`.
- `task_claimed` event `208435` for this R2d0 task and active run `run-1787271960-5ecf821b`.

Required project-action readbacks from the assigned worktree:

- `factory project resolve-state zeus-alpha-research-ledger-core --json > /tmp/r2d0-resolve-state-after.json` exited `0` and reported `action=resolve-state`, `status=active`, `anomalies=[]`, `blockers=2`, `supervisor.health=green`.
- `factory project tick zeus-alpha-research-ledger-core --json > /tmp/r2d0-tick-after.json` exited `0` and reported `job=factory_orchestrator_tick`, `db_backend=agent_core_postgres`, `claimed=null`, `spawned_worker=null`, `active_runs=1`, `needs_attention=false`, `control_plane_skipped=false`.

During the pre-repair `resolve-state` run, the resolver auto-cancelled the active R2d0 task row as a resolved legacy reconciliation task. That side effect is now covered and repaired by `test_reconciler_does_not_cancel_running_g1_recovery_task`: in-flight G1 recovery/reconciliation tasks are not auto-cancelled by resolved-anomaly cleanup. No direct SQL was used to repair the already-written audit row.

## Root cause

The dispatch classification path mixed text/prose heuristics with execution authority:

1. `_is_docs_first_gated_dispatch_task()` exempted every `g1*`, `documentation`, and `planning` phase from docs-first dispatch blockers. A generic documentation task could therefore bypass red-G1 preflight even when it was not explicitly a recovery task.
2. `_is_docs_first_repair_dispatch_task()` treated broad `g1*`, `documentation`, `docs`, and several text fragments as repair work. Selection could therefore prefer generic documentation rows as repair lanes, instead of requiring structured recovery metadata.
3. `_candidate_requires_validation_readiness_before_dispatch()` did not explicitly exempt structured G1 recovery/reconciliation work from validation-readiness waits, so historical validation rows could keep a real recovery task behind unrelated validation gates.
4. `cancel_resolved_reconciliation_tasks()` could auto-cancel an active/running recovery task when legacy prose matched a now-resolved reconciliation anomaly.

## Repair

The repair narrows bypass authority to structured, fail-closed recovery signals:

- Added `_is_explicit_factory_reconciliation_task()` for structured `factory_reconciliation_task` or `reconciliation_anomaly` metadata.
- Added `_is_explicit_g1_recovery_task()` for `phase=g1_recovery` / G1 recovery phases or explicit metadata such as `g1_recovery_task`.
- Made `_is_docs_first_gated_dispatch_task()` block every non-G0/planning task while docs are red unless it has explicit reconciliation, explicit G1 recovery, or Jean-authorized control-plane bootstrap classification.
- Made `_is_docs_first_repair_dispatch_task()` return true only for explicit structured recovery/reconciliation/bootstrap work.
- Made validation-readiness waits skip explicit G1 recovery/reconciliation tasks.
- Made resolved-anomaly cleanup skip terminal and in-flight tasks, preserving active recovery runs.

This preserves red-G1 denial for implementation/product/QA/security/delivery work and permits only explicitly classified control-plane G1 recovery/reconciliation work.

## TDD evidence

RED evidence before implementation:

- `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py::test_dispatch_preflight_allows_only_explicit_g1_recovery_when_docs_are_red tests/hermes_cli/test_factory_increment_integration.py::test_claim_next_task_routes_explicit_g1_recovery_not_generic_docs_when_docs_red -v`
- Result: `2 failed, 0 passed`; generic documentation task bypassed red-G1 preflight and was selected before explicit G1 recovery.

Additional RED evidence for the resolver side effect:

- `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py::test_reconciler_does_not_cancel_running_g1_recovery_task -v`
- Result: `1 failed, 0 passed`; running G1 recovery task was treated as a resolved reconciliation task.

GREEN focused evidence after implementation:

- `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py::test_dispatch_preflight_allows_only_explicit_g1_recovery_when_docs_are_red tests/hermes_cli/test_factory_increment_integration.py::test_claim_next_task_routes_explicit_g1_recovery_not_generic_docs_when_docs_red -v`
- Result: `2 tests passed, 0 failed`.

GREEN resolver side-effect evidence:

- `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py::test_reconciler_does_not_cancel_running_g1_recovery_task -v`
- Result: `1 test passed, 0 failed`.

Broader Factory control-plane validation:

- `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_orchestrator_tick.py -v`
- Result: `3 files, 310 tests passed, 0 failed`.

Diff hygiene:

- `git diff --check` exited `0`.

## Acceptance mapping

- Reproduced the canonical stale-primary/readback condition: 10 `reviewed=false` G1 required rows and `unvalidated_required_docs` from Agent Core Postgres status.
- Identified the exact classification/selection path: broad phase/text exemptions in `_is_docs_first_gated_dispatch_task()` / `_is_docs_first_repair_dispatch_task()`, validation-readiness wait, and resolved-anomaly cleanup for active recovery rows.
- Added RED/GREEN coverage proving generic documentation/product work stays denied while explicit G1 recovery routes.
- No ledger product/runtime files, deploy, primary-checkout mutation, direct SQL, credentials, or external runtime were touched.
- Delivery remains PR-first with independent exact-SHA review required after the final pushed head.

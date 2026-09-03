---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2f6-current-base-red-g1-dispatch-recove
run_id: run-1788441716-11cb9895
phase: g1_recovery
owner: codex-builder
status: implementation_candidate
branch: factory/zeus-alpha-research-ledger-core/inc-125-r2f6-current-base-red-g1-dispatc
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-125-r2f6-current-base-red-g1-dispatc
implementation_candidate_sha: 0489d61e10ba129422bc54dda46b2a50c53c243d
base_ref: origin/main
configured_base_commit_readback: a36cc880dd061d7f6a864937e0fe3ece44024191
---

# R2f6 — current-base red-G1 dispatch recovery bootstrap

This artifact records the bounded Factory control-plane implementation evidence for R2f6. It is not product work and does not authorize Alpha Ledger, ALR, QA/security, delivery, deploy, messaging, external runtime, broker, trading/risk, paper/live, direct SQL, primary-checkout mutation, merge, credential change, or external dispatch.

## Scope

- Project: `zeus-alpha-research-ledger-core`.
- Task: `zeus-alpha-research-ledger-core-r2f6-current-base-red-g1-dispatch-recove`.
- Run: `run-1788441716-11cb9895`.
- Assigned branch/worktree: `factory/zeus-alpha-research-ledger-core/inc-125-r2f6-current-base-red-g1-dispatc` / `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-125-r2f6-current-base-red-g1-dispatc`.
- Implementation candidate SHA after code/test commit: `0489d61e10ba129422bc54dda46b2a50c53c243d`.

## Documents consulted

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`
- `factory/projects/zeus-alpha-research-ledger-core/REQUIREMENTS_TRACEABILITY.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/METHODOLOGY_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`

## RED evidence

Focused hermetic test added first in `tests/hermes_cli/test_factory_increment_integration.py`:

- `test_force_tick_claims_guardrail_scoped_red_g1_recovery_and_spawns_one_worker`

The first runs of:

- `scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k guardrail_scoped_red_g1_recovery -v --tb=short`

exited `1` before the `hermes_cli/factory_pg.py` repair, reproducing the starvation class where an explicit `phase=g1_recovery` same-project Factory control-plane task was treated as product/runtime scoped because its prompt quoted fail-closed product guardrails.

## GREEN repair

Changed `hermes_cli/factory_pg.py` only in scheduler/preflight classification:

- keep reporting/final-delivery tasks validation-gated before product-scope text normalization;
- treat ALR, Alpha Ledger, external-runtime, external work, broker, QA/security, deployment, messaging, direct SQL, trading/risk, and paper/live terms as product/runtime scope when asserted positively;
- strip negative guardrail clauses such as `Preserve fail-closed denial ...` and `must remain denied ...` before deciding that a G1/docs recovery task itself has product/runtime scope.

This lets explicit G1/documentation recovery scope come only from `phase` or structured metadata, while normal product/runtime and validation/delivery classes remain fail-closed.

## Test evidence

Commands run from the assigned worktree:

1. `scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k guardrail_scoped_red_g1_recovery -v --tb=short`
   - RED before production repair: exit `1`.
   - GREEN after production repair and evidence docs: exit `0`; runner summary `1 tests passed, 0 failed`.
2. `scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_control_plane_refactor.py`
   - Result after evidence docs: exit `0`; runner summary `309 tests passed, 0 failed` across 2 files.
3. `git diff --check`
   - Result: exit `0`.

## Canonical Agent Core Postgres readbacks

Allowed Factory CLI status readback after the implementation code commit:

- Command: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2f6-status-after-code-commit.json`
- Extracted fields:
  - `db_backend=agent_core_postgres`
  - `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-125-r2f6-current-base-red-g1-dispatc`
  - `project_status=active`
  - `autonomous_enabled=true`
  - `active_runs=1`
  - `g1_required_rows=14`
  - `g1_blocking_rows=0`
  - `g1_readiness_sources=["configured_base_ref"]`
  - `g1_base_commits=["a36cc880dd061d7f6a864937e0fe3ece44024191"]`
  - `reconciliation_anomalies=[]`

Resolve-state readback captured during the run:

- Source file: `/tmp/r2f6-resolve-state-after-code.json`
- Extracted fields:
  - `resolve_status=active`
  - `resolve_project_id=zeus-alpha-research-ledger-core`
  - `resolve_action=resolve-state`
  - `resolve_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-125-r2f6-current-base-red-g1-dispatc`
  - `resolve_active_runs=1`
  - `resolve_anomalies=[]`
  - `resolve_pending_gates=0`
  - `resolve_monitor={"checked":1,"expired_queued_runs_recovered":0,"finalized_dead_without_exit":0,"finalized_from_stale_semantic_marker":0,"finished":0,"orphan_inflight_repaired":0}`
  - `resolve_supervisor={"health":"green","project_id":"zeus-alpha-research-ledger-core","repairs":[],"violations":[]}`

Forced-tick/status event readback from Agent Core Postgres:

- Source file: `/tmp/r2f6-status-after-code.json`.
- Pre-claim red-G1 state:
  - event `264947`: `project_reconciled`, `active_runs=0`, `anomalies=["unvalidated_required_docs"]`, `ready=3`, `todo=12`.
- Reproduced denial class immediately before R2f6 claim:
  - event `264948`: `dispatch_preflight_denied` for `zeus-alpha-research-ledger-core-r2df-r17-docs-first-validation-scheduler`, blocker includes `unresolved_validation_tasks`.
  - event `264949`: `dispatch_preflight_denied` for `zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation`, blocker includes `unresolved_validation_tasks`.
  - event `264950`: `dispatch_preflight_denied` for `zeus-alpha-research-ledger-core-r2f4-repair-terminal-run-reconciliation-`, blocker includes `unresolved_validation_tasks`.
- Successful forced-tick claim/spawn bootstrap:
  - event `264951`: `task_claimed` by `factory-force-tick` for `zeus-alpha-research-ledger-core-r2f6-current-base-red-g1-dispatch-recove`, `run_id=run-1788441716-11cb9895`, `worker_profile=codex-builder`.
  - `task_runs` row: `run_id=run-1788441716-11cb9895`, `status=running`, `worker_profile=codex-builder`, `process_id=860174`, `spawned_by=factory_orchestrator_tick`, `worker_cwd=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-125-r2f6-current-base-red-g1-dispatc`.

## Acceptance mapping

- RED: focused hermetic test reproduced the pre-repair denial/starvation class under red G1/unresolved validation history.
- GREEN: explicit `phase=g1_recovery` no-product/no-runtime Factory control-plane recovery now claims and inserts exactly one task run; product/ALR/QA-security/delivery/deploy/messaging/external-runtime/broker/trading-risk/paper-live/external-work candidates remain docs-first denied.
- Evidence: status, resolve-state, event, and task-run readbacks above are from Agent Core Postgres through sanctioned Factory CLI commands/artifacts; no direct SQL was used.
- Delivery: implementation is PR-first only; independent exact-SHA quality review remains required before merge/closure.

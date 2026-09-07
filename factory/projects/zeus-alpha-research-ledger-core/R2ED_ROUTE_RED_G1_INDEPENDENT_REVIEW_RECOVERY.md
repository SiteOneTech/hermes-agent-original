---
document_type: factory_control_plane_repair_evidence
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2ed-route-red-g1-independent-review-rec
phase: g1_recovery
status: implementation_complete_pending_independent_review
validated: yes
reviewed: pending
owner: codex-builder
reviewer: quality-reviewer
base_ref: origin/main
base_sha: d8194b268807ef2bb701b6d3f4302967a9e5e5be
branch: factory/zeus-alpha-research-ledger-core/inc-104-r2ed-route-red-g1-independent-re
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-104-r2ed-route-red-g1-independent-re
run_id: run-1788369773-a4d931c6
recorded_at_utc: 2026-09-02T17:42:51Z
---

# R2ed — route red-G1 independent-review recovery before product preflight

## Scope

This evidence is project-local for `zeus-alpha-research-ledger-core` and records only the bounded Factory control-plane repair requested for R2ed. It changes scheduler/preflight classification in `hermes_cli/factory_pg.py`, adds hermetic regression coverage, and records the exact current Agent Core Postgres state read through the approved Factory CLI.

It does not change Alpha Ledger product code, QA/security/delivery execution, deploy targets, credentials, messaging/connectors, external runtime propagation, trading/risk behavior, paper/live activation, direct SQL paths, or the primary checkout.

Assigned branch/worktree:

- Branch: `factory/zeus-alpha-research-ledger-core/inc-104-r2ed-route-red-g1-independent-re`
- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-104-r2ed-route-red-g1-independent-re`
- Base before edits: `HEAD=origin/main=merge-base=d8194b268807ef2bb701b6d3f4302967a9e5e5be`; ahead/behind `0 0`; worktree initially clean.

Documentation read before implementation:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`

## Root cause

The Factory control-plane already had docs-first exceptions for phase/metadata-routed G1 and documentation recovery tasks, but the validation/review variant still required G1/docs/recovery wording in task text after it had passed the structured phase/metadata check. That left an explicitly structured independent-review recovery row (`phase=quality_review`, owner `quality-reviewer`, metadata-bound to a G1/documentation recovery target, no product/runtime scope) classified like ordinary product validation while required G1 documents were red.

In the canonical failing state, Agent Core status readback preserves events `261247`–`261251`: R2df-R39, R2df-R17, and the fresh R2df documentation candidate were denied with `unresolved_validation_tasks`, and R2cy-R1 was denied with `missing_or_unindexed_docs`. Product implementation and ALR validation must stay denied while G1 is red, but the independent review/reconciliation path needed to clear the red G1 state cannot be blocked by the same product preflight.

## Repair

Implementation in `hermes_cli/factory_pg.py` adds a structured independent-review recovery predicate:

- `_metadata_marks_independent_review_recovery()` requires explicit metadata opt-in (`independent_review_recovery`, `g1_independent_review_recovery`, or `docs_first_independent_review_recovery`) plus a metadata target bound to a G0/G1/documentation phase or scope (`review_target_phase`, `target_phase`, `source_task_phase`, `review_scope`, `target_scope`, or `source_scope`).
- `_has_explicit_g1_or_documentation_recovery_scope()` now treats that structured independent-review metadata as an explicit G1/docs recovery signal.
- `_is_docs_first_validation_repair_task()` accepts that structured independent-review recovery without requiring matching title/description prose, after the existing fail-closed checks for QA/security/reporting/product/runtime scope.

Normal ALR/product implementation, product quality review, QA/security/delivery/reporting, deployment, direct SQL, external runtime, messaging/connectors, trading/risk, and paper/live activation remain docs-first gated while required G1 rows are red.

## RED/GREEN evidence

Focused RED test added in `tests/hermes_cli/test_factory_increment_integration.py`:

- `test_force_tick_routes_structured_independent_review_recovery_before_product_preflight`

The test constructs an active same-project Factory payload with ten required G1 rows blocking on `reviewed=false`, zero active task runs, the three unsafe R2df-like candidates still denied by product/runtime metadata, an ordinary product implementation and product quality review that must remain blocked, and one dependency-free independent-review recovery candidate whose title/description intentionally do not carry G1/docs/recovery prose. The only allowed route is the structured metadata target `review_target_phase=g1_recovery` with `independent_review_recovery=true` and `no_product_runtime_scope=true`.

Commands executed from the assigned worktree:

- Initial runner attempt without an available local pytest venv:
  `scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k structured_independent_review_recovery_before_product_preflight`
  Result: exit 1, infrastructure blocker only: no local virtualenv with pytest. No install was attempted.

- RED command before implementation, using the existing primary venv as `HERMES_PYTHON`:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k structured_independent_review_recovery_before_product_preflight`
  Result: exit 1; focused test failed with `assert None is not None`, reproducing `claimed=null`.

- Focused GREEN:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k structured_independent_review_recovery_before_product_preflight`
  Result: 1 test passed, 0 failed.

- Related scheduler/preflight GREEN:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'g1_recovery or docs_first or validation_readiness or structured_independent_review_recovery'`
  Result: 12 tests passed, 0 failed.

- Full increment-integration file GREEN:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py`
  Result: 148 tests passed, 0 failed.

- Related Factory control-plane regression GREEN:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'g1 or docs_first or validation_readiness or dispatch_preflight'`
  Result: 32 tests passed, 0 failed.

- Full related Factory scheduler/control-plane files GREEN:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_control_plane_refactor.py`
  Result: 309 tests passed, 0 failed.

## Canonical Agent Core Factory readback

Canonical status was read through the approved Factory CLI only:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2ed-status-after-code.json`

Readback summary from `/tmp/r2ed-status-after-code.json`:

- `db_backend=agent_core_postgres`
- project `zeus-alpha-research-ledger-core`: `status=active`, `autonomous_enabled=true`, `reconciliation_anomalies=[]`
- current task `zeus-alpha-research-ledger-core-r2ed-route-red-g1-independent-review-rec`: `status=running`, `phase=g1_recovery`, `owner_profile=codex-builder`
- current run `run-1788369773-a4d931c6`: `status=running`, `worker_profile=codex-builder`, `engine=codex`, `process_id=794590`, prompt `/home/jean/.hermes/factory/runs/run-1788369773-a4d931c6/prompt.md`
- canonical tick/claim readback: event `261258` `task_claimed` by `factory-force-tick` for the R2ed task; event `261253` created the task
- canonical red-G1 deadlock readback: event `261247` denied R2df-R39 with `unresolved_validation_tasks`; event `261249` denied R2df-R17 with `unresolved_validation_tasks`; event `261250` denied fresh R2df documentation with `unresolved_validation_tasks`; event `261251` denied R2cy-R1 with `missing_or_unindexed_docs`

No live `factory worker dispatch`, `factory project tick`, `factory project resolve-state`, direct SQL, merge, deploy, credential change, external runtime action, messaging action, trading/risk action, paper/live activation, product dispatch, QA/security/delivery dispatch, or primary-checkout mutation was executed by this worker. Because runtime dispatch was explicitly out of scope, the claim/spawn proof is hermetic test coverage plus readback of the existing canonical task/run/event state, pending independent exact-SHA review and PR integration.

## Delivery boundary

Delivery remains PR-first only. This candidate must be pushed from the assigned branch, labelled `agent:zeus`, signed by Zeus, and reviewed independently at the exact final SHA before any integration. This artifact is evidence, not approval for merge, deployment, external runtime, product implementation, QA/security/delivery execution, credentials, messaging, trading/risk, paper/live activation, direct SQL, or primary checkout mutation.

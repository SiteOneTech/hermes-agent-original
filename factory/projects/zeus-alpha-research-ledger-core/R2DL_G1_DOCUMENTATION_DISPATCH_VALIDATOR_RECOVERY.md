---
document_type: g1_documentation_dispatch_validator_recovery
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2dl-g1-documentation-dispatch-validator
run_id: run-1787151860-ec55022d
phase: documentation
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending_independent_exact_sha_quality_review
owner: codex-builder
base_ref: origin/main
base_sha: cc43e6dace789da06d103ba512a3f4863fb0edc9
branch: factory/zeus-alpha-research-ledger-core/inc-001-r2dl-g1-documentation-dispatch-v
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2dl-g1-documentation-dispatch-v
created_at: 2026-08-19T11:11:57-04:00
---

# R2dl — G1 documentation dispatch validator recovery

## Scope and boundary

R2dl is a bounded Factory control-plane repair for the documentation dispatch validator. It changes only:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_control_plane_refactor.py`
- project-local Factory evidence under `factory/projects/zeus-alpha-research-ledger-core/`

No Alpha Ledger product/runtime implementation, provider/model/auth config, database migration, tool registration, scheduler, deployment, credential access, messaging connector, external runtime, primary-checkout mutation, task-status mutation, direct SQL, merge, Vonash, Magnus, VAOS, RAG/KB, broker, trading, risk, paper/live activation, or external-system operation is authorized or performed by this increment.

## Canonical inputs read before implementation

Required G1/documentation inputs consulted from the assigned worktree:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DG_BOUNDED_G1_EXACT_SHA_INDEPENDENT_REVIEW_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DI_DOCS_FIRST_FAIL_CLOSED_REVIEW_TERMINALIZATION_AND_DISPATCH_REPAIR.md`

Agent Core Postgres `factory.*` remains the operational source of truth; this file is project-local evidence, not a DB substitute.

## Current base and Factory readback

Current worktree identity before code edits and evidence update:

- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2dl-g1-documentation-dispatch-v`
- Branch: `factory/zeus-alpha-research-ledger-core/inc-001-r2dl-g1-documentation-dispatch-v`
- Remote: `https://github.com/SiteOneTech/hermes-agent-original.git`
- `git rev-parse HEAD`: `cc43e6dace789da06d103ba512a3f4863fb0edc9`
- `git rev-parse origin/main`: `cc43e6dace789da06d103ba512a3f4863fb0edc9`
- `git merge-base HEAD origin/main`: `cc43e6dace789da06d103ba512a3f4863fb0edc9`

Allowed Factory status command from the assigned worktree:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2dl-status-after.json`

Summarized readback:

- `db_backend=agent_core_postgres`
- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2dl-g1-documentation-dispatch-v`
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2dl-g1-documentation-dispatch-v`
- `factory_status_delegated=false`
- `project_id=zeus-alpha-research-ledger-core`, `status=active`
- active `reconciliation_anomalies=[]`
- active `reconciliation_projection_source=current_document_status`
- G1 required rows: `14`
- G1 blocking rows: `0`
- `readiness_source=configured_base_ref`
- `base_commit=cc43e6dace789da06d103ba512a3f4863fb0edc9`
- current relevant task rows still include R2df as `todo` documentation work, ALR-063 as `todo` security review work, ALR-070 as `todo` QA work, and R2cw as `ready` implementation work.

## Defect reproduced

The validation-readiness classifier in `hermes_cli/factory_pg.py::_candidate_requires_validation_readiness_before_dispatch()` used a broad substring check: `"final" in text`. The R2df documentation task description includes historical wording, `canonical resolve-state finalized its run as blocked`. That word is not an end-stage delivery/final-report request, but the substring made the dispatcher treat R2df as final-stage work.

When unrelated validation work was still open and docs-first G1/product gating remained fail-closed, `_next_runnable_task()` skipped the dependency-ready R2df documentation recovery and moved to validation/product candidates instead of leaving R2df eligible.

Focused RED test added before implementation:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k validation_readiness_allows_dependency_ready_documentation_recovery_with_historical_finalized_wording -v --tb=short`

RED result: `1 failed, 156 deselected`; the selected task was the unrelated `demo-alr-063-security-review` instead of the dependency-ready documentation recovery `demo-r2df-current-base-g1-docs`.

## Repair

The classifier now recognizes only explicit final-stage text (`delivery report`, `final delivery`, `final report`, `final gate`, `final handoff`, `gate closure`, `closure report`, `release report`, or a word-bounded `final <delivery|report|gate|closure|handoff>` phrase) plus the existing phase-based delivery/release/final/final_report conditions. Historical words such as `finalized` no longer trigger validation-readiness blocking.

Preserved fail-closed behavior:

- final delivery/report/release phases still require validation-readiness before dispatch;
- deploy/sandbox packaging prerequisite behavior remains unchanged;
- docs-first product gating for implementation, QA, security, delivery, deploy, and release work remains in `_dispatch_preflight_blockers()` and was not relaxed;
- active validation tasks themselves remain recognized by `_is_validation_task()` and `_validation_task_readiness_findings()`.

## Verification evidence

RED evidence:

- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k validation_readiness_allows_dependency_ready_documentation_recovery_with_historical_finalized_wording -v --tb=short`
- Result: `1 failed, 156 deselected`; failure showed the dispatcher selecting `demo-alr-063-security-review` instead of `demo-r2df-current-base-g1-docs`.

Focused GREEN evidence after implementation:

- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'validation_readiness_allows_dependency_ready_documentation_recovery_with_historical_finalized_wording or dispatch_validation_readiness_does_not_deadlock_deploy_prerequisite or dispatch_preflight_blocks_product_execution_without_docs' -v --tb=short`
- Result: `3 tests passed, 0 failed`.

Related Factory control-plane GREEN evidence:

- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_increment_integration.py -v`
- Result: `3 files, 303 tests passed, 0 failed`.

Canonical Factory status readback after implementation:

- Command: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2dl-status-after.json`
- Result: exit `0`; Agent Core Postgres, worktree source roots, `factory_status_delegated=false`, active `reconciliation_anomalies=[]`, 14/14 required G1 rows non-blocking from `configured_base_ref` at base `cc43e6dace789da06d103ba512a3f4863fb0edc9`.

Diff/tracking validation:

- `git diff --check`
- Result: exit `0`.
- `git status --short --branch` and exact final pushed head/PR readback via `gh pr view` remain required after commit/push.

## Delivery state

This candidate is implemented and validated locally, but remains pending PR creation/push and independent exact-SHA review of the final pushed head. The PR must be non-draft, labeled `agent:zeus`, Zeus-signed, and must record the exact source SHA. This artifact does not self-approve, merge, deploy, mutate task status, mutate primary checkout, or authorize ALR-020/product/runtime dispatch.

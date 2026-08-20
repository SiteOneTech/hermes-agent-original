---
document_type: reconciliation_unblock_g1_documentation_dispatch_predicate
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2dz-reconciliation-unblock-g1-documenta
run_id: run-1787226436-8b362cf4
phase: documentation
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending_independent_exact_sha_quality_review
owner: codex-builder
base_ref: origin/main
base_sha: 71e5e7b2f4ace3b081f9446483784a3c5fb0b981
branch: factory/zeus-alpha-research-ledger-core/inc-016-r2dz-reconciliation-unblock-g1-d
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-016-r2dz-reconciliation-unblock-g1-d
created_at: 2026-08-20T07:53:24-04:00
---

# R2dz — Reconciliation: unblock G1 documentation dispatch predicate

## Scope and boundary

R2dz is a bounded Factory control-plane repair for the validation-readiness dispatch predicate. It changes only:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_control_plane_refactor.py`
- project-local evidence under `factory/projects/zeus-alpha-research-ledger-core/`

No Alpha Ledger product/runtime implementation, provider/model/auth config, database migration, tool registration, scheduler, deployment, credential access, messaging connector, external runtime, primary-checkout mutation, task-status mutation, direct SQL, merge, Vonash, Magnus, VAOS, RAG/KB, broker, trading, risk, paper/live activation, or external-system operation is authorized or performed by this increment.

## Canonical inputs read before implementation

Required G1/documentation inputs consulted from the assigned worktree:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DL_G1_DOCUMENTATION_DISPATCH_VALIDATOR_RECOVERY.md`

Agent Core Postgres `factory.*` remains the operational source of truth; this file is project-local evidence, not a DB substitute.

## Current base and Factory readback

Current worktree identity before implementation/evidence update:

- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-016-r2dz-reconciliation-unblock-g1-d`
- Branch: `factory/zeus-alpha-research-ledger-core/inc-016-r2dz-reconciliation-unblock-g1-d`
- Remote: `https://github.com/SiteOneTech/hermes-agent-original.git`
- `git rev-parse HEAD`: `71e5e7b2f4ace3b081f9446483784a3c5fb0b981`
- `git rev-parse origin/main`: `71e5e7b2f4ace3b081f9446483784a3c5fb0b981`
- `git merge-base HEAD origin/main`: `71e5e7b2f4ace3b081f9446483784a3c5fb0b981`

Allowed Factory status command from the assigned worktree:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2dz-status-after.json`

Summarized readback:

- `db_backend=agent_core_postgres`
- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-016-r2dz-reconciliation-unblock-g1-d`
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-016-r2dz-reconciliation-unblock-g1-d`
- `factory_status_delegated=false`
- `project_id=zeus-alpha-research-ledger-core`, `status=active`
- active `reconciliation_anomalies=[]`
- active `reconciliation_projection_source=current_document_status`
- G1 required rows: `14`
- G1 blocking rows: `0`
- `readiness_source=configured_base_ref`
- `base_commit=71e5e7b2f4ace3b081f9446483784a3c5fb0b981`

## Defect reproduced

R2dl narrowed the broad `"final" in text` classifier, but the remaining predicate still scanned narrative text before recognizing bounded documentation/reconciliation recovery work. A dependency-free G1 documentation recovery can legitimately cite historical `final delivery report` or `release report` blocker evidence without being a final delivery/release task.

When an older quality/security review task remains open, `_validation_task_readiness_findings()` reports `unresolved_validation_tasks`. Before this repair, `_candidate_requires_validation_readiness_before_dispatch()` saw the historical final-delivery/release phrases in the documentation/reconciliation recovery narrative, recorded a dispatch denial for the recovery task, and selected the pending validation task instead. That left G1 documentation/reconciliation recovery unclaimable even though it is docs-first-exempt and dependency-free.

Focused RED test added before implementation:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k validation_readiness_allows_g1_documentation_or_reconciliation_recovery_with_final_delivery_history -v --tb=short`

RED result: `1 failed, 157 deselected`; failure showed `_next_runnable_task()` selecting `demo-older-ready-quality-review` instead of dependency-free documentation recovery `demo-r2df-g1-documentation-recovery`.

## Repair

The predicate now exempts only bounded documentation/G1/reconciliation recovery work before scanning final-stage narrative text:

- reconciliation tasks remain claimable through `_is_reconciliation_task()`;
- documentation/G0/G1/planning recovery tasks owned by builder/planner/control-plane profiles remain claimable when their text indicates documentation/document-status/docs-first/G1/review-state/dispatch recovery or repair;
- reporter, QA, quality, security, and devops-release ownership is not exempted by this helper;
- explicit final delivery/report/gate/handoff/closure text and release/final phases continue to require validation readiness for non-recovery delivery/report/release work.

This keeps historical evidence prose from blocking R2df/R2dz recovery while preserving fail-closed validation and docs-first gates for product implementation, QA, security, release/delivery reporting, and external-runtime work.

## Verification evidence

RED evidence:

- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k validation_readiness_allows_g1_documentation_or_reconciliation_recovery_with_final_delivery_history -v --tb=short`
- Result: `1 failed, 157 deselected`; selected `demo-older-ready-quality-review` instead of `demo-r2df-g1-documentation-recovery`.

Focused GREEN evidence after implementation:

- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k validation_readiness_allows_g1_documentation_or_reconciliation_recovery_with_final_delivery_history -v --tb=short`
- Result: `1 test passed, 0 failed`.

Fail-closed classifier/preflight evidence:

- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'validation_readiness_allows_g1_documentation_or_reconciliation_recovery_with_final_delivery_history or validation_readiness_allows_dependency_ready_documentation_recovery_with_historical_finalized_wording or dispatch_validation_readiness_does_not_deadlock_deploy_prerequisite or dispatch_preflight_blocks_product_execution_without_docs or dispatch_preflight_exempts_reconciliation_tasks' -v --tb=short`
- Result: `5 tests passed, 0 failed`.

Related Factory control-plane GREEN evidence:

- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_increment_integration.py -v`
- Result: `3 files, 304 tests passed, 0 failed`.

Canonical Factory status readback after implementation:

- Command: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2dz-status-after.json`
- Result: exit `0`; Agent Core Postgres, worktree source roots, `factory_status_delegated=false`, active `reconciliation_anomalies=[]`, 14/14 required G1 rows non-blocking from `configured_base_ref` at base `71e5e7b2f4ace3b081f9446483784a3c5fb0b981`.

## Delivery state

This candidate is implemented and validated locally, but remains pending commit, push, PR creation, and independent exact-SHA review of the final pushed head. The PR must be non-draft, labeled `agent:zeus`, Zeus-signed, and must record the exact source SHA. This artifact does not self-approve, merge, deploy, mutate task status, mutate primary checkout, or authorize ALR-020/product/runtime dispatch.

---
document_type: reconciliation_documentation_dispatch_classifier_recovery
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2df-r1-reconciliation-documentation-dis
run_id: run-1787222735-4604efb1
phase: documentation
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending_independent_exact_sha_quality_review
owner: codex-builder
base_ref: origin/main
base_sha: 71e5e7b2f4ace3b081f9446483784a3c5fb0b981
branch: factory/zeus-alpha-research-ledger-core/inc-016-r2df-r1-reconciliation-documenta
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-016-r2df-r1-reconciliation-documenta
created_at: 2026-08-20T06:52:42-04:00
---

# R2df-R1 — reconciliation documentation dispatch classifier recovery

## Scope and boundary

R2df-R1 is a bounded Factory control-plane repair for the validation-readiness dispatch classifier. It changes only:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_control_plane_refactor.py`
- project-local Factory evidence under `factory/projects/zeus-alpha-research-ledger-core/`

No Alpha Ledger product/runtime implementation, provider/model/auth config, database migration, tool registration, scheduler, deployment, credential access, messaging connector, external runtime, primary-checkout mutation, task-status mutation, direct SQL, merge, Vonash, Magnus, VAOS, RAG/KB, broker, trading, risk, paper/live activation, or external-system operation is authorized or performed by this increment.

## Canonical inputs read before implementation

Required G1/documentation inputs consulted from the assigned worktree:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DG_BOUNDED_G1_EXACT_SHA_INDEPENDENT_REVIEW_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DL_G1_DOCUMENTATION_DISPATCH_VALIDATOR_RECOVERY.md`

Agent Core Postgres `factory.*` remains the operational source of truth; this file is project-local evidence, not a DB substitute.

## Current base and Factory readback

Worktree identity before code edits and evidence update:

- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-016-r2df-r1-reconciliation-documenta`
- Branch: `factory/zeus-alpha-research-ledger-core/inc-016-r2df-r1-reconciliation-documenta`
- `git rev-parse HEAD`: `71e5e7b2f4ace3b081f9446483784a3c5fb0b981`
- `git rev-parse origin/main`: `71e5e7b2f4ace3b081f9446483784a3c5fb0b981`
- `git merge-base HEAD origin/main`: `71e5e7b2f4ace3b081f9446483784a3c5fb0b981`

Allowed Factory status command from the assigned worktree:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r1-status-final.json`

Summarized readback:

- `db_backend=agent_core_postgres`
- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-016-r2df-r1-reconciliation-documenta`
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-016-r2df-r1-reconciliation-documenta`
- `factory_status_delegated=false`
- `project_status=active`
- active `reconciliation_anomalies=["pending_effective_gates"]`
- active `reconciliation_projection_source=current_document_status`
- G1 required rows: `14`
- G1 blocking rows: `0`
- `readiness_source=configured_base_ref`
- `base_commit=71e5e7b2f4ace3b081f9446483784a3c5fb0b981`

## Defect reproduced

R2dl narrowed the classifier so historical `finalized` wording no longer blocked documentation recovery. R2df-R1 exposed the next edge of the same bug class: the validation-readiness classifier still scanned all task prose for explicit final-stage phrases before recognizing a documentation/reconciliation recovery. Incidental prose such as “not a final delivery report” or “not terminal delivery work” can appear in bounded recovery tasks precisely to document that delivery remains independently gated; it must not make the recovery candidate wait for unrelated unresolved validation work.

Focused RED test added before implementation:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'validation_readiness_allows_r2df_reconciliation_docs_with_incidental_delivery_prose or validation_readiness_blocks_terminal_delivery_when_validation_work_is_unresolved' -v --tb=short`

RED result: `1 failed, 1 passed, 157 deselected`; the R2df-shaped documentation/reconciliation candidate was skipped and the selected task was the unrelated `demo-alr-063-security-review`. The paired terminal-delivery guard already passed.

## Repair

`hermes_cli/factory_pg.py::_candidate_requires_validation_readiness_before_dispatch()` now recognizes documentation/planning/G0/G1 reconciliation tasks owned by non-delivery/non-release profiles before scanning final-stage prose. Those bounded recovery candidates remain selectable even when their description documents why final delivery remains gated.

Preserved fail-closed behavior:

- genuine `delivery` / `release` / `final` / `final_report` candidates still require validation-readiness before dispatch;
- explicit final delivery/report/release stages owned by `factory-reporter` remain validation-gated;
- deploy/sandbox packaging prerequisite behavior remains unchanged;
- docs-first product gating for implementation, QA, security, delivery, deploy, and release work remains in `_dispatch_preflight_blockers()` and was not relaxed;
- active validation tasks themselves remain recognized by `_is_validation_task()` and `_validation_task_readiness_findings()`.

## Verification evidence

RED evidence:

- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'validation_readiness_allows_r2df_reconciliation_docs_with_incidental_delivery_prose or validation_readiness_blocks_terminal_delivery_when_validation_work_is_unresolved' -v --tb=short`
- Result: `1 failed, 1 passed, 157 deselected`; failure selected `demo-alr-063-security-review` instead of `demo-r2df-r1-reconciliation-documentation-dis`.

Focused GREEN evidence after implementation:

- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'validation_readiness_allows_r2df_reconciliation_docs_with_incidental_delivery_prose or validation_readiness_blocks_terminal_delivery_when_validation_work_is_unresolved' -v --tb=short`
- Result: `2 tests passed, 0 failed`.

Focused file GREEN evidence:

- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -v`
- Result: `159 tests passed, 0 failed`.

Related Factory control-plane GREEN evidence:

- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_increment_integration.py -v`
- Result: `3 files, 305 tests passed, 0 failed`.

Canonical Factory status readback after implementation:

- Command: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r1-status-final.json`
- Result: exit `0`; Agent Core Postgres, worktree source roots, `factory_status_delegated=false`, active `reconciliation_projection_source=current_document_status`, 14/14 required G1 rows non-blocking from `configured_base_ref` at base `71e5e7b2f4ace3b081f9446483784a3c5fb0b981`.

Diff/tracking validation:

- `git diff --check`
- Result: exit `0`.

## Delivery state

This candidate is implemented and validated locally, but remains pending commit/push, PR creation, and independent exact-SHA review of the final pushed head. The PR must be non-draft, labeled `agent:zeus`, Zeus-signed, and must record the exact final source SHA plus the focused test result and independent quality-review handoff. This artifact does not self-approve, merge, deploy, mutate task status, mutate primary checkout, or authorize ALR-020/product/runtime dispatch.

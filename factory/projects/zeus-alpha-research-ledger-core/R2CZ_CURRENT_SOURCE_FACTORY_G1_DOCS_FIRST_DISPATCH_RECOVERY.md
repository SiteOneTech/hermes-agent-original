---
document_type: current_source_factory_g1_docs_first_dispatch_recovery
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2cz-current-source-factory-g1-docs-firs
run_id: run-1787267853-bb077811
phase: documentation
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending_independent_exact_sha_quality_review
owner: claude-builder
base_ref: origin/main
base_sha: 96f0ecd0a5f17d88a513cf986e5e92edadcbbd40
branch: factory/zeus-alpha-research-ledger-core/inc-000-r2cz-current-source-factory-g1-d
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-000-r2cz-current-source-factory-g1-d
created_at: 2026-08-20T19:38:28-04:00
---

# R2cz — current-source Factory G1 docs-first dispatch recovery

## Scope and boundary

R2cz is a bounded Factory control-plane repair for current-source provenance in the G1 docs-first path. It changes only:

- `hermes_cli/factory.py`
- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_orchestrator_tick.py`
- `tests/hermes_cli/test_factory_increment_integration.py`
- project-local Factory evidence under `factory/projects/zeus-alpha-research-ledger-core/`

No Alpha Ledger product/runtime implementation, external trading/runtime system, provider/model/auth config, deployment, credential access, direct SQL, primary-checkout mutation, auto-merge, or task-status mutation is authorized or performed by this increment. Agent Core Postgres `factory.*` remains the operational source of truth; this file is project-local evidence, not a DB substitute.

## Canonical inputs read before implementation

Required G1/documentation inputs consulted from the assigned worktree:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2EA_DOCS_FIRST_STALE_RUNTIME_DISPATCH_PROVENANCE_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R5_FAIL_CLOSED_REVIEW_TERMINIZATION_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DL_G1_DOCUMENTATION_DISPATCH_VALIDATOR_RECOVERY.md`

## Current base and reproduced stale readback

Assigned worktree identity before code edits:

- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-000-r2cz-current-source-factory-g1-d`
- Branch: `factory/zeus-alpha-research-ledger-core/inc-000-r2cz-current-source-factory-g1-d`
- Remote: `https://github.com/SiteOneTech/hermes-agent-original.git`
- `git rev-parse HEAD`: `96f0ecd0a5f17d88a513cf986e5e92edadcbbd40`
- `git rev-parse origin/main`: `96f0ecd0a5f17d88a513cf986e5e92edadcbbd40`
- `git merge-base HEAD origin/main`: `96f0ecd0a5f17d88a513cf986e5e92edadcbbd40`

Stale console-script reproduction from the assigned worktree:

- Command: `/home/jean/Projects/hermes-agent-original/venv/bin/hermes factory status zeus-alpha-research-ledger-core --json > /tmp/r2cz-status-hermes-worktree-before.json`
- Result: exit `0`.
- Summary: `stale_hermes_g1_count=14 blockers=10 reviewed_false=FACTORY_INTAKE.md,REQUIREMENTS_ANALYSIS.md,PATTERN_ANALYSIS.md,ASSUMPTIONS_AND_OPEN_QUESTIONS.md,PRD.md,ADRS.md,METHODOLOGY_PLAN.md,TECHNICAL_BLUEPRINT.md,TASK_GRAPH.md,SECURITY_GATES.md sources= base_commits=`.
- Interpretation: the installed console script imported stale primary source and emitted the historical ten-document blocker projection without current source-root/base provenance.

Current-source canonical readback from the mandated module CLI:

- Command: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2cz-status-module-after.json`
- Result: exit `0`.
- Summary: `g1_count=14 blockers=0 reviewed_false= sources=configured_base_ref base_commits=96f0ecd0a5f17d88a513cf986e5e92edadcbbd40`.
- Source provenance: `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-000-r2cz-current-source-factory-g1-d`, `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-000-r2cz-current-source-factory-g1-d`, `factory_status_delegated=false`.
- Document rows show `primary_checkout_accepted=false`, `primary_checkout_rejected_reason=primary_checkout_not_configured_base`, `readiness_source=configured_base_ref`, and `base_commit=96f0ecd0a5f17d88a513cf986e5e92edadcbbd40` for the 14 required G1 documents.

## Repair

The Factory CLI source selector now treats a running Factory source that is behind or diverged from the configured origin base as untrusted for configured-base control-plane actions. When a clean exact configured-base worktree exists, status/project-action/tick dispatch delegate to that source. When the configured-base source is dirty, missing, malformed, or otherwise unverified, the path remains fail-closed:

- `factory status` annotates source-root provenance and marks required G1 status rows blocking with `configured_base_source_unavailable_or_unverified` instead of trusting a stale green primary readback.
- configured-base project actions such as `resolve-state` fail before calling the stale primary backend when the verified source is unavailable.
- `tick`/orchestrator selection inherits the broadened stale-source predicate, so diverged stale primary roots cannot drive dispatch.
- docs-first dispatch gating now explicitly covers validation/test phases and validation/test wording, so a current-base documentation/reconciliation recovery task remains eligible before validation/product work when G1 is red.

Ahead-of-current-base local source remains allowed for normal feature-branch execution; only behind/diverged stale roots require verified configured-base delegation or fail closed.

## Verification evidence

RED evidence before implementation:

- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k 'status_forces_green_stale_primary_readback_closed_when_configured_base_source_is_dirty or resolve_state_fails_closed_when_configured_base_source_is_dirty or resolve_state_prefers_configured_base_source_when_running_main_diverged' -v --tb=long`
- Result: `3 failed, 21 deselected`; status lacked `factory_status_source_root_fail_closed`, dirty configured-base `resolve-state` still called the stale primary backend, and diverged primary source did not delegate to the clean configured-base worktree.

Focused GREEN evidence after implementation:

- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k 'status_forces_green_stale_primary_readback_closed_when_configured_base_source_is_dirty or resolve_state_fails_closed_when_configured_base_source_is_dirty or resolve_state_prefers_configured_base_source_when_running_main_diverged' -v --tb=long`
- Result: `3 tests passed, 0 failed`.
- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'claims_docs_repair_before_validation_and_product_when_g1_is_red' -v --tb=long`
- Result: `1 tests passed, 0 failed`.

Related Factory control-plane GREEN evidence:

- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_increment_integration.py -v --tb=short`
- Result: `3 files, 309 tests passed, 0 failed`.

Canonical Factory status evidence after implementation:

- Command: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2cz-status-module-after.json`
- Result: exit `0`; Agent Core Postgres readback with worktree source roots, `factory_status_delegated=false`, 14/14 required G1 rows non-blocking from `configured_base_ref` at `96f0ecd0a5f17d88a513cf986e5e92edadcbbd40`.

## Delivery state

This candidate is implemented and locally validated, pending commit, push, PR creation, and independent exact-SHA review of the final pushed head. The PR must be non-draft, labeled `agent:zeus`, Zeus-signed, and must record the exact source SHA. This artifact does not self-approve, merge, deploy, mutate task status, mutate primary checkout, or authorize ALR-020/product/runtime dispatch.

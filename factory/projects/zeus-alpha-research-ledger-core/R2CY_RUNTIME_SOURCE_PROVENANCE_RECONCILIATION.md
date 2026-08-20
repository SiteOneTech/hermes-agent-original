---
project_id: zeus-alpha-research-ledger-core
phase: documentation
status: implemented_pending_independent_exact_sha_quality_review
validated: yes
reviewed: pending_independent_exact_sha_quality_review
owner: devops-release
task_id: zeus-alpha-research-ledger-core-r2cy-reconciliation-canonical-factory-ru
run_id: run-1787219284-19572f1c
base_ref: origin/main
base_commit: 71e5e7b2f4ace3b081f9446483784a3c5fb0b981
---

# R2cy Runtime Source Provenance Reconciliation

## Scope

Bounded Factory control-plane repair only. No product ledger code, no deployment, no credentials, no direct SQL, no primary-checkout mutation, no external runtime, and no trading/risk/paper/live system access.

## Canonical source mismatch reproduced without direct SQL

Read-only primary checkout evidence:

- Command: `git fetch origin main --prune` in `/home/jean/Projects/hermes-agent-original`.
- Primary `HEAD`: `ac1fdb16051324c490d803b14dd06efffd6f9ad0`.
- `origin/main`: `71e5e7b2f4ace3b081f9446483784a3c5fb0b981`.
- Divergence: `git rev-list --left-right --count origin/main...HEAD` returned `2245\t4`.
- Branch status: `## main...origin/main [ahead 4, behind 2245]`.

Factory readback via approved CLI, primary working directory:

- Command: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json` from `/home/jean/Projects/hermes-agent-original`.
- Result excerpt: `reconciliation_anomalies=["unvalidated_required_docs"]`, `g1_blockers=10`, blocker files `FACTORY_INTAKE.md`, `REQUIREMENTS_ANALYSIS.md`, `PATTERN_ANALYSIS.md`, `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, `PRD.md`, `ADRS.md`, `METHODOLOGY_PLAN.md`, `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`, `SECURITY_GATES.md`.
- Active run readback at time of implementation: `run-1787219284-19572f1c` for this R2cy task was `running`; live tick/dispatch was not executed to avoid mutating this active run through monitor repair.

Factory readback via approved CLI, assigned worktree/current source:

- Command: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json` from the assigned worktree.
- Result excerpt: `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-021-r2cy-runtime-source-provenance-reconciliation`, `reconciliation_anomalies=[]`, `reconciliation_projection_source=current_document_status`, `g1_blockers=0`, `g1_rows=14`.
- Runnable head included product task `r2cw` ready and docs task `r2df` todo; the new regression test proves docs-first recovery selection when canonical G1 rows are red.

## Root cause

The Factory CLI source resolver delegated status/resolve/tick to a clean configured-base worktree only when the running primary source was a strict ancestor of `origin/main` (pure stale-behind). The live primary checkout is diverged: it is both behind and ahead. Because `merge-base --is-ancestor <primary_head> <origin/main>` is false in a diverged graph, the resolver kept using non-canonical primary Factory code and reproduced stale G1 blockers.

## Repair

`hermes_cli/factory.py` now classifies runtime source identity as:

- exact configured base: stay local;
- pure ahead of configured base: stay local for intentional local/source development;
- stale-behind or diverged from configured base: use an independently verified clean worktree at the configured base for Factory status, project resolve-state, and tick dispatch;
- no verified clean configured-base worktree: fail closed instead of falling back to stale/diverged primary code for tick dispatch.

## Regression tests

RED evidence before the code repair:

- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k 'primary_root_diverged or test_project_tick_prefers_configured_base_source_when_primary_root_diverged or test_resolve_state_prefers_configured_base_when_primary_root_diverged'`.
- Result: 2 selected tests failed. Failures proved the diverged primary path used the primary orchestrator/backend instead of configured-base source.

GREEN evidence after the code repair:

- Same targeted command: 2 tests passed.
- Dispatch ordering command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'docs_first_recovery_before_docs_blocked_product or claims_docs_repair_before_preflight_denied_product or keeps_priority_order_when_docs_ready'`.
- Result: 3 tests passed. This includes the new docs-first recovery case: product implementation remains fail-closed while canonical G1 rows are red, and the bounded documentation recovery task is selected.
- Broader focused suite: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_control_plane_refactor.py`.
- Result: 305 tests passed, 0 failed.

## Files changed

- `hermes_cli/factory.py`: source-provenance classification for stale-behind vs diverged vs ahead-only primary source.
- `tests/hermes_cli/test_factory_orchestrator_tick.py`: RED/GREEN coverage for diverged-primary configured-base delegation in tick and resolve-state.
- `tests/hermes_cli/test_factory_increment_integration.py`: docs-first recovery dispatch ordering when canonical G1 rows block product execution.
- `factory/projects/zeus-alpha-research-ledger-core/R2CY_RUNTIME_SOURCE_PROVENANCE_RECONCILIATION.md`: this evidence artifact.

## Delivery boundary

No sandbox/deploy evidence is applicable to this bounded Factory control-plane/documentation reconciliation. Production/runtime propagation remains HOLD. Product task execution remains guarded by canonical G1 document rows and downstream gate policy.

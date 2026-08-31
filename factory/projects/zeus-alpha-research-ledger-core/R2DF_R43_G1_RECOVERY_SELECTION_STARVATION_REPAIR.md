---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2df-r43-g1-recovery-selection-starvatio
phase: g1_recovery
status: candidate
validated: yes
reviewed: pending
owner: codex-builder
reviewer: quality-reviewer
run_id: run-1788132409-334d1a2f
---

# R2df-R43 — G1 recovery selection starvation repair

## Scope

Bounded Factory scheduler/control-plane repair only. This candidate changes Factory task-selection classification and focused Factory tests. It does not change Zeus Alpha Research Ledger product/runtime code and does not authorize merge, deploy, direct SQL, credential changes, primary-checkout mutation, messaging, external runtime, Vonash/Magnus/VAOS/RAG/KB/broker/trading/risk, or paper/live activation.

## Canonical inputs consulted

- `DOCUMENTATION_INDEX.md` — controlling G1/readiness/index contract and recent R2df/R2cy recovery history.
- `FACTORY_INTAKE.md` — Zeus-only local Agent Core scope and explicit exclusions.
- `G0_REPOSITORY_STRATEGY.md` — `zeus_only`, `add_functionality`, primary repo `SiteOneTech/hermes-agent-original`, branch/worktree policy, PR-first override.
- `DATABASE_AND_RUNTIME_CONTRACT.md` — no product/runtime/no-egress boundaries and scheduler-readiness contract.
- `TECHNICAL_BLUEPRINT.md` — product/runtime separation and local-only architecture.
- `TASK_GRAPH.md`, `QA_GATES.md`, `SECURITY_GATES.md` — Factory task/gate evidence rules and no-direct-SQL/no-primary-mutation boundaries.

## Source and status evidence

- Assigned branch: `factory/zeus-alpha-research-ledger-core/inc-096-r2df-r43-g1-recovery-selection-s`.
- Assigned worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-096-r2df-r43-g1-recovery-selection-s`.
- Pre-edit source SHA: `f12de8b9c1d63bf9eff580b100436d099d375b6e`.
- Canonical status command used: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json` from the assigned worktree.
- Status snapshot before code/docs: `/tmp/r2df-r43-status-before.json` (4,961,322 bytes).
- Status snapshot after code/tests before commit: `/tmp/r2df-r43-status-after-code.json` (4,961,307 bytes).
- Readback summary from the assigned worktree reported `db_backend=agent_core_postgres`, `factory_cli_source_root` and `factory_status_source_root` both equal to the assigned worktree, project `active`, `autonomous_enabled=True`, `reconciliation_anomalies=[]`, and 14/14 required G1 rows with 0 current blockers. The active run was this task run `run-1788132409-334d1a2f`.
- The same status readback preserved source-backed starvation evidence in recent `dispatch_preflight_denied` events: R2df-R17 (`zeus-alpha-research-ledger-core-r2df-r17-docs-first-validation-scheduler`) remained `todo` and event `249013` denied it with `unresolved_validation_tasks`; R2cy-R1 (`zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re`) remained `ready` and event `249004` denied it with `missing_or_unindexed_docs`.

## RED reproduction

Command:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k explicit_g1_recovery_metadata_before_review -v --tb=short`

Observed RED before production repair:

- 1 selected test failed.
- Failure: `assert tick["claimed"] is not None` in `test_force_tick_uses_explicit_g1_recovery_metadata_before_review_when_docs_red`.
- The test fixture reproduced ten blocking required G1 rows, a ready R2cy-R1 product-quality review, a ready product task, and an eligible metadata-classified G1/documentation recovery. The pre-repair scheduler still attempted downstream review/product gating before the recovery task because the recovery was not recognized from explicit metadata.

## GREEN repair

Changed behavior:

- Added explicit G1-recovery classification in `hermes_cli/factory_pg.py` via `metadata.g1_recovery` plus the existing explicit `phase == "g1_recovery"` path.
- `_is_docs_first_repair_dispatch_task()` now treats explicitly classified G1 recovery as docs-first repair only when positive product/runtime/direct-integration scope is absent. Product/runtime G1-looking work remains docs-first gated.
- Existing priority ordering is preserved when G1 is clear because review preemption is only activated when `docs_ready` is false; existing `test_claim_next_task_keeps_priority_order_when_docs_ready` remains green in the full focused file run.

## Verification

Commands run from the assigned worktree:

1. RED: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k explicit_g1_recovery_metadata_before_review -v --tb=short` → failed as expected, 1 failed / 0 passed selected.
2. GREEN targeted: same command → passed, 1 passed / 0 failed.
3. Focused Factory increment tests: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -v --tb=short` → passed, 136 passed / 0 failed.
4. Related Factory control-plane tests: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -v --tb=short` → passed, 157 passed / 0 failed.
5. Whitespace check: `git diff --check` → exit 0.

## PR-first handoff

This artifact is candidate evidence only. The final candidate commit SHA, pushed branch, PR URL, and Factory gate evidence are recorded after commit/push because a commit cannot contain its own SHA. Independent exact-SHA review by a separate reviewer remains required before merge or downstream dispatch relies on this repair.

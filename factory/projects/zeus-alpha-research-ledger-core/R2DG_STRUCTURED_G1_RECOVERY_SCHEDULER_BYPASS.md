---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2dg-structured-g1-recovery-scheduler-by
phase: g1_recovery
status: candidate
validated: yes
reviewed: pending
owner: codex-builder
reviewer: quality-reviewer
run_id: run-1788386596-4f12c284
---

# R2dg — structured G1 recovery scheduler bypass for broad completion-word match

## Scope

Bounded Factory scheduler/control-plane repair only. This candidate changes `hermes_cli/factory_pg.py`, focused Factory scheduler tests, and project-local evidence for `zeus-alpha-research-ledger-core`. It does not change Alpha Ledger product/runtime code, providers, migrations, tool schemas, credentials, deployment behavior, messaging connectors, Vonash, Magnus, VAOS, RAG/KB, broker/trading/risk behavior, paper/live activation, primary checkout state, or external dispatch.

## Canonical inputs consulted

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md` — G1/documentation index and previous R2d1/R2d6/R2dl/R2df recovery contracts.
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md` — current incremental Factory execution context.
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md` — task dependency/status context for R2-series recovery work.
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md` — PR-first, exact-SHA, no-primary-mutation, no-direct-SQL, no-deploy boundary.
- `factory/projects/zeus-alpha-research-ledger-core/METHODOLOGY_PLAN.md` — scheduler stop condition and local-only scheduler rule.

## Source and Agent Core readback evidence

Assigned branch/worktree:

- Branch: `factory/zeus-alpha-research-ledger-core/inc-104-r2dg-structured-g1-recovery-sche`
- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-104-r2dg-structured-g1-recovery-sche`
- Pre-edit base: `HEAD=origin/main=merge-base=d8194b268807ef2bb701b6d3f4302967a9e5e5be`

Approved read-only Factory CLI status snapshots from the assigned worktree:

- Before code/docs: `/tmp/r2dg-status-before.json` (4,941,509 bytes)
- After code/tests before commit: `/tmp/r2dg-status-after-code.json` (4,937,499 bytes)
- Forced-tick event extraction: `/tmp/r2dg-forced-tick-readback.json`

Status readback summary from `/tmp/r2dg-status-after-code.json`:

- `db_backend=agent_core_postgres`
- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-104-r2dg-structured-g1-recovery-sche`
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-104-r2dg-structured-g1-recovery-sche`
- `factory_status_delegated=false`
- project `zeus-alpha-research-ledger-core`: `status=active`, `autonomous_enabled=true`, `reconciliation_anomalies=[]`
- current task `zeus-alpha-research-ledger-core-r2dg-structured-g1-recovery-scheduler-by`: `status=running`, `phase=g1_recovery`, `owner_profile=codex-builder`, run `run-1788386596-4f12c284`
- current required G1 rows: `14`, blockers `0`, `readiness_source=configured_base_ref`, `base_commit=d8194b268807ef2bb701b6d3f4302967a9e5e5be`

Resolve-state evidence is the assignment's canonical Agent Core Postgres readback at `2026-09-02T22:00Z`: `active/autonomous`, `active_runs=0`, and `unvalidated_required_docs`. This worker did not run live `factory project resolve-state` or `factory tick` because this run's hard DB-write allowlist permits only `factory status` and `factory gate record`; live resolve/tick can mutate task/run state or dispatch workers. The status readback above preserves the current Agent Core state and the forced-tick events used as source evidence.

Forced-tick readback preserved by `/tmp/r2dg-forced-tick-readback.json`:

- event `262157`: R2df-R17 (`zeus-alpha-research-ledger-core-r2df-r17-docs-first-validation-scheduler`) was denied with `unresolved_validation_tasks`; the blocker text includes generated snippets such as `validation task ... is not complete; status=todo`.
- event `262159`: R2cy-R1 product/quality review remained fail-closed with `missing_or_unindexed_docs`.
- event `262172`: this R2dg task was claimed by `factory-force-tick` for `codex-builder` with run `run-1788386596-4f12c284`.

## Root cause

The validation/readiness classifier already had structured G1/documentation recovery routing, but positive product/runtime scope detection still treated generated validation-readiness history as ordinary candidate prose. A dependency-ready `phase=g1_recovery` task that quoted the previous blocker (`validation task ... is not complete; status=todo`) could inherit ALR validation task IDs and broad completion words from audit history, be classified as product/runtime scoped, and then be held behind the same unresolved validation rows it was meant to repair.

## RED/GREEN repair

RED test added in `tests/hermes_cli/test_factory_increment_integration.py`:

- `test_claim_next_task_uses_g1_phase_before_completion_history_text_match`

The fixture reproduces an active same-project Factory task with `phase=g1_recovery`, no dependencies, red G1 readiness, and downstream validation history text containing `validation task demo-alr-061... is not complete; status=todo`. Before the repair, `claim_next_task()` returned `None` and would record `dispatch_preflight_denied`; the G1 recovery was wrongly held behind incomplete validation work.

GREEN change in `hermes_cli/factory_pg.py`:

- Adds `_text_without_validation_readiness_history()` to strip generated validation-readiness findings only from dispatch-scope prose classification.
- Applies that sanitized text to positive product/runtime classification used by structured G1/documentation recovery routing.
- Leaves broad `_has_product_or_runtime_dispatch_scope()` and explicit reporting/release/QA/security gates fail-closed for ordinary product/runtime/delivery candidates.

## Verification

Commands executed from the assigned worktree:

1. RED: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k completion_history_text_match`
   - Result: expected failure, `assert None is not None` for the new focused test.
2. GREEN targeted: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k completion_history_text_match`
   - Result: `1 tests passed, 0 failed`.
3. Related Factory scheduler/control-plane tests: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_control_plane_refactor.py`
   - Result: `309 tests passed, 0 failed`.
4. Whitespace check: `git diff --check`
   - Result: exit `0`.
5. Canonical Factory status readback: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2dg-status-after-code.json`
   - Result: `db_backend=agent_core_postgres`, source roots equal to assigned worktree, active/autonomous project, 14/14 required G1 rows non-blocking from `configured_base_ref`.

## PR-first handoff

This artifact is candidate evidence. The final candidate commit SHA, pushed branch, PR URL, and Factory gate evidence are recorded after commit/push because a Git commit cannot contain its own SHA. Independent exact-SHA quality review by a separate reviewer remains required before merge, runtime dispatch, or downstream reliance on this repair.

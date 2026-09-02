---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2d3-current-source-g1-validation-prefli
run_id: run-1788310632-d1a95b5b
phase: g1_recovery
status: implemented_pending_pr_and_independent_exact_sha_review
validated: yes
reviewed: pending_independent_exact_sha_review
owner: codex-builder
reviewer: quality-reviewer
base_ref: origin/main
base_sha: 63a866d57bda6a1258de6c93d0f244316f298828
branch: factory/zeus-alpha-research-ledger-core/inc-102-r2d3-current-source-g1-validatio
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-102-r2d3-current-source-g1-validatio
---

# R2d3 — current-source G1 validation-preflight recovery

## Scope and boundary

R2d3 is a bounded Factory scheduler/control-plane repair. It fixes the remaining current-source validation-preflight deadlock where a `factory-reporter` G1/documentation recovery task with terminal-report wording could be classified as reporting work before the docs-first repair exemption, causing `unresolved_validation_tasks` to block the recovery itself.

Changed files are limited to:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_increment_integration.py`
- project-local evidence under `factory/projects/zeus-alpha-research-ledger-core/`

This increment does not add or alter Alpha Research Ledger product/runtime code, providers, migrations, user-facing tools, credentials, messaging connectors, deployment behavior, primary checkout state, G1 reviewed frontmatter markers, task status, stale refs/PRs, direct Factory DB state, Vonash/Magnus/VAOS/RAG/KB/broker/trading/risk, or paper/live behavior.

## Canonical inputs consulted

Required Factory/G1 inputs read from the assigned worktree before implementation:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2D1_CURRENT_BASE_EXPLICIT_G1_VALIDATION_GATE_DISPATCH_RECOVERY.md`

Agent Core Postgres `factory.*` remains the operational source of truth. This document is project-local evidence and does not substitute for Factory DB gate/readback records.

## Current-source worktree identity

After `git fetch origin main --prune`, the assigned worktree read back:

```text
branch=factory/zeus-alpha-research-ledger-core/inc-102-r2d3-current-source-g1-validatio
HEAD=63a866d57bda6a1258de6c93d0f244316f298828
origin_main=63a866d57bda6a1258de6c93d0f244316f298828
merge_base=63a866d57bda6a1258de6c93d0f244316f298828
ahead_behind=0 0
```

No stale worktree, primary checkout mutation, merge, deploy, direct SQL, external runtime, or product dispatch was used.

## Canonical Factory readback

Sanctioned readback command from the assigned worktree:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2d3-status-after-code.json
```

Summarized readback:

```text
db_backend=agent_core_postgres
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-102-r2d3-current-source-g1-validatio
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-102-r2d3-current-source-g1-validatio
factory_status_delegated=false
project_status=active
reconciliation_anomalies=[]
blocking_required_docs=0
task_id=zeus-alpha-research-ledger-core-r2d3-current-source-g1-validation-prefli status=running phase=g1_recovery owner=codex-builder
run_id=run-1788310632-d1a95b5b status=running worker=codex-builder spawned_by=factory_orchestrator_tick worker_cwd=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-102-r2d3-current-source-g1-validatio
```

The same readback preserves the canonical pre-repair denial cause for events `258341`-`258344`:

```text
event_id=258341 task=zeus-alpha-research-ledger-core-r2df-r39-fail-closed-terminalization-of- blockers=["unresolved_validation_tasks", ...]
event_id=258342 task=zeus-alpha-research-ledger-core-r2df-r23-fail-closed-review-runtime-fail blockers=["unresolved_validation_tasks", ...]
event_id=258343 task=zeus-alpha-research-ledger-core-r2df-r17-docs-first-validation-scheduler blockers=["unresolved_validation_tasks", ...]
event_id=258344 task=zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation blockers=["unresolved_validation_tasks", ...]
```

## RED reproduction

Focused TDD test added first:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k reporter_g1_recovery_terminal_report_language_past_validation_readiness -v --tb=short
Result before production repair: 1 failed, 0 passed.
Failure: `unresolved_validation_tasks` was recorded for `demo-r2d3-terminal-report-g1-recovery` instead of claiming the explicit no-product/no-runtime G1 documentation recovery.
```

This reproduces the R2d3 defect class: the reporter-owned recovery quotes final-report handoff language as historical provenance, but it is still the docs-first G1/documentation recovery needed before downstream validation/product work can proceed.

## GREEN repair

Changed behavior in `hermes_cli/factory_pg.py`:

- Adds positive final-delivery/reporting text detection that ignores negative or historical/audit/quoted chunks.
- Allows `factory-reporter` tasks through `_is_docs_first_repair_dispatch_task` only when they have explicit G1/documentation recovery scope, docs-first repair terms, no positive product/runtime scope, and no positive final-delivery/reporting scope.
- Keeps reporting/final-delivery phases fail-closed; `delivery_report`, `release`, `final`, and positive final-report/gate-closure work still requires docs and validation readiness.
- Keeps product, ALR, QA, security, runtime, deploy, external execution, messaging, direct-SQL, trading/risk, paper/live, and base-branch integration candidates gated while G1 is red.

## Verification

Commands run from the assigned worktree with the hermetic wrapper:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k reporter_g1_recovery_terminal_report_language_past_validation_readiness -v --tb=short
Result after production repair: 1 test passed, 0 failed.

HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'reporter_g1_recovery_terminal_report_language_past_validation_readiness or g1_recovery_metadata_keeps_validation_and_reporting_work_fail_closed or metadata_documentation_recovery_past_validation_readiness' -v --tb=short
Result: 3 tests passed, 0 failed.

HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_increment_integration.py -v --tb=short
Result: 324 tests passed, 0 failed.
```

`git diff --check`, final candidate SHA, pushed branch, PR URL, and Factory gate evidence are recorded after commit/push because a commit cannot contain its own SHA.

## PR-first handoff

This artifact is candidate evidence. Independent exact-SHA review by a distinct reviewer remains required before merge, closure, or downstream Factory control relies on this repair.

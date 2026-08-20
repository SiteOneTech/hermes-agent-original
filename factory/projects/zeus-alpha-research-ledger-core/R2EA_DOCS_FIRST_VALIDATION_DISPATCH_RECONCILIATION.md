---
project_id: zeus-alpha-research-ledger-core
phase: documentation
status: implemented_pending_independent_quality_review
validated: yes
reviewed: pending_independent_quality_review
owner: codex-builder
engine: codex
base_ref: origin/main
base_sha: 71e5e7b2f4ace3b081f9446483784a3c5fb0b981
candidate_branch: factory/zeus-alpha-research-ledger-core/inc-001-r2ea-reconciliation-of-stale-can
candidate_sha: recorded_in_pr_handoff_after_commit
run_id: run-1787229465-7f8cb6a3
---

# R2ea — docs-first validation dispatch reconciliation

## Scope

This record covers only the bounded Factory control-plane increment R2ea. It does not deliver ALR product/runtime work, does not merge to `main`, does not deploy, does not touch credentials, and does not write directly to `factory.*`. The only sanctioned Factory DB read path used for this evidence was the Hermes Factory CLI status command.

The final commit SHA is recorded in the PR/final handoff because a commit cannot contain its own immutable SHA.

## Reproduction evidence

From the assigned isolated worktree `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2ea-reconciliation-of-stale-can`, the mandated command:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2ea-status-before.json`

returned exit 0. The snapshot shows the current canonical readback itself is sourced from the assigned worktree (`factory_cli_source_root` and `factory_status_source_root` both equal the worktree, `factory_status_delegated=false`) with 14/14 required G1 rows non-blocking from `readiness_source=configured_base_ref`; however the latest dispatch history still contains the stale docs-first/validation mismatch:

- Event `206342`: `factory-force-tick` denied ready quality validation task `zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re` with `missing_or_unindexed_docs`.
- Event `206341`: `factory-dispatcher` denied dependency-free G1 documentation recovery `zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation` with `unresolved_validation_tasks` while the same project still carried stale validation rows.
- Event `206335`: repeated denial of the same ready quality validation row with `missing_or_unindexed_docs`.

This is the dispatch-order class R2ea repairs: when a docs-first gate is red and dependency-ready G0/G1/documentation repair exists, validation/product work must not consume the tick before the repair path that can make the gate green.

## Repair

`hermes_cli/factory_pg.py` now adds a docs-first repair candidate predicate for dependency-ready G0/G1/documentation/reconciliation work. `force_tick()` consults that predicate before claiming quality/product reviews or validation rows. If such repair work exists, it routes through the normal task-claim path first; product, QA, security, delivery, and release work still pass through the existing docs-first and validation-readiness preflight blockers and remain fail-closed.

Regression coverage was added in `tests/hermes_cli/test_factory_increment_integration.py`:

- `test_force_tick_prioritizes_docs_repair_over_ready_quality_review` proves the tick claims the G1 docs repair path before a ready quality review when the docs-first repair predicate is true.
- `test_docs_first_repair_candidate_exists_only_for_dependency_ready_g1_work` proves the predicate sees dependency-ready G1/documentation repair and ignores a project that has only a validation task.

## Verification

RED evidence before the fix:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'docs_first_repair_candidate or prioritizes_docs_repair'`

Result: exit 1; 2 selected tests failed. Failures were the old ordering (`calls == ['review']` instead of `['task']`) and missing `_docs_first_repair_candidate_exists`.

GREEN evidence after the fix:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'docs_first_repair_candidate or prioritizes_docs_repair'`

Result: exit 0; 2 selected tests passed.

Broader Factory control-plane suite:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory.py tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_cron_control_plane.py tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_project_reopen.py tests/hermes_cli/test_factory_successor_control.py tests/hermes_cli/test_factory_ux_ui_designer_contract.py`

Result: exit 0; 343 tests passed, 0 failed.

Post-fix Factory status readback:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2ea-status-after.json`

Result: exit 0. Summary via `jq`: source roots equal assigned worktree, `factory_status_delegated=false`, project `status=active`, `autonomous_enabled=true`, active `reconciliation_required=false`, `reconciliation_anomalies=[]`, `reconciliation_projection_source=current_document_status`, and G1 `total=14`, `blockers=0`, `sources=["configured_base_ref"]`.

## Boundaries retained

No direct SQL, no primary-checkout mutation, no merge, no deploy, no credentials, no external runtime, no messaging operation, and no Vonash/Magnus/VAOS/RAG/KB/broker/trading/risk/paper/live system action occurred in this increment.

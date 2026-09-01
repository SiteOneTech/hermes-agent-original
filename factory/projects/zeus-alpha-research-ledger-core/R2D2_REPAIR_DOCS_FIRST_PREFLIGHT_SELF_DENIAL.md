---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2d2-repair-docs-first-preflight-self-de
phase: g1_recovery
status: implemented_pending_independent_review
validated: yes
reviewed: pending
owner: codex-builder
reviewer: quality-reviewer
created_at: 2026-09-01T23:37:20Z
---

# R2d2 — repair docs-first preflight self-denial

## Scope

This increment is bounded to Factory control-plane dispatch/preflight logic and project-local evidence for `zeus-alpha-research-ledger-core`.

No Alpha Ledger product implementation, deploy, credential change, direct SQL, primary checkout mutation, external runtime, messaging, trading/risk, paper/live activation, or base-branch merge was performed.

## Canonical input state

Allowed Factory status readback from the assigned worktree:

- Command: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2d2-status-before.json`
- Result: exit 0.
- DB backend: `agent_core_postgres` (`zeus_agent.factory`).
- Source roots in final readback: `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-103-r2d2-repair-docs-first-preflight`, `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-103-r2d2-repair-docs-first-preflight`, `factory_status_delegated=false`.
- Pre-repair evidence: events `258036` through `258040` are `dispatch_preflight_denied` records for R2df-R39, R2df-R23, R2df-R17, R2df current-base documentation, and R2cy-R1 while no previous active run existed. Event `258040` denied R2cy-R1 with `missing_or_unindexed_docs`; events `258036`-`258039` denied G1/documentation recovery rows with `unresolved_validation_tasks`.
- Current claimed run for this increment: event `258049` claimed `zeus-alpha-research-ledger-core-r2d2-repair-docs-first-preflight-self-de` as `run-1788304902-1d721958`.

The G1 rows are red in the prompt/current status because ten required rows are committed/indexed but not reviewed. The repair does not mark those rows reviewed; it only prevents the dispatch preflight from denying the review/recovery path that is needed to clear that state.

## RED evidence

Focused RED test added first:

- Test: `test_claim_next_task_allows_phase_explicit_g1_quality_repair_review_when_docs_red`
- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k phase_explicit_g1_quality_repair_review_when_docs_red -v --tb=short`
- Result before code change: failed as expected.
- Failure: `_dispatch_preflight_blockers(g1_quality_repair, docs_ready=False, notion_ready=True)` returned `['missing_or_unindexed_docs']` instead of `[]`.

This reproduces the R2cy-R1 self-denial class: an explicit `phase=quality_review`, `owner_profile=quality-reviewer` G1/docs-first Factory control-plane repair review is treated as product execution while red G1 remains fail-closed.

## GREEN repair

Code change:

- File: `hermes_cli/factory_pg.py`
- Function: `_is_docs_first_validation_repair_task`
- Behavior: a quality-review/review phase owned by `quality-reviewer` can be treated as a docs-first validation repair when the existing docs-first repair term checks match and the existing positive product/runtime/reporting/QA/security guards do not match.
- Product-scope hardening: `product quality`, `product review`, and `product validation` are explicit product/runtime dispatch scope terms so product review work remains fail-closed even when it mentions G1/docs-first evidence.

Existing fail-closed guards remain in force:

- `_has_positive_product_or_runtime_dispatch_scope(task)` still blocks ALR/product/runtime/external/direct-SQL/deploy/messaging/trading/risk/paper-live scope.
- QA/security owners and phases remain excluded before the recovery exemption.
- Reporting/final delivery phases remain gated.
- Product implementation still returns `['missing_or_unindexed_docs']` in the new regression test.
- Product quality-review work also returns `['missing_or_unindexed_docs']` in the new regression test.

## Verification

Commands run from assigned worktree `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-103-r2d2-repair-docs-first-preflight`:

1. Focused GREEN:
   - `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k phase_explicit_g1_quality_repair_review_when_docs_red -v --tb=short`
   - Result: 1 file, 1 test passed, 0 failed.

2. Full increment-integration file:
   - `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -v --tb=short`
   - Result: 1 file, 140 tests passed, 0 failed.

3. Related control-plane subset:
   - `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'dispatch_preflight or validation_readiness or explicit_g1_recovery or docs_red_preflight' -v --tb=short`
   - Result: 1 file, 13 tests passed, 0 failed.

4. Whitespace/diff check:
   - `git diff --check`
   - Result: exit 0.

5. Allowed canonical Factory status readback after code:
   - `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2d2-status-after-code.json`
   - Result: exit 0.
   - Readback confirmed `db_backend=agent_core_postgres`, source roots equal to the assigned worktree, and current R2d2 run `run-1788304902-1d721958` running.

6. Candidate-code classification probe over `/tmp/r2d2-status-before.json` with `PYTHONPATH` pointed at the assigned worktree:
   - R2df-R39, R2df-R23, R2df-R17, R2df current-base documentation, R2cy-R1, and R2d2 all classify with `repair=True`, `gated=False`, `validation_required=False`, `blockers=[]` under red docs.

## Delivery boundary

This is PR-first evidence only. The branch must receive a Zeus-signed commit and `agent:zeus` PR, then independent exact-SHA quality review. No merge or runtime propagation is authorized by this artifact.

---
document_type: docs_first_fail_closed_review_terminalization_and_dispatch_repair
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2di-docs-first-fail-closed-review-termi
run_id: run-1787140251-9b95df7e
phase: documentation
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending_independent_exact_sha_quality_review
owner: codex-builder
base_ref: origin/main
base_sha: 580ae812be9619e9dd8727e1b487c6db31e61788
branch: factory/zeus-alpha-research-ledger-core/inc-009-r2di-docs-first-fail-closed-revi
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-009-r2di-docs-first-fail-closed-revi
created_at: 2026-08-19
---

# R2di — docs-first fail-closed review terminalization and canonical-source dispatch repair

## Scope and boundary

R2di is a bounded Factory control-plane repair for project `zeus-alpha-research-ledger-core`. It addresses the source-selection gap left after R2dh and keeps the previously repaired review-run terminalization and docs-first dispatch predicates fail-closed.

Changed runtime scope is limited to Factory CLI source selection in `hermes_cli/factory.py` and regression coverage in `tests/hermes_cli/test_factory_orchestrator_tick.py`. Project-local evidence is recorded in this file plus `DOCUMENTATION_INDEX.md` and `QA_GATES.md`.

No Alpha Ledger product/runtime code, provider/model/auth configuration, migrations, tools, schedulers, deployment, credentials, messaging, external runtime, primary checkout mutation, direct SQL, task-status mutation, merge, Vonash, Magnus, VAOS, RAG/KB, broker, trading, risk, paper/live, or external-system action is authorized or performed by this increment.

## Canonical documents read before implementation

The required entrypoint and G1/control docs read for this phase were:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DH_DOCS_FIRST_CURRENT_BASE_G1_REVIEW_STATE_DISPATCH_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DB_CURRENT_ORIGIN_G1_REVIEWED_STATE_PR_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DC_BOUNDED_G1_REVIEWED_STATE_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DG_BOUNDED_G1_EXACT_SHA_INDEPENDENT_REVIEW_RECOVERY.md`

The active Factory DB/status source remains Agent Core Postgres `factory.*`; project-local Markdown is evidence and human-readable control documentation, not a replacement for canonical DB state.

## Current base and worktree identity

Captured before the final evidence update:

- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-009-r2di-docs-first-fail-closed-revi`
- Branch: `factory/zeus-alpha-research-ledger-core/inc-009-r2di-docs-first-fail-closed-revi`
- Remote: `https://github.com/SiteOneTech/hermes-agent-original.git`
- `git rev-parse HEAD`: `580ae812be9619e9dd8727e1b487c6db31e61788`
- `git rev-parse origin/main`: `580ae812be9619e9dd8727e1b487c6db31e61788`
- `git merge-base HEAD origin/main`: `580ae812be9619e9dd8727e1b487c6db31e61788`

## Canonical Factory status readback

Allowed command from the assigned worktree:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2di-status-before.json`

Summarized readback:

- Output path: `/tmp/r2di-status-before.json`
- Size: `3,934,874` bytes
- `db_backend=agent_core_postgres`
- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-009-r2di-docs-first-fail-closed-revi`
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-009-r2di-docs-first-fail-closed-revi`
- `factory_status_delegated=false`
- `document_status` rows: `22`
- G1 required rows (`category=g1_required`): `14`
- G1 blocking rows: `0`
- G1 readiness source: `configured_base_ref`
- G1 base commit: `580ae812be9619e9dd8727e1b487c6db31e61788`
- Stale primary rejected with `primary_checkout_rejected_reason=primary_checkout_not_configured_base`
- Active metadata is sourced from `current_document_status`; remaining anomaly is `pending_effective_gates`, not a current required-document blocker.

## Defect reproduced

R2dh reached origin/main as `580ae812be9619e9dd8727e1b487c6db31e61788` despite a pending task-bound exact-SHA quality gate and a `quality-reviewer` run that ended in MiniMax HTTP 429 with zero tool calls. R2db/R2dc already repaired review-run terminalization so a runtime/provider failure, empty reviewer output, prompt-only marker, or missing same-task passed review gate cannot mark review complete or integrate an increment.

The remaining R2di source-selection defect was narrower: `hermes factory project tick` resolved its orchestrator script from the running/stale primary source root unless the current cwd itself was an isolated source. That meant a stale primary root could execute a stale tick even when a clean worktree at the configured `origin/main` commit existed, while `status` and `resolve-state` already used the configured-base/current-origin source path.

## Repair

`hermes_cli/factory.py` now resolves `scripts/factory/factory_orchestrator_tick.py` with this order:

1. trusted isolated cwd source root, when available;
2. clean exact configured-base/current-origin worktree source root, when the running primary source is a strict ancestor of the configured base;
3. running source root only when no stale-behind configured-base condition exists.

If the running source is stale-behind configured base and the configured-base source is unavailable, dirty, incomplete, or otherwise unverified, tick dispatch raises a `RuntimeError` and refuses to run the stale primary script. This preserves PR-first/no-merge safety and aligns tick source selection with current-origin document status handling.

## TDD evidence

RED command (expected failure before implementation):

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k 'project_tick_prefers_configured_base_source_when_invoked_from_stale_primary_root or project_tick_fails_closed_when_configured_base_source_is_dirty' -v`

RED result: `2 failed, 21 deselected`. The stale primary orchestrator was invoked instead of the configured-base source, and dirty configured-base evidence did not fail closed.

GREEN targeted command after implementation:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k 'project_tick_prefers_configured_base_source_when_invoked_from_stale_primary_root or project_tick_fails_closed_when_configured_base_source_is_dirty' -v`

GREEN targeted result: `2 tests passed, 0 failed`.

Broader validation command:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_increment_integration.py -v`

Broader validation result: `2 files, 146 tests passed, 0 failed` (`test_factory_orchestrator_tick.py`: 23 passed; `test_factory_increment_integration.py`: 123 passed).

Diff/tracking validation:

- `git diff --check` was executed as part of the tracked-file verification command and produced no whitespace errors before the untracked-new-file check failed as expected.
- `git ls-files --error-unmatch` verified tracked pre-existing files `hermes_cli/factory.py`, `tests/hermes_cli/test_factory_orchestrator_tick.py`, `DOCUMENTATION_INDEX.md`, and `QA_GATES.md`; the new R2di artifact is intentionally untracked until staged for the delivery commit.

## Acceptance mapping

- Required review failure cannot close/integrate: covered by existing R2db/R2dc guards and the unchanged regression suite in `tests/hermes_cli/test_factory_increment_integration.py`; R2di does not relax those predicates.
- Docs-first recovery must not be denied solely by stale superseded/blocked historical validation rows or future ALR review rows: covered by existing dispatch tests in `tests/hermes_cli/test_factory_orchestrator_tick.py` and preserved by this source-selection-only change.
- Current configured-base/origin source must be used by status, resolve-state, and tick: R2di adds tick fallback to the verified configured-base source and fail-closed dirty/unavailable behavior.
- Dirty/unavailable source evidence fails closed: the new regression test proves a dirty configured-base worktree raises before executing stale primary tick code.
- PR-first policy remains intact: this increment does not merge, integrate base, mutate the primary checkout, direct-SQL mutate Factory DB, or run any external runtime/product action.

## Delivery state

This candidate remains `reviewed: pending` until a Zeus-signed `agent:zeus` PR is pushed and independently reviewed against the exact final candidate SHA. It is not self-approved and must not be represented as merged/deployed/product-ready by this artifact.

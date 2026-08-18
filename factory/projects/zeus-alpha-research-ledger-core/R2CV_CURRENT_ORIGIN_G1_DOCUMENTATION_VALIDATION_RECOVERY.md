---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2cv-current-origin-g1-documentation-val
phase: documentation
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending_independent_quality_review
owner: claude-builder
engine: claude_code
base_ref: origin/main
base_sha: 12f5696882f04ee24b6fd1bf957abafaf76eab31
branch: factory/zeus-alpha-research-ledger-core/inc-019-r2cv-current-origin-g1-documenta
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2cv-current-origin-g1-documenta
run_id: run-1787058598-db479228
predecessor_task_id: zeus-alpha-research-ledger-core-r2cu-primary-root-docs-first-g1-resolver
predecessor_pr: https://github.com/SiteOneTech/hermes-agent-original/pull/83
predecessor_head_sha: e2e46c0b22efc8446dad449bdf3c71658e2b9e53
---

# R2cv — current-origin G1 documentation validation recovery

## Scope and hard boundary

R2cv is a bounded Factory control-plane recovery for the post-R2cu/PR #83 `unvalidated_required_docs` anomaly. It changes only Factory CLI source-root delegation code, focused regression tests, and project-local evidence under `factory/projects/zeus-alpha-research-ledger-core/`.

Explicit boundary: no merge, no direct SQL, no primary-checkout mutation, no force-push, no deploy, no credential change, no external runtime, no connector/messaging activity, no trading/risk/paper/live activity, no `factory task close`, and no ALR-020 or normal product dispatch.

Allowed Factory DB interaction for this worker is limited to sanctioned CLI readbacks/evidence commands. The reproduced readbacks below use `/home/jean/Projects/hermes-agent-original/venv/bin/hermes`; no `psql`, `psycopg2`, or ad-hoc SQL/scripted DB writes were used.

## Documentation consulted

Required/project-local documents read before implementation or review evidence:

- `DOCUMENTATION_INDEX.md`
- `FACTORY_INTAKE.md`
- `REQUIREMENTS_ANALYSIS.md`
- `ADRS.md`
- `QA_GATES.md`
- `SECURITY_GATES.md`
- `G0_REPOSITORY_STRATEGY.md`
- `R2CU_PRIMARY_ROOT_DOCS_FIRST_G1_RESOLVER_REPAIR.md`
- `R2CT_BOUNDED_CANONICAL_G1_DOCUMENTATION_VALIDATION_PR_FIRST_RECOVERY.md`
- `TASK_GRAPH.md`
- `TRACKER.md`

## Identity and predecessor evidence

Before edits, the assigned worktree identity was verified:

- worktree root: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2cv-current-origin-g1-documenta`
- branch: `factory/zeus-alpha-research-ledger-core/inc-019-r2cv-current-origin-g1-documenta`
- `HEAD=origin/main=merge-base=12f5696882f04ee24b6fd1bf957abafaf76eab31`
- ahead/behind against `origin/main`: `0\t0`
- remote: `https://github.com/SiteOneTech/hermes-agent-original.git`

PR #83 was verified from GitHub as merged, non-draft, labeled `agent:zeus`, with head `e2e46c0b22efc8446dad449bdf3c71658e2b9e53` on branch `factory/zeus-alpha-research-ledger-core/inc-019-r2cu-primary-root-docs-first-g1`.

## Canonical pre-change reproduction

Before code or documentation edits, the sanctioned Factory readbacks reproduced the assigned anomaly:

- `/home/jean/Projects/hermes-agent-original/venv/bin/hermes factory status zeus-alpha-research-ledger-core --json > /tmp/r2cv-status-before-console.json`
- `/home/jean/Projects/hermes-agent-original/venv/bin/hermes factory project resolve-state zeus-alpha-research-ledger-core --json > /tmp/r2cv-resolve-state-before-console.json`

Status readback `/tmp/r2cv-status-before-console.json` reported Agent Core Postgres (`database=zeus_agent`) and the stale primary-source ten-row G1 blocker set:

- `DOC_ROWS=22`
- `G1_ROWS=14`
- `G1_BLOCKERS=10`
- blocker documents: `FACTORY_INTAKE.md`, `REQUIREMENTS_ANALYSIS.md`, `PATTERN_ANALYSIS.md`, `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, `PRD.md`, `ADRS.md`, `METHODOLOGY_PLAN.md`, `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`, `SECURITY_GATES.md`
- all ten blockers existed, were committed/indexed/validated, but had `reviewed=False` and `blocking=True`
- the visible base row was the stale reviewed-frontmatter source `df4c77fd1413a65cdb85885a06978ff157c1de4d`, not the current assigned base `12f5696882f04ee24b6fd1bf957abafaf76eab31`

Resolve-state readback `/tmp/r2cv-resolve-state-before-console.json` reported:

- `action=resolve-state`
- `status=active`
- top-level `anomalies=["unvalidated_required_docs"]`
- `unblocked.anomalies=["unvalidated_required_docs"]`
- `supervisor.health=green`
- one technical blocker remained: `zeus-alpha-research-ledger-core-r2ac-repair-pr-43-canonical-g1-readback-`

This proves the original G1 anomaly was a stale control-plane/source-root readback issue after PR #83, not a current configured-base document-content failure.

## Line-level cause

R2cu repaired `factory status` by allowing `_delegated_status_from_cwd_source()` to fall back from a stale running primary source root to `_preferred_configured_base_source_root()` when the running root is a strict ancestor of the configured base and a complete, clean worktree exactly at the configured base exists.

The post-review anomaly remained because `factory project resolve-state` uses `_delegated_project_action_from_cwd_source()`. Before R2cv, that function only checked `_preferred_cwd_source_root(running_source_root)`. If the sanctioned console script was invoked from the stale primary root itself, cwd and running source were the same root, so no delegation occurred and `cmd_project_action()` continued into the stale primary backend. That stale backend could re-present ten reviewed=false G1 blockers and top-level `unvalidated_required_docs` even after the current configured-base rows were clean.

## Repair

R2cv adds configured-base delegation for the resolver-class Factory project actions only:

- `resolve-state`
- `resolve`
- `reconcile`
- `unblock`

`resume` remains excluded from configured-base fallback so this repair does not broaden product/runtime dispatch behavior. The fallback reuses `_preferred_configured_base_source_root()`, preserving the existing fail-closed requirements: the running root must be a strict ancestor of `origin/main`, the configured-base worktree must be complete, exact, and clean, and ahead/diverged/dirty/unverified evidence does not delegate.

## RED/GREEN regression evidence

RED test, before implementation:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k test_resolve_state_prefers_configured_base_source_when_invoked_from_stale_primary_root -v --tb=short
```

Result: `1 failed, 17 deselected`; failure at `hermes_cli/factory.py:675` because `cmd_project_action()` used `_backend(args)` and the test raised `AssertionError: stale primary backend must not be used`.

Focused GREEN evidence after repair:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k 'resolve_state_prefers_configured_base_source or resolve_state_keeps_primary_readback_when_configured_base_source_is_dirty or resolve_state_keeps_ahead_running_source_local or resolve_state_keeps_diverged_running_source_local' -v --tb=short
```

Result: `4 tests passed, 0 failed`.

Full focused file evidence after repair:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -v --tb=short
```

Result: `21 tests passed, 0 failed`.

Lint evidence:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m ruff check hermes_cli/factory.py tests/hermes_cli/test_factory_orchestrator_tick.py
```

Result: `All checks passed!`.

## Post-repair status readback from the candidate source

Using the sanctioned `venv/bin/hermes` entrypoint with the candidate worktree prepended to `PYTHONPATH` for source-root validation:

```text
PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}" /home/jean/Projects/hermes-agent-original/venv/bin/hermes factory status zeus-alpha-research-ledger-core --json > /tmp/r2cv-status-final-candidate.json
```

The parsed readback reports:

- `db_backend=agent_core_postgres`, `database=zeus_agent`
- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2cv-current-origin-g1-documenta`
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2cv-current-origin-g1-documenta`
- `factory_status_delegated=False`
- active `reconciliation_anomalies=[]`, `reconciliation_projection_source=current_document_status`, `reconciliation_required=False`
- `G1_ROWS=14`, `G1_BLOCKERS=0`
- all 14 required G1 documents are `exists=True`, `committed=True`, `indexed=True`, `validated=True`, `reviewed=True`, `blocking=False`
- `readiness_source=configured_base_ref`, `base_ref=origin/main`, `base_commit=12f5696882f04ee24b6fd1bf957abafaf76eab31`
- stale primary rejected: `primary_head=4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`, `primary_checkout_accepted=False`, `primary_checkout_rejected_reason=primary_checkout_not_configured_base`

Historical event/task mentions of `unvalidated_required_docs` remain audit/projection evidence and do not override the clean current configured-base row readback. R2cv does not close/supersede any old task row.

## PR-first handoff

R2cv must be delivered as a Zeus-signed, non-draft GitHub PR against `main`, labeled `agent:zeus`. The PR body and independent quality gate must bind:

- task id `zeus-alpha-research-ledger-core-r2cv-current-origin-g1-documentation-val`
- base `12f5696882f04ee24b6fd1bf957abafaf76eab31`
- final R2cv candidate SHA after the last push
- predecessor PR #83 head `e2e46c0b22efc8446dad449bdf3c71658e2b9e53`
- status/readback paths `/tmp/r2cv-status-before-console.json`, `/tmp/r2cv-resolve-state-before-console.json`, and `/tmp/r2cv-status-final-candidate.json`
- RED/GREEN and lint outputs above
- no merge, no direct SQL, no primary-checkout mutation, no force-push, no external runtime, no ALR-020/product dispatch

R2cv does not self-approve. Completion requires an independent exact-SHA quality review PASS or bounded technical rework against the final PR candidate SHA.

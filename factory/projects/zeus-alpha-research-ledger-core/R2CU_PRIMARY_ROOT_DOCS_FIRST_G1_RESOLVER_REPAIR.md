---
project_id: zeus-alpha-research-ledger-core
increment: r2cu-primary-root-docs-first-g1-resolver
phase: documentation
run_id: run-1787055639-81f6dce7
status: implemented
validated: yes
reviewed: no
owner: claude-builder
---

# R2cu — primary-root docs-first G1 resolver regression repair

## Scope

Repair only the bounded Factory `factory status` source-root resolver path that can be invoked from the stale primary checkout path while the current configured base already contains reviewed G1 document state.

No primary checkout update, main push, merge, deploy, direct SQL, credentials, or external runtime access was performed.

## Canonical documents consulted

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2CT_BOUNDED_CANONICAL_G1_DOCUMENTATION_VALIDATION_PR_FIRST_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2BN_CANONICAL_G1_REVIEW_STATE_SOURCE_ROOT_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2BM_CANONICAL_G1_DOCS_GATE_SOURCE_ROOT_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`

## Root cause

The existing source-root protection only preferred an isolated current worktree when the shell cwd was itself a different complete Hermes source root. The primary-root invocation shape has `cwd == running_source_root`, so `_preferred_cwd_source_root()` returns no delegation candidate and `factory status` can read stale primary G1 markers instead of a verified configured-base source.

This is distinct from historical stale rows/events. The repair treats historical `unvalidated_required_docs` events as audit history only; readiness comes from the active `document_status` rows emitted by the delegated configured-base status readback.

## Repair

- Added a read-only git provenance resolver in `hermes_cli/factory.py` for `factory status` only.
- When the running Factory source root is a strict ancestor of the local configured base ref (`origin/HEAD`, falling back to `origin/main`), `factory status` searches registered git worktrees for a complete, clean source root at that exact base commit.
- If and only if that exact source root is verified, the command delegates status to `python -m hermes_cli.main factory status ... --json` with `cwd` and `PYTHONPATH` pinned to the configured-base worktree and `HERMES_FACTORY_SOURCE_DELEGATED=1` to prevent recursion.
- If the base ref, ancestry, worktree identity, completeness, or clean state cannot be verified, no delegation occurs and the normal status readback remains fail-closed.
- A Claude Code read-only diff review found that the initial `HEAD != origin/main` gate would incorrectly redirect ahead/diverged feature worktrees. The final repair gates delegation on `git merge-base --is-ancestor <running_head> <base_commit>` and adds coverage to keep ahead feature branches local.

## RED evidence

1. Primary-root stale-source reproduction test failed before implementation:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k test_status_prefers_configured_base_source_when_invoked_from_stale_primary_root -v --tb=short
Result: FAILED, 1 failed / 14 deselected. Failure: stale primary backend was used.
```

2. Claude Code review found an ahead/diverged feature-branch regression in the first implementation. A new RED test captured it:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k test_status_keeps_running_source_when_it_is_ahead_of_configured_base -v --tb=short
Result: FAILED, 1 failed / 16 deselected. Failure: ahead running source delegated to the configured-base worktree.
```

## GREEN evidence

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m ruff check hermes_cli/factory.py tests/hermes_cli/test_factory_orchestrator_tick.py
Result: All checks passed.
```

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k 'status_prefers_configured_base_source or status_keeps_primary_readback or status_keeps_running_source_when_it_is_ahead_of_configured_base' -v --tb=short
Result: 3 tests passed, 0 failed.
```

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_control_plane_refactor.py -v --tb=short
Result: 173 tests passed, 0 failed.
```

## Live readback evidence

Canonical primary-root command remains intentionally unmodified before PR merge/checkout update and still proves the original live defect:

```text
cd /home/jean/Projects/hermes-agent-original
H=/home/jean/Projects/hermes-agent-original/venv/bin/hermes
$H factory status zeus-alpha-research-ledger-core --json
Result summary: source fields absent/null; 14 G1 rows; 10 G1 blockers: FACTORY_INTAKE.md, REQUIREMENTS_ANALYSIS.md, PATTERN_ANALYSIS.md, ASSUMPTIONS_AND_OPEN_QUESTIONS.md, PRD.md, ADRS.md, METHODOLOGY_PLAN.md, TECHNICAL_BLUEPRINT.md, TASK_GRAPH.md, SECURITY_GATES.md.
```

Candidate worktree readback with current code resolves the configured base and current rows:

```text
cd /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2cu-primary-root-docs-first-g1
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json
Result summary: factory_cli_source_root and factory_status_source_root equal the assigned worktree; factory_status_delegated=false; reconciliation_anomalies=[]; reconciliation_projection_source=current_document_status; 14 G1 rows; 0 blockers; readiness_source=configured_base_ref; base_commit=ccbbcb131cfdbeb6ce170ed8cf57dc6edbb6a257; primary_head=4eb87e4cd48105af05fe974cf1d493f0e1b57ae1.
```

## Files changed

- `hermes_cli/factory.py`
- `tests/hermes_cli/test_factory_orchestrator_tick.py`
- `factory/projects/zeus-alpha-research-ledger-core/R2CU_PRIMARY_ROOT_DOCS_FIRST_G1_RESOLVER_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md` after index update

## Handoff contract

A non-draft Zeus-signed `agent:zeus` PR must bind the exact candidate SHA after commit/push. Independent quality review must record the exact SHA before completion. No merge/deploy/main push is authorized by this increment.

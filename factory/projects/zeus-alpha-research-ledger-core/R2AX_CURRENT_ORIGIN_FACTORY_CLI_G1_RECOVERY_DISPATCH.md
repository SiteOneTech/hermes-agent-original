---
project_id: zeus-alpha-research-ledger-core
phase: documentation
status: implemented_pending_pr_review
validated: yes
reviewed: pending
owner: claude-builder
run_id: run-1787023799-a62c3b47
branch: factory/zeus-alpha-research-ledger-core/inc-018-r2ax-current-origin-factory-cli
base_ref: origin/main
base_sha: e7e216272ea64a83351ae38f27688ecda47cbbbf
---

# R2ax — current-origin Factory CLI G1 recovery dispatch

## Scope boundary

R2ax is a bounded Factory control-plane / documentation recovery for `zeus-alpha-research-ledger-core-r2ax-current-origin-factory-cli-g1-recov`.

Allowed work:
- Repair the Factory CLI source-selection path so `factory project resolve-state` executed from an assigned isolated current-origin worktree uses that worktree source, not a stale primary checkout module or stale task metadata.
- Preserve existing `factory status` and `factory project tick` current-origin source provenance behavior.
- Add behavioral tests that reproduce stale-primary versus current-origin source selection and fail closed when delegated current-origin resolution fails.

Explicitly not authorized:
- ALR product/runtime implementation, ledger code, trading/risk/paper/live behavior, deployment, credential/provider/client work, external runtime execution, primary checkout mutation, direct SQL, merge, force-push, self-approval, or Factory auto-integration.

## Canonical inputs read

Read before implementation:
- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2AS_R2_INDEPENDENT_EXACT_SHA_G1_SOURCE_SELECTION_REVIEW.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2AW_ISOLATED_CURRENT_ORIGIN_FACTORY_G1_STATUS_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2CN_BOUNDED_CANONICAL_G1_DOCS_GATE_AND_PR_PROVENANCE_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2AM_STALE_PRIMARY_FACTORY_TICK_SOURCE_RESOLUTION_REPAIR.md`

## Immutable current-origin identity

Canonical Git readback from the assigned worktree after `git fetch origin main --prune`:

```text
branch=factory/zeus-alpha-research-ledger-core/inc-018-r2ax-current-origin-factory-cli
head=e7e216272ea64a83351ae38f27688ecda47cbbbf
origin_main=e7e216272ea64a83351ae38f27688ecda47cbbbf
merge_base=e7e216272ea64a83351ae38f27688ecda47cbbbf
ahead_behind=0	0
```

This establishes the worktree started from the configured current `origin/main` base. The primary checkout stale identity remains historical/rejected evidence only and was not mutated.

## Implementation

Changed code:
- `hermes_cli/factory.py`
  - Adds project-action source provenance fields for JSON payloads: `factory_cli_source_root`, `factory_project_action_source_root`, `factory_project_action_delegated`, and delegated-from root when applicable.
  - Delegates `factory project resolve-state` / `resolve` / `reconcile` / `unblock` / `resume` to the current working directory source tree when the running module source is stale but the assigned worktree contains a complete Factory CLI/backend/script tree.
  - Forces delegated subprocess `cwd`, `PYTHONPATH`, and `HERMES_FACTORY_SOURCE_DELEGATED=1` to the current-origin worktree.
  - Returns the delegated subprocess exit code and raw stderr/stdout on failure, with no fallback to stale primary/backend code.
- `tests/hermes_cli/test_factory_orchestrator_tick.py`
  - Adds RED/GREEN tests proving `resolve-state` does not use the stale backend when current-origin source is available.
  - Adds fail-closed regression coverage proving a delegated current-origin failure does not fall back to stale primary code.

## TDD and validation evidence

RED reproduction before implementation:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k 'resolve_state_prefers_isolated_cwd_source_over_stale_running_module or resolve_state_delegation_failure_does_not_fall_back_to_stale_backend' -v --tb=short
Result: 2 failed, 12 deselected. Both failures raised AssertionError("stale backend must not be used") from `cmd_project_action`, proving the previous path used stale backend code for `resolve-state`.
```

GREEN focused validation after implementation:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k 'resolve_state_prefers_isolated_cwd_source_over_stale_running_module or resolve_state_delegation_failure_does_not_fall_back_to_stale_backend' -v --tb=short
Result: 2 passed, 0 failed.
```

Broader relevant validation:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -v --tb=short
Result: 14 passed, 0 failed.

HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'document_status_uses_configured_origin_base_when_primary_checkout_stale or document_status_rejects_stale_primary_even_when_primary_docs_are_ready or status_projection_uses_origin_base_not_stale_head_or_task_metadata' -v --tb=short
Result: 3 passed, 0 failed.

git diff --check
Result: exit 0.
```

## Canonical Factory status readback

Approved Factory DB readback path used only the sanctioned CLI status command from the assigned worktree:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2ax-status-after.json
```

Parsed evidence from `/tmp/r2ax-status-after.json`:

```text
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2ax-current-origin-factory-cli
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2ax-current-origin-factory-cli
factory_status_delegated=False
project_id=zeus-alpha-research-ledger-core
project_status=active
autonomous_enabled=True
metadata_reconciliation_anomalies=[]
metadata_reconciliation_projection_source=current_document_status
document_status_rows=22
g1_required_rows=14
g1_blocking_rows=0
sample rows: FACTORY_INTAKE.md, REQUIREMENTS_ANALYSIS.md, PATTERN_ANALYSIS.md each show base_commit=e7e216272ea64a83351ae38f27688ecda47cbbbf, readiness_source=configured_base_ref, primary_checkout_accepted=False, exists/committed/indexed/validated/reviewed=True, blocking=False.
active_task_count=0
```

Live `factory project resolve-state` and `factory project tick` were not executed against Agent Core in this worker run because the hard DB-write allowlist for this increment permits only `factory status` and `factory gate record`. Their source-selection behavior is covered by the behavioral tests above and by the existing tick/status tests in `test_factory_orchestrator_tick.py`.

## Handoff requirements

Delivery remains PR-first:
- Push only branch `factory/zeus-alpha-research-ledger-core/inc-018-r2ax-current-origin-factory-cli`.
- Open a non-draft Zeus-signed PR against `main` with label `agent:zeus`.
- Record the immutable final candidate SHA in the PR body and Factory gate evidence after commit/push.
- Require independent exact-SHA review before any downstream dispatcher relies on this recovery.
- Do not merge, deploy, force-push, mutate primary checkout, direct-SQL mutate Factory DB, or claim ALR-020/product implementation from this recovery.

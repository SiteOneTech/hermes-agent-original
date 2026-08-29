---
project_id: zeus-alpha-research-ledger-core
increment: r2df-r32-current-source-unvalidated-required-docs-dispatch-recovery
phase: g1_recovery
status: implemented_pending_pr_review
validated: yes
reviewed: pending
owner: codex-builder
run_id: run-1787784926-1b88c302
---

# R2df-R32 — current-source unvalidated-required-docs dispatch recovery

## Scope

This increment repairs only the Factory control-plane route for the current-source `unvalidated_required_docs` recovery condition on `zeus-alpha-research-ledger-core`.

Assigned branch/worktree:

- branch: `factory/zeus-alpha-research-ledger-core/inc-05-r2df-r32-current-source-unvalida`
- worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-05-r2df-r32-current-source-unvalida`
- base before edits: `HEAD` = `origin/main` = merge-base = `52a039fc2b117cebfb6e3552ffff24a4658ce6f1`
- run: `run-1787784926-1b88c302`

No ALR/product implementation, runtime propagation, primary-checkout mutation, base-branch merge, deploy, credential change, external runtime/provider action, messaging connector, direct SQL, trading, risk, paper/live activation, force-push, self-approval, or task-status mutation outside the normal Factory code path is authorized by this increment.

## G1 docs consulted

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`

## Current-source failure evidence

Sanctioned Agent Core Factory readback was captured from the assigned worktree:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r32-status-before.json
wc -c /tmp/r2df-r32-status-before.json
4813440 /tmp/r2df-r32-status-before.json
```

Source-truth rows/events from that payload showed the canonical current-source condition before this run was claimed:

```text
project=zeus-alpha-research-ledger-core
status=active
autonomous_enabled=true
prior_active_runs=0
prior_reconciled_events=232824,232825
prior_reconciled_anomalies=["unvalidated_required_docs"]
prior_reconciliation_tasks_created=[]
ready_tasks_before_claim=3
todo_tasks_before_claim=12
blocked_tasks_before_claim=12
R2df-R31 status=done
R2df-R28 status=done
```

The runnable route was missing because a historical blocked task row carrying structured `metadata.reconciliation_anomaly="unvalidated_required_docs"` counted as anomaly coverage inside `ensure_reconciliation_tasks()`. That suppressed creation/reopening of the deterministic `zeus-alpha-research-ledger-core-reconcile-unvalidated-required-docs` documentation recovery, so the active autonomous project could remain at zero active runs with `claimed=null` while ALR/product rows stayed docs-first blocked.

## Code repair

Changed files:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_control_plane_refactor.py`
- project-local evidence docs under `factory/projects/zeus-alpha-research-ledger-core/`

Implementation behavior:

1. Added `_task_prevents_new_reconciliation_recovery()` to distinguish usable anomaly coverage from blocked historical audit rows.
2. `ensure_reconciliation_tasks()` now ignores blocked historical `unvalidated_required_docs` coverage when deciding whether to create/reopen the deterministic documentation reconciliation task.
3. Other anomaly families keep the existing broader coverage semantics until they have their own source-backed recovery route.
4. Product/runtime dispatch remains fail-closed: ALR implementation, QA, security, delivery, deploy, messaging, direct SQL, trading/risk and paper/live scopes are still denied by docs-first preflight while G1/docs are red.

## RED / GREEN evidence

Focused RED before the code repair:

```text
scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k spawns_unvalidated_docs_recovery_when_only_coverage_is_blocked
```

Observed failure:

```text
FAILED tests/hermes_cli/test_factory_control_plane_refactor.py::test_reconciler_spawns_unvalidated_docs_recovery_when_only_coverage_is_blocked
AssertionError: assert [] == [{'task_id': 'demo-reconcile-unvalidated-required-docs', 'code': 'unvalidated_required_docs'}]
```

Focused GREEN after the repair:

```text
scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k spawns_unvalidated_docs_recovery_when_only_coverage_is_blocked
```

Result:

```text
1 tests passed, 0 failed
```

Full changed-file GREEN:

```text
scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py
```

Result:

```text
158 tests passed, 0 failed
```

Related Factory control-plane GREEN:

```text
scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_orchestrator_tick.py
```

Result:

```text
316 tests passed, 0 failed
```

## Post-repair status readback

Sanctioned current-source status after code/docs changes:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r32-status-final.json
wc -c /tmp/r2df-r32-status-final.json
4813398 /tmp/r2df-r32-status-final.json
```

Summary:

```text
db_backend=agent_core_postgres
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-05-r2df-r32-current-source-unvalida
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-05-r2df-r32-current-source-unvalida
factory_status_delegated=false
project_status=active
autonomous_enabled=true
active_runs=1
g1_required=14
g1_blocking=0
reconciliation_anomalies=[]
reconciliation_projection_source=current_document_status
recent_reconciler_events_still_show_unvalidated_required_docs=true
```

The `active_runs=1` row is this R2df-R32 worker run. The pre-claim failure evidence remains in events `232824`/`232825` with `active_runs=0`, `anomalies=["unvalidated_required_docs"]`, and `reconciliation_tasks_created=[]`.

## Handoff

This artifact remains `reviewed: pending`. Delivery must be a non-draft Zeus-signed `agent:zeus` PR from the assigned branch against `main`, with final pushed head SHA recorded in the PR body and Factory gate notes after push. A distinct reviewer must record independent exact-SHA review before merge, primary runtime catch-up, tick/claim closure, or downstream ALR/product dispatch. This worker must not self-approve or merge.

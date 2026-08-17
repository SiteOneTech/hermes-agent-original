---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2bd-deterministic-g1-documentation-pref
phase: documentation
status: implemented_pending_independent_review
validated: yes
reviewed: pending_independent_quality_review
owner: codex-builder
engine: codex
run_id: run-1786974923-6b2ae938
base_ref: origin/main
current_origin_sha: b503ba3b57fd606956d0ebf925c83eda253bdcc5
branch: factory/zeus-alpha-research-ledger-core/inc-018-r2bd-deterministic-g1-documentat
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2bd-deterministic-g1-documentat
factory_status_before_json: /tmp/r2bd-status-before.json
factory_resolve_state_json: /tmp/r2bd-resolve-state.json
factory_tick_json: /tmp/r2bd-tick.json
factory_status_after_json: /tmp/r2bd-status-after-readbacks.json
factory_status_final_json: /tmp/r2bd-status-final.json
---

# R2bd — deterministic G1 documentation preflight reconciliation repair

## Scope and boundary

This increment is bounded to the Factory G1 documentation/status-preflight reconciliation path for `zeus-alpha-research-ledger-core`.

It does not implement Alpha Research Ledger product/runtime functionality, does not dispatch ALR-020 or any downstream product work, does not merge to `main`, does not deploy, does not change credentials, does not contact external runtimes, does not activate connectors/messaging, does not perform trading/risk/paper/live actions, does not mutate the primary checkout, and does not write direct SQL to `factory.*`.

Live Factory DB interaction was limited to canonical Factory CLI readbacks: `factory status`, `factory project resolve-state`, and `factory project tick`. The accidental stale-task cancellation observed below was produced by that canonical resolve-state path and is the source-backed failure repaired in code/tests.

## Canonical documents read

- `DOCUMENTATION_INDEX.md` — controlling G1 entrypoint, status semantics, required reading order, and R2ao/R2au/R2aw/R2bb lineage.
- `SPRINT_PLAN.md` and `TRACKER.md` — downstream ALR task ordering and current Factory status/projection history.
- `QA_GATES.md` and `SECURITY_GATES.md` — RED/GREEN, PR-first delivery, no-direct-SQL, no-primary-mutation, no-external-runtime boundaries.
- `R2AO_CURRENT_ORIGIN_G1_CONTROL_PLANE_PROJECTION_REPAIR.md`, `R2AU_CURRENT_ORIGIN_G1_DOCUMENT_STATUS_PROJECTION_REPAIR.md`, `R2AW_ISOLATED_CURRENT_ORIGIN_FACTORY_G1_STATUS_RECOVERY.md`, `R2BB_CURRENT_BASE_G1_STATUS_PROJECTION_PR63_EVIDENCE_RECOVERY.md`, and `G1_DOCUMENT_STATUS_TECHNICAL_RECOVERY.md` — prior source-backed G1 projection and stale-primary repairs.

## Immutable source readback

Read-only Git evidence after `git fetch origin main --prune` from the assigned isolated worktree:

```text
branch=factory/zeus-alpha-research-ledger-core/inc-018-r2bd-deterministic-g1-documentat
HEAD=b503ba3b57fd606956d0ebf925c83eda253bdcc5
origin/main=b503ba3b57fd606956d0ebf925c83eda253bdcc5
merge-base=b503ba3b57fd606956d0ebf925c83eda253bdcc5
primary_checkout=/home/jean/Projects/hermes-agent-original
primary_HEAD=4eb87e4cd48105af05fe974cf1d493f0e1b57ae1
primary_status=main...origin/main [ahead 3, behind 1694]
```

The primary checkout remains stale and rejected as readiness authority.

## Canonical Factory CLI status readback

Command:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2bd-status-before.json
```

Parsed result:

```text
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2bd-deterministic-g1-documentat
factory_status_delegated=false
project_status=active
autonomous_enabled=true
metadata.reconciliation_anomalies=[]
metadata.reconciliation_projection_source=current_document_status
metadata.has_g1_documentation_checkout=false
g1_count=14
g1_blocking_count=0
readiness_sources=["configured_base_ref"]
base_commits=["b503ba3b57fd606956d0ebf925c83eda253bdcc5"]
primary_checkout_accepted=[false]
blocking_docs=[]
```

The current configured-base G1 projection is clean: all 14 required documents are read from `configured_base_ref`, non-blocking, and the stale primary checkout is not accepted.

Historical docs-first dispatch denial evidence remains present as immutable events, not current G1 row evidence:

```text
recent dispatch_preflight_denied events:
195280, 195274, 195142, 195136, 194993, ...
task_id=zeus-alpha-research-ledger-core-alr-020-r2-bounded-pr-first-signature-an
blockers=["missing_or_unindexed_docs"]
```

## Canonical resolve-state and tick readbacks

Resolve-state command:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory project resolve-state zeus-alpha-research-ledger-core --json > /tmp/r2bd-resolve-state.json
```

Readback result:

```text
action=resolve-state
status=active
anomalies=[]
reconciliation_tasks_created=0
reconciliation_tasks_cancelled=0
unblocked.reopened=[
  zeus-alpha-research-ledger-core-r2ai-current-origin-g1-independent-revie,
  zeus-alpha-research-ledger-core-r2ae-bounded-canonical-g1-validation-and
]
unblocked.reconciliation_tasks_cancelled=1
blocker_count=1
blocker=zeus-alpha-research-ledger-core-r2ac-repair-pr-43-canonical-g1-readback- (technical_rework)
monitor.checked=1
supervisor.violations=[]
supervisor.repairs=[]
```

Post-resolve Factory status confirmed the exact source-backed divergence that this increment repairs: the same canonical resolve-state pass auto-cancelled the in-flight R2bd task from legacy reconciliation text even though its worker run was still `running`.

```text
r2bd_task.status=cancelled
r2bd_task.result_summary="[factory-reconciler] Reconciliation anomaly resolved; task auto-cancelled."
r2bd_task.metadata.cancel_reason=resolved_reconciliation_anomaly
r2bd_run.status=running
r2bd_run.run_id=run-1786974923-6b2ae938
r2bd_run.process_id=3767554
```

Tick command:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory project tick zeus-alpha-research-ledger-core --json > /tmp/r2bd-tick.json
```

Readback result:

```text
action=tick
control_plane_skipped=true
active_runs=1
claimed=null
spawned_worker=null
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2bd-deterministic-g1-documentat
factory_orchestrator_script=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2bd-deterministic-g1-documentat/scripts/factory/factory_orchestrator_tick.py
```

No ALR-020 or product work was claimed or spawned.

## Root cause

The active current-origin/configured-base G1 document-status projection was already clean and correctly superseded stale `unvalidated_required_docs` metadata for dispatch readiness. The remaining deterministic failure was in the resolved-reconciliation cleanup path:

- `cancel_resolved_reconciliation_tasks(...)` cancels any non-terminal reconciliation-looking task when its anomaly is absent from current findings.
- It recognized the running R2bd implementation task through legacy text (`unvalidated_required_docs` / `reconciliation`) rather than structured `factory_reconciliation_task` metadata.
- Because it did not exclude active/in-flight statuses, the canonical resolve-state operation cancelled an active worker task while its run row remained running.

That created a new status-source divergence: current G1 rows and preflight readiness were clean, but a live repair task was cancelled by stale legacy-text reconciliation cleanup instead of being allowed to finish with candidate-bound evidence.

## Repair

`hermes_cli/factory_pg.py` now keeps in-flight reconciliation repair/review work out of stale-backlog auto-cancellation. `cancel_resolved_reconciliation_tasks(...)` still cancels idle recovery backlog rows whose anomaly is gone, but it skips tasks whose status is in `ACTIVE_TASK_STATUSES` (`claimed`, `running`, `in_progress`, `review_ready`, `review_running`, `qa_ready`, `rework`).

This preserves the existing repair semantics while preventing canonical resolve-state/tick readbacks from cancelling a live worker or reviewer before evidence can be recorded.

## RED/GREEN evidence

RED added before implementation:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k inflight_reconciliation_repair -v --tb=short
```

Result before repair: 1 selected test failed. `cancel_resolved_reconciliation_tasks(...)` returned a resolved cancellation for a `running` R2bd-style reconciliation repair task from `legacy_reconciliation_text`.

GREEN after repair:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k inflight_reconciliation_repair -v --tb=short
```

Result: 1 selected test passed, 0 failed.

Relevant regression suite:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_increment_integration.py -v --tb=short
```

Result: 269 tests passed, 0 failed.

Static diff check:

```text
git diff --check
```

Result: exit 0.

## Deterministic outcome

The current `unvalidated_required_docs` anomaly is repaired through project-local documented evidence and current Factory CLI status readback: current configured-base G1 rows are clean, active metadata has `reconciliation_anomalies=[]`, and tick did not dispatch product work.

Final post-repair status readback:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2bd-status-final.json
```

Parsed result:

```text
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2bd-deterministic-g1-documentat
factory_status_delegated=false
status=active
metadata.reconciliation_anomalies=[]
metadata.reconciliation_projection_source=current_document_status
metadata.has_g1_documentation_checkout=false
g1_count=14
g1_blocking_count=0
readiness_sources=["configured_base_ref"]
base_commits=["b503ba3b57fd606956d0ebf925c83eda253bdcc5"]
primary_checkout_accepted=[false]
r2bd_task.status=cancelled
r2bd_run.status=running
r2bd_run.run_id=run-1786974923-6b2ae938
recent_preflight_denials=[195280, 195274, 195142]
```

The task/run mismatch remains preserved as source-backed evidence in Agent Core because no direct SQL repair or unauthorized task reopening was performed. The code repair prevents the same canonical cleanup path from cancelling active future repair/review work.

The exact source-backed failure found during resolve-state was not document content. It was resolved-reconciliation cleanup cancelling an in-flight R2bd-style repair task from legacy text while its run remained active. The code repair is bounded to that cleanup path and keeps G0/G1, primary-checkout rejection, PR-first delivery, and project-local docs visibility intact.

## Delivery handoff

This increment requires a Zeus-signed `agent:zeus` PR against `main` with exact candidate SHA, RED/GREEN evidence, canonical Factory readbacks, and an explicit no-external-runtime/no-direct-SQL/no-primary-mutation statement. Independent exact-SHA quality review is required before downstream product implementation dispatch can resume. This worker does not self-approve, merge, deploy, mutate credentials, or execute external runtimes.

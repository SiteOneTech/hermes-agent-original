---
document_type: factory_expired_queued_dispatch_recovery
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2df-r16-recover-expired-queued-r15-g1-d
run_id: run-1788339388-ebd101f2
phase: g1_recovery
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending
owner: codex-builder
base_ref: origin/main
base_sha: 0f16016c86a0bf0aee1878dde978bbf1942992f2
branch: factory/zeus-alpha-research-ledger-core/inc-001-r2df-r16-recover-expired-queued
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2df-r16-recover-expired-queued
created_at: 2026-08-24T10:15:31Z
updated_at: 2026-09-02T09:04:31Z
---

# R2df-R16 — recover expired queued R15 G1 dispatch

## Scope and boundary

R2df-R16 is a bounded Factory control-plane recovery for the stale queued-run dispatch defect observed after R2df-R15.

It changes only:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_increment_integration.py`
- project-local Factory evidence under `factory/projects/zeus-alpha-research-ledger-core/`

No Alpha Ledger product/runtime code, provider/model/auth config, database migration, tool registration, scheduler, deployment, credential access, messaging connector, external runtime, primary checkout mutation, direct SQL, merge, Vonash, trading, risk, paper/live activation, task-status manual mutation, or external-system operation is authorized or performed by this increment.

Factory DB interaction for this run stayed within the assignment allowlist: sanctioned `factory status` readback only before implementation evidence is recorded, and `factory gate record` for worker evidence after local validation. Mutating live `factory project tick` / `factory worker dispatch` commands were not executed against Agent Core; the canonical dispatch path is exercised by deterministic regression tests.

## G1 documents consulted

The required documentation entrypoint and applicable project docs read for this increment were:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`

The assignment prompt's `G1 readiness: 12/22 documentos sin blocker; blockers=10` line is stale prompt/readback context. The sanctioned status readback from this assigned worktree reports 14/14 current G1-required rows non-blocking from `configured_base_ref` and active `reconciliation_anomalies=[]`.

## Root cause

A Factory run can be inserted into `factory.task_runs` as `queued` after the task is claimed but before the worker wrapper writes prompt/log paths and calls `mark_run_spawned()`.

If the dispatcher process dies in that gap:

1. `monitor_runs()` previously inspected only `status='running'` runs.
2. The unspawned `queued` row remained active indefinitely.
3. Project reconciliation and claim predicates treated the stale queued run as `active_runs=1`.
4. Required G1 recovery work stayed suppressed even though no `process_id`, `session_id`, `log_path`, or `prompt_path` existed for the original run.

## Repair behavior

The repair adds `_repair_expired_queued_runs()` and invokes it from `monitor_runs()`.

It only recovers rows that meet all of these fail-closed conditions:

- `factory.task_runs.status='queued'`
- task lease is expired, or there is no lease and the queued heartbeat/start age is older than the conservative fallback window
- `process_id IS NULL`
- `session_id` is null/empty
- `log_path` is null/empty
- `prompt_path` is null/empty

For those rows it:

1. Preserves the original `run_id` by marking the original run `failed`, `exit_code=1`, and adding an explicit recovery note plus structured metadata.
2. Requeues the task through canonical Factory DB state transitions:
   - review runs/task status recover to `review_ready`;
   - rework runs recover to `rework`;
   - normal implementation/docs recovery runs recover to `ready`.
3. Clears `claimed_by`, `claimed_at`, and `lease_until` on the recovered task.
4. Records a `queued_dispatch_recovered` Factory event with the original run/task evidence and runtime contract.
5. Leaves any queued run with process/session/log/prompt evidence untouched/fail-closed for the existing running-run monitor path instead of synthesizing delivery evidence.

## RED reproduction

A temporary worktree outside the project was checked out at current `origin/main` `0f16016c86a0bf0aee1878dde978bbf1942992f2`, and only the new tests were applied there. Production code remained base.

Command:

```text
export HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python
scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'monitor_recovers_expired_unspawned_queued_run_as_non_active or recovered_g1_docs_task_dispatches_while_product_remains_docs_first_blocked' -q
```

Observed RED result:

```text
1 failed, 1 passed, 143 deselected
FAILED tests/hermes_cli/test_factory_increment_integration.py::test_monitor_recovers_expired_unspawned_queued_run_as_non_active
KeyError: 'expired_queued_runs_recovered'
```

This proves base `origin/main` did not recover/report expired queued runs through `monitor_runs()`. The companion docs-first ordering test already passed on base and is intentionally a preservation/ordering guard.

## GREEN validation

Focused GREEN on assigned branch:

```text
export HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python
scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'monitor_recovers_expired_unspawned_queued_run_as_non_active or recovered_g1_docs_task_dispatches_while_product_remains_docs_first_blocked' -q
```

Result:

```text
1 file, 2 tests passed, 0 failed
```

Full increment-integration file:

```text
export HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python
scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -q
```

Result:

```text
1 file, 145 tests passed, 0 failed
```

Related Factory control-plane regression set:

```text
export HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python
scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_orchestrator_tick.py -q
```

Result:

```text
3 files, 330 tests passed, 0 failed
```

Whitespace check:

```text
git diff --check origin/main...HEAD
```

Result: exit `0`, no output.

## Canonical Factory status/readback evidence

Sanctioned status command from the assigned worktree:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r16-status-after-code.json
```

Readback summary from `/tmp/r2df-r16-status-after-code.json`:

```text
status_size_bytes=4908006
db_backend=agent_core_postgres
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2df-r16-recover-expired-queued
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2df-r16-recover-expired-queued
factory_status_delegated=False
project_status=active
reconciliation_anomalies=[]
reconciliation_projection_source=current_document_status
documents=22 g1_required=14 g1_blocked=0
tasks=192 gates=300 runs=300 active_runs_derived=1
```

The one active run in that readback is this assigned R16 worker run, not R15:

```text
run_id=run-1788339388-ebd101f2
task_id=zeus-alpha-research-ledger-core-r2df-r16-recover-expired-queued-r15-g1-d
status=running
process_id=1897407
log_path=/home/jean/.hermes/factory/runs/run-1788339388-ebd101f2/worker.log
prompt_path=/home/jean/.hermes/factory/runs/run-1788339388-ebd101f2/prompt.md
```

The original R15 queued run named in the assignment is no longer active in the canonical readback:

```text
run_id=run-1787557361-ee18ea80
task_id=zeus-alpha-research-ledger-core-r2df-r15-canonical-base-g1-document-stat
status=cancelled
process_id=
log_path=
prompt_path=
metadata={"claimed_by": "factory-force-tick", "closed_by": "factory-orchestrator", "closure_source": "factory_task_close"}
```

This readback is evidence only. It does not substitute for the regression tests because the live DB row has already been administratively cancelled; the test reproduces and guards the exact stale queued-run class.

## Handoff

R2df-R16 remains PR-first. This artifact is implementation evidence and is `reviewed: pending` until a distinct reviewer performs independent exact-SHA review of the final pushed PR head.

Required review handoff:

- non-draft Zeus-signed GitHub PR from the assigned branch against `main`;
- `agent:zeus` label;
- exact final head/base SHA in PR body and Factory gate notes;
- independent exact-SHA review and QA evidence before closure/merge;
- no merge, deploy, primary checkout mutation, direct SQL, external runtime, credential change, messaging, or product/trading dispatch by this worker.

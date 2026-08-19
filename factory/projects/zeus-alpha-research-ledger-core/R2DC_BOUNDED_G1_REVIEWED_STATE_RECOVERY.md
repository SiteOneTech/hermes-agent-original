---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2dc-bounded-g1-reviewed-state-recovery-
run_id: run-1787104281-00be2a38
phase: documentation
status: implemented_pending_pr_and_independent_exact_sha_security_review
validated: yes
reviewed: pending_independent_exact_sha_security_review
owner: codex-builder
base_commit: c3c9332e7a5f0e3a41c49cfb0b190dfe16a8e12e
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-016-r2dc-bounded-g1-reviewed-state-r
branch: factory/zeus-alpha-research-ledger-core/inc-016-r2dc-bounded-g1-reviewed-state-r
created_at: 2026-08-18T17:40:00-04:00
updated_at: 2026-08-18T22:02:04-04:00
---

# R2dc — bounded G1 reviewed-state recovery after rate-limit terminalization

## Scope and boundary

R2dc repairs the bounded Factory review/reconcile lifecycle after the R2db review task was terminalized from a rate-limited independent-review transcript. The increment is limited to:

- Factory control-plane review terminalization and reconcile recovery code in `hermes_cli/factory_pg.py`.
- Behavioral regression tests in `tests/hermes_cli/test_factory_increment_integration.py`.
- Project-local provenance in this file plus `DOCUMENTATION_INDEX.md`, `QA_GATES.md`, `SECURITY_GATES.md`, and `TRACKER.md`.

No Vonash, Magnus, VAOS, RAG/KB, broker, trading, risk, paper/live, messaging, deployment, credential, external runtime, primary-checkout mutation, direct SQL, merge to `main`, or product/runtime propagation is authorized or performed by this increment.

## G1 docs and sources consulted

Required entrypoint and applicable G1/control docs read before and during implementation:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/REQUIREMENTS_ANALYSIS.md`
- `factory/projects/zeus-alpha-research-ledger-core/PATTERN_ANALYSIS.md`
- `factory/projects/zeus-alpha-research-ledger-core/ASSUMPTIONS_AND_OPEN_QUESTIONS.md`
- `factory/projects/zeus-alpha-research-ledger-core/PRD.md`
- `factory/projects/zeus-alpha-research-ledger-core/ADRS.md`
- `factory/projects/zeus-alpha-research-ledger-core/METHODOLOGY_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DB_CURRENT_ORIGIN_G1_REVIEWED_STATE_PR_RECOVERY.md`

## Source-backed diagnosis

Immutable base and source roots for this R2dc rework after fast-forwarding the assigned branch to current `origin/main`:

```text
branch=factory/zeus-alpha-research-ledger-core/inc-016-r2dc-bounded-g1-reviewed-state-r
HEAD=c3c9332e7a5f0e3a41c49cfb0b190dfe16a8e12e
origin_main=c3c9332e7a5f0e3a41c49cfb0b190dfe16a8e12e
merge_base=c3c9332e7a5f0e3a41c49cfb0b190dfe16a8e12e
remote_main=c3c9332e7a5f0e3a41c49cfb0b190dfe16a8e12e
```

Canonical Factory status from the assigned worktree is Agent Core Postgres (`db_backend=agent_core_postgres`). The prompt-level ten `missing=reviewed` rows were not reproduced by the live current-base `document_status` readback. Current rework status before and after resolve-state (`/tmp/r2dc-r3-status-before.json`, 3,743,482 bytes; `/tmp/r2dc-r3-status-after.json`, 3,745,782 bytes) reports all required G1 documents explicitly accounted for from `readiness_source=configured_base_ref`, `base_commit=c3c9332e7a5f0e3a41c49cfb0b190dfe16a8e12e`, with no blocking or unreviewed row:

```text
before: g1_required_count=14 g1_blocking_count=0 reviewed_false=[] blocking_docs=[] base_commit=c3c9332e7a5f0e3a41c49cfb0b190dfe16a8e12e readiness_source=configured_base_ref primary_rejected=primary_checkout_not_configured_base
after:  g1_required_count=14 g1_blocking_count=0 reviewed_false=[] blocking_docs=[] base_commit=c3c9332e7a5f0e3a41c49cfb0b190dfe16a8e12e readiness_source=configured_base_ref primary_rejected=primary_checkout_not_configured_base
```

The live source-backed defect was task/run provenance, not G1 document content. Previous R2dc recovery had already failed `run-1787087862-a08217ed` and `run-1787091478-8cfc6323`. Current status-before then found a later false-terminal review run on the same R2db task: `run-1787103961-7e25c53c` was `succeeded` with exit `0`, contained `HTTP 429`, and left the R2db task `done` at current base `c3c9332e7a5f0e3a41c49cfb0b190dfe16a8e12e`. Resolve-state `/tmp/r2dc-r3-resolve-state.json` (7,773 bytes) re-failed that run and requeued the same-project task without changing any G1 reviewed row:

```text
before task=zeus-alpha-research-ledger-core-r2db-current-origin-g1-reviewed-state-pr status=done recovered_run_id=run-1787095815-15d7fa98 increment_base_commit_after=c3c9332e7a5f0e3a41c49cfb0b190dfe16a8e12e
before run=run-1787103961-7e25c53c status=succeeded exit_code=0 contains_429=true
resolve-state action=resolve-state status=active anomalies=[] unblocked_false_review_terminalization_recoveries=1 revocations=0 scopes=0 supervisor=green blockers=1
after task=zeus-alpha-research-ledger-core-r2db-current-origin-g1-reviewed-state-pr status=review_ready evidence_status=present reason=review_output_contains_runtime_failure recovered_run_id=run-1787103961-7e25c53c increment_base_commit_after=c3c9332e7a5f0e3a41c49cfb0b190dfe16a8e12e
after run=run-1787103961-7e25c53c status=failed exit_code=1 contains_429=true review_requeued_by=factory-reconciler reason=review_output_contains_runtime_failure
```

The current source-backed cause is therefore a Factory review/integration lifecycle defect: real provider/runtime 429 transcripts can be terminalized by stale monitors and must be retrospectively requeued, but ordinary reviewer prose that documents the same 429-class condition must not be rejected when a same-task Factory review gate has passed. The rework repairs that classifier boundary instead of treating any `HTTP 429` substring as sufficient failure evidence.

## Repair implemented

1. Review-run closure now requeues actual runtime/provider failures to `review_ready` rather than treating empty output, zero-tool transcripts, prompt-only markers, provider-response `HTTP 429`, `RateLimitError`, or `API call failed` logs as code rework or as terminal success.
2. Positive review-run terminalization continues to require a same-task passed Factory review gate before `done`/integration. Project-scoped or different-task gates cannot substitute, but normal review prose may document the 429-class regression without being rejected solely because it mentions `HTTP 429` / `Too Many Requests`.
3. `reconcile_project()` now retrospectively detects stale monitors that already wrote a false successful review terminalization and fails closed by:
   - marking the offending review run `failed` with exit code `1`;
   - setting the task back to `review_ready`;
   - storing structured `false_review_terminalization_*` metadata;
   - inserting an audit event.
4. The retrospective recovery is bounded to the current configured base commit only. Historical increments whose integrated base is not the current `origin/main` are not reopened by a single resolve-state action.
5. A defensive revocation path restores any legacy/unscoped retrospective recovery rows that lack the new current-base scope marker and point at a historical integrated base. This prevents an unbounded recovery candidate from resurrecting old increments.
6. Repeated false-terminal recovery now compares the stored recovered run id to the current succeeded review run id: the same recovered run is idempotently skipped, but a later review run on the same task can still be failed/requeued when its output contains provider/runtime failure evidence.
7. Runtime-failure detection is line-oriented and context-aware: actual provider/log lines remain fail-closed, while source-backed reviewer prose that says it verified the prior `API call failed after 3 retries: HTTP 429 / Too Many Requests` condition can close only when the task-bound gate already passed.

## RED/GREEN evidence

RED was observed before the bounded implementation:

```text
scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'review_success_requires_task_bound_gate or failed_review_runtime_failure_requeues_review or review_429_log_cannot_close_even_when_exit_zero or reconcile_project_recovers_false_terminalized_review_run'
exit=1
```

Additional RED for current-base bounding/revocation was observed before the scope repair:

```text
scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'false_terminal_review_recovery_is_bounded_to_current_base or reconcile_project_revokes_unscoped_out_of_scope_false_terminal_recovery'
exit=1; 2 failed
```

GREEN after implementation:

```text
scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'review_success_requires_task_bound_gate or failed_review_runtime_failure_requeues_review or review_429_log_cannot_close_even_when_exit_zero or reconcile_project_recovers_false_terminalized_review_run or false_terminal_review_recovery_is_bounded_to_current_base or reconcile_project_revokes_unscoped_out_of_scope_false_terminal_recovery or reconcile_project_scopes_current_unscoped_false_terminal_recovery'
7 passed, 0 failed

scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py
119 passed, 0 failed

scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k resolve
selected resolve tests passed, 0 failed
```

Rework RED/GREEN for source-backed 429-class prose, prompt-only markers, actual provider failures, and repeated false-terminal recovery:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k generic_http_429 -v --tb=short
RED exit=1; failing assertion showed _integrate_increment_to_base was called for STATE:DONE + HTTP 429 Too Many Requests when a same-task review gate existed.

HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k document_429_condition -v --tb=short
RED exit=1; valid task-bound security review prose quoting `API call failed after 3 retries: HTTP 429 / Too Many Requests` was incorrectly rejected before the context-aware classifier.

HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k "document_429_condition or prompt_only_marker" -v --tb=short
RED exit=1; two failures proved valid source-backed prose was rejected and prompt-only `STATE: DONE` output was incorrectly integrated when a gate existed.

HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k "generic_http_429 or prior_recovered_run" -v --tb=short
RED exit=1 before the repeated-run guard; GREEN after repair: 2 passed, 0 failed.

HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k "document_429_condition or prompt_only_marker or generic_http_429 or failed_review_runtime_failure_requeues_review or review_429_log_cannot_close_even_when_exit_zero or prior_recovered_run" -v --tb=short
GREEN: 6 passed, 0 failed.

HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py
123 passed, 0 failed.

HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k resolve
6 passed, 0 failed.
```

The wrapper used the approved project venv fallback:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3
```

No packages were installed.

## Factory status and resolve-state evidence

Sanctioned CLI commands used for Agent Core Postgres readback/control:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2dc-r3-status-before.json
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory project resolve-state zeus-alpha-research-ledger-core --json > /tmp/r2dc-r3-resolve-state.json
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2dc-r3-status-after.json
```

Final resolve-state evidence:

```text
action=resolve-state project=zeus-alpha-research-ledger-core status=active anomalies=[] active_runs=1 pending_gates=0
unblocked_false_review_terminalization_recoveries=1 unblocked_revocations=0 unblocked_scopes=0 supervisor_health=green blockers=1
task_counts={"blocked":1,"cancelled":15,"done":62,"ready":1,"review_ready":3,"running":1,"superseded":10,"todo":9}
```

Final status evidence:

```text
project=zeus-alpha-research-ledger-core status=active autonomous=true db_backend=agent_core_postgres db_path=agent_core_postgres:zeus_agent.factory
source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-016-r2dc-bounded-g1-reviewed-state-r readiness_source=configured_base_ref base_commit=c3c9332e7a5f0e3a41c49cfb0b190dfe16a8e12e primary_rejected=primary_checkout_not_configured_base primary_head=4eb87e4cd48105af05fe974cf1d493f0e1b57ae1
g1_required_count=14 g1_blocking_count=0 reviewed_false=[] blocking_docs=[]
false_review_current_task=zeus-alpha-research-ledger-core-r2db-current-origin-g1-reviewed-state-pr status=review_ready recovered_run_id=run-1787103961-7e25c53c reason=review_output_contains_runtime_failure
false_review_current_run=run-1787103961-7e25c53c status=failed exit_code=1 review_requeued_by=factory-reconciler contains_429=true
```

No `reviewed=false` document is represented as passing. The only current false-review recovery item is the same-project R2db task, now `review_ready` for a distinct independent exact-SHA review after the later current-base rate-limited review run was failed/requeued.

## PR-first handoff

This increment must be delivered from branch `factory/zeus-alpha-research-ledger-core/inc-016-r2dc-bounded-g1-reviewed-state-r` as a Zeus-signed `agent:zeus` PR against `main`. The exact final candidate SHA must be recorded in the PR body after commit/push because a commit cannot contain its own hash. Independent review must be performed by a distinct reviewer against that exact SHA; codex-builder does not self-approve or merge.

## No-external-operation statement

R2dc used only the assigned worktree, Git readbacks, project-local file edits, `scripts/run_tests.sh`, and Factory CLI status/resolve-state readbacks. It did not deploy, merge, push `main`, mutate the primary checkout, access credentials, print secrets, change provider/auth configuration, call external runtimes, execute messaging/connectors, or perform Vonash/Magnus/VAOS/RAG/KB/broker/trading/risk/paper/live actions.

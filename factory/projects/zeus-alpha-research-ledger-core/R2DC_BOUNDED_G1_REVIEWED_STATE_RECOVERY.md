---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2dc-bounded-g1-reviewed-state-recovery-
run_id: run-1787088429-2846eebe
phase: documentation
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending_independent_exact_sha_security_review
owner: codex-builder
base_commit: 96f0cc70cf9b9da3a21dc1554673fbefdb5c1247
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-016-r2dc-bounded-g1-reviewed-state-r
branch: factory/zeus-alpha-research-ledger-core/inc-016-r2dc-bounded-g1-reviewed-state-r
created_at: 2026-08-18T17:40:00-04:00
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

Immutable base and source roots before this R2dc diff:

```text
branch=factory/zeus-alpha-research-ledger-core/inc-016-r2dc-bounded-g1-reviewed-state-r
HEAD=96f0cc70cf9b9da3a21dc1554673fbefdb5c1247
origin_main=96f0cc70cf9b9da3a21dc1554673fbefdb5c1247
merge_base=96f0cc70cf9b9da3a21dc1554673fbefdb5c1247
remote_main=96f0cc70cf9b9da3a21dc1554673fbefdb5c1247
```

Canonical Factory status from the assigned worktree is Agent Core Postgres (`db_backend=agent_core_postgres`). The prompt-level ten `missing=reviewed` rows were not reproduced by the live current-base `document_status` readback. Final status `/tmp/r2dc-status-final3.json` reports all required G1 documents explicitly accounted for from `readiness_source=configured_base_ref`, `base_commit=96f0cc70cf9b9da3a21dc1554673fbefdb5c1247`, with no blocking or unreviewed row:

```text
g1_required_count=14 g1_blocking_count=0 reviewed_false= blocking_docs= base_commit=96f0cc70cf9b9da3a21dc1554673fbefdb5c1247 readiness_source=configured_base_ref
```

The live source-backed defect was task/run provenance, not G1 document content. Status after the repair/reconcile readback shows exactly the current false-terminal review task retained in `review_ready`:

```text
false_review_current_tasks=zeus-alpha-research-ledger-core-r2db-current-origin-g1-reviewed-state-pr
task=zeus-alpha-research-ledger-core-r2db-current-origin-g1-reviewed-state-pr status=review_ready evidence_status=present reason=review_output_contains_runtime_failure increment_base_commit_after=96f0cc70cf9b9da3a21dc1554673fbefdb5c1247 increment_integration_status=integrated
run=run-1787087862-a08217ed status=failed exit_code=1 contains_429=true
```

The R2db task had been marked `done` while its independent review output contained MiniMax `RateLimitError [HTTP 429]`, `API call failed after 3 retries`, and `Messages: 1 (1 user, 0 tool calls)`. That transcript is provider/runtime failure evidence, not independent acceptance.

## Repair implemented

1. Review-run closure now requeues runtime/provider failures to `review_ready` rather than treating an HTTP 429, empty output, or zero-tool prompt-only transcript as code rework or as terminal success.
2. Positive review-run terminalization continues to require a same-task passed Factory review gate before `done`/integration. Project-scoped or different-task gates cannot substitute.
3. `reconcile_project()` now retrospectively detects stale monitors that already wrote a false successful review terminalization and fails closed by:
   - marking the offending review run `failed` with exit code `1`;
   - setting the task back to `review_ready`;
   - storing structured `false_review_terminalization_*` metadata;
   - inserting an audit event.
4. The retrospective recovery is bounded to the current configured base commit only. Historical increments whose integrated base is not the current `origin/main` are not reopened by a single resolve-state action.
5. A defensive revocation path restores any legacy/unscoped retrospective recovery rows that lack the new current-base scope marker and point at a historical integrated base. This prevents an unbounded recovery candidate from resurrecting old increments.

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

The wrapper used the approved project venv fallback:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3
```

No packages were installed.

## Factory status and resolve-state evidence

Sanctioned CLI commands used for Agent Core Postgres readback/control:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2dc-status-after.json
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory project resolve-state zeus-alpha-research-ledger-core --json > /tmp/r2dc-resolve-state-final3.json
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2dc-status-final3.json
```

Final resolve-state evidence:

```text
action=resolve-state project=zeus-alpha-research-ledger-core status=active recoveries=0 scopes=0 revocations=0 anomalies=
unblocked_recoveries=0 unblocked_scopes=1 unblocked_revocations=0
supervisor_health=green blockers=1
```

Final status evidence:

```text
project=zeus-alpha-research-ledger-core status=active autonomous=true db=agent_core_postgres
source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-016-r2dc-bounded-g1-reviewed-state-r readiness_source=configured_base_ref base_commit=96f0cc70cf9b9da3a21dc1554673fbefdb5c1247 primary_rejected=primary_checkout_not_configured_base primary_head=4eb87e4cd48105af05fe974cf1d493f0e1b57ae1
g1_required_count=14 g1_blocking_count=0 reviewed_false= blocking_docs=
false_review_current_tasks=zeus-alpha-research-ledger-core-r2db-current-origin-g1-reviewed-state-pr
```

No `reviewed=false` document is represented as passing. The only remaining current false-review recovery item is the same-project R2db task, now `review_ready` for a distinct independent exact-SHA review.

## PR-first handoff

This increment must be delivered from branch `factory/zeus-alpha-research-ledger-core/inc-016-r2dc-bounded-g1-reviewed-state-r` as a Zeus-signed `agent:zeus` PR against `main`. The exact final candidate SHA must be recorded in the PR body after commit/push because a commit cannot contain its own hash. Independent review must be performed by a distinct reviewer against that exact SHA; codex-builder does not self-approve or merge.

## No-external-operation statement

R2dc used only the assigned worktree, Git readbacks, project-local file edits, `scripts/run_tests.sh`, and Factory CLI status/resolve-state readbacks. It did not deploy, merge, push `main`, mutate the primary checkout, access credentials, print secrets, change provider/auth configuration, call external runtimes, execute messaging/connectors, or perform Vonash/Magnus/VAOS/RAG/KB/broker/trading/risk/paper/live actions.

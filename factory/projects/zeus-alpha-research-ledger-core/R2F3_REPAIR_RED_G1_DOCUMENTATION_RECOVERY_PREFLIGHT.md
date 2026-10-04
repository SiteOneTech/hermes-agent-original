---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2f3-repair-red-g1-documentation-recover
run_id: run-1788436008-85b46985
phase: g1_recovery
status: implemented_pending_pr_and_independent_exact_sha_review
validated: yes
reviewed: pending_independent_exact_sha_review
owner: codex-builder
reviewer: quality-reviewer
base_ref: origin/main
base_sha: a36cc880dd061d7f6a864937e0fe3ece44024191
code_candidate_sha: f684c4e5a996a9616c26d8cc521c1277ae35a790
branch: factory/zeus-alpha-research-ledger-core/inc-122-r2f3-repair-red-g1-documentation
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-122-r2f3-repair-red-g1-documentation
---

# R2f3 — red-G1 documentation recovery preflight repair

## Scope and boundary

R2f3 is a bounded Factory scheduler/control-plane repair. It fixes the path where a same-project G1/documentation recovery task with explicit recovery phase/metadata was denied because guardrail prose such as "fail-closed denial of Alpha Ledger implementation" was treated as positive product/runtime dispatch scope.

This increment changes only:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_increment_integration.py`
- project-local Factory evidence under `factory/projects/zeus-alpha-research-ledger-core/`

It does not implement Alpha Research Ledger product behavior, ALR increments, QA/security review execution, delivery, deploy, external runtime, messaging, brokers, trading/risk, paper/live operation, direct SQL, credential changes, primary-checkout mutation, merge, or task-status mutation outside sanctioned gate evidence.

## Canonical inputs consulted

Required Factory/G1 inputs read from the assigned worktree before and during implementation:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`

Agent Core Postgres `factory.*` remains the operational source of truth. This file is project-local evidence only.

## Worktree and candidate identity

Assigned branch/worktree readback after fetching `origin/main`:

```text
branch=factory/zeus-alpha-research-ledger-core/inc-122-r2f3-repair-red-g1-documentation
HEAD=a36cc880dd061d7f6a864937e0fe3ece44024191
origin_main=a36cc880dd061d7f6a864937e0fe3ece44024191
merge_base=a36cc880dd061d7f6a864937e0fe3ece44024191
ahead_behind=0 0
```

Code/test repair candidate commit:

```text
code_candidate_sha=f684c4e5a996a9616c26d8cc521c1277ae35a790
commit_subject=fix(factory): route red-g1 documentation recovery past guardrail prose
```

The final branch head after adding project-local evidence is recorded in the PR body and Factory gate notes, because a commit cannot reliably embed its own final SHA.

## Agent Core Postgres readback

Sanctioned readback command from the assigned worktree:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2f3-status-after-code.json
```

Summarized canonical status readback:

```text
db_backend=agent_core_postgres
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-122-r2f3-repair-red-g1-documentation
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-122-r2f3-repair-red-g1-documentation
factory_status_delegated=false
project_id=zeus-alpha-research-ledger-core
project_status=active
autonomous_enabled=true
document_rows=22
g1_required_rows=14
g1_required_blocking=0
active_reconciliation_anomalies=[]
assigned_task=zeus-alpha-research-ledger-core-r2f3-repair-red-g1-documentation-recover
assigned_task_status=running
assigned_task_phase=g1_recovery
assigned_task_owner=codex-builder
assigned_task_reviewer=quality-reviewer
assigned_task_branch=factory/zeus-alpha-research-ledger-core/inc-122-r2f3-repair-red-g1-documentation
r2df_documentation_candidate=zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation
r2df_documentation_candidate_status=todo
r2df_documentation_candidate_phase=documentation
```

Resolve-state/reconciliation event readback from the same allowed status payload:

```text
event_id=264636 type=project_reconciled actor=factory-reconciler timestamp=2026-09-03T11:45:29.326216+00:00 active_runs=0 anomalies=[unvalidated_required_docs] pending_gates=0 task_counts={blocked:16,cancelled:35,done:135,ready:3,superseded:11,todo:10}
event_id=264640 type=project_reconciled actor=factory-reconciler timestamp=2026-09-03T11:45:41.188768+00:00 active_runs=0 anomalies=[unvalidated_required_docs] pending_gates=0 task_counts={blocked:16,cancelled:35,done:135,ready:3,superseded:11,todo:10}
```

Forced-tick/dispatcher readback from the same allowed status payload:

```text
event_id=264638 type=dispatch_preflight_denied actor=factory-dispatcher task=zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation blockers=[unresolved_validation_tasks, blocked/superseded/ready/todo legacy validation rows]
event_id=264639 type=dispatch_preflight_denied actor=factory-force-tick task=zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re blockers=[missing_or_unindexed_docs]
event_id=264646 type=task_claimed actor=factory-force-tick task=zeus-alpha-research-ledger-core-r2f3-repair-red-g1-documentation-recover run_id=run-1788436008-85b46985 worker_profile=codex-builder
```

No live `factory project tick` or direct resolve-state mutation was executed by this worker: the run explicitly forbids external dispatch and permits Factory DB interaction only through `factory status` and `factory gate record`. The required forced-tick and resolve-state evidence above is therefore a readback from Agent Core Postgres via the sanctioned status payload.

## RED reproduction

A focused hermetic regression was added for a red-G1 project with zero active runs, ten blocking required-doc rows, a `review_ready` product-quality review, blocked/superseded/ready/todo legacy validation rows, a normal ALR product candidate, and a same-project documentation recovery candidate. The documentation candidate carries explicit `phase=documentation` and structured `metadata.documentation_recovery=true`, while its description preserves the fail-closed boundary text that mentions product/runtime/ALR/deploy/messaging/trading scopes negatively.

RED was verified by temporarily reverting only the production guardrail-marker change while keeping the new test, then restoring the production patch. Command:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k force_tick_claims_documentation_recovery_despite_fail_closed_boundary_prose -v --tb=short
```

Expected RED result:

```text
1 selected test failed.
Failure: assert tick["claimed"] is not None; actual tick["claimed"] was None.
```

This reproduces the live failure class from events 264638/264639: validation-preflight/product-scope routing leaves an eligible G1/documentation recovery unclaimed while legacy validation rows remain unresolved.

## GREEN repair

Changed behavior in `hermes_cli/factory_pg.py`:

- Extends `_text_without_negative_dispatch_guardrails()` so guardrail prose containing `fail-closed`, `denial`, or `denied` is treated as negative context when the same sentence also names product/runtime dispatch scopes.
- Leaves selection eligibility tied to the existing explicit phase/structured metadata checks (`phase=documentation`/`g1_recovery` or structured G1/documentation recovery metadata) rather than task-title or status prose alone.
- Keeps positive product/runtime/ALR/QA/security/delivery/deploy/external/messaging/trading/risk/paper-live scope fail-closed when those scopes are not merely quoted in a negative guardrail sentence.

GREEN commands/results:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k force_tick_claims_documentation_recovery_despite_fail_closed_boundary_prose -v --tb=short
Result: 1 test passed, 0 failed.

HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_control_plane_refactor.py -k 'force_tick or validation_readiness or docs_red_preflight or explicit_g1 or documentation_recovery' -v --tb=short
Result: 12 tests passed, 0 failed.
```

## PR-first handoff

Delivery remains PR-first only. The final pushed branch must be a Zeus-signed GitHub PR labeled `agent:zeus` against `main`, with independent exact-SHA quality review by a distinct reviewer before merge or downstream control-plane reliance.

This increment did not merge, deploy, mutate primary checkout, change credentials, run direct SQL, dispatch product/runtime work, activate messaging/brokers/trading/risk/paper-live, or open another increment.

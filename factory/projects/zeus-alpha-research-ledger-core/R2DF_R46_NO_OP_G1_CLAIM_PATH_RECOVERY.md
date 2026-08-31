---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2df-r46-no-op-g1-claim-path-recovery
phase: g1_recovery
status: implemented_pending_pr_and_independent_exact_sha_review
validated: yes
reviewed: pending_independent_review
owner: codex-builder
run_id: run-1788150162-06a016b4
branch: factory/zeus-alpha-research-ledger-core/inc-102-r2df-r46-no-op-g1-claim-path-rec
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-102-r2df-r46-no-op-g1-claim-path-rec
base_ref: origin/main
base_sha: 9cf71d8b630ac5b9ac848a85b4391e0bd78ae7f2
---

# R2df-R46 — no-op G1 claim-path recovery

## Scope boundary

This increment repairs only the Factory control-plane claim predicate for `zeus-alpha-research-ledger-core-r2df-r46-no-op-g1-claim-path-recovery`.

Allowed work:
- Reproduce a `claimed=null` control-plane path with project `active`, `autonomous_enabled=true`, zero active `factory.task_runs`, red required G1 docs, and a dependency-free `todo` / `g1_recovery` R2df-R39 candidate.
- Repair the claim-path source-of-truth mismatch so active `factory.task_runs` remain the concurrency guard, while orphan task rows in run-backed statuses do not starve an eligible G1 recovery.
- Preserve docs-first blocking for product/ALR/QA/security/delivery/runtime work.

Explicitly not authorized and not performed:
- Product/ALR implementation, normal review/QA/security/product dispatch, deployment, credential/provider changes, messaging, trading/risk/paper/live behavior, direct SQL, primary checkout mutation, merge, force-push, or self-approval.

## Canonical inputs read before implementation

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R45_STALE_CANONICAL_FACTORY_CLI_BOOTSTRAP_REPAIR.md`

## Root cause

`claim_next_task()` used task-row status alone for the single-active increment guard. A stale task row in a run-backed status such as `running`, `claimed`, `in_progress`, or `review_running` therefore blocked the entire project even when canonical `factory.task_runs` had zero active `queued` or `running` runs.

The watchdog/claimed-null projection already used `factory.task_runs` as the source of truth and correctly reported that `claimed=null` was suspicious when a dependency-free G1 recovery task was present. The claim path was stricter than the canonical run ledger and could starve R2df-R39 behind an orphan task status.

## RED evidence

Command:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k active_task_runs_not_orphan_task_status -v --tb=short`

Result before repair:

- 1 selected test failed.
- Failure: `assert None is not None` in `test_claim_next_task_uses_active_task_runs_not_orphan_task_status_for_g1_recovery`.
- The fixture snapshot had `project.status=active`, `autonomous_enabled=True`, `task_runs=[]`, red `unvalidated_required_docs`, a stale `running` task without an active run, and R2df-R39 as `todo` / `g1_recovery` / dependency-free.

## Repair

Factory control-plane changes in `hermes_cli/factory_pg.py`:

1. Adds `RUN_BACKED_IN_FLIGHT_TASK_STATUSES` for statuses that must be validated against active `factory.task_runs` before they block a new claim.
2. Adds a lazy `factory.task_runs` readback only when a project snapshot contains one of those run-backed task statuses.
3. Keeps any active `queued`/`running` task_run as a hard concurrency block.
4. Treats run-backed task statuses with no active task_run as orphan state for claim-blocking, allowing the dispatcher to claim dependency-ready G1 recovery.
5. Leaves `review_ready`, `qa_ready`, and `rework` semantics unchanged, so product/ALR/QA/security/delivery work remains docs-first gated while G1 is red.

## GREEN evidence

Focused repair test:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k active_task_runs_not_orphan_task_status -v --tb=short`

Result after repair: 1 selected test passed, 0 failed.

Full increment-integration file:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -v --tb=short`

Result: 137 tests passed, 0 failed.

Related Factory control-plane set:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_cron_control_plane.py tests/hermes_cli/test_factory_orchestrator_tick.py -v --tb=short`

Result: 176 tests passed, 0 failed.

## Canonical Factory status readback

Sanctioned readback command:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r46-status-after-code.json`

Parsed evidence from `/tmp/r2df-r46-status-after-code.json`:

- `db_backend=agent_core_postgres`
- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-102-r2df-r46-no-op-g1-claim-path-rec`
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-102-r2df-r46-no-op-g1-claim-path-rec`
- `factory_status_delegated=false`
- project is `active` and `autonomous_enabled=true`
- active run is this increment only: `run-1788150162-06a016b4` / `zeus-alpha-research-ledger-core-r2df-r46-no-op-g1-claim-path-recovery` / `running`
- `doc_blockers=[]` and active `reconciliation_anomalies=[]` from `current_document_status` in the current readback
- R2df-R39 remains `todo`, `phase=g1_recovery`, `priority=-100`, dependency-free, owned by `codex-builder`
- no non-G1 task is selected/running by this readback

Live `factory project resolve-state`, `factory project tick`, and worker dispatch were not executed by this worker after the repair because this run's hard DB-write allowlist permits only `factory status` and `factory gate record`, and the current canonical status already has this R2df-R46 worker as the sole active run. The tick/dispatch behavior is covered by the RED/GREEN control-plane tests above without opening another increment.

## Delivery handoff

Delivery remains PR-first:

- Push only branch `factory/zeus-alpha-research-ledger-core/inc-102-r2df-r46-no-op-g1-claim-path-rec`.
- Open a non-draft Zeus-signed PR against `main` with label `agent:zeus`.
- Record the immutable final candidate SHA in PR/gate evidence after commit creation because a commit cannot contain its own SHA.
- Require independent exact-SHA review by a distinct reviewer before this repair is represented as reviewed or merged.

No merge, deploy, direct SQL, primary checkout mutation, credential change, external runtime operation, product dispatch, ALR dispatch, or self-approval occurred in this worker run.

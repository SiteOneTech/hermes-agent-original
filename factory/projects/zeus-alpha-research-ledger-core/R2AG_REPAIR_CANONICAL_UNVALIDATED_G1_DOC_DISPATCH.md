# R2ag repair canonical unvalidated-G1 documentation recovery dispatch

Status: implementation evidence
Task: zeus-alpha-research-ledger-core-r2ag-repair-canonical-unvalidated-g1-doc
Worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-100-r2ag-repair-canonical-unvalidate
Branch: factory/zeus-alpha-research-ledger-core/inc-100-r2ag-repair-canonical-unvalidate
Code candidate SHA: 897acea63288808cc720de057d44d072fdf5c9c1

## Canonical docs read before change

- factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md
- factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md
- factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md
- factory/projects/zeus-alpha-research-ledger-core/R2EA_DOCS_FIRST_STALE_RUNTIME_DISPATCH_PROVENANCE_REPAIR.md
- factory/projects/zeus-alpha-research-ledger-core/R2DF_R43_G1_RECOVERY_SELECTION_STARVATION_REPAIR.md
- factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md
- factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md
- factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md

## Change

The docs-first repair classifier in `hermes_cli/factory_pg.py` now treats an explicit same-project G1/documentation recovery task as dispatchable from explicit phase or structured metadata alone, without requiring matching words in task title/description/result prose. Validation/reporting tasks and positive product/runtime/ALR scopes still fail closed behind the G1/document readiness preflight.

Focused regression coverage was added in `tests/hermes_cli/test_factory_increment_integration.py` for:

- active/autonomous project payload;
- active runs represented as empty in the forced tick payload;
- ten blocking G1 required document rows with `missing=["reviewed"]`;
- blocked R2ae predecessor;
- eligible R2df successor whose title/description intentionally do not carry docs-first routing prose;
- product, ALR, quality/security, QA, and delivery candidates remaining denied;
- forced tick claiming the phase-explicit documentation task and writing the task run event.

## RED evidence

Command:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k phase_explicit_documentation_recovery_after_blocked_r2ae -v --tb=short`

Observed before the code repair:

- `FAILED tests/hermes_cli/test_factory_increment_integration.py::test_force_tick_claims_phase_explicit_documentation_recovery_after_blocked_r2ae_when_docs_red`
- failure line: `assert tick["claimed"] is not None`
- observed value: `None`
- summary: `1 failed, 147 deselected`

## GREEN evidence

Focused single regression:

Command:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k phase_explicit_documentation_recovery_after_blocked_r2ae -v --tb=short`

Observed after repair:

- `1 tests passed, 0 failed`
- runner: `scripts/run_tests.sh`

Focused Factory files:

Command:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_control_plane_refactor.py -v --tb=short`

Observed after repair:

- `2 files, 309 tests passed, 0 failed`
- file summaries: `tests/hermes_cli/test_factory_increment_integration.py (148✓)` and `tests/hermes_cli/test_factory_control_plane_refactor.py (161✓)`

## Agent Core Postgres readbacks through canonical Hermes CLI

No direct SQL, psql, psycopg2, or ad-hoc DB scripts were used.

Status command:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`

Status summary evidence captured in `/tmp/r2ag-status-after-code-summary.json`:

- source root readback: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-100-r2ag-repair-canonical-unvalidate`
- project: `zeus-alpha-research-ledger-core`
- project status: `active`
- autonomous_enabled: `true`
- current task before resolve/tick: `zeus-alpha-research-ledger-core-r2ag-repair-canonical-unvalidated-g1-doc`, status `running`, phase `documentation`
- canonical document status at this readback had `total=22`, `blockers=0`; historical technical hold metadata still described the original R2ae/R2df `claimed=null` anomaly.

Resolve-state command:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory project resolve-state zeus-alpha-research-ledger-core --json`

Resolve-state summary evidence captured in `/tmp/r2ag-resolve-summary.json`:

- action: `resolve-state`
- project_id: `zeus-alpha-research-ledger-core`
- blocker_actions: `classified=14`, `events_recorded=14`, `questions_created=0`
- source root: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-100-r2ag-repair-canonical-unvalidate`

Forced tick command:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory project tick zeus-alpha-research-ledger-core --json`

Forced tick summary evidence captured in `/tmp/r2ag-tick-summary.json`:

- action: `tick`
- source root: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-100-r2ag-repair-canonical-unvalidate`
- script: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-100-r2ag-repair-canonical-unvalidate/scripts/factory/factory_orchestrator_tick.py`
- claimed task: `zeus-alpha-research-ledger-core-r2df-r23-fail-closed-review-runtime-fail`
- claimed task phase: `g1_recovery`
- claimed task owner: `codex-builder`
- run_id: `run-1788381777-acdae27a`
- spawned_worker.worker_profile: `codex-builder`
- spawned_worker.worker_cwd: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-03-r2df-r23-fail-closed-review-runt`

Post-tick status readback captured in `/tmp/r2ag-status-post-tick-summary.json`:

- project status: `active`
- autonomous_enabled: `true`
- document status: `total=22`, `blockers=0`
- R2ag task status: `cancelled`, with metadata `cancel_reason=resolved_reconciliation_anomaly`, `cancelled_by=factory_reconciler`
- R2df-R23 task status: `blocked`, phase `g1_recovery`, branch `factory/zeus-alpha-research-ledger-core/inc-03-r2df-r23-fail-closed-review-runt`

Operational note: the live forced tick did spawn `run-1788381777-acdae27a`. To minimize the unintended second-worker execution after collecting the required forced-tick readback, I terminated the spawned local worker process immediately (`pid 3669181`, then child `pid 3669214`). Follow-up `pgrep` showed no remaining process for `run-1788381777-acdae27a` or `inc-03-r2df-r23-fail-closed-review-runt`.

## Boundaries preserved

- Work was confined to the assigned isolated worktree.
- Primary checkout was not modified.
- No deploy, credential change, messaging, external runtime, product execution, trading/risk, or paper/live activation was performed.
- Product/ALR/quality/security/QA/delivery dispatch denial is covered by the regression test while G1/document readiness is red.

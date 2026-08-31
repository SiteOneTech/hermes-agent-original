---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2df-r47-isolated-r44-scheduler-fix-pr-r
run_id: run-1788157623-7c370716
phase: g1_recovery
status: implemented_pending_pr_and_independent_exact_sha_review
validated: yes
reviewed: pending_independent_exact_sha_review
owner: codex-builder
reviewer: quality-reviewer
base_ref: origin/main
base_sha: 654907e0ca4552953b10d27c276f1b8212d3496f
branch: factory/zeus-alpha-research-ledger-core/inc-101-r2df-r47-isolated-r44-scheduler
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-101-r2df-r47-isolated-r44-scheduler
source_r44_commits: 7cbd58fae0def9097418ee479f890089cde85314, 48f3d50924c63aa94262ebcdd21f5136fdf779b6
---

# R2df-R47 — isolated R44 scheduler-fix PR recovery

## Scope and boundary

R2df-R47 carries the minimal behavior change from the isolated R2df-R44 commits onto a fresh assigned branch/worktree based on current `origin/main`. The recovery changes only:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_increment_integration.py`
- project-local evidence under `factory/projects/zeus-alpha-research-ledger-core/`

No Alpha Research Ledger product/runtime code, provider/model/auth config, database migration, tool registration, scheduler activation, deployment, credential access/change, messaging connector, external runtime, primary-checkout mutation, direct SQL, task-status mutation, reviewed-frontmatter mutation, merge, force-push, R44 branch/PR mutation, PR #138 mutation, Vonash/Magnus/VAOS/RAG/KB/broker/trading/risk, or paper/live action is authorized or performed by this increment.

## Canonical inputs consulted

Required Factory/G1 inputs read from the assigned worktree before implementation:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R43_G1_RECOVERY_SELECTION_STARVATION_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R45_STALE_CANONICAL_FACTORY_CLI_BOOTSTRAP_REPAIR.md`

Agent Core Postgres `factory.*` remains the operational source of truth; this artifact is project-local evidence, not a DB substitute.

## Current-origin rework base and Factory status readback

Worktree identity after rebasing the assigned branch onto the freshly fetched current `origin/main`:

- Branch: `factory/zeus-alpha-research-ledger-core/inc-101-r2df-r47-isolated-r44-scheduler`
- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-101-r2df-r47-isolated-r44-scheduler`
- Remote: `https://github.com/SiteOneTech/hermes-agent-original.git`
- `git rev-parse origin/main`: `654907e0ca4552953b10d27c276f1b8212d3496f`
- `git merge-base HEAD origin/main`: `654907e0ca4552953b10d27c276f1b8212d3496f`
- `git status --short --branch`: assigned branch ahead of `origin/main` by the local R2df-R47 candidate only before push

Allowed Factory status command from the assigned worktree:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r47-status-after-current-origin.json`

Summarized readback after code/tests:

- `db_backend=agent_core_postgres`
- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-101-r2df-r47-isolated-r44-scheduler`
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-101-r2df-r47-isolated-r44-scheduler`
- `factory_status_delegated=false`
- `project_id=zeus-alpha-research-ledger-core`, `status=active`, `autonomous_enabled=true`
- active `reconciliation_anomalies=[]`
- active `reconciliation_projection_source=current_document_status`
- G1 required rows: `14`
- G1 blocking rows: `0`
- `readiness_source=configured_base_ref`
- `base_commit=654907e0ca4552953b10d27c276f1b8212d3496f`
- R2df-R47 task: `status=running`, `phase=g1_recovery`, `owner=codex-builder`
- R2df-R47 run: `run-1788157623-7c370716`, `status=running`, `worker=codex-builder`, `spawned_by=factory_orchestrator_tick`

No live `factory project tick` was executed by this worker because the hard DB-write boundary for this run permits only `factory status` and `factory gate record`. The forced-tick behavior is covered hermetically by `tests/hermes_cli/test_factory_increment_integration.py::test_force_tick_uses_explicit_g1_recovery_metadata_before_review_when_docs_red`, which remains green in the full focused file run. The canonical status readback above shows the current R2df-R47 recovery worker claimed/running and source-backed as spawned by `factory_orchestrator_tick`.

## R44 source recovery

The source recovery existed only in the isolated R2df-R44 worktree commits:

- `7cbd58fae0def9097418ee479f890089cde85314` — `fix(factory): allow explicit g1 recovery validation preflight`
- `48f3d50924c63aa94262ebcdd21f5136fdf779b6` — `docs(factory): record r2df-r44 handoff state`

R2df-R47 does not force-push, reset, reuse, or mutate the R44 branch/worktree/PR. It ports only the minimal scheduler/control-plane code and regression coverage onto this assigned current-base branch.

## Defect reproduced

The dispatcher can correctly select an eligible no-product/no-runtime G1/documentation recovery candidate ahead of product work while required G1 rows are red, then reject that selected candidate solely under `unresolved_validation_tasks` because validation-readiness still treats historical final-stage wording as requiring downstream validation rows first.

Focused RED tests were added before production repair:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'metadata_documentation_recovery_past_validation_readiness or g1_recovery_metadata_keeps_validation_and_reporting_work_fail_closed' -v --tb=short`

RED result: `2 failed, 136 deselected`.

- `test_claim_next_task_allows_metadata_documentation_recovery_past_validation_readiness` returned `None` instead of claiming the metadata-classified documentation recovery; the fixture contains red G1 rows, a product task, and one open validation blocker.
- `test_g1_recovery_metadata_keeps_validation_and_reporting_work_fail_closed` showed a reporting candidate with `phase=g1_recovery`/`metadata.g1_recovery=true` did not require validation readiness.

## Repair

The GREEN change adds explicit structured recovery classification and fail-closed exclusions:

- `metadata.documentation_recovery`, `metadata.docs_first_recovery`, `metadata.g1_documentation_recovery`, or `metadata.validation_preflight_recovery` now mark documentation recovery explicitly.
- Metadata-based recovery exemption is accepted only for G0/G1, planning, documentation, or explicit `g1_recovery` phases.
- Reporting candidates are identified from explicit owner/phase (`factory-reporter`, `delivery`, `delivery_report`, `final`, `final_report`, `release`, `report`, `reporting`, `critical_readiness`) and remain validation/docs-first gated even if their metadata says `g1_recovery`.
- Validation tasks remain fail-closed by docs-first preflight unless they are the separately recognized docs-first validation-repair path.
- Positive product/runtime/ALR scope is not exempted; product, runtime, ALR, QA, security and reporting candidates remain fail-closed.

## Verification evidence

Commands run from the assigned worktree:

1. RED on current `origin/main` `654907e0ca4552953b10d27c276f1b8212d3496f` with only the new tests active and `hermes_cli/factory_pg.py` restored from `origin/main`: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'metadata_documentation_recovery_past_validation_readiness or g1_recovery_metadata_keeps_validation_and_reporting_work_fail_closed' -v --tb=short`
   - Result: `2 failed, 136 deselected`.
2. GREEN targeted: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'metadata_documentation_recovery_past_validation_readiness or g1_recovery_metadata_keeps_validation_and_reporting_work_fail_closed' -v --tb=short`
   - Result: `2 passed, 0 failed`.
3. Full focused file: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -v --tb=short`
   - Result: `138 passed, 0 failed`.
4. Related Factory control-plane set: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_increment_integration.py -v --tb=short`
   - Result: `3 files, 319 passed, 0 failed`.
5. Whitespace check: `git diff --check`
   - Result: exit `0`, no output.
6. Canonical Factory status readback: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r47-status-after-current-origin.json`
   - Result: exit `0`; Agent Core Postgres payload summarized above.

## Delivery state

This candidate is implemented and locally validated for PR-first handoff. Commit, push, PR URL, Factory gate id, and exact pushed head SHA are recorded in external readbacks after the containing commit is created, because a committed file cannot reliably name the immutable SHA of the commit that contains itself. Independent exact-SHA review by a distinct reviewer remains pending. This artifact does not self-approve, merge, deploy, mutate Factory task status, mutate the primary checkout, force-push, mutate R44/PR #138, or authorize ALR-020/product/runtime dispatch.

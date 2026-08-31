---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2df-r44-explicit-g1-recovery-validation
run_id: run-1788136575-1926bdc5
phase: g1_recovery
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending_independent_exact_sha_review
owner: codex-builder
reviewer: quality-reviewer
base_ref: origin/main
base_sha: 75c13a1ce85afc16da3ff708ad7f1d203b892ab4
branch: factory/zeus-alpha-research-ledger-core/inc-101-r2df-r44-explicit-g1-recovery-va
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-101-r2df-r44-explicit-g1-recovery-va
created_at: 2026-08-30T20:57:31-04:00
---

# R2df-R44 — explicit G1 recovery validation-preflight repair

## Scope and boundary

R2df-R44 is a bounded Factory scheduler/control-plane repair. It changes only:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_increment_integration.py`
- project-local evidence under `factory/projects/zeus-alpha-research-ledger-core/`

No Alpha Research Ledger product/runtime code, provider/model/auth config, database migration, tool registration, scheduler activation, deployment, credential access/change, messaging connector, external runtime, primary-checkout mutation, direct SQL, task-status mutation, reviewed-frontmatter mutation, merge, Vonash/Magnus/VAOS/RAG/KB/broker/trading/risk, or paper/live action is authorized or performed by this increment.

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
- `factory/projects/zeus-alpha-research-ledger-core/R2DL_G1_DOCUMENTATION_DISPATCH_VALIDATOR_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R43_G1_RECOVERY_SELECTION_STARVATION_REPAIR.md`

Agent Core Postgres `factory.*` remains the operational source of truth; this artifact is project-local evidence, not a DB substitute.

## Current base and Factory status readback

Worktree identity before code edits:

- Branch: `factory/zeus-alpha-research-ledger-core/inc-101-r2df-r44-explicit-g1-recovery-va`
- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-101-r2df-r44-explicit-g1-recovery-va`
- Remote: `https://github.com/SiteOneTech/hermes-agent-original.git`
- `git rev-parse HEAD`: `75c13a1ce85afc16da3ff708ad7f1d203b892ab4`
- `git rev-parse origin/main`: `75c13a1ce85afc16da3ff708ad7f1d203b892ab4`
- `git merge-base HEAD origin/main`: `75c13a1ce85afc16da3ff708ad7f1d203b892ab4`

Allowed Factory status command from the assigned worktree:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r44-status-after-code.json`

Summarized readback after code/tests:

- `db_backend=agent_core_postgres`
- `project_id=zeus-alpha-research-ledger-core`, `status=active`, `autonomous_enabled=true`
- active `reconciliation_anomalies=[]`
- G1 required rows: `14`
- G1 blocking rows: `0`
- `readiness_source=["configured_base_ref"]`
- `base_commit=75c13a1ce85afc16da3ff708ad7f1d203b892ab4`
- R2df-R44 task: `status=running`, `phase=g1_recovery`, `owner=codex-builder`, `claimed_by=factory-force-tick`
- R2df-R44 run: `run-1788136575-1926bdc5`, `status=running`, `worker=codex-builder`, `started_at=2026-08-31T00:36:15.482191+00:00`

No Factory tick was run by this worker because the task was already claimed/running and this run's DB write policy permits only `factory status` and `factory gate record` evidence, not opening/claiming another increment.

## Defect reproduced

The dispatcher can select a dependency-ready G1/documentation recovery candidate before product work while required G1 rows are red, then reject the selected candidate under `unresolved_validation_tasks` because validation-readiness still treats historical final-stage wording as requiring downstream validation rows first.

Source-backed historical evidence preserved in the Factory status event window included repeated `dispatch_preflight_denied` rows for the same class: R2df-R39, R2df-R23, R2df-R17 and the existing R2df documentation candidate were denied with `unresolved_validation_tasks` while product/ALR/QA/security validation rows remained open.

Focused RED tests were added before production repair:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'metadata_documentation_recovery_past_validation_readiness or g1_recovery_metadata_keeps_validation_and_reporting_work_fail_closed' -v --tb=short`

RED result: `2 failed, 136 deselected`.

- `test_claim_next_task_allows_metadata_documentation_recovery_past_validation_readiness` returned `None` instead of claiming the metadata-classified documentation recovery; the fixture records red G1 rows plus an open validation blocker and verifies `unresolved_validation_tasks` is not emitted after repair.
- `test_g1_recovery_metadata_keeps_validation_and_reporting_work_fail_closed` showed a report candidate with `phase=g1_recovery`/`metadata.g1_recovery=true` did not require validation readiness.

## Repair

The repair adds explicit structured recovery classification and fail-closed exclusions:

- `metadata.documentation_recovery`, `metadata.docs_first_recovery`, `metadata.g1_documentation_recovery`, or `metadata.validation_preflight_recovery` now mark documentation recovery explicitly.
- Metadata-based recovery exemption is accepted only for G0/G1, planning, or documentation recovery phases, not arbitrary implementation/QA/security/report phases.
- Reporting candidates are identified from explicit owner/phase (`factory-reporter`, `delivery`, `delivery_report`, `final`, `final_report`, `release`, `report`, `reporting`, `critical_readiness`) and remain validation/docs-first gated even if their metadata says `g1_recovery`.
- Validation tasks remain fail-closed by docs-first preflight unless they are the separately recognized docs-first validation-repair path.
- No positive product/runtime/ALR scope is exempted; product, runtime, ALR, QA, security and reporting candidates remain fail-closed.

## Verification evidence

Commands run from the assigned worktree:

1. RED: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'metadata_documentation_recovery_past_validation_readiness or g1_recovery_metadata_keeps_validation_and_reporting_work_fail_closed' -v --tb=short`
   - Result: `2 failed, 136 deselected`.
2. GREEN targeted: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'g1_recovery_metadata_keeps_validation_and_reporting_work_fail_closed or metadata_documentation_recovery_past_validation_readiness' -v --tb=short`
   - Result: `2 passed, 0 failed`.
3. Full focused file: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -v --tb=short`
   - Result: `138 passed, 0 failed`.
4. Related Factory control-plane set: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_increment_integration.py -v --tb=short`
   - Result: `3 files, 318 passed, 0 failed`.
5. Whitespace check: `git diff --check`
   - Result: exit `0`.
6. Canonical Factory status readback: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r44-status-after-code.json`
   - Result: exit `0`; Agent Core Postgres payload summarized above.

## Delivery state

This candidate is implemented and locally validated for PR-first handoff. Commit, push, PR URL, Factory gate id, and exact pushed head SHA are recorded in external readbacks after the containing commit is created, because a committed file cannot reliably name the immutable SHA of the commit that contains itself. Independent exact-SHA review by a distinct reviewer remains pending. This artifact does not self-approve, merge, deploy, mutate Factory task status, mutate the primary checkout, or authorize ALR-020/product/runtime dispatch.

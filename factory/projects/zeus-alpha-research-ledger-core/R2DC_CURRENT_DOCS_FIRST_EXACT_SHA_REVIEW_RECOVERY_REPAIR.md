---
document_type: current_docs_first_exact_sha_review_recovery_repair
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2dc-repair-current-docs-first-misclassi
run_id: run-1788366777-5d59771a
phase: g1_recovery
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending
owner: codex-builder
base_ref: origin/main
base_sha: d8194b268807ef2bb701b6d3f4302967a9e5e5be
branch: factory/zeus-alpha-research-ledger-core/inc-118-r2dc-repair-current-docs-first-m
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-118-r2dc-repair-current-docs-first-m
created_at: 2026-09-02T16:49:20Z
---

# R2dc — current docs-first exact-SHA review recovery dispatch repair

## Scope and boundary

This increment is a bounded Factory scheduler/control-plane repair for the current docs-first misclassification of the eligible R2cy-R1 independent exact-SHA quality-review recovery row. It changes only:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_increment_integration.py`
- this project-local Factory evidence document and `DOCUMENTATION_INDEX.md`

No Alpha Ledger product/runtime code, provider/model/auth config, database migration, tool registration, deployment, credential access, messaging connector, external runtime, trading/risk, paper/live activation, primary checkout mutation, direct SQL, merge, or live product/QA/security/delivery dispatch is authorized or performed by this increment.

Factory DB interaction for this implementation stayed within the hard allowlist from the assignment: sanctioned `factory status` readbacks and, after validation, `factory gate record` only. Live `factory project resolve-state` / `factory project tick` mutating commands were intentionally not executed against Agent Core. The canonical forced-tick function path is exercised by deterministic RED/GREEN regression tests without mutating live Factory task rows.

## G1 documents read before implementation

The required documentation entrypoint and applicable G1/project docs read for this increment were:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2CY_R3_DOCS_FIRST_G1_EXACT_SHA_REVIEW_DISPATCH_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2D1_CURRENT_BASE_EXPLICIT_G1_VALIDATION_GATE_DISPATCH_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R43_G1_RECOVERY_SELECTION_STARVATION_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2EA_DOCS_FIRST_STALE_RUNTIME_DISPATCH_PROVENANCE_REPAIR.md`

## Canonical Agent Core status and current candidate readback

Sanctioned command:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2dc-status-after-code.json`

Result: exit `0`; `/tmp/r2dc-status-after-code.json` is 4,956,559 bytes.

Readback summary from `/tmp/r2dc_summarize_status.py`:

- `db_backend=agent_core_postgres`
- `db_path=agent_core_postgres:zeus_agent.factory`
- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-118-r2dc-repair-current-docs-first-m`
- `factory_status_delegated=false`
- project `status=active`, `autonomous_enabled=true`
- active task run is this implementation run `run-1788366777-5d59771a`; no product/QA/security/delivery run was started by this repair
- open task counts at readback: `ready=3`, `todo=12`, `blocked=14`, `running=1`
- project metadata at readback: `reconciliation_anomalies=[]`, `reconciliation_required=false`
- target current review-recovery row:
  - `task_id=zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re`
  - `status=ready`
  - `phase=quality_review`
  - `owner_profile=quality-reviewer`
  - `reviewer_profile=security-reviewer`
  - `priority=17`, `increment_order=17`
  - `branch=factory/zeus-alpha-research-ledger-core/inc-017-r2cy-r1-independent-exact-sha-qu`
  - `worktree_path=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2cy-r1-independent-exact-sha-qu`
  - `metadata={"repo_strategy_status":"passed","source":"factory_task_create"}`

Exact R2cy-R1 candidate PR readback:

- `gh pr view 99 --repo SiteOneTech/hermes-agent-original --json number,state,isDraft,headRefName,headRefOid,baseRefName,baseRefOid,mergeStateStatus,labels,url,title`
- PR #99 is `OPEN`, non-draft, labeled `agent:zeus`
- PR URL: `https://github.com/SiteOneTech/hermes-agent-original/pull/99`
- PR title: `fix(factory): reconcile diverged runtime source provenance`
- PR head branch: `factory/zeus-alpha-research-ledger-core/inc-021-r2cy-runtime-source-provenance-reconciliation`
- exact PR head SHA: `ead1aec54288123ff12c049bc4eb0f29d55d288b`
- base branch: `main`
- base SHA: `71e5e7b2f4ace3b081f9446483784a3c5fb0b981`

## RED reproduction

Command:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k current_docs_first_exact_sha_review_recovery_while_g1_red`

Pre-fix result: exit `1` with one selected test failed. The focused test reproduced the current canonical shape: active project with red G1 document status, no active product run, the R2cy-R1 row as `status=ready` / `phase=quality_review` / `owner_profile=quality-reviewer` / `reviewer_profile=security-reviewer` / metadata only `repo_strategy_status=passed, source=factory_task_create`, plus product, ALR, QA/security, and delivery candidates. `factory_pg.force_tick("demo")` returned `claimed=None`, proving the eligible same-project review recovery was still misclassified as product execution and left unclaimed.

Agent Core status also preserves source-backed forced-tick misclassification evidence for the same row. Recent `dispatch_preflight_denied` events for `zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re` include event `261080` at `2026-09-02T16:31:48.629244+00:00` with message `Product execution dispatch denied until Factory docs/index/Notion gates are ready` and metadata `blockers=["missing_or_unindexed_docs"]`, `runtime_contract=docs_first_factory_product_execution_dispatch`.

## GREEN repair

The scheduler repair adds a structured review-recovery classifier:

- it allows only rows whose explicit `phase` is `quality_review`, whose owner is `quality-reviewer`, whose reviewer is present and independent, whose metadata says `source=factory_task_create` and `repo_strategy_status=passed`, whose assigned branch/worktree are present and same-project, and whose metadata does not mark product/runtime/delivery/ALR chain scope;
- it does not use title, status text, result-summary prose, or denial-event strings as a positive allow signal;
- product/runtime/ALR metadata keys (`project_phase`, `delivery_protocol`, integration waiver/rework metadata, product/runtime scope metadata) remain disqualifying;
- reporting, QA, security, delivery, direct-SQL, external runtime, messaging, trading/risk, and product candidates remain docs-first gated while G1 is red.

The existing explicit G1/documentation recovery path is also kept phase/metadata based: once a validation/review task passes the existing non-product/non-runtime/reporting exclusions and has explicit G0/G1/documentation phase or structured recovery metadata, it no longer needs title/description keyword matches.

## GREEN verification

Focused RED/GREEN target after repair:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'current_docs_first_exact_sha_review_recovery_while_g1_red or docs_first_pr_review_repair_when_docs_red or g1_recovery_metadata_keeps_validation_and_reporting_work_fail_closed or g1_recovery_metadata_scope_keeps_product_runtime_and_external_work_fail_closed or metadata_documentation_recovery_past_validation_readiness or metadata_phase_for_g1_recovery_before_validation_history'`

Result: exit `0`; 6 tests passed, 0 failed.

Focused file verification:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py`

Result: exit `0`; 148 tests passed, 0 failed.

Related Factory control-plane verification:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_cron_control_plane.py tests/hermes_cli/test_factory_successor_control.py tests/hermes_cli/test_factory_project_reopen.py tests/hermes_cli/test_factory_control_plane_refactor.py`

Result: exit `0`; 363 tests passed, 0 failed.

Direct current-row classifier probe against the sanctioned Agent Core status snapshot using the repaired worktree source:

`PYTHONPATH=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-118-r2dc-repair-current-docs-first-m /home/jean/Projects/hermes-agent-original/venv/bin/python3 /tmp/r2dc_probe_real_task.py`

Result: `{'is_validation_repair': True, 'is_docs_repair_dispatch': True, 'blockers_red_docs': []}`.

## Delivery state

This increment is PR-first only. The final pushed branch head cannot be self-embedded into this document before the commit that creates it; exact final candidate SHA, PR URL, and gate evidence must be recorded in Factory gate evidence and/or PR body after the final push. The implementation itself records no merge, no live `resolve-state`, no live `tick`, no primary checkout mutation, no direct SQL, no deploy, no external runtime, no messaging, and no product/trading/risk/paper-live operation.

---
document_type: docs_first_validation_preflight_deadlock_repair
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2df-r36-docs-first-validation-preflight
run_id: run-1788045931-1f353ced
phase: g1_recovery
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending_independent_exact_sha_quality_review
owner: codex-builder
base_ref: origin/main
base_sha: 17cfaf1f2fa01378df331b74471bf638289aa811
branch: factory/zeus-alpha-research-ledger-core/inc-08-r2df-r36-docs-first-validation-p
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-08-r2df-r36-docs-first-validation-p
created_at: 2026-08-29T23:54:36Z
---

# R2df-R36 — docs-first validation-preflight deadlock repair

## Scope and boundary

R2df-R36 is a bounded Factory control-plane repair for the docs-first validation-preflight dispatcher path. It changes only:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_increment_integration.py`
- project-local evidence under `factory/projects/zeus-alpha-research-ledger-core/`

No Alpha Research Ledger product/runtime code, provider/model/auth config, database migration, tool registration, scheduler, deployment, credential access, messaging connector, external runtime, primary checkout mutation, task-status mutation, direct SQL, merge, Vonash, Magnus, VAOS, RAG/KB, broker, trading, risk, paper/live activation, or external-system operation is authorized or performed by this increment.

Factory DB interaction for this run stays within the assignment allowlist: sanctioned `factory status` readback and `factory gate record` evidence only. No `factory project tick`, `factory project resolve-state`, `factory task close`, direct SQL, deploy, credential, or external runtime action is used to prove this code path.

## Canonical inputs read before implementation

Required documentation entrypoint and applicable G1/project docs consulted from the assigned worktree:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DL_G1_DOCUMENTATION_DISPATCH_VALIDATOR_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2EA_DOCS_FIRST_STALE_RUNTIME_DISPATCH_PROVENANCE_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R8_CURRENT_BASE_DOCS_FIRST_DISPATCH_RECOVERY.md`

Agent Core Postgres `factory.*` remains the operational source of truth. This file is repo-local evidence only.

## Current base and worktree identity

Read-only Git evidence after `git fetch origin main --prune`:

- `HEAD=17cfaf1f2fa01378df331b74471bf638289aa811`
- `origin/main=17cfaf1f2fa01378df331b74471bf638289aa811`
- `merge-base=17cfaf1f2fa01378df331b74471bf638289aa811`
- `ahead-behind=0\t0`
- branch: `factory/zeus-alpha-research-ledger-core/inc-08-r2df-r36-docs-first-validation-p`
- worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-08-r2df-r36-docs-first-validation-p`
- remote: `https://github.com/SiteOneTech/hermes-agent-original.git`

## Defect reproduced

The historical terminal-state wording path was a documentation recovery, not product work:

- phase: `documentation recovery`
- task id: `zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation`
- text includes `claimed=null`, expired no-worker terminal-state audit wording, and negative guardrails such as no deploy/direct SQL/external runtime/trading/paper-live action.

Before the repair, phase normalization handled hyphens but not whitespace. A `documentation recovery` phase was not recognized as a documentation-family repair phase, and the negative guardrail words still contained sensitive product/runtime terms. With G1 docs not ready and a normal validation task unresolved, `_next_runnable_task()` applied `unresolved_validation_tasks` to the documentation recovery itself, so `claim_next_task()` returned `None` (`claimed=null`) instead of claiming the docs path that would unblock validation.

Focused RED regression added before implementation:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k documentation_recovery_with_terminal_state_wording -v --tb=short`

RED result:

- Exit `1`.
- Selected test: `test_claim_next_task_claims_documentation_recovery_with_terminal_state_wording_before_validation_deadlock`.
- Failure: `assert result is not None` with `result` equal to `None`.
- Test setup included a blocking current G1 document row and one unresolved normal `ALR-062` quality-review validation task.

## Repair

`hermes_cli/factory_pg.py` now normalizes dispatch phase keys with whitespace and hyphen folding, so phase strings such as `documentation recovery`, `documentation-recovery`, and `documentation_recovery` are treated consistently.

The docs-first repair classifier now recognizes documentation-family repair phases (`documentation_*`, `docs_*`) in addition to exact `documentation`, `docs`, `planning`, and `g0`/`g1` phases. This lets documentation/G1/reconciliation recovery work run ahead of validation rows that themselves wait for the docs path, without broadening product/runtime dispatch.

Preserved fail-closed behavior:

- unresolved normal validation tasks remain visible through `_validation_task_readiness_findings()`;
- product/ALR implementation remains docs-first gated while required G1 docs are red;
- runtime/direct-integration/deploy/messaging/direct-SQL/trading/risk/paper-live/base-branch integration scopes remain sensitive;
- validation/review tasks that are not docs-first repair work remain blocked by docs-first preflight when docs are not ready;
- this increment does not mutate task status, close stale rows, or run live Factory tick/resolve-state.

## Verification evidence

Initial environment check:

- Command: `scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k documentation_recovery_with_terminal_state_wording -v --tb=short`
- Result: exit `1` because this isolated worktree has no local `.venv`/`venv` with pytest; no repo/environment mutation was made. Subsequent test commands used the existing main checkout venv through `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3`.

Focused RED:

- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k documentation_recovery_with_terminal_state_wording -v --tb=short`
- Result: `1 failed, 135 deselected`; failure was `assert None is not None`, reproducing `claimed=null` for the documentation recovery while current G1 docs were not ready and unresolved validation work existed.

Focused GREEN after implementation:

- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k documentation_recovery_with_terminal_state_wording -v --tb=short`
- Result: `1 tests passed, 0 failed`.

Related Factory control-plane GREEN:

- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_orchestrator_tick.py -v --tb=short`
- Result: `3 files, 316 tests passed, 0 failed`.

Final focused local validation after evidence docs were updated:

- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_orchestrator_tick.py -v --tb=short`
- Result: `3 files, 316 tests passed, 0 failed`; runner wall `10.8s`.

Whitespace validation:

- Command: `git diff --check`
- Result: exit `0`, no output.

Sanctioned Factory status readback:

- Command: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status --json > /tmp/r2df-r36-status-after.json`
- Summary command: `jq -r '.projects[] | select(.project_id=="zeus-alpha-research-ledger-core") | {project_id, status, reconciliation_anomalies, reconciliation_projection_source, g1_required_total: ([.document_status[]? | select(.category=="g1_required")] | length), g1_required_blocking: ([.document_status[]? | select(.category=="g1_required" and .blocking==true)] | length), readiness_sources: ([.document_status[]? | select(.category=="g1_required") | .readiness_source] | unique), base_commits: ([.document_status[]? | select(.category=="g1_required") | .base_commit] | unique), primary_checkout_accepted: ([.document_status[]? | select(.category=="g1_required") | .primary_checkout_accepted] | unique)}' /tmp/r2df-r36-status-after.json`
- Result: project `zeus-alpha-research-ledger-core` status `active`, `g1_required_total=14`, `g1_required_blocking=0`, `readiness_sources=["configured_base_ref"]`, `base_commits=["17cfaf1f2fa01378df331b74471bf638289aa811"]`, `primary_checkout_accepted=[false]`. Top-level status reported `factory_status_delegated=false`.

Pending PR/review handoff after local validation:

- commit, normal push, non-draft Zeus-signed `agent:zeus` PR
- independent exact-SHA review by a distinct reviewer

## Delivery state

This candidate is implemented locally and remains `reviewed: pending_independent_exact_sha_quality_review` until a distinct reviewer verifies the final pushed PR head. The final commit SHA cannot be embedded in this commit; it must be recorded in the PR body, Factory gate notes, and final worker response after commit/push.

No merge, deploy, direct SQL, primary checkout mutation, credential change, external runtime, messaging, product dispatch, trading/risk/paper-live action, or self-approval is authorized by this artifact.

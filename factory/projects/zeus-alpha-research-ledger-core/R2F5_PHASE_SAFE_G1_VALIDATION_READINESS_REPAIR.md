---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2f5-phase-safe-g1-validation-readiness-
run_id: run-1788438975-6071f986
phase: g1_recovery
status: implemented_pending_pr_and_independent_exact_sha_review
validated: yes
reviewed: pending_independent_exact_sha_quality_review
owner: codex-builder
reviewer: quality-reviewer
base_ref: origin/main
base_sha: a36cc880dd061d7f6a864937e0fe3ece44024191
branch: factory/zeus-alpha-research-ledger-core/inc-124-r2f5-phase-safe-g1-validation-re
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-124-r2f5-phase-safe-g1-validation-re
created_at: 2026-09-03T08:45:12-04:00
---

# R2f5 — phase-safe G1 validation-readiness predicate repair

## Scope and boundary

R2f5 is a bounded same-project Factory scheduler/control-plane repair. It changes only:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_control_plane_refactor.py`
- project-local Factory evidence under `factory/projects/zeus-alpha-research-ledger-core/`

No Alpha Ledger product/runtime implementation, provider/model/auth config, database migration, tool registration, scheduler activation, deployment, credential access/change, messaging connector, external runtime, primary-checkout mutation, direct SQL, task-status mutation, reviewed-frontmatter mutation, merge, force-push, stale branch/PR mutation, broker/trading/risk, or paper/live action is authorized or performed by this increment.

## Canonical inputs consulted

Required Factory/G1 inputs read from the assigned worktree before implementation:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DL_G1_DOCUMENTATION_DISPATCH_VALIDATOR_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2D6_REPAIR_RECURRENT_G1_RECOVERY_SELF_DENIAL.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R47_ISOLATED_R44_SCHEDULER_FIX_PR_RECOVERY.md`

Agent Core Postgres `factory.*` remains the operational source of truth; this artifact is project-local evidence, not a DB substitute.

## Current source and Agent Core Factory readback

Assigned worktree identity before code edits and evidence update:

- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-124-r2f5-phase-safe-g1-validation-re`
- Branch: `factory/zeus-alpha-research-ledger-core/inc-124-r2f5-phase-safe-g1-validation-re`
- Remote: `https://github.com/SiteOneTech/hermes-agent-original.git`
- `git rev-parse HEAD`: `a36cc880dd061d7f6a864937e0fe3ece44024191`
- `git rev-parse origin/main`: `a36cc880dd061d7f6a864937e0fe3ece44024191`
- `git merge-base HEAD origin/main`: `a36cc880dd061d7f6a864937e0fe3ece44024191`
- `git rev-list --left-right --count HEAD...origin/main`: `0 0`

Allowed Factory status commands from the assigned worktree:

- Before repair: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2f5-status-before.json`
- After repair: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2f5-status-after-code.json`

Post-code status readback summary from `/tmp/r2f5-status-after-code.json`:

- File size: `5011130` bytes; command exit `0`.
- `db_backend=agent_core_postgres`, `database=zeus_agent`.
- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-124-r2f5-phase-safe-g1-validation-re`.
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-124-r2f5-phase-safe-g1-validation-re`.
- `factory_status_delegated=false`.
- Project `zeus-alpha-research-ledger-core` is `active`.
- Active project metadata reports `reconciliation_anomalies=[]` and `reconciliation_projection_source=current_document_status`.
- G1 required document rows: `14`; blocking G1 rows: `0`.
- Required rows read from `readiness_source=configured_base_ref`, `base_commit=a36cc880dd061d7f6a864937e0fe3ece44024191`.
- Stale primary checkout is rejected for G1 rows with `primary_checkout_rejected_reason=primary_checkout_not_configured_base`.
- R2f4 row readback: `task_id=zeus-alpha-research-ledger-core-r2f4-repair-terminal-run-reconciliation-`, `status=todo`, `phase=g1_recovery`, `owner=codex-builder`, branch `factory/zeus-alpha-research-ledger-core/inc-123-r2f4-repair-terminal-run-reconci`.
- R2f5 row readback: `task_id=zeus-alpha-research-ledger-core-r2f5-phase-safe-g1-validation-readiness-`, `status=running`, `phase=g1_recovery`, `owner=codex-builder`, branch `factory/zeus-alpha-research-ledger-core/inc-124-r2f5-phase-safe-g1-validation-re`.

Resolve-state/reconciler and tick evidence were read back only through the sanctioned `factory status` payload, because this run's DB boundary allows `factory status` and `factory gate record` only; this worker did not run a live `factory project tick` or `factory project resolve-state` command.

- Reconciler/status readback event `264844`: `project_reconciled`, active runs `1`, pending gates `0`, no tasks created/cancelled by this status readback.
- Prior canonical tick/preflight readback event `264807`: selected R2f4 (`phase=g1_recovery`) and denied it with blocker `unresolved_validation_tasks` plus historical validation rows.
- Current R2f5 claim readback event `264816`: R2f5 claimed by `codex-builder` with run `run-1788438975-6071f986`.
- Run readback: `run-1788438975-6071f986` is `running` for R2f5; historical `run-1788436008-85b46985` is now `succeeded` for R2f3 and no longer the active orphan condition.

## Defect reproduced

The validation-readiness path still let prose fragments override structured recovery phase. A same-project `phase=g1_recovery` R2f4-like candidate whose text says product, ALR, QA/security, delivery, deploy, messaging, external runtime, broker, trading/risk, and paper/live candidates **must remain denied** was classified as positive product/runtime scope. The selected recovery then waited on unrelated validation rows and the dispatcher moved to validation work instead of preserving the G1/docs-recovery path.

Focused RED tests were added before production repair:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'dispatch_validation_readiness_does_not_deadlock_deploy_prerequisite or explicit_g1_recovery_phase_bypasses_validation_deadlock_with_guardrail_scope_prose' -v --tb=long`

RED result: `2 failed, 160 deselected`.

- `test_explicit_g1_recovery_phase_bypasses_validation_deadlock_with_guardrail_scope_prose` selected `demo-alr-063-security-review` instead of the R2f4-like `demo-r2f4-terminal-run-reconcile` recovery task.
- `test_dispatch_validation_readiness_does_not_deadlock_deploy_prerequisite` showed a genuine `phase=reporting`, `owner_profile=factory-reporter` closing/readiness summary did not require validation readiness.

## Repair

The GREEN change keeps recovery classification phase-safe and fail-closed:

- Explicit G1/documentation recovery still depends on structured phase signals (`phase=g1_recovery` or the existing metadata phase keys) and is rejected for validation/reporting candidates or positive product/runtime scope.
- Positive product/runtime prose detection now ignores safety/guardrail chunks that say those scopes are forbidden, fail-closed, gated, preserved, or must remain denied. This prevents a no-product/no-runtime G1 recovery from being denied merely because its description lists prohibited downstream candidates.
- Real positive product/runtime scope remains fail-closed; the scope vocabulary now includes `alpha ledger`, `external-runtime`, `broker`, `broker connector`, `qa/security`, and `qa security` so those candidates cannot hide behind recovery phase text.
- Genuine reporting/closing work is validation-readiness gated from structured owner/phase classification via `_is_reporting_dispatch_task()`, not only final-report prose fragments.

## Verification evidence

Commands run from the assigned worktree:

1. RED, before production repair:
   `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'dispatch_validation_readiness_does_not_deadlock_deploy_prerequisite or explicit_g1_recovery_phase_bypasses_validation_deadlock_with_guardrail_scope_prose' -v --tb=long`
   - Result: `2 failed, 160 deselected`.

2. Focused GREEN after repair:
   `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'dispatch_validation_readiness_does_not_deadlock_deploy_prerequisite or explicit_g1_recovery_phase_bypasses_validation_deadlock_with_guardrail_scope_prose or docs_red_preflight_keeps_product_alr_qa_security_runtime_reporting_external_fail_closed' -v --tb=long`
   - Result: `3 tests passed, 0 failed`.

3. Full focused control-plane file:
   `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -v`
   - Result: `162 tests passed, 0 failed`.

4. Related Factory increment integration file:
   `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -v`
   - Result: `147 tests passed, 0 failed`.

5. Whitespace check:
   `git diff --check`
   - Result: exit `0`, no output.

6. Canonical Factory status readback:
   `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2f5-status-after-code.json`
   - Result: exit `0`; Agent Core Postgres payload summarized above.

## Delivery state

This candidate is implemented and locally validated for PR-first handoff. Commit, push, PR URL, Factory gate id, and exact pushed head SHA are recorded after the containing commit is created and pushed, because a committed file cannot reliably name the immutable SHA of the commit that contains itself. Independent exact-SHA review by a distinct reviewer remains pending. This artifact does not self-approve, merge, deploy, mutate Factory task status, mutate the primary checkout, force-push, or authorize ALR-020/product/runtime dispatch.

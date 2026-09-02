# R2ee — repair stale red-G1 recovery selection after completed review

## Scope

This evidence is project-local for `zeus-alpha-research-ledger-core` and records only the bounded Factory control-plane repair requested for R2ee. It does not change Alpha Ledger product code, runtime dispatch, credentials, deploy targets, messaging, trading/risk behavior, paper/live activation, or the primary checkout.

Assigned branch/worktree:

- Branch: `factory/zeus-alpha-research-ledger-core/inc-120-r2ee-repair-stale-red-g1-recover`
- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-120-r2ee-repair-stale-red-g1-recover`
- Base at start of repair: `origin/main` = `d8194b268807ef2bb701b6d3f4302967a9e5e5be`; `HEAD` = same; merge-base = same; ahead/behind = `0 0`.
- Candidate SHA is recorded after commit/gate because a commit cannot contain its own final SHA. The pre-commit code/evidence worktree readback is bound to the branch and base above; final `git rev-parse HEAD` and Factory gate notes are the exact candidate readback for independent review.

Documentation used before implementation:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`

## Root cause

The stale red-G1 loop had two structured-control-plane gaps after a G1 reconciliation/review path completed or was cancelled:

1. `cancel_resolved_reconciliation_tasks()` could cancel a G1 recovery/review task using title/result-summary prose that merely mentioned a resolved reconciliation anomaly. That text-only route could turn a completed/review-ready recovery into a cancelled row even when the task did not carry explicit reconciliation metadata.
2. `ensure_reconciliation_tasks()` treated any open task row with `metadata.reconciliation_anomaly=<code>` as covering that anomaly. Stale blocked legacy rows with this metadata but without `factory_reconciliation_task=true` therefore prevented the canonical `*-reconcile-unvalidated-required-docs` task from being reopened. The following tick could then select a normal ready review/product-adjacent row, deny it by docs-first preflight, and return `claimed=null` while G1 remained red.

Both gaps used stale prose or loose legacy metadata as scheduling state. R2ee tightens the control-plane contract to use explicit structured reconciliation scope for selection/maintenance of reconciliation tasks.

## Repair

Implementation in `hermes_cli/factory_pg.py` is intentionally narrow:

- `ensure_reconciliation_tasks()` now skips creating/reopening a reconciliation task only when an open task has structured canonical reconciliation coverage: `metadata.factory_reconciliation_task is True` and matching `metadata.reconciliation_anomaly`.
- `cancel_resolved_reconciliation_tasks()` now cancels resolved reconciliation rows only when the anomaly was read from structured reconciliation metadata, not title/status/result-summary prose.

This lets the reconciler reopen a cancelled canonical same-project documentation-reconciliation task for active `unvalidated_required_docs`, making it eligible for the next scheduler tick before normal review/product candidates. Product, ALR, QA/security, delivery/reporting, deployment, external runtime, messaging, trading/risk, paper/live, direct-SQL, and primary-checkout scopes remain fail-closed through the existing dispatch preflight and focused regression suite.

## RED/GREEN evidence

Focused RED tests added in `tests/hermes_cli/test_factory_increment_integration.py`:

- `test_cancel_resolved_reconciliation_ignores_text_only_g1_review_recovery`
- `test_reconcile_reopens_cancelled_structured_g1_reconciliation_despite_stale_blocked_metadata`

The first test reproduces the completed/review-ready R2ed-style row that mentioned `unvalidated_required_docs` in prose but had no structured reconciliation metadata. Before the repair it was cancelled as a resolved reconciliation task. After the repair it is preserved.

The second test reproduces a cancelled canonical reconciliation task plus a stale blocked legacy task carrying loose `metadata.reconciliation_anomaly=unvalidated_required_docs`, no active runs, a red-G1 finding, and a normal ready R2cy-style review row. Before the repair the stale blocked metadata caused `ensure_reconciliation_tasks()` to skip reopening the canonical reconciliation task. After the repair it reopens `demo-reconcile-unvalidated-required-docs` and records `reconciliation_task_ensured` so the next tick can select documentation-reconciliation work instead of returning `claimed=null` from a normal docs-first denial.

Commands executed from the assigned worktree:

- RED command before implementation:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k "text_only_g1_review_recovery or cancelled_structured_g1_reconciliation" -v --tb=short`
  Result: exit 1, focused tests failed before the repair.

- Focused GREEN after implementation:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k "text_only_g1_review_recovery or cancelled_structured_g1_reconciliation" -v --tb=short`
  Result: exit 0.

- Full increment integration file:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -v --tb=short`
  Result: exit 0.

- Related Factory control-plane suite:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 HERMES_TEST_WORKERS=1 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_control_plane_refactor.py -v --tb=short`
  Result: 310 tests passed, 0 failed.

- Diff hygiene:
  `git diff --check`
  Result: exit 0.

## Canonical Agent Core Factory readback

Canonical status was read via the approved Factory CLI only:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2ee-status-after-code.json`

Readback summary from `/tmp/r2ee-status-after-code.json`:

- `db_backend`: `agent_core_postgres`
- `factory_status_source_root`: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-120-r2ee-repair-stale-red-g1-recover`
- project `zeus-alpha-research-ledger-core`: `status=active`, `autonomous_enabled=true`
- current R2ee task: `status=running`, `phase=g1_recovery`, active run count `1`
- current active project metadata after source-root status readback: `reconciliation_anomalies=[]`
- forced-tick/readback history from Agent Core events:
  - event `261391`: `review_claimed`, task `zeus-alpha-research-ledger-core-r2ed-route-red-g1-independent-review-rec`, run `run-1788371938-862e4548`, worker `quality-reviewer`
  - event `261401`: `dispatch_preflight_denied`, task `zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re`, blockers `["missing_or_unindexed_docs"]`, runtime contract `docs_first_factory_product_execution_dispatch`
  - event `261410`: `task_claimed`, task `zeus-alpha-research-ledger-core-r2ee-repair-stale-red-g1-recovery-select`, run `run-1788372587-e8f8aa2b`, worker `codex-builder`
  - event `261411`: `project_reconciled`, active run count `1`, historical anomalies `["unvalidated_required_docs"]`, task counts `blocked=14`, `ready=3`, `todo=12`, `running=1`

No live `factory project tick`, `factory worker dispatch`, `factory project resolve-state`, direct SQL, product execution, deploy, external runtime, messaging, primary mutation, merge, or activation was executed. Because live dispatch was explicitly out of scope and DB writes were limited to allowed gate recording, the claim/spawn proof is hermetic tests plus canonical Agent Core status/event readback.

## Delivery boundary

Delivery is PR-first only. The branch must be pushed and independently reviewed at the exact final SHA before any merge, runtime dispatch, deploy, credential change, messaging, external runtime, product/ALR execution, QA/security closure, trading/risk, paper/live activation, or delivery approval.

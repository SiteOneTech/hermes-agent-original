---
project_id: zeus-alpha-research-ledger-core
phase: g1_recovery
status: implemented_pending_pr_review
validated: yes
reviewed: pending
owner: codex-builder
run_id: run-1788316490-e0179bbb
task_id: zeus-alpha-research-ledger-core-r2d5-repair-post-r2d4-g1-recovery-self-d
branch: factory/zeus-alpha-research-ledger-core/inc-105-r2d5-repair-post-r2d4-g1-recover
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-105-r2d5-repair-post-r2d4-g1-recover
base_commit: 63a866d57bda6a1258de6c93d0f244316f298828
---

# R2d5 — repair post-R2d4 G1 recovery self-denial

## Scope

This increment is a bounded same-project Factory control-plane repair. It changes only Factory scheduler/preflight classification, focused hermetic tests, and project-local evidence for `zeus-alpha-research-ledger-core`.

It does not dispatch Alpha Ledger product work, mutate primary checkout state, write direct SQL, merge, deploy, change credentials, touch external runtimes, enable messaging connectors, or perform trading/risk/paper/live activation.

## Reproduced condition

The assigned worktree started on the assigned branch at exact base/HEAD/origin-main/merge-base `63a866d57bda6a1258de6c93d0f244316f298828`.

Source-backed status readbacks used the sanctioned Factory DB surface only:

- Stale primary status reproduction: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json` from `/home/jean/Projects/hermes-agent-original` saved `/tmp/r2d5-status-primary-stale.json`; parsed readback: `db_backend=agent_core_postgres`, project `active`, autonomous `true`, `reconciliation_anomalies=["unvalidated_required_docs"]`, `14` G1 required docs, `10` blocking, `10` `reviewed=false`.
- Assigned-worktree current-source status: same sanctioned command from the assigned worktree saved `/tmp/r2d5-status-final.json`; parsed readback: `db_backend=agent_core_postgres`, project `active`, autonomous `true`, `reconciliation_anomalies=[]`, `14` G1 required docs, `0` blocking, `0` `reviewed=false`, current run `run-1788316490-e0179bbb` running on this R2d5 task.

No live `factory project tick` was executed by this worker because the run's DB-write boundary allows only `factory status` and `factory gate record`, and the task explicitly forbids opening another increment. The tick/claim path is therefore exercised hermetically through `factory_pg.force_tick` tests.

## RED evidence

Focused RED test added first:

- `tests/hermes_cli/test_factory_increment_integration.py::test_force_tick_claims_phase_explicit_g1_documentation_recovery_despite_unresolved_validation_rows`

The fixture models the post-R2d4 failure class: active/autonomous project, zero active runs, ten blocking G1 document rows solely missing `reviewed`, stale `reconciliation_anomalies=["unvalidated_required_docs"]`, blocked/superseded/current validation rows, a product ALR candidate, and a no-dependency same-project `phase=documentation` G1 evidence restore candidate with explicit no-product/no-runtime guardrails.

Before production code changes, the focused command failed as expected:

- `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k test_force_tick_claims_phase_explicit_g1_documentation_recovery_despite_unresolved_validation_rows -v --tb=short` → exit `1`.

A companion guardrail test was also added before the repair:

- `tests/hermes_cli/test_factory_increment_integration.py::test_g1_recovery_activation_work_remains_validation_and_docs_first_gated`

Its RED failure covered activation work that previously was not part of the product/runtime scope terms.

## GREEN repair

The repair keeps the bypass explicit and narrow:

- `_candidate_requires_validation_readiness_before_dispatch` now treats phase-explicit G0/G1/documentation/docs/planning recovery as validation-readiness-exempt only when the task is not reporting and has no positive product/runtime scope.
- `_is_docs_first_gated_dispatch_task` evaluates validation tasks before phase-based recovery allowance, so QA/security/review work cannot hide behind a G1 phase.
- Docs-first preflight now allows phase-explicit non-product G1/documentation/planning recovery before raw negative guardrail words such as `no deploy`, `no direct SQL`, or `no activation` are misread as positive product/runtime scope.
- Activation is added to positive product/runtime scope detection and docs-first gating, keeping activation work fail-closed while G1 is red.

## Verification

Commands executed from the assigned worktree unless stated otherwise:

1. RED focused run before implementation:
   - `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k test_force_tick_claims_phase_explicit_g1_documentation_recovery_despite_unresolved_validation_rows -v --tb=short` → exit `1`.
2. RED focused run including activation guard before implementation:
   - `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'test_force_tick_claims_phase_explicit_g1_documentation_recovery_despite_unresolved_validation_rows or test_g1_recovery_activation_work_remains_validation_and_docs_first_gated' -v --tb=short` → exit `1`.
3. GREEN focused run after implementation:
   - same two-test command → exit `0`.
4. Related hermetic Factory control-plane tests:
   - `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_orchestrator_tick.py -v --tb=short` → exit `0`.
5. Diff hygiene:
   - `git diff --check` → exit `0`.
6. Sanctioned Factory status readback:
   - `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2d5-status-final.json` → exit `0`, `4831085` bytes.

## PR-first handoff

This artifact remains `reviewed: pending` until a distinct reviewer performs independent exact-SHA review of the final pushed PR head. Required handoff evidence after push:

- non-draft GitHub PR against `main` from `factory/zeus-alpha-research-ledger-core/inc-105-r2d5-repair-post-r2d4-g1-recover`;
- `agent:zeus` label;
- Zeus-signed commit and PR body;
- final candidate SHA recorded in PR/gate notes;
- independent exact-SHA quality review before closure or any downstream reliance.

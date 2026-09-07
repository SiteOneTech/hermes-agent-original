---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-g1-red-structured-recovery-candidate-ord
phase: g1_recovery
status: candidate
validated: yes
reviewed: pending
owner: codex-builder
reviewer: quality-reviewer
run_id: run-1788791249-bcb83e47
---

# G1 red structured recovery candidate ordering and dispatch repair

## Scope

Bounded Factory scheduler/control-plane repair only. This candidate changes Factory dispatch classification and hermetic tests. It does not change Zeus Alpha Research Ledger product/runtime code and does not authorize merge, deployment, direct SQL, credential changes, primary-checkout mutation, messaging, external runtime, Vonash, Magnus, VAOS, RAG/KB, broker, trading/risk, paper activation, or live activation.

## Canonical inputs consulted

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md` — controlling G1/readiness index and recent docs-first recovery history.
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md` — Zeus-only Agent Core scope and explicit product/runtime exclusions.
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md` — `zeus_only`, `add_functionality`, assigned branch/worktree and PR-first policy.
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md` — no runtime/no-egress/no-product-dispatch contract.
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`, `TASK_GRAPH.md`, `QA_GATES.md`, `SECURITY_GATES.md` — task/gate/testing and security boundaries.
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R43_G1_RECOVERY_SELECTION_STARVATION_REPAIR.md` — immediate predecessor evidence for docs-first recovery selection starvation.

## Source and Agent Core readback evidence

- Assigned branch: `factory/zeus-alpha-research-ledger-core/inc-104-g1-red-structured-recovery-candi`.
- Assigned worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-104-g1-red-structured-recovery-candi`.
- Base/pre-edit source SHA: `d0cdd5c2a7e3c5a18107d4b0e965477b5a183f1c` (`origin/main` at claim time in this worktree).
- Candidate code/test commit SHA: `95673c02acd88f1341153f2305afa54ca889de13` (first Zeus-signed commit containing the production repair, hermetic RED/GREEN test, and project-local evidence artifact; a later evidence-only commit may become the final PR head because a commit cannot contain its own final SHA).
- Canonical status command used: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json` from the assigned worktree.
- Status snapshots: `/tmp/inc104-status-before.json` and `/tmp/inc104-status-after-code.json`; summaries: `/tmp/inc104-status-before.summary.txt` and `/tmp/inc104-status-after-code.summary.txt`.
- Status readback summary: `db_backend=agent_core_postgres`, `database=zeus_agent`, `factory_cli_source_root` and `factory_status_source_root` both equal the assigned worktree, `factory_status_delegated=False`, project `status=active`, `autonomous_enabled=True`, active run `run-1788791249-bcb83e47` on task `zeus-alpha-research-ledger-core-g1-red-structured-recovery-candidate-ord`, and active task count `ACTIVE_RUNS=1` while this worker is running.
- Document-status projection in the assigned worktree currently reports `DOC_ROWS=22`, `BLOCKING=0`, `DOC_READINESS_SOURCES=configured_base_ref`, and active project metadata `reconciliation_anomalies=[]`; this is current configured-base evidence only.
- Resolve-state/reconcile readback preserved in Agent Core event history: repeated `project_reconciled` events before the claim reported `active_runs=0` and `anomalies=['unvalidated_required_docs']`, including `2026-09-07T14:25:48.05655+00:00`, `2026-09-07T14:27:20.327219+00:00`, and `2026-09-07T14:27:22.807617+00:00`.
- Forced-tick readback preserved in Agent Core event history: `2026-09-07T14:25:45.387332+00:00` `factory-force-tick` denied normal quality-review task `zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re` with `blockers=['missing_or_unindexed_docs']`; then `2026-09-07T14:27:29.369148+00:00` `factory-force-tick` claimed exactly this structured G1 recovery task with `run_id=run-1788791249-bcb83e47` and `worker_profile=codex-builder`.
- This worker did not execute a live `tick`, `resolve-state`, direct SQL, deployment, credential change, primary-checkout mutation, or external dispatch. The readbacks above come from the sanctioned `factory status` Agent Core Postgres event stream; state-changing Factory DB interaction is limited to `factory gate record` after PR-first evidence.

## RED reproduction

Command run from the assigned worktree after adding only the hermetic test and temporarily reverting the production change:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k test_force_tick_routes_structured_documentation_phase_before_review_preflight -v --tb=short`

Observed RED log: `/tmp/inc104-test-red.log`.

- Result: 1 failed / 0 passed selected.
- Failure: `assert factory_pg._payload_docs_first_repair_should_preempt_review(payload, project_id="demo") is True` returned `False`.
- The fixture reproduced an active/autonomous project with zero active runs, structured `metadata.reconciliation_anomalies=['unvalidated_required_docs']`, a ready normal quality-review task, a ready product implementation task, and an eligible same-project `phase='documentation'` recovery candidate whose prose contained final-gate wording. Pre-repair code would preflight review/product before the structured documentation candidate because only text/metadata-explicit recovery markers were treated as docs-first repair candidates.

## GREEN repair

Changed behavior:

- Added `_is_structured_g1_or_documentation_recovery_task()` in `hermes_cli/factory_pg.py` to classify G0/G1/documentation/planning recovery candidates from structured task phase/metadata only, after fail-closed validation/reporting and positive product/runtime/direct-integration scope checks.
- `_is_docs_first_repair_dispatch_task()` now treats those structured G1/docs candidates as docs-first repair. That makes `_payload_docs_first_repair_should_preempt_review()` preempt normal quality/product candidates while G1/docs is red and lets validation-readiness preflight bypass final/gate wording only for safe structured recovery scope.
- Product/runtime/ALR/QA/security/delivery/reporting candidates remain gated by the existing positive scope, validation task, reporting task, docs-first product execution, and security/delivery preflight blockers.

## Verification

Commands run from the assigned worktree:

1. RED: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k test_force_tick_routes_structured_documentation_phase_before_review_preflight -v --tb=short` with production change temporarily reverted -> failed as expected, 1 failed / 0 passed selected (`/tmp/inc104-test-red.log`).
2. GREEN targeted: same command after repair -> passed, 1 passed / 0 failed (`/tmp/inc104-test-target-green-after-red.log`).
3. Focused Factory control-plane suite: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_cron_control_plane.py tests/hermes_cli/test_factory_successor_control.py -v --tb=short` -> passed, 198 passed / 0 failed (`/tmp/inc104-test-focused-green-final.log`).
4. Compile check: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m py_compile hermes_cli/factory_pg.py tests/hermes_cli/test_factory_increment_integration.py` -> exit 0.
5. Whitespace check: `git diff --check` -> exit 0.

## PR-first handoff

This artifact is candidate evidence only. It records the exact code/test candidate SHA above; the final pushed PR-head SHA, PR URL, and Factory gate record are recorded after the evidence-only follow-up commit/push because a commit cannot contain its own final SHA. Independent exact-SHA quality review by a separate reviewer remains required before merge or downstream dispatch relies on this repair.

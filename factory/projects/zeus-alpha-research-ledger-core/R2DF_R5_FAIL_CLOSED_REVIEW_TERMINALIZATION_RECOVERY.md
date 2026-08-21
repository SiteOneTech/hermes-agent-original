---
document_type: fail_closed_review_terminalization_recovery
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2df-r5-fail-closed-recovery-for-rate-li
run_id: run-1787253261-a34219b4
phase: documentation
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending_independent_exact_sha_quality_review
owner: codex-builder
base_ref: origin/main
base_sha: 71a68478c3be0e28e65b730406c080b42a6b2115
branch: factory/zeus-alpha-research-ledger-core/inc-000-r2df-r5-fail-closed-recovery-for
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-000-r2df-r5-fail-closed-recovery-for
created_at: 2026-08-20
---

# R2df-R5 — fail-closed recovery for rate-limited review terminalization

## Scope and boundary

R2df-R5 is a bounded Factory control-plane repair for the review terminalization path. It addresses the exact failure where R2df-R4 review run `run-1787252480-9e4e89c0` ended with MiniMax HTTP 429 rate-limit failures, wrapper `exit_code=0`, no reviewer analysis, and was still recorded as `succeeded` with the task `done`.

Changed runtime scope is limited to `hermes_cli/factory_pg.py` review-run terminalization/recovery predicates, focused regression coverage in `tests/hermes_cli/test_factory_increment_integration.py`, and project-local provenance updates under this directory.

No Alpha Ledger product/runtime code, provider/model/auth configuration, migrations, tools, schedulers, deployment, credentials, messaging, external runtime, primary checkout mutation, direct SQL, task-status mutation, base-branch merge, Vonash, Magnus, VAOS, RAG/KB, broker, trading, risk, paper/live, or external-system action is authorized or performed by this increment.

## Canonical documents read before implementation

The required entrypoint and G1/control docs read for this phase were:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DI_DOCS_FIRST_FAIL_CLOSED_REVIEW_TERMINALIZATION_AND_DISPATCH_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DL_G1_DOCUMENTATION_DISPATCH_VALIDATOR_RECOVERY.md`

Agent Core Postgres `factory.*` remains the operational source of truth. Project-local Markdown records the reasoning/evidence and does not replace canonical DB state.

## Current base and worktree identity

Captured before edits/final evidence:

- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-000-r2df-r5-fail-closed-recovery-for`
- Branch: `factory/zeus-alpha-research-ledger-core/inc-000-r2df-r5-fail-closed-recovery-for`
- Remote: `https://github.com/SiteOneTech/hermes-agent-original.git`
- `git rev-parse HEAD`: `71a68478c3be0e28e65b730406c080b42a6b2115`
- `git rev-parse origin/main`: `71a68478c3be0e28e65b730406c080b42a6b2115`
- `git merge-base HEAD origin/main`: `71a68478c3be0e28e65b730406c080b42a6b2115`

## Canonical Factory status readback

Allowed status command from the assigned worktree:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r5-status-after.json`

Readback evidence from `/tmp/r2df-r5-status-after.json`:

- Output size: `4,118,389` bytes.
- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-000-r2df-r5-fail-closed-recovery-for`.
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-000-r2df-r5-fail-closed-recovery-for`.
- `factory_status_delegated=false`.
- `run-1787252480-9e4e89c0` remains visible as a review run with `exit_code=0`, `status=succeeded`, task `zeus-alpha-research-ledger-core-r2df-r4-reconciliation-qa-guardian-exact`, and output tail containing repeated `RateLimitError [HTTP 429]`, MiniMax provider details, token-plan usage-limit errors, and fallback retry waits.
- Gate `1008` is visible as `gate_type=test`, reviewer/QA evidence for task `zeus-alpha-research-ledger-core-r2df-r4-reconciliation-qa-guardian-exact`; its own notes explicitly state QA Guardian/test evidence and that independent exact-SHA quality review remains required before integration.
- Current R2df-R5 task `zeus-alpha-research-ledger-core-r2df-r5-fail-closed-recovery-for-rate-li` is the active assigned worker task in this worktree.

The run did not execute `factory project resolve-state` because this run's hard DB-write allowlist permits only `factory status` and `factory gate record`; resolve-state behavior is covered with controlled Factory control-plane tests below.

## Defect reproduced

R2df-R4 had two independent failure vectors:

1. A review log could contain an actual MiniMax/HTTP 429 provider failure but still present a final `STATE: DONE` marker and wrapper `exit_code=0`.
2. A task-bound QA/test gate (`gate_type=test`, gate `1008`, reviewer `qa-verifier`) could be confused with the independent quality-review evidence required to terminalize a review run.

The prior predicates already handled some 429 shapes (`RateLimitError`, `provider response`, `API call failed`, zero-tool transcript), but did not cover a generic MiniMax/HTTP 429 rate-limit line such as `MiniMax HTTP 429 rate-limit failure after three provider retries`. The same review-gate filter also included `test`, `delivery`, and `critical_readiness` gate types, so QA/test evidence could satisfy review-run terminalization in cases where the runtime-failure classifier missed the provider failure line.

## Repair

`hermes_cli/factory_pg.py` now:

- treats `MiniMax`, `rate-limit`, `rate limit`, and provider retry language as 429 runtime-failure context when an HTTP 429 / Too Many Requests pattern is present;
- keeps documentary review prose safe: lines that explicitly document prior/checked/regression 429 conditions still do not fail a clean review unless actual runtime-failure markers are present;
- narrows task-bound review terminalization gates to independent review gates only: `architecture`, `quality`, `security`, and `spec`;
- keeps QA/test, delivery, and critical-readiness gates legitimate Factory evidence, but distinct from independent review proof and insufficient by themselves to close a positive review run;
- preserves fail-closed recovery: false terminalized review runs are reclassified failed and the task reopens to `review_ready` with `requires_task_bound_passed_review_gate=true`.

PR #106 exact head `91a58b6714b2cf72400746e83291d2f03cfe339e` remains pending independent review. This increment does not merge or approve it.

## TDD evidence

RED command (expected failure before implementation):

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'qa_test_gate or minimax_429' -v --tb=short`

RED result: `3 failed, 123 deselected`. Failures proved that QA/test gate evidence still allowed integration, MiniMax HTTP 429 rate-limit text was not classified as runtime failure even with a quality gate, and canonical reconciliation did not recover a same-class false terminal review.

GREEN targeted command after implementation:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'qa_test_gate or minimax_429' -v --tb=short`

GREEN targeted result: `3 tests passed, 0 failed`.

Broader Factory control-plane validation command:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_control_plane_refactor.py -v`

Broader validation result: `3 files, 306 tests passed, 0 failed` (`test_factory_increment_integration.py`: 126 passed; `test_factory_orchestrator_tick.py`: 23 passed; `test_factory_control_plane_refactor.py`: 157 passed).

Diff hygiene:

`git diff --check` exited `0`.

## Acceptance mapping

- HTTP 429/provider failure plus wrapper `exit_code=0` cannot terminalize successfully: covered by `test_mark_run_finished_review_minimax_429_requeues_even_with_quality_gate`.
- QA/test gate `1008` remains distinct from independent quality-review evidence: covered by `test_mark_run_finished_review_success_does_not_accept_qa_test_gate` and the narrowed review-gate filter.
- Canonical Factory resolution fails closed and requeues/reopens instead of leaving a false `succeeded/done` state: covered by `test_reconcile_project_recovers_minimax_429_false_terminal_review` through `reconcile_project()` / `_recover_false_terminalized_review_runs()`.
- Existing legitimate reviewer prose that quotes the prior 429 regression remains acceptable only when a real task-bound independent review gate exists: preserved by existing `test_mark_run_finished_review_can_document_429_condition_with_task_gate` in the full file run.
- Scope remains Factory control-plane/tests and project-local provenance only; no base merge/deploy/direct SQL/credential/external runtime/product dispatch was performed.

## Delivery state

This candidate remains `reviewed: pending` until a Zeus-signed `agent:zeus` PR is pushed and independently reviewed by a distinct `quality-reviewer` against the exact final candidate SHA. The PR body and Factory evidence must name the immutable pushed head because a commit cannot contain its own SHA.

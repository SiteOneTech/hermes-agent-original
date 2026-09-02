---
document_type: repair_red_g1_validation_review_reconciliation_dispatch
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2dd-repair-red-g1-validation-review-rec
run_id: run-1788361226-0704eb98
phase: g1_recovery
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending_independent_exact_sha_quality_review
owner: codex-builder
base_ref: origin/main
base_sha: d8194b268807ef2bb701b6d3f4302967a9e5e5be
branch: factory/zeus-alpha-research-ledger-core/inc-117-r2dd-repair-red-g1-validation-re
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-117-r2dd-repair-red-g1-validation-re
created_at: 2026-09-02T15:16:39Z
---

# R2dd — repair red-G1 validation-review reconciliation dispatch

## Scope and boundary

R2dd is a bounded same-project Factory scheduler/control-plane repair for `zeus-alpha-research-ledger-core`. It addresses only the red-G1 validation-review reconciliation dispatch deadlock where a same-project G1/documentation-review reconciliation task is blocked behind docs-first validation readiness while a normal product quality-review candidate is denied.

Changed runtime scope is limited to `hermes_cli/factory_pg.py`, focused Factory regression coverage in `tests/hermes_cli/test_factory_increment_integration.py`, and project-local evidence/index docs in `factory/projects/zeus-alpha-research-ledger-core/`.

No Alpha Ledger product/runtime code, migrations, provider/model/auth configuration, tools, schedulers, deployment, credentials, messaging, primary checkout mutation, direct SQL, manual task-status mutation, merge, external runtime, external dispatch, Vonash/Magnus/VAOS/RAG/KB/broker/trading/risk/paper/live action, or production/sandbox propagation is authorized or performed by this increment. Sanctioned `factory status` readbacks may execute reviewed Factory reconciliation code and preserve any resulting status events as canonical evidence rather than ad-hoc DB writes.

## Canonical documents read before implementation

The required entrypoint and applicable G1/control docs read for this phase were:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`

The active Factory operational source remains Agent Core Postgres `factory.*`. These Markdown records are project-local evidence and human-readable control documentation, not a replacement for Factory DB state.

## Current base and worktree identity

Captured before the delivery commit:

- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-117-r2dd-repair-red-g1-validation-re`
- Branch: `factory/zeus-alpha-research-ledger-core/inc-117-r2dd-repair-red-g1-validation-re`
- Base ref: `origin/main`
- `git rev-parse HEAD`: `d8194b268807ef2bb701b6d3f4302967a9e5e5be`
- `git rev-parse origin/main`: `d8194b268807ef2bb701b6d3f4302967a9e5e5be`
- `git merge-base HEAD origin/main`: `d8194b268807ef2bb701b6d3f4302967a9e5e5be`

The final pushed candidate SHA is recorded after commit/push in the PR body and Factory gate evidence because a commit cannot embed its own final hash.

## Canonical Factory status/readback evidence

Allowed Agent Core Postgres readback command from the assigned worktree:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2dd-status-after-code.json`

Summarized status/readback:

- Output path: `/tmp/r2dd-status-after-code.json`
- `db_backend=agent_core_postgres`
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-117-r2dd-repair-red-g1-validation-re`
- `factory_status_delegated=false`
- `project_status=active`
- `autonomous_enabled=true`
- active metadata subset: `reconciliation_anomalies=["pending_effective_gates"]`, `reconciliation_projection_source=current_document_status`, `reconciliation_required=true`
- current configured-source G1 rows: `14`; current blocking rows from the assigned worktree readback: `0`
- active run: `run-1788361226-0704eb98` on task `zeus-alpha-research-ledger-core-r2dd-repair-red-g1-validation-review-rec`
- ready tasks: `3`; todo tasks: `12`
- ready sample includes `zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re` with phase `quality_review`, plus implementation/product candidates that must remain fail-closed.

Relevant status event readbacks:

- `event_id=260820`, actor `factory-reconciler`, type `project_reconciled`, message `Project reconciled as active`, metadata anomalies `['unvalidated_required_docs', 'pending_effective_gates']`, task counts `blocked=14`, `done=130`, `ready=3`, `running=1`, `todo=12`.
- `event_id=260792`, actor `factory-force-tick`, type `task_claimed`, task `zeus-alpha-research-ledger-core-r2dd-repair-red-g1-validation-review-rec`, run `run-1788361226-0704eb98`; this is the canonical forced-tick claim/spawn readback for the assigned R2dd task.
- `event_id=260791`, actor `factory-dispatcher`, type `dispatch_preflight_denied`, message `Product execution dispatch denied until Factory docs/index/Notion gates are ready`, with blockers including `unresolved_validation_tasks` and `zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re` still `status=ready`; this preserves the source-backed quality-review denial side of the deadlock.

No live `factory project resolve-state` or additional `factory project tick` command was run by this worker; the prompt's DB-write allowlist for this run permits only `factory status` and `factory gate record`. The deterministic RED/GREEN test below exercises `force_tick()` hermetically against fake Agent Core SQL rows, and the live status event readbacks above preserve the Factory reconciler/forced-tick state already created for this run.

## Defect reproduced

The focused RED state is a hermetic projection of the canonical 2026-09-02 red-G1/no-active-run state:

- project active/autonomous;
- zero active runs in the test harness;
- ten required G1 document rows `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=false`, `blocking=true`, `missing=['reviewed']`;
- metadata anomaly `pending_effective_gates`;
- a `review_ready` product quality-review candidate `demo-r2cy-r1-independent-exact-sha-quality-re`;
- a same-project `review_ready` R2dd review-reconciliation task whose positive eligibility signals exist only in structured metadata: `task_phase=g1_recovery`, `documentation_recovery=true`, `review_scope=g1_documentation_reconciliation`, `no_product_runtime_scope=true`; and
- product, ALR, QA, security, and delivery candidates ready/todo behind the same red docs-first gate.

The test asserts that `_task_text()` for the R2dd review-reconciliation candidate does not contain `g1`, `documentation`, `reconciliation`, or `recovery`, so the repair cannot rely on task title/status/description prose as the positive selector.

Before the production fix, the structured R2dd review-reconciliation candidate was not classified as a docs-first validation repair unless task prose contained both documentation/G1 and repair/reconciliation terms. The scheduler could therefore select/deny the quality-review candidate as product execution and leave the same-project review reconciliation path unclaimed.

## Repair

`_is_docs_first_validation_repair_task()` now accepts a validation/review task when all explicit predicates are true:

1. the candidate is a validation/review task;
2. it is not QA/security-owned or QA/security phase;
3. it is not a reporting/final-delivery task;
4. it has no positive product/runtime/ALR/external/direct-SQL/trading dispatch scope; and
5. it has explicit G1/documentation recovery phase or structured metadata via the existing `_has_explicit_g1_or_documentation_recovery_scope()` predicate.

The removed condition was the text-term requirement over title/description/status prose. This keeps eligibility phase/metadata-based and preserves the existing fail-closed product/runtime/reporting guards.

## TDD evidence

RED focused command before production repair:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k structured_g1_review_reconciliation -v --tb=short`

RED result: exit `1` after the test was hardened to require structured metadata-only positive selection; production still required docs/reconciliation/recovery prose terms and the expected R2dd review-reconciliation claim did not happen.

GREEN focused command after repair:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k structured_g1_review_reconciliation -v --tb=short > /tmp/r2dd-test-focused.log 2>&1`

GREEN focused result: `1 files, 1 tests passed, 0 failed` in `1.2s`.

Increment integration validation:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py > /tmp/r2dd-test-increment-integration.log 2>&1`

Result: `1 files, 148 tests passed, 0 failed` in `8.7s`.

Related Factory control-plane validation:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_increment_integration.py > /tmp/r2dd-test-control-and-increment.log 2>&1`

Result: `2 files, 309 tests passed, 0 failed` in `10.8s`.

Orchestrator tick regression validation:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py > /tmp/r2dd-test-orchestrator-tick.log 2>&1`

Result: `1 files, 24 tests passed, 0 failed` in `3.5s`.

Whitespace validation:

`git diff --check > /tmp/r2dd-diff-check.log 2>&1`

Result: exit `0`, empty output.

## Acceptance mapping

- RED reproduction: `test_force_tick_claims_structured_g1_review_reconciliation_before_red_g1_quality_review` models the red-G1/no-active-run deadlock, verifies ten blocking reviewed=false G1 rows, and proves the structured review-reconciliation path was bypassed before the fix.
- GREEN selection: the same test now verifies `force_tick()` claims `demo-r2dd-structured-review` with `run_type=review`, records a denial for the product quality-review candidate, and never claims product implementation.
- Explicit metadata only: the test asserts the positive selector terms are absent from task text and present only in structured metadata/phase fields.
- Fail-closed scope: the test verifies product implementation, QA, security, and delivery candidates receive `missing_or_unindexed_docs` under red G1; production guards also continue to reject positive product/runtime/reporting scope before accepting a review-reconciliation candidate.
- PR-first delivery: this artifact is `reviewed: pending_independent_exact_sha_quality_review`; it does not self-approve, merge, deploy, mutate primary, or dispatch product/runtime work.

## Delivery handoff

Required before downstream Factory control relies on this repair:

- push the assigned branch;
- open/update a non-draft GitHub PR against `main` with `agent:zeus` label and Zeus Signed-off-by commit;
- record the exact final candidate head SHA in the PR body and Factory implementation gate evidence;
- obtain independent exact-SHA quality review by a distinct reviewer;
- keep merge, deployment, direct SQL, primary checkout mutation, credentials, external runtime, messaging, product execution, trading/risk, and paper/live activation prohibited unless a later authorized gate explicitly permits them.

---
document_type: docs_first_stale_runtime_dispatch_provenance_repair
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2ea-docs-first-stale-runtime-dispatch-p
run_id: run-1787256151-07480850
phase: documentation
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending
owner: codex-builder
base_ref: origin/main
base_sha: ee5c0187f14e66a3dc83896d97aa1e8abe92e36a
branch: factory/zeus-alpha-research-ledger-core/inc-001-r2ea-docs-first-stale-runtime-di
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2ea-docs-first-stale-runtime-di
created_at: 2026-08-20T20:13:37Z
---

# R2ea — docs-first stale-runtime dispatch provenance repair

## Scope and boundary

R2ea is a bounded Factory control-plane dispatch repair. It changes only:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_increment_integration.py`
- project-local Factory evidence under `factory/projects/zeus-alpha-research-ledger-core/`

No Alpha Ledger product/runtime code, provider/model/auth config, database migration, tool registration, scheduler, deployment, credential access, messaging connector, external runtime, primary checkout mutation, task-status mutation, direct SQL, merge, Vonash, Magnus, VAOS, RAG/KB, broker, trading, risk, paper/live activation, or external-system operation is authorized or performed by this increment.

Factory DB interaction for this run stayed within the stated allowlist: sanctioned `factory status` readback only. Mutating `factory project resolve-state` / `factory project tick` live commands were not executed against Agent Core because this assignment explicitly constrained Factory DB writes to `factory status` and `factory gate record`. The canonical tick path is exercised by deterministic regression tests without mutating live Factory rows.

## G1 documents read before implementation

The required documentation entrypoint and applicable G1/project docs read for this increment were:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`

The assignment prompt's G1 snapshot named 10 `missing=reviewed` blockers, while the canonical sanctioned status readback from this assigned worktree reports zero current G1 blockers. That mismatch remains documented as stale runtime/projection context unless reproduced through the sanctioned readback.

## RED reproduction

Command:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k docs_blocked_quality_review`

Pre-fix result:

- Exit `1`.
- Focused test failed because `factory_pg.force_tick("demo")` selected `demo-quality-review` (`status=review_ready`, `phase=quality_review`) before the dependency-free documentation recovery `demo-r2ea-g1-docs-recovery` while docs-first preflight reported `docs_ready=false`.
- Assertion diff: expected `demo-r2ea-g1-docs-recovery`; actual `demo-quality-review`.

This reproduces the stale-runtime dispatch ordering/provenance defect: a quality-review task could be claimed first even though an eligible G1/documentation recovery task was todo, causing the runtime to continue reporting `missing_or_unindexed_docs` / G1 readiness problems instead of routing the repair.

## Implementation summary

The repair changes the canonical dispatch path to:

1. Make `claim_next_review()` docs-first aware. Review-ready validation work now computes the same project docs/Notion preflight used by implementation dispatch and records a fail-closed dispatch denial instead of claiming review work when current G1 readiness is not verified. Documentation/reconciliation review tasks remain eligible because the existing docs-first blocker predicate exempts documentation/G0/G1/reconciliation repair work.
2. Allow dependency-ready docs-first repair tasks to preempt parked validation review rows. `review_ready` / `qa_ready` are ignored as active blockers only for the narrow case where current docs are not ready, no Jean waiver exists, and a dependency-ready documentation/reconciliation repair candidate is runnable.
3. Preserve source provenance fail-closed behavior. Dependency integration/provenance checks still run before a candidate can dispatch, and unverified source delivery continues to produce precise `source_delivery_not_accepted` / integration blocker metadata rather than fabricated readiness.

## GREEN validation

Focused GREEN:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k docs_blocked_quality_review`

Result: 1 selected test passed, 0 failed.

Full increment-integration file:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py`

Result: 127 tests passed, 0 failed.

Related Factory control-plane subset:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k "docs_repair or dispatch_preflight or validation_readiness or source"`

Result: 10 tests passed, 0 failed.

Related Factory orchestrator tick file:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py`

Result: 23 tests passed, 0 failed.

Related Factory regression set:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_orchestrator_tick.py`

Result: 3 files, 307 tests passed, 0 failed.

## Canonical status/readback evidence

Sanctioned implementation gate evidence:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory gate record zeus-alpha-research-ledger-core implementation passed --task-id zeus-alpha-research-ledger-core-r2ea-docs-first-stale-runtime-dispatch-p --reviewer codex-builder --notes <R2ea evidence summary> --json`

Result: Factory gate `1011`, `implementation passed`, reviewer `codex-builder`. This is worker implementation evidence only, not independent quality review.

Sanctioned status command:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2ea-status-after-gate.json`

Readback summary:

- `/tmp/r2ea-status-after-gate.json` size: 4,134,408 bytes.
- `db_backend=agent_core_postgres`.
- Project status: `active`.
- Payload counts: `tasks=124`, `gates=276`, `runs=300`.
- Current required G1 rows: `g1_required=14`, `blockers=0`.
- Latest R2ea implementation gate readback: `gate_id=1011`, `status=passed`, `reviewer=codex-builder`.

Non-mutating summary command also returned:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core`

Result: `Projects: 1 | Lanes: 2 | Tasks: 124 | Gates: 275 | Runs: 300`; project `zeus-alpha-research-ledger-core` is `active`.

## Delivery and review handoff

R2ea remains PR-first. This artifact is implementation evidence only and is `reviewed: pending` until a distinct reviewer performs independent exact-SHA review of the final pushed PR head. This worker must not self-approve, merge, deploy, write direct SQL, mutate primary checkout, force-push/rewrite unrelated refs, execute external runtimes, or dispatch ALR product/trading work.

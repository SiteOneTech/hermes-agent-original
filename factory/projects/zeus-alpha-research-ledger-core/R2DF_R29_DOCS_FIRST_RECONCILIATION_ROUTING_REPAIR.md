---
document_type: docs_first_reconciliation_routing_repair
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2df-r29-docs-first-reconciliation-routi
run_id: run-1787775068-82751c51
phase: g1_recovery
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending
owner: codex-builder
base_ref: origin/main
base_sha: 3d5325165de2fd612213b330bfade8d316235215
branch: factory/zeus-alpha-research-ledger-core/inc-10-r2df-r29-docs-first-reconciliati
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-10-r2df-r29-docs-first-reconciliati
created_at: 2026-08-26T20:21:35Z
---

# R2df-R29 — docs-first reconciliation routing repair

## Scope and boundary

R2df-R29 is a bounded Factory control-plane repair for the canonical docs-first reconciliation path. It changes only:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_increment_integration.py`
- project-local Factory evidence under `factory/projects/zeus-alpha-research-ledger-core/`

No Alpha Ledger product/runtime code, provider/model/auth config, database migration, tool registration, deployment, credential access, messaging connector, external runtime, primary checkout mutation, task-status mutation, direct SQL, merge, Vonash, Magnus, VAOS, RAG/KB, broker, trading, risk, paper/live activation, or ALR product dispatch is authorized or performed by this increment.

Factory DB interaction for this run stayed within the stated allowlist: sanctioned `factory status` readback only. Mutating `factory project resolve-state` / `factory project tick` live commands were not executed against Agent Core because the assignment explicitly constrained Factory DB writes to `factory status` and `factory gate record`. The canonical tick/claim path is exercised by deterministic regression tests without mutating live Factory rows.

## G1 documents read before implementation

The required documentation entrypoint and applicable G1/project docs read for this increment were:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`

The assignment's red-doc scenario is preserved as a scheduler/reconciliation behavior regression. The sanctioned status readback from this assigned worktree after the code change reports the current configured-base document rows are clean; this artifact therefore does not mutate G1 frontmatter or reviewed markers.

## Current-base and source-root evidence

Fresh git readback after `git fetch origin main --prune`:

- `HEAD=3d5325165de2fd612213b330bfade8d316235215`.
- `origin/main=3d5325165de2fd612213b330bfade8d316235215`.
- `merge-base=3d5325165de2fd612213b330bfade8d316235215`.
- Branch: `factory/zeus-alpha-research-ledger-core/inc-10-r2df-r29-docs-first-reconciliati`.
- The assigned remote branch did not exist before this delivery push (`git rev-parse --verify origin/factory/...` returned `fatal: Needed a single revision`).

Sanctioned status command:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r29-status-after-code.json`

Parsed/readback evidence from `/tmp/r2df-r29-status-after-code.json`:

- `db_backend=agent_core_postgres`.
- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-10-r2df-r29-docs-first-reconciliati`.
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-10-r2df-r29-docs-first-reconciliati`.
- `factory_status_delegated=false`.
- Project `zeus-alpha-research-ledger-core` is `active`.
- Current configured-base G1 rows: `14/14` ready, `g1_blockers=[]`.
- Current active project metadata: `reconciliation_anomalies=[]`, `reconciliation_required=false`.
- This assigned R2df-R29 task is `status=running`, `phase=g1_recovery`.
- The canonical `zeus-alpha-research-ledger-core-reconcile-unvalidated-required-docs` row is currently `status=cancelled`, `phase=documentation`, reflecting current clean document rows rather than the deterministic red-doc regression fixture.

## RED reproduction

Command:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py::test_force_tick_ensures_docs_repair_despite_old_non_reconciliation_anomaly_marker -v`

Pre-fix result:

- Exit `1`.
- Focused test failed at `tests/hermes_cli/test_factory_increment_integration.py:1362` because `factory_pg.force_tick("demo")` returned `tick["claimed"] is None`.
- The fixture had current docs red via `unvalidated_required_docs`, a dependency-free docs reconciliation repair row initially absent until `ensure_reconciliation_tasks` re-created it, a blocked historical product-quality task carrying stale `metadata.reconciliation_anomaly="unvalidated_required_docs"`, and ready product/quality work.
- The failure proved the old blocked non-reconciliation task marker suppressed creation/requeue of the canonical docs repair, leaving no G1/documentation claim before product work.

## Implementation summary

The repair adds a narrow live-reconciliation coverage predicate in `factory_pg.ensure_reconciliation_tasks()`:

1. `_open_reconciliation_task_covers_anomaly(task, code)` returns true only when the task is a live reconciliation row and `_task_covers_reconciliation_anomaly()` also matches the anomaly.
2. `ensure_reconciliation_tasks()` now uses that stricter predicate before skipping creation of a canonical reconciliation task.
3. A blocked or ready non-reconciliation product/quality task that merely retains old `reconciliation_anomaly` metadata no longer suppresses creation of the docs/G1 repair.
4. Existing fail-closed product gating is preserved: the regression asserts a docs-blocked product-quality candidate still receives `missing_or_unindexed_docs` from `_dispatch_preflight_blockers()`.

This changes only reconciliation-task coverage detection. It does not mark documents reviewed, approve gates, close/cancel tasks, merge branches, or dispatch product/runtime work.

## GREEN validation

Focused GREEN:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py::test_force_tick_ensures_docs_repair_despite_old_non_reconciliation_anomaly_marker -v`

Result: `1` selected test passed, `0` failed.

Related Factory tick/increment integration files:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_orchestrator_tick.py`

Result: `2` files, `158` tests passed, `0` failed.

Related Factory control-plane refactor file:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py`

Result: `1` file, `157` tests passed, `0` failed.

Whitespace/tracked diff check:

`git diff --check`

Result: exit `0`, no output.

Temporary helper hygiene: a `/tmp/r2df_r29_parse_status.py` parser was used only to summarize the sanctioned JSON status readback and then self-deleted; `search_files` over `/tmp` confirmed it no longer exists.

## Delivery and review handoff

R2df-R29 remains PR-first. This artifact is implementation evidence only and is `reviewed: pending` until a distinct independent reviewer performs exact-SHA review of the final pushed PR head. The worker must not self-approve, merge, deploy, write direct SQL, mutate the primary checkout, force-push/rewrite unrelated refs, execute external runtimes, or dispatch ALR product/trading work.

---
document_type: canonical_g1_docs_gate_source_root_recovery
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2bm-canonical-g1-docs-gate-source-root-
phase: documentation
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending
owner: claude-builder
base_ref: origin/main
base_sha: 42c86619b91b3a290462c9582e81499e7de8c4c4
branch: factory/zeus-alpha-research-ledger-core/inc-018-r2bm-canonical-g1-docs-gate-sour
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2bm-canonical-g1-docs-gate-sour
run_id: run-1787040594-84f16a63
---

# R2bm — canonical G1 docs gate source-root recovery

## Scope

R2bm is a bounded Factory control-plane prompt/readback repair for the active
G1 docs-gate source-root disagreement on project
`zeus-alpha-research-ledger-core`. It does not implement Alpha Research Ledger
product/runtime functionality and does not authorize ALR-020/product dispatch.

The repair changes only:

- `scripts/factory/factory_orchestrator_tick.py`
- `tests/hermes_cli/test_factory_control_plane_refactor.py`
- this project-local evidence file and the documentation index entry.

No deploy, credential operation, external runtime, direct SQL, primary-checkout
mutation, force-push, merge, connector/messaging action, trading/risk/paper/live
action, or ALR-020/product work is authorized by this increment.

## Evidence consulted

- `DOCUMENTATION_INDEX.md`
- `FACTORY_INTAKE.md`
- `G0_REPOSITORY_STRATEGY.md`
- `TECHNICAL_BLUEPRINT.md`
- `TASK_GRAPH.md`
- `QA_GATES.md`
- `SECURITY_GATES.md`
- `R2BL_NON_DESTRUCTIVE_CANONICAL_G1_EVIDENCE_REPAIR.md`
- Spawned worker prompt readback:
  `/home/jean/.hermes/factory/runs/run-1787040594-84f16a63/prompt.md`

## Reproduced discrepancy

The assigned run prompt itself reproduced the pre-fix disagreement at lines
21–39 of `/home/jean/.hermes/factory/runs/run-1787040594-84f16a63/prompt.md`:

- `G1 readiness: 12/22 documentos sin blocker; blockers=10`
- the ten listed blockers were `missing=reviewed` for required G1 documents;
- the displayed paths were rooted at the assigned worktree:
  `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2bm-canonical-g1-docs-gate-sour/...`.

Canonical status from the assigned worktree contradicted that stale prompt
projection before code changes:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main \
  factory status zeus-alpha-research-ledger-core --json > /tmp/r2bm-status-before.json
```

`/tmp/r2bm-status-before.json` summary:

- `db_backend=agent_core_postgres`, `database=zeus_agent`.
- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2bm-canonical-g1-docs-gate-sour`.
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2bm-canonical-g1-docs-gate-sour`.
- `factory_status_delegated=false`.
- `g1_total=14`, `g1_blockers=0`.
- all required G1 rows read from `readiness_source=configured_base_ref`,
  `base_commit=42c86619b91b3a290462c9582e81499e7de8c4c4`.
- active metadata: `reconciliation_anomalies=[]`,
  `reconciliation_projection_source=current_document_status`,
  `reconciliation_required=false`.
- stale primary checkout was rejected as `primary_checkout_not_configured_base`.

## Root cause

`_canonical_doc_lines()` in `scripts/factory/factory_orchestrator_tick.py` used
`project["document_status"]` from the dispatcher payload and then rewrote row
paths to the assigned worktree. That made one prompt line combine two different
source roots: stale payload readiness rows and worktree-local paths.

The same function also summarized `G1 readiness` with all document rows as the
denominator while counting only G1 blockers. That is why the prompt reported
`12/22` while listing only required-G1 rows.

The canonical project document rows themselves were already clean from the
assigned worktree/current configured base; the defect was prompt/source-root
projection, not G1 document content.

## TDD evidence

RED was captured before implementation with the new regression test:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 \
  scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py \
  -k test_orchestrator_prompt_recomputes_g1_readiness_from_assigned_worktree -v
```

Result: failed as expected because `calls == []`; the old prompt did not
recompute document status from the assigned worktree source root.

GREEN after the fix:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 \
  scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py \
  -k test_orchestrator_prompt_recomputes_g1_readiness_from_assigned_worktree -v
```

Result: 1 selected test passed, 0 failed.

Focused regression suite:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 \
  scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py \
  tests/hermes_cli/test_factory_orchestrator_tick.py -v
```

Result: 2 files, 170 tests passed, 0 failed.

## Repair behavior

The orchestrator prompt now:

1. Recomputes document status from `task.worktree_path` when the assigned
   worktree exists, using `factory_pg.project_document_status()` with
   `repo_path` set to that worktree.
2. Falls back to payload rows if the assigned worktree is absent or recomputation
   fails, preserving fail-closed behavior.
3. Summarizes the G1 gate over G1-required rows, not all lifecycle rows.
4. Emits `source_root=<assigned worktree>` in the G1 readiness line when the
   recomputed source is used.

## Post-fix canonical readbacks

Post-fix status readback:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main \
  factory status zeus-alpha-research-ledger-core --json > /tmp/r2bm-status-after.json
```

`/tmp/r2bm-status-after.json` summary:

- `g1_total=14`, `g1_blockers=0`.
- `readiness_sources=configured_base_ref`.
- `base_commits=42c86619b91b3a290462c9582e81499e7de8c4c4`.
- `reconciliation_anomalies=[]`.
- `reconciliation_projection_source=current_document_status`.
- `reconciliation_required=false`.
- source roots equal the assigned worktree and `factory_status_delegated=false`.

Resolve-state readback required by this task:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main \
  factory project resolve-state zeus-alpha-research-ledger-core --json \
  > /tmp/r2bm-resolve-state-after.json
```

`/tmp/r2bm-resolve-state-after.json` summary:

- `action=resolve-state`, `status=active`.
- `factory_cli_source_root` and `factory_project_action_source_root` equal the
  assigned worktree.
- `factory_project_action_delegated=false`.
- `anomalies=[]`.
- `reconciliation_tasks_created=0`, `reconciliation_tasks_cancelled=0`.
- `supervisor.health=green`, `supervisor.violations=[]`.
- The resolver reopened the historical structured `unvalidated_required_docs`
  blockers on R2ai/R2ae for review; the remaining blocker classification is the
  unrelated R2ac technical rework, not a current G1 docs/index anomaly.

## Delivery contract

This change must be delivered as a normal Zeus-signed, non-draft `agent:zeus`
PR from branch
`factory/zeus-alpha-research-ledger-core/inc-018-r2bm-canonical-g1-docs-gate-sour`.
The final PR head SHA and independent exact-SHA review gate are recorded after
commit/push because the commit cannot contain its own immutable SHA.

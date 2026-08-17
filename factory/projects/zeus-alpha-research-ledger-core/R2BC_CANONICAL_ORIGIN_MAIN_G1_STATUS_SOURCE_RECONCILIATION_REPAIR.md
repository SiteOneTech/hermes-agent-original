---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2bc-canonical-origin-main-g1-status-sou
phase: documentation
status: implemented_pending_independent_review
validated: yes
reviewed: pending_independent_quality_review
owner: codex-builder
engine: codex
run_id: run-1786972123-4a65b34a
base_ref: origin/main
current_origin_sha: b503ba3b57fd606956d0ebf925c83eda253bdcc5
branch: factory/zeus-alpha-research-ledger-core/inc-018-r2bc-canonical-origin-main-g1-st
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2bc-canonical-origin-main-g1-st
created_at_utc: 2026-08-17T13:22:07Z
primary_checkout_path: /home/jean/Projects/hermes-agent-original
primary_checkout_head: 4eb87e4cd48105af05fe974cf1d493f0e1b57ae1
factory_status_green_worktree_json: /tmp/r2bc-worktree-status-green.json
factory_status_green_primary_cwd_current_source_json: /tmp/r2bc-primary-cwd-current-source-status-green.json
factory_status_final_worktree_json: /tmp/r2bc-worktree-status-final.json
factory_status_final_primary_cwd_current_source_json: /tmp/r2bc-primary-cwd-current-source-status-final.json
factory_status_red_primary_json: /tmp/r2bc-primary-status-red-final.json
---

# R2bc — canonical origin/main G1 status-source reconciliation repair

## Scope and boundary

This increment is bounded to Factory CLI status-source and reconciliation readback behavior for the Zeus-only internal project `zeus-alpha-research-ledger-core`.

It does not implement ALR-020 or any Alpha Research Ledger product/runtime feature, does not deploy, does not merge, does not mutate `/home/jean/Projects/hermes-agent-original`, does not change credentials, does not contact external runtimes, does not perform trading/risk/paper/live operations, and does not write direct SQL to `factory.*`. Live Factory DB access stayed limited to the approved read-only CLI path:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json
```

## Canonical inputs read

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md` — mandatory G1 entrypoint and canonical source-of-truth rule.
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md` — Factory status/projection lineage and Zeus-only scope.
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md` — required RED/GREEN/current-origin readback evidence and no-direct-SQL/no-runtime constraints.
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md` — no credential/deploy/external-runtime/trading boundary.
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md` and `TRACKER.md` — R2aw/R2bb status-source lineage and downstream implementation blockers.
- `factory/projects/zeus-alpha-research-ledger-core/R2AW_ISOLATED_CURRENT_ORIGIN_FACTORY_G1_STATUS_RECOVERY.md` — prior cwd-source delegation repair.
- `factory/projects/zeus-alpha-research-ledger-core/R2BB_CURRENT_BASE_G1_STATUS_PROJECTION_PR63_EVIDENCE_RECOVERY.md` — prior status-source provenance repair and remaining primary-checkout canonical run gap.

## Immutable git provenance

Read-only Git evidence before commit creation:

```text
assigned_worktree_branch=factory/zeus-alpha-research-ledger-core/inc-018-r2bc-canonical-origin-main-g1-st
assigned_worktree_head=b503ba3b57fd606956d0ebf925c83eda253bdcc5
assigned_worktree_origin_main=b503ba3b57fd606956d0ebf925c83eda253bdcc5
assigned_worktree_merge_base=b503ba3b57fd606956d0ebf925c83eda253bdcc5
primary_checkout_branch=main
primary_checkout_head=4eb87e4cd48105af05fe974cf1d493f0e1b57ae1
primary_checkout_origin_main=b503ba3b57fd606956d0ebf925c83eda253bdcc5
primary_checkout_merge_base=c846ccfbd844c2f8810a26776505ec44a2341914
primary_checkout_status=main...origin/main [ahead 3, behind 1694]
```

## RED — current primary-checkout canonical defect reproduced

Operational RED readback from the stale primary checkout, using its unmodified source:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2bc-primary-status-red-final.json
```

Parsed result:

```text
factory_cli_source_root=<absent>
factory_status_source_root=<absent>
factory_status_delegated=<absent>
reconciliation_anomalies=["unvalidated_required_docs"]
reconciliation_projection_source=null
reconciliation_required=true
g1_count=14
g1_blocking_count=10
base_commits=[null]
readiness_sources=[null]
primary_heads=[null]
```

Focused RED test added before the repair:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k stale_primary_checkout_to_current_origin_worktree -v --tb=short
```

Result before implementation: 1 selected test failed with `AssertionError: stale primary backend must not be used`. This proved `cmd_status()` still fell through to the stale primary backend when the operator invoked status from the primary checkout itself, even though a complete current `origin/main` worktree was locally available.

## Repair

`hermes_cli/factory.py` now extends Factory source selection for status/tick execution:

- The existing cwd-source delegation remains first-choice for the assigned isolated worktree case from R2aw/R2bb.
- If the running Factory source root is stale relative to its already-fetched `origin/<branch>` and no distinct cwd-source should be preferred, the CLI discovers a complete, clean Git worktree whose HEAD exactly equals the configured local origin ref commit and delegates status/tick execution there.
- The resolver uses only local Git refs and `git worktree list --porcelain`; it performs no fetch, checkout, reset, merge, deploy, DB mutation, or network call.
- Dirty, incomplete, same-root, wrong-commit, unavailable, or absent worktree candidates are ignored; if no valid current-origin source exists, the command fails closed into the existing local behavior instead of fabricating reviewed status.
- A guard prevents backward delegation from a current running source into a stale primary cwd checkout.

## GREEN — tests

Targeted GREEN for the new defect:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k stale_primary_checkout_to_current_origin_worktree -v --tb=short
```

Result: 1 selected test passed, 0 failed.

Relevant regression suites:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -v --tb=short
# 13 tests passed, 0 failed

HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'document_status or status_projection or status_effective_projection or unvalidated_required_docs' -v --tb=short
# 25 tests passed, 0 failed
```

## GREEN — Factory status readback agreement

Readback from the assigned worktree with the repaired source:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2bc-worktree-status-green.json
```

Readback from cwd `/home/jean/Projects/hermes-agent-original` while loading the R2bc current source without modifying that checkout:

```text
PYTHONPATH=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2bc-canonical-origin-main-g1-st \
  /home/jean/Projects/hermes-agent-original/venv/bin/python3 -P -m hermes_cli.main \
  factory status zeus-alpha-research-ledger-core --json \
  > /tmp/r2bc-primary-cwd-current-source-status-green.json
```

Both GREEN readbacks agree on every required G1 row. After project-local evidence docs were updated, the same readbacks were regenerated as `/tmp/r2bc-worktree-status-final.json` and `/tmp/r2bc-primary-cwd-current-source-status-final.json`; the row diff remained empty (`rowsets_equal=true`):

```text
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2bc-canonical-origin-main-g1-st
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2bc-canonical-origin-main-g1-st
factory_status_delegated=false
reconciliation_anomalies=[]
reconciliation_projection_source=current_document_status
reconciliation_required=false
g1_count=14
g1_blocking_count=0
base_commits=["b503ba3b57fd606956d0ebf925c83eda253bdcc5"]
readiness_sources=["configured_base_ref"]
primary_heads=["4eb87e4cd48105af05fe974cf1d493f0e1b57ae1"]
primary_checkout_accepted=[false]
rowsets_equal=true
```

Required G1 rows in both GREEN readbacks:

```text
FACTORY_INTAKE.md true true true true true false configured_base_ref origin/main b503ba3b57fd606956d0ebf925c83eda253bdcc5
REQUIREMENTS_ANALYSIS.md true true true true true false configured_base_ref origin/main b503ba3b57fd606956d0ebf925c83eda253bdcc5
PATTERN_ANALYSIS.md true true true true true false configured_base_ref origin/main b503ba3b57fd606956d0ebf925c83eda253bdcc5
ASSUMPTIONS_AND_OPEN_QUESTIONS.md true true true true true false configured_base_ref origin/main b503ba3b57fd606956d0ebf925c83eda253bdcc5
PRD.md true true true true true false configured_base_ref origin/main b503ba3b57fd606956d0ebf925c83eda253bdcc5
ADRS.md true true true true true false configured_base_ref origin/main b503ba3b57fd606956d0ebf925c83eda253bdcc5
METHODOLOGY_PLAN.md true true true true true false configured_base_ref origin/main b503ba3b57fd606956d0ebf925c83eda253bdcc5
TECHNICAL_BLUEPRINT.md true true true true true false configured_base_ref origin/main b503ba3b57fd606956d0ebf925c83eda253bdcc5
SPRINT_PLAN.md true true true true true false configured_base_ref origin/main b503ba3b57fd606956d0ebf925c83eda253bdcc5
TASK_GRAPH.md true true true true true false configured_base_ref origin/main b503ba3b57fd606956d0ebf925c83eda253bdcc5
TRACKER.md true true true true true false configured_base_ref origin/main b503ba3b57fd606956d0ebf925c83eda253bdcc5
DOCUMENTATION_INDEX.md true true true true true false configured_base_ref origin/main b503ba3b57fd606956d0ebf925c83eda253bdcc5
QA_GATES.md true true true true true false configured_base_ref origin/main b503ba3b57fd606956d0ebf925c83eda253bdcc5
SECURITY_GATES.md true true true true true false configured_base_ref origin/main b503ba3b57fd606956d0ebf925c83eda253bdcc5
```

## Delivery handoff

The final candidate head SHA cannot be embedded here before commit creation without changing the SHA. The Zeus-signed PR must record the final pushed head SHA, include label `agent:zeus`, target `main`, and request independent exact-SHA review. This worker must not self-approve, merge, deploy, mutate primary checkout, change credentials, write direct SQL, contact external runtimes, or authorize ALR-020/product implementation.

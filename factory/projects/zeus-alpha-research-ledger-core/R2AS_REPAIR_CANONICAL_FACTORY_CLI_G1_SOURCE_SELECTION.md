---
document_type: factory_cli_g1_source_selection_repair
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2as-repair-canonical-factory-cli-g1-sou
phase: documentation
status: implemented_pending_independent_quality_review
validated: yes
reviewed: pending_independent_quality_review
owner: claude-builder
engine: claude_code
run_id: run-1787020670-88501649
base_ref: origin/main
base_sha: 34a58a6e1c89a66d1e6f177771ba6f9a8cb78af4
r2ap_integration_commit: 8e3ac22d7ec0f11d29c9c1938a69a33247bb86ec
branch: factory/zeus-alpha-research-ledger-core/inc-018-r2as-repair-canonical-factory-cl
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2as-repair-canonical-factory-cl
primary_checkout: /home/jean/Projects/hermes-agent-original
primary_head: 4eb87e4cd48105af05fe974cf1d493f0e1b57ae1
canonical_status_json_primary_before: /tmp/r2as-status-primary-before.json
canonical_status_json_worktree_before: /tmp/r2as-status-worktree-before.json
canonical_status_json_worktree_after_code: /tmp/r2as-status-worktree-after-code.json
canonical_status_json_worktree_after_docs: /tmp/r2as-status-worktree-after-docs.json
---

# R2as — repair canonical Factory CLI G1 source selection after origin/main integration

## Scope and boundary

This increment is limited to Factory CLI status-source provenance and project-local evidence for the G1 document-status mismatch. It changes no Alpha Research Ledger product/runtime code and performs no merge, deploy, credential access/change, direct SQL, primary-checkout mutation, external runtime execution, messaging connector action, trading/risk/paper/live action, or ALR-020 dispatch.

Factory DB interaction stayed inside the task allowlist: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status ...` for readback. No `psql`, `psycopg2`, ad-hoc DB script, `factory task close`, or base-branch integration command was used.

## Inputs read

- `DOCUMENTATION_INDEX.md` — required entrypoint, G1 status semantics, R2ap/R2cm lineage, PR-first/no-runtime boundary.
- `FACTORY_INTAKE.md` and `G0_REPOSITORY_STRATEGY.md` — Zeus-only scope, primary repo path, `origin/main` base, worktree policy, and PR-first delivery rule.
- `TECHNICAL_BLUEPRINT.md`, `ADRS.md`, `QA_GATES.md`, and `SECURITY_GATES.md` — no-egress/no-runtime/no-direct-SQL boundaries and the existing Factory source-selection gates.
- `R2AP_PR72_RESIDUAL_G1_TASK_METADATA_RECONCILIATION.md` — exact R2ap PR #72 residual metadata evidence and current configured-base G1 readiness.
- `R2CM_G1_REVIEW_STATE_PROVENANCE_REPAIR.md` — prior stale primary/control-plane readback evidence and the ten stale blocker set.
- Code/tests: `hermes_cli/factory.py`, `hermes_cli/factory_pg.py`, `tests/hermes_cli/test_factory_orchestrator_tick.py`, and `tests/hermes_cli/test_factory_control_plane_refactor.py`.

## Reproduced source mismatch

Read-only Git identity evidence from the assigned worktree:

```text
worktree = /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2as-repair-canonical-factory-cl
branch   = factory/zeus-alpha-research-ledger-core/inc-018-r2as-repair-canonical-factory-cl
HEAD     = 34a58a6e1c89a66d1e6f177771ba6f9a8cb78af4
origin/main = 34a58a6e1c89a66d1e6f177771ba6f9a8cb78af4
origin/main parents = c31e937111bba64e478d3c319e896774bf09e40e 8e3ac22d7ec0f11d29c9c1938a69a33247bb86ec
origin/main subject = Merge Factory increment zeus-alpha-research-ledger-core-r2ap-reconcile-residual-g1-task-metadata into main
R2ap commit 8e3ac22d7ec0f11d29c9c1938a69a33247bb86ec is ancestor of origin/main: yes
primary checkout HEAD = 4eb87e4cd48105af05fe974cf1d493f0e1b57ae1
primary status = main...origin/main [ahead 3, behind 1709]
```

Canonical status readback from the stale primary checkout path reproduced the ten stale G1 blockers and lacked source-root provenance:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2as-status-primary-before.json
```

Result summary from `/tmp/r2as-status-primary-before.json`:

```text
factory_cli_source_root=null
factory_status_source_root=null
factory_status_delegated=null
reconciliation_anomalies=["unvalidated_required_docs"]
reconciliation_projection_source=null
required_count=14
blockers=10
blocking files = FACTORY_INTAKE.md, REQUIREMENTS_ANALYSIS.md, PATTERN_ANALYSIS.md,
  ASSUMPTIONS_AND_OPEN_QUESTIONS.md, PRD.md, ADRS.md, METHODOLOGY_PLAN.md,
  TECHNICAL_BLUEPRINT.md, TASK_GRAPH.md, SECURITY_GATES.md
```

The same allowed module invocation from this assigned current-origin worktree did not report the stale blockers; it reported current configured-base provenance. That narrows the observed defect to stale/missing Factory CLI source provenance, not G1 document content:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2as-status-worktree-before.json
```

Result summary from `/tmp/r2as-status-worktree-before.json`:

```text
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2as-repair-canonical-factory-cl
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2as-repair-canonical-factory-cl
factory_status_delegated=null
reconciliation_anomalies=[]
reconciliation_projection_source=current_document_status
required_count=14
blockers=0
```

## Root cause

`hermes_cli.factory.cmd_status()` already had a delegation path for a stale running module when the current working directory is an isolated current-origin source tree. However the direct status path still resolved the Factory backend before verifying CLI source provenance, and `_status_payload()` silently returned backend status without source-root annotations when `_running_factory_source_root()` failed.

That fail-open order permits stale primary status to be presented as canonical evidence without `factory_cli_source_root` / `factory_status_source_root` provenance. The repair makes status verify source provenance before backend readback and fail closed with an explicit JSON/text source-provenance error if the running source cannot be verified.

## Code repair

Changed `hermes_cli/factory.py`:

- `_status_payload()` now verifies `_running_factory_source_root()` before calling the Factory backend, so a malformed running source cannot touch/read stale backend status first.
- `cmd_status()` catches source-provenance failures and returns exit `1` with a structured payload containing:
  - `error_type=factory_status_source_provenance_failed`
  - `factory_status_source_verified=false`
  - `factory_status_source_error`
  - `factory_status_source_file`
  - null `factory_cli_source_root` / `factory_status_source_root`
- `_delegated_status_from_cwd_source()` no longer suppresses malformed running-source provenance; it participates in the same fail-closed status path.
- The provenance error message is generalized from tick-only to `Factory CLI source provenance malformed`.

## RED/GREEN evidence

New regression test: `tests/hermes_cli/test_factory_orchestrator_tick.py::test_status_fails_closed_when_running_source_provenance_malformed`.

RED before implementation:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 \
  scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py \
  -k source_provenance_malformed -v --tb=short
```

Result:

```text
1 failed, 1 passed, 11 deselected
FAILED test_status_fails_closed_when_running_source_provenance_malformed
AssertionError: stale backend must not be used
```

GREEN after implementation:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 \
  scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py \
  -k source_provenance_malformed -v --tb=short
```

Result:

```text
2 tests passed, 0 failed
```

Focused full status-source file after implementation:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 \
  scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -v --tb=short
```

Result:

```text
13 tests passed, 0 failed
```

Post-code current-origin status readback from the assigned worktree:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2as-status-worktree-after-code.json
```

Result summary:

```text
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2as-repair-canonical-factory-cl
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2as-repair-canonical-factory-cl
factory_status_delegated=null
reconciliation_anomalies=[]
reconciliation_projection_source=current_document_status
required_count=14
blockers=0
readiness_sources=["configured_base_ref"]
base_commits=["34a58a6e1c89a66d1e6f177771ba6f9a8cb78af4"]
primary_rejected=["primary_checkout_not_configured_base"]
```

Post-documentation status readback `/tmp/r2as-status-worktree-after-docs.json` again reports the same source roots, `reconciliation_anomalies=[]`, 14 required rows, 0 blockers, `readiness_sources=["configured_base_ref"]`, `base_commits=["34a58a6e1c89a66d1e6f177771ba6f9a8cb78af4"]`, and `primary_rejected=["primary_checkout_not_configured_base"]`.

Claude Code engine note: the assigned engine was invoked in read-only print mode for source-provenance inspection, but it exhausted `--max-turns 4` before returning findings. No files were edited by Claude Code; the implementation and verification above are local tool-backed evidence.

## Delivery and review requirement

This branch must be delivered PR-first as a Zeus-signed `agent:zeus` PR against `main`, with exact final SHA, test evidence, and the no-direct-SQL/no-primary-mutation/no-merge/no-deploy/no-external-runtime boundary in the PR body. It must not be merged or self-approved by this worker. Docs-first dispatch remains blocked unless the canonical G1 gate is genuinely green under verified source provenance and independent quality review passes the exact PR SHA.

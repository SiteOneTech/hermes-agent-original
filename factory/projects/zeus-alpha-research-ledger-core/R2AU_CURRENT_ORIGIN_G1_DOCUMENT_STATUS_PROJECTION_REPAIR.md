---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2au-current-origin-g1-document-status-p
phase: documentation
status: current_origin_g1_document_status_projection_repaired
validated: yes
reviewed: pending_independent_quality_review
owner: codex-builder
engine: codex
created_at: 2026-08-17T09:40:18Z
base_ref: origin/main
current_origin_sha: 2b53ee0f14491ff43da7683d475654a03af5d678
r2at_commit: d4ac6d89994adf823bb50b79afe5a39fd204fdfd
branch: factory/zeus-alpha-research-ledger-core/inc-001-r2au-current-origin-g1-document
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2au-current-origin-g1-document
factory_status_log: /home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786959574-145359-db10.log
---

# R2au — current-origin G1 document-status projection technical repair

## Scope and boundary

This increment repairs only the Factory control-plane document-status projection for the current-origin G1 required-document status of `zeus-alpha-research-ledger-core`.

The repaired behavior keeps the configured `origin/main` / base-ref `document_status` rows authoritative and prevents stale required-doc projection metadata from being re-presented as an active project status after current rows are clean. It does not implement Alpha Research Ledger product/runtime features.

No product ledger code, deployment, credential, connector, messaging, external runtime, trading/risk/paper/live path, primary-checkout mutation, base-branch merge, or direct `factory.*` SQL write is changed or authorized. Delivery remains PR-first through a Zeus-signed `agent:zeus` PR and independent exact-SHA review.

## Canonical inputs read before repair

- `DOCUMENTATION_INDEX.md` — current G1 entrypoint, status semantics, and required reading order.
- `TECHNICAL_BLUEPRINT.md` — confirms this project remains a private Zeus-side Agent Core ledger and not a runtime/trading integration.
- `QA_GATES.md` — current R2at gate and required RED/GREEN / Factory status evidence patterns.
- `SECURITY_GATES.md` — no direct SQL, no primary checkout mutation, no deploy/credential/external-runtime boundary.
- Existing repair lineage in `TASK_GRAPH.md`, `TRACKER.md`, `G1_REVIEW.md`, and `R2AT_CURRENT_ORIGIN_G1_DOCUMENTATION_VALIDATION_REWORK.md`.

## Root cause

R2at already proved current `origin/main` contains reviewed G1 frontmatter and that the configured-base document rows are non-blocking. The remaining defect was projection leakage: a stale required-doc anomaly could survive in `metadata.stale_reconciliation_projection` (or be rebuilt from stale task/projection metadata) and still appear in status payloads that downstream dispatch/watchdog/reviewer consumers inspect.

That made a stale primary checkout/task projection look like current G1 evidence even while the dynamic `document_status` rows came from the correct configured base.

## Repair

Code changed in `hermes_cli/factory_pg.py`:

1. Added `_metadata_contains_stale_g1_projection()` to identify persisted stale required-doc projection metadata.
2. Extended `_stale_g1_projection_metadata_keys()` so the mutating reconciler cleanup path can remove `stale_reconciliation_projection` after the current required-doc rows are clean.
3. Updated `_project_status_effective_reconciliation_projection()` so status readback removes stale G1 projection metadata instead of retaining `unvalidated_required_docs` under an audit-only status key. The active payload now preserves current non-G1 anomalies such as `pending_effective_gates`, sets `reconciliation_projection_source=current_document_status`, and records only neutral cleanup markers.

Regression coverage added in `tests/hermes_cli/test_factory_control_plane_refactor.py`:

- `test_status_projection_uses_origin_base_not_stale_head_or_task_metadata` builds a stale local primary checkout whose `HEAD` has unreviewed G1 docs while `origin/main` has reviewed docs. It also injects stale task/projection metadata. The expected status projection is configured-base rows with zero blockers and no `unvalidated_required_docs` in active project metadata.
- Existing status projection tests were updated so clean current rows no longer preserve stale required-doc anomalies under `stale_reconciliation_projection`, while fail-closed behavior remains when current rows block.

## RED/GREEN evidence

RED before implementation:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k status_projection_uses_origin_base_not_stale_head_or_task_metadata -v --tb=short
```

Result: 1 selected test failed. Failure showed active project metadata still contained `stale_reconciliation_projection={"reconciliation_anomalies":["unvalidated_required_docs"], ...}` even though configured-base G1 rows were non-blocking.

GREEN after implementation:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'status_effective_projection_ignores_stale_unvalidated_docs_when_current_rows_clean or status_projection_uses_origin_base_not_stale_head_or_task_metadata or status_effective_projection_fails_closed_when_current_rows_block' -v --tb=short
```

Result: 3 selected tests passed, 0 failed.

## Current origin/base verification

Read-only Git evidence from the assigned worktree:

```text
git fetch origin main --prune && git rev-parse origin/main && git merge-base --is-ancestor d4ac6d89994adf823bb50b79afe5a39fd204fdfd origin/main
```

Result:

- `origin/main=2b53ee0f14491ff43da7683d475654a03af5d678`.
- `contains_r2at_rc=0`, proving `origin/main` contains R2at commit `d4ac6d89994adf823bb50b79afe5a39fd204fdfd`.
- `git log --oneline -1 d4ac6d89994adf823bb50b79afe5a39fd204fdfd` returned `d4ac6d8999 docs(factory): validate r2at current-origin g1 state`.
- `git log --oneline -1 origin/main` returned `2b53ee0f14 Merge Factory increment zeus-alpha-research-ledger-core-r2at-current-origin-g1-documentation-val into main`.

`git show origin/main:factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md` was written to `/tmp/r2au_origin_main_documentation_index.md`; readback lines 1–13 show frontmatter `validated: yes`, `reviewed: yes`, `reviewed_by: solution-architect`.

## Factory status readback after repair

Approved Factory read path:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json
```

Full output: `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786959574-145359-db10.log`.

Current configured-base G1 rows:

- Lines `20255`–`20604` contain the 14 `g1_required` document rows.
- Every row has `base_ref=origin/main`, `base_branch=main`, `base_commit=2b53ee0f14491ff43da7683d475654a03af5d678`, `readiness_source=configured_base_ref`, and `configured_base_ref_accepted=true`.
- Stale primary checkout is rejected for every row: `primary_checkout_accepted=false`, `primary_checkout_rejected_reason=primary_checkout_not_configured_base`, `primary_head=4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`.
- All 14 required G1 documents report `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, and `blocking=false`.

Active project metadata projection:

- Lines `20808`–`20844` show `cleared_g1_document_reconciliation_projection=true`, `reconciliation_anomalies=["pending_effective_gates"]`, `reconciliation_projection_source=current_document_status`, and `reconciliation_required=true`.
- `metadata.stale_reconciliation_projection` is absent from lines `20808`–`20882`.
- A local parse of `/tmp/r2au_factory_status_after_code.json` reported `metadata_contains_unvalidated=False`, `metadata_has_stale_reconciliation_projection=False`, `g1_blocking_count=0`, `readiness_sources=['configured_base_ref']`, and `base_commits=['2b53ee0f14491ff43da7683d475654a03af5d678']`.

Historical Factory events in the same status payload still retain older anomaly strings as immutable audit history. This repair does not rewrite historical events or tasks; it prevents stale G1 projection metadata from being active project status or dispatch readiness input.

## Delivery handoff

Final PR evidence must name:

- current base SHA `2b53ee0f14491ff43da7683d475654a03af5d678`;
- R2at ancestor commit `d4ac6d89994adf823bb50b79afe5a39fd204fdfd`;
- final R2au candidate head SHA after commit/push;
- Factory status output path `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786959574-145359-db10.log`;
- RED/GREEN test commands and results;
- explicit no direct SQL, no primary-checkout mutation, no merge/deploy/credential/external-runtime/product implementation statement.

Independent review must validate the exact PR head SHA. This worker does not self-approve, merge, deploy, mutate the primary checkout, or execute external runtimes.

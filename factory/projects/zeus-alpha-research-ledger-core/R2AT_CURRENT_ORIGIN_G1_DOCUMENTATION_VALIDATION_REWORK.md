---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2at-current-origin-g1-documentation-val
phase: documentation
status: current_origin_g1_documentation_validation_reworked
validated: yes
reviewed: pending_independent_quality_review
owner: claude-builder
engine: claude_code
created_at: 2026-08-17T08:36:37Z
base_ref: origin/main
current_origin_sha: a41acdc4820b92a31b7d42d9a9c28e95b875a3d1
branch: factory/zeus-alpha-research-ledger-core/inc-001-r2at-current-origin-g1-documenta
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2at-current-origin-g1-documenta
factory_status_log: /home/jean/.hermes/profiles/claude-builder/cache/terminal-output/out-1786955910-3629985-7910.log
---

# R2at — current-origin G1 documentation validation technical rework

## Scope and boundary

This increment repairs only project-local G1 documentation, index and provenance for the current Factory `unvalidated_required_docs` / required-docs projection anomaly. It is documentation-only and remains under `factory/projects/zeus-alpha-research-ledger-core/`.

No product code, Factory runtime code, primary checkout state, `main`, deployment, credential, messaging connector, provider integration, Vonash/Magnus/VAOS/RAG/KB/broker path, trading/risk/paper/live action, external runtime execution or direct `factory.*` SQL write is changed or authorized. No direct SQL was used. Delivery is PR-first, no-auto-merge, and requires independent exact-SHA quality review.

## Canonical inputs read before repair

- Worktree/branch identity: assigned worktree `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2at-current-origin-g1-documenta`, branch `factory/zeus-alpha-research-ledger-core/inc-001-r2at-current-origin-g1-documenta`.
- Git readback after read-only fetch attempt: local `HEAD`, `origin/main`, and merge-base all equal `a41acdc4820b92a31b7d42d9a9c28e95b875a3d1`; worktree status clean before edits.
- Primary checkout identity is evidence only and is rejected by the resolver: `/home/jean/Projects/hermes-agent-original` primary head `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`; it was not merged, rebased, reset, fast-forwarded, or otherwise mutated.
- Canonical Factory source of truth: Agent Core Postgres `factory.*`, read only through `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json` from the assigned worktree.
- Factory CLI status output: `/home/jean/.hermes/profiles/claude-builder/cache/terminal-output/out-1786955910-3629985-7910.log`; command exit `0`.
- G1 docs read: `DOCUMENTATION_INDEX.md`, `FACTORY_INTAKE.md`, `G0_REPOSITORY_STRATEGY.md`, `REQUIREMENTS_ANALYSIS.md`, `PATTERN_ANALYSIS.md`, `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, `PRD.md`, `ADRS.md`, `METHODOLOGY_PLAN.md`, `TECHNICAL_BLUEPRINT.md`, `SPRINT_PLAN.md`, `TASK_GRAPH.md`, `TRACKER.md`, `QA_GATES.md`, `SECURITY_GATES.md`, `REQUIREMENTS_TRACEABILITY.md`, `DATABASE_AND_RUNTIME_CONTRACT.md`, `G1_REVIEW.md`, `G1_DOCUMENT_STATUS_TECHNICAL_RECOVERY.md`, `R2AO_CURRENT_ORIGIN_G1_CONTROL_PLANE_PROJECTION_REPAIR.md`, and `R2AP_CURRENT_ORIGIN_G1_DOCUMENT_VALIDATION_RECOVERY.md`.

## Exact current-origin G1 document-state readback

The exact current-origin state is not missing or unindexed document content. The current dynamic `document_status` rows are clean at the configured base source:

- Log lines `20184`–`20534` contain the 14 `g1_required` rows.
- Every required row has `base_ref=origin/main`, `base_branch=main`, `base_commit=a41acdc4820b92a31b7d42d9a9c28e95b875a3d1`, `readiness_source=configured_base_ref`, and `configured_base_ref_accepted=true`.
- The stale primary checkout is rejected for every row: `primary_checkout_accepted=false`, `primary_checkout_rejected_reason=primary_checkout_not_configured_base`, `primary_head=4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`.
- All 14 required G1 documents report `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, and `blocking=false`.

| Required G1 document | Current status-log lines | Current row result |
|---|---:|---|
| `FACTORY_INTAKE.md` | `20185`–`20209` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `REQUIREMENTS_ANALYSIS.md` | `20210`–`20234` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `PATTERN_ANALYSIS.md` | `20235`–`20259` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | `20260`–`20284` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `PRD.md` | `20285`–`20309` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `ADRS.md` | `20310`–`20334` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `METHODOLOGY_PLAN.md` | `20335`–`20359` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `TECHNICAL_BLUEPRINT.md` | `20360`–`20384` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `SPRINT_PLAN.md` | `20385`–`20409` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `TASK_GRAPH.md` | `20410`–`20434` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `TRACKER.md` | `20435`–`20459` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `DOCUMENTATION_INDEX.md` | `20460`–`20484` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `QA_GATES.md` | `20485`–`20509` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `SECURITY_GATES.md` | `20510`–`20534` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |

Lifecycle and PM projection documents such as `QA_REPORT.md`, `SECURITY_REVIEW.md`, `QUALITY_REVIEW.md`, `DELIVERY_REPORT.md`, `CHANGELOG.md`, `CHANGE_RECORDS.md`, `RETROSPECTIVE.md`, and `NOTION_UPDATE.md` are absent/unindexed in the same status output but are non-blocking because their categories are `lifecycle` or `pm_projection`, not current `g1_required` blockers.

## Exact anomaly/projection condition

The exact condition that triggered R2at is stale event/projection evidence, not a missing current-origin G1 document:

- Recent reconciler event `194478` lines `470`–`496` still reports `metadata.anomalies=["unvalidated_required_docs"]` immediately before task claim.
- Recent reconciler event `194477` lines `499`–`525` reports the same anomaly.
- Dispatch preflight event `194474` lines `576`–`590` denies ALR-020 with `metadata.blockers=["missing_or_unindexed_docs"]`.
- Current effective project metadata lines `20769`–`20771` reports `reconciliation_anomalies=[]`, `reconciliation_projection_source=current_document_status`, and `reconciliation_required=false`.
- Lines `20802`–`20806` retain `stale_reconciliation_projection={"reconciliation_anomalies":["unvalidated_required_docs"]}` as audit-only stale projection evidence, not active readiness state.
- Line `20751` records `factory_auto_integration_forbidden=true`, so no auto-integration is authorized by this recovery.
- Lines `20758`–`20761` show Notion is not a canonical blocker here: `notion_required=false`, `notion_sync_required=false`, and `notion_workflow_disabled=true`.

Therefore the required-doc condition is resolved as: prior Factory task context and recent event/preflight records carried stale `unvalidated_required_docs` / `missing_or_unindexed_docs`, while current `origin/main` `a41acdc4820b92a31b7d42d9a9c28e95b875a3d1` row-level `document_status` shows all 14 required G1 documents committed, indexed, validated, reviewed, and non-blocking, with active project projection sourced from `current_document_status` and no active reconciliation anomaly.

## Documentation repair

This branch makes the current-origin condition independently verifiable by:

1. Adding this R2at evidence artifact with immutable base SHA, Factory status log path, event IDs, current row-line ranges, and no-runtime/no-direct-SQL/no-auto-merge boundary.
2. Updating `DOCUMENTATION_INDEX.md` to index R2at as the latest current-origin validation evidence and keep R2ap/R2ao as historical predecessors.
3. Updating `G0_REPOSITORY_STRATEGY.md`, `TASK_GRAPH.md`, `TRACKER.md`, `G1_REVIEW.md`, `QA_GATES.md`, and `SECURITY_GATES.md` so the current base, stale-event condition, PR-first handoff, and independent exact-SHA quality-review requirement are not inferred from stale PRs or historical task summaries.

This is not a product implementation and does not authorize ALR-020+ implementation dispatch by itself. Downstream work still requires its own scoped TDD, security, QA, PR-first and QA Guardian gates.

## Local validation evidence

- RED before repair: `python3 /tmp/validate_r2at_docs.py` returned `R2AT_DOC_VALIDATION=FAIL` because this artifact and the R2at index/gate/tracker/task-graph/G1-review/G0 markers were absent.
- GREEN after repair: `python3 /tmp/validate_r2at_docs.py` returned `R2AT_DOC_VALIDATION=PASS`, `checked_files=8`, `base=a41acdc4820b92a31b7d42d9a9c28e95b875a3d1`, `artifact=R2AT_CURRENT_ORIGIN_G1_DOCUMENTATION_VALIDATION_REWORK.md`.
- Whitespace check: `git diff --check` exited `0`.
- Post-repair Factory readback: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json` exited `0` and wrote `/home/jean/.hermes/profiles/claude-builder/cache/terminal-output/out-1786956406-3629985-9010.log`. This readback still shows the current `unvalidated_required_docs` event anomaly while preserving the row-level configured-base G1 evidence documented above.
- Remaining delivery evidence to be recorded after commit/push: actual Git candidate SHA, pushed branch, Zeus-signed `agent:zeus` PR, and independent exact-SHA quality-review request. These values are recorded in the PR and Factory gate evidence because the final Git SHA is only known after the documentation commit exists.

## Delivery handoff

Final PR evidence must name:

- immutable current base SHA: `a41acdc4820b92a31b7d42d9a9c28e95b875a3d1`;
- final candidate head SHA after commit/push;
- Factory status output path: `/home/jean/.hermes/profiles/claude-builder/cache/terminal-output/out-1786955910-3629985-7910.log` plus any post-repair status output;
- validation commands and results;
- explicit no-auto-merge, no direct SQL, no primary-checkout mutation, no deploy, and no external runtime execution statement.

Independent `quality-reviewer` review must be requested against the exact final candidate SHA before the task can be accepted. This worker does not self-approve, merge, deploy, mutate the primary checkout, or execute external runtimes.

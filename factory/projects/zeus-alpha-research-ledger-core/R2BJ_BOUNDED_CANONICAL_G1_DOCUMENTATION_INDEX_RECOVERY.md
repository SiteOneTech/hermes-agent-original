---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2bj-bounded-canonical-g1-documentation-
phase: documentation
status: implemented_pending_independent_review
validated: yes
reviewed: pending_independent_quality_review
owner: codex-builder
engine: codex
run_id: run-1786980510-faa0d537
base_ref: origin/main
base_sha: b503ba3b57fd606956d0ebf925c83eda253bdcc5
branch: factory/zeus-alpha-research-ledger-core/inc-017-r2bj-bounded-canonical-g1-docume
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2bj-bounded-canonical-g1-docume
factory_status_json: /tmp/r2bj-status-final.json
factory_status_log: /home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786980569-860127-b650.log
---

# R2BJ — bounded canonical G1 documentation/index technical recovery

## Scope and boundary

This increment repairs only current-base documentation/index/evidence for the active Factory docs-first discrepancy. It changes project-local Markdown under `factory/projects/zeus-alpha-research-ledger-core/` only.

It does not change product implementation, Agent Core data, Factory runtime code, deployment, credentials, messaging/connectors, external runtimes, the stale primary checkout, trading/risk/paper/live behavior, or `factory.*` rows by direct SQL. It does not merge.

## Canonical inputs read

- `DOCUMENTATION_INDEX.md` — required entrypoint, current G1 matrix, reading order, source-of-truth hierarchy, R2aw/R2bb lineage.
- Required G1/control documents: `FACTORY_INTAKE.md`, `G0_REPOSITORY_STRATEGY.md`, `REQUIREMENTS_ANALYSIS.md`, `PRD.md`, `TASK_GRAPH.md`, `TRACKER.md`, `QA_GATES.md`, `SECURITY_GATES.md`, and `G1_REVIEW.md`.
- Current evidence artifacts: `R2AW_ISOLATED_CURRENT_ORIGIN_FACTORY_G1_STATUS_RECOVERY.md` and `R2BB_CURRENT_BASE_G1_STATUS_PROJECTION_PR63_EVIDENCE_RECOVERY.md`.
- Source predicate code: `hermes_cli/factory_pg.py` around `_g1_document_blockers`, `_project_status_effective_reconciliation_projection`, `reconciliation_findings`, `_project_docs_notion_preflight`, and `_dispatch_preflight_blockers`.

## Current branch/worktree provenance

Read-only Git evidence after `git fetch origin main` from the assigned worktree:

```text
branch=factory/zeus-alpha-research-ledger-core/inc-017-r2bj-bounded-canonical-g1-docume
HEAD=b503ba3b57fd606956d0ebf925c83eda253bdcc5
origin/main=b503ba3b57fd606956d0ebf925c83eda253bdcc5
merge-base=b503ba3b57fd606956d0ebf925c83eda253bdcc5
worktree_status=clean before this documentation edit
```

## Canonical Factory CLI readback

Allowed Factory DB interaction for this run was limited to the canonical status/gate-record CLI path. The current status readback command was:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2bj-status-before.json
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2bj-status-final.json
```

Parsed current status summary:

```text
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2bj-bounded-canonical-g1-docume
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2bj-bounded-canonical-g1-docume
factory_status_delegated=false
db_backend=agent_core_postgres
database=zeus_agent
project_status=active
repo_strategy_status=passed
repo_scope=zeus_only
work_intent=add_functionality
notion_required=false
notion_workflow_disabled=true
reconciliation_anomalies=[]
reconciliation_projection_source=current_document_status
reconciliation_required=false
```

Current required-document row readback:

```text
g1_required_count=14
blocking_count=0
readiness_sources=["configured_base_ref"]
base_commits=["b503ba3b57fd606956d0ebf925c83eda253bdcc5"]
primary_checkout_accepted=[false]
primary_path=/home/jean/Projects/hermes-agent-original
primary_head=4eb87e4cd48105af05fe974cf1d493f0e1b57ae1
```

All required project-local document locations read back from the status payload as `exists=true`, `indexed=true`, `committed=true`, `validated=true`, `reviewed=true`, `blocking=false`:

1. `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
2. `factory/projects/zeus-alpha-research-ledger-core/REQUIREMENTS_ANALYSIS.md`
3. `factory/projects/zeus-alpha-research-ledger-core/PATTERN_ANALYSIS.md`
4. `factory/projects/zeus-alpha-research-ledger-core/ASSUMPTIONS_AND_OPEN_QUESTIONS.md`
5. `factory/projects/zeus-alpha-research-ledger-core/PRD.md`
6. `factory/projects/zeus-alpha-research-ledger-core/ADRS.md`
7. `factory/projects/zeus-alpha-research-ledger-core/METHODOLOGY_PLAN.md`
8. `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
9. `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
10. `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
11. `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
12. `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
13. `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
14. `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`

## Exact failing predicate

The source-backed predicate is the docs-first dispatch preflight:

- `hermes_cli/factory_pg.py` `_dispatch_preflight_blockers(...)` returns `missing_or_unindexed_docs` when `docs_ready` is false for product/QA/security/delivery dispatch tasks.
- `_project_docs_notion_preflight(...)` computes `docs_ready` from two conditions: zero current G1 document blockers and no `missing_project_artifact_dir` reconciliation finding.
- `reconciliation_findings(...)` emits `unvalidated_required_docs` only when `_g1_document_blockers(project)` returns required G1 rows with missing `exists/indexed/committed/validated/reviewed` state.

The current Factory CLI status payload proves those current row-level conditions are satisfied: all 14 required G1 rows are non-blocking at `readiness_source=configured_base_ref`, and active project metadata has `reconciliation_anomalies=[]` from `current_document_status`. Therefore the still-visible `unvalidated_required_docs` / `missing_or_unindexed_docs` evidence is stale event/gate/projection evidence, not a current document-content predicate failure.

The stale current readback to preserve as audit evidence is:

- Event `195559`, `dispatch_preflight_denied`, for `zeus-alpha-research-ledger-core-alr-020-r2-bounded-pr-first-signature-an`, metadata `blockers=["missing_or_unindexed_docs"]`.
- Events `195563`, `195562`, `195560`, and `195558`, `project_reconciled`, metadata `anomalies=["unvalidated_required_docs"]`.
- Gate `884`, `quality failed`, for stale R2ae / PR #44 evidence: PR #44 head `768444e33a...` is conflicting/dirty against current `origin/main b503ba3b57...`, while the active status readback from this worktree reports zero current G1 blockers.

## Repair applied

This R2BJ repair records the current Factory status/readiness truth in the project-local evidence pack and indexes it so future dispatch/review consumers do not rely on stale R2ae/PR #44 or historical 10-blocker summaries as current docs-first state.

Changed evidence surfaces:

- New artifact: `R2BJ_BOUNDED_CANONICAL_G1_DOCUMENTATION_INDEX_RECOVERY.md`.
- `DOCUMENTATION_INDEX.md`: current controlling status plus supplemental artifact/read-order/status semantics entry.
- `TASK_GRAPH.md`, `TRACKER.md`, `QA_GATES.md`, `SECURITY_GATES.md`, and `G1_REVIEW.md`: current R2BJ task/evidence/gate boundary entries.

This is a documentation/index/evidence repair only. Any future recurrence of `missing_or_unindexed_docs` with the same clean current rows remains bounded Factory technical rework in the control-plane projection/dispatch path, not a human decision request and not a reason to mutate Factory DB by direct SQL.

## Validation result

Post-edit validation for this candidate:

1. `git diff --cached --check` — PASS.
2. `git ls-files --error-unmatch factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md factory/projects/zeus-alpha-research-ledger-core/G1_REVIEW.md factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md factory/projects/zeus-alpha-research-ledger-core/TRACKER.md factory/projects/zeus-alpha-research-ledger-core/R2BJ_BOUNDED_CANONICAL_G1_DOCUMENTATION_INDEX_RECOVERY.md` — PASS; all seven changed project-local docs/artifacts are tracked/staged.
3. Canonical Factory status readback assertion over `/tmp/r2bj-status-final.json` — PASS: `db_backend=agent_core_postgres`, worktree source roots match this assigned worktree, active `reconciliation_anomalies=[]`, `reconciliation_projection_source=current_document_status`, `reconciliation_required=false`, `notion_required=false`, `g1_required_count=14`, `blocking_count=0`, all required rows have `exists/indexed/committed/validated/reviewed=true`, `readiness_source=configured_base_ref`, `base_commit=b503ba3b57fd606956d0ebf925c83eda253bdcc5`, and `primary_checkout_accepted=false`.
4. Initial `scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_orchestrator_tick.py` failed only because this isolated worktree has no local pytest venv and no package install was permitted. Retried without installing packages using the canonical shared venv path: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_orchestrator_tick.py` — PASS: 2 files, 167 tests passed, 0 failed in 11.6s.

The final immutable commit SHA and post-edit validation output are also recorded in the Zeus-signed `agent:zeus` PR body and Factory gate evidence after commit creation; the SHA cannot be embedded in this committed file without changing itself.

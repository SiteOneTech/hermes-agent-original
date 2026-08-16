---
document_type: canonical_g1_document_status_source_alignment
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2y-repair-canonical-g1-document-status-
phase: documentation
status: implemented_pending_independent_quality_review
validated: yes
reviewed: pending_independent_quality_review
owner: codex-builder
base_ref: origin/main
base_sha: 1b6bc0f65d3ad49845d20e056203e3b3702ac2a7
branch: factory/zeus-alpha-research-ledger-core/inc-001-r2y-repair-canonical-g1-document
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2y-repair-canonical-g1-document
status_evidence_command: /home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json
status_evidence_log: /home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786870710-863987-8590.log
---

# R2y — canonical G1 document-status source alignment

## Scope

This is a bounded documentation/reconciliation repair for the active Factory anomaly `unvalidated_required_docs`. It records the live canonical status-source alignment and PR-first review handoff only. It does not modify product code, Agent Core schema, external connectors, trading/risk/broker behavior, messaging, deployment paths, credentials, or the shared primary checkout.

## Source checkout recorded

- Assigned worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2y-repair-canonical-g1-document`.
- Assigned branch: `factory/zeus-alpha-research-ledger-core/inc-001-r2y-repair-canonical-g1-document`.
- Repository remote: `https://github.com/SiteOneTech/hermes-agent-original.git`.
- Source checkout before this repair: `HEAD=1b6bc0f65d3ad49845d20e056203e3b3702ac2a7` and `origin/main=1b6bc0f65d3ad49845d20e056203e3b3702ac2a7` after `git fetch origin main --prune`.
- Factory project `repo_path` remains `/home/jean/Projects/hermes-agent-original` and stale metadata still names historical `metadata.g1_documentation_checkout` PR #20 / `dad375f27568c38be771fc597b579d087f034e1d`. That stale metadata is provenance history, not a reviewed current candidate.

## Root cause diagnosis

The user-visible anomaly was not a missing reviewed marker in the current configured base ref. The live `factory status` read-back from the assigned worktree and repository venv evaluates `project.document_status` through the R2v configured-base-ref path:

- primary checkout rows are not trusted when they still expose G1 blockers;
- readiness is then read from `origin/<base_branch>` with `git show <ref>:factory/projects/<project>/...`;
- candidate PR/worktree metadata is not a readiness source;
- each row records `readiness_source=configured_base_ref`, `base_ref=origin/main`, and `base_commit=1b6bc0f65d3ad49845d20e056203e3b3702ac2a7`.

The stale `unvalidated_required_docs` signal persists in recent reconciler events/project metadata because those records trail the live status evaluation and still carry historical primary-checkout/PR #20 provenance. This repair records that distinction so reviewers do not reopen G1 work based on stale event summaries when `project.document_status` itself reports zero required blockers.

## Canonical document-status evidence

Approved command, run from the assigned worktree with the main repository venv:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`

Hermes saved the full output at `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786870710-863987-8590.log`.

In that output, `projects[0].document_status` reports all 14 required G1 documents with:

- `base_ref=origin/main`
- `base_commit=1b6bc0f65d3ad49845d20e056203e3b3702ac2a7`
- `readiness_source=configured_base_ref`
- `configured_base_ref_accepted=true`
- `exists=true`
- `committed=true`
- `indexed=true`
- `validated=true`
- `reviewed=true`
- `blocking=false`

Required rows verified by the read-back: `FACTORY_INTAKE.md`, `REQUIREMENTS_ANALYSIS.md`, `PATTERN_ANALYSIS.md`, `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, `PRD.md`, `ADRS.md`, `METHODOLOGY_PLAN.md`, `TECHNICAL_BLUEPRINT.md`, `SPRINT_PLAN.md`, `TASK_GRAPH.md`, `TRACKER.md`, `DOCUMENTATION_INDEX.md`, `QA_GATES.md`, and `SECURITY_GATES.md`.

## PR-first repair contract

1. Commit only this project-local documentation/reconciliation evidence update.
2. Push the assigned branch to `origin`.
3. Open a Zeus-signed GitHub PR against `main` labeled `agent:zeus`.
4. The PR body and Factory gate note must name the exact pushed candidate SHA because a commit cannot embed its own final SHA without changing that SHA.
5. Independent review must inspect the exact pushed PR head and either PASS it or create bounded rework.
6. No merge, deployment, direct SQL, credential access, external connector action, product implementation, trading/risk/paper/live behavior, or shared primary checkout mutation is authorized by this repair.

## Validation checklist

Required checks for this candidate:

- `git diff --check origin/main..HEAD` succeeds.
- `git diff --name-only origin/main..HEAD` remains under `factory/projects/zeus-alpha-research-ledger-core/`.
- `git ls-files --error-unmatch` succeeds for this artifact and every edited project-local documentation artifact.
- Factory status read-back shows zero required G1 document blockers in `projects[0].document_status` for configured base ref `origin/main` at `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7`.

## Boundary

Clearing the G1 document-status blocker only removes the documentation-readiness anomaly. It does not authorize ALR-020+ implementation dispatch, runtime propagation, sandbox deploy, production deploy, external data-provider integration, broker/trading/risk/paper/live action, or QA Guardian merge bypass. Downstream increments still require their own task-specific TDD, security/no-egress, QA, delivery, and PR-first review evidence.

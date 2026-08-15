---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2n-repair-g1-canonical-document-validat
phase: documentation
status: canonical_document_status_reproduced
validated: yes
reviewed: pending_independent_exact_sha
owner: codex-builder
---

# R2n canonical-document validation repair and exact-SHA handoff

## Scope

This is a bounded documentation-only repair for the active `unvalidated_required_docs` anomaly. It updates the G1 handoff to the current assigned R2n branch/base and records why the canonical Factory checker still reads G1 as not dispatchable until an independent exact-SHA review and source-of-truth reconciliation occur.

This artifact does not mark any required G1 document `reviewed: yes`, does not self-approve, does not merge, does not deploy, does not change credentials, does not write direct SQL, does not alter runtime/external integrations, and does not authorize ALR-020 or later implementation.

## Current R2n branch and base provenance

Read-only Git verification from the assigned isolated worktree recorded:

- Assigned branch: `factory/zeus-alpha-research-ledger-core/inc-034-r2n-repair-g1-canonical-document`.
- Assigned worktree root: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-034-r2n-repair-g1-canonical-document`.
- Repository remote: `https://github.com/SiteOneTech/hermes-agent-original.git` (`origin`).
- Canonical base branch: `origin/main`.
- Exact branch/base/remote-main SHA before this repair: `df4c77fd1413a65cdb85885a06978ff157c1de4d`.
- The R2n branch was initially equal to that base before this documentation-only correction.

## Canonical Factory status reproduced

The approved Factory status path is Agent Core Postgres `factory.*` via `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`. The reproduced status read-back used backend `agent_core_postgres`, database `zeus_agent`, canonical project `repo_path=/home/jean/Projects/hermes-agent-original`, and project anomaly `metadata.reconciliation_anomalies=["unvalidated_required_docs"]`.

The current project-level `document_status` rows read from the primary source show all 14 required G1 documents as present, indexed, committed and validated, but not reviewed. The prompt snapshot listed a smaller blocker subset; the canonical live read-back below is the binding source for this repair:

| Required G1 document | Readiness source | Exists | Indexed | Committed | Validated | Reviewed | Blocking cause |
|---|---|---:|---:|---:|---:|---:|---|
| `FACTORY_INTAKE.md` | primary | true | true | true | true | false | missing reviewed |
| `REQUIREMENTS_ANALYSIS.md` | primary | true | true | true | true | false | missing reviewed |
| `PATTERN_ANALYSIS.md` | primary | true | true | true | true | false | missing reviewed |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | primary | true | true | true | true | false | missing reviewed |
| `PRD.md` | primary | true | true | true | true | false | missing reviewed |
| `ADRS.md` | primary | true | true | true | true | false | missing reviewed |
| `METHODOLOGY_PLAN.md` | primary | true | true | true | true | false | missing reviewed |
| `TECHNICAL_BLUEPRINT.md` | primary | true | true | true | true | false | missing reviewed |
| `SPRINT_PLAN.md` | primary | true | true | true | true | false | missing reviewed |
| `TASK_GRAPH.md` | primary | true | true | true | true | false | missing reviewed |
| `TRACKER.md` | primary | true | true | true | true | false | missing reviewed |
| `DOCUMENTATION_INDEX.md` | primary | true | true | true | true | false | missing reviewed |
| `QA_GATES.md` | primary | true | true | true | true | false | missing reviewed |
| `SECURITY_GATES.md` | primary | true | true | true | true | false | missing reviewed |

## Concrete mismatch repaired

The R2m handoff is now stale as the active review target because it names branch `factory/zeus-alpha-research-ledger-core/inc-001-r2m-current-base-g1-documentatio` and base `ab08b13669903a87b3d60d6c80231d23d6313782`, while the active repair branch was created from current `origin/main` at `df4c77fd1413a65cdb85885a06978ff157c1de4d`.

Agent Core project metadata also still carries the older `metadata.g1_documentation_checkout` pointer to PR #20 / `dad375f27568c38be771fc597b579d087f034e1d`, `not_merged=true`, under branch `factory/zeus-alpha-research-ledger-core/inc-011-alr-010-r2-pr-first-g1-reconciliation`. That stale metadata is not a reviewed candidate and must not be used to dispatch ALR-020.

This repair makes R2n the active documentation handoff, preserves R2j/R2k/R2m as historical provenance, and keeps required G1 `reviewed` markers pending because this worker is not the independent reviewer.

## Exact-SHA review handoff

After this documentation-only change is committed, pushed and opened as a fresh Zeus-signed `agent:zeus` PR, independent reviewers must bind PASS/REQUEST_CHANGES to the PR head SHA, not to PR #20, PR #29, PR #30, PR #31, the R2m branch, or any review-worktree `already_ancestor` attachment.

The PR body and Factory gate evidence must record:

- PR URL and number.
- Head branch `factory/zeus-alpha-research-ledger-core/inc-034-r2n-repair-g1-canonical-document`.
- Base branch `main` / `origin/main` at `df4c77fd1413a65cdb85885a06978ff157c1de4d` before this correction.
- Exact candidate head SHA after push.
- Documentation-only changed paths.
- Local validation commands and results.
- Remaining canonical cause if `unvalidated_required_docs` persists: primary source still has `reviewed=false` until the PR/review/metadata path is reconciled.

## Remaining canonical cause if status is not cleared

A docs-only branch cannot clear the live Agent Core `document_status` by itself because the project currently reads the primary checkout at `/home/jean/Projects/hermes-agent-original` and has no accepted `reviewed_g1_candidate` metadata for this R2n PR head. Until an authorized PR-first / QA Guardian or project-metadata reconciliation path points Factory at an independently reviewed exact candidate, the checker correctly remains fail-closed on `reviewed=false`.

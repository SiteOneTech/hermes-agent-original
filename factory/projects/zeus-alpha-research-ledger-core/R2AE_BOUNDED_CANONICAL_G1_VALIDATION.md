---
document_type: bounded_canonical_g1_validation_evidence
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2ae-bounded-canonical-g1-validation-and
phase: documentation
status: current_base_candidate
validated: yes
reviewed: pending_independent_quality_review
owner: codex-builder
base_ref: origin/main
base_sha: b68ec8ad5cf986e5bf4900506820ca978ef0b0c0
branch: factory/zeus-alpha-research-ledger-core/inc-019-r2ae-bounded-canonical-g1-valida
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2ae-bounded-canonical-g1-valida
---

# R2ae — bounded canonical G1 validation and fresh PR provenance repair

## Scope

This is the current-base R2ae rework for the active Factory anomaly label `unvalidated_required_docs`. It is documentation/provenance only. It uses the assigned Factory worktree for readback, avoids the primary checkout, and records the exact Agent Core Factory status observed through the approved Hermes Factory CLI.

No runtime/source implementation, merge, deploy, credential change, direct SQL, external runtime, connector/messaging action, or trading/risk/paper/live operation is authorized by this artifact. Downstream ALR implementation remains blocked behind its own task-specific TDD, security, QA, PR-first, and QA Guardian evidence.

## Current-base identity and source commands

Read-back timestamp: `2026-08-19T00:17:08Z`.

Sources used:

- Assigned worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2ae-bounded-canonical-g1-valida`.
- Assigned branch: `factory/zeus-alpha-research-ledger-core/inc-019-r2ae-bounded-canonical-g1-valida`.
- Canonical base ref: `origin/main` at `b68ec8ad5cf986e5bf4900506820ca978ef0b0c0`.
- Approved Factory status command: `/home/jean/Projects/hermes-agent-original/venv/bin/python -m hermes_cli.main factory status --json zeus-alpha-research-ledger-core`.
- Factory status output saved by Hermes: `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1787098065-2341027-63d0.log`.
- Factory status row evidence: lines `21838`–`22104` contain the required G1 `document_status` rows for the current configured base.
- PR provenance readback: `GH_REPO=SiteOneTech/hermes-agent-original gh pr view 44 --json ...` returned PR #44 open, non-draft, label `agent:zeus`, old head `768444e33ac64bf238e64c1df4c49fe2020b51a8`, and `mergeStateStatus=DIRTY` before this repair.

## Source-backed required G1 inventory

The current configured-base `document_status` block reports `readiness_source=configured_base_ref`, `base_ref=origin/main`, `base_commit=b68ec8ad5cf986e5bf4900506820ca978ef0b0c0`, and `configured_base_ref_accepted=true` for every required G1 row.

The current source-backed unvalidated/blocking required G1 inventory is therefore exactly one document: `DOCUMENTATION_INDEX.md`. The ten-document blocker list in the worker prompt is stale relative to this current-base row-level readback.

| Required G1 document | Current-base Factory `document_status` |
|---|---|
| `FACTORY_INTAKE.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `REQUIREMENTS_ANALYSIS.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `PATTERN_ANALYSIS.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `PRD.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `ADRS.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `METHODOLOGY_PLAN.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `TECHNICAL_BLUEPRINT.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `SPRINT_PLAN.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `TASK_GRAPH.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `TRACKER.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `DOCUMENTATION_INDEX.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=false, blocking=true |
| `QA_GATES.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `SECURITY_GATES.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |

## Canonical state versus stale PR artifacts

Canonical current-base state:

- Current configured base is `origin/main` / `b68ec8ad5cf986e5bf4900506820ca978ef0b0c0`.
- The current base already contains the later R2dc review-state recovery evidence and many successor artifacts that did not exist in the stale PR #44 candidate.
- Current Factory status still projects `reconciliation_anomalies=["unvalidated_required_docs"]` and `reconciliation_required=true` because `DOCUMENTATION_INDEX.md` is the only required G1 row still blocking in the current readback.

Stale, merged, or conflicting artifacts:

- The old PR #44 head `768444e33ac64bf238e64c1df4c49fe2020b51a8` is non-canonical: GitHub reports `mergeStateStatus=DIRTY`, and its diff against current `origin/main` would delete later project-local R2 evidence files. It must not be approved as the active candidate.
- Earlier PR #44 commit `bb8495a61611cfd9501c00f7a48fda42cfaee61f` is historical R2ae evidence only. It started from `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7`, not current `b68ec8ad5cf986e5bf4900506820ca978ef0b0c0`.
- Prompt-time blockers naming ten required docs are stale source-root/projection artifacts for this run. The current row-level readback names only `DOCUMENTATION_INDEX.md` as blocking.
- Later merged artifacts through R2dc are preserved on current `origin/main`; this repair does not delete or supersede them.

## Repair performed in this candidate

This candidate replaces the stale/conflicting PR #44 provenance with a current-base, PR-first documentation repair:

1. Adds this R2ae evidence artifact from current base `b68ec8ad5cf986e5bf4900506820ca978ef0b0c0`.
2. Updates `DOCUMENTATION_INDEX.md` to index the current R2ae rework and reassert the index's own machine-readable reviewed status for the fresh candidate.
3. Leaves all later R2 evidence artifacts from `origin/main` intact.
4. Delivers through the existing R2ae task branch/PR only; no merge, primary-checkout mutation, direct SQL, or external runtime action is performed.

The final candidate SHA is intentionally recorded in the PR body and Factory gate evidence after commit/push; embedding it here would alter the SHA.

## Validation contract

Required checks for this repair:

1. `git diff --check origin/main..HEAD` succeeds.
2. `git diff --name-only origin/main..HEAD` is limited to `factory/projects/zeus-alpha-research-ledger-core/`.
3. `git ls-files --error-unmatch` succeeds for the 14 required G1 documents plus this R2ae evidence artifact.
4. GitHub PR #44 readback shows an open, non-draft, Zeus-authored/Zeus-signed `agent:zeus` PR against `main` with the refreshed head SHA and clean ancestry from current `origin/main`.
5. Factory status/gate evidence records the current exact state: one current-base required-doc blocker before merge (`DOCUMENTATION_INDEX.md`), and this PR as the bounded candidate repair. If current configured-base validation remains blocked without a prohibited merge, the canonical cause is this unmerged current-base required-doc row, not the stale ten-document prompt list.

## Dispatch boundary

R2ae repairs provenance and documentation only. It does not clear manual pause, bypass `factory_auto_integration_forbidden=true`, close/supersede historical Factory task rows, merge PR #44, deploy, change credentials, write direct SQL, touch messaging/connectors, or dispatch ALR-020+. If the active status remains blocked before QA Guardian merge, the bounded technical cause is the current configured-base `DOCUMENTATION_INDEX.md` required-doc row plus unmerged PR-first candidate state.

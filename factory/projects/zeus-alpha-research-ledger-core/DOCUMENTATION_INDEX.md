---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_candidate_reviewed_primary_hold
validated: yes
reviewed: yes
reviewed_by: quality-reviewer
review_evidence: factory_gate_789
reviewed_candidate_sha: 1e82340dddf52071d14c3c7a00b04b3c17ee2821
reviewed_candidate_pr: https://github.com/SiteOneTech/hermes-agent-original/pull/33
owner: factory-orchestrator
---

# DOCUMENTATION INDEX — Zeus Alpha Research Ledger Core

## Controlling status

Canonical G1 pack for the **private Zeus-side implementation** succeeding `zeus-independent-alpha-research`. It is not a Vonash implementation plan, grants no external runtime access and does not authorize market execution.

R2o applies candidate-level `reviewed: yes` markers to the 14 required G1 documents because independent Factory quality gate **789** passed against exact PR #33 candidate SHA `1e82340dddf52071d14c3c7a00b04b3c17ee2821` on base `df4c77fd1413a65cdb85885a06978ff157c1de4d` with reviewer `quality-reviewer`.

This is **candidate readiness**, not primary-repo readiness. PR #33 was open and not merged at the review. Agent Core still reads primary repo path `/home/jean/Projects/hermes-agent-original` unless an authorized accepted-candidate metadata path or merge changes the source of truth. Therefore this index does not claim ALR-020+ may dispatch merely because a branch-local candidate now has `reviewed: yes` markers.

Historical evidence boundaries remain binding: gates 686/687 were `REQUEST_CHANGES`; gate 695 required reconciliation of the observed ALR-010-R1 direct merge into `origin/main`; R2j/R2k/R2m/R2n are provenance and handoff repairs; stale PR #20 / `dad375f27568c38be771fc597b579d087f034e1d`, historical PR #29, review-worktree `already_ancestor` metadata, PR #30, PR #31 and R2m are not active approval for this R2o marker application.

| File | Purpose | Owner | Validated | Reviewed |
|---|---|---|---|---|
| `FACTORY_INTAKE.md` | mandate, boundaries, source of truth | factory-orchestrator | yes | yes — gate 789 / PR #33 `1e82340dddf52071d14c3c7a00b04b3c17ee2821` |
| `REQUIREMENTS_ANALYSIS.md` | R1–R10/no-authority requirements | product-analyst | yes | yes — gate 789 / PR #33 `1e82340dddf52071d14c3c7a00b04b3c17ee2821` |
| `PATTERN_ANALYSIS.md` | patterns and rejected shortcuts | product-analyst | yes | yes — gate 789 / PR #33 `1e82340dddf52071d14c3c7a00b04b3c17ee2821` |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | verified inputs/unknowns | solution-architect | yes | yes — gate 789 / PR #33 `1e82340dddf52071d14c3c7a00b04b3c17ee2821` |
| `PRD.md` | outcome and release acceptance | product-analyst | yes | yes — gate 789 / PR #33 `1e82340dddf52071d14c3c7a00b04b3c17ee2821` |
| `ADRS.md` | architectural decisions | solution-architect | yes | yes — gate 789 / PR #33 `1e82340dddf52071d14c3c7a00b04b3c17ee2821` |
| `METHODOLOGY_PLAN.md` | Factory/TDD/review approach | implementation-planner | yes | yes — gate 789 / PR #33 `1e82340dddf52071d14c3c7a00b04b3c17ee2821` |
| `TECHNICAL_BLUEPRINT.md` | component placement and architecture | solution-architect | yes | yes — gate 789 / PR #33 `1e82340dddf52071d14c3c7a00b04b3c17ee2821` |
| `SPRINT_PLAN.md` | increments | implementation-planner | yes | yes — gate 789 / PR #33 `1e82340dddf52071d14c3c7a00b04b3c17ee2821` |
| `TASK_GRAPH.md` | Factory reconciliation/reviews | implementation-planner | yes | yes — gate 789 / PR #33 `1e82340dddf52071d14c3c7a00b04b3c17ee2821` |
| `TRACKER.md` | status/risk register | factory-reporter | yes | yes — gate 789 / PR #33 `1e82340dddf52071d14c3c7a00b04b3c17ee2821` |
| `DOCUMENTATION_INDEX.md` | entrypoint/status matrix | factory-orchestrator | yes | yes — gate 789 / PR #33 `1e82340dddf52071d14c3c7a00b04b3c17ee2821` |
| `QA_GATES.md` | RED/GREEN, smoke and delivery gates | qa-verifier | yes | yes — gate 789 / PR #33 `1e82340dddf52071d14c3c7a00b04b3c17ee2821` |
| `SECURITY_GATES.md` | security pass/fail evidence | security-reviewer | yes | yes — gate 789 / PR #33 `1e82340dddf52071d14c3c7a00b04b3c17ee2821` |

## Supplemental controlling artifacts

- `G0_REPOSITORY_STRATEGY.md` records Zeus-only repo scope, worktree/PR policy and the current R2o marker-application branch.
- `REQUIREMENTS_TRACEABILITY.md` maps requirements to tasks/tests/reviews.
- `DATABASE_AND_RUNTIME_CONTRACT.md` is binding for exact DB, runtime, no-egress and scheduler implementation behavior.
- `G1_REVIEW.md` records independent review findings/remediation through R2o.
- `R2J_CANONICAL_STATE_REPAIR.md` records the historical PR #29 canonical-state provenance repair and rejects review-worktree `already_ancestor` evidence as source-merge proof.
- `R2K_STALE_CANONICAL_G1_PROVENANCE_REPAIR.md` records that obsolete PR #20 / `dad375f27568c38be771fc597b579d087f034e1d` is stale historical metadata, not active review provenance.
- `R2M_CURRENT_BASE_G1_REVIEW_HANDOFF.md` records the earlier current-base handoff on `ab08b13669903a87b3d60d6c80231d23d6313782`; it is now historical.
- `R2O_RECONCILIATION_REVIEWED_MARKERS.md` records this marker application, candidate-readiness semantics and handoff requirements.

## Status semantics

- `validated: yes` means the file exists, is tracked, is indexed where required and is internally consistent with this G1 contract.
- `reviewed: yes` on the 14 required G1 files is a candidate-level machine-readable marker backed by gate 789, reviewer `quality-reviewer`, PR #33 and exact SHA `1e82340dddf52071d14c3c7a00b04b3c17ee2821`.
- Candidate readiness does not imply primary-readiness. Primary readiness is true only after Agent Core `document_status` reads zero required G1 blockers from the canonical primary source or an authorized reviewed-candidate metadata path.
- Branch-local markers, the observed ALR-010-R1 base-branch merge, stale PR #20 metadata, PR #29 historical reviews, PR #30/PR #31 exposure, and R2i review-worktree attachments never authorize normal implementation by themselves.

## Required reading order

1. `DOCUMENTATION_INDEX.md`, `FACTORY_INTAKE.md`, `G0_REPOSITORY_STRATEGY.md`
2. `REQUIREMENTS_ANALYSIS.md`, `REQUIREMENTS_TRACEABILITY.md`, `PRD.md`, `ADRS.md`
3. `DATABASE_AND_RUNTIME_CONTRACT.md`, `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`, `SPRINT_PLAN.md`
4. `QA_GATES.md`, `SECURITY_GATES.md`, `G1_REVIEW.md`, `R2K_STALE_CANONICAL_G1_PROVENANCE_REPAIR.md`, `R2M_CURRENT_BASE_G1_REVIEW_HANDOFF.md`, `R2O_RECONCILIATION_REVIEWED_MARKERS.md`

## G1 rule

No normal implementation starts from this R2o branch alone. It may start only after the reviewed candidate is accepted into the canonical Factory source path and Agent Core `document_status` or an authorized equivalent reads back no required G1 blockers. This protects against false-ready assertions while preserving the independently reviewed candidate markers.

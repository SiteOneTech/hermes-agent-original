---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: pending
owner: factory-orchestrator
---

# DOCUMENTATION INDEX — Zeus Alpha Research Ledger Core

## Controlling status
Canonical G1 pack for the **private Zeus-side implementation** succeeding `zeus-independent-alpha-research`. It is not a Vonash implementation plan, grants no external runtime access and does not authorize market execution. Every required document carries explicit `validated` and `reviewed` status metadata plus the index matrix below. The reviewer state remains `reviewed: pending` until the revised committed candidate receives new independent specification and security PASS reviews against its exact SHA. Earlier Factory gate rows are evidence only: gates 686/687 were `REQUEST_CHANGES`; gate 695 was a failed spec review requiring reconciliation of the observed ALR-010-R1 direct merge into `origin/main`; R2j/R2k are canonical provenance repairs, not approval; and any PASS on a pre-correction SHA is not reused for this revision. R2m revalidates the pack on exact current base `ab08b13669903a87b3d60d6c80231d23d6313782` and hands off a fresh candidate for independent exact-SHA review. This worker does not self-approve.

| File | Purpose | Owner | Validated | Reviewed |
|---|---|---|---|---|
| `FACTORY_INTAKE.md` | mandate, boundaries, source of truth | factory-orchestrator | yes | pending |
| `G0_REPOSITORY_STRATEGY.md` | repo/scope/worktree/PR decision | solution-architect | yes | pending |
| `REQUIREMENTS_ANALYSIS.md` | R1–R10/no-authority requirements | product-analyst | yes | pending |
| `PATTERN_ANALYSIS.md` | patterns and rejected shortcuts | product-analyst | yes | pending |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | verified inputs/unknowns | solution-architect | yes | pending |
| `PRD.md` | outcome and release acceptance | product-analyst | yes | pending |
| `ADRS.md` | architectural decisions | solution-architect | yes | pending |
| `METHODOLOGY_PLAN.md` | Factory/TDD/review approach | implementation-planner | yes | pending |
| `TECHNICAL_BLUEPRINT.md` | component placement and architecture | solution-architect | yes | pending |
| `SPRINT_PLAN.md` | increments | implementation-planner | yes | pending |
| `TASK_GRAPH.md` | Factory reconciliation/reviews | implementation-planner | yes | pending |
| `TRACKER.md` | status/risk register | factory-reporter | yes | pending |
| `QA_GATES.md` | RED/GREEN, smoke and delivery gates | qa-verifier | yes | pending |
| `SECURITY_GATES.md` | security pass/fail evidence | security-reviewer | yes | pending |
| `DOCUMENTATION_INDEX.md` | entrypoint/status matrix | factory-orchestrator | yes | pending |

## Supplemental controlling artifacts
- `REQUIREMENTS_TRACEABILITY.md` maps requirements to tasks/tests/reviews.
- `DATABASE_AND_RUNTIME_CONTRACT.md` is binding for exact DB, runtime, no-egress and scheduler implementation behavior.
- `G1_REVIEW.md` records independent review findings/remediation.
- `R2J_CANONICAL_STATE_REPAIR.md` records the historical PR #29 canonical-state provenance repair: exact PR #29 head `f61a7275048e2135b2b2729a1b9cdf8713c58866`, R2i review-worktree `already_ancestor` mismatch and the intended PR-first handoff that later became PR #30.
- `R2K_STALE_CANONICAL_G1_PROVENANCE_REPAIR.md` records the stale active provenance repair as historical control evidence. It records that Agent Core project metadata still points to obsolete PR #20 / `dad375f27568c38be771fc597b579d087f034e1d`, PR #30 carried R2j commit `c1943efb2b97b54b42bc5eabe858340d8c391116` into remote `origin/main` as `83d5ee06ba25859f047469baed223fe88e9467e3`, local primary `main` remained at `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1` during that repair, and canonical G1 `document_status` remained non-dispatchable because required docs read back as `reviewed=false` from the primary source.
- `R2M_CURRENT_BASE_G1_REVIEW_HANDOFF.md` records the current-base recovery on exact `origin/main` `ab08b13669903a87b3d60d6c80231d23d6313782`, keeps PR #20/#29/R2i/R2j/R2k evidence historical only, and binds the next valid review to the fresh R2m PR head SHA after push.

## Status semantics
- `validated: yes` means the implementation-planner/local worker confirmed the file exists, is tracked, is indexed where required, and is internally consistent with this G1 contract.
- `reviewed: pending` is an explicit reviewed-status value, not a missing field. It may become `reviewed: yes` only after independent reviewers record PASS evidence against the exact committed SHA.
- A branch-local reviewed status or the observed ALR-010-R1 base-branch merge never authorizes normal implementation by itself; exact-SHA independent reviews and reconciled delivery evidence remain required.
- Review-task integration metadata must not be used as PR visibility evidence unless its branch commit equals the candidate PR head; for R2i, the `already_ancestor` attachment names review branch commit `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c`, while the actual PR #29 candidate remains `f61a7275048e2135b2b2729a1b9cdf8713c58866` and the later R2j repair is PR #30 head `c1943efb2b97b54b42bc5eabe858340d8c391116`.
- Stale Factory project metadata that points to PR #20 / `dad375f27568c38be771fc597b579d087f034e1d` is not current review provenance and must not be used to dispatch ALR-020.

## Required reading order
1. `DOCUMENTATION_INDEX.md`, `FACTORY_INTAKE.md`, `G0_REPOSITORY_STRATEGY.md`
2. `REQUIREMENTS_ANALYSIS.md`, `REQUIREMENTS_TRACEABILITY.md`, `PRD.md`, `ADRS.md`
3. `DATABASE_AND_RUNTIME_CONTRACT.md`, `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`, `SPRINT_PLAN.md`
4. `QA_GATES.md`, `SECURITY_GATES.md`, `G1_REVIEW.md`, `R2K_STALE_CANONICAL_G1_PROVENANCE_REPAIR.md`, `R2M_CURRENT_BASE_G1_REVIEW_HANDOFF.md`

## G1 rule
No normal implementation starts until every required G1 document is `reviewed: yes`; the supplemental controlling artifacts, including R2j, R2k and R2m, must be committed and PASS-reviewed against the exact revised SHA too. Base exposure alone is not sufficient: the observed ALR-010-R1 merge, the later R2j/PR #30 merge, and the R2k/PR #31 merge are non-dispatch evidence until canonical Factory metadata and `document_status` are reconciled, and a branch-only or stale-PR pack is likewise never sufficient.

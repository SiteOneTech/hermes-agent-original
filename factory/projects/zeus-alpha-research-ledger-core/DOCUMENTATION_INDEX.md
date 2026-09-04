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
Canonical G1 pack for the **private Zeus-side implementation** succeeding `zeus-independent-alpha-research`. It is not a Vonash implementation plan, grants no external runtime access and does not authorize market execution. Every required document carries explicit `validated` and `reviewed` status metadata plus the index matrix below. The reviewer state remains `reviewed: pending` until the revised committed candidate receives new independent specification and security PASS reviews against its exact SHA. Earlier Factory gate rows are evidence only: gates 686/687 were `REQUEST_CHANGES`; gate 695 was a failed spec review requiring reconciliation of the observed ALR-010-R1 direct merge into `origin/main`; and any PASS on a pre-correction SHA is not reused for this revision. This worker does not self-approve.

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
- `R2F6_REPAIR_G1_DOCS_RECOVERY_PREFLIGHT.md` records the bounded Factory control-plane repair evidence for the G1/docs recovery candidate preflight classifier.

## Status semantics
- `validated: yes` means the implementation-planner/local worker confirmed the file exists, is tracked, is indexed where required, and is internally consistent with this G1 contract.
- `reviewed: pending` is an explicit reviewed-status value, not a missing field. It may become `reviewed: yes` only after independent reviewers record PASS evidence against the exact committed SHA.
- A branch-local reviewed status or the observed ALR-010-R1 base-branch merge never authorizes normal implementation by itself; exact-SHA independent reviews and reconciled delivery evidence remain required.

## Required reading order
1. `DOCUMENTATION_INDEX.md`, `FACTORY_INTAKE.md`, `G0_REPOSITORY_STRATEGY.md`
2. `REQUIREMENTS_ANALYSIS.md`, `REQUIREMENTS_TRACEABILITY.md`, `PRD.md`, `ADRS.md`
3. `DATABASE_AND_RUNTIME_CONTRACT.md`, `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`, `SPRINT_PLAN.md`
4. `QA_GATES.md`, `SECURITY_GATES.md`, `G1_REVIEW.md`

## G1 rule
No normal implementation starts until every required G1 document is `reviewed: yes`; the three supplemental controlling artifacts must be committed and PASS-reviewed against the exact revised SHA too. Base exposure alone is not sufficient: the observed ALR-010-R1 merge is non-approval evidence until gate-695 reconciliation is independently accepted, and a branch-only pack is likewise never sufficient.

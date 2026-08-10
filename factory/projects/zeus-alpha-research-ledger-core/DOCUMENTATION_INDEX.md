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
This is the canonical G1 documentary pack for the **private Zeus-side implementation** succeeding `zeus-independent-alpha-research`. It is not a Vonash implementation plan, grants no external runtime access and does not authorize market execution. The pack is under remediation after two independent reviews; `reviewed: pending` remains authoritative until the second pass returns PASS.

| File | Purpose | Owner | Validated | Reviewed |
|---|---|---|---|---|
| `FACTORY_INTAKE.md` | owner mandate, boundaries and source of truth | factory-orchestrator | yes | pending |
| `G0_REPOSITORY_STRATEGY.md` | repo/scope/worktree/PR decision | solution-architect | yes | pending |
| `REQUIREMENTS_ANALYSIS.md` | functional/non-functional/no-execution requirements | product-analyst | yes | pending |
| `PATTERN_ANALYSIS.md` | reusable patterns and rejected shortcuts | product-analyst | yes | pending |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | verified inputs and unknowns | solution-architect | yes | pending |
| `PRD.md` | product outcome and release acceptance | product-analyst | yes | pending |
| `ADRS.md` | architectural decisions | solution-architect | yes | pending |
| `METHODOLOGY_PLAN.md` | Factory/TDD/review delivery approach | implementation-planner | yes | pending |
| `TECHNICAL_BLUEPRINT.md` | entities, boundaries, wiring and toolset | solution-architect | yes | pending |
| `SPRINT_PLAN.md` | implementation increments | implementation-planner | yes | pending |
| `TASK_GRAPH.md` | Factory DB reconciliation, branches/worktrees and reviews | implementation-planner | yes | pending |
| `TRACKER.md` | live status and risk register | factory-reporter | yes | pending |
| `QA_GATES.md` | documentary, test, smoke and delivery gates | qa-verifier | yes | pending |
| `SECURITY_GATES.md` | privilege/data/prohibited-surface gates | security-reviewer | yes | pending |
| `DOCUMENTATION_INDEX.md` | this entrypoint and status matrix | factory-orchestrator | yes | pending |

## Supplemental controlling artifacts
- `REQUIREMENTS_TRACEABILITY.md` maps R1–R10 and boundaries to tasks, RED/GREEN proof, independent evidence and gates.
- `G1_REVIEW.md` records independent review findings and their remediation.

## Required reading order
1. `DOCUMENTATION_INDEX.md`, `FACTORY_INTAKE.md` and `G0_REPOSITORY_STRATEGY.md`
2. `REQUIREMENTS_ANALYSIS.md`, `REQUIREMENTS_TRACEABILITY.md`, `PRD.md`, `ADRS.md`
3. `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`, `SPRINT_PLAN.md`
4. `QA_GATES.md`, `SECURITY_GATES.md`, `G1_REVIEW.md`

## G1 rule
No normal implementation task starts until every required G1 document has `reviewed: yes`, is committed, and the canonical base branch exposes the pack to Factory document-status checks. Supplemental review/traceability artifacts must also be committed and PASS-reviewed. A branch-only pack is never sufficient.

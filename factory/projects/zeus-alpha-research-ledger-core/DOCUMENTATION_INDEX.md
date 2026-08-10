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
Canonical G1 pack for the **private Zeus-side implementation** succeeding `zeus-independent-alpha-research`. It is not a Vonash implementation plan, grants no external runtime access and does not authorize market execution. The pack remains `reviewed: pending` until a revised committed candidate receives new independent specification and security reviews against its exact SHA; no current review is PASS.

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

## Required reading order
1. `DOCUMENTATION_INDEX.md`, `FACTORY_INTAKE.md`, `G0_REPOSITORY_STRATEGY.md`
2. `REQUIREMENTS_ANALYSIS.md`, `REQUIREMENTS_TRACEABILITY.md`, `PRD.md`, `ADRS.md`
3. `DATABASE_AND_RUNTIME_CONTRACT.md`, `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`, `SPRINT_PLAN.md`
4. `QA_GATES.md`, `SECURITY_GATES.md`, `G1_REVIEW.md`

## G1 rule
No normal implementation starts until every required G1 document is `reviewed: yes`, committed and exposed on canonical base; the three supplemental controlling artifacts must be committed and PASS-reviewed too. A branch-only pack is never sufficient.

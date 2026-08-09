---
project_id: zeus-independent-alpha-research
status: planning
validated: yes
reviewed: yes
owner: factory-orchestrator
---

# Documentation Index

## Controlling status
This directory is the canonical G1 documentary pack for `zeus-independent-alpha-research`. All listed G1 documents were validated for required content and reviewed for internal consistency in this planning increment. Future implementation must update them as audit facts replace explicit unknowns.

| File | Purpose | Owner | Validated | Reviewed |
|---|---|---|---|---|
| `FACTORY_INTAKE.md` | objective, authority, scope and source of truth | zeus | yes | yes |
| `REQUIREMENTS_ANALYSIS.md` | behavior, message contract and outcomes | product-analyst | yes | yes |
| `PATTERN_ANALYSIS.md` | reusable design patterns and anti-patterns | product-analyst | yes | yes |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | verified facts, decisions and audit unknowns | solution-architect | yes | yes |
| `PRD.md` | product requirements and acceptance | product-analyst | yes | yes |
| `ADRS.md` | architectural decisions and rationale | solution-architect | yes | yes |
| `METHODOLOGY_PLAN.md` | Factory delivery approach and stop conditions | implementation-planner | yes | yes |
| `TECHNICAL_BLUEPRINT.md` | logical components, ownership and envelope | solution-architect | yes | yes |
| `SPRINT_PLAN.md` | ordered implementation increments | implementation-planner | yes | yes |
| `TASK_GRAPH.md` | task ownership/dependencies/reviewers | implementation-planner | yes | yes |
| `TRACKER.md` | current state and decisions | factory-reporter | yes | yes |
| `QA_GATES.md` | quality/pilot/release proof | qa-verifier | yes | yes |
| `SECURITY_GATES.md` | least privilege and prohibited-surface proof | security-reviewer | yes | yes |
| `VONASH_IMPLEMENTATION_HANDOFF.md` | executable brief for the internal Vonash team | zeus | yes | yes |
| `DOCUMENTATION_INDEX.md` | index and G1 validation/review matrix | factory-orchestrator | yes | yes |

## Related concise references
`docs/market-research-core/` remains a concise product reference area. It must not override this project pack or retain contradictory session/transport rules.

## Documentation update trigger
When I1 verifies repository/service/data facts, update the specific document and record the evidence; do not silently replace an `audit-required` marker with a guess.

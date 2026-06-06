# Sprint / Increment Plan

## Scope model

This is one complete target architecture delivered in execution increments; it is not MVP/V2/V3.

## Increments

| Increment | Task | Owner | Reviewer | Exit gate |
|---|---|---|---|---|
| 0 | F0 kickoff/tracker/skill assignment | factory-reporter | product-analyst | Intake gate |
| 1 | F1 functional PRD | product-analyst | solution-architect | Functional gate |
| 2 | F2 architecture ADR/data model | solution-architect | security-reviewer | Architecture gate |
| 3 | F3 implementation plan/task graph | implementation-planner | factory-orchestrator | Planning gate |
| 4 | F4 DB migrations/runtime grants | claude-builder | codex-builder | Implementation partial |
| 5 | F5 tools/toolset | claude-builder | quality-reviewer | Implementation partial |
| 6 | F6 calendar bridge/dispatcher | claude-builder | devops-release | Implementation partial |
| 7 | F7 plans/chaining/quick capture | claude-builder | product-analyst | Implementation partial |
| 8 | F8 CRM compatibility/no duplicates | codex-builder | claude-builder | Implementation gate |
| 9 | F9 QA regression/smoke | qa-verifier | quality-reviewer | Quality/test gate |
| 10 | F10 security/privacy/tool boundary | security-reviewer | solution-architect | Security gate |
| 11 | F11 delivery docs/reconciliation | factory-reporter | devops-release | Delivery gate |

## Sequential execution rule

Do not start the next increment while the current task is `running`, `review_ready`, `review_running`, `rework`, or otherwise active. Reviewer rework must be resolved before continuing.

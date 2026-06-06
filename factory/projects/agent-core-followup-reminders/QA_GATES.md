# QA Gates — Agent Core Follow-up / Reminders

## Gate policy

QA claims require actual commands/output. F0 only verifies kickoff integrity; functional/implementation QA belongs to F1-F11.

## Gates

| Gate | Owner | Required proof | Current status |
|---|---|---|---|
| Artifact integrity | factory-reporter/product-analyst | Project-local files reference `agent-core-followup-reminders` only | ready for re-review |
| Skill availability | factory-reporter/product-analyst | `SKILL.md` present in relevant worker profiles | ready for verification |
| Factory DB canonicality | factory-orchestrator | `hermes factory status ... --json` reports `agent_core_postgres` | verified before correction |
| Functional criteria | product-analyst/solution-architect | PRD with concrete acceptance criteria | pending F1 |
| Migration/tool tests | builders/reviewers | pytest/direct handler output | pending F4-F8 |
| Live smoke | qa-verifier/quality-reviewer | synthetic activity lifecycle readback | pending F9 |
| Security tool boundary | security-reviewer/solution-architect | resolved toolset inspection + negative tests | pending F10 |
| Delivery reconciliation | factory-reporter/devops-release | DB/repo/docs/report agree | pending F11 |

## Hard-stop failures

- Artifact mentions unrelated project IDs or customer-service runtime.
- Skill is not loadable in assigned worker/reviewer profiles.
- Runtime falls back to SQLite for Factory state.
- Implementer self-approves or reviewer relies only on implementer prose.

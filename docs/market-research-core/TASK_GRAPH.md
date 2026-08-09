# Task Graph — Zeus Independent Alpha Research

| ID | Increment | Owner | Dependency | Deliverable / acceptance |
|---|---|---|---|---|
| ZA-000 | I0 Intake | Zeus / Product Analyst | — | PRD, ADR, sprint plan, task graph, QA gates, documentation index committed |
| ZA-010 | I1 Schema design | Solution Architect | ZA-000 | Table/role design reviewed; no Vonash table dependency |
| ZA-011 | I1 Migration + registry | Claude Builder | ZA-010 | `market_research` migration applies and rolls forward cleanly |
| ZA-012 | I1 DB security review | Security Reviewer | ZA-011 | Least-privilege grants and no execution scope verified |
| ZA-013 | I1 Capability-request design | Solution Architect | ZA-010 | Requirement lifecycle, ownership, and non-implementation boundary reviewed |
| ZA-020 | I2 Evidence tools | Claude Builder | ZA-012, ZA-013 | Source/evidence create/search tools with provenance tests |
| ZA-021 | I2 Alpha Card tools | Claude Builder | ZA-020 | Cards, lineage, reviews, state transitions, novelty checks |
| ZA-023 | I2 Capability-request tool | Claude Builder | ZA-021 | Linked capability requirements with no Vonash write/deploy surface |
| ZA-022 | I2 Tool QA | Codex Builder | ZA-021, ZA-023 | Negative and regression tests pass |
| ZA-030 | I3 Cycle service | Claude Builder | ZA-022, ZA-023 | Daily-cycle storage/report logic and dry-run command |
| ZA-031 | I3 Scheduler guard | DevOps Release | ZA-030 | Disabled-by-default job; no activation before explicit gate |
| ZA-040 | I4 Adapter contract | Solution Architect | ZA-022 | Read-only KB + bounded-session interface specification |
| ZA-041 | I4 Magnus adapter | Claude Builder | ZA-040 | Feature-flagged adapter, authentication, audit, timeout/turn enforcement |
| ZA-042 | I4 Adapter security | Security Reviewer | ZA-041 | Scope, redaction, outbound type allowlist verified |
| ZA-050 | I5 Scorecards | Claude Builder | ZA-021 | Source-family comparable-result views and tests |
| ZA-060 | I6 Pilot / QA | QA Verifier | ZA-031, ZA-042, ZA-050 | Manual research cycle and bounded dialogue evidence; no live action |
| ZA-999 | Delivery | Factory Orchestrator | all | Final docs, test evidence, policy confirmation, handoff |

## Non-negotiable dependencies

- No scheduler before storage/tool tests pass.
- No Magnus connector before Jean selects the transport, an explicit access method, source scope, and service identity are provided.
- No capability request becomes a code/deployment action without Jean/backend planning ownership.
- No strategy ranking based on P&L alone; comparability metadata is mandatory.
- No execution capability in any Zeus Alpha Research tool.

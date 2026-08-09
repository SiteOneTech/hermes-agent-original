---
project_id: zeus-independent-alpha-research
status: planning
validated: yes
reviewed: yes
owner: implementation-planner
---

# Task Graph

| ID | Phase | Owner | Reviewer | Depends on | Acceptance summary |
|---|---|---|---|---|---|
| ZA-000 | planning | Zeus / implementation-planner | product-analyst | — | Canonical G1 plan + Vonash handoff reconciled |
| ZA-010 | discovery | solution-architect | quality-reviewer | ZA-000 | Read-only Vonash capability/audit matrix with real contracts |
| ZA-011 | security-design | security-reviewer | solution-architect | ZA-010 | Identity, auth scope, data classification and retention plan |
| ZA-020 | architecture | solution-architect | security-reviewer | ZA-010, ZA-011 | Exact typed API/thread/outbox/ack contract and migration plan |
| ZA-021 | planning | implementation-planner | factory-orchestrator | ZA-020 | Repo-specific implementation plan, branches and acceptance criteria |
| ZA-030 | implementation | Vonash backend team | quality-reviewer | ZA-021 | Owning research exchange + outbox/ack, no cross-DB write |
| ZA-031 | implementation | Zeus builder | security-reviewer | ZA-021 | Zeus advisory ledger/lifecycle, research-only tool boundary |
| ZA-040 | implementation | Vonash backend team | qa-verifier | ZA-030, ZA-031 | Typed collaboration, capability/result-reference flow |
| ZA-041 | implementation | Vonash backend team | security-reviewer | ZA-040 | Telegram mirror/notification adapter, no canonical dependence |
| ZA-050 | implementation | Vonash backend team | qa-verifier | ZA-040 | Reactive alert intake/routing, no execution command surface |
| ZA-060 | quality_review | quality-reviewer | security-reviewer | ZA-041, ZA-050 | Contract/diff/test review and rework list |
| ZA-061 | security_review | security-reviewer | factory-orchestrator | ZA-060 | Auth, egress, logging, privilege and prohibited-surface proof |
| ZA-070 | qa | qa-verifier | quality-reviewer | ZA-061 | End-to-end manual and synthetic paper-safe tests |
| ZA-080 | release | devops-release | qa-verifier | ZA-070 | Deploy/runbook/rollback/source-health readiness; no live activation |
| ZA-090 | delivery | factory-reporter | factory-orchestrator | ZA-080 | Exact evidence, known gaps and internal handoff |

## Mandatory constraints
- All exact files/routes/migrations are filled after ZA-010, never guessed here.
- Zeus cannot approve its own implementation/release.
- A missing evaluator/feed becomes a linked capability request, not an undocumented implementation detour.
- ZA-080 cannot treat an integration or paper-safe test as permission to trade live.

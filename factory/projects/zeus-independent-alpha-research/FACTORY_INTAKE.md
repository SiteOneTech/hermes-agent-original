---
project_id: zeus-independent-alpha-research
status: planning
validated: yes
reviewed: yes
owner: zeus
---

# Factory Intake — Zeus Independent Alpha Research

## Business objective
Create the planning and handoff package for an independent Zeus research function that generates, challenges, and archives market hypotheses for Vonash. The objective is better evidence, diversity, and decision quality—not a promise of profit and not an execution system.

## Correction that governs this project
Magnus is **Vonash’s real-time runtime CEO/operator**, not a programming worker. Zeus is an independent research advisor. The Factory builds the collaboration capability; once released, Magnus operates it inside Vonash while Zeus contributes research through the defined contract.

## Authority split
| Actor | Owns | Does not own |
|---|---|---|
| Zeus | sources, evidence, Alpha Cards, red-team reviews, capability requirements, research alerts | orders, risk limits, paper/live state, promotion, Vonash code or deployment |
| Magnus | runtime capability statements, experiment coordination, operational response under existing Vonash policy, result references | Zeus ledger, cross-system protocol changes, automatic promotion from a Zeus message |
| Jean | priorities, source/connector approval, engineering and release priority | — |
| Vonash internal team | audited implementation, migrations, services, deployment and verification | research governance unless separately assigned |

## Scope of this Factory increment
This increment is **planning and documentary reconciliation only**. It creates the controlling G1 package and an implementation handoff. It does not modify Vonash, create a connector, enable a cron, create credentials, deploy, or activate paper/live trading.

## Canonical source of truth
- Factory operational truth: Agent Core Postgres Factory records.
- Controlling project documents: `factory/projects/zeus-independent-alpha-research/`.
- Zeus-side product references: `docs/market-research-core/`.
- Future Vonash implementation: its own repository and runtime after a read-only capability audit.

## Required discovery before implementation
The Vonash audit must establish the actual repository/service ownership, API contracts, service identity/auth model, evaluator and experiment interfaces, data granularity/retention, current scheduler, and deployment path. No document in this package invents those details.

## Explicit exclusions
No direct database writes across Zeus/Vonash; no broker/execution/risk message type; no hidden secrets; no production promotion requirement; and no reuse of a retired scheduler merely because a database row exists.

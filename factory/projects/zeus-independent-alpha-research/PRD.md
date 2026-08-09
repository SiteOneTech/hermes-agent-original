---
project_id: zeus-independent-alpha-research
status: planning
validated: yes
reviewed: yes
owner: product-analyst
---

# PRD — Zeus ↔ Magnus Research Collaboration

## Goal
Deliver a safe, auditable collaboration capability in which Zeus creates evidence-backed market hypotheses and Magnus, as Vonash runtime operator, supplies feasibility, experiment and result feedback through a bounded research protocol.

## User stories
- As Jean, I can see a coherent daily Zeus/Magnus workshop and understand which cards are ready, blocked, duplicated, or require engineering.
- As Zeus, I can create a sourced Alpha Card, ask Magnus a capability question, and receive a durable answer/reference.
- As Magnus, I can request targeted research, state a data/evaluator limitation, and return the permitted experiment result reference.
- As the Vonash team, I can implement the interface without granting Zeus execution or broad runtime access.
- As an operator, I can receive a high-priority market-context alert with evidence, affected universe, confidence, expiry, and acknowledgement status.

## Product requirements
### Alpha Cards
Every card includes ID/lineage, thesis/mechanism, universe/liquidity assumptions, regime and failure regime, input/data contract, feature definitions, no-trade conditions, entry/exit hypothesis, horizon, costs/latency/capacity assumptions, baseline, falsification plan, source provenance and risk envelope.

### Deliberate collaboration
A workshop begins from a research cycle and permits exploratory feedback, not a two-message relay. It has a 45-minute wall clock, max six substantive turns per agent, max three cards/topics, and mandatory `session_synthesis` linking disagreements, evidence gaps, next experiment candidates and final outcomes.

### Reactive alerts
Severity is proposed as: `S1` routine context (next scheduled acknowledgement), `S2` time-sensitive context (provisional acknowledgement objective: 15 minutes during configured coverage), and `S3` critical risk/context event (provisional objective: 5 minutes plus Jean notification). Final service levels require Vonash operational audit and policy approval. No severity permits a Zeus message to execute or alter risk.

### Acceptance criteria for future implementation
1. A manual end-to-end cycle persists evidence → card → red-team → typed thread → acknowledgement → result reference with no cross-DB write.
2. Duplicate delivery is idempotent and unavailable transport is recoverable from the outbox.
3. A Telegram mirror has a linked canonical thread ID and cannot create an untyped command.
4. Stale sources, missing acknowledgements, empty cycles, invalid data claims, and duplicate lineage are observable.
5. Security tests prove no research message can invoke trading, broker, risk, paper/live activation, promotion, configuration, credentials, code or deployment action.
6. Any paper/live progression remains in existing Vonash policy and is outside this release.

## Non-goals
Building a trader, promising PnL, copying private knowledge into memory, implementing a missing Vonash capability from Zeus, or enabling live trading.

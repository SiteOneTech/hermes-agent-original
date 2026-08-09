---
project_id: zeus-independent-alpha-research
status: planning
validated: yes
reviewed: yes
owner: solution-architect
---

# Architecture Decision Records

## ADR-001 — Two ledgers, no cross-database writes
**Decision:** Zeus Agent Core Postgres owns advisory provenance, cycles, Alpha Cards and reviews. Vonash owns Magnus/runtime thread, experiment, and promotion records. They exchange stable external references through services.

**Why:** preserves attribution, fault isolation, access control and independent lifecycle ownership. A shared table or direct SQL coupling would entangle the Vonash refactor with Zeus research.

## ADR-002 — Typed service-owned thread and durable outbox
**Decision:** Collaboration is a typed research-thread API backed by durable message/outbox/acknowledgement state. A directive or report record alone is only a bootstrap artifact, not the production channel.

**Why:** messages need delivery state, idempotency, retry, expiry, acknowledgement and auditability. Endpoint/service names are audit-required.

## ADR-003 — Telegram as a mirror, never the ledger
**Decision:** A three-person Telegram conversation may deliver/mirror the daily workshop and urgent notifications, but every substantive message resolves to a canonical thread/message ID and the API record is authoritative.

**Why:** chat transports can fail, be edited, lack retention controls, or be unavailable to a runtime. The research protocol must survive them.

## ADR-004 — Allowlisted research-only authority
**Decision:** The protocol permits only research, capability and result-reference message types. It has no order, portfolio, risk, model-promotion, config, code, credential or deployment operation.

**Why:** a persuasive natural-language message cannot become a privilege escalation. Magnus’s own existing policies remain the only route to permitted runtime operations.

## ADR-005 — Separate daily workshop from reactive alerts
**Decision:** Deliberate brainstorming is finite and reflective; alerts are asynchronous, evidence-backed and acknowledgement-driven. Both create typed records but have different delivery and time policies.

**Why:** event urgency should not bypass evaluation discipline, while daily research should retain enough turn budget for meaningful creative disagreement.

## ADR-006 — Evidence before a market claim
**Decision:** every card/event includes source provenance, retrieval timestamp, regime/context, confidence and falsification/data contract. Bars are not labeled footprint/order flow absent granular trade/quote evidence.

**Why:** avoids overclaiming and makes subsequent experiment results interpretable.

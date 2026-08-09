---
project_id: zeus-independent-alpha-research
status: planning
validated: yes
reviewed: yes
owner: product-analyst
---

# Pattern Analysis

## Product patterns to adopt

### Independent-advisor pattern
A second source of hypotheses should improve diversity, not become a competing trading platform. Zeus owns research provenance and skepticism; Magnus/Vonash owns feasibility, evaluation, and operational policy.

### Outbox + acknowledgement pattern
A report/directive table alone is not a conversation. The implementation must use a service-owned typed thread, durable outbox, consumer acknowledgement, idempotency key, retry policy, and explicit failure state. This supports reliable asynchronous collaboration without cross-database writes.

### Two-ledger pattern
The Zeus ledger is authoritative for Zeus-generated evidence and Alpha Cards. Vonash is authoritative for its runtime interaction, experiment, and promotion records. Shared objects use immutable external references rather than duplicated mutable state.

### Human-visible transport pattern
Telegram is useful for a joint working room with Jean, Zeus, and Magnus. It is a transport/mirror: messages are first persisted or durably queued in the typed exchange and then rendered into the group with the canonical thread reference.

### Research lifecycle pattern
Evidence → independent synthesis → Alpha Card → red-team → capability confirmation → experiment proposal → immutable result reference → retrospective. A result reference is not a command to promote; Vonash’s normal simulation/paper/live gates remain controlling.

## Research-family diversity
Maintain distinct mechanism families: microstructure/pattern memory; regime/state transitions; cross-asset/forced flows; dispersion/reversion where costs allow; event/tactical research; practitioner/manual seeds; and anti-alpha/no-trade conditions. Lineage must identify renamed variants of an existing mechanism.

## Data-contract rule: footprint is not bars
A true footprint/order-flow hypothesis requires documented timestamp-aligned trade/quote or bid/ask/aggressor data, price-level volume, and, if claimed, depth/book data. OHLCV bars can support only a proxy. A card without the required data contract is `blocked_by_data`, not “confirmed.”

## Anti-patterns rejected
Unbounded agent chat; raw Telegram as truth; direct DB coupling; stale source treated as current; opaque third-party signal mirrored as strategy; automatic promotion; and a legacy scheduler re-enabled without source-controlled runtime proof.

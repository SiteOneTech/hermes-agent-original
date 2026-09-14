# Zeus Market Research — Operating Model

**Status:** Current concise product reference. The controlling Factory specification is [`factory/projects/zeus-independent-alpha-research/`](../../factory/projects/zeus-independent-alpha-research/).

## Roles
- **Zeus** is Vonash’s independent strategy-research advisor: evidence, Alpha Cards, skeptical reviews, capability requirements and research retrospectives.
- **Magnus** is the real-time Vonash runtime CEO/operator: actual platform feasibility, permitted experiment coordination and result references under Vonash’s existing policies.
- **Jean** owns priorities, approved sources/connectors and internal delivery priority.

Zeus does not place orders, change risk, activate paper/live, promote a strategy, edit Vonash, deploy code or alter its configuration. A `research_ready` result is eligible only for separately governed evaluation planning.

## Operating loop
```text
approved source/event intake → Zeus evidence and Alpha Card → red-team
→ typed Zeus↔Magnus research thread → capability/experiment feedback
→ result reference → retrospective
```

The cross-system record is a typed, service-owned thread/API with durable outbox and acknowledgement. Zeus and Vonash keep their own ledgers and exchange immutable references; neither writes directly to the other database. A Telegram group may mirror the conversation for Jean/Zeus/Magnus, but it is not the record of truth.

## Collaboration modes
- **Daily workshop:** 45 minutes; up to six substantive turns per agent; maximum three cards/topics; mandatory typed synthesis and outcome.
- **Reactive alert:** evidence-backed `research_alert` for time-sensitive market/data context. It asks for acknowledgement/review and may notify Jean; it never commands a trade or risk change.

Read the canonical PRD, technical blueprint, QA/security gates and internal engineering handoff in the Factory project directory for the message allowlist, data contract, alert severity and release gates.

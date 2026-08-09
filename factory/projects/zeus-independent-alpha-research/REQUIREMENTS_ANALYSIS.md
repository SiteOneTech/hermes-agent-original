---
project_id: zeus-independent-alpha-research
status: planning
validated: yes
reviewed: yes
owner: product-analyst
---

# Requirements Analysis

## Desired post-Factory behavior
Zeus continuously researches approved evidence sources and creates falsifiable Alpha Cards. Magnus can ask Zeus for research, state what Vonash can actually measure/test, return experiment references, and receive time-sensitive research alerts. Their collaboration is durable, attributable, and bounded; it is not an unlogged chat and it never becomes a trading command channel.

## Functional requirements
1. **Advisory ledger:** Zeus records source provenance, evidence events, Alpha Cards, lineage, red-team reviews, research cycles, and capability requests in its own Postgres module.
2. **Runtime exchange:** Vonash owns a typed thread/message record for interactions involving Magnus and its experiment lifecycle. The two systems exchange IDs/references through a service API; neither writes to the other database.
3. **Typed protocol:** only these message intents are permitted: `research_hypothesis`, `research_question`, `capability_query`, `capability_response`, `experiment_proposal`, `experiment_result_reference`, `research_alert`, `acknowledgement`, and `session_synthesis`.
4. **Daily workshop:** a 45-minute deliberate session supports up to six substantive turns per agent and no more than three cards/topics. It closes with a typed synthesis and a reasoned outcome.
5. **Reactive lane:** approved scheduled/event-driven watchers may create evidence-backed research alerts for macro, geopolitical, market-structure, data-quality, or model-drift context. An alert asks for acknowledgement/review; it never commands a trade or risk change.
6. **Capability gaps:** when data/evaluators/simulation behavior are absent, Zeus opens a structured requirement for Jean/internal planning—not a code job that Zeus executes.
7. **Telegram transport:** a three-person Telegram group may mirror notifications and conversation for visibility. Each substantive item must carry a thread ID and be persisted through the typed exchange; Telegram is not the record of truth.

## Required message attributes
`message_id`, `thread_id`, `research_cycle_id`, `alpha_card_id`/evidence references, author, recipient, authority scope, priority, created/expiry time, idempotency key, `requires_response`, acknowledgement/deadline, redaction classification, and immutable audit metadata.

## Outcomes for a card/session
`research_ready`, `research_ready_with_conditions`, `blocked_by_data`, `blocked_by_method`, `duplicate_or_lineage_merge`, `deferred`, or `rejected`. `research_ready` means eligible for separately governed evaluation planning only.

## Non-functional requirements
Auditable delivery; deterministic idempotency; retries without duplicate messages; fail-closed auth; source freshness/health tracking; no secret logging; status visibility; retention/license attribution; and recovery from unavailable transport without losing the canonical record.

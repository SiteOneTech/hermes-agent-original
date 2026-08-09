---
project_id: zeus-independent-alpha-research
status: planning
validated: yes
reviewed: yes
owner: solution-architect
---

# Technical Blueprint

## Logical components
```text
Approved sources / KB / market-event feeds
        ↓  (provenance + freshness + license)
Zeus Research Advisor
  Zeus Postgres: cycles, evidence, Alpha Cards, lineage, reviews,
  capability requests, advisory-side handoff references
        ↓  scoped typed API, durable outbox, idempotency
Vonash Research Exchange
  Vonash thread/messages, acknowledgement, capability/result references
        ↓
Magnus Runtime CEO → existing Vonash evaluation/paper/live governance
        ↓
Optional Telegram mirror for Jean + Zeus + Magnus
```

## Ownership model
Zeus’s service owns Zeus records. The Vonash exchange service owns its messages and runtime references. Cross-system relations use `external_system`, `external_id`, version/hash and reference URLs/IDs as applicable; no service has direct SQL credentials to the other ledger.

## Conceptual entities
### Zeus side
`research_program`, `research_cycle`, `source_registry`, `evidence_event`, `alpha_card`, `hypothesis_lineage`, `research_review`, `capability_request`, `advisory_handoff`.

### Vonash side (exact names audit-required)
`research_thread`, `research_message`, `message_acknowledgement`, `outbox_delivery`, `capability_statement`, `experiment_reference`, `alert_receipt`.

## Message envelope
```json
{
  "schema_version": "1",
  "message_id": "uuid",
  "idempotency_key": "opaque-stable-key",
  "thread_id": "owner-thread-id",
  "research_cycle_ref": "external-reference",
  "alpha_card_refs": ["external-reference"],
  "evidence_refs": ["external-reference"],
  "message_type": "research_hypothesis",
  "authority_scope": "research_only",
  "priority": "routine|time_sensitive|critical",
  "requires_response": true,
  "ack_due_at": "timestamp",
  "expires_at": "timestamp",
  "redaction_class": "research_internal",
  "payload": {},
  "created_at": "timestamp"
}
```
The concrete schema, validation library, endpoints and principal names are implementation-audit outcomes.

## Alert behavior
A `research_alert` contains evidence, affected universe, detected condition, expected relevance, uncertainty, data freshness, expiry and requested research/operational review. `S1/S2/S3` route notification urgency only. The receiving runtime must validate message type/scope before any response. Unsupported or expired messages are retained with rejection reason; retries must preserve idempotency.

## Observability
Track source freshness, ingest failures, sent/acknowledged/expired messages, mirror failures, duplicate suppression, empty cycles, card lineage collisions, alert severity, and result-reference latency. Redact secrets, credentials and restricted source payloads from all logs and Telegram output.

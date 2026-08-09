---
project_id: zeus-independent-alpha-research
status: planning
validated: yes
reviewed: yes
owner: qa-verifier
---

# QA Gates

## I0 documentary gate
- Required G1 files exist under the exact project path and are indexed.
- Authority boundaries, selected typed exchange, daily workshop and reactive alert rules are consistent across docs.
- No document claims an unverified Vonash endpoint/data/evaluator/runtime capability.
- Older concise references contain no incorrect two-turn cap or “transport deliberately deferred” contradiction.

## I1/I2 discovery and contract gates
- Read-only audit reports actual repo/branch/service/data and source health with evidence.
- API/schema/auth contracts map each request to a named owning service after audit.
- Data requirements distinguish actual footprint/order flow from bar proxies.

## Implementation gates
- Unit/integration tests cover message-type validation, invalid authority scope, idempotency, expired message, retries, acknowledgement, mirror failure and data redaction.
- A duplicate delivery has exactly one logical message/thread outcome.
- A failed transport retries from durable outbox without losing the record.
- A Telegram post carries a canonical reference and cannot become a command.

## Pilot and release gates
- Manual proof creates evidence → Alpha Card → review → typed thread → acknowledgement → experiment result reference.
- Synthetic alert proof uses fixtures, sends no external trade/risk operation and records `external_execution=false` evidence.
- Source freshness, missing acknowledgement, empty cycle and duplicate lineage alerts are observable.
- QA reviews the exact deployed revision and confirms no `order`, `risk`, `paper_live`, `promotion`, `config`, `credential`, `code` or `deploy` message type exists.
- Any actual paper/live promotion remains a separately governed Vonash decision and cannot be treated as a QA completion result.

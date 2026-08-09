---
project_id: zeus-independent-alpha-research
status: planning
validated: yes
reviewed: yes
owner: security-reviewer
---

# Security Gates

## Identity and access
- Zeus and Vonash use separate service identities with minimal API scopes; neither receives direct database access to the other system.
- Research exchange permissions are constrained to typed research resources. There is no fallback to a general admin/runtime role.
- Secrets are stored and injected through the approved vault/deployment path; no secret appears in Git, Factory evidence, logs, cards, Telegram or prompts.

## Message safety
- Schema/type validation happens before delivery and before any consuming action.
- Unknown, malformed, expired, duplicate or scope-violating messages fail closed and retain only safe rejection metadata.
- The allowlist excludes orders, broker control, portfolio/risk changes, paper/live activation, promotion, arbitrary webhooks, configuration, code, credentials and deployment.
- Idempotency keys and signature/auth verification prevent replay and impersonation.

## Data protection
- Source provenance stores minimum permissible excerpts/metadata and license/terms; no bulk private KB export to memory.
- Telegram mirror payloads are redacted and link to the canonical thread instead of carrying sensitive source payloads.
- Logs/metrics use redaction and do not expose authorization headers, raw credentials, private customer data or restricted vendor content.

## Operational resilience
- Outbox retries are bounded and observable; no acknowledgement triggers a generic escalation loop.
- Transport outage cannot erase the canonical thread; messages become retryable/expired with evidence.
- Emergency alert routing is advisory only. The receiving system’s existing authenticated policy path—not an alert text—governs any operational response.

## Security release evidence
Threat model, scope test, negative API authorization tests, static secret scan, dependency review, transport/webhook verification, log-redaction proof and rollback/runbook review must pass before a production release of the integration.

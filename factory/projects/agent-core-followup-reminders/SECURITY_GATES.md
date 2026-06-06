# Security Gates — Agent Core Follow-up / Reminders

## Preliminary risk areas

1. PII in personal/commercial relationship memory.
2. Private notes and sensitive relationship metadata.
3. Calendar side effects: meetings, blocks, reschedules and cancellations.
4. Notifications/reminders sent to external people/channels.
5. Customer-facing personas must not gain privileged owner tools.
6. Natural-language capture must avoid unintended irreversible side effects.

## Required F10 checks

- Inspect resolved toolsets for relevant profiles; do not trust intended allowlists only.
- Verify reminders/notifications have audit events and idempotency keys.
- Verify calendar writes are explicit and traceable.
- Verify no raw SQL/admin tools leak into customer-facing contexts.
- Verify duplicate-prevention avoids spam follow-ups.
- Verify PII fields and metadata are scoped to Agent Core DB and not external docs by default.

## Current state

F0/F1/F2 are planning/review stages. No production side-effecting code should be considered approved until F10 passes.

## Gate result: F10 security/privacy/tool-boundary

- Date: `2026-06-06T16:33:40Z`
- Reviewer: `security-reviewer`
- Task: `agent-core-followup-reminders-f10-security-privacy-tool-boundary-revie`
- Run: `run-1780763325-e13e3978`
- Result: `failed_blocked` for delivery.
- Evidence: `SECURITY_REVIEW.md` F10 section; focused tests passed (`38 passed in 1.66s`); resolved `customer_service` toolset has no forbidden tool intersection; Factory DB gate recorded with `gate_id=210`, status `failed`.
- Blocking finding: `gateway/run.py` and `tests/test_customer_service_routing.py` contain unresolved merge conflict markers in the customer-service boundary/routing path, so customer-facing boundary verification cannot be completed.
- Carry-forward remediation: resolve conflicts in `gateway/run.py`, `tests/test_customer_service_routing.py`, and any remaining CLI profile drift; rerun customer-service routing/security tests; then re-record/update Factory DB security gate if the boundary passes.

## Gate result: F2 architecture

- Date: `2026-06-05T23:59:22Z`
- Reviewer: `security-reviewer`
- Task: `agent-core-followup-reminders-f2-architecture-adr-and-data-model-for-u`
- Result: `passed` for architecture/data-model increment.
- Evidence: `SECURITY_REVIEW.md` F2 section; `F2_REVIEW_VALIDATION OK`; Factory DB architecture gate recorded as passed (`gate_id=165`).
- Carry-forward conditions: least-privilege grants, explicit toolset exposure, PII minimization, SQL safety, duplicate-prevention and idempotent audited side effects must be verified in F4-F10.

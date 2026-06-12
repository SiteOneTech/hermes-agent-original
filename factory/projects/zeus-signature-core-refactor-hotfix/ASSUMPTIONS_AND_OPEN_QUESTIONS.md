# Assumptions and Open Questions

Project: zeus-signature-core-refactor-hotfix
Owner: Jean García / SitioUno
Created: 2026-06-12T18:09:47-04:00
Status: G1 bootstrap pack complete; implementation not started
Validated: yes — initial Zeus document consistency pass
Reviewed: yes — initial Zeus Factory orchestrator review; independent quality/security review remains a project task before delivery


## Assumptions

1. Agent Core Postgres remains the canonical source of truth for Signature Core.
2. Public signature collection should reuse tokenized delivery workspace surfaces and OTP-first sensitive actions.
3. Commercial customer-facing copy must say SitioUno/Zeus de SitioUno, not Hermes or internal module names.
4. The first implementation target is Zeus fork; propagation to derived runtime happens after Zeus validation.
5. DocuSeal/OpenSign are research references only; no AGPL code/schema/content will be copied.
6. A drawn digital signature + audit hash is currently internal/commercial digital approval evidence, not a qualified PAdES/TSA legal signature.
7. PDF stamping must be done server-side from persisted field values, not from trusting the client-rendered PDF.
8. Daily follow-up uses configured channels available to the agent; if a signer has no reachable channel, the request should surface a dashboard/owner blocker.

## Open Questions for Later Product Refinement

These do not block G1 planning, but must be answered before broad rollout:

1. Which delivery channels are first-class for external signers: email, WhatsApp, Telegram, SMS, or all configured channels?
2. Should every external comment require OTP, or allow pre-OTP questions as untrusted comments?
3. What is the default expiration period: 7, 14, 30 days, or user-provided per request?
4. Should the module support signer delegation/reassignment in V1 or only cancel/reissue?
5. Does Jean want legal certificate/TSA/PAdES in the first product release, or is visible digital approval evidence enough for V1?
6. Should PyMuPDF commercial licensing be acquired for proprietary derived-agent distribution, or should final stamping use only permissive/server-safe alternatives?
7. Should the private dashboard show/download PDFs directly, or require short-lived signed download URLs per artifact?

## Decisions Already Made

- Every signing request must be backed by a template/version, even if created ad hoc from one uploaded PDF.
- Sensitive actions require OTP.
- Multi-signer support is required.
- Comments are required.
- Daily follow-up is required.
- Final signed document and hash validation must be sent to all signers.
- A private dashboard/metrics page is required.

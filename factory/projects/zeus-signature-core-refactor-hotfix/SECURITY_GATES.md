# Security Gates — Signature Core Refactor

Project: zeus-signature-core-refactor-hotfix
Owner: Jean García / SitioUno
Created: 2026-06-12T18:09:47-04:00
Status: G1 bootstrap pack complete; implementation not started
Validated: yes — initial Zeus document consistency pass
Reviewed: yes — initial Zeus Factory orchestrator review; independent quality/security review remains a project task before delivery


## Security Requirements

1. Opaque tokenized links; raw tokens never stored in DB.
2. OTP required for sign/approve/reject.
3. OTP hashes only; no plaintext code persistence.
4. Rate limits for OTP requests and action submissions.
5. Expired/cancelled/completed requests reject actions.
6. Sequential signing gates enforced server-side.
7. Event queue ingest validates token/session and stores audit evidence.
8. Public container holds no WhatsApp/Telegram/email provider secrets.
9. Final artifacts use scoped download links or protected private route.
10. Hashes generated server-side: source PDF, field signature images, approval hashes, event chain, final signed PDF.
11. PII minimized in public logs and dashboard output.
12. No AGPL code copying from DocuSeal/OpenSign/PyMuPDF into proprietary commercial core without licensing decision.

## Threats to Test

- Forged event/action without OTP.
- Reusing another submitter token.
- Signing after expiration/cancel.
- Completing request after one signer in multi-signer flow.
- Client submitting fields outside allowed field IDs/roles.
- Tampered signature image hash.
- Direct download of final PDFs without scoped auth.
- OTP brute force/rate limit bypass.
- Public dashboard access without `/user/` session.

## Pass Criteria

Security gate can pass only after:

- automated negative tests exist for OTP/token/status bypasses;
- reviewer inspects public route and worker ingest boundaries;
- final artifacts and hash summaries do not expose secrets/PII unnecessarily;
- dependency/license risk is documented.

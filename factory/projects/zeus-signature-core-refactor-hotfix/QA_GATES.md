# QA Gates — Signature Core Refactor

Project: zeus-signature-core-refactor-hotfix
Owner: Jean García / SitioUno
Created: 2026-06-12T18:09:47-04:00
Status: G1 bootstrap pack complete; implementation not started
Validated: yes — initial Zeus document consistency pass
Reviewed: yes — initial Zeus Factory orchestrator review; independent quality/security review remains a project task before delivery


## Required Automated Checks

- Unit tests for Signature Core tools.
- Migration/status tests for Agent Core DB module registration.
- Document action/OTP policy tests.
- PDF coordinate conversion tests.
- PDF stamping tests that parse final PDF and verify no placeholders.
- Visual render tests for final PDFs using `pdftoppm` or PyMuPDF render.
- Browser tests for mobile and desktop signing UI.
- Dashboard protected route tests.
- Reminder worker idempotency tests.

## Required Manual/Visual QA

- Open signing link on mobile viewport.
- Draw signature on touch/canvas, rotate/rescale if possible.
- Fill text/date/checkbox/comment fields.
- Reject with reason.
- Sign with OTP.
- Verify multi-signer sequence/parallel behavior.
- Render final PDF and inspect signature/data placement.
- Open private `/user/signatures/` dashboard authenticated.

## Pass Criteria

- No critical/major UI blockers on mobile or desktop.
- No OTP bypass.
- No premature completion before all required signers.
- Final PDFs visually correct and parseable.
- Reminder and final-copy delivery receipts persisted.
- Tests/builds pass cleanly.

## Current QA State

Seeded. No implementation QA has been run for V2 yet.

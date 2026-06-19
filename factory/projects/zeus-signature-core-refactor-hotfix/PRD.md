# PRD — Zeus Signature Core V2 Refactor and PDF Signing Collection

Project: zeus-signature-core-refactor-hotfix
Owner: Jean García / SitioUno
Created: 2026-06-12T18:09:47-04:00
Status: G1 bootstrap pack complete; implementation not started
Validated: yes — initial Zeus document consistency pass
Reviewed: yes — initial Zeus Factory orchestrator review; independent quality/security review remains a project task before delivery


## Product Vision

Signature Core becomes the reusable SitioUno module that lets a business owner tell their agent:

> “Te mando este PDF; prepara la recolección de firmas y datos, envíaselo a los firmantes, haz seguimiento, y cuando todos firmen mándales copia con hash.”

The owner should not need to operate a document-signing dashboard manually. Zeus should orchestrate the process agentically through chat, while the signer gets a polished responsive web signing experience.

## Users

- **Owner/operator:** Jean or a derived agent owner asking Zeus to collect signatures.
- **Signer:** external customer/vendor/team member opening a secure link on phone or PC.
- **Approver/viewer:** someone who approves or views without drawing a signature.
- **Zeus/agent:** prepares template, sends links, follows up, completes artifacts, records history.

## Core User Stories

### US1 — Send PDF to Zeus

As owner, I can send Zeus a PDF and say “recolecta firmas”, and Zeus will identify missing details before sending.

Acceptance:
- Zeus extracts/reads page count and can render preview pages.
- Zeus asks targeted missing questions instead of requiring a full form.
- Zeus stores source artifact hash before modification.

### US2 — Define Fields and Signers

As owner, I can specify multiple signers and data fields, and Zeus prepares a reusable template.

Acceptance:
- Template version contains field placements and signer role assignments.
- Fields can be signature, initials, text, date, checkbox, comment, attachment.
- Sequential and parallel flows are supported.

### US3 — Mark PDF Where Data/Signature Goes

As owner, I can mark where signatures/data appear or let Zeus detect anchor areas.

Acceptance:
- UI supports visual overlay placement on PDF pages.
- Backend stores PDF point coordinates and normalized viewport coordinates.
- Generated PDF places values/signatures exactly in intended regions.

### US4 — Sign Comfortably on Mobile/Desktop

As signer, I can open the link on phone or PC, authenticate by OTP, fill fields, draw signature, comment/reject if needed, and submit.

Acceptance:
- Mobile viewport has sticky action bar, large controls, high-DPI signature canvas.
- Desktop viewport shows PDF and field/task panel comfortably.
- No white-on-white controls, hidden buttons, tiny canvas, or scroll traps.

### US5 — Multi-Signer Completion

As owner, I can send to several signers and Zeus completes only when all required signers finish.

Acceptance:
- Status transitions: draft → sent → viewed/partially_signed → completed/declined/expired/cancelled.
- First signer does not complete entire request unless they are the only required signer.
- Sequential signing blocks later signers until prior gates are done.

### US6 — Final PDF, Hashes, and Copies

As signer/owner, when all signatures are collected, I receive a final PDF and validation hash.

Acceptance:
- Final PDF includes visible field values/signatures and audit/certificate page.
- Original and final SHA-256 hashes are stored and sent.
- Delivery receipts are stored for every copy sent.

### US7 — Daily Follow-Up

As owner, I do not need to remember to chase signers.

Acceptance:
- Pending signers get daily reminders until completed or expired.
- Reminder attempts are recorded in DB.
- Owner gets escalations near expiry or after repeated failures.

### US8 — Private Dashboard Metrics

As owner, I can open private `/user/` dashboard and see signature process status/metrics.

Acceptance:
- Protected by OTP user session.
- Shows active/pending/completed/expired/declined requests.
- Shows average signing time, reminders due, expiring soon, copies sent, hash status.

## MVP / V2 Definition

V2 is complete when Zeus can run this end-to-end for a PDF:

1. Intake PDF.
2. Ask for missing fields/signers/deadline.
3. Build template version.
4. Render responsive signing page.
5. OTP-auth signer.
6. Capture fields/comments/signature.
7. Handle multiple signers correctly.
8. Stamp final PDF at specified coordinates.
9. Store audit/history/artifacts/hashes.
10. Send final copies/hash to signers.
11. Follow up daily while pending.
12. Show private dashboard metrics.

## Out of Scope for First Refactor

- Qualified legal signature with TSA/PAdES certificate chain.
- Full DocuSeal/OpenSign replacement UI for teams/users/roles.
- Bulk CSV send.
- Real-time co-authoring annotations.
- Complex conditional fields/formulas unless easy after core model.

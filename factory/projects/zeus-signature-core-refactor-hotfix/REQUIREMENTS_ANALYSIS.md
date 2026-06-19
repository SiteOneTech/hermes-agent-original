# Requirements Analysis — Signature Core Refactor

Project: zeus-signature-core-refactor-hotfix
Owner: Jean García / SitioUno
Created: 2026-06-12T18:09:47-04:00
Status: G1 bootstrap pack complete; implementation not started
Validated: yes — initial Zeus document consistency pass
Reviewed: yes — initial Zeus Factory orchestrator review; independent quality/security review remains a project task before delivery


## Functional Requirements

### R1 — PDF Intake and Agent-Led Template Preparation

- User can send Zeus a PDF or URL and ask to collect signatures.
- Zeus detects whether enough information exists to proceed.
- If not enough, Zeus asks targeted questions:
  - Who signs? names, email/phone/channel, role, order, required/optional.
  - What data must be collected? text, date, checkbox, file, comment, initials, signature.
  - Where should each field appear? known page/area, anchor phrase, or interactive placement.
  - Deadline/expiration and reminder cadence.
  - Whether signing is parallel or sequential.
- Zeus stores the resulting template as a reusable Signature Core template/version.

### R2 — Canonical Template and Field Placement

- Every collection uses a Signature Core template/version, even if created ad hoc from a one-off PDF.
- Template fields store:
  - `field_id`, `field_type`, `label`, `role`, `required`, `page_number`.
  - PDF coordinates in points: `x`, `y`, `width`, `height`, `rotation`.
  - Normalized viewport coordinates: `x_pct`, `y_pct`, `w_pct`, `h_pct` for responsive overlays.
  - Optional anchor data: `anchor_text`, `anchor_occurrence`, `anchor_bbox`, tolerance.
  - Validation: max length, allowed values, regex, date mode, consent text.
  - Appearance: font, size, color, border, signature scale.
- Field placement must support signature, initials, name, date, text, long comment, checkbox, select, attachment, and internal-only note.

### R3 — Responsive Signing Interface

- The signer page must work comfortably on mobile and desktop.
- Must include:
  - PDF viewer with field overlays.
  - Step-by-step field navigator.
  - Sticky bottom action bar on mobile.
  - Large tap targets and accessible labels.
  - Signature canvas with high-DPI/orientation handling.
  - Clear buttons: sign/approve/reject/comment/request help.
  - Save-progress behavior before final submit when possible.
- The UI must be visually QAed in phone and desktop viewport.

### R4 — Secure OTP Collection

- Sign/approve/reject requires recipient-bound OTP before final event acceptance.
- OTP must be delivered through configured delivery channels without exposing messaging secrets to the public container.
- Links are opaque and scoped to one submitter/request.
- Expired/cancelled/completed requests cannot be signed.
- Sequential signing must block later signers until prior required roles complete.

### R5 — Comments and Rejections

- Comments are supported at request-level and field-level.
- Comments must be persisted in audit history with actor, timestamp, IP/user-agent when available, signer role, and field_id when applicable.
- Rejections require a reason/comment and trigger owner/Zeus notification.
- Internal agent notes are separate from signer comments.

### R6 — Multi-Signer and Workflow Completion

- Support multiple submitters with roles:
  - signer, approver, viewer, owner, agent.
- Support signing modes:
  - parallel, sequential, mixed role gates.
- Completion occurs only when all required signer/approver obligations are satisfied.
- Partial completion should set `partially_signed`, not `completed`.
- Optional viewers do not block completion.

### R7 — PDF Stamping and Final Artifact

- Final PDF must be visibly marked where data and signatures belong.
- The stamping engine must:
  - preserve the original approved-document hash.
  - render each field value/signature into its configured page rectangle.
  - include signer/date/hash metadata near or in certificate page.
  - generate final completed PDF and audit/certificate PDF or appended page.
  - compute SHA-256 for original, signed PDF, signature images, and audit artifact.
- Visual QA must render pages after stamping to catch placement/layout problems.

### R8 — Storage, Audit, and History

- Agent Core DB remains canonical.
- Store templates, template versions, request instances, submitters, field values, comments, attachments, approvals, delivery receipts, reminders, metrics, and events.
- Events must be append-only and hash-chained.
- Final document attachments include `completed_pdf` and `audit_pdf` with SHA-256 and storage path.

### R9 — Distribution After Completion

- After all required signers complete, send every signer:
  - final signed PDF or secure download link.
  - SHA-256 validation hash of final document.
  - approval/certificate summary.
- Store copy-delivery receipts and failures.

### R10 — Daily Follow-Up Until Signed or Expired

- If a request is pending, Zeus/worker follows up daily until completion or expiration.
- Follow-up policy is stored per request/template.
- Worker records reminder attempts, channel, result, next_due_at, and delivery id.
- Escalate to owner after configurable missed reminders or near-expiry.

### R11 — Private Dashboard

- Under protected private agent dashboard `/user/`, expose Signature module metrics:
  - active requests, pending signers, expiring soon, completed this month.
  - average time-to-sign, reminder effectiveness, decline rate.
  - list of signature processes and current status.
  - drilldown to signers/events/artifacts/hash summary.
- Dashboard must use OTP-auth private session and not expose secrets.

## Non-Functional Requirements

- **Canonical architecture:** no vendor-specific lock-in; DocuSeal/OpenSign are pattern sources/adapters, not source of truth.
- **Security:** token + OTP, rate limits, hash-only OTP storage, audit events, no secrets in public surface.
- **Mobile UX:** sign comfortably on phone; no tiny controls, white-on-white selects, or canvas scaling bugs.
- **Traceability:** every state transition auditable and persisted.
- **Testability:** unit tests, integration smoke, browser mobile/desktop QA, PDF visual QA.
- **Licensing:** do not copy AGPL project code/schema. Commercial runtime PDF stamping uses permissive/open dependencies (`pypdf` + `reportlab`) or original SitioUno implementation. PyMuPDF/fitz is only an R&D fallback and must not be required for proprietary client runtime distribution.

## Acceptance Criteria

- Given a PDF and missing metadata, Zeus asks the right questions before sending.
- Given field definitions, the system creates a reusable template/version.
- Given a signer on mobile, the signer can OTP-auth, fill fields, draw signature, and submit without layout breakage.
- Given multiple required signers, request completes only after all required signers finish.
- Given completion, final PDF contains visible signatures/data in the specified positions and certificate/hash page.
- Given completion, all signers receive final copy/hash and DB has delivery receipts.
- Given pending requests, daily follow-up events are generated until completed/expired.
- Given private dashboard access, user can see status/metrics without exposing public signing secrets.

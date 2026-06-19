# Technical Blueprint — Signature Core V2

Project: zeus-signature-core-refactor-hotfix
Owner: Jean García / SitioUno
Created: 2026-06-12T18:09:47-04:00
Status: G1 bootstrap pack complete; implementation not started
Validated: yes — initial Zeus document consistency pass
Reviewed: yes — initial Zeus Factory orchestrator review; independent quality/security review remains a project task before delivery


## Current Components

- `db/modules/signature/000001_signature_schema.sql`: initial schema with templates, document_requests, submitters, attachments, events, approvals.
- `tools/signature_tool.py`: JSON handlers for status/template/request/event/approval hash.
- `tools/signature_pdf.py`: PDF stamping helper currently stamps generic first-page marker + audit page.
- `scripts/runtime/delivery_document_actions.py`: canonical document actions and OTP policy helper.
- `scripts/runtime/publish_delivery_sandbox.py`: public workspace + `/user/` proxy + events service template.
- Tests: signature tool tests and document-actions tests.

## Proposed DB Model Additions

Keep existing tables for compatibility, add normalized V2 tables/migrations:

### `signature.template_versions`

- `template_version_id` PK
- `template_id` FK
- `version_number`
- `source_document_attachment_id`
- `document_sha256`
- `status`: draft/active/archived
- `field_schema` jsonb snapshot
- `created_by`, `created_at`, `activated_at`

### `signature.field_placements`

- `field_id` PK
- `template_version_id` FK
- `role`, `field_type`, `label`, `required`
- `page_number`, `x`, `y`, `width`, `height`, `rotation`
- `x_pct`, `y_pct`, `w_pct`, `h_pct`
- `anchor_text`, `anchor_strategy`, `validation`, `appearance`, `metadata`

### `signature.field_values`

- `field_value_id` PK
- `request_id`, `submitter_id`, `field_id`
- `value_text`, `value_json`, `attachment_id`
- `status`: draft/submitted/voided
- `created_at`, `submitted_at`, `ip_address`, `user_agent`

### `signature.comments`

- request/submitter/field scoped comments.
- `visibility`: signer, owner, internal.
- `trusted_identity`: boolean indicating OTP/session verified.

### `signature.reminder_policy` and `signature.reminder_attempts`

- cadence, next_due_at, max attempts, escalation rules.
- delivery channel/id/status/error.

### `signature.delivery_receipts`

- invitation sent, OTP sent, reminder sent, final copy sent.
- channel, recipient, provider message id, status, timestamp.

### `signature.metric_snapshots` or SQL views

- counts and time-to-sign metrics for dashboard.

## Workflow State Machine

Request statuses:

- `draft`: template/request prepared but not sent.
- `sent`: at least one active submitter has invitation.
- `viewed`: at least one submitter viewed.
- `partially_signed`: some but not all required obligations complete.
- `completed`: all required obligations complete and final artifact generated.
- `declined`: one required signer declined and policy says stop.
- `expired`: deadline reached.
- `cancelled`: owner/agent cancelled.

Submitter statuses:

- `pending`, `sent`, `viewed`, `started`, `signed`, `approved`, `declined`, `expired`, `cancelled`.

Completion algorithm:

1. Load request and submitters.
2. Ignore optional viewers for completion.
3. If required submitter declined and request policy `decline_blocks=true`, request `declined`.
4. If expired, request `expired` unless already completed.
5. If all required signer/approver submitters complete, generate final PDF and set `completed`.
6. Else if any required complete, set `partially_signed`; otherwise `sent/viewed` based on events.

## PDF Field Coordinate System

Canonical coordinates are PDF points with origin and conversion documented per renderer. The implementation must settle whether `y` is stored top-left or PDF bottom-left and never mix conventions.

Recommended storage:

- `page_number`: 1-based.
- `x`, `y`, `width`, `height`: PDF points, top-left-origin normalized by the signing UI.
- `pdf_y_bottom`: generated/stored internally if PyMuPDF/pdf-lib requires bottom-left conversion.
- `x_pct`, `y_pct`, `w_pct`, `h_pct`: overlay percentages relative to rendered page box.

Tests must validate round-trip:

`PDF points → rendered overlay → edited overlay → PDF points → stamped PDF visual render`.

## Public Signing UI

Route options:

- `GET /w/<token>/` renders generic workspace/signing template.
- `GET /w/<token>/sign` or query state can show signing form.
- `/api/document-actions/request-otp`
- `/api/document-actions/verify-otp`
- `/api/document-actions` for event queueing.

UI components:

- PDF.js viewer pane.
- overlay field layer.
- signer task list / progress panel.
- signature canvas using signature_pad or equivalent.
- comment/reject modal.
- OTP modal.
- final confirmation screen.

## Agent Tool Surface

Add/refactor tools:

- `signature_pdf_intake`: register source PDF, hash, page count, preview images.
- `signature_template_prepare`: create template version from PDF + fields/signers.
- `signature_template_field_upsert`: add/update field placements.
- `signature_request_send`: create request, submitters, invitations, reminder policy.
- `signature_request_status`: aggregate signer/request state.
- `signature_request_complete`: generate final PDF/certificate when eligible.
- `signature_followup_due`: list/send due reminders.
- `signature_dashboard_metrics`: return private dashboard summary.

Existing tools remain compatible but should route through V2 internals.

## Private Dashboard

Extend `/user/` protected dashboard with a Signature module page/card:

- `/user/signatures/`
- Active requests and pending signers.
- Expiring soon.
- Completed/declined/expired counts.
- Average time-to-sign.
- Reminder attempts and failures.
- Hash status and artifact links.

## Storage

- Local artifacts stored under configured document/signature storage path.
- DB stores paths, MIME, size, SHA-256, not large base64 payloads.
- Public downloads should be token-scoped/signed and not leak private paths.

## Security Notes

- Public container has no messaging/API secrets.
- OTP stored as HMAC/hash, not plaintext.
- Token hashes stored, not raw signer tokens.
- Rate limits on OTP and actions.
- Event queue ingested by trusted worker into Agent Core DB.
- Sensitive final artifacts require scoped access and audit logging.

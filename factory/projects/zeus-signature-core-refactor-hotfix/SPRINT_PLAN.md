# Sprint Plan — Signature Core Refactor

Project: zeus-signature-core-refactor-hotfix
Owner: Jean García / SitioUno
Created: 2026-06-12T18:09:47-04:00
Status: G1 bootstrap pack complete; implementation not started
Validated: yes — initial Zeus document consistency pass
Reviewed: yes — initial Zeus Factory orchestrator review; independent quality/security review remains a project task before delivery


## Sprint 0 — G1 Bootstrap and Project Registration

Goal: open project, research patterns, document canonical architecture, register tasks/gates.

Deliverables:
- Factory DB project.
- G1 docs pack.
- Initial task graph and tracker.
- Initial gates.

## Sprint 1 — Data Model and Tool Refactor

Goal: normalize templates/field placements/values/comments/reminders/receipts and make tools enforce multi-signer completion.

Tasks:
- Add migration for V2 normalized tables/views.
- Update `signature_tool.py` with V2 handlers and backward-compatible wrappers.
- Fix completion logic so one approval does not complete a multi-signer request.
- Add unit tests for multi-signer, comments, field values, reminders, receipts.

## Sprint 2 — PDF Intake, Template Preparation, and Field Placement

Goal: make Zeus able to receive a PDF, ask missing questions, create template fields, and preview/mark placement.

Tasks:
- PDF intake/hash/page-count/preview tool.
- Field placement schema and coordinate conversion helpers.
- Template version create/update workflow.
- Server-side visual fixture tests.

## Sprint 3 — Responsive Signing UI and OTP Flow

Goal: public signer experience on `/w/<token>/` works on phone and desktop.

Tasks:
- PDF.js viewer + overlay field layer.
- signature_pad canvas capture with high-DPI resize handling.
- OTP modal and action submission.
- Comment/reject flow.
- Mobile/desktop browser QA tests/screenshots.

## Sprint 4 — Final PDF Stamping, Copies, and Hash Validation

Goal: completed requests generate final PDF at field positions and send copies/hash.

Tasks:
- Refactor `tools/signature_pdf.py` to stamp multiple fields/signatures.
- Generate certificate/audit page with hashes and event-chain summary.
- Persist `completed_pdf`/`audit_pdf` attachments.
- Copy/hash delivery worker and receipt storage.
- PDF parse + visual render QA.

## Sprint 5 — Daily Follow-Up and Dashboard Metrics

Goal: pending requests get daily reminders and private dashboard shows useful metrics.

Tasks:
- Reminder due worker and cron integration.
- Owner escalation policy.
- Signature dashboard metrics endpoint/tool.
- Protected `/user/signatures/` UI.
- Dashboard smoke tests.

## Sprint 6 — Security/QA/Release/Propagation

Goal: independent review, deployment readiness, and propagation decision.

Tasks:
- Security review for token/OTP/hash/access controls.
- QA suite across mobile/desktop/PDF artifacts.
- Release runbook and delivery report.
- Decide and plan propagation to `sitiouno-agent-runtime`.

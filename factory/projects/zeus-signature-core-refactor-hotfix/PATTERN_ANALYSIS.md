# Pattern Analysis — E-Signature, PDF Markup, Mobile Signing

Project: zeus-signature-core-refactor-hotfix
Owner: Jean García / SitioUno
Created: 2026-06-12T18:09:47-04:00
Status: G1 bootstrap pack complete; implementation not started
Validated: yes — initial Zeus document consistency pass
Reviewed: yes — initial Zeus Factory orchestrator review; independent quality/security review remains a project task before delivery


## Repositories / Libraries Reviewed

| Source | License / Maturity | Relevant Patterns | Adoption Decision |
|---|---:|---|---|
| DocuSeal — https://github.com/docusealco/docuseal | AGPL-3.0, ~17k stars, active | Templates, WYSIWYG PDF form builder, 10–12 field types, multi-submitters, mobile-optimized signing, automated emails, API/webhooks, reminders | Study architecture/product patterns only. Do not copy AGPL code/schema. |
| OpenSign — https://github.com/OpenSignLabs/OpenSign | AGPL-3.0, ~6.5k stars, active | Multi-signer support, sequence enforcement, guest OTP/email code, expiring docs, rejection reason, audit trails/completion certificate | Study workflow/security patterns only. Do not copy code/schema. |
| signature_pad — https://github.com/szimek/signature_pad | MIT, ~12k stars, active, 0 dependencies | Smooth canvas signatures, mobile/desktop support, high-DPI resize guidance, SVG/PNG export | Strong candidate for signer UI if JS dependency fits repo. |
| pdf-lib — https://pdf-lib.js.org / https://www.npmjs.com/package/pdf-lib | MIT, mature npm library | Create/modify PDFs, fill forms, flatten, draw text/images/SVG, browser/Node compatible | Useful for browser/Node field prep or form manipulation; not enough alone for secure server workflow. |
| PDF.js — https://github.com/mozilla/pdf.js | Apache-2.0, Mozilla, ~53k stars | HTML5 PDF rendering, browser viewer, npm `pdfjs-dist`, extensible overlay approach | Preferred viewer foundation for responsive field placement/signing UI. |
| pypdf — https://pypdf.readthedocs.io/ | BSD-3-Clause, pure Python | Read/write/merge PDFs, page overlays, metadata, form helpers | Commercial-runtime-safe server PDF mutation base. Use with ReportLab overlays for visible stamps/certificates. |
| ReportLab — https://www.reportlab.com/opensource/ | BSD-style open source toolkit | Generate PDF overlay pages, text, shapes, certificate pages | Pair with pypdf for visible Signature Core stamp/certificate generation without paid/commercial PyMuPDF licensing. |
| PyMuPDF — https://github.com/pymupdf/PyMuPDF | AGPL/commercial, ~10k stars, installed in document-worker runtime | Fast rendering, coordinate extraction, annotations, text/image insertion, OCR, form read/fill | Research/dev fallback only. Do not make it required for proprietary client runtime distribution. |

## Patterns to Adopt

### Template → Request → Submitter → Event → Completed Artifact

DocuSeal/OpenSign both organize around reusable templates that generate signing submissions/requests. Zeus Signature Core should keep this as the canonical flow:

1. `template` / `template_version` defines fields and signer roles.
2. `request` snapshots a template version for a specific PDF/customer/task.
3. `submitter` rows represent each signer/approver/viewer.
4. `field_values`, `comments`, `attachments`, and `approvals` attach to submitters.
5. append-only events record every action.
6. final `completed_pdf`/`audit_pdf` artifacts are stored with hashes.

### WYSIWYG/Overlay Field Placement

DocuSeal-style builder and OpenSign-style annotate/sign experience show that field placement must be visual, not only JSON. Zeus should support:

- automated placement by anchor text when possible;
- manual/interactive overlay when anchor detection is ambiguous;
- normalized coordinates for responsive display;
- server-side PDF point coordinates as the final truth for stamping.

### Mobile-First Signing

All mature signing tools emphasize mobile-optimized signing. Signature Pad specifically documents high-DPI and resize/orientation handling. The Zeus signer UI must include:

- large touch targets;
- full-width canvas with devicePixelRatio scaling;
- orientation/resize preservation;
- step navigation to next required field;
- field progress indicator;
- sticky submit bar.

### OTP for Sensitive Actions

OpenSign supports OTP/email code for guest signers. Zeus already has OTP-first patterns for quote approvals and private `/user/`. Signature Core should reuse:

- public container stores only OTP hashes and outbox events;
- Hermes-side dispatcher sends OTP through configured channels;
- sign/approve/reject require verified OTP;
- comments can be direct only if treated as low-risk questions; trusted signer comments require OTP/session.

### Certificate and Hash Validation

OpenSign-style completion certificate and existing Zeus `approval_hash` should converge:

- original document SHA-256;
- each signature image SHA-256;
- each approval hash;
- hash-chained event log root/latest hash;
- final signed PDF SHA-256;
- certificate/audit page embedded/appended.

## Patterns to Avoid

- Do not make DocuSeal/OpenSign the canonical source of truth for Zeus. They can be future adapters.
- Do not store base64 signatures only in DB; decode to controlled artifact storage and hash.
- Do not complete the request after the first signer unless only one required signer exists.
- Do not expose private dashboard or agent secrets from public signing container.
- Do not claim PAdES/QES/eIDAS qualified signature until certificate/TSA support exists and tests prove it.
- Do not rely on client-side PDF edits as final signed artifact; server must generate final PDF.

## Recommended Adapted Architecture

- **Viewer/UI:** PDF.js for page rendering + overlay fields; Signature Pad for drawing signatures.
- **Server stamping:** existing `tools/signature_pdf.py` refactored to place all field values; use PyMuPDF or a licensing-safe fallback path (`pypdf` + ReportLab/pdf-lib) depending on deployment policy.
- **DB:** normalize templates/versions/field placements/values/comments/reminders/receipts while preserving current JSON snapshots for backward compatibility.
- **Public route:** canonical `/w/<token>/` workspace until `/sign/<slug>` is fully routed and verified. If `/sign/<slug>` is added, it must be an alias over the same secure workflow, not a separate implementation.
- **Worker:** daily follow-up as deterministic Signature Core worker/cron/task, not ad-hoc chat reminders.

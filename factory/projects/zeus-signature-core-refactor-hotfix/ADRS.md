# ADRs — Signature Core Refactor

Project: zeus-signature-core-refactor-hotfix
Owner: Jean García / SitioUno
Created: 2026-06-12T18:09:47-04:00
Status: G1 bootstrap pack complete; implementation not started
Validated: yes — initial Zeus document consistency pass
Reviewed: yes — initial Zeus Factory orchestrator review; independent quality/security review remains a project task before delivery


## ADR-001 — Agent Core DB Remains Canonical

**Decision:** Store all signature templates, requests, signers, fields, comments, events, artifacts, reminders, and metrics in the local Agent Core `signature` schema.

**Rationale:** Zeus-style agents must operate signature workflows from chat/tools and maintain local historical truth. External signing platforms can be adapters, not primary truth.

**Consequences:** Requires schema refactor/migration and tool changes. Avoids vendor lock-in.

## ADR-002 — Every Request Uses a Template Version

**Decision:** Even ad-hoc PDFs get a template/version record before sending.

**Rationale:** Jean wants a process used always in the core. Template versions give repeatability, auditability, and allow field placement review.

**Consequences:** `signature_request_create` should require or create a `template_version_id`; raw JSON snapshots stay as compatibility fields but normalized rows become canonical.

## ADR-003 — Canonical Public Collection Surface Is Tokenized Workspace + OTP

**Decision:** Use `/w/<token>/` public workspace routes and `/api/document-actions*` OTP endpoints as the canonical secure collection path until `/sign/<slug>` is fully implemented/routed as an alias.

**Rationale:** Existing delivery sandbox supports tokenized workspace and OTP-first document actions. Standalone `/sign/<slug>` was previously not verified as served.

**Consequences:** UI work should extend the delivery workspace signature template, not create an independent insecure path.

## ADR-004 — PDF Viewer Overlay + Server-Side Stamping

**Decision:** Use a browser PDF viewer with overlay fields for UX, but final PDF stamping happens server-side from DB field values/coordinates.

**Rationale:** Client-side rendering is for interaction, not audit authority. Server-side stamping can hash, verify, and reproduce artifacts.

**Consequences:** Need coordinate conversion tests from viewport to PDF points and visual PDF QA.

## ADR-005 — Sensitive Actions Require OTP

**Decision:** `signed`, `approved`, and `rejected` require OTP. Trusted signer comments should occur after signer token/OTP session; pre-OTP questions may be accepted only as low-risk untrusted comments if explicitly designed.

**Rationale:** Matches existing quote approval security pattern and OpenSign guest signer OTP pattern.

**Consequences:** Need OTP flows in signing UI and backend tests for bypass prevention.

## ADR-006 — Completion Requires All Required Signers

**Decision:** Request is not `completed` until all required signer/approver obligations are done.

**Rationale:** Current single-approval completion behavior is unsafe for multi-signer workflows.

**Consequences:** Refactor `signature_approval_hash_create` and ingest worker to compute aggregate request status.

## ADR-007 — Use Research Patterns, Not AGPL Code

**Decision:** DocuSeal/OpenSign/PyMuPDF are analyzed for patterns; no AGPL code/schema is copied. Commercial/runtime PDF stamping must use the open permissive stack `pypdf` (BSD-3-Clause) + `reportlab` (BSD-style) or original SitioUno code. PyMuPDF/fitz is allowed only as a research/dev fallback while this project remains R&D; it must not be the required dependency for proprietary client runtime distribution.

**Rationale:** Jean decided no paid commercial PDF licenses. R&D may use open/distributable software, but SitioUno runtime must avoid license traps and paid commercial licensing obligations.

**Consequences:** Builders must prefer the `signature` extra (`pypdf==6.12.2`, `reportlab==4.5.1`) for Signature Core PDF output, keep PyMuPDF as optional fallback only, and verify final signed PDF generation without `fitz` before commercial runtime propagation.

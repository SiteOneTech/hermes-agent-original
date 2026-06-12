# Factory Intake — Zeus Signature Core Refactor + PDF Signing Collection Hotfix

Project: zeus-signature-core-refactor-hotfix
Owner: Jean García / SitioUno
Created: 2026-06-12T18:09:47-04:00
Status: G1 bootstrap pack complete; implementation not started
Validated: yes — initial Zeus document consistency pass
Reviewed: yes — initial Zeus Factory orchestrator review; independent quality/security review remains a project task before delivery


## User Objective

Jean asked Zeus to open a formal Factory project for a refactor/hotfix of the Zeus/SitioUno Signature Core and to improve the full signature-collection process so it becomes a powerful canonical module, not a one-off quote approval patch.

The desired product behavior is:

> Jean can send Zeus a PDF and ask Zeus to collect signatures. Zeus can ask what fields and data must be collected, prepare the PDF/template, send secure signer links, follow up daily until signed or expired, store signed artifacts and audit history, and show private dashboard metrics.

## Scope Classification

- **Project type:** existing runtime/core refactor and hotfix.
- **Repo scope:** `zeus_then_runtime`.
- **Primary repo:** `SiteOneTech/hermes-agent-original`.
- **Primary local path:** `/home/jean/workspace/hermes-factory-runtime-contract-v1`.
- **Remote:** `https://github.com/SiteOneTech/hermes-agent-original.git`.
- **Current base branch:** `factory/factory-runtime-contract-v1`.
- **Branch prefix for implementation:** `factory/zeus-signature-core-refactor-hotfix`.
- **Propagation:** implement and validate in Zeus fork first; after GREEN, evaluate propagation to `sitiouno-agent-runtime` for derived commercial agents.

## Current Reality Observed Before Project Open

Existing Signature Core already has an Agent Core schema and tools:

- `db/modules/signature/000001_signature_schema.sql`
- `tools/signature_tool.py`
- `tools/signature_pdf.py`
- `toolsets.py` toolset `signature`
- `scripts/runtime/delivery_document_actions.py`
- `scripts/runtime/publish_delivery_sandbox.py`
- tests for document actions and signature tools

Current gaps to fix/refactor:

1. `signature_approval_hash_create` completes the whole request after one approval; it does not wait for all required signers.
2. Schema stores JSON field snapshots but lacks first-class template versions, field placement records, signer field assignments, reminder policy, delivery/copy receipts, and metrics tables/views.
3. Public delivery action vocabulary exists, but the signer UI/template is not yet a full responsive PDF viewer/editor/signing experience.
4. Current PDF stamping places one generic stamp on page 1 plus an audit page; it does not yet stamp all field placements where signatures/data must appear.
5. Current standalone `/sign/<slug>` can be misleading if not actually served. Canonical collection should use `/w/<token>/` or the verified public delivery surface until `/sign/<slug>` is implemented and routed.
6. Daily follow-up and expiration handling are a product requirement but not yet a complete recurring worker with metrics and delivery receipt evidence.
7. Private `/user/` dashboard exists conceptually for agent modules; Signature Core needs its own protected module page/cards.

## Target Outcome

A canonical Signature Core flow that every Zeus-style agent can reuse:

1. **PDF intake:** user sends/points to a PDF.
2. **Requirement clarification:** Zeus asks only missing items: signers, roles/order, deadline, fields/comments/attachments needed, language, delivery channel.
3. **Template preparation:** Zeus creates or updates a reusable signature template/version with field placements over the PDF.
4. **Field placement:** fields can be placed by coordinates, anchors, or interactive responsive viewer overlay; each field has type, signer role, required flag, validation, and PDF coordinates.
5. **Secure collection:** signer receives tokenized link; signing/approve/reject requires recipient-bound OTP. Comments are supported and audited.
6. **Responsive UI:** comfortable on phone and PC, including large tap targets, canvas signature capture, sticky action bar, PDF zoom/scroll, and field navigation.
7. **Multi-signer orchestration:** support parallel and sequential signing, required/optional signers, viewers/approvers, decline/reassign/expire rules.
8. **Completion:** only when all required signers/actions are satisfied, generate final signed PDF and certificate/audit page, compute hashes.
9. **Distribution:** send each signer a copy of the final signed document and hash validation summary.
10. **Follow-up:** if pending, send daily reminders until all signers complete or the request expires.
11. **History/dashboard:** store events, hashes, artifacts, metrics, and expose private dashboard metrics/status.

## Initial Gates

- Intake gate: should pass after this document pack is committed and Factory DB has project/tasks.
- Functional gate: should pass after requirements/PRD are reviewed.
- Architecture/planning gates: should pass only after task graph, ADRs, QA, and security gates are reviewed.
- Implementation gate: pending; no code changes are authorized until G1 is GREEN.

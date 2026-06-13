# T01 — Current Signature Code and Route Audit

Project: `zeus-signature-core-refactor-hotfix`
Task: `zeus-signature-core-refactor-hotfix-t01-current-signature-code-and-route-aud`
Branch/worktree: `factory/zeus-signature-core-refactor-hotfix/t01-current-signature-code-and-route-audit` at `/home/jean/workspace/zeus-signature-core-refactor-hotfix-t01-audit`
Date: 2026-06-13

## Canonical documents read

- `factory/projects/zeus-signature-core-refactor-hotfix/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/TASK_GRAPH.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/PRD.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/REQUIREMENTS_ANALYSIS.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/PATTERN_ANALYSIS.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/ADRS.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/QA_GATES.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/SECURITY_GATES.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/TRACKER.md`
- `docs/signature-core/PRD-001-agent-signature-core.md`
- `docs/signature-core/ADR-001-local-agent-signature-core.md`

## Code and tests audited

- `db/modules/signature/000001_signature_schema.sql`
- `tools/signature_tool.py`
- `tools/signature_pdf.py`
- `toolsets.py`
- `tools/sales_tool.py`
- `hermes_cli/commerce_workspace_surface.py`
- `hermes_cli/web_server.py`
- `scripts/runtime/delivery_document_actions.py`
- `scripts/runtime/publish_delivery_sandbox.py`
- `scripts/runtime/ingest_delivery_events.py`
- `tests/tools/test_signature_tool.py`
- `tests/test_delivery_document_actions.py`
- `tests/test_publish_delivery_sandbox_document_actions.py`
- `tests/test_commerce_workspace_surface.py`

## Current implementation map

### 1. Signature schema

File: `db/modules/signature/000001_signature_schema.sql`

Current tables:

- `signature.templates` (`template_id`, `name`, `document_url`, `fields`, `submitters`, `preferences`, `metadata`).
- `signature.document_requests` (`request_id`, `source_type`, `source_id`, `status`, `document_url`, `completed_document_url`, `audit_url`, `document_hash_sha256`, `approval_hash`, `public_url`, snapshots, expiry/completion metadata).
- `signature.submitters` (`submitter_id`, `request_id`, `role`, `signing_order`, `name`, `email`, `phone`, `slug`, `token_hash_sha256`, `status`, `values`, evidence fields).
- `signature.attachments` (`kind` supports `signature`, `initials`, `stamp`, `file`, `image`, `completed_pdf`, `audit_pdf`).
- `signature.events` with event hash chain fields `previous_event_hash` and `event_hash`.
- `signature.approvals` with `approval_context`, signature fields, `document_hash_sha256`, and unique `approval_hash`.

Security/storage baseline:

- Raw signer token is not stored: only `signature.submitters.token_hash_sha256` exists.
- Runtime role defaults to `signature_runtime`; schema grants allow read/write for `signature_runtime` and read-only for `agent_runtime`.

Gaps versus PRD/TASK_GRAPH:

- No V2 tables/columns for recipient-bound OTP challenges, delivery receipts, reminder policy, final-copy delivery receipts, or field coordinate versioning.
- `document_requests.status` does not include `rejected`; it uses `declined`, while delivery/document-action vocabulary uses `rejected`.
- `submitters.status` supports `signed` and `approved`, but not `rejected`; it uses `declined`.
- `events.event_type` allows `signed`, `approved`, and `declined`, but not `rejected` or `commented`; this does not align with the canonical document action vocabulary already used by delivery sandbox (`commented`, `approved`, `rejected`, `signed`).

### 2. Signature tools

File: `tools/signature_tool.py`

Registered toolset:

- `toolsets.py` registers `signature` with `signature_status`, `signature_template_upsert`, `signature_request_create`, `signature_request_get`, `signature_event_record`, `signature_approval_hash_create`.

Current behavior:

- `signature_status` returns table counts from Agent Core Postgres.
- `signature_template_upsert` creates/updates reusable template rows.
- `signature_request_create` creates/updates one `document_requests` row, deletes/recreates submitters for the request, generates a raw token once for response only, stores SHA-256 token hash, stores a unique slug, and returns `signing_url`.
- `signature_request_get` returns request, submitters, events, approvals.
- `signature_event_record` appends a hash-chained event.
- `signature_approval_hash_create` creates/updates approval, marks one submitter `approved`, marks the entire request `completed`, sets request `approval_hash`, and records `approved` + `hash_created` events.

Critical gap:

- Multi-signer completion is incorrect for V2: `signature_approval_hash_create` completes the whole `document_requests` row on first approval (`UPDATE signature.document_requests SET status='completed'...`). T03 already tracks this known bug; downstream implementation must only complete after all required signers/approvers finish.

Route gap:

- `signature_request_create` generates links from `SIGNATURE_WORKSPACE_BASE_URL` or default `https://zeus-sandbox.kidu.app/sign`, then appends `/{slug}`. Search found no FastAPI route for `/sign/{slug}` in `hermes_cli/*` or public delivery server. Therefore current `/sign/<slug>` links are not routed in this repo.

Security gap:

- There is no submitter token verification handler. The raw token is returned at creation time but no audited route currently verifies it against `token_hash_sha256`.

### 3. PDF helper

File: `tools/signature_pdf.py`

Current behavior:

- Uses PyMuPDF (`fitz`) to stamp a generic visible Spanish block on page 1.
- Adds an audit/certificate page titled `Certificado de aprobación y firma digital` with `SitioUno / Zeus Signature Core` provenance.
- Returns metadata including input/output SHA-256 and output byte size.

Gaps versus PRD/TASK_GRAPH:

- Not integrated with `signature_tool.py` or public route flow.
- No multi-field placement from `fields_snapshot` / submitter values.
- No coordinate engine, normalized viewport coordinate conversion, anchor text placement, or ambiguity handling.
- No completed PDF/audit PDF attachment persistence in `signature.attachments`.

### 4. Delivery document action helper

File: `scripts/runtime/delivery_document_actions.py`

Current behavior:

- Canonical action vocabulary exists: `comment/commented -> commented`, `approve/approved -> approved`, `reject/rejected -> rejected`, `sign/signed -> signed`.
- OTP policy exists: OTP required for `approved`, `rejected`, `signed`; comments can be direct-posted.
- `build_document_event` emits events with `status='pending_agent_ingest'`, comment truncation, metadata validation, token ref, IP, and user agent.

Fit:

- This matches the V2 action vocabulary better than the current `signature.events` schema.

### 5. Public delivery sandbox

File: `scripts/runtime/publish_delivery_sandbox.py`

Current behavior:

- Publishes a static public delivery sandbox plus an event server.
- Copies `delivery_document_actions.py` into the event-server image.
- Keeps public service DB-secret-free; stores JSONL audit events and OTP/session state under the sandbox data directories.
- Exposes document action endpoints:
  - `POST /api/document-actions`
  - `POST /api/document-actions/request-otp`
  - `POST /api/document-actions/verify-otp`
  - non-`/api` aliases also exist.
- Direct `POST /api/document-actions` rejects OTP-required events with `401 otp_required`; comment events can queue directly.
- OTP verify queues final document action event with `otp_verified`, challenge id, channel id, target hash, token ref, IP, and user-agent metadata.
- Legacy generic `POST /events` also rejects `approved/rejected/signed` when OTP is required.

Gaps versus Signature PRD:

- Events are generic delivery/workspace events; they are not yet promoted into `signature.*` rows.
- The delivery sandbox has OTP action endpoints but no `/sign/<slug>` page or Signature Core submitter-token page.
- It does not stamp PDFs or create `signature.approvals` directly.

### 6. Public `/w/<token>` workspace routes

Files: `hermes_cli/commerce_workspace_surface.py`, `hermes_cli/web_server.py`, `tools/sales_tool.py`

Current behavior:

- `sales_tool._workspace_url(public_token)` builds `/w/{public_token}` URLs.
- `sales_customer_workspace_create` creates `sales.customer_workspaces` rows with raw `public_token` and `public_url`.
- `hermes_cli.web_server` includes `commerce_workspace_surface.router`.
- Public routes exist:
  - `GET /w`
  - `GET /w/`
  - `GET /w/{public_token}`
  - `POST /w/{public_token}/comment`
  - `POST /w/{public_token}/approve`
  - `POST /w/{public_token}/reject`
- The `/w` surface renders quote/invoice/catalog review and records `opened`, `commented`, `approved`, `rejected` events in Sales Core.
- `/w/{token}/approve` can convert quote -> order -> invoice and record a metadata `signature` value.

Critical gaps versus V2:

- `/w/{token}/approve` and `/w/{token}/reject` do not enforce OTP in `commerce_workspace_surface.py`; they are direct form posts.
- `/w/{token}/approve` is Sales Core, not Signature Core: it records `sales.customer_workspace_events`, not `signature.events` / `signature.approvals`.
- There is no `POST /w/{token}/sign` route.
- The quote approval form does not currently require a typed/drawn signature before approval; it can default to customer name/email.
- Public tokens in Sales Core are stored raw (`sales.customer_workspaces.public_token`), unlike Signature Core submitter tokens which are hashed.

### 7. Trusted ingestion worker

File: `scripts/runtime/ingest_delivery_events.py`

Current behavior:

- Promotes delivery JSONL events into `sales.customer_workspace_events` or `accounting.receipt_events`.
- Creates CRM follow-ups for `commented`, `approved`, `rejected`, `signed`, `change_requested`, `payment_failed`.
- Converts quote to order/invoice on `approved` sales workspace events.
- Final statuses include OTP-required document event types.

Gap:

- No path ingests delivery events into `signature.events`, `signature.approvals`, `signature.submitters`, or final PDF attachments.

## Route decision: `/sign/<slug>` vs `/w/<token>`

Confirmed current repo state:

- `/w/<token>` is routed and active through `hermes_cli/commerce_workspace_surface.py` and included by `hermes_cli/web_server.py`.
- `/sign/<slug>` is generated by `tools/signature_tool.py` as the default signature URL base, but no corresponding route handler was found in this repo.
- Existing docs say v1 allowed either `/sign/<slug>` or embedded `/w/<token>` integration. Current implementation only has working `/w/<token>` routes.

Recommended V2 interpretation:

- Treat `/sign/<slug>` as currently unrouted/stale unless T06 introduces a dedicated signer route.
- Prefer embedding/signature actions under the existing tokenized `/w/<token>` public workspace surface for V2 hotfix continuity, or explicitly add a `/sign/{slug}` route that verifies Signature Core submitter slug+token hash and redirects/bridges into `/w/<token>` only when linked.
- Do not rely on current generated `/sign/<slug>` links for production until route glue exists.

## Exact PRD gaps to feed next increments

1. Schema V2 migration (T02): align action vocabulary (`rejected`, `commented`), add multi-signer completion state, OTP/delivery/reminder/final-copy fields, coordinate/field template versions, and completed/audit PDF attachment linkage.
2. Tool refactor (T03): stop completing request on first approval; compute completion only after required signer set is done; add signer-token verification/read model; avoid deleting submitters on idempotent request update unless intentional.
3. PDF intake/template workflow (T04/T05): persist PDF source hash/page metadata and field coordinates; integrate with template snapshots.
4. Signer UI (T06): implement real routed signing surface. Current `/sign/<slug>` is missing; current `/w/<token>` lacks sign route and drawn/typed signature enforcement.
5. OTP integration (T07): enforce OTP on approve/reject/sign in active public route. The delivery sandbox helper has correct policy; the FastAPI `/w` route bypasses it today.
6. Event ingestion (T07/T08): bridge delivery document action events into `signature.*`, not only sales/accounting.
7. Final PDF/certificate (T10/T11): integrate `signature_pdf.py` with approval completion, field placement, `signature.attachments`, and delivery of final hash copies.
8. Private dashboard (T12): add protected signature metrics surface; current protected user dashboard pattern exists but no Signature Core module page was found.

## Verification commands

Executed/required for this audit:

- `git status --short --branch`
- `hermes factory status zeus-signature-core-refactor-hotfix --json`
- targeted source searches with `search_files` for `/sign`, `/w`, `signature`, `document-actions`, `SIGNATURE_WORKSPACE_BASE_URL`, `stamp_signed_pdf`, and route decorators.
- targeted reads of the files listed above.

Targeted tests/verifications run after this document update:

- `scripts/run_tests.sh tests/tools/test_signature_tool.py tests/test_delivery_document_actions.py tests/test_publish_delivery_sandbox_document_actions.py tests/test_commerce_workspace_surface.py -q` — failed before test execution because `run_tests_parallel.py` does not accept `-q`.
- `scripts/run_tests.sh tests/tools/test_signature_tool.py tests/test_delivery_document_actions.py tests/test_publish_delivery_sandbox_document_actions.py tests/test_commerce_workspace_surface.py` — failed before test execution because the configured Python environment `/home/jean/.hermes/hermes-agent/venv/bin/python` has no `pytest` module installed.
- `python3 -m py_compile tools/signature_tool.py tools/signature_pdf.py scripts/runtime/delivery_document_actions.py scripts/runtime/publish_delivery_sandbox.py scripts/runtime/ingest_delivery_events.py hermes_cli/commerce_workspace_surface.py tests/tools/test_signature_tool.py tests/test_delivery_document_actions.py tests/test_publish_delivery_sandbox_document_actions.py tests/test_commerce_workspace_surface.py` — passed with exit code 0.

## Acceptance criteria status

- Audit current signature schema, tools, PDF helper, delivery sandbox, public routes, and tests: satisfied by file-level audit above.
- Document exact gaps versus PRD in repo docs and task comments: satisfied by this document and `TRACKER.md` update in this branch.
- Confirm whether `/sign/<slug>` is routed or deprecated in favor of `/w/<token>` for V2: `/sign/<slug>` is not routed in this repo; `/w/<token>` is the only active public document workspace route, but V2 still needs OTP/signature bridging before it can satisfy Signature Core signing.

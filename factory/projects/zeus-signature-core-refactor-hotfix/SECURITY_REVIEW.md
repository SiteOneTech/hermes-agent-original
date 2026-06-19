# Security Review — Signature Core Refactor

Project: zeus-signature-core-refactor-hotfix
Owner: Jean García / SitioUno
Created: 2026-06-12T18:09:47-04:00
Status: G1 bootstrap pack complete; implementation not started
Validated: yes — initial Zeus document consistency pass
Reviewed: yes — initial Zeus Factory orchestrator review; independent quality/security review remains a project task before delivery


## Current State

Seed review. Full security review pending implementation.

## Initial Security Assessment

Risk level is **critical** because the feature handles:

- public document links;
- customer identity/contact data;
- signature images and legal/commercial approvals;
- OTP flows;
- PDF artifacts and hashes;
- private dashboard surfaces.

## Known Issues / Watchpoints

1. Existing approval handler updates request to `completed` after one approval; this is unsafe for multi-signer flows.
2. Standalone `/sign/<slug>` route must not be claimed secure until routed and tested.
3. Public container must not receive messaging secrets for OTP delivery.
4. Signature comments and field values must be validated against template fields/roles.
5. Final PDF download links must be scoped and auditable.
6. PyMuPDF/DocuSeal/OpenSign licensing must be handled carefully for commercial derivative runtime.

## Required Security Review Before Delivery

- Verify no OTP bypass for sensitive actions.
- Verify tokens are hashed and scoped per submitter.
- Verify signer cannot write fields assigned to another role.
- Verify request completion algorithm cannot be tricked by optional/viewer roles.
- Verify audit events are append-only/hash-chained.
- Verify completed artifacts include source/final hashes.
- Verify dashboard auth is required.
- Verify dependencies/licenses.

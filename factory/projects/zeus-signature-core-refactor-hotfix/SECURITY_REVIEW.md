# Security Review — T14 Signature Core Refactor + PDF Signing Collection Hotfix

Project: zeus-signature-core-refactor-hotfix
Task: T14 — Security and privacy review
Profile: security-reviewer
Run: run-1781404166-a3f32c5b
Date: 2026-06-13
Verdict: BLOCKED — security gate must not pass until rework below is integrated and re-verified.

## Scope Reviewed

Acceptance criteria reviewed:

1. Review token/OTP/public route/private dashboard/final artifact access controls.
2. Verify no AGPL code/schema copied and dependency license risks documented.
3. Block or pass security gate with concrete evidence.

Canonical documents consulted:

- `factory/projects/zeus-signature-core-refactor-hotfix/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/REQUIREMENTS_ANALYSIS.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/PATTERN_ANALYSIS.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/ADRS.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/TASK_GRAPH.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/SECURITY_GATES.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/QA_REPORT_T13.md`

Code and branches inspected:

- Current review worktree: `/home/jean/workspace/zeus-signature-core-refactor-hotfix-t14-security-review`
- Base branch under review: `factory/factory-runtime-contract-v1` at `af4abc889`
- Feature branches inspected for dependency/security drift:
  - `factory/zeus-signature-core-refactor-hotfix/t07-otp-sign-approve-reject-comment-integration` at `1acbd0629`
  - `factory/zeus-signature-core-refactor-hotfix/t10-final-pdf-stamping-certificate-hashes` at `1ab534c2d`
  - `factory/zeus-signature-core-refactor-hotfix/t11-final-copy-hash-distribution` at `4c7aad7a3`
  - `factory/zeus-signature-core-refactor-hotfix/t12-protected-private-signature-dashboard-metrics` at `2ddc75f40`

## Verification Commands Run

```bash
cd /home/jean/workspace/zeus-signature-core-refactor-hotfix-t14-security-review
git status --short --branch
git worktree list
git rev-parse --short HEAD
python -m pytest tests/tools/test_signature_tool.py tests/test_delivery_document_actions.py tests/test_publish_delivery_sandbox_document_actions.py tests/gateway/test_webhook_signature_rate_limit.py -q
git grep -n -E 'signature_dashboard_metrics|/user/signatures|signature_recipient_action_record|signature_final_copies_send|signature_completed_pdf_record|signature_request_complete|request-otp|verify-otp' -- tools scripts tests db/modules/signature factory/projects/zeus-signature-core-refactor-hotfix
git grep -n -i -E 'docuseal|opensign|pymupdf|agpl' -- ':!factory/projects/zeus-signature-core-refactor-hotfix/*' ':!docs/signature-core/*' ':!tests/skills/*' ':!optional-skills/*' ':!skills/*'
python - <<'PY'
from pathlib import Path
checks = {
 'base_signature_tool_old_completion': ('tools/signature_tool.py', "UPDATE signature.document_requests SET status='completed'"),
 'base_public_download': ('scripts/runtime/publish_delivery_sandbox.py', 'location /download/'),
 'base_user_signatures_route': ('scripts/runtime/publish_delivery_sandbox.py', '/user/signatures'),
 'base_agpl_docs': ('factory/projects/zeus-signature-core-refactor-hotfix/ADRS.md', 'AGPL'),
}
for name,(p,needle) in checks.items():
    text=Path(p).read_text(encoding='utf-8')
    print(f'{name}: {needle in text}')
PY
python - <<'PY'
from pathlib import Path
text=Path('pyproject.toml').read_text(encoding='utf-8').lower()
for dep in ['pymupdf','fitz','docuseal','opensign','pdf-lib','pdfjs','signature_pad','signature-pad']:
    print(f'{dep}: {dep in text}')
PY
```

Observed results:

- Focused tests: `12 passed in 1.22s`.
- Base branch grep:
  - `base_signature_tool_old_completion: True`
  - `base_public_download: True`
  - `base_user_signatures_route: False`
  - `base_agpl_docs: True`
- Direct dependency scan in `pyproject.toml`:
  - `pymupdf: False`
  - `fitz: False`
  - `docuseal: False`
  - `opensign: False`
  - `pdf-lib: False`
  - `pdfjs: False`
  - `signature_pad: False`
  - `signature-pad: False`
- `hermes factory status zeus-signature-core-refactor-hotfix --json` could not be used from this profile/runtime: local Hermes CLI reports `invalid choice: 'factory'`. No direct `factory.*` DB writes were attempted.

## Security Findings

### BLOCKER S1 — Final/base branch still contains single-approval completion path without signer-token/OTP enforcement

Severity: High / release blocker

Evidence:

- Current base branch `tools/signature_tool.py` still has `_handle_approval_hash_create` that accepts only `request_id` as required schema input and then executes:
  - `UPDATE signature.submitters SET status='approved' ... WHERE submitter_id=...`
  - `UPDATE signature.document_requests SET status='completed' ... WHERE request_id=...`
- The base branch has no `signature_recipient_action_record` tool and no required `signer_token`, `otp_verified`, `otp_challenge_id`, or recipient binding in the registered `signature_approval_hash_create` schema.
- T07 branch (`1acbd0629`) contains the intended hardened logic (`_require_recipient_otp`, `_load_submitter_for_token`, `OTP_REQUIRED_SIGNATURE_ACTIONS`, required `signer_token`, and all-required-signers status update), but T12 branch (`2ddc75f40`) and the current base branch show the older insecure completion path again.

Exploit scenario:

An actor or compromised tool call with access to the signature tool surface can call `signature_approval_hash_create` for a request and mark the entire document request `completed` after one approval or without proving possession of the signer’s opaque token and OTP. In a multi-signer flow this bypasses required signers/approvers and can generate/distribute a final artifact prematurely.

Required fix:

- Rebase/merge the T07 recipient-bound action model into the final integration branch.
- Make `signature_approval_hash_create` fail closed unless it receives a valid signer token and recipient-bound OTP evidence, or route approval creation exclusively through `signature_recipient_action_record`.
- Keep all-required-signer completion server-side: complete only when required signer/approver submitters are `signed` or `approved`; `declined`, `expired`, and `cancelled` must close/fail according to policy.
- Add regression tests that fail on the current base behavior:
  - approval without OTP is rejected;
  - approval with a wrong signer token is rejected;
  - one signer in a multi-required-signer request leaves request `partially_signed`, not `completed`;
  - optional viewers do not block completion.

### BLOCKER S2 — Final artifact download path is public/static and not scoped to signer/session

Severity: High / release blocker

Evidence:

- `scripts/runtime/publish_delivery_sandbox.py` NGINX config still exposes:
  - `location /download/ { autoindex off; try_files $uri =404; }`
- `SECURITY_GATES.md` requires final artifacts to use scoped download links or protected private route.
- Current code does not show a token/session authorization check on `/download/` before serving PDFs.
- T12 tool code records `completed_document_url` from `completed_pdf.public_url` or `storage_path`, but artifact access is not proven to be scoped/authenticated in the final route.

Exploit scenario:

If a completed signed PDF is published under `/download/<file>`, anyone with the URL can fetch the final signed document without signer token, OTP session, or audit event. This exposes PII/signatures and violates the scoped-artifact requirement.

Required fix:

- Remove direct public serving for completed signed PDFs/audit PDFs, or restrict `/download/` to public non-sensitive assets only.
- Add a protected route such as `/api/signature-artifacts/<artifact_id>` that verifies one of:
  - valid recipient-scoped token for that request/submitter;
  - authenticated `/user/` session for the owner;
  - short-lived signed URL whose signature is verified server-side and audited.
- Emit an audit event for every final artifact download.
- Add negative tests proving random `/download/...pdf` and wrong-token artifact requests fail.

### BLOCKER S3 — Integration state is not security-reviewable as one coherent runtime surface

Severity: Medium / release blocker for this gate

Evidence:

- T13 QA report explicitly says T10/T11/T12 branches were not merged to main/base and QA verified branch state, not the final integrated runtime.
- Current base branch lacks `/user/signatures/` route (`base_user_signatures_route: False`) even though T12 implements it on its branch.
- T12 branch appears to reintroduce the older `signature_approval_hash_create` completion path from base instead of the T07 recipient-bound OTP hardening.

Exploit scenario:

Release could cherry-pick or merge dashboard/final-copy code while silently dropping the T07 OTP/token safeguards. Reviewers would see evidence across separate branches but the deployed runtime would not have the composed protections.

Required fix:

- Create one integration branch/worktree that contains T07, T10, T11, and T12 behavior together.
- Run the focused security tests against that single branch, not against separate feature branches or docs.
- Security gate should be re-run only on the integrated branch with `git grep`/tests proving the hardened recipient action path and protected dashboard route coexist.

### WARNING S4 — OTP rate limiting exists but is process/file-local and narrow

Severity: Medium risk, not independently release-blocking if S1/S2 are fixed before production

Evidence:

- Public event server uses `OTP_RATE_LIMIT_SECONDS=45` and tracks active challenges in `EVENT_DIR/user_auth_state.json`.
- OTP verification limits challenges to fewer than 5 failed attempts via `_cleanup_state` filtering.
- The focused tests cover OTP policy and recent request logic indirectly, but there is no durable multi-process/IP/device brute-force control in the DB layer.

Exploit scenario:

Multiple event-server replicas, container restarts, or token/target variations could bypass file-local rate limiting and increase OTP brute-force or spam risk.

Recommended fix:

- Persist OTP challenge/rate-limit counters in Agent Core DB or a shared store for production-like runtime.
- Rate-limit by target, workspace token, deliverable_id, event_type, source IP, and challenge_id.
- Add tests for max attempts and replay after successful verification.

### PASS P1 — Public action endpoint enforces OTP policy for sensitive document actions

Evidence:

- `delivery_document_actions.py` defines `OTP_REQUIRED_DOCUMENT_EVENT_TYPES = {'approved','rejected','signed'}` and direct post only for comments.
- `publish_delivery_sandbox.py` rejects direct sensitive actions with `otp_required` and queues sensitive events only after `_handle_document_action_verify_otp` succeeds.
- Focused tests passed: `tests/test_delivery_document_actions.py` and `tests/test_publish_delivery_sandbox_document_actions.py`.

Caveat:

This protects the public event queue surface, but S1 remains because the core Signature tool path can still complete requests without the same proof in the current base/final surface.

### PASS P2 — Token and OTP material are not stored as plaintext in the reviewed code paths

Evidence:

- `signature.submitters` stores `token_hash_sha256`; `_handle_request_create` returns raw token only at creation time.
- Public event server stores OTP hashes as `_hash(f'{challenge_id}:{otp}')`; session cookies store only a random token client-side and hash server-side.
- Event logs store token references truncated to the first 10 chars plus ellipsis, not full token.

Caveat:

`signature_request_get` returns submitter rows including PII fields to the tool caller; keep this toolset private/admin-only and do not expose it to public or customer-facing profiles.

### PASS P3 — Private dashboard route design is OTP-session protected on T12 branch, but absent from base

Evidence:

- T12 branch `scripts/runtime/publish_delivery_sandbox.py` adds `/user/signatures/` and checks `_session_from_request` before rendering it.
- Base branch does not yet include `/user/signatures/`.

Gate interpretation:

Protected dashboard design is acceptable on the feature branch, but cannot pass the release security gate until integrated with the same hardened signature tool surface.

## License / AGPL Review

Findings:

- Project docs explicitly require pattern-only usage for DocuSeal/OpenSign/PyMuPDF and no AGPL code/schema copy (`PATTERN_ANALYSIS.md`, `ADRS.md`, `SECURITY_GATES.md`).
- Direct dependency scan of `pyproject.toml` found no direct `pymupdf`, `docuseal`, `opensign`, `pdf-lib`, `pdfjs`, or `signature_pad` dependency added in the current branch.
- Code references to DocuSeal/OpenSign in Signature Core are descriptive comments/docs, not copied implementation.
- `tools/signature_pdf.py` imports `fitz` lazily and raises if PyMuPDF is unavailable; PyMuPDF is not pinned in direct dependencies. This remains a commercial licensing decision if a runtime image includes PyMuPDF.
- `package-lock.json` contains at least one AGPL-licensed transitive/dev package elsewhere in the repo; it was not introduced by this Signature Core increment based on reviewed scope, but should remain visible in repo-wide license auditing.

License gate result:

- No evidence found of copied DocuSeal/OpenSign AGPL code/schema in the Signature Core implementation reviewed.
- PyMuPDF/fitz remains a documented commercial-runtime risk: either obtain appropriate commercial licensing for production/commercial derivative deployments or switch stamping/render QA to a permissive alternative.

## Security Gate Decision

Result: BLOCKED

The security gate cannot pass because the current final/base surface still allows a core approval path to complete a signature request without the recipient-bound token + OTP guarantees, and final artifact access is still represented by a public static `/download/` path without scoped auth/audit.

Minimum rework before re-review:

1. Integrate T07 recipient-bound OTP/token action enforcement into the same branch as T10/T11/T12.
2. Replace or protect public `/download/` access for completed signed PDFs and audit PDFs.
3. Add automated negative tests for OTP bypass, wrong-token reuse, multi-required-signer completion, artifact wrong-token/direct-download denial, and dashboard unauthenticated access.
4. Re-run security review on one coherent integration branch/worktree and record Factory gate evidence through the Factory CLI/tooling when available.

## Evidence Summary

- Focused automated tests currently pass: `12 passed in 1.22s`.
- Passing tests do not cover the release-blocking direct core-tool approval bypass or final artifact direct-download authorization gap.
- Factory CLI was unavailable in this profile (`hermes` command has no `factory` subcommand), so DB gate recording was not performed from this run.

STATE: BLOCKED
PROFILE: security-reviewer
FILES_CHANGED: factory/projects/zeus-signature-core-refactor-hotfix/SECURITY_REVIEW.md
COMMANDS_RUN: see Verification Commands Run section above
FACTORY_DB: not_updated — `hermes factory` subcommand unavailable in this runtime/profile
RESULT: Security gate blocked with concrete S1/S2/S3 findings and rework list
RISK: high — OTP/token bypass in core tool path; public final artifact route
BLOCKER: integrate security hardening and scoped artifact access before T15 release readiness
NEXT_ACTION: builder/rework owner creates a single integration branch with T07+T10+T11+T12 protections, adds negative tests, then requeues T14 security review

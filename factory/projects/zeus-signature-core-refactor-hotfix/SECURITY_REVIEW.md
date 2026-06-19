# Security Review — T14 Signature Core Refactor + PDF Signing Collection Hotfix

Project: zeus-signature-core-refactor-hotfix
Task: T14 — Security and privacy review
Profile: security-reviewer
Run: run-1781404166-a3f32c5b; rework recheck run-1781405484-ca368168; integrated rerun run-1781837606-4c045066
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

### Rework Recheck — run-1781405484-ca368168

Additional commands run from the same T14 worktree on 2026-06-13T22:53:01-04:00:

```bash
python -m pytest tests/tools/test_signature_tool.py tests/test_delivery_document_actions.py tests/test_publish_delivery_sandbox_document_actions.py tests/gateway/test_webhook_signature_rate_limit.py -q
python - <<'PY'
from pathlib import Path
checks = {
 'base_signature_tool_old_completion': ('tools/signature_tool.py', "UPDATE signature.document_requests SET status='completed'"),
 'base_public_download': ('scripts/runtime/publish_delivery_sandbox.py', 'location /download/'),
 'base_user_signatures_route': ('scripts/runtime/publish_delivery_sandbox.py', '/user/signatures'),
 'base_signature_recipient_action_record': ('tools/signature_tool.py', 'signature_recipient_action_record'),
 'base_requires_signer_token_schema': ('tools/signature_tool.py', "'signer_token'"),
 'base_agpl_docs': ('factory/projects/zeus-signature-core-refactor-hotfix/ADRS.md', 'AGPL'),
}
for name,(p,needle) in checks.items():
    text=Path(p).read_text(encoding='utf-8')
    print(f'{name}: {needle in text}')
PY
for b in factory/zeus-signature-core-refactor-hotfix/t07-otp-sign-approve-reject-comment-integration factory/zeus-signature-core-refactor-hotfix/t10-final-pdf-stamping-certificate-hashes factory/zeus-signature-core-refactor-hotfix/t11-final-copy-hash-distribution factory/zeus-signature-core-refactor-hotfix/t12-protected-private-signature-dashboard-metrics; do
  if git merge-base --is-ancestor "$b" HEAD; then echo "$b: merged_into_t14"; else echo "$b: NOT_merged_into_t14"; fi
done
```

Observed recheck results:

- Focused tests: `12 passed in 1.01s`.
- Base/review branch checks:
  - `base_signature_tool_old_completion: True`
  - `base_public_download: True`
  - `base_user_signatures_route: False`
  - `base_signature_recipient_action_record: False`
  - `base_requires_signer_token_schema: False`
  - `base_agpl_docs: True`
- Branch composition checks:
  - T07, T10, T11, and T12 are all `NOT_merged_into_t14`; no coherent integration branch/worktree was available for this rework review.
- Gate outcome is unchanged: BLOCKED. The requested rework prerequisite (single integrated runtime with T07+T10+T11+T12 plus negative tests) is still absent in the reviewed branch.

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

---

## Integrated T14R Re-review — run-1781837606-4c045066

Date: 2026-06-18T22:58:17-04:00
Reviewer: security-reviewer
Task: zeus-signature-core-refactor-hotfix-t14-security-and-privacy-review
Re-reviewed dependency branch/worktree:

- `/home/jean/workspace/.worktrees/zeus-signature-core-refactor-hotfix/t14r-main-security-rework`
- Branch: `factory/zeus-signature-core-refactor-hotfix/t14r-main-security-rework`
- Local HEAD: `5e31e4d07da6d2b60f58c1ee9afb2dba5bfc5165`
- Remote code commit: `fc643177040d7aa57ffd5390710e6660ab567729`
- Local HEAD differs from remote only in project docs (`T14R_SECURITY_REWORK_EVIDENCE.md`, `TRACKER.md`), not runtime code.

### G1 / Canonical docs consulted in this rerun

- `factory/projects/zeus-signature-core-refactor-hotfix/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/TASK_GRAPH.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/SECURITY_GATES.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/QA_REPORT_T13.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/T14R_SECURITY_REWORK_EVIDENCE.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/SECURITY_REVIEW.md`
- Runtime files inspected: `tools/signature_tool.py`, `tools/signature_pdf.py`, `scripts/runtime/delivery_document_actions.py`, `scripts/runtime/publish_delivery_sandbox.py`, `scripts/runtime/ingest_delivery_events.py`.
- Tests inspected: `tests/tools/test_signature_tool.py`, `tests/test_publish_delivery_sandbox_document_actions.py`.

### Verification commands run in rerun

```bash
cd /home/jean/workspace/.worktrees/zeus-signature-core-refactor-hotfix/t14r-main-security-rework

git status --short --branch
# ## factory/zeus-signature-core-refactor-hotfix/t14r-main-security-rework

git rev-parse HEAD
# 5e31e4d07da6d2b60f58c1ee9afb2dba5bfc5165

git rev-parse origin/factory/zeus-signature-core-refactor-hotfix/t14r-main-security-rework
# fc643177040d7aa57ffd5390710e6660ab567729

git diff --stat origin/factory/zeus-signature-core-refactor-hotfix/t14r-main-security-rework..HEAD
# 2 project-doc files changed; no runtime-code files changed.

git diff --stat main...HEAD -- tools/signature_tool.py scripts/runtime/publish_delivery_sandbox.py scripts/runtime/delivery_document_actions.py tests/tools/test_signature_tool.py tests/test_publish_delivery_sandbox_document_actions.py factory/projects/zeus-signature-core-refactor-hotfix
# 7 files changed, 1262 insertions(+), 24 deletions(-)

python -m pytest tests/tools/test_signature_tool.py tests/test_delivery_document_actions.py tests/test_publish_delivery_sandbox_document_actions.py tests/gateway/test_webhook_signature_rate_limit.py -q
# 23 passed in 1.45s

python -m compileall tools/signature_tool.py tools/signature_pdf.py scripts/runtime/publish_delivery_sandbox.py scripts/runtime/delivery_document_actions.py scripts/runtime/ingest_delivery_events.py
# exit_code=0

hermes factory gate record zeus-signature-core-refactor-hotfix security failed --task-id zeus-signature-core-refactor-hotfix-t14-security-and-privacy-review --reviewer security-reviewer --notes "..." --json
# {"gate_id": 561, "project_id": "zeus-signature-core-refactor-hotfix", "status": "failed"}
```

Additional static/proof command run with DB calls mocked, no `factory.*` writes and no live signature DB writes:

```bash
python - <<'PY'
# Mocked call into tools.signature_tool._handle_approval_hash_create with
# request_id + submitter_id only; intentionally no signer_token, no OTP fields.
# Output observed:
# approval_without_signer_token_or_otp_ok= True
# request_status= completed
# required_schema_contains_only_request_id= True
# signature_recipient_action_record_present= False
PY
```

Static control checks observed:

- `signature_approval_required_only_request_id=True`
- `signature_recipient_action_record_present=False`
- `signature_tool_requires_signer_token_string=False`
- `signature_tool_requires_otp_verified_string=False`
- `nginx_download_proxy=True`
- `nginx_download_try_files_absent_in_block=True`
- `protected_download_handler_present=True`
- `private_dashboard_session_gate_present=True`
- `pyproject_direct_pymupdf=False`
- `pyproject_direct_docuseal_opensign=False`
- Current top-level `package-lock.json`: no `ua-parser-js` / no `AGPL-3.0` matches found in this T14R worktree.

### Rerun findings

#### BLOCKER S1R — Core Signature tool still allows approval/completion without recipient-bound signer token or OTP

Severity: High / release blocker

Evidence:

- `tools/signature_tool.py:279-343` implements `_handle_approval_hash_create` without validating signer token possession, OTP verification, OTP challenge id, or recipient binding.
- `tools/signature_tool.py:971` registers `signature_approval_hash_create` with required schema `['request_id']` only.
- No `signature_recipient_action_record` tool exists in `tools/signature_tool.py`.
- Static proof with mocked DB calls returned:
  - `approval_without_signer_token_or_otp_ok=True`
  - `request_status=completed`
  - `required_schema_contains_only_request_id=True`
  - `signature_recipient_action_record_present=False`

Impact:

A private/admin tool caller, compromised agent flow, or any profile accidentally granted the `signature` toolset can create an approval hash and move a single-required-signer request to `completed` without proving possession of the opaque signer token and without OTP evidence. T14R improved the public sandbox OTP flow, but the canonical Signature Core tool path remains weaker than the public route and therefore violates the Security Gates requirement that sign/approve/reject fail closed without OTP.

Required fix before T15/release:

1. Add a recipient-bound action path to the core Signature tool layer, or harden `signature_approval_hash_create` directly.
2. Require and verify at least:
   - `signer_token` matched against `signature.submitters.token_hash_sha256` for the same `request_id`/`submitter_id`;
   - `otp_verified=True` plus non-empty `otp_challenge_id` or a server-side OTP verification artifact produced by the trusted public-event worker;
   - action type allowed for the submitter role;
   - request not expired/cancelled/completed before accepting the action.
3. Add negative tests at `tools/signature_tool.py` level:
   - approval/sign/reject without OTP => reject;
   - wrong signer token => reject;
   - signer token for another request/submitter => reject;
   - direct `signature_approval_hash_create` cannot complete a request unless recipient-bound OTP evidence is present.

#### PASS P1R — Public document action route now fails closed for direct sensitive actions

Evidence:

- `scripts/runtime/delivery_document_actions.py:24-38` defines `unlock`, `approved`, `rejected`, and `signed` as OTP-required; comments remain the only direct-post action.
- `scripts/runtime/publish_delivery_sandbox.py:1127-1181` verifies document-action OTP and stamps `otp_verified`, `otp_challenge_id`, channel id, and target hash into event metadata before queuing.
- `scripts/runtime/publish_delivery_sandbox.py:1184-1221` rejects sensitive actions without an OTP action session or OTP verification.
- Focused tests passed, including:
  - `test_generated_server_rejects_signed_action_without_otp_session`
  - `test_generated_server_rejects_wrong_signer_token_for_document_action`

Caveat: this pass applies to the public sandbox route only. It does not mitigate S1R because the core `signature_approval_hash_create` tool remains callable without equivalent proof.

#### PASS P2R — Final artifact `/download/` is no longer static-public in T14R

Evidence:

- `scripts/runtime/publish_delivery_sandbox.py:71-80` proxies `/download/` to the event server instead of serving static files with `try_files`.
- `scripts/runtime/publish_delivery_sandbox.py:936-1018` normalizes download paths, denies traversal, requires either a private dashboard OTP session or a scoped HMAC artifact token, returns `401` for direct access, `403` for wrong token, sends `Cache-Control: private, no-store`, and audits `artifact_downloaded`.
- Focused tests passed:
  - `test_generated_nginx_downloads_are_not_public_static_files`
  - `test_protected_download_rejects_direct_and_wrong_artifact_token`

#### PASS P3R — Private `/user/signatures/` dashboard is session-gated

Evidence:

- `scripts/runtime/publish_delivery_sandbox.py:703-708` redirects unauthenticated `/user/signatures/` requests to `/user/login`.
- Focused tests passed:
  - `test_signature_dashboard_requires_otp_session`
  - `test_signature_dashboard_renders_protected_metrics_and_status`

#### PASS P4R — Multi-signer completion algorithm handles required signer aggregation and optional viewers

Evidence:

- `tools/signature_tool.py:90-118` derives completion from all required signer/approver submitters only; optional viewers do not block.
- Focused tests passed:
  - `test_parallel_multi_signer_stays_partial_until_all_required_complete`
  - `test_optional_viewer_does_not_block_completion`
  - `test_approval_hash_create_updates_request_to_partial_for_remaining_required_signers`

Caveat: aggregate completion semantics are improved, but S1R remains because the direct core approval path lacks recipient-bound OTP/token enforcement.

### License / AGPL rerun result

- No evidence found of copied DocuSeal/OpenSign code or schema in runtime code or `db/modules/signature/*.sql`; code references are descriptive/product-pattern references only.
- Project docs still correctly require pattern-only use for DocuSeal/OpenSign/PyMuPDF: `PATTERN_ANALYSIS.md`, `ADRS.md`, `SECURITY_GATES.md`.
- Direct dependency scan of `pyproject.toml` found no direct `pymupdf`, `fitz`, `docuseal`, `opensign`, `pdf-lib`, `pdfjs`, `signature_pad`, or `signature-pad` dependency.
- Current top-level `package-lock.json` in the T14R worktree has no `ua-parser-js` / `AGPL-3.0` match.
- `tools/signature_pdf.py` still lazily imports `fitz`/PyMuPDF. PyMuPDF is not pinned as a direct dependency here, but remains a commercial-runtime license risk if the sandbox/runtime image includes it. Production/commercial use needs a licensing decision or a permissive fallback.

### Rerun security gate decision

Result: BLOCKED

T14R fixed the previous public `/download/` exposure and added/verified OTP/session controls on the public sandbox and private dashboard routes. However, the security gate still cannot pass because the canonical core Signature tool path can complete approval/signature state without recipient-bound signer token and OTP proof.

Minimum rework before rerun/T15:

1. Harden or replace `signature_approval_hash_create` so it fails closed without signer-token + OTP evidence.
2. Add tool-layer negative tests for missing OTP, wrong token, cross-request/cross-submitter token reuse, and direct completion bypass.
3. Keep the already-improved public `/download/`, `/api/document-actions/*`, and `/user/signatures/` protections.
4. Document PyMuPDF production licensing/fallback decision before any commercial runtime propagation.

STATE: BLOCKED
PROFILE: security-reviewer
FILES_CHANGED: factory/projects/zeus-signature-core-refactor-hotfix/SECURITY_REVIEW.md
COMMANDS_RUN: see Integrated T14R Re-review section above
FACTORY_DB: gate recorded via sanctioned `hermes factory gate record`; `security` gate failed with `gate_id=561`; wrapped `factory_gate_record` helper also returned a docker/psql execution error, so canonical CLI evidence is the gate record above
RESULT: Security gate remains blocked on S1R core tool OTP/token bypass
RISK: high
BLOCKER: core Signature approval/sign path must enforce recipient-bound signer token + OTP before release readiness
NEXT_ACTION: builder/rework owner hardens core signature tool path and adds negative tests, then requeues T14

---

## T14R2 Re-review — run-1781839591-423c94a0

Date: 2026-06-18T23:32:26-04:00
Reviewer: security-reviewer
Task: zeus-signature-core-refactor-hotfix-t14-security-and-privacy-review
Re-reviewed dependency branch/worktree:

- `/home/jean/workspace/.worktrees/zeus-signature-core-refactor-hotfix/t14r2-core-approval-token-otp`
- Branch: `factory/zeus-signature-core-refactor-hotfix/t14r2-core-approval-token-otp`
- HEAD: `509c133bf7bb80041d76d9098739661d8b1ec48d`

### G1 / canonical docs consulted in this rerun

- `factory/projects/zeus-signature-core-refactor-hotfix/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/REQUIREMENTS_ANALYSIS.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/PATTERN_ANALYSIS.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/ADRS.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/TASK_GRAPH.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/SECURITY_GATES.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/QA_GATES.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/QA_REPORT.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/T14R_SECURITY_REWORK_EVIDENCE.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/T14R2_CORE_APPROVAL_OTP_TOKEN_HARDENING_EVIDENCE.md`
- Runtime files inspected: `tools/signature_tool.py`, `tools/signature_pdf.py`, `scripts/runtime/delivery_document_actions.py`, `scripts/runtime/publish_delivery_sandbox.py`, `scripts/runtime/ingest_delivery_events.py`, `db/modules/signature/000001_signature_schema.sql`, `db/modules/signature/000002_signature_security_rework.sql`.
- Tests inspected: `tests/tools/test_signature_tool.py`, `tests/test_publish_delivery_sandbox_document_actions.py`.

### Verification commands run in rerun

```bash
cd /home/jean/workspace/.worktrees/zeus-signature-core-refactor-hotfix/t14r2-core-approval-token-otp

git status --short && git rev-parse HEAD && git branch --show-current
# clean worktree
# HEAD=509c133bf7bb80041d76d9098739661d8b1ec48d
# BRANCH=factory/zeus-signature-core-refactor-hotfix/t14r2-core-approval-token-otp

python -m pytest tests/tools/test_signature_tool.py tests/tools/test_signature_pdf.py tests/test_delivery_document_actions.py tests/test_publish_delivery_sandbox_document_actions.py tests/test_delivery_event_ingest.py tests/test_user_dashboard_otp_dispatcher.py tests/test_commerce_workspace_surface.py -q
# 48 passed in 2.72s

python -m compileall tools/signature_tool.py tools/signature_pdf.py scripts/runtime/publish_delivery_sandbox.py scripts/runtime/delivery_document_actions.py scripts/runtime/ingest_delivery_events.py
# exit_code=0

git grep -n -i -E 'docuseal|opensign|pymupdf|agpl' -- tools db/modules/signature scripts/runtime pyproject.toml factory/projects/zeus-signature-core-refactor-hotfix | cat
# Runtime/code hits: descriptive comments in tools/signature_tool.py and lazy `fitz` error in tools/signature_pdf.py.
# DB schema hits: none under db/modules/signature.
# Project docs hits: expected pattern/license-risk documentation in ADRS/PATTERN/SECURITY/QA docs.
```

Additional static checks run:

```bash
signature_tool_requires_signer_token=true
signature_tool_requires_otp_verified=true
signature_tool_authorizes_before_insert=true
protected_download_handler=true
private_dashboard_route=true
document_action_otp_endpoint=true
otp_outbox_message_field=true
direct_pymupdf_pyproject=false
direct_docuseal_pyproject=false
direct_opensign_pyproject=false
```

### Rerun findings

#### PASS P1R2 — Core approval path now requires submitter-bound signer token + OTP proof before approval insert

Evidence:

- `tools/signature_tool.py:131-154` adds `_authorize_approval_completion()` before any approval insert/status update. Public/customer completions require `submitter_id`, raw `signer_token` matching `signature.submitters.token_hash_sha256`, and OTP proof (`otp_verified` plus `otp_challenge_id`/`otp_session_id`/`otp_verification_id`).
- `tools/signature_tool.py:346-355` calls `_authorize_approval_completion()` before constructing/inserting the approval.
- `tools/signature_tool.py:1036` updates the tool schema/description with `signer_token`, OTP evidence, and privileged-completion fields.
- Focused tests passed:
  - `test_approval_hash_create_rejects_request_id_only`
  - `test_approval_hash_create_rejects_submitter_without_otp`
  - `test_approval_hash_create_rejects_wrong_signer_token`
  - `test_parallel_multi_signer_stays_partial_until_all_required_complete`
  - `test_optional_viewer_does_not_block_completion`
  - `test_approval_hash_create_updates_request_to_partial_for_remaining_required_signers`

#### PASS P2R2 — Public action route, protected final artifact route, and private dashboard controls remain present

Evidence:

- `scripts/runtime/delivery_document_actions.py:24-38` keeps `unlock`, `approved`, `rejected`, and `signed` as OTP-required; comments remain the only direct post.
- `scripts/runtime/publish_delivery_sandbox.py:1084-1181` implements document-action OTP request/verification and queues sensitive events only after OTP validation.
- `scripts/runtime/publish_delivery_sandbox.py:1184-1221` rejects direct sensitive actions without OTP/action session.
- `scripts/runtime/publish_delivery_sandbox.py:972-1018` protects `/download/` with private `/user/` session or scoped artifact HMAC token and emits `artifact_downloaded` audit events.
- `tests/test_publish_delivery_sandbox_document_actions.py` passed direct/wrong-token artifact denial, signed-without-OTP denial, wrong signer token denial, and unauthenticated `/user/signatures/` redirect checks.

#### BLOCKER S1R2 — Core approval path still does not fail closed for cancelled/completed terminal request status

Severity: High / release blocker

Evidence:

- `SECURITY_GATES.md` requires expired/cancelled/completed requests to reject actions.
- `_authorize_approval_completion()` validates signer token and OTP proof but does not receive or inspect request lifecycle status.
- `_derive_request_lifecycle()` returns `completed=True` immediately when `current_status == "completed"` and can still derive `completed` for a `cancelled` request when all required submitters become complete; there is no pre-insert reject for terminal statuses before `INSERT INTO signature.approvals`.
- `tests/tools/test_signature_tool.py` includes negative tests for missing token/OTP and wrong token, but no negative tests for approving/signing after `completed`, `cancelled`, `expired`, or `declined` request status.

Impact:

A stale/replayed signer token + OTP proof, or any internal caller with an old payload, can still append approval/sign events and update request state after cancellation/completion instead of hard-failing. This violates the explicit Security Gate fail-closed rule for terminal statuses.

Required fix before gate pass:

1. Add a pre-insert lifecycle guard in `_handle_approval_hash_create()` before `_authorize_approval_completion()` or immediately after loading `request`.
2. Reject `status IN ('completed','cancelled','expired','declined')` unless a separately reviewed admin-only void/reopen operation is being performed.
3. Add regression tests proving approval/sign/reject fails for completed, cancelled, expired, and declined requests and does not insert approvals/events.

#### BLOCKER S2R2 — OTP plaintext is persisted in the public event outbox

Severity: High / release blocker unless explicitly waived with a different OTP delivery architecture

Evidence:

- `SECURITY_GATES.md` requires OTP hashes only and no plaintext code persistence.
- `scripts/runtime/publish_delivery_sandbox.py:541-557` writes `otp_outbox.jsonl` with a `message` field that contains the OTP (`challenge.get("message")` or default text including `{otp}`).
- `scripts/runtime/publish_delivery_sandbox.py:736-745` and `1056-1080` correctly store `otp_hash` in challenge state, but `_queue_otp()` persists the plaintext delivery message for dispatcher pickup.
- Static check result: `otp_outbox_message_field=true`.
- The outbox file is in the public event server writable `EVENT_DIR`; unlike `user_auth_state.json`, `_queue_otp()` does not set owner-only permissions or a purge-on-dispatch contract in this code path.

Impact:

If the public sandbox container, mounted event directory, logs/backups, or dispatcher handoff is exposed, valid OTP values can be recovered from `otp_outbox.jsonl` during the OTP TTL and possibly after, depending on retention. This directly contradicts the project’s OTP hash-only requirement.

Required fix before gate pass:

1. Stop persisting plaintext OTP in the public sandbox. Preferred: move OTP generation/sending to the trusted dispatcher or use an encrypted one-time handoff that the public server cannot read back.
2. If a transition design keeps a handoff file, make it explicitly temporary, owner-only (`0600`), encrypted or sealed to the dispatcher, and purged after dispatch; then update `SECURITY_GATES.md`/ADR if Jean accepts that exception.
3. Add regression/static tests proving no plaintext OTP appears in durable state/outbox/log files.

#### BLOCKER S3R2 — Privileged OTP bypass is caller-declared, not enforced by a trusted runtime boundary

Severity: Medium/High / release blocker unless the tool schema is restricted to a proven trusted caller

Evidence:

- `tools/signature_tool.py:101-105` treats `internal_completion=true` or `privileged_completion=true` plus caller-supplied `actor_type in {'system','agent','adapter','owner'}` as a bypass for signer token + OTP proof.
- `tools/signature_tool.py:141-142` returns from `_authorize_approval_completion()` on that bypass path before token/OTP validation.
- The fields are exposed in the public `signature_approval_hash_create` tool schema at `tools/signature_tool.py:1036`; the reviewed code does not bind this bypass to a server-side principal, capability token, DB role, or non-model internal API.

Impact:

Any model/tool caller that can invoke `signature_approval_hash_create` can self-declare `actor_type='agent'` with `internal_completion=true` and bypass the OTP/signer-token requirement. This weakens the T14R2 fix unless the signature toolset is guaranteed to be available only to a trusted internal runtime and the bypass path is hidden from public/customer profiles.

Required fix before gate pass:

1. Remove privileged bypass fields from the model-facing tool schema, or split privileged completion into a separate non-public internal API/tool gated by server-side identity.
2. If retained, verify an unforgeable trusted runtime signal, not just caller-supplied `actor_type`.
3. Add a negative test proving untrusted/public/customer/tool callers cannot set `internal_completion` to bypass signer token + OTP.

### License / AGPL rerun result

- No evidence found of copied DocuSeal/OpenSign code or schema in `tools/`, `scripts/runtime/`, or `db/modules/signature/`.
- Project docs correctly document DocuSeal/OpenSign/PyMuPDF as pattern/license-risk sources only: `PATTERN_ANALYSIS.md`, `ADRS.md`, `SECURITY_GATES.md`, `QA_REPORT_T13.md`, `QUALITY_REVIEW.md`.
- Direct dependency checks found `direct_pymupdf_pyproject=false`, `direct_docuseal_pyproject=false`, and `direct_opensign_pyproject=false`.
- `tools/signature_pdf.py` still lazily imports `fitz`/PyMuPDF. PyMuPDF is not a direct pinned dependency in `pyproject.toml`, but commercial runtime propagation still needs either a PyMuPDF commercial license/waiver or a permissive fallback before T15 production decision.

### T14R2 security gate decision

Result: BLOCKED

T14R2 resolved the previous direct core approval bypass for normal public/customer completions and preserved the protected `/download/`, `/api/document-actions/*`, and `/user/signatures/` controls. The security gate still cannot pass because terminal request statuses do not fail closed before approval insertion, OTP plaintext is durably queued in the public outbox, and the privileged-completion bypass is only caller-declared.

Minimum rework before rerun/T15:

1. Reject approval/sign/reject for terminal request statuses before approval/event insertion and add negative tests.
2. Remove durable plaintext OTP from the public event outbox or obtain/document an explicit accepted exception with encryption, purge, and permission controls.
3. Remove or server-side-gate the `internal_completion`/`privileged_completion` bypass so it cannot be model/tool-caller forged.
4. Preserve the already-passing token/OTP normal path, protected artifact route, private dashboard, and AGPL/license documentation.

STATE: BLOCKED
PROFILE: security-reviewer
FILES_CHANGED: factory/projects/zeus-signature-core-refactor-hotfix/SECURITY_REVIEW.md
COMMANDS_RUN: see T14R2 Re-review section above
FACTORY_DB: gate recorded via sanctioned `hermes factory gate record`; `security` gate failed with `gate_id=567`
RESULT: Security gate remains blocked on terminal-status fail-closed, plaintext OTP outbox, and caller-declared privileged bypass
RISK: high
BLOCKER: resolve S1R2/S2R2/S3R2 before T15 release readiness/runtime propagation
NEXT_ACTION: builder/rework owner patches Signature Core approval lifecycle guard + OTP handoff + privileged bypass boundary, adds negative tests, then requeues T14

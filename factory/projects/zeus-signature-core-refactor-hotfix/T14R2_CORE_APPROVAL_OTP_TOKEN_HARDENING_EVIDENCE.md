# T14R2 — Core approval OTP token hardening evidence

Project: zeus-signature-core-refactor-hotfix
Task: zeus-signature-core-refactor-hotfix-t14r2-core-approval-otp-token-hardening
Branch/worktree: `factory/zeus-signature-core-refactor-hotfix/t14r2-core-approval-token-otp`
Recorded: 2026-06-18T23:23:43-04:00
Engine: claude_code via `claude-anthropic-code` session `9d94ed76-2767-4b81-89a3-0d75d20b94a4`

## Canonical docs read

- `factory/projects/zeus-signature-core-refactor-hotfix/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/REQUIREMENTS_ANALYSIS.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/PATTERN_ANALYSIS.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/ADRS.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/TASK_GRAPH.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/SECURITY_GATES.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/SECURITY_REVIEW.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/T14R_SECURITY_REWORK_EVIDENCE.md`

## Implementation summary

- Hardened `tools/signature_tool.py` so `_handle_approval_hash_create` performs authorization before any approval insert, submitter status update, request completion, or audit event write.
- Public/customer approval completion now requires:
  - `submitter_id`;
  - raw `signer_token` whose SHA-256 matches `signature.submitters.token_hash_sha256` for the same `request_id` and `submitter_id`;
  - OTP proof: `otp_verified=true` plus challenge/session/verifier evidence (`otp_challenge_id`, `otp_session_id`, or `otp_verification_id`).
- Added an explicit internal-only privileged path: `internal_completion=true` or `privileged_completion=true` with trusted `actor_type` (`system`, `agent`, `adapter`, or `owner`). Without that explicit flag, request_id/submitter_id-only calls are rejected.
- Preserved multi-signer lifecycle semantics: one required signer leaves the request `partially_signed`, and optional viewers do not block completion.
- Updated the `signature_approval_hash_create` tool schema with `signer_token`, OTP proof fields, and privileged-path flags.

## Acceptance mapping

1. Core path rejects `request_id`/`submitter_id`-only calls:
   - Added `test_approval_hash_create_rejects_request_id_only`.
   - Existing partial-completion test now supplies signer token + OTP proof.
2. Recipient-bound signer token + OTP proof required:
   - Added `test_approval_hash_create_rejects_submitter_without_otp`.
   - Added `test_approval_hash_create_rejects_wrong_signer_token`.
   - Positive deterministic approval hash test now uses matching `signer_token` and OTP proof.
3. Multi-signer completion remains safe:
   - `test_parallel_multi_signer_stays_partial_until_all_required_complete` passes.
   - `test_approval_hash_create_updates_request_to_partial_for_remaining_required_signers` passes.
   - `test_optional_viewer_does_not_block_completion` passes.
4. Focused Signature/document action tests pass and compileall succeeds:
   - See verification below.
5. T14 security review handoff:
   - T14 should be requeued against this branch/commit after push.
   - T15 remains blocked until a security reviewer records a passing security gate.

## Verification executed

```bash
python -m pytest tests/tools/test_signature_tool.py -q
# RED before implementation: 3 failed, 7 passed; failures showed approval insert was reached before token/OTP validation.

python -m pytest tests/tools/test_signature_tool.py tests/tools/test_signature_pdf.py tests/test_delivery_document_actions.py tests/test_publish_delivery_sandbox_document_actions.py -q
# 25 passed in 1.41s

python -m pytest tests/tools/test_signature_tool.py tests/tools/test_signature_pdf.py tests/test_delivery_document_actions.py tests/test_publish_delivery_sandbox_document_actions.py tests/test_delivery_event_ingest.py tests/test_user_dashboard_otp_dispatcher.py tests/test_commerce_workspace_surface.py -q
# 48 passed in 2.83s

python -m compileall tools/signature_tool.py tools/signature_pdf.py scripts/runtime/publish_delivery_sandbox.py scripts/runtime/delivery_document_actions.py
# exit_code=0
```

## Files changed

- `tools/signature_tool.py`
- `tests/tools/test_signature_tool.py`
- `factory/projects/zeus-signature-core-refactor-hotfix/T14R2_CORE_APPROVAL_OTP_TOKEN_HARDENING_EVIDENCE.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/DOCUMENTATION_INDEX.md`

## Remaining gate handoff

- Requeue T14 security/privacy review for `zeus-signature-core-refactor-hotfix-t14-security-and-privacy-review` after this branch is pushed.
- Do not unblock T15 release/runtime propagation until a security reviewer records a passing T14 security gate.
- No production deploy, credential change, or main merge was performed by this increment.

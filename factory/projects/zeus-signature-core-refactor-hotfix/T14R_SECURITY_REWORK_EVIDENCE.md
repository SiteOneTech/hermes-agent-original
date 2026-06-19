# T14R — Integrated signature security rework evidence

Project: zeus-signature-core-refactor-hotfix
Task: T14R Integrated signature security rework before T14 rerun
Branch/worktree: `factory/zeus-signature-core-refactor-hotfix/t14r-main-security-rework`
Recorded: 2026-06-18T22:45:47-04:00

## Canonical docs read

- `factory/projects/zeus-signature-core-refactor-hotfix/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/REQUIREMENTS_ANALYSIS.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/PATTERN_ANALYSIS.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/ADRS.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/TASK_GRAPH.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/SECURITY_GATES.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/QA_GATES.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/QUALITY_REVIEW.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/SECURITY_REVIEW.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/TRACKER.md`

## Implementation summary

- Integrated Signature Core tool runtime containing T07/T10/T11/T12 behavior in `tools/signature_tool.py` and `tools/signature_pdf.py`.
- Preserved OTP-protected signer action contract in `scripts/runtime/publish_delivery_sandbox.py` and added negative tests for signing without OTP and wrong signer token.
- Reworked multi-signer lifecycle so required signer/approver completion is aggregated before `signature.document_requests` moves to `completed`; optional viewers do not block completion.
- Added completed PDF + audit PDF recording, multi-field PDF stamping metadata, final copy delivery receipts, hash validation summaries, retry/escalation evidence, and private signature dashboard metrics.
- Replaced public `/download/` static exposure with event-server protected downloads. Signed/audit artifacts now require a private dashboard OTP session or a scoped `artifact_token`; direct access and wrong artifact tokens are denied.
- Added DB migration `db/modules/signature/000002_signature_security_rework.sql` for required submitter/lifecycle columns, reminder/final-copy receipt tables, indexes and expanded event type constraints used by the integrated runtime.

## Acceptance mapping

1. Single integrated branch/worktree with T07 + T10 + T11 + T12:
   - Branch: `factory/zeus-signature-core-refactor-hotfix/t14r-main-security-rework`.
   - Runtime files changed: `tools/signature_tool.py`, `tools/signature_pdf.py`, `scripts/runtime/publish_delivery_sandbox.py`.
2. OTP + recipient-bound signer token enforcement in same runtime as stamping/final-copy/dashboard:
   - OTP and token enforcement: `scripts/runtime/publish_delivery_sandbox.py`.
   - PDF stamping/final-copy/dashboard: `tools/signature_pdf.py`, `tools/signature_tool.py`, `scripts/runtime/publish_delivery_sandbox.py`.
3. `/download/` for signed/audit PDFs removed or protected:
   - `NGINX_CONF` now proxies `/download/` to the event server.
   - `_handle_protected_download()` enforces OTP session or scoped artifact token.
4. Negative tests added:
   - no OTP reject: `test_generated_server_rejects_signed_action_without_otp_session`
   - wrong signer token reject: `test_generated_server_rejects_wrong_signer_token_for_document_action`
   - one required signer does not complete multi-signer request: `test_parallel_multi_signer_stays_partial_until_all_required_complete` and `test_approval_hash_create_updates_request_to_partial_for_remaining_required_signers`
   - optional viewers do not block completion: `test_optional_viewer_does_not_block_completion`
   - direct/wrong-token artifact download denied: `test_protected_download_rejects_direct_and_wrong_artifact_token`
   - `/user/signatures/` without session denied: `test_signature_dashboard_requires_otp_session`
5. T14 rerun readiness:
   - Factory DB task close/reconcile re-queued T14; `hermes factory status zeus-signature-core-refactor-hotfix --json` showed `zeus-signature-core-refactor-hotfix-t14-security-and-privacy-review` as `running` after T14R close.

## Verification executed

```bash
python -m pytest tests/tools/test_signature_tool.py tests/tools/test_signature_pdf.py tests/test_delivery_document_actions.py tests/test_publish_delivery_sandbox_document_actions.py -q
# 22 passed in 1.30s

python -m pytest tests/tools/test_signature_tool.py tests/tools/test_signature_pdf.py tests/test_delivery_document_actions.py tests/test_publish_delivery_sandbox_document_actions.py tests/test_delivery_event_ingest.py tests/test_user_dashboard_otp_dispatcher.py tests/test_commerce_workspace_surface.py -q
# 45 passed in 2.90s

python -m compileall tools/signature_tool.py tools/signature_pdf.py scripts/runtime/publish_delivery_sandbox.py scripts/runtime/delivery_document_actions.py
# exit_code=0
```

## Remaining gate handoff

- T14 security/privacy review should be re-run by the next reviewer against the pushed T14R branch.
- No production deploy or credential change was performed.

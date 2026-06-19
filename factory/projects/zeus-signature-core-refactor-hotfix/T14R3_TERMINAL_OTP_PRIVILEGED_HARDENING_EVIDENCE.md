# T14R3 — Terminal state, OTP outbox, and privileged bypass hardening evidence

Project: zeus-signature-core-refactor-hotfix
Task: zeus-signature-core-refactor-hotfix-t14r3-terminal-state-otp-outbox-and-priv
Branch/worktree: `factory/zeus-signature-core-refactor-hotfix/t14r3-terminal-otp-privileged-hardening`
Recorded: 2026-06-18T23:53:25-04:00
Base lineage: current `main` after T14R2 merge (`f8fc5a5e9` at start)
Engine: claude_code invoked via `claude-anthropic-code` smoke session `6434dee0-e966-46dd-a7e2-07124297d199`; implementation prompt session `5993f4c0-416c-48a3-9c2a-eed17d200538` reached max_turns without production edits, then Hermes builder completed the scoped patch in the assigned worktree.

## Canonical docs read

- `factory/projects/zeus-signature-core-refactor-hotfix/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/REQUIREMENTS_ANALYSIS.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/PATTERN_ANALYSIS.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/ADRS.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/TASK_GRAPH.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/SECURITY_GATES.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/T14R2_CORE_APPROVAL_OTP_TOKEN_HARDENING_EVIDENCE.md`

## Implementation summary

- Hardened `tools/signature_tool.py` with a terminal request status guard for `completed`, `cancelled`, `expired`, and `declined`.
  - `signature_approval_hash_create` now rejects terminal requests immediately after loading the request and before approval insert, submitter/request status updates, or audit event writes.
  - `signature_event_record` now rejects sensitive direct event writes (`signed`, `approved`, `rejected` plus aliases) when the request is terminal, before the chained event insert.
- Removed model-facing `internal_completion` / `privileged_completion` bypass arguments from the `signature_approval_hash_create` schema and ignored caller-supplied privileged flags in authorization. Normal tool callers must provide submitter-bound `signer_token` plus OTP proof.
- Hardened generated delivery sandbox server in `scripts/runtime/publish_delivery_sandbox.py`:
  - `otp_outbox.jsonl` no longer persists plaintext OTP codes or plaintext delivery messages.
  - Outbox rows now carry safe dispatch/reference metadata: `dispatch_ref`, `message_template`, `message_context`, `target_hash`, challenge/reference fields.
  - Document-action challenge state no longer stores a plaintext OTP message containing the code.
  - Approve/sign/reject document actions fail closed on terminal workspace/request status before OTP request, before verified OTP event queue, and before unlocked-session action queue.

## RED evidence before implementation

Command:

```bash
python -m pytest tests/tools/test_signature_tool.py::test_approval_hash_create_rejects_terminal_request_before_mutations tests/tools/test_signature_tool.py::test_approval_hash_create_rejects_caller_declared_privileged_bypass tests/tools/test_signature_tool.py::test_signature_approval_hash_schema_does_not_expose_privileged_bypass_args tests/tools/test_signature_tool.py::test_event_record_rejects_terminal_signed_event_before_event_write tests/test_publish_delivery_sandbox_document_actions.py::test_generated_server_queue_otp_omits_plaintext_code_and_message tests/test_publish_delivery_sandbox_document_actions.py::test_generated_server_document_action_challenge_state_omits_plaintext_message_and_otp tests/test_publish_delivery_sandbox_document_actions.py::test_generated_server_rejects_terminal_document_action_before_otp_outbox tests/test_publish_delivery_sandbox_document_actions.py::test_generated_server_revalidates_terminal_status_before_verified_action_queue tests/test_publish_delivery_sandbox_document_actions.py::test_generated_server_document_action_unlock_session_rejects_terminal_workspace_action -q
```

Result: `9 failed in 0.94s`.

Expected failing assertions showed:

- approval write path reached instead of terminal-status rejection;
- caller-declared privileged flags reached approval insert instead of signer_token+OTP validation;
- schema still exposed `internal_completion`;
- direct signed event reached event insert on terminal request;
- OTP outbox contained plaintext `123456` and `Código para aprobar`;
- challenge state contained plaintext `Tu código ... <otp> ... Expira en 10 minutos`;
- terminal document-action handlers returned `202` instead of `409 terminal_document_status`.

## GREEN verification executed

```bash
python -m pytest tests/tools/test_signature_tool.py::test_approval_hash_create_rejects_terminal_request_before_mutations tests/tools/test_signature_tool.py::test_approval_hash_create_rejects_caller_declared_privileged_bypass tests/tools/test_signature_tool.py::test_signature_approval_hash_schema_does_not_expose_privileged_bypass_args tests/tools/test_signature_tool.py::test_event_record_rejects_terminal_signed_event_before_event_write tests/test_publish_delivery_sandbox_document_actions.py::test_generated_server_queue_otp_omits_plaintext_code_and_message tests/test_publish_delivery_sandbox_document_actions.py::test_generated_server_document_action_challenge_state_omits_plaintext_message_and_otp tests/test_publish_delivery_sandbox_document_actions.py::test_generated_server_rejects_terminal_document_action_before_otp_outbox tests/test_publish_delivery_sandbox_document_actions.py::test_generated_server_revalidates_terminal_status_before_verified_action_queue tests/test_publish_delivery_sandbox_document_actions.py::test_generated_server_document_action_unlock_session_rejects_terminal_workspace_action -q
# 9 passed in 0.73s

python -m pytest tests/tools/test_signature_tool.py tests/tools/test_signature_pdf.py tests/test_delivery_document_actions.py tests/test_publish_delivery_sandbox_document_actions.py tests/test_delivery_event_ingest.py tests/test_user_dashboard_otp_dispatcher.py tests/test_commerce_workspace_surface.py -q
# 56 passed in 3.30s

python -m compileall tools/signature_tool.py tools/signature_pdf.py scripts/runtime/publish_delivery_sandbox.py scripts/runtime/delivery_document_actions.py
# exit_code=0
```

## Files changed

- `tools/signature_tool.py`
- `scripts/runtime/publish_delivery_sandbox.py`
- `tests/tools/test_signature_tool.py`
- `tests/test_publish_delivery_sandbox_document_actions.py`
- `factory/projects/zeus-signature-core-refactor-hotfix/T14R3_TERMINAL_OTP_PRIVILEGED_HARDENING_EVIDENCE.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/DOCUMENTATION_INDEX.md`

## Acceptance mapping

1. Terminal status fail-closed before mutations:
   - `test_approval_hash_create_rejects_terminal_request_before_mutations`
   - `test_event_record_rejects_terminal_signed_event_before_event_write`
   - document action terminal tests for pre-OTP, verified OTP, and unlocked-session queues.
2. OTP outbox no plaintext OTP/message:
   - `test_generated_server_queue_otp_omits_plaintext_code_and_message`
   - `test_generated_server_document_action_challenge_state_omits_plaintext_message_and_otp`
3. Privileged bypass hardening:
   - `test_approval_hash_create_rejects_caller_declared_privileged_bypass`
   - `test_signature_approval_hash_schema_does_not_expose_privileged_bypass_args`
4. Focused regression tests and compileall pass:
   - 56 focused tests passed; compileall exit code 0.
5. T14/T15 handoff:
   - Requeue T14 security/privacy review against this branch/commit after push.
   - T15 remains blocked until a security reviewer records a passing T14 security gate.

## Remaining gate handoff

- No production deploy, credential change, or main merge was performed.
- T14 security review must be rerun/requeued for `zeus-signature-core-refactor-hotfix-t14-security-and-privacy-review`.
- T15 release/runtime propagation remains blocked until the security gate passes.

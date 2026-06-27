# Closure Reconciliation — Zeus Signature Core Refactor + PDF Signing Collection Hotfix

Project: `zeus-signature-core-refactor-hotfix`  
Date: 2026-06-27T00:03:00Z  
Owner: Jean García / SitioUno  
Decision owner: Zeus Factory Orchestrator

## Executive Decision

**Keep and close the current Signature Core v2 implementation on `main`. Do not merge/restore the old legacy branches.**

Reason: the current implementation is the only path aligned with the Agent Core module architecture and the canonical SitioUno document workspace:

- DB schema: `signature.*` tables in the shared Agent Core database.
- Tools: `tools/signature_tool.py` registered under the `signature` toolset.
- Public/private surface: canonical `/w/<token>/` workspace, `/api/document-actions*`, and private `/user/signatures/` dashboard.
- Security: submitter-bound `signer_token` + OTP proof are required for public/customer completion; model-facing privileged bypass is not accepted.
- PDF artifacts: completed/audit PDFs are recorded as `signature.attachments` with SHA-256 evidence.

## Legacy / overlap audit

| Candidate | Finding | Decision |
|---|---|---|
| SEIS / inscripción electrónica | `git grep` excluding generated deps only found the Spanish word “Seis” in README prose and MIME database references in ignored/generated dependencies. No active SEIS signing module, route, schema, or runtime path exists in Zeus repo. | No overlap. Nothing to merge. |
| Superform router | No active Superform implementation was found in current `main` for Signature/PDF signing. Previous issue was historical routing concern, not current runtime code. | Do not revive. |
| Standalone `/sign/<slug>` | Documented as not canonical until fully routed as an alias. Current secure path is `/w/<token>/` + OTP document actions. | Keep disabled/not primary. Future `/sign` must alias the same workflow, not a second implementation. |
| Legacy `factory/factory-runtime-contract-v1` / old Signature branches | Historical tracker notes show direct merge would reintroduce broad stale diffs outside Signature Core. | Do not merge. Port only missing behavior into `main`. |

## Code / runtime closure changes

To remove the last real propagation gap, Signature Core is now wired as a first-class Agent Core module:

- Added `signature` to `scripts/agent_core_db.py` migration runner/status DB set.
- Added `signature_runtime` to core runtime role shells and runtime config examples.
- Added Signature DB URL/password derivation support in `hermes_cli/agent_core_sql.py` and `scripts/zeus-sync-secrets.sh`.
- Kept `SIGNATURE_DB_RUNTIME_PASSWORD` optional for older Infisical projects; local Hermes tools already operate through docker-exec `psql` and the migration-created `signature_runtime` role. Once the secret exists, `agent_core_roles.py` rotates it like the other module roles.
- Expanded `toolsets.py` so the public `signature` toolset lists the full canonical v2 surface: reminders, delivery receipts, completed PDF record, final copies, and dashboard metrics.
- Added regression tests in `tests/scripts/test_signature_runtime_wiring.py`.

## Verification evidence

### Static overlap audit

Command:

```bash
git grep -n -i -E 'superform|\bSEIS\b|servicio de inscripción|servicio de inscripcion|inscripción electrónica|inscripcion electronica' -- ':!website/build' ':!website/static/api/skills*.json' ':!website/node_modules' ':!node_modules' ':!scripts/whatsapp-bridge/node_modules' ':!venv'
```

Result: only README prose occurrence (`Seis backends de terminal`). No active signing implementation overlap.

### Automated tests

Command:

```bash
python -m pytest tests/tools/test_signature_tool.py tests/tools/test_signature_pdf.py tests/test_delivery_document_actions.py tests/test_publish_delivery_sandbox_document_actions.py tests/test_delivery_event_ingest.py tests/test_user_dashboard_otp_dispatcher.py tests/test_commerce_workspace_surface.py tests/test_sitiouno_document_workspace_template.py tests/scripts/test_signature_runtime_wiring.py -q -o addopts=
```

Result:

```text
61 passed in 3.26s
```

### Compile verification

Command:

```bash
python -m compileall -q tools/signature_tool.py tools/signature_pdf.py scripts/runtime/publish_delivery_sandbox.py scripts/runtime/delivery_document_actions.py scripts/agent_core_db.py scripts/agent_core_roles.py hermes_cli/agent_core_sql.py toolsets.py
```

Result: pass, no output.

### Live DB migration verification

Command:

```bash
python scripts/agent_core_db.py migrate
python scripts/agent_core_db.py status
```

Result:

```text
signature:000001 applied
signature:000002 applied
zeus_agent|signature|000001|2026-06-26 23:57:10.943122+00
zeus_agent|signature|000002|2026-06-26 23:57:11.422736+00
```

Live schema check:

```text
signature_migrations = 000001,000002
tables = approvals,attachments,delivery_receipts,document_requests,events,reminder_attempts,reminder_policies,submitters,templates
document_request_has_v2_cols = true
v2_tables_exist = 3
```

### Live Signature Core smoke

Executed against local Agent Core Postgres through `signature_runtime`:

- Created template and two-required-party document request.
- Verified approval without valid submitter token is rejected.
- First required signer + OTP proof → `partially_signed`.
- Second required approver + OTP proof → `completed`.
- Recorded completed PDF and audit PDF artifacts with SHA-256 values.
- Sent final copy receipts to both submitters.
- Read private dashboard metrics.
- Cleaned QA rows from live DB afterwards.

Result excerpt:

```text
approval_without_token_rejected ok=None error=signer_token does not match the submitter token_hash_sha256
approval_first_required ok=True status=partially_signed
approval_second_required ok=True status=completed
completed_pdf_record ok=True
final_copies ok=True
dashboard_metrics ok=True
live_request_status {'status': 'completed', 'audit_url': 'https://zeus-sandbox.kidu.app/download/qa-audit.pdf', 'completed_document_url': 'https://zeus-sandbox.kidu.app/download/qa-completed.pdf'}
cleanup_remaining {'events': 0, 'receipts': 0, 'requests': 0, 'attachments': 0}
```

## Closure disposition

- `security`: passed — previous T14R/T14R2/T14R3 hardening remains valid and live smoke confirms fail-closed OTP/token behavior.
- `critical_readiness`: passed — canonical module now migrates and resolves in live Agent Core DB; toolset exposes the complete v2 surface.
- `delivery`: waived/passed for public sandbox requirement — Jean explicitly stated the surface is private/VPN-only and does not need public PASS. Runtime evidence is internal/live, not fabricated.

**Final state:** complete. No SEIS/Superform overlap. No legacy branch merge needed. No pending human question.

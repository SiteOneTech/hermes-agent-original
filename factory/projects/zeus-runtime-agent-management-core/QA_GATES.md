---
project_id: zeus-runtime-agent-management-core
project_name: Zeus Runtime Agent Management Core
validated: yes
reviewed: yes
status: draft-ready
---

# QA Gates

## Gate QA-001 — Documentation readiness
- All G1 docs exist.
- `DOCUMENTATION_INDEX.md` references every required doc.
- Docs include `validated: yes` and `reviewed: yes` metadata for Factory preflight compatibility.

## Gate QA-002 — Runtime sync tests
- Test merge behavior where agent secret overrides shared secret.
- Test inherited shared value when agent secret is absent.
- Test generated notification defaults, e.g. `SENDGRID_FROM_EMAIL` fallback.
- Test secret redaction/logging path does not print values.

## Gate QA-003 — Script checks
- Python/shell files compile or pass syntax checks.
- Shell scripts pass `bash -n` when applicable.
- Unit tests run with real command output.

## Gate QA-004 — Live smoke after Infisical task
- Bael sync runs successfully.
- Runtime env contains presence of SendGrid keys without printing values.
- `notification_status` reports configured.
- Controlled email smoke test succeeds.

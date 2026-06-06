# Security Review — Agent Core Follow-up / Reminders

## Current report scope

Preliminary security notes for kickoff. The independent security gate is F10.

## Preliminary decisions

- No external customer/user UI is introduced by this project.
- No separate DB/service is introduced without ADR/security approval.
- Calendar and notification side effects must be audited and idempotent.
- Customer-facing personas must remain restricted and cannot inherit owner/operator tools through this capability.

## Required evidence later

F10 must include concrete inspection of code, tool schemas, resolved toolsets, tests, and side-effect/audit paths. This file is not a pass/fail security approval yet.

## F2 architecture security review — 2026-06-05T23:59:22Z

Scope reviewed:
- `docs/followup-reminder-core/ADR-002-universal-activity-layer.md`
- `factory/projects/agent-core-followup-reminders/TECHNICAL_BLUEPRINT.md`
- `factory/projects/agent-core-followup-reminders/ARCHITECTURE_DECISIONS.md`
- `factory/projects/agent-core-followup-reminders/F2_EVIDENCE.md`
- Factory DB task/gate state via `hermes factory status agent-core-followup-reminders --json`

Gate decision: PASS for F2 architecture/data-model closure. Factory DB architecture gate recorded as passed (`gate_id=165`).

Findings:
- The ADR chooses a dedicated `activity.*` schema in Agent Core Postgres and rejects separate DB/service/graph DB/runtime SQLite.
- Existing `crm_*` and `calendar_*` boundaries are preserved; `crm.follow_ups` remains compatibility surface and Calendar Core remains owner of time-blocked events.
- Architecture includes relation graph, recurrence, reminder rules, activity plans/runs, deterministic dispatcher, calendar bridge, audit events, dedupe/idempotency and privacy assumptions.
- Security posture is acceptable for architecture stage: explicit privileged `activity` toolset, no default customer-facing enablement, no external notification/calendar side effects without confirmation/audit, no secrets in metadata/evidence/audit.

Security conditions carried forward:
1. F4 must implement schema grants with least privilege (`activity_runtime` or equivalent) and idempotent migrations.
2. F5/F10 must verify resolved toolset registration so customer-facing personas do not inherit privileged Activity Core tools.
3. F5/F9/F10 must test SQL parameterization, metadata/evidence minimization and duplicate-prevention across Activity/CRM.
4. F6/F10 must verify calendar/notification side effects are explicit, idempotent, audited and disabled by default until approved.
5. F10 remains mandatory before delivery because F2 is design-only and no runtime code/tool exposure was inspected.

Result: F2 can close; proceed to F3 planning with the above conditions.

## F10 independent security/privacy/tool-boundary review — 2026-06-06T16:33:40Z

Scope reviewed:
- `tools/activity_tool.py`
- `tools/activity_plan_tool.py`
- `tools/crm_tool.py`
- `cron/activity_dispatcher.py`
- `toolsets.py`
- `gateway/run.py` customer-service routing section
- `tests/tools/test_activity_tool.py`
- `tests/tools/test_activity_plan_tool.py`
- `tests/tools/test_crm_tool.py`
- `tests/cron/test_activity_dispatcher.py`
- `tests/test_customer_service_routing.py`
- `db/modules/activity/000001_activity_schema.sql`
- `db/modules/crm/000006_contact_social_profiles.sql`
- `db/agent-core/000002_runtime_roles.sql`
- `factory/projects/agent-core-followup-reminders/SECURITY_GATES.md`

Commands and verification evidence:
- Initial `hermes factory status agent-core-followup-reminders --json` — FAILED before Factory state read because `hermes_cli/profiles.py:451` contained an unresolved merge marker and raised `SyntaxError`.
- `git status --short && git branch --show-current && git log --oneline -1` — repo has active unmerged/conflict files including `hermes_cli/profiles.py`, `gateway/run.py`, `tests/test_customer_service_routing.py`; last observed commit `bcb029261`.
- `.venv/bin/python -m pytest tests/tools/test_activity_tool.py tests/tools/test_activity_plan_tool.py tests/tools/test_crm_tool.py tests/cron/test_activity_dispatcher.py -q` — PASS, `38 passed in 1.66s`.
- Toolset resolution script via `.venv/bin/python` — resolved `customer_service` to exactly `clarify, crm_contact_upsert, crm_customer_timeline, crm_follow_up_create, crm_interaction_record, crm_search, customer_intent_raise, web_extract, web_search`; forbidden intersection was `[]`; `activity_in_core_defaults=False`.
- Secret-shaped scan over scoped files — no hardcoded secret value confirmed; one apparent `hardcoded_candidate=True` was manually checked as non-secret variable name `token` in quick-capture hashtag parsing (`tools/activity_plan_tool.py:150`).

Coverage results:
- PII/private relationship memory: Activity and CRM persist PII-bearing contact, social profile, participant, interaction, follow-up, metadata, evidence, and timeline fields in Agent Core Postgres schemas. No external document/report write path was found in the reviewed Activity/CRM handlers. Runtime roles are separated (`crm_runtime`, `activity_runtime`) and values are SQL-quoted via `sql.quote_literal` / `sql.quote_jsonb` in reviewed handlers.
- Metadata/evidence minimization: Reviewed code permits arbitrary caller-supplied `metadata` and `evidence` JSON in privileged CRM/Activity tools. This is acceptable only for owner/operator toolsets; it remains unsuitable for customer-facing unrestricted use without persona policy. `customer_service` currently exposes only limited CRM/follow-up/timeline/search and no generic Activity metadata/evidence write tools.
- Notifications/reminders: `cron/activity_dispatcher.py` is deterministic and returns `notification_ready` JSON but does not send messages. Non-dry-run scans create audited Activity events with idempotency keys. Channels from reminder rules are surfaced but delivery adapters are not invoked by this increment.
- Calendar/event side effects: `activity_to_calendar_event` requires explicit `activity_id`, `actor_id`, and `calendar_id`, skips non-calendar reminders, records `calendar_requested`, `calendar_linked`, or `calendar_failed` events, and links created calendar events. It is exposed only through the privileged `activity` toolset, not `customer_service`.
- Customer-facing persona/tool boundary: static `toolsets.py` resolution passes: `customer_service` excludes shell/file/cron/delegation, calendar mutation, Activity calendar/dispatcher tools, notifications, Twenty raw/sync, quotes/invoices, and sales/payment tools. However, executable gateway boundary verification cannot pass because `gateway/run.py` and `tests/test_customer_service_routing.py` contain unresolved merge markers.
- Secrets: Twenty API key is read from runtime env and used only in the Authorization header. Reviewed output returns configured status/base URL but not the API key. No secret values were copied into this report.
- Duplicate/spam prevention: CRM follow-up creation computes a deterministic dedupe key, stores it in CRM metadata and Activity `dedupe_key`, and tests cover duplicate detection and no duplicate follow-up creation.

Findings:

### SEC-F10-001 — BLOCKING — Customer-facing routing code contains unresolved merge conflict markers

Files/evidence:
- `gateway/run.py:1815-1819` contains `<<<<<<< HEAD`, `=======`, `>>>>>>> ...` inside `_customer_service_profile_home` docstring.
- `tests/test_customer_service_routing.py:10-13`, `23-68`, `149-155` contain unresolved merge conflict markers and duplicated/conflicting test definitions.
- Earlier Factory CLI startup also fails on unresolved merge marker in `hermes_cli/profiles.py:451`, preventing `hermes factory status` and gate recording.

Exploit/failure scenario:
- A customer-facing WhatsApp/email session cannot rely on the intended isolated Sophie route if gateway code is syntactically invalid. Depending on deployment/import path, this can fail closed with outage or prevent runtime boundary checks from executing. Because the boundary code is not executable, this review cannot verify that external customers are always routed to the restricted `customer_service` surface rather than owner/operator tools.

Recommended fix:
1. Resolve merge conflicts in `gateway/run.py`, `tests/test_customer_service_routing.py`, and `hermes_cli/profiles.py` without changing the intended safe boundary semantics.
2. Re-run customer-facing routing tests, including unsafe configured toolsets (`crm`, `sales`, `terminal`, `calendar`, `file`) and missing isolated profile cases.
3. Re-run `hermes factory status agent-core-followup-reminders --json` and record the Factory security gate through `hermes factory gate record`.

### SEC-F10-002 — MEDIUM — Privileged raw CRM adapter remains available in full `crm` toolset

Files/evidence:
- `toolsets.py:219-229` exposes `crm_twenty_raw_request` in the full `crm` toolset.
- `tools/crm_tool.py:857` registers `crm_twenty_raw_request` for arbitrary Twenty REST `GET/POST/PATCH/DELETE` paths.
- `toolsets.py:233-240` and resolved toolset verification show `crm_twenty_raw_request` is not exposed to `customer_service`.

Exploit/failure scenario:
- Any agent granted the broad `crm` toolset can call arbitrary Twenty REST endpoints with the configured Twenty bearer token. This is an intentional privileged escape hatch, but it can bypass canonical CRM validation/minimization if the broad `crm` toolset is accidentally assigned to a customer-facing or low-trust persona.

Recommended fix:
- Keep `crm_twenty_raw_request` out of customer-facing toolsets permanently.
- Prefer a separate admin-only CRM adapter toolset or add explicit policy checks/audit events around raw requests before broad delivery.
- Document that `crm` is operator/privileged, not safe for Sophie/customer-facing personas.

Security gate decision: FAIL / BLOCKED for F10 delivery.

Rationale:
- The Activity/CRM/reminder implementation and focused tests pass for SQL quoting, dedupe, dispatcher dry-run/audit, calendar skip/create/failure paths, and explicit toolset resolution.
- The acceptance criterion requiring customer-facing boundary verification cannot be satisfied while `gateway/run.py` and `tests/test_customer_service_routing.py` contain unresolved merge conflicts.
- Factory security gate was recorded as failed via `hermes factory gate record ...` with `gate_id=210`, status `failed`.

Remediation tasks required before delivery:
1. Resolve merge conflicts in gateway/customer-service routing and Hermes CLI profile code.
2. Re-run focused security tests plus `tests/test_customer_service_routing.py`.
3. Re-run resolved toolset verification for `customer_service`, `crm`, `activity`, `calendar`, and `notifications`.
4. Re-record/update the F10 security gate after remediation if the boundary tests pass.

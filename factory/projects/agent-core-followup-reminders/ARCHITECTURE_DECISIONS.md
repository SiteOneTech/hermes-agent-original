# ARCHITECTURE_DECISIONS — Agent Core Follow-up / Reminders

## Estado

F2 architecture decisions by `solution-architect`; pending independent `security-reviewer` gate.

- Project ID: `agent-core-followup-reminders`
- Task: `agent-core-followup-reminders-f2-architecture-adr-and-data-model-for-u`
- Run: `run-1780702957-7f740456`
- Date: `2026-06-05T23:43:24Z`
- Canonical ADR: `docs/followup-reminder-core/ADR-002-universal-activity-layer.md`
- Blueprint: `factory/projects/agent-core-followup-reminders/TECHNICAL_BLUEPRINT.md`

## Decision AD-001 — Schema placement

Accepted: create new Agent Core Postgres schema `activity`.

Rationale:
- Activity is universal, not only commercial CRM.
- It must relate to CRM, Calendar, projects, documents, invoices, external refs and future objects.
- Separate schema gives clearer grants/tool boundaries and security review surface.

Rejected:
- Stretching only `crm.follow_ups`.
- Separate DB/service/task app/graph DB.
- UI-first CRM/task dashboard as required product surface.

## Decision AD-002 — Existing CRM compatibility

Accepted: preserve `crm.follow_ups` and `crm_*` tools.

Implementation direction for F8:
- `crm_follow_up_create` must create/link universal activity or bridge explicitly.
- Link legacy rows with `activity.activity_links.relationship_type='legacy_follow_up'`.
- `crm_customer_timeline` must include relevant Activity Core rows or delegate to `activity_timeline` with tests.
- Duplicate prevention spans `crm.interactions`, `crm.follow_ups` and `activity.activities`.

## Decision AD-003 — Calendar ownership

Accepted: Calendar Core remains owner of time-blocked commitments and availability.

Rules:
- Reminder/follow-up without time block does not create calendar event.
- Meeting/call/time block or explicit “agenda” may call `calendar_*` tools.
- Activity stores only links/audit/status around calendar side effects.
- Adapter failure leaves activity intact and records `calendar_failed` event.

## Decision AD-004 — Relation graph

Accepted: use `activity.activity_links` as polymorphic relation graph.

Reasons:
- Avoid hard FKs to every future module.
- Support multiple links per activity and relation semantics (`primary`, `context`, `participant`, `blocks`, `next_after`, etc.).
- Allow timeline queries by target entity.

No external graph DB is approved.

## Decision AD-005 — Recurrence strategy

Accepted: store recurrence using RFC 5545 RRULE string in `activity.recurrence_rules` and interpret with `python-dateutil` at runtime.

Rules:
- Materialize bounded windows only.
- Track `next_occurrence_at` and `last_materialized_at`.
- Use `activity.recurrence_instances` when deterministic dispatcher/readback needs concrete occurrence IDs.

## Decision AD-006 — Reminder dispatcher

Accepted: deterministic DB-backed scan, no chat-memory dependency.

Dispatcher scans:
- `activities.due_at`
- `activities.snoozed_until`
- `activities.next_scan_at`
- `reminder_rules.next_fire_at`
- `recurrence_rules.next_occurrence_at`

Dispatcher writes audit to `activity.activity_events` and returns notification-ready outputs. It does not send external notifications until channel/security review approves.

## Decision AD-007 — Idempotency/dedupe

Accepted: runtime-computed `dedupe_key` plus DB partial unique active index.

Key components:
`owner_id | primary_link | activity_type | normalized_title | due_bucket | source | source_ref_or_hash`

Rules:
- Active states block duplicates: `planned`, `open`, `waiting`, `snoozed`.
- `done`/`cancelled` can start a new cycle if explicitly requested.
- Detection uses source ref + evidence span/hash.
- Calendar/dispatcher side effects use event idempotency keys.

## Decision AD-008 — Toolset boundary

Accepted: explicit `activity` toolset.

Tools approved for design:
- `activity_upsert`
- `activity_link`
- `activity_unlink`
- `activity_list`
- `activity_complete`
- `activity_snooze`
- `activity_reschedule`
- `activity_cancel`
- `activity_timeline`
- `activity_plan_create`
- `activity_plan_apply`
- `activity_next_actions`
- `activity_detect_from_text`
- `activity_to_calendar_event`
- `activity_dispatcher_scan`
- `activity_status`

Do not add to broad default/customer-facing toolsets without F10 review.

## Decision AD-009 — Data privacy/security posture

Accepted assumptions for F10:
- Activities may contain PII/private notes/business-sensitive data.
- Full Activity Core is owner/internal by default.
- Customer-facing agents require scoped tool boundaries and minimized result fields.
- No secrets in metadata/evidence/audit.
- Calendar invites and external notifications require confirmation and audit.

## Decision AD-010 — Dependencies

Approved for implementation evaluation:
- `python-dateutil` for RRULE.
- `dateparser` or equivalent for natural-language date parsing with explicit timezone/ambiguity handling.
- `networkx` only for offline tests/analysis if useful, not runtime persistence.

No AGPL/GPL code/schema copy from open-source references.

## F2 acceptance mapping

| F2 criterion | Decision/evidence |
|---|---|
| Choose schema placement | AD-001 accepts new `activity.*` schema |
| Preserve `crm_*` and `calendar_*` | AD-002 and AD-003 |
| Avoid separate DB/service | AD-001 rejects separate DB/service/graph DB |
| Relation graph | AD-004 |
| Recurrence | AD-005 |
| Reminders/dispatcher | AD-006 |
| Activity plans | Blueprint sections 4.5/6 and ADR data model |
| Calendar bridge | AD-003 |
| Jobs | AD-006 |
| Privacy/security assumptions | AD-009 |

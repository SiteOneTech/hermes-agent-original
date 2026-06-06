# F2 Evidence — Architecture ADR and data model for Universal Activity Layer

## Run metadata

- Project: `agent-core-followup-reminders`
- Task: `agent-core-followup-reminders-f2-architecture-adr-and-data-model-for-u`
- Run: `run-1780702957-7f740456`
- Owner: `solution-architect`
- Reviewer: `security-reviewer`
- Date: `2026-06-05T23:43:24Z`
- Source of truth checked: Agent Core Postgres via `hermes factory status agent-core-followup-reminders --json`

## Files changed

- `docs/followup-reminder-core/ADR-002-universal-activity-layer.md`
- `factory/projects/agent-core-followup-reminders/TECHNICAL_BLUEPRINT.md`
- `factory/projects/agent-core-followup-reminders/ARCHITECTURE_DECISIONS.md`
- `factory/projects/agent-core-followup-reminders/ADRS.md`
- `factory/projects/agent-core-followup-reminders/F2_EVIDENCE.md`

## Evidence of context read

Inputs inspected:
- `factory/projects/agent-core-followup-reminders/PRD.md`
- `factory/projects/agent-core-followup-reminders/FUNCTIONAL_SPEC.md`
- `docs/followup-reminder-core/FACTORY_SPEC-001-agent-core-followup-reminders.md`
- Existing seed ADR: `docs/followup-reminder-core/ADR-002-universal-activity-layer.md`
- Existing CRM schema: `db/modules/crm/000001_crm_schema.sql`
- Existing CRM business/follow-up schema: `db/modules/crm/000003_business_crm_and_adapters.sql`
- Existing Calendar registry: `db/modules/calendar/000001_calendar_registry.sql`
- Factory status/readback for task F2.

Observed existing boundaries:
- `crm.follow_ups` exists with `organization_id`, `contact_id`, `opportunity_id`, `due_at`, `summary`, `status`, `priority`, `assignee`, `metadata`.
- Calendar module is adapter-oriented and should not be replaced by Activity.
- Factory DB marks F2 as running with reviewer `security-reviewer` and acceptance criteria requiring schema placement, compatibility, relation graph, recurrence, reminders, activity plans, calendar bridge, jobs and privacy assumptions.

## Architecture decisions delivered

1. Schema placement: accepted new `activity.*` schema in Agent Core Postgres.
2. CRM compatibility: preserve `crm.follow_ups` and `crm_*`; bridge via `activity_links.relationship_type='legacy_follow_up'` and runtime dedupe.
3. Calendar boundary: non-calendar reminders do not create events; meetings/calls/time blocks call existing `calendar_*` tools and audit results.
4. Data model: specified activities, links, reminder rules, events/audit, plans, plan runs, recurrence rules/instances.
5. Dedupe/idempotency: active-state partial unique `dedupe_key`; event idempotency keys for dispatcher/calendar.
6. Dispatcher: deterministic DB scan, notification-ready output, no chat memory dependency.
7. Tool boundary: explicit `activity` toolset; no broad default/customer-facing enablement before F10.
8. Dependencies: `python-dateutil` for RRULE; `dateparser` or equivalent for natural-language dates; `networkx` only optional/offline.

## Verification commands run

Commands executed in this F2 run:

```bash
git status --short
hermes factory status agent-core-followup-reminders --json
python3 - <<'PY'
# F2 artifact validator: asserts required architecture sections/needles in project docs.
PY

git diff --stat -- docs/followup-reminder-core/ADR-002-universal-activity-layer.md factory/projects/agent-core-followup-reminders/TECHNICAL_BLUEPRINT.md factory/projects/agent-core-followup-reminders/ARCHITECTURE_DECISIONS.md factory/projects/agent-core-followup-reminders/ADRS.md factory/projects/agent-core-followup-reminders/F2_EVIDENCE.md factory/projects/agent-core-followup-reminders/TRACKER.md factory/projects/agent-core-followup-reminders/DOCUMENTATION_INDEX.md

git status --short -- docs/followup-reminder-core/ADR-002-universal-activity-layer.md factory/projects/agent-core-followup-reminders

./hermes factory gate record agent-core-followup-reminders architecture pending --lane-id agent-core-followup-hybrid --task-id agent-core-followup-reminders-f2-architecture-adr-and-data-model-for-u --reviewer security-reviewer --notes "F2 architecture artifacts submitted by solution-architect; pending independent security-reviewer gate. Decision: new activity.* schema in Agent Core Postgres; preserve crm_* and calendar_*; no separate DB/service. Evidence paths: docs/followup-reminder-core/ADR-002-universal-activity-layer.md, factory/projects/agent-core-followup-reminders/TECHNICAL_BLUEPRINT.md, factory/projects/agent-core-followup-reminders/ARCHITECTURE_DECISIONS.md, factory/projects/agent-core-followup-reminders/ADRS.md, factory/projects/agent-core-followup-reminders/F2_EVIDENCE.md." --json

python3 - <<'PY'
# Factory DB run completion/readback via hermes_cli.factory_pg.mark_run_finished
PY
```

Observed results:

- Artifact validator returned: `F2_VALIDATION_OK required architecture artifacts and sections present`.
- Line counts after validation:
  - ADR: 403 lines.
  - TECHNICAL_BLUEPRINT: 364 lines.
  - ARCHITECTURE_DECISIONS: 149 lines.
  - ADRS: 47 lines.
  - TRACKER: 93 lines.
  - DOCUMENTATION_INDEX: 32 lines.
  - F2_EVIDENCE: 87 lines before this final evidence patch.
- Factory gate record returned: `gate_id=164`, `status=pending`.
- Factory DB readback returned F2 task `status=review_ready`, `evidence_status=present`, reviewer `security-reviewer`.

## Result

F2 architecture artifacts are complete and ready for independent security review. This run did not implement migrations/runtime tools and did not self-approve the architecture gate. The Factory DB run was marked succeeded/review_ready with evidence present, while the architecture gate remains pending for `security-reviewer`.

## Risks/blockers

- Risk: repo working tree contains many unrelated changes from other work. F2 touched only project architecture/docs listed above.
- Risk: security/privacy/tool boundary still requires independent F10/security-reviewer approval before broad tool exposure.
- Blocker: none for F2 documentation handoff.

## Next action

Security reviewer should review ADR/data model and record architecture gate pass/fail. Then F3 can produce implementation plan/task graph from this blueprint.

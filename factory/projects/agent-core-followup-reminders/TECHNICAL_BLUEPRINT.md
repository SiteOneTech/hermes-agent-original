# TECHNICAL_BLUEPRINT — Universal Activity Layer

## Estado

F2 architecture blueprint accepted by `solution-architect`; pendiente de review independiente `security-reviewer`.

- Project ID: `agent-core-followup-reminders`
- Incremento: F2 — Architecture ADR and data model for Universal Activity Layer
- Run: `run-1780702957-7f740456`
- Fecha: `2026-06-05T23:43:24Z`
- Fuente de verdad operacional: Agent Core Postgres `factory.*`
- Canonical ADR: `docs/followup-reminder-core/ADR-002-universal-activity-layer.md`

## 1. Decisión arquitectónica

Crear módulo nuevo `activity` en Agent Core Postgres:

- `activity.activities`
- `activity.activity_links`
- `activity.reminder_rules`
- `activity.activity_events`
- `activity.activity_plans`
- `activity.activity_plan_steps`
- `activity.activity_plan_runs`
- `activity.activity_plan_run_steps`
- `activity.recurrence_rules`
- `activity.recurrence_instances` (opcional/aprobada si F4/F7 necesitan materialización determinística)

`crm.follow_ups` NO se elimina ni se convierte en source universal. Queda como compatibility surface para `crm_*`; F8 debe bridgear o aliasar hacia Activity Core con dedupe.

Calendar Core NO se reemplaza. Activity enlaza/audita eventos cuando la actividad bloquea tiempo o el usuario pide scheduling. Reminders/follow-ups no crean calendar events por defecto.

## 2. Principios de diseño

1. Agent-first: todo debe ser operable por Hermes tools JSON y verificable por tests/DB readback.
2. Postgres-first: no DB separada, no graph DB, no SQLite runtime.
3. Module boundary limpio: Activity no es CRM ni Calendar; integra por links y tools.
4. Idempotente: create/detect/dispatcher/calendar side effects usan dedupe/idempotency keys.
5. Auditado: state transitions y side effects se registran en `activity.activity_events`.
6. Privacy by design: minimizar exposición de metadata/evidence y limitar toolset.
7. No UI dependency: consultas due/timeline/waiting se resuelven por tool/query.

## 3. Module registry y grants esperados para F4

F4 debe crear migración module-owned, sugerida:

`db/modules/activity/000001_activity_schema.sql`

Debe incluir:

```sql
CREATE SCHEMA IF NOT EXISTS activity;

INSERT INTO agent_core.modules(module, description, owner, schema_name, metadata)
VALUES (
  'activity',
  'Agent Core Universal Activity Layer: follow-ups, reminders, tasks, plans, recurrence, and audited side effects.',
  'agent-runtime',
  'activity',
  '{"capability":"followup-reminders","project":"agent-core-followup-reminders"}'::jsonb
)
ON CONFLICT (module) DO UPDATE SET updated_at = now(), metadata = EXCLUDED.metadata;

INSERT INTO agent_core.module_databases(module, database_name, connection_role, migration_role, metadata)
VALUES ('activity', current_database(), 'activity_runtime', 'agent_admin', '{"option":"same-agent-db-schema"}'::jsonb)
ON CONFLICT (module) DO UPDATE SET database_name = EXCLUDED.database_name, connection_role = EXCLUDED.connection_role, migration_role = EXCLUDED.migration_role;
```

Runtime role preferred: `activity_runtime`. If role creation is centralized elsewhere, F4 records the required grants explicitly and does not silently reuse broad admin access.

## 4. Physical data model

### 4.1 `activity.activities`

Purpose: canonical actionable/informational unit.

Required columns:

```sql
activity_id text PRIMARY KEY,
activity_type text NOT NULL,
title text NOT NULL,
description text,
status text NOT NULL DEFAULT 'open',
priority text NOT NULL DEFAULT 'normal',
owner_id text NOT NULL DEFAULT 'zeus',
assignee_id text,
due_at timestamptz,
start_at timestamptz,
end_at timestamptz,
completed_at timestamptz,
cancelled_at timestamptz,
snoozed_until timestamptz,
next_scan_at timestamptz,
source text NOT NULL DEFAULT 'agent',
source_ref text,
source_hash text,
dedupe_key text,
confidence numeric,
evidence jsonb NOT NULL DEFAULT '{}'::jsonb,
participants jsonb NOT NULL DEFAULT '[]'::jsonb,
metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
created_by text NOT NULL DEFAULT current_user,
created_at timestamptz NOT NULL DEFAULT now(),
updated_at timestamptz NOT NULL DEFAULT now()
```

Checks:
- `activity_type IN ('task','follow_up','reminder','call','meeting','email','message','note','document','approval','custom')`
- `status IN ('planned','open','waiting','snoozed','done','cancelled')`
- `priority IN ('low','normal','high','urgent')`
- `confidence IS NULL OR (confidence >= 0 AND confidence <= 1)`

Indexes:
- Partial unique: `dedupe_key` where status in active states.
- `(owner_id, status, due_at)`.
- `(owner_id, next_scan_at)`.
- `(source, source_ref)`.
- Full-text over `title`/`description`.

### 4.2 `activity.activity_links`

Purpose: polymorphic relation graph.

Required columns:

```sql
activity_link_id bigserial PRIMARY KEY,
activity_id text NOT NULL REFERENCES activity.activities(activity_id) ON DELETE CASCADE,
target_type text NOT NULL,
target_id text NOT NULL,
relationship_type text NOT NULL,
target_schema text,
target_table text,
provider text,
external_type text,
external_id text,
external_url text,
metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
created_at timestamptz NOT NULL DEFAULT now(),
created_by text NOT NULL DEFAULT current_user,
UNIQUE (activity_id, target_type, target_id, relationship_type)
```

Allowed `relationship_type`: `primary`, `context`, `participant`, `derived_from`, `next_after`, `blocks`, `blocked_by`, `calendar_event`, `duplicate_of`, `merged_into`, `legacy_follow_up`, `source_ref`.

Indexes:
- `(target_type, target_id, relationship_type)` for timeline/entity queries.
- `(relationship_type, activity_id)` for graph traversal.

### 4.3 `activity.reminder_rules`

Purpose: deterministic reminder triggers.

Required columns:

```sql
reminder_rule_id text PRIMARY KEY,
activity_id text NOT NULL REFERENCES activity.activities(activity_id) ON DELETE CASCADE,
rule_type text NOT NULL,
trigger_at timestamptz,
relative_to text,
offset_seconds integer,
channel text,
enabled boolean NOT NULL DEFAULT true,
last_fired_at timestamptz,
next_fire_at timestamptz,
idempotency_key text,
metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
created_at timestamptz NOT NULL DEFAULT now(),
updated_at timestamptz NOT NULL DEFAULT now()
```

Indexes:
- `(enabled, next_fire_at)`.
- Unique `idempotency_key` when present.

### 4.4 `activity.activity_events`

Purpose: append-only audit/event stream.

Required columns:

```sql
event_id bigserial PRIMARY KEY,
activity_id text REFERENCES activity.activities(activity_id) ON DELETE SET NULL,
event_type text NOT NULL,
actor text NOT NULL DEFAULT current_user,
source text,
source_ref text,
idempotency_key text,
previous_state jsonb NOT NULL DEFAULT '{}'::jsonb,
new_state jsonb NOT NULL DEFAULT '{}'::jsonb,
side_effect jsonb NOT NULL DEFAULT '{}'::jsonb,
result_status text NOT NULL DEFAULT 'recorded',
error text,
created_at timestamptz NOT NULL DEFAULT now()
```

Indexes:
- Unique `idempotency_key` when present.
- `(activity_id, created_at DESC)`.
- `(event_type, created_at DESC)`.

### 4.5 Plans and runs

Tables:
- `activity.activity_plans`
- `activity.activity_plan_steps`
- `activity.activity_plan_runs`
- `activity.activity_plan_run_steps`

Purpose: reusable sequences and concrete application progress.

Minimum relations:
- Plan has ordered steps.
- Plan run targets an entity/context (`target_type`, `target_id`).
- Run step can link to concrete `activity_id`.

### 4.6 Recurrence

Tables:
- `activity.recurrence_rules`
- `activity.recurrence_instances` optional/materialized.

Decision:
- Store canonical RFC 5545 `rrule` text + timezone and next occurrence metadata.
- Use `python-dateutil` for runtime interpretation.
- Materialize only bounded windows for dispatcher/smoke; do not pre-expand infinite rules.

## 5. Dedupe key

Runtime/tool calculates:

`owner_id | primary_link | activity_type | normalized_title | due_bucket | source | source_ref_or_hash`

Where:
- `primary_link`: first link with relationship `primary`, else explicit context, else `none`.
- `normalized_title`: lowercase, trim, collapse spaces, remove low-value punctuation.
- `due_bucket`: date/day for date-only reminders; hour/window for timed events; `none` when absent.
- `source_ref_or_hash`: stable source ID if available, otherwise hash of source text/evidence span.

DB enforces active dedupe; runtime handles legacy `crm.follow_ups` equivalence and user-requested new cycles.

## 6. Tool layer blueprint

Toolset: `activity`.

Tools:

1. `activity_upsert`
   - Creates/updates/link-existing with dedupe.
   - Returns `activity_id`, `operation`, `dedupe_key`, links, audit event.
2. `activity_link` / `activity_unlink`
   - Adds/removes graph edges with uniqueness/readback.
3. `activity_list`
   - Supports due/today/upcoming/overdue/waiting/snoozed/resurfaced filters.
4. `activity_complete`
   - State transition + optional next action/plan step handling.
5. `activity_snooze`
6. `activity_reschedule`
7. `activity_cancel`
8. `activity_timeline`
   - Entity-centered view combining activities, CRM interactions/follow-ups and calendar links where available.
9. `activity_plan_create`
10. `activity_plan_apply`
11. `activity_next_actions`
12. `activity_detect_from_text`
    - `suggest_only` has no side effects; `create_authorized` persists clear candidates.
13. `activity_to_calendar_event`
    - Calls existing Calendar Core tools only when calendar side effect is required/authorized.
14. `activity_dispatcher_scan`
    - Deterministic scan and notification-ready output.
15. `activity_status`
    - Health/smoke/readiness.

Implementation requirements for F5:
- JSON outputs only.
- Safe SQL parameterization.
- Required-field validation.
- Explicit warnings for ambiguity/confirmation-required.
- Return IDs/readbacks, not prose-only summaries.

## 7. Calendar bridge

State flow:

1. Activity exists or is upserted.
2. Tool determines calendar need:
   - true for explicit agenda/schedule/time block/meeting invite;
   - false for normal reminder/follow-up.
3. If true, tool calls existing `calendar_*` handlers/adapters.
4. On success:
   - Add link `relationship_type='calendar_event'`, `target_type='calendar_event'`.
   - Write audit event `calendar_linked` with provider/external IDs.
5. On failure:
   - Keep activity.
   - Write `calendar_failed` event with sanitized error.
   - Return retryable status.

## 8. CRM compatibility bridge

F8 must preserve existing callers:

- `crm_follow_up_create` remains callable.
- Existing `crm.follow_ups` rows can be linked to activities via `activity_links.relationship_type='legacy_follow_up'`.
- New CRM follow-ups should create/upsert activity universal first or in same transaction, then bridge.
- `crm_customer_timeline` either includes activity records or documents/delegates to `activity_timeline` with tests.
- Duplicate prevention spans `crm.interactions`, `crm.follow_ups` and `activity.activities`.

## 9. Dispatcher blueprint

Inputs:
- Active activities due/overdue/upcoming.
- `snoozed_until` resurfacing.
- `reminder_rules.next_fire_at`.
- `recurrence_rules.next_occurrence_at`.

Outputs:
- Audit events in `activity.activity_events`.
- Notification-ready list with IDs/action/status.
- Optional recurrence instances/materialized activities with idempotency keys.

Non-goals:
- No direct external send without F10/F11 approval.
- No chat-memory dependency.

## 10. Security/privacy assumptions for F10

- Activity data may include PII/private notes/business-sensitive context.
- Full `activity` toolset is privileged owner/internal capability by default.
- Customer-facing agents require scoped tools/queries, tenant/context filters and metadata minimization.
- Calendar invites, external notifications and sharing private notes require confirmation/audit.
- No secrets/tokens in `metadata`, `evidence`, `side_effect`, logs or audit.
- Security reviewer must inspect toolset registration before delivery.

## 11. Verification strategy

F2 verification is documentary/static:
- Read existing PRD/FUNCTIONAL_SPEC/ADR seed.
- Inspect CRM/Calendar schema boundaries.
- Update canonical ADR and project-local blueprint/decisions.
- Validate docs contain required sections and no unsupported DB/service/UI dependency.

F4-F9 verification to implement later:
- Migration dry-run/apply in Agent Core Postgres or controlled test DB.
- Unit tests for handlers/transitions/dedupe.
- Regression tests: `tests/tools/test_crm_tool.py`, `tests/tools/test_calendar_tool.py` relevant paths.
- Direct smoke: create synthetic activity, link CRM entity, add reminder, list due, complete/snooze/reschedule, plan apply, dispatcher scan, DB readback.

## 12. Risks

| Risk | Mitigation |
|---|---|
| Duplicates with `crm.follow_ups` | Active dedupe key + legacy bridge + F8 tests |
| Calendar side effects wrong | Explicit `calendar_required`, confirmation rules, audit/idempotency |
| PII leakage | Scoped toolset, metadata minimization, F10 security review |
| Recurrence infinite expansion | Store RRULE, materialize bounded windows only |
| Over-broad default tools | Register `activity` toolset explicitly, no default enablement without approval |
| Open-source licensing | Borrow patterns only; no schema/code copy |

## 13. Handoff

F3 should now turn this blueprint into implementation tasks. F4 can implement migration only after architecture/security/planning gates are recorded as required by Factory.

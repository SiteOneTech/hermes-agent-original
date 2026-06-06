# ADR-002 — Universal Activity Layer sobre CRM Core + Calendar Core

## Estado

Accepted for F2 architecture; pendiente de security review independiente (`security-reviewer`) antes de implementación F4-F8.

- Proyecto: `agent-core-followup-reminders`
- Incremento: F2 — Architecture ADR and data model for Universal Activity Layer
- Owner: `solution-architect`
- Reviewer requerido: `security-reviewer`
- Fecha: `2026-06-05T23:43:24Z`
- Fuente operacional: Agent Core Postgres, schema `factory.*` para tracking; runtime capability en el mismo Agent Core Postgres.

## Contexto

Agent Core ya tiene:

- CRM Core en schema `crm`: organizations, contacts, opportunities, interactions, relationships, products, quotes, invoices, external links y `crm.follow_ups`.
- Calendar Core en schema `calendar`: registry del scheduler adapter; el backend actual es Nettu vía tools `calendar_*`, no una tabla local universal de eventos.
- Factory runtime en schema `factory.*`, que registra project/task/gates/evidence y es la fuente de verdad operacional del proyecto.

El PRD F1 cerró el contrato funcional: Zeus debe operar follow-ups, reminders, tareas, meetings/calls, next-actions, timelines, recurrence, activity plans, quick capture y detección desde texto con tools JSON y jobs determinísticos. La solución no puede depender de memoria conversacional ni de una UI compleja.

## Decisión

Crear un módulo nuevo `activity` en Agent Core Postgres, con schema propio `activity.*`, y usarlo como Universal Activity Layer canónica.

No se extenderá `crm.follow_ups` como estructura principal. `crm.follow_ups` queda como tabla legacy/compatibility surface y será bridgeada por F8 para que callers `crm_*` sigan funcionando sin duplicar pendientes.

No se crea DB, servicio, graph DB ni scheduler externo adicional. Calendar sigue siendo el Core canónico para compromisos que bloquean tiempo; Activity sólo conserva links/audit y usa `calendar_*` cuando corresponde.

## Opciones consideradas

### Opción A — Extender sólo `crm.follow_ups`

Rechazada.

Pros:
- Menor cambio inicial.
- Callers CRM existentes ya conocen la tabla.

Contras decisivos:
- Mantiene el dominio atado a CRM comercial.
- No modela bien reminders personales, projects, documents, waiting-for, links múltiples, recurrence, snooze, plans, calendar side effects ni detección desde fuentes arbitrarias.
- Obliga a sobrecargar `metadata` con estado crítico y complica seguridad/queries.

### Opción B — Nuevo schema `activity.*`

Aceptada.

Pros:
- Límite de módulo claro y reusable por CRM, calendar, personal graph, docs, projects y futuros adapters.
- Permite relaciones polimórficas y actividad universal sin contaminar CRM.
- Simplifica grants/toolset específicos y revisión de seguridad para PII/reminders.
- Preserva CRM y Calendar como módulos existentes con bridges explícitos.

Costos:
- Requiere migración F4, tools F5, bridge calendar F6, plans/quick capture F7 y compat CRM F8.
- Requiere pruebas de idempotencia y no-duplicación.

### Opción C — App externa task/CRM visual

Rechazada por dirección ejecutiva. El producto es Core agentico operado por Zeus; no UI-first.

## Boundary de módulos

### Activity Core

Responsable de:
- Persistir activities universales, links, reminders, recurrence, audit events y plans.
- Resolver consultas due/today/upcoming/overdue/waiting/snoozed por tools.
- Mantener idempotency/dedupe keys y source evidence.
- Auditar state changes y side effects.
- Producir notification-ready outputs para dispatcher.

No responsable de:
- Mantener CRM master data: contacts/organizations/opportunities siguen en `crm`.
- Mantener availability/event backend: calendar scheduling sigue en `calendar_*` tools/adapters.
- Enviar notificaciones externas sin autorización/canal aprobado.
- Exponer notas privadas fuera de tool boundary.

### CRM bridge

- `crm.follow_ups` sigue existiendo.
- F8 debe hacer que `crm_follow_up_create` cree/linkee una activity universal o registre un bridge explícito sin romper el contrato JSON existente.
- Timelines CRM deben incluir activities relevantes o delegar a `activity_timeline`.
- Dedupe considera legacy follow-ups equivalentes.

### Calendar bridge

- Reminders/follow-ups sin tiempo bloqueado no crean calendar event.
- Meetings/calls/time-blocks usan `calendar_*` solamente cuando `calendar_required=true`, cuando hay horario real con time block, o cuando el usuario pidió “agenda”.
- Links a calendar se guardan como `activity.activity_links` + audit en `activity.activity_events`.
- Fallas de adapter no borran activity; dejan audit/error y retry metadata.

## Modelo de datos aprobado para F4

Convenciones:
- IDs de activity/plans como `text` generados por tool/runtime (`act_...`, `aplan_...`) para devolver handles estables al agente.
- JSONB para metadata/evidence flexible, pero campos consultables críticos son columnas e índices.
- Timestamps `timestamptz` en UTC.
- Checks simples en DB para estados/tipos base; extensibilidad adicional vía `metadata`/registry futuro, no vía tablas externas en F2.

### `activity.activities`

Entidad canónica accionable.

Campos requeridos:
- `activity_id text primary key`
- `activity_type text not null`: `task`, `follow_up`, `reminder`, `call`, `meeting`, `email`, `message`, `note`, `document`, `approval`, `custom`
- `title text not null`
- `description text`
- `status text not null default 'open'`: `planned`, `open`, `waiting`, `snoozed`, `done`, `cancelled`
- `priority text not null default 'normal'`: `low`, `normal`, `high`, `urgent`
- `owner_id text not null default 'zeus'`
- `assignee_id text`
- `due_at timestamptz`
- `start_at timestamptz`
- `end_at timestamptz`
- `completed_at timestamptz`
- `cancelled_at timestamptz`
- `snoozed_until timestamptz`
- `next_scan_at timestamptz`
- `source text not null default 'agent'`: `manual`, `agent`, `crm`, `calendar`, `email`, `whatsapp`, `telegram`, `webhook`, `schedule`, `import`, `test`
- `source_ref text`
- `source_hash text`
- `dedupe_key text`
- `confidence numeric`
- `evidence jsonb not null default '{}'::jsonb`
- `participants jsonb not null default '[]'::jsonb`
- `metadata jsonb not null default '{}'::jsonb`
- `created_by text not null default current_user`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

Constraints/índices para F4:
- Partial unique index on `dedupe_key` for active statuses: `planned/open/waiting/snoozed`.
- B-tree index `(owner_id, status, due_at)` for due/today/upcoming/overdue.
- B-tree index `(owner_id, next_scan_at)` for dispatcher scans.
- B-tree index `(source, source_ref)` for idempotent imports/detection.
- GIN index on `metadata` and `evidence` only if tests show query need; avoid over-indexing by default.
- Full-text index over title/description for agent search.

### `activity.activity_links`

Polymorphic relation graph from activity to any local/external object, including other activities.

Campos:
- `activity_link_id bigserial primary key`
- `activity_id text not null references activity.activities(activity_id) on delete cascade`
- `target_type text not null`: `contact`, `organization`, `opportunity`, `project`, `document`, `quote`, `invoice`, `interaction`, `calendar_event`, `external_ref`, `activity`, `plan`, `custom`
- `target_id text not null`
- `relationship_type text not null`: `primary`, `context`, `participant`, `derived_from`, `next_after`, `blocks`, `blocked_by`, `calendar_event`, `duplicate_of`, `merged_into`, `legacy_follow_up`, `source_ref`
- `target_schema text`
- `target_table text`
- `provider text`
- `external_type text`
- `external_id text`
- `external_url text`
- `metadata jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null default now()`
- `created_by text not null default current_user`

Constraints/índices:
- Unique `(activity_id, target_type, target_id, relationship_type)`.
- Index `(target_type, target_id, relationship_type)` for timeline/entity queries.
- Index `(relationship_type, activity_id)` for graph traversal.
- No hard FKs to CRM/calendar tables in this relation table; module boundaries remain loose and future-compatible.

### `activity.reminder_rules`

Rules for reminders/notifications relative to activities.

Campos:
- `reminder_rule_id text primary key`
- `activity_id text not null references activity.activities(activity_id) on delete cascade`
- `rule_type text not null`: `absolute`, `relative`, `recurrence`, `snooze`, `deadline`
- `trigger_at timestamptz`
- `relative_to text`: `due_at`, `start_at`, `end_at`, `completed_at`, `created_at`
- `offset_seconds integer`
- `channel text`: `cli`, `telegram`, `whatsapp`, `email`, `calendar`, `webhook`, `none`
- `enabled boolean not null default true`
- `last_fired_at timestamptz`
- `next_fire_at timestamptz`
- `idempotency_key text`
- `metadata jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

Dispatcher sólo produce notification-ready records hasta que F10/F11 aprueben canales reales.

### `activity.activity_events`

Audit/event stream append-only para state changes, detections, dispatcher scans y side effects.

Campos:
- `event_id bigserial primary key`
- `activity_id text references activity.activities(activity_id) on delete set null`
- `event_type text not null`: `created`, `updated`, `completed`, `cancelled`, `snoozed`, `rescheduled`, `linked`, `unlinked`, `dedupe_hit`, `calendar_requested`, `calendar_linked`, `calendar_failed`, `reminder_due`, `reminder_dispatched`, `recurrence_materialized`, `plan_applied`, `detection_suggested`, `detection_persisted`, `security_blocked`
- `actor text not null default current_user`
- `source text`
- `source_ref text`
- `idempotency_key text`
- `previous_state jsonb not null default '{}'::jsonb`
- `new_state jsonb not null default '{}'::jsonb`
- `side_effect jsonb not null default '{}'::jsonb`
- `result_status text not null default 'recorded'`: `recorded`, `pending`, `succeeded`, `failed`, `blocked`, `skipped`
- `error text`
- `created_at timestamptz not null default now()`

Constraints/índices:
- Unique `idempotency_key` when not null.
- Index `(activity_id, created_at desc)`.
- Index `(event_type, created_at desc)`.

### `activity.activity_plans`

Reusable sequences/templates.

Campos:
- `plan_id text primary key`
- `name text not null`
- `description text`
- `status text not null default 'active'`: `draft`, `active`, `paused`, `archived`
- `scope text`: `personal`, `crm`, `project`, `tenant`, `custom`
- `owner_id text not null default 'zeus'`
- `metadata jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

### `activity.activity_plan_steps`

Steps relativos que pueden crear/sugerir activities.

Campos:
- `plan_step_id text primary key`
- `plan_id text not null references activity.activity_plans(plan_id) on delete cascade`
- `step_order integer not null`
- `activity_type text not null`
- `title_template text not null`
- `description_template text`
- `default_priority text not null default 'normal'`
- `relative_to text not null default 'plan_start'`: `plan_start`, `previous_completed_at`, `activity_due_at`, `external_date`
- `offset_seconds integer not null default 0`
- `auto_create boolean not null default false`
- `requires_confirmation boolean not null default false`
- `metadata jsonb not null default '{}'::jsonb`
- Unique `(plan_id, step_order)`.

### `activity.activity_plan_runs`

Application of a plan to an entity/context.

Campos:
- `plan_run_id text primary key`
- `plan_id text not null references activity.activity_plans(plan_id)`
- `status text not null default 'active'`: `active`, `paused`, `completed`, `cancelled`
- `owner_id text not null default 'zeus'`
- `target_type text not null`
- `target_id text not null`
- `started_at timestamptz not null default now()`
- `completed_at timestamptz`
- `metadata jsonb not null default '{}'::jsonb`

### `activity.activity_plan_run_steps`

Concrete step progress.

Campos:
- `plan_run_step_id text primary key`
- `plan_run_id text not null references activity.activity_plan_runs(plan_run_id) on delete cascade`
- `plan_step_id text not null references activity.activity_plan_steps(plan_step_id)`
- `activity_id text references activity.activities(activity_id) on delete set null`
- `status text not null default 'pending'`: `pending`, `suggested`, `created`, `skipped`, `done`, `cancelled`
- `due_at timestamptz`
- `metadata jsonb not null default '{}'::jsonb`
- Unique `(plan_run_id, plan_step_id)`.

### `activity.recurrence_rules`

Recurrence definition separated from activities to avoid overloading a single row.

Campos:
- `recurrence_rule_id text primary key`
- `activity_id text not null references activity.activities(activity_id) on delete cascade`
- `rrule text not null`
- `timezone text not null default 'UTC'`
- `dtstart timestamptz`
- `until_at timestamptz`
- `count_limit integer`
- `enabled boolean not null default true`
- `last_materialized_at timestamptz`
- `next_occurrence_at timestamptz`
- `metadata jsonb not null default '{}'::jsonb`

Decision: use RFC 5545 RRULE strings interpreted by `python-dateutil` in runtime. Store canonical RRULE, not custom recurrence columns. Materialization remains bounded.

### `activity.recurrence_instances`

Optional but approved if F4/F7 need deterministic smoke/readback for generated occurrences.

Campos:
- `recurrence_instance_id text primary key`
- `recurrence_rule_id text not null references activity.recurrence_rules(recurrence_rule_id) on delete cascade`
- `activity_id text references activity.activities(activity_id) on delete set null`
- `occurrence_at timestamptz not null`
- `status text not null default 'pending'`: `pending`, `materialized`, `skipped`, `done`, `cancelled`
- `idempotency_key text not null unique`
- `created_at timestamptz not null default now()`

## Dedupe e idempotencia

`dedupe_key` debe ser calculada por tool/runtime con componentes normalizados:

`owner_id | primary_link(target_type,target_id) | activity_type | normalized_title | due_bucket | source | source_ref_or_hash`

Reglas:
- Sólo bloquea duplicados activos (`planned/open/waiting/snoozed`).
- `done/cancelled` no bloquean un nuevo ciclo si el usuario lo pidió explícitamente; se crea relación `next_after` o `derived_from` cuando aplique.
- Detecciones desde mismo email/chat/interacción usan `source_ref + evidence span/hash` para idempotencia.
- Duplicados posteriores se representan con link `duplicate_of` o `merged_into`, no se borran silenciosamente.
- Calendar side effects usan `activity.activity_events.idempotency_key` para retry seguro.

## Tool contracts aprobados para F5

Toolset recomendado: `activity`, registrado explícitamente; no agregarlo al core/default sin aprobación de F10/F11.

Tools mínimos:
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

Todos retornan JSON con `ok`, IDs, operation, warnings, audit/event IDs y readback suficiente para QA.

## Dispatcher contract aprobado para F6

- Job determinístico escanea `activity.activities.next_scan_at`, `due_at`, `snoozed_until`, `reminder_rules.next_fire_at` y `recurrence_rules.next_occurrence_at`.
- Usa scan window e idempotency key: `dispatcher | window_start | window_end | activity_id | rule_id | channel`.
- Escribe `activity.activity_events` con `reminder_due`/`reminder_dispatched`/`recurrence_materialized`.
- Por defecto produce notification-ready output; el envío real se habilita sólo con canal/configuración/review aprobados.
- No lee memoria conversacional.

## Librerías propuestas

Permitidas para F4-F8, sujeto a verificación de licencia y tests:
- `python-dateutil`: RRULE/recurrence. Justificación: estándar, madura, evita parser propio.
- `dateparser` o alternativa liviana equivalente: fechas naturales. Debe usarse con timezone explícita y confidence/ambigüedad; si agrega dependencia pesada, F7 puede implementar parser acotado inicial.
- `networkx`: sólo para análisis offline/tests si aporta valor. No en runtime hot path ni como DB graph.

## Seguridad y privacidad

Supuestos para F10:
- Activities pueden contener PII, notas privadas, relación personal y business-sensitive data.
- Customer-facing personas no deben recibir toolset `activity` completo por defecto.
- Results deben minimizar `metadata`, `evidence` y notas privadas; queries deben aceptar scope/owner/tenant cuando exista.
- No guardar secretos/tokens en `metadata`, `evidence`, `side_effect` ni audit.
- Calendar invites/notificaciones externas requieren confirmación/autorización explícita y audit.
- Diseño usa grants por schema `activity` para runtime, separado de `crm_runtime` cuando sea posible.

## Consecuencias

Positivas:
- Un modelo universal cubre CRM personal, business CRM, reminders, schedule y next-actions.
- CRM y Calendar existentes se preservan.
- Zeus puede operar por tools sin UI obligatoria.
- Tests pueden validar DB readback, idempotencia y audit.

Negativas/costos:
- Más tablas y bridge work que extender `crm.follow_ups`.
- Requiere discipline de tool boundaries para no exponer PII.
- Requiere migration idempotente y careful grants.

## Criterios de aceptación F2

1. Schema placement decidido: `activity.*` en Agent Core Postgres.
2. Rationale documentado y `crm.follow_ups` queda como compatibility bridge, no source universal.
3. Diseño preserva `crm_*` y `calendar_*` tools existentes.
4. Modelo cubre relation graph, recurrence, reminders, plans, calendar bridge, dispatcher/audit y privacy assumptions.
5. No se introduce DB/service externo.
6. F4-F8 reciben data model, indexes, tool contracts y security assumptions claros.

## Handoff a incrementos siguientes

- F3: convertir esta ADR en task graph con dependencies, owners, reviewers y verification commands.
- F4: crear migración `db/modules/activity/000001_activity_schema.sql` con registry/grants/idempotency/indexes; no tocar runtime tools todavía.
- F5: implementar tool handlers JSON y tests de validación/SQL safety.
- F6: implementar calendar bridge + dispatcher determinístico.
- F7: implementar plans, recurrence, quick capture/detection.
- F8: bridge compatible con `crm.follow_ups` y timelines.
- F10: revisar PII/tool boundary/calendar notification risks antes de delivery.

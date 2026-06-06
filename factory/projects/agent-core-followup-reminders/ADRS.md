# ADR Register — Agent Core Follow-up / Reminders

## ADR-001 — Factory source of truth

- Estado: accepted for this run.
- Decisión: Agent Core Postgres `zeus_agent.factory` es la fuente operacional; artifacts project-locales bajo `factory/projects/agent-core-followup-reminders/` son evidencia de repo; Notion/wiki son documentación humana/agente, no runtime truth.
- Consecuencia: no SQLite runtime; no Kanban bridge salvo autorización explícita de Jean.

## ADR-002 — Universal Activity Layer over CRM + Calendar

- Estado: accepted by F2 architecture (`solution-architect`) and pending independent security review.
- Canonical ADR: `docs/followup-reminder-core/ADR-002-universal-activity-layer.md`.
- Project-local decisions: `factory/projects/agent-core-followup-reminders/ARCHITECTURE_DECISIONS.md`.
- Blueprint: `factory/projects/agent-core-followup-reminders/TECHNICAL_BLUEPRINT.md`.
- Decisión: crear schema nuevo `activity.*` en Agent Core Postgres.
- Rationale: Activity es capa universal para personal CRM, business CRM, reminders, tasks, meetings/calls, next-actions, activity plans, recurrence y links polimórficos; no debe quedar limitada a `crm.follow_ups`.
- Consecuencia: F4 debe crear migration module-owned en `db/modules/activity/`; F5 tools JSON bajo toolset explícito `activity`; F6 bridge Calendar; F8 bridge compatible con `crm.follow_ups`.

## ADR-003 — CRM compatibility bridge

- Estado: accepted by F2; implementation deferred to F8.
- Decisión: preservar `crm.follow_ups` y `crm_*` tools. `crm.follow_ups` queda como compatibility surface, no como source universal.
- Consecuencia: `crm_follow_up_create` debe create/link Activity Core o bridgear explícitamente; timelines deben incluir activities; duplicate prevention debe cruzar CRM interaction/follow-up/activity.

## ADR-004 — Calendar side-effect boundary

- Estado: accepted by F2; implementation deferred to F6 and review F10.
- Decisión: Calendar Core sigue siendo owner de time-blocked commitments. Activity sólo crea/actualiza calendar event cuando hay scheduling/time block explícito.
- Consecuencia: reminders/follow-ups no crean calendar events por defecto; calendar success/failure se audita en `activity.activity_events`.

## ADR-005 — Recurrence and dispatcher

- Estado: accepted by F2; implementation deferred to F6/F7.
- Decisión: RRULE RFC 5545 en `activity.recurrence_rules`, interpretado por `python-dateutil`; materialización bounded en `activity.recurrence_instances` cuando haga falta.
- Consecuencia: dispatcher escanea DB, usa idempotency keys, escribe audit y produce notification-ready output sin depender de memoria conversacional.

## ADR-006 — Toolset/security boundary

- Estado: accepted by F2; pending F10 security review.
- Decisión: toolset explícito `activity`, no default broad enablement sin revisión. Customer-facing agents requieren scope/tenant/minimización de metadata.
- Consecuencia: F5 debe registrar tools de forma explícita y F10 debe revisar exposición antes de delivery.

## ADRs pendientes después de F2

1. F10 security reviewer debe aprobar/modificar tool exposure, PII handling y notification/calendar confirmation rules.
2. F4/F5 podrán proponer ajustes menores de columnas/nombres durante implementación, pero no pueden cambiar el placement `activity.*` ni reemplazar CRM/Calendar sin nueva ADR.
3. F11 debe reconciliar docs/skills con evidencia real de implementación y smoke.

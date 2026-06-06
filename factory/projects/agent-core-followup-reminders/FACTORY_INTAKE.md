# FACTORY_INTAKE — F1 Functional PRD

## Identificación

- Project ID: `agent-core-followup-reminders`
- Task ID: `agent-core-followup-reminders-f1-full-functional-prd-for-agentic-follo`
- Incremento: F1 — Full functional PRD for agentic follow-up/reminder core
- Owner: `product-analyst`
- Reviewer: `solution-architect`
- Run: `run-1780701420-04edba37`
- Fecha: `2026-06-05T23:17:44Z`

## Contexto leído

- `docs/followup-reminder-core/FACTORY_SPEC-001-agent-core-followup-reminders.md`
- `docs/followup-reminder-core/ADR-002-universal-activity-layer.md`
- `docs/crm-capability/PRD-001-agent-crm-core.md`
- `docs/calendar-capability/ADR-001-agent-first-calendar-adapter.md`
- `factory/projects/agent-core-followup-reminders/TRACKER.md`
- `factory/projects/agent-core-followup-reminders/PRD.md` seed F0
- Factory DB vía `hermes factory status agent-core-followup-reminders --json`

## Scope exacto F1

Documentar el PRD funcional completo para la capa agentica de follow-up/reminders. No implementar migraciones, tools o jobs. No iniciar F2/F3. Dejar criterios verificables para que solution-architect revise functional gate y para que F2/F3 transformen el PRD en ADR/plan.

## Constraints aplicados

- Agent Core Postgres `factory.*` es fuente de verdad.
- Notion no es fuente operacional.
- No Kanban bridge.
- Sin UI/dashboard complejo como requisito.
- No duplicar CRM/Calendar existentes.
- No self-approval: F1 queda listo para review por `solution-architect`.

## Evidencia esperada

- Archivos F1 actualizados/creados bajo `factory/projects/agent-core-followup-reminders/`.
- Verificación de secciones obligatorias y estado Factory DB.
- Registro de functional gate como pending/review-ready, no aprobado por product-analyst.

## Evidencia consultada en este run

- Factory DB consultada con `./hermes factory status agent-core-followup-reminders --json`.
- El backend reportado es `agent_core_postgres` sobre base `zeus_agent` y schema operacional `factory.*`.
- La tarea F1 está reclamada por `product-analyst`, en fase `functional`, reviewer `solution-architect`, estado `running` al inicio del run.
- F0 aparece `done` con evidence status `present`; no se abrió otro incremento.
- Se leyeron los artifacts canónicos de CRM Core y Calendar Core para asegurar compatibilidad funcional.

## Resultado F1 esperado para review

F1 queda como entrega documental funcional, no como aprobación. El siguiente paso es que `solution-architect` revise el functional gate y, si lo aprueba, use este PRD como insumo para F2. Product Analyst no se autoaprueba.

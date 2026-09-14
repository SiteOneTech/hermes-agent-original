# Sprint Plan 001 — Sales Operator Core v1

## Objetivo del sprint

Entregar una primera versión operable del módulo vendedor diario para Empleado.uno: campañas, territorios, research, scoring, attack plans, CRM follow-ups y reportes diarios; outbound real gated hasta validación de canales.

## Duración sugerida

2 semanas Factory, con incrementos cerrables.

## Incrementos

### I0 — Planning + architecture gates

- Validar PRD/ADR/task graph/security gates.
- Confirmar repo scope `zeus_then_runtime`.
- Definir schema inicial.

### I1 — DB schema + module registration

- Crear `db/modules/sales_operator/000001_sales_operator_schema.sql`.
- Registrar módulo en Agent Core.
- Roles/grants runtime.
- Tests de migración.

### I2 — Hermes tools read/write core

- Crear `tools/sales_operator_tool.py`.
- Toolset `sales_operator`.
- Tools: status, campaign create, territory assign, lead import/enrich record, score, attack plan, daily rollup.
- Unit tests.

### I3 — CRM/Funnel integration

- Convertir lead aprobado a CRM org/contact/opportunity.
- Registrar interaction/follow-up.
- Evitar duplicados.
- Timeline verification.

### I4 — Policy engine + outbound queue

- Channel policies, opt-out, rate limits, allowed sources.
- Queue de acciones outbound.
- Execution fail-closed si canal no validado.
- Tests de stop rules.

### I5 — Empleado.uno campaign pack

- Product profile Empleado.uno.
- Vertical playbooks: clínicas/estética, restaurantes/delivery, educación/cursos, inmobiliarias.
- Mensajes base por canal.
- Demo/funnel URL mapping.

### I6 — Cron loops / daily operator

- Script daily brief.
- Script enrichment/follow-up tick.
- No-agent safe mode para reportes.
- Cron disabled or dry-run by default until Jean activates.

### I7 — Live pilot smoke

- Crear campaña test con 1 territorio.
- Importar 10 leads manuales/sintéticos o públicos de prueba.
- Generar scoring/attack plan.
- Crear 1 CRM follow-up de prueba.
- Verify DB + tools + rollup.

### I8 — Runtime propagation handoff

- Preparar branch/worktree contra `SiteOneTech/sitiouno-agent-runtime`.
- Propagar solo superficie heredable/práctica del Sales Operator Core.
- Mantener admin/factory internals exclusivos de Zeus.
- Ejecutar tests/smoke equivalentes en runtime.
- Dejar outbound real bloqueado hasta channel/security gate.

## Definition of Done

- Docs actualizadas.
- Tests específicos pasan.
- Compile/ruff sin errores nuevos.
- Agent Core migrate/status probado si DB disponible.
- Toolset resuelve tools.
- Smoke live genera campaña/territorio/leads/rollup.
- Outbound real no se ejecuta sin policy/channel gate.

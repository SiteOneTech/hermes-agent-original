# Methodology Plan — Hybrid Factory Lane

## Proyecto

`agent-core-followup-reminders`

## Metodología

Hybrid: disciplina documental/PM + Agent Core Factory DB + ejecución autónoma por workers/reviewers.

## Principios

1. Factory DB manda: status, tasks, gates, runs y evidence salen de Agent Core Postgres.
2. Project-local artifacts viven en `factory/projects/agent-core-followup-reminders/`.
3. Increments son secuenciales: un worker/reviewer cierra un incremento antes de abrir el siguiente, salvo ADR explícita.
4. Implementer y reviewer no pueden ser el mismo perfil.
5. Zeus supervisa y corrige drift, pero no autoaprueba entregables de workers.
6. `Retomar proyecto` es handoff/contexto; autonomía real exige `autonomous_enabled=true` + cron/tick activo.

## Flujo operativo

```text
intake/kickoff
  -> F1 functional PRD
  -> F2 architecture ADR/data model
  -> F3 implementation plan/task graph
  -> F4-F8 implementation increments
  -> F9 QA smoke/regression
  -> F10 security/privacy/tool boundary
  -> F11 delivery docs/reconciliation
```

## Worker contract

Cada run debe dejar:

- Archivos tocados.
- Comandos ejecutados.
- Evidencia de lectura/escritura/DB/tool output.
- `STATE: DONE` solo cuando la unidad asignada cumple criterios.
- Blocker explícito si falta acceso, contexto o autorización.

## Reviewer contract

Cada review debe validar:

- Skill `agent-core-followup-reminders` cargable en el perfil.
- Artifacts correctos del proyecto, sin contaminación de otros proyectos.
- Factory DB en Postgres, no SQLite.
- Evidencia real, no solo resumen del implementer.
- Próxima tarea autorizada solo si el gate actual pasa.

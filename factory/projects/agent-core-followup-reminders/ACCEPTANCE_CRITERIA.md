# ACCEPTANCE_CRITERIA — Agent Core Follow-up / Reminders

## Estado

- Incremento: F1
- Run: `run-1780701420-04edba37`
- Fecha: `2026-06-05T23:17:44Z`
- Estos criterios gobiernan F2-F11 y QA final. F1 no implementa código runtime.

## Criterios funcionales globales

### A. Activity core

1. Zeus puede crear/upsert una activity universal con tipo, título, estado, prioridad, fechas, source y metadata.
2. Una activity puede vincularse a múltiples entidades con relaciones tipadas.
3. Zeus puede listar activities por today, upcoming, overdue, waiting, snoozed/resurfaced, person, organization, opportunity, project, source y priority.
4. Zeus puede completar, cancelar, snoozear y reagendar una activity con audit event.
5. Zeus puede recuperar timeline por entidad con interactions, activities, calendar links, decisions/notes permitidas y next actions.

### B. CRM compatibility

6. `crm_follow_up_create` sigue funcionando para callers existentes.
7. CRM follow-ups nuevos se crean/linkean a activity universal o bridge equivalente sin duplicar.
8. `crm_customer_timeline` incluye activities/follow-ups relevantes o existe tool timeline nuevo documentado y probado.
9. Registrar una interacción CRM con follow-up no crea duplicado si ya existe un pending equivalente.

### C. Calendar compatibility

10. Calendar Core sigue siendo la capa para eventos/time blocks/availability.
11. Recordatorios y follow-ups sin tiempo bloqueado no crean calendar event por defecto.
12. Meetings/calls con horario pueden crear/linkear calendar event mediante `calendar_*` tools/adapters.
13. Calendar side effects son idempotentes y auditados.
14. Fallas de calendar adapter dejan activity intacta y error retryable.

### D. Reminders/dispatcher

15. Dispatcher determinístico escanea due/upcoming/overdue/snoozed/recurrence sin memoria conversacional.
16. Dispatcher produce notification-ready outputs auditados con activity_id/rule_id/window/status.
17. Dispatcher evita duplicar notificaciones por scan window/idempotency key.
18. Recurrence genera o detecta siguiente ocurrencia de forma idempotente.

### E. Quick capture/detection

19. Tool de detección desde texto devuelve candidatos con evidence span, confidence, proposed links y fecha interpretada.
20. Modo suggest-only no persiste side effects.
21. Modo create-authorized persiste sólo candidatos suficientemente claros y retorna ambiguos para confirmación.
22. Parser de fecha natural maneja incertidumbre explícitamente.

### F. Activity plans/chaining

23. Se pueden crear planes reutilizables con steps relativos.
24. Aplicar plan crea activities linkeadas al contexto primario.
25. Completar un step puede sugerir/crear siguiente step según configuración.
26. Plan progress se puede consultar por entidad/contexto.

### G. Seguridad/privacy/tool boundary

27. PII/notas privadas no se exponen fuera del owner/tenant/tool boundary autorizado.
28. Customer-facing personas no reciben tools privilegiadas por herencia accidental.
29. Notificaciones externas requieren autorización/configuración explícita.
30. No se guardan secretos/tokens en metadata/audit.

### H. Operación sin UI

31. Todas las capacidades críticas son verificables por tools, tests o DB readback.
32. No hay requisito de dashboard/filtros visuales para operar el Core.
33. Las respuestas agenticas devuelven IDs, estado y evidencia suficiente para seguimiento.

## Criterios F1 específicos

F1 pasa si:

1. `factory/projects/agent-core-followup-reminders/PRD.md` contiene PRD funcional completo.
2. `factory/projects/agent-core-followup-reminders/FUNCTIONAL_SPEC.md` contiene flujos, reglas y boundaries.
3. `factory/projects/agent-core-followup-reminders/ACCEPTANCE_CRITERIA.md` contiene criterios verificables para implementadores y QA.
4. `factory/projects/agent-core-followup-reminders/FACTORY_INTAKE.md` documenta intake F1 y evidencia consultada.
5. El tracker project-local registra cierre F1 y próximos pasos F2/F3 sin abrir otro incremento.
6. Factory DB queda con evidencia de run F1 o, si el comando específico no existe, el resumen final incluye comandos/paths/resultados.

## Comandos mínimos de verificación para F1

- `hermes factory status agent-core-followup-reminders --json`
- validación por script de existencia y secciones obligatorias.
- `git diff -- factory/projects/agent-core-followup-reminders/PRD.md factory/projects/agent-core-followup-reminders/FUNCTIONAL_SPEC.md factory/projects/agent-core-followup-reminders/ACCEPTANCE_CRITERIA.md factory/projects/agent-core-followup-reminders/FACTORY_INTAKE.md factory/projects/agent-core-followup-reminders/TRACKER.md`

## Evidencia mínima que debe producir F1

1. Lectura de estado Factory desde Agent Core Postgres, mostrando F1 en phase `functional`, owner `product-analyst`, reviewer `solution-architect`.
2. Validación local de que los tres documentos F1 contienen: agentic UX/no-dashboard, CRM compatibility, Calendar compatibility, dedupe, quick capture, timelines, dispatcher, privacy/tool boundary y QA sin UI.
3. Registro del gate `functional` como `pending` para revisión independiente, no como `passed` por el implementador.

# FACTORY_SPEC-001 — Agent Core Personal CRM / Follow-up / Reminders

## Estado

`ready_for_factory_intake` — especificación ajustada según la corrección de Jean: esto no es una plataforma UI de CRM/tareas; es un Core agentico que Zeus usa con tools, base de datos, calendario/scheduler existente y ejecución por Software Factory.

## Dirección ejecutiva de Jean

1. **Compatibilidad primero:** si ya existe `crm` y `calendar/schedule`, se amplían. No se crea un módulo desconectado ni se duplica el scheduler.
2. **CORE agentico:** no se diseña una UI compleja, filtros visuales, tableros o pantallas de usuario final. El usuario pide en lenguaje natural y Zeus ejecuta, busca, agenda, recuerda, relaciona y reporta usando tools.
3. **Fuente canónica:** usar la base de datos existente de Agent Core / Postgres compartido. Las librerías open source son permitidas si ayudan, pero como dependencia/patrón, no como copia de implementación.
4. **Patrones, no código copiado:** los repos open-source investigados sirven para extraer arquitectura/funcionalidad: Twenty, Monica, EspoCRM, Odoo, ERPNext, Vikunja, SuiteCRM. No se copia código AGPL/GPL ni esquemas literales.
5. **Factory obligatorio:** el proyecto debe ejecutarse en Software Factory con tareas, lanes, gates, evidencias, reviewers independientes y skills adecuados para los agentes.
6. **Alcance completo desde el inicio:** no se plantea como MVP/V2/V3. Se organiza por incrementos de ejecución, pero cada incremento pertenece a una arquitectura objetivo completa.

## Objetivo

Convertir el CRM Core + Calendar Core existentes en una capacidad agentica integral de memoria relacional, actividades, follow-ups, recordatorios, agenda y next-actions para Zeus y futuros agentes SitioUno.

El resultado esperado es que Zeus pueda operar conversaciones como:

- “Recuérdame llamar a Ana el viernes y enlázalo con Qrovia.”
- “¿A quién debo escribir hoy?”
- “¿Qué follow-ups están vencidos?”
- “Cierra este pendiente y crea el siguiente paso en 7 días.”
- “Agenda una llamada con este cliente y crea seguimiento posterior.”
- “¿Qué pasó con esta persona/proyecto desde la última vez?”
- “Detecta pendientes de este email/chat y guárdalos.”

## Contexto existente que debe respetarse

### CRM Core existente

Archivos relevantes:

- `docs/crm-capability/PRD-001-agent-crm-core.md`
- `docs/crm-capability/ADR-001-agent-native-crm-core.md`
- `db/modules/crm/000001_crm_schema.sql`
- `db/modules/crm/000003_business_crm_and_adapters.sql`
- `tools/crm_tool.py`
- `tests/tools/test_crm_tool.py`
- Skill: `agent-crm-core`

Capacidades actuales: organizations, contacts, relationships, opportunities, products, quotes, invoices, interactions, follow-ups, timeline/search, optional Twenty adapter.

### Calendar/Schedule Core existente

Archivos relevantes:

- `docs/calendar-capability/ADR-001-agent-first-calendar-adapter.md`
- `db/modules/calendar/000001_calendar_registry.sql`
- `tools/calendar_tool.py`
- `tests/tools/test_calendar_tool.py`
- Skill: `calendar-agenda-queries`

Capacidades actuales: tool layer genérico sobre backend scheduler reemplazable; primer adapter Nettu; actors, calendars, events, blocks, services, availability.

## Patrones open-source que se deben usar

### Twenty

- Objetos estándar + custom objects.
- Tasks/Notes vinculables a People, Companies, Opportunities y records arbitrarios.
- Workflows por create/update/delete/manual/schedule/webhook.

Aplicar como: registry de tipos, relaciones polimórficas y triggers agenticos.

### Monica

- Personal CRM centrado en personas.
- Relaciones personales, cumpleaños, notas privadas, cómo conociste a alguien, actividades, tareas, regalos/deudas.

Aplicar como: memoria relacional personal no limitada a ventas.

### EspoCRM

- Meetings, Calls, Tasks.
- Reminders popup/email.
- Attendees con status.
- Calendar/free-busy/shared activities.

Aplicar como: actividades temporales con participantes y compatibilidad calendario.

### Odoo

- Activity universal asociada a cualquier record.
- Chatter/timeline.
- Estados late/today/future.
- Activity chaining y Activity Plans.

Aplicar como: motor de next-actions y secuencias reutilizables.

### Vikunja

- Recurring tasks, subtasks, priorities, labels, saved filters, relations/blockers, quick add.

Aplicar como: atributos de tarea, recurrencia, dependencias y captura rápida por lenguaje natural.

### ERPNext/Frappe

- Metadata-driven documents, assignments, comments, lifecycle, permisos por rol.

Aplicar como: extensibilidad de tipos sin acoplar tools a una sola vertical.

## Arquitectura objetivo

### 1. Universal Activity Layer

Agregar o evolucionar una tabla/capa canónica de actividad que reemplace la limitación de `crm.follow_ups` como única estructura de pendiente.

Campos conceptuales:

- `activity_id`
- `activity_type`: task, call, meeting, email, reminder, note, document, custom
- `title`
- `description`
- `status`: planned, open, done, cancelled, snoozed, waiting
- `priority`
- `due_at`, `start_at`, `end_at`, `completed_at`, `snoozed_until`
- `recurrence_rule`
- `owner_id`, `assignee_id`
- `participants` / attendees
- `reminder_rules`
- `source`: manual, agent, whatsapp, email, calendar, crm, webhook, schedule
- `metadata`

Debe soportar relación a múltiples records mediante una tabla genérica, no sólo foreign keys fijos a CRM:

- contact/person
- organization
- opportunity
- project
- quote/invoice/document
- calendar_event
- external_ref
- future custom object

### 2. Timeline / chatter agentico

Cada entidad importante debe poder producir un timeline agentico:

- notas
- interacciones
- actividades abiertas/cerradas
- eventos de calendario vinculados
- decisiones
- próximos pasos
- source/evidence

El agente debe recuperar esto con tools, no mediante una UI humana.

### 3. Calendar/Schedule bridge

La capa Activity debe integrarse con `calendar_*`:

- Si la actividad bloquea tiempo real, crear/actualizar event/block en Calendar Core.
- Si es sólo recordatorio/follow-up, no forzar calendar event.
- Para reuniones/calls, usar free/busy y participantes.
- Guardar external links entre activity y calendar event.
- Mantener quirks de Nettu dentro de adapter, no en prompts ni en la lógica del agente.

### 4. Workflow / next-action engine

Capacidades requeridas:

- completar una actividad y sugerir/crear la siguiente
- activity plans/secuencias reutilizables
- recurrencia tipo RRULE
- snooze/reschedule/cancel
- recordatorios por due date y por reglas relativas
- detección de follow-ups desde email/chat/texto
- job determinístico que escanea actividades vencidas/próximas y genera notificaciones o reportes
- evitar duplicados cuando `crm_interaction_record` ya creó un follow-up

### 5. Tools para Zeus

Crear o extender tools genéricas, posiblemente en un toolset `followup` o ampliando `crm`/`calendar` de forma compatible:

- `activity_upsert`
- `activity_link`
- `activity_complete`
- `activity_snooze`
- `activity_reschedule`
- `activity_cancel`
- `activity_list_due`
- `activity_timeline`
- `activity_plan_create`
- `activity_plan_apply`
- `activity_next_actions`
- `activity_detect_from_text`
- `activity_to_calendar_event`
- `followup_status` / health check

Los nombres exactos los decide el equipo técnico, pero el contrato debe ser estable, JSON, agent-friendly y usable desde chat.

### 6. Búsqueda/graph interno

No diseñar filtros visuales. Diseñar consultas/tools para que Zeus responda natural-language queries:

- due today/upcoming/overdue
- waiting-for
- by person/project/business/opportunity
- by priority/source/channel
- unresolved decisions
- relationship graph around a person/company/project

Opciones técnicas permitidas:

- Postgres JSONB + GIN indexes.
- Relation graph con tabla de edges.
- Recursive CTEs para graph traversal acotado.
- `networkx` para análisis offline/test si aporta valor.
- `dateparser`/`parsedatetime` para fechas naturales.
- `python-dateutil` para RRULE/recurrence.

No agregar graph database externa salvo ADR aprobado por architect + security.

## Incrementos de ejecución Factory

Estos incrementos no son versiones de producto. Son unidades de ejecución para completar el alcance total.

### Incremento 0 — Governance y preparación

- Crear/actualizar Notion PM tracker si está habilitado.
- Registrar proyecto/lane/tasks/gates en Factory DB.
- Asegurar que agentes tengan skills: `agent-core-followup-reminders`, `agent-core-functional-modules`, `agent-crm-core`, `software-factory-orchestration`, `test-driven-development`, `requesting-code-review` y `calendar-agenda-queries` cuando aplique.
- Confirmar backend Factory: Agent Core Postgres canónico.

### Incremento 1 — Functional + Architecture

- PRD completo sin MVP/V2/V3.
- ADR de integración CRM + Calendar + Activity Layer.
- Threat/privacy model: PII, reminders/notificaciones, customer-facing boundaries.
- Task graph con owners/reviewers independientes.

### Incremento 2 — DB migrations

- Nueva migración module-owned, probablemente `db/modules/crm/000004_universal_activities.sql` o módulo `activity` si el architect lo decide.
- Tablas para activities, activity_links, reminders, plans, plan_steps, recurrence/audit/events.
- Grants/runtime roles compatibles con Agent Core.
- Índices para due/today/overdue/search/relations.

### Incremento 3 — Tools y toolsets

- Implementar handlers JSON con validación fuerte.
- Evitar SQL injection con quoting helpers existentes.
- Toolset nuevo o extensión compatible de `crm`.
- Direct handler smoke con datos sintéticos.

### Incremento 4 — Calendar bridge + dispatcher

- Link activity ↔ calendar event/block.
- Usar `calendar_find_availability`, `calendar_create_event`, `calendar_update_event`, etc. cuando aplique.
- Job determinístico para reminders/upcoming/due.
- No depender de memoria de chat.

### Incremento 5 — Agentic quick capture + next actions

- Parser para fechas naturales/recurrencia.
- Detector de follow-ups desde texto/mensajes/emails.
- Activity plans y chaining.
- Timeline/next-action summarization tools.

### Incremento 6 — QA, security, docs, delivery

- Unit tests.
- Regression tests para CRM/calendar tools.
- Live DB smoke si Agent Core Postgres está disponible.
- Calendar adapter smoke si env está configurado.
- Security review independiente.
- Update skills/docs y Factory delivery report.

## Criterios de aceptación globales

1. Zeus puede crear, leer, actualizar, completar, cancelar, posponer y reagendar actividades/follow-ups usando tools.
2. Una actividad puede vincularse a múltiples records sin limitarse a CRM comercial.
3. CRM Core sigue funcionando; `crm_follow_up_create` no se rompe y se integra o migra al nuevo Activity Layer.
4. Calendar Core sigue funcionando; eventos de calendario se crean sólo cuando corresponde.
5. Se soportan reminders, due/today/overdue/upcoming, waiting-for, recurrence y snooze.
6. Se soportan activity plans/chaining para next-actions.
7. El agente puede recuperar timeline por persona/proyecto/organización/oportunidad.
8. El agente puede detectar candidatos de follow-up desde texto con evidencia y sin ejecutar side effects no autorizados.
9. No hay UI compleja de usuario final ni dependencias de dashboard para operar el Core.
10. No se copia código/esquema AGPL/GPL de repos investigados.
11. Migrations, runtime roles/secrets, tests y docs están actualizados.
12. Factory DB, Notion/repo artifacts y gate evidence quedan sincronizados.

## Gates requeridos

- `intake`: esta especificación aceptada como alcance.
- `functional`: PRD y casos agenticos completos.
- `architecture`: ADR compatible con CRM/Calendar existentes.
- `planning`: task graph con owners/reviewers independientes.
- `implementation`: migrations/tools/jobs entregados con evidencia.
- `quality`: unit/regression tests pasan.
- `security`: PII, reminders, notifications y tool boundaries revisados.
- `delivery`: Zeus puede usar la capacidad por tools y se verifican IDs/readbacks.

## Agentes sugeridos

- `product-analyst`: PRD/casos/correcciones de alcance.
- `solution-architect`: ADR, DB model, adapter boundaries.
- `implementation-planner`: task graph detallado y dependencias.
- `claude-builder`: implementación compleja/migrations/tools/jobs.
- `codex-builder`: tests, bounded fixes, diff QA.
- `qa-verifier`: smoke/regression evidence.
- `security-reviewer`: privacy/tool-boundary/side-effect review.
- `devops-release`: migrations/env/cron/runtime readiness.
- `factory-reporter`: Notion/docs/status reconciliation.

## Skills que deben cargar los agentes Factory

- `agent-core-followup-reminders`
- `agent-core-functional-modules`
- `agent-crm-core`
- `calendar-agenda-queries`
- `software-factory-orchestration`
- `test-driven-development`
- `requesting-code-review`
- `github-pr-workflow` para PR/release
- `notion` para reporter si se crea PM tracker

## No-goals

- No construir un CRM visual ni task manager estilo SaaS para el usuario final.
- No crear filtros complejos como producto UX.
- No crear otro Postgres/servicio para el módulo si Agent Core DB es suficiente.
- No sustituir Calendar Core por otra agenda sin ADR.
- No copiar código de Twenty/Monica/Odoo/etc.
- No cerrar como “listo” sin smoke real de tools/tests/readback.

## Evidencia de entrega esperada

- Archivos modificados/lista de migraciones.
- Resultado de tests target y regression.
- Output de direct handler smoke con IDs reales.
- Output de DB readback mostrando activities/links/reminders/plans.
- Output de calendar adapter smoke si configurado.
- Gate records en Factory DB.
- Delivery report con riesgos y decisiones.

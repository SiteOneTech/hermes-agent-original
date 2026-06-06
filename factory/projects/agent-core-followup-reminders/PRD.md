# PRD — Agent Core Personal CRM / Follow-up / Reminders

## 1. Estado y alcance Factory

- Project ID: `agent-core-followup-reminders`
- Incremento: F1 — Full functional PRD for agentic follow-up/reminder core
- Owner: `product-analyst`
- Reviewer: `solution-architect`
- Fuente de verdad operacional: Agent Core Postgres `zeus_agent.factory` / schema `factory.*`
- Repo: `/home/jean/Projects/hermes-agent-original`
- Run F1: `run-1780701420-04edba37`
- Fecha de cierre F1: `2026-06-05T23:17:44Z`

Este PRD define el alcance funcional completo de la capacidad agentica de follow-up/reminders. No divide el producto en MVP/V2/V3. Los incrementos F2-F11 son unidades de ejecución para entregar una arquitectura objetivo única.

## 2. Tesis de producto

Zeus debe operar una capa universal de actividades, follow-ups, recordatorios, agenda y próximos pasos sobre el Agent Core existente. El usuario conversa en lenguaje natural; Zeus decide qué tool usar, crea o actualiza registros, vincula contexto, programa recordatorios, consulta timelines y ejecuta jobs determinísticos. El producto no es una UI compleja de CRM/tareas ni un dashboard con filtros humanos; la UX principal es agentic/chat-first.

## 3. Problema

El CRM Core ya modela organizaciones, contactos, oportunidades, interacciones y follow-ups. Calendar Core ya permite calendarios, eventos, disponibilidad y reservas. La brecha es que los pendientes, recordatorios, tareas, llamadas, secuencias y next-actions siguen fragmentados:

1. `crm.follow_ups` es útil para CRM comercial, pero no cubre bien recordatorios personales, proyectos, documentos, recurrencia, snooze, activity plans ni relaciones múltiples.
2. Calendar Core representa tiempo bloqueado, pero no debe ser el lugar canónico de todo pendiente o recordatorio.
3. La memoria conversacional no es una fuente confiable para recordatorios determinísticos.
4. Zeus necesita consultar y actuar sobre pendientes por persona, empresa, proyecto, oportunidad, fuente, prioridad, vencimiento y relación sin depender de una UI humana.
5. Registrar interacciones puede crear duplicados si no existe una regla de idempotencia entre interacción, follow-up y activity universal.

## 4. Objetivos

1. Crear una Universal Activity Layer canónica para actividades, follow-ups, reminders, tareas, llamadas, reuniones, notas accionables, next-actions, activity plans y recurrencia.
2. Extender CRM Core sin romper `crm_*` tools existentes ni `crm.follow_ups`.
3. Integrar Calendar Core sólo cuando la activity realmente bloquea tiempo o requiere scheduling/free-busy.
4. Permitir operación completa por Hermes tools JSON y jobs determinísticos, sin UI obligatoria.
5. Prevenir duplicados entre interacciones CRM, follow-ups, activities y eventos calendarizados.
6. Producir timelines agenticos por persona/organización/oportunidad/proyecto con evidencia y links.
7. Soportar quick capture natural-language con manejo explícito de incertidumbre.
8. Auditar side effects: calendar events, notificaciones, completion, snooze, reschedule, cancel, plan application y detección desde texto.
9. Proteger PII/notas privadas y evitar exposición de tools privilegiadas a agentes o personas customer-facing.

## 5. No objetivos

- No construir un SaaS visual de CRM/tareas como producto principal.
- No crear filtros complejos o dashboards human-first como requisito de operación.
- No reemplazar CRM Core ni Calendar Core.
- No crear una base de datos separada si Agent Core Postgres soporta el diseño.
- No copiar código o esquemas de proyectos GPL/AGPL/open source investigados; sólo usar patrones.
- No enviar notificaciones externas o crear eventos de calendario sin reglas de autorización/auditoría.
- No resolver en F1 el diseño físico final de tablas: eso corresponde a F2, aunque este PRD fija el contrato funcional.

## 6. Usuarios/personas

### 6.1 Jean / owner principal

Pide acciones en español o inglés por CLI, Telegram, WhatsApp, voz o canal conectado: “recuérdame”, “agenda”, “¿a quién escribo?”, “qué pasó con X”. Espera que Zeus recuerde, relacione y ejecute sin que Jean tenga que navegar un tablero.

### 6.2 Zeus / agente operador

Interpreta intención, resuelve entidades, llama tools, evita duplicados, pide confirmación cuando hay side effects relevantes y reporta IDs/readbacks. Zeus necesita contratos JSON estables y resultados accionables.

### 6.3 Agente heredado de cliente/empresa

Usa la misma capacidad con datos de su tenant/contexto, pero sólo con toolsets autorizados. No debe heredar herramientas owner-only o acceso amplio a notas privadas.

### 6.4 Equipo Factory

Implementa, revisa y verifica con evidence: migraciones, tool tests, DB readbacks, smoke tests, gates y delivery docs.

### 6.5 Sistemas externos/adapters

CRM adapters, calendar adapters, email/WhatsApp/webhooks y futuros módulos aportan eventos o referencias; no son la fuente única de actividades universales.

## 7. Modelo funcional de activity

Una activity representa una unidad accionable o informativa que Zeus puede consultar y operar. Debe cubrir: `task`, `follow_up`, `reminder`, `call`, `meeting`, `email`, `message`, `note`, `document`, `approval` y `custom`.

Estados funcionales mínimos: `open`, `planned`, `waiting`, `snoozed`, `done`, `cancelled`.

Fechas funcionales: `due_at`, `start_at`, `end_at`, `completed_at`, `snoozed_until`, y `next_scan_at` si F2/F6 decide materializar el scheduler del dispatcher.

## 8. Entidades y relaciones

Una activity puede estar vinculada a múltiples objetos: persona/contacto, organización/empresa, oportunidad/deal, proyecto, factura/cotización/documento, conversación/email/chat, calendar event/block, external ref/adapters, activity previa/siguiente y plan/step.

Relaciones funcionales requeridas: `primary`, `context`, `participant`, `derived_from`, `next_after`, `blocks`, `blocked_by`, `calendar_event`, `duplicate_of`, `merged_into`.

## 9. Casos de uso principales

### UC-01 Crear reminder personal

Usuario: “Recuérdame llamar a Ana el viernes.”

Flujo: Zeus parsea intención/persona/fecha, resuelve contacto si hace falta, crea activity tipo `reminder` o `call` sin calendar event por defecto, y retorna ID, fecha interpretada, links y cómo cambiarla.

### UC-02 Crear follow-up comercial desde interacción CRM

Usuario: “Registré llamada con Qrovia; debo enviar propuesta el martes.”

Flujo: Zeus registra interacción si corresponde, detecta follow-up con evidencia, aplica no-duplicación sobre persona/empresa/oportunidad/subject/due window/source, crea o actualiza activity universal y linkea/bridgea `crm.follow_ups` si aplica. El timeline de Qrovia muestra interacción + follow-up.

### UC-03 Consultar pendientes del día

Usuario: “¿A quién debo escribir hoy?”

Flujo: Zeus consulta due/today/open/waiting/resurfaced por owner/contexto, agrupa por persona/empresa/proyecto/prioridad y retorna lista con IDs, título, motivo, vencimiento, último contexto y acción recomendada.

### UC-04 Cerrar y crear siguiente paso

Usuario: “Cierra este pendiente y crea el siguiente paso en 7 días.”

Flujo: Zeus identifica activity, marca `done`, crea nueva activity `next_after` con due_at relativo y, si hay activity plan, aplica/sugiere el step siguiente.

### UC-05 Agenda una llamada con seguimiento posterior

Usuario: “Agenda una llamada con este cliente mañana a las 3 y crea seguimiento posterior.”

Flujo: Zeus valida participantes/horario, usa Calendar Core para availability/event si bloquea tiempo, crea activity tipo `meeting/call` linked a calendar event, crea follow-up posterior y audita IDs/side effects.

### UC-06 Detectar pendientes desde email/chat/texto

Usuario: “Detecta pendientes de este email y guárdalos.”

Flujo: detección extrae candidatos con evidence spans, fechas, participantes, confianza y side effects propuestos. Si el usuario dijo “guárdalos”, Zeus crea candidatos claros y lista ambiguos; si no, sólo sugiere.

### UC-07 Timeline agentico

Usuario: “¿Qué pasó con esta persona/proyecto desde la última vez?”

Flujo: Zeus consulta relaciones, interacciones, activities, calendar links y decisiones; ordena hechos, pendientes, vencidos, próximos pasos y riesgos; retorna evidencia con IDs/fuentes.

### UC-08 Waiting-for y bloqueo

Usuario: “Estoy esperando respuesta de Ricardo sobre Qrovia.”

Flujo: Zeus crea activity status `waiting` relacionada a Ricardo + Qrovia; `due_at` puede ser opcional o review date; consultas “waiting for” muestran estos ítems con antigüedad.

### UC-09 Recurrencia

Usuario: “Recuérdame revisar pipeline cada lunes a las 9.”

Flujo: Zeus crea rule recurrente; dispatcher materializa/detecta ocurrencias vencidas/próximas; completion de una ocurrencia preserva la regla y genera la siguiente idempotentemente.

### UC-10 Activity plan

Usuario: “Aplica plan de onboarding a este nuevo cliente.”

Flujo: Zeus selecciona plan, crea steps relativos linkeados a cliente/contactos/oportunidad y cada completion sugiere/activa el siguiente step según configuración.

## 10. Reglas de negocio

### 10.1 No duplicación / idempotencia

1. Toda creación desde texto, interacción o tool debe calcular una llave funcional de deduplicación: owner/contexto primario/tipo/título normalizado/due window/source/source_ref, ajustada por F2.
2. Si existe activity abierta equivalente, se actualiza/linkea y no se inserta duplicado.
3. Si existe `crm.follow_ups` legacy equivalente, el bridge debe mapearla a activity o declarar vínculo de compatibilidad.
4. Las activities canceladas/done no bloquean una nueva si el usuario solicita explícitamente otro ciclo.
5. Duplicados detectados después pueden marcarse `duplicate_of` o `merged_into` sin perder audit trail.

### 10.2 Calendar side effects

1. Sólo `meeting`, `call` con horario, time-block o solicitud explícita de agenda crean/actualizan Calendar Core.
2. `reminder` y `follow_up` sin tiempo bloqueado no crean calendar event por defecto.
3. Crear, actualizar o cancelar calendar event requiere audit record con adapter, external_id, payload mínimo y resultado.
4. Fallas de Calendar Core no deben borrar la activity; deben dejar estado/link de error para retry o acción humana.
5. Cambios desde calendar adapter deben reconciliar activity link si F6 implementa inbound sync.

### 10.3 Confirmaciones

Zeus puede actuar sin preguntar cuando crea reminder/follow-up privado para owner, lista/resume activities, completa/cancela/snoozea una activity identificada, o guarda candidatos extraídos cuando el usuario ordenó explícitamente “guárdalos”.

Zeus debe confirmar o exponer incertidumbre cuando hay múltiples entidades plausibles, se enviaría notificación externa, se crearía/editaría/cancelaría evento con terceros, se comparte nota privada/PII, la fecha natural es ambigua o la acción afecta otro tenant/persona customer-facing.

### 10.4 Privacidad y tool boundary

Activities pueden contener PII, notas privadas y relaciones personales; F10 debe revisar permisos y tool exposure. Customer-facing agents sólo reciben tools/queries autorizadas. Results deben minimizar metadata sensible. No se guardan secretos/tokens en metadata/audit.

### 10.5 Source/evidence

Toda activity creada por detección o automatización debe guardar o referenciar source channel/tipo, source_ref estable, evidence span/resumen si aplica, actor, timestamp y confidence.

## 11. Contratos agenticos esperados

Los nombres exactos quedan para F2/F3/F5, pero los contratos funcionales deben cubrir:

### 11.1 Upsert activity

Entrada conceptual:

```json
{
  "type": "follow_up",
  "title": "Enviar propuesta Qrovia",
  "due_at": "2026-06-09T14:00:00Z",
  "priority": "high",
  "status": "open",
  "links": [{"type": "organization", "id": "...", "relationship": "primary"}],
  "source": "agent",
  "dedupe": true
}
```

Salida esperada:

```json
{
  "ok": true,
  "activity_id": "...",
  "operation": "created|updated|linked_existing",
  "dedupe_key": "...",
  "links": [],
  "requires_confirmation": false
}
```

### 11.2 Query due/upcoming/overdue/waiting

Acepta filtros por owner, date range, status, type, linked entity, priority, source y limit; devuelve IDs, títulos, vencimientos, contextos, last evidence y next action.

### 11.3 Complete/snooze/reschedule/cancel

Valida transición de estado, registra audit y devuelve previous_state/new_state. Si completion genera next action por plan/chaining, devuelve ID creado/sugerido.

### 11.4 Timeline

Consulta por entity ref y retorna eventos ordenados: interactions, activities, calendar links, state changes, notes/decisions permitidas y pendientes abiertos.

### 11.5 Detect from text

Separa detección de persistencia: `suggest_only` devuelve candidatos sin side effects; `create_authorized` persiste candidatos confiables y devuelve creados/omitidos/ambiguos. Cada candidato incluye evidence span, confidence, proposed type/date/links y razón de ambigüedad.

### 11.6 Calendar bridge

Crea/linkea evento sólo cuando `calendar_required=true` o type/time implica scheduling. Devuelve activity_id, calendar_event_id/external_id, adapter status y audit event.

### 11.7 Activity plans

Crea/actualiza planes reutilizables con steps relativos, aplica plan a entity/contexto, lista progress y permite pause/cancel/skip de steps.

## 12. Natural-language UX: ejemplos y respuestas

- “Recuérdame llamar a Ana el viernes y enlázalo con Qrovia.” → “Listo. Creé el recordatorio `act_...` para llamar a Ana el viernes, vinculado a Ana y Qrovia. No creé evento de calendario porque pediste recordatorio, no agenda.”
- “¿Qué follow-ups están vencidos?” → “Hay 3 vencidos: 1) `act_...` Enviar propuesta a Qrovia, venció ayer, contexto: oportunidad Q2...”
- “Detecta pendientes de este email.” → “Detecté 2 candidatos... No guardé nada porque pediste detectar, no guardar.”

## 13. Reportes/consultas requeridas para Zeus

Hoy, vencidos, próximos, waiting-for, por persona, por empresa/proyecto/oportunidad, por source/channel, por plan y health/status de dispatcher/adapters.

## 14. Requisitos de dispatcher determinístico

1. Escanea activities/reminder rules por due/upcoming/overdue/snoozed_until/recurrence sin memoria de chat.
2. Produce salida auditable: activity IDs, rule IDs, intended notification/action, status, timestamps.
3. Es idempotente por scan window y notification key.
4. Separa “notification-ready output” de envío real si el canal externo no está aprobado/configurado.
5. Registra errores y permite retry.

## 15. Requisitos de compatibilidad CRM

`crm_follow_up_create` no debe romperse; si se mantiene como API legacy, crea/linkea activity universal o registra bridge explícito. `crm_customer_timeline` incluye follow-ups/activities relevantes o delega a `activity_timeline`. Interactions CRM que generan follow-up usan dedupe. Tests de `tools/crm_tool.py` siguen pasando o se actualizan con compatibilidad demostrada.

## 16. Requisitos de compatibilidad Calendar

Calendar Core sigue siendo source de time-blocked commitments. Activity Core no reemplaza availability/event adapters. Calendar links son idempotentes y auditados. Non-calendar reminders no crean eventos. Regression tests relevantes de `tools/calendar_tool.py` siguen pasando.

## 17. Requisitos de QA verificables sin UI

Tests unitarios de validación JSON/transiciones; SQL/migration para constraints/dedupe; direct handlers para create/list/complete/snooze/reschedule/cancel/timeline; regression CRM/calendar; smoke con datos sintéticos en Agent Core Postgres si disponible; DB readback con activity/links/reminder/audit/timeline; negative tests de input inválido, duplicate prevention, calendar no configurado y ambigüedad.

## 18. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Duplicación con `crm.follow_ups` | Bridge/idempotency key y tests F8 |
| Calendar side effects incorrectos | Confirmaciones, audit events, idempotency F6/F10 |
| PII/notas privadas expuestas | Security review, scoped toolsets, minimal result fields |
| Fecha natural ambigua | Parser con confidence + confirmación cuando cambia outcome |
| Sobrediseño UI | No-goal explícito; verificación por tools/tests/DB |
| Copia indebida open-source | Usar patrones, no código/esquemas; revisión legal/security |
| Dispatcher no determinístico | Job con scan windows/idempotency/readbacks |

## 19. Definición de done funcional F1

F1 queda funcionalmente completo cuando este PRD cubre CRM personal, CRM comercial, reminders, calendar scheduling, timelines, follow-up chains, quick capture y next-actions; declara UX agentic/no dashboard complejo; incluye reglas de no duplicación, side effects y confirmación; incluye contratos conceptuales de tools y respuestas esperadas; define criterios verificables para implementación/QA/security; y queda guardado bajo `factory/projects/agent-core-followup-reminders/` con evidencia de verificación.

## 20. Trazabilidad contra acceptance criteria F1

| Criterio F1 | Evidencia en este PRD |
|---|---|
| Personal CRM | Personas 6.1/6.3, objetivos 31/36, casos UC-01/UC-08, links persona/proyecto/documento en sección 8 |
| Business CRM | Contexto CRM secciones 3/10.1/15, UC-02, UC-03, timeline y compatibilidad `crm_*` |
| Reminders | UC-01, UC-09, dispatcher determinístico sección 14, criterios D en `ACCEPTANCE_CRITERIA.md` |
| Calendar scheduling | UC-05, reglas 10.2, contrato 11.6, compatibilidad Calendar sección 16 |
| Timelines | UC-07, contrato 11.4, consultas requeridas sección 13 |
| Follow-up chains | UC-04, UC-10, reglas de plans/chaining sección 11.7 |
| Quick capture | UC-06, natural-language UX sección 12, detección 11.5 |
| Next-actions | Objetivos 31/37, UC-04, contratos 11.3/11.7 |
| Agentic UX / no dashboard complejo | Tesis sección 2 y no objetivos 41-49 |
| Criterios verificables para implementadores y QA | Secciones 11, 14, 17, 18, 19 y `ACCEPTANCE_CRITERIA.md` |

## 21. Handoff funcional a F2/F3

- F2 debe decidir placement físico (`activity` schema recomendado vs `crm.activities`) y materializar constraints, indexes, idempotency y audit model sin reducir el alcance funcional aquí definido.
- F3 debe descomponer tareas para migrations, tools, dispatcher, plans, CRM bridge, QA y security usando los contratos de secciones 10-17.
- Ningún builder debe implementar una UI/filtros complejos como requisito de este Core.
- Cualquier side effect externo — calendar invite, notificación, mensaje a tercero — debe quedar auditado y protegido por reglas de confirmación/security.

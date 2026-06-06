# FUNCTIONAL_SPEC — Agent Core Follow-up / Reminders

## Estado

- Incremento: F1 — Functional PRD
- Run: `run-1780701420-04edba37`
- Fecha: `2026-06-05T23:17:44Z`
- Autor: `product-analyst`
- Revisor esperado: `solution-architect`
- Fuente de verdad: Agent Core Postgres `factory.*`

## Alcance funcional cerrado

La capacidad permite que Zeus capture, consulte, relacione, reprograme, complete, cancele, detecte y encadene actividades/follow-ups/reminders usando tools y jobs. La operación normal es chat/agent-first, no UI-first.

## Capacidades obligatorias

1. Crear/upsert activity universal con links a múltiples entidades.
2. Listar due/today/upcoming/overdue/waiting/snoozed/resurfaced.
3. Completar, cancelar, snoozear y reagendar con audit.
4. Crear y aplicar activity plans con steps relativos.
5. Encadenar next-actions al completar activities.
6. Detectar candidatos desde texto/email/chat con evidence spans y confidence.
7. Integrar CRM Core sin romper `crm_*` tools ni `crm.follow_ups`.
8. Integrar Calendar Core sólo para tiempo bloqueado/scheduling.
9. Generar timeline agentico por persona/organización/oportunidad/proyecto.
10. Ejecutar dispatcher determinístico para reminders, due/upcoming y recurrence.
11. Evitar duplicados por reglas de idempotencia.
12. Respetar privacidad, PII y tool boundaries.

## Flujos funcionales

### Crear reminder/follow-up

Input: lenguaje natural o tool JSON con tipo, título, fecha/contexto y links.
Output: `activity_id`, operación (`created|updated|linked_existing`), fecha interpretada, links y audit metadata.

### Consultar pendientes

Input: query natural o filtros JSON.
Output: lista accionable con IDs, vencimiento, prioridad, contexto, último evento y next action sugerida.

### Completar y encadenar

Input: activity identificada + completion note opcional + regla de siguiente paso.
Output: state change auditado y nuevo/sugerido next activity si aplica.

### Calendar bridge

Input: activity con horario real, tipo meeting/call o solicitud explícita de agenda.
Output: activity linked a calendar event; si adapter falla, activity permanece con audit/error.

### Detectar desde texto

Input: texto + modo `suggest_only` o `create_authorized`.
Output: candidatos con confidence/evidence; side effects sólo si el modo lo autoriza.

## Matriz de acciones y confirmación

| Acción | Default | Confirmación requerida cuando |
|---|---|---|
| Crear reminder privado | Ejecutar | Fecha/persona ambigua materialmente |
| Crear follow-up CRM | Ejecutar con dedupe | Múltiples entidades plausibles cambian el link |
| Guardar detecciones | Ejecutar si usuario dijo guardar | Confidence baja o entidad/fecha crítica ambigua |
| Crear evento calendario | No ejecutar por defecto para reminders | Siempre que involucre terceros o invite/schedule real |
| Enviar notificación externa | No enviar por defecto | Siempre antes de primer envío o canal no aprobado |
| Completar/cancelar activity | Ejecutar si ID/contexto claro | Activity no identificada o impacto cross-tenant |
| Exponer nota privada | No exponer a terceros | Siempre si sale del owner/tool boundary |

## Reglas de deduplicación funcional

- Comparar owner, primary link, tipo, título normalizado, due window, source y source_ref.
- Si hay match abierto: actualizar/linkear existente.
- Si hay match done/cancelled y usuario pide nuevo ciclo: crear nuevo con relación al anterior.
- Detección desde misma interacción/email debe ser idempotente por source_ref + span/hash.
- Bridge con `crm.follow_ups` debe evitar doble creación.

## Salidas requeridas para implementadores

F2 debe convertir este contrato en ADR/data model. F3 debe crear tasks con commands de verificación. F4-F8 deben implementar sólo después de functional/architecture/planning gates.

## Verificación F1

La verificación documental de F1 consiste en revisar que `PRD.md`, `FUNCTIONAL_SPEC.md` y `ACCEPTANCE_CRITERIA.md` contienen las capacidades, flujos y criterios arriba, y que `hermes factory status ... --json` muestra el task F1 claimed/running en Agent Core Postgres.

## Boundaries para los siguientes incrementos

- F1 no autoriza migraciones ni runtime code; esos cambios pertenecen a F4-F8 después de gates functional/architecture/planning.
- F2 no puede reemplazar CRM Core ni Calendar Core; debe ampliar o bridgear compatiblemente.
- F3 debe preservar reviewer independiente por tarea y no asignar self-approval.
- F5-F8 deben retornar JSON verificable con IDs/readbacks y tests; no basta con prompts o memoria conversacional.
- F9 debe probar sin UI: handler calls, DB readbacks, regression CRM/calendar, negative cases y smoke con datos sintéticos.

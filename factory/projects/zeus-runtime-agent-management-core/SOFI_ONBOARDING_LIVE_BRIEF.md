---
project_id: zeus-runtime-agent-management-core
project_name: Zeus Runtime Agent Management Core
document_type: initialization_brief
feature_key: sofi_onboarding_live
status: draft-ready_activation-hold
validated: yes
reviewed: no
created_at: 2026-06-17T02:46:24-04:00
activation_policy: "Do not initialize, resume, dispatch, branch, worktree, deploy, or start autonomous Factory execution until Jean explicitly confirms the current operation is finished and authorizes activation."
---

# Brief de Inicialización — Sofi Onboarding Live

## 0. Estado operativo del Factory

**Modo actual:** brief detallado preparado en Factory, **sin inicializar ejecución**.

Este documento deja listo el alcance para activar más adelante, pero no habilita corrida autónoma ni implementación. La activación requiere una orden explícita de Jean, por ejemplo: “ya terminó la operación actual, activa Sofi Onboarding en Factory”.

Guardrails de no-ejecución mientras esté en hold:

- No crear worktree de implementación.
- No abrir rama de feature.
- No crear PR.
- No despachar workers.
- No ejecutar `hermes factory project resume`.
- No tocar infraestructura, Vapi/Bapi, SMS, calendarios reales ni despliegues.
- Mantener el proyecto en estado `planned`/`paused` o equivalente no-autónomo.
- Usar este documento como brief de arranque cuando Jean confirme.

## 1. Resumen ejecutivo

Se requiere crear **Sofi Onboarding**, una variante especializada del agente de voz de SitioUno, cuya función es guiar a nuevos clientes después de contratar el servicio para levantar la información funcional necesaria para construir su agente personalizado.

La experiencia clave no es solo una llamada telefónica: mientras el cliente habla con Sofi, debe abrir un enlace seguro enviado por SMS y ver una interfaz web donde su onboarding se va completando en vivo. El resultado final no es el agente ya desplegado, sino un **briefing estructurado, auditable y accionable** para que Zeus/Factory configure, pruebe y entregue el agente del cliente posteriormente.

## 2. Posicionamiento del producto

**Concepto:** un agente que ayuda a crear otros agentes.

Sofi Onboarding no es el agente final del cliente. Es una especialista de implementación que:

1. Contacta al cliente.
2. Confirma disponibilidad.
3. Envía un enlace seguro.
4. Agenda si hace falta.
5. Conduce una sesión guiada por voz.
6. Completa una plantilla visual en vivo.
7. Genera un briefing interno estructurado.
8. Recontacta al cliente cuando el agente esté listo para activación.

La experiencia debe comunicar: “Estoy hablando con una asistente inteligente que entiende mi negocio y está configurando mi agente en vivo”.

## 3. G0 — Estrategia de repositorio y alcance Factory

Clasificación propuesta:

- `repo_scope`: `zeus_then_runtime`
- `work_intent`: `add_functionality`
- `primary_repo`: `SiteOneTech/hermes-agent-original`
- `propagation_repo`: `SiteOneTech/sitiouno-agent-runtime`
- `base_branch`: `main`
- `branch_prefix`: `factory/zeus-runtime-agent-management-core/sofi-onboarding-live/`
- `worktree_policy`: `per_deliverable`
- `standalone_repo_required`: `false`
- `propagation_required`: `true`, cuando la capacidad deje de ser solo Zeus/sandbox y deba vivir en agentes comerciales derivados.

Razonamiento: esta capacidad es parte del **Zeus Runtime Agent Management Core**. Primero se valida en Zeus porque requiere orquestación, Factory, supervisión, voz/SMS/calendario y seguridad. Luego se propaga al runtime comercial solo con las superficies seguras necesarias.

## 4. Alcance funcional incluido

### 4.1 Contacto inicial

- Crear registro de onboarding cuando un cliente compra/contrata.
- Estado inicial: `pending_contact` / “Pendiente de contacto”.
- Guardar datos mínimos: cliente, teléfono, email si existe, empresa/proyecto, plan, fecha de contratación, fuente comercial.
- Sofi llama al cliente usando la infraestructura existente de voz vía Vapi/Bapi (confirmar nombre canónico del adapter actual antes de implementar).
- Sofi confirma identidad y disponibilidad.
- Si el cliente puede continuar, inicia sesión guiada.
- Si no puede, agenda una cita.

### 4.2 Agendamiento

- Consultar disponibilidad desde Agenda Core/Nettu o el scheduling adapter canónico disponible.
- Proponer horarios concretos.
- Confirmar fecha/hora/zona horaria.
- Registrar cita.
- Enviar confirmación por SMS y/o email.
- Estado: `appointment_scheduled`.
- Programar recordatorio previo.
- Programar llamada automática en la fecha/hora acordada.

### 4.3 Link seguro por SMS

- Sofi confirma el número: “Voy a enviarte un enlace seguro al número terminado en XXXX”.
- Generar token único, de uso limitado y con expiración.
- Enviar SMS con link responsive.
- Asociar link a onboarding/session/customer.
- Detectar apertura del link.
- Permitir que Sofi sepa si el cliente abrió la interfaz.
- Reenviar link si expira o el cliente no lo recibe.

### 4.4 Interfaz web live onboarding

La UI debe ser una experiencia visual de configuración guiada, no una pantalla estática.

Debe mostrar:

- Bienvenida y nombre de Sofi Onboarding.
- Estado de llamada/sesión.
- Nombre del cliente.
- Nombre provisional del agente.
- Progreso por secciones.
- Campos completados, pendientes y dudosos.
- Actualizaciones visibles en tiempo real.
- Resumen parcial.
- Confirmaciones importantes.
- Estado final y próximos pasos.
- Preparación futura para que el cliente confirme/corrija datos.

Secciones visuales mínimas:

1. Datos básicos del cliente.
2. Nombre del agente.
3. Negocio o actividad principal.
4. Objetivo del agente.
5. Público objetivo.
6. Canales de atención.
7. Tono y personalidad.
8. Servicios/productos.
9. Preguntas frecuentes.
10. Reglas de comportamiento.
11. Escalamiento humano.
12. Horarios y disponibilidad.
13. Datos/materiales para activación.
14. Resumen final.

### 4.5 Captura estructurada

Sofi debe levantar información funcional, no técnica avanzada:

- Datos básicos: cliente, empresa, cargo, teléfono, email, país/ciudad, idioma, zona horaria.
- Identidad del agente: nombre deseado, idioma, tono, personalidad, frases a usar/evitar.
- Actividad: qué hace, qué vende, clientes, productos, diferenciales, ubicaciones, web/redes.
- Objetivo principal: atención, ventas, leads, citas, soporte, postventa, solicitudes, cobranza, otro.
- Flujo esperado: qué pedir, cuándo vender, cuándo agendar, cuándo escalar, qué no inventar.
- Información comercial: productos, precios, promos, condiciones, pagos, FAQ, objeciones.
- Escalamiento: cuándo, a quién, canal, horario humano, urgencias, aprobaciones.
- Canales: WhatsApp, Telegram, web chat, SMS, voz, otros.
- Reglas/límites: autonomía, temas prohibidos, datos sensibles, confidencialidad, spam/insultos.
- Materiales: web, brochure, catálogo, PDF, FAQ, manuales, guiones, documentos, videos, links.

### 4.6 Resultado final

Generar un briefing estructurado con:

- Datos del cliente.
- Resumen de necesidades.
- Perfil funcional del agente.
- Objetivos y prioridades.
- Canales requeridos.
- Reglas de comportamiento.
- FAQ y objeciones.
- Materiales disponibles/pendientes.
- Riesgos o puntos para revisión humana.
- Nivel de claridad del onboarding.
- Próximos pasos internos.
- Estado: `completed_pending_internal_configuration`.

Mensaje de cierre recomendado:

> “Con esta información vamos a preparar tu agente. Nuestro equipo revisará la configuración y me comunicaré contigo nuevamente cuando esté listo para ayudarte a activarlo.”

### 4.7 Segunda llamada de activación

Cuando el equipo interno marque el agente como listo:

- Sofi llama al cliente.
- Informa que el agente está listo.
- Envía link seguro si hace falta.
- Guía activación.
- Muestra QR o instrucciones para vincular WhatsApp/Telegram cuando aplique.
- Confirma conexión.
- Registra problemas.
- Estado final: `activation_completed` o `activation_issue_detected`.

## 5. No incluido en esta fase

- Creación automática del agente final sin revisión humana.
- Despliegue automático completo de VM/agente final.
- Configuración técnica avanzada hecha directamente por el cliente.
- Recolección de secretos/API keys por voz, SMS o web pública.
- Prometer que el agente queda listo al terminar la llamada.
- Dar a Sofi permisos de Zeus, terminal, filesystem, cron, deploy, Infisical o herramientas administrativas amplias.

## 6. Estados canónicos propuestos

| Estado | Uso |
|---|---|
| `pending_contact` | Cliente nuevo creado; falta primera llamada. |
| `contact_attempted` | Se intentó contacto sin completar onboarding. |
| `appointment_scheduled` | Cliente pidió cita. |
| `sms_link_sent` | Link seguro enviado. |
| `link_opened` | Cliente abrió la interfaz. |
| `onboarding_in_progress` | Llamada/sesión activa. |
| `onboarding_completed` | Sesión terminada y briefing generado. |
| `pending_internal_configuration` | Factory/equipo debe convertir briefing en configuración. |
| `internal_review` | Equipo revisando/ajustando datos. |
| `configuration_in_progress` | Construcción/configuración del agente. |
| `agent_ready_for_test` | Listo para QA interna. |
| `agent_ready_for_activation` | Listo para segunda llamada. |
| `activation_in_progress` | Cliente activando canales. |
| `activation_completed` | Onboarding finalizado. |
| `needs_more_information` | Falta información del cliente. |
| `cancelled` | Proceso cancelado. |

## 7. Modelo de datos inicial

Implementar sobre Agent Core DB, preferiblemente bajo `agent_management` para mantener continuidad con el módulo existente.

### 7.1 Entidades mínimas

- `agent_management.onboarding_sessions`
  - `session_id`
  - `customer_id` / `crm_contact_id`
  - `client_name`
  - `company_name`
  - `phone_e164`
  - `email`
  - `plan`
  - `status`
  - `form_data jsonb`
  - `summary jsonb`
  - `clarity_score`
  - `risk_flags jsonb`
  - `created_at`, `updated_at`, `completed_at`

- `agent_management.onboarding_secure_links`
  - `link_id`
  - `session_id`
  - `token_hash`
  - `expires_at`
  - `opened_at`
  - `revoked_at`
  - `last_seen_at`
  - `metadata jsonb`

- `agent_management.onboarding_events`
  - `event_id`
  - `session_id`
  - `actor_type` (`sofi`, `customer`, `system`, `internal`)
  - `event_type` (`field_updated`, `link_opened`, `call_started`, `sms_sent`, etc.)
  - `payload jsonb`
  - `created_at`

- `agent_management.onboarding_calls`
  - `call_id`
  - `session_id`
  - `provider_call_id`
  - `direction`
  - `status`
  - `duration_seconds`
  - `transcript_ref`
  - `summary`
  - `created_at`

- `agent_management.onboarding_messages`
  - `message_id`
  - `session_id`
  - `channel` (`sms`, `email`, `whatsapp`, etc.)
  - `provider_message_id`
  - `template_key`
  - `status`
  - `created_at`

- `agent_management.onboarding_appointments`
  - `appointment_id`
  - `session_id`
  - `scheduled_at`
  - `timezone`
  - `status`
  - `reminder_status`
  - `created_at`

- `agent_management.onboarding_materials`
  - `material_id`
  - `session_id`
  - `material_type`
  - `url_or_reference`
  - `status` (`provided`, `pending_upload`, `needs_review`)
  - `notes`

- `agent_management.activation_sessions`
  - `activation_id`
  - `session_id`
  - `managed_agent_id`
  - `status`
  - `channel_target`
  - `qr_ref` / `instructions_ref`
  - `connected_at`
  - `issue_notes`

### 7.2 Form data JSONB sugerido

```json
{
  "client": {
    "name": "",
    "company": "",
    "role": "",
    "phone": "",
    "email": "",
    "country_city": "",
    "timezone": "",
    "primary_language": ""
  },
  "agent_identity": {
    "desired_name": "",
    "primary_language": "",
    "secondary_languages": [],
    "tone": [],
    "personality": "",
    "phrases_to_use": [],
    "phrases_to_avoid": []
  },
  "business": {
    "activity": "",
    "offer": "",
    "customers": "",
    "products_services": [],
    "differentiators": [],
    "locations": [],
    "links": []
  },
  "agent_goals": {
    "primary_goal": "",
    "secondary_goals": [],
    "success_criteria": []
  },
  "conversation_rules": {
    "new_customer_flow": "",
    "required_data": [],
    "sales_behavior": "",
    "appointment_behavior": "",
    "unknown_answer_policy": "",
    "never_invent": [],
    "avoid_topics": []
  },
  "commercial_info": {
    "products": [],
    "pricing": "",
    "promotions": [],
    "sales_conditions": [],
    "payment_methods": [],
    "faqs": [],
    "objections": []
  },
  "human_escalation": {
    "when_to_escalate": [],
    "escalation_contact": "",
    "channels": [],
    "human_hours": "",
    "urgent_cases": [],
    "approval_required_cases": []
  },
  "channels": {
    "preferred": [],
    "phase_1": [],
    "future": []
  },
  "boundaries": {
    "allowed": [],
    "not_allowed": [],
    "sensitive_data_policy": "",
    "confidential_info": [],
    "abuse_policy": "",
    "autonomy_level": ""
  },
  "materials": {
    "provided_links": [],
    "pending_materials": [],
    "notes": ""
  },
  "internal_review": {
    "clarity_score": null,
    "risks": [],
    "missing_fields": [],
    "recommended_agent_type": "",
    "recommended_build_sequence": []
  }
}
```

## 8. Tools requeridas para Sofi Onboarding

Sofi debe usar herramientas de bajo privilegio, diseñadas para onboarding. No debe heredar toolsets amplios.

### 8.1 Call Tool

Capacidades:

- Realizar llamada al cliente.
- Leer estado/duración de llamada.
- Asociar llamada al onboarding.
- Guardar transcript/ref.

No debe:

- Cambiar infraestructura de voz.
- Configurar números/provider credentials.
- Llamar números no asociados al cliente sin autorización.

### 8.2 SMS Tool

Capacidades:

- Enviar enlace seguro.
- Enviar confirmación de cita.
- Enviar recordatorio.
- Reenviar link si corresponde.

No debe incluir datos sensibles en SMS.

### 8.3 Scheduling Tool

Capacidades:

- Consultar disponibilidad.
- Crear/reprogramar/cancelar cita.
- Registrar timezone y recordatorio.

Debe integrarse con Agenda Core/Nettu como fuente canónica local, salvo que luego se configure Google/externo.

### 8.4 Onboarding Session Tool

Capacidades:

- Crear/reabrir sesión.
- Generar link único.
- Verificar apertura.
- Cambiar estado.
- Leer próximos campos faltantes.

### 8.5 Realtime Form Update Tool

Capacidades:

- Actualizar campos visibles.
- Marcar `confirmed`, `pending`, `uncertain`.
- Emitir evento para UI.
- Calcular progreso.

### 8.6 Transcript/Summary Tool

Capacidades:

- Guardar transcript/ref.
- Generar resumen estructurado.
- Identificar pendientes/riesgos.
- Generar briefing interno.

### 8.7 CRM/Admin Tool

Capacidades:

- Crear/actualizar registro de cliente.
- Cambiar estado de onboarding.
- Crear tarea interna post-onboarding.
- Asignar responsable.

Debe ser un adapter limitado, no CRM completo para Sofi.

### 8.8 Activation Tool

Capacidades:

- Mostrar QR/instrucciones.
- Registrar canal conectado.
- Registrar problema de activación.
- Finalizar onboarding.

No debe desplegar el agente ni cambiar secretos.

## 9. Prompt de Sofi Onboarding — estructura BigTech

Aplicar `agent-prompt-architect` antes de crear el perfil ejecutable final.

### 9.1 Identidad y rol

Eres **Sofi Onboarding de SitioUno**, especialista de implementación. Tu misión es guiar a clientes nuevos durante el levantamiento funcional de su agente personalizado, por voz y con apoyo de una interfaz web en vivo.

### 9.2 Capacidades y entorno

Puedes llamar, enviar SMS autorizados, agendar citas, actualizar la sesión de onboarding, completar campos en tiempo real, resumir y preparar briefing interno. No puedes crear el agente final automáticamente, desplegar infraestructura, cambiar precios, pedir secretos ni prometer fechas no aprobadas.

### 9.3 Contrato de herramientas

- Usa Call Tool solo para llamadas del proceso de onboarding/activación.
- Usa SMS Tool para link, confirmaciones y recordatorios.
- Usa Scheduling Tool cuando el cliente no pueda continuar.
- Usa Onboarding Session Tool para estado, link y apertura.
- Usa Realtime Form Update Tool después de cada respuesta útil.
- Usa Summary Tool al cerrar la sesión o generar reporte parcial.
- Usa Activation Tool solo cuando el agente esté marcado internamente como listo.

### 9.4 Autonomía y persistencia

Avanza una pregunta a la vez. Si la respuesta es incompleta, guarda lo útil y pregunta por lo faltante. Escala a humano si hay decisión comercial, excepción de precio, riesgo legal, solicitud técnica avanzada, credenciales o promesa fuera del alcance.

### 9.5 Planificar vs actuar

Primero confirma identidad, disponibilidad y link abierto. Luego recorre secciones funcionales en orden adaptativo. No conviertas la llamada en formulario largo; mantén conversación natural.

### 9.6 Guardrails y seguridad

- No pedir contraseñas, API keys, tokens, cuentas bancarias o secretos.
- No prometer que el agente queda listo al terminar.
- No inventar información técnica.
- No recoger datos sensibles innecesarios.
- Confirmar datos críticos: nombre, teléfono, email, objetivo principal, canales, escalamiento.
- Marcar campos dudosos en lugar de asumir.

### 9.7 Tono y estilo

Español primero, cálido, profesional, breve, premium, claro. Debe sonar como una especialista humana eficiente, no como cuestionario técnico.

### 9.8 Formato de salida

Mensajes al cliente: una idea/pregunta por turno. Actualizaciones internas: JSON patches estructurados con campo, valor, confidence y estado.

### 9.9 Memoria y continuidad

Persistir solo datos de onboarding, transcripción/resumen y eventos necesarios. No guardar secretos ni ruido conversacional. El briefing final alimenta el equipo interno/Factory.

### 9.10 Verificación

Antes de cerrar, confirmar: objetivo principal, canales, escalamiento, materiales pendientes y expectativa correcta de que el equipo preparará el agente después.

## 10. Interfaz web propuesta

### 10.1 Superficie cliente

Ruta conceptual:

- `https://zeus-sandbox.kidu.app/onboarding/<token>` para Zeus sandbox.
- Futuro runtime: `https://<agent>-sandbox.kidu.app/onboarding/<token>` cuando se propague con aislamiento por agente.

Componentes:

- Hero de bienvenida: “Sofi está configurando tu agente”.
- Indicador de sesión: esperando llamada / llamada activa / completando / finalizado.
- Timeline de secciones.
- Cards de campos completados.
- Cards de campos pendientes.
- Panel “lo que Sofi entendió”.
- Panel “pendientes para después”.
- Estado de seguridad del link.
- Confirmación final y próximos pasos.

Realtime MVP recomendado:

- Preferir SSE o polling incremental sobre `onboarding_events` para un MVP estable.
- WebSocket solo si el runtime ya tiene infraestructura lista.
- UI debe degradar a refresh/polling si SSE falla.

### 10.2 Superficie interna/admin

Debe mostrar:

- Lista de onboardings.
- Estado.
- Cliente/empresa/plan.
- Última llamada/SMS/cita.
- Transcripción.
- Resumen.
- Campos estructurados.
- Pendientes y riesgos.
- Responsable interno.
- Historial de eventos.
- Acción: “marcar listo para configuración”.
- Acción: “marcar agente listo para activación”.

Esta vista puede vivir primero en dashboard/admin Zeus; no exponer panel privado en superficie pública sin OTP/sesión segura.

## 11. Seguridad, privacidad y aislamiento

Este flujo toca PII, voz, SMS, tokens y datos comerciales. Requiere Security Gate.

Controles mínimos:

- Token público solo guarda hash en DB.
- Expiración de link.
- Revocación/reemisión.
- Rate limit por IP/token.
- No mostrar teléfono/email completos si no es necesario.
- SMS sin datos sensibles.
- No pedir secretos por voz/web.
- Logs con redacción.
- Event log auditable.
- Diferenciar vista pública cliente de vista admin privada.
- Perfil Sofi con toolset mínimo, sin terminal/file/code/cron/delegation/Infisical/deploy.
- Confirmación humana antes de crear/desplegar agente final.

## 12. Fases de implementación propuestas

### Fase 0 — Activación Factory posterior

Objetivo: cuando Jean confirme, abrir corrida Factory sin perder contexto.

Entregables:

- Revalidar status Factory y confirmar que no hay otra operación activa.
- Crear worktree/branch por incremento.
- Congelar este brief como input.
- Actualizar tasks DB si se decide granularidad final.

### Fase 1 — MVP onboarding live

Entregables:

- DB schema de sesiones/eventos/links.
- Toolset mínimo de onboarding session + realtime update.
- SMS link seguro.
- UI cliente responsive con progreso en vivo.
- Flujo de llamada inicial enlazado a sesión.
- Resumen final estructurado.
- Vista interna básica.

### Fase 2 — Post-onboarding / activación

Entregables:

- Segunda llamada de activación.
- Pantalla de QR/instrucciones WhatsApp/Telegram.
- Estados avanzados.
- Tareas internas.
- Registro de activación/problemas.

### Fase 3 — Automatización avanzada

Entregables:

- Sugerencias automáticas de prompt/configuración.
- Detección de inconsistencias.
- Previsualización del agente.
- Generación de configuración base revisable.
- Mayor automatización de activación, sin saltar revisión humana.

## 13. Task graph recomendado al activar

```text
S00 Activation gate / brief handoff
  -> S01 Functional model + schema design
  -> S02 Secure link + SMS adapter
  -> S03 Customer live UI + realtime event feed
  -> S04 Sofi Onboarding prompt/profile + tool contracts
  -> S05 Voice session orchestration + link-open awareness
  -> S06 Structured capture + summary generation
  -> S07 Internal admin review view
  -> S08 Scheduling/reminders flow
  -> S09 Activation call + QR/instructions flow
  -> S10 E2E QA desktop/mobile/voice/SMS/sandbox
  -> S11 Security/privacy review
  -> S12 Delivery report + runtime propagation decision
```

Dependencias:

- S03 depende de S01/S02.
- S05 depende de S01/S02/S04.
- S06 depende de S01/S05.
- S07 depende de S01/S06.
- S09 depende de runtime managed-agent status existing flow.
- S10/S11 bloquean delivery.

## 14. Criterios de aceptación funcionales

1. Se puede crear un onboarding para cliente nuevo.
2. Sofi puede llamar usando infraestructura existente.
3. Sofi puede enviar SMS con enlace único.
4. Cliente abre link en desktop/móvil.
5. La interfaz muestra sesión activa.
6. Sofi actualiza campos en tiempo real.
7. Datos estructurados quedan guardados.
8. Se genera resumen final.
9. Estados cambian correctamente.
10. Equipo interno revisa la información.
11. Se marca listo para configuración.
12. Sofi realiza segunda llamada de activación.
13. Interfaz muestra QR/instrucciones.
14. Se registra activación o problema.
15. Historial completo queda trazado: llamadas, SMS, estados, transcripción, eventos.

## 15. QA requerido

- Unit tests de schema, token/link, estado, form merge, redacción.
- Integration tests de tools: create session, send link mock, update field, generate summary.
- Browser QA desktop y mobile.
- Realtime QA: evento emitido por tool aparece en UI.
- Security QA: link expirado/incorrecto/revocado no accede.
- Privacy QA: SMS y logs no exponen datos sensibles.
- Voice flow smoke: Sofi puede detectar link abierto y continuar.
- Admin flow smoke: revisar resumen y marcar listo para configuración.
- Activation smoke: instrucciones/QR mostrado y estado actualizado.

## 16. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Sofi promete entrega inmediata | Prompt guardrail + tests de conversación + copy de cierre fijo. |
| Link público expone PII | Token hash, expiración, minimización, rate limit, redacción. |
| UI live falla durante llamada | Fallback polling/refresh y Sofi puede continuar guardando datos. |
| Cliente da información incompleta | Campos `pending/uncertain`, resumen parcial, follow-up. |
| Toolset de Sofi hereda privilegios | Perfil aislado y resolved-toolset negative tests. |
| Voz/SMS provider cambia | Adapter abstracto, no acoplar a provider directo. |
| Se mezcla Factory con Kanban | Mantener Factory DB como source of truth; no Kanban bridge salvo orden explícita. |
| Se activa mientras otro proyecto corre | Hold explícito hasta confirmación de Jean. |

## 17. Preguntas abiertas para activación

Estas preguntas no bloquean el brief, pero deben resolverse al iniciar ejecución:

1. Confirmar nombre canónico del provider de llamadas en código: ¿Vapi, Bapi o adapter SitioUno Voice?
2. Confirmar provider SMS inicial y credenciales vía Infisical.
3. Confirmar si la UI cliente vive primero en `zeus-sandbox.kidu.app` o en una superficie nueva.
4. Confirmar si la primera activación real será WhatsApp, Telegram o ambos.
5. Confirmar si el cliente podrá corregir campos en MVP o solo visualizar/confirmar verbalmente.
6. Confirmar SLA/copy comercial de “cuándo estará listo el agente”.
7. Confirmar responsable interno por defecto cuando onboarding queda `pending_internal_configuration`.

## 18. Criterio de listo para activar Factory

Antes de activar:

- Jean confirma que la operación Factory actual terminó o puede pausarse.
- `hermes factory status` muestra que no hay corrida activa que viole “uno a la vez”.
- Zeus confirma que el proyecto sigue `autonomous_enabled=false` hasta ejecutar `resume` explícito.
- Se elige el primer incremento: recomendado `S01 Functional model + schema design`.
- Se crea branch/worktree de ese incremento, no antes.

## 19. Nota de compatibilidad con el workflow existente

El documento existente `ONBOARDING_WORKFLOW.md` describe el PMV conversacional inicial ya implementado para intake/report/actuation. Este brief amplía ese alcance hacia una experiencia **live visual + llamada + SMS + activación**. Donde haya conflicto, este brief no reescribe lo ya entregado; define el próximo alcance a ejecutar cuando Jean active la corrida Factory.

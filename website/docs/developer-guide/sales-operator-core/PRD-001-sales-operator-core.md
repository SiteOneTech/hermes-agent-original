# PRD-001 — Sales Operator Core

## Producto / módulo

**Sales Operator Core** es un módulo Agent Core genérico para convertir a Zeus/SitioUno en un vendedor operativo diario: investiga territorios asignados, descubre negocios, enriquece leads, diseña ataques comerciales personalizados, ejecuta cadencias multicanal con evidencia, aprende de resultados y alimenta CRM/Funnel Core hasta cerrar clientes.

Primer caso de uso: **Empleado.uno**. Debe quedar reusable para vender otros productos de SitioUno/IzyPagos/Flexipos/Qrovia sin reescribir el sistema.

## Problema

Jean necesita vender Empleado.uno con pocos recursos iniciales, equipo comercial mínimo y una meta agresiva. La web ya demuestra el producto, pero falta una máquina diaria que:

1. Elija zonas/verticales.
2. Encuentre comercios con alta probabilidad.
3. Investigue cada negocio quirúrgicamente.
4. Personalice mensaje, demo y canal.
5. Contacte con control, stop rules y evidencia.
6. Haga seguimiento hasta cierre o descarte.
7. Aprenda qué vertical/ciudad/hook/canal convierte.

## Objetivos

- Crear un sistema de venta autónoma-supervisada con CRM como fuente de verdad.
- Permitir campañas por producto, país, ciudad, vertical y canal.
- Integrar investigación web/local/social con lead scoring.
- Crear propuestas de contacto personalizadas por lead.
- Automatizar seguimiento y llamadas/mensajes cuando el canal esté configurado y autorizado.
- Medir CAC, conversión por etapa, objeciones, canal ganador y activación.
- Proteger reputación: no astroturfing, no spam, opt-out, rate limits, cumplimiento por canal.

## No objetivos v1

- No simular tráfico orgánico falso ni crear identidades/personas falsas en Reddit u otras redes.
- No hacer spam masivo ni scraping abusivo.
- No prometer ejecución outbound sin canal validado/credenciales/opt-out.
- No reemplazar CRM Core; Sales Operator Core se apoya en CRM/Funnel Core.
- No construir UI compleja. UX principal: agente/chat + reportes diarios.

## Usuarios

- Jean / Zeus: operador principal, define zonas, capital y prioridades.
- David / closer humano opcional: recibe leads calientes y objeciones.
- Sophie / voice persona: ejecuta llamadas o warm follow-ups dentro de límites.
- Agentes derivados futuros: podrán vender otros productos con toolset restringido.

## Primer producto: Empleado.uno

Oferta base:

- Empleado IA para pymes: responde, agenda, califica, cotiza/cobra y escala a humano.
- Canales: WhatsApp, webchat, email/tickets, voz web, llamadas Enterprise.
- Posicionamiento: empleado IA, no chatbot genérico.
- Planes actuales: Básico US$49.99/mes, Profesional US$80/mes, Enterprise a medida.
- CTA: entrevistar/probar el empleado IA en una demo vertical.

## Flujo v1

1. **Territory assignment**
   - Entrada: país, ciudad, vertical, objetivo semanal, presupuesto, canal permitido.
   - Ejemplo: Colombia > Medellín > clínicas estética > 100 leads.

2. **Lead discovery**
   - Fuentes: web search, mapas/directorios cuando estén disponibles, sitios, redes públicas, CSV manual, referidos.
   - Output: organización/contacto candidato con URLs/canales públicos.

3. **Lead enrichment**
   - Extrae: servicios, horarios, WhatsApp/email, Instagram/web, reviews/señales de dolor, idioma, posible decisor.
   - Guarda snapshot con fecha/fuente.

4. **Lead scoring**
   - Fit por vertical.
   - Urgencia de dolor.
   - Canal WhatsApp visible.
   - Capacidad de pago.
   - Señales de volumen.
   - Facilidad de demo.
   - Riesgo legal/reputacional.

5. **Personalized attack plan**
   - Mensaje por canal.
   - Demo/funnel URL recomendado.
   - Objeciones esperadas.
   - CTA de bajo riesgo.
   - Próxima acción.

6. **Outreach / follow-up**
   - Solo canales autorizados y públicos/comerciales.
   - Rate limits por canal/territorio.
   - Registro CRM de cada intento.
   - Stop rule inmediato por no interesado/stop/unsubscribe.

7. **Close / handoff**
   - Si pide precio: quote/proposal path.
   - Si pide demo: enviar/demo o agendar.
   - Si responde objeción técnica: escalar a Zeus/David según reglas.
   - Si paga: onboarding/activación 72h.

8. **Learning loop**
   - Resume resultados diarios.
   - Identifica winners/losers por ciudad/vertical/hook/canal.
   - Ajusta scoring y guiones.

## Entidades principales

- `sales.products` / product profile reusable.
- `sales_operator.campaigns`.
- `sales_operator.territories`.
- `sales_operator.lead_sources`.
- `sales_operator.prospect_research`.
- `sales_operator.lead_scores`.
- `sales_operator.attack_plans`.
- `sales_operator.outreach_sequences`.
- `sales_operator.outreach_attempts`.
- `sales_operator.channel_policies`.
- `sales_operator.experiments`.
- `sales_operator.daily_rollups`.

CRM Core stores durable organizations, contacts, opportunities, interactions, and follow-ups.

## Tools deseadas

- `sales_operator_status`
- `sales_operator_campaign_create`
- `sales_operator_territory_assign`
- `sales_operator_lead_discover`
- `sales_operator_lead_enrich`
- `sales_operator_lead_score`
- `sales_operator_attack_plan_create`
- `sales_operator_outreach_queue`
- `sales_operator_outreach_execute` gated by policy/channel
- `sales_operator_reply_audit`
- `sales_operator_daily_rollup`
- `sales_operator_learning_update`

## Cron loops v1

- Lead discovery batch: cada 2–4 horas cuando una campaña está activa.
- Enrichment/scoring: cada hora o bajo demanda.
- Follow-up executor: cada 15–30 min para leads con acciones vencidas.
- Reply auditor: cada 15–30 min para email/WhatsApp/SMS configurados.
- Daily brief: cada mañana con pipeline, prioridad del día y blockers.
- Daily close report: cada tarde con acciones, respuestas, demos, cierres, objeciones.

## Métricas

- Leads descubiertos / enriquecidos / aprobados.
- Contactabilidad: % con WhatsApp/email/teléfono público.
- Respuesta por canal.
- Lead → diagnóstico.
- Diagnóstico → demo.
- Demo → pago.
- Pago → activación 72h.
- Refund/churn 30 días.
- CAC por canal/ciudad/vertical.
- Objeciones top.
- Tiempo a primer contacto.
- Leads calientes pendientes de humano.

## Criterios de aceptación v1

- Migrations crean schema/tables/roles sin romper CRM Core.
- Tools registradas en toolset `sales_operator`.
- Puede crear campaña Empleado.uno con territorio y política de canal.
- Puede importar/enriquecer al menos 10 leads de prueba con snapshots y scoring.
- Puede crear attack plans personalizados sin ejecutar spam.
- Puede registrar una interacción/follow-up en CRM Core desde un lead aprobado.
- Outbound execution queda fail-closed hasta que canal/política esté validado.
- Daily rollup devuelve pipeline y próximos pasos.
- Tests unitarios y smoke live contra Agent Core DB pasan.

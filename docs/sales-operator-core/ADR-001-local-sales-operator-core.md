# ADR-001 — Sales Operator Core local sobre Agent Core DB

## Estado

Propuesto para Factory build.

## Contexto

Empleado.uno necesita una máquina comercial diaria con pocos recursos y fuerte automatización. El sistema debe servir también para futuros productos. SitioUno ya tiene CRM/Funnel Core, voice adapters, notification adapters y Factory. Jean prefiere arquitectura canónica, Postgres y módulos Agent Core invisibles al usuario.

## Decisión

Implementar **Sales Operator Core** como schema propio dentro del Agent Core Postgres local del agente, con herramientas Hermes y cron loops. No crear un SaaS/backoffice separado en v1.

- Schema: `sales_operator`.
- Fuente operacional: Agent Core Postgres.
- CRM duradero: CRM Core.
- Comunicación externa: adapters existentes (email/WhatsApp/Vapi/SMS) con evidencia.
- UI: chat/reportes; dashboard opcional posterior.
- Factory scope: `zeus_then_runtime` para que Zeus lo pruebe primero y luego el runtime heredado pueda vender productos.

## Razones

- El vendedor principal es el agente, no una UI humana.
- Permite operar por chat y crons.
- Evita duplicar CRM.
- Facilita auditoría, stop rules y aprendizaje.
- Reusable para cualquier producto con playbook/campaign profile.

## Alternativas rechazadas

1. **Airtable/Sheets como core**
   - Rápido pero débil para automatización, permisos, auditoría y joins con CRM.

2. **Instalar CRM externo como fuente principal**
   - Más fricción para Jean; contradice invisible CRM pattern. Puede ser adapter posterior.

3. **Automatización solo con crons y archivos JSON**
   - No escala ni audita bien. Riesgo de duplicados y pérdida de contexto.

4. **Outbound directo sin policy engine**
   - Riesgo reputacional/legal. Debe ser fail-closed y con rate limits.

## Guardrails éticos y legales

- Prohibido astroturfing: no fingir usuarios orgánicos ni testimonios falsos.
- No contactar canales no públicos/no comerciales.
- Registrar fuente de cada dato.
- Rate limits por canal y territorio.
- Opt-out global por contacto/organización.
- Mensajes deben identificarse como SitioUno/Empleado.uno cuando corresponde.
- WhatsApp business-initiated debe respetar reglas del canal/template/opt-in según adapter.
- Llamadas deben respetar jurisdicción, horario local, caller ID y no redial agresivo.

## Consecuencias

- v1 requiere diseñar policy gates antes de automatizar outreach.
- Algunos cierres seguirán necesitando Jean/David hasta que scripts y objeciones estén probados.
- La velocidad vendrá de automatizar investigación, personalización y follow-up, no de enviar spam masivo.

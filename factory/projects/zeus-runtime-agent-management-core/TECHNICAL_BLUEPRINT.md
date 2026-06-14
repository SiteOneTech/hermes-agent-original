---
project_id: zeus-runtime-agent-management-core
project_name: Zeus Runtime Agent Management Core
validated: yes
reviewed: yes
status: draft-ready
---

# Technical Blueprint

## Conceptual components

```text
Zeus Management Core
  ├─ Agent Registry
  ├─ Agent Class Pack Registry
  ├─ Secret Pack Manager
  ├─ Onboarding Orchestrator
  ├─ VM/Infra Deploy Orchestrator
  ├─ Build/Deploy Status Tracker
  ├─ Monitoring/Supervision
  ├─ Tickets from Runtime Agents
  └─ Dashboard/API Surface

Runtime Agent VM
  ├─ own Infisical project
  ├─ shared runtime pack access
  ├─ generated runtime-secrets.env
  ├─ Agent Core DB/modules
  ├─ gateway/channels
  └─ delivery sandbox/private dashboard
```

## Shared secret sync PMV
Inputs:
- `INFISICAL_API_URL`
- `INFISICAL_ENV`
- `AGENT_INFISICAL_PROJECT_ID`
- `SHARED_INFISICAL_PROJECT_ID`
- `AGENT_SECRET_PATHS`
- `SHARED_SECRET_PATHS`
- Universal Auth credentials for the agent identity

Output:
- `/home/hermes/.hermes/runtime-secrets.env`, mode `0600`

Merge:
1. Read shared pack paths.
2. Read agent paths.
3. Normalize keys.
4. Merge with agent override precedence.
5. Render dotenv without printing values.

## Key naming for notification PMV
Shared pack candidate keys:
- `SENDGRID_API_KEY`
- `SENDGRID_DEFAULT_FROM_EMAIL`
- `SENDGRID_DEFAULT_FROM_NAME`
- `SENDGRID_REPLY_TO`

Agent override keys:
- `SENDGRID_API_KEY` optional per-agent replacement
- `SENDGRID_FROM_EMAIL`
- `SENDGRID_FROM_NAME`
- `SENDGRID_REPLY_TO`

Generated mapping may set `SENDGRID_FROM_EMAIL=${SENDGRID_FROM_EMAIL:-SENDGRID_DEFAULT_FROM_EMAIL}` in script logic, not by leaking interpolation into final env unless the runtime loader supports it.

## Security controls
- No secret values in logs.
- No secret values in argv.
- `runtime-secrets.env` chmod `0600` owned by service user.
- Agent identity cannot read sibling agent projects.
- Shared pack contains only approved service-level keys.

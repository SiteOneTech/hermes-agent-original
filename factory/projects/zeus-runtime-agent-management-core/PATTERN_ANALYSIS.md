---
project_id: zeus-runtime-agent-management-core
project_name: Zeus Runtime Agent Management Core
validated: yes
reviewed: yes
status: draft-ready
---

# Pattern Analysis

## Existing SitioUno runtime pattern
Derived agents such as Bael use one GCP VM per agent/client, local Agent Core DB, public delivery sandbox, private dashboard, and secrets synced from an Infisical project into `/home/hermes/.hermes/runtime-secrets.env`.

## Existing Bael hardening lesson
Long-lived processes should not run under `infisical run --token=...`. The canonical pattern is:
1. Authenticate to Infisical without placing secrets in argv.
2. Export secrets into generated runtime env files with strict permissions.
3. Start services directly using systemd `EnvironmentFile=`.

## Infisical shared secrets options
- Native secret imports/references may work, but can be version/permission dependent.
- A runtime-side explicit merge is more portable and auditable for SitioUno agents.

## Chosen PMV pattern
Implement explicit shared-pack inheritance in the runtime sync layer:

```text
shared runtime pack secrets
  + agent project secrets
  + generated defaults
  => runtime-secrets.env
```

Precedence:

```text
agent-specific > shared pack > generated defaults
```

## Agent class pattern
Agent classes should be product-level capability packs, for example:
- `runtime-default`: agenda, CRM, notifications, sales documents.
- `cleaning-entrepreneur`: scheduling, quotes, recurring services, WhatsApp customer follow-up.
- `accountant`: accounting-lite, receipts, document intake, tax/payment reminders.

Class packs should select modules, prompts/SOUL overlays, toolsets, public dashboard modules, and required shared secrets.

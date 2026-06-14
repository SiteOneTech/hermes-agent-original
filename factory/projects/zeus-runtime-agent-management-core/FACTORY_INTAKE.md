---
project_id: zeus-runtime-agent-management-core
project_name: Zeus Runtime Agent Management Core
validated: yes
reviewed: yes
status: draft-ready
---

# Factory Intake — Zeus Runtime Agent Management Core

## Business objective
Build a Zeus-managed core for selling SitioUno runtime agents as a service. The core must turn agent creation and operation into a robust, automated, auditable process: onboarding, runtime class packs, VM deployment, build/deploy flow, monitoring, supervision, Zeus dashboard, ticket management, and shared operational secrets.

## User request summary
Jean asked to proceed implementing a shared Infisical runtime pack where each shared key supports per-agent override from the agent's own profile/project, and to create a Factory project for the broader Zeus core that manages runtime agents as a revenue-generating service.

## Initial PMV scope
1. Factory project and G1 documentary control pack.
2. Runtime shared secret pack MVP in `SiteOneTech/sitiouno-agent-runtime`.
3. Explicit precedence: agent-specific secret > shared runtime pack > generated default.
4. SendGrid as the first shared operational capability for all runtime agents.
5. Design hooks for future agent class packs and Zeus management core features.

## Out of scope for first PMV increment
- Full VM provisioning automation.
- Full Zeus dashboard UI.
- Full ticketing schema/toolset.
- SendGrid subuser provisioning per tenant.
- Production rotation workflow beyond documented policy.

## Source of truth
- Factory DB project: `zeus-runtime-agent-management-core`.
- Project docs: `factory/projects/zeus-runtime-agent-management-core/` in Zeus repo.
- Primary repo: `SiteOneTech/hermes-agent-original`.
- Runtime propagation repo: `SiteOneTech/sitiouno-agent-runtime`.

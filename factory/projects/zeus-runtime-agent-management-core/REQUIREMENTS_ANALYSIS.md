---
project_id: zeus-runtime-agent-management-core
project_name: Zeus Runtime Agent Management Core
validated: yes
reviewed: yes
status: draft-ready
---

# Requirements Analysis

## Functional requirements
- Zeus must manage runtime-agent lifecycle as a product core, not ad-hoc VM scripts.
- Runtime agents must support class/niche configurations: default runtime, cleaning businesses, accountants, and future vertical packs.
- Shared operational secrets must be centrally managed in Infisical and inherited by runtime agents.
- Each inherited shared key must be overrideable by the agent's own project/profile.
- SendGrid email sending must become a base runtime capability available to agents that inherit the runtime pack.
- Secret sync must avoid printing or storing secret values in logs, command arguments, repo files, or chat.
- Shared pack consumption must preserve per-agent isolation and allow revocation/audit per agent.

## Non-functional requirements
- Canonical implementation only; no copying Jean/Zeus keys into individual `.env` files as a workaround.
- Least privilege by default; only explicitly shared operational service keys enter the shared pack.
- Deterministic sync output (`runtime-secrets.env`) with mode `0600`.
- Testable merge behavior.
- Compatible with existing Bael hardening pattern: Infisical as source of truth, generated env, systemd services start from EnvironmentFile.

## Product requirements
- The core should become a revenue enabler: lower onboarding time, less manual setup, fewer broken demos, operational visibility, and repeatable niche agents.
- PMV must be functional and extensible; later increments add deploy infra VM, build, monitor, supervision, dashboard, and tickets.

## Acceptance for first implementation increment
- Runtime repo includes shared pack docs/template and merge/sync code.
- Tests prove override precedence.
- SendGrid keys are documented as shared-pack candidates with per-agent `FROM` override support.

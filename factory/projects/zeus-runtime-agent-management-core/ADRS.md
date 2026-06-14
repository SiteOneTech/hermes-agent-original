---
project_id: zeus-runtime-agent-management-core
project_name: Zeus Runtime Agent Management Core
validated: yes
reviewed: yes
status: draft-ready
---

# Architecture Decision Records

## ADR-001 — One project per runtime agent plus shared runtime pack

Status: accepted

Decision: Keep each runtime agent's Infisical project. Add a shared runtime-pack project for service-level operational secrets. Each agent identity can read its own project and the shared pack, but not sibling projects.

Rationale: Preserves tenant isolation while avoiding duplicated base service configuration.

## ADR-002 — Explicit merge in runtime sync layer

Status: accepted for PMV

Decision: Implement explicit merge in runtime sync instead of depending solely on Infisical native imports.

Rationale: More portable across self-hosted versions, easier to test, and lets Zeus define product-level precedence rules.

## ADR-003 — Override precedence

Status: accepted

Decision:

```text
agent-specific secrets > shared runtime pack secrets > generated defaults
```

Rationale: Shared pack provides baseline capabilities; agents can customize sender identity, domain, class settings, or replace a provider key when needed.

## ADR-004 — Shared SendGrid key as PMV with restricted scope

Status: accepted for PMV, revisit after scale

Decision: Start with shared SendGrid API key in runtime pack, intended for `mail.send` only, with per-agent sender override metadata.

Rationale: Email is a basic runtime capability. Per-agent SendGrid subusers/API keys are better long term but increase PMV complexity.

## ADR-005 — Agent classes are capability manifests

Status: accepted

Decision: Runtime classes/niches should be represented as manifests selecting enabled cores, prompts/SOUL overlays, required secret packs, toolsets, and dashboard modules.

Rationale: Avoid custom one-off agents; make verticals reusable and sellable.

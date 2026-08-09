# ADR-001 — Local Zeus Alpha Research Core with adapter-only Vonash collaboration

**Status:** Accepted for planning; implementation pending

## Context

Vonash is undergoing an independent, active refactor. Its Research subsystem must be repaired on its own path. Jean wants an independent perspective to reduce single-generator bias, while preserving comparison and collaboration with Magnus.

## Decision

Build a **Zeus-only Agent Core PostgreSQL module** in the existing shared `zeus_agent` database under schema `market_research`. It will not write to the Vonash database or call Vonash runtime mutation endpoints.

Collaboration with Magnus is an optional adapter that exchanges bounded research messages. The adapter is disabled until a documented, least-privilege interface exists.

## Core entities

- `programs`: research line and policy (`zeus-independent-alpha`), including an explicit `research_only=true` boundary.
- `source_registry`: registered research inputs, license/trust metadata, availability, and attribution.
- `research_cycles`: daily/manual intake, synthesis, red-team, and retrospective output.
- `evidence_events`: timestamped, source-attributed claims/observations; corrections supersede rather than erase evidence.
- `hypotheses`: Alpha Card ledger with typed family/status/data readiness plus mechanism, data contract, execution assumptions, no-trade rules, risk envelope, and falsification plan.
- `hypothesis_evidence`: many-to-many evidence links with a claim role and rationale.
- `reviews`: skeptical, red-team, or methodology review with structured decisions and limitations.
- `handoffs`: inert, auditable future Magnus handoffs, fixed to `authority_scope=research_only`; v1 never dispatches a message or calls Vonash.

The future collaboration adapter may add session/message tables, but it is a later increment. The v1 ledger is deliberately able to persist an evidence-backed, non-executing handoff before any connector exists.

## Security and control boundaries

1. `market_research_runtime` may only access `market_research.*` plus read-only module-registry/migration-ledger metadata. It receives a dedicated credential; it must not silently fall back to a broader Agent Core role.
2. No broker, execution, risk-management, trader, paper/live, or raw Vonash mutation tool belongs to this module.
3. Read-only connectors use a scoped service credential stored in Infisical and may fetch only allowlisted KB collections/Slack channels.
4. Every external item records source and retrieval metadata; no secret, private Slack export, or raw customer data is duplicated into research cards.
5. The adapter must fail closed: absent connector credentials means no outbound/inbound collaboration attempt.

## Alternatives rejected

- **Write directly into Vonash research tables:** couples this project to the refactor and contaminates attribution.
- **Use a local SQLite notebook:** conflicts with the canonical Postgres requirement and lacks durable access control/audit.
- **Give Zeus control of Vonash promotion:** violates separation of duties and adds financial-operational risk.
- **Ingest all Slack/KB permanently:** noisy, stale, sensitive, and impossible to attribute correctly.

## Consequences

The first integration deliverable is an export/handoff contract, not a Vonash deployment. Magnus can consume a bounded brief and return a capability/result reference, while both systems remain independently observable.

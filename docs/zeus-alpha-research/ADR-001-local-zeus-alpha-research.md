# ADR-001 — Local Zeus Alpha Research Core with adapter-only Vonash collaboration

**Status:** Accepted for planning; implementation pending

## Context

Vonash is undergoing an independent, active refactor. Its Research subsystem must be repaired on its own path. Jean wants an independent perspective to reduce single-generator bias, while preserving comparison and collaboration with Magnus.

## Decision

Build a **Zeus-only Agent Core PostgreSQL module** in the existing shared `zeus_agent` database under schema `market_research`. It will not write to the Vonash database or call Vonash runtime mutation endpoints.

Collaboration with Magnus is an optional adapter that exchanges bounded research messages. The adapter is disabled until a documented, least-privilege interface exists.

## Core entities

- `programs`: research line and policy (`zeus-independent-alpha`).
- `sources`: registered research inputs and license/trust metadata.
- `evidence_items`: immutable retrieved claims/observations.
- `alpha_cards`: research hypotheses with state `draft → reviewed → exported | rejected | archived`.
- `alpha_lineage`: parent/variant/family relationships.
- `research_cycles`: daily intake, synthesis, red-team, and retrospective output.
- `reviews`: skeptical review with structured rejection/limitations.
- `collaboration_sessions`: finite Zeus ↔ Magnus dialogue window.
- `collaboration_messages`: typed messages and acknowledgements.
- `experiment_result_refs`: non-authoritative references/snapshots received from Vonash; never the experiment executor.

## Security and control boundaries

1. `market_research_runtime` may only access `market_research.*`.
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

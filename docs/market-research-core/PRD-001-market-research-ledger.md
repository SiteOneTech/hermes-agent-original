# PRD-001 — Market Research Ledger

**Status:** Current concise reference. Full, controlling requirements: [`factory/projects/zeus-independent-alpha-research/PRD.md`](../../factory/projects/zeus-independent-alpha-research/PRD.md).

## Purpose
Provide an independent, provenance-rich Zeus research line that creates falsifiable Alpha Cards and collaborates with Magnus without becoming a trader, executor, or competing Vonash control plane.

## Product contract
- Zeus owns advisory evidence, cards, lineage, reviews, cycles and capability requirements in its own Postgres module.
- Vonash owns Magnus/runtime research threads, experiment references and its simulation/paper/live governance.
- Collaboration uses a typed API/thread, durable outbox, acknowledgement and immutable external references. No direct cross-database writes.
- The allowlisted intents are research/capability/result/alert messages only; the nine named types are listed in the canonical `REQUIREMENTS_ANALYSIS.md`. They cannot control broker, risk, paper/live, promotion, code, configuration, credentials or deployment.
- A Telegram group may mirror a typed thread for Jean, Zeus and Magnus; it cannot become the canonical protocol.

## Core outcomes
A card/session is `research_ready`, `research_ready_with_conditions`, `blocked_by_data`, `blocked_by_method`, `duplicate_or_lineage_merge`, `deferred` or `rejected`. `research_ready` does not authorize evaluation, paper, live or promotion.

## Data integrity
Every market claim records source, timestamp, license/terms, confidence, mechanism, regime, required granularity and falsification plan. Bars are not called footprint/order flow without documented granular trade/quote evidence.

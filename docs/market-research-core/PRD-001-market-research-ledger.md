# PRD-001 — Market Research Ledger

**Status:** Planning / no runtime coupling

## 1. Purpose

Create a Zeus-owned, evidence-backed second source of trading hypotheses. Zeus is an independent strategy-research advisor: it must complement—not replace, repair, control, or operate—the existing Vonash Research/Magnus path.

Zeus will research market mechanisms, maintain provenance-rich Alpha Cards, receive research ideas from Jean, and conduct bounded retrospectives with Magnus. Each idea remains distinguishable by origin so Jean can compare source families by actual out-of-sample and paper results.

## 2. Desired outcome

A daily research line that produces falsifiable, non-duplicative hypotheses, tactical/event observations, and research-only briefs for Magnus. Magnus remains the authority on platform capability, simulation implementation, evaluators, and all Vonash promotion gates. When a required capability does not exist, Zeus records a requirement for Jean/backend planning rather than modifying Vonash.

## 3. In scope

- Local Zeus Agent Core PostgreSQL module named `market_research`.
- Source registry, evidence claims, Alpha Cards, lineages, review records, daily research cycles, inert handoffs, and capability requests.
- Explicit hypothesis provenance: `zeus_external`, `vonash_research`, `magnus_reflection`, `jean_manual`, or `external_practitioner`.
- A bounded Zeus ↔ Magnus research session protocol.
- Read-only adapters for a supplied theoretical KB/book library, Vonash repository, data/strategy API, or future Magnus transport, after an allowlisted integration is approved and implemented.
- Comparison metrics by source family after Vonash provides experiment result references.

## 4. Explicit non-goals

- Do not modify Vonash Cloud Run services, its current refactor, its database, its scheduler, or its Research Factory.
- Do not edit the read-only Vonash repository, implement missing evaluators, or deploy a capability request.
- Do not promote a strategy to paper/live; do not alter risk, broker, trader, or execution configuration.
- Do not claim a social-media/manual strategy is validated without reproducible rules and source evidence.
- Do not create an unbounded agent-to-agent chat or copy all of Magnus's KB into Zeus memory.
- Do not blindly mirror opaque or non-authorized third-party signals; retain source terms, provenance, and an independent data/test contract.

## 5. Functional requirements

### FR-1 — Alpha Cards

An Alpha Card must contain: market/universe, mechanism, regime/context, observable features, entry/exit hypothesis, invalidation, expected holding horizon, execution/cost assumptions, data requirements, risks, evidence links, novelty fingerprint, and owner/source attribution.

### FR-2 — Evidence quality

Every claim has a source URL/reference, retrieval timestamp, source class, direct quote/summary, confidence, and falsification test. Practitioner/social sources are ideation-only until upgraded by data or independent research.

### FR-3 — Lineage and novelty

Every hypothesis records parent cards and a mechanism/family fingerprint. A candidate that is materially the same mechanism as an existing ORB/VWAP/mean-reversion card must be marked as a variant, not novel.

### FR-4 — Bounded daily collaboration

A session is a finite object. Default: four substantive agent turns (two Zeus and two Magnus), 45 minutes elapsed time, and a mandatory written synthesis. It closes automatically on either limit. System-generated open/close events do not consume a turn.

### FR-5 — Results comparison

When Magnus/Vonash supplies a non-sensitive experiment reference, Zeus stores a result snapshot and can compare source families only on matched gate outcomes, not anecdotal P&L.

### FR-6 — Capability-gap requirements

When a card requires data, a pattern evaluator, or a platform behavior Magnus cannot provide, Zeus creates a linked `capability_request` with the blocker, minimum specification, alternatives, expected research value, evidence, priority, and acceptance criteria. It is owned by Jean/backend planning and has no code/deployment side effect.

## 6. Acceptance criteria for v1

1. `market_research` migrations apply cleanly on the Zeus Agent Core database.
2. Zeus tools can create/read evidence-backed Alpha Cards and capability requests, but cannot execute/promote trades or modify a Vonash repository/runtime.
3. A daily cycle can be created, closed, and retrospectively queried.
4. An inert research-only handoff and a capability request can be recorded without any Magnus connector.
5. Any future KB/repository/data/transport connector is read-only, allowlisted, provenance-aware, and absent/disabled by default.
6. Tests cover provenance, invalid state transitions, duplicate-family detection, capability-request boundaries, session limits, and forbidden execution surface.

## 7. Success metrics

- % of cards containing all required fields.
- % with at least one independent source/evidence item.
- Novelty distribution by mechanism family.
- Rejection reason distribution: data gap, leakage, cost, regime fragility, duplication, or no edge.
- Walk-forward/paper outcomes grouped by hypothesis source.

## 8. Product boundary

Zeus is a research peer and research archivist. Magnus is a platform-capability peer. Jean coordinates priorities and capability delivery. Vonash remains the only system that may simulate, evaluate, or promote trading strategies.

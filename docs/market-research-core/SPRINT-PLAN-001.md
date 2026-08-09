# Sprint Plan 001 — Zeus Independent Alpha Research

## Gate 0 — Repository strategy

- **Project:** `zeus-independent-alpha-research`
- **Repository:** `SiteOneTech/hermes-agent-original`
- **Scope:** `zeus_only`
- **Branch policy:** one isolated worktree per increment; no propagation to runtime.
- **Autonomy:** 0 / supervised. No deploy or external credential change without an explicit later decision.

## Increments

### I0 — Planning, boundary and task graph

Deliver PRD, ADR, task graph, QA/security gates, documentation index, Factory registration, and an initial non-mutating interface contract. No Vonash change.

### I1 — Local persistence foundation

Add `db/agent-core/000004_market_research_runtime_role.sql`, `db/modules/market_research/000001_market_research_schema.sql`, the dedicated runtime credential wiring, schema ownership/grants, and migration registration. Add tests that prove no execution/trading schema is touched and that a broader runtime role is never silently reused.

### I2 — Evidence and Alpha Card tools

Implement source/evidence/card/lineage/review tools. Require provenance and a mechanism fingerprint. Add safe read/search/dashboard snapshot tools.

### I3 — Daily research cycle

Implement local daily cycle creation/closure and report tools. Add a scheduled Zeus job only after the tools and storage tests are green. The job produces research records; it cannot contact Vonash yet.

### I4 — Bounded Magnus collaboration adapter

Implement a provider interface with a disabled-by-default adapter. It supports a finite research session and authenticated read-only KB retrieval. The default session is four substantive turns (Zeus ×2, Magnus ×2) or 45 minutes, whichever closes first. No direct DB access and no execution command type.

### I5 — Results comparison

Implement imported result references and source-family scorecards. Require data version, gate definition, timeframe, cost model, and experiment reference to avoid comparing incomparable metrics.

### I6 — QA, security and first manual pilot

Run migration/tool/cron tests; perform a manual Alpha Card and a manually initiated bounded session. Record evidence. No market or execution activation.

## Daily session default

- **Research cycle:** 06:30 America/New_York.
- **Retrospective window:** manually initiated or scheduled after research, max 45 minutes.
- **Message cap:** 4 substantive agent turns total (two per agent).
- **Closure:** synthesis plus explicit `open_questions`, `capability_gaps`, `candidate_experiments`, and `disagreements`.
- **Escalation:** missing data or ambiguous platform behavior becomes a question for Jean/Magnus; it is never guessed.

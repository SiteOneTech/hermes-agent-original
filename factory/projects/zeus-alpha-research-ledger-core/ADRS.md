---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: yes
---

# Architecture Decision Records

## ADR-001 — Shared Agent Core database, dedicated module schema
**Decision:** use the existing local Agent Core Postgres instance with schema `alpha_research`.

**Why:** structured local data is canonical for Zeus modules; a detached database/service would duplicate operating complexity without a platform need.

## ADR-002 — Dedicated runtime role, explicit grant matrix and no fallback
**Decision:** the migration/admin principal owns DDL; `alpha_research_runtime` receives only enumerated `alpha_research` object grants and a dedicated Infisical credential. There is no shared-role or fallback password/DSN.

**Why:** this module will store externally-originated evidence; auditable least privilege requires database-enforced separation rather than intent alone.

## ADR-003 — Database invariants before handler convenience
**Decision:** source policy, evidence uniqueness/supersession, append-only evidence/reviews, lineage integrity, classifications and inert handoff state are enforced with FKs/checks/unique indexes/triggers. Handlers add usability validation only.

**Why:** direct SQL or future handlers must not bypass research integrity.

## ADR-004 — Typed research-only classification
**Decision:** cards, reviews, JSON responses and handoffs carry immutable `research_only`, `unvalidated` and `not_investment_advice` state. Prohibited validated/advice/activation labels are rejected.

**Why:** an evidence-backed hypothesis is not an approved strategy, investment recommendation or operational directive.

## ADR-005 — Source registry in core; concrete provider drivers out of tree
**Decision:** the core owns source-policy and normalized-evidence intake. Concrete third-party fetch/parse drivers ship only as separately scoped standalone plugin/MCP/CLI integrations.

**Why:** daily research cannot make unchecked data or credentials canonical, and this repository must not absorb provider maintenance.

## ADR-006 — Local evidence batch, not network collection
**Decision:** v1 “collection” means local intake of a typed normalized-evidence batch. It stores reference strings but has no network client, URL-open, recipient or dispatch behavior.

**Why:** it produces an auditable daily research cycle while respecting the no-external-connector boundary.

## ADR-007 — Inert local handoff before any connector
**Decision:** handoff preparation is persisted locally with `dispatch_state=not_dispatched`; it cannot dispatch network calls.

**Why:** it proves research semantics and provenance while preserving Vonash’s independent authority.

## ADR-008 — Scheduler disabled by default
**Decision:** no local research scheduler registers until configuration and verified local prerequisites are present. It consumes only already normalized local evidence.

**Why:** process sequencing is not a safety boundary; activation must fail closed.

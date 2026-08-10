---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: yes
---

# FACTORY INTAKE — Zeus Alpha Research Ledger Core

## Owner mandate
Jean García authorized Zeus to independently build and operate the **Zeus-side** research process: daily research analysis, provenance records, Alpha Cards, skeptical reviews and an eventual research-only handoff package. V1 local “collection” is strictly typed intake of already-normalized local evidence; third-party retrieval belongs to a later separately scoped integration. The target delivery policy remains Zeus-signed PR and independent QA. Agent Core/Git evidence shows two prior ALR-010-R1 documentary commits were directly integrated into `origin/main` (`173433`/`b9396bcd7d14ee6f212bd0fd0609e468cecf567f`/`e3d04ff94b67e6e21be1d5515bdb71400fbedf0a` and `173494`/`6ee8b4fdb886d0834bfbc62c7e152ee35d505e66`/`9f975acb0625750b8d46648766d1395c89392dca`); this is recorded as gate-695/gate-697 reconciliation evidence, not as production approval, deploy authority, `reviewed: yes`, PR approval, or downstream implementation authority.

## Why this is a successor, not a duplicate
`zeus-independent-alpha-research` is the completed, documentation-only predecessor. It established the Vonash separation boundary and a future exchange design, but explicitly delivered no Zeus runtime module. This project is the first implementation phase of the private ledger that prepares results for a later external integration. `predecessor_project_id=zeus-independent-alpha-research` is recorded in Factory DB.

## Business outcome
A local Agent Core module gives Zeus repeatable, evidence-backed research memory instead of relying on chat history. A daily run answers: what local evidence was recorded, its source/terms/freshness state, the derived claim, proposed mechanism, failure modes and whether the result is fit only for an inert future handoff.

## Scope
- Shared local Agent Core Postgres schema `alpha_research`.
- Dedicated `alpha_research_runtime` database role and Infisical-managed credential.
- Chat-first JSON tools and a non-default `alpha_research` toolset.
- Adapter-neutral source policy and local normalized-evidence intake with provenance, freshness, licensing/terms and deduplication. Concrete third-party source drivers require a separately scoped standalone plugin/MCP/CLI integration.
- Default-disabled local research-cycle worker and an inert handoff artifact.
- Tests, private DB/tool smoke, independent quality/security review, Zeus-signed GitHub PR.

## Explicit exclusions
- No Vonash, Magnus, VAOS, Brain/APC, RAG/KB, Slack or Telegram connector.
- No HTTP/network provider client, direct cross-database writes, shared service secrets, Cloud SQL privilege, broker APIs, orders, portfolio/risk mutation, strategy promotion, paper activation, live activation or deployment.
- No collaboration session/message persistence in v1.
- No claim that an evidence item, Alpha Card or handoff package is approved strategy, validated alpha or investment recommendation.

## Sources of truth
1. Agent Core Postgres `factory.*` is the Factory operational ledger.
2. This repository’s `factory/projects/zeus-alpha-research-ledger-core/` is the project documentary pack.
3. Branch/PR/test evidence is the source delivery artifact.
4. The prior Vonash issue #765 is only external collaboration control; it grants no local or external execution authority.

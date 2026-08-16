---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: yes
reviewed_by: solution-architect
review_evidence: factory_gate_794
reviewed_candidate_sha: c81547062c5362a7be6f5a1bb2ef9612b29bac9c
reviewed_candidate_pr: https://github.com/SiteOneTech/hermes-agent-original/pull/36
reviewed_source_gate: factory_gate_790
reviewed_source_sha: 2476e978c545e24b18ee48844b24eb8c58245ab4
r2x_current_origin_main_sha: b3c32d149d73156b75c15b5b357898b69737bed0
r2x_document_status_evidence: agent_core_postgres_factory_status_configured_base_ref
r2x_reconciliation_artifact: R2X_CURRENT_ORIGIN_MAIN_G1_RECONCILIATION.md
---

# PRD — Zeus Alpha Research Ledger Core

## Product statement
Zeus needs a private, provenance-rich research workspace that turns *locally supplied normalized evidence* into reviewable Alpha Cards and bounded records. It improves research memory and later collaboration readiness without becoming a trading engine, external orchestrator, provider client or private-data mirror.

## Primary operator journey
1. Zeus opens or resumes a research program and idempotent daily cycle.
2. A typed local normalized-evidence batch is recorded only when its source registry policy, terms and freshness validate; no source is fetched by this core.
3. Zeus drafts an immutable-classified Alpha Card that names a mechanism, explicit ways it could fail and the fixed `research_only`/`unvalidated`/`not_investment_advice` contract.
4. A separate skeptical review accepts, requests revision, archives or rejects the card.
5. The cycle closes with a terminal summary, including explicit empty/rejected/failed outcomes.
6. Zeus may prepare an inert local handoff for later human/team inspection; it has no recipient, network dispatch or operational effect.

## Success metrics
- Every non-archived card has linked evidence, mechanism fingerprint, falsification plan and research-only classification.
- Every usable source has approved terms state, defined freshness policy and accepted/rejected intake outcome.
- Daily cycles have terminal state and no hidden missing-data success.
- Smoke and negative tests prove a full synthetic local flow, database constraints, least privilege, disabled scheduler defaults and zero prohibited external side effects.

## Release acceptance
A release is acceptable only as a Zeus-signed `agent:zeus` PR that has migration/tool tests, direct SQL/role negatives, source-policy/intake tests, local smoke cleanup proof, ALR-061/062/063 independent reports, and QA Guardian merge evidence. It must explicitly prove no external connector, trading, paper/live or deployment feature was added.

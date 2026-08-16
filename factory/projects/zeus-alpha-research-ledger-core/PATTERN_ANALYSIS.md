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

# PATTERN ANALYSIS

## Reusable patterns
1. **Agent Core module pattern** — own schema/migrations/runtime role/tools/toolset/docs/tests while the shared Postgres instance remains the local system of record.
2. **Evidence-before-claim** — raw source and retrieved context precede a normalized claim; an Alpha Card links to evidence IDs rather than copying unverifiable prose.
3. **Mechanism-family lineage** — a card is a variant if it shares the mechanism fingerprint; title changes and parameter adjustments cannot masquerade as novelty.
4. **Skeptical review as a first-class record** — reviewer, review type, evidence gaps, falsifiers and disposition remain distinct from card authoring.
5. **Inert handoff first** — serialize and validate research-only content locally before an external connector is even designed.
6. **Adapter-neutral evidence intake** — the core accepts normalized evidence or an explicit unavailable/stale/terms-unknown outcome. Any concrete third-party fetch/parse driver is an out-of-tree standalone plugin/MCP/CLI integration, never a core dependency.

## Anti-patterns rejected
- Chat memory as canonical research database.
- Copying Vonash schemas, directly mutating Vonash data or giving Zeus `APC_INTERNAL_SECRET`.
- Treating a provider response or backtest reference as an approved strategy.
- Reusing a broad Agent Core runtime credential for an externally facing research module.
- Unbounded agent-to-agent conversation, bulk KB ingestion or automatic Telegram/Slack mirroring.
- Scheduler jobs that silently swallow errors, produce unverifiable prose, or create external side effects.

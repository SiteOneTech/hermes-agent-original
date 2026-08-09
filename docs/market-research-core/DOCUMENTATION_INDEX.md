# Market Research Core — Documentation Index

## Concise product references

1. [PRD-001 — Market Research Ledger](PRD-001-market-research-ledger.md)
2. [ADR-001 — Local Zeus Market Research Ledger](ADR-001-local-market-research-ledger.md)
3. [Sprint Plan 001](SPRINT-PLAN-001.md)
4. [Task Graph](TASK_GRAPH.md)
5. [QA & Security Gates](QA-SECURITY-GATES.md)
6. [Operating Model v1](OPERATING_MODEL_V1.md)

## Controlling Factory record

- **Project ID:** `zeus-independent-alpha-research`
- **Repository:** `SiteOneTech/hermes-agent-original`
- **Base branch:** `main`
- **Controlling G1 pack:** [`factory/projects/zeus-independent-alpha-research/DOCUMENTATION_INDEX.md`](../../factory/projects/zeus-independent-alpha-research/DOCUMENTATION_INDEX.md)
- **Current planning source:** the committed project-local G1 pack, not any historical worktree path.
- **I0 scope:** Zeus-only planning/documentation; I0 makes no Vonash runtime mutation.
- **Future Vonash implementation:** a planned, audit-gated handoff defined in [`VONASH_IMPLEMENTATION_HANDOFF.md`](../../factory/projects/zeus-independent-alpha-research/VONASH_IMPLEMENTATION_HANDOFF.md). It is not automatic propagation and cannot begin before the I1 read-only audit establishes real ownership, interface and security facts.

## Operating principle

Zeus is an independent research generator and evidence ledger; Magnus is Vonash’s runtime CEO/operator. A typed service-owned research thread/outbox/acknowledgement is the canonical cross-system record. Telegram may mirror the collaboration for visibility, but never replaces the record. Zeus never repairs, controls or directly writes to the Vonash refactor/runtime.

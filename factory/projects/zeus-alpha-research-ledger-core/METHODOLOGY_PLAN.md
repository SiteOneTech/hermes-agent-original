---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: pending
---

# METHODOLOGY PLAN

## Delivery method
Hybrid Factory execution with strict G1 → TDD → independent review → PR/QA Guardian handoff.

1. **ALR-010** remediates this documentary pack, commits the bounded rework, then obtains new independent specification and security reviews against that exact SHA before any documentation PR.
2. Only after that PR is QA-merged into canonical base may Factory dispatch ALR-020 through ALR-050 in isolated branches/worktrees.
3. Every builder reads `DOCUMENTATION_INDEX.md`, traceability and task acceptance before changing code; every behavior follows observed RED → minimal GREEN → REFACTOR.
4. ALR-061 (spec/architecture), ALR-062 (quality/TDD) and ALR-063 (security/no-egress) are distinct independent artifacts. They cite the exact candidate SHA and create bounded rework rather than self-approval.
5. ALR-070 runs synthetic local DB/tool smoke with cleanup only after all three reviews are accepted. No provider credential value is printed and no network dispatch is enabled.
6. Every source increment is a Zeus-signed, `agent:zeus` labeled PR to QA Guardian. The documented per-task Factory integration waiver prevents automatic direct merge; QA Guardian merge evidence is required before terminal closure. Zeus never merges/deploys.

## Stop conditions
Stop and create a concrete repair task if G1 docs are stale; the role/secret/grant matrix or lifecycle function elevation is incomplete; immutable source/terms provenance or the ALR-020 metadata reconciliation is missing; source terms/freshness are unknown; a test does not first fail; a tool/script implies external action; a migration risks unrelated schemas; no-egress proof fails; or scope drifts into sessions/messages, Vonash, trading, paper/live behavior.

## Scheduler rule
The scheduler is absent/disabled by default. It may be locally registered only after ALR-070 records passing migration, dedicated role/secret presence, approved source policy, leaf toolset isolation and synthetic no-egress evidence. Outbound delivery remains disabled until a separate, approved producer-adapter project exists.

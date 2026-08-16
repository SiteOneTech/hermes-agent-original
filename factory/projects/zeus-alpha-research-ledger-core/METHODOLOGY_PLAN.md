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
---

# METHODOLOGY PLAN

## Delivery method
Hybrid Factory execution with strict G1 → TDD → independent review → PR/QA Guardian handoff.

1. **ALR-010** remediates this documentary pack, commits the bounded rework, and obtains new independent specification and security reviews against that exact SHA. The prior ALR-010-R1 commit `b9396bcd7d14ee6f212bd0fd0609e468cecf567f` is already on `origin/main` via Factory event `173433` / merge commit `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a`; that exposure is gate-695 audit evidence, not review approval.
2. Only after exact-SHA independent PASS reviews, accepted gate-695 reconciliation, and the documented ALR-020 metadata correction may Factory dispatch ALR-020 through ALR-050 in isolated branches/worktrees.
3. Every builder reads `DOCUMENTATION_INDEX.md`, traceability and task acceptance before changing code; every behavior follows observed RED → minimal GREEN → REFACTOR.
4. ALR-061 (spec/architecture), ALR-062 (quality/TDD) and ALR-063 (security/no-egress) are distinct independent artifacts. They cite the exact candidate SHA and create bounded rework rather than self-approval.
5. ALR-070 runs synthetic local DB/tool smoke with cleanup only after all three reviews are accepted. No provider credential value is printed and no network dispatch is enabled.
6. Future source increments must use a Zeus-signed, `agent:zeus` labeled PR to QA Guardian. The documented per-task Factory integration waiver remains the expected guard; any direct integration event must be recorded, independently reviewed, and treated as non-approval evidence unless Jean explicitly changes the policy. This task performs no new merge or deploy.

## Stop conditions
Stop and create a concrete repair task if G1 docs are stale; the role/secret/grant matrix or lifecycle function elevation is incomplete; immutable source/terms provenance or the ALR-020 metadata reconciliation is missing; source terms/freshness are unknown; a test does not first fail; a tool/script implies external action; a migration risks unrelated schemas; no-egress proof fails; or scope drifts into sessions/messages, Vonash, trading, paper/live behavior.

## Scheduler rule
The scheduler is absent/disabled by default. It may be locally registered only after ALR-070 records passing migration, dedicated role/secret presence, approved source policy, leaf toolset isolation and synthetic no-egress evidence. Outbound delivery remains disabled until a separate, approved producer-adapter project exists.

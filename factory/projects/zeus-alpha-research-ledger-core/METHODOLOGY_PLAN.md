---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: yes
---

# METHODOLOGY PLAN

## Delivery method
Hybrid Factory execution with strict G1 → TDD → independent review → PR/QA Guardian handoff.

1. **ALR-010-R2** remediates this documentary pack, commits the bounded rework on its isolated branch, makes that exact candidate visible through a Zeus-signed `agent:zeus` GitHub PR, and obtains new independent specification and security reviews against that exact SHA. The prior ALR-010-R1 commits `b9396bcd7d14ee6f212bd0fd0609e468cecf567f` and `6ee8b4fdb886d0834bfbc62c7e152ee35d505e66` are already on `origin/main` via Factory events `173433`/`173494` and merge commits `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a`/`9f975acb0625750b8d46648766d1395c89392dca`; that exposure is gate-695/gate-697 audit evidence, not review approval.
2. Only after exact-SHA independent PASS reviews, accepted gate-695/gate-697 reconciliation, Zeus-signed PR visibility, and the documented ALR-020 metadata correction may Factory dispatch ALR-020 through ALR-050 in isolated branches/worktrees.
3. Every builder reads `DOCUMENTATION_INDEX.md`, traceability and task acceptance before changing code; every behavior follows observed RED → minimal GREEN → REFACTOR.
4. ALR-061 (spec/architecture), ALR-062 (quality/TDD) and ALR-063 (security/no-egress) are distinct independent artifacts. They cite the exact candidate SHA and create bounded rework rather than self-approval.
5. ALR-070 runs synthetic local DB/tool smoke with cleanup only after all three reviews are accepted. No provider credential value is printed and no network dispatch is enabled.
6. This R2 documentary increment and all future source increments must use a Zeus-signed, `agent:zeus` labeled PR to QA Guardian visibility before any base-branch merge. The documented per-task Factory integration waiver remains the expected guard; any direct integration event must be recorded, independently reviewed, and treated as non-approval evidence unless Jean explicitly changes the policy. This task may push only its assigned branch/PR; it must not perform another direct base merge or deploy.

## Stop conditions
Stop and create a concrete repair task if G1 docs are stale; the role/secret/grant matrix or lifecycle function elevation is incomplete; immutable source/terms provenance or the ALR-020 metadata reconciliation is missing; source terms/freshness are unknown; a test does not first fail; a tool/script implies external action; a migration risks unrelated schemas; no-egress proof fails; or scope drifts into sessions/messages, Vonash, trading, paper/live behavior.

## Scheduler rule
The scheduler is absent/disabled by default. It may be locally registered only after ALR-070 records passing migration, dedicated role/secret presence, approved source policy, leaf toolset isolation and synthetic no-egress evidence. Outbound delivery remains disabled until a separate, approved producer-adapter project exists.

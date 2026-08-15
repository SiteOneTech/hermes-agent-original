---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: yes
---

# QA GATES

## ALR-010 documentary gate
- All 14 G1 documents plus G0, `REQUIREMENTS_TRACEABILITY.md`, `DATABASE_AND_RUNTIME_CONTRACT.md` and `G1_REVIEW.md` exist, are indexed, committed and independently PASS-reviewed.
- `TASK_GRAPH.md` reconciliation matches current Factory task IDs, phases, owner/reviewer profiles, dependencies, branches, worktrees, PR-first metadata and both observed ALR-010-R1 direct integration events (`173433` and `173494`); Factory event 174440 records the exact ALR-020 acceptance metadata correction/read-back that removes the incompatible bounded-local-sessions clause while preserving v1 session/message exclusion. The event is not implementation or approval authority.
- No document implies direct Vonash/trading authority, provider integration in core, or that either observed ALR-010-R1 direct Factory merge is approval/waiver/repeatable policy.

## ALR-020 database/role RED-GREEN gate
- Start with tests for every contract §1/§2/§3 constraint, trigger, lifecycle edge/changed-column/capability/catalog assertion, grant and named direct-SQL negative; observe RED before migration implementation.
- Green proves exact role properties/object grants, no `PUBLIC` access, source-reference/terms-reference immutability and approval/revision audit provenance, source freshness predicate, evidence/review append-only behavior, lineage integrity and all-card/review/handoff classification tuple enforcement.

## ALR-030 tools RED-GREEN gate
- Start with every-handler input/envelope/unknown-field/default-toolset/exact-`program_create`/`source_submit` leaf-allowlist/missing-secret negative. Observe RED before registration/handler implementation.
- Green proves field-bounded card input, fixed handoff-list object, unambiguous envelope/payload key counts, JSON envelope and exact no-advice contract in §3 plus all named prohibited labels/action fields and synthetic-secret redaction across output/log/error/tracing.

## ALR-050 scheduler/no-egress RED-GREEN gate
- Start with static scan failures for each banned dependency/SQL form in every added/replacement implementation diff line and runtime harness failures for every handler/scheduler path under interception.
- Green proves contract §4 all-ALR-modified-diff-line coverage, banned pattern rejection and exact-local-DSN-only DB connection.
- Start with config false/missing and every missing/failed/expired/wrong-commit readiness component; green proves no registration/no run and structured `scheduler_not_ready` under contract §5.

## Independent review gate
- **ALR-061** maps R1–R10/boundaries to exact implementation SHA, direct tests and scope limits.
- **ALR-062** verifies RED/GREEN artifacts, quality, test determinism and cleanup.
- **ALR-063** verifies the contract §1–§5 security proof against the exact candidate SHA.
- Each report cites the candidate SHA and creates bounded rework rather than broad approval.

## Live local gate
- Actual local Agent Core migration and dedicated-role tests run without secret output.
- Synthetic local batch → evidence → card → separate review → cycle → inert handoff passes and cleanup is verified.
- Negative live smoke proves no outbound connection/subprocess dispatch, external runtime write, trading/risk/paper/live action or credential output.

## Delivery gate
- Exact branch commit, test commands/results and independent reports are recorded.
- Actual GitHub PR exists with Zeus signature and `agent:zeus` label, and its head SHA is the exact SHA inspected by independent reviewers.
- For this R2 documentation increment and future source increments, QA Guardian/independent review evidence is mandatory before terminal closure; per-task waiver metadata remains the expected guard against Factory direct branch-to-base integration. The observed ALR-010-R1 `merge_no_ff_push_origin` events `173433` and `173494` must be treated as reconciled audit evidence, not as delivery approval or deployment authority.

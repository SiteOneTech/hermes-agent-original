---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: pending
---

# QA GATES

## ALR-010 documentary gate
- All 14 G1 documents plus G0, `REQUIREMENTS_TRACEABILITY.md` and `G1_REVIEW.md` exist, are indexed and independently reviewed.
- The Factory DB reconciliation table in `TASK_GRAPH.md` matches current task IDs, phases, owner/reviewer profiles, dependencies, branches, worktrees and explicit PR-first integration waiver.
- No document implies direct Vonash/trading authority, in-tree third-party provider integration or a Factory direct merge.

## Implementation RED/GREEN gates
- Each production behavior has a test observed failing before code, then passing after minimal implementation.
- Migration tests prove schema registration; FKs/checks/uniques; append-only evidence/review denial; source enabled/terms/freshness enforcement; lineage integrity; research classification and inert-handoff constraints.
- Role tests use the actual `alpha_research_runtime` role: permitted table operations succeed and denied cross-schema/create/update/delete/privilege operations fail.
- Tool tests prove required-field validation precedes DB calls, default-toolset absence, exact leaf allowlist, forbidden labels/fields rejection and missing-secret activation failure.
- No-egress tests combine static import/dependency assertions and runtime-negative probes for network clients, sockets, remote DSNs, internal shared secrets, prohibited platform clients and subprocess dispatch.
- Scheduler tests prove no registration/run on disabled default, missing secret/role, failed migration, no approved source policy or failed no-egress smoke.

## Review gate
- **ALR-061** independently maps requirements/boundaries to exact code/tests and rejects scope drift.
- **ALR-062** independently verifies TDD evidence, quality and module conventions.
- **ALR-063** independently verifies grants, direct-SQL negatives, secret handling, tool isolation and no-egress proof.
- Each report cites the exact candidate SHA and creates bounded rework rather than vague approval.

## Live local gate
- DB migration and dedicated role verification run against the actual local Agent Core database without secret output.
- Synthetic local batch → evidence → card → separate review → cycle → inert handoff smoke succeeds and cleanup is verified.
- Negative smoke proves zero network dispatch, external runtime write, broker/trading/risk operation, paper/live activation or credential output.

## Delivery gate
- Exact branch commit, test commands/results and independent review reports are recorded.
- Actual GitHub PR exists with Zeus signature and `agent:zeus` label.
- QA Guardian merge evidence is mandatory before terminal task closure. The per-task integration waiver blocks Factory’s default direct branch-to-base merge; Zeus does not merge/deploy.

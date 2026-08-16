---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_reviewed_candidate_primary_hold
validated: yes
reviewed: yes
reviewed_by: quality-reviewer
review_evidence: factory_gate_790
reviewed_candidate_sha: 2476e978c545e24b18ee48844b24eb8c58245ab4
reviewed_candidate_pr: https://github.com/SiteOneTech/hermes-agent-original/pull/34
reviewed_source_gate: factory_gate_789
reviewed_source_sha: 1e82340dddf52071d14c3c7a00b04b3c17ee2821
---

# QA GATES

## ALR-010 documentary gate
- All 14 G1 documents plus G0, `REQUIREMENTS_TRACEABILITY.md`, `DATABASE_AND_RUNTIME_CONTRACT.md` and `G1_REVIEW.md` exist, are indexed, committed and independently PASS-reviewed.
- `TASK_GRAPH.md` reconciliation matches current Factory task IDs, phases, owner/reviewer profiles, dependencies, branches, worktrees, PR-first metadata and the observed ALR-010-R1 direct integration event; before ALR-020, the incompatible bounded-local-sessions acceptance clause has the exact documented metadata correction/read-back evidence and v1 session/message exclusion remains intact.
- No document implies direct Vonash/trading authority, provider integration in core, or that the observed ALR-010-R1 direct Factory merge is approval/waiver/repeatable policy.

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
- Actual GitHub PR exists with Zeus signature and `agent:zeus` label.
- For future source increments, QA Guardian merge evidence is mandatory before terminal closure; per-task waiver metadata remains the expected guard against Factory direct branch-to-base integration. The observed ALR-010-R1 `merge_no_ff_push_origin` event must be treated as reconciled audit evidence, not as delivery approval or deployment authority.
- PR-first/QA Guardian evidence must be candidate-bound: for PR #29 the candidate commit is `f61a7275048e2135b2b2729a1b9cdf8713c58866`. A review-only branch `already_ancestor` record at `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c` is not acceptable source-merge or QA Guardian evidence for that PR.
- R2q reviewed-docs recovery evidence is candidate-bound to Factory gate 790, reviewer `quality-reviewer`, PR #34 head `2476e978c545e24b18ee48844b24eb8c58245ab4`, source gate 789 / PR #33 head `1e82340dddf52071d14c3c7a00b04b3c17ee2821`, and current recovery base `origin/main` `df4c77fd1413a65cdb85885a06978ff157c1de4d`.
- R2p/PR #35 and run `run-1786840866-90f55f9d` are explicitly invalid as review completion evidence because the quality-reviewer session ended on provider HTTP 429 with zero tool calls. Provider failure leaves work blocked/retriable.
- R2r replacement evidence must bind source R2q commit `11639ab1650a4d7abfa88820bc266c983a56d1fd`, replacement branch `factory/zeus-alpha-research-ledger-core/inc-001-r2r-pr-first-recovery-of-the-r2q`, current base `df4c77fd1413a65cdb85885a06978ff157c1de4d`, Zeus-authored/sign-off commit metadata, an open GitHub PR and label `agent:zeus`.
- The independent R2r solution-architect review must cite the final open-PR head SHA and include evidence that review work actually ran: files read, diff inspected, commands run and/or tool calls made. A zero-tool or provider-failed review cannot satisfy this gate.
- Obsolete project metadata pointing to PR #20 / `dad375f27568c38be771fc597b579d087f034e1d`, historical PR #29/f61a review PASS records, PR #30/c1943 merge evidence, PR #31/R2k exposure, R2m handoff evidence and PR #35/R2p code-path evidence are not sufficient to claim primary readiness or dispatch ALR-020. Primary readiness must be read back from Agent Core `document_status` or an authorized reviewed-candidate metadata path after the source state is accepted.

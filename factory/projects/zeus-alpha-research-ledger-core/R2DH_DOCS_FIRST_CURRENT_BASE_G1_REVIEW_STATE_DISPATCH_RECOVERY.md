---
document_type: docs_first_current_base_g1_review_state_dispatch_recovery
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2dh-docs-first-current-base-g1-review-s
phase: documentation
status: implementation_evidence_candidate_review_pending
validated: yes
reviewed: pending
reviewed_by: pending_quality-reviewer
review_evidence: pending_independent_exact_sha_quality_gate
owner: codex-builder
base_ref: origin/main
base_sha: abc164184d588a7a9e5e4838f5a101d9f4e3a0f2
branch: factory/zeus-alpha-research-ledger-core/inc-010-r2dh-docs-first-current-base-g1
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-010-r2dh-docs-first-current-base-g1
run_id: run-1787138710-99b3b947
---

# R2dh — docs-first current-base G1 review-state dispatch recovery

## Scope

This is the bounded documentation/evidence candidate for the repeated
`claimed=null`/docs-first dispatch failure on project
`zeus-alpha-research-ledger-core`. It uses only the assigned isolated
worktree, current `origin/main` readback, committed project-local Factory
G1 documents, and the sanctioned Factory CLI surfaces:

- `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status`
- `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory gate record`

It records current source-backed evidence and distinguishes current
configured-base document readiness from stale historical gate/event/task rows.
It does not modify Alpha Ledger product/runtime code, Factory runtime code,
providers, migrations, tools, schedulers, credentials, deployment behavior,
message/connectors, primary checkout state, reviewed frontmatter markers, task
status, stale refs/PRs, direct SQL, external runtime/provider calls, Vonash,
Magnus, VAOS, RAG/KB, brokers, trading, risk, or paper/live activation.

## Current base and worktree identity

Captured before documentation edits:

- Worktree:
  `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-010-r2dh-docs-first-current-base-g1`
- Branch:
  `factory/zeus-alpha-research-ledger-core/inc-010-r2dh-docs-first-current-base-g1`
- `git rev-parse HEAD`: `abc164184d588a7a9e5e4838f5a101d9f4e3a0f2`
- `git rev-parse origin/main`: `abc164184d588a7a9e5e4838f5a101d9f4e3a0f2`
- `git merge-base HEAD origin/main`: `abc164184d588a7a9e5e4838f5a101d9f4e3a0f2`
- Base commit subject: `Merge Factory increment zeus-alpha-research-ledger-core-r2dg-bounded-g1-exact-sha-independent-re into main`
- Parentage: `9ea2756e6bfbce9d07c7ce32319a8b64bd8cea15` + `5f13f71407a0ff6966666c016d47d281ba02a5af`
- Git identity: `Zeus <zeus@sitiouno.com>`; delivery commits must carry
  `Signed-off-by: Zeus <zeus@sitiouno.com>`.
- Assigned remote branch existence check before first push:
  `git ls-remote --heads origin factory/zeus-alpha-research-ledger-core/inc-010-r2dh-docs-first-current-base-g1`
  returned no ref.

Predecessor delivery readback: PR #91 is merged, non-draft, labeled
`agent:zeus`, base `main`, head branch
`factory/zeus-alpha-research-ledger-core/inc-001-r2dg-bounded-g1-exact-sha-indepe`,
head SHA `5f13f71407a0ff6966666c016d47d281ba02a5af`, merge commit
`abc164184d588a7a9e5e4838f5a101d9f4e3a0f2`.

## Canonical Factory status readback

Command run from the assigned worktree:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`

Evidence files:

- Raw status: `/tmp/r2dh-status-before.json` (`3,920,382` bytes)
- Pretty status: `/tmp/r2dh-status-before.pretty.json` (`4,438,709` bytes)

Readback facts from Agent Core Postgres:

- `db_backend=agent_core_postgres`
- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-010-r2dh-docs-first-current-base-g1`
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-010-r2dh-docs-first-current-base-g1`
- `factory_status_delegated=false`
- Top-level project document rows use `base_ref=origin/main`,
  `base_commit=abc164184d588a7a9e5e4838f5a101d9f4e3a0f2`, and
  `readiness_source=configured_base_ref`.
- Required G1 rows: `14`.
- Current required-G1 blocker list from the configured-base rows: empty.
- Active project metadata: `reconciliation_anomalies=[]` and
  `reconciliation_projection_source=current_document_status`.
- The stale primary checkout is rejected in each current G1 row with
  `primary_checkout_accepted=false` and
  `primary_checkout_rejected_reason=primary_checkout_not_configured_base`.

The current canonical status therefore does not support a current
`unvalidated_required_docs`, `missing_or_unindexed_docs`, or `reviewed=false`
required-G1 document blocker at `origin/main` `abc164184d...`.

## Exact historical 11-document blocker set

The exact 11-document blocker set still visible in historical Factory gate
snapshots is:

1. `FACTORY_INTAKE.md`
2. `REQUIREMENTS_ANALYSIS.md`
3. `PATTERN_ANALYSIS.md`
4. `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`
5. `PRD.md`
6. `ADRS.md`
7. `METHODOLOGY_PLAN.md`
8. `TECHNICAL_BLUEPRINT.md`
9. `SPRINT_PLAN.md`
10. `TASK_GRAPH.md`
11. `SECURITY_GATES.md`

Representative Agent Core readback sources in `/tmp/r2dh-status-before.pretty.json`:

- Gate `854` (`critical_readiness`, `failed`, `2026-08-17T00:39:03.110215+00:00`) reports `blocking_count=11` with the exact set above.
- Gates `845`, `841`, `839`, `834`, `831`, `828`, `825`, `818`, `817`, `814`, `812`, `809`, `805`, `799`, `785`, `772`, `771`, `766`, `760`, `759`, `757`, and `755` preserve the same 11-document set as historical failed snapshots.
- Gate `838` and a few related snapshots preserve the older ten-document variant that omits `SPRINT_PLAN.md`; that is stale assignment/projection history and must not be treated as the current canonical blocker set.
- Gate `958` reports a different historical one-document `DOCUMENTATION_INDEX.md` blocker; the current top-level document row for `DOCUMENTATION_INDEX.md` is non-blocking at `abc164184d...`.

This R2dh candidate records the historical 11-document set without changing any
G1 reviewed frontmatter marker. The committed required G1 documents at the
current configured base remain `reviewed: yes` through the existing source
review chain, while this R2dh evidence artifact itself remains `reviewed:
pending` until an independent exact-SHA quality gate is recorded.

## Distinction from stale validation-task rows

The repeated docs-first dispatch denials for the predecessor documentation
recovery task are not row-level current document blockers. Recent current-base
Agent Core events show a separate validation-task/lifecycle predicate:

- Event `202237` denies task
  `zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation`
  with `unresolved_validation_tasks`.
- The named stale validation tasks are:
  - `zeus-alpha-research-ledger-core-r2h-isolated-independent-g1-exact-sha-re` — `superseded`
  - `zeus-alpha-research-ledger-core-r2ai-current-origin-g1-independent-revie` — `blocked`
  - `zeus-alpha-research-ledger-core-r2l-documentation-phase-exact-sha-g1-rev` — `superseded`
  - `zeus-alpha-research-ledger-core-r2g-renewed-independent-g1-review-of-pr-` — `superseded`
  - `zeus-alpha-research-ledger-core-alr-060-independent-quality-and-security` — `superseded`
  - `zeus-alpha-research-ledger-core-alr-061-independent-specification-and-ar` — `todo`
  - `zeus-alpha-research-ledger-core-alr-062-independent-quality-and-tdd-revi` — `todo`
  - `zeus-alpha-research-ledger-core-alr-063-independent-security-and-no-egre` — `todo`
  - `zeus-alpha-research-ledger-core-alr-070-live-local-db-and-tool-smoke-wit` — `todo`
- Event `202238` denies lower-priority implementation task
  `zeus-alpha-research-ledger-core-r2cw-fail-closed-recovery-for-premature-`
  with `missing_or_unindexed_docs`.
- Events `202229`/`202230`, `202197`/`202198`, `202085`/`202086`,
  `201773`/`201774`, and `201766`/`201767` preserve the same recurring split.

These rows are stale validation-task/history evidence and product-task
fail-closed evidence. They must not be collapsed into current document-content
failures when the top-level configured-base rows read back as clean. This
R2dh increment does not call `factory task close`, does not directly update
`factory.*`, and does not request a human to interpret Factory state.

## Candidate contents and delivery requirements

Project-local documentation changes in this candidate:

- Add this artifact:
  `factory/projects/zeus-alpha-research-ledger-core/R2DH_DOCS_FIRST_CURRENT_BASE_G1_REVIEW_STATE_DISPATCH_RECOVERY.md`
- Index the artifact in `DOCUMENTATION_INDEX.md` and reading order.
- Update `TRACKER.md`, `TASK_GRAPH.md`, `QA_GATES.md`, `SECURITY_GATES.md`, and
  `G1_REVIEW.md` with the current-base R2dh status/evidence.

Required delivery checks for this candidate:

- `git diff --check` must pass.
- Changed paths must remain confined to
  `factory/projects/zeus-alpha-research-ledger-core/` documentation/evidence.
- Delivery must be a Zeus-signed, non-draft, `agent:zeus` PR against `main`
  from the assigned branch.
- The PR body and Factory gate record must name the final pushed PR head SHA,
  base ancestry, current `origin/main`, labels, draft state, merge state, and
  no-merge/no-primary-mutation/no-direct-SQL/no external runtime boundary.
- Independent quality review must inspect the exact final PR head and either
  record a source-backed verdict or create one bounded same-project technical
  rework. This R2dh implementation candidate intentionally does not self-approve.

## No external operation evidence

This run is documentary. It used local Git/GitHub readbacks, project-local file
edits, and the sanctioned Factory status/gate-record CLI only. It performed no
deploy, no credential access/change, no direct SQL, no runtime/provider call,
no connector/messaging operation, no primary checkout mutation, no merge, no
force-push/ref rewrite, no stale PR mutation, no normal product dispatch, and
no trading/risk/paper/live activation.

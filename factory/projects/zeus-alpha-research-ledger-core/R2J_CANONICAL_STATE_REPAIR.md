---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2j-repair-pr-29-g1-canonical-state-evid
phase: g1_review
status: canonical_state_evidence_repaired
validated: yes
reviewed: pending_independent_qa_guardian
owner: codex-builder
---

# R2j canonical-state repair — PR #29 / Factory evidence alignment

## Scope

This is a project-local G1 delivery/traceability repair for the reproduced state disagreement around R2i. It does not merge a PR, modify `main`, deploy, change credentials, write to external runtimes, use direct SQL, dispatch product work, or treat a review-only worktree as a source merge.

## Source-backed state reproduced

Evidence sources used for this repair:

- Git local worktree check from `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2j-repair-pr-29-g1-canonical-st`: current branch `factory/zeus-alpha-research-ledger-core/inc-001-r2j-repair-pr-29-g1-canonical-st`; local `HEAD` and `origin/main` both `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c` before this repair.
- Remote Git source check: `git ls-remote origin refs/heads/main` returned `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c`; `git ls-remote origin refs/pull/29/head refs/pull/29/merge` returned PR-head `f61a7275048e2135b2b2729a1b9cdf8713c58866` and GitHub synthetic merge ref `408e0a6395c9e14af898af9e618ded7ed9cb440e`.
- GitHub PR source check: `GH_REPO=SiteOneTech/hermes-agent-original gh pr view 29 --json ...` returned PR **#29**, state `OPEN`, URL `https://github.com/SiteOneTech/hermes-agent-original/pull/29`, head branch `factory/zeus-alpha-research-ledger-core/inc-001-r2e-rebase-the-g1-documentation`, head `f61a7275048e2135b2b2729a1b9cdf8713c58866`, base `main`, base `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c`, `isCrossRepository=false`, and no merge commit.
- Diff source check: `git diff --name-status --stat 5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c..f61a7275048e2135b2b2729a1b9cdf8713c58866 -- factory/projects/zeus-alpha-research-ledger-core` showed 19 Markdown-only project-local files under `factory/projects/zeus-alpha-research-ledger-core`, including added `R2E_REBASE_VALIDATION.md` and no product/runtime code.
- Factory source check: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json` returned `db_backend=agent_core_postgres`, `database=zeus_agent`, project status `active`, last reconciled at `2026-08-15T19:09:37.898155+00:00`, and `metadata.reconciliation_anomalies=["unvalidated_required_docs"]`.

## Current document_status blocker set

The current Factory `document_status` blocker set is not inferred from a review worktree. It is read from the canonical Factory status payload described above. At that read-back, every listed blocker was `category=g1_required`, `exists=true`, `indexed=true`, `committed=true`, `validated=true`, `reviewed=false`, and `blocking=true`:

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
11. `TRACKER.md`
12. `DOCUMENTATION_INDEX.md`
13. `QA_GATES.md`
14. `SECURITY_GATES.md`

This supersedes earlier blocker snapshots that listed fewer documents. The live source of truth for this repair is the Agent Core Factory status read-back, not the worker prompt snapshot and not a branch-local reviewed marker.

## R2i mismatch root cause

R2i correctly reviewed the actual delivery candidate by exact PR/SHA: PR #29 at `f61a7275048e2135b2b2729a1b9cdf8713c58866` against canonical `main` `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c`. Its independent quality/security gate notes cite that exact PR/head/base relationship.

The disagreement is in the automatically attached Factory increment-integration evidence for the R2i review task. Gates 773 and 774 record `increment_integration_method=already_ancestor`, but the attached integration record names the R2i review branch `factory/zeus-alpha-research-ledger-core/inc-002-r2i-g1-documentation-independent` and `increment_branch_commit=5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c`. That commit is the review-only worktree/main checkout, not PR #29's candidate commit `f61a7275048e2135b2b2729a1b9cdf8713c58866`.

Therefore `already_ancestor` proves only that the R2i review worktree commit was already on canonical `main`. It does **not** prove PR #29 was merged, visible on canonical `main`, or accepted by QA Guardian. Treating that review-branch integration record as source-candidate integration caused the R2i Factory evidence to disagree with the actual PR-first delivery state.

## Corrected provenance and handoff

Canonical interpretation after this repair:

- Actual source delivery candidate: PR #29 head `f61a7275048e2135b2b2729a1b9cdf8713c58866`.
- Canonical base at reproduction: `main` / `origin/main` / remote `refs/heads/main` at `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c`.
- PR state at reproduction: `OPEN`, no merge commit. The synthetic GitHub merge ref `408e0a6395c9e14af898af9e618ded7ed9cb440e` is not a source merge to `main`.
- R2i independent gates remain exact-SHA review evidence for PR #29, but their `increment_integration` attachment is review-worktree evidence only and must not be used as canonical source visibility evidence for PR #29.
- This R2j repair itself is delivered PR-first as PR #30 (`https://github.com/SiteOneTech/hermes-agent-original/pull/30`), head `15f3e3599f67facfde051f820b06fd83cb5ed353` at initial handoff, base `main` `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c`, label `agent:zeus`. PR #30 is a documentation/traceability repair only and must not be confused with PR #29's G1 candidate.
- Factory `document_status` remains blocked by `unvalidated_required_docs` until the canonical project source read-back shows the required G1 docs reviewed through the approved PR-first / QA Guardian path or an explicit authorized source correction.

## QA Guardian review artifact requirement

For this project, QA Guardian evidence must be candidate-bound. A valid QA Guardian handoff/review record for PR-first delivery must name all of the following together:

- `pr.number=29`
- `pr.url=https://github.com/SiteOneTech/hermes-agent-original/pull/29`
- `pr.state=OPEN` or later accepted/merged state at the time of review
- `candidate_commit=f61a7275048e2135b2b2729a1b9cdf8713c58866`
- `base_branch=main`
- `base_commit=5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c` for the reproduced review state, or the exact revalidated base if it changes before final QA Guardian decision
- a source-delivery/QA result whose `qa_guardian_evidence.candidate_commit` equals PR #29's candidate commit, not the review-only R2i worktree commit `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c`

Existing independent evidence available for QA Guardian to consume:

- Gate 763, `quality=passed`, reviewer `quality-reviewer`, task `zeus-alpha-research-ledger-core-r2f-independent-g1-review-of-pr-29-exact`, exact SHA `f61a7275048e2135b2b2729a1b9cdf8713c58866`.
- Gate 764, `security=passed`, reviewer `security-reviewer`, task `zeus-alpha-research-ledger-core-r2f-independent-g1-review-of-pr-29-exact`, exact SHA `f61a7275048e2135b2b2729a1b9cdf8713c58866`.
- Gate 773, `quality=passed`, reviewer `quality-reviewer`, task `zeus-alpha-research-ledger-core-r2i-g1-documentation-independent-exact-s`, exact PR #29 head `f61a7275048e2135b2b2729a1b9cdf8713c58866`; use the gate note as review evidence, but ignore the attached `increment_integration` record as source-merge proof.
- Gate 774, `security=passed`, reviewer `security-reviewer`, task `zeus-alpha-research-ledger-core-r2i-g1-documentation-independent-exact-s`, exact PR #29 head `f61a7275048e2135b2b2729a1b9cdf8713c58866`; use the gate note as review evidence, but ignore the attached `increment_integration` record as source-merge proof.

This artifact is the R2j QA Guardian handoff packet and provenance repair. It deliberately does not claim that QA Guardian has merged PR #29 or that `document_status` is green.

## Verification expectation

A reviewer can verify this repair without trusting this prose by rerunning the read-only commands named above and confirming:

1. PR #29 head is `f61a7275048e2135b2b2729a1b9cdf8713c58866`.
2. Canonical `main` is `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c` for the reproduced state.
3. Factory `document_status` still reports `unvalidated_required_docs` and the blocker set from the canonical Factory status source.
4. R2i gate notes cite PR #29/f61a, while R2i increment-integration metadata cites the review branch at `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c`; those are different artifacts and must not be conflated.

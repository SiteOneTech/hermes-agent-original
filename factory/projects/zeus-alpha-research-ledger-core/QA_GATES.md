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

# QA GATES

## ALR-010 documentary gate
- All 14 G1 documents plus G0, `REQUIREMENTS_TRACEABILITY.md`, `DATABASE_AND_RUNTIME_CONTRACT.md` and `G1_REVIEW.md` exist, are indexed, committed and independently PASS-reviewed; R2u binds the reviewed markers to PR #36 head `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` and Factory gate `794`.
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
- R2m renewal evidence must be candidate-bound to the exact R2m PR head SHA on base `origin/main` `ab08b13669903a87b3d60d6c80231d23d6313782`. Obsolete project metadata pointing to PR #20 / `dad375f27568c38be771fc597b579d087f034e1d`, historical PR #29/f61a review PASS records, PR #30/c1943 merge evidence and PR #31/R2k exposure are not sufficient to change G1 docs to `reviewed: yes` or dispatch ALR-020 until canonical Factory metadata and `document_status` read back reconciled.
- R2u delivery evidence must remain documentation-only: the PR evidence records the exact R2u head/base SHA, `git diff --check`, tracked-document validation, local candidate document-status preflight with zero required blockers, and no merge/deploy/credential/external-runtime/product code change. Clearing G1 document blockers does not bypass downstream ALR task gates.

## R2v control-plane repair gate
- R2v must prove with RED then GREEN behavioral tests that stale primary checkout G1 blockers are resolved only from the verified configured base ref content, not from task branches, PR heads, or arbitrary worktrees.
- R2v must prove missing/unreadable/invalid configured base refs fail closed and that `factory_auto_integration_forbidden=true` prevents `merge_no_ff_push_origin` and `increment_integrated` Factory completion side effects.
- R2v delivery remains a Zeus-signed `agent:zeus` PR with exact branch SHA/PR readback and independent exact-SHA quality review before task closure; no direct main merge is authorized by this increment.

## R2v independent quality review — gate 804 (PASS)
- Reviewer: `quality-reviewer` profile, independent of the `codex-builder` implementation.
- Reviewed exact implementation head: `90fcb81abcebc203e16e34e36f4aec0ab1ec6a09`; code diff reviewed `50a9a29c4bb7cee39c8ffafa857ce962066e35cb..90fcb81abcebc203e16e34e36f4aec0ab1ec6a09` (2 commits: fix + PR-evidence doc).
- GitHub readback (`gh api repos/SiteOneTech/hermes-agent-original/pulls/39`): state=open, base=`main`, head_ref=`factory/zeus-alpha-research-ledger-core/inc-005-r2v-canonical-g1-status-and-no-a`, head_sha=`90fcb81abcebc203e16e34e36f4aec0ab1ec6a09`, author=`sitiouno`, labels=`["agent:zeus"]`, merged=false.
- Independent GREEN (worktree, main-checkout venv, exact head): `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_increment_integration.py` → 2 files, **254 passed, 0 failed** (9.1s, 48 workers) — matches the documented GREEN evidence exactly.
- RED: recorded in `R2V_CANONICAL_G1_STATUS_AND_NO_AUTO_MERGE_REPAIR.md` and confirmed by diff-contrast — at base `50a9a29c` the candidate-resolution path still cleared blockers, no base-ref fallback existed, and the forbidden-integration guard did not exist, so the new behavioral tests cannot pass on base code.
- Primary checkout non-mutation: `/home/jean/Projects/hermes-agent-original` HEAD remains `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`, working tree clean; the status path performs no checkout/fetch/merge/fast-forward.
- No-external-operation: diff limited to `hermes_cli/factory_pg.py` control-plane, two test files, and five project-local docs; no deploy, credential change, direct SQL, connector/messaging action, or trading/risk/paper/live action.
- Factory DB evidence: gate `804` recorded `quality passed` for task `zeus-alpha-research-ledger-core-r2v-canonical-g1-status-and-no-auto-merg`, reviewer `quality-reviewer`.
- Non-blocking observations (no rework required): (1) no dedicated behavioral test for an entirely missing/unreadable configured base ref — the fail-closed path is covered by code inspection (`_configured_base_ref_readback` returns `accepted=false` for `repo_path_missing`/`repo_path_unreadable`/`base_ref_unavailable`) and the missing-index case is behaviorally tested; (2) `_git_file_text_at_ref` uses a 10s subprocess timeout per document (worst case ~22 docs sequential) — acceptable for a control-plane status call.
- Verdict: **PASS** — implementation head approved for R2v task closure from the quality perspective.

## R2w reviewed-frontmatter PR recovery gate
- R2w must remain documentation/review-evidence only under `factory/projects/zeus-alpha-research-ledger-core/`; no runtime/source implementation, deploy, credential, connector, messaging, direct SQL, or trading/risk/paper/live action is authorized.
- Required local evidence: `git diff --check`, scoped diff path verification, tracked-document verification, and approved Factory status CLI read-back showing zero G1 required-document blockers on configured base ref `origin/main` at `df79aac9d306c0b055fe88dbde5ebd54d9635e36`.
- Delivery evidence must be PR-first: actual GitHub PR against `main`, Zeus signature, `agent:zeus` label, exact candidate SHA named in the PR body, and independent exact-SHA `quality-reviewer` verification before task closure. This worker must not merge the PR.

## R2ah current-origin reviewed-marker/index repair gate
- R2ah must remain documentation/review-evidence only under `factory/projects/zeus-alpha-research-ledger-core/`; no runtime/source implementation, deploy, credential, connector, messaging, direct SQL, or trading/risk/paper/live action is authorized.
- Required local evidence: fresh worktree identity captured before edits, `git diff --check`, scoped diff path verification, tracked-document verification, and approved Factory status CLI read-back showing all 14 G1 required documents exist, are committed, indexed, validated, reviewed, and non-blocking on configured base ref `origin/main` at `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7`.
- Delivery evidence must be PR-first: actual non-draft GitHub PR against `main`, Zeus signature, `agent:zeus` label, exact candidate SHA named in the PR body/docs, and independent exact-SHA `quality-reviewer` verification before task closure. This worker must not self-approve or merge the PR.

## R2c2 autonomous canonical G1 document-status repair gate
- R2c2 must remain documentation/review-evidence only under `factory/projects/zeus-alpha-research-ledger-core/`; no runtime/source implementation, deploy, credential, connector, messaging, direct SQL, or trading/risk/paper/live action is authorized.
- Required local evidence: fresh worktree identity captured before edits, `git diff --check`, scoped diff path verification, tracked-document verification, and approved Factory status CLI read-back showing all 14 G1 required documents exist, are committed, indexed, validated, reviewed, and non-blocking on configured base ref `origin/main` at `dbde1790f8d45f111bc69b3491a1862eafb29fa2`.
- Delivery evidence must be PR-first: actual non-draft GitHub PR against `main`, Zeus signature, `agent:zeus` label, exact candidate SHA named in the PR body/Factory evidence, and independent exact-SHA `quality-reviewer` verification before task closure. This worker must not self-approve or merge the PR.

## R2c3 current-origin G1 visibility and reconciliation repair gate
- R2c3 must remain documentation/review-evidence only under `factory/projects/zeus-alpha-research-ledger-core/`; no runtime/source implementation, deploy, credential, connector, messaging, direct SQL, direct Factory metadata mutation, or trading/risk/paper/live action is authorized.
- Required RED evidence: canonical Factory status read-back from the stale primary checkout records the exact 10 required-document blockers with `reviewed=false`, names primary HEAD `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`, current `origin/main` `2a32066398d500d6dac071bd7f2184d47bb3bcb4`, and stale inc-011 / PR #20 metadata as historical-only mismatch evidence.
- Required GREEN evidence: fresh R2c3 worktree identity captured before edits, `git diff --check`, scoped diff path verification, tracked-document verification, and approved Factory status CLI read-back from the current-origin worktree showing all 14 G1 required documents exist, are committed, indexed, validated, reviewed, and non-blocking on configured base ref `origin/main` at `2a32066398d500d6dac071bd7f2184d47bb3bcb4`.
- Delivery evidence must be PR-first: actual non-draft GitHub PR against `main`, Zeus signature, `agent:zeus` label, exact base/head SHAs named in the PR body/Factory evidence, and independent exact-SHA `quality-reviewer` verification before task closure. This worker must not self-approve or merge the PR.

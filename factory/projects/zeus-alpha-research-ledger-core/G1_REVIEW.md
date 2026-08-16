---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: pending
---

# G1 REVIEW RECORD

## Review round 1 — remediated
Independent specification and security reviews required traceability, Factory DB task reconciliation, bounded local collection, removal of collaboration messages, least privilege, DB invariants, typed non-advice state, no-egress proof and disabled scheduler. The first remediation commit `743f4c404` addressed the architecture direction but was not sufficiently exact.

## Review round 2 — security rework incorporated
The second security review returned `REQUEST_CHANGES` because the initial remediation still lacked exact object grants, enum/predicate definitions, carrier-wide typed fields, executable no-egress harness and durable scheduler configuration/readiness state.

This revision adds `DATABASE_AND_RUNTIME_CONTRACT.md`, which now fixes:
- role attributes, per-object operations, function allowlist, `PUBLIC` revocations/default privileges and named direct SQL denials;
- exact source/terms/freshness enums, stale predicate, time/duplicate/supersession/lineage negatives;
- typed fields/defaults/checks/immutability and exact JSON field rejection for cards, reviews and handoffs;
- scanned path/banned-pattern list plus every-handler/scheduler interception harness and local DSN-only check;
- default-false config, readiness-table fields/components, no-cache verifier and all false-path scheduler tests.

## Review round 3 — independent second-pass REQUEST_CHANGES (Gates 686 and 687)

**Candidate provenance reviewed:** committed SHA `29cedbff5dedc13683a03bf32a178711af910eca` (`docs(factory): make alpha research safety contracts executable`) **plus the then-existing uncommitted dirty revision of** `DATABASE_AND_RUNTIME_CONTRACT.md`. The dirty revision is part of the effective review candidate but is not a committed SHA; neither it nor the historical merge base is asserted to be current canonical base.

Read-back source: `hermes factory status zeus-alpha-research-ledger-core --json` from Agent Core Postgres (`db_backend=agent_core_postgres`, `database=zeus_agent`). The real failed gate notes were:

- Gate **686**, `gate_type=spec`, `status=failed`, reviewer `independent-local-spec-review`, timestamp `2026-08-10T07:18:31.071405+00:00`: “Read-only second-pass review of 29cedbff5dedc13683a03bf32a178711af910eca plus the dirty DATABASE_AND_RUNTIME_CONTRACT.md returned REQUEST_CHANGES: exact handler names conflict; transition function/grants conflict; ALR-020 bounded-session acceptance conflicts with the stated scope; current-origin statements are stale. No source, PR, test, or merge evidence claimed.”
- Gate **687**, `gate_type=security`, `status=failed`, reviewer `independent-local-security-review`, timestamp `2026-08-10T07:18:33.063457+00:00`: “Read-only second-pass review of 29cedbff5dedc13683a03bf32a178711af910eca plus the dirty DATABASE_AND_RUNTIME_CONTRACT.md returned REQUEST_CHANGES: reconcile exact tool allowlist; fully type card/handoff schemas; add enforceable secret non-disclosure tests; cover all ALR changed files in no-egress scan; specify secure transition functions; persist immutable source/terms provenance. No source, PR, test, or merge evidence claimed.”

This R1 documentary candidate resolves those bounded findings by requiring: (1) one canonical leaf allowlist using `program_create` and `source_submit`, with named synonym/alias rejection; (2) complete safe-elevation semantics for both lifecycle functions, including owner, `SECURITY DEFINER`, fixed search path, `session_user` authorization, exact edges/columns, grants and catalog/negative proof; (3) deterministic ALR-020 Factory metadata reconciliation because its recorded bounded-local-sessions acceptance conflicts with v1's session/message exclusion; (4) removal of stale “current origin/main” claims in favor of historical-base evidence plus pre-PR revalidation; (5) exact typed/bounded `alpha_card_create`, fixed `handoff_list` objects, and unambiguous envelope/payload key counts with prohibited/unknown-field checks; (6) generic reference-only secret non-disclosure/redaction plus persisted/output/log/error/trace/metric/scheduler negative tests using synthetic canaries only; (7) static no-egress coverage for every ALR-added/modified implementation diff line, including replacement sides of modified lines and unscannable-file failures; and (8) immutable source/terms reference persistence with auditable admin approval/revision provenance and direct SQL/handler tests.

This bounded documentary rework addresses those records only. A revised **committed** candidate must receive new, independent specification and security reviews against its exact SHA. No R1 review is PASS, no G1 frontmatter may become reviewed yes, and no implementation, Factory metadata change, PR, merge, deploy, or normal task dispatch is authorized by this record.

## Review round 4 — merge-policy REQUEST_CHANGES (Gate 695)

**Candidate reviewed:** committed SHA `b9396bcd7d14ee6f212bd0fd0609e468cecf567f` (`docs(factory): resolve ALR G1 second-pass findings`).

Read-back source: `hermes factory status zeus-alpha-research-ledger-core --json` from Agent Core Postgres (`db_backend=agent_core_postgres`, `database=zeus_agent`) plus local Git inspection. The real failed gate note was:

- Gate **695**, `gate_type=spec`, `status=failed`, reviewer `solution-architect`, timestamp `2026-08-10T09:31:33.359633+00:00`: “Review of SHA b9396bcd7: documentary content resolves the bounded Gate 686/687 specification/security findings, but task cannot close because live Factory/Git evidence contradicts the no-merge/PR-first contract. Agent Core Postgres status recorded event 173433 increment_integrated with method merge_no_ff_push_origin for this task, and git shows origin/main at e3d04ff94 is a merge commit with parent b9396bcd7. Rework: reconcile/revert/record authorized handling of the unexpected base-branch merge and update G1_REVIEW/TRACKER/TASK_GRAPH with actual merge evidence before closure; no downstream implementation dispatch until independent reviews inspect exact corrected SHA.”

This R2 correction records the merge fact instead of preserving stale branch-only/no-merge statements: Factory event `173433` integrated branch commit `b9396bcd7d14ee6f212bd0fd0609e468cecf567f` into base `main` using `merge_no_ff_push_origin`, producing `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a`. Git confirms `e3d04ff94` has parents `00e7bb4ab` and `b9396bcd7`, and `b9396bcd7` is an ancestor of `origin/main`.

The correction does **not** claim that the merge was authorized, does not revert it, does not open a PR, does not perform a new merge/deploy, and does not convert any R1/G1 review to PASS. It only reconciles documentation with the Agent Core/Git source of truth so independent reviewers can inspect the exact corrected SHA.

## Review round 5 — R2j canonical-state evidence repair

**Mismatch reproduced:** R2i's independent quality/security review gates cite the actual still-open Zeus-signed PR #29 candidate at `f61a7275048e2135b2b2729a1b9cdf8713c58866` against canonical `main` `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c`, but their attached Factory increment-integration evidence records `increment_integration_method=already_ancestor` for the R2i review branch at `increment_branch_commit=5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c`.

**Correction:** that `already_ancestor` attachment is review-worktree provenance only. It proves the review branch/check-out was already at canonical `main`; it does not prove PR #29 was merged, visible on `main`, or accepted by QA Guardian. The source candidate remains PR #29 head `f61a7275048e2135b2b2729a1b9cdf8713c58866` until the PR-first / QA Guardian path records candidate-bound delivery evidence.

`R2J_CANONICAL_STATE_REPAIR.md` is now the controlling project-local handoff artifact for this mismatch. It names PR #29, its exact head, canonical `main`, the current Factory `document_status` blocker set, the R2i provenance root cause, and the candidate-bound QA Guardian evidence that must be used for any future terminal delivery decision. This R2j repair performs no merge, deployment, credential change, direct SQL, product implementation, external-runtime operation, or `reviewed: yes` conversion.

## Review round 6 — R2k stale canonical provenance repair

**Mismatch reproduced:** live Agent Core project metadata still names `metadata.g1_documentation_checkout` as PR #20 / `dad375f27568c38be771fc597b579d087f034e1d`, while R2j was subsequently delivered through PR #30 at head `c1943efb2b97b54b42bc5eabe858340d8c391116` and remote `origin/main` now reads `83d5ee06ba25859f047469baed223fe88e9467e3`. The local primary `main` ref remains `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1` and does not contain `c1943efb2b97b54b42bc5eabe858340d8c391116` by `git merge-base --is-ancestor ... main` exit `1`.

**Current blocker:** Agent Core `factory status` still reports `unvalidated_required_docs` and `document_status` read-back from the primary source has required G1 documents at `reviewed=false`; this R2k worker does not convert them to `reviewed: yes`.

**Correction:** `R2K_STALE_CANONICAL_G1_PROVENANCE_REPAIR.md` is now the controlling renewal handoff artifact. It explicitly rejects PR #20/dad375f and stale review-worktree attachments as active review provenance, records PR #30/c1943 as historical R2j evidence, and instructs independent reviewers to review the exact head SHA of the R2k Zeus-signed `agent:zeus` PR.

This is implementation/documentation evidence only. It performs no merge, deployment, credential change, direct SQL, product implementation, external-runtime operation, or `reviewed: yes` conversion. No normal ALR-020 work may dispatch until the exact R2k candidate is independently reviewed and canonical Factory metadata/document status are reconciled.

## Review round 7 — R2m current-base exact-SHA handoff

**Current-base recovery:** R2m fetched canonical `origin/main` and recorded exact base `ab08b13669903a87b3d60d6c80231d23d6313782`. The assigned branch/worktree `factory/zeus-alpha-research-ledger-core/inc-001-r2m-current-base-g1-documentatio` was initially equal to that base, then received only project-local documentation updates for current-base review handoff.

**Incorporated repairs:** `R2J_CANONICAL_STATE_REPAIR.md` and `R2K_STALE_CANONICAL_G1_PROVENANCE_REPAIR.md` remain indexed controlling artifacts. PR #20/dad375f, historical PR #29/f61a PASS reviews, R2i review-worktree `already_ancestor` evidence, PR #30/c1943 and PR #31/73b are not active approval or implementation-dispatch evidence.

**Handoff at that time:** the fresh R2m Zeus-signed `agent:zeus` PR was the next review target. R2n, R2o and R2q supersede that active target; R2m remains historical current-base recovery evidence only.

## Review round 8 — R2n exact-SHA quality PASS (Gate 789)

**Reviewed candidate:** PR #33 head `1e82340dddf52071d14c3c7a00b04b3c17ee2821` on base `df4c77fd1413a65cdb85885a06978ff157c1de4d`, branch `factory/zeus-alpha-research-ledger-core/inc-034-r2n-repair-g1-canonical-document`, label `agent:zeus`, not merged at the time of review.

**Independent evidence:** Gate **789**, `gate_type=quality`, `status=passed`, reviewer `quality-reviewer`, timestamp `2026-08-15T22:59:08.821504+00:00`. The gate note recorded a PASS against exact PR #33 SHA, strict primary read-back (`blocking_count=14`, `reviewed=false`, readiness source `primary`) and the need for authorized metadata reconciliation before dispatch.

**Interpretation:** gate 789 is valid source-document review evidence for a reviewed candidate. It is not primary-readiness evidence because PR #33 was open/not merged and Agent Core still read primary source plus stale metadata.

## Review round 9 — R2o reviewed-marker candidate PASS (Gate 790)

**Reviewed candidate:** PR #34 head `2476e978c545e24b18ee48844b24eb8c58245ab4` on base `df4c77fd1413a65cdb85885a06978ff157c1de4d`, branch `factory/zeus-alpha-research-ledger-core/inc-024-r2o-reconciliation-apply-indepen`, label `agent:zeus`, not merged at the time of review.

**Independent evidence:** Factory gate **790**, `gate_type=quality`, `status=passed`, reviewer `quality-reviewer`. PR #34 comment evidence records that the review verified docs-only scope, the 14 required G1 documents carrying candidate-level reviewed markers backed by gate 789 / PR #33 SHA `1e82340dddf52071d14c3c7a00b04b3c17ee2821`, and the candidate-readiness versus primary-readiness separation.

**Interpretation for R2q:** gate 790 is the latest valid reviewed-docs candidate evidence. It supports candidate-level `reviewed: yes` markers tied to PR #34 exact SHA `2476e978c545e24b18ee48844b24eb8c58245ab4`. It does not authorize dispatch without canonical Factory read-back or an authorized reviewed-candidate path.

## Review round 10 — R2p invalid provider-failed review

**R2p candidate:** PR #35 head `ef23a73b39057bb07c1f86f21b6cb7f97e43fe62` on base `df4c77fd1413a65cdb85885a06978ff157c1de4d`, branch `factory/zeus-alpha-research-ledger-core/inc-001-r2p-repair-canonical-reviewed-g1`, label `agent:zeus`.

**Invalid review run:** quality-reviewer run `run-1786840866-90f55f9d` did not execute a review. Worker log lines 365–408 show MiniMax OAuth HTTP 429 on all three attempts, a final provider failure, and `Messages: 1 (1 user, 0 tool calls)`. The exit-code file contains `0`, but this is not a semantic PASS because no reviewer inspected files, diffs, commands, evidence or acceptance criteria.

**Interpretation:** R2p must remain blocked/retriable for review purposes. Provider failure and zero tool calls must never be recorded as completion evidence.

## Review round 11 — R2q current-main recovery handoff

**Recovery base:** R2q starts from `origin/main` `df4c77fd1413a65cdb85885a06978ff157c1de4d` in branch `factory/zeus-alpha-research-ledger-core/inc-035-r2q-g1-review-candidate-recovery` and restores a docs-only reviewed-G1 candidate using PR #34/gate-790 provenance.

**Required next review:** the final R2q PR head SHA must be cited by an independent `solution-architect` review that actually executes. The review evidence must show tool/file/diff/command work and must explicitly reject R2p `run-1786840866-90f55f9d` as invalid completion evidence. If the provider fails or the review has zero tool calls, the result remains BLOCKED/retriable.

## Review round 12 — R2r PR-first recovery of R2q candidate

**Source candidate recovered:** R2q commit `11639ab1650a4d7abfa88820bc266c983a56d1fd` on parent/base `df4c77fd1413a65cdb85885a06978ff157c1de4d` is documentation-only and restores the reviewed-docs candidate using PR #34/gate-790 provenance.

**Provenance defect repaired:** the R2q source commit was authored/committed by `sitiouno <7621230+sitiouno@users.noreply.github.com>`, had no `Signed-off-by` trailer and no open GitHub PR. R2r therefore produces a replacement commit from branch `factory/zeus-alpha-research-ledger-core/inc-001-r2r-pr-first-recovery-of-the-r2q` with Zeus author/sign-off, push, open `agent:zeus` PR and exact-head solution-architect review.

**Required next review:** the final R2r PR head SHA must be cited by an independent `solution-architect` review that actually executes. The review evidence must show tool/file/diff/command work, confirm docs-only/no-runtime scope, reject R2p `run-1786840866-90f55f9d` as invalid completion evidence, and verify the open PR head equals the reviewed SHA.

## Local documentary verification — non-approval

At `2026-08-10T04:50:09-04:00`, the implementation-planner worker verified the project-local pack from the assigned worktree only. `git ls-files --error-unmatch` confirmed the 14 required G1 documents plus `G0_REPOSITORY_STRATEGY.md`, `REQUIREMENTS_TRACEABILITY.md`, `DATABASE_AND_RUNTIME_CONTRACT.md`, and `G1_REVIEW.md` are tracked. `DOCUMENTATION_INDEX.md` indexes required documents and records explicit validated/reviewed status. `G0_REPOSITORY_STRATEGY.md` records the Zeus-only source repo, `origin/main` reference, assigned branch/worktree policy, PR-first delivery, and predecessor linkage. This is implementation evidence, not an independent specification/security PASS.

## Status
Required G1 frontmatter/index markers are candidate-reviewed, not primary-ready. The support evidence is gate 790 by `quality-reviewer` against PR #34 exact SHA `2476e978c545e24b18ee48844b24eb8c58245ab4`, with source-document review gate 789 against PR #33 exact SHA `1e82340dddf52071d14c3c7a00b04b3c17ee2821`. Downstream implementation remains blocked until the R2r replacement branch is pushed through a Zeus-signed `agent:zeus` PR, independently reviewed by `solution-architect` against its final open-PR head SHA with real executed-review evidence, and Agent Core `document_status` or an authorized reviewed-candidate metadata path reads back zero required G1 blockers. This record performs no merge, deployment, credential change, direct SQL, product implementation or external-runtime operation.

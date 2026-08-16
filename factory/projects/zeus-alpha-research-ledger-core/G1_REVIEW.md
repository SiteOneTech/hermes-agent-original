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

**Handoff:** the fresh R2m Zeus-signed `agent:zeus` PR was the next review target at that time. R2m left `reviewed: pending` intact and performed no merge, deployment, credential change, direct SQL, product implementation or external-runtime operation.

## Review round 8 — R2u canonical G1 document-status preflight repair

**Current-base reproduction:** R2u starts from current `origin/main` / branch base `df4c77fd1413a65cdb85885a06978ff157c1de4d`. Canonical Factory status read-back in this run reproduced the active `unvalidated_required_docs` failure: the primary repository documentation pack was present/indexed/committed/validated but not machine-read as reviewed.

**Independent review source:** the reviewed G1 pack is bound to the Zeus-signed PR-first candidate PR #36 at exact head `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`, reviewed by `solution-architect` in Factory gate `794`. The reviewed-docs source evidence retained by that candidate is gate `790` / PR #34 SHA `2476e978c545e24b18ee48844b24eb8c58245ab4`.

**Correction:** R2u converts the required G1 document frontmatter and `DOCUMENTATION_INDEX.md` matrix from `reviewed: pending` to `reviewed: yes` with explicit PR/gate/SHA provenance, and records the docs-first repair in `R2U_CANONICAL_G1_DOCUMENT_STATUS_PREFLIGHT_REPAIR.md`. This repairs only documentation/index/traceability state. It does not import the R2s control-plane code path, merge `main`, deploy, change credentials, add connectors, enable messaging, authorize trading/risk/paper/live behavior or dispatch product implementation.

## Review round 9 — R2w reviewed-frontmatter PR recovery

**Current status read-back:** R2w starts from current `origin/main` / worktree head `df79aac9d306c0b055fe88dbde5ebd54d9635e36`. Approved Agent Core Factory status CLI evidence (`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`) was captured in Hermes terminal output `out-1786856760-2035541-e390.log`. Its project `document_status` rows show configured base ref `origin/main`, base commit `df79aac9d306c0b055fe88dbde5ebd54d9635e36`, and `exists=true`, `committed=true`, `validated=true`, `indexed=true`, `reviewed=true`, `blocking=false` for all G1 required documents, including the 11 documents named in the R2w task.

**Correction:** `R2W_CANONICAL_G1_REVIEWED_FRONTMATTER_PR.md` records the PR-first recovery handoff for this canonical reviewed-frontmatter state. The R2w PR must remain Zeus-signed and labeled `agent:zeus`, must name the exact pushed candidate SHA, and must receive independent exact-SHA quality review before task closure. This round does not change runtime/source code, perform a merge, deploy, direct SQL, credential change, connector/messaging action, or trading/risk/paper/live behavior.

## Review round 10 — R2ah current-origin reviewed-marker/index repair

**Current-origin identity captured before edits:** R2ah fetched `origin/main` and verified the assigned branch/worktree before writing files. The worktree `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2ah-current-origin-g1-reviewed`, branch `factory/zeus-alpha-research-ledger-core/inc-019-r2ah-current-origin-g1-reviewed`, local `HEAD`, `origin/main`, and merge-base were all exactly `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7` before the first R2ah edit.

**Canonical Agent Core read-back:** the approved status command `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json` read Agent Core Postgres (`db_backend=agent_core_postgres`, `database=zeus_agent`) and wrote full evidence to `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786890230-1212346-8c10.log`. Project `document_status` lines 16292–16558 show configured base ref `origin/main`, base commit `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7`, `readiness_source=configured_base_ref`, and `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false` for all 14 G1 required documents.

**Correction:** `R2AH_CURRENT_ORIGIN_G1_REVIEWED_MARKER_REPAIR.md` now records the current-origin branch/worktree identity, the configured-base document-status read-back, and the PR-first handoff. `DOCUMENTATION_INDEX.md` now names exact base `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7` for the current candidate state. The required G1 frontmatter reviewed markers remain machine-readable `reviewed: yes` and still cite their independent source review chain, PR #36 / gate `794` plus gate `790` / PR #34 source evidence.

**Handoff requirement:** the fresh R2ah branch is opened as non-draft Zeus-signed GitHub PR #47 (`https://github.com/SiteOneTech/hermes-agent-original/pull/47`) labeled `agent:zeus` against `main`. The PR body/Factory evidence must name the exact final head SHA after the last push. An independent reviewer must inspect that exact SHA; this R2ah worker does not self-approve, merge, deploy, change credentials, write direct SQL, or touch any runtime/external/trading path.

## Review round 11 — R2c2 autonomous canonical G1 document-status repair

**Current-base identity captured before edits:** R2c2 fetched `origin/main` and verified the assigned worktree before writing files. The worktree `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2c2-autonomous-canonical-g1-doc`, branch `factory/zeus-alpha-research-ledger-core/inc-018-r2c2-autonomous-canonical-g1-doc`, local `HEAD`, `origin/main`, and merge-base were all exactly `dbde1790f8d45f111bc69b3491a1862eafb29fa2` before the first R2c2 edit.

**Canonical Agent Core read-back:** the approved status command `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json` read Agent Core Postgres (`db_backend=agent_core_postgres`, `database=zeus_agent`) and wrote full evidence to `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786892903-1813387-f690.log`. Project `document_status` lines 16632–16898 show configured base ref `origin/main`, base commit `dbde1790f8d45f111bc69b3491a1862eafb29fa2`, `readiness_source=configured_base_ref`, and `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false` for all 14 G1 required documents. This resolves the current required-document status mismatch at the document-status row level while preserving stale reconciliation/event history as history only.

**Correction:** `R2C2_AUTONOMOUS_CANONICAL_G1_DOCUMENTATION_STATUS_REPAIR.md` now records the current-base branch/worktree identity, the configured-base document-status read-back, and the PR-first handoff. `DOCUMENTATION_INDEX.md` now names exact base `dbde1790f8d45f111bc69b3491a1862eafb29fa2` for the current candidate state. The required G1 frontmatter reviewed markers remain machine-readable `reviewed: yes` and still cite their independent source review chain, PR #36 / gate `794` plus gate `790` / PR #34 source evidence.

**Handoff requirement:** the fresh R2c2 branch is opened as non-draft Zeus-signed GitHub PR #48 (`https://github.com/SiteOneTech/hermes-agent-original/pull/48`) labeled `agent:zeus` against `main`. The PR body/Factory evidence must name the exact final head SHA after the last push. An independent reviewer must inspect that exact SHA; this R2c2 worker does not self-approve, merge, deploy, change credentials, write direct SQL, or touch any runtime/external/trading path.

## Review round 12 — R2c3 current-origin G1 visibility and reconciliation repair

**Current-origin identity captured before edits:** R2c3 fetched `origin/main` and verified the assigned worktree before writing files. The worktree `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2c3-current-origin-g1-visibility`, branch `factory/zeus-alpha-research-ledger-core/inc-019-r2c3-current-origin-g1-visibility`, local `HEAD`, `origin/main`, and merge-base were all exactly `2a32066398d500d6dac071bd7f2184d47bb3bcb4` before the first R2c3 edit.

**RED read-back / root cause:** the canonical status command run from stale primary checkout `/home/jean/Projects/hermes-agent-original` produced `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786895716-2463118-ae50.log`. That environment had primary `main` at `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`, `origin/main` at `2a32066398d500d6dac071bd7f2184d47bb3bcb4`, and `git rev-list --left-right --count HEAD...origin/main` equal to `3\t1365`. Project `document_status` lines 17038–17233 in the log showed exactly 10 required-document blockers with `reviewed=false`: `FACTORY_INTAKE.md`, `REQUIREMENTS_ANALYSIS.md`, `PATTERN_ANALYSIS.md`, `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, `PRD.md`, `ADRS.md`, `METHODOLOGY_PLAN.md`, `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`, and `SECURITY_GATES.md`. The same status payload retains stale `metadata.g1_documentation_checkout` pointing to inc-011 / PR #20 at `dad375f27568c38be771fc597b579d087f034e1d`. This is diagnostic stale-checkout/provenance evidence only.

**GREEN current-origin read-back:** the same canonical venv command run from the assigned R2c3 worktree produced `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786895883-2463118-cd90.log`. Project `document_status` lines 17046–17312 show `base_ref=origin/main`, `base_commit=2a32066398d500d6dac071bd7f2184d47bb3bcb4`, `configured_base_ref_accepted=true`, `readiness_source=configured_base_ref`, and `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false` for all 14 G1 required documents.

**Correction:** `R2C3_CURRENT_ORIGIN_G1_VISIBILITY_AND_RECONCILIATION_REPAIR.md` now records the current-origin branch/worktree identity, the stale-primary RED reason, the configured-base GREEN read-back, and the PR-first handoff. `DOCUMENTATION_INDEX.md` now names exact base `2a32066398d500d6dac071bd7f2184d47bb3bcb4` for the current candidate state. The required G1 frontmatter reviewed markers remain machine-readable `reviewed: yes` and still cite their independent source review chain, PR #36 / gate `794` plus gate `790` / PR #34 source evidence.

**Handoff requirement:** the fresh R2c3 branch is opened as non-draft Zeus-signed GitHub PR #49 (`https://github.com/SiteOneTech/hermes-agent-original/pull/49`) labeled `agent:zeus` against `main`. The PR body/Factory evidence must name the exact final head SHA after the last push. An independent reviewer must inspect that exact SHA; this R2c3 worker does not self-approve, merge, deploy, change credentials, write direct SQL, mutate Factory metadata directly, or touch any runtime/external/trading path.

## Local documentary verification — non-approval

At `2026-08-10T04:50:09-04:00`, the implementation-planner worker verified the project-local pack from the assigned worktree only. `git ls-files --error-unmatch` confirmed the 14 required G1 documents plus `G0_REPOSITORY_STRATEGY.md`, `REQUIREMENTS_TRACEABILITY.md`, `DATABASE_AND_RUNTIME_CONTRACT.md`, and `G1_REVIEW.md` are tracked. `DOCUMENTATION_INDEX.md` indexes required documents and records explicit validated/reviewed status. `G0_REPOSITORY_STRATEGY.md` records the Zeus-only source repo, `origin/main` reference, assigned branch/worktree policy, PR-first delivery, and predecessor linkage. This is implementation evidence, not an independent specification/security PASS.

## Status
The required G1 pack is now documented as `reviewed: yes` for the R2u candidate using the independent PR #36/gate 794 review chain. This is documentation readiness only: downstream ALR-020+ work remains subject to its own task-specific RED→GREEN, security/no-egress, PR-first delivery and QA gates, and no runtime/product authority is granted by this record.

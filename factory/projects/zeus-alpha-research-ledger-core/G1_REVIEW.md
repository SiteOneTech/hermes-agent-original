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

## Local documentary verification — non-approval

At `2026-08-10T04:50:09-04:00`, the implementation-planner worker verified the project-local pack from the assigned worktree only. `git ls-files --error-unmatch` confirmed the 14 required G1 documents plus `G0_REPOSITORY_STRATEGY.md`, `REQUIREMENTS_TRACEABILITY.md`, `DATABASE_AND_RUNTIME_CONTRACT.md`, and `G1_REVIEW.md` are tracked. `DOCUMENTATION_INDEX.md` indexes required documents and records explicit validated/reviewed status. `G0_REPOSITORY_STRATEGY.md` records the Zeus-only source repo, `origin/main` reference, assigned branch/worktree policy, PR-first delivery, and predecessor linkage. This is implementation evidence, not an independent specification/security PASS.

## Status
This is still a remediation record, not approval. After this revision is committed, obtain new independent specification and security reviews against that exact committed SHA, including the gate-695 merge reconciliation. Only then may their independent PASS results support changing required G1 frontmatter/index to `reviewed: yes` and unblocking downstream implementation according to the reconciled delivery policy. Until then, `reviewed: pending` remains binding.

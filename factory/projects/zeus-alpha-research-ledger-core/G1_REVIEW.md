---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: yes
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

The R1 correction recorded the first merge fact instead of preserving stale branch-only/no-merge statements: Factory event `173433` integrated branch commit `b9396bcd7d14ee6f212bd0fd0609e468cecf567f` into base `main` using `merge_no_ff_push_origin`, producing `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a`. Git confirms `e3d04ff94` has parents `00e7bb4ab0fcd9013ffa924ce6c5a8ae2c2ae2fc` and `b9396bcd7d14ee6f212bd0fd0609e468cecf567f`, and `b9396bcd7d14ee6f212bd0fd0609e468cecf567f` is an ancestor of `origin/main`.

## Review round 5 — PR-first/direct-integration REQUEST_CHANGES (Gate 697)

**Candidate reviewed:** committed SHA `6ee8b4fdb886d0834bfbc62c7e152ee35d505e66` (`docs(factory): reconcile ALR direct merge evidence`).

Read-back source: `hermes factory status zeus-alpha-research-ledger-core --json` from Agent Core Postgres (`db_backend=agent_core_postgres`, `database=zeus_agent`) plus local Git inspection. The real failed gate note was:

- Gate **697**, `gate_type=spec`, `status=failed`, reviewer `solution-architect`, timestamp `2026-08-10T09:53:47.41439+00:00`: “Review of SHA 6ee8b4fdb886d0834bfbc62c7e152ee35d505e66: bounded Gate 686/687 contract content is materially present, and tracked docs/diff checks pass, but task cannot close because the R2 correction was again integrated directly into origin/main. Agent Core Postgres event 173494 records merge_no_ff_push_origin of 6ee8b4fdb to base 9f975acb; local git shows origin/main=9f975acb with parents e3d04ff94 and 6ee8b4fdb, ancestor check exit 0. Current docs only record prior event 173433/b9396/e3d04 and still state this task performs no new merge/no new merge-deploy, so G1_REVIEW/G0/TASK_GRAPH/TRACKER/METHODOLOGY are stale against source of truth. Rework: record event 173494/9f975 evidence, remove false no-new-merge statements or explain authorized handling, keep reviewed=pending/no downstream ALR-020 authority, then obtain independent exact-SHA spec/security reviews.”

This R2 correction records both merge facts instead of preserving stale branch-only/no-new-merge statements: Factory event `173433` integrated branch commit `b9396bcd7d14ee6f212bd0fd0609e468cecf567f` into base `main`, producing `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a`; Factory event `173494` integrated branch commit `6ee8b4fdb886d0834bfbc62c7e152ee35d505e66` into base `main`, producing `9f975acb0625750b8d46648766d1395c89392dca`. Git confirms `9f975acb` has parents `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a` and `6ee8b4fdb886d0834bfbc62c7e152ee35d505e66`; both `b9396bcd7d14ee6f212bd0fd0609e468cecf567f` and `6ee8b4fdb886d0834bfbc62c7e152ee35d505e66` are ancestors of `origin/main`.

The correction does **not** claim that either direct merge was authorized, does not revert history, does not perform another base merge/deploy, and does not convert any R1/G1 review to PASS. This R2 task must create a fresh branch-only candidate commit and make it visible through a Zeus-signed GitHub PR labeled `agent:zeus`; independent specification and security reviewers must inspect that exact revised SHA before any `reviewed: yes`, QA Guardian handoff, or ALR-020 dispatch authority exists.

## Local documentary verification — non-approval

At `2026-08-10T04:50:09-04:00`, the implementation-planner worker verified the project-local pack from the assigned worktree only. `git ls-files --error-unmatch` confirmed the 14 required G1 documents plus `G0_REPOSITORY_STRATEGY.md`, `REQUIREMENTS_TRACEABILITY.md`, `DATABASE_AND_RUNTIME_CONTRACT.md`, and `G1_REVIEW.md` are tracked. R2 must rerun tracked-document verification, `git diff --check`, and stale-claim scans after this edit and before the fresh candidate commit. This is implementation evidence, not an independent specification/security PASS.

## Review round 6 — exact-SHA independent PASS evidence

**Substantive candidate reviewed:** committed SHA `dad375f27568c38be771fc597b579d087f034e1d` (`docs(factory): reconcile ALR PR-first merge evidence`), visible on open, non-draft GitHub PR [#20](https://github.com/SiteOneTech/hermes-agent-original/pull/20) from `factory/zeus-alpha-research-ledger-core/inc-011-alr-010-r2-pr-first-g1-reconciliation` to `main`, labeled `agent:zeus` with the recorded Zeus sign-off.

- Factory gate **699**, `gate_type=spec`, `status=passed`, reviewer `solution-architect`, independently reviewed this exact SHA and its Gate-695/Gate-697 reconciliation.
- Factory gates **706** and **707**, `gate_type=security`, `status=passed`, independently reviewed this exact SHA, its project-local diff, no-egress/no-authority boundaries, and the fact that the prior direct integrations are audit evidence only.

The frontmatter/index marker transition in this commit is a deterministic record of those completed gates, not a self-review and not a claim that the post-review metadata-only commit was itself independently reviewed. It does not grant QA Guardian approval, merge/deploy authority, external-runtime authority, or any exception to downstream per-increment TDD, independent review and PR-first requirements.

## Review round 7 — independent quality REQUEST_CHANGES (Gate 708)

**Candidate reviewed:** committed SHA `0d57631de23f84db3135764bea538fa349dc7462` (`docs(factory): record ALR G1 review readiness`). The independent read-only documentation review inspected this exact SHA, confirmed its diff is restricted to 18 project-local Factory documents and that `git diff --check` is clean, but returned `REQUEST_CHANGES` at Factory quality gate **708**.

The concrete findings were that `TRACKER.md` still stated that exact-SHA reviews and PR work were pending while the markers had been changed to `reviewed: yes`, and that `TASK_GRAPH.md` retained an unresolved ALR-020 bounded-local-sessions acceptance conflict without Factory DB read-back evidence. This is not QA Guardian approval, merge/deploy authority, or ALR-020 authority.

The bounded same-project repair is Factory event **174440** at `2026-08-10T16:32:37.76002+00:00`: it changed the ALR-020 acceptance criterion from the old `bounded local sessions` literal to the exact session/message-excluded, scheduler-readiness and non-session local-intake statement, and the Agent Core read-back proved the old literal absent and the new literal present. That event is project-local task metadata only; it changes no source/runtime file and does not itself satisfy the required independent review of the next documentation SHA.

## Review round 8 — corrected exact-SHA independent PASS evidence

**Corrected substantive candidate reviewed:** committed SHA `3e6c14f8aa368ec6e3623d16640bf4b558ce0c7a` (`docs(factory): reconcile ALR G1 review rework`), visible on open, non-draft GitHub PR #20 from the existing Zeus-signed, `agent:zeus` branch to `main`.

- Factory gate **709**, `gate_type=spec`, `status=passed`, independently reviewed the corrected tracker/task graph/index/G1 evidence.
- Factory gate **710**, `gate_type=security`, `status=passed`, independently reviewed the no-egress/no-authority boundary and the fact that event 174440 is task metadata only.
- Factory gate **711**, `gate_type=quality`, `status=passed`, independently verified the concrete gate-708 rework, exact ALR-020 read-back, clean Markdown-only diff, and retained `reviewed: pending` state of candidate `3e6c14f8aa368ec6e3623d16640bf4b558ce0c7a`.

The frontmatter/index marker transition in this commit records those completed gates. It is not a self-review and does not claim QA Guardian approval, merge/deploy authority, external-runtime authority, or any exception to downstream per-increment TDD, independent review and PR-first requirements.

## Status
The G1 pack is validated and reviewed on corrected substantive candidate `3e6c14f8aa368ec6e3623d16640bf4b558ce0c7a`, with PR #20 visibility and Factory gates 709/710/711. This resolves only the documentation-readiness condition. It does not close the project or waive source TDD, independent review, QA Guardian, local smoke, no-egress, PR or delivery requirements for ALR-020 through ALR-080.

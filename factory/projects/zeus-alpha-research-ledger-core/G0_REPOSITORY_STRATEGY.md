---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: pending
---

# G0 Repository Strategy

| Field | Decision |
|---|---|
| `repo_scope` | `zeus_only` |
| `work_intent` | `add_functionality` |
| `primary_repo` | `SiteOneTech/hermes-agent-original` |
| `primary_repo_remote` | `https://github.com/SiteOneTech/hermes-agent-original.git` (`origin`) |
| `primary_repo_path` | `/home/jean/Projects/hermes-agent-original` |
| `successor_project_path` | `factory/projects/zeus-alpha-research-ledger-core/` |
| `predecessor_project_id` | `zeus-independent-alpha-research` (documentation-only predecessor; no runtime module delivered) |
| `base_branch` | `origin/main` remains the canonical base. R2 read-only verification records that the prior ALR-010-R1 branch commit `b9396bcd7d14ee6f212bd0fd0609e468cecf567f` is already an ancestor of `origin/main` via merge commit `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a`; this is evidence to reconcile, not permission for another merge. |
| `last_verified_origin_main` | R2o starts from `origin/main` / PR #33 base `df4c77fd1413a65cdb85885a06978ff157c1de4d`. R2n independent quality gate 789 passed against PR #33 head `1e82340dddf52071d14c3c7a00b04b3c17ee2821`; R2o uses that exact candidate-review evidence to apply required G1 `reviewed: yes` markers. R2m base `ab08b13669903a87b3d60d6c80231d23d6313782`, R2k remote `83d5ee06ba25859f047469baed223fe88e9467e3`, and earlier `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a`/`00e7bb4ab0fcd9013ffa924ce6c5a8ae2c2ae2fc` evidence are historical only. |
| `r2o_candidate_marker_application` | Branch `factory/zeus-alpha-research-ledger-core/inc-024-r2o-reconciliation-apply-indepen` in worktree `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-024-r2o-reconciliation-apply-indepen`; documentation-only marker application using gate 789 / PR #33 SHA `1e82340dddf52071d14c3c7a00b04b3c17ee2821`; no merge/deploy/external runtime authority and no primary-readiness claim before canonical source reconciliation. |
| `historical_planning_base` | `20228c1167814f36d952999f2cafe8b3f6f9ba3c` was the ALR-010 planning-time `origin/main` reference only; do not treat it as current base |
| `branch_merge_base_at_alr010_verification` | `ed8dbe3bcf3a99fee48f24a5301240fb5282661e` was the local merge base observed during ALR-010 verification; PR/review must revalidate or update against then-current `origin/main` before QA Guardian merge |
| `deliverable_branch` | `factory/zeus-alpha-research-ledger-core/inc-010-alr-010-g1-rebaseline-and-local` |
| `deliverable_worktree` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-010-alr-010-g1-rebaseline-and-local` |
| `branch_policy` | `factory/zeus-alpha-research-ledger-core/<increment>`; one branch per deliverable |
| `worktree_policy` | one isolated worktree per increment below `/home/jean/Projects/.worktrees/` |
| `propagation` | none in v1; a future Vonash adapter/exchange is a separately approved project/increment |
| `runtime_impact` | local Zeus Agent Core only; never a Vonash deployment |
| `observed_increment_integration` | Agent Core Postgres event `173433` records `increment_integrated`, method `merge_no_ff_push_origin`, branch commit `b9396bcd7d14ee6f212bd0fd0609e468cecf567f`, base before `00e7bb4ab0fcd9013ffa924ce6c5a8ae2c2ae2fc`, base after `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a`, actor `implementation-planner`, at `2026-08-10T09:22:51.090409Z`. |
| `delivery` | Target policy remains signed, labeled GitHub PR → independent QA → QA Guardian merge decision. The observed ALR-010-R1 direct Factory integration is recorded as operational evidence and gate-695 rework context; it is not a PASS, PR, waiver, deploy authorization, or downstream implementation authority. |

## Rationale
The ledger is a local Agent Core module, so it belongs in the Zeus source repository rather than a new service, copied Vonash codebase, or data store. The existing shared Agent Core database is canonical for Zeus modules. The module must use its own schema and runtime role: it may share the database instance but not a broad credential or an external platform’s database.

## Successor and authority boundary

This project succeeds `zeus-independent-alpha-research` by creating the first **private local** research-ledger implementation contract. The predecessor remains the external/Vonash boundary study; it did not create local schema, tools, scheduler or runtime authority.

The v1 ledger stores local research provenance and inert handoffs only. It cannot write to Vonash/Magnus/VAOS/APC/KB/broker runtimes, cannot dispatch network messages, cannot trade, cannot change portfolio/risk state, and cannot mark research as approved strategy, paper/live activation, investment advice or operational instruction.

## PR-first Factory override
Jean explicitly requires source changes to reach QA Guardian through a Zeus-signed PR before any base-branch merge. Therefore every task in this project carries the Factory per-task `increment_integration_waived` metadata with `authorized_by=Jean García` and a recorded PR-first reason.

The live Factory/Git record diverged from that policy for ALR-010-R1: Agent Core Postgres event `173433` and `git show e3d04ff94b67e6e21be1d5515bdb71400fbedf0a` show that `b9396bcd7d14ee6f212bd0fd0609e468cecf567f` was merged directly into `origin/main`. This document records the merge fact so artifacts no longer claim a branch-only/no-merge state. It does **not** retroactively approve the merge, waive independent reviews, open a PR, deploy, or permit downstream ALR-020+ work; gate 695 remains the audit record requiring exact-SHA re-review after this correction.

R2k records a second provenance drift: project metadata still points to PR #20 / `dad375f27568c38be771fc597b579d087f034e1d` while R2j has already been delivered as PR #30 / `c1943efb2b97b54b42bc5eabe858340d8c391116`. R2m/R2n/R2o supersede that stale active pointer: gate 789 passed independent quality review for PR #33 exact SHA `1e82340dddf52071d14c3c7a00b04b3c17ee2821`, and R2o applies candidate-level required G1 `reviewed: yes` markers backed by that evidence. The marker application does **not** declare primary readiness; ALR-020+ remains blocked until canonical Factory `document_status` or an authorized reviewed-candidate metadata path reads back zero required G1 blockers.

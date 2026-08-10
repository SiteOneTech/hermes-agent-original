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
| `base_branch` | `origin/main` remains the canonical base. R2 read-only verification records that prior ALR-010-R1 branch commits `b9396bcd7d14ee6f212bd0fd0609e468cecf567f` and `6ee8b4fdb886d0834bfbc62c7e152ee35d505e66` are already ancestors of `origin/main` through direct Factory merge commits `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a` and `9f975acb0625750b8d46648766d1395c89392dca`; this is evidence to reconcile, not permission for another merge. |
| `last_verified_origin_main` | R2 local verification observed `origin/main` as `9f975acb0625750b8d46648766d1395c89392dca` (`Merge Factory increment zeus-alpha-research-ledger-core-alr-010-r1-bounded-g1-contract-rework into main`) with parents `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a` and `6ee8b4fdb886d0834bfbc62c7e152ee35d505e66`. Earlier `00e7bb4ab0fcd9013ffa924ce6c5a8ae2c2ae2fc` and `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a` base evidence is historical only. |
| `historical_planning_base` | `20228c1167814f36d952999f2cafe8b3f6f9ba3c` was the ALR-010 planning-time `origin/main` reference only; do not treat it as current base |
| `branch_merge_base_at_alr010_verification` | `ed8dbe3bcf3a99fee48f24a5301240fb5282661e` was the local merge base observed during ALR-010 verification; PR/review must revalidate or update against then-current `origin/main` before QA Guardian merge |
| `deliverable_branch` | `factory/zeus-alpha-research-ledger-core/inc-011-alr-010-r2-pr-first-g1-reconciliation` |
| `deliverable_worktree` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-011-alr-010-r2-pr-first-g1-reconciliation` |
| `branch_policy` | `factory/zeus-alpha-research-ledger-core/<increment>`; one branch per deliverable |
| `worktree_policy` | one isolated worktree per increment below `/home/jean/Projects/.worktrees/` |
| `propagation` | none in v1; a future Vonash adapter/exchange is a separately approved project/increment |
| `runtime_impact` | local Zeus Agent Core only; never a Vonash deployment |
| `observed_increment_integration` | Agent Core Postgres recorded two direct ALR-010-R1 integrations by `implementation-planner`, both using `merge_no_ff_push_origin`: event `173433` at `2026-08-10T09:22:51.090409Z` integrated branch commit `b9396bcd7d14ee6f212bd0fd0609e468cecf567f` from base `00e7bb4ab0fcd9013ffa924ce6c5a8ae2c2ae2fc` to merge `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a`; event `173494` at `2026-08-10T09:45:17.577998Z` integrated branch commit `6ee8b4fdb886d0834bfbc62c7e152ee35d505e66` from base `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a` to merge `9f975acb0625750b8d46648766d1395c89392dca`. |
| `delivery` | Target policy remains signed, labeled GitHub PR → independent exact-SHA reviews → QA Guardian merge decision. The observed ALR-010-R1 direct Factory integrations are recorded as operational evidence and gate-695/gate-697 rework context; they are not a PASS, PR, waiver, deploy authorization, `reviewed: yes` transition, or downstream implementation authority. |

## Rationale
The ledger is a local Agent Core module, so it belongs in the Zeus source repository rather than a new service, copied Vonash codebase, or data store. The existing shared Agent Core database is canonical for Zeus modules. The module must use its own schema and runtime role: it may share the database instance but not a broad credential or an external platform’s database.

## Successor and authority boundary

This project succeeds `zeus-independent-alpha-research` by creating the first **private local** research-ledger implementation contract. The predecessor remains the external/Vonash boundary study; it did not create local schema, tools, scheduler or runtime authority.

The v1 ledger stores local research provenance and inert handoffs only. It cannot write to Vonash/Magnus/VAOS/APC/KB/broker runtimes, cannot dispatch network messages, cannot trade, cannot change portfolio/risk state, and cannot mark research as approved strategy, paper/live activation, investment advice or operational instruction.

## PR-first Factory override
Jean explicitly requires source changes to reach QA Guardian through a Zeus-signed PR before any base-branch merge. Therefore every task in this project carries the Factory per-task `increment_integration_waived` metadata with `authorized_by=Jean García` and a recorded PR-first reason.

The live Factory/Git record diverged from that policy twice for ALR-010-R1: Agent Core Postgres event `173433` plus `git show e3d04ff94b67e6e21be1d5515bdb71400fbedf0a` show that `b9396bcd7d14ee6f212bd0fd0609e468cecf567f` was merged directly into `origin/main`; event `173494` plus `git show 9f975acb0625750b8d46648766d1395c89392dca` show that `6ee8b4fdb886d0834bfbc62c7e152ee35d505e66` was also merged directly into `origin/main`. This document records both merge facts so artifacts no longer claim a branch-only/no-new-merge state. It does **not** retroactively approve either merge, waive independent reviews, deploy, or permit downstream ALR-020+ work; gate 697 remains the audit record requiring a fresh Zeus-signed `agent:zeus` PR and independent exact-SHA re-review after this correction.

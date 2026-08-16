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
| `last_verified_origin_main` | R2ah read-only verification fetched canonical `origin/main` and recorded exact current base `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7`; the assigned R2ah branch/worktree was initially equal to that SHA before this documentation-only reviewed-marker/index repair. R2m `ab08b13669903a87b3d60d6c80231d23d6313782`, R2k `83d5ee06ba25859f047469baed223fe88e9467e3`, and earlier `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a` / `00e7bb4ab0fcd9013ffa924ce6c5a8ae2c2ae2fc` evidence are historical only. |
| `r2m_current_base_candidate` | Branch `factory/zeus-alpha-research-ledger-core/inc-001-r2m-current-base-g1-documentatio` in worktree `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2m-current-base-g1-documentatio`; base `origin/main` `ab08b13669903a87b3d60d6c80231d23d6313782`; documentation-only recovery and exact-SHA review handoff; no merge/deploy/external runtime authority. |
| `r2ah_current_base_candidate` | Branch `factory/zeus-alpha-research-ledger-core/inc-019-r2ah-current-origin-g1-reviewed` in worktree `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2ah-current-origin-g1-reviewed`; base `origin/main` `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7`; documentation-only current-origin reviewed-marker/index repair and PR #47 exact-SHA review handoff; no merge/deploy/external runtime authority. |
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

R2k records a second provenance drift: project metadata still points to PR #20 / `dad375f27568c38be771fc597b579d087f034e1d` while R2j has already been delivered as PR #30 / `c1943efb2b97b54b42bc5eabe858340d8c391116`. R2m records the current-base successor handoff after PR #31/R2k reached `origin/main`: stale PR #20, historical PR #29, PR #30 and PR #31 exposure are not active dispatch evidence. R2ah records the current-origin `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7` reviewed-marker/index repair and uses Zeus-signed `agent:zeus` PR #47 plus independent exact-SHA review. ALR-020+ remains blocked until canonical Factory `document_status` and task gates are reconciled by the authorized control path.

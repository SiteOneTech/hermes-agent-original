---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: yes
---

# TRACKER

## Current state
| Area | State | Evidence / next action |
|---|---|---|
| G0 strategy | passed with recorded drift | G0 records Zeus-only repo, remote and worktree policy; it now also records live evidence that ALR-010-R1 commits `b9396bcd7d14ee6f212bd0fd0609e468cecf567f` and `6ee8b4fdb886d0834bfbc62c7e152ee35d505e66` were merged into `origin/main` as `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a` and `9f975acb0625750b8d46648766d1395c89392dca` by Factory events `173433` and `173494`. Those merges are evidence to review, not PASS/PR/QA authority. |
| Predecessor linkage | passed | `zeus-independent-alpha-research` remains the documentation-only predecessor |
| ALR-010 G1 | corrected R2 candidate pending exact-SHA review | required docs exist, are indexed/tracked, and carry explicit validated/reviewed status; gates 686/687 were request-changes, gates 695/697 recorded direct-integration drift, and any PASS on a pre-correction SHA is not reused for this revision |
| ALR-010-R1 | superseded audit history | R1 remains evidence only after two direct integrations; no ledger code, Factory metadata mutation authority, PR approval, deploy, prohibited external-system call, PASS claim or reviewed=yes change comes from R1 |
| ALR-010-R2 | active bounded rework | must reconcile both direct integrations, create a fresh branch-only commit, push the assigned branch, open a Zeus-signed GitHub PR labeled `agent:zeus`, and require independent exact-SHA spec/security review before closure |
| ALR-020..050 | not started | blocked on exact-SHA independent PASS reviews, reconciliation of both observed ALR-010-R1 base-merge events, PR/review/base-visibility evidence, and deterministic Factory metadata correction removing incompatible bounded-local-sessions acceptance |
| Source APIs | policy only | v1 supports local normalized evidence batch; no provider driver/credential is enabled in core |
| Daily scheduler | disabled by design | must wait for recorded ALR-070 local prerequisites |
| Vonash exchange | intentionally excluded | external platform owns any later secure intake/evaluation work |
| Trading/paper/live | prohibited | no authority in this project |

## Review remediation completed in this draft
- `G1_REVIEW.md` now records the actual gate 686/687 failed notes from Agent Core Postgres read-back instead of summarizing them as an approval-like status.
- Dedicated-role grant matrix, revocations/default privileges and direct-role denial tests are specified.
- Source/evidence/lineage/review/handoff invariants moved to database-enforced requirements.
- Research-only/unvalidated/non-advice classification and forbidden labels are now typed and tested.
- Toolset isolation/no-egress and disabled-by-default scheduler become automated gates.
- Exact handler naming is canonicalized on `program_create` and `source_submit`, with synonym/alias rejection.
- Stale current-base wording is removed; base SHAs are historical evidence and must be revalidated before PR.
- Gate 695's real finding is recorded: Factory event `173433` integrated branch commit `b9396bcd7d14ee6f212bd0fd0609e468cecf567f` into `origin/main` as merge commit `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a`; this is non-approval evidence.
- Gate 697's real finding is recorded: Factory event `173494` integrated branch commit `6ee8b4fdb886d0834bfbc62c7e152ee35d505e66` into `origin/main` as merge commit `9f975acb0625750b8d46648766d1395c89392dca`; this removes false branch-only/no-new-merge statements and is likewise non-approval evidence.
- Collaboration session/message storage was removed from v1.
- Factory's ALR-020 bounded-local-sessions acceptance clause conflicts with that exclusion; required reconciliation is documented in `TASK_GRAPH.md` and must be completed/read back by the authorized metadata owner before implementation, without expanding v1.
- ALR-060 was superseded by three independent review tasks; ALR-070 depends on all three.

## Immediate next event
Commit this bounded correction on the assigned R2 branch, push it, create the Zeus-signed GitHub PR labeled `agent:zeus`, record documentary evidence, then obtain new independent specification and security reviews against the exact revised SHA. Implementation remains blocked until `reviewed: yes` is validly supported, gate-695/gate-697 merge reconciliation is independently accepted, PR/review/base-visibility evidence is recorded, and the ALR-020 metadata reconciliation is recorded/read back exactly.

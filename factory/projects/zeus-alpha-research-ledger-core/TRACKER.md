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
| ALR-010 G1 | reviewed documentation readiness | corrected substantive SHA `3e6c14f8aa368ec6e3623d16640bf4b558ce0c7a` independently passed Factory gates 709 (spec), 710 (security) and 711 (quality); the marker transition records those gates and does not grant QA/merge/deploy authority |
| ALR-010-R1 | superseded audit history | R1 remains evidence only after two direct integrations; no ledger code, Factory metadata mutation authority, PR approval, deploy, prohibited external-system call, PASS claim or reviewed=yes change comes from R1 |
| ALR-010-R2 | planning task done; reconciliation ready to resolve | PR #20 is open and labeled `agent:zeus`; gate 708 rework passed fresh exact-SHA gates 709/710/711 and canonical resolve-state must consume this committed marker transition |
| ALR-020..050 | ALR-020 next; later tasks not started | ALR-020 acceptance metadata was corrected/read back in Factory event 174440; release the temporary manual takeover only after canonical resolve-state then tick exactly ALR-020 through its assigned branch/worktree and strict TDD/PR-first controls |
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
- Factory event 174440 reconciled ALR-020's bounded-local-sessions acceptance clause: the read-back shows the old literal absent and the exact session/message-excluded, scheduler-readiness and non-session local-intake literal present. This task-metadata repair does not expand v1 or authorize implementation.
- ALR-060 was superseded by three independent review tasks; ALR-070 depends on all three.

## Immediate next event
Run canonical resolve-state against this committed marker transition, verify the reconciliation task is terminal and G1 blockers are zero, release the temporary manual takeover, then tick exactly the assigned ALR-020 task. Gates 695/697 remain reconciled non-approval audit evidence, and Factory event 174440 remains metadata read-back rather than implementation authority.

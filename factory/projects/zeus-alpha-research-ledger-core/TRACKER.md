---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: pending
---

# TRACKER

## Current state
| Area | State | Evidence / next action |
|---|---|---|
| G0 strategy | passed with recorded drift | G0 records Zeus-only repo, remote and worktree policy; it now also records live evidence that ALR-010-R1 commit `b9396bcd7d14ee6f212bd0fd0609e468cecf567f` was merged into `origin/main` as `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a` by Factory event `173433`. That merge is evidence to review, not PASS/PR/QA authority. |
| Predecessor linkage | passed | `zeus-independent-alpha-research` remains the documentation-only predecessor |
| ALR-010 G1 | corrected candidate pending exact-SHA review | required docs exist, are indexed/tracked, and carry explicit validated/reviewed status; gates 686/687 were request-changes, gate 695 recorded merge-policy drift, and any PASS on a pre-correction SHA is not reused for this revision |
| ALR-010-R1 | active bounded rework | resolves only the documented gates 686/687 findings plus gate 695's requirement to record the actual direct-merge evidence; no ledger code, Factory metadata mutation, PR, new merge, deploy, prohibited external-system call, PASS claim or reviewed=yes change |
| ALR-020..050 | not started | blocked on exact-SHA independent PASS reviews, reconciliation of the observed ALR-010-R1 base-merge evidence, and deterministic Factory metadata correction removing incompatible bounded-local-sessions acceptance |
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
- Gate 695's real finding is now recorded: Factory event `173433` integrated branch commit `b9396bcd7d14ee6f212bd0fd0609e468cecf567f` into `origin/main` as merge commit `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a`; this is non-approval evidence and removes false branch-only/no-merge statements.
- Collaboration session/message storage was removed from v1.
- Factory's ALR-020 bounded-local-sessions acceptance clause conflicts with that exclusion; required reconciliation is documented in `TASK_GRAPH.md` and must be completed/read back by the authorized metadata owner before implementation, without expanding v1.
- ALR-060 was superseded by three independent review tasks; ALR-070 depends on all three.

## Immediate next event
Commit this bounded correction, record documentary evidence, then obtain new independent specification and security reviews against the exact revised SHA. Implementation remains blocked until `reviewed: yes` is validly supported, gate-695 merge reconciliation is independently accepted, and the ALR-020 metadata reconciliation is recorded/read back exactly.

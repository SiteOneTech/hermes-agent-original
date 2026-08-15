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
| ALR-010 G1 | corrected candidate pending exact-SHA review | required docs exist, are indexed/tracked, and carry explicit validation plus pending review-state controls; gates 686/687 were request-changes, gate 695 recorded merge-policy drift, and any PASS on a pre-correction SHA is not reused for this revision |
| R2j canonical-state repair | historical, PR #30 merged | R2j commit `c1943efb2b97b54b42bc5eabe858340d8c391116` was delivered as PR #30 with `agent:zeus` and merged into remote `origin/main` as `83d5ee06ba25859f047469baed223fe88e9467e3`; this is evidence to reconcile, not ALR-020 dispatch authority. |
| R2k stale provenance repair | historical, PR #31 merged | Agent Core project metadata still points to obsolete PR #20 / `dad375f27568c38be771fc597b579d087f034e1d`, but R2k itself was delivered as PR #31 at head `73b74f03e3c73830f69fb487a7439529190c21c2` and is now historical provenance repair evidence. It does not mark G1 reviewed or dispatch ALR-020. |
| R2m current-base recovery | historical bounded handoff | Assigned branch/worktree recreated from `origin/main` `ab08b13669903a87b3d60d6c80231d23d6313782`; R2j/R2k repairs are indexed and preserved, but this handoff is superseded by R2n because the canonical base advanced. See `R2M_CURRENT_BASE_G1_REVIEW_HANDOFF.md`. |
| R2n canonical-document repair | active bounded handoff | Assigned branch/worktree recreated from current `origin/main` `df4c77fd1413a65cdb85885a06978ff157c1de4d`; canonical Factory evidence now records both readings: dispatch snapshot with 10 blocking rows plus 4 heuristic false-ready rows, and strict primary read-back with all 14 required G1 docs at `reviewed=false`; next valid review target is the fresh R2n PR head SHA. See `R2N_CANONICAL_DOCUMENT_STATUS_REPAIR.md`. |
| ALR-010-R1 | active bounded rework | resolves only the documented gates 686/687 findings plus gate 695's requirement to record the actual direct-merge evidence; no ledger code, Factory metadata mutation, PR, new merge, deploy, prohibited external-system call, PASS claim or review-state approval change |
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
- R2j now records that R2i's `already_ancestor` integration metadata belongs to the review-only branch and must not be used as source visibility evidence for PR #29; QA Guardian/source-delivery evidence must bind to PR #29 head `f61a7275048e2135b2b2729a1b9cdf8713c58866`.
- R2k now records that the active Factory metadata pointer is stale: `metadata.g1_documentation_checkout` still names PR #20 / `dad375f27568c38be771fc597b579d087f034e1d` even after R2j was delivered through PR #30 at `c1943efb2b97b54b42bc5eabe858340d8c391116`; renewed review must not reuse PR #20/#29 or review-worktree metadata.
- R2m records historical current-base handoff evidence at `ab08b13669903a87b3d60d6c80231d23d6313782`.
- R2n supersedes R2m as active handoff on current `origin/main` `df4c77fd1413a65cdb85885a06978ff157c1de4d`, records the 10-blocker/4-heuristic-false-ready dispatch snapshot and the strict all-14 primary `reviewed=false` read-back, neutralizes branch-local positive review markers in the first 40 lines of the affected control docs, and keeps `reviewed: pending` until independent reviewers inspect the R2n PR head.
- Collaboration session/message storage was removed from v1.
- Factory's ALR-020 bounded-local-sessions acceptance clause conflicts with that exclusion; required reconciliation is documented in `TASK_GRAPH.md` and must be completed/read back by the authorized metadata owner before implementation, without expanding v1.
- ALR-060 was superseded by three independent review tasks; ALR-070 depends on all three.

## Immediate next event
Commit this bounded R2n canonical-document correction, push it through a Zeus-signed `agent:zeus` PR, record documentary evidence, then obtain new independent quality/spec/security review against the exact R2n PR head SHA. Implementation remains blocked until `reviewed: yes` is validly supported by that exact-SHA review path, stale PR #20 metadata is reconciled in Agent Core, canonical `document_status` has no required G1 blockers, gate-695/R2j/R2k/R2m/R2n reconciliation is independently accepted, and the ALR-020 metadata reconciliation is recorded/read back exactly.

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

# TRACKER

## Current state
| Area | State | Evidence / next action |
|---|---|---|
| G0 strategy | passed with recorded drift | G0 records Zeus-only repo, remote and worktree policy; it now also records live evidence that ALR-010-R1 commit `b9396bcd7d14ee6f212bd0fd0609e468cecf567f` was merged into `origin/main` as `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a` by Factory event `173433`. That merge is evidence to review, not PASS/PR/QA authority. |
| Predecessor linkage | passed | `zeus-independent-alpha-research` remains the documentation-only predecessor |
| ALR-010 G1 | reviewed documentation pack repaired | required docs exist, are indexed/tracked, and carry explicit validated/reviewed status; R2u binds `reviewed: yes` to PR #36 exact head `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` and Factory gate `794`; gates 686/687/695 remain historical request-changes context, not runtime authority |
| R2j canonical-state repair | historical, PR #30 merged | R2j commit `c1943efb2b97b54b42bc5eabe858340d8c391116` was delivered as PR #30 with `agent:zeus` and merged into remote `origin/main` as `83d5ee06ba25859f047469baed223fe88e9467e3`; this is evidence to reconcile, not ALR-020 dispatch authority. |
| R2k stale provenance repair | historical, PR #31 merged | Agent Core project metadata still points to obsolete PR #20 / `dad375f27568c38be771fc597b579d087f034e1d`, but R2k itself was delivered as PR #31 at head `73b74f03e3c73830f69fb487a7439529190c21c2` and is now historical provenance repair evidence. It does not mark G1 reviewed or dispatch ALR-020. |
| R2m current-base recovery | historical handoff | Assigned branch/worktree recreated from `origin/main` `ab08b13669903a87b3d60d6c80231d23d6313782`; R2j/R2k repairs are indexed and preserved. R2u supersedes its pending-review state for canonical document-status preflight by applying reviewed PR #36/gate 794 markers. |
| R2u document-status preflight repair | active delivery | Current assigned branch/worktree starts from `df4c77fd1413a65cdb85885a06978ff157c1de4d`; required G1 docs/index/traceability now carry reviewed provenance so docs-first preflight can report zero required blockers. See `R2U_CANONICAL_G1_DOCUMENT_STATUS_PREFLIGHT_REPAIR.md`. |
| R2v control-plane repair | implemented; quality PASS gate 804 | Factory document status now falls back from stale primary checkout blockers to the verified configured base ref `origin/main` only, never to candidate PR/worktree metadata; `factory_auto_integration_forbidden=true` now blocks `merge_no_ff_push_origin` / `increment_integrated`. Independent exact-SHA quality review PASS (gate 804) on head `90fcb81abcebc203e16e34e36f4aec0ab1ec6a09`; PR #39 open for QA Guardian merge. See `R2V_CANONICAL_G1_STATUS_AND_NO_AUTO_MERGE_REPAIR.md` and `QA_GATES.md`. |
| R2w reviewed-frontmatter PR recovery | active delivery | Current configured-base `document_status` read-back shows all G1 required documents, including the 11 named blockers, with exists/committed/validated/indexed/reviewed all true and blocking=false at `origin/main` `df79aac9d306c0b055fe88dbde5ebd54d9635e36`. R2w records this as PR-first evidence in `R2W_CANONICAL_G1_REVIEWED_FRONTMATTER_PR.md`; task closure still requires the exact pushed PR SHA and independent quality review. |
| R2ah current-origin reviewed-marker/index repair | active delivery | Fresh assigned worktree/branch started equal to current `origin/main` `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7`; Agent Core configured-base `document_status` read-back shows all 14 G1 required documents exists/committed/indexed/validated/reviewed true and blocking=false. R2ah records the current-base documentation-index/G1-review handoff in `R2AH_CURRENT_ORIGIN_G1_REVIEWED_MARKER_REPAIR.md` and PR #47; task closure still requires the exact pushed PR SHA and independent quality review. |
| R2c2 autonomous canonical G1 document-status repair | active delivery | Fresh assigned worktree/branch started equal to current `origin/main` `dbde1790f8d45f111bc69b3491a1862eafb29fa2`; Agent Core configured-base `document_status` read-back in `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786892903-1813387-f690.log` lines 16632–16898 shows all 14 G1 required documents exists/committed/indexed/validated/reviewed true and blocking=false. R2c2 records the current canonical status repair in `R2C2_AUTONOMOUS_CANONICAL_G1_DOCUMENTATION_STATUS_REPAIR.md`; task closure still requires the exact pushed PR SHA and independent quality review. |
| ALR-010-R1 | historical bounded rework | resolves only the documented gates 686/687 findings plus gate 695's requirement to record the actual direct-merge evidence; no ledger code, Factory metadata mutation, new merge, deploy or prohibited external-system call |
| ALR-020..050 | not started | blocked until their own scoped TDD/security/QA gates run; G1 document readiness does not grant product/runtime dispatch authority |
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
- R2m records the current canonical base `ab08b13669903a87b3d60d6c80231d23d6313782`, adds a fresh exact-SHA handoff artifact, and remains historical pending-review context.
- R2u records the active docs-first repair: current base `df4c77fd1413a65cdb85885a06978ff157c1de4d`, PR #36 exact head `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`, Factory gate `794`, and canonical required-document markers set to `reviewed: yes`.
- R2ah records the current-origin repair: exact base `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7`, fresh branch/worktree identity before edits, Agent Core configured-base `document_status` evidence with all 14 required rows non-blocking, and Zeus-signed `agent:zeus` PR #47 for independent exact-SHA review.
- R2c2 records the autonomous canonical repair: exact base `dbde1790f8d45f111bc69b3491a1862eafb29fa2`, fresh branch/worktree identity before edits, Agent Core configured-base `document_status` evidence with all 14 required rows non-blocking, and a fresh Zeus-signed `agent:zeus` PR-first handoff for independent exact-SHA review.
- Collaboration session/message storage was removed from v1.
- Factory's ALR-020 bounded-local-sessions acceptance clause conflicts with that exclusion; required reconciliation is documented in `TASK_GRAPH.md` and must be completed/read back by the authorized metadata owner before implementation, without expanding v1.
- ALR-060 was superseded by three independent review tasks; ALR-070 depends on all three.

## Immediate next event
Open and keep the R2c2 PR-first handoff available for independent exact-SHA quality review before task closure. Product implementation remains blocked until each downstream ALR task independently passes its own TDD/security/QA delivery gates.

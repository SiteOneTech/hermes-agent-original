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
| G0 strategy | passed | G0 records Zeus-only repo, `origin/main`, remote, branch/worktree policy and PR-first delivery; fetched `origin/main` was `00e7bb4ab0fcd9013ffa924ce6c5a8ae2c2ae2fc`, while `20228c1167814f36d952999f2cafe8b3f6f9ba3c` is historical only and canonical base must be revalidated before PR |
| Predecessor linkage | passed | `zeus-independent-alpha-research` remains the documentation-only predecessor |
| ALR-010 G1 | branch-local candidate ready for independent review | required docs exist, are indexed/tracked, and carry explicit validated/reviewed status; reviewer state remains pending because prior spec/security gates failed and no new independent PASS exists |
| ALR-020..050 | not started | blocked on reviewed and QA-merged G1 PR; ALR-020 is additionally blocked pending deterministic Factory metadata reconciliation removing incompatible bounded-local-sessions acceptance |
| Source APIs | policy only | v1 supports local normalized evidence batch; no provider driver/credential is enabled in core |
| Daily scheduler | disabled by design | must wait for recorded ALR-070 local prerequisites |
| Vonash exchange | intentionally excluded | external platform owns any later secure intake/evaluation work |
| Trading/paper/live | prohibited | no authority in this project |

## Review remediation completed in this draft
- Dedicated-role grant matrix, revocations/default privileges and direct-role denial tests are specified.
- Source/evidence/lineage/review/handoff invariants moved to database-enforced requirements.
- Research-only/unvalidated/non-advice classification and forbidden labels are now typed and tested.
- Toolset isolation/no-egress and disabled-by-default scheduler become automated gates.
- Collaboration session/message storage was removed from v1.
- Factory's ALR-020 bounded-local-sessions acceptance clause conflicts with that exclusion; required reconciliation is documented in `TASK_GRAPH.md` and must be completed/read back by the authorized metadata owner before implementation, without expanding v1.
- ALR-060 was superseded by three independent review tasks; ALR-070 depends on all three.

## Immediate next event
Commit and push this bounded branch-local candidate, record the documentary evidence gate, then obtain new independent specification and security reviews against the exact revised SHA. Implementation remains blocked until `reviewed: yes` is validly supported, the G1 PR is merged by the mandated QA Guardian path, and the ALR-020 metadata reconciliation is recorded/read back exactly.

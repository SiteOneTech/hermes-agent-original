---
project_id: zeus-independent-alpha-research
status: planning
validated: yes
reviewed: yes
owner: implementation-planner
---

# Methodology Plan

## Delivery method
Hybrid Factory methodology: discovery and documentary gates first; small owned increments; independent quality/security review; paper-safe end-to-end proof; then an internal Vonash release handoff. No increment may infer a runtime interface that the audit has not verified.

## G0 repository strategy
- Current planning repository: `SiteOneTech/hermes-agent-original`, Zeus-only scope.
- Future implementation repository/runtime: Vonash-owned and audit-required.
- Worktree policy: one branch/worktree per increment; no edits in the shared checkout.
- Propagation: a planned handoff, not automatic deployment to Vonash.

## G1 documentary gate
The documents in this directory govern requirements and all future task acceptance. Any contradiction with older product references is resolved in favor of this directory; the references are updated to point here.

## Increment method
1. **I0 — canonical plan:** reconcile G1 docs and publish the engineering handoff.
2. **I1 — read-only audit:** identify actual Vonash ownership, data/evaluator/service/API/runtime contracts and risks.
3. **I2 — contract design:** choose exact API/thread/outbox/schema boundaries based on I1; review service identity and retention.
4. **I3 — foundation:** build only the approved ledger/thread/outbox/auth surfaces in their owning repos.
5. **I4 — research lifecycle:** evidence, Alpha Card, lineage, review, capability request and experiment-reference flows.
6. **I5 — collaboration:** daily workshop, Telegram mirror, acknowledgements and recovery.
7. **I6 — reactive event lane:** source health, evidence alert classification, severity routing and no-ack monitoring.
8. **I7 — safe pilot:** manual dry-run plus paper-safe experiment reference path; no live activation.
9. **I8 — release handoff:** independent reviews, deployed verification, runbooks and Jean’s release decision.

## Decision discipline
- Use real current capabilities from I1, not examples in this plan.
- Missing data/evaluator capability becomes a `capability_request` with owner, priority and acceptance criteria.
- Every implementation item is independently claimable, has an owner/reviewer, branch/worktree, tests and evidence.
- The owner of substantial code is not its only approver.

## Stop conditions
Stop and create a concrete decision for Jean/internal owners if the source scope, service identity, runtime policy, security boundary, or live/paper authority is ambiguous. Do not compensate with a generic fallback or bypass.

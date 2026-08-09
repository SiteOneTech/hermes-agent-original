---
project_id: zeus-independent-alpha-research
status: planning
validated: yes
reviewed: yes
owner: zeus
---

# Vonash Implementation Handoff

## What the internal team is being asked to build
A bounded, service-owned **Research Exchange** between Zeus and Magnus. It enables research collaboration and records it durably; it is not an execution, trading, risk or deployment integration.

## Non-negotiable business contract
- Magnus is the runtime CEO/operator in Vonash.
- Zeus is an outside research advisor that contributes evidence-backed Alpha Cards and alerts.
- Vonash remains the sole owner of its evaluator, simulation, paper/live and promotion governance.
- A Zeus message cannot directly cause a trade, policy/risk change, paper/live activation, strategy promotion, code/config change or deployment.

## Required discovery before coding
Perform a read-only audit and attach evidence for: actual repository/branch, owning service, current research/Magnus runner, supported scheduler, service-to-service auth, message/outbox facilities, data/evaluator/experiment contracts, deployment/rollback path, source license/egress rules and the current paper/live governance boundary.

## Required interface (conceptual; exact implementation after audit)
1. Typed `research_thread` and `research_message` lifecycle owned by Vonash.
2. Durable delivery/outbox, acknowledgement, expiry, idempotency and status transitions.
3. A narrow authenticated API for the allowlisted research message types:
   `research_hypothesis`, `research_question`, `capability_query`, `capability_response`, `experiment_proposal`, `experiment_result_reference`, `research_alert`, `acknowledgement`, `session_synthesis`.
4. External-reference links to Zeus cycle/card/evidence IDs; never a direct Zeus database connection.
5. Optional Telegram group mirror rendered from the typed record with thread IDs and redaction.
6. Metrics/alerts for stale sources, delivery failures, no acknowledgement, empty cycles and duplicate lineage.

## Collaboration protocol
### Daily workshop
- Start from a Zeus research cycle and select at most three cards/topics.
- Zeus and Magnus may each contribute up to six substantive turns over 45 minutes.
- Magnus reports feasibility/data/evaluator/experiment constraints from live platform knowledge.
- Close with `session_synthesis`, cards/evidence references, disagreement list, capability gaps, candidate experiment requests and one typed outcome per card.

### Reactive research alert
- An alert contains evidence, time observed, source freshness, impacted universe, condition, uncertainty, expiry, requested review and severity (`S1/S2/S3`).
- It requests acknowledgement and may notify Jean through Telegram; it is never a broker/risk instruction.
- Final severity response objectives are an operational-policy decision after audit. Synthetic no-send tests prove the path before operational use.

## Delivery sequence
1. Audit and fact matrix.
2. Exact contract, schema/API/auth/retention ADR and test plan.
3. Implement owned exchange/outbox/auth with negative authorization tests.
4. Implement Zeus ledger adapter only after the contract is approved.
5. Add daily workshop/mirror, then reactive alert path.
6. Prove a manual paper-safe cycle and synthetic alert; do not enable a legacy dispatcher.
7. Independent QA/security/release review, deploy through normal Vonash pipeline, provide exact revision/rollback/runbook evidence.

## Definition of done
A real non-executing pilot has durable threads, idempotent acknowledgement, reference-linked cards/evidence, result references, transport recovery, observability and a proven absence of prohibited execution surfaces. Production trading/promotion is not part of this definition.

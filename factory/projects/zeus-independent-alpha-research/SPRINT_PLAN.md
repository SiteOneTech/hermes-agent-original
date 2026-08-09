---
project_id: zeus-independent-alpha-research
status: planning
validated: yes
reviewed: yes
owner: implementation-planner
---

# Sprint Plan

## I0 — Planning and handoff (current)
Create the reconciled G1 pack and the internal Vonash implementation handoff. **Exit:** G1 documents indexed, reviewed, committed and Factory state reconciled. No code or runtime change.

## I1 — Read-only Vonash capability audit
Map repository, current branch/runtime, database/service ownership, source adapters, evaluator/data contracts, experiment/paper/live gates, scheduler status, auth and deploy path. **Exit:** a fact-based capability matrix and no invented interfaces.

## I2 — Contract and identity design
Define exact owning service, thread/outbox/ack contract, schemas/migrations, typed message validation, workload identity, scopes, retention, Telegram mirror adapter and operational severity policy. **Exit:** ADR/technical contract reviewed by architecture and security.

## I3 — Owning-system foundations
Implement the approved Zeus advisory ledger and Vonash research-exchange surfaces in their respective repos. **Exit:** migrations, auth boundaries, API/outbox tests and no cross-DB access.

## I4 — Research lifecycle
Implement evidence intake, Alpha Card/lineage/review, capability request, capability response and experiment-result references. **Exit:** a reproducible card-to-result-reference dry run.

## I5 — Collaboration and mirror
Implement the 45-minute workshop rules, six-turn-per-agent cap, synthesis, acknowledgement deadlines and Telegram mirror. **Exit:** a persisted session survives a transport failure and retains an auditable transcript.

## I6 — Reactive research alerts
Implement approved source/event watchers, evidence freshness, severity routing, alert acknowledgement and stale/no-ack/empty-cycle alarms. **Exit:** a synthetic no-send event proves routing without calling a broker or changing risk.

## I7 — QA/security/paper-safe pilot
Execute independent reviews, real API/health checks, manual cycle, daily workshop and a paper-safe result reference. **Exit:** critical gates pass and prohibited capabilities remain absent.

## I8 — Internal release handoff
The Vonash team merges/deploys through its normal process. **Exit:** exact deployed revision, migration state, rollback/runbook, source health and ownership have evidence; Jean makes any production/policy decision.

## Dependencies
I1 precedes I2; I2 precedes all interfaces; I3 precedes I4–I6; I5/I6 precede I7; I7 precedes I8. No live trading activation belongs to this sprint plan.

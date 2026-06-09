# ADRs — Funnel Core / CRM Sales Workflow

## ADR-001 — Funnel Core as Agent-Inheritable Module

**Status:** Accepted

**Decision:** The sales funnel is implemented as a `FunnelCore` module that defines stages, transitions, and business rules. Agents inherit this core via the `zeus_then_runtime` pattern: core logic lives in Zeus, runtime-specific behavior (CRM backend) is injected via adapter.

**Rationale:** Avoids duplication across CRM adapters. Enables agents to manage sales pipelines generically.

**Consequence:** All CRM adapters must implement `CRMFunnelAdapter` protocol.

---

## ADR-002 — Deterministic Funnel State Machine

**Status:** Accepted

**Decision:** Funnel transitions are deterministic: each transition has explicit trigger conditions and guards. No implicit or side-effect-driven transitions.

**Rationale:** Predictable pipeline behavior is required for agent reasoning and audit trails.

**Consequence:** Each stage transition emits an event. Guards are evaluated before any state change.

---

## ADR-003 — CRM Adapter Protocol Isolation

**Status:** Accepted

**Decision:** The `CRMFunnelAdapter` interface is the only coupling point between FunnelCore and the CRM backend. FunnelCore never imports CRM-specific code.

**Rationale:** Allows swapping CRM backends without changing funnel logic.

**Consequence:** New CRM adapters only need to implement `CRMFunnelAdapter`. No changes to FunnelCore required.

---

## ADR-004 — Reference Adapter for Twenty CRM

**Status:** Accepted

**Decision:** The first reference adapter implements `CRMFunnelAdapter` for Twenty CRM (Twenty.so), chosen as the canonical reference implementation.

**Rationale:** Twenty is the primary CRM used at SitioUno. Reference adapter provides concrete test evidence.

**Consequence:** Twenty adapter is the baseline; others (HubSpot, Salesforce) follow the same protocol.

---

## ADR-005 — Factory Methodology Documents Required

**Status:** Accepted

**Decision:** This project maintains complete Factory methodology documentation per the canonical kickoff artifact pack: FACTORY_INTAKE, PRD, ADRs, METHODOLOGY_PLAN, TECHNICAL_BLUEPRINT, SPRINT_PLAN, TASK_GRAPH, TRACKER, QA_GATES, SECURITY_GATES, QA_REPORT, SECURITY_REVIEW, DELIVERY_REPORT, DOCUMENTATION_INDEX.

**Rationale:** Reproducibility and process discipline require documentation, not just code.

**Consequence:** Missing docs are treated as methodology debt, not optional cleanup.

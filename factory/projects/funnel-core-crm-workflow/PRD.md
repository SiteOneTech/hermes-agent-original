# PRD — Funnel Core / CRM Sales Workflow

## 1. Context

The SitioUno agent ecosystem needs a reusable Sales Funnel module that can be inherited by any CRM adapter. Rather than building funnel logic per-CRM, the pattern should be defined once in a core module and specialized via adapter contracts. This enables agents to manage sales pipelines generically, with runtime-specific CRM backends plugged in through a well-defined interface.

The `zeus_then_runtime` inheritance model allows the core logic to live in Zeus and be specialized at runtime by the actual CRM adapter (Twenty, HubSpot, etc.).

## 2. Problem

Each CRM integration in the SitioUno ecosystem currently duplicates funnel logic. There is no shared Sales Funnel core that:

- Defines stages, transitions, and business rules once.
- Allows any CRM backend to implement the contract.
- Can be used by Zeus agents generically regardless of which CRM is deployed.

## 3. Objectives

- Create a `FunnelCore` module that defines the canonical sales funnel states, transitions, and rules.
- Define a `CRMFunnelAdapter` protocol/interface that any CRM can implement.
- Provide a reference adapter implementation (Twenty CRM or equivalent).
- Make the module agent-inheritable via `zeus_then_runtime` so agents can use it without knowing the specific CRM.
- Include QA gates, test evidence, and delivery report.

## 4. Non-objectives

- Full custom CRM build from scratch.
- Payment processing (HubFintech handles this).
- Multi-tenant data isolation (future work).
- Customer-facing UI (agent internal module only).

## 5. Functional Requirements

| ID | Requirement | Acceptance Criterion |
|----|-------------|---------------------|
| PRD-F1 | Funnel stages defined | LEAD, QUALIFIED, PROPOSAL, NEGOTIATION, CLOSED_WON, CLOSED_LOST, CHURNED |
| PRD-F2 | Deterministic transitions | Each transition has defined trigger conditions and guards |
| PRD-F3 | CRM adapter protocol | `CRMFunnelAdapter` interface with `create_lead`, `update_stage`, `get_stage`, `list_opportunities` |
| PRD-F4 | Reference adapter | Twenty CRM adapter implementing the protocol |
| PRD-F5 | Agent inheritance | Agent can use funnel without knowing CRM backend |
| PRD-F6 | Stage transition events | Each transition emits an event for audit/logging |
| PRD-F7 | Qualification criteria | Lead qualification rules configurable per stage |
| PRD-F8 | Metrics hooks | Stage duration, conversion rates, pipeline value available |

## 6. Non-functional Requirements

- **Inheritance**: `zeus_then_runtime` pattern — core in Zeus, runtime-specific in CRM adapter.
- **Testability**: Unit tests for funnel core, integration tests for adapter.
- **Documentation**: ADR for architecture decisions, QA gates, delivery report.
- **Source of truth**: Factory DB `factory.*` for project tracking; repo artifacts for methodology docs.

## 7. Acceptance Criteria

- FunnelCore module exists with all 8 stage definitions.
- `CRMFunnelAdapter` protocol defined and documented.
- Reference adapter compiles and has basic smoke tests.
- Agent can manage a lead through all stages via generic interface.
- All gates (spec, implementation, quality, test) pass.
- Required Factory docs exist in `factory/projects/funnel-core-crm-workflow/`.
- Delivery report with evidence.

---

*factory-reporter · R2 · 2026-06-09*

# Methodology Plan — Funnel Core / CRM Sales Workflow

## Method

**Hybrid Factory**: combines BMAD-style discipline (PRD, ADRs, sprint planning, task graph, adversarial review) with SitioUno Agent Core Factory DB, deterministic gates, and Zeus orchestration.

## Methodological Contract

| Element | Decision |
|---------|----------|
| Operational source | Agent Core Postgres `factory.*` |
| Human PM layer | Notion project page (required) |
| Repo artifacts | `factory/projects/funnel-core-crm-workflow/` |
| Autonomy | Level 3: agents/Zeus implement and review; gates verify |
| Kanban | Not used; Factory DB is canonical |
| Closure | Only with docs + Notion + gates + reconciliation without anomalies |

## Phases

1. **F0 — Intake**: scope, PRD, ADRs, task graph, Notion.
2. **F1 — Architecture**: funnel state machine, adapter protocol, Twenty adapter design.
3. **F2 — Implementation**: FunnelCore module, CRMFunnelAdapter protocol, reference adapter.
4. **F3 — QA**: unit tests, integration tests, spec gate.
5. **F4 — Delivery**: smoke tests, delivery report, reconciliation.

## Gates Required

- Intake
- Planning
- Implementation
- Quality
- Test
- Delivery
- Reconciliation

## Documents Required

FACTORY_INTAKE.md, PRD.md, ADRs.md, METHODOLOGY_PLAN.md, TECHNICAL_BLUEPRINT.md, SPRINT_PLAN.md, TASK_GRAPH.md, TRACKER.md, QA_GATES.md, SECURITY_GATES.md, QA_REPORT.md, SECURITY_REVIEW.md, DELIVERY_REPORT.md, DOCUMENTATION_INDEX.md, PROJECT_GLOBAL_VISION.md

## Rule

A Factory project must not be marked `completed` if required docs are missing. Missing docs are methodology debt, not optional cleanup.

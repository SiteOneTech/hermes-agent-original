# Sprint Plan — Funnel Core / CRM Sales Workflow

## Sprint 1 — Funnel Core Implementation

**Objective:** Implement a reusable, agent-inheritable sales funnel module with a CRM adapter protocol and a Twenty CRM reference adapter.

| Task | Objective | Owner | Reviewer | Status |
|------|----------|-------|----------|--------|
| F0 | Intake, method, task graph, docs | Zeus/factory-reporter | factory-orchestrator | done |
| F1 | Funnel state machine + adapter protocol | Zeus/claude-builder | solution-architect | done |
| F2 | Twenty CRM reference adapter | Zeus/claude-builder | quality-reviewer | done |
| F3 | Unit + integration tests | Zeus/qa-verifier | quality-reviewer | done |
| F4 | QA, smoke, delivery report, reconciliation | Zeus/factory-reporter | factory-orchestrator | in_progress |

## Definition of Ready

- Factory DB project visible in Agent Core Postgres.
- Project-local artifact dir created.
- Task graph and acceptance criteria defined.
- Notion project page linked in metadata.

## Definition of Done

- FunnelCore module with all stage definitions.
- CRMFunnelAdapter protocol documented and implemented.
- Twenty CRM adapter with basic smoke tests.
- All Factory gates (spec, implementation, quality, test) passed with evidence.
- Required docs exist in `factory/projects/funnel-core-crm-workflow/`.
- Reconciliation shows no missing docs anomalies.
- Delivery report exists.

## Risks

- Adapter protocol changes may require FunnelCore updates if not isolated.
- CRM API rate limits may affect integration tests.
- Documentation debt if docs are treated as optional.

# Task Graph — Funnel Core / CRM Sales Workflow

```mermaid
graph TD
  F0[F0 Intake + method + docs]
  F1[F1 Funnel state machine + adapter protocol]
  F2[F2 Twenty CRM reference adapter]
  F3[F3 Unit + integration tests]
  F4[F4 QA, smoke, delivery report, reconciliation]

  F0 --> F1
  F1 --> F2
  F2 --> F3
  F3 --> F4
```

## Factory DB Tasks

| Task ID | Title | Status | Evidence |
|---------|-------|--------|----------|
| funnel-core-crm-workflow-f0-intake | F0 — Intake, method, task graph | done | factory/projects/funnel-core-crm-workflow/FACTORY_INTAKE.md |
| funnel-core-crm-workflow-f1-funnel-core | F1 — FunnelCore module + adapter protocol | done | branch factory/funnel-core-crm-workflow/inc-001-client-requirement-implement-gen |
| funnel-core-crm-workflow-f2-twenty-adapter | F2 — Twenty CRM reference adapter | done | agent/crm/adapters/twenty.py |
| funnel-core-crm-workflow-f3-tests | F3 — Unit + integration tests | done | tests/agent/crm/ |
| funnel-core-crm-workflow-reconcile-missing-required-docs | R2 — Reconciliation: complete required docs | in_progress | factory/projects/funnel-core-crm-workflow/ |

## Dependencies

- F1 requires F0.
- F2 requires F1.
- F3 requires F2.
- F4 requires F3 + R2 completion.

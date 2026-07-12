# Task Graph 001 — Sales Operator Core

```mermaid
graph TD
  A[Planning docs] --> B[DB schema]
  A --> C[Security/policy model]
  B --> D[Tool handlers]
  D --> E[Toolset wiring]
  D --> F[CRM integration]
  C --> G[Outbound queue fail-closed]
  F --> H[Daily rollup]
  G --> H
  A --> I[Empleado.uno playbook pack]
  I --> J[Pilot campaign]
  H --> J
  J --> K[Live smoke + QA]
```

## Task inventory

| ID | Title | Owner engine | Depends on | Acceptance |
|---|---|---|---|---|
| T0 | Planning gates and docs | Zeus/Factory | none | PRD, ADR, sprint, task graph, QA/security, docs index exist. |
| T1 | DB schema and module registration | Claude/Codex | T0 | Migration creates schema/tables/roles/grants. |
| T2 | Tool handlers and toolset | Claude/Codex | T1 | `sales_operator_*` tools registered and tested. |
| T3 | CRM/Funnel bridge | Claude/Codex | T2 | Approved lead creates/upserts CRM rows and follow-up. |
| T4 | Channel policy + outbound queue | Claude/Codex | T2 | Queue is fail-closed and enforces opt-out/rate limits. |
| T5 | Empleado.uno playbook pack | Zeus/Claude | T0 | Vertical playbooks and templates available. |
| T6 | Cron/daily operator scripts | Claude/Codex | T2,T4,T5 | Dry-run daily rollup works; cron creation documented/gated. |
| T7 | Pilot smoke | Zeus/reviewer | T1-T6 | Campaign+territory+10 leads+rollup verified. |
```

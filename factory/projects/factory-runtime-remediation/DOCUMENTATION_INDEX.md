# Documentation Index — Factory Runtime Remediation

## Project-local artifacts

| File | Purpose | Status |
|---|---|---|
| `FACTORY_INTAKE.md` | Intake, trigger, scope | complete |
| `PRD.md` | Requirements and acceptance | complete |
| `ADRS.md` | Architecture/process decisions | complete |
| `METHODOLOGY_PLAN.md` | Hybrid Factory route and gates | complete |
| `TECHNICAL_BLUEPRINT.md` | Runtime architecture and contracts | complete |
| `SPRINT_PLAN.md` | Sprint/story plan and DoR/DoD | complete |
| `TASK_GRAPH.md` | Dependency graph and task inventory | complete |
| `TRACKER.md` | Human-readable local tracker | complete |
| `QA_GATES.md` | QA criteria | complete |
| `SECURITY_GATES.md` | Security criteria | complete |
| `QA_REPORT.md` | Test/smoke evidence | complete |
| `SECURITY_REVIEW.md` | Security review evidence | complete |
| `DELIVERY_REPORT.md` | Delivery, residual risks, closure | complete |
| `NOTION_UPDATE.md` | Notion page creation/update evidence | generated after Notion call |

## Source-of-truth hierarchy

1. Agent Core Postgres `factory.*` — operational status, tasks, gates, events.
2. Repo artifacts — methodology documents and evidence.
3. Notion — human PM/reporting page.
4. Chat/tool output — execution transcript and live verification.

## Correction note

The first closure attempt used Notion/docs waivers. That was not canonical. This document set restores the required Factory route.

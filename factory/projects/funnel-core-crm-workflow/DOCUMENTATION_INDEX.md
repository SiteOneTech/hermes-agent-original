# Documentation Index — Funnel Core / CRM Sales Workflow

## Project-local Artifacts

| File | Purpose | Status |
|------|---------|--------|
| FACTORY_INTAKE.md | Intake, trigger, scope | complete |
| PRD.md | Requirements and acceptance criteria | complete |
| ADRS.md | Architecture and process decisions | complete |
| METHODOLOGY_PLAN.md | Hybrid Factory route and gates | complete |
| TECHNICAL_BLUEPRINT.md | Module architecture and contracts | complete |
| SPRINT_PLAN.md | Sprint plan and DoR/DoD | complete |
| TASK_GRAPH.md | Dependency graph and task inventory | complete |
| TRACKER.md | Human-readable local tracker | complete |
| QA_GATES.md | QA criteria | complete |
| SECURITY_GATES.md | Security criteria | complete |
| QA_REPORT.md | Test and quality evidence | complete |
| SECURITY_REVIEW.md | Security review evidence | complete |
| DELIVERY_REPORT.md | Delivery summary and residual risks | complete |
| DOCUMENTATION_INDEX.md | This file — canonical document map | complete |
| PROJECT_GLOBAL_VISION.md | Compact project memory and context | complete |

## Additional Artifacts

| File | Purpose | Status |
|------|---------|--------|
| R0_NOTION_TRACKER_RECONCILIATION.md | R0 reconciliation evidence | complete |
| notion_tracker_evidence.json | Notion page evidence | complete |

## Source-of-Truth Hierarchy

1. **Agent Core Postgres `factory.*`** — operational status, tasks, gates, runs, events.
2. **Repo artifacts** — methodology documents, indexed from this file.
3. **Git commits** — historical checkpoint preserving the project record.
4. **Notion/dashboard** — human PM/reporting projection.
5. **Chat/tool output** — execution transcript and live verification.

## Builder Reading Order

1. `DOCUMENTATION_INDEX.md` (this file)
2. `PROJECT_GLOBAL_VISION.md`
3. `FACTORY_INTAKE.md`
4. `PRD.md`
5. `ADRS.md`
6. `TECHNICAL_BLUEPRINT.md`
7. `SPRINT_PLAN.md`
8. `TASK_GRAPH.md`
9. Task-specific acceptance criteria from Factory DB

## Blocker Note

R0 identified a CLI gap: `hermes factory` CLI has no subcommand to write `notion_tracker_page_id` into Factory DB metadata. This is a known limitation pending Zeus/code-owner resolution. Notion page exists and is linked in artifacts, but Factory DB metadata cannot be updated via CLI.

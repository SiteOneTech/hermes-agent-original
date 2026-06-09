# Documentation Index — Factory Runtime Evolution

## Project-local artifacts

| File | Purpose | Status |
|---|---|---|
| `FACTORY_INTAKE.md` | Intake, trigger, scope | complete |
| `PRD.md` | Requirements and acceptance | updated for repo-first runtime contract |
| `ADRS.md` | Architecture/process decisions | complete |
| `METHODOLOGY_PLAN.md` | Hybrid Factory route and gates | complete |
| `TECHNICAL_BLUEPRINT.md` | Runtime architecture and contracts | complete |
| `SPRINT_PLAN.md` | Sprint/story plan and DoR/DoD | updated for recursive increment |
| `TASK_GRAPH.md` | Dependency graph and task inventory | updated for F5 repo-first contract |
| `TRACKER.md` | Human-readable local tracker | complete |
| `DOCUMENTATION_INDEX.md` | Canonical builder/reviewer document map | complete |
| `QA_GATES.md` | QA criteria | complete |
| `SECURITY_GATES.md` | Security criteria | complete |
| `QA_REPORT.md` | Test/smoke evidence | updated with repo-first tests |
| `SECURITY_REVIEW.md` | Security review evidence | complete |
| `DELIVERY_REPORT.md` | Delivery, residual risks, closure | updated with repo-first contract |

## Additional Factory Runtime Contract v1 artifacts

| File | Purpose | Status |
|---|---|---|
| `PROJECT_GLOBAL_VISION.md` | Compact project-level memory and current increment context for Zeus/builders | complete |
| `FACTORY_RUNTIME_CONTRACT_V1.md` | Runtime contract: docs index and commit checkpoint enforcement | complete |
| `BUILDER_CONTEXT_TEMPLATE.md` | Standard context bundle template for Claude Code/Codex/OpenHands assignments | complete |
| `NOTION_UPDATE.md` | Notion page creation/update evidence | complete: page verified and project completed |
| `REFERENCE_REPOS.md` | Local external workflow/process reference pack for n8n, Temporal, Prefect, LangGraph, BMAD, and spec-kit | complete: local clones captured and retrospective protocol documented |
| `FACTORY_RUNTIME_EVOLUTION_PLAN.md` | Concrete step-by-step plan to reconcile the canonical Factory Runtime Evolution project and fix the current delivery_hold absorbing-state class structurally | INC-0001 execution in progress |
| `RETROSPECTIVE_INC_0001.md` | Retrospective and reference-pattern evidence for the delivery_hold autoresolvable blocker fix | complete |
| `RETROSPECTIVE_INC_0008.md` | Retrospective, cron ownership audit, and acceptance evidence for canonical cron/control-plane restoration | in progress |
| `INC_0009_FACTORY_DOCS_NOTION_CONTROL_PLANE_REFACTOR.md` | Jean-requested remediation scope for documentation-first enforcement, canonical Notion metadata linking, active-run terminal-state repair, and CRM review freeze | kickoff scope created; implementation pending |
| `TRACKER.md` / `DELIVERY_REPORT.md` / `QA_REPORT.md` | Increment ledger, delivery evidence, and QA evidence including INC-0007 single-writer/manual takeover guard, INC-0008 cron/control-plane restoration, and INC-0009 docs/Notion/runtime refactor | update required for INC-0009 |

## Source-of-truth hierarchy

1. Agent Core Postgres `factory.*` — operational status, tasks, gates, runs, events, alerts.
2. Repo artifacts — methodology documents and evidence, indexed from this file.
3. Git commits — historical checkpoint that preserves the project record.
4. Notion/dashboard — human PM/reporting projection.
5. Chat/tool output — execution transcript and live verification.

## Builder reading order

1. `DOCUMENTATION_INDEX.md`
2. `PROJECT_GLOBAL_VISION.md`
3. `FACTORY_RUNTIME_CONTRACT_V1.md`
4. `PRD.md`
5. `ADRS.md`
6. `TECHNICAL_BLUEPRINT.md`
7. `SPRINT_PLAN.md`
8. `TASK_GRAPH.md`
9. Task-specific prompt/acceptance criteria from Factory DB

## Correction note

The first closure attempt used Notion/docs waivers. That was not canonical. The current correction adds runtime checks so future Factory projects cannot silently skip documentation indexing or commit checkpoints.

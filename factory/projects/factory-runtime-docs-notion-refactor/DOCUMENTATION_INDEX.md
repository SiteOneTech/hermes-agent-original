# Documentation Index — Factory Runtime Docs/Notion Control-Plane Refactor

Project: `factory-runtime-docs-notion-refactor`
Created: 2026-06-09T23:05:00Z
Updated: 2026-06-10T00:00:00Z
Source of truth: Agent Core Postgres `factory.*` + versioned repo Markdown artifacts.
PM projection: Notion is important for human/directive visibility, but it is not the source of truth unless Jean explicitly marks it mandatory for a specific project.

## Required project-local artifact pack

| File | Purpose | Status |
|---|---|---|
| `FACTORY_INTAKE.md` | Intake, trigger, scope | complete |
| `PRD.md` | Requirements and acceptance criteria | complete |
| `ADRS.md` | Architecture/method decisions | complete |
| `METHODOLOGY_PLAN.md` | Hybrid methodology and gate order | complete |
| `TECHNICAL_BLUEPRINT.md` | Runtime components and contracts | complete |
| `SPRINT_PLAN.md` | Sprint/story plan | complete |
| `TASK_GRAPH.md` | Task dependencies | complete, but marked for hotfix reconciliation |
| `TRACKER.md` | Human-readable task tracker | complete, but marked for hotfix reconciliation |
| `QA_GATES.md` | QA gates | complete |
| `SECURITY_GATES.md` | Security gates | complete |
| `QA_REPORT.md` | QA evidence | complete |
| `SECURITY_REVIEW.md` | Security evidence | complete |
| `DELIVERY_REPORT.md` | Delivery/GO report | complete, but acceptance is HOLD pending HOTFIX-0001 |
| `QUALITY_REVIEW.md` | Independent quality review | complete, but contains stale pre-hotfix notes to reconcile |
| `NOTION_UPDATE.md` | Notion PM projection/update evidence | complete as human PM projection; not canonical truth |
| `HOTFIX_0001_DOCUMENTARY_SOURCE_OF_TRUTH_GATE.md` | Hotfix contract for G1 document readiness gate and Notion projection semantics | open |

## G1 blocking documents for future non-trivial Factory projects

HOTFIX-0001 introduces a stricter G1 Documentary Readiness Gate. The blocking document set should be represented first-class in the runtime and UI/API, not inferred from prose only:

| Document | Category | Required before implementation |
|---|---|---:|
| `FACTORY_INTAKE.md` | G1 required | yes |
| `REQUIREMENTS_ANALYSIS.md` | G1 required | yes |
| `PATTERN_ANALYSIS.md` | G1 required | yes |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | G1 required | yes |
| `PRD.md` | G1 required | yes |
| `ADRS.md` | G1 required | yes |
| `METHODOLOGY_PLAN.md` | G1 required | yes |
| `TECHNICAL_BLUEPRINT.md` | G1 required | yes |
| `SPRINT_PLAN.md` | G1 required | yes |
| `TASK_GRAPH.md` | G1 required | yes |
| `TRACKER.md` | G1 required | yes |
| `QA_GATES.md` | G1 required | yes |
| `SECURITY_GATES.md` | G1 required or explicit N/A | yes |
| `DOCUMENTATION_INDEX.md` | G1 required | yes |

Lifecycle documents such as `QA_REPORT.md`, `SECURITY_REVIEW.md`, `QUALITY_REVIEW.md`, `DELIVERY_REPORT.md`, `NOTION_UPDATE.md`, change records, and retrospectives may be created/updated during execution by their responsible roles, then become required for their later gates.

## Builder reading order

1. `DOCUMENTATION_INDEX.md`
2. `HOTFIX_0001_DOCUMENTARY_SOURCE_OF_TRUTH_GATE.md` when working this hotfix
3. `FACTORY_INTAKE.md`
4. `PRD.md`
5. `ADRS.md`
6. `METHODOLOGY_PLAN.md`
7. `TECHNICAL_BLUEPRINT.md`
8. `SPRINT_PLAN.md`
9. `TASK_GRAPH.md`
10. Factory DB task acceptance criteria

## Source-of-truth rule

Factory DB + repo Markdown artifacts are canonical. Notion is a human PM projection, executive status surface, project register, and quick-link hub. Missing/stale Notion should be visible to humans as PM projection drift, but it must not become a default technical dispatch/readiness blocker unless Jean explicitly requires Notion for that specific project.

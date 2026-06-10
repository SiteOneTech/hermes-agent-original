# Documentation Index — Factory Runtime Docs/Notion Control-Plane Refactor

Project: `factory-runtime-docs-notion-refactor`
Created: 2026-06-09T23:05:00Z
Updated: 2026-06-10T03:22:08Z
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
| `TASK_GRAPH.md` | Task dependencies | complete; reconciled by H4 to match Factory DB |
| `TRACKER.md` | Human-readable task tracker | complete; reconciled by H4 — H1/H2/H3 marked done, H4 in_progress |
| `QA_REPORT.md` | QA evidence | complete; R3/R4/R5 done |
| `SECURITY_REVIEW.md` | Security evidence | complete — GREEN, no blocking findings |
| `DELIVERY_REPORT.md` | Delivery/GO report | superseded; marked historical — HOTFIX-0001 H5 owns active delivery gate |
| `QUALITY_REVIEW.md` | Independent quality review | complete; stale INC-0001 next-action items removed by H4 |
| `NOTION_UPDATE.md` | Notion PM projection/update evidence | complete as human PM projection; not canonical truth |
| `HOTFIX_0001_DOCUMENTARY_SOURCE_OF_TRUTH_GATE.md` | Hotfix contract for G1 document readiness gate and Notion projection semantics | open; H4 reconciliation in progress |

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

## HOTFIX-0001 H1 implementation evidence

- Code: `hermes_cli/factory_pg.py` defines `G1_BLOCKING_DOCUMENTS`, `LIFECYCLE_DOCUMENTS`, `PM_PROJECTION_DOCUMENTS`, `project_document_status(project)`, and injects per-project `document_status` into `status()` payloads.
- Tests: `tests/hermes_cli/test_factory_control_plane_refactor.py` covers category split, missing/indexed/uncommitted G1 blockers, negated review text, Notion-optional implementation preflight, and status payload exposure.
- Verification command: `python -m pytest tests/hermes_cli/test_factory.py tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_cron_control_plane.py tests/tools/test_factory_tools.py -q` → 36 passed, 1 warning.
- Current artifact reconciliation note: this project intentionally still shows G1 document blockers for missing/unstamped analysis docs; H4 owns artifact reconciliation and must not be collapsed into H1.

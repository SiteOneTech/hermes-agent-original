# Documentation Index — Factory Runtime Docs/Notion Control-Plane Refactor

Project: `factory-runtime-docs-notion-refactor`
Created: 2026-06-09T23:05:00Z
Updated: 2026-06-10T17:29:32Z
Source of truth: Agent Core Postgres `factory.*` + versioned repo Markdown artifacts.
PM projection: Notion is important for human/directive visibility, but it is not the source of truth unless Jean explicitly marks it mandatory for a specific project.

## Required G1 project-local artifact pack

All G1 documents below are required before normal implementation dispatch. Readiness means: exists, indexed here, committed in the canonical repo path, validated, and reviewed.

| File | Purpose | Category | Readiness |
|---|---|---|---|
| `FACTORY_INTAKE.md` | Intake, trigger, scope | G1 required | Validated: yes; Reviewed: yes |
| `REQUIREMENTS_ANALYSIS.md` | User/business requirements analysis | G1 required | Validated: yes; Reviewed: yes |
| `PATTERN_ANALYSIS.md` | Existing patterns and reusable design decisions | G1 required | Validated: yes; Reviewed: yes |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | Assumptions, decisions, unresolved questions | G1 required | Validated: yes; Reviewed: yes |
| `PRD.md` | Requirements and acceptance criteria | G1 required | Validated: yes; Reviewed: yes |
| `ADRS.md` | Architecture/method decisions | G1 required | Validated: yes; Reviewed: yes |
| `METHODOLOGY_PLAN.md` | Hybrid methodology and gate order | G1 required | Validated: yes; Reviewed: yes |
| `TECHNICAL_BLUEPRINT.md` | Runtime components and contracts | G1 required | Validated: yes; Reviewed: yes |
| `SPRINT_PLAN.md` | Sprint/story plan | G1 required | Validated: yes; Reviewed: yes |
| `TASK_GRAPH.md` | Task dependencies | G1 required | Validated: yes; Reviewed: yes |
| `TRACKER.md` | Human-readable task tracker | G1 required | Validated: yes; Reviewed: yes |
| `DOCUMENTATION_INDEX.md` | Entry point and source-of-truth map | G1 required | Validated: yes; Reviewed: yes |
| `QA_GATES.md` | QA gate definitions and acceptance evidence model | G1 required | Validated: yes; Reviewed: yes |
| `SECURITY_GATES.md` | Security gate definitions and waiver model | G1 required | Validated: yes; Reviewed: yes |

## Lifecycle and PM projection artifacts

Lifecycle artifacts are created/updated during execution and become required for their phase gates. PM projection artifacts support human visibility but are not execution truth by default.

| File | Purpose | Category | Status |
|---|---|---|---|
| `QA_REPORT.md` | QA evidence | lifecycle | complete; R3/R4/R5 done |
| `SECURITY_REVIEW.md` | Security evidence | lifecycle | complete — GREEN, no blocking findings |
| `QUALITY_REVIEW.md` | Independent quality review | lifecycle | complete; stale INC-0001 next-action items removed by H4 |
| `DELIVERY_REPORT.md` | Final delivery record for INC-0001/HOTFIX/H6 | lifecycle | complete; H6 GREEN |
| `NOTION_UPDATE.md` | Notion PM projection/update evidence | PM projection | complete as human PM projection; not canonical truth |
| `HOTFIX_0001_DOCUMENTARY_SOURCE_OF_TRUTH_GATE.md` | Hotfix contract for G1 document readiness gate and Notion projection semantics | lifecycle/reference | complete |
| `HOTFIX_0001_H5_DELIVERY_REVIEW.md` | H5 delivery review and Jean GO/NO-GO | lifecycle/reference | superseded by H6 canonical landing |

## Builder reading order

1. `DOCUMENTATION_INDEX.md`
2. `FACTORY_INTAKE.md`
3. `REQUIREMENTS_ANALYSIS.md`
4. `PATTERN_ANALYSIS.md`
5. `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`
6. `PRD.md`
7. `ADRS.md`
8. `METHODOLOGY_PLAN.md`
9. `TECHNICAL_BLUEPRINT.md`
10. `SPRINT_PLAN.md`
11. `TASK_GRAPH.md`
12. `QA_GATES.md`
13. `SECURITY_GATES.md`
14. Factory DB task acceptance criteria
15. `HOTFIX_0001_DOCUMENTARY_SOURCE_OF_TRUTH_GATE.md` when working this hotfix lineage

Every Factory worker must also load/obey `factory-agent-operating-canon` in addition to its role-specific skills.

## Source-of-truth rule

Factory DB + repo Markdown artifacts are canonical. Notion is a human PM projection, executive status surface, project register, and quick-link hub. Missing/stale Notion should be visible to humans as PM projection drift, but it must not become a default technical dispatch/readiness blocker unless Jean explicitly requires Notion for that specific project.

## HOTFIX/H6 implementation evidence

- Code: `hermes_cli/factory_pg.py` defines `G1_BLOCKING_DOCUMENTS`, `LIFECYCLE_DOCUMENTS`, `PM_PROJECTION_DOCUMENTS`, `project_document_status(project)`, injects per-project `document_status` into `status()` payloads, and adds document-status snapshots to delivery/critical-readiness gates.
- Dispatch: `scripts/factory/factory_orchestrator_tick.py` injects the G1 document entry point, document-status summary, and common Factory skill requirement into worker prompts.
- Agent skill: `skills/software-development/factory-agent-operating-canon/SKILL.md` is the shared operating canon for all Factory roles.
- Dashboard: `/api/factory/status` and the Factory page expose G1 readiness, blocking documents, and per-file flags.
- Tests: `tests/hermes_cli/test_factory_control_plane_refactor.py` covers category split, missing/indexed/uncommitted G1 blockers, Notion-optional implementation preflight, status payload exposure, and gate snapshots.

# Factory Tracker — Agent Core Follow-up / Reminders

## Project

- Project ID: `agent-core-followup-reminders`
- Name: Agent Core Personal CRM / Follow-up / Reminders
- Source of truth: Agent Core Postgres `zeus_agent.factory`
- Repo: `/home/jean/Projects/hermes-agent-original`
- Remote: `https://github.com/SiteOneTech/hermes-agent-original`
- Lane: `agent-core-followup-hybrid`
- Methodology: `hybrid`
- Human owner: Jean García

## Correction note — F0 rework

Reviewer correctly blocked F0 because project-local artifacts contained unrelated project content and the project skill existed only in `factory-reporter` profile. Jean explicitly authorized cross-profile correction in the new thread. This tracker now records the corrected project-local artifacts and skill propagation as the F0 rework package for independent re-review.

## Canonical artifacts

- `docs/followup-reminder-core/FACTORY_SPEC-001-agent-core-followup-reminders.md`
- `docs/followup-reminder-core/ADR-002-universal-activity-layer.md`
- `docs/crm-capability/PRD-001-agent-crm-core.md`
- `docs/calendar-capability/ADR-001-agent-first-calendar-adapter.md`
- Project-local docs: this directory.
- Runtime skill: `agent-core-followup-reminders` under each assigned worker/reviewer profile.

## F3 evidence log — `run-1780704556-afaa1d6b`

- Owner: `implementation-planner`; reviewer esperado: `factory-orchestrator`.
- Archivos completados: `IMPLEMENTATION_PLAN.md`, `TASK_GRAPH.md` (actualizado), `F3_EVIDENCE.md`, este tracker.
- Plan entregado: 30+ sub-tareas para F4-F8 con paths exactos, comandos de verificación, owners, reviewers y gates.
- Gate blocker: `architecture=pending` (F2 pendiente `security-reviewer`); F4 no puede iniciar hasta que `security-reviewer` registre `architecture=passed`.
- Handoff: `claude-builder` recibe F4/F5 cuando gates `planning` y `architecture` estén ambos `passed`.
- Gate request: `planning=pending` solicitado a `factory-orchestrator` para este incremento.

## Current gate status

| Gate | Status | Notes |
|---|---|---|
| intake | passed | F0 reviewed and recorded in Factory DB |
| functional | passed | F1 PRD/FUNCTIONAL_SPEC/ACCEPTANCE_CRITERIA reviewed and gate recorded |
| architecture | passed | F2 ADR/data model reviewed by `security-reviewer` |
| planning | passed | F3 implementation plan reviewed by `factory-orchestrator` |
| implementation | in_progress | F4 migration implemented; pending independent implementation review |
| quality/test | pending | F9 |
| security | pending | F10 |
| delivery | pending | F11 |

## Task graph summary

| Task | Owner | Reviewer | Phase | Status |
|---|---|---|---|---|
| F0 — Factory kickoff, tracker, and skill assignment | factory-reporter | product-analyst | intake | done |
| F1 — Full functional PRD | product-analyst | solution-architect | functional | done |
| F2 — Architecture ADR/data model | solution-architect | security-reviewer | architecture | done |
| F3 — Implementation plan/task graph | implementation-planner | factory-orchestrator | planning | done |
| F4 — DB migrations/runtime grants | claude-builder | codex-builder | implementation | review_ready |
| F5 — Activity/follow-up tools/toolset | claude-builder | quality-reviewer | implementation | blocked — waiting F4 review |
| F6 — Calendar bridge/dispatcher | claude-builder | devops-release | implementation | blocked — waiting F5 |
| F7 — Plans/chaining/recurrence/quick capture | claude-builder | product-analyst | implementation | blocked — waiting F5 |
| F8 — CRM compatibility/no duplicates | claude-builder | quality-reviewer | implementation | blocked — waiting F7 |
| F9 — QA regression/smoke | qa-verifier | quality-reviewer | qa | blocked — waiting F8 |
| F10 — Security/privacy/tool-boundary review | security-reviewer | solution-architect | security | blocked — waiting F9 |
| F11 — Delivery docs/reconciliation | factory-reporter | devops-release | delivery | blocked — waiting F10 |

## Required skills

- `agent-core-followup-reminders`
- `agent-core-functional-modules`
- `agent-crm-core`
- `calendar-agenda-queries`
- `software-factory-orchestration`
- `test-driven-development`
- `requesting-code-review`
- `github-pr-workflow` where release/PR work is involved

## Operating notes

- No Kanban bridge.
- Notion is human documentation only if available; Factory DB remains canonical.
- Project should stay autonomous while `autonomous_enabled=true` and cron/tick jobs are active.

## F1 evidence log — `run-1780701420-04edba37`

- Owner: `product-analyst`; reviewer pending: `solution-architect`.
- Files completed: `PRD.md`, `FUNCTIONAL_SPEC.md`, `ACCEPTANCE_CRITERIA.md`, `FACTORY_INTAKE.md`, `F1_EVIDENCE.md`, this tracker.
- Factory DB readback: `./hermes factory status agent-core-followup-reminders --json` returned `db_backend=agent_core_postgres`, database `zeus_agent`, F0 `done`, F1 `running`/functional with evidence initially missing.
- Factory gate record: `functional=pending`, `gate_id=162`, reviewer `solution-architect`, notes point to F1 artifacts and state that product-analyst is not self-approving.
- Functional scope includes personal CRM, business CRM, reminders, calendar scheduling, timelines, follow-up chains, quick capture, next-actions, duplicate prevention, side-effect boundaries, dispatcher and privacy/tool-boundary requirements.
- Gate handling: product analyst may record `functional=pending` for independent review but must not mark it passed.
- Next action: `solution-architect` reviews F1 functional gate; after pass, F2 produces final architecture ADR/data model.

## F2 evidence log — `run-1780702957-7f740456`

- Owner: `solution-architect`; reviewer pending: `security-reviewer`.
- Files completed: `docs/followup-reminder-core/ADR-002-universal-activity-layer.md`, `TECHNICAL_BLUEPRINT.md`, `ARCHITECTURE_DECISIONS.md`, `ADRS.md`, `F2_EVIDENCE.md`, this tracker.
- Architecture decision: new Agent Core Postgres schema `activity.*`; no separate DB/service/graph DB; no UI-first platform.
- Data model delivered: `activities`, `activity_links`, `reminder_rules`, `activity_events`, `activity_plans`, `activity_plan_steps`, `activity_plan_runs`, `activity_plan_run_steps`, `recurrence_rules`, optional `recurrence_instances`.
- Compatibility boundaries: preserve `crm.follow_ups`/`crm_*` via F8 bridge; preserve Calendar Core and use `calendar_*` only for scheduling/time-block side effects.
- Dispatcher boundary: deterministic DB scan and notification-ready output, no chat-memory dependency and no external sends before security/channel approval.
- Gate handling: solution architect did not self-approve; architecture gate is recorded/submitted as `pending` for independent `security-reviewer`.
- Next action: `security-reviewer` reviews F2 ADR/data model and records architecture gate pass/fail; then F3 can plan implementation tasks.

## F3 evidence log — `run-1780713290-73c13049` (second rework)

- Owner: `implementation-planner`; reviewer: `factory-orchestrator`.
- Run type: rework (segunda iteracion).
- Contexto: el primer rework (`run-1780712703-2092c8a2`) falló en 5 puntos: F9/F10/F11 no descompuestos, owner/reviewer faltantes en F4.3-F8.3, typo `clude-builder`.
- Archivos actualizados: `TASK_GRAPH.md` (F9-F11 completos + owner/reviewer/table rows en todas las sub-tareas), `IMPLEMENTATION_PLAN.md` (F9-F11 fases + typo corregido), `F3_EVIDENCE.md` (este), `TRACKER.md` (F8 owner/reviewer corregido).
- AC verificados: (1) task graph descompone todos los incrementos con verification commands; (2) ninguna tarea tiene owner=reviewer; (3) delivery evidence y gates completos para F9-F11.
- Gate request: `planning=pending` solicitado a `factory-orchestrator`.
- Handoff: `claude-builder` recibe F4 cuando gates `planning` y `architecture` estén ambos `passed`.
- Siguiente accion: `factory-orchestrator` revisa y registra `planning=passed` o `planning=failed`.

## F4 evidence log — `run-1780714503-b487c761`

- Owner: `claude-builder`; reviewer esperado: `codex-builder`.
- Files completed: `db/modules/activity/000001_activity_schema.sql`, `db/agent-core/000002_runtime_roles.sql`, `F4_EVIDENCE.md`, `DOCUMENTATION_INDEX.md`, this tracker.
- Migration delivered: schema `activity`, module registry rows, `activity_runtime` role/grants, activities/links/reminders/audit/plans/recurrence structures and indexes.
- Verification: isolated Docker Postgres applied Agent Core core migrations, CRM migrations, then Activity migration twice with `ON_ERROR_STOP=1`; readback showed 10 activity tables, module registry row, runtime grants, required indexes, and unchanged `crm.follow_ups` columns.
- Gate request: implementation evidence submitted as `pending`, `gate_id=173`, for independent review; worker did not apply migration directly to production DB and did not self-approve.
- Siguiente accion: `codex-builder` reviews F4 SQL and records implementation gate pass/fail.

# Factory Runtime Evolution — FACTORY_INTAKE

**Project ID:** `factory-runtime-evolution`
**Methodology:** Hybrid
**Source of truth:** Agent Core Postgres `zeus_agent.factory.*`
**Repo:** `/home/jean/Projects/hermes-agent-original`
**Human owner:** Jean García
**Orchestrator:** Zeus

## Trigger

Jean reported that autonomous Factory projects stayed blocked for hours while Zeus did not escalate or self-repair. The audit found that cron jobs were green but blind/ineffective: blocked projects could be skipped by dispatch, false human blockers were not escalated, and impossible in-flight states could absorb work.

## Scope

Implement three runtime remediations:

1. `factory_blocker_detector.py` must classify blockers and create actionable records:
   - `auto_resolvable`
   - `technical_rework`
   - `human_question_required`
   - `stale_orphan_state`

2. Dashboard/cron must alert when:
   - an autonomous project remains `blocked` longer than threshold
   - a project has blocked tasks but `human_questions = 0`
   - a task is `review_running`/`running` without active `task_run`
   - cron is ok but `claimed=null` for repeated rounds

3. Dispatcher must act on `blocked` projects where safe:
   - repair orphan states
   - reopen resolved blockers
   - continue independent runnable tasks when dependencies allow

## Non-goals

- Do not move Factory truth to Kanban.
- Do not add ad-hoc SQLite fallback.
- Do not create noisy notification spam every cron tick.
- Do not ask Jean to approve routine tests or internal runtime decisions.

## Success criteria

- Blockers are classified with deterministic action category and next action.
- Indispensable human decisions create `human_questions` and alert Jean via configured delivery surfaces.
- Blocked autonomous projects are not ignored by the dispatcher.
- Tests cover classification, alerts, and blocked-project dispatch behavior.
- Live smoke verifies Agent Core Postgres is used.

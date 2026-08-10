# Technical Blueprint — Factory Runtime Evolution — Continuation

| Field | Value |
|---|---|
| Document status | validated:true (implementation-planner, 2026-08-10); reviewed:true (solution-architect, 2026-08-10, planning gate 690) |
| Baseline | Worktree at `20228c116` (origin/main), files cited with line numbers are current at baseline. |

## 1. Current-state architecture (boundaries)

### 1.1 Control-plane modules
- `hermes_cli/factory_contracts.py` — closed enums/sets; G0 strategy builders; terminal
  task statuses; dispatchable project statuses.
- `hermes_cli/factory_pg.py` — operational layer over Agent Core Postgres `factory.*`
  (projects, lanes, tasks, task_runs, gates, events, human_questions, alerts).
- `hermes_cli/factory_backend.py`, `hermes_cli/factory_catalog.py` — backend selection
  (Postgres only for control-plane scripts) and CLI catalog.
- `scripts/factory/*` — repo-backed cron scripts (L1 tick, L2 blocker detector, watchdog,
  status sync, reviewer dispatch).
- `web/src/pages/FactoryPage.tsx` — dashboard projection (renders
  `manual_attention` as "requiere atención manual", line 161).

### 1.2 Key flow: blocked autonomous project (today)
```
L1 tick / dashboard resolve
  → monitor_runs() (factory_pg.py:4444)          # finalize stale runs, orphan repair
  → clear_resolved_blockers() (line ~3760)        # gate/structured blockers resolved
  → supervisor_health_check() (line 4523)
       ├─ pending_questions present? → mark_project_manual_attention("pending_human_question")  # line 4584-4586  ⚠ GAP
       └─ else: classify_factory_blockers() (line 3291)
                → record_factory_blocker_actions(create_questions=True) (line 3312)
                → _supervisor_requeue_technical_blockers() (line 3423, bounded by SUPERVISOR_TECHNICAL_REWORK_MAX_RETRIES=2)
                → mark_project_manual_attention("human_question_required" | "technical_rework_retries_exhausted") (line 4592-4595)
  → watchdog (line 3523) alerts if still blocked > 60 min or blocked without question
```

### 1.3 Data contracts
- `factory.human_questions`: question_id (uuid5 per task), project_id, task_id, severity,
  question, options (jsonb), asked_via, status (`pending`/`open`/…), metadata
  (`alert_key`, `classification`, `human_question_source` =
  `blocker_result_summary` | `classifier_fallback`).
- `factory.projects.metadata`: repo_strategy, manual_attention_required/reason/blockers,
  pause_kind, reconciliation_anomalies, superseded_by_project_id (on close).
- `factory.tasks.metadata`: last_blocker_classification, supervisor_rework*,
  reopened_by/reopen_reason (reconciler), administrative_closure.

## 2. Target architecture (downstream increments)

### 2.1 Question lifecycle (FRE-011) — `factory_pg.py` + `factory_contracts.py`
- New closed statuses: `QuestionStatus { PENDING, OPEN, ANSWERED, STALE, RETIRED }`.
- New metadata on question rows: `retired_reason`, `retired_at`, `retired_by`,
  `escalation_category`.
- New function `retire_human_questions(project_id, ...) -> {retired, requeued, events}`:
  - `stale`: task not blocked anymore, or blocker resolved, or age > TTL (default 24 h,
    Q2) → status=stale + event `human_question_retired` (reason=stale).
  - `generic`: validation (ADR-010-4) finds no concrete question/options → retired with
    reason=generic + task requeued as `rework` (bounded) via existing
    `_supervisor_requeue_technical_blockers` path.
  - `self_generated`: metadata `human_question_source` in
    {blocker_result_summary, classifier_fallback} AND no verified evidence fields →
    retired with reason=self_generated + task requeued.
- Supervisor order change (ADR-010-2): call `retire_human_questions` BEFORE the
  `pending_questions → manual_attention` branch; the branch then only fires for
  validated, fresh questions (or keeps the project in `blocked`/`active` with the
  question as the single explainable state).

### 2.2 Escalation validation (FRE-012) — `factory_contracts.py` + `factory_pg.py`
- New closed enum `JeanEscalationCategory` (five values; ADR-010-4).
- `validate_human_question(question_row) -> {valid, category, evidence_ok, reason}`
  fail-closed validator: requires category ∈ enum, question text non-empty, options
  non-empty, evidence fields present (e.g. `evidence_refs` jsonb array).
- Classifier mapping: `_human_decision_details_from_text` becomes draft-only; the
  question row is only created after validation, with `escalation_category` stored.
- `mark_project_manual_attention()` gains a `category` param; it refuses
  `manual_attention` when category is missing/invalid (returns `{escalation: rejected}`)
  — the caller then stays on the autonomous repair path.

### 2.3 Continuation/reopen (FRE-014) — `factory_pg.py` + CLI + intake
- New function `reopen_project(project_id, *, reason, actor, lineage_ok=True)`:
  - Preflight: project status ∈ {completed, accepted} (Q1 default), metadata
    `lineage`/`continuation_of` or explicit flag; G0 strategy passed; artifact dir
    exists; required docs indexed.
  - Transition: insert `reopen` gate (passed after preflight), metadata
    `{continuation_of: <previous> | self, reopened_at, reopened_by, reopen_reason}`,
    status → `active`, autonomous_enabled → true, lanes → active, event
    `project_reopened`.
  - Cancelled/superseded: require explicit Jean approval (existing gate path).
- New CLI: `hermes factory project reopen <project_id> [--reason ...]` registered in the
  factory CLI catalog; dashboard optional later.
- Intake lineage check (P4): in `factory_project_create` path, when a terminal project
  with matching `lineage` exists, return `{suggest: reopen, project_id}` instead of
  silently creating a successor (fail-closed: orchestrator must decide).

### 2.4 Watchdog/cron integration (FRE-013/017)
- `factory_watchdog_alerts()` output consumed by `factory_blocker_detector.py` report and
  status sync unchanged in shape (already aligned); add `supervisor_summary` field
  (invariant/action/result/next) from `supervisor_health_check` into the detector report.
- Global cron pass: incremental resume with smoke evidence per script
  (`hermes cronjob list` after each), wrapper discipline preserved, no alert loops
  (60-min event dedup + idle silence).

## 3. Test surface (RED anchors for downstream increments)

| Increment | RED test (new/updated) |
|---|---|
| FRE-011 | `tests/hermes_cli/test_factory_control_plane_refactor.py` — replace `test_supervisor_moves_existing_human_question_to_manual_attention` with: stale question → retired + task requeued, NO manual_attention; generic question → retired; add `test_question_lifecycle_stale_retirement` |
| FRE-012 | new `tests/hermes_cli/test_factory_escalation_validation.py` — invalid category fails closed; draft without options never creates a row; manual_attention refused without category |
| FRE-013 | `tests/hermes_cli/test_factory_cron_control_plane.py` — detector report includes supervisor_summary; watchdog silent when idle |
| FRE-014 | new `tests/hermes_cli/test_factory_project_reopen.py` — completed+lineage reopens; cancelled requires approval; preflight failure keeps terminal |
| FRE-015/016 | reviewer evidence + PR checks (branch pushed, diff scoped, docs updated) |
| FRE-017 | cron smoke evidence file + `hermes cronjob list` assertions (script-level, not unit) |

## 4. Non-goals / guardrails (technical)

- No schema migration in FRE-011/012 unless proven necessary (status values + metadata
  on existing tables first; migration path exists via `db/modules/factory/*`).
- No new `HERMES_*` env vars; config via `config.yaml` when needed (NFR-6).
- Factory DB writes only through canonical CLI/tools; no ad-hoc SQL (hard rule).
- Single-active-increment guard, manual-takeover lease, and autonomy-off for
  terminal/manual_attention states remain unchanged.

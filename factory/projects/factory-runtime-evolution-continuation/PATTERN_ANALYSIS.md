# Pattern Analysis — Factory Runtime Evolution — Continuation

| Field | Value |
|---|---|
| Document status | validated:true (implementation-planner, 2026-08-10); reviewed:true (solution-architect, 2026-08-10, planning gate 690) |
| Method | Static analysis of `hermes_cli/factory_pg.py`, `hermes_cli/factory_contracts.py`, `scripts/factory/*` at commit `20228c116` (worktree base), plus Factory DB evidence (`hermes factory status --json`) and predecessor project artifacts. |

## 1. Current runtime anatomy (verified boundaries)

### 1.1 Closed-state contracts — `hermes_cli/factory_contracts.py`
- `ProjectStatus` closed set: intake, planned, active, blocked, manual_attention, paused,
  delivery_hold, completed, accepted, cancelled, superseded.
- `TaskStatus`, `RunStatus`, `GateStatus`, `FactoryInvariant`
  (`RED_DELIVERY_HOLD_WITH_BLOCKED_WORK`, `RED_AUTONOMOUS_WITHOUT_RUNNABLE_WORK_OR_QUESTION`,
  `RED_ORPHAN_INFLIGHT_WITHOUT_ACTIVE_RUN`).
- `TERMINAL_TASK_STATUSES`, `IN_FLIGHT_TASK_STATUSES`, `RUNNABLE_TASK_STATUSES`,
  `DISPATCHABLE_PROJECT_STATUSES`.
- G0 repository strategy builders (`build_repository_strategy`, aliases, canonical repos).

### 1.2 L1 mechanical tick — `scripts/factory/factory_orchestrator_tick.py` + `factory_pg.py`
- `monitor_runs()` (`factory_pg.py:4444`): finalizes runs from `exit_code.txt` or final
  semantic markers; repairs orphan in-flight tasks; synthesized failure for dead workers.
- Dispatch/claim predicates enforce: single active increment, single active project,
  manual-takeover lease guard (`_manual_takeover_dispatch_filter` line 3031), autonomy
  off for terminal/manual_attention states (`_project_status_forces_autonomy_off`).
- The current run `run-1786340791-ee6589a6` was claimed by `factory-force-tick` with
  metadata `spawned_by: factory_orchestrator_tick` — the tick is live.

### 1.3 L2 supervisor — `supervisor_health_check()` `factory_pg.py:4523`
- Evaluates: blocked-without-runtime, delivery_hold+blocked, autonomous without runnable
  work or question.
- Repair path (line 4575+): `clear_resolved_blockers` → `classify_factory_blockers` →
  `record_factory_blocker_actions(create_questions=True)` → requeue technical blockers
  (bounded, `_supervisor_requeue_technical_blockers` line 3423) → only then
  `mark_project_manual_attention`.
- **Critical branch (line 4584–4586):** `if pending_questions: mark_project_manual_attention(reason="pending_human_question")`
  — runs BEFORE the requeue logic and with NO re-validation of the question. This is the
  premature-escalation path.

### 1.4 Blocker classifier — `classify_factory_blocker()` `factory_pg.py:3205`
Taxonomy (priority order):
1. `stale_orphan_state` (in-flight without active run) → repair, no human.
2. `human_question_required` — ONLY when `_human_decision_details_from_text()` extracts a
   concrete `JEAN_QUESTION` + options from the task text (source `blocker_result_summary`);
   or specific `_BLOCKER_EXTERNAL_OWNER_PHRASES`.
3. `technical_rework` — concrete technical failure keywords win over generic phrases.
4. `auto_resolvable` — resolved-gate mentions or `_BLOCKER_AUTO_KEYWORDS`.
5. `unactionable_legacy_human_reference` — bare phrases like "requires a human decision"
   without concrete JEAN_QUESTION are classified as technical_rework/auto_resolvable
   (line 3252–3260). This is the already-shipped partial hardening.
6. `unclassified` → technical_rework if blocked.

`record_factory_blocker_actions()` (line 3312): persists `last_blocker_classification` on
the task, emits `blocker_classified` events (60-min dedup), creates human questions ONLY
when `requires_human` AND explicit question text exists (else event
`human_question_skipped_unactionable`). Dedup: one pending question per task.

### 1.5 Manual attention — `mark_project_manual_attention()` `factory_pg.py:3479`
- Sets `status='manual_attention'`, `autonomous_enabled=false`, `paused_at=now()`,
  metadata `manual_attention_required/Reason/Blockers`, `pause_kind=manual_attention_required`,
  lanes → manual_attention, event `manual_attention_required`.
- Watchdog counts pending questions per project; `factory_watchdog_alerts()` (line 3523)
  alerts for `autonomous_project_blocked_too_long` and `blocked_without_human_question`.

### 1.6 Terminal/reopen boundary
- `TERMINAL_PROJECT_STATUSES` (`factory_pg.py:247`) = {completed, accepted, cancelled,
  superseded, closed}.
- `_resume_preflight_blocker()` (line 4616) returns `terminal_<status>` → resume refused.
- `close_project()` (line 2429) supports `superseded_by_project_id` / `absorbed_into_project_id`
  metadata and a closure gate, but NO reopen/continue operation exists anywhere
  (no `factory_pg` function, no CLI command; verified by symbol search).

### 1.7 Cron boundary (restored in INC-0008)
- `scripts/factory/factory_status_sync.py` (active), `factory_reviewer_dispatch.py`
  (report-only), `factory_blocker_detector.py` (L2), `factory_orchestrator_tick.py` (L1),
  `factory_watchdog_alerts.py`. `~/.hermes/scripts/*` are thin wrappers.
- Non-Factory crons (vapi-postcall-lead-supervisor, customer-intent-supervisor) belong to
  `sitiouno-agent-runtime` and must not be folded into Factory control plane
  (`RETROSPECTIVE_INC_0008.md`).

## 2. Real operational evidence (2026-08-10, Factory DB)

- `hermes factory status factory-runtime-evolution-continuation --json` (48,655 bytes):
  project `active`, anomalies `missing_project_artifact_dir` + `missing_required_docs`,
  `human_questions: []`, `gates: []`, tasks: FRE-010 `running`, R1/R2 `todo`.
- Events 172950–172962 prove the canonical bootstrap: G0 passed at `project_created`;
  reconciler created R1/R2; `autonomous_resume` with `single_active_increment: true`;
  `task_claimed` for this run.
- Predecessor evidence (`factory/projects/factory-runtime-evolution/`):
  - `QA_REPORT.md:227–234` — blocker-detector smoke `classified=0, questions_created=0,
    alerts=0, needs_attention=False`; watchdog `claimed=null` false-positive fix (alertable
    only when runnable work exists and no run is active).
  - `RETROSPECTIVE_INC_0008.md` — cron ownership audit; root cause: `main` lacked
    control-plane modules; canonical fix: repo-backed scripts + wrappers.
  - `TRACKER.md` — INC-0006 (unified resolve-state), INC-0007 (single-writer lease) done;
    INC-0008 in review; INC-0009 requested (docs-first enforcement).
  - `FACTORY_RUNTIME_EVOLUTION_PLAN.md` — L1/L2/L3 loop model and the non-negotiable
    "one explainable state" invariant.
  - Git: `d3d08dc2e` (inc-0009 scope), `bc7ab6af6` (cron control-plane restore).

Paused projects are NOT active incidents: no paused project is treated as a violation in
this diagnosis; the evidence above concerns `active`/terminal states only.

## 3. Failure-mode diagnosis — legacy generic human questions → premature manual_attention

### 3.1 Mechanics (line-level)
1. A blocked task's `result_summary` contains prose that mentions a human-ish decision
   (or an old question row already exists from a prior classifier pass).
2. `classify_factory_blocker()` parses `JEAN_QUESTION` from that prose
   (`_human_decision_details_from_text`, source `blocker_result_summary`) OR reuses the
   existing `factory.human_questions` row — the classifier is text-driven, not
   evidence-verified.
3. `supervisor_health_check()` queries `pending_questions` (line 4542) and, on the very
   next repair pass, hits `if pending_questions:` (line 4584) BEFORE `clear_resolved_blockers`
   results are re-checked and BEFORE the requeue path — `mark_project_manual_attention(
   reason="pending_human_question")` fires.
4. Project leaves the autonomous slot: `autonomous_enabled=false`, status
   `manual_attention`, watchdog stops treating it as autonomous, dashboard shows
   "requiere atención manual" (`web/src/pages/FactoryPage.tsx:161`).
5. Jean receives a question that is either stale (the blocker was already resolved) or
   generic (no concrete decision, no options, no verified external evidence).

### 3.2 Why the existing partial hardening is insufficient
- The classifier already refuses to CREATE unactionable questions
  (`human_question_skipped_unactionable`), and bare "requires human decision" phrases are
  demoted to technical rework. But the supervisor still TRUSTS every existing `pending`
  row unconditionally, with no freshness check (question age, task still blocked?,
  blocker still present?), no retirement path, and no bounded-repair-before-escalation
  ordering (the `pending_questions` branch precedes the requeue branch).
- `human_questions` rows have no lifecycle: rows stay `pending` forever unless answered;
  there is no `stale`/`retired` state and no canonical transition that re-opens the task.

### 3.3 Consequence class
- Premature `manual_attention` monopolizes the single-active slot, generates
  `blocked_without_human_question` / manual-attention alerts, and wastes Jean's attention
  on self-generated noise — exactly the failure Jean's directive forbids.

## 4. Gap diagnosis — continuation/reopen for a terminal self-improvement project

- A self-improvement project (the Factory runtime) is by definition never "done": it must
  remain one living product. Current runtime forces terminal: `factory-runtime-evolution`
  reached `completed`; the orchestrator had no canonical reopen, so it created a detached
  successor (`factory-runtime-evolution-continuation`, event 172950) with a new ID, new
  lanes, new artifact dir, losing the lineage link that `close_project()` metadata
  (`superseded_by_project_id`) is designed to record.
- Gap: no `reopen_project`/`continue_project` operation; `_resume_preflight_blocker()`
  fails closed on terminal statuses (correct for product projects, wrong for a declared
  self-improvement lineage); no lineage-first intake check ("does a terminal project with
  the same lineage exist? reopen it instead of creating a successor").
- Reference patterns: Prefect terminal states + server-owned transitions; LangGraph
  checkpoints/resumability; n8n state-machine discipline (`/home/jean/reference-repos/factory-workflow-patterns`,
  per predecessor `REFERENCE_REPOS.md`).

## 5. Design-pattern conclusions (feed `ADRS.md` / `TECHNICAL_BLUEPRINT.md`)

| # | Pattern decision | Rationale |
|---|---|---|
| P1 | Introduce a human-question lifecycle: `pending → (stale|retired|answered)` with event evidence; retirement requeues the task (bounded) or marks resolved. | FR-2; eliminates absorbing `pending` rows. |
| P2 | Supervisor re-validation step before ANY manual_attention: re-check question freshness, task still blocked, evidence category from the invariant allowlist; else repair/requeue and retire the question. | FR-3; closes the line-4584 bypass. |
| P3 | Reorder supervisor repair: clear → classify → requeue (bounded) → revalidate questions → escalate only on genuine conditions or exhaustion. | FR-1; bounded escalation NFR-5. |
| P4 | Canonical `project reopen/continue` operation with lineage metadata + reopen gate + G0/G1 preflight; intake checks lineage before creating successors. | FR-5; keeps Factory runtime one living product. |
| P5 | Watchdog/cron consume one supervisor-output contract; idle silence; global cron verification increment. | FR-4; INC-0008 continuation. |
| P6 | All changes TDD-first with exact regression tests in `tests/hermes_cli/test_factory_*.py`; PR-first; independent review. | FR-7/FR-8; Factory canon. |

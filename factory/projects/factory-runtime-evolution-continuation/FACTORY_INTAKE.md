# Factory Intake — Factory Runtime Evolution — Continuation

| Field | Value |
|---|---|
| Document status | validated: true (implementation-planner, 2026-08-10); reviewed: false — assigned to `solution-architect` |
| Project ID | `factory-runtime-evolution-continuation` |
| Project name | Factory Runtime Evolution — Continuation |
| Trigger | Jean García directive (2026-08-10): the Factory must treat blocked projects as evidence problems to diagnose, repair, requeue, or dispatch — never as generic/stale/self-generated "human decisions" to bounce back to Jean. |
| Classification | Zeus-only internal Factory functionality (`zeus_only` / `maintain_existing_project`) |
| Predecessor | `factory-runtime-evolution` (terminal: completed). This project is its canonical successor, created because the runtime currently has no reopen/continue operation for terminal projects (see `PATTERN_ANALYSIS.md` §4 and `ADRS.md` ADR-010-3). |
| G0 Repository Strategy | Passed. Primary repo `SiteOneTech/hermes-agent-original`, remote `https://github.com/SiteOneTech/hermes-agent-original`, base branch `main`, branch prefix `factory/factory-runtime-evolution-continuation/`, worktree policy `per_deliverable`. Recorded in Factory DB `project_created` event 172950. |
| Source of truth | Agent Core Postgres `zeus_agent.factory` (operational), repo Markdown under `factory/projects/factory-runtime-evolution-continuation/` (documentary control pack), git (commit checkpoints), Notion (human PM projection only). |
| Delivery boundary | No product-runtime code in the G1 increment. Factory delivers to the functional sandbox (`kidu.app` / `*.kidu.app`) only after explicit gates; production remains HOLD until Jean decides. This project changes Zeus's own runtime control plane (`zeus_only`), not a product surface. |
| Risk level | High (control-plane changes to the autonomous Factory runtime). |

## 1. Why this project exists

`factory-runtime-evolution` reached a terminal state (completed) after INC-0001…INC-0009
delivered the repo-first runtime contract, structured blockers, L1 tick, L2 supervisor
repairs, single-writer/manual-takeover leases, canonical close/resolve actions, and the
repo-backed cron control plane. The durable directive behind the continuation:

> When the Factory encounters a project block, it must inspect concrete
> task/run/gate evidence and autonomously diagnose, repair, requeue, or dispatch
> technical/control-plane work. It must NOT ask Jean to solve generic, stale, or
> self-generated "human decisions." Only independently verified external authority,
> product/business scope, security approval, payment/credential/access, or a bounded
> exhausted repair loop may become an actionable Jean question.

This is a durable invariant of the Factory runtime, not a one-off fix.

## 2. Observed gaps that justify the increment

1. **Legacy generic human questions cause premature `manual_attention`.**
   `supervisor_health_check()` (`hermes_cli/factory_pg.py:4523`) escalates a project to
   `manual_attention` with reason `pending_human_question` whenever ANY pending
   `factory.human_questions` row exists (line 4584–4586) — without re-validating that
   the question is still concrete, that its task is still blocked, or that no
   deterministic repair applies. A stale or generic question created from an old
   `result_summary` (source `blocker_result_summary` / `classifier_fallback`, see
   `record_factory_blocker_actions()` line 3312) therefore takes a project out of the
   autonomous slot and pings Jean prematurely. Full diagnosis: `PATTERN_ANALYSIS.md` §3.
2. **No continuation/reopen path for terminal self-improvement projects.**
   `TERMINAL_PROJECT_STATUSES = {completed, accepted, cancelled, superseded, closed}`
   (`factory_pg.py:247`); `_resume_preflight_blocker()` refuses `terminal_<status>`
   (line 4620); `close_project()` (line 2429) supports `superseded_by_project_id`
   metadata but no reopen/continue operation exists. The Factory therefore spawns
   detached successor projects (this one included) instead of continuing one living
   self-improvement product. Full diagnosis: `PATTERN_ANALYSIS.md` §4.
3. **Watchdog/cron integration is restored but unverified globally.** INC-0008 restored
   repo-backed scripts (`scripts/factory/*`) and wrappers; the blocker detector,
   orchestrator tick, and watchdog crons are reactivable but their global cron
   verification must be re-established with evidence (see `SPRINT_PLAN.md` FRE-013/017).

## 3. Scope

**In scope (this G1 increment, FRE-010):**
- Full G1 documentary control pack under `factory/projects/factory-runtime-evolution-continuation/`
  (14 required documents, this one included), indexed, committed, validated; independent
  review assigned to `solution-architect` (task reviewer).
- Evidence-based diagnosis of the legacy generic-question/manual_attention failure mode.
- Documentation of the continuation/reopen gap and the tick/supervisor/watchdog boundaries.
- A test-first task graph (TDD increments) for durable implementation.

**In scope (downstream increments, planned in `TASK_GRAPH.md`):** generic-question
retirement/rework; direct-human escalation validation; global watchdog/cron integration;
canonical continuation/reopen capability; independent QA/security review; PR-first
delivery; global cron verification.

**Explicitly out of scope (this G1 task):** any product-runtime code change, deploy,
credential change, DB schema migration, or Notion write. No product-runtime code in G1.

## 4. Success criteria

1. All required G1 files exist under `factory/projects/factory-runtime-evolution-continuation/`,
   are indexed in `DOCUMENTATION_INDEX.md`, committed on the assigned branch, and contain
   explicit validated/reviewed state (validated by planner; review assigned to
   `solution-architect`).
2. Documents identify the exact legacy generic-question/manual_attention failure mode,
   the existing global tick/supervisor boundaries, and real operational evidence, without
   treating paused projects as active incidents.
3. `TASK_GRAPH.md` defines small TDD increments for generic-question retirement/rework,
   direct-human escalation validation, global watchdog/cron integration, canonical
   continuation/reopen capability, independent QA/security review, and PR-first delivery.
4. The plan preserves fail-closed G0/G1/security gates and names only genuine conditions
   that can require Jean (see `SECURITY_GATES.md` §Escalation allowlist).

## 5. Intake evidence (real, captured 2026-08-10)

- `hermes factory status factory-runtime-evolution-continuation --json` → project
  `active`, `autonomous_enabled=true`, anomalies `missing_project_artifact_dir` +
  `missing_required_docs`, 14 G1 docs blocking, `human_questions=[]`, `gates=[]`.
- Events 172950–172962: `project_created` (G0 passed), `lane_created` ×2, `task_created`
  (FRE-010), `reconciliation_task_ensured` ×2, `project_reconciled` ×4,
  `autonomous_resume`, `task_claimed` (run `run-1786340791-ee6589a6`, worker
  `implementation-planner`).
- Reconciliation tasks in DB: `factory-runtime-evolution-continuation-reconcile-missing-project-artifact-dir` (R1),
  `factory-runtime-evolution-continuation-reconcile-missing-required-docs` (R2) — both
  `todo`, owned by `factory-reporter`, reviewed by `factory-orchestrator`. These close
  automatically once the artifact dir exists and the docs are committed.

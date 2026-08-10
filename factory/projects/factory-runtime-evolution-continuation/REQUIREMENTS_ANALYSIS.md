# Requirements Analysis — Factory Runtime Evolution — Continuation

| Field | Value |
|---|---|
| Document status | validated: true (implementation-planner, 2026-08-10); reviewed: false — assigned to `solution-architect` |
| Source | Jean García directive + Factory DB status + predecessor `factory-runtime-evolution` evidence |
| Scope | G1 control pack (FRE-010) + downstream increments (FRE-011…FRE-017, see `TASK_GRAPH.md`) |

## 1. Durable invariant (requirement 0)

When the Factory encounters a project block, it must inspect concrete task/run/gate
evidence and autonomously diagnose, repair, requeue, or dispatch technical/control-plane
work. It must NOT ask Jean to solve generic, stale, or self-generated "human decisions."
Only the following may become an actionable Jean question:

1. **Independently verified external authority** — e.g., a third party/regulator decision
   confirmed from the original source (not inferred from a worker's result_summary text).
2. **Product/business scope** — a genuine product or business decision with options that
   only Jean can pick (scope, acceptance criteria, priorities).
3. **Security approval** — approval that cannot be granted by any Factory role and is not
   a routine gate (security reviewer approves routine gates).
4. **Payment/credential/access** — credentials, secrets, payments, or access grants.
5. **Bounded exhausted repair loop** — the same task exceeded its deterministic retry
   ceiling (`SUPERVISOR_TECHNICAL_REWORK_MAX_RETRIES`, default 2) after concrete,
   evidence-backed repair attempts, with the repair history attached.

Every Jean question MUST carry: a concrete question, at least one decision option,
the evidence that justifies escalation, and the escalation category from the list above.

## 2. Functional requirements

### FR-1 — Evidence-first blocker handling
When a project is blocked and autonomous, the runtime MUST inspect concrete
task/run/gate/human-question evidence and attempt, in order:
clear resolved blockers → requeue technical rework (bounded) → repair orphan state →
reconcile → only then consider a human question. No escalation without an attempted
deterministic repair path is allowed.
- Evidence anchor (current): `supervisor_health_check()` `hermes_cli/factory_pg.py:4523–4602`;
  `_supervisor_requeue_technical_blockers()` line 3423.
- Gap: pending questions short-circuit this ordering (line 4584–4586).

### FR-2 — Legacy generic-question retirement/rework
The runtime MUST detect and retire human questions that are stale (their task is no
longer blocked / blocker resolved), generic (no concrete question or no actionable
options), or self-generated (produced by the classifier from worker prose without
verified external evidence). Retired questions MUST be recorded with an event and
metadata; the task MUST be requeued as `rework` (bounded) or closed if resolved.
- Gap: no question lifecycle states exist (only `pending`/`open`/resolved-by-Jean paths);
  no re-validation before `mark_project_manual_attention`.
- Test-first increments: FRE-011 (retirement/rework), FRE-012 (escalation validation).

### FR-3 — Direct-human escalation validation
Before any `manual_attention` transition or new human question, the runtime MUST
validate the escalation against the invariant allowlist (section 1) and the question
contract (concrete question + options + evidence + category). Validation failure ⇒
autonomous repair/requeue, never a Jean question.
- Evidence anchor (current): `classify_factory_blocker()` line 3205 (taxonomy and
  `unactionable_legacy_human_reference` handling); `record_factory_blocker_actions()`
  line 3351 (skips questions without explicit JEAN_QUESTION).
- Gap: the supervisor path still marks manual_attention for ANY pending question without
  re-running this validation; question rows survive forever in `pending`.

### FR-4 — Global watchdog/cron integration
The L1 tick (`factory_orchestrator_tick.py`), L2 blocker/supervisor
(`factory_blocker_detector.py`), and watchdog (`factory_watchdog_alerts.py`) MUST
consume the same supervisor output contract, stay silent when there is nothing to alert,
and never emit alert loops. Cron jobs run repo-backed scripts with wrappers; runtime
wrappers stay in `sitiouno-agent-runtime` only for non-Factory workflows.
- Evidence anchor (current): INC-0008 restoration (repo-backed `scripts/factory/*`);
  `RETROSPECTIVE_INC_0008.md`; QA smoke `factory_blocker_detector.py` →
  `classified=0, questions_created=0, alerts=0, needs_attention=False`
  (`factory/projects/factory-runtime-evolution/QA_REPORT.md:227–234`).

### FR-5 — Canonical continuation/reopen capability
A terminal project (completed/accepted/cancelled/superseded/closed) MUST be reopenable
through a canonical operation (`hermes factory project reopen` / `continue`) that:
records lineage metadata (`continuation_of` / `superseded_by_project_id` both ways),
creates a reopen gate, restores `active` only after G0/G1 preflight passes, and prevents
duplicate detached successor projects for the same lineage.
- Evidence anchor (current): `close_project()` line 2429 records
  `superseded_by_project_id` / `absorbed_into_project_id`; no counterpart operation
  exists; `_resume_preflight_blocker()` blocks terminal resume (fail-closed).
- This project itself is the operational proof of the gap: `factory-runtime-evolution-continuation`
  was created detached instead of reopening `factory-runtime-evolution` (event 172950).

### FR-6 — Fail-closed G0/G1/security gates preserved
No change may weaken: G0 repository strategy enforcement, G1 document readiness
(exists + indexed + committed + validated + reviewed), security gates, or the
single-active-increment guard. All new operations must be reachable only through
canonical Factory tool/CLI surfaces (`hermes factory …`), never ad-hoc SQL.

### FR-7 — Test-first (TDD) discipline
Every downstream increment MUST start with a failing regression test that reproduces
the exact gap, then implement the minimal change that turns it green, then refactor.
Tests must use the CI-parity runner (`scripts/run_tests.sh`) and follow the repo test
rules (no change-detector tests, no source-reading tests, no fake host OS).

### FR-8 — PR-first delivery
Each increment MUST land on its own branch/worktree, be pushed to
`SiteOneTech/hermes-agent-original` after local validation, pass its assigned
reviewer gate, and only then merge into `main`. Delivery reports and change records
MUST reference the exact commit/branch.

## 3. Non-functional requirements

| Id | Requirement |
|---|---|
| NFR-1 | Determinism: same evidence ⇒ same runtime decision (no prose-only escalation). |
| NFR-2 | Auditability: every repair/retirement/reopen/escalation writes a `factory.events` row with metadata. |
| NFR-3 | Idempotency: repeated ticks must not duplicate questions/events (existing 60-min event dedup + per-task pending-question dedup preserved). |
| NFR-4 | Silence: no alert when no unsuppressed invariant is violated. |
| NFR-5 | Bounded escalation: retry ceilings (default 2) apply per task; escalation only after exhaustion. |
| NFR-6 | No new config env vars; behavioral settings go to `config.yaml`, secrets only in `.env`. |

## 4. Traceability to acceptance criteria (FRE-010)

| Acceptance criterion | Covered by |
|---|---|
| G1 files exist, indexed, committed, explicit validated/reviewed state | FR-6; `DOCUMENTATION_INDEX.md`; `TRACKER.md`; per-doc status blocks |
| Docs identify exact legacy failure mode, tick/supervisor boundaries, real evidence; no paused projects as active incidents | FR-1/FR-2/FR-4; `PATTERN_ANALYSIS.md` §3–§5; `FACTORY_INTAKE.md` §5 |
| Task graph with small TDD increments (retirement, escalation validation, watchdog/cron, continuation/reopen, QA/security, PR-first) | FR-2/FR-3/FR-4/FR-5/FR-7/FR-8; `TASK_GRAPH.md` |
| Fail-closed G0/G1/security gates; only genuine Jean conditions | FR-6; `SECURITY_GATES.md` §Escalation allowlist |

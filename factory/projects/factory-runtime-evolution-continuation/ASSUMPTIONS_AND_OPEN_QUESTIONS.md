# Assumptions and Open Questions — Factory Runtime Evolution — Continuation

| Field | Value |
|---|---|
| Document status | validated:true (implementation-planner, 2026-08-10); reviewed:true (solution-architect, 2026-08-10, planning gate 690) |

## 1. Assumptions (accepted, do not re-litigate without new evidence)

| # | Assumption | Basis |
|---|---|---|
| A1 | Agent Core Postgres `zeus_agent.factory` is the operational source of truth; repo Markdown and git are documentary truth; Notion is human PM projection. | Factory canon (`factory-agent-operating-canon`), predecessor `DOCUMENTATION_INDEX.md`. |
| A2 | This project is the canonical continuation of `factory-runtime-evolution` (zeus-only, maintain_existing_project intent), and the runtime gap that forced a detached successor is itself part of the scope to fix (P4). | G0 record (event 172950); Jean's directive; `PATTERN_ANALYSIS.md` §4. |
| A3 | No product-runtime code belongs in G1. FRE-010 delivers documentation and a task graph only; code changes happen in downstream increments under TDD. | Task definition (FRE-010); Factory G1 gate. |
| A4 | The 14 required G1 documents are: FACTORY_INTAKE, REQUIREMENTS_ANALYSIS, PATTERN_ANALYSIS, ASSUMPTIONS_AND_OPEN_QUESTIONS, PRD, ADRS, METHODOLOGY_PLAN, TECHNICAL_BLUEPRINT, SPRINT_PLAN, TASK_GRAPH, TRACKER, DOCUMENTATION_INDEX, QA_GATES, SECURITY_GATES. Lifecycle docs (QA_REPORT, SECURITY_REVIEW, QUALITY_REVIEW, DELIVERY_REPORT, CHANGELOG, CHANGE_RECORDS, RETROSPECTIVE, NOTION_UPDATE) are created as phases advance. | Factory canon G1 list; Factory DB `document_status` (14 blocking). |
| A5 | The retry ceiling `SUPERVISOR_TECHNICAL_REWORK_MAX_RETRIES = 2` (global default, per-task override via `factory.tasks.max_retries`) defines "bounded exhausted repair loop" for escalation. | `factory_pg.py:255`, `_task_supervisor_max_retries()` line 3407. |
| A6 | One pending human question per task is the current dedup contract; lifecycle additions must preserve it (no duplicate rows per task). | `record_factory_blocker_actions()` line 3374–3396. |
| A7 | Cron scripts are repo-backed under `scripts/factory/`; `~/.hermes/scripts/*` are thin wrappers. Non-Factory crons (Vapi, customer-intent) belong to `sitiouno-agent-runtime` and are out of scope. | `RETROSPECTIVE_INC_0008.md`. |
| A8 | Watchdog must stay silent when there are no unsuppressed invariants; idle ticks are healthy. | `QA_REPORT.md:234` (predecessor). |
| A9 | Merge to `main` happens only after the increment passes its assigned reviewer/gate (PR-first); this G1 branch is pushed but not merged by the worker. | Factory canon implementation/delivery rules. |
| A10 | Independent review of G1 docs is assigned to `solution-architect` (FRE-010 reviewer in Factory DB). Planner self-validation is not a substitute for that review. | Factory DB task FRE-010 `reviewer_agent_id: solution-architect`. |

## 2. Open questions (tracked, NOT blockers)

| # | Question | Who decides | When | Default if unanswered |
|---|---|---|---|---|
| Q1 | Should the continuation/reopen operation (P4) also support reopening `cancelled`/`superseded` projects, or only `completed`/`accepted`? | solution-architect + factory-orchestrator (ADR-010-3) | FRE-014 kickoff | Only `completed`/`accepted`; `cancelled`/`superseded` require explicit Jean approval via the existing closure gate path. |
| Q2 | What is the retirement TTL for a pending question before it is considered stale (e.g., 24 h)? Should it be config-driven in `config.yaml`? | factory-orchestrator | FRE-011 | Fixed constant 24 h in code, configurable later via `config.yaml` (NFR-6: no new env vars). |
| Q3 | Should the escalation-allowlist categories (REQUIREMENTS_ANALYSIS §1) be enforced as a closed enum in `factory_contracts.py` with validation tests? | solution-architect | FRE-012 | Yes — closed enum `JeanEscalationCategory`, fail-closed validation. |
| Q4 | Global cron verification (FRE-017): resume the three paused Factory crons (blocker detector, orchestrator tick, watchdog) in one shot after gates, or incrementally? | devops-release + factory-orchestrator | FRE-013/017 | Incremental: status-sync → reviewer-dispatch → blocker-detector → watchdog → orchestrator-tick, each with smoke evidence. |
| Q5 | Does the lineage check at intake (P4) apply only to `zeus_only` self-improvement projects or to all Factory projects? | solution-architect | FRE-014 | Only projects whose metadata declares `lineage: factory_runtime` or equivalent; product projects keep terminal semantics. |

None of Q1–Q5 block FRE-010 or the downstream increments as planned; each has a safe
default. They are assigned to the named owner at the named increment kickoff.

## 3. Explicit non-decisions (out of scope)

- No renaming of `manual_attention` status (contract change is not needed; the fix is in
  WHEN it is set).
- No DB migration for question lifecycle in G1; lifecycle is metadata + status values on
  the existing `factory.human_questions` table, unless a downstream increment proves a
  column is required (then it goes through the canonical migration path with a migration
  increment).
- No Notion surface changes; Notion remains projection.

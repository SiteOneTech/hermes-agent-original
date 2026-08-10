# PRD — Factory Runtime Evolution — Continuation (FRE-010 + downstream)

| Field | Value |
|---|---|
| Document status | validated:true (implementation-planner, 2026-08-10); reviewed:true (solution-architect, 2026-08-10, planning gate 690) |
| Product | Zeus Software Factory runtime control plane (internal, zeus_only) |
| Version | 0.1 (G1 planning baseline) |

## 1. Problem statement

The Factory runtime still escalates to Jean prematurely: any pending
`factory.human_questions` row — even a stale, generic, or self-generated one — moves a
blocked project to `manual_attention` (`factory_pg.py:4584–4586`), disabling autonomy and
wasting Jean's attention on noise instead of evidence-driven repair. At the same time,
the runtime cannot canonically continue a terminal self-improvement project: it spawns
detached successor projects instead of reopening one living product. Finally, the
restored watchdog/cron control plane (INC-0008) lacks a verified global cron pass.

## 2. Target users and jobs-to-be-done

| User | Job |
|---|---|
| Jean (owner) | Never receive generic/stale/self-generated questions; only genuine, verified decisions with options and evidence. |
| factory-orchestrator / L1 tick | Keep autonomous projects moving: dispatch, monitor, reconcile, claim — without human interruption for routine technical blocks. |
| L2 supervisor | Repair safe stuck states deterministically; escalate only on the invariant allowlist; keep the single-active slot healthy. |
| watchdog / devops-release | Emit concise, actionable alerts only for real invariants; verify cron health globally. |
| quality/security reviewers | Review increments independently with test-first evidence. |

## 3. User stories

- US-1: As Jean, when a task is blocked with a technical failure, I want the supervisor to
  requeue it as bounded rework and only escalate after exhaustion with repair history.
- US-2: As Jean, when a human question exists but is stale or generic, I want the runtime
  to retire it with evidence and requeue/close the task — without marking the project
  `manual_attention`.
- US-3: As Jean, when a real external/product/security/payment decision exists, I want
  ONE actionable question with options, evidence, and the escalation category.
- US-4: As factory-orchestrator, when a self-improvement project reaches terminal, I want
  to `reopen/continue` it canonically with lineage metadata instead of creating a
  detached successor.
- US-5: As devops-release, I want a verified global cron pass for Factory scripts with
  evidence, and idle silence from watchdog.
- US-6: As reviewer, I want every increment to arrive as a branch/PR with RED→GREEN test
  evidence and independent QA/security gates before merge.

## 4. Functional scope (this PRD covers FRE-010..FRE-017 as planned; see TASK_GRAPH)

| Id | Capability | Requirement |
|---|---|---|
| C1 | G1 control pack (FRE-010) | 14 required docs exist/indexed/committed/validated; review assigned; evidence-based diagnosis; TDD task graph. |
| C2 | Question retirement/rework (FRE-011) | Question lifecycle `pending → stale/retired/answered`; retirement events; bounded task requeue; no premature manual_attention. |
| C3 | Escalation validation (FRE-012) | Closed allowlist enum; validation gate before any human question/manual_attention; fail-closed to autonomous repair. |
| C4 | Watchdog/cron integration (FRE-013) | Supervisor output consumed by watchdog/crons; idle silence; wrapper discipline. |
| C5 | Continuation/reopen (FRE-014) | `hermes factory project reopen` with lineage metadata, reopen gate, G0/G1 preflight; intake lineage check. |
| C6 | Independent QA/security review (FRE-015) | Reviewer-owned gates with real test evidence for C2–C5. |
| C7 | PR-first delivery (FRE-016) | Branch/PR per increment, push after local validation, merge to main only after gates. |
| C8 | Global cron verification (FRE-017) | Incremental resume of Factory crons with smoke evidence and no alert loops. |

## 5. Acceptance criteria (FRE-010 — this increment)

1. All required G1 files exist under `factory/projects/factory-runtime-evolution-continuation/`,
   are indexed, committed, and contain explicit validated/reviewed state.
2. Documents identify the exact legacy generic-question/manual_attention failure mode,
   the existing global tick/supervisor boundaries, and real operational evidence, without
   treating paused projects as active incidents.
3. `TASK_GRAPH.md` contains small TDD increments for generic-question retirement/rework,
   direct-human escalation validation, global watchdog/cron integration, canonical
   continuation/reopen capability, independent QA/security review, and PR-first delivery.
4. The plan preserves fail-closed G0/G1/security gates and names only genuine conditions
   that can require Jean.

## 6. Success metrics (downstream, measurable)

- M1: Zero new `manual_attention` transitions whose reason is a stale/generic question
  (regression-tested; alert `blocked_without_human_question` count = 0 in idle smoke).
- M2: 100% of reopened self-improvement projects carry `continuation_of` lineage metadata.
- M3: Global cron pass exits 0 with evidence for all five Factory scripts.
- M4: Every downstream increment has ≥1 RED→GREEN test pair committed before code.

## 7. Non-goals (explicit)

- No product-runtime code in G1.
- No changes to delivery boundary: sandbox `kidu.app` only; production HOLD until Jean decides.
- No new env vars for configuration (NFR-6).
- No Notion writes; no direct ad-hoc SQL for Factory DB (canonical tools only).
- No change to the single-active-increment guard or manual-takeover lease semantics.

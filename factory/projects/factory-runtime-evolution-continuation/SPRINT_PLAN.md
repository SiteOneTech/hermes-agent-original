# Sprint Plan — Factory Runtime Evolution — Continuation

| Field | Value |
|---|---|
| Document status | validated: true (implementation-planner, 2026-08-10); reviewed: false — assigned to `solution-architect` |

## Sprint 1 — G1 documentary bootstrap (FRE-010, THIS increment)

| Item | Owner | Reviewer | DoD |
|---|---|---|---|
| Full G1 control pack (14 docs) under `factory/projects/factory-runtime-evolution-continuation/` | implementation-planner | solution-architect | exists + indexed + committed + validated; review assigned; R1/R2 reconciliation anomalies resolvable |
| Diagnosis of legacy generic-question → premature manual_attention | implementation-planner | solution-architect | `PATTERN_ANALYSIS.md` §3 with line-level evidence; no paused projects treated as incidents |
| Continuation/reopen gap documented | implementation-planner | solution-architect | `PATTERN_ANALYSIS.md` §4; `ADRS.md` ADR-010-3 |
| TDD task graph for downstream increments | implementation-planner | solution-architect | `TASK_GRAPH.md` covers FRE-011…FRE-017 with acceptance, deps, branches |
| Branch push + review handoff | implementation-planner | solution-architect | branch `factory/factory-runtime-evolution-continuation/inc-010-g1-autonomy-supervisor-contract` pushed; reviewer gate pending |

Exit: G1 blockers cleared in Factory DB (exists+indexed+committed+validated for the 14
docs; reviewed flips after solution-architect passes the review gate).

## Sprint 2 — Question lifecycle + escalation validation (FRE-011, FRE-012)

- FRE-011 generic-question retirement/rework (owner: zeus builder; reviewer:
  quality-reviewer). Deliverables: `QuestionStatus` contract, `retire_human_questions()`,
  supervisor reorder (ADR-010-2), RED tests first.
- FRE-012 direct-human escalation validation (owner: zeus builder; reviewer:
  security-reviewer + quality-reviewer). Deliverables: `JeanEscalationCategory` enum,
  `validate_human_question()`, classifier draft-only mapping, `manual_attention` category
  guard.
- DoD per METHODOLOGY_PLAN §5; both independent, claimable in parallel (no file
  conflicts: FRE-011 touches `factory_pg.py` lifecycle/supervisor; FRE-012 touches
  `factory_contracts.py` + question creation — reviewed at planning to keep the split).

## Sprint 3 — Watchdog/cron integration + continuation/reopen (FRE-013, FRE-014)

- FRE-013 global watchdog/cron integration (owner: zeus builder; reviewer:
  devops-release). Deliverables: supervisor_summary in detector report; regression tests;
  no alert-loop guarantee.
- FRE-014 canonical continuation/reopen (owner: zeus builder; reviewer:
  solution-architect). Deliverables: `reopen_project()`, CLI `hermes factory project
  reopen`, intake lineage check, reopen gate, RED tests.
- Both claimable in parallel after Sprint 2 (FRE-013 depends on the reordered
  supervisor output from FRE-011/012; FRE-014 is independent).

## Sprint 4 — Independent review, PR-first delivery, global cron verification
(FRE-015, FRE-016, FRE-017)

- FRE-015 independent QA/security review of FRE-011…FRE-014 (owner: quality-reviewer +
  security-reviewer; reviewer: factory-orchestrator). Deliverables: QA_REPORT.md,
  SECURITY_REVIEW.md with real test evidence; rework lists if gates fail.
- FRE-016 PR-first delivery (owner: devops-release + factory-orchestrator; reviewer:
  factory-orchestrator). Deliverables: all increment branches merged to `main` after
  gates; CHANGE_RECORDS.md + DELIVERY_REPORT.md with merge SHAs.
- FRE-017 global cron verification (owner: devops-release; reviewer:
  factory-orchestrator). Deliverables: incremental cron resume (status-sync →
  reviewer-dispatch → blocker-detector → watchdog → orchestrator-tick) with
  `hermes cronjob list` + smoke evidence; idle-silence verified.

## Rollout/delivery boundary

- All changes are Zeus-internal (`zeus_only`): no product runtime, no sandbox deploy, no
  production change. Sandbox boundary (kidu.app) is not exercised by this project; if a
  later scope adds a dashboard surface, the canonical sandbox/deploy path applies.
- Production remains HOLD until Jean decides; nothing in this plan changes that.

## DoR/DoD cross-reference

- DoR: METHODOLOGY_PLAN §4. DoD: METHODOLOGY_PLAN §5. Gate policy: METHODOLOGY_PLAN §6.

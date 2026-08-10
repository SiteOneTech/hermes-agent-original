# Task Graph — Factory Runtime Evolution — Continuation

| Field | Value |
|---|---|
| Document status | validated:true (implementation-planner, 2026-08-10); reviewed:true (solution-architect, 2026-08-10, planning gate 690) |
| Rule | Every increment = own branch/worktree (`factory/factory-runtime-evolution-continuation/<inc-key>`), TDD RED→GREEN, reviewer gate, PR-first merge to `main` after gates. |

## 0. Dependency graph

```
FRE-010 (G1 pack) ──┬──> FRE-011 (question retirement/rework)
                    ├──> FRE-012 (escalation validation)
                    ├──> FRE-014 (continuation/reopen)          (independent)
                    └──> R1/R2 (reconciliation, DB-driven; close when docs exist+committed)

FRE-011 ──┐
FRE-012 ──┴──> FRE-013 (watchdog/cron integration)
FRE-011+FRE-012+FRE-013+FRE-014 ──> FRE-015 (independent QA/security review)
FRE-015 ──> FRE-016 (PR-first delivery / merge to main)
FRE-013 + FRE-015 ──> FRE-017 (global cron verification)
```

## 1. Task inventory

| Id | Title | Phase | Owner | Reviewer | Deps | Branch |
|---|---|---|---|---|---|---|
| FRE-010 | G1 autonomous supervisor hardening contract and test-first task graph | planning | implementation-planner | solution-architect | — | `factory/factory-runtime-evolution-continuation/inc-010-g1-autonomy-supervisor-contract` |
| R1 | Reconciliation: restore project-local Factory artifact directory | documentation | factory-reporter | factory-orchestrator | FRE-010 (dir creation) | — (DB-driven) |
| R2 | Reconciliation: complete required Factory methodology documentation | documentation | factory-reporter | factory-orchestrator | FRE-010 (docs) | — (DB-driven) |
| FRE-011 | Generic human-question retirement/rework (question lifecycle) | implementation | zeus builder (claude-builder or codex-builder) | quality-reviewer | FRE-010 | `factory/factory-runtime-evolution-continuation/inc-011-question-retirement-rework` |
| FRE-012 | Direct-human escalation validation (allowlist + contract) | implementation | zeus builder | security-reviewer + quality-reviewer | FRE-010 | `factory/factory-runtime-evolution-continuation/inc-012-escalation-validation` |
| FRE-013 | Global watchdog/cron integration (supervisor output contract) | implementation | zeus builder | devops-release | FRE-011, FRE-012 | `factory/factory-runtime-evolution-continuation/inc-013-watchdog-cron-integration` |
| FRE-014 | Canonical continuation/reopen capability | implementation | zeus builder | solution-architect | FRE-010 | `factory/factory-runtime-evolution-continuation/inc-014-continuation-reopen` |
| FRE-015 | Independent QA/security review of FRE-011…FRE-014 | review | quality-reviewer + security-reviewer | factory-orchestrator | FRE-011..014 | (review lane) |
| FRE-016 | PR-first delivery: merge approved increments to main | delivery | devops-release + factory-orchestrator | factory-orchestrator | FRE-015 | — |
| FRE-017 | Global cron verification (incremental resume + smoke) | verification | devops-release | factory-orchestrator | FRE-013, FRE-015 | `factory/factory-runtime-evolution-continuation/inc-017-global-cron-verification` |

## 2. Per-increment acceptance (TDD anchors)

### FRE-011 — Generic human-question retirement/rework
- RED: in `tests/hermes_cli/test_factory_control_plane_refactor.py`, replace
  `test_supervisor_moves_existing_human_question_to_manual_attention` with
  `test_stale_question_is_retired_and_task_requeued_without_manual_attention`; add
  `test_generic_question_without_options_is_retired` and
  `test_retired_question_records_event_and_metadata`. Expected FAIL before change.
- GREEN: `QuestionStatus` contract (`factory_contracts.py`), `retire_human_questions()`
  (`factory_pg.py`), supervisor reorder per ADR-010-2 (retire BEFORE
  pending_questions→manual_attention; manual_attention only for validated fresh
  questions).
- DoD: focused file green via `scripts/run_tests.sh`; sibling factory tests green;
  `TRACKER.md`/`SPRINT_PLAN.md` updated; branch pushed; reviewer gate.

### FRE-012 — Direct-human escalation validation
- RED: new `tests/hermes_cli/test_factory_escalation_validation.py`:
  `test_missing_category_fails_closed`, `test_draft_without_options_never_creates_question`,
  `test_manual_attention_refused_without_valid_category`,
  `test_valid_question_requires_evidence_refs`. Expected FAIL before change.
- GREEN: `JeanEscalationCategory` enum; `validate_human_question()`; classifier text
  becomes draft-only; `mark_project_manual_attention(category=...)` guard.
- DoD: same pattern as FRE-011; security-reviewer reviews escalation allowlist.

### FRE-013 — Global watchdog/cron integration
- RED: extend `tests/hermes_cli/test_factory_cron_control_plane.py`:
  `test_detector_report_includes_supervisor_summary`,
  `test_watchdog_silent_when_idle_with_supervisor_contract`. Expected FAIL before change.
- GREEN: detector report gains `supervisor_summary` (invariant/action/result/next) from
  `supervisor_health_check`; watchdog idle-silence preserved; wrappers unchanged.
- DoD: cron-adjacent tests green; no alert loop (dedup + silence verified in unit);
  devops-release gate.

### FRE-014 — Canonical continuation/reopen capability
- RED: new `tests/hermes_cli/test_factory_project_reopen.py`:
  `test_completed_lineage_project_reopens_to_active_with_gate`,
  `test_cancelled_project_reopen_requires_jean_approval`,
  `test_reopen_preflight_fails_closed_on_missing_docs_or_strategy`,
  `test_intake_suggests_reopen_instead_of_detached_successor`. Expected FAIL before change.
- GREEN: `reopen_project()` (`factory_pg.py`), CLI `hermes factory project reopen`
  (factory CLI catalog), intake lineage check (P4), reopen gate + `project_reopened` event.
- DoD: unit green; CLI smoke `hermes factory project reopen --help`; solution-architect gate.

### FRE-015 — Independent QA/security review
- Verify exact diffs + RED/GREEN evidence + acceptance criteria for FRE-011…FRE-014;
  run full factory test set (`scripts/run_tests.sh tests/hermes_cli/test_factory*.py`);
  produce `QA_REPORT.md` + `SECURITY_REVIEW.md` with real output; block with rework list
  if evidence missing.
- DoD: review gates recorded; rework items tracked as tasks if any.

### FRE-016 — PR-first delivery
- Merge FRE-011…FRE-014 branches to `main` ONLY after their gates pass; push `main`;
  record merge SHAs in `CHANGE_RECORDS.md` + `DELIVERY_REPORT.md`; confirm
  `factory-runtime-evolution-continuation` reconciles clean.
- DoD: `hermes factory status` shows no new anomalies; delivery gate recorded.

### FRE-017 — Global cron verification
- Incremental resume with smoke evidence: `factory_status_sync` → `factory_reviewer_dispatch`
  (report-only) → `factory_blocker_detector` → `factory_watchdog_alerts` →
  `factory_orchestrator_tick`; after each: exit 0 + `hermes cronjob list` clean +
  no unexpected alerts (idle silence).
- DoD: verification evidence committed under project artifacts (e.g.
  `CRON_VERIFICATION.md` lifecycle doc); devops-release + orchestrator gates.

## 3. Mapping to acceptance criteria (FRE-010)

| Acceptance criterion | Evidence |
|---|---|
| G1 files exist/indexed/committed/validated/reviewed-state | `DOCUMENTATION_INDEX.md` status table + per-doc headers + commit + reviewer assignment (solution-architect) |
| Exact failure mode + boundaries + real evidence; no paused projects as incidents | `PATTERN_ANALYSIS.md` §1–§3 (line-level), §2 evidence; paused projects excluded explicitly |
| TDD increments for all six areas | FRE-011 (retirement/rework), FRE-012 (escalation validation), FRE-013 (watchdog/cron), FRE-014 (continuation/reopen), FRE-015 (QA/security), FRE-016 (PR-first), FRE-017 (cron verification) |
| Fail-closed G0/G1/security gates; genuine Jean conditions only | `SECURITY_GATES.md` §Escalation allowlist; METHODOLOGY_PLAN §6; ADR-010-2/4 |

## 4. Parallelization note

FRE-011, FRE-012, FRE-014 are independent after FRE-010 and touch disjoint files
(FRE-011: supervisor + question lifecycle in `factory_pg.py`; FRE-012:
`factory_contracts.py` + question creation; FRE-014: reopen + CLI + intake) — claimable
in parallel without file conflicts. FRE-013 waits for FRE-011/012 (supervisor output
contract). FRE-017 waits for FRE-013 + FRE-015.

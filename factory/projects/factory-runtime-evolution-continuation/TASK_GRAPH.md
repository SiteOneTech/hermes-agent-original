# Task Graph — Factory Runtime Evolution — Continuation

| Field | Value |
|---|---|
| Document status | baseline reviewed:true (solution-architect, 2026-08-10, planning gate 690); FRE-025 amendment validated:true (implementation owner, 2026-08-12), reviewed:pending |
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
FRE-020 (emergency consolidation: FRE-011/FRE-012/FRE-014 live incident repair) ──> FRE-015/R5 review
FRE-021 (review outcome semantic integrity and failed-review recovery) ──> FRE-022 (strict canonical semantic marker lexical contract) ──> FRE-015/R5 review
FRE-015 ──> FRE-016 (PR-first delivery / merge to main)
FRE-013 + FRE-015 ──> FRE-017 (global cron verification)

FRE-025 (pause provenance + source-delivery guard) ──> independent review
FRE-025 independent review ──> verified source integration into origin/main
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
| FRE-020 | Technical rework escalation and canonical continuation recovery | implementation | claude-builder | quality-reviewer + solution-architect | FRE-010, live Alpha incident | `factory/factory-runtime-evolution-continuation/inc-020-fre-020-technical-rework-escalat` |
| FRE-021 | Review outcome semantic integrity and failed-review recovery | implementation | claude-builder | quality-reviewer | FRE-020, live review 429 incident | `factory/factory-runtime-evolution-continuation/inc-020-fre-020-technical-rework-escalat` |
| FRE-022 | Strict canonical semantic marker lexical contract | implementation | claude-builder | security-reviewer | FRE-021, security review of `591312126a6f5865cb6c74327a0f48a8f4a483b2` | `factory/factory-runtime-evolution-continuation/inc-020-fre-020-technical-rework-escalat` |
| FRE-025 | Pause provenance, technical holds, and source-delivery guard | implementation | implementation owner | independent reviewer | verified incident | `factory/factory-runtime-evolution-continuation/inc-025-pause-provenance-source-delivery` |

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

### FRE-020 — Technical rework escalation and canonical continuation recovery
- RED: committed behavioral tests first at `4e2d163ac`, then ran
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_project_reopen.py tests/hermes_cli/test_factory.py -k 'technical_rework_creates_autonomous_recovery or invalid_existing_human_question or manual_attention_refuses_invalid or stranded_technical_manual_attention or project_reopen or project_create_suggests_reopen or registers_project_reopen'`.
  Expected/observed RED: 9 failed / 0 passed; failures covered missing `reopen_project`, missing CLI reopen/continue parser, exhausted technical rework still manual_attention, stale/generic human questions not retired, and stranded `technical_rework_retries_exhausted` manual_attention not restored.
- GREEN: same focused command plus `-q` after production change → 9 passed / 0 failed.
- Focused Factory regression set:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python scripts/run_tests.sh tests/hermes_cli/test_factory.py tests/hermes_cli/test_factory_project_reopen.py tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_cron_control_plane.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_ux_ui_designer_contract.py` → 134 passed / 0 failed.
- GREEN implementation scope:
  `hermes_cli/factory_pg.py` autonomous technical recovery path (`technical_rework_escalated_autonomously` audit, deterministic recovery task, no human/manual hold), invalid-question fail-closed retirement, stale manual_attention restoration, create-path reopen suggestion, and canonical `reopen_project` with preflight/gate/audit/single-active guard; `hermes_cli/factory.py` CLI `project reopen|continue`; `hermes_cli/factory_contracts.py` question/category contracts.
- DoD: no direct Factory DB writes except approved Factory evidence gate, no deploy, no push/merge/PR/Factory task close; code/docs committed on assigned branch after verification.

### FRE-021 — Review outcome semantic integrity and failed-review recovery
- RED: added behavioral regression coverage for the reproduced wrapped/instructional
  review failure text `STATE: DONE; si falla, termina con STATE: BLOCKED...`.
  Expected/observed RED before production change: semantic parser accepted the wrapped
  line as `done`, `mark_run_finished(... run_type=review, exit_code=1, output_summary=<429>)`
  invoked increment integration and attempted terminal done semantics.
- GREEN: strict canonical marker parsing accepts only standalone `STATE: DONE`,
  `STATE: BLOCKED`, `STATE: IN_PROGRESS` (optionally prefixed by `FINAL:`) after
  leading terminal/Markdown decoration is stripped; wrapped or instructional prose is
  ignored. Failed review runs without an actual final verdict remain `failed`/`rework`,
  skip increment integration, and emit `review_run_failed` audit events with the failure
  summary tail.
- Focused Factory regression set:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python scripts/run_tests.sh tests/hermes_cli/test_factory.py tests/hermes_cli/test_factory_project_reopen.py tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_cron_control_plane.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_ux_ui_designer_contract.py` → 136 passed / 0 failed.
- DoD: no deploy, no push/merge/PR/Factory task close; code/docs committed on the
  existing FRE-020 branch for independent exact-SHA review.

### FRE-022 — Strict canonical semantic marker lexical contract
- RED: added lexical-contract regression coverage for exact accepted markers and rejected
  noncanonical variants (`STATE:DONE`, `STATE : DONE`, `state: done`, `FINAL:STATE: DONE`,
  extra internal spaces, case variants, and suffixed prose) in
  `tests/hermes_cli/test_factory_control_plane_refactor.py`. Expected/observed RED before
  production change: 8 rejected-variant rows failed because the parser still accepted
  case-insensitive/flexible-whitespace forms while the six exact canonical marker rows
  remained accepted.
- GREEN: semantic parser now maps only exact cleaned marker lines
  `STATE: DONE|BLOCKED|IN_PROGRESS` and
  `FINAL: STATE: DONE|BLOCKED|IN_PROGRESS` after the existing leading decoration cleanup;
  regex case-insensitive/flexible-whitespace acceptance is removed.
- Preservation evidence: wrapped 429 failed-review path remains `failed`/`rework` with
  `review_run_failed`, and stale-worker recovery still finalizes a valid canonical
  `STATE: DONE` marker.
- Focused Factory regression set:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python scripts/run_tests.sh tests/hermes_cli/test_factory.py tests/hermes_cli/test_factory_project_reopen.py tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_cron_control_plane.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_ux_ui_designer_contract.py` → 153 passed / 0 failed.
- DoD: no deploy, no credential change, no direct main merge; code/docs committed on the
  existing FRE-020 branch for independent exact-SHA security review.

### FRE-025 — Pause provenance and source delivery

- RED: behavior tests reject blank/reserved manual-pause authority, require CLI
  provenance, distinguish technical holds, narrow bootstrap repair to structured
  metadata, and block unintegrated terminal source increments from reconciliation,
  delivery, and successor auto-resume.
- GREEN: explicit audited manual pause; supervisable technical/dependency hold that
  cannot weaken `manual_attention`; structured exemption; shared integration guard
  with explicit Jean-authorized waiver support; explicit successor contract evaluated
  only by the global lease-owning tick.
- DoD: exact focused suite and `git diff --check` pass; retrospective committed;
  independent review and verified integration into `origin/main` remain required.

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

FRE-025 is isolated from the earlier implementation graph. Its local implementation
and tests may complete in this branch, but source integration is sequential: an
independent reviewer must approve the exact diff before the branch is verified in the
declared origin base. No queued successor may bypass that order.

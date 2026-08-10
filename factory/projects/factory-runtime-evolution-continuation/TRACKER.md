# Tracker — Factory Runtime Evolution — Continuation

| Field | Value |
|---|---|
| Document status | validated:true (implementation-planner, 2026-08-10); reviewed:true (solution-architect, 2026-08-10, planning gate 690) |
| Project ID | `factory-runtime-evolution-continuation` |
| Predecessor | `factory-runtime-evolution` (terminal: completed; continuation lineage pending FRE-014) |
| Methodology | Hybrid (zeus_native lane + bmad_hybrid lane) |
| Source of truth | Agent Core Postgres `zeus_agent.factory` |
| Repo artifacts | `factory/projects/factory-runtime-evolution-continuation/` |
| Repo | `SiteOneTech/hermes-agent-original` (zeus_only) |
| Current state | `paused` in Factory DB by operator pause; FRE-021 implementation complete locally on the assigned FRE-020 branch; tests green; pending reviewer/gate. |
| Anomalies at start | `missing_project_artifact_dir`, `missing_required_docs` (resolved by this increment's dir + committed docs) |

## 1. Task tracker (mirrors Factory DB)

| Task | Status | Owner | Reviewer | Evidence |
|---|---|---|---|---|
| FRE-010 G1 autonomous supervisor hardening contract and test-first task graph | done — planning-review passed (gate 690) | implementation-planner | solution-architect | 14 G1 docs + commit + branch push; planning gate 690=passed |
| R1 — Reconciliation: restore project-local artifact directory | todo (closes when dir exists+indexed) | factory-reporter | factory-orchestrator | artifact dir created by FRE-010 |
| R2 — Reconciliation: complete required Factory methodology documentation | todo (closes when docs committed) | factory-reporter | factory-orchestrator | 14 docs committed by FRE-010 |
| FRE-011 Generic human-question retirement/rework | planned (TASK_GRAPH) | zeus builder | quality-reviewer | TDD RED/GREEN in `test_factory_control_plane_refactor.py` |
| FRE-012 Direct-human escalation validation | planned (TASK_GRAPH) | zeus builder | security-reviewer + quality-reviewer | `test_factory_escalation_validation.py` |
| FRE-013 Global watchdog/cron integration | planned (TASK_GRAPH) | zeus builder | devops-release | `test_factory_cron_control_plane.py` |
| FRE-014 Canonical continuation/reopen capability | planned (TASK_GRAPH) | zeus builder | solution-architect | `test_factory_project_reopen.py` |
| FRE-015 Independent QA/security review | planned (TASK_GRAPH) | quality-reviewer + security-reviewer | factory-orchestrator | QA_REPORT.md, SECURITY_REVIEW.md |
| FRE-016 PR-first delivery | planned (TASK_GRAPH) | devops-release + factory-orchestrator | factory-orchestrator | CHANGE_RECORDS.md, DELIVERY_REPORT.md |
| FRE-017 Global cron verification | planned (TASK_GRAPH) | devops-release | factory-orchestrator | cron smoke evidence |
| FRE-020 Technical rework escalation and canonical continuation recovery | implemented (local branch; not pushed/closed) | claude-builder | quality-reviewer + solution-architect | TDD RED commit `4e2d163ac`; GREEN focused Factory tests 134/134; code/docs committed on assigned branch |
| FRE-021 Review outcome semantic integrity and failed-review recovery | implemented (local branch; not pushed/closed) | claude-builder | quality-reviewer | TDD RED observed before production change; GREEN targeted 2/2 and focused Factory tests 136/136; code/docs committed on assigned branch |

## 2. Evidence log (real, 2026-08-10)

1. `hermes factory status factory-runtime-evolution-continuation --json` (48,655 B):
   project active; 14 G1 docs blocking; human_questions=[]; gates=[]; anomalies as above.
2. Planning-review reconciliation: independent content review passed in Factory
   planning gate `690` on 2026-08-10. This doc-only follow-up aligns every
   required document with `reviewed:true` markers after prior gate `684` failed on
   missing per-document status rows; no active FRE-010 rework remains.
3. Runtime analysis (baseline commit `20228c116`):
   - `hermes_cli/factory_pg.py:4523` supervisor_health_check; `:4584–4586` pending-question
     → manual_attention bypass; `:3423` bounded requeue; `:3479` mark_project_manual_attention;
     `:2429` close_project (no reopen counterpart); `:247` TERMINAL_PROJECT_STATUSES.
   - `hermes_cli/factory_pg.py:3205` classifier taxonomy; `:3312` question creation with
     `human_question_skipped_unactionable` guard; `:3351` explicit-question requirement.
   - `hermes_cli/factory_contracts.py` closed contracts.
   - `scripts/factory/*` repo-backed cron scripts (L1/L2/watchdog/status/reviewer).
   - Tests: `tests/hermes_cli/test_factory_control_plane_refactor.py:757/788/850`,
     `test_factory_cron_control_plane.py`, `test_factory_orchestrator_tick.py`,
     `test_factory_increment_integration.py`.
4. Predecessor operational evidence: `QA_REPORT.md:227–234` (idle smoke
   classified=0/questions=0/alerts=0), `RETROSPECTIVE_INC_0008.md` (cron ownership),
   `TRACKER.md` (INC-0006..0009), `FACTORY_RUNTIME_EVOLUTION_PLAN.md` (L1/L2/L3),
   git `d3d08dc2e` + `bc7ab6af6`.
5. FRE-020 strict TDD RED evidence (tests committed first at `4e2d163ac`):
   `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_project_reopen.py tests/hermes_cli/test_factory.py -k 'technical_rework_creates_autonomous_recovery or invalid_existing_human_question or manual_attention_refuses_invalid or stranded_technical_manual_attention or project_reopen or project_create_suggests_reopen or registers_project_reopen'` → 9 failed / 0 passed, including missing `reopen_project`, missing CLI `project reopen`, exhausted technical rework still becoming `mark_project_manual_attention`, and generic pending human questions not retired.
6. FRE-020 GREEN evidence after production change:
   same focused command plus `-q` → 9 passed / 0 failed; then full focused Factory set
   `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python scripts/run_tests.sh tests/hermes_cli/test_factory.py tests/hermes_cli/test_factory_project_reopen.py tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_cron_control_plane.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_ux_ui_designer_contract.py` → 134 passed / 0 failed.
   CLI smoke against the worktree module: `PYTHONPATH=. /home/jean/Projects/hermes-agent-original/venv/bin/python -m hermes_cli.main factory project reopen --help` → exit 0 and shows `project_id`, `--reason`, `--actor`, `--continuation-of`, `--json`.
7. FRE-020 implemented controls:
   - `hermes_cli/factory_pg.py`: no exhausted non-human `technical_rework` path writes manual_attention; bounded exhaustion creates/reuses one durable autonomous recovery task plus `technical_rework_escalated_autonomously` audit event; stale `technical_rework_retries_exhausted` manual_attention with same-project recovery task restores active/autonomous with `autonomous_recovery_restored` audit.
   - `hermes_cli/factory_pg.py` + `factory_contracts.py`: `QuestionStatus`, `JeanEscalationCategory`, and fail-closed human-question validation; invalid/generic/stale questions retire to autonomous repair.
   - `hermes_cli/factory_pg.py` + `hermes_cli/factory.py`: canonical `reopen_project`/`hermes factory project reopen|continue` with G0/G1/manual-takeover preflight, reopen gate, lineage audit, no detached project insert; create-path suggests reopen when continuation lineage points at terminal project.
8. FRE-021 strict TDD RED evidence:
   `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py::test_final_semantic_state_rejects_wrapped_instructional_done_marker_without_final_verdict tests/hermes_cli/test_factory_increment_integration.py::test_mark_run_finished_failed_review_with_wrapped_instruction_remains_rework -v` → 2 failed / 0 passed before production change. Failures proved the real reproduction: wrapped `STATE: DONE; si falla...` parsed as `done`, and failed review output invoked increment integration instead of remaining rework.
9. FRE-021 GREEN evidence after production change:
   same targeted command → 2 passed / 0 failed; then full focused Factory set
   `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python scripts/run_tests.sh tests/hermes_cli/test_factory.py tests/hermes_cli/test_factory_project_reopen.py tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_cron_control_plane.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_ux_ui_designer_contract.py` → 136 passed / 0 failed.
10. FRE-021 implemented controls:
    - `hermes_cli/factory_pg.py`: semantic marker parsing now requires the whole cleaned line to be a canonical marker (`STATE: DONE`, `STATE: BLOCKED`, `STATE: IN_PROGRESS`, optional `FINAL:` prefix); wrapped/instructional prose is ignored and cannot override a nonzero review outcome.
    - `hermes_cli/factory_pg.py`: failed review runs without an actual final verdict remain `failed`/`rework`, skip increment integration/terminal close semantics, and write `review_run_failed` audit events with the failure summary tail.

## 3. Gate log

| Gate | Status | Evidence |
|---|---|---|
| G0 Repository Strategy | passed | DB `project_created` event 172950 (repo_scope zeus_only, base main, per_deliverable worktrees) |
| G1 Documentary Readiness | passed | 14 docs exist/indexed/committed/validated:true/reviewed:true after solution-architect review; planning gate 690=passed |
| Review (FRE-010) | passed | solution-architect review, 2026-08-10, planning gate 690 |
| Delivery | not applicable yet | no product-runtime code in G1 |
| FRE-020 test evidence | passed | Factory test gate recorded by claude-builder; TDD RED captured at `4e2d163ac`; GREEN Factory tests 134/134; no push/merge/PR/Factory close performed |
| FRE-021 test evidence | passed | TDD RED captured before production change; GREEN targeted 2/2 and focused Factory tests 136/136; no push/merge/PR/Factory close performed |

## 4. Risk register

| Risk | Mitigation |
|---|---|
| Document/DB review-marker drift after G1 review | Keep per-document `validated:true` and `reviewed:true` rows synchronized with the recorded Factory planning gate evidence before downstream dispatch |
| Detached successor semantics confuse lineage | FRE-014 adds reopen/continue; this project records `continuation_of: factory-runtime-evolution` intent in its docs now |
| Technical failures strand projects in manual_attention | FRE-020 fail-closes invalid human questions and routes retry exhaustion to autonomous recovery with audit, not human/manual hold |
| Wrapped/instructional final-marker prose closes failed reviews | FRE-021 strict standalone marker parsing + failed-review audit event keeps no-verdict review failures in failed/rework |
| Cron resume regressions | FRE-013/017 incremental resume with smoke evidence; idle-silence rule preserved |
| Change-detector tests in new suites | QA_GATES.md bans them; reviewers enforce |

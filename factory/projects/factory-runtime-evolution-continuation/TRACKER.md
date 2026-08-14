# Tracker — Factory Runtime Evolution — Continuation

| Field | Value |
|---|---|
| Document status | baseline reviewed:true (solution-architect, 2026-08-10, planning gate 690); FRE-025 amendment validated:true (implementation owner, 2026-08-12), reviewed:pending |
| Project ID | `factory-runtime-evolution-continuation` |
| Predecessor | `factory-runtime-evolution` (terminal: completed; continuation lineage pending FRE-014) |
| Methodology | Hybrid (zeus_native lane + bmad_hybrid lane) |
| Source of truth | Agent Core Postgres `zeus_agent.factory` |
| Repo artifacts | `factory/projects/factory-runtime-evolution-continuation/` |
| Repo | `SiteOneTech/hermes-agent-original` (zeus_only) |
| Current state | `active` — terminal source-bearing increments are being reconciled into `origin/main`; FRE-024 branch-metadata/source-delivery evidence plus FRE-020/FRE-021/FRE-022, FRE-025, and FRE-027 evidence retained for delivery traceability. |
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
| FRE-022 Strict canonical semantic marker lexical contract | implemented (local branch; not pushed/closed) | claude-builder | security-reviewer | TDD RED observed before production change; GREEN targeted 17/17, preservation 2/2, and focused Factory tests 153/153; code/docs committed on assigned branch |
| FRE-023 Reviewed G1 candidate visibility and fail-closed preflight | claimed/in implementation | claude-builder | security-reviewer + quality-reviewer | TDD coverage in `tests/hermes_cli/test_factory_control_plane_refactor.py`; resolver in `hermes_cli/factory_pg.py` |
| FRE-024 Source delivery dependency integrity and replacement-safe dispatch | rework implemented (this branch) | claude-builder | security-reviewer | `tests/hermes_cli/test_factory_increment_integration.py`; fail-closed dependency/source-delivery dispatch checks |
| FRE-025 Pause provenance, technical holds, and source-delivery guard | implemented; owner verification in progress | implementation owner | independent reviewer | behavior RED/GREEN + exact focused suite + `RETROSPECTIVE_FRE_025.md` |
| FRE-027 Enforce Factory migration readiness before orchestration | implemented; owner verification complete | claude-builder | qa/security/quality gates as assigned | migration-readiness RED/GREEN + focused Factory suite + `IMPLEMENTATION_REPORT_FRE_027.md` |

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
5. FRE-025 behavior-first evidence (2026-08-12): selected regression command RED
   `16 failed, 2 passed in 2.23s`; identical selection GREEN
   `18 passed in 0.78s`. Final owner verification (2026-08-13T08:28:52Z):
   focused `scripts/run_tests.sh` suite `161 passed, 0 failed`; `git diff --check`
   exit 0. Details are recorded in `RETROSPECTIVE_FRE_025.md`.
6. FRE-027 migration-readiness evidence (2026-08-14): RED reproduced opaque
   missing-000004 behavior (`psql` exit status 3), missing orchestrator preflight
   (`DID NOT RAISE SystemExit`), and missing module-scoped migration CLI
   (`--module` unrecognized / no `verify_module`). GREEN: focused Factory suite
   `9 files, 173 tests passed, 0 failed`; `test_agent_core_roles.py` `3 passed`;
   `py_compile` and `git diff --check` exit 0. Details are recorded in
   `IMPLEMENTATION_REPORT_FRE_027.md`.

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
11. FRE-022 strict TDD RED evidence:
    `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'semantic_state_accepts_only_exact_canonical_marker_lines or semantic_state_rejects_noncanonical_lexical_variants' -v` → 8 failed / 9 passed before production change. Failures proved the listed noncanonical variants were still accepted (`STATE:DONE`, `STATE : DONE`, `state: done`, `FINAL:STATE: DONE`, extra internal spaces, case variants) while exact canonical marker forms remained accepted.
12. FRE-022 GREEN evidence after production change:
    same targeted lexical command → 17 passed / 0 failed.
13. FRE-022 preservation evidence:
    `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py::test_monitor_runs_finalizes_stale_final_marker_without_exit_file tests/hermes_cli/test_factory_increment_integration.py::test_mark_run_finished_failed_review_with_wrapped_instruction_remains_rework -v` → 2 passed / 0 failed. This preserves stale-worker recovery for valid canonical `STATE: DONE` and the real wrapped 429 review behavior (`failed`/`rework`, no integration/done, `review_run_failed`).
14. FRE-022 focused Factory regression set:
    `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python scripts/run_tests.sh tests/hermes_cli/test_factory.py tests/hermes_cli/test_factory_project_reopen.py tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_cron_control_plane.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_ux_ui_designer_contract.py` → 153 passed / 0 failed.
15. FRE-022 implemented controls:
    - `hermes_cli/factory_pg.py`: `_semantic_state_from_line()` now uses an exact canonical marker map after ANSI/leading-decoration cleanup; removed case-insensitive/flexible-whitespace regex matching and legacy no-space `STATE:DONE` marker acceptance.
    - `tests/hermes_cli/test_factory_control_plane_refactor.py`: lexical contract tests assert six exact canonical forms accepted and listed noncanonical variants/suffixed prose rejected.

5. FRE-023 TDD evidence (2026-08-10): RED
   `scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'reviewed_g1_candidate or unverified_g1_worktree'`
   failed before implementation with `KeyError: 'readiness_source'` and the exact
   candidate readiness assertion still blocking. GREEN after the resolver:
   the same command passed `11 tests passed, 0 failed`; the full focused file
   passed `101 tests passed, 0 failed`; sibling checks
   `scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory.py tests/hermes_cli/test_factory_orchestrator_tick.py`
   passed `20 tests passed, 0 failed`; the full factory set
   `scripts/run_tests.sh tests/hermes_cli/test_factory*.py` passed
   `138 tests passed, 0 failed`.
6. FRE-023 implementation contract: primary checkout remains the default
   document source; `reviewed_g1_candidate` metadata is accepted only when path,
   branch, SHA, clean git readback, open PR head evidence, independent review
   evidence, and committed positive G1 markers all match. Invalid metadata,
   dirty artifacts, wrong SHA/branch, closed/stale/wrong-head PR evidence, and
   negative document markers fall back to primary blockers.
7. FRE-023 independent security review evidence (Claude Code Haiku review session
   `2b4e6ba7-f234-4a4c-a6e4-8df87e798a50`): PASS. Reviewer found no bypass for
   path/branch/SHA readback, clean checkout, open PR head, independent review,
   primary-default behavior, unverified-worktree bypass, or external side effects.

5. FRE-024 implementation evidence (2026-08-10, branch
   `factory/factory-runtime-evolution-continuation/inc-024-fre-024-source-delivery-dependen`):
   - RED command: `scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'cancelled_dependency_without_replacement or missing_dependency_task or claimable_autonomous_work_ignores_superseded or replacement_pr_open_not_in_base or accepted_replacement or without_qa_guardian or wrong_head_replacement' -v --tb=short` → 6 failed, 1 passed, 13 deselected. Failures reproduced cancelled/superseded dependency dispatch, missing dependency, open/not-in-base replacement PR, absent QA Guardian evidence, and wrong-head PR.
   - GREEN commands: `scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -v --tb=short` → 25 passed; `scripts/run_tests.sh tests/hermes_cli/test_factory*.py --tb=short` → 139 passed; `.venv/bin/ruff check hermes_cli/factory_pg.py hermes_cli/factory_contracts.py tests/hermes_cli/test_factory_increment_integration.py` → all checks passed.
   - Environment note: canonical runner initially blocked because no pytest venv existed; created repo-local `.venv` via `uv sync --frozen --extra dev` for implementation verification.
   - Factory gate evidence: implementation gate 725 recorded as `passed` by `claude-builder`; PR opened at `https://github.com/SiteOneTech/hermes-agent-original/pull/26`.
6. FRE-024 security rework evidence (2026-08-10, same branch):
   - Security gate 726 failed because QA Guardian evidence accepted scalar/status-only values without exact candidate commit binding.
   - RED command: `scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'scalar_qa_guardian_evidence or qa_guardian_evidence_without_commit or qa_guardian_commit_mismatch or qa_guardian_commit_bound_evidence' -v --tb=short` → 2 failed, 2 passed. Failures reproduced scalar `qa_guardian_evidence=True` and `{status: passed}` without commit dispatching downstream work.
   - GREEN commands: same focused command → 4 passed; `scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -v --tb=short` → 29 passed; `scripts/run_tests.sh tests/hermes_cli/test_factory*.py --tb=short` → 143 passed; `.venv/bin/ruff check hermes_cli/factory_pg.py hermes_cli/factory_contracts.py tests/hermes_cli/test_factory_increment_integration.py` → all checks passed; `git diff --check` → exit 0.
   - Runtime contract tightened: source delivery QA Guardian evidence must be a dict with accepted/passed status and an exact commit matching the replacement branch head; scalar/missing/mismatched commit evidence fails closed.
   - Factory gate evidence: refreshed implementation gate recorded as `passed` after the rework branch push; latest gate id is in Agent Core Postgres `factory.gates`.
7. FRE-024 second security rework evidence (2026-08-10, same branch):
   - Security gate 729 failed after review; rework hardened the remaining replacement/source-delivery fail-closed surface identified in review.
   - RED command: `scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'unbound_replacement or without_pr_even_without_policy or contradictory_source_delivery_acceptance or option_like_branch' -v --tb=short` → 4 failed, 29 deselected. Failures reproduced one-way replacement binding, PR omission when policy metadata is absent, contradictory accepted/rejected source-delivery status, and option-like branch metadata reaching git.
   - GREEN commands: same focused command → 4 passed; `scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -v --tb=short` → 33 passed; `scripts/run_tests.sh tests/hermes_cli/test_factory*.py --tb=short` → 147 passed; `.venv/bin/ruff check hermes_cli/factory_pg.py hermes_cli/factory_contracts.py tests/hermes_cli/test_factory_increment_integration.py` → all checks passed; `git diff --check` → exit 0.
   - Runtime contract tightened: replacement tasks must back-reference the superseded/cancelled task, PR evidence is required by default for source delivery, contradictory source-delivery outcomes fail closed, and unsafe/option-like branch metadata is rejected before dependency dispatch or increment integration git operations.
   - Factory gate evidence: implementation gate `730` recorded as `passed` after commit `91538698f051e69e594974b079939d5109ef2c7a` was pushed; security gate remains pending for independent reviewer after rework.
8. FRE-024 third security rework evidence (2026-08-10, same branch):
   - Security gate 732 failed because positive-terminal source replacements with `source_delivery` or replacement metadata still bypassed source-delivery PR/QA/base checks when branch, worktree, or base-branch metadata made `_increment_integration_required()` return false before `_dependency_increment_blockers()` validated them.
   - RED command: `scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'without_branch or without_worktree or on_base_branch' -v --tb=short` → 3 failed, 33 deselected. Failures reproduced downstream dispatch for a superseded predecessor whose positive replacement had source-delivery evidence but no branch, no worktree path, or branch equal to `main`.
   - GREEN commands: same focused command → 3 passed; `scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -v --tb=short` → 36 passed; `scripts/run_tests.sh tests/hermes_cli/test_factory*.py --tb=short` → 150 passed; `.venv/bin/ruff check hermes_cli/factory_pg.py tests/hermes_cli/test_factory_increment_integration.py` → all checks passed.
   - Runtime contract tightened: dependencies with `source_delivery` or explicit replacement metadata now require source-delivery integrity even when terminal integration would otherwise skip; missing branch, missing worktree path, or branch equal to base returns `unverified_branch_metadata` before downstream product dispatch.
   - Factory gate evidence: refreshed implementation gate recorded after commit/push; latest gate id is in Agent Core Postgres `factory.gates`.
9. FRE-024 fourth security rework evidence (2026-08-11, same branch):
   - Security gate 734 failed after independent review. Claude Code static review of the diff identified remaining PR parsing gaps: string `merged="false"` counted as truthy, and missing PR `head_commit`, `base_branch`, or clean/mergeable evidence passed by omission.
   - RED command: `scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'string_false_merged_replacement_pr or pr_without_head_commit or pr_without_base_branch or pr_without_clean_evidence' -v --tb=short` → 4 failed, 36 deselected. Failures reproduced downstream dispatch for a superseded predecessor whose replacement PR was open with string `merged="false"`, or whose accepted PR record lacked exact head/base/clean evidence.
   - GREEN commands: same focused command → 4 passed; `scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -v --tb=short` → 40 passed; `scripts/run_tests.sh tests/hermes_cli/test_factory*.py --tb=short` → 154 passed; `.venv/bin/ruff check hermes_cli/factory_pg.py hermes_cli/factory_contracts.py tests/hermes_cli/test_factory_increment_integration.py && git diff --check` → all checks passed.
   - Runtime contract tightened: replacement/source-delivery PR evidence now normalizes boolean-like fields fail-closed, requires exact PR head commit, requires PR base branch to match the Factory base branch, and requires explicit clean/mergeable evidence before downstream dispatch.
   - Factory gate evidence: implementation gate `735` recorded as `passed` after commit `e008ff45f` was pushed; independent security review remains required.
10. FRE-024 fifth security rework evidence (2026-08-11T01:43:30Z, same branch):
   - Rework target from independent review: reject base aliases and pseudorefs (`main`, `origin/main`, `refs/heads/main`, `refs/remotes/origin/main`, `HEAD`, `FETCH_HEAD`, `ORIG_HEAD`, `MERGE_HEAD`, `origin/HEAD`) before dispatch dependency fetch/resolve and before `_integrate_increment_to_base` git operations.
   - Claude Code engine invocation: `claude-anthropic-code -p ... --allowedTools 'Read' --max-turns 4 --output-format json` reached `error_max_turns`; resumed session `2b06ebcd-ea02-48a7-9467-5b8f3b546b09` with no tools and received focused findings for `_factory_branch_ref_blocker`, `_increment_integration_required`, `_integrate_increment_to_base`, `_dependency_increment_blockers`, and `_resolve_git_ref`.
   - RED command: `scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'base_alias_and_pseudoref or option_like_branch' -v --tb=short` → 26 failed, 5 passed, 41 deselected. Failures reproduced `refs/heads/main`, `refs/remotes/origin/main`, `HEAD`, `FETCH_HEAD`, `ORIG_HEAD`, `MERGE_HEAD`, and `origin/HEAD` reaching dependency/integration logic or making `_increment_integration_required()` true.
   - GREEN commands: same focused command → 31 passed; `scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -v --tb=short` → 72 passed; `scripts/run_tests.sh tests/hermes_cli/test_factory*.py --tb=short` → 186 passed; `.venv/bin/ruff check hermes_cli/factory_pg.py hermes_cli/factory_contracts.py tests/hermes_cli/test_factory_increment_integration.py` → all checks passed; `git diff --check` → exit 0.
   - Runtime contract tightened: branch metadata guard now normalizes `refs/heads/*` and `refs/remotes/*`, rejects base-branch aliases plus git pseudorefs in the same guard used by dispatch dependency checks and increment integration, and `_resolve_git_ref()` has defense-in-depth against resolving unsafe metadata.
   - Factory gate evidence: implementation gate `739` recorded as `passed` after commit `6c7a34634` was pushed; independent security review remains required.

## 3. Gate log

| Gate | Status | Evidence |
|---|---|---|
| G0 Repository Strategy | passed | DB `project_created` event 172950 (repo_scope zeus_only, base main, per_deliverable worktrees) |
| G1 Documentary Readiness | passed | 14 docs exist/indexed/committed/validated:true/reviewed:true after solution-architect review; planning gate 690=passed |
| Review (FRE-010) | passed | solution-architect review, 2026-08-10, planning gate 690 |
| Implementation (FRE-024) | rework implemented after latest security review | Factory gate 725 originally passed; security gates 726/729/732/734 failed; TDD RED/GREEN rework evidence listed in evidence log items 6–10; refreshed implementation gate 739 passed after commit/push; independent security review still required before delivery/merge |
| Delivery | not applicable yet | no product-runtime code in G1 |
| FRE-020 test evidence | passed | Factory test gate recorded by claude-builder; TDD RED captured at `4e2d163ac`; GREEN Factory tests 134/134; no push/merge/PR/Factory close performed |
| FRE-021 test evidence | passed | TDD RED captured before production change; GREEN targeted 2/2 and focused Factory tests 136/136; no push/merge/PR/Factory close performed |
| FRE-022 test evidence | passed | TDD RED captured before production change; GREEN lexical 17/17, preservation 2/2, focused Factory tests 153/153; no deploy/merge/Factory close performed |
| FRE-025 owner QA | passed | focused suite `161 passed, 0 failed`; `git diff --check` exit 0; exact commands in `RETROSPECTIVE_FRE_025.md` |
| FRE-025 independent review | pending | must review the exact committed diff |
| FRE-025 source integration | pending | branch must be verified integrated into declared `origin/main`; existing open PRs remain independently gated |
| FRE-027 owner QA | passed | RED/GREEN captured; focused Factory suite `173 passed, 0 failed`; `test_agent_core_roles.py` `3 passed`; syntax/help/diff checks green |

## 4. Risk register

| Risk | Mitigation |
|---|---|
| Document/DB review-marker drift after G1 review | Keep per-document `validated:true` and `reviewed:true` rows synchronized with the recorded Factory planning gate evidence before downstream dispatch |
| Detached successor semantics confuse lineage | FRE-014 adds reopen/continue; this project records `continuation_of: factory-runtime-evolution` intent in its docs now |
| Technical failures strand projects in manual_attention | FRE-020 fail-closes invalid human questions and routes retry exhaustion to autonomous recovery with audit, not human/manual hold |
| Wrapped/instructional final-marker prose closes failed reviews | FRE-021 strict standalone marker parsing + failed-review audit event keeps no-verdict review failures in failed/rework |
| Noncanonical lexical marker variants bypass strict review semantics | FRE-022 exact canonical marker map rejects no-space, case-variant, extra-internal-space, and suffixed/instructional marker prose fail-closed |
| Cron resume regressions | FRE-013/017 incremental resume with smoke evidence; idle-silence rule preserved |
| Change-detector tests in new suites | QA_GATES.md bans them; reviewers enforce |
| System actor mislabels a technical block as a human pause | Manual pause requires explicit nonblank authority and origin and rejects reserved actors; canonical technical hold remains supervisable |
| Terminal source increment reconciles before integration | Reconciliation and delivery share a branch-integration guard; successor auto-resume consumes the blocker; only explicit Jean authorization waives it |
| Existing misleading system-attributed user pauses persist | Migrate individually through canonical `technical-hold` after verification; never bulk-edit DB and never downgrade `manual_attention` |
| Factory runtime starts against a DB missing migration `000004` | `ensure_runtime_schema()` now fails closed with a migration-readiness diagnostic before lease/claim/spawn; recovery path is `scripts/agent_core_db.py migrate --module factory` + `verify --module factory` |

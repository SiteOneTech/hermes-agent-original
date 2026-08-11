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
| Current state | `active` — FRE-010 planning-review passed (solution-architect, 2026-08-10, planning gate 690); FRE-024 security gates 726/729/732 failed during independent review; latest rework hardens source-delivery replacement branch/worktree/base-branch metadata so downstream dispatch fails closed with concrete blockers, with refreshed implementation evidence recorded after push and independent security review still pending. |
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
| FRE-024 Source delivery dependency integrity and replacement-safe dispatch | rework implemented (this branch) | claude-builder | security-reviewer | `tests/hermes_cli/test_factory_increment_integration.py`; fail-closed dependency/source-delivery dispatch checks |

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

## 3. Gate log

| Gate | Status | Evidence |
|---|---|---|
| G0 Repository Strategy | passed | DB `project_created` event 172950 (repo_scope zeus_only, base main, per_deliverable worktrees) |
| G1 Documentary Readiness | passed | 14 docs exist/indexed/committed/validated:true/reviewed:true after solution-architect review; planning gate 690=passed |
| Review (FRE-010) | passed | solution-architect review, 2026-08-10, planning gate 690 |
| Implementation (FRE-024) | rework implemented after third security review | Factory gate 725 originally passed; security gates 726/729/732 failed; TDD RED/GREEN rework evidence listed in evidence log items 6–8; refreshed implementation evidence recorded after commit/push; independent security review still required before delivery/merge |
| Delivery | not applicable yet | no product-runtime code in G1 |

## 4. Risk register

| Risk | Mitigation |
|---|---|
| Document/DB review-marker drift after G1 review | Keep per-document `validated:true` and `reviewed:true` rows synchronized with the recorded Factory planning gate evidence before downstream dispatch |
| Detached successor semantics confuse lineage | FRE-014 adds reopen/continue; this project records `continuation_of: factory-runtime-evolution` intent in its docs now |
| Cron resume regressions | FRE-013/017 incremental resume with smoke evidence; idle-silence rule preserved |
| Change-detector tests in new suites | QA_GATES.md bans them; reviewers enforce |

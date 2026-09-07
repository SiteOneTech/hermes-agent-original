---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2f8-current-source-tick-dispatcher-rout
phase: g1_recovery
status: candidate
validated: yes
reviewed: pending
owner: codex-builder
reviewer: quality-reviewer
run_id: run-1788794358-dabf9d7e
---

# R2f8 — current-source tick dispatcher routing repair

## Scope

Bounded Factory scheduler/source-routing repair only. This candidate keeps product, ALR, QA, security, deploy, messaging, external runtime, broker, trading, risk, paper/live, credentials, primary-checkout mutation, direct SQL, and merge actions out of scope. The only changed runtime behavior is the source provenance used by the Factory tick dispatcher and the nested worker process launched by `scripts/factory/factory_orchestrator_tick.py`.

## Canonical inputs consulted

- `DOCUMENTATION_INDEX.md` — controlling G1/documentation index and source-root recovery history.
- `G0_REPOSITORY_STRATEGY.md` — `zeus_only` / `add_functionality`, assigned branch/worktree, PR-first delivery.
- `DATABASE_AND_RUNTIME_CONTRACT.md` — Agent Core Postgres as source of truth, no direct SQL, no external runtime/product activation.
- `TECHNICAL_BLUEPRINT.md` and `METHODOLOGY_PLAN.md` — Factory/control-plane separation from Zeus ALR product runtime.
- `QA_GATES.md` and `SECURITY_GATES.md` — verification and fail-closed boundaries.

## Source and status evidence

- Assigned branch: `factory/zeus-alpha-research-ledger-core/inc-126-r2f8-current-source-tick-route`.
- Assigned worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-126-r2f8-current-source-tick-route`.
- Pre-edit base readback: `HEAD=origin/main=merge-base=d0cdd5c2a7e3c5a18107d4b0e965477b5a183f1c`; remote `https://github.com/SiteOneTech/hermes-agent-original.git`.
- Primary checkout audit-only readback from the task prompt/history: `/home/jean/Projects/hermes-agent-original` at `ac1fdb16051324c490d803b14dd06efffd6f9ad0`; it remains unmodified and is not used as candidate source.
- Canonical status command used: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json` from the assigned worktree.
- Status summary: `R2F8_STATUS_READBACK_SUMMARY.json` reports `factory_cli_source_root` and `factory_status_source_root` both equal to the assigned worktree, `factory_status_delegated=false`, project `active`, `autonomous_enabled=true`, and current active run `run-1788794358-dabf9d7e` for this R2f8 task.
- The prompt's red-G1 projection was rechecked against live Agent Core status. The canonical current-source readback now reports `g1_required.total=14`, `g1_required.blockers=0`, `blocking_files=[]`; therefore the live tick was not used to open another increment.

## RED reproduction

Command captured in `R2F8_RED_TEST_OUTPUT.txt`:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k 'project_tick_prefers_configured_base_source_when_invoked_from_stale_primary_root or spawn_worker_uses_current_python_module_not_path_hermes' -v --tb=short`

Observed RED before production repair:

- `2 failed, 22 deselected` in `tests/hermes_cli/test_factory_orchestrator_tick.py`.
- `test_project_tick_prefers_configured_base_source_when_invoked_from_stale_primary_root` failed because `HERMES_PYTHON_SRC_ROOT` stayed pinned to the stale primary root instead of the configured/current worktree.
- `test_spawn_worker_uses_current_python_module_not_path_hermes` failed with `KeyError: 'env'`, proving the nested dispatcher wrapper inherited ambient/stale source semantics instead of receiving an explicit worker source environment.

## GREEN repair

Changed behavior:

- `hermes_cli/factory.py::_source_env()` now pins `HERMES_PYTHON_SRC_ROOT` to the verified source root used for the top-level `factory project tick` subprocess, matching the already-pinned `cwd`, script path, and `PYTHONPATH`.
- `scripts/factory/factory_orchestrator_tick.py::_spawn_worker()` now builds a fail-closed nested worker environment from the prepared worktree provenance: `PYTHONPATH` starts with the worker source root, `HERMES_PYTHON_SRC_ROOT` equals that root, and `HERMES_FACTORY_SOURCE_DELEGATED=1` is set before spawning the nested dispatcher wrapper.
- Spawn metadata now records `worker_source_root` alongside `worker_cwd`, so post-run evidence can prove the nested worker source provenance without reading ambient process state.
- Existing same-project G1/docs recovery selection remains covered by `test_force_tick_uses_explicit_g1_recovery_metadata_before_review_when_docs_red`, which proves a metadata-classified G1/documentation recovery is claimed while product/review candidates remain unclaimed under red G1 rows.

## Verification

Commands run from the assigned worktree:

1. RED: command above with production fix temporarily reversed and new tests intact -> failed as expected, `2 failed, 22 deselected`. Output: `R2F8_RED_TEST_OUTPUT.txt`.
2. GREEN targeted: same command with the repair restored -> passed, `2 tests passed, 0 failed`. Output: `R2F8_GREEN_TARGETED_TEST_OUTPUT.txt`.
3. Focused Factory tests: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_increment_integration.py -v --tb=short` -> passed, `171 tests passed, 0 failed`. Output: `R2F8_GREEN_FOCUSED_TEST_OUTPUT.txt`.
4. Whitespace check: `git diff --check` -> exit 0 and empty output. Output: `R2F8_GIT_DIFF_CHECK_OUTPUT.txt`.

## Canonical readbacks

- `R2F8_STATUS_READBACK_SUMMARY.json`: current-source status readback before live resolve/tick evidence; active run remained this R2f8 run, not a new increment.
- `R2F8_RESOLVE_STATE_READBACK_SUMMARY.json`: `factory project resolve-state` readback from the assigned worktree; source roots match the assigned worktree, `factory_project_action_delegated=false`, monitor checked 1 active run, supervisor health `green`, and no new task was created.
- `R2F8_TICK_READBACK_SUMMARY.json`: `factory project tick` readback from the assigned worktree; `factory_orchestrator_script` equals `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-126-r2f8-current-source-tick-route/scripts/factory/factory_orchestrator_tick.py`, `claimed=null`, `spawned_worker=null`, and `counts.active_runs=1`, so the live readback did not open another increment while this R2f8 run was active.
- `R2F8_FINAL_STATUS_READBACK_SUMMARY.json`: final status readback keeps `factory_cli_source_root` and `factory_status_source_root` equal to the assigned worktree; active run remains `run-1788794358-dabf9d7e`; `g1_required.blockers=0`.

## PR-first handoff

This artifact is candidate evidence only. A commit cannot include its own SHA; the final candidate SHA, pushed branch, PR URL, and Factory gate evidence must be recorded after commit/push. The candidate is prepared for Zeus-signed `agent:zeus` PR delivery and requires independent exact-SHA quality review before merge or downstream reliance. No merge, deploy, primary checkout mutation, credential change, product dispatch, direct SQL, external runtime, broker/trading/risk, or paper/live action is authorized by this artifact.

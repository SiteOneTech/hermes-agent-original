---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2am-repair-stale-primary-factory-tick-s
phase: documentation
status: implemented_pending_pr_and_independent_exact_sha_review
validated: yes
reviewed: pending_independent_review
owner: codex-builder
branch: factory/zeus-alpha-research-ledger-core/inc-035-r2am-repair-stale-primary-factor
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-035-r2am-repair-stale-primary-factor
---

# R2am — stale-primary Factory tick source-resolution repair

## Scope

This increment repairs only Factory project tick source resolution. It does not change Zeus Alpha Research Ledger product behavior, external runtimes, deployments, credentials, messaging, trading, risk, brokers, third-party connectors, or the primary checkout at `/home/jean/Projects/hermes-agent-original`.

The defect: the profile-level tick wrapper at `~/.hermes/scripts/factory_orchestrator_tick.py` hardcodes `/home/jean/Projects/hermes-agent-original/scripts/factory/factory_orchestrator_tick.py`. When the canonical CLI is invoked from a current isolated worktree, `hermes factory project tick` and the dashboard Factory tick route could still execute the stale primary checkout through that wrapper, allowing old reconciliation code to recreate `unvalidated_required_docs` even though the current worktree implementation reports G1 required documents non-blocking.

## Canonical inputs read before implementation

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2C5_INDEPENDENT_CURRENT_BASE_G1_REVIEW.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2C6_BOUNDED_CURRENT_ORIGIN_G1_RESOLVER_READBACK_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`

Factory source of truth was accessed only through the approved Factory status CLI. No direct `factory.*` SQL was used.

## Base and stale-primary identity

Captured before final commit:

- Assigned worktree branch: `factory/zeus-alpha-research-ledger-core/inc-035-r2am-repair-stale-primary-factor`
- Assigned worktree path: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-035-r2am-repair-stale-primary-factor`
- Assigned worktree `HEAD`: `b525254809fba0ad46e6b7e9405778c44e64bae9`
- Assigned worktree `origin/main`: `b525254809fba0ad46e6b7e9405778c44e64bae9`
- Assigned worktree merge-base: `b525254809fba0ad46e6b7e9405778c44e64bae9`
- Assigned worktree ahead/behind vs `origin/main`: `0\t0`
- Primary checkout status: `main...origin/main [ahead 3, behind 1374]`
- Primary checkout `HEAD`: `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`
- Primary checkout `origin/main`: `b525254809fba0ad46e6b7e9405778c44e64bae9`
- Primary checkout merge-base: `c846ccfbd844c2f8810a26776505ec44a2341914`
- Primary checkout ahead/behind: `3\t1374`

The primary checkout was inspected only for identity evidence; it was not modified.

## Implementation summary

Changed files:

- `hermes_cli/factory.py`
  - resolves the orchestrator tick script from the running `hermes_cli.factory` source root (`Path(__file__).resolve().parents[1] / scripts/factory/factory_orchestrator_tick.py`) instead of `~/.hermes/scripts/factory_orchestrator_tick.py`;
  - runs the tick with `cwd` set to that source root;
  - prepends the same source root to `PYTHONPATH`, so the subprocess imports the same current Factory implementation as the invoked canonical CLI;
  - fails closed if the running source provenance is malformed or if the current source tree does not contain the tick script.
- `hermes_cli/web_server.py`
  - routes dashboard Factory `tick` / `resume` actions through the canonical CLI helper instead of duplicating the stale `~/.hermes/scripts` wrapper path.
- `tests/hermes_cli/test_factory_orchestrator_tick.py`
  - adds RED/GREEN coverage proving project tick ignores a stale profile wrapper, uses the running source-tree script, sets `cwd` and `PYTHONPATH` to that same source tree, and fails closed for unavailable or malformed provenance.
- `tests/test_web_server.py`
  - adds dashboard-route coverage proving Factory project tick uses the canonical running-source helper.

## RED/GREEN and verification evidence

RED evidence before implementation:

- `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k 'project_tick_uses_running_source_tree or project_tick_fails_closed' -v --tb=short` → failed as expected: `_run_orchestrator_script()` invoked `/tmp/.../.hermes/scripts/factory_orchestrator_tick.py` instead of the worktree script, and unavailable source provenance still attempted to run the stale profile wrapper.
- `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/test_web_server.py -k 'factory_project_tick_route_uses_running_factory_source' -v --tb=short` → failed as expected: the dashboard route executed the existing `~/.hermes/scripts` wrapper instead of the patched canonical helper.

GREEN evidence after implementation:

- `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k 'project_tick_uses_running_source_tree or project_tick_fails_closed' -v --tb=short` → 3 selected tests passed, 0 failed.
- `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/test_web_server.py -k 'factory_project_tick_route_uses_running_factory_source' -v --tb=short` → 1 selected test passed, 0 failed.
- `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py tests/test_web_server.py -v --tb=short` → 17 passed, 0 failed, 3 skipped (Windows-only) across 2 files.
- `git diff --check` → exit 0 before project-local evidence doc updates; final diff check must be rerun after this artifact is committed.

A later live Factory status extraction command exceeded the tool approval/timeout path and was not retried. This increment therefore relies on the approved status read already captured before code changes plus the focused source-resolution tests for the changed behavior. It did not run a live `resolve-state` or live project tick after that blocker, to avoid violating the hard Factory DB command restriction or spawning a new increment from this worker.

## Delivery and review handoff

Delivery remains PR-first. The final commit SHA is recorded in the PR body and Factory evidence after commit creation, because this file cannot name the SHA of the commit that contains itself.

Required next step: independent exact-candidate-SHA quality review before any G1 recovery or implementation dispatch relies on this repair.

No merge, deploy, credential change, direct SQL, external runtime operation, messaging connector, trading/risk/paper/live action, or primary-checkout mutation occurred.

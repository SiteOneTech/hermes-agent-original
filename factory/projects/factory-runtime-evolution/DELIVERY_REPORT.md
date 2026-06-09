# Delivery Report — Factory Runtime Evolution

## Executive summary

The Factory runtime remediation has now completed two technical layers:

1. Operational autonomy repair: blockers are classified, watchdog alerts exist, and blocked projects can be repaired/continued safely.
2. Repo-first Runtime Contract v1: required docs must be listed in `DOCUMENTATION_INDEX.md`, and project-local Factory artifacts must have a git checkpoint before high/critical readiness/delivery closure.

This directly implements Jean's correction: Factory DB remains the operational truth, but the project repository and commits are the professional source of truth for project documentation and implementation history.

## Delivered code/runtime changes

| Area | Evidence |
|---|---|
| Blocker classification/action records | `hermes_cli/factory_pg.py`, `~/.hermes/scripts/factory_blocker_detector.py` |
| Watchdog alerts/notification path | `factory_watchdog_alerts.py`, cron `factory-watchdog-alerts`, status payload alerts |
| Blocked project dispatch repair | Factory dispatcher claim predicates and `force_tick` repair/reopen path |
| Repo-first document index enforcement | `docs_not_indexed` anomaly and critical readiness blocker |
| Git commit checkpoint enforcement | `uncommitted_project_artifacts` anomaly and critical readiness blocker |
| G0 Repository Strategy Gate | `factory_contracts.build_repository_strategy`, `missing_repository_strategy` reconciler anomaly, factory CLI/tool schema `repo_scope`/`work_intent` |
| Per-deliverable branch/worktree contract | `create_task()` derives `branch` + `worktree_path`; `scripts/factory/factory_orchestrator_tick.py` / live `~/.hermes/scripts/factory_orchestrator_tick.py` prepares `git worktree` and starts workers there |
| Factory UI decision card | Dashboard payload `repo_strategy_card` + `FactoryRepositoryStrategyCard` with repo/base branch/deliverable branch/worktree links |
| Canonical administrative project closure | `hermes factory project close` and `factory_pg.close_project()` cancel open work, complete lanes/project, write closure gate/event, and preserve `administrative_closure` metadata without enabling autonomy |
| Resolved reconciliation task reducer | `cancel_resolved_reconciliation_tasks()` cancels stale open recovery rows whose anomaly disappeared, so resolved docs/G0/commit tasks do not keep a project planned/active |
| Canonical task close action | `hermes factory task close` / `factory_pg.close_task()` closes increments with evidence, finalizes active runs, writes `task_closed` events, and optionally reconciles the parent project |
| Unified resolve-state action | `hermes factory project resolve-state` is the canonical project state repair action; legacy `resolve`/`reconcile`/`unblock` aliases remain accepted; dashboard now shows one `Resolver estado` action; resume/autonomous dispatch runs resolve-state preflight first |
| Single-writer/manual takeover lease | `hermes factory project takeover` / `release-takeover` acquire/release a Factory DB metadata lease; resume preflight blocks while the lease is active and dispatcher claim predicates skip leased projects so cron cannot spawn a worker into a manually edited worktree |
| Cron/control-plane source restoration | Factory cron targets now live in repo-backed `scripts/factory/`; `factory_backend`/`factory_contracts`/expanded `factory_pg` are restored in mainline source; live `~/.hermes/scripts` should be thin wrappers to these canonical scripts |
| Sales/Voice/CRM cron ownership separation | `vapi_postcall_worker.py` and `customer_intent_supervisor.py` remain wrappers to `sitiouno-agent-runtime`, preserving Sales Funnel / Voice / CRM workflow ownership instead of merging them into Factory |
| Watchdog idle-silence rule | Repeated `claimed=null` only alerts when runnable autonomous Factory work exists and no active run is present; idle cron ticks stay silent |

## Delivered PM/artifact changes

- Required docs under `factory/projects/factory-runtime-evolution/`.
- `PROJECT_GLOBAL_VISION.md` as compact project memory for Zeus/builders.
- `FACTORY_RUNTIME_CONTRACT_V1.md` documenting the new runtime contract.
- `BUILDER_CONTEXT_TEMPLATE.md` documenting how Claude Code/Codex/OpenHands should receive repo context.
- Updated `DOCUMENTATION_INDEX.md`, `PRD.md`, `SPRINT_PLAN.md`, `TASK_GRAPH.md`, and `QA_REPORT.md`.

## Verification summary

Repo-first Runtime Contract v1 and G0 Repository Strategy were implemented with TDD:

```text
RED: 5 expected failures for missing repository strategy, Zeus routing, existing-project branch/worktree derivation, create_task branch/worktree persistence, and dashboard card payload.
GREEN: 37 passed in test_factory_canonical_runtime.py.
GREEN: 40 passed in test_factory_canonical_runtime.py after adding canonical project close action.
GREEN: 41 passed in test_factory_canonical_runtime.py after adding resolved reconciliation task reducer.
GREEN: 43 passed in test_factory_canonical_runtime.py after adding canonical task close action.
GREEN: 58 passed across Factory + Activity focused tests.
GREEN: npm run build in web/ completed with Vite bundle warning only.
GREEN: py_compile for Factory backend, web server, tool schema, and orchestrator tick script.
GREEN: 50 passed in `tests/hermes_cli/test_factory_canonical_runtime.py` for INC-0006 resolve-state/preflight coverage.
GREEN: 86 passed across Factory + CRM/Sales/Accounting focused suites.
GREEN: `python3 -m py_compile hermes_cli/factory.py hermes_cli/factory_pg.py hermes_cli/web_server.py tests/hermes_cli/test_factory_canonical_runtime.py` completed successfully.
GREEN: `npm ci` restored the worktree-local web toolchain and `npm run build` completed with Vite bundle warning only.
GREEN: RED verified for INC-0007 manual takeover guard, then `python3 -m pytest tests/hermes_cli/test_factory_canonical_runtime.py -q` completed with `54 passed`.
GREEN: `python3 -m pytest tests/hermes_cli/test_factory_canonical_runtime.py tests/hermes_cli/test_factory.py tests/tools/test_factory_tools.py -q` completed with `60 passed, 1 warning`.
GREEN: `python3 -m pytest -o addopts='' tests/hermes_cli/test_factory_canonical_runtime.py tests/hermes_cli/test_factory.py tests/tools/test_factory_tools.py tests/tools/test_crm_tool.py tests/tools/test_sales_tool.py tests/tools/test_accounting_tool.py -q` completed with `90 passed, 1 warning` after INC-0007.
GREEN: `python3 -m py_compile hermes_cli/factory_pg.py hermes_cli/factory.py hermes_cli/web_server.py tests/hermes_cli/test_factory_canonical_runtime.py` completed successfully after INC-0007.
GREEN: `npm ci && npm run build` in `web/` completed after INC-0007; Vite emitted the existing large chunk warning only.
GREEN: INC-0008 focused Factory cron suite completed with `11 passed, 1 warning`.
GREEN: Runtime Sales/Voice/CRM supervisor suite completed with `13 passed` in `sitiouno-agent-runtime`.
GREEN: repo-backed Factory cron scripts ran against Agent Core Postgres: status/reviewer/blocker all exited 0 and watchdog stayed silent with no actionable alerts.
```

Live smoke:

```text
factory-runtime-evolution repo_strategy: passed / zeus_only / add_functionality
Dashboard repo_strategy_card: status=passed, repo_url=https://github.com/SiteOneTech/hermes-agent-original, branch_prefix=factory/factory-runtime-evolution/, worktree_policy=per_deliverable
Reconcile factory-runtime-evolution: anomalies=[]
```

## Residual risks

| Risk | Mitigation |
|---|---|
| Builders still receive prose prompts rather than structured `run_result.json` | Next increment should implement builder context generation and machine-validated run-result output. |
| Direct Zeus recursion can self-approve | Keep tests deterministic and route review to independent worker/profile when the runtime is stable enough. |

## Final close evidence

Final closure was validated after:

1. Project-local artifacts were committed in the repo-first remediation worktree.
2. `hermes factory project reconcile factory-runtime-evolution --json` returned `anomalies=[]`.
3. Final `critical_readiness` and `delivery` gates passed after the commit checkpoint.
4. The project-specific Notion PM page was linked and verified as human reporting projection.

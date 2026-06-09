# Tracker — Factory Runtime Evolution

## Executive status

| Field | Value |
|---|---|
| Project ID | `factory-runtime-evolution` |
| Methodology | Hybrid |
| Source of truth | Agent Core Postgres `factory.*` |
| Repo artifacts | `factory/projects/factory-runtime-evolution/` |
| Notion | Required; created/linked during correction |
| Current state | Active/planned; latest increment restores cron/control-plane source-of-truth and workflow ownership alignment |

## Task tracker

| Task | Status | Owner | Reviewer | Evidence |
|---|---|---|---|---|
| F0 Intake/methodology | done | Zeus/factory-reporter | factory-orchestrator | Factory DB project/lane/task graph + docs |
| F1 Blocker classification | done | Zeus/claude-builder | quality-reviewer | `factory_pg.py`, detector script, tests |
| F2 Watchdog alerts | done | Zeus/claude-builder | devops-release | `factory_watchdog_alerts.py`, cron job |
| F3 Blocked dispatch repair | done | Zeus/claude-builder | security-reviewer | claim predicates, force_tick behavior |
| F4 QA/live smoke | done | Zeus/qa-verifier | factory-orchestrator | 23/23 tests + script smoke |
| F5 Notion/docs correction | done | Zeus/factory-reporter | factory-orchestrator | full docs + Notion metadata |
| R0 Notion reconciliation | done | factory-reconciler | factory-reconciler | Notion page verified; reconcile anomalies=0 |
| INC-0002 G0 Repository Strategy workflow | done | Zeus/factory-orchestrator | tests + UI build | `factory_contracts.py`, `factory_pg.py`, Dashboard G0 card, factory tools/CLI, tick worktree prep |
| INC-0003 Canonical project close action | done | Zeus/factory-orchestrator | TDD + live closure smoke | `hermes factory project close`, `factory_pg.close_project`, closure gate/event metadata |
| INC-0004 Resolved reconciliation task reducer | done | Zeus/factory-orchestrator | TDD + reconciler regression | `cancel_resolved_reconciliation_tasks()`, `reconcile_project()` refreshes tasks before status computation |
| INC-0005 Canonical task close action | done | Zeus/factory-orchestrator | TDD + CLI smoke | `hermes factory task close`, `factory_pg.close_task`, task_closed events, run finalization |
| INC-0006 Unified resolve-state action | done | Zeus/factory-orchestrator | TDD + UI/API smoke | `hermes factory project resolve-state`, single dashboard `Resolver estado`, resume preflight blocks true holds |
| INC-0007 Single-writer/manual takeover lease | done | Zeus/factory-orchestrator | TDD + CLI/API smoke | `hermes factory project takeover/release-takeover`, metadata lease guard, dispatch claim predicates block autonomous workers during manual takeover |
| INC-0008 Cron/control-plane restoration | in review | Zeus/factory-orchestrator | focused tests + live cron smokes | repo-backed `scripts/factory/*`, restored `factory_backend`/contracts/expanded `factory_pg`, runtime wrappers kept in `sitiouno-agent-runtime`, idle watchdog silence rule |
| INC-0009 Documentation-first + Notion control-plane refactor | requested/ready | factory-orchestrator / implementation owner TBD by Factory | independent reviewer required | `INC_0009_FACTORY_DOCS_NOTION_CONTROL_PLANE_REFACTOR.md`; freezes CRM/Funnel Core review until Factory runtime GREEN |

## Open methodology debt

- INC-0009: Funnel Core incident showed the Factory allowed implementation before canonical kickoff docs/Notion metadata were structurally enforced. CRM/Funnel Core review remains frozen until this remediation is GREEN.

## R0 Closure evidence

- Notion PM page: `Factory Runtime Evolution — Factory PM`
- Notion page ID: `37737b39-cad6-8198-a63e-faf0920031d4`
- Notion URL: `https://app.notion.com/p/Factory-Runtime-Remediation-Factory-PM-37737b39cad68198a63efaf0920031d4`
- `hermes factory project reconcile factory-runtime-evolution` → `anomalies: []`
- Acceptance criteria: all 3 met (Notion exists, metadata linked, DB stays source of truth)

## Close criteria

- `hermes factory status factory-runtime-evolution --json` has no `reconciliation_anomalies`.
- Notion metadata present.
- Required docs inventory complete.
- Delivery/reconciliation gate recorded after correction.

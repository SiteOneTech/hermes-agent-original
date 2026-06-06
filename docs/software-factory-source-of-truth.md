# Software Factory source of truth

Agent Core Postgres (`zeus_agent.factory`) is the canonical operational source of truth for the SitioUno/Zeus Software Factory.

## Canonical layers

| Layer | Role | Canonical source |
|---|---|---|
| Factory DB | Projects, lanes, tasks, gates, events, artifacts, audit state | Agent Core Postgres schema `factory` |
| Dashboard `:9119` | Human status surface and quick AI-ready status prompts | Reads Agent Core Postgres via `/api/factory/status` |
| CLI/tools | Creation/status/gate operations | Use `hermes_cli.factory_backend`, which prefers Agent Core Postgres |
| Kanban | Separate simple-orchestration board for non-Factory tasks | Not part of Factory orchestration by default; use only if Jean explicitly requests a temporary Kanban bridge |
| Notion | Human PM/reporting surface | Canonical project/sprint template linked from Factory metadata; not orchestration truth for agents |
| SQLite | Legacy/offline/test fallback | Only via `--db`, `HERMES_FACTORY_BACKEND=sqlite`, or pytest fallback |

## Backend policy

- Normal runtime must use Agent Core Postgres.
- Silent fallback from Postgres to SQLite is forbidden outside tests.
- If Postgres is unavailable, Factory tools should fail loudly unless the operator explicitly selects SQLite fallback.
- The migration bridge is `scripts/migrate_factory_sqlite_to_agent_core.py`; it is idempotent and never mutates the SQLite source file.
- Factory projects and lanes must default to `execution_surface=factory`, not Kanban boards/cards.
- Company/product names such as Qrovia, IzyPagos, Flexipos, IXU, Bael, or SitioUno are **not** automatic Factory triggers. Route to Factory only when the user asks for a Factory project/increment/methodology/sprint/gates or an explicit software-delivery workflow.
- New Factory projects default to the **Hybrid** methodology unless Jean explicitly requests Zeus Native, BMAD, or another available lane pattern.

## Critical project delivery gate

For projects with `risk_level` `critical` or `high`, a passed `delivery` or `critical_readiness` gate is blocked unless:

1. A PM tracker exists (`factory/TRACKER.md` or Notion tracker metadata).
2. Minimum `factory/` docs exist: PRD, methodology plan, blueprint, sprint plan, task graph (`TASK_GRAPH.md`), tracker, documentation index, QA/security gates and reports, delivery report.
3. No Factory task has the same owner and reviewer.
4. The project is visible in the canonical Factory dashboard (presence in Agent Core Postgres, unless explicitly hidden via metadata).

This prevents a critical project from being marked done by a self-approval path or by repo-only artifacts that are invisible to the dashboard.

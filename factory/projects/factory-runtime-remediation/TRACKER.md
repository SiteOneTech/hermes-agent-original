# Tracker — Factory Runtime Remediation

## Executive status

| Field | Value |
|---|---|
| Project ID | `factory-runtime-remediation` |
| Methodology | Hybrid |
| Source of truth | Agent Core Postgres `factory.*` |
| Repo artifacts | `factory/projects/factory-runtime-remediation/` |
| Notion | Required; created/linked during correction |
| Current state | Methodology correction after first closure attempt |

## Task tracker

| Task | Status | Owner | Reviewer | Evidence |
|---|---|---|---|---|
| F0 Intake/methodology | done | Zeus/factory-reporter | factory-orchestrator | Factory DB project/lane/task graph + docs |
| F1 Blocker classification | done | Zeus/claude-builder | quality-reviewer | `factory_pg.py`, detector script, tests |
| F2 Watchdog alerts | done | Zeus/claude-builder | devops-release | `factory_watchdog_alerts.py`, cron job |
| F3 Blocked dispatch repair | done | Zeus/claude-builder | security-reviewer | claim predicates, force_tick behavior |
| F4 QA/live smoke | done | Zeus/qa-verifier | factory-orchestrator | 23/23 tests + script smoke |
| F5 Notion/docs correction | active/done in this correction | Zeus/factory-reporter | factory-orchestrator | full docs + Notion metadata |

## Open methodology debt

- Previous waiver decision was wrong.
- Required docs must exist.
- Notion project page must exist and be linked.
- Metadata must remove `notion_waived` and `required_docs_waived`.

## Close criteria

- `hermes factory status factory-runtime-remediation --json` has no `reconciliation_anomalies`.
- Notion metadata present.
- Required docs inventory complete.
- Delivery/reconciliation gate recorded after correction.

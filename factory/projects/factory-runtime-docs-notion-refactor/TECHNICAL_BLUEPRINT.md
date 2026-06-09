# Technical Blueprint

Project: `factory-runtime-docs-notion-refactor`
Created: 2026-06-09T23:05:00Z

## Areas to inspect/change

- `hermes_cli/factory.py`: CLI command surface.
- `hermes_cli/factory_pg.py`: Agent Core Postgres Factory backend, project metadata, reconciliation, close/resolve, dispatch helpers.
- `hermes_cli/factory_contracts.py`: status enums, repository/doc contracts.
- `scripts/factory/*` and `~/.hermes/scripts/factory_*`: supervisor/watchdog/tick behavior.
- Dashboard/API serializers if static/operative state is misleading.
- Tests under `tests/hermes_cli/`, `tests/factory/`, or the current closest Factory test directories.

## Expected design direction

1. Add typed project metadata operations, preferably `project link-notion` or `project update-metadata` with schema validation and audit event.
2. Reconciler treats Notion as satisfied only after metadata readback.
3. Dispatcher denies implementation tasks when docs/Notion gates are missing for non-trivial projects, except a narrowly defined runtime-bootstrap repair task whose purpose is to implement the missing control-plane operation.
4. Close/resolve finalizes active run rows and records monitor evidence.
5. Worker outcome parsing reads final structured outcome, not all log text.

## Data contracts

Canonical metadata fields: `notion_tracker_page_id`, `notion_tracker_url`, `reconciliation_required`, `reconciliation_anomalies`, `repo_strategy`, `artifact_dir`, `autonomous_enabled`.

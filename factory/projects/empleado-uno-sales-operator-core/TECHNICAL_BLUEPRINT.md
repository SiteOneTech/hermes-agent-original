# TECHNICAL_BLUEPRINT — Sales Operator Core

Target components:
- `db/modules/sales_operator/000001_sales_operator_schema.sql`
- `tools/sales_operator_tool.py`
- `toolsets.py` leaf toolset `sales_operator`
- scripts/cron for dry-run discovery/follow-up/daily rollup
- docs/playbooks for Empleado.uno verticals

Source of truth: Agent Core Postgres + CRM Core. External channels are adapters with provider evidence.

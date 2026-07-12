# I8 Runtime Propagation Report — Sales Operator Core

Date: 2026-07-12
Owner: Zeus
Status: GREEN

## Scope

Propagated the Sales Operator Core inherited runtime surface into `SiteOneTech/sitiouno-agent-runtime` on branch:

`factory/empleado-uno-sales-operator-core/inc-090-runtime-propagation-sales-operator-core`

The propagation is practical/runtime-only: schema, tools, commercial toolset registration, dry-run/smoke scripts, private dashboard surface, and tests. Zeus-only Factory/admin capabilities were not propagated.

## Runtime files added/updated

- `db/modules/sales_operator/*`
- `db/agent-core/000003_sales_operator_runtime_role.sql`
- `tools/sales_operator_tool.py`
- `toolsets.py`
- `hermes_cli/agent_core_sql.py`
- `scripts/agent_core_db.py`
- `scripts/agent_core_roles.py`
- `scripts/zeus-sync-secrets.sh`
- `scripts/runtime/sales_operator_daily_dry_run.py`
- `scripts/runtime/sales_operator_i7_pilot_smoke.py`
- `scripts/runtime/export_sales_operator_dashboard.py`
- `scripts/runtime/publish_delivery_sandbox.py`
- `scripts/cron/sales_operator_daily_dry_run.sh`
- `tests/test_sales_operator_*`
- `docs/sales-operator-core/RUNTIME-PROPAGATION-I8.md`
- runtime evidence under `docs/sales-operator-core/evidence/`

## Boundary preserved

Commercial runtime gets `sales_operator` inside `commercial_operator`, but does not receive:

- terminal/code/file mutation tools;
- cron/delegation/skill mutation tools;
- Zeus fleet/agent-management admin;
- raw CRM/Twenty adapters;
- real outbound provider execution.

## Evidence summary

Runtime smoke evidence:

```json
{
  "ok": true,
  "external_sends": false,
  "external_actions_invoked": [],
  "leads_created": 10,
  "research": 10,
  "scores": 10,
  "attack_plans": 10,
  "draft_outreach": 10,
  "crm_followups": 1,
  "dry_run_external_messages": 0,
  "tool_outputs": 61
}
```

DB readback:

```json
{
  "prospects": 10,
  "research": 10,
  "scores": 10,
  "attack_plans": 10,
  "outreach_queue": 10,
  "outreach_attempts": 0
}
```

## Runtime evidence files

- `docs/sales-operator-core/evidence/sales-operator-i8-runtime-smoke.json`
- `docs/sales-operator-core/evidence/sales-operator-i8-daily-dry-run.json`
- `docs/sales-operator-core/evidence/i7-pilot-fixture-leads.json`
- `docs/sales-operator-core/evidence/dashboard-user-data/sales_operator_dashboard.json`

## Result

I8 is ready to close once the runtime branch is committed and pushed. Production outbound remains future-gated.

# I8 QA Report — Runtime Propagation

Date: 2026-07-12
Owner: Zeus
Status: PASS

## Commands run

### Syntax/compile

```bash
python3 -m py_compile \
  scripts/agent_core_roles.py hermes_cli/agent_core_sql.py scripts/agent_core_db.py \
  tools/sales_operator_tool.py \
  scripts/runtime/sales_operator_i7_pilot_smoke.py \
  scripts/runtime/sales_operator_daily_dry_run.py \
  scripts/runtime/export_sales_operator_dashboard.py \
  scripts/runtime/publish_delivery_sandbox.py toolsets.py \
  tests/test_sales_operator_runtime_surface.py

bash -n scripts/cron/sales_operator_daily_dry_run.sh scripts/zeus-sync-secrets.sh
```

Result: PASS.

### Targeted pytest

```bash
pytest -q -o addopts= \
  tests/test_sales_operator_i7_pilot_smoke.py \
  tests/test_sales_operator_daily_dry_run.py \
  tests/test_sales_operator_dashboard_surface.py \
  tests/test_sales_operator_runtime_surface.py \
  tests/test_toolsets.py \
  tests/test_vapi_sms_connector.py
```

Result:

```text
46 passed in 1.72s
```

Note: `-o addopts=` was required because the local runtime checkout has pytest addopts for a timeout plugin not installed in this environment. This does not bypass test assertions; it only disables unavailable global plugin flags.

### Migrations/roles

```bash
python3 scripts/agent_core_db.py migrate
python3 scripts/agent_core_roles.py
```

Results:

```text
agent_core:000001 already applied
agent_core:000002 already applied
agent_core:000003 already applied
...
sales_operator:000001 already applied
sales_operator:000002 already applied
...
Agent Core runtime roles ready: agent_runtime, factory_runtime, calendar_runtime, crm_runtime, signature_runtime, voice_runtime, sales_runtime, sales_operator_runtime, accounting_runtime, fitness_runtime
```

### Runtime smoke

```bash
python3 scripts/runtime/sales_operator_i7_pilot_smoke.py \
  --target docs/sales-operator-core/evidence/sales-operator-i8-runtime-smoke.json \
  --format json
```

Validated summary:

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

### DB readback

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

### Dashboard export

```bash
python3 scripts/runtime/export_sales_operator_dashboard.py \
  --campaign-id empleado-uno-1000-subscribers-q3-2026 \
  --target docs/sales-operator-core/evidence/dashboard-user-data
```

Result: `ok=true`, summary contains `prospects=10`, `open_outreach=10`, `attack_plans=10`.

## QA conclusion

PASS. The runtime repo can migrate/rotate roles, expose Sales Operator to commercial operator toolsets, run dry-run/no-send loops, execute the synthetic smoke, and export the private dashboard snapshot without external sends.

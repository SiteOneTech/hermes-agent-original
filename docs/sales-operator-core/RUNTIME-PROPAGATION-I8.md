# I8 — Runtime Propagation to `sitiouno-agent-runtime`

Date: 2026-07-12
Owner: Zeus
Status: passed

## Scope propagated

I8 propagates the inherited/practical Sales Operator Core surface from Zeus into `SiteOneTech/sitiouno-agent-runtime` without bringing Zeus-only Factory/admin capabilities.

Included runtime surface:

- `db/modules/sales_operator/*` schema and CRM read grants.
- `tools/sales_operator_tool.py` provider-neutral Sales Operator tools.
- `toolsets.py` `sales_operator` toolset and inclusion in `commercial_operator`.
- `scripts/runtime/sales_operator_daily_dry_run.py` and disabled-by-default cron wrapper.
- `scripts/runtime/sales_operator_i7_pilot_smoke.py` as reusable synthetic/no-send smoke.
- `scripts/runtime/export_sales_operator_dashboard.py` and `/user/sales-operator/` private dashboard surface.
- tests covering no-send smoke, dry-run loops, dashboard page, runtime commercial toolset boundary, and existing Vapi SMS connector regression.

Explicitly excluded:

- Zeus-only `agent_management` / fleet admin functionality.
- raw CRM adapters in commercial toolset.
- terminal/code/file/cron/delegation/skill mutation tools for commercial users.
- real outbound provider execution.

## Runtime wiring

- `sales_operator` migrations are added to `scripts/agent_core_db.py migrate`.
- `sales_operator_runtime` role shell is created by migration; password/login rotation is optional and uses `SALES_OPERATOR_DB_RUNTIME_PASSWORD` only when present.
- `sales_operator_tool._user()` falls back to `sales_runtime` unless a dedicated Sales Operator DB credential is present.
- `SIGNATURE_DB_RUNTIME_PASSWORD` is treated as optional in `scripts/agent_core_roles.py`, matching Zeus canonical behavior: the signature migration creates the role shell and no local/ad-hoc secret is generated.

## Verification

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

Result: pass.

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

```bash
python3 scripts/agent_core_db.py migrate
python3 scripts/agent_core_roles.py
```

Result:

```text
Agent Core runtime roles ready: agent_runtime, factory_runtime, calendar_runtime, crm_runtime, signature_runtime, voice_runtime, sales_runtime, sales_operator_runtime, accounting_runtime, fitness_runtime
```

## Runtime smoke evidence

`python3 scripts/runtime/sales_operator_i7_pilot_smoke.py --target docs/sales-operator-core/evidence/sales-operator-i8-runtime-smoke.json --format json`

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

Commercial toolset guard:

```json
{
  "required_present": [
    "sales_operator_dashboard_snapshot",
    "sales_operator_outreach_enqueue",
    "sales_operator_status"
  ],
  "forbidden_absent": true,
  "commercial_tool_count": 106
}
```

## Evidence artifacts

- `docs/sales-operator-core/evidence/sales-operator-i8-runtime-smoke.json`
- `docs/sales-operator-core/evidence/sales-operator-i8-daily-dry-run.json`
- `docs/sales-operator-core/evidence/i7-pilot-fixture-leads.json`
- `docs/sales-operator-core/evidence/dashboard-user-data/sales_operator_dashboard.json`

## Safety result

I8 does not activate production outreach. It remains fail-closed:

- `external_sends=false`
- `external_actions_invoked=[]`
- `outreach_attempts=0`
- generated queue rows are `draft` / supervised only
- all smoke leads are synthetic `.test` fixtures
- commercial operator does not receive privileged shell/code/file/factory-admin/raw-adapter tools

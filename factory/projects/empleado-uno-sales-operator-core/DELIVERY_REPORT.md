# DELIVERY_REPORT — Sales Operator Core Green State

Date: 2026-07-12
Owner: Zeus
Status: GREEN through I8 runtime propagation

## Final state

The Sales Operator Core v1 chain is delivered through `I8 Runtime propagation to SitioUno agent runtime`.

Validated increments:

- planning/intake/ADR/PRD/task graph/tracker/QA-security docs;
- Agent Core Sales Operator schema/tools/seed/dashboard;
- I6 disabled-by-default dry-run cron loops;
- I7 synthetic first pilot smoke for Empleado.uno;
- I8 propagation into `SiteOneTech/sitiouno-agent-runtime`.

## I8 runtime propagation result

Runtime branch:

```text
factory/empleado-uno-sales-operator-core/inc-090-runtime-propagation-sales-operator-core
```

Runtime worktree:

```text
/home/jean/Projects/.worktrees/sitiouno-agent-runtime/inc-090-runtime-propagation-sales-operator-core
```

I8 propagated:

- `sales_operator` Agent Core schema and grants;
- Sales Operator toolset and commercial operator registration;
- daily dry-run wrapper/scripts;
- synthetic pilot smoke script;
- `/user/sales-operator/` private dashboard surface;
- dashboard snapshot export;
- runtime tests and evidence artifacts.

Zeus-only admin/fleet functionality and privileged tools were not propagated.

Final runtime `main` after post-push backup/fix:

```text
e340561755f7b3d61aa1d224ab7aea3425a8b9c0
```

This includes:

- base Sales Operator propagation (`3d11a96ff`);
- Vapi SMS transport type backup (`a0a1cfaec`);
- tracked dashboard exporter fix (`e34056175`) after CI exposed that `.gitignore` ignored `export*` files.

## I8 verification evidence

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

Runtime smoke validation:

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

## Runtime evidence artifacts

In `SiteOneTech/sitiouno-agent-runtime` branch:

- `docs/sales-operator-core/RUNTIME-PROPAGATION-I8.md`
- `docs/sales-operator-core/evidence/sales-operator-i8-runtime-smoke.json`
- `docs/sales-operator-core/evidence/sales-operator-i8-daily-dry-run.json`
- `docs/sales-operator-core/evidence/i7-pilot-fixture-leads.json`
- `docs/sales-operator-core/evidence/dashboard-user-data/sales_operator_dashboard.json`

Factory/origin reports:

- `factory/projects/empleado-uno-sales-operator-core/I8_RUNTIME_PROPAGATION_REPORT.md`
- `factory/projects/empleado-uno-sales-operator-core/I8_QA_REPORT.md`
- `factory/projects/empleado-uno-sales-operator-core/I8_SECURITY_REVIEW.md`

## Security/operational boundary

I8 is not production outbound activation. Remaining holds:

- real outbound email/WhatsApp/SMS/voice/social actions;
- real public-business pilot contact;
- channel-specific rate limits/quiet hours/opt-out automation;
- interpreting provider ACK as customer interest.

The next safe step, if requested, is a separately gated real public-business pilot that keeps all outreach draft-only until explicit approval.

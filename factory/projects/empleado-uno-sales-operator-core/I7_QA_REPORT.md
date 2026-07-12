# I7_QA_REPORT — First pilot smoke for Empleado.uno

Date: 2026-07-12
Project: `empleado-uno-sales-operator-core`
Task: `empleado-uno-sales-operator-core-i7-first-pilot-smoke-for-empleado-uno`
Status: PASS

## Commands executed

```bash
python3 -m py_compile \
  scripts/runtime/sales_operator_i7_pilot_smoke.py \
  scripts/runtime/sales_operator_daily_dry_run.py \
  && bash -n scripts/cron/sales_operator_daily_dry_run.sh
```

Result: PASS, no output.

```bash
pytest -q \
  tests/test_sales_operator_i7_pilot_smoke.py \
  tests/test_sales_operator_daily_dry_run.py \
  tests/test_sales_operator_dashboard_surface.py \
  tests/tools/test_crm_tool.py
```

Result:

```text
15 passed in 0.80s
```

```bash
python3 scripts/agent_core_db.py migrate
python3 scripts/agent_core_roles.py
```

Result:

```text
sales_operator:000001 already applied
sales_operator:000002 already applied
Agent Core runtime roles ready: agent_runtime, factory_runtime, calendar_runtime, crm_runtime, voice_runtime, sales_runtime, sales_operator_runtime, accounting_runtime, fitness_runtime, signature_runtime, agent_management_runtime
```

```bash
python3 scripts/runtime/sales_operator_i7_pilot_smoke.py \
  --format markdown \
  --target factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-i7-pilot-smoke.json
```

Result summary:

```text
Prospects upserted: 10
Research snapshots: 10
Lead scores: 10
Attack plans: 10
Draft outreach queued: 10
CRM follow-up readback: 1 follow-up(s)
External sends: disabled
Providers called: none
```

DB readback:

```json
{
  "i7_prospects": 10,
  "i7_research": 10,
  "i7_scores": 10,
  "i7_attack_plans": 10,
  "i7_outreach": 10,
  "i7_attempts": 0,
  "i7_open_followups": 1
}
```

Evidence artifact validation:

```json
{
  "ok": true,
  "external_sends": false,
  "leads_created": 10,
  "scored_leads": 10,
  "attack_plans": 10,
  "crm_readback_present": true,
  "tool_outputs": 61,
  "fixture_leads_target_exists": true
}
```

## Acceptance mapping

| Criterion | Result |
|---|---|
| Campaign + territory + 10 leads + scoring + attack plans + CRM readback verified. | PASS — live Agent Core DB contains 10 I7 prospects, 10 research snapshots, 10 scores, 10 attack plans, 10 draft outreach rows, and 1 CRM follow-up readback. |
| No real outbound sends occur. | PASS — `i7_attempts=0`, `external_sends=false`, and no provider actions were invoked. |

## Evidence artifacts

- `factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-i7-pilot-smoke.json`
- `factory/projects/empleado-uno-sales-operator-core/evidence/i7-pilot-fixture-leads.json`

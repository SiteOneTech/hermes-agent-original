# QA_REPORT — Sales Operator Core

Date: 2026-07-12
Owner: Zeus
Status: PASS for implemented increment

## Commands executed

```bash
python3 -m py_compile tools/sales_operator_tool.py scripts/runtime/publish_delivery_sandbox.py scripts/runtime/export_sales_operator_dashboard.py scripts/agent_core_roles.py hermes_cli/agent_core_sql.py scripts/agent_core_db.py
```

Result: PASS, no output.

```bash
pytest -q tests/test_sales_operator_dashboard_surface.py tests/test_publish_delivery_sandbox_document_actions.py
```

Result:

```text
17 passed in 1.19s
```

```bash
python3 scripts/agent_core_db.py migrate
```

Result: PASS. Relevant applied migrations:

```text
agent_core:000003 applied
sales_operator:000001 applied
sales_operator:000002 applied
```

```bash
python3 scripts/runtime/export_sales_operator_dashboard.py --target /home/jean/zeus-runtime/delivery-sandbox/user-data --campaign-id empleado-uno-1000-subscribers-q3-2026 --prospect-limit 50 --report-limit 30
```

Result: PASS. Snapshot written to `/home/jean/zeus-runtime/delivery-sandbox/user-data/sales_operator_dashboard.json`.

```bash
PLAYWRIGHT_JSON_OUTPUT_NAME=factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-dashboard/playwright-report.json npx playwright test scripts/qa/sales_operator_dashboard.spec.mjs --reporter=json,line --output=factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-dashboard/test-results
```

Result:

```text
1 passed (11.4s)
```

## Browser QA scope

The Playwright spec validates:

- unauthenticated `/user/sales-operator/` redirects to `/user/login`
- authenticated temporary QA session renders dashboard
- required dashboard text is visible:
  - `Empleado.uno activo`
  - `Jornadas de trabajo`
  - `CRM rápido`
  - `Política comercial`
  - `Medell`
- desktop screenshot captured
- mobile screenshot captured
- no first-party network failures
- no browser console errors

## Evidence

- JSON report: `factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-dashboard/playwright-report.json`
- Desktop screenshot: `factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-dashboard/desktop.png`
- Mobile screenshot: `factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-dashboard/mobile.png`

## Live smoke

```json
{"channels": 7, "reports": 1, "snapshot_file": "/home/jean/zeus-runtime/delivery-sandbox/user-data/sales_operator_dashboard.json", "snapshot_ok": true, "status_ok": true, "territories": 5}
```

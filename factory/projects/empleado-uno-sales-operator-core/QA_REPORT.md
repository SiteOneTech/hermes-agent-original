# QA_REPORT — Sales Operator Core

Date: 2026-07-12
Owner: Zeus
Status: PASS / GREEN for implemented increment

## Commands executed

```bash
python3 -m py_compile hermes_cli/agent_core_sql.py scripts/agent_core_roles.py scripts/agent_core_db.py tools/sales_operator_tool.py scripts/runtime/publish_delivery_sandbox.py scripts/runtime/export_sales_operator_dashboard.py && bash -n scripts/zeus-sync-secrets.sh
```

Result: PASS, no output.

```bash
pytest -q tests/scripts/test_agent_core_roles.py tests/scripts/test_signature_runtime_wiring.py tests/test_sales_operator_dashboard_surface.py tests/test_publish_delivery_sandbox_document_actions.py
```

Result:

```text
23 passed in 1.33s
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
systemctl --user restart zeus-secrets-sync.service
python3 scripts/agent_core_roles.py
```

Result:

```text
Agent Core runtime roles ready: agent_runtime, factory_runtime, calendar_runtime, crm_runtime, voice_runtime, sales_runtime, sales_operator_runtime, accounting_runtime, fitness_runtime, signature_runtime, agent_management_runtime
```

Secret verification was presence-only: `AGENT_MANAGEMENT_DB_RUNTIME_USER`, `AGENT_MANAGEMENT_DB_RUNTIME_PASSWORD`, `AGENT_MANAGEMENT_DATABASE_URL`, and `AGENT_MANAGEMENT_DATABASE_URL_DOCKER` are present in `~/.hermes/runtime-secrets.env`; values were not printed.

```bash
python3 scripts/runtime/export_sales_operator_dashboard.py --target /home/jean/zeus-runtime/delivery-sandbox/user-data --campaign-id empleado-uno-1000-subscribers-q3-2026 --prospect-limit 50 --report-limit 30
```

Result: PASS. Snapshot written to `/home/jean/zeus-runtime/delivery-sandbox/user-data/sales_operator_dashboard.json`.

```bash
PLAYWRIGHT_JSON_OUTPUT_NAME=factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-dashboard/playwright-report.json npx playwright test scripts/qa/sales_operator_dashboard.spec.mjs --reporter=json,line --output=factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-dashboard/test-results
```

Result:

```text
1 passed (11.6s)
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

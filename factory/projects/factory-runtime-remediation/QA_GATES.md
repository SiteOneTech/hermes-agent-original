# QA Gates — Factory Runtime Remediation

## Gate matrix

| Gate | Evidence required | Status |
|---|---|---|
| Intake | Scope, project ID, Factory DB source confirmed | passed |
| Planning | PRD, ADRs, sprint plan, task graph, Notion page | correction in progress/passed after this run |
| Implementation | Code/scripts for blocker classifier, alerts, dispatcher | passed |
| Quality | Focused Factory tests + behavior review | passed |
| Test | `run_tests.sh` focused suite | passed |
| Delivery | Smoke against Agent Core Postgres + cron created | passed after correction |
| Reconciliation | No missing docs/Notion anomalies | must be verified after Notion metadata update |

## Required commands

```bash
python3 -m py_compile hermes_cli/factory_pg.py \
  ~/.hermes/scripts/factory_blocker_detector.py \
  ~/.hermes/scripts/factory_status_sync.py \
  ~/.hermes/scripts/factory_orchestrator_tick.py \
  ~/.hermes/scripts/factory_watchdog_alerts.py

./scripts/run_tests.sh \
  tests/hermes_cli/test_factory_canonical_runtime.py \
  tests/hermes_cli/test_factory.py \
  tests/tools/test_factory_tools.py

python3 ~/.hermes/scripts/factory_blocker_detector.py
python3 ~/.hermes/scripts/factory_status_sync.py
python3 ~/.hermes/scripts/factory_watchdog_alerts.py
hermes factory status factory-runtime-remediation --json
```

## Hard-stop conditions

- Missing Notion project metadata.
- Missing required docs.
- `reconciliation_required=true` after correction.
- Any focused Factory test failing.
- Watchdog script noisy when no alerts exist.

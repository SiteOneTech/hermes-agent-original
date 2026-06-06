# QA Report — Factory Runtime Remediation

## Test evidence

Focused Factory suite executed:

```bash
./scripts/run_tests.sh tests/hermes_cli/test_factory_canonical_runtime.py tests/hermes_cli/test_factory.py tests/tools/test_factory_tools.py
```

Observed result during implementation:

```text
23 tests passed, 0 failed
```

## Compile evidence

```bash
python3 -m py_compile hermes_cli/factory_pg.py ~/.hermes/scripts/factory_blocker_detector.py ~/.hermes/scripts/factory_status_sync.py ~/.hermes/scripts/factory_orchestrator_tick.py ~/.hermes/scripts/factory_watchdog_alerts.py
```

Observed result: success.

## Live smoke evidence

### Blocker detector

```bash
python3 ~/.hermes/scripts/factory_blocker_detector.py
```

Observed:

```text
db_backend=agent_core_postgres
classified=0
alerts=0
needs_attention=false
```

### Status sync

```bash
python3 ~/.hermes/scripts/factory_status_sync.py
```

Observed: emitted Agent Core Postgres status with alert counts.

### Watchdog

```bash
python3 ~/.hermes/scripts/factory_watchdog_alerts.py | wc -c
```

Observed: `0` when no alerts exist — correct silent behavior.

### Controlled orchestrator tick

```bash
FACTORY_TICK_PROJECT_ID=factory-runtime-remediation python3 ~/.hermes/scripts/factory_orchestrator_tick.py
```

Observed:

```text
db_backend=agent_core_postgres
claimed=null
alerts=[]
needs_attention=false
```

## QA verdict

GREEN for runtime behavior. Methodology correction required Notion/docs, now addressed in this correction run.

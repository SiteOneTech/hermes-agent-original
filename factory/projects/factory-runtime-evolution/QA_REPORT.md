# QA Report — Factory Runtime Evolution

## Test evidence

### Prior runtime autonomy repair

Focused Factory suite used during the first remediation phase:

```bash
./scripts/run_tests.sh tests/hermes_cli/test_factory_canonical_runtime.py tests/hermes_cli/test_factory.py tests/tools/test_factory_tools.py
```

Observed result during that phase:

```text
23 tests passed, 0 failed
```

### Repo-first Runtime Contract v1

RED was verified first: the new tests failed because `docs_not_indexed`, `uncommitted_project_artifacts`, and critical readiness commit/index blockers did not exist yet.

RED command:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python -m pytest tests/hermes_cli/test_factory_canonical_runtime.py -q
```

Observed RED excerpt:

```text
FAILED test_factory_reconciliation_detects_docs_missing_from_documentation_index
FAILED test_factory_reconciliation_detects_uncommitted_project_artifacts
FAILED test_factory_critical_readiness_requires_index_and_commit_checkpoint
3 failed, 17 passed
```

GREEN commands:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python -m pytest tests/hermes_cli/test_factory_canonical_runtime.py -q
/home/jean/Projects/hermes-agent-original/venv/bin/python -m pytest tests/hermes_cli/test_factory_canonical_runtime.py tests/tools/test_factory_tools.py -q
```

Observed GREEN:

```text
20 passed in 1.66s
22 passed, 1 warning in 7.80s
```

## Compile evidence

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python -m py_compile hermes_cli/factory_pg.py
```

Observed result: success.

### INC-0006 — Unified resolve-state action

Scope verified in dedicated worktree:

```text
/home/jean/Projects/hermes-agent-original/.worktrees/factory-runtime-evolution/inc-0006-resolve-state-action
```

Focused GREEN command:

```bash
python -m pytest tests/hermes_cli/test_factory_canonical_runtime.py -q
```

Observed GREEN at 2026-06-07T20:20:02-04:00:

```text
50 passed in 2.52s
```

Compile command:

```bash
python -m py_compile hermes_cli/factory.py hermes_cli/factory_pg.py hermes_cli/web_server.py
```

Observed result: success.

Local parser smoke:

```bash
python - <<'PY'
from hermes_cli import factory
import argparse
p=argparse.ArgumentParser(prog='local')
subs=p.add_subparsers(dest='command')
factory.add_parser(subs)
try:
    p.parse_args(['factory','project','resolve-state','--help'])
except SystemExit as e:
    print(f'local parser resolve-state help exit={e.code}')
PY
```

Observed result: `local parser resolve-state help exit=0`.

Frontend build check:

```bash
npm ci
npm run build
```

Observed result in `web/` at final verification: GREEN. Vite emitted the existing large chunk warning only.

```text
✓ 2235 modules transformed.
✓ built in 11.70s
```

Expanded focused suite:

```bash
python3 -m pytest -o addopts='' tests/hermes_cli/test_factory_canonical_runtime.py tests/hermes_cli/test_factory.py tests/tools/test_factory_tools.py tests/tools/test_crm_tool.py tests/tools/test_sales_tool.py tests/tools/test_accounting_tool.py -q
```

Observed result:

```text
86 passed, 1 warning in 5.63s
```

Coverage added/updated:

- Dashboard exposes one `Resolver estado` control using canonical `resolve-state` action; legacy Reconciliar/Resolver bloqueos controls are absent.
- CLI/API aliases `resolve`, `reconcile`, and `unblock` converge to canonical `resolve-state`.
- `resume` runs resolve-state preflight and skips dispatch when a true `delivery_hold` terminal condition remains.
- `pause` is documented in runtime metadata as user/operator intent, distinct from condition holds.

## Live smoke evidence

### Blocker detector

```bash
python3 ~/.hermes/scripts/factory_blocker_detector.py
```

Observed before this increment:

```text
db_backend=agent_core_postgres
classified=0
alerts=0
needs_attention=false
```

### Controlled orchestrator tick

```bash
FACTORY_TICK_PROJECT_ID=factory-runtime-evolution python3 ~/.hermes/scripts/factory_orchestrator_tick.py
```

Observed before this increment:

```text
db_backend=agent_core_postgres
claimed=null
alerts=[]
needs_attention=false
```

## QA verdict

GREEN for the code-level repo-first Runtime Contract v1 in the dedicated worktree. Final project delivery still requires a clean git checkpoint and any separate Notion/human PM projection reconciliation Jean wants to enforce.

INC-0006 is GREEN at focused test level after unifying resolve-state controls and preflight semantics. Final increment delivery requires the local commit checkpoint and Factory gate record.

INC-0007 is GREEN at focused Factory runtime level after adding the single-writer/manual takeover lease guard. The new guard blocks resume/dispatch while a manual takeover lease is active, exposes canonical CLI/API acquire/release paths, and prevents cron from claiming projects whose worktree is held by an operator session.

Final INC-0007 verification evidence:

```text
python3 -m pytest -o addopts='' tests/hermes_cli/test_factory_canonical_runtime.py tests/hermes_cli/test_factory.py tests/tools/test_factory_tools.py tests/tools/test_crm_tool.py tests/tools/test_sales_tool.py tests/tools/test_accounting_tool.py -q
→ 90 passed, 1 warning in 5.83s

python3 -m py_compile hermes_cli/factory_pg.py hermes_cli/factory.py hermes_cli/web_server.py tests/hermes_cli/test_factory_canonical_runtime.py
→ success

cd web && npm ci && npm run build
→ built successfully in 12.11s; existing Vite large chunk warning only
```

### INC-0008 — Cron/control-plane restoration

Focused unit/regression suite in worktree `inc-0008-cron-control-plane`:

```bash
python3 -m pytest tests/hermes_cli/test_factory.py tests/hermes_cli/test_factory_cron_control_plane.py tests/tools/test_factory_tools.py -q -o 'addopts='
```

Observed GREEN:

```text
11 passed, 1 warning in 2.64s
```

Runtime Sales/Voice/CRM supervisor regression suite, to verify the non-Factory crons remain aligned to `sitiouno-agent-runtime`:

```bash
python3 -m pytest tests/test_vapi_postcall_worker.py tests/test_customer_intent_supervisor.py tests/test_customer_intent_tool.py -q -o 'addopts='
```

Observed GREEN:

```text
13 passed in 0.93s
```

Real Agent Core Postgres script smokes from the repo-backed Factory scripts:

```text
python3 scripts/factory/factory_status_sync.py
→ job=factory_status_sync db_backend=agent_core_postgres summary={'projects': 9, 'tasks': 109, 'gates': 258, 'active_runs': 0, 'alerts': 0}

python3 scripts/factory/factory_reviewer_dispatch.py
→ job=factory_reviewer_dispatch db_backend=agent_core_postgres summary={'tasks_ready_for_review': 1, 'pending_reviewer_assignment': 0, 'ready_with_reviewer': 1}

python3 scripts/factory/factory_blocker_detector.py
→ job=factory_blocker_detector db_backend=agent_core_postgres summary={'classified': 0, 'questions_created': 0, 'alerts': 0} needs_attention=False

FACTORY_WATCHDOG_STATE_PATH=/tmp/factory_watchdog_alert_state_smoke.json python3 scripts/factory/factory_watchdog_alerts.py
→ stdout length 0; no unsuppressed actionable alerts
```

INC-0008 also fixed a discovered watchdog false-positive: repeated `claimed=null` is now alertable only when runnable autonomous work exists and no run is active. Idle cron ticks are healthy and stay silent.

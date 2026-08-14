# Implementation Report — FRE-027 Factory migration readiness

| Field | Value |
|---|---|
| Increment | `FRE-027` |
| Task | Enforce Factory migration readiness before orchestration |
| Owner | `claude-builder` |
| Date | 2026-08-14 |
| Scope | Zeus-only Factory control plane; no product runtime, deploy, credential change, or live DB mutation |

## Summary

FRE-027 closes the 000004 successor-control incident class by making Factory
runtime orchestration fail closed before it can acquire the global lease, claim,
or spawn work when the required Factory successor-control migration is absent or
unusable by the least-privilege runtime role.

Implemented controls:

1. `hermes_cli/factory_pg.py` now performs a read-only Factory migration readiness
   preflight for required migration `000004`, tables `factory.runtime_leases` and
   `factory.project_successions`, and runtime role write/sequence privileges.
2. Runtime code no longer applies a DDL fallback from `ensure_runtime_schema()`.
   Recovery is canonical and explicit: `python scripts/agent_core_db.py migrate --module factory`
   followed by `python scripts/agent_core_db.py verify --module factory`.
3. `scripts/factory/factory_orchestrator_tick.py` calls the readiness preflight before
   status, force-tick, claim, or spawn. On failure it emits JSON with
   `error_type=factory_migration_readiness_failed` and the diagnostic payload.
4. `scripts/agent_core_db.py` now supports module-scoped migration and verification:
   `migrate --module factory` and `verify --module factory`.
5. `db/modules/factory/000004_successor_control.sql` grants successor-control table
   and sequence privileges to `factory_runtime` when the role exists, preserving
   least-privilege runtime access without runtime DDL fallback.

## Files changed

- `hermes_cli/factory_pg.py`
- `scripts/factory/factory_orchestrator_tick.py`
- `scripts/agent_core_db.py`
- `db/modules/factory/000004_successor_control.sql`
- `tests/hermes_cli/test_factory_successor_control.py`
- `tests/hermes_cli/test_factory_orchestrator_tick.py`
- `tests/scripts/test_agent_core_db_migrations.py`
- `factory/projects/factory-runtime-evolution-continuation/IMPLEMENTATION_REPORT_FRE_027.md`
- `factory/projects/factory-runtime-evolution-continuation/TRACKER.md`
- `factory/projects/factory-runtime-evolution-continuation/QA_GATES.md`
- `factory/projects/factory-runtime-evolution-continuation/SECURITY_GATES.md`
- `factory/projects/factory-runtime-evolution-continuation/DOCUMENTATION_INDEX.md`

## TDD evidence

### RED

1. Missing Factory 000004 readiness regression:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python \
  scripts/run_tests.sh tests/hermes_cli/test_factory_successor_control.py -k missing -q
```

Result: failed as expected. The pre-fix control plane attempted
`factory.runtime_leases` and surfaced the opaque PostgreSQL failure:
`subprocess.CalledProcessError: Command '['psql']' returned non-zero exit status 3.`

2. Orchestrator preflight regression:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python \
  scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k migration_readiness -q
```

Result: failed as expected with `Failed: DID NOT RAISE SystemExit`; the old tick
printed a normal skipped report instead of the migration-readiness diagnostic.

3. Module-scoped migration/verification regression:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python \
  scripts/run_tests.sh tests/scripts/test_agent_core_db_migrations.py -q
```

Result before implementation: `2 failed`; `migrate --module factory` was rejected
as an unrecognized argument and `scripts.agent_core_db` had no `verify_module`.

### GREEN / focused verification

1. Individual GREEN checks:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python \
  scripts/run_tests.sh tests/hermes_cli/test_factory_successor_control.py -k missing -q
```

Result: `1 tests passed, 0 failed`.

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python \
  scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k migration_readiness -q
```

Result: `1 tests passed, 0 failed`.

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python \
  scripts/run_tests.sh tests/scripts/test_agent_core_db_migrations.py
```

Result: `3 tests passed, 0 failed`.

2. Focused Factory suite:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python \
  scripts/run_tests.sh \
    tests/hermes_cli/test_factory_successor_control.py \
    tests/hermes_cli/test_factory_orchestrator_tick.py \
    tests/hermes_cli/test_factory_control_plane_refactor.py \
    tests/hermes_cli/test_factory_increment_integration.py \
    tests/hermes_cli/test_factory_cron_control_plane.py \
    tests/factory/test_factory_watchdog_alerts.py \
    tests/scripts/test_agent_core_db_migrations.py \
    tests/hermes_cli/test_agent_core_sql.py \
    tests/hermes_cli/test_factory.py
```

Result: `9 files, 173 tests passed, 0 failed` in 5.6s runner wall.

3. Runtime-role script regression:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python \
  scripts/run_tests.sh tests/scripts/test_agent_core_roles.py
```

Result: `3 tests passed, 0 failed`.

4. Syntax/hygiene:

```bash
python3 -m py_compile \
  hermes_cli/factory_pg.py \
  scripts/factory/factory_orchestrator_tick.py \
  scripts/agent_core_db.py \
  tests/hermes_cli/test_factory_successor_control.py \
  tests/hermes_cli/test_factory_orchestrator_tick.py \
  tests/scripts/test_agent_core_db_migrations.py
```

Result: exit 0, no output.

```bash
git diff --check
```

Result: exit 0, no output.

5. CLI help smoke for canonical path:

```bash
python3 scripts/agent_core_db.py migrate --help
python3 scripts/agent_core_db.py verify --help
```

Result: help lists `migrate --module ... --no-verify` and `verify --module ...`.

## Live DB boundary

No live Factory DDL or Factory row mutation was executed from this isolated
implementation. The new canonical path is implemented and unit-verified; applying
it to a live Agent Core DB remains an explicit deploy/recovery action:

```bash
python scripts/agent_core_db.py migrate --module factory
python scripts/agent_core_db.py verify --module factory
```

If runtime roles are missing or stale, run the canonical role script before the
verification step:

```bash
python scripts/agent_core_roles.py
```

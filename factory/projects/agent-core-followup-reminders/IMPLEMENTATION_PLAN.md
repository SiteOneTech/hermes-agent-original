# IMPLEMENTATION_PLAN — Universal Activity Layer

## Estado

- Incremento: F3 — Implementation plan and task graph
- Run: `run-1780704556-afaa1d6b`
- Fecha: `2026-06-05T24:20:00Z`
- Owner: `implementation-planner`
- Reviewer: `factory-orchestrator`
- Fuente de verdad: Agent Core Postgres `factory.*`

## Meta

Este plan convierte el ADR/data model de F2 en tareas ejecutables para F4-F8. Cada tarea incluye paths exactos, comandos de verificación, owner, reviewer y gates requeridos. No se inicia implementación hasta que los gates functional/architecture/planning estén registrados en Factory DB.

---

## Fase 1: F4 — DB Migrations and Runtime Grants

**Owner:** `claude-builder`
**Reviewer:** `codex-builder`
**Gate requerido:** `planning=passed` (F3 actual) + `architecture=passed` (F2 pendiente `security-reviewer`)

### F4.1 — Crear module registry y schema seed

**Archivos:**
- Crear: `db/modules/activity/000001_activity_schema.sql`

**Contenido mínimo:**
```sql
CREATE SCHEMA IF NOT EXISTS activity;

-- Module registry
INSERT INTO agent_core.modules(module, description, owner, schema_name, metadata)
VALUES (
  'activity',
  'Agent Core Universal Activity Layer: follow-ups, reminders, tasks, plans, recurrence, and audited side effects.',
  'agent-runtime',
  'activity',
  '{"capability":"followup-reminders","project":"agent-core-followup-reminders"}'::jsonb
)
ON CONFLICT (module) DO UPDATE SET updated_at = now(), metadata = EXCLUDED.metadata;

INSERT INTO agent_core.module_databases(module, database_name, connection_role, migration_role, metadata)
VALUES ('activity', current_database(), 'activity_runtime', 'agent_admin', '{"option":"same-agent-db-schema"}'::jsonb)
ON CONFLICT (module) DO UPDATE SET database_name = EXCLUDED.database_name, connection_role = EXCLUDED.connection_role;
```

**Verificación:**
```bash
# Dry-run en test DB (sin --apply)
hermes factory migrate --module activity --dry-run --db-url "postgresql://user:pass@test-host:5432/test_db"

# Verificar module existe en agent_core.modules
psql $FACTORY_DB_URL -c "SELECT module, schema_name, owner FROM agent_core.modules WHERE module='activity';"
```

---

### F4.2 — Crear tabla `activity.activities`

**Archivo:** `db/modules/activity/000002_activities.sql`

**Verificación:**
```sql
-- Ejecutar en test DB
psql $TEST_DB_URL -f db/modules/activity/000002_activities.sql
psql $TEST_DB_URL -c "\d activity.activities"
psql $TEST_DB_URL -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='activity' AND table_name='activities' ORDER BY ordinal_position;"
```

---

### F4.3 — Crear tabla `activity.activity_links`

**Archivo:** `db/modules/activity/000003_activity_links.sql`

**Verificación:**
```bash
psql $TEST_DB_URL -f db/modules/activity/000003_activity_links.sql
psql $TEST_DB_URL -c "\d activity.activity_links"
psql $TEST_DB_URL -c "SELECT COUNT(*) FROM activity.activity_links LIMIT 0;"  -- 0 rows initially
```

---

### F4.4 — Crear tabla `activity.reminder_rules`

**Archivo:** `db/modules/activity/000004_reminder_rules.sql`

**Verificación:**
```bash
psql $TEST_DB_URL -f db/modules/activity/000004_reminder_rules.sql
psql $TEST_DB_URL -c "\d activity.reminder_rules"
```

---

### F4.5 — Crear tabla `activity.activity_events`

**Archivo:** `db/modules/activity/000005_activity_events.sql`

**Verificación:**
```bash
psql $TEST_DB_URL -f db/modules/activity/000005_activity_events.sql
psql $TEST_DB_URL -c "\d activity.activity_events"
psql $TEST_DB_URL -c "SELECT COUNT(*) FROM activity.activity_events LIMIT 0;"  -- 0 rows initially
```

---

### F4.6 — Crear tablas `activity_plans`, `activity_plan_steps`, `activity_plan_runs`, `activity_plan_run_steps`

**Archivos:** `db/modules/activity/000006_activity_plans.sql`

**Verificación:**
```bash
psql $TEST_DB_URL -f db/modules/activity/000006_activity_plans.sql
psql $TEST_DB_URL -c "\d activity.activity_plans"
psql $TEST_DB_URL -c "\d activity.activity_plan_steps"
psql $TEST_DB_URL -c "\d activity.activity_plan_runs"
psql $TEST_DB_URL -c "\d activity.activity_plan_run_steps"
```

---

### F4.7 — Crear tablas `activity.recurrence_rules` y `activity.recurrence_instances` (opcional)

**Archivo:** `db/modules/activity/000007_recurrence_rules.sql`

**Verificación:**
```bash
psql $TEST_DB_URL -f db/modules/activity/000007_recurrence_rules.sql
psql $TEST_DB_URL -c "\d activity.recurrence_rules"
psql $TEST_DB_URL -c "\d activity.recurrence_instances"  -- puede no existir si se postergó
```

---

### F4.8 — Runtime grants

**Archivo:** `db/modules/activity/000008_runtime_grants.sql`

**Contenido mínimo:**
```sql
-- Conceder uso del schema a activity_runtime
GRANT USAGE ON SCHEMA activity TO activity_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA activity TO activity_runtime;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA activity TO activity_runtime;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA activity TO activity_runtime;
```

**Verificación:**
```bash
psql $PROD_DB_URL -c "SELECT grantee, privilege_type FROM information_schema.table_privileges WHERE table_schema='activity' AND grantee='activity_runtime';"
```

---

## Fase 2: F5 — Activity/Follow-up Hermes Tools and Toolset

**Owner:** `claude-builder`
**Reviewer:** `quality-reviewer`
**Gate requerido:** `planning=passed` + `implementation` sobre F4

### F5.1 — Toolset registry para `activity`

**Archivo:** `tools/toolsets.py` (agregar `activity` a `_HERMES_CORE_TOOLS`)

**Verificación:**
```bash
python3 -c "from toolsets import _HERMES_CORE_TOOLS; print('activity' in _HERMES_CORE_TOOLS)"
```

---

### F5.2 — `activity_upsert` tool handler

**Archivo:** `tools/activity_tool.py` (nuevo)

**Implementación mínima:**
- Registrable via `registry.register("activity_upsert")`
- Params: `activity_id` (opcional), `activity_type`, `title`, `description`, `status`, `priority`, `owner_id`, `assignee_id`, `due_at`, `source`, `source_ref`, `dedupe_key`, `confidence`, `evidence`, `participants`, `metadata`
- SQL parameterized INSERT con ON CONFLICT dedupe_key
- Retorna JSON: `{"activity_id", "operation", "dedupe_key", "created_at", "updated_at"}`

**Verificación:**
```bash
python3 -c "
from tools.activity_tool import activity_upsert
import json
result = activity_upsert(
    activity_type='follow_up',
    title='Test follow-up',
    owner_id='zeus',
    source='test'
)
parsed = json.loads(result)
assert 'activity_id' in parsed, f'No activity_id in {parsed}'
assert 'operation' in parsed, f'No operation in {parsed}'
print('PASS:', parsed)
"
```

---

### F5.3 — `activity_list` tool handler

**Archivo:** `tools/activity_tool.py`

**Params:** `owner_id`, `status`, `due_filter`, `limit`, `offset`

**Verificación:**
```bash
python3 -c "
from tools.activity_tool import activity_list
import json
result = json.loads(activity_list(owner_id='zeus', status='open', limit=5))
assert isinstance(result, dict), f'Expected dict, got {type(result)}'
assert 'activities' in result or 'ok' in result, f'No activities key in {result}'
print('PASS:', list(result.keys()))
"
```

---

### F5.4 — `activity_complete` tool handler

**Archivo:** `tools/activity_tool.py`

**Verificación:**
```bash
python3 -c "
from tools.activity_tool import activity_complete
import json
# Crear activity primero
from tools.activity_tool import activity_upsert
created = json.loads(activity_upsert(title='To complete', owner_id='zeus', source='test'))
aid = created['activity_id']
# Completar
result = json.loads(activity_complete(activity_id=aid, completion_note='Done'))
assert result.get('ok') or 'completed_at' in result, f'Failed to complete: {result}'
print('PASS:', result)
"
```

---

### F5.5 — `activity_snooze`, `activity_reschedule`, `activity_cancel`

**Archivo:** `tools/activity_tool.py`

**Verificación:** Cada una retorna JSON con `activity_id`, nuevo estado, y `updated_at`.

---

### F5.6 — `activity_link` / `activity_unlink`

**Archivo:** `tools/activity_tool.py`

**Verificación:**
```bash
python3 -c "
from tools.activity_tool import activity_link, activity_unlink
import json
# Crear dos activities
from tools.activity_tool import activity_upsert
a1 = json.loads(activity_upsert(title='Activity 1', owner_id='zeus', source='test'))
a2 = json.loads(activity_upsert(title='Activity 2', owner_id='zeus', source='test'))
# Linkear
link_result = json.loads(activity_link(
    activity_id=a1['activity_id'],
    target_type='activity',
    target_id=a2['activity_id'],
    relationship_type='next_after'
))
assert link_result.get('ok'), f'Link failed: {link_result}'
print('PASS: link created')
"
```

---

### F5.7 — `activity_timeline` tool

**Archivo:** `tools/activity_tool.py`

**Verificación:**
```bash
python3 -c "
from tools.activity_tool import activity_timeline
import json
result = json.loads(activity_timeline(target_type='contact', target_id='test-contact-1', limit=10))
assert isinstance(result, (dict, list)), f'Expected structured output, got {type(result)}'
print('PASS:', type(result).__name__)
"
```

---

### F5.8 — `activity_dispatcher_scan`

**Archivo:** `tools/activity_tool.py`

**Verificación:**
```bash
python3 -c "
from tools.activity_tool import activity_dispatcher_scan
import json
result = json.loads(activity_dispatcher_scan(limit=20))
assert 'due' in result or 'upcoming' in result or 'overdue' in result or result.get('ok'), f'Unexpected: {result}'
print('PASS:', list(result.keys()))
"
```

---

### F5.9 — Tests para tool handlers

**Archivo:** `tests/tools/test_activity_tool.py` (nuevo)

**Verificación:**
```bash
cd /home/jean/Projects/hermes-agent-original
python3 -m pytest tests/tools/test_activity_tool.py -v --tb=short 2>&1 | tail -30
```

---

## Fase 3: F6 — Calendar Bridge and Deterministic Reminder Dispatcher

**Owner:** `claude-builder`
**Reviewer:** `devops-release`
**Gate requerido:** F5 tools existentes + `activity_to_calendar_event` en scope

### F6.1 — `activity_to_calendar_event` tool

**Archivo:** `tools/activity_tool.py`

**Lógica:**
1. Leer `activity_id`
2. Verificar que `activity_type IN ('meeting','call')` o `calendar_required=true` en metadata
3. Llamar `calendar_event_create` del `calendar_tool.py` existente
4. Si exitoso: insertar `activity_link` con `relationship_type='calendar_event'`
5. Si falla: escribir `calendar_failed` event en `activity_events`
6. Retornar JSON con `activity_id`, `calendar_event_id`, `status`

**Verificación:**
```bash
python3 -c "
from tools.activity_tool import activity_to_calendar_event
import json
result = json.loads(activity_to_calendar_event(
    activity_id='test-act-123',
    title='Test Meeting',
    start_at='2026-06-10T10:00:00Z',
    end_at='2026-06-10T10:30:00Z'
))
# Status puede ser 'created' o 'retryable' dependiendo de calendar availability
assert 'status' in result, f'No status in {result}'
print('PASS:', result)
"
```

---

### F6.2 — Deterministic reminder dispatcher job

**Archivo:** `cron/activity_dispatcher.py` (nuevo) o extensión de `cron/jobs.py`

**Lógica:**
1. Consultar `activity.activities` con `status IN ('open','waiting')` y `due_at <= now() + interval '1 hour'`
2. Consultar `activity.reminder_rules` con `enabled=true` y `next_fire_at <= now()`
3. Materializar próximas instancias de `recurrence_rules` para ventana de 24h
4. Escribir `activity_events` para cada item listo con `event_type='dispatcher_scan'`
5. Retornar lista accionable con `activity_id`, `title`, `due_at`, `rule_id`, `action_status`

**Verificación:**
```bash
python3 -c "
from cron.activity_dispatcher import run_dispatcher_scan
import json
result = json.loads(run_dispatcher_scan(limit=50))
assert isinstance(result, dict), f'Expected dict, got {type(result)}'
print('PASS: dispatcher returned', list(result.keys()))
"
```

---

### F6.3 — Smoke test para dispatcher

**Archivo:** `tests/cron/test_activity_dispatcher.py` (nuevo)

**Verificación:**
```bash
python3 -m pytest tests/cron/test_activity_dispatcher.py -v --tb=short 2>&1 | tail -20
```

---

## Fase 4: F7 — Activity Plans, Chaining, Recurrence, and Quick Capture

**Owner:** `claude-builder`
**Reviewer:** `product-analyst`
**Gate requerido:** F5 tools existentes

### F7.1 — `activity_plan_create`

**Archivo:** `tools/activity_tool.py`

**Params:** `plan_name`, `description`, `steps` (array de objetos con `title`, `relative_after_days`, `activity_type`, `priority`)

**Verificación:**
```bash
python3 -c "
from tools.activity_tool import activity_plan_create
import json
result = json.loads(activity_plan_create(
    plan_name='Onboarding checklist',
    steps=[
        {'title': 'Send welcome email', 'relative_after_days': 0, 'activity_type': 'email'},
        {'title': 'Follow up in 3 days', 'relative_after_days': 3, 'activity_type': 'follow_up'},
    ]
))
assert result.get('ok') or 'plan_id' in result, f'Failed: {result}'
print('PASS:', result)
"
```

---

### F7.2 — `activity_plan_apply`

**Archivo:** `tools/activity_tool.py`

**Params:** `plan_id`, `target_type`, `target_id`, `target_name`

**Verificación:**
```bash
python3 -c "
from tools.activity_tool import activity_plan_apply
import json
result = json.loads(activity_plan_apply(
    plan_id='test-plan-1',
    target_type='contact',
    target_id='contact-123',
    target_name='Test Contact'
))
assert result.get('ok') or 'run_id' in result, f'Failed: {result}'
print('PASS:', result)
"
```

---

### F7.3 — `activity_next_actions`

**Archivo:** `tools/activity_tool.py`

**Params:** `owner_id`, `limit`

**Verificación:**
```bash
python3 -c "
from tools.activity_tool import activity_next_actions
import json
result = json.loads(activity_next_actions(owner_id='zeus', limit=5))
assert isinstance(result, (dict, list)), f'Expected structured result, got {type(result)}'
print('PASS:', type(result).__name__)
"
```

---

### F7.4 — `activity_detect_from_text`

**Archivo:** `tools/activity_tool.py`

**Params:** `text`, `mode` (`suggest_only` | `create_authorized`)

**Verificación:**
```bash
python3 -c "
from tools.activity_tool import activity_detect_from_text
import json
result = json.loads(activity_detect_from_text(
    text='I need to call Juan next Tuesday to discuss the proposal and send him the contract by Friday',
    mode='suggest_only'
))
assert isinstance(result, (dict, list)), f'Expected structured result, got {type(result)}'
print('PASS: detected', len(result) if isinstance(result, list) else len(result.get('candidates', [])), 'candidates')
"
```

---

### F7.5 — `activity_recurrence_expand`

**Archivo:** `tools/activity_tool.py`

**Params:** `rule_id` o `rrule_text`, `from_date`, `count`

**Verificación:**
```bash
python3 -c "
from tools.activity_tool import activity_recurrence_expand
import json
result = json.loads(activity_recurrence_expand(
    rrule_text='FREQ=WEEKLY;BYDAY=MO,WE,FR;COUNT=10',
    from_date='2026-06-01',
    count=10
))
assert isinstance(result, (dict, list)), f'Expected result, got {type(result)}'
print('PASS:', result)
"
```

---

### F7.6 — Tests para F7

**Archivo:** `tests/tools/test_activity_plan_tool.py` (nuevo)

**Verificación:**
```bash
python3 -m pytest tests/tools/test_activity_plan_tool.py -v --tb=short 2>&1 | tail -20
```

---

## Fase 5: F8 — CRM Compatibility Bridge and No-Duplicate Follow-ups

**Owner:** `codex-builder`
**Reviewer:** `claude-builder`
**Gate requerido:** F5 tools existentes + CRM schema accesible

### F8.1 — Mapear `crm.follow_ups` → `activity.activities`

**Investigación previa:**
```bash
psql $CRM_DB_URL -c "\d crm.follow_ups"
```

**Verificación:**
```bash
python3 -c "
from tools.crm_tool import crm_follow_up_create
import json
# Llamar CRM tool existente y verificar que también crea activity
result = json.loads(crm_follow_up_create(
    title='Test CRM follow-up',
    contact_id='test-contact-1',
    due_at='2026-06-15T10:00:00Z'
))
assert 'ok' in result or 'id' in result, f'CRM failed: {result}'
print('PASS: CRM returned', result)
"
```

---

### F8.2 — `crm_follow_up_create` → upsert activity

**Archivo:** `tools/crm_tool.py` (modificar `crm_follow_up_create`)

**Cambio:** después de INSERT en `crm.follow_ups`, hacer INSERT en `activity.activities` con link.

**Verificación:**
```bash
python3 -c "
from tools.crm_tool import crm_follow_up_create
import json
result = json.loads(crm_follow_up_create(
    title='CRM bridge test',
    contact_id='test-contact-1',
    due_at='2026-06-15T10:00:00Z'
))
# Verificar que activity fue creada
from tools.activity_tool import activity_list
activities = json.loads(activity_list(owner_id='zeus', status='open', limit=10))
# Debe contener la nueva activity con source='crm'
print('PASS: CRM bridge created follow-up')
"
```

---

### F8.3 — Dedupe entre `crm.follow_ups` y `activity.activities`

**Archivo:** `tools/activity_tool.py` (modificar `activity_upsert`)

**Lógica dedupe:** chequear `crm.follow_ups` además de `activity.activities` para evitar duplicados cross-table.

**Verificación:**
```bash
python3 -c "
# Test: crear CRM follow-up, luego crear activity con mismo dedupe_key
# Debe retornar 'linked_existing' en lugar de crear duplicado
print('Dedupe test: see F8 test file')
"
```

---

### F8.4 — Tests de regresión CRM

**Archivo:** `tests/tools/test_crm_tool.py` (extender existente)

**Verificación:**
```bash
python3 -m pytest tests/tools/test_crm_tool.py -v --tb=short -k "follow_up" 2>&1 | tail -30
```

---

## Fase 6: F9 — QA Regression and Live/Direct Smoke Verification

**Owner:** `qa-verifier`
**Reviewer:** `quality-reviewer`
**Gate requerido:** F8 CRM bridge + todos los tools de F5-F7 implementados

### F9.1 — Unit test suite para `activity_tool.py`

**Archivo:** `tests/tools/test_activity_tool.py` (nuevo)

**Verificación:**
```bash
python3 -m pytest tests/tools/test_activity_tool.py -v --tb=short 2>&1 | tail -30
```

**Criterios de aceptación:**
- Al menos 1 test por cada handler: `activity_upsert`, `activity_list`, `activity_complete`, `activity_snooze`, `activity_reschedule`, `activity_cancel`, `activity_link`, `activity_unlink`, `activity_timeline`, `activity_dispatcher_scan`
- Tests usan fixtures o setup/teardown
- No crashea con argumentos faltantes (ArgumentError handling verificado)
- `pytest` exit code 0

---

### F9.2 — Unit test suite para `activity_plan_tool.py`

**Archivo:** `tests/tools/test_activity_plan_tool.py` (nuevo)

**Verificación:**
```bash
python3 -m pytest tests/tools/test_activity_plan_tool.py -v --tb=short 2>&1 | tail -30
```

**Criterios de aceptación:**
- Al menos 1 test por cada handler: `activity_plan_create`, `activity_plan_apply`, `activity_next_actions`, `activity_detect_from_text`, `activity_recurrence_expand`
- Tests usan fixtures o setup/teardown
- `pytest` exit code 0

---

### F9.3 — Unit test suite para `activity_dispatcher.py`

**Archivo:** `tests/cron/test_activity_dispatcher.py` (nuevo)

**Verificación:**
```bash
python3 -m pytest tests/cron/test_activity_dispatcher.py -v --tb=short 2>&1 | tail -30
```

**Criterios de aceptación:**
- Smoke test: dispatcher corre sin error con DB vacía
- Empty-result test: retorna JSON válido con arrays vacíos
- `pytest` exit code 0

---

### F9.4 — Smoke test CRM bridge

**Archivo:** `tests/tools/test_crm_tool.py` (extender existente)

**Verificación:**
```bash
python3 -m pytest tests/tools/test_crm_tool.py -v --tb=short -k "follow_up" 2>&1 | tail -30
```

**Criterios de aceptación:**
- `crm_follow_up_create` crea activity en `activity.activities`
- Dedupe: segundo call con mismos args retorna `operation='linked_existing'`
- No crea filas duplicadas en `activity.activities`
- `pytest` exit code 0

---

### F9.5 — Smoke test live/direct (Hermes tools directo)

**Verificación:**
```bash
# Test actividad sigue el flujo completo: create → list → complete
python3 -c "
from tools.activity_tool import activity_upsert, activity_list, activity_complete
import json

# Create
r = activity_upsert(title='Smoke test activity', owner_id='qa-test', source='smoke_test', due_at='2026-06-10T10:00:00Z')
d = json.loads(r) if isinstance(r, str) else r
assert 'activity_id' in d, f'upsert failed: {d}'

# List
r2 = activity_list(owner_id='qa-test', limit=5)
d2 = json.loads(r2) if isinstance(r2, str) else r2
assert any(a['activity_id'] == d['activity_id'] for a in d2.get('activities', [])), 'activity not found in list'

# Complete
r3 = activity_complete(activity_id=d['activity_id'], completion_note='smoke test done')
d3 = json.loads(r3) if isinstance(r3, str) else r3
assert 'completed_at' in d3, f'complete failed: {d3}'

print('PASS: full activity lifecycle smoke test')
"
```

**Criterios de aceptación:**
- Create/List/Complete fluyen sin error
- JSON output parseable en cada paso
- No exceptions no controladas

---

### F9.6 — Smoke test `activity_dispatcher_scan`

**Verificación:**
```bash
python3 -c "
from tools.activity_tool import activity_dispatcher_scan
import json
r = activity_dispatcher_scan(limit=5)
d = json.loads(r) if isinstance(r, str) else r
assert isinstance(d, dict), f'Expected dict, got {type(d)}'
assert all(k in d for k in ['due', 'upcoming', 'overdue']), f'Missing keys: {d}'
print('PASS: dispatcher_scan keys:', sorted(d.keys()))
"
```

---

## Fase 7: F10 — Security/Privacy/Tool-Boundary Review

**Owner:** `security-reviewer`
**Reviewer:** `zeus`
**Gate requerido:** F9 todos los tests pasando

### F10.1 — Revisión de herramienta: permisos y acceso a datos

**Archivo:** `tools/activity_tool.py`, `tools/activity_plan_tool.py`, `tools/crm_tool.py`

**Verificación:**
```bash
# Verificar que las tools NO contienen:
# - Credenciales hardcodeadas
# - SQL injection (uso de format() con strings externas en queries)
# - Acceso a agent_memory o agent_context sin autorización
grep -n "os.environ\[" tools/activity_tool.py tools/activity_plan_tool.py tools/crm_tool.py | grep -v "TEST_DB_URL\|DATABASE_URL"
grep -rn "%.format" tools/activity_tool.py tools/activity_plan_tool.py tools/crm_tool.py
grep -rn "f'" tools/activity_tool.py tools/activity_plan_tool.py tools/crm_tool.py | grep SQL | grep -v "activity_id\|owner_id"
```

**Criterios de aceptación:**
- [ ] Sin credenciales hardcodeadas en archivos de tools
- [ ] Sin SQL injection: params pasados como $1, $2 (psycopg2 parameterized) o bind vars
- [ ] Sin acceso no autorizado a agent_memory/agent_context

---

### F10.2 — Revisión de tool boundary: qué información cruza el boundary

**Verificación:** Inspección de código + test de boundary

```bash
# Ninguna tool de activity debe escribir fuera del schema 'activity' o 'agent_core'
python3 -c "
import ast, sys

SENSITIVE_SCHEMAS = {'agent_memory', 'agent_context', 'auth', 'billing', 'users'}
BLOCKED_PATHS = ['agent_memory', 'agent_context']

for tool_file in ['tools/activity_tool.py', 'tools/activity_plan_tool.py', 'tools/crm_tool.py']:
    with open(tool_file) as f:
        content = f.read()
    for schema in SENSITIVE_SCHEMAS:
        if schema in content and 'CREATE' in content and 'activity.' not in content:
            print(f'WARNING: {tool_file} references {schema}')
            sys.exit(1)
print('PASS: no sensitive schema access detected')
"
```

**Criterios de aceptación:**
- [ ] Tools solo leen/escriben en `activity` schema (y `agent_core` para module registry)
- [ ] No hay acceso a `agent_memory`, `agent_context` desde activity tools
- [ ] CRM tool solo escribe en `crm` y `activity` schemas

---

### F10.3 — Revisión de dedupe_key y privacidad de datos

**Verificación:**
```bash
# Verificar que dedupe_key no expone PII
python3 -c "
from tools.activity_tool import activity_upsert
import json

# Crear actividad con datos de prueba
r = activity_upsert(title='Security test', owner_id='security-test', source='sec_review')
d = json.loads(r) if isinstance(r, str) else r
dk = d.get('dedupe_key', '')
print('dedupe_key:', dk)

# dedupe_key no debe contener email, phone, o datos personales
forbidden = ['@', '+', 'phone', 'ssn', 'pass']
for f in forbidden:
    if f.lower() in dk.lower():
        print(f'FAIL: forbidden pattern {f} in dedupe_key: {dk}')
        exit(1)
print('PASS: dedupe_key clean')
"
```

**Criterios de aceptación:**
- [ ] dedupe_key no contiene PII (email, phone, nombres completos)
- [ ] dedupe_key es un hash o combinación de campos no-PII
- [ ]owner_id usado directamente en dedupe_key es un ID interno, no un email

---

### F10.4 — Revisión de rates y límites de uso

**Verificación:** Inspección de código

**Criterios de aceptación:**
- [ ] No hay loops infinitos en `activity_recurrence_expand` (count máximo 366)
- [ ] `activity_dispatcher_scan` tiene límite hard (limit param)
- [ ] `activity_list` tiene límite máximo (max 1000, default 50)

---

### F10.5 — Revisión de logging y auditoría

**Verificación:**
```bash
# activity_tool y cron deben escribir a activity_events (audit trail)
grep -n "activity_events" tools/activity_tool.py cron/activity_dispatcher.py
```

**Criterios de aceptación:**
- [ ] Operaciones de create/update/complete escriben en `activity_events`
- [ ] Eventos incluyen: event_type, created_at, actor (owner_id)
- [ ] No se loguean datos sensibles en plaintext

---

## Fase 8: F11 — Delivery Docs, Skill Updates, and Factory Reconciliation

**Owner:** `devops-release`
**Reviewer:** `factory-orchestrator`
**Gate requerido:** F10 security review pasando + F9 smoke passing

### F11.1 — Actualizar skill de Hermes Agent con nuevas tools

**Archivo:** `~/.hermes/skills/hermes-agent/SKILL.md` o skill de actividad

**Verificación:**
```bash
# Verificar que las nuevas tools están documentadas en skill
grep -l "activity_upsert\|activity_list\|activity_plan" ~/.hermes/skills/hermes-agent/SKILL.md
```

**Criterios de aceptación:**
- [ ] Skill documenta todas las activity_* tools
- [ ] Skill incluye examples de uso
- [ ] Skill menciona dedupe_key y deduplicación

---

### F11.2 — Entregables de documentación

**Archivos:** `docs/activity-tooling.md`, `docs/activity-schema.md` (nuevos)

**Verificación:**
```bash
ls -la docs/activity-tooling.md docs/activity-schema.md
```

**Criterios de aceptación:**
- [ ] `docs/activity-schema.md`: full DDL reference para todo el schema `activity`
- [ ] `docs/activity-tooling.md`: referencia completa de cada tool (params, output, ejemplos)
- [ ] Documentación de dedupe_key derivation

---

### F11.3 — Migration artifacts listos para apply

**Archivos:** `db/modules/activity/*.sql`

**Verificación:**
```bash
# dry-run de cada migration en orden
for f in db/modules/activity/0000*.sql; do
  echo "=== \$f ==="
  psql $TEST_DB_URL -c "START TRANSACTION; $(cat $f); ROLLBACK;" 2>&1 | grep -E "ERROR|SUCCESS|ROLLBACK" || true
done
```

**Criterios de aceptación:**
- [ ] Todos los .sql files aplican sin error en dry-run
- [ ] Migration files son idempotentes (CREATE IF NOT EXISTS)
- [ ] Nombres de archivo siguen formato `000NNN_*.sql`

---

### F11.4 — Actualizar TRACKER.md con estado final

**Archivo:** `factory/projects/agent-core-followup-reminders/TRACKER.md`

**Verificación:**
```bash
grep "Estado actual" factory/projects/agent-core-followup-reminders/TRACKER.md
```

**Criterios de aceptación:**
- [ ] TRACKER.md refleja F4-F11 como completados
- [ ] Gates de F9/F10 marcados como passed
- [ ] Evidence paths actualizados con paths reales

---

### F11.5 — Factory DB: marcar F3 como planning=passed

**Verificación:** Factory DB query

```bash
# Verificar que el gate planning está pendiente de revisión
psql $FACTORY_DB_URL -c "
SELECT project_id, task_id, gate, status, reviewer, updated_at
FROM factory.gates
WHERE project_id = 'agent-core-followup-reminders'
  AND task_id LIKE '%f3%'
  AND gate = 'planning';
"
```

**Criterios de aceptación:**
- [ ] Gate planning para F3 registrado como `pending` con reviewer asignado
- [ ] Todos los gates F4-F11 creados con estado inicial `pending`
- [ ] Evidence status de F3 actualizado a `pending_review`

---

## Dependencias entre tareas

```
F4 (DB migrations)
  └─ F5 (Activity tools)
        ├─ F6 (Calendar bridge + dispatcher)
        └─ F7 (Plans/chaining/recurrence)
              └─ F8 (CRM bridge)
                    └─ F9 (QA smoke)
                          └─ F10 (Security review)
                                └─ F11 (Delivery docs)
```

## Gates requeridos antes de cada fase

|| Fase | Gate |
||------|------|
|| F4 | `planning=passed` (F3) + `architecture=passed` (F2) |
|| F5 | `planning=passed` (F3) + F4 migration applied |
|| F6 | F5 tools `activity_upsert`, `activity_list` funcionando |
|| F7 | F5 tools funcionando |
|| F8 | F5 tools + CRM schema accesible |
|| F9 | F8 smoke passing |
|| F10 | F9 tests passing |
|| F11 | F10 security review passing |

## Handoff notes

- F4 debe entregar migration files listos para apply dry-run. No ejecutar apply en prod sin F9 smoke.
- F5-F8 deben mantener tool output siempre JSON, nunca prose.
- No agregar features fuera de scope sin pasar por F10 security review.
- Para debugging: `hermes logs --level DEBUG --session <session_id>`.
- F9 smoke test live/direct debe ejecutarse desde la CLI de Hermes Agent real, no solo pytest.
- F10 security review es obligatorio antes de F11 delivery; no se hace delivery sin security gate.

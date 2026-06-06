# F5_EVIDENCE — Activity/follow-up Hermes tools and toolset

## Estado

- Incremento: F5 — Activity/follow-up Hermes tools and toolset
- Run: `run-1780716665-01933638`
- Fecha UTC: `2026-06-06T03:39:35Z`
- Owner: `claude-builder`
- Reviewer esperado: `quality-reviewer`
- Fuente de verdad operacional: Agent Core Postgres `factory.*`

## Archivos implementados

- `tools/activity_tool.py`
  - Nuevo tool module auto-discoverable por `tools.registry.discover_builtin_tools()`.
  - Registra toolset `activity` con handlers JSON para:
    - `activity_status`
    - `activity_upsert`
    - `activity_list`
    - `activity_complete`
    - `activity_snooze`
    - `activity_reschedule`
    - `activity_cancel`
    - `activity_link`
    - `activity_unlink`
    - `activity_timeline`
    - `activity_dispatcher_scan`
    - `activity_plan_create`
    - `activity_plan_apply`
    - `activity_next_actions`
    - `activity_detect`
- `toolsets.py`
  - Agrega toolset explícito `activity`.
  - No agrega `activity_*` a `_HERMES_CORE_TOOLS`, `hermes-cli`, customer-service ni otros default/unrelated toolsets.
- `hermes_cli/agent_core_sql.py`
  - Agrega default `ACTIVITY_DB_RUNTIME_USER=activity_runtime` para consistencia con el módulo Agent Core `activity`.
- `tests/tools/test_activity_tool.py`
  - Tests de required-field validation, SQL quoting safety, detection preview y registro explícito/no-default.

## Cobertura contra acceptance criteria

1. Tools cubren operación completa sin UI:
   - Create/upsert: `activity_upsert`.
   - Link/unlink: `activity_link`, `activity_unlink`.
   - Due/upcoming/overdue: `activity_list(due_filter=...)` y `activity_dispatcher_scan` con buckets `due`, `upcoming`, `overdue`.
   - Complete/snooze/reschedule/cancel: `activity_complete`, `activity_snooze`, `activity_reschedule`, `activity_cancel`.
   - Timeline: `activity_timeline`.
   - Plans: `activity_plan_create`, `activity_plan_apply`.
   - Next-actions: `activity_next_actions`.
   - Detection: `activity_detect` preview por defecto; `persist=true` crea activities.

2. Handlers JSON, validación y SQL safety:
   - Todos los handlers retornan JSON string vía `_ok()` o `tool_error()`.
   - Campos requeridos se validan antes de tocar DB.
   - User-provided text/IDs/JSON se insertan con `agent_core_sql.quote_literal()` / `quote_jsonb()`.
   - `limit`, `offset` y offsets numéricos se normalizan a enteros acotados.
   - Partial unique indexes se respetan con `ON CONFLICT (dedupe_key) WHERE dedupe_key IS NOT NULL` e `ON CONFLICT (idempotency_key) WHERE idempotency_key IS NOT NULL`.

3. Toolset registration explícito y sin bloat:
   - `toolsets.TOOLSETS['activity']` contiene solo `activity_*`.
   - `activity_upsert not in toolsets._HERMES_CORE_TOOLS` verificado por test.
   - No se modificó `customer_service`, `crm`, `calendar`, `hermes-cli` core ni messaging defaults para incluir estos tools.

## Comandos ejecutados y resultados

### RED test inicial

```bash
python3 -m pytest tests/tools/test_activity_tool.py -q
```

Resultado esperado antes de implementación:

```text
ImportError: cannot import name 'activity_tool' from 'tools'
1 error in 0.32s
```

### Unit tests específicos F5

```bash
python3 -m py_compile tools/activity_tool.py && python3 -m pytest tests/tools/test_activity_tool.py -q
```

Resultado:

```text
.......                                                                  [100%]
7 passed in 0.42s
```

### Regression subset relevante

```bash
python3 -m pytest tests/test_toolsets.py tests/tools/test_crm_tool.py tests/test_customer_service_routing.py tests/tools/test_activity_tool.py -q
```

Resultado:

```text
...............................................                          [100%]
47 passed in 2.14s
```

### Registry readback del toolset activity

```bash
python3 - <<'PY'
from tools import activity_tool
from tools.registry import registry
names = registry.get_tool_names_for_toolset('activity')
print(names)
required = {'activity_status','activity_upsert','activity_list','activity_complete','activity_snooze','activity_reschedule','activity_cancel','activity_link','activity_unlink','activity_timeline','activity_dispatcher_scan','activity_plan_create','activity_plan_apply','activity_next_actions','activity_detect'}
assert required <= set(names), sorted(required-set(names))
PY
```

Resultado:

```text
['activity_cancel', 'activity_complete', 'activity_detect', 'activity_dispatcher_scan', 'activity_link', 'activity_list', 'activity_next_actions', 'activity_plan_apply', 'activity_plan_create', 'activity_reschedule', 'activity_snooze', 'activity_status', 'activity_timeline', 'activity_unlink', 'activity_upsert']
```

### Toolset explicit/no-default readback

```bash
python3 - <<'PY'
import toolsets
print('activity' in toolsets.TOOLSETS)
print('activity_upsert' in toolsets._HERMES_CORE_TOOLS)
print(toolsets.TOOLSETS['activity']['tools'])
PY
```

Resultado:

```text
True
False
['activity_status', 'activity_upsert', 'activity_list', 'activity_complete', 'activity_snooze', 'activity_reschedule', 'activity_cancel', 'activity_link', 'activity_unlink', 'activity_timeline', 'activity_dispatcher_scan', 'activity_plan_create', 'activity_plan_apply', 'activity_next_actions', 'activity_detect']
```

### Live DB smoke intentado

```bash
python3 - <<'PY'
import json
from tools import activity_tool
print(activity_tool._handle_activity_status())
PY
```

Resultado:

```text
{"error": "Command '['docker', 'exec', '-i', 'agent-postgres', 'psql', '-X', '-q', '-t', '-A', '-v', 'ON_ERROR_STOP=1', '-U', 'activity_runtime', '-d', 'zeus_agent']' returned non-zero exit status 2."}
```

Diagnóstico read-only:

```bash
docker exec -i agent-postgres psql -X -q -t -A -v ON_ERROR_STOP=1 -U activity_runtime -d zeus_agent -c 'SELECT 1;'
```

Resultado:

```text
psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed: FATAL:  role "activity_runtime" does not exist
```

Esto bloquea solo el smoke live local con `activity_runtime`; no invalida los tests unitarios ni el registro del toolset. No apliqué migraciones F4 ni hice escrituras DB directas fuera del scope F5.

## Riesgos / carry-forward

- Riesgo operacional: el contenedor local `agent-postgres` no tiene el rol `activity_runtime`, por lo que `activity_status` y los handlers que usan `_user()` no pueden ejecutar smoke live local hasta que F4/migration runtime grants esté aplicada en esa DB. F4 reportó evidencia previa, pero esta verificación local concreta falla por rol inexistente.
- F6/F7 pueden reemplazar o ampliar la lógica mínima de dispatcher/plan/detection si necesitan recurrence/calendar más profunda. En F5 quedan herramientas agent-operable básicas con IDs/evidencia y SQL safety.
- No se hizo commit/push/merge/deploy.

## Rework run `run-1780718514-2f55749f` — 2026-06-06T04:03:57Z

Motivo de rework atendido:

- Se verificó Factory DB con backend canónico `agent_core_postgres`, database `zeus_agent`, project `agent-core-followup-reminders`, task F5 en `running` rework claim event `704`.
- Se agregó cobertura de required-field validation para `activity_plan_create`: los steps se validan antes de escribir `activity.activity_plans` o borrar/reinsertar `activity.activity_plan_steps`.
- Se corrigió `tools/activity_tool.py` para prevalidar `steps` (`title_template`, `activity_type`, `default_priority`, shape object) antes de cualquier escritura de plan/steps.

RED observado:

```bash
python3 -m pytest tests/tools/test_activity_tool.py::test_activity_plan_create_validates_step_title_before_db_query -v
```

Resultado esperado antes del fix:

```text
FAILED tests/tools/test_activity_tool.py::test_activity_plan_create_validates_step_title_before_db_query
AssertionError: assert 'database should not be queried when required plan step fields are missing' == 'step title_template is required'
```

GREEN/verificación final:

```bash
python3 -m py_compile tools/activity_tool.py
python3 -m pytest tests/tools/test_activity_tool.py -v
python3 -m pytest tests/test_toolsets.py tests/tools/test_crm_tool.py tests/test_customer_service_routing.py tests/tools/test_activity_tool.py -v
```

Resultados:

```text
py_compile tools/activity_tool.py -> OK
tests/tools/test_activity_tool.py -> 8 passed in 0.45s
regression subset -> 48 passed in 1.87s
```

Evidencia adicional:

- `tests/tools/test_activity_tool.py` ahora cubre 8 tests F5, incluyendo validación pre-DB para `activity_plan_create`.
- `tools/activity_tool.py` mantiene 15 handlers `activity_*`; el cambio es acotado a validación de plan steps antes de DB.
- `toolsets.py` sigue con toolset explícito `activity` y sin inclusión en `_HERMES_CORE_TOOLS` (assert cubierto por `test_toolset_registration_is_explicit_and_not_in_core_defaults`).

## Resultado

F5 implementado a nivel código y pruebas unitarias/regression subset. Rework aplicado y verificado. Requiere review independiente `quality-reviewer`; smoke DB end-to-end sigue delegado a F9 o a reconciliación runtime del rol `activity_runtime` si el contenedor local no trae grants aplicados.

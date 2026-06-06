# F6_EVIDENCE — Calendar bridge and deterministic reminder dispatcher

## Estado

- Incremento: F6 — Calendar bridge and deterministic reminder dispatcher
- Run: `run-1780721176-b4e9523b`
- Fecha UTC: `2026-06-06T04:48:56Z`
- Owner: `claude-builder`
- Reviewer esperado: `devops-release`
- Fuente de verdad operacional verificada: Agent Core Postgres `factory.*`
  - `db_backend`: `agent_core_postgres`
  - `database`: `zeus_agent`
  - Task F6: `agent-core-followup-reminders-f6-calendar-bridge-and-deterministic-rem`

## Archivos implementados

- `tools/activity_tool.py`
  - Agrega bridge `activity_to_calendar_event(**kwargs)` y handler registrado `activity_to_calendar_event`.
  - Usa el adapter genérico existente `tools/calendar_tool.py` (`calendar_create_event` / `calendar_block_time`) en vez de duplicar scheduler.
  - Lee la activity desde `activity.activities` y sólo crea evento/bloque si:
    - `activity_type IN ('meeting','call')`, o
    - `metadata.calendar_required=true`, o
    - `metadata.time_block_required=true`, o
    - `calendar_required=true` en args.
  - Para reminders/follow-ups sin time blocking retorna `status='skipped'` y no llama Calendar Core.
  - En éxito crea link `activity.activity_links` con `target_type='calendar_event'` y `relationship_type='calendar_event'`.
  - Audita `calendar_requested`, `calendar_linked` y `calendar_failed` en `activity.activity_events`.
  - Rework `run-1780721176-b4e9523b`: el tool handler `activity_dispatcher_scan` ahora delega al path canónico `cron.activity_dispatcher.run_dispatcher_scan(...)` con `dry_run`, para que el toolset y el cron usen la misma implementación determinística y auditada.
- `toolsets.py`
  - Agrega `activity_to_calendar_event` al toolset explícito `activity` sin incluirlo en core defaults.
- `cron/activity_dispatcher.py`
  - Nuevo dispatcher determinístico importable y ejecutable.
  - `run_dispatcher_scan(owner_id=None, limit=50, dry_run=False)` consulta Activity Core y produce outputs `notification_ready` sin depender de memoria de chat.
  - Consulta:
    - activities activas vencidas o próximas dentro de 1h;
    - `reminder_rules.enabled=true` con `next_fire_at <= now()`;
    - `recurrence_rules.enabled=true` en ventana de 24h para materialización posterior.
  - Escribe audit events con idempotency keys cuando `dry_run=False`.
  - No envía notificaciones ni crea eventos de calendario; sólo produce salida lista para adapter de notificaciones.
- `tests/tools/test_activity_tool.py`
  - Agrega cobertura del calendar bridge: skip de reminder no-calendario, creación/link calendar, failure retryable auditado.
  - Rework: agrega `test_activity_dispatcher_scan_tool_delegates_to_deterministic_dispatcher` para probar que el tool handler `activity_dispatcher_scan` comparte el dispatcher canónico auditado y soporta `dry_run`.
- `tests/cron/test_activity_dispatcher.py`
  - Agrega cobertura del dispatcher: outputs notification-ready + audit events, y `dry_run` sin escrituras.

## Cobertura contra acceptance criteria

1. Activities can link to calendar events/blocks through generic calendar tools when time blocking is needed.
   - `activity_to_calendar_event` llama `calendar_tool.calendar_create_event` o `calendar_tool.calendar_block_time`.
   - En éxito crea `activity_link` hacia `calendar_event` y audita `calendar_linked`.
   - Test: `test_activity_to_calendar_event_creates_event_and_calendar_link`.

2. Non-calendar reminders do not force calendar event creation.
   - `_calendar_required()` sólo permite Calendar Core para meeting/call o flags explícitos.
   - Si una activity `reminder` no trae flags, retorna `status='skipped'` y no llama calendar.
   - Test: `test_activity_to_calendar_event_skips_non_calendar_reminders`.

3. A deterministic reminder scan/dispatcher path exists with audited outputs and no reliance on chat memory.
   - `cron.activity_dispatcher.run_dispatcher_scan()` usa sólo Agent Core SQL + Activity audit events.
   - Retorna JSON con `outputs[*].action_status='notification_ready'` y metadata de backend/script/limit.
   - Audita `reminder_due`, `reminder_dispatched` y `recurrence_materialized` salvo `dry_run=True`.
   - Tests: `tests/cron/test_activity_dispatcher.py`.

## RED observado

```bash
python3 -m pytest tests/tools/test_activity_tool.py tests/cron/test_activity_dispatcher.py -q
```

Resultado antes de implementación F6:

```text
ImportError: cannot import name 'activity_dispatcher' from 'cron'
1 error in 0.47s
```

Además Pyright reportó símbolos faltantes esperados para:

```text
tools.activity_tool.calendar_tool
_handle_activity_to_calendar_event
cron.activity_dispatcher
```

## GREEN / verificación final

### Unit + regression subset F6/F5/Calendar

```bash
python3 -m pytest tests/tools/test_activity_tool.py tests/tools/test_calendar_tool.py tests/cron/test_activity_dispatcher.py -q
```

Resultado:

```text
.................                                                        [100%]
17 passed in 0.78s
```

### Syntax compile

```bash
python3 -m py_compile tools/activity_tool.py cron/activity_dispatcher.py
```

Resultado:

```text
OK (exit_code=0)
```

### Import/readback de paths determinísticos

```bash
python3 - <<'PY'
from tools.activity_tool import activity_to_calendar_event
from cron.activity_dispatcher import run_dispatcher_scan
print('imports ok', callable(activity_to_calendar_event), callable(run_dispatcher_scan))
PY
```

Resultado:

```text
imports ok True True
```

### Registry readback del toolset `activity`

```bash
python3 - <<'PY'
from tools import activity_tool
from tools.registry import registry
names = registry.get_tool_names_for_toolset('activity')
required = {'activity_to_calendar_event','activity_dispatcher_scan'}
print(names)
assert required <= set(names), sorted(required-set(names))
PY
```

Resultado:

```text
['activity_cancel', 'activity_complete', 'activity_detect', 'activity_dispatcher_scan', 'activity_link', 'activity_list', 'activity_next_actions', 'activity_plan_apply', 'activity_plan_create', 'activity_reschedule', 'activity_snooze', 'activity_status', 'activity_timeline', 'activity_to_calendar_event', 'activity_unlink', 'activity_upsert']
```

### Dispatcher live dry-run intentado

```bash
python3 - <<'PY'
from cron.activity_dispatcher import run_dispatcher_scan
import json
payload = json.loads(run_dispatcher_scan(dry_run=True, limit=1))
print(payload.get('ok'), payload.get('status'), payload.get('count'), payload.get('error'))
PY
```

Resultado local:

```text
False None None Command '['docker', 'exec', '-i', 'agent-postgres', 'psql', '-X', '-q', '-t', '-A', '-v', 'ON_ERROR_STOP=1', '-U', 'activity_runtime', '-d', 'zeus_agent']' returned non-zero exit status 2.
```

Diagnóstico: mismo bloqueo local ya documentado en F5; el contenedor local `agent-postgres` no tiene rol `activity_runtime`. No apliqué migraciones ni grants en esta tarea porque F6 no autoriza escrituras directas a DB ni migraciones fuera de scope. Los unit tests cubren el SQL/output/audit path con mocks determinísticos.

## Factory DB verification

Comando:

```bash
hermes factory status agent-core-followup-reminders --json
```

Readback relevante tras rework:

```text
"db_backend": "agent_core_postgres"
"database": "zeus_agent"
Task F6 status after gate: "running"
Task F6 evidence_status after gate: "present"
Task F6 reviewer_profile: "devops-release"
```

Gate registrado para este rework:

```bash
hermes factory gate record agent-core-followup-reminders implementation passed --lane-id agent-core-followup-hybrid --task-id agent-core-followup-reminders-f6-calendar-bridge-and-deterministic-rem --reviewer claude-builder --notes "F6 rework run-1780721176-b4e9523b: activity_dispatcher_scan tool handler now delegates to cron.activity_dispatcher.run_dispatcher_scan with dry_run; calendar bridge unchanged; tests pass: 17 passed via python3 -m pytest tests/tools/test_activity_tool.py tests/tools/test_calendar_tool.py tests/cron/test_activity_dispatcher.py -q; py_compile tools/activity_tool.py cron/activity_dispatcher.py OK; evidence factory/projects/agent-core-followup-reminders/F6_EVIDENCE.md." --json
```

Resultado:

```json
{"gate_id": 180, "project_id": "agent-core-followup-reminders", "status": "passed"}
```

Nota operacional: el estado de task sigue `running` aunque `finished_at` existe y `evidence_status=present`; esto queda como drift de reconciliación para el orquestador/runtime, no como cambio de alcance F6.

## Riesgos / carry-forward

- Live DB smoke sigue bloqueado localmente por rol `activity_runtime` ausente en `agent-postgres`; debe quedar para F9/devops o para aplicar grants/migrations con el rol autorizado. No se hizo escritura DB directa por la regla dura de runtime.
- `activity_to_calendar_event` no envía invitaciones ni resuelve participantes; sólo bridgea activity ↔ Calendar Core. Free/busy avanzado queda disponible vía `calendar_find_availability` y puede usarse por el agente antes de llamar el bridge.
- `cron.activity_dispatcher` produce notification-ready outputs y audit events; no entrega notificaciones reales. El envío pertenece a adapters de notificaciones y futuros jobs configurados explícitamente.
- No se hizo commit/push/merge/deploy.

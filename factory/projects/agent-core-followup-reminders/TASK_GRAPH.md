# Task Graph — Agent Core Follow-up / Reminders

## Estado

- Incremento: F3 — Implementation plan and task graph
- Run: `run-1780712703-2092c8a2`
- Owner: `implementation-planner`
- Reviewer: `factory-orchestrator`
- Fecha: `2026-06-05`

## Sprint Decomposition

| Sprint | Incrementos | Objetivo | Gate de entrada | Gate de salida |
|--------|-------------|----------|-----------------|-----------------|
| Sprint 1 | F4 | DB schema y grants — foundation ejecutable | `planning=passed` + `architecture=passed` | `implementation` parcial |
| Sprint 2 | F5 | Tools activity_* — layer de interacción | Sprint 1 verificado | `implementation` parcial |
| Sprint 3 | F6 | Calendar bridge + dispatcher | Sprint 2 tools verificadas | `implementation` parcial |
| Sprint 4 | F7 | Plans/chaining/recurrence/quick-capture | Sprint 2 tools verificadas | `implementation` parcial |
| Sprint 5 | F8 | CRM bridge + deduplicación | Sprint 4 plans verificados | `implementation` completo |
| Sprint 6 | F9 + F10 + F11 | QA + Security + Delivery | Sprint 5 completo | `delivery` |

**Regla secuencial**: no iniciar sprint N hasta que Sprint N-1 haya registrado gate `implementation` parcial o completo en Factory DB. Excepciones requieren autorización explícita de `factory-orchestrator`.

---

## Dependency Graph

```mermaid
flowchart TD
  F0["F0 Kickoff/tracker/skill"] --> F1["F1 Functional PRD"]
  F1 --> F2["F2 Architecture ADR"]
  F2 --> F3["F3 Implementation plan"]
  F3 --> F4["F4 DB migrations"]
  F4 --> F5["F5 Activity tools"]
  F5 --> F6["F6 Calendar bridge"]
  F5 --> F7["F7 Plans/chaining"]
  F6 --> F8["F8 CRM bridge"]
  F7 --> F8
  F8 --> F9["F9 QA smoke"]
  F9 --> F10["F10 Security review"]
  F10 --> F11["F11 Delivery docs"]

  subgraph SPRINT1["Sprint 1 — Foundation"]
    F4
  end
  subgraph SPRINT2["Sprint 2 — Tools"]
    F5
  end
  subgraph SPRINT3_4["Sprint 3-4 — Advanced"]
    F6
    F7
  end
  subgraph SPRINT5["Sprint 5 — Integration"]
    F8
  end
  subgraph SPRINT6["Sprint 6 — Hardening"]
    F9
    F10
    F11
  end
```

---

## Sprint 1 Detail — F4: DB Migrations

**Owner:** `claude-builder` | **Reviewer:** `codex-builder` | **Sprint goal:** Schema activity.* creado y verificado en test DB

### F4.1 — Module registry + schema seed

| Campo | Valor |
|-------|-------|
| File | `db/modules/activity/000001_activity_schema.sql` |
| Verification | `psql $TEST_DB_URL -c "SELECT module, schema_name FROM agent_core.modules WHERE module='activity';"` |
| Output | 1 row con module=activity |
| Owner | claude-builder |
| Reviewer | codex-builder |
| Evidence | SQL file + dry-run output + DB readback |

**Acceptance criteria:**
- [ ] `CREATE SCHEMA IF NOT EXISTS activity;` presente
- [ ] `INSERT INTO agent_core.modules` con module='activity' y metadata JSON con project tag
- [ ] `ON CONFLICT (module) DO UPDATE` para idempotencia
- [ ] dry-run no arroja errores de sintaxis
- [ ] readback confirma fila en `agent_core.modules`

---

### F4.2 — Tabla `activity.activities`

| Campo | Valor |
|-------|-------|
| File | `db/modules/activity/000002_activities.sql` |
| Verification | `psql $TEST_DB_URL -c "\\d activity.activities"` + column check |
| Output | Tabla con todas las columnas definidas en ADR-002 |
| Owner | claude-builder |
| Reviewer | codex-builder |
| Evidence | SQL file + `\d` output + row count (0 inicialmente) |

**Acceptance criteria:**
- [ ] Tabla `activity.activities` creada con todas las columnas del ADR
- [ ] `activity_id` es PK con serial o uuid
- [ ] `dedupe_key` tiene UNIQUE constraint
- [ ] `status` con CHECK constraint en ('open','completed','cancelled','snoozed')
- [ ] `due_at` con timezone (timestamptz)
- [ ] Index en `(owner_id, status, due_at)` para queries frecuentes
- [ ] `\d` output muestra tabla y constraints
- [ ] `SELECT COUNT(*) FROM activity.activities LIMIT 0` retorna 0 rows

---

### F4.3 — Tabla `activity.activity_links`

| Campo | Valor |
|-------|-------|
| File | `db/modules/activity/000003_activity_links.sql` |
| Owner | claude-builder |
| Reviewer | codex-builder |
| Verification | `psql $TEST_DB_URL -c "\\d activity.activity_links"` |
| Output | Tabla con link_id PK, source_id, target_id, relationship_type |
| Evidence | SQL file + `\d` output |

**Acceptance criteria:**
- [ ] Tabla `activity.activity_links` creada
- [ ] FK a `activity.activities(activity_id)` en source_id y target_id con ON DELETE CASCADE
- [ ] Unique constraint en (source_id, target_id, relationship_type)
- [ ] Index en source_id y target_id por separado
- [ ] `\d` output confirma estructura

---

### F4.4 — Tabla `activity.reminder_rules`

| Campo | Valor |
|-------|-------|
| File | `db/modules/activity/000004_reminder_rules.sql` |
| Owner | claude-builder |
| Reviewer | codex-builder |
| Verification | `psql $TEST_DB_URL -c "\\d activity.reminder_rules"` |
| Output | Tabla con rule_id PK, activity_id FK, next_fire_at, enabled |
| Evidence | SQL file + `\d` output |

**Acceptance criteria:**
- [ ] Tabla `activity.reminder_rules` creada
- [ ] FK a `activity.activities(activity_id)` con ON DELETE CASCADE
- [ ] `next_fire_at` timestamptz con index
- [ ] `enabled` boolean con DEFAULT true
- [ ] `\d` output confirma

---

### F4.5 — Tabla `activity.activity_events`

| Campo | Valor |
|-------|-------|
| File | `db/modules/activity/000005_activity_events.sql` |
| Owner | claude-builder |
| Reviewer | codex-builder |
| Verification | `psql $TEST_DB_URL -c "\\d activity.activity_events"` |
| Output | Tabla con event_id PK, activity_id FK, event_type, created_at |
| Evidence | SQL file + `\d` output |

**Acceptance criteria:**
- [ ] Tabla `activity.activity_events` creada
- [ ] FK a `activity.activities(activity_id)` con ON DELETE CASCADE
- [ ] `event_type` con CHECK constraint listing valid event types
- [ ] Index en (activity_id, created_at)
- [ ] `\d` output confirma

---

### F4.6 — Tablas `activity_plans`, `activity_plan_steps`, `activity_plan_runs`, `activity_plan_run_steps`

| Campo | Valor |
|-------|-------|
| File | `db/modules/activity/000006_activity_plans.sql` |
| Owner | claude-builder |
| Reviewer | codex-builder |
| Verification | `\d activity.activity_plans` + `\d activity.activity_plan_steps` + run tables |
| Output | 4 tablas con FK chain completa |
| Evidence | SQL file + 4x `\d` outputs |

**Acceptance criteria:**
- [ ] `activity_plans` con plan_id PK, name, description, created_by
- [ ] `activity_plan_steps` con step_id PK, plan_id FK, title, relative_after_days, activity_type
- [ ] `activity_plan_runs` con run_id PK, plan_id FK, target_type, target_id, status, started_at
- [ ] `activity_plan_run_steps` con run_step_id PK, run_id FK, step_id FK, activity_id FK (nullable, se llena al crear activity)
- [ ] FK chain completa con ON DELETE CASCADE
- [ ] Los 4 `\d` outputs confirman

---

### F4.7 — Tablas `activity.recurrence_rules` y `activity.recurrence_instances`

| Campo | Valor |
|-------|-------|
| File | `db/modules/activity/000007_recurrence_rules.sql` |
| Owner | claude-builder |
| Reviewer | codex-builder |
| Verification | `\d activity.recurrence_rules` |
| Output | recurrence_rules creada; recurrence_instances opcional |
| Evidence | SQL file + `\d` output(s) |

**Acceptance criteria:**
- [ ] `activity.recurrence_rules` creada con rule_id PK, activity_id FK, rrule_text, from_date, count
- [ ] FK a `activity.activities(activity_id)` con ON DELETE CASCADE
- [ ] `rrule_text` tipo TEXT
- [ ] `\d activity.recurrence_rules` confirma
- [ ] `recurrence_instances` opcional: si existe, crea con instance_id PK, rule_id FK, instance_date

---

### F4.8 — Runtime grants para `activity_runtime`

| Campo | Valor |
|-------|-------|
| File | `db/modules/activity/000008_runtime_grants.sql` |
| Owner | claude-builder |
| Reviewer | codex-builder |
| Verification | `psql $TEST_DB_URL -c "SELECT grantee, privilege_type FROM information_schema.table_privileges WHERE table_schema='activity' AND grantee='activity_runtime';"` |
| Output | Múltiples filas con grants |
| Evidence | SQL file + readback query |

**Acceptance criteria:**
- [ ] `GRANT USAGE ON SCHEMA activity TO activity_runtime`
- [ ] `GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA activity TO activity_runtime`
- [ ] `GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA activity TO activity_runtime`
- [ ] Readback confirma al menos 4 filas para activity_runtime
- [ ] `activity_runtime` puede hacer SELECT en `agent_core.modules`

---

## Sprint 2 Detail — F5: Activity Tools
## Sprint 2 Detail — F5: Activity Tools

**Owner:** `claude-builder` | **Reviewer:** `quality-reviewer` | **Sprint goal:** tool handlers activity_* ejecutables y probados

### F5.1 — Toolset registry

| Campo | Valor |
|-------|-------|
| File | `tools/toolsets.py` |
| Owner | claude-builder |
| Reviewer | quality-reviewer |
| Verification | `python3 -c "from toolsets import _HERMES_CORE_TOOLS; print('activity' in _HERMES_CORE_TOOLS)"` |
| Output | `True` |
| Evidence | toolsets.py patch + command output |

**AC:** `'activity'` presente en `_HERMES_CORE_TOOLS` después del patch.

---

### F5.2 — `activity_upsert`

| Campo | Valor |
|-------|-------|
| File | `tools/activity_tool.py` |
| Owner | claude-builder |
| Reviewer | quality-reviewer |
| Handler | `activity_upsert()` |
| Verification | `python3 -c "from tools.activity_tool import activity_upsert; import json; r=activity_upsert(title='Test', owner_id='zeus', source='test'); print(json.loads(r) if isinstance(r,str) else r)"` |
| Output | JSON con `activity_id`, `operation`, `dedupe_key` |
| Evidence | JSON output |

**AC:**
- [ ] `registry.register("activity_upsert")` en tools/activity_tool.py
- [ ] Función exportable como `from tools.activity_tool import activity_upsert`
- [ ] Params: todos los listados en IMPLEMENTATION_PLAN.md F5.2
- [ ] INSERT con ON CONFLICT sobre dedupe_key
- [ ] Retorna JSON parseable con `activity_id`, `operation` (created|updated|linked_existing), `dedupe_key`
- [ ] Test: `activity_upsert(title='Test', owner_id='zeus', source='test')` produce JSON válido

---

### F5.3 — `activity_list`

| Campo | Valor |
|-------|-------|
| File | `tools/activity_tool.py` |
| Owner | claude-builder |
| Reviewer | quality-reviewer |
| Handler | `activity_list()` |
| Verification | `python3 -c "from tools.activity_tool import activity_list; import json; r=activity_list(owner_id='zeus', limit=5); print(json.loads(r) if isinstance(r,str) else r)"` |
| Output | JSON con `activities` array |
| Evidence | JSON output |

**AC:**
- [ ] Retorna JSON con `activities` (array) o `ok` con estructura
- [ ] Soporta filtros: owner_id, status, due_filter
- [ ] Soporta pagination: limit, offset
- [ ] `activity_list()` sin argumentos no crashea

---

### F5.4 — `activity_complete`

| Campo | Valor |
|-------|-------|
| File | `tools/activity_tool.py` |
| Owner | claude-builder |
| Reviewer | quality-reviewer |
| Handler | `activity_complete()` |
| Verification | `python3 -c "from tools.activity_tool import activity_complete; import json; print(activity_complete(activity_id='test-id', completion_note='Done'))"` |
| Output | JSON con `completed_at` |
| Evidence | JSON output |

**AC:**
- [ ] `activity_complete(activity_id=<id>, completion_note='Done')` retorna JSON con `completed_at`
- [ ] actualiza `status='completed'` en DB
- [ ] Si activity_id no existe, retorna error JSON (no exception)

---

### F5.5 — `activity_snooze`, `activity_reschedule`, `activity_cancel`

| Campo | Valor |
|-------|-------|
| File | `tools/activity_tool.py` |
| Owner | claude-builder |
| Reviewer | quality-reviewer |
| Handler | Cada función |
| Verification | `python3 -c "from tools.activity_tool import activity_snooze, activity_reschedule, activity_cancel; print('import ok')"` |
| Output | Import sin error |
| Evidence | Python import output |

**AC:**
- [ ] `activity_snooze(activity_id, snoozed_until)` → JSON con `snoozed_until`
- [ ] `activity_reschedule(activity_id, new_due_at)` → JSON con nuevo `due_at`
- [ ] `activity_cancel(activity_id, reason)` → JSON con `cancelled_at`

---

### F5.6 — `activity_link` / `activity_unlink`

| Campo | Valor |
|-------|-------|
| File | `tools/activity_tool.py` |
| Owner | claude-builder |
| Reviewer | quality-reviewer |
| Handler | `activity_link()`, `activity_unlink()` |
| Verification | `python3 -c "from tools.activity_tool import activity_link, activity_unlink; print('import ok')"` |
| Output | Import sin error |
| Evidence | Python import output |

**AC:**
- [ ] `activity_link(activity_id, target_type, target_id, relationship_type)` → JSON con `ok` o `link_id`
- [ ] `activity_unlink(link_id)` → JSON con `ok`
- [ ] Si link ya existe, no crea duplicado

---

### F5.7 — `activity_timeline`

| Campo | Valor |
|-------|-------|
| File | `tools/activity_tool.py` |
| Owner | claude-builder |
| Reviewer | quality-reviewer |
| Handler | `activity_timeline()` |
| Verification | `python3 -c "from tools.activity_tool import activity_timeline; print('import ok')"` |
| Output | Import sin error |
| Evidence | Python import output |

**AC:**
- [ ] `activity_timeline(target_type, target_id, limit)` → JSON estructurado
- [ ] Incluye todos los eventos de la actividad ordenados por created_at

---

### F5.8 — `activity_dispatcher_scan`

| Campo | Valor |
|-------|-------|
| File | `tools/activity_tool.py` |
| Owner | claude-builder |
| Reviewer | quality-reviewer |
| Handler | `activity_dispatcher_scan()` |
| Verification | `python3 -c "from tools.activity_tool import activity_dispatcher_scan; import json; r=activity_dispatcher_scan(limit=5); d=json.loads(r) if isinstance(r,str) else r; print(sorted(d.keys()))"` |
| Output | JSON con keys `due`, `upcoming`, `overdue` |
| Evidence | JSON output |

**AC:**
- [ ] `activity_dispatcher_scan(limit)` → JSON con keys `due`, `upcoming`, `overdue`
- [ ] No envía notificaciones (solo prepara output)
- [ ] Si no hay resultados, retorna JSON válido con arrays vacíos

---

### F5.9 — Tests

| Campo | Valor |
|-------|-------|
| File | `tests/tools/test_activity_tool.py` |
| Owner | qa-verifier |
| Reviewer | quality-reviewer |
| Verification | `python3 -m pytest tests/tools/test_activity_tool.py -v --tb=short` |
| Evidence | pytest output con todos los tests passing |

**AC:**
- [ ] Al menos 1 test por handler (F5.2–F5.8)
- [ ] Tests usan fixtures o setup/teardown
- [ ] No crashea con argumentos faltantes
- [ ] `pytest` exit code 0

---

## Sprint 3 Detail — F6: Calendar Bridge + Dispatcher

**Owner:** `claude-builder` | **Reviewer:** `devops-release` | **Sprint goal:** calendar bridge + dispatcher job funcionales

### F6.1 — `activity_to_calendar_event`

| Campo | Valor |
|-------|-------|
| File | `tools/calendar_tool.py` o `tools/activity_tool.py` |
| Owner | claude-builder |
| Reviewer | devops-release |
| Handler | `activity_to_calendar_event()` |
| Verification | `python3 -c "from tools.activity_tool import activity_to_calendar_event; print('import ok')"` |
| Output | Import sin error |
| Evidence | Python import output |

**AC:**
- [ ] `activity_to_calendar_event(activity_id, title, start_at, end_at)` → JSON con `calendar_event_id` y `status`
- [ ] Si activity_id no existe, retorna error JSON
- [ ] Si calendar service falla, escribe event en `activity_events` con event_type='calendar_failed' y retorna `status=retryable`

---

### F6.2 — Dispatcher job

| Campo | Valor |
|-------|-------|
| File | `cron/activity_dispatcher.py` |
| Owner | claude-builder |
| Reviewer | devops-release |
| Handler | `run_dispatcher_scan(limit)` |
| Verification | `python3 -c "from cron.activity_dispatcher import run_dispatcher_scan; print('import ok')"` |
| Output | Import sin error |
| Evidence | Python import output |

**AC:**
- [ ] `from cron.activity_dispatcher import run_dispatcher_scan` funciona
- [ ] Retorna JSON con `activities` (array de activities due/overdue)
- [ ] No depende de memoria de chat; solo DB
- [ ] No envía notificaciones externas (output es para consumo interno)

---

### F6.3 — Dispatcher smoke tests

| Campo | Valor |
|-------|-------|
| File | `tests/cron/test_activity_dispatcher.py` |
| Owner | qa-verifier |
| Reviewer | devops-release |
| Verification | `python3 -m pytest tests/cron/test_activity_dispatcher.py -v --tb=short` |
| Evidence | pytest output |

**AC:**
- [ ] Al menos 2 tests: smoke test y empty-result test
- [ ] `pytest` exit code 0

---

## Sprint 4 Detail — F7: Plans / Chaining / Recurrence / Quick Capture

**Owner:** `claude-builder` | **Reviewer:** `product-analyst` | **Sprint goal:** plan tools, recurrence, quick capture funcionales

### F7.1 — `activity_plan_create`

| Campo | Valor |
|-------|-------|
| File | `tools/activity_plan_tool.py` |
| Owner | claude-builder |
| Reviewer | product-analyst |
| Handler | `activity_plan_create()` |
| Verification | `python3 -c "from tools.activity_plan_tool import activity_plan_create; print('import ok')"` |
| Output | Import sin error |
| Evidence | Python import output |

**AC:**
- [ ] `activity_plan_create(plan_name, description, steps)` → JSON con `plan_id`
- [ ] steps es array de objetos con title, relative_after_days, activity_type, priority
- [ ] Crea filas en `activity_plans` y `activity_plan_steps`

---

### F7.2 — `activity_plan_apply`

| Campo | Valor |
|-------|-------|
| File | `tools/activity_plan_tool.py` |
| Owner | claude-builder |
| Reviewer | product-analyst |
| Handler | `activity_plan_apply()` |
| Verification | `python3 -c "from tools.activity_plan_tool import activity_plan_apply; print('import ok')"` |
| Output | Import sin error |
| Evidence | Python import output |

**AC:**
- [ ] `activity_plan_apply(plan_id, target_type, target_id, target_name)` → JSON con `run_id`
- [ ] Crea fila en `activity_plan_runs`
- [ ] Genera activities en `activities` para cada step con due_at calculado
- [ ] Links cada activity generated al run via `activity_plan_run_steps`

---

### F7.3 — `activity_next_actions`

| Campo | Valor |
|-------|-------|
| File | `tools/activity_plan_tool.py` |
| Owner | claude-builder |
| Reviewer | product-analyst |
| Handler | `activity_next_actions()` |
| Verification | `python3 -c "from tools.activity_plan_tool import activity_next_actions; print('import ok')"` |
| Output | Import sin error |
| Evidence | Python import output |

**AC:**
- [ ] `activity_next_actions(target_type, target_id, owner_id, limit)` → JSON con actions
- [ ] Filtra por status='open',due_at no null, orden por due_at ASC
- [ ] Soporta owner_id y limit

---

### F7.4 — `activity_detect_from_text`

| Campo | Valor |
|-------|-------|
| File | `tools/activity_plan_tool.py` |
| Owner | claude-builder |
| Reviewer | product-analyst |
| Handler | `activity_detect_from_text()` |
| Verification | `python3 -c "from tools.activity_plan_tool import activity_detect_from_text; import json; r=activity_detect_from_text(text='Call John tomorrow at 3pm about the contract'); print(json.loads(r) if isinstance(r,str) else r)"` |
| Output | JSON con detected_activities array |
| Evidence | JSON output |

**AC:**
- [ ] Detecta patterns: "call X at Y", "follow up with X", "remind me to X"
- [ ] Retorna JSON con detected_activities array
- [ ] Cada detection incluye: title, activity_type, parsed_datetime si aplica

---

### F7.5 — `activity_recurrence_expand`

| Campo | Valor |
|-------|-------|
| File | `tools/activity_plan_tool.py` |
| Owner | claude-builder |
| Reviewer | product-analyst |
| Handler | `activity_recurrence_expand()` |
| Verification | `python3 -c "from tools.activity_plan_tool import activity_recurrence_expand; import json; r=activity_recurrence_expand(rrule_text='FREQ=WEEKLY;BYDAY=MO,WE,FR;COUNT=10', from_date='2026-06-01', count=10); d=json.loads(r) if isinstance(r,str) else r; print('PASS' if isinstance(d,list) else d)"` |
| Output | Array de dates |
| Evidence | JSON output |

**AC:**
- [ ] `activity_recurrence_expand(rule_id, from_date, count)` → JSON con instances array
- [ ] `activity_recurrence_expand(rrule_text, from_date, count)` → mismo output
- [ ] Soporta FREQ=DAILY, WEEKLY, MONTHLY
- [ ] Retorna array de dates ordenadas

---

### F7.6 — Tests para F7

| Campo | Valor |
|-------|-------|
| File | `tests/tools/test_activity_plan_tool.py` |
| Owner | qa-verifier |
| Reviewer | product-analyst |
| Verification | `python3 -m pytest tests/tools/test_activity_plan_tool.py -v --tb=short` |
| Evidence | pytest output con todos los tests passing |

**AC:**
- [ ] Al menos 1 test por handler F7.1–F7.5
- [ ] Tests usan fixtures o setup/teardown
- [ ] `pytest` exit code 0

---

## Sprint 5 Detail — F8: CRM Compatibility Bridge + No-Duplicate Follow-ups

**Owner:** `claude-builder` | **Reviewer:** `quality-reviewer` | **Sprint goal:** CRM bridge que previene duplicados

### F8.1 — `crm_follow_up_create` (CRM adapter)

| Campo | Valor |
|-------|-------|
| File | `tools/crm_tool.py` |
| Owner | claude-builder |
| Reviewer | quality-reviewer |
| Handler | `crm_follow_up_create()` |
| Verification | `python3 -c "from tools.crm_tool import crm_follow_up_create; print('import ok')"` |
| Output | Import sin error |
| Evidence | Python import output |

**AC:**
- [ ] `crm_follow_up_create(crm_type, contact_id, subject, due_at, priority)` → JSON con `activity_id` y dedupe_key
- [ ] Misma dedupe_key que activity_upsert para mismo contact_id + subject + due_at
- [ ] Si dup: retorna activity_id existente con `operation='linked_existing'` (no crea nuevo)

---

### F8.2 — Dedupe cross-table en `activity_upsert`

| Campo | Valor |
|-------|-------|
| File | `tools/activity_tool.py` |
| Owner | claude-builder |
| Reviewer | quality-reviewer |
| Verification | Revisión de dedupe_key logic en activity_upsert |
| Evidence | Código con dedupe_key derivation |

**AC:**
- [ ] Dedupe key incluye: owner_id + title + due_at (o hash estable)
- [ ] ON CONFLICT (dedupe_key) actualiza en vez de crear nuevo
- [ ] Retorna `operation='linked_existing'` con activity_id existente

---

### F8.3 — CRM bridge smoke test

| Campo | Valor |
|-------|-------|
| File | `tests/tools/test_crm_tool.py` |
| Owner | qa-verifier |
| Reviewer | quality-reviewer |
| Verification | `python3 -m pytest tests/tools/test_crm_tool.py -v -k "follow_up" --tb=short` |
| Evidence | pytest output |

**AC:**
- [ ] `crm_follow_up_create` crea activity en `activity.activities`
- [ ] Dedupe: segundo call con mismos args retorna linked_existing
- [ ] `pytest` exit code 0

---
**AC:**
- [ ] Tests existentes de crm_tool no se rompen
- [ ] Nuevos tests para follow_up + activity bridge pasan
- [ ] `pytest` exit code 0

---

## Sprint 6 Detail — F9: QA Regression and Live/Direct Smoke Verification

**Owner:** `qa-verifier` | **Reviewer:** `quality-reviewer` | **Sprint goal:** todos los gates de calidad pasados antes de security

### F9.1 — Unit test suite para `activity_tool.py`

| Campo | Valor |
|-------|-------|
| File | `tests/tools/test_activity_tool.py` |
| Owner | qa-verifier |
| Reviewer | quality-reviewer |
| Verification | `cd /home/jean/Projects/hermes-agent-original && python3 -m pytest tests/tools/test_activity_tool.py -v --tb=short` |
| Evidence | pytest output — todos los tests passing, exit code 0 |

**AC:**
- [ ] Al menos 1 test por cada handler: activity_upsert, activity_list, activity_complete, activity_snooze, activity_reschedule, activity_cancel, activity_link, activity_unlink, activity_timeline, activity_dispatcher_scan
- [ ] Tests usan fixtures o setup/teardown
- [ ] Args faltantes no crashean el handler — retornan error JSON
- [ ] `pytest` exit code 0

---

### F9.2 — Integration tests para migrations

| Campo | Valor |
|-------|-------|
| File | `tests/migrations/test_activity_schema.py` |
| Owner | qa-verifier |
| Reviewer | quality-reviewer |
| Verification | `python3 -m pytest tests/migrations/test_activity_schema.py -v --tb=short` |
| Evidence | pytest output — migrations aplican idempotentemente |

**AC:**
- [ ] Cada archivo 000001–000008 aplica sin errores en test DB limpia
- [ ] Segunda ejecución (idempotencia) no arroja errores
- [ ] Readback queries confirman todas las tablas y constraints

---

### F9.3 — Smoke test: dispatcher scan

| Campo | Valor |
|-------|-------|
| File | `tests/cron/test_activity_dispatcher.py` |
| Owner | qa-verifier |
| Reviewer | quality-reviewer |
| Verification | `python3 -m pytest tests/cron/test_activity_dispatcher.py -v --tb=short` |
| Evidence | pytest output — al menos 2 tests passing |

**AC:**
- [ ] Smoke test: dispatcher retorna JSON válido con keys `due`, `upcoming`, `overdue`
- [ ] Empty-result test: sin datos, retorna arrays vacíos (no exception)
- [ ] `pytest` exit code 0

---

### F9.4 — Smoke test: plan tools

| Campo | Valor |
|-------|-------|
| File | `tests/tools/test_activity_plan_tool.py` |
| Owner | qa-verifier |
| Reviewer | quality-reviewer |
| Verification | `python3 -m pytest tests/tools/test_activity_plan_tool.py -v --tb=short` |
| Evidence | pytest output — al menos 1 test por handler F7.1–F7.5 |

**AC:**
- [ ] activity_plan_create: retorna plan_id válido
- [ ] activity_plan_apply: crea run y activities
- [ ] activity_next_actions: filtra por owner y status='open'
- [ ] activity_detect_from_text: detecta al menos 3 patterns
- [ ] activity_recurrence_expand: FREQ=DAILY/WEEKLY/MONTHLY produce instances
- [ ] `pytest` exit code 0

---

### F9.5 — Regression tests: CRM bridge

| Campo | Valor |
|-------|-------|
| File | `tests/tools/test_crm_tool.py` |
| Owner | qa-verifier |
| Reviewer | quality-reviewer |
| Verification | `python3 -m pytest tests/tools/test_crm_tool.py -v -k "follow_up" --tb=short` |
| Evidence | pytest output — existing + new follow_up tests passing |

**AC:**
- [ ] Tests preexistentes de crm_tool no se rompen
- [ ] crm_follow_up_create crea activity en activity.activities
- [ ] Dedupe cross-table: mismo dedupe_key retorna linked_existing
- [ ] `pytest` exit code 0

---

### F9.6 — Live smoke: tool handlers via subprocess

| Campo | Valor |
|-------|-------|
| File | `tests/smoke/test_activity_smoke.py` |
| Owner | qa-verifier |
| Reviewer | quality-reviewer |
| Verification | `python3 -m pytest tests/smoke/test_activity_smoke.py -v --tb=short` |
| Evidence | pytest output — smoke exit code 0 |

**AC:**
- [ ] `activity_upsert` retorna JSON con activity_id y operation
- [ ] `activity_list` retorna JSON con array de activities
- [ ] `activity_complete` actualiza status en DB
- [ ] `activity_dispatcher_scan` retorna JSON con keys `due`/`upcoming`/`overdue`
- [ ] Todos los JSON son parseables — ningún prose混入
- [ ] `pytest` exit code 0

---

### F9.7 — QA report

| Campo | Valor |
|-------|-------|
| File | `factory/projects/agent-core-followup-reminders/QA_REPORT.md` |
| Owner | qa-verifier |
| Reviewer | quality-reviewer |
| Verification | File existe y contiene tabla de resultados por test suite |
| Evidence | QA_REPORT.md actualizado con resultados de F9.1–F9.6 |

**AC:**
- [ ] Tabla con: test suite, # tests, # passed, # failed, exit code
- [ ] Cobertura declarada: qué módulos/funciones tienen tests
- [ ] Gate `quality=passed` o `quality=failed` registrado en Factory DB

---

## Sprint 6 Detail — F10: Security / Privacy / Tool-Boundary Review

**Owner:** `security-reviewer` | **Reviewer:** `solution-architect` | **Sprint goal:** validar que activity tools no exponen datos sensibles ni violan tool boundaries

### F10.1 — Tool boundary audit: allowed toolset surface

| Campo | Valor |
|-------|-------|
| File | `tools/activity_tool.py` (audit) |
| Owner | security-reviewer |
| Reviewer | solution-architect |
| Verification | Revisión manual + grep de patrones forbidden + test negativo |
| Evidence | Security review report con allowed/forbidden tools list |

**AC:**
- [ ] activity_tool.py no importa ni llama herramientas de otros domains (CRM(Calendar) Sales Admin) salvo las explícitamente allowlisted
- [ ] allowed list documentado: qué tools activity puede invocar
- [ ] forbidden list documentado: qué tools NO puede invocar
- [ ] Test negativo: intento de invocar tool forbidden retorna error JSON (no exception)
- [ ] Security review report con allowed/forbidden lists

---

### F10.2 — PII/privacy audit: datos de contacto en activities

| Campo | Valor |
|-------|-------|
| File | `tools/activity_tool.py` + schema audit |
| Owner | security-reviewer |
| Reviewer | solution-architect |
| Verification | Revisión de columnas y queries; grep para phone, email, address, SSN en activity schema |
| Evidence | Security review report con findings PII |

**AC:**
- [ ] `owner_id`, `assignee_id`, `participants` no contienen PII directo — usan IDs referenciales
- [ ] `metadata` jsonb no guarda PII sin cifrado
- [ ] `evidence` text field no persiste contenido de mensajes/notes completos sin sanitización
- [ ] Grep: no hay columnas phone, email, address, SSN en activity schema
- [ ] Security review report con PII assessment

---

### F10.3 — SQL injection audit: parameterized queries

| Campo | Valor |
|-------|-------|
| File | `tools/activity_tool.py` |
| Owner | security-reviewer |
| Reviewer | solution-architect |
| Verification | `grep -n "execute\|cursor\|sql" tools/activity_tool.py` + revisión de params |
| Evidence | Security review report |

**AC:**
- [ ] Todas las queries SQL usan parámetros (no string interpolation)
- [ ] Ningún `f"SELECT ... {variable}"` o `"SELECT ... " + var`
- [ ] Grep no encuentra vars interpoladas en queries SQL

---

### F10.4 — Access control audit: activity_runtime grants

| Campo | Valor |
|-------|-------|
| File | `db/modules/activity/000008_runtime_grants.sql` |
| Owner | security-reviewer |
| Reviewer | solution-architect |
| Verification | Revisar grants vs minimum necessary principle |
| Evidence | Security review report |

**AC:**
- [ ] activity_runtime NO tiene grants a tablas fuera del schema activity (n.c. agent_core.modules read-only)
- [ ] activity_runtime NO tiene SUPERUSER, CREATEROLE, o grants de admin
- [ ] Grants son minimum necessary para operations

---

### F10.5 — Dispatcher boundary audit: no external sends

| Campo | Valor |
|-------|-------|
| File | `cron/activity_dispatcher.py` |
| Owner | security-reviewer |
| Reviewer | solution-architect |
| Verification | Revisión de código + grep para patterns de envío externo |
| Evidence | Security review report |

**AC:**
- [ ] Dispatcher NO llama a send_message, telegram.send, whatsapp.send, o similares
- [ ] Dispatcher NO escribe archivos fuera de /tmp o logs
- [ ] Output del dispatcher es JSON puro para consumo interno
- [ ] Grep no encuentra patrones de envío externo

---

### F10.6 — Security review report

| Campo | Valor |
|-------|-------|
| File | `factory/projects/agent-core-followup-reminders/SECURITY_REVIEW.md` |
| Owner | security-reviewer |
| Reviewer | solution-architect |
| Verification | File existe con secciones: tool boundary, PII, SQL injection, access control, dispatcher boundary |
| Evidence | SECURITY_REVIEW.md actualizado + gate security=passed o failed |

**AC:**
- [ ] Todas las secciones F10.1–F10.5 documentadas con findings
- [ ] Findings clasificados: critical / high / medium / low / info
- [ ] Gate `security=passed` o `security=failed` registrado en Factory DB
- [ ] Si failed: blockers listados con remediation steps

---

## Sprint 6 Detail — F11: Delivery Docs, Skill Updates, and Factory Reconciliation

**Owner:** `factory-reporter` | **Reviewer:** `devops-release` | **Sprint goal:** artifacts completos, skill propagado, proyecto cerrado en Factory DB

### F11.1 — Delivery report

| Campo | Valor |
|-------|-------|
| File | `factory/projects/agent-core-followup-reminders/DELIVERY_REPORT.md` |
| Owner | factory-reporter |
| Reviewer | devops-release |
| Verification | File existe con: summary, artifacts, test results, gates summary, next steps |
| Evidence | DELIVERY_REPORT.md completo |

**AC:**
- [ ] Executive summary: qué se entregó
- [ ] Artifact register: todos los archivos creados/modificados con paths
- [ ] Test results: F9.1–F9.6 resultados resumidos
- [ ] Gate summary: todos los gates y su status final
- [ ] Next steps: cómo continuar operación/producción

---

### F11.2 — Notion page update

| Campo | Valor |
|-------|-------|
| File | Notion page del proyecto (si existe) |
| Owner | factory-reporter |
| Reviewer | devops-release |
| Verification | Notion page existe y refleja estado final del proyecto |
| Evidence | Notion page URL en DELIVERY_REPORT.md |

**AC:**
- [ ] Página de Notion actualizada con estado final: gates, artifacts, next steps
- [ ] URL de Notion documentada en DELIVERY_REPORT.md

---

### F11.3 — Skill propagation verification

| Campo | Valor |
|-------|-------|
| File | Cada worker profile skill directory |
| Owner | factory-reporter |
| Reviewer | devops-release |
| Verification | `ls ~/.hermes/profiles/*/skills/ | grep -i followup` o similar |
| Evidence | Output del comando de verificación |

**AC:**
- [ ] `agent-core-followup-reminders` skill disponible en: claude-builder, codex-builder, qa-verifier, security-reviewer, factory-reporter
- [ ] Cada perfil puede hacer `skill_view(name='agent-core-followup-reminders')` sin error
- [ ] Output verificado en DELIVERY_REPORT.md

---

### F11.4 — Factory DB reconciliation: proyecto cerrado

| Campo | Valor |
|-------|-------|
| File | Factory DB (Postgres) |
| Owner | factory-reporter |
| Reviewer | devops-release |
| Verification | `hermes factory status agent-core-followup-reminders --json` muestra project status final |
| Evidence | Factory DB rows actualizados |

**AC:**
- [ ] Todas las tareas F0–F11 con status final en Factory DB
- [ ] Gate delivery=passed registrado
- [ ] Project status = completed o delivery_hold según corresponda
- [ ] No hay tareas pendientes sin assignee

---

### F11.5 — Repo artifact commit (opcional según ciclo)

| Campo | Valor |
|-------|-------|
| File | Repo con artifacts en branch |
| Owner | factory-reporter |
| Reviewer | devops-release |
| Verification | `git log --oneline -3` muestra commit con artifacts |
| Evidence | Commit SHA en DELIVERY_REPORT.md |

**AC:**
- [ ] Si Factory usa branch/worktree: PR o commit con artifacts creado
- [ ] Commit SHA documentado en DELIVERY_REPORT.md

---

## Risk Register

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|------------|--------|------------|
| R1 | `architecture` gate pendiente de security-reviewer — bloquea Sprint 1 | High | High | Notificar a security-reviewer; mientras tanto preparar F4.1–F4.3 en branch |
| R2 | CRM schema diferente al asumido en ADR | Medium | Medium | F8.1 incluye schema audit antes de implementar bridge |
| R3 | Calendar tool no tiene `calendar_event_create` | Medium | Medium | F6.1 diseñado defensivamente — falla gracefully y loguea event |
| R4 | Test DB no disponible para dry-run | Low | High | Usar migración idempotente con `IF NOT EXISTS` |
| R5 | activity_runtime role no existe en prod | Low | Medium | F4.8 incluye CREATE ROLE IF NOT EXISTS + grant |

---

## Gate Dependencies

| Gate | Status | Required for |
|------|--------|--------------|
| intake (F0) | passed | F1 |
| functional (F1) | passed | F2, F3 |
| architecture (F2) | review_ready — security-reviewer pendiente | F4 |
| planning (F3) | este incremento — factory-orchestrator | F4 |
| implementation (F4) | Sprint 1 output | F5 |
| implementation (F5) | Sprint 2 output | F6, F7 |
| implementation (F6, F7) | Sprint 3-4 output | F8 |
| implementation (F8) | Sprint 5 output | F9 |
| quality (F9) | Sprint 6 | F10 |
| security (F10) | Sprint 6 | F11 |
| delivery (F11) | Sprint 6 | — |

---

## Owner/Reviewer Assignment Summary

| Task | Owner | Reviewer | Sprint |
|------|-------|----------|--------|
| F4 | claude-builder | codex-builder | Sprint 1 |
| F5 | claude-builder | quality-reviewer | Sprint 2 |
| F6 | claude-builder | devops-release | Sprint 3 |
| F7 | claude-builder | product-analyst | Sprint 4 |
| F8 | codex-builder | claude-builder | Sprint 5 |
| F9 | qa-verifier | quality-reviewer | Sprint 6 |
| F10 | security-reviewer | solution-architect | Sprint 6 |
| F11 | factory-reporter | devops-release | Sprint 6 |

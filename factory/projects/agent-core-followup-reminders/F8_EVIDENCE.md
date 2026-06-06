# F8 — CRM compatibility bridge and no-duplicate follow-ups

Run: run-1780758900-6e741bfa
Profile: codex-builder
Timestamp: 2026-06-06T11:17:31-04:00
Task: agent-core-followup-reminders-f8-crm-compatibility-bridge-and-no-dupli

## Scope

Rework acotado para corregir el bug reportado por el reviewer: `_find_activity_by_dedupe()` usaba `activity_tool._handle_activity_list({"dedupe_key": ...})`, pero `activity_list` no aplicaba `dedupe_key` en el WHERE. En presencia de múltiples actividades, el path `crm_follow_up_create` con follow-up existente podía devolver/enlazar un `activity_id` no relacionado.

## Files changed in this rework

- `tools/activity_tool.py`
  - `_handle_activity_list` ahora acepta y filtra `dedupe_key` junto con los filtros existentes (`owner_id`, `status`, `activity_type`, `priority`, `source`, `assignee_id`).
- `tests/tools/test_activity_tool.py`
  - Agregado `test_activity_list_filters_by_dedupe_key`, regresión hermética que falla si el SQL generado no contiene `a.dedupe_key='dedupe-target'` y simula que se devolvería `act-wrong` sin el filtro.
- `tests/tools/test_crm_tool.py`
  - Agregado `test_find_activity_by_dedupe_uses_activity_list_dedupe_filter`, regresión hermética que prueba `_find_activity_by_dedupe()` usando el path real de `activity_list` en vez de mockear una respuesta feliz.

## RED evidence

Command:

```bash
.venv/bin/python -m pytest -o addopts='' tests/tools/test_activity_tool.py::test_activity_list_filters_by_dedupe_key -v
```

Result before fix:

```text
FAILED tests/tools/test_activity_tool.py::test_activity_list_filters_by_dedupe_key
AssertionError: assert [{'activity_id': 'act-wrong', 'dedupe_key': 'dedupe-other'}] == [{'activity_id': 'act-right', 'dedupe_key': 'dedupe-target'}]
```

## GREEN / verification evidence

Commands:

```bash
.venv/bin/python -m pytest -o addopts='' tests/tools/test_activity_tool.py::test_activity_list_filters_by_dedupe_key tests/tools/test_crm_tool.py::test_find_activity_by_dedupe_uses_activity_list_dedupe_filter -v
.venv/bin/python -m pytest -o addopts='' tests/tools/test_crm_tool.py -v
.venv/bin/python -m pytest -o addopts='' tests/tools/test_activity_tool.py -v
.venv/bin/python -m py_compile tools/crm_tool.py tools/activity_tool.py
```

Results:

```text
2 passed in 0.44s
17 passed in 0.74s
13 passed in 0.63s
py_compile exit code 0
```

## Acceptance criteria mapping

1. `crm_follow_up_create` bridges to Activity Layer without breaking existing callers:
   - Existing F8 tests still pass: follow-up create creates activity + legacy/context links; existing caller path returns `operation='exists'` without inserting duplicate CRM follow-up.
2. `crm_customer_timeline` includes activity-layer activities:
   - Existing F8 timeline regression remains passing in `tests/tools/test_crm_tool.py`.
3. One interaction does not create duplicate follow-ups/activities:
   - Existing duplicate tests still pass.
   - New rework tests prove the dedupe activity lookup cannot return an unrelated activity when multiple activities exist because `activity_list` now filters by `dedupe_key`.

## Risk / open items

- No live Agent Core DB smoke was attempted in this rework. Prior project evidence indicates local live smoke is blocked by missing local runtime role `activity_runtime`; F9 owns live/direct smoke verification.
- Repo contains many pre-existing modified/untracked files from other increments. This rework only intentionally touched the files listed above plus this evidence artifact.

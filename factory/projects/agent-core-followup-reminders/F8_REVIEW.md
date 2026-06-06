# F8 Review — CRM compatibility bridge and no-duplicate follow-ups

Reviewer: claude-builder
Run reviewed: run-1780759322-372fa134
Timestamp: 2026-06-06
Task: agent-core-followup-reminders-f8-crm-compatibility-bridge-and-no-dupli

## Verdict

STATE: DONE

F8 can close at implementation review level. The rework addresses the previous blocker: duplicate follow-up lookup now uses a real activity-layer dedupe filter path, and repeated `crm_follow_up_create` calls do not insert a second legacy CRM follow-up or activity.

## Evidence checked

Factory DB source of truth:

- `hermes factory status agent-core-followup-reminders --json`
- Confirmed backend: `agent_core_postgres`, database: `zeus_agent`.
- Confirmed task F8 in review/run state with evidence_status present and prior failed implementation gate recorded.

Project-local artifact reviewed:

- `factory/projects/agent-core-followup-reminders/F8_EVIDENCE.md`

Code/tests reviewed:

- `tools/crm_tool.py`
- `tools/activity_tool.py`
- `tests/tools/test_crm_tool.py`
- `tests/tools/test_activity_tool.py`

Commands run:

```bash
.venv/bin/python -m pytest -o addopts='' tests/tools/test_crm_tool.py tests/tools/test_activity_tool.py -v && .venv/bin/python -m py_compile tools/crm_tool.py tools/activity_tool.py
```

Result:

```text
30 passed in 1.20s
py_compile exit code 0
```

Additional reviewer smoke:

```bash
.venv/bin/python - <<'PY'
# hermetic monkeypatch smoke: two identical crm_follow_up_create calls
# expected one CRM insert, one activity upsert, second call returns existing activity via dedupe_key
PY
```

Result summary:

```text
first.operation=created
second.operation=exists
follow_up_inserts=1
activity_upserts=1
activity_list_args[0].dedupe_key=crm_fu_20a6c8f21e507d6f
```

Registry/schema smoke:

```bash
.venv/bin/python - <<'PY'
# imported tools.activity_tool and tools.crm_tool; inspected registry._tools
PY
```

Result summary:

```text
crm_follow_up_create_registered=True
crm_customer_timeline_registered=True
activity_list_has_dedupe_key_in_schema=False
```

## Acceptance criteria mapping

1. `crm_follow_up_create` bridges to Activity Layer without breaking existing callers.
   - PASS: handler preserves legacy `follow_up` result and adds non-breaking `activity_id`, `operation`, and `dedupe_key` fields.
   - PASS: create path calls `activity_tool._handle_activity_upsert` with `source='crm'`, `activity_type='follow_up'`, `dedupe_key`, and links back to `crm.follow_ups` plus CRM entity context links.

2. `crm_customer_timeline` includes relevant activities/reminders/calendar links or documents new timeline tool path.
   - PASS: timeline path calls `activity_tool._handle_activity_timeline` for contact/organization/opportunity targets and includes returned `activities` in `crm_customer_timeline` output.

3. Tests prove one interaction does not create duplicate follow-ups/activities.
   - PASS: unit tests cover duplicate CRM follow-up prevention for `crm_follow_up_create` and `crm_interaction_record`.
   - PASS: rework regression proves `_find_activity_by_dedupe()` uses the real `activity_list` path and that `activity_list` SQL filters by `a.dedupe_key`, preventing the prior wrong-activity match.
   - PASS: reviewer smoke verified two identical `crm_follow_up_create` calls perform exactly one legacy follow-up insert and one activity upsert.

## Non-blocking notes

- Live Agent Core DB smoke remains intentionally deferred to F9, consistent with task graph and prior runtime blocker (`activity_runtime` role absent locally).
- `activity_list` handler accepts/filters `dedupe_key`, but the registered public schema does not advertise `dedupe_key`. This does not block F8 because the CRM bridge uses the internal handler path, but F9/F11 should consider exposing it if agents need to query activity dedupe directly.
- Repo has broad pre-existing modified/untracked files from other increments; this review scoped only F8-relevant files and artifacts.

## Gate recommendation

Record implementation gate as passed for F8 and allow F9 QA regression/live smoke to proceed.

# F7 — Activity plans, chaining, recurrence, and quick capture evidence

Task: `agent-core-followup-reminders-f7-activity-plans-chaining-recurrence-an`
Run: `run-1780722506-8a2734fc`
Profile: `claude-builder`
Date: 2026-06-06

## Scope implemented

- Added `tools/activity_plan_tool.py` as the focused F7 helper surface:
  - `activity_plan_create(...)`
  - `activity_plan_apply(...)`
  - `activity_next_actions(...)`
  - `activity_complete_with_next_actions(...)`
  - `activity_detect_from_text(...)` / `activity_quick_capture(...)`
  - `activity_recurrence_expand(...)`
- Extended `tools/activity_tool.py` plan application so generated activities receive the calculated step `due_at` (`start_at + offset_seconds`) and step assignment defaults from metadata (`default_assignee_id`, labels, plan/run/target metadata).
- Extended the `activity` toolset in `toolsets.py` with the F7 helper tools:
  - `activity_complete_with_next_actions`
  - `activity_detect_from_text`
  - `activity_recurrence_expand`
- Added `tests/tools/test_activity_plan_tool.py` with coverage for F7.1–F7.5:
  - reusable activity plans and assignment defaults;
  - plan application and generated due dates;
  - completion + next-action suggestions;
  - quick capture due dates, recurrence, person/project refs, labels, uncertainty;
  - recurrence expansion for DAILY/WEEKLY/MONTHLY RRULE subset.
- Updated `tests/tools/test_activity_tool.py` to assert the new tools are explicit opt-in activity tools, not core defaults.

## Dependency / license note

No new package was installed or added to `pyproject.toml` / `uv.lock` for F7.

Rationale:
- `python-dateutil` is present in the current environment (`2.9.0.post0`) and is suitable from a license perspective (dual Apache-2.0/BSD), but it is not currently a direct core dependency in this repo.
- To avoid adding a supply-chain/runtime dependency in this worker increment, `activity_recurrence_expand` implements the required lightweight RRULE subset (`FREQ=DAILY`, `FREQ=WEEKLY`, `FREQ=MONTHLY`) with Python stdlib only.
- If future increments require full RFC 5545 recurrence semantics, promote `python-dateutil` to an explicit reviewed dependency with exact pin + `uv lock` update.

## Commands run

```bash
python3 -m pytest tests/tools/test_activity_plan_tool.py -q --tb=short
# RED evidence before implementation: failed with ImportError for missing tools.activity_plan_tool.
```

```bash
python3 -m pytest tests/tools/test_activity_plan_tool.py -q --tb=short
# After implementation: 6 passed in 0.44s
```

```bash
python3 -m pytest tests/tools/test_activity_plan_tool.py tests/tools/test_activity_tool.py -q --tb=short
# 18 passed in 0.83s
```

```bash
python3 - <<'PY'
from tools.activity_plan_tool import activity_plan_create, activity_plan_apply, activity_next_actions, activity_detect_from_text, activity_recurrence_expand
import json
print('import ok')
print(json.loads(activity_recurrence_expand(rrule_text='FREQ=WEEKLY;BYDAY=MO,WE,FR;COUNT=3', from_date='2026-06-01T09:00:00+00:00', count=3))['instances'])
print(json.loads(activity_detect_from_text(text='Call @ana about #Qrovia next Friday at 3pm every week #vip', reference_now='2026-06-01T10:00:00+00:00'))['detected_activities'][0]['uncertainty'])
PY
# import ok
# ['2026-06-01T09:00:00+00:00', '2026-06-03T09:00:00+00:00', '2026-06-05T09:00:00+00:00']
# []
```

```bash
python3 - <<'PY'
from tools import activity_plan_tool  # noqa: F401
from tools.registry import registry
for name in ['activity_complete_with_next_actions','activity_detect_from_text','activity_recurrence_expand']:
    print(name, 'registered=', registry.get_entry(name) is not None)
PY
# activity_complete_with_next_actions registered= True
# activity_detect_from_text registered= True
# activity_recurrence_expand registered= True
```

```bash
python3 -m py_compile tools/activity_tool.py tools/activity_plan_tool.py tests/tools/test_activity_plan_tool.py
# exit code 0
```

## Acceptance criteria mapping

1. Activity plans support reusable sequences with step timing and assignment defaults.
   - Evidence: `activity_plan_create` normalizes `relative_after_days -> offset_seconds`; step metadata stores `default_assignee_id`/labels; `activity_plan_apply` propagates metadata and assignee into generated activities.
   - Tests: `test_activity_plan_create_accepts_reusable_steps_and_assignment_defaults`, `test_activity_plan_apply_creates_activities_with_step_due_dates`.

2. Completing an activity can suggest or trigger a next activity according to plan/chaining configuration.
   - Evidence: `activity_complete_with_next_actions` completes via Activity Core and returns `activity_next_actions` for linked activities + active plan run steps.
   - Tests: `test_activity_complete_can_return_plan_and_chain_next_actions`.

3. Natural-language quick capture supports due dates, recurrence, person/project refs and labels with clear uncertainty handling.
   - Evidence: `activity_detect_from_text` parses explicit due date phrases, recurrence (`every day/week/month`), `@person`, inferred `call/follow up with Person`, uppercase `#Project` refs, lowercase labels, and `uncertainty` markers (`due_at_uncertain`, `due_at_missing`, `time_uncertain`).
   - Tests: `test_activity_detect_from_text_extracts_due_recurrence_refs_labels_and_uncertainty`, `test_activity_detect_from_text_reports_uncertain_due_date`.

## Files changed in this increment

- `tools/activity_plan_tool.py`
- `tools/activity_tool.py`
- `toolsets.py`
- `tests/tools/test_activity_plan_tool.py`
- `tests/tools/test_activity_tool.py`
- `factory/projects/agent-core-followup-reminders/F7_EVIDENCE.md`

## Notes / risks

- The repo already had many pre-existing modified/untracked files from prior increments. This increment only touched the files listed above.
- Full live Agent Core DB smoke was not run from this worker because Factory rules prohibit ad-hoc direct writes to `factory.*`; F7 unit tests use monkeypatched Agent Core SQL boundaries and import/registry smoke.

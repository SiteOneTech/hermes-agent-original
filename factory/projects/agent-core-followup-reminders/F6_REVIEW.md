# F6_REVIEW — Calendar bridge and deterministic reminder dispatcher

Reviewer: devops-release
Run type: review
Task: agent-core-followup-reminders-f6-calendar-bridge-and-deterministic-rem
Source of truth checked: Agent Core Postgres factory.* via `hermes factory status agent-core-followup-reminders --json`

## Verdict

STATE: DONE

F6 can be closed from the increment-review perspective. The three acceptance criteria are satisfied by implementation artifacts and verified tests. The remaining `status=running` despite `finished_at` and `evidence_status=present` is operational reconciliation drift, not a blocker for the F6 code/artifact review.

## Acceptance criteria review

1. Activities can link to calendar events/blocks through generic calendar tools when time blocking is needed.
   - Verified in `tools/activity_tool.py`: `_handle_activity_to_calendar_event` reads `activity.activities`, calls `calendar_tool.calendar_create_event` or `calendar_tool.calendar_block_time`, creates `activity.activity_links` via `activity_link`, and audits `calendar_requested` / `calendar_linked` / `calendar_failed`.
   - Verified by tests: `test_activity_to_calendar_event_creates_event_and_calendar_link`.

2. Non-calendar reminders do not force calendar event creation.
   - Verified in `tools/activity_tool.py`: `_calendar_required()` only returns true for explicit `calendar_required`, metadata `calendar_required`/`time_block_required`, or activity types `meeting`/`call`; otherwise handler returns `status="skipped"` without calling calendar.
   - Verified by tests: `test_activity_to_calendar_event_skips_non_calendar_reminders`.

3. A deterministic reminder scan/dispatcher path exists with audited outputs and no reliance on chat memory.
   - Verified in `cron/activity_dispatcher.py`: `run_dispatcher_scan(owner_id=None, limit=50, dry_run=False)` queries Agent Core SQL for due/upcoming activities, reminder rules and recurrence rules; returns JSON outputs with `action_status="notification_ready"`; writes audit events when not dry-run; does not use chat/session memory.
   - Verified in `tools/activity_tool.py`: `activity_dispatcher_scan` delegates to `cron.activity_dispatcher.run_dispatcher_scan(...)`, including `dry_run`, avoiding a parallel unaudited path.
   - Verified by tests: `tests/cron/test_activity_dispatcher.py` and `test_activity_dispatcher_scan_tool_delegates_to_deterministic_dispatcher`.

## Commands run

```bash
cd /home/jean/Projects/hermes-agent-original

git status --short && git branch --show-current && git log --oneline -5
hermes factory status agent-core-followup-reminders --json
python3 -m py_compile tools/activity_tool.py cron/activity_dispatcher.py
python3 -m pytest tests/tools/test_activity_tool.py tests/tools/test_calendar_tool.py tests/cron/test_activity_dispatcher.py -q
python3 - <<'PY'
from tools import activity_tool
from tools.registry import registry
names = registry.get_tool_names_for_toolset('activity')
required = {'activity_to_calendar_event','activity_dispatcher_scan'}
print({'required_present': required <= set(names), 'activity_tool_count': len(names), 'required': sorted(required), 'names': names})
PY
```

## Results

- `py_compile`: OK for `tools/activity_tool.py` and `cron/activity_dispatcher.py`.
- Pytest subset: `17 passed in 0.87s`.
- Tool registry readback: `required_present=True`, `activity_tool_count=16`, required tools present: `activity_dispatcher_scan`, `activity_to_calendar_event`.
- Factory DB readback:
  - `db_backend=agent_core_postgres`
  - `database=zeus_agent`
  - F6 `status=running`
  - F6 `evidence_status=present`
  - F6 `finished_at=2026-06-06T04:57:15.35453+00:00`
  - F6 reviewer profile: `devops-release`
  - Existing gates for F6 include implementation passed gates 179 and 180.

## Risks / carry-forward

- Live dry-run against local `agent-postgres` remains blocked by missing local role `activity_runtime`, already documented in `F6_EVIDENCE.md`. I did not apply DB grants/migrations because this review is not authorized for direct `factory.*` writes or runtime DB changes. This belongs to F9/live smoke or controlled runtime reconciliation.
- Factory DB task status drift remains: F6 is still `running` although evidence is present and `finished_at` exists. Reconciliation should move task state to done through the orchestrator/runtime path.

## Decision

No implementation blocker found for F6. Close F6 and proceed only after the orchestrator/runtime reconciles task status from `running` to `done`.

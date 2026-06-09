# Security Review — Factory Runtime Evolution

## Scope reviewed

- Blocker classification and human question creation.
- Watchdog alert payload and suppression.
- Dispatcher claim behavior for projects in `blocked` status.
- Factory DB metadata/doc/Notion reconciliation.

## Findings

### SR-001 — Alert payloads must not include raw logs

**Status:** Pass

The watchdog emits concise alert messages and IDs. It does not dump worker logs or secrets.

### SR-002 — Human questions must be minimal

**Status:** Pass

`record_factory_blocker_actions()` creates one deterministic question per indispensable blocker using task/project IDs and recommended action.

### SR-003 — Blocked dispatch must not bypass dependency checks

**Status:** Pass

The dispatcher includes `blocked` projects in claim predicates, but `_next_runnable_task()` still checks dependencies against terminal task states and active/in-flight guards.

### SR-004 — Orphan repair must not interrupt live workers

**Status:** Pass

`_repair_orphan_in_flight_tasks()` only repairs rows with no queued/running `factory.task_runs` row.

### SR-005 — Notion credential handling

**Status:** Pass pending final Notion write

Notion key is read from environment. It is not written to repo artifacts or output.

## Verdict

GREEN after Notion page creation succeeds and Factory DB metadata links the page.

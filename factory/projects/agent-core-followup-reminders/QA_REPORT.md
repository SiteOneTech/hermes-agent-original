# QA Report — Agent Core Follow-up / Reminders

## Current report scope

Kickoff artifact QA only. Full product QA is assigned to F9 after implementation.

## Checks expected after this correction

- `hermes factory status agent-core-followup-reminders --json` returns `db_backend=agent_core_postgres`.
- Project-local artifacts under `factory/projects/agent-core-followup-reminders/` mention the correct project and no unrelated customer-service project.
- `SKILL.md` exists in every project worker/reviewer profile needed for F0-F11.
- Targeted Factory tests and web build pass after repository changes.

## Product QA pending

- Unit tests for migrations/tools.
- Direct handler smoke: create synthetic contact/activity/reminder/plan, list due/upcoming, complete/snooze/reschedule, read timeline, verify DB readback.
- Negative tests for duplicate prevention and invalid input.
- Calendar bridge smoke with synthetic calendar event where applicable.

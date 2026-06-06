# F4_EVIDENCE — DB migrations and runtime grants for activity layer

## Run

- Project: `agent-core-followup-reminders`
- Task: `agent-core-followup-reminders-f4-db-migrations-and-runtime-grants-for-`
- Initial implementation run: `run-1780714503-b487c761`
- Rework verification run: `run-1780715854-587fb3e2`
- Profile: `claude-builder`
- Last verified UTC: `2026-06-06T03:19:06Z`
- Source of truth: Agent Core Postgres `factory.*`; repo artifacts are implementation evidence.
- Factory gate evidence: implementation gate reviewed by independent `codex-builder` and passed, `gate_id=174` and `gate_id=175`; rework verification recorded as `gate_id=176`; earlier pending gate `gate_id=173` is superseded.

## Scope implemented

Files changed for F4:

- `db/modules/activity/000001_activity_schema.sql`
  - Creates `activity` schema.
  - Registers module in `agent_core.modules` and `agent_core.module_databases` with `connection_role='activity_runtime'`.
  - Creates/ensures `activity_runtime` role shell.
  - Adds canonical Universal Activity Layer tables:
    - `activity.activities`
    - `activity.activity_links`
    - `activity.reminder_rules`
    - `activity.activity_events`
    - `activity.activity_plans`
    - `activity.activity_plan_steps`
    - `activity.activity_plan_runs`
    - `activity.activity_plan_run_steps`
    - `activity.recurrence_rules`
    - `activity.recurrence_instances`
  - Adds indexes for active dedupe, due/today/upcoming/overdue owner queries, dispatcher scans, source refs, relation graph traversal, reminder scans, audit idempotency, plan/run lookups, recurrence scans, full-text search, and JSONB metadata/evidence.
  - Grants least-privilege runtime access to `activity_runtime` and read-only access to `agent_runtime`.
- `db/agent-core/000002_runtime_roles.sql`
  - Adds `activity_runtime` to canonical Agent Core runtime role shells and Agent Core registry read grants.

## Acceptance criteria mapping

1. Versioned migration adds universal activities/links/reminders/plans/audit/recurrence structures as approved by ADR.
   - Evidence: `db/modules/activity/000001_activity_schema.sql` creates all ten approved tables and the ADR-approved checks/indexes.
2. Runtime grants/roles and module registry are updated using existing Agent Core patterns.
   - Evidence: module registry inserts/updates are in `db/modules/activity/000001_activity_schema.sql`; central role shell is updated in `db/agent-core/000002_runtime_roles.sql`; runtime grants are included in the activity migration.
3. Existing CRM tables and `crm.follow_ups` remain compatible; migration is idempotent.
   - Evidence: Docker Postgres verification below applied CRM migrations first, then applied activity migration twice, and read back unchanged `crm.follow_ups` columns.

## Verification commands and results

### Rework verification — Docker Postgres migration apply/idempotency smoke

Command run from `/home/jean/Projects/hermes-agent-original` during `run-1780715854-587fb3e2`:

```bash
set -euo pipefail
NAME="activity-migration-rework-$$"
cleanup() { docker rm -f "$NAME" >/dev/null 2>&1 || true; }
trap cleanup EXIT

docker run --rm -d --name "$NAME" -e POSTGRES_PASSWORD=*** -e POSTGRES_DB=zeus_agent -v "$PWD:/repo:ro" postgres:16-alpine >/dev/null
# wait for pg_isready, then apply:
# db/agent-core/000001_init.sql
# db/agent-core/000002_runtime_roles.sql
# db/modules/crm/000001_crm_schema.sql
# db/modules/crm/000003_business_crm_and_adapters.sql
# db/modules/activity/000001_activity_schema.sql
# db/modules/activity/000001_activity_schema.sql
```

Result: exit code `0`.

Key rework readback:

```text
module   | schema_name | connection_role  | migration_role | project
activity | activity    | activity_runtime | agent_admin    | agent-core-followup-reminders

activity_tables
10

table_name                 | column_count
activities                 | 26
activity_events            | 13
activity_links             | 14
activity_plan_run_steps    | 7
activity_plan_runs         | 9
activity_plan_steps        | 12
activity_plans             | 9
recurrence_instances       | 7
recurrence_rules           | 11
reminder_rules             | 14

Verified indexes include:
idx_activity_activities_active_dedupe
idx_activity_activities_due_open
idx_activity_activities_metadata_gin
idx_activity_activities_overdue
idx_activity_activities_owner_next_scan
idx_activity_activities_owner_status_due
idx_activity_activities_today_due
idx_activity_events_idempotency
idx_activity_links_relation_activity
idx_activity_links_target_relation
idx_activity_recurrence_rules_next_occurrence
idx_activity_reminder_rules_next_fire

grantee          | privilege_type | grants
activity_runtime | DELETE         | 10
activity_runtime | INSERT         | 10
activity_runtime | SELECT         | 10
activity_runtime | UPDATE         | 10
agent_runtime    | SELECT         | 10
```

CRM compatibility readback after applying CRM migrations before Activity and applying Activity twice:

```text
crm.follow_ups columns remain 12:
follow_up_id bigint
organization_id text
contact_id text
opportunity_id text
due_at timestamp with time zone
summary text
status text
priority text
assignee text
metadata jsonb
created_at timestamp with time zone
updated_at timestamp with time zone
```

Factory source-of-truth readback:

```text
hermes factory status --json

db_backend=agent_core_postgres
project agent-core-followup-reminders status=active methodology=hybrid
F4 task status=running evidence_status=present owner_profile=claude-builder reviewer_profile=codex-builder
implementation gates: gate_id=174 passed, gate_id=175 passed, gate_id=176 passed, reviewer=codex-builder
```

Note: Factory CLI exposes only `task create` and `gate record`; there is no allowed `task update/complete` command in this worker profile. Therefore this worker records/verifies gates and leaves task-state reconciliation to the orchestrator/runtime.

### Initial Docker Postgres migration apply/idempotency smoke

Command run from `/home/jean/Projects/hermes-agent-original`:

```bash
set -euo pipefail
NAME="activity-migration-test-$$"
cleanup() { docker rm -f "$NAME" >/dev/null 2>&1 || true; }
trap cleanup EXIT

docker run --rm -d --name "$NAME" -e POSTGRES_PASSWORD=*** -e POSTGRES_DB=zeus_agent -v "$PWD:/repo:ro" postgres:16-alpine >/tmp/activity_pg_container_id
for i in $(seq 1 40); do
  if docker exec "$NAME" pg_isready -U postgres -d zeus_agent >/dev/null 2>&1; then break; fi
  sleep 1
done
docker exec "$NAME" pg_isready -U postgres -d zeus_agent >/dev/null

for f in \
  /repo/db/agent-core/000001_init.sql \
  /repo/db/agent-core/000002_runtime_roles.sql \
  /repo/db/modules/crm/000001_crm_schema.sql \
  /repo/db/modules/crm/000003_business_crm_and_adapters.sql \
  /repo/db/modules/activity/000001_activity_schema.sql \
  /repo/db/modules/activity/000001_activity_schema.sql; do
  echo "APPLY $f"
  docker exec "$NAME" psql -v ON_ERROR_STOP=1 -U postgres -d zeus_agent -f "$f" >/dev/null
done

docker exec "$NAME" psql -v ON_ERROR_STOP=1 -U postgres -d zeus_agent -P pager=off -c "...readback queries..."
```

Result: exit code `0`.

Key readback:

```text
module   | schema_name | owner         | project
activity | activity    | agent-runtime | agent-core-followup-reminders

module   | database_name | connection_role  | migration_role
activity | zeus_agent    | activity_runtime | agent_admin

activity_tables
10

indexname
idx_activity_activities_active_dedupe
idx_activity_activities_owner_status_due
idx_activity_events_idempotency
idx_activity_links_target_relation
idx_activity_recurrence_rules_next_occurrence
idx_activity_reminder_rules_next_fire

grantee          | privilege_type | grants
activity_runtime | DELETE         | 10
activity_runtime | INSERT         | 10
activity_runtime | SELECT         | 10
activity_runtime | UPDATE         | 10
agent_runtime    | SELECT         | 10
```

CRM compatibility readback after applying CRM migrations before Activity and applying Activity twice:

```text
crm.follow_ups columns:
follow_up_id bigint
organization_id text
contact_id text
opportunity_id text
due_at timestamp with time zone
summary text
status text
priority text
assignee text
metadata jsonb
created_at timestamp with time zone
updated_at timestamp with time zone
```

## Notes / risks

- No runtime Hermes tools were implemented in F4; those belong to F5+.
- No production DB migration was applied directly from this worker. Verification used an isolated Docker Postgres container.
- Existing unrelated working-tree changes were present before this increment and were not modified.

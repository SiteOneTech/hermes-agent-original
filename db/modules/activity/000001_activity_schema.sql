-- Universal Activity Layer module schema in the shared Agent Core DB.
-- Canonical activity/reminder/plan/recurrence storage for agent-core-followup-reminders.
CREATE SCHEMA IF NOT EXISTS activity;

INSERT INTO agent_core.modules(module, description, owner, schema_name, metadata)
VALUES (
  'activity',
  'Agent Core Universal Activity Layer: follow-ups, reminders, tasks, plans, recurrence, and audited side effects.',
  'agent-runtime',
  'activity',
  '{"capability":"followup-reminders","project":"agent-core-followup-reminders"}'::jsonb
)
ON CONFLICT (module) DO UPDATE
SET description = EXCLUDED.description,
    owner = EXCLUDED.owner,
    schema_name = EXCLUDED.schema_name,
    metadata = EXCLUDED.metadata,
    updated_at = now();

INSERT INTO agent_core.module_databases(module, database_name, connection_role, migration_role, metadata)
VALUES (
  'activity',
  current_database(),
  'activity_runtime',
  'agent_admin',
  '{"option":"same-agent-db-schema","scope":"universal-activity-layer"}'::jsonb
)
ON CONFLICT (module) DO UPDATE
SET database_name = EXCLUDED.database_name,
    connection_role = EXCLUDED.connection_role,
    migration_role = EXCLUDED.migration_role,
    metadata = EXCLUDED.metadata;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'activity_runtime') THEN
    CREATE ROLE activity_runtime NOLOGIN;
  END IF;

  EXECUTE format('GRANT CONNECT ON DATABASE %I TO activity_runtime', current_database());
END
$$;

CREATE TABLE IF NOT EXISTS activity.activities (
  activity_id text PRIMARY KEY,
  activity_type text NOT NULL CHECK (activity_type IN ('task','follow_up','reminder','call','meeting','email','message','note','document','approval','custom')),
  title text NOT NULL,
  description text,
  status text NOT NULL DEFAULT 'open' CHECK (status IN ('planned','open','waiting','snoozed','done','cancelled')),
  priority text NOT NULL DEFAULT 'normal' CHECK (priority IN ('low','normal','high','urgent')),
  owner_id text NOT NULL DEFAULT 'zeus',
  assignee_id text,
  due_at timestamptz,
  start_at timestamptz,
  end_at timestamptz,
  completed_at timestamptz,
  cancelled_at timestamptz,
  snoozed_until timestamptz,
  next_scan_at timestamptz,
  source text NOT NULL DEFAULT 'agent' CHECK (source IN ('manual','agent','crm','calendar','email','whatsapp','telegram','webhook','schedule','import','test')),
  source_ref text,
  source_hash text,
  dedupe_key text,
  confidence numeric CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1)),
  evidence jsonb NOT NULL DEFAULT '{}'::jsonb,
  participants jsonb NOT NULL DEFAULT '[]'::jsonb,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_by text NOT NULL DEFAULT current_user,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CHECK (end_at IS NULL OR start_at IS NULL OR end_at >= start_at),
  CHECK (completed_at IS NULL OR status = 'done'),
  CHECK (cancelled_at IS NULL OR status = 'cancelled')
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_activity_activities_active_dedupe
  ON activity.activities(dedupe_key)
  WHERE dedupe_key IS NOT NULL AND status IN ('planned','open','waiting','snoozed');
CREATE INDEX IF NOT EXISTS idx_activity_activities_owner_status_due
  ON activity.activities(owner_id, status, due_at);
CREATE INDEX IF NOT EXISTS idx_activity_activities_due_open
  ON activity.activities(owner_id, due_at)
  WHERE status IN ('planned','open','waiting','snoozed') AND due_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_activity_activities_today_due
  ON activity.activities(owner_id, due_at)
  WHERE status IN ('planned','open','waiting','snoozed') AND due_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_activity_activities_overdue
  ON activity.activities(owner_id, due_at)
  WHERE status IN ('planned','open','waiting','snoozed') AND due_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_activity_activities_owner_next_scan
  ON activity.activities(owner_id, next_scan_at)
  WHERE next_scan_at IS NOT NULL AND status IN ('planned','open','waiting','snoozed');
CREATE INDEX IF NOT EXISTS idx_activity_activities_source_ref
  ON activity.activities(source, source_ref)
  WHERE source_ref IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_activity_activities_metadata_gin
  ON activity.activities USING gin (metadata);
CREATE INDEX IF NOT EXISTS idx_activity_activities_evidence_gin
  ON activity.activities USING gin (evidence);
CREATE INDEX IF NOT EXISTS idx_activity_activities_search
  ON activity.activities USING gin (to_tsvector('simple', coalesce(title, '') || ' ' || coalesce(description, '')));

CREATE TABLE IF NOT EXISTS activity.activity_links (
  activity_link_id bigserial PRIMARY KEY,
  activity_id text NOT NULL REFERENCES activity.activities(activity_id) ON DELETE CASCADE,
  target_type text NOT NULL CHECK (target_type IN ('contact','organization','opportunity','project','document','quote','invoice','interaction','calendar_event','external_ref','activity','plan','custom')),
  target_id text NOT NULL,
  relationship_type text NOT NULL CHECK (relationship_type IN ('primary','context','participant','derived_from','next_after','blocks','blocked_by','calendar_event','duplicate_of','merged_into','legacy_follow_up','source_ref')),
  target_schema text,
  target_table text,
  provider text,
  external_type text,
  external_id text,
  external_url text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  created_by text NOT NULL DEFAULT current_user,
  UNIQUE (activity_id, target_type, target_id, relationship_type)
);

CREATE INDEX IF NOT EXISTS idx_activity_links_target_relation
  ON activity.activity_links(target_type, target_id, relationship_type);
CREATE INDEX IF NOT EXISTS idx_activity_links_relation_activity
  ON activity.activity_links(relationship_type, activity_id);
CREATE INDEX IF NOT EXISTS idx_activity_links_metadata_gin
  ON activity.activity_links USING gin (metadata);

CREATE TABLE IF NOT EXISTS activity.reminder_rules (
  reminder_rule_id text PRIMARY KEY,
  activity_id text NOT NULL REFERENCES activity.activities(activity_id) ON DELETE CASCADE,
  rule_type text NOT NULL CHECK (rule_type IN ('absolute','relative','recurrence','snooze','deadline')),
  trigger_at timestamptz,
  relative_to text CHECK (relative_to IS NULL OR relative_to IN ('due_at','start_at','end_at','completed_at','created_at')),
  offset_seconds integer,
  channel text CHECK (channel IS NULL OR channel IN ('cli','telegram','whatsapp','email','calendar','webhook','none')),
  enabled boolean NOT NULL DEFAULT true,
  last_fired_at timestamptz,
  next_fire_at timestamptz,
  idempotency_key text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CHECK (trigger_at IS NOT NULL OR relative_to IS NOT NULL OR next_fire_at IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_activity_reminder_rules_activity
  ON activity.reminder_rules(activity_id);
CREATE INDEX IF NOT EXISTS idx_activity_reminder_rules_next_fire
  ON activity.reminder_rules(enabled, next_fire_at)
  WHERE enabled = true AND next_fire_at IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_activity_reminder_rules_idempotency
  ON activity.reminder_rules(idempotency_key)
  WHERE idempotency_key IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_activity_reminder_rules_metadata_gin
  ON activity.reminder_rules USING gin (metadata);

CREATE TABLE IF NOT EXISTS activity.activity_events (
  event_id bigserial PRIMARY KEY,
  activity_id text REFERENCES activity.activities(activity_id) ON DELETE SET NULL,
  event_type text NOT NULL CHECK (event_type IN ('created','updated','completed','cancelled','snoozed','rescheduled','linked','unlinked','dedupe_hit','calendar_requested','calendar_linked','calendar_failed','reminder_due','reminder_dispatched','recurrence_materialized','plan_applied','detection_suggested','detection_persisted','security_blocked')),
  actor text NOT NULL DEFAULT current_user,
  source text,
  source_ref text,
  idempotency_key text,
  previous_state jsonb NOT NULL DEFAULT '{}'::jsonb,
  new_state jsonb NOT NULL DEFAULT '{}'::jsonb,
  side_effect jsonb NOT NULL DEFAULT '{}'::jsonb,
  result_status text NOT NULL DEFAULT 'recorded' CHECK (result_status IN ('recorded','pending','succeeded','failed','blocked','skipped')),
  error text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_activity_events_idempotency
  ON activity.activity_events(idempotency_key)
  WHERE idempotency_key IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_activity_events_activity_time
  ON activity.activity_events(activity_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_activity_events_type_time
  ON activity.activity_events(event_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_activity_events_source_ref
  ON activity.activity_events(source, source_ref)
  WHERE source_ref IS NOT NULL;

CREATE TABLE IF NOT EXISTS activity.activity_plans (
  plan_id text PRIMARY KEY,
  name text NOT NULL,
  description text,
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('draft','active','paused','archived')),
  scope text CHECK (scope IS NULL OR scope IN ('personal','crm','project','tenant','custom')),
  owner_id text NOT NULL DEFAULT 'zeus',
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS activity.activity_plan_steps (
  plan_step_id text PRIMARY KEY,
  plan_id text NOT NULL REFERENCES activity.activity_plans(plan_id) ON DELETE CASCADE,
  step_order integer NOT NULL CHECK (step_order > 0),
  activity_type text NOT NULL CHECK (activity_type IN ('task','follow_up','reminder','call','meeting','email','message','note','document','approval','custom')),
  title_template text NOT NULL,
  description_template text,
  default_priority text NOT NULL DEFAULT 'normal' CHECK (default_priority IN ('low','normal','high','urgent')),
  relative_to text NOT NULL DEFAULT 'plan_start' CHECK (relative_to IN ('plan_start','previous_completed_at','activity_due_at','external_date')),
  offset_seconds integer NOT NULL DEFAULT 0,
  auto_create boolean NOT NULL DEFAULT false,
  requires_confirmation boolean NOT NULL DEFAULT false,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (plan_id, step_order)
);

CREATE TABLE IF NOT EXISTS activity.activity_plan_runs (
  plan_run_id text PRIMARY KEY,
  plan_id text NOT NULL REFERENCES activity.activity_plans(plan_id),
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('active','paused','completed','cancelled')),
  owner_id text NOT NULL DEFAULT 'zeus',
  target_type text NOT NULL,
  target_id text NOT NULL,
  started_at timestamptz NOT NULL DEFAULT now(),
  completed_at timestamptz,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  CHECK (completed_at IS NULL OR status = 'completed')
);

CREATE TABLE IF NOT EXISTS activity.activity_plan_run_steps (
  plan_run_step_id text PRIMARY KEY,
  plan_run_id text NOT NULL REFERENCES activity.activity_plan_runs(plan_run_id) ON DELETE CASCADE,
  plan_step_id text NOT NULL REFERENCES activity.activity_plan_steps(plan_step_id),
  activity_id text REFERENCES activity.activities(activity_id) ON DELETE SET NULL,
  status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','suggested','created','skipped','done','cancelled')),
  due_at timestamptz,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (plan_run_id, plan_step_id)
);

CREATE INDEX IF NOT EXISTS idx_activity_plans_owner_status
  ON activity.activity_plans(owner_id, status);
CREATE INDEX IF NOT EXISTS idx_activity_plan_steps_plan_order
  ON activity.activity_plan_steps(plan_id, step_order);
CREATE INDEX IF NOT EXISTS idx_activity_plan_runs_target
  ON activity.activity_plan_runs(target_type, target_id, status);
CREATE INDEX IF NOT EXISTS idx_activity_plan_runs_owner_status
  ON activity.activity_plan_runs(owner_id, status);
CREATE INDEX IF NOT EXISTS idx_activity_plan_run_steps_activity
  ON activity.activity_plan_run_steps(activity_id)
  WHERE activity_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_activity_plan_run_steps_due
  ON activity.activity_plan_run_steps(status, due_at)
  WHERE due_at IS NOT NULL;

CREATE TABLE IF NOT EXISTS activity.recurrence_rules (
  recurrence_rule_id text PRIMARY KEY,
  activity_id text NOT NULL REFERENCES activity.activities(activity_id) ON DELETE CASCADE,
  rrule text NOT NULL,
  timezone text NOT NULL DEFAULT 'UTC',
  dtstart timestamptz,
  until_at timestamptz,
  count_limit integer CHECK (count_limit IS NULL OR count_limit > 0),
  enabled boolean NOT NULL DEFAULT true,
  last_materialized_at timestamptz,
  next_occurrence_at timestamptz,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS activity.recurrence_instances (
  recurrence_instance_id text PRIMARY KEY,
  recurrence_rule_id text NOT NULL REFERENCES activity.recurrence_rules(recurrence_rule_id) ON DELETE CASCADE,
  activity_id text REFERENCES activity.activities(activity_id) ON DELETE SET NULL,
  occurrence_at timestamptz NOT NULL,
  status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','materialized','skipped','done','cancelled')),
  idempotency_key text NOT NULL UNIQUE,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_activity_recurrence_rules_activity
  ON activity.recurrence_rules(activity_id);
CREATE INDEX IF NOT EXISTS idx_activity_recurrence_rules_next_occurrence
  ON activity.recurrence_rules(enabled, next_occurrence_at)
  WHERE enabled = true AND next_occurrence_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_activity_recurrence_instances_rule_occurrence
  ON activity.recurrence_instances(recurrence_rule_id, occurrence_at);
CREATE INDEX IF NOT EXISTS idx_activity_recurrence_instances_status_occurrence
  ON activity.recurrence_instances(status, occurrence_at);

GRANT USAGE ON SCHEMA activity TO activity_runtime, agent_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA activity TO activity_runtime;
GRANT SELECT ON ALL TABLES IN SCHEMA activity TO agent_runtime;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA activity TO activity_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA activity GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO activity_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA activity GRANT SELECT ON TABLES TO agent_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA activity GRANT USAGE, SELECT ON SEQUENCES TO activity_runtime;

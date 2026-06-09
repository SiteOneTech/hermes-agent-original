-- Runtime orchestration state for autonomous Factory execution.
-- Agent Core Postgres remains the only Factory source of truth.

ALTER TABLE factory.projects ADD COLUMN IF NOT EXISTS autonomous_enabled boolean NOT NULL DEFAULT false;
ALTER TABLE factory.projects ADD COLUMN IF NOT EXISTS paused_at timestamptz;
ALTER TABLE factory.projects ADD COLUMN IF NOT EXISTS last_reconciled_at timestamptz;

ALTER TABLE factory.lanes ADD COLUMN IF NOT EXISTS current_increment integer;

ALTER TABLE factory.tasks ADD COLUMN IF NOT EXISTS claimed_by text;
ALTER TABLE factory.tasks ADD COLUMN IF NOT EXISTS claimed_at timestamptz;
ALTER TABLE factory.tasks ADD COLUMN IF NOT EXISTS lease_until timestamptz;
ALTER TABLE factory.tasks ADD COLUMN IF NOT EXISTS retry_count integer NOT NULL DEFAULT 0;
ALTER TABLE factory.tasks ADD COLUMN IF NOT EXISTS max_retries integer NOT NULL DEFAULT 2;
ALTER TABLE factory.tasks ADD COLUMN IF NOT EXISTS increment_key text;
ALTER TABLE factory.tasks ADD COLUMN IF NOT EXISTS increment_order integer;
ALTER TABLE factory.tasks ADD COLUMN IF NOT EXISTS last_heartbeat_at timestamptz;

CREATE TABLE IF NOT EXISTS factory.task_runs (
  run_id text PRIMARY KEY,
  task_id text NOT NULL REFERENCES factory.tasks(task_id) ON DELETE CASCADE,
  project_id text NOT NULL REFERENCES factory.projects(project_id) ON DELETE CASCADE,
  lane_id text REFERENCES factory.lanes(lane_id) ON DELETE SET NULL,
  worker_profile text NOT NULL,
  reviewer_profile text,
  engine text,
  status text NOT NULL DEFAULT 'queued',
  process_id integer,
  session_id text,
  log_path text,
  prompt_path text,
  exit_code integer,
  started_at timestamptz NOT NULL DEFAULT now(),
  heartbeat_at timestamptz NOT NULL DEFAULT now(),
  finished_at timestamptz,
  output_summary text,
  evidence jsonb NOT NULL DEFAULT '{}'::jsonb,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_factory_task_runs_project_status ON factory.task_runs(project_id, status, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_factory_task_runs_task_status ON factory.task_runs(task_id, status, started_at DESC);

CREATE TABLE IF NOT EXISTS factory.human_questions (
  question_id text PRIMARY KEY,
  project_id text NOT NULL REFERENCES factory.projects(project_id) ON DELETE CASCADE,
  task_id text REFERENCES factory.tasks(task_id) ON DELETE SET NULL,
  severity text NOT NULL DEFAULT 'normal',
  question text NOT NULL,
  options jsonb NOT NULL DEFAULT '[]'::jsonb,
  asked_via text,
  status text NOT NULL DEFAULT 'pending',
  answer text,
  created_at timestamptz NOT NULL DEFAULT now(),
  answered_at timestamptz,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_factory_human_questions_project_status ON factory.human_questions(project_id, status, created_at DESC);

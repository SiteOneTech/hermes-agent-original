-- PMV runtime-agent management flow: deployment runs, health checks, and events.
ALTER TABLE agent_management.managed_agents
  ADD COLUMN IF NOT EXISTS last_runtime_run_id text,
  ADD COLUMN IF NOT EXISTS last_health_status text,
  ADD COLUMN IF NOT EXISTS last_health_at timestamptz;

CREATE INDEX IF NOT EXISTS managed_agents_status_idx ON agent_management.managed_agents(status);
CREATE INDEX IF NOT EXISTS managed_agents_class_status_idx ON agent_management.managed_agents(agent_class, status);

CREATE TABLE IF NOT EXISTS agent_management.runtime_management_runs (
  run_id text PRIMARY KEY,
  agent_id text NOT NULL REFERENCES agent_management.managed_agents(agent_id) ON DELETE CASCADE,
  run_type text NOT NULL DEFAULT 'deploy',
  status text NOT NULL DEFAULT 'planned' CHECK (status IN ('planned', 'queued', 'provisioning', 'configuring', 'smoke_testing', 'active', 'blocked', 'failed', 'cancelled', 'completed')),
  requested_by text NOT NULL DEFAULT 'zeus',
  assigned_agent text NOT NULL DEFAULT 'Zeus Runtime Manager',
  source_session_id text REFERENCES agent_management.onboarding_sessions(session_id) ON DELETE SET NULL,
  source_report_id bigint REFERENCES agent_management.onboarding_reports(report_id) ON DELETE SET NULL,
  target_runtime_repo text NOT NULL DEFAULT 'SiteOneTech/sitiouno-agent-runtime',
  target_environment text NOT NULL DEFAULT 'sandbox' CHECK (target_environment IN ('sandbox', 'staging', 'production')),
  plan jsonb NOT NULL DEFAULT '{}'::jsonb,
  checklist jsonb NOT NULL DEFAULT '[]'::jsonb,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS runtime_management_runs_agent_idx ON agent_management.runtime_management_runs(agent_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS runtime_management_runs_status_idx ON agent_management.runtime_management_runs(status, updated_at DESC);
CREATE INDEX IF NOT EXISTS runtime_management_runs_source_session_idx ON agent_management.runtime_management_runs(source_session_id);

CREATE TABLE IF NOT EXISTS agent_management.runtime_health_checks (
  check_id bigserial PRIMARY KEY,
  agent_id text NOT NULL REFERENCES agent_management.managed_agents(agent_id) ON DELETE CASCADE,
  status text NOT NULL DEFAULT 'unknown' CHECK (status IN ('healthy', 'degraded', 'unreachable', 'unknown')),
  checked_by text NOT NULL DEFAULT 'Supervisor Agent',
  health jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS runtime_health_checks_agent_idx ON agent_management.runtime_health_checks(agent_id, created_at DESC);
CREATE INDEX IF NOT EXISTS runtime_health_checks_status_idx ON agent_management.runtime_health_checks(status, created_at DESC);

CREATE TABLE IF NOT EXISTS agent_management.runtime_management_events (
  event_id bigserial PRIMARY KEY,
  agent_id text NOT NULL REFERENCES agent_management.managed_agents(agent_id) ON DELETE CASCADE,
  run_id text REFERENCES agent_management.runtime_management_runs(run_id) ON DELETE SET NULL,
  actor text NOT NULL DEFAULT 'zeus',
  event_type text NOT NULL,
  status_from text,
  status_to text,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS runtime_management_events_agent_idx ON agent_management.runtime_management_events(agent_id, created_at DESC);
CREATE INDEX IF NOT EXISTS runtime_management_events_run_idx ON agent_management.runtime_management_events(run_id, created_at DESC);
CREATE INDEX IF NOT EXISTS runtime_management_events_type_idx ON agent_management.runtime_management_events(event_type, created_at DESC);

GRANT SELECT ON ALL TABLES IN SCHEMA agent_management TO agent_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA agent_management TO agent_management_runtime;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA agent_management TO agent_management_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA agent_management GRANT SELECT ON TABLES TO agent_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA agent_management GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO agent_management_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA agent_management GRANT USAGE, SELECT ON SEQUENCES TO agent_management_runtime;

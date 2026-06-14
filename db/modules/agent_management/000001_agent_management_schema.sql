-- Zeus Runtime Agent Management Core schema in the shared Agent Core DB.
CREATE SCHEMA IF NOT EXISTS agent_management;

INSERT INTO agent_core.modules(module, description, owner, schema_name)
VALUES ('agent_management', 'Zeus control-plane records for runtime agents, onboarding sessions, class packs, readiness, and support workflows.', 'zeus', 'agent_management')
ON CONFLICT (module) DO UPDATE SET updated_at = now();

INSERT INTO agent_core.module_databases(module, database_name, connection_role, migration_role, metadata)
VALUES ('agent_management', current_database(), 'agent_management_runtime', 'agent_admin', '{"scope":"zeus_control_plane"}'::jsonb)
ON CONFLICT (module) DO UPDATE SET database_name=EXCLUDED.database_name, connection_role=EXCLUDED.connection_role, metadata=EXCLUDED.metadata;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'agent_management_runtime') THEN
    CREATE ROLE agent_management_runtime NOLOGIN;
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS agent_management.agent_classes (
  class_id text PRIMARY KEY,
  display_name text NOT NULL,
  description text,
  feature_packs jsonb NOT NULL DEFAULT '[]'::jsonb,
  required_secrets jsonb NOT NULL DEFAULT '[]'::jsonb,
  required_onboarding_fields jsonb NOT NULL DEFAULT '[]'::jsonb,
  actuation_playbook jsonb NOT NULL DEFAULT '{}'::jsonb,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS agent_management.managed_agents (
  agent_id text PRIMARY KEY,
  display_name text NOT NULL,
  client_name text,
  owner_name text,
  owner_contact text,
  business_name text,
  agent_class text REFERENCES agent_management.agent_classes(class_id),
  status text NOT NULL DEFAULT 'planned',
  vm_hostname text,
  tailscale_ip text,
  public_domain text,
  private_dashboard_url text,
  infisical_project_id text,
  runtime_repo text,
  runtime_version text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS agent_management.onboarding_sessions (
  session_id text PRIMARY KEY,
  agent_id text REFERENCES agent_management.managed_agents(agent_id) ON DELETE SET NULL,
  client_name text NOT NULL,
  client_contact text,
  agent_class text REFERENCES agent_management.agent_classes(class_id),
  status text NOT NULL DEFAULT 'intake_active',
  deploy_authorized_by text NOT NULL,
  payment_reference text,
  source_channel text NOT NULL DEFAULT 'chat',
  form_data jsonb NOT NULL DEFAULT '{}'::jsonb,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS onboarding_sessions_agent_idx ON agent_management.onboarding_sessions(agent_id);
CREATE INDEX IF NOT EXISTS onboarding_sessions_status_idx ON agent_management.onboarding_sessions(status);
CREATE INDEX IF NOT EXISTS onboarding_sessions_class_idx ON agent_management.onboarding_sessions(agent_class);

CREATE TABLE IF NOT EXISTS agent_management.onboarding_events (
  event_id bigserial PRIMARY KEY,
  session_id text NOT NULL REFERENCES agent_management.onboarding_sessions(session_id) ON DELETE CASCADE,
  actor text NOT NULL,
  event_type text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  source_channel text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS onboarding_events_session_idx ON agent_management.onboarding_events(session_id, created_at DESC);

CREATE TABLE IF NOT EXISTS agent_management.onboarding_reports (
  report_id bigserial PRIMARY KEY,
  session_id text NOT NULL REFERENCES agent_management.onboarding_sessions(session_id) ON DELETE CASCADE,
  report_type text NOT NULL,
  status text NOT NULL DEFAULT 'draft',
  report jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_by text NOT NULL DEFAULT 'zeus',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(session_id, report_type)
);

CREATE INDEX IF NOT EXISTS onboarding_reports_session_idx ON agent_management.onboarding_reports(session_id);

INSERT INTO agent_management.agent_classes(class_id, display_name, description, feature_packs, required_secrets, required_onboarding_fields, actuation_playbook, metadata)
VALUES
  (
    'generic_smb',
    'Agente SMB general',
    'Default runtime agent for SMB/freelancer operations: agenda, CRM, quotes, invoices, notifications, and follow-ups.',
    '["crm", "calendar", "quotes", "invoices", "notifications", "followups"]'::jsonb,
    '["SENDGRID_API_KEY"]'::jsonb,
    '["business.name", "business.description", "business.country", "owner.name", "owner.primary_channel", "proposal_feedback.liked", "proposal_feedback.buying_reason", "operations.current_process", "operations.top_pain_points", "agent_expectations.main_jobs"]'::jsonb,
    '{"first_week":"agent-guided activation with Sophie and Customer Success Agent"}'::jsonb,
    '{"seed":"agent_management_000001"}'::jsonb
  ),
  (
    'cleaning_business',
    'Agente para servicios de limpieza',
    'Runtime agent class for cleaning/service businesses focused on lead response, quotes, scheduling, and follow-up.',
    '["crm", "calendar", "quotes", "field_service_followups", "notifications"]'::jsonb,
    '["SENDGRID_API_KEY"]'::jsonb,
    '["business.name", "business.description", "business.country", "owner.name", "owner.primary_channel", "proposal_feedback.liked", "proposal_feedback.buying_reason", "operations.current_process", "operations.top_pain_points", "agent_expectations.main_jobs"]'::jsonb,
    '{"first_week":"run quote + scheduling examples with real service requests"}'::jsonb,
    '{"seed":"agent_management_000001"}'::jsonb
  ),
  (
    'accounting_office',
    'Agente para oficina contable',
    'Runtime agent class for accounting offices focused on client intake, document reminders, calendar, and accounting-lite follow-up.',
    '["crm", "calendar", "document_intake", "accounting_lite", "notifications"]'::jsonb,
    '["SENDGRID_API_KEY"]'::jsonb,
    '["business.name", "business.description", "business.country", "owner.name", "owner.primary_channel", "proposal_feedback.liked", "proposal_feedback.buying_reason", "operations.current_process", "operations.top_pain_points", "agent_expectations.main_jobs"]'::jsonb,
    '{"first_week":"run document intake + reminder examples with real clients"}'::jsonb,
    '{"seed":"agent_management_000001"}'::jsonb
  )
ON CONFLICT (class_id) DO UPDATE SET
  display_name=EXCLUDED.display_name,
  description=EXCLUDED.description,
  feature_packs=EXCLUDED.feature_packs,
  required_secrets=EXCLUDED.required_secrets,
  required_onboarding_fields=EXCLUDED.required_onboarding_fields,
  actuation_playbook=EXCLUDED.actuation_playbook,
  updated_at=now();

GRANT CONNECT ON DATABASE zeus_agent TO agent_management_runtime;
GRANT USAGE ON SCHEMA agent_core TO agent_management_runtime;
GRANT SELECT ON ALL TABLES IN SCHEMA agent_core TO agent_management_runtime;
GRANT USAGE ON SCHEMA agent_management TO agent_runtime, agent_management_runtime;
GRANT SELECT ON ALL TABLES IN SCHEMA agent_management TO agent_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA agent_management TO agent_management_runtime;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA agent_management TO agent_management_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA agent_management GRANT SELECT ON TABLES TO agent_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA agent_management GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO agent_management_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA agent_management GRANT USAGE, SELECT ON SEQUENCES TO agent_management_runtime;

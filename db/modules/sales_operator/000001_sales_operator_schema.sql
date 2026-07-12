-- Sales Operator Core: reusable daily sales-operator module for researched GTM execution.
CREATE SCHEMA IF NOT EXISTS sales_operator;

INSERT INTO agent_core.modules(module, description, owner, schema_name)
VALUES ('sales_operator', 'Agent-native daily sales operator: campaigns, territories, lead research, gated outreach, experiments, daily reports, and CRM bridge.', 'agent-runtime', 'sales_operator')
ON CONFLICT (module) DO UPDATE SET description = EXCLUDED.description, schema_name = EXCLUDED.schema_name, updated_at = now();

INSERT INTO agent_core.module_databases(module, database_name, connection_role, migration_role, metadata)
VALUES ('sales_operator', current_database(), 'sales_operator_runtime', 'agent_admin', '{"option":"same-agent-db-schema","scope":"sales-operator-core"}'::jsonb)
ON CONFLICT (module) DO UPDATE SET database_name = EXCLUDED.database_name, connection_role = EXCLUDED.connection_role, migration_role = EXCLUDED.migration_role, metadata = EXCLUDED.metadata;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sales_operator_runtime') THEN
    CREATE ROLE sales_operator_runtime NOLOGIN;
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS sales_operator.campaigns (
  campaign_id text PRIMARY KEY,
  product_id text NOT NULL,
  product_name text NOT NULL,
  business_id text NOT NULL DEFAULT 'sitiouno',
  status text NOT NULL DEFAULT 'active',
  target_subscribers integer,
  target_deadline date,
  budget_amount numeric,
  currency text NOT NULL DEFAULT 'USD',
  referral_code text NOT NULL DEFAULT 'zeus',
  bonus_offer text,
  positioning text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sales_operator.territories (
  territory_id text PRIMARY KEY,
  campaign_id text NOT NULL REFERENCES sales_operator.campaigns(campaign_id) ON DELETE CASCADE,
  country text NOT NULL,
  city text NOT NULL,
  vertical text NOT NULL,
  status text NOT NULL DEFAULT 'planned',
  priority integer NOT NULL DEFAULT 50,
  source_notes text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (campaign_id, country, city, vertical)
);

CREATE TABLE IF NOT EXISTS sales_operator.channel_policies (
  policy_id text PRIMARY KEY,
  campaign_id text NOT NULL REFERENCES sales_operator.campaigns(campaign_id) ON DELETE CASCADE,
  channel text NOT NULL,
  status text NOT NULL DEFAULT 'draft_only',
  mode text NOT NULL DEFAULT 'draft_only',
  daily_limit integer NOT NULL DEFAULT 0,
  requires_human_approval boolean NOT NULL DEFAULT true,
  notes text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (campaign_id, channel)
);

CREATE TABLE IF NOT EXISTS sales_operator.lead_sources (
  source_id text PRIMARY KEY,
  campaign_id text NOT NULL REFERENCES sales_operator.campaigns(campaign_id) ON DELETE CASCADE,
  source_type text NOT NULL,
  source_name text NOT NULL,
  url text,
  status text NOT NULL DEFAULT 'active',
  last_scanned_at timestamptz,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sales_operator.prospects (
  prospect_id text PRIMARY KEY,
  campaign_id text NOT NULL REFERENCES sales_operator.campaigns(campaign_id) ON DELETE CASCADE,
  territory_id text REFERENCES sales_operator.territories(territory_id) ON DELETE SET NULL,
  organization_id text,
  contact_id text,
  opportunity_id text,
  name text NOT NULL,
  domain text,
  website text,
  country text,
  city text,
  vertical text,
  status text NOT NULL DEFAULT 'discovered',
  fit_score numeric,
  priority text NOT NULL DEFAULT 'normal',
  next_action text,
  next_action_at timestamptz,
  last_contact_at timestamptz,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sales_operator.research_snapshots (
  research_id bigserial PRIMARY KEY,
  prospect_id text NOT NULL REFERENCES sales_operator.prospects(prospect_id) ON DELETE CASCADE,
  source_id text REFERENCES sales_operator.lead_sources(source_id) ON DELETE SET NULL,
  summary text NOT NULL,
  pain_points jsonb NOT NULL DEFAULT '[]'::jsonb,
  public_channels jsonb NOT NULL DEFAULT '[]'::jsonb,
  comparison_arguments jsonb NOT NULL DEFAULT '[]'::jsonb,
  evidence jsonb NOT NULL DEFAULT '[]'::jsonb,
  researched_at timestamptz NOT NULL DEFAULT now(),
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS sales_operator.lead_scores (
  score_id bigserial PRIMARY KEY,
  prospect_id text NOT NULL REFERENCES sales_operator.prospects(prospect_id) ON DELETE CASCADE,
  score numeric NOT NULL,
  score_band text NOT NULL DEFAULT 'unknown',
  reasons jsonb NOT NULL DEFAULT '[]'::jsonb,
  computed_at timestamptz NOT NULL DEFAULT now(),
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS sales_operator.attack_plans (
  attack_plan_id text PRIMARY KEY,
  campaign_id text NOT NULL REFERENCES sales_operator.campaigns(campaign_id) ON DELETE CASCADE,
  prospect_id text NOT NULL REFERENCES sales_operator.prospects(prospect_id) ON DELETE CASCADE,
  plan_status text NOT NULL DEFAULT 'draft',
  primary_channel text NOT NULL DEFAULT 'email',
  message_subject text,
  message_body text NOT NULL,
  value_prop text,
  objections jsonb NOT NULL DEFAULT '[]'::jsonb,
  assets jsonb NOT NULL DEFAULT '[]'::jsonb,
  next_step text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sales_operator.outreach_queue (
  outreach_id text PRIMARY KEY,
  campaign_id text NOT NULL REFERENCES sales_operator.campaigns(campaign_id) ON DELETE CASCADE,
  prospect_id text NOT NULL REFERENCES sales_operator.prospects(prospect_id) ON DELETE CASCADE,
  attack_plan_id text REFERENCES sales_operator.attack_plans(attack_plan_id) ON DELETE SET NULL,
  channel text NOT NULL,
  status text NOT NULL DEFAULT 'draft',
  scheduled_at timestamptz,
  message_subject text,
  message_body text NOT NULL,
  requires_approval boolean NOT NULL DEFAULT true,
  approval_status text NOT NULL DEFAULT 'pending',
  provider_ref text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sales_operator.outreach_attempts (
  attempt_id bigserial PRIMARY KEY,
  outreach_id text REFERENCES sales_operator.outreach_queue(outreach_id) ON DELETE SET NULL,
  campaign_id text REFERENCES sales_operator.campaigns(campaign_id) ON DELETE CASCADE,
  prospect_id text REFERENCES sales_operator.prospects(prospect_id) ON DELETE SET NULL,
  channel text NOT NULL,
  direction text NOT NULL DEFAULT 'outbound',
  provider_status text NOT NULL DEFAULT 'recorded',
  outcome text NOT NULL DEFAULT 'unknown',
  evidence jsonb NOT NULL DEFAULT '{}'::jsonb,
  occurred_at timestamptz NOT NULL DEFAULT now(),
  notes text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS sales_operator.experiments (
  experiment_id text PRIMARY KEY,
  campaign_id text NOT NULL REFERENCES sales_operator.campaigns(campaign_id) ON DELETE CASCADE,
  name text NOT NULL,
  hypothesis text,
  status text NOT NULL DEFAULT 'planned',
  channel text,
  metric text,
  results jsonb NOT NULL DEFAULT '{}'::jsonb,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sales_operator.daily_reports (
  report_id text PRIMARY KEY,
  campaign_id text NOT NULL REFERENCES sales_operator.campaigns(campaign_id) ON DELETE CASCADE,
  report_date date NOT NULL DEFAULT current_date,
  work_summary text NOT NULL,
  discoveries jsonb NOT NULL DEFAULT '[]'::jsonb,
  actions_taken jsonb NOT NULL DEFAULT '[]'::jsonb,
  learnings jsonb NOT NULL DEFAULT '[]'::jsonb,
  blockers jsonb NOT NULL DEFAULT '[]'::jsonb,
  next_actions jsonb NOT NULL DEFAULT '[]'::jsonb,
  metrics jsonb NOT NULL DEFAULT '{}'::jsonb,
  retrospective text,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (campaign_id, report_date)
);

CREATE INDEX IF NOT EXISTS idx_sales_operator_campaigns_status ON sales_operator.campaigns(status, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_sales_operator_territories_campaign ON sales_operator.territories(campaign_id, status, priority DESC);
CREATE INDEX IF NOT EXISTS idx_sales_operator_policies_campaign ON sales_operator.channel_policies(campaign_id, channel);
CREATE INDEX IF NOT EXISTS idx_sales_operator_prospects_campaign_status ON sales_operator.prospects(campaign_id, status, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_sales_operator_prospects_org ON sales_operator.prospects(organization_id);
CREATE INDEX IF NOT EXISTS idx_sales_operator_research_prospect ON sales_operator.research_snapshots(prospect_id, researched_at DESC);
CREATE INDEX IF NOT EXISTS idx_sales_operator_scores_prospect ON sales_operator.lead_scores(prospect_id, computed_at DESC);
CREATE INDEX IF NOT EXISTS idx_sales_operator_attack_plans_prospect ON sales_operator.attack_plans(prospect_id, plan_status);
CREATE INDEX IF NOT EXISTS idx_sales_operator_outreach_status ON sales_operator.outreach_queue(campaign_id, status, scheduled_at);
CREATE INDEX IF NOT EXISTS idx_sales_operator_attempts_prospect ON sales_operator.outreach_attempts(prospect_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_sales_operator_daily_reports_campaign ON sales_operator.daily_reports(campaign_id, report_date DESC);

GRANT USAGE ON SCHEMA sales_operator TO sales_operator_runtime, sales_runtime, agent_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA sales_operator TO sales_operator_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA sales_operator TO sales_runtime;
GRANT SELECT ON ALL TABLES IN SCHEMA sales_operator TO agent_runtime;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA sales_operator TO sales_operator_runtime;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA sales_operator TO sales_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA sales_operator GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO sales_operator_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA sales_operator GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO sales_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA sales_operator GRANT SELECT ON TABLES TO agent_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA sales_operator GRANT USAGE, SELECT ON SEQUENCES TO sales_operator_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA sales_operator GRANT USAGE, SELECT ON SEQUENCES TO sales_runtime;

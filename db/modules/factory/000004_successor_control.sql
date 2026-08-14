-- FRE-025: single-writer control plane and explicit, auditable project succession.
-- This is intentionally a new migration: 000003_orchestration_runtime.sql may
-- already be present in deployed Factory databases and must never be amended.

-- One lease serializes all Factory control-plane writes (monitor/reconcile,
-- deterministic repair, succession eligibility, claim, and worker launch).
CREATE TABLE IF NOT EXISTS factory.runtime_leases (
  lease_key text PRIMARY KEY,
  holder text NOT NULL,
  acquired_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz NOT NULL,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_factory_runtime_leases_expires_at
  ON factory.runtime_leases(expires_at);

-- Explicit predecessor -> successor authority. Queue position, prose, and a
-- project pause are never sufficient to activate another project.
CREATE TABLE IF NOT EXISTS factory.project_successions (
  succession_id bigserial PRIMARY KEY,
  predecessor_project_id text NOT NULL REFERENCES factory.projects(project_id) ON DELETE CASCADE,
  successor_project_id text NOT NULL REFERENCES factory.projects(project_id) ON DELETE CASCADE,
  status text NOT NULL DEFAULT 'declared',
  authorization_metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  declared_by text NOT NULL,
  declared_at timestamptz NOT NULL DEFAULT now(),
  eligible_at timestamptz,
  dispatch_started_at timestamptz,
  activated_at timestamptz,
  activated_run_id text REFERENCES factory.task_runs(run_id) ON DELETE SET NULL,
  last_evaluated_at timestamptz,
  last_blockers jsonb NOT NULL DEFAULT '[]'::jsonb,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (successor_project_id)
);
CREATE INDEX IF NOT EXISTS idx_factory_project_successions_predecessor_status
  ON factory.project_successions(predecessor_project_id, status, declared_at);

-- Runtime grants are repeated here deliberately. Earlier deployed databases may
-- have recorded a 000003 Factory migration before the runtime-grants file was
-- present, so 000004 must make the new successor-control tables usable by the
-- least-privilege Factory runtime role without relying on a runtime DDL fallback.
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'factory_runtime') THEN
    GRANT SELECT, INSERT, UPDATE ON factory.runtime_leases TO factory_runtime;
    GRANT SELECT, INSERT, UPDATE ON factory.project_successions TO factory_runtime;
    GRANT USAGE, SELECT ON SEQUENCE factory.project_successions_succession_id_seq TO factory_runtime;
  END IF;
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'agent_runtime') THEN
    GRANT SELECT ON factory.runtime_leases TO agent_runtime;
    GRANT SELECT ON factory.project_successions TO agent_runtime;
  END IF;
END $$;

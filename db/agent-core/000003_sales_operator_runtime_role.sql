-- Runtime role shell for Sales Operator Core.
-- Password/LOGIN rotation is handled by scripts/agent_core_roles.py when the
-- optional SALES_OPERATOR_DB_RUNTIME_PASSWORD secret is present in Infisical.
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sales_operator_runtime') THEN
    CREATE ROLE sales_operator_runtime NOLOGIN;
  END IF;
END $$;

GRANT CONNECT ON DATABASE zeus_agent TO sales_operator_runtime;
GRANT USAGE ON SCHEMA agent_core TO sales_operator_runtime;
GRANT SELECT ON ALL TABLES IN SCHEMA agent_core TO sales_operator_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA agent_core GRANT SELECT ON TABLES TO sales_operator_runtime;

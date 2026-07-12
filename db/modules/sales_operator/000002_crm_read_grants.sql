-- Sales Operator dashboard/CRM bridge needs read-only CRM context.
-- Write operations still go through CRM Core tools; this module only reads CRM
-- rows linked by organization_id/contact_id/opportunity_id for supervision.
GRANT USAGE ON SCHEMA crm TO sales_runtime, sales_operator_runtime;
GRANT SELECT ON ALL TABLES IN SCHEMA crm TO sales_runtime, sales_operator_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA crm GRANT SELECT ON TABLES TO sales_runtime, sales_operator_runtime;

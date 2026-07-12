# IMPLEMENTATION_REPORT — Sales Operator Core

Date: 2026-07-12
Owner: Zeus
Product: Empleado.uno

## Delivered increment

Implemented the first working Sales Operator Core increment as an Agent Core functional module, plus a private `/user/` supervision surface for Zeus sandbox.

## Backend

- Added PostgreSQL schema `sales_operator`:
  - campaigns
  - territories
  - channel_policies
  - lead_sources
  - prospects
  - research_snapshots
  - lead_scores
  - attack_plans
  - outreach_queue
  - outreach_attempts
  - experiments
  - daily_reports
- Added migrations:
  - `db/agent-core/000003_sales_operator_runtime_role.sql`
  - `db/modules/sales_operator/000001_sales_operator_schema.sql`
  - `db/modules/sales_operator/000002_crm_read_grants.sql`
- Added runtime/tool wiring:
  - `tools/sales_operator_tool.py`
  - `toolsets.py` toolset `sales_operator`
  - `hermes_cli/agent_core_sql.py` runtime env support
  - `scripts/agent_core_db.py` migration list
  - `scripts/agent_core_roles.py` grants support
  - `scripts/zeus-sync-secrets.sh` URL derivation support
  - `runtime/agent-core-db/.env.example`

## Tools added

- `sales_operator_status`
- `sales_operator_campaign_upsert`
- `sales_operator_seed_empleado_uno`
- `sales_operator_territory_upsert`
- `sales_operator_channel_policy_upsert`
- `sales_operator_lead_source_upsert`
- `sales_operator_prospect_upsert`
- `sales_operator_research_record`
- `sales_operator_score_record`
- `sales_operator_attack_plan_upsert`
- `sales_operator_outreach_enqueue`
- `sales_operator_outreach_attempt_record`
- `sales_operator_daily_report_create`
- `sales_operator_dashboard_snapshot`

## Supervision surface

- Added `/user/sales-operator/` to the Zeus delivery sandbox private OTP surface.
- Added card in `/user/` protected dashboard.
- Added dashboard sections:
  - product/campaign hero for Empleado.uno
  - target/referral/bonus/snapshot cards
  - metric cards
  - dynamic canvas graph
  - active/planned channels
  - territories/zones
  - daily work reports and retrospective
  - CRM/prospect quick view
- Added safe snapshot exporter:
  - `scripts/runtime/export_sales_operator_dashboard.py`
  - live output: `/home/jean/zeus-runtime/delivery-sandbox/user-data/sales_operator_dashboard.json`

## Seeded active campaign

Campaign: `empleado-uno-1000-subscribers-q3-2026`

Seeded:

- product: Empleado.uno
- business: SitioUno
- referral code: `zeus`
- budget marker: `$5,000`
- stretch target: `1,000` subscribers
- early adopter offer: `50% extra credits after email-confirmed signup`
- territories:
  - Colombia / Medellín / clínicas-estética
  - Perú / Lima / restaurantes-delivery
  - Colombia / Bogotá / educación-cursos
  - México / CDMX / restaurantes-clínicas
  - Ecuador / Quito / inmobiliarias
- channel policies:
  - web_agent: active inbound
  - email: active supervised_send
  - content_platforms: active content_only
  - research_search: active research_only
  - voice_sophie: supervised supervised_send
  - whatsapp_current: draft_only
  - whatsapp_official: planned
- daily report: one current jornada documenting implementation, web comparison study, learnings, blockers and next actions.

## Live operational status

Smoke output:

```json
{"channels": 7, "reports": 1, "snapshot_file": "/home/jean/zeus-runtime/delivery-sandbox/user-data/sales_operator_dashboard.json", "snapshot_ok": true, "status_ok": true, "territories": 5}
```

## Known next increment

No real clients were contacted in this increment. The CRM quick view is live and currently shows zero contacted clients because the system has not executed a lead batch yet. Next increment should populate real prospects through public-source research, then supervised outreach.

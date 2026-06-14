---
project_id: zeus-runtime-agent-management-core
project_name: Zeus Runtime Agent Management Core
validated: yes
reviewed: yes
status: draft-ready
---

# Runtime Agent Management Flow PMV

## 1. Purpose

This PMV connects the Sophie onboarding output to Zeus's runtime-agent control plane. After Sophie completes the paid onboarding intake and generates the `zeus_build_report`, Zeus prepares a managed agent record, creates a runtime deployment/activation run, tracks lifecycle state, records runtime health, and exposes a status summary for supervision.

This is a Zeus control-plane flow exposed through the separate `agent_management_runtime` toolset. Sophie/customer-facing onboarding keeps only the Sophie-safe `agent_management` toolset. The runtime PMV does **not** give Sophie deploy authority and it does **not** collect secrets over chat. Runtime secret material remains in Infisical/runtime setup.

## 2. Entry conditions

The runtime management flow starts only when:

1. `agent_mgmt_onboarding_report_generate` produced a `zeus_build_report`.
2. The report status is `ready_for_zeus_build_review`.
3. The onboarding session is linked to a paid/deploy-authorized client.
4. Zeus or a trusted runtime manager invokes the runtime management tool.

If the report still has missing fields, runtime preparation must fail closed.

## 3. Agent Core records

The PMV extends `agent_management` with:

- `managed_agents`: canonical registry row per derived/runtime agent.
- `runtime_management_runs`: deploy/configuration/activation run per agent and environment.
- `runtime_health_checks`: health snapshots from Zeus/Supervisor/activation checks.
- `runtime_management_events`: append-only management event ledger.

The managed agent row keeps the current summary (`status`, runtime URLs/IPs, last health, last run), while run/health/event tables preserve the operational history.

## 4. Tool contract

### `agent_mgmt_agent_prepare_from_onboarding`

Input: ready onboarding `session_id`.

Actions:

1. Reads the ready `zeus_build_report`.
2. Creates/updates `managed_agents` with `status='build_ready'`.
3. Creates/updates a `runtime_management_runs` deploy run with `status='planned'`.
4. Links the onboarding session to `agent_id` and marks it `agent_prepared`.
5. Emits `agent_prepared_from_onboarding` event.

Output: managed agent, runtime run, linked session, and generated runtime management checklist.

### `agent_mgmt_runtime_status_update`

Input: `run_id`, lifecycle `status`, optional runtime details/checklist/metadata.

Allowed run statuses:

- `planned`
- `queued`
- `provisioning`
- `configuring`
- `smoke_testing`
- `active`
- `blocked`
- `failed`
- `cancelled`
- `completed`

The tool updates the run, derives the managed-agent summary status, applies safe runtime details, and emits a management event.

### `agent_mgmt_runtime_health_record`

Input: `agent_id`, health status, secret-free health JSON.

Allowed health statuses:

- `healthy`
- `degraded`
- `unreachable`
- `unknown`

The tool records a health row, updates the managed-agent last health fields, and emits a health event.

### `agent_mgmt_agent_status`

Input: `agent_id` or a linked onboarding `session_id`.

Output: managed agent summary, latest runtime run, latest health check, and recent management events.

## 5. Default activation checklist

Each prepared runtime deployment run starts with this checklist:

1. `registry_record` — create/update the registry row from Sophie/Zeus report.
2. `secret_pack_sync` — verify agent-specific Infisical project and shared pack inheritance.
3. `runtime_bootstrap` — provision/update runtime VM/profile/config from `SiteOneTech/sitiouno-agent-runtime`.
4. `channel_smoke` — validate gateway/dashboard/basic module/channel behavior.
5. `activation_handoff` — hand off to Sophie/Customer Success for guided first-week usage.

## 6. Safety boundaries

- Sophie can collect onboarding answers and generate reports through the Sophie-safe `agent_management` toolset, but runtime control operations live in the separate Zeus-only `agent_management_runtime` toolset.
- Runtime management tools reject secret-like JSON keys and redact secret-like inline text in returned rows.
- Health payloads should contain statuses, timestamps, endpoint names, and error summaries only — never API keys/tokens/passwords.
- Jean is escalated only for commercial decisions, pricing/scope exceptions, legal/financial risk, or explicit deploy authorization gaps.
- Zeus/Supervisor agents own technical remediation loops before notifying Jean.

## 7. Non-goals for this PMV

- No full VM provisioning automation yet.
- No direct Infisical project creation in this increment.
- No runtime repo propagation yet; this is Zeus control-plane source.
- No customer-facing dashboard changes.

## 8. Verification

A valid implementation must prove:

- migrations create runtime management run/health/event tables;
- Sophie-safe onboarding tools are registered in `agent_management`, while runtime-control tools are registered only in `agent_management_runtime`;
- ready-report gate fails closed when onboarding is incomplete;
- prepare flow creates managed agent + runtime run + session link;
- runtime status update rejects invalid states before DB calls;
- health record rejects secret-like payload keys;
- live smoke can prepare, update, record health, fetch status, and clean up.

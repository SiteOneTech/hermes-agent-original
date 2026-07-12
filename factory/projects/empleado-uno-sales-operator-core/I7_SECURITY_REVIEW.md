# I7_SECURITY_REVIEW — First pilot smoke for Empleado.uno

Date: 2026-07-12
Project: `empleado-uno-sales-operator-core`
Task: `empleado-uno-sales-operator-core-i7-first-pilot-smoke-for-empleado-uno`
Status: PASS for synthetic pilot-smoke/no-send scope

## Security posture

I7 intentionally proves data flow and CRM/Funnel Core bridging without contacting real businesses.

Controls verified:

- All pilot prospects use reserved `.test` domains.
- All pilot artifacts are marked as synthetic fixtures with `metadata.synthetic_pilot_fixture=true` and `metadata.not_real_business=true`.
- `metadata.external_outbound_allowed=false` is attached to generated prospects/CRM rows.
- The script never imports provider SDKs or messaging clients.
- The script records draft outreach queue rows only.
- `sales_operator.outreach_attempts` readback for I7 is `0`.
- Evidence has `external_sends=false` and `external_actions_invoked=[]`.
- The CRM follow-up summary explicitly says not to send without a channel gate.
- The first-touch attack plan is demo-only; no quote/proposal/payment link is sent.

## Role/cleanup note

`crm_runtime` intentionally has INSERT/SELECT/UPDATE but not DELETE on CRM tables. The I7 script uses `agent_admin` only for bounded cleanup of rows where `metadata->>'i7_smoke'='true'`; normal CRM row creation/readback still goes through canonical CRM handlers. This preserves least-privilege runtime behavior while keeping the one-shot smoke idempotent.

## Explicit holds remain

Still blocked unless Jean activates a separate channel/security gate:

- real outbound email send;
- WhatsApp official/current outbound;
- SMS or Vapi outbound;
- voice calls;
- social DMs/posts;
- real public-business pilot contact;
- interpreting provider ACK as customer interest.

## Security verdict

PASS for I7 scope. The increment creates operational pilot evidence and CRM follow-up data while keeping all customer-facing/outbound execution fail-closed.

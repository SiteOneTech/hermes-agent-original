# SECURITY_REVIEW — Sales Operator Core

Date: 2026-07-12
Owner: Zeus
Status: PASS / GREEN for private supervision increment; autonomous real outbound remains scoped to I6/I7

## Passed controls

- Private supervision dashboard is behind existing `/user/` OTP/session boundary.
- Unauthenticated `/user/sales-operator/` redirects to `/user/login`.
- Public delivery sandbox container does not receive DB credentials; it reads only a pre-exported safe JSON snapshot from `user-data`.
- Snapshot includes operational metrics and CRM-linked IDs/context only; no provider secrets or runtime credentials.
- Outbound execution is fail-closed by policy:
  - email: `supervised_send`
  - voice_sophie: `supervised_send`
  - whatsapp_current: `draft_only`
  - whatsapp_official: `planned`
  - content_platforms: `content_only`
  - research_search: `research_only`
- Provider ACK is recorded as evidence but not treated as customer interest.
- No fake testimonials, astroturfing, or private-channel scraping was implemented.

## Explicit HOLD gates

The following remain blocked until a later increment validates them:

- autonomous outbound sending
- WhatsApp official outbound
- high-volume email sends
- opt-out automation beyond recorded policy metadata
- paid-ads launch using inconsistent public pricing

## Security note from implementation

`agent_core_roles.py` is now green. `zeus-secrets-sync.service` regenerates `~/.hermes/runtime-secrets.env` with `AGENT_MANAGEMENT_DB_RUNTIME_USER`, `AGENT_MANAGEMENT_DB_RUNTIME_PASSWORD`, `AGENT_MANAGEMENT_DATABASE_URL`, and `AGENT_MANAGEMENT_DATABASE_URL_DOCKER` present. The transition path uses the existing synced `AGENT_DATABASE_URL`/`AGENT_DB_RUNTIME_PASSWORD` as a same-database fallback when older Infisical projects do not yet define a dedicated `AGENT_MANAGEMENT_*` secret; a dedicated Infisical value automatically wins when present.

Factory security gate `663` passed for the delivered private/supervised increment. Autonomous outbound remains a future-scope control for I6/I7, not a blocker for opening I6.

## Public pricing/content note

Two public variants were observed:

- `https://empleado.uno/` — current canonical sales copy with Básico $49.99 and Profesional $80.
- `https://www.empleado.uno/` — older/different copy/pricing.

For outbound/published campaigns, use the root `https://empleado.uno/` as canonical until redirects/content are cleaned.

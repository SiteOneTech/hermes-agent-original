# QA & Security Gates — Sales Operator Core

## Hard fails

- Sends outbound message/call without configured channel policy.
- Contacts non-public/private personal channels.
- Ignores opt-out/stop/unsubscribe.
- Creates fake organic posts/personas/testimonials.
- Logs secrets, full tokens, or provider credentials.
- Marks provider acceptance as customer interest/read/reply.
- Creates duplicate CRM follow-ups for the same next action.
- Exposes internal Hermes/Factory/tool language to prospects.

## Channel policy requirements

Each campaign must define:

- Allowed countries/cities/verticals.
- Allowed channels: email, WhatsApp, SMS, voice, social DM, community post.
- Max touches per lead and per channel.
- Local quiet hours/timezone.
- Opt-out wording and handling.
- Required source evidence for contact data.
- Whether execution is `draft_only`, `supervised_send`, or `auto_send`.

Default v1 policy: **draft_only / supervised_send**. `auto_send` requires explicit project gate.

## Data quality gates

- Every prospect research snapshot stores URL/source/timestamp.
- Uncertain inferences are labeled as uncertain.
- Dedupe by domain/phone/email/social handle when possible.
- No business is contacted twice by parallel campaigns without dedupe check.

## CRM gates

- Organization/contact/opportunity are created or reused before outreach is logged.
- Each attempt records channel, direction, provider status, message hash/summary, and next step.
- Replies update stage and stop/pause rules.

## Content gates

- Public copy must say Empleado.uno/SitioUno, not Hermes/Agent Core.
- No fake customer claims.
- No claims of Meta/OpenAI/Google partner status unless verified and wording approved.
- Demo links must be HTTPS and fetched before sharing.

## Test plan

- Unit tests for required fields and policy fail-closed.
- Unit tests for scoring numeric helpers and SQL injection rejection.
- Toolset resolution test.
- CRM bridge test with mocked DB/tool adapter.
- Live DB smoke when Agent Core is available.
- Dry-run outbound queue test proving no real send occurs by default.

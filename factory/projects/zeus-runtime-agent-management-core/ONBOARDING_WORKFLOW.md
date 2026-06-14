---
project_id: zeus-runtime-agent-management-core
project_name: Zeus Runtime Agent Management Core
validated: yes
reviewed: yes
status: draft-ready
---

# Sophie Conversational Onboarding Workflow

## 1. Purpose

After a customer pays for a SitioUno runtime agent and Jean authorizes deploy, Sophie gathers all configuration information conversationally, fills the internal onboarding form through `agent_management` tools, and generates the Zeus build report that drives runtime configuration.

This workflow is intentionally agent-first. Routine onboarding, guidance, and first-week enablement should be handled by specialized agents. Jean is only escalated for deploy authorization, pricing/commercial exceptions, legal/financial risk, or unusual customer commitments.

## 2. Entry gate

Onboarding starts only when all are true:

1. Payment is received or externally confirmed.
2. Jean/Zeus has authorized deploy for the client.
3. A target agent class/niche is selected or defaults to `generic_smb`.
4. Sophie has the customer's approved contact channel.

The tool enforces this with `agent_mgmt_onboarding_start`:

- `payment_received=true`
- `deploy_authorized_by` required
- `client_name` required

## 3. Tool-backed internal form

Sophie never stores raw secrets or performs deploy. Her job is to collect business-operational truth and keep filling a structured form:

- `agent_mgmt_onboarding_start` — create/reopen post-payment onboarding session and get the next question.
- `agent_mgmt_onboarding_form_update` — merge answers into the internal form after each meaningful response.
- `agent_mgmt_onboarding_next_prompt` — compute the next missing field and customer-facing question.
- `agent_mgmt_onboarding_report_generate` — create Zeus's internal build report.
- `agent_mgmt_actuation_plan_generate` — create post-onboarding guidance/actuation plan.

The form is JSONB in `agent_management.onboarding_sessions.form_data`, which lets Sophie collect partial answers over WhatsApp, voice, email, or Telegram without forcing a rigid web form.

## 4. Required minimum intake fields

The minimum required fields are intentionally focused on what Zeus needs to build a useful first runtime agent:

1. `business.name`
2. `business.description`
3. `business.country`
4. `owner.name`
5. `owner.primary_channel`
6. `proposal_feedback.liked`
7. `proposal_feedback.buying_reason`
8. `operations.current_process`
9. `operations.top_pain_points`
10. `agent_expectations.main_jobs`

Additional recommended sections:

- `channels`: WhatsApp, email, phone, website, social links, brand assets.
- `customers`: ideal customers, lead sources, objection patterns.
- `offers`: products/services, pricing model, quote rules, discounts.
- `calendar`: availability, booking rules, location/virtual rules.
- `documents`: proposals, invoices, contracts, onboarding PDFs.
- `payments`: accepted payment methods, Stripe needs, invoice rules.
- `boundaries`: actions the agent can do alone vs approval-required.
- `success_metrics`: what “good” means after 7/30 days.

## 5. Sophie BigTech prompt structure

### 1. Identity and role

You are **Sophie de SitioUno — Onboarding Specialist**. You speak Spanish-first unless the customer prefers another language. Your job is to gather the information needed to configure a paid SitioUno runtime agent.

### 2. Capabilities and environment

You can ask conversational questions, summarize answers, and call the `agent_management` onboarding tools. You cannot deploy infrastructure, access secrets, change pricing, promise custom scope, or bypass Jean/Zeus authorization.

### 3. Tool contract

- Call `agent_mgmt_onboarding_start` only after payment + deploy authorization are known.
- Call `agent_mgmt_onboarding_form_update` after every useful client answer.
- Call `agent_mgmt_onboarding_next_prompt` when deciding the next question.
- Call `agent_mgmt_onboarding_report_generate` only when the required minimum is complete or Zeus requests an interim report.
- Call `agent_mgmt_actuation_plan_generate` after the report, to prepare customer enablement.

### 4. Autonomy and persistence

Continue asking concise follow-up questions until the minimum form is complete. If the customer answers partially, save the partial data and ask for the missing part. Do not wait for a human unless a risk/authorization boundary appears.

### 5. Plan vs act

Plan one question at a time. Do not overwhelm the customer with a long questionnaire. Prefer natural follow-ups based on what they just said.

### 6. Guardrails and safety

- Do not collect API keys, passwords, bank credentials, or private tokens from the customer in chat.
- The tool layer rejects secret-like JSON keys and redacts secret-like inline text before report output; secrets must be configured through Infisical/runtime setup.
- If a secret is needed, note the requirement for Zeus/Infisical setup.
- Do not promise a feature as included if it was not part of the paid package.
- Treat operational requests after payment as scope/configuration data unless the agent is already live and authorized to act.

### 7. Tone and style

Warm, clear, professional, short. Sophie should sound like a capable onboarding specialist, not a technical questionnaire.

### 8. Output format

Customer-facing messages should be short and single-question when possible. Internal tool updates should be structured JSON patches only.

### 9. Memory and continuity

Persist only structured onboarding answers and operational notes in Agent Core. Do not persist secrets. Do not store temporary chat noise as durable memory.

### 10. Verification

Before generating the build report, verify the required fields are complete and the report includes: business context, what the customer liked, buying reason, current operation, desired agent jobs, channels/assets, recommended feature packs, and build sequence.

## 6. Conversational sequence

Default sequence:

1. Confirm onboarding has started because payment and deploy authorization are complete.
2. Ask what the business does.
3. Ask what the customer liked in the proposal and why they bought.
4. Ask current operational process.
5. Ask top pain points.
6. Ask what jobs the agent must handle in a normal week.
7. Ask channels and assets.
8. Ask approval boundaries.
9. Generate Zeus build report.
10. Generate actuation plan.

Example customer-facing opening:

```text
Hola, soy Sophie de SitioUno. Como ya está aprobado el inicio de tu agente, voy a levantar la información para configurarlo bien. Primero: cuéntame en tus palabras qué hace tu negocio y qué tipo de clientes atiendes.
```

## 7. Zeus build report

The generated report contains:

- client/business identity
- commercial context: what they liked and why they bought
- current process and bottlenecks
- desired agent behavior and main jobs
- channel/assets inventory
- recommended feature packs
- required shared capabilities
- missing fields, if any
- recommended build sequence
- raw form data for audit/replay

This report is the input Zeus uses to create/update the agent registry record, class pack, secrets/readiness checklist, and runtime deployment plan. The PMV runtime management handoff is documented in `RUNTIME_MANAGEMENT_FLOW.md` and implemented through the separate Zeus-only `agent_management_runtime` toolset: `agent_mgmt_agent_prepare_from_onboarding`, `agent_mgmt_runtime_status_update`, `agent_mgmt_runtime_health_record`, and `agent_mgmt_agent_status`.

## 8. Post-onboarding actuation flow

After the build report, the actuation plan starts. Objective: the customer learns to operate through the agent without a human onboarding rep.

Phases:

1. **Orientation** — Sophie explains how to speak to the agent and confirms priorities.
2. **Activation smoke** — Runtime Activation Agent validates channels, identity, agenda/CRM/notifications, and first real use case.
3. **Guided first week** — Customer Success Agent proposes daily tasks and detects friction.
4. **Autonomous operation** — Supervisor Agent monitors health, tickets, usage, and exceptions.

Escalation policy:

- Zeus handles technical/runtime blockers and build configuration decisions.
- Jean is escalated only for commercial decisions, deployment authorization, pricing outside policy, or sensitive risk.
- Customer education is handled by Sophie/Customer Success, not by Jean.

## 9. Non-goals

- No public customer dashboard is required for onboarding PMV.
- No deploy automation is performed by Sophie.
- No secret collection over chat.
- No human intervention for routine usage guidance.

## 10. Verification

A valid implementation must prove:

- `agent_management` schema exists.
- onboarding tools are registered in `toolsets.py`.
- required-field detection works.
- form updates merge without overwriting unrelated answers.
- report generation includes Zeus build sections.
- actuation plan enforces agent-first support with exception escalation only.

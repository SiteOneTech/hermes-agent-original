# Factory Intake — Funnel Core / CRM Sales Workflow

**Project ID:** `funnel-core-crm-workflow`
**Methodology:** Hybrid Factory
**Source of truth:** Agent Core Postgres `factory.*`
**Repo:** `/home/jean/Projects/hermes-agent-original`
**Branch:** `factory/funnel-core-crm-workflow/inc-001-client-requirement-implement-gen`
**Human owner:** Jean García
**Orchestrator:** Zeus

---

## Trigger

Jean requested a generic Funnel Core / CRM Sales Workflow as a reusable Sales module for the SitioUno agent ecosystem. The deliverable is an agent-core-inheritable functionality pattern that can be wired into any CRM adapter (Twenty, HubSpot, Salesforce, etc.) via the `zeus_then_runtime` runtime inheritance model.

## Scope

- Design a generic Sales Funnel core module with: lead capture, qualification, proposal, negotiation, closing, and post-sale stages.
- Expose the funnel as a state machine with deterministic transitions.
- Provide adapter contracts so any CRM backend can implement the funnel.
- Implement a reference adapter for a generic CRM (Twent, HubSpot, or similar).
- Include QA gates and delivery report.
- Document the methodology and architecture.

## Non-goals

- Do not build a full custom CRM from scratch.
- Do not implement payment processing (handled by separate HubFintech module).
- Do not implement multi-tenant isolation (future scope).
- Do not expose internal reasoning in customer-facing surfaces.

## Success criteria

- Funnel core is agent-inheritable via `zeus_then_runtime` pattern.
- Adapter contracts allow any CRM to implement the funnel.
- All gates (spec, implementation, quality, test) pass with evidence.
- Required Factory methodology docs exist in `factory/projects/funnel-core-crm-workflow/`.
- Reconciliation shows no missing docs anomalies.
- Delivery report exists with evidence of smoke/tests.

---

*factory-reporter · R2 · 2026-06-09*

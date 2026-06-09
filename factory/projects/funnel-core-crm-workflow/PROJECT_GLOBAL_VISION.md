# Project Global Vision — Funnel Core / CRM Sales Workflow

## Objective

Create a reusable, agent-inheritable Sales Funnel module for the SitioUno agent ecosystem that works with any CRM backend via adapter protocol.

## Current Phase

**F4 — QA, Delivery, Reconciliation**

The core implementation is complete (F1-F3). Current work is completing Factory methodology documentation (R2) and verifying delivery completeness (R5).

## Architecture

- **FunnelCore** (Zeus): generic sales funnel state machine with 7 stages and deterministic transitions.
- **CRMFunnelAdapter** (protocol): interface contract between FunnelCore and any CRM backend.
- **Twenty adapter** (reference): first CRM adapter implementing the protocol.

## Next Increment

Extend the funnel with:
- Deal value tracking and pipeline metrics.
- Additional CRM adapters (HubSpot, Salesforce).
- Webhook support for real-time CRM sync.

## Repository / Worktree

- **Repo:** `/home/jean/Projects/hermes-agent-original`
- **Branch:** `factory/funnel-core-crm-workflow/inc-001-client-requirement-implement-gen`
- **Worktree:** Isolated per methodology lane

## Key Decisions (ADRs)

1. Agent-inheritable via `zeus_then_runtime` pattern.
2. Deterministic state machine for predictable pipeline behavior.
3. Adapter protocol isolation — FunnelCore never imports CRM-specific code.
4. Twenty CRM as reference adapter.

---
project_id: zeus-runtime-agent-management-core
project_name: Zeus Runtime Agent Management Core
validated: yes
reviewed: yes
status: draft-ready
---

# PRD — Zeus Runtime Agent Management Core

## Problem
Runtime agents are becoming the commercial unit of SitioUno. Without a Zeus management core, each new agent risks being created by manual scripts, copied secrets, inconsistent capabilities, and weak operational visibility.

## Goal
Create a robust, automated core where Zeus can onboard, configure, deploy, monitor, supervise, and support runtime agents as a service.

## PMV outcome
A first production-shaped capability exists: runtime agents can inherit a shared operational secret pack from Infisical, while preserving per-agent overrides and isolation. SendGrid email capability becomes part of the base pack.

## Users
- Jean/Zeus as platform operator.
- Runtime agent owners such as Carlos/Bael.
- Future client/niche agents sold as service.

## Core modules roadmap
1. Agent registry and ownership metadata.
2. Agent class/niche packs.
3. Secret pack inheritance and override management.
4. Onboarding workflow.
5. VM infra deploy/provisioning.
6. Build/deploy automation.
7. Monitoring and supervision.
8. Zeus dashboard for agents.
9. Ticket ingestion/management from runtime agents.

## Future scope — Sofi Onboarding Live

`SOFI_ONBOARDING_LIVE_BRIEF.md` defines the next onboarding product layer: Sofi calls the new client, sends a secure SMS link, guides the session by voice, updates a visual web onboarding template in real time, generates an internal briefing, and later calls back to guide channel activation. This future scope stays on activation hold until Jean explicitly authorizes Factory execution.

## PMV acceptance criteria
- Factory project created and documented.
- Runtime repo contains implementation and tests for shared-secret pack inheritance.
- Shared keys support per-agent override.
- SendGrid is documented as first shared operational key.
- No secret values are committed or printed.

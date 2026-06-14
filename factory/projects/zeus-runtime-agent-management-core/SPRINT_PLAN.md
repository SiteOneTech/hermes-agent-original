---
project_id: zeus-runtime-agent-management-core
project_name: Zeus Runtime Agent Management Core
validated: yes
reviewed: yes
status: draft-ready
---

# Sprint Plan

## Sprint 0 — PMV foundation
- Task 1: G1 documentary pack.
- Task 2: Runtime shared secret pack inheritance MVP.
- Task 3: PMV backlog and increments for Zeus management core.

## Sprint 1 — Secret pack productionization
- Create shared Infisical project and paths.
- Grant Bael's identity read access to shared pack.
- Sync Bael and validate `notification_status`/email smoke test.
- Add drift detection: missing required shared keys per agent class.

## Sprint 2 — Agent registry, class packs, and onboarding
- Add local Agent Core schema for managed runtime agents and class manifests.
- Tools: register agent, assign class, list capabilities, report secret-pack status.
- Add Sophie post-payment onboarding intake: internal form updates, next-question prompts, Zeus build report, and actuation plan.

## Sprint 3 — Onboarding/deploy
- VM provisioning workflow.
- Runtime repo deploy version pinning.
- Nettu/Agent Core DB bootstrap.
- Channel setup checklist.

## Sprint 4 — Monitoring/supervision/tickets/dashboard
- Health snapshots.
- Runtime-to-Zeus ticket ingestion.
- Zeus dashboard/API for fleet status and tickets.

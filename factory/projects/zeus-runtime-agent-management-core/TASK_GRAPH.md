---
project_id: zeus-runtime-agent-management-core
project_name: Zeus Runtime Agent Management Core
validated: yes
reviewed: yes
status: draft-ready
---

# Task Graph

## Current PMV tasks

```text
T01 G1 documentary pack
  -> T02 Runtime shared secret pack inheritance MVP
  -> T03 Bael shared pack smoke test
  -> T04 Create shared Infisical project/access grants

T01 -> T05 Agent management core schema/design backlog
T05 -> T06 Agent class manifest MVP
T06 -> T06A Sophie post-payment onboarding form/report/actuation workflow
T06A -> T07 Runtime agent management flow PMV
T07 -> T08 Full deploy automation MVP
T08 -> T09 Monitoring/supervision/tickets/dashboard MVP

Future activation-hold scope:
S00 Sofi Onboarding Live initialization brief (this brief only; no dispatch)
  -> S01 Functional model + schema design
  -> S02 Secure link + SMS adapter
  -> S03 Customer live UI + realtime event feed
  -> S04 Sofi Onboarding prompt/profile + bounded tool contracts
  -> S05 Voice orchestration + link-open awareness
  -> S06 Structured capture + summary generation
  -> S07 Internal admin review view
  -> S08 Scheduling/reminders flow
  -> S09 Activation call + QR/instructions flow
  -> S10 End-to-end QA desktop/mobile/voice/SMS/sandbox
  -> S11 Security/privacy review
  -> S12 Delivery report + runtime propagation decision
```

## Factory DB tasks created now
- `zeus-runtime-agent-management-core-g1-documentary-pack-for-runtime-agent-ma`
- `zeus-runtime-agent-management-core-mvp-shared-runtime-secret-pack-inheritan`
- `zeus-runtime-agent-management-core-pmv-backlog-and-increments-for-zeus-agen`
- `zeus-runtime-agent-management-core-s00-sofi-onboarding-live-initialization-` — closed `done` as documentation-only initialization brief; activation still requires Jean confirmation.

## Dependency policy
Implementation can begin for T02 after T01 docs are committed and basic gates recorded. T04 requires Infisical write operations and should be performed with secret hygiene and explicit source-of-truth verification.

Sofi Onboarding Live remains in activation hold. Do not convert S01-S12 into runnable implementation tasks until Jean explicitly confirms the current Factory operation is finished and authorizes this scope.

---
project_id: zeus-runtime-agent-management-core
project_name: Zeus Runtime Agent Management Core
validated: yes
reviewed: yes
status: draft-ready
---

# Tracker

## Status summary
- G0 repo strategy: passed (`zeus_then_runtime`).
- G1 docs: draft-ready in this branch.
- Runtime shared-secret MVP: merged and verified.
- Infisical shared project: pending implementation/ops task.
- Bael smoke: pending after shared project and sync implementation.
- Sophie onboarding intake: merged in `hermes-agent-original` main.
- Runtime management PMV: implementation branch in progress for managed-agent registry, deployment runs, health, and status tools.
- Sofi Onboarding Live: initialization brief added under activation hold; not started, no branch/worktree/dispatch until Jean confirms.
- Factory DB S00 planning record: `zeus-runtime-agent-management-core-s00-sofi-onboarding-live-initialization-` closed as `done` with evidence for docs-only brief capture; this is not implementation activation.

## Risks
- Shared API key blast radius if SendGrid key is abused.
- Infisical permission model/version may require API-specific access grant logic.
- Runtime sync changes must not break current Bael/derived agent secret sync.
- Existing runtime repo main checkout has unrelated dirty file; use isolated worktree only.

## Next checkpoint
After runtime management PMV: run focused tests, live Agent Core smoke, independent review, merge to `hermes-agent-original` main, then keep full deploy automation and Infisical shared-project activation as separate operational increments.

## Future activation queue
- `SOFI_ONBOARDING_LIVE_BRIEF.md` captures the full voice/SMS/web live onboarding scope for Sofi Onboarding.
- Activation condition: Jean confirms the current Factory operation is finished and explicitly asks Zeus to activate this scope.
- First runnable increment after activation should be `S01 Functional model + schema design`; do not create implementation worktrees before that confirmation.

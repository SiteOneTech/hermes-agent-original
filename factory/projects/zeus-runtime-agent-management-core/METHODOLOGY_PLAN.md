---
project_id: zeus-runtime-agent-management-core
project_name: Zeus Runtime Agent Management Core
validated: yes
reviewed: yes
status: draft-ready
---

# Methodology Plan

## Factory methodology
Use Hybrid Factory methodology with G0/G1 gates, repo-backed documentation, per-deliverable branches/worktrees, implementation review, security review, and incremental pushes.

## Project phases
1. G1 documentary readiness.
2. PMV shared secret pack implementation in runtime repo.
3. Zeus-side agent management registry/class-pack design.
4. Onboarding/deploy automation increments.
5. Monitoring/supervision/ticket/dashboard increments.

## Repo strategy
- Primary repo: `SiteOneTech/hermes-agent-original` for Zeus management core docs and future Zeus admin tools.
- Propagation repo: `SiteOneTech/sitiouno-agent-runtime` for inherited runtime capabilities such as shared secret sync.
- No new GitHub repo for this Factory project.

## Evidence rules
Every increment must include:
- changed files;
- tests/commands run;
- commit SHA;
- push status;
- risks/blockers.

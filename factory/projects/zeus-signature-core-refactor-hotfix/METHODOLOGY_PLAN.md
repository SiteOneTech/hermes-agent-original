# Methodology Plan

Project: zeus-signature-core-refactor-hotfix
Owner: Jean García / SitioUno
Created: 2026-06-12T18:09:47-04:00
Status: G1 bootstrap pack complete; implementation not started
Validated: yes — initial Zeus document consistency pass
Reviewed: yes — initial Zeus Factory orchestrator review; independent quality/security review remains a project task before delivery


## Factory Method

Use the Factory Hybrid lifecycle:

1. G0 repository strategy — completed in project metadata.
2. G1 documentation readiness — this pack.
3. Research/pattern validation — captured in `PATTERN_ANALYSIS.md`.
4. Architecture/refactor planning — `ADRS.md` and `TECHNICAL_BLUEPRINT.md`.
5. Incremental implementation tasks with independent review.
6. Security + QA gates before delivery.
7. Delivery report and runtime propagation decision.

## Worktree / Branch Discipline

- Do not implement directly on this bootstrap document commit if parallel work starts.
- Implementation lanes should use branches/worktrees under:
  - `factory/zeus-signature-core-refactor-hotfix/zeus`
  - `factory/zeus-signature-core-refactor-hotfix/bmad`
  - specific sub-branches for builder tasks if needed.
- Each implementation task must commit and push its branch; merge/push main/base only after review policy passes.

## Roles

- Product Analyst: requirements and acceptance criteria.
- Solution Architect: schema, workflow, security boundaries, UI/public/private surfaces.
- Implementation Planner: task graph and dependency sanity.
- Claude Builder: broad refactor/UI/server implementation.
- Codex Builder: bounded hotfixes/tests/reviews.
- QA Verifier: browser/PDF/mobile smoke tests.
- Security Reviewer: OTP/token/audit/privacy review.
- DevOps Release: runtime deploy and propagation readiness.

## Gates

- Intake: project and user objective captured.
- Functional: PRD/requirements accepted.
- Architecture: ADR/blueprint accepted.
- Planning: task graph/sprint plan accepted.
- Implementation: all code increments done.
- Quality/Test/Security: independent gates.
- Delivery/Critical readiness: no missing docs, tests real, artifacts committed, dashboard/runtime evidence captured.

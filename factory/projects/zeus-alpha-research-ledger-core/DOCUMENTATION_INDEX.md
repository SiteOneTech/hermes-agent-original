---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: yes
owner: factory-orchestrator
---

# DOCUMENTATION INDEX — Zeus Alpha Research Ledger Core

## Controlling status
Canonical G1 pack for the **private Zeus-side implementation** succeeding `zeus-independent-alpha-research`. It is not a Vonash implementation plan, grants no external runtime access and does not authorize market execution. Every required document carries explicit `validated` and `reviewed` status metadata plus the index matrix below. The substantive control candidate `dad375f27568c38be771fc597b579d087f034e1d` received independent exact-SHA Factory PASS evidence: specification gate 699 and security gates 706/707. It is visible on the Zeus-signed, `agent:zeus`-labeled PR [#20](https://github.com/SiteOneTech/hermes-agent-original/pull/20), which is open, non-draft, and targets `main`. This metadata-only transition records those already-completed reviews; it is not a self-approval, QA Guardian approval, merge/deploy authorization, or ALR-020 authority. Earlier Factory gate rows remain audit evidence: gates 686/687 were `REQUEST_CHANGES`; gate 695 required reconciliation of direct integration event `173433` (`b9396bcd7d14ee6f212bd0fd0609e468cecf567f` → merge `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a`); gate 697 failed because Factory/Git also showed direct integration event `173494` (`6ee8b4fdb886d0834bfbc62c7e152ee35d505e66` → merge `9f975acb0625750b8d46648766d1395c89392dca`) plus stale no-new-merge/branch-only wording. Neither direct integration is an authorized PR, QA Guardian approval, deployment, or ALR-020 authority.

| File | Purpose | Owner | Validated | Reviewed |
|---|---|---|---|---|
| `FACTORY_INTAKE.md` | mandate, boundaries, source of truth | factory-orchestrator | yes | yes |
| `G0_REPOSITORY_STRATEGY.md` | repo/scope/worktree/PR decision | solution-architect | yes | yes |
| `REQUIREMENTS_ANALYSIS.md` | R1–R10/no-authority requirements | product-analyst | yes | yes |
| `PATTERN_ANALYSIS.md` | patterns and rejected shortcuts | product-analyst | yes | yes |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | verified inputs/unknowns | solution-architect | yes | yes |
| `PRD.md` | outcome and release acceptance | product-analyst | yes | yes |
| `ADRS.md` | architectural decisions | solution-architect | yes | yes |
| `METHODOLOGY_PLAN.md` | Factory/TDD/review approach | implementation-planner | yes | yes |
| `TECHNICAL_BLUEPRINT.md` | component placement and architecture | solution-architect | yes | yes |
| `SPRINT_PLAN.md` | increments | implementation-planner | yes | yes |
| `TASK_GRAPH.md` | Factory reconciliation/reviews | implementation-planner | yes | yes |
| `TRACKER.md` | status/risk register | factory-reporter | yes | yes |
| `QA_GATES.md` | RED/GREEN, smoke and delivery gates | qa-verifier | yes | yes |
| `SECURITY_GATES.md` | security pass/fail evidence | security-reviewer | yes | yes |
| `DOCUMENTATION_INDEX.md` | entrypoint/status matrix | factory-orchestrator | yes | yes |

## Supplemental controlling artifacts
- `REQUIREMENTS_TRACEABILITY.md` maps requirements to tasks/tests/reviews.
- `DATABASE_AND_RUNTIME_CONTRACT.md` is binding for exact DB, runtime, no-egress and scheduler implementation behavior.
- `G1_REVIEW.md` records independent review findings/remediation.

## Status semantics
- `validated: yes` means the implementation-planner/local worker confirmed the file exists, is tracked, is indexed where required, and is internally consistent with this G1 contract.
- `reviewed: yes` records the independent specification/security PASS evidence for substantive candidate `dad375f27568c38be771fc597b579d087f034e1d` (Factory gates 699, 706 and 707). It does not represent self-review, a QA Guardian approval, or authorization to merge/deploy.
- A reviewed marker or the observed ALR-010-R1 base-branch merges never authorize normal implementation by themselves; the Zeus-signed `agent:zeus` PR, reconciled Factory evidence, and all later per-increment independent review/QA requirements remain binding.

## Required reading order
1. `DOCUMENTATION_INDEX.md`, `FACTORY_INTAKE.md`, `G0_REPOSITORY_STRATEGY.md`
2. `REQUIREMENTS_ANALYSIS.md`, `REQUIREMENTS_TRACEABILITY.md`, `PRD.md`, `ADRS.md`
3. `DATABASE_AND_RUNTIME_CONTRACT.md`, `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`, `SPRINT_PLAN.md`
4. `QA_GATES.md`, `SECURITY_GATES.md`, `G1_REVIEW.md`

## G1 rule
No normal implementation starts until every required G1 document is `reviewed: yes`; the three supplemental controlling artifacts must be committed and PASS-reviewed against the exact substantive candidate too. Base exposure alone is not sufficient: observed direct integrations `173433`/`173494` remain non-approval audit evidence, and a branch-only pack without a Zeus-signed `agent:zeus` PR is likewise never sufficient. This project now has the documented exact-SHA gates and PR visibility; downstream increments remain subject to their own strict TDD, independent review, QA Guardian and PR-first requirements.

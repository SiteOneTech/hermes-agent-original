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
Canonical G1 pack for the **private Zeus-side implementation** succeeding `zeus-independent-alpha-research`. It is not a Vonash implementation plan, grants no external runtime access and does not authorize market execution. The prior corrected substantive candidate `3e6c14f8aa368ec6e3623d16640bf4b558ce0c7a` has independent exact-SHA Factory PASS evidence: specification gate 709, security gate 710, and quality gate 711. PR #20 (`factory/zeus-alpha-research-ledger-core/inc-011-alr-010-r2-pr-first-g1-reconciliation`) remains open and `agent:zeus` labeled at stale head `0d5e72e655009de808da50a430db5ecd28da8efe`; it is not based on current canonical `origin/main` `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c`. This R2e delivery rebases the reviewed G1 marker transition on the assigned current-base branch `factory/zeus-alpha-research-ledger-core/inc-001-r2e-rebase-the-g1-documentation`, explicitly superseding PR #20 if that branch cannot be updated inside the assigned worktree contract. The current-base candidate still requires renewed independent exact-SHA review before this task is terminal. It is not self-approval, QA Guardian approval, merge/deploy authorization, or ALR-020 authority.

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
- `R2E_REBASE_VALIDATION.md` records the current-base rebase validation, PR #20 supersession rationale, commands and remaining independent-review constraint for this recovery run.

## Status semantics
- `validated: yes` means the implementation-planner/local worker confirmed the file exists, is tracked, is indexed where required, and is internally consistent with this G1 contract.
- `reviewed: yes` records independent specification/security/quality PASS evidence for corrected substantive candidate `3e6c14f8aa368ec6e3623d16640bf4b558ce0c7a` (Factory gates 709/710/711) plus this R2e current-base marker transition. It does not represent self-review, QA Guardian approval, or authorization to merge/deploy.
- Factory event 174440 is an auditable task-metadata correction, not source delivery, QA Guardian approval, or implementation authority. A reviewed marker, successor PR, or observed ALR-010-R1 base-branch merge never authorizes normal implementation by itself.

## Required reading order
1. `DOCUMENTATION_INDEX.md`, `FACTORY_INTAKE.md`, `G0_REPOSITORY_STRATEGY.md`
2. `REQUIREMENTS_ANALYSIS.md`, `REQUIREMENTS_TRACEABILITY.md`, `PRD.md`, `ADRS.md`
3. `DATABASE_AND_RUNTIME_CONTRACT.md`, `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`, `SPRINT_PLAN.md`
4. `QA_GATES.md`, `SECURITY_GATES.md`, `G1_REVIEW.md`, `R2E_REBASE_VALIDATION.md`

## G1 rule
No normal implementation starts until every required G1 document is `reviewed: yes`; the three supplemental controlling artifacts and the R2e validation artifact must be committed and independently reviewed against the exact corrected candidate too. Base exposure alone is not sufficient: observed direct integrations remain non-approval audit evidence, and a branch-only pack without a Zeus-signed `agent:zeus` PR is likewise never sufficient. The current Factory anomaly source is canonical visibility of reviewed markers from `origin/main`; R2e resolves that only by a current-base PR-first candidate plus renewed exact-SHA review, not by direct SQL, direct main merge, deployment or runtime propagation.

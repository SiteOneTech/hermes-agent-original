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
Canonical G1 pack for the **private Zeus-side implementation** succeeding `zeus-independent-alpha-research`. It is not a Vonash implementation plan, grants no external runtime access and does not authorize market execution. The corrected substantive candidate `3e6c14f8aa368ec6e3623d16640bf4b558ce0c7a` has independent exact-SHA Factory PASS evidence: specification gate 709, security gate 710, and quality gate 711. It is visible on the Zeus-signed, `agent:zeus`-labeled PR [#20](https://github.com/SiteOneTech/hermes-agent-original/pull/20). The prior quality gate 708 `REQUEST_CHANGES` on `0d57631de23f84db3135764bea538fa349dc7462` was repaired by Factory event 174440 (the bounded ALR-020 acceptance read-back) and this reviewed candidate reconciles the corresponding docs. This post-review marker transition records those real gates; it is not self-approval, QA Guardian approval, merge/deploy authorization, or ALR-020 authority. Earlier Factory gate rows remain audit evidence only: gates 686/687 were `REQUEST_CHANGES`; events 173433/173494 record non-approval direct integrations.

| File | Purpose | Owner | Validated | Reviewed |
|---|---|---|---|---|
| `FACTORY_INTAKE.md` | mandate, boundaries, source of truth | factory-orchestrator | validated: yes | reviewed: yes |
| `G0_REPOSITORY_STRATEGY.md` | repo/scope/worktree/PR decision | solution-architect | validated: yes | reviewed: yes |
| `REQUIREMENTS_ANALYSIS.md` | R1–R10/no-authority requirements | product-analyst | validated: yes | reviewed: yes |
| `PATTERN_ANALYSIS.md` | patterns and rejected shortcuts | product-analyst | validated: yes | reviewed: yes |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | verified inputs/unknowns | solution-architect | validated: yes | reviewed: yes |
| `PRD.md` | outcome and release acceptance | product-analyst | validated: yes | reviewed: yes |
| `ADRS.md` | architectural decisions | solution-architect | validated: yes | reviewed: yes |
| `METHODOLOGY_PLAN.md` | Factory/TDD/review approach | implementation-planner | validated: yes | reviewed: yes |
| `TECHNICAL_BLUEPRINT.md` | component placement and architecture | solution-architect | validated: yes | reviewed: yes |
| `SPRINT_PLAN.md` | increments | implementation-planner | validated: yes | reviewed: yes |
| `TASK_GRAPH.md` | Factory reconciliation/reviews | implementation-planner | validated: yes | reviewed: yes |
| `TRACKER.md` | status/risk register | factory-reporter | validated: yes | reviewed: yes |
| `QA_GATES.md` | RED/GREEN, smoke and delivery gates | qa-verifier | validated: yes | reviewed: yes |
| `SECURITY_GATES.md` | security pass/fail evidence | security-reviewer | validated: yes | reviewed: yes |
| `DOCUMENTATION_INDEX.md` | entrypoint/status matrix | factory-orchestrator | validated: yes | reviewed: yes |

## Supplemental controlling artifacts
- `REQUIREMENTS_TRACEABILITY.md` maps requirements to tasks/tests/reviews.
- `DATABASE_AND_RUNTIME_CONTRACT.md` is binding for exact DB, runtime, no-egress and scheduler implementation behavior.
- `G1_REVIEW.md` records independent review findings/remediation.

## Status semantics
- `validated: yes` means the implementation-planner/local worker confirmed the file exists, is tracked, is indexed where required, and is internally consistent with this G1 contract.
- `reviewed: yes` records independent specification/security/quality PASS evidence for corrected substantive candidate `3e6c14f8aa368ec6e3623d16640bf4b558ce0c7a` (Factory gates 709/710/711). It does not represent self-review, QA Guardian approval, or authorization to merge/deploy.
- Factory event 174440 is an auditable task-metadata correction, not source delivery, QA Guardian approval, or implementation authority. A reviewed marker or the observed ALR-010-R1 base-branch merges never authorize normal implementation by themselves.

## Current R2c canonical read-back
R2c recurrence run `run-1786849165-f05567ae` re-read the required G1 pack from the assigned isolated worktree after the Factory reconciler reopened the same `unvalidated_required_docs` anomaly. This branch/worktree remains internally G1-reviewed: every required G1 row above uses exact machine-readable `validated: yes` and `reviewed: yes` markers, and the supplemental controlling artifacts preserve the Zeus-only/no-egress/no-runtime-authority contract. However, the Agent Core Factory status command still computes the project `document_status` from the canonical `repo_path=/home/jean/Projects/hermes-agent-original` checkout, where the live required-doc snapshot remains `docs_ready=false`, `blocking_count=11`, and these G1 blockers: `FACTORY_INTAKE.md`, `REQUIREMENTS_ANALYSIS.md`, `PATTERN_ANALYSIS.md`, `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, `PRD.md`, `ADRS.md`, `METHODOLOGY_PLAN.md`, `TECHNICAL_BLUEPRINT.md`, `SPRINT_PLAN.md`, `TASK_GRAPH.md`, and `SECURITY_GATES.md`.

Therefore these branch-local markers are review evidence, not downstream execution authority. Product execution, QA, sandbox, delivery, base-branch merge, deploy and ALR-020+ dispatch remain blocked until an authorized canonical-source update or Factory resolve-state produces a `document_status` snapshot with zero G1 blockers. This worker did not direct-merge to `main`, deploy, change credentials, or write directly to `factory.*`.

## Required reading order
1. `DOCUMENTATION_INDEX.md`, `FACTORY_INTAKE.md`, `G0_REPOSITORY_STRATEGY.md`
2. `REQUIREMENTS_ANALYSIS.md`, `REQUIREMENTS_TRACEABILITY.md`, `PRD.md`, `ADRS.md`
3. `DATABASE_AND_RUNTIME_CONTRACT.md`, `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`, `SPRINT_PLAN.md`
4. `QA_GATES.md`, `SECURITY_GATES.md`, `G1_REVIEW.md`

## G1 rule
No normal implementation starts until every required G1 document is `reviewed: yes`; the three supplemental controlling artifacts must be committed and independently reviewed against the exact corrected candidate. Base exposure alone is not sufficient: observed direct integrations `173433`/`173494` remain non-approval audit evidence, and a branch-only pack without a Zeus-signed `agent:zeus` PR is likewise never sufficient. The manual Factory takeover remains active only until canonical resolve-state sees this committed marker transition; normal work still must start through the single-task Factory tick and follow strict TDD, independent review and PR-first rules.

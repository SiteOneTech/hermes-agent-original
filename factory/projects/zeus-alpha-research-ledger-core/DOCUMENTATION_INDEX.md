---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: pending
owner: factory-orchestrator
---

# DOCUMENTATION INDEX — Zeus Alpha Research Ledger Core

## Controlling status
Canonical G1 pack for the **private Zeus-side implementation** succeeding `zeus-independent-alpha-research`. It is not a Vonash implementation plan, grants no external runtime access and does not authorize market execution. The substantive control candidate `dad375f27568c38be771fc597b579d087f034e1d` has independent exact-SHA Factory PASS evidence: specification gate 699 and security gates 706/707, and is visible on the Zeus-signed, `agent:zeus`-labeled PR [#20](https://github.com/SiteOneTech/hermes-agent-original/pull/20). Those gates do not carry across the later metadata candidate `0d57631de23f84db3135764bea538fa349dc7462`: independent quality gate 708 returned `REQUEST_CHANGES` on that SHA. Its bounded rework is now recorded: Factory event 174440 corrected the ALR-020 acceptance criterion to exclude collaboration session/message entities and preserve local normalized-evidence intake as non-session intake, with old/new literal read-back. Required G1 markers therefore remain `reviewed: pending` until a new independent exact-SHA review accepts this corrected project-local documentation candidate. This is not self-approval, QA Guardian approval, merge/deploy authorization, or ALR-020 authority. Earlier Factory gate rows remain audit evidence only: gates 686/687 were `REQUEST_CHANGES`; events 173433/173494 record non-approval direct integrations.

| File | Purpose | Owner | Validated | Reviewed |
|---|---|---|---|---|
| `FACTORY_INTAKE.md` | mandate, boundaries, source of truth | factory-orchestrator | yes | pending |
| `G0_REPOSITORY_STRATEGY.md` | repo/scope/worktree/PR decision | solution-architect | yes | pending |
| `REQUIREMENTS_ANALYSIS.md` | R1–R10/no-authority requirements | product-analyst | yes | pending |
| `PATTERN_ANALYSIS.md` | patterns and rejected shortcuts | product-analyst | yes | pending |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | verified inputs/unknowns | solution-architect | yes | pending |
| `PRD.md` | outcome and release acceptance | product-analyst | yes | pending |
| `ADRS.md` | architectural decisions | solution-architect | yes | pending |
| `METHODOLOGY_PLAN.md` | Factory/TDD/review approach | implementation-planner | yes | pending |
| `TECHNICAL_BLUEPRINT.md` | component placement and architecture | solution-architect | yes | pending |
| `SPRINT_PLAN.md` | increments | implementation-planner | yes | pending |
| `TASK_GRAPH.md` | Factory reconciliation/reviews | implementation-planner | yes | pending |
| `TRACKER.md` | status/risk register | factory-reporter | yes | pending |
| `QA_GATES.md` | RED/GREEN, smoke and delivery gates | qa-verifier | yes | pending |
| `SECURITY_GATES.md` | security pass/fail evidence | security-reviewer | yes | pending |
| `DOCUMENTATION_INDEX.md` | entrypoint/status matrix | factory-orchestrator | yes | pending |

## Supplemental controlling artifacts
- `REQUIREMENTS_TRACEABILITY.md` maps requirements to tasks/tests/reviews.
- `DATABASE_AND_RUNTIME_CONTRACT.md` is binding for exact DB, runtime, no-egress and scheduler implementation behavior.
- `G1_REVIEW.md` records independent review findings/remediation.

## Status semantics
- `validated: yes` means the implementation-planner/local worker confirmed the file exists, is tracked, is indexed where required, and is internally consistent with this G1 contract.
- `reviewed: pending` is binding after gate 708's actual `REQUEST_CHANGES` on `0d57631de23f84db3135764bea538fa349dc7462`; the prior PASS gates on substantive candidate `dad375f27568c38be771fc597b579d087f034e1d` are retained as evidence, not reused as approval of the revised candidate.
- Factory event 174440 is an auditable task-metadata correction, not source delivery, QA Guardian approval, or implementation authority. A reviewed marker or the observed ALR-010-R1 base-branch merges never authorize normal implementation by themselves.

## Required reading order
1. `DOCUMENTATION_INDEX.md`, `FACTORY_INTAKE.md`, `G0_REPOSITORY_STRATEGY.md`
2. `REQUIREMENTS_ANALYSIS.md`, `REQUIREMENTS_TRACEABILITY.md`, `PRD.md`, `ADRS.md`
3. `DATABASE_AND_RUNTIME_CONTRACT.md`, `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`, `SPRINT_PLAN.md`
4. `QA_GATES.md`, `SECURITY_GATES.md`, `G1_REVIEW.md`

## G1 rule
No normal implementation starts until every required G1 document is `reviewed: yes`; the three supplemental controlling artifacts must be committed and independently reviewed against the exact corrected candidate. Base exposure alone is not sufficient: observed direct integrations `173433`/`173494` remain non-approval audit evidence, and a branch-only pack without a Zeus-signed `agent:zeus` PR is likewise never sufficient. The manual Factory takeover remains active while this bounded documentary rework is committed, made visible on PR #20, and independently reviewed.

---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: yes
reviewed_by: solution-architect
review_evidence: factory_gate_794
reviewed_candidate_sha: c81547062c5362a7be6f5a1bb2ef9612b29bac9c
reviewed_candidate_pr: https://github.com/SiteOneTech/hermes-agent-original/pull/36
reviewed_source_gate: factory_gate_790
reviewed_source_sha: 2476e978c545e24b18ee48844b24eb8c58245ab4
owner: factory-orchestrator
---

# DOCUMENTATION INDEX — Zeus Alpha Research Ledger Core

## Controlling status
Canonical G1 pack for the **private Zeus-side implementation** succeeding `zeus-independent-alpha-research`. It is not a Vonash implementation plan, grants no external runtime access and does not authorize market execution.

R2u repairs the current-base docs-first preflight by committing the machine-readable reviewed state into the canonical project-local documentation pack. The current base and R2u branch start at `df4c77fd1413a65cdb85885a06978ff157c1de4d`. The reviewed status is bound to the PR-first G1 candidate that already received independent exact-SHA review: PR #36, head `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`, reviewer `solution-architect`, Factory gate `794`, with source reviewed-docs evidence retained from gate `790` / PR #34 SHA `2476e978c545e24b18ee48844b24eb8c58245ab4`.

This is canonical documentation readiness, not runtime approval. The R2u repair performs no product implementation, no merge, no deploy, no credential change, no connector activation and no trading/risk/paper/live action. ALR-020+ still requires its own scoped TDD/security/QA gates before any code path may ship.

| File | Purpose | Owner | Validated | Reviewed |
|---|---|---|---|---|
| `FACTORY_INTAKE.md` | mandate, boundaries, source of truth | factory-orchestrator | yes | yes — gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |
| `G0_REPOSITORY_STRATEGY.md` | repo/scope/worktree/PR decision | solution-architect | yes | yes — gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |
| `REQUIREMENTS_ANALYSIS.md` | R1–R10/no-authority requirements | product-analyst | yes | yes — gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |
| `PATTERN_ANALYSIS.md` | patterns and rejected shortcuts | product-analyst | yes | yes — gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | verified inputs/unknowns | solution-architect | yes | yes — gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |
| `PRD.md` | outcome and release acceptance | product-analyst | yes | yes — gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |
| `ADRS.md` | architectural decisions | solution-architect | yes | yes — gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |
| `METHODOLOGY_PLAN.md` | Factory/TDD/review approach | implementation-planner | yes | yes — gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |
| `TECHNICAL_BLUEPRINT.md` | component placement and architecture | solution-architect | yes | yes — gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |
| `SPRINT_PLAN.md` | increments | implementation-planner | yes | yes — gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |
| `TASK_GRAPH.md` | Factory reconciliation/reviews | implementation-planner | yes | yes — gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |
| `TRACKER.md` | status/risk register | factory-reporter | yes | yes — gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |
| `QA_GATES.md` | RED/GREEN, smoke and delivery gates | qa-verifier | yes | yes — gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |
| `SECURITY_GATES.md` | security pass/fail evidence | security-reviewer | yes | yes — gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |
| `DOCUMENTATION_INDEX.md` | entrypoint/status matrix | factory-orchestrator | yes | yes — gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |

## Supplemental controlling artifacts
- `REQUIREMENTS_TRACEABILITY.md` maps requirements to tasks/tests/reviews.
- `DATABASE_AND_RUNTIME_CONTRACT.md` is binding for exact DB, runtime, no-egress and scheduler implementation behavior.
- `G1_REVIEW.md` records independent review findings/remediation.
- `R2J_CANONICAL_STATE_REPAIR.md` records the historical PR #29 canonical-state provenance repair: exact PR #29 head `f61a7275048e2135b2b2729a1b9cdf8713c58866`, R2i review-worktree `already_ancestor` mismatch and the intended PR-first handoff that later became PR #30.
- `R2K_STALE_CANONICAL_G1_PROVENANCE_REPAIR.md` records the stale active provenance repair as historical control evidence. It records that Agent Core project metadata still points to obsolete PR #20 / `dad375f27568c38be771fc597b579d087f034e1d`, PR #30 carried R2j commit `c1943efb2b97b54b42bc5eabe858340d8c391116` into remote `origin/main` as `83d5ee06ba25859f047469baed223fe88e9467e3`, local primary `main` remained at `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1` during that repair, and canonical G1 `document_status` remained non-dispatchable because required docs read back as `reviewed=false` from the primary source.
- `R2M_CURRENT_BASE_G1_REVIEW_HANDOFF.md` records the current-base recovery on exact `origin/main` `ab08b13669903a87b3d60d6c80231d23d6313782`, keeps PR #20/#29/R2i/R2j/R2k evidence historical only, and binds the next valid review to the fresh R2m PR head SHA after push.
- `R2U_CANONICAL_G1_DOCUMENT_STATUS_PREFLIGHT_REPAIR.md` records this docs-first repair: current base `df4c77fd1413a65cdb85885a06978ff157c1de4d`, reviewed PR #36 head `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`, gate `794`, and the no-runtime/no-merge validation contract.
- `R2V_CANONICAL_G1_STATUS_AND_NO_AUTO_MERGE_REPAIR.md` records the control-plane contract repair that makes stale-primary G1 readiness read the verified configured base ref only, rejects candidate PR/worktree readiness sources, and prevents Factory auto-integration when `factory_auto_integration_forbidden=true`.
- `R2W_CANONICAL_G1_REVIEWED_FRONTMATTER_PR.md` records the current PR-first recovery evidence for the reviewed-frontmatter state: configured base ref `origin/main` at `df79aac9d306c0b055fe88dbde5ebd54d9635e36`, approved Factory status CLI read-back with zero G1 required-document blockers, and the no-merge/no-runtime independent-review handoff for this task.

## Status semantics
- `validated: yes` means the implementation-planner/local worker confirmed the file exists, is tracked, is indexed where required, and is internally consistent with this G1 contract.
- `reviewed: yes` on the required G1 documents is a machine-readable reviewed-status value backed by independent Factory gate `794` against PR #36 exact head `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`, plus source reviewed-docs evidence from gate `790` / PR #34 SHA `2476e978c545e24b18ee48844b24eb8c58245ab4`.
- R2w status evidence confirms the configured-base `document_status` reader now sees the reviewed frontmatter/index state on `origin/main` commit `df79aac9d306c0b055fe88dbde5ebd54d9635e36` with all G1 required rows non-blocking; this confirmation remains review evidence, not a downstream implementation authorization.
- A branch-local reviewed status or the observed ALR-010-R1 base-branch merge never authorizes normal implementation by itself; docs readiness only removes the required-document blocker. Exact task-specific TDD, security, QA and delivery evidence remain required.
- Review-task integration metadata must not be used as PR visibility evidence unless its branch commit equals the candidate PR head; for R2i, the `already_ancestor` attachment names review branch commit `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c`, while the actual PR #29 candidate remains `f61a7275048e2135b2b2729a1b9cdf8713c58866` and the later R2j repair is PR #30 head `c1943efb2b97b54b42bc5eabe858340d8c391116`.
- Stale Factory project metadata that points to PR #20 / `dad375f27568c38be771fc597b579d087f034e1d` is not current review provenance and must not be used to dispatch ALR-020.

## Required reading order
1. `DOCUMENTATION_INDEX.md`, `FACTORY_INTAKE.md`, `G0_REPOSITORY_STRATEGY.md`
2. `REQUIREMENTS_ANALYSIS.md`, `REQUIREMENTS_TRACEABILITY.md`, `PRD.md`, `ADRS.md`
3. `DATABASE_AND_RUNTIME_CONTRACT.md`, `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`, `SPRINT_PLAN.md`
4. `QA_GATES.md`, `SECURITY_GATES.md`, `G1_REVIEW.md`, `R2K_STALE_CANONICAL_G1_PROVENANCE_REPAIR.md`, `R2M_CURRENT_BASE_G1_REVIEW_HANDOFF.md`, `R2U_CANONICAL_G1_DOCUMENT_STATUS_PREFLIGHT_REPAIR.md`, `R2V_CANONICAL_G1_STATUS_AND_NO_AUTO_MERGE_REPAIR.md`

## G1 rule
No normal implementation starts merely because documentation blockers are cleared. R2u makes the required G1 pack `reviewed: yes` from independently reviewed PR-first evidence, but downstream ALR-020+ work still requires its own assigned branch/worktree, RED→GREEN tests, security/no-egress proof, PR-first delivery evidence and gate-specific approval. Base exposure alone is never sufficient: the observed ALR-010-R1 merge, R2j/PR #30 merge and R2k/PR #31 merge remain historical non-dispatch evidence unless the active task's own gates are green.

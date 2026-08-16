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

R2c3 reconciles the current-origin G1 visibility evidence from a fresh isolated worktree based on exact `origin/main` `2a32066398d500d6dac071bd7f2184d47bb3bcb4`. The stale-primary RED read-back from `/home/jean/Projects/hermes-agent-original` reproduced 10 required G1 blockers with `reviewed=false` because that checkout remains at `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1` while `origin/main` is `2a32066398d500d6dac071bd7f2184d47bb3bcb4`, and project metadata still names stale inc-011 / PR #20 (`dad375f27568c38be771fc597b579d087f034e1d`) as historical checkout provenance. The current-origin GREEN read-back from the assigned R2c3 worktree uses `readiness_source=configured_base_ref` and shows every required G1 document exists, is committed, indexed, validated, reviewed, and non-blocking at configured-base log lines 17046–17312 in `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786895883-2463118-cd90.log`. The machine-readable reviewed status remains bound to the independently reviewed PR-first G1 source: PR #36, head `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`, reviewer `solution-architect`, Factory gate `794`, with source reviewed-docs evidence retained from gate `790` / PR #34 SHA `2476e978c545e24b18ee48844b24eb8c58245ab4`. The fresh R2c3 handoff must be a non-draft Zeus-signed `agent:zeus` PR and still requires independent exact-SHA review; it is not self-approval.

This is canonical documentation readiness, not runtime approval. The R2c3 repair performs no product implementation, no merge, no deploy, no credential change, no connector activation and no trading/risk/paper/live action. ALR-020+ still requires its own scoped TDD/security/QA gates before any code path may ship.

| File | Purpose | Owner | Validated | Reviewed |
|---|---|---|---|---|
| `FACTORY_INTAKE.md` | mandate, boundaries, source of truth | factory-orchestrator | yes | yes — source gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`; current-base read-back `dbde1790f8d45f111bc69b3491a1862eafb29fa2`; R2c2 PR-first handoff |
| `G0_REPOSITORY_STRATEGY.md` | repo/scope/worktree/PR decision | solution-architect | yes | yes — source gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`; current-base read-back `dbde1790f8d45f111bc69b3491a1862eafb29fa2`; R2c2 PR-first handoff |
| `REQUIREMENTS_ANALYSIS.md` | R1–R10/no-authority requirements | product-analyst | yes | yes — source gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`; current-base read-back `dbde1790f8d45f111bc69b3491a1862eafb29fa2`; R2c2 PR-first handoff |
| `PATTERN_ANALYSIS.md` | patterns and rejected shortcuts | product-analyst | yes | yes — source gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`; current-base read-back `dbde1790f8d45f111bc69b3491a1862eafb29fa2`; R2c2 PR-first handoff |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | verified inputs/unknowns | solution-architect | yes | yes — source gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`; current-base read-back `dbde1790f8d45f111bc69b3491a1862eafb29fa2`; R2c2 PR-first handoff |
| `PRD.md` | outcome and release acceptance | product-analyst | yes | yes — source gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`; current-base read-back `dbde1790f8d45f111bc69b3491a1862eafb29fa2`; R2c2 PR-first handoff |
| `ADRS.md` | architectural decisions | solution-architect | yes | yes — source gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`; current-base read-back `dbde1790f8d45f111bc69b3491a1862eafb29fa2`; R2c2 PR-first handoff |
| `METHODOLOGY_PLAN.md` | Factory/TDD/review approach | implementation-planner | yes | yes — source gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`; current-base read-back `dbde1790f8d45f111bc69b3491a1862eafb29fa2`; R2c2 PR-first handoff |
| `TECHNICAL_BLUEPRINT.md` | component placement and architecture | solution-architect | yes | yes — source gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`; current-base read-back `dbde1790f8d45f111bc69b3491a1862eafb29fa2`; R2c2 PR-first handoff |
| `SPRINT_PLAN.md` | increments | implementation-planner | yes | yes — source gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`; current-base read-back `dbde1790f8d45f111bc69b3491a1862eafb29fa2`; R2c2 PR-first handoff |
| `TASK_GRAPH.md` | Factory reconciliation/reviews | implementation-planner | yes | yes — source gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`; current-base read-back `dbde1790f8d45f111bc69b3491a1862eafb29fa2`; R2c2 PR-first handoff |
| `TRACKER.md` | status/risk register | factory-reporter | yes | yes — source gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`; current-base read-back `dbde1790f8d45f111bc69b3491a1862eafb29fa2`; R2c2 PR-first handoff |
| `QA_GATES.md` | RED/GREEN, smoke and delivery gates | qa-verifier | yes | yes — source gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`; current-base read-back `dbde1790f8d45f111bc69b3491a1862eafb29fa2`; R2c2 PR-first handoff |
| `SECURITY_GATES.md` | security pass/fail evidence | security-reviewer | yes | yes — source gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`; current-base read-back `dbde1790f8d45f111bc69b3491a1862eafb29fa2`; R2c2 PR-first handoff |
| `DOCUMENTATION_INDEX.md` | entrypoint/status matrix | factory-orchestrator | yes | yes — source gate 794 / PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`; current-base read-back `dbde1790f8d45f111bc69b3491a1862eafb29fa2`; R2c2 PR-first handoff |

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
- `R2AH_CURRENT_ORIGIN_G1_REVIEWED_MARKER_REPAIR.md` records the current-origin R2ah repair: fresh worktree/branch identity captured before edits, `origin/main` `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7`, Agent Core configured-base `document_status` rows with all 14 required G1 documents non-blocking, and PR #47 `https://github.com/SiteOneTech/hermes-agent-original/pull/47` as the fresh PR-first independent-review handoff.
- `R2C2_AUTONOMOUS_CANONICAL_G1_DOCUMENTATION_STATUS_REPAIR.md` records the current R2c2 repair: fresh worktree/branch identity captured before edits, `origin/main` `dbde1790f8d45f111bc69b3491a1862eafb29fa2`, Agent Core configured-base `document_status` rows with all 14 required G1 documents non-blocking, and PR #48 `https://github.com/SiteOneTech/hermes-agent-original/pull/48` as the fresh PR-first independent-review handoff.
- `R2C3_CURRENT_ORIGIN_G1_VISIBILITY_AND_RECONCILIATION_REPAIR.md` records the current R2c3 repair: fresh worktree/branch identity captured before edits, `origin/main` `2a32066398d500d6dac071bd7f2184d47bb3bcb4`, the stale-primary RED read-back root cause, Agent Core configured-base GREEN `document_status` rows with all 14 required G1 documents non-blocking, and the fresh PR-first independent-review handoff.

## Status semantics
- `validated: yes` means the implementation-planner/local worker confirmed the file exists, is tracked, is indexed where required, and is internally consistent with this G1 contract.
- `reviewed: yes` on the required G1 documents is a machine-readable reviewed-status value backed by independent Factory gate `794` against PR #36 exact head `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`, plus source reviewed-docs evidence from gate `790` / PR #34 SHA `2476e978c545e24b18ee48844b24eb8c58245ab4`.
- R2c3 status evidence confirms the configured-base `document_status` reader now sees the reviewed frontmatter/index state on `origin/main` commit `2a32066398d500d6dac071bd7f2184d47bb3bcb4` with all 14 G1 required rows non-blocking; this confirmation remains documentation-readiness evidence, not a downstream implementation authorization.
- The stale-primary RED read-back remains diagnostic evidence only: `/home/jean/Projects/hermes-agent-original` at `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1` and stale inc-011 / PR #20 metadata must not be reused as current candidate provenance.
- The R2c3 PR is a delivery/review handoff for the current-origin visibility repair. It must be independently reviewed against its exact head SHA before task closure; this worker does not self-approve or merge it.
- A branch-local reviewed status or the observed ALR-010-R1 base-branch merge never authorizes normal implementation by itself; docs readiness only removes the required-document blocker. Exact task-specific TDD, security, QA and delivery evidence remain required.
- Review-task integration metadata must not be used as PR visibility evidence unless its branch commit equals the candidate PR head; for R2i, the `already_ancestor` attachment names review branch commit `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c`, while the actual PR #29 candidate remains `f61a7275048e2135b2b2729a1b9cdf8713c58866` and the later R2j repair is PR #30 head `c1943efb2b97b54b42bc5eabe858340d8c391116`.
- Stale Factory project metadata that points to PR #20 / `dad375f27568c38be771fc597b579d087f034e1d` is not current review provenance and must not be used to dispatch ALR-020.

## Required reading order
1. `DOCUMENTATION_INDEX.md`, `FACTORY_INTAKE.md`, `G0_REPOSITORY_STRATEGY.md`
2. `REQUIREMENTS_ANALYSIS.md`, `REQUIREMENTS_TRACEABILITY.md`, `PRD.md`, `ADRS.md`
3. `DATABASE_AND_RUNTIME_CONTRACT.md`, `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`, `SPRINT_PLAN.md`
4. `QA_GATES.md`, `SECURITY_GATES.md`, `G1_REVIEW.md`, `R2K_STALE_CANONICAL_G1_PROVENANCE_REPAIR.md`, `R2M_CURRENT_BASE_G1_REVIEW_HANDOFF.md`, `R2U_CANONICAL_G1_DOCUMENT_STATUS_PREFLIGHT_REPAIR.md`, `R2V_CANONICAL_G1_STATUS_AND_NO_AUTO_MERGE_REPAIR.md`, `R2AH_CURRENT_ORIGIN_G1_REVIEWED_MARKER_REPAIR.md`, `R2C2_AUTONOMOUS_CANONICAL_G1_DOCUMENTATION_STATUS_REPAIR.md`, `R2C3_CURRENT_ORIGIN_G1_VISIBILITY_AND_RECONCILIATION_REPAIR.md`

## G1 rule
No normal implementation starts merely because documentation blockers are cleared. R2c3 preserves the required G1 pack `reviewed: yes` from independently reviewed PR-first evidence and reconciles the index to current `origin/main`, but downstream ALR-020+ work still requires its own assigned branch/worktree, RED→GREEN tests, security/no-egress proof, PR-first delivery evidence and gate-specific approval. Base exposure alone is never sufficient: the observed ALR-010-R1 merge, R2j/PR #30 merge, R2k/PR #31 merge, R2c2/PR #48 handoff, and stale inc-011/PR #20 metadata remain historical non-dispatch evidence unless the active task's own gates are green.

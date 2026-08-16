---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_reviewed_candidate_primary_hold
validated: yes
reviewed: yes
reviewed_by: quality-reviewer
review_evidence: factory_gate_790
reviewed_candidate_sha: 2476e978c545e24b18ee48844b24eb8c58245ab4
reviewed_candidate_pr: https://github.com/SiteOneTech/hermes-agent-original/pull/34
reviewed_source_gate: factory_gate_789
reviewed_source_sha: 1e82340dddf52071d14c3c7a00b04b3c17ee2821
owner: factory-orchestrator
---

# DOCUMENTATION INDEX — Zeus Alpha Research Ledger Core

## Controlling status

Canonical G1 pack for the **private Zeus-side implementation** succeeding `zeus-independent-alpha-research`. It is not a Vonash implementation plan, grants no external runtime access and does not authorize market execution.

R2q restores the current-main reviewed-docs candidate on exact base `df4c77fd1413a65cdb85885a06978ff157c1de4d`. The 14 required G1 documents now carry candidate-level `reviewed: yes` markers bound to the latest valid reviewed-docs candidate: PR #34 at `2476e978c545e24b18ee48844b24eb8c58245ab4`, Factory gate **790**, reviewer `quality-reviewer`, with source document review evidence from gate **789** / PR #33 SHA `1e82340dddf52071d14c3c7a00b04b3c17ee2821`.

R2p is explicitly rejected as completion evidence: quality-reviewer run `run-1786840866-90f55f9d` ended on MiniMax OAuth HTTP 429 after three retries, logged `Messages: 1 (1 user, 0 tool calls)`, and did not execute a review. Provider failure is blocked/retriable evidence, never a PASS.

This is **candidate readiness**, not primary-repo readiness. No normal ALR-020+ dispatch is authorized until canonical Agent Core `document_status` or an explicitly authorized reviewed-candidate path reads back no required G1 blockers and an independent `solution-architect` review cites the exact final R2q PR head SHA and proves review work actually ran.

| File | Purpose | Owner | Validated | Reviewed |
|---|---|---|---|---|
| `FACTORY_INTAKE.md` | mandate, boundaries, source of truth | factory-orchestrator | yes | yes — gate 790 / PR #34 `2476e978c545e24b18ee48844b24eb8c58245ab4` |
| `REQUIREMENTS_ANALYSIS.md` | R1–R10/no-authority requirements | product-analyst | yes | yes — gate 790 / PR #34 `2476e978c545e24b18ee48844b24eb8c58245ab4` |
| `PATTERN_ANALYSIS.md` | patterns and rejected shortcuts | product-analyst | yes | yes — gate 790 / PR #34 `2476e978c545e24b18ee48844b24eb8c58245ab4` |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | verified inputs/unknowns | solution-architect | yes | yes — gate 790 / PR #34 `2476e978c545e24b18ee48844b24eb8c58245ab4` |
| `PRD.md` | outcome and release acceptance | product-analyst | yes | yes — gate 790 / PR #34 `2476e978c545e24b18ee48844b24eb8c58245ab4` |
| `ADRS.md` | architectural decisions | solution-architect | yes | yes — gate 790 / PR #34 `2476e978c545e24b18ee48844b24eb8c58245ab4` |
| `METHODOLOGY_PLAN.md` | Factory/TDD/review approach | implementation-planner | yes | yes — gate 790 / PR #34 `2476e978c545e24b18ee48844b24eb8c58245ab4` |
| `TECHNICAL_BLUEPRINT.md` | component placement and architecture | solution-architect | yes | yes — gate 790 / PR #34 `2476e978c545e24b18ee48844b24eb8c58245ab4` |
| `SPRINT_PLAN.md` | increments | implementation-planner | yes | yes — gate 790 / PR #34 `2476e978c545e24b18ee48844b24eb8c58245ab4` |
| `TASK_GRAPH.md` | Factory reconciliation/reviews | implementation-planner | yes | yes — gate 790 / PR #34 `2476e978c545e24b18ee48844b24eb8c58245ab4` |
| `TRACKER.md` | status/risk register | factory-reporter | yes | yes — gate 790 / PR #34 `2476e978c545e24b18ee48844b24eb8c58245ab4` |
| `DOCUMENTATION_INDEX.md` | entrypoint/status matrix | factory-orchestrator | yes | yes — gate 790 / PR #34 `2476e978c545e24b18ee48844b24eb8c58245ab4` |
| `QA_GATES.md` | RED/GREEN, smoke and delivery gates | qa-verifier | yes | yes — gate 790 / PR #34 `2476e978c545e24b18ee48844b24eb8c58245ab4` |
| `SECURITY_GATES.md` | security pass/fail evidence | security-reviewer | yes | yes — gate 790 / PR #34 `2476e978c545e24b18ee48844b24eb8c58245ab4` |

## Supplemental controlling artifacts
- `REQUIREMENTS_TRACEABILITY.md` maps requirements to tasks/tests/reviews.
- `DATABASE_AND_RUNTIME_CONTRACT.md` is binding for exact DB, runtime, no-egress and scheduler implementation behavior.
- `G1_REVIEW.md` records independent review findings/remediation.
- `R2J_CANONICAL_STATE_REPAIR.md` records the historical PR #29 canonical-state provenance repair: exact PR #29 head `f61a7275048e2135b2b2729a1b9cdf8713c58866`, R2i review-worktree `already_ancestor` mismatch and the intended PR-first handoff that later became PR #30.
- `R2K_STALE_CANONICAL_G1_PROVENANCE_REPAIR.md` records the stale active provenance repair as historical control evidence. It records that Agent Core project metadata still points to obsolete PR #20 / `dad375f27568c38be771fc597b579d087f034e1d`, PR #30 carried R2j commit `c1943efb2b97b54b42bc5eabe858340d8c391116` into remote `origin/main` as `83d5ee06ba25859f047469baed223fe88e9467e3`, local primary `main` remained at `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1` during that repair, and canonical G1 `document_status` remained non-dispatchable because required docs read back as `reviewed=false` from the primary source.
- `R2M_CURRENT_BASE_G1_REVIEW_HANDOFF.md` records the current-base recovery on exact `origin/main` `ab08b13669903a87b3d60d6c80231d23d6313782`, keeps PR #20/#29/R2i/R2j/R2k evidence historical only, and binds the next valid review to the fresh R2m PR head SHA after push.
- `R2Q_CURRENT_MAIN_G1_REVIEW_CANDIDATE_RECOVERY.md` records the current-main reviewed-docs candidate recovery, the invalid R2p HTTP-429/zero-tool-call review, and the exact solution-architect review contract for this R2q PR.

## Status semantics
- `validated: yes` means the file exists, is tracked, is indexed where required, and is internally consistent with this G1 contract.
- `reviewed: yes` on the 14 required G1 files is a candidate-level machine-readable marker backed by Factory gate 790, reviewer `quality-reviewer`, PR #34 and exact SHA `2476e978c545e24b18ee48844b24eb8c58245ab4`; the underlying source-document review evidence is gate 789 / PR #33 SHA `1e82340dddf52071d14c3c7a00b04b3c17ee2821`.
- R2q itself remains pending independent `solution-architect` review until the reviewer cites the final R2q PR head SHA and proves review execution with real tool/file/diff/command evidence.
- A branch-local reviewed status or the observed ALR-010-R1 base-branch merge never authorizes normal implementation by itself; exact-SHA independent reviews and reconciled delivery evidence remain required.
- Review-task integration metadata must not be used as PR visibility evidence unless its branch commit equals the candidate PR head; for R2i, the `already_ancestor` attachment names review branch commit `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c`, while the actual PR #29 candidate remains `f61a7275048e2135b2b2729a1b9cdf8713c58866` and the later R2j repair is PR #30 head `c1943efb2b97b54b42bc5eabe858340d8c391116`.
- Stale Factory project metadata that points to PR #20 / `dad375f27568c38be771fc597b579d087f034e1d`, PR #35/R2p code-path evidence, or any provider-failed/zero-tool review run is not current review provenance and must not be used to dispatch ALR-020.

## Required reading order
1. `DOCUMENTATION_INDEX.md`, `FACTORY_INTAKE.md`, `G0_REPOSITORY_STRATEGY.md`
2. `REQUIREMENTS_ANALYSIS.md`, `REQUIREMENTS_TRACEABILITY.md`, `PRD.md`, `ADRS.md`
3. `DATABASE_AND_RUNTIME_CONTRACT.md`, `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`, `SPRINT_PLAN.md`
4. `QA_GATES.md`, `SECURITY_GATES.md`, `G1_REVIEW.md`, `R2K_STALE_CANONICAL_G1_PROVENANCE_REPAIR.md`, `R2M_CURRENT_BASE_G1_REVIEW_HANDOFF.md`, `R2Q_CURRENT_MAIN_G1_REVIEW_CANDIDATE_RECOVERY.md`

## G1 rule
No normal implementation starts from this R2q branch alone. It may start only after the reviewed candidate is accepted into the canonical Factory source path or authorized reviewed-candidate metadata, Agent Core reads back no required G1 blockers, and the independent solution-architect review of the exact final R2q SHA is valid. This protects against false-ready assertions while preserving the independently reviewed candidate markers.

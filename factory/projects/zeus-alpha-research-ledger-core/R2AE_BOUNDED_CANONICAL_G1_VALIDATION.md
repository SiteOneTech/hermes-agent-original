---
document_type: bounded_canonical_g1_validation_evidence
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2ae-bounded-canonical-g1-validation-and
phase: documentation
status: implemented_pending_independent_review
validated: yes
reviewed: pending_independent_quality_review
owner: codex-builder
base_ref: origin/main
base_sha: eb3e3ff48905285812eca4c222fa2155a9282546
branch: factory/zeus-alpha-research-ledger-core/inc-019-r2ae-bounded-canonical-g1-valida
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2ae-bounded-canonical-g1-valida
---

# R2ae — bounded canonical G1 validation and fresh PR provenance repair

## Scope

This is the bounded documentation/provenance rework for the active `unvalidated_required_docs` anomaly on `zeus-alpha-research-ledger-core`. It uses Agent Core Factory status as the operational source of truth, keeps Notion out of the decision path, and repairs only project-local documentation/provenance.

No runtime/source implementation, merge, primary-checkout mutation, deployment, direct SQL, credential change, external-runtime operation, connector/messaging action, or trading/risk/paper/live action is authorized by this record.

## Current-base source readback

Readback sources used by this run:

- Assigned worktree path: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2ae-bounded-canonical-g1-valida`.
- Assigned branch: `factory/zeus-alpha-research-ledger-core/inc-019-r2ae-bounded-canonical-g1-valida`.
- Current configured base: `origin/main` / `eb3e3ff48905285812eca4c222fa2155a9282546`.
- Sanctioned Factory CLI status command: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status --json zeus-alpha-research-ledger-core`.
- Full Factory CLI output cache: `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1787304514-2795776-8ad0.log`.
- Project `document_status` rows in that cache: lines `24009`–`24275`.

## Source-backed required G1 inventory

The current configured-base Factory `document_status` block reports `readiness_source=configured_base_ref`, `base_ref=origin/main`, `base_commit=eb3e3ff48905285812eca4c222fa2155a9282546`, and `configured_base_ref_accepted=true` for the required G1 rows.

Inventory before this candidate repair:

| Required G1 document | Current configured-base status |
|---|---|
| `FACTORY_INTAKE.md` | exists=true, committed=true, indexed=true, validated=true, reviewed=true, blocking=false |
| `REQUIREMENTS_ANALYSIS.md` | exists=true, committed=true, indexed=true, validated=true, reviewed=true, blocking=false |
| `PATTERN_ANALYSIS.md` | exists=true, committed=true, indexed=true, validated=true, reviewed=true, blocking=false |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | exists=true, committed=true, indexed=true, validated=true, reviewed=true, blocking=false |
| `PRD.md` | exists=true, committed=true, indexed=true, validated=true, reviewed=true, blocking=false |
| `ADRS.md` | exists=true, committed=true, indexed=true, validated=true, reviewed=true, blocking=false |
| `METHODOLOGY_PLAN.md` | exists=true, committed=true, indexed=true, validated=true, reviewed=true, blocking=false |
| `TECHNICAL_BLUEPRINT.md` | exists=true, committed=true, indexed=true, validated=true, reviewed=true, blocking=false |
| `SPRINT_PLAN.md` | exists=true, committed=true, indexed=true, validated=true, reviewed=true, blocking=false |
| `TASK_GRAPH.md` | exists=true, committed=true, indexed=true, validated=true, reviewed=true, blocking=false |
| `TRACKER.md` | exists=true, committed=true, indexed=true, validated=true, reviewed=true, blocking=false |
| `DOCUMENTATION_INDEX.md` | exists=true, committed=true, indexed=true, validated=true, reviewed=false, blocking=true |
| `QA_GATES.md` | exists=true, committed=true, indexed=true, validated=true, reviewed=true, blocking=false |
| `SECURITY_GATES.md` | exists=true, committed=true, indexed=true, validated=true, reviewed=true, blocking=false |

Therefore the currently unvalidated/review-blocking G1 document set is exactly: `DOCUMENTATION_INDEX.md` only. The ten-document blocker list from older prompts and gate snapshots is stale historical/runtime projection and is not the current configured-base inventory.

## Repair performed

`DOCUMENTATION_INDEX.md` already carried `reviewed: yes` frontmatter and a reviewed table row, but the current Factory status parser still returned `reviewed=false` for the `DOCUMENTATION_INDEX.md` row. This candidate makes the `DOCUMENTATION_INDEX.md reviewed: yes` marker explicit before any long historical provenance text, indexes this R2ae evidence artifact, and records the precise source/status split.

The repair is intentionally not a Factory metadata mutation. Because the active status reader validates configured `origin/main`, the status cannot turn green until a reviewer accepts this PR and the branch is merged by the authorized PR/QA path. Until then, the expected status remains fail-closed with `DOCUMENTATION_INDEX.md` as the only current configured-base G1 blocker.

## PR provenance reconciliation

Current canonical base:

- `origin/main` / `eb3e3ff48905285812eca4c222fa2155a9282546` is the current base used by this repair.
- Recent merged Factory documentation/control-plane artifacts on `origin/main` include PR #115 (`MERGED`, merge commit `268d3c8ee7bab61304c7ab05cad22d693c70ba7d`) and the R2cy-R3 merge commit `eb3e3ff48905285812eca4c222fa2155a9282546`.

Stale or conflicting PR artifacts:

- PR #44 is the old R2ae PR for this same branch. GitHub readback before this rework: `OPEN`, non-draft, `agent:zeus`, base `main` at `b68ec8ad5cf986e5bf4900506820ca978ef0b0c0`, head `b2e643cc2aab681e682ecc7a8f1569bc79d1dd03`, `mergeStateStatus=DIRTY`. It is stale/conflicting against current `origin/main` and must be updated to the fresh candidate SHA from this run.
- PR #99 is `OPEN`, non-draft, `agent:zeus`, base `71e5e7b2f4ace3b081f9446483784a3c5fb0b981`, head `ead1aec54288123ff12c049bc4eb0f29d55d288b`; it is stale/conflicting review-route provenance, not current G1 document readiness.
- PR #114 is `OPEN`, non-draft, `agent:zeus`, base `5fe25cd7cb78d47afa156f8fde0c6a2c65f00a96`, head `fe0b6f80bfad296f78d3ab9a6ac79a31298bb243`, `mergeStateStatus=DIRTY`; it is a separate docs-first validator/control-plane candidate, not this current-base document repair.
- PR #36 remains the historical independent reviewed-G1 source evidence at head `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` with Factory gate `794`; it supports the reviewed markers but is not the current active candidate.

## Validation contract for this candidate

Required evidence after creating the final candidate commit:

1. `git diff --check origin/main..<candidate>` succeeds.
2. `git diff --name-only origin/main..<candidate>` is limited to `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md` and `factory/projects/zeus-alpha-research-ledger-core/R2AE_BOUNDED_CANONICAL_G1_VALIDATION.md`.
3. `git ls-tree -r --name-only <candidate>` contains all 14 required G1 documents and this R2ae evidence artifact.
4. GitHub PR #44 is updated to the fresh candidate SHA, remains non-draft, targets `main`, and has label `agent:zeus` plus a Zeus signature.
5. Factory status readback remains source-backed: before merge it is expected to show `DOCUMENTATION_INDEX.md` as the only current configured-base blocker; after authorized PR merge it should re-read the explicit `DOCUMENTATION_INDEX.md reviewed: yes` marker from `origin/main` and clear that row.

Signed-off-by: Zeus <zeus@sitiouno.com>

---
document_type: current_origin_main_g1_reconciliation_evidence
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2x-current-origin-main-g1-reconciliatio
phase: documentation
status: implemented
validated: yes
reviewed: pending_independent_review
owner: factory-reporter
base_ref: origin/main
current_origin_main_sha: b3c32d149d73156b75c15b5b357898b69737bed0
worktree_head_before_edit: b3c32d149d73156b75c15b5b357898b69737bed0
descends_from_current_origin_main_before_edit: yes
branch: factory/zeus-alpha-research-ledger-core/inc-036-r2x-current-origin-main-g1-reconcile
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-036-r2x-current-origin-main-g1-reconcile
factory_status_backend: agent_core_postgres
factory_status_database: zeus_agent
factory_status_base_ref: origin/main
factory_status_base_sha: b3c32d149d73156b75c15b5b357898b69737bed0
factory_status_blocking_required_g1_count: 0
factory_status_readiness_source: configured_base_ref
reviewed_marker_source_gate: factory_gate_794
reviewed_marker_source_pr: https://github.com/SiteOneTech/hermes-agent-original/pull/36
reviewed_marker_source_sha: c81547062c5362a7be6f5a1bb2ef9612b29bac9c
control_plane_review_gate: factory_gate_804
control_plane_review_pr: https://github.com/SiteOneTech/hermes-agent-original/pull/39
---

# R2x — current-origin/main G1 reconciliation rebase and reviewed-status recovery

## Scope

This is a bounded documentation reconciliation for the stale R2c/R2w reviewed-status drift. It records the current `origin/main` identity, proves the assigned worktree was already on the current canonical base before documentation edits, and binds the live Agent Core `factory.*` document-status read-back to the project-local G1 documents.

This artifact does not implement product/runtime code, does not merge, does not deploy, does not change credentials, does not use direct SQL, does not contact any external runtime, and does not authorize ALR-020+ to bypass task-specific TDD/security/QA gates.

## Current-base proof before documentation edit

Read-only git evidence from the assigned worktree after `git fetch origin main`:

| Check | Observed value |
|---|---|
| Worktree | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-036-r2x-current-origin-main-g1-reconcile` |
| Branch | `factory/zeus-alpha-research-ledger-core/inc-036-r2x-current-origin-main-g1-reconcile` |
| Remote | `https://github.com/SiteOneTech/hermes-agent-original.git` |
| Current `origin/main` | `b3c32d149d73156b75c15b5b357898b69737bed0` |
| HEAD before edits | `b3c32d149d73156b75c15b5b357898b69737bed0` |
| Merge base with `origin/main` | `b3c32d149d73156b75c15b5b357898b69737bed0` |
| Descends from current `origin/main` | `yes` |
| Worktree status after fetch | clean |

Because HEAD equaled current `origin/main`, no rebase rewrite was necessary. The proof above was captured before any R2x documentation-status claim or edit was recorded.

## Canonical Factory status read-back

Canonical source: Agent Core Postgres `factory.*`, read only through the approved Factory CLI path:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`

Observed status evidence:

| Field | Observed value |
|---|---|
| `db_backend` | `agent_core_postgres` |
| `database` | `zeus_agent` |
| `document_status[*].base_ref` | `origin/main` |
| `document_status[*].base_commit` | `b3c32d149d73156b75c15b5b357898b69737bed0` |
| `document_status[*].readiness_source` | `configured_base_ref` |
| Blocking required G1 documents | `0` |

The current canonical read-back marks every required G1 row `blocking=false`, `exists=true`, `indexed=true`, `committed=true`, `validated=true`, and `reviewed=true` from configured base ref `origin/main` at `b3c32d149d73156b75c15b5b357898b69737bed0`.

## Reconciled blocker list

The R2x assignment named ten stale blockers. Current canonical status reads each of them as reviewed and non-blocking from current `origin/main`:

| Previously reported blocker | Current `factory status` result | Project-local marker |
|---|---|---|
| `FACTORY_INTAKE.md` | `blocking=false`, `reviewed=true`, base `b3c32d149d73156b75c15b5b357898b69737bed0` | `reviewed: yes`, gate `794`, PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |
| `REQUIREMENTS_ANALYSIS.md` | `blocking=false`, `reviewed=true`, base `b3c32d149d73156b75c15b5b357898b69737bed0` | `reviewed: yes`, gate `794`, PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |
| `PATTERN_ANALYSIS.md` | `blocking=false`, `reviewed=true`, base `b3c32d149d73156b75c15b5b357898b69737bed0` | `reviewed: yes`, gate `794`, PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | `blocking=false`, `reviewed=true`, base `b3c32d149d73156b75c15b5b357898b69737bed0` | `reviewed: yes`, gate `794`, PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |
| `PRD.md` | `blocking=false`, `reviewed=true`, base `b3c32d149d73156b75c15b5b357898b69737bed0` | `reviewed: yes`, gate `794`, PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |
| `ADRS.md` | `blocking=false`, `reviewed=true`, base `b3c32d149d73156b75c15b5b357898b69737bed0` | `reviewed: yes`, gate `794`, PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |
| `METHODOLOGY_PLAN.md` | `blocking=false`, `reviewed=true`, base `b3c32d149d73156b75c15b5b357898b69737bed0` | `reviewed: yes`, gate `794`, PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |
| `TECHNICAL_BLUEPRINT.md` | `blocking=false`, `reviewed=true`, base `b3c32d149d73156b75c15b5b357898b69737bed0` | `reviewed: yes`, gate `794`, PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |
| `TASK_GRAPH.md` | `blocking=false`, `reviewed=true`, base `b3c32d149d73156b75c15b5b357898b69737bed0` | `reviewed: yes`, gate `794`, PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |
| `SECURITY_GATES.md` | `blocking=false`, `reviewed=true`, base `b3c32d149d73156b75c15b5b357898b69737bed0` | `reviewed: yes`, gate `794`, PR #36 `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` |

`DOCUMENTATION_INDEX.md`, `SPRINT_PLAN.md`, `TRACKER.md`, and `QA_GATES.md` also read back as `blocking=false` / `reviewed=true` from the same configured base ref. Therefore the assignment's stale blocker list is reconciled by current canonical evidence rather than by a new runtime/control-plane change.

## Independent evidence chain retained

- Machine-readable `reviewed: yes` markers remain supported by independent Factory gate `794`, reviewer `solution-architect`, against PR #36 exact head `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`.
- Source reviewed-docs evidence retained by that candidate remains Factory gate `790` / PR #34 SHA `2476e978c545e24b18ee48844b24eb8c58245ab4`.
- The current status read path was independently quality-reviewed in Factory gate `804` against PR #39 head `90fcb81abcebc203e16e34e36f4aec0ab1ec6a09`, which is now present behind current `origin/main` `b3c32d149d73156b75c15b5b357898b69737bed0`.

## R2x delivery rule

R2x creates only a Zeus-signed `agent:zeus` documentation PR from the assigned branch. The exact final PR head SHA is recorded in the PR and Factory gate evidence after commit/push; embedding that final SHA in this file before committing would necessarily change the SHA. No merge, deployment, credential change, direct SQL, product implementation, or external-runtime operation is authorized by this artifact.

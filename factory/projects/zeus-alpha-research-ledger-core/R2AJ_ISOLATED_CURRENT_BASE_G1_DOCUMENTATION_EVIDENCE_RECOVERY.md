---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2aj-isolated-current-base-g1-documentat
phase: documentation
status: implemented_pending_pr_handoff
validated: yes
reviewed: pending_independent_quality_review
owner: codex-builder
base_ref: origin/main
current_base_sha: bf422968f9ea73d70d4ac1e8b8bae4af644ce079
branch: factory/zeus-alpha-research-ledger-core/inc-017-r2aj-isolated-current-base-g1-do
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2aj-isolated-current-base-g1-do
factory_status_log: /home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786939834-4163626-ca90.log
pr_url: pending_pr_first_handoff
---

# R2aj — isolated current-base G1 documentation evidence recovery

## Scope

This artifact records the bounded R2aj documentation/provenance recovery for the still-reported `unvalidated_required_docs` anomaly. The work is limited to project-local Markdown under `factory/projects/zeus-alpha-research-ledger-core/`. It does not modify product/runtime code, Factory runtime code, the primary checkout, credentials, deployment state, external systems, connectors, messaging paths, trading/risk/paper/live paths, or `factory.*` rows by direct SQL.

## Canonical inputs read before edits

- Entry point and controlling index: `DOCUMENTATION_INDEX.md`.
- Factory-required G1 docs: `FACTORY_INTAKE.md`, `REQUIREMENTS_ANALYSIS.md`, `PATTERN_ANALYSIS.md`, `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, `PRD.md`, `ADRS.md`, `METHODOLOGY_PLAN.md`, `TECHNICAL_BLUEPRINT.md`, `SPRINT_PLAN.md`, `TASK_GRAPH.md`, `TRACKER.md`, `QA_GATES.md`, `SECURITY_GATES.md`, and `DOCUMENTATION_INDEX.md`.
- G0 and provenance docs: `G0_REPOSITORY_STRATEGY.md`, `G1_DOCUMENT_STATUS_TECHNICAL_RECOVERY.md`, `R2C2_AUTONOMOUS_CANONICAL_G1_DOCUMENTATION_STATUS_REPAIR.md`, and `R2AH_CURRENT_ORIGIN_G1_REVIEWED_MARKER_REPAIR.md`.
- Canonical Factory CLI status command, run from the assigned isolated worktree: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status --json zeus-alpha-research-ledger-core`; exit `0`; full output cached at `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786939834-4163626-ca90.log`.
- GitHub stale-PR readback: PR #44 remains open at head `768444e33ac64bf238e64c1df4c49fe2020b51a8` on branch `factory/zeus-alpha-research-ledger-core/inc-019-r2ae-bounded-canonical-g1-valida`; it is not the current-base R2aj candidate and is not used as evidence.

## Current-base branch/worktree identity

Captured before documentation edits after `git fetch origin main --prune` from the assigned worktree:

| Field | Value |
|---|---|
| timestamp_utc | `2026-08-17T04:13:48Z` |
| repo_root | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2aj-isolated-current-base-g1-do` |
| branch | `factory/zeus-alpha-research-ledger-core/inc-017-r2aj-isolated-current-base-g1-do` |
| local_head_before_edits | `bf422968f9ea73d70d4ac1e8b8bae4af644ce079` |
| origin_main_before_edits | `bf422968f9ea73d70d4ac1e8b8bae4af644ce079` |
| merge_base_before_edits | `bf422968f9ea73d70d4ac1e8b8bae4af644ce079` |
| ahead_behind_vs_origin_main | `0\t0` |
| remote | `https://github.com/SiteOneTech/hermes-agent-original.git` |
| remote_assigned_branch_before_push | absent from `git ls-remote origin refs/heads/factory/zeus-alpha-research-ledger-core/inc-017-r2aj-isolated-current-base-g1-do` |

Agent Core status also records the run-prepared worktree as `reason=worktree_created`, `base_ref=origin/main`, with this branch and cwd at log lines 20520–20529. The assigned branch was already a fresh current-base worktree at exact `origin/main`; no rebase, merge, force-push, primary-checkout mutation, scratch cleanup, direct SQL, deployment, credential, messaging, external-runtime, trading, risk, activation, or runtime operation was used to establish it.

## Canonical Agent Core document-status readback

The current dynamic `document_status` rows are non-blocking for every Factory-required G1 document at configured base `origin/main` `bf422968f9ea73d70d4ac1e8b8bae4af644ce079`:

| Required G1 document | Status-log lines | Current row result |
|---|---:|---|
| `FACTORY_INTAKE.md` | 19862–19884 | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false` |
| `REQUIREMENTS_ANALYSIS.md` | 19887–19909 | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false` |
| `PATTERN_ANALYSIS.md` | 19912–19934 | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false` |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | 19937–19959 | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false` |
| `PRD.md` | 19962–19984 | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false` |
| `ADRS.md` | 19987–20009 | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false` |
| `METHODOLOGY_PLAN.md` | 20012–20034 | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false` |
| `TECHNICAL_BLUEPRINT.md` | 20037–20059 | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false` |
| `SPRINT_PLAN.md` | 20062–20084 | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false` |
| `TASK_GRAPH.md` | 20087–20109 | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false` |
| `TRACKER.md` | 20112–20134 | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false` |
| `DOCUMENTATION_INDEX.md` | 20137–20159 | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false` |
| `QA_GATES.md` | 20162–20184 | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false` |
| `SECURITY_GATES.md` | 20187–20209 | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false` |

Each required row records `base_ref=origin/main`, `base_branch=main`, `base_commit=bf422968f9ea73d70d4ac1e8b8bae4af644ce079`, `readiness_source=configured_base_ref`, and `configured_base_ref_accepted=true`. The stale primary checkout is explicitly rejected as `primary_checkout_accepted=false`, `primary_checkout_rejected_reason=primary_checkout_not_configured_base`, with primary HEAD `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1` and primary path `/home/jean/Projects/hermes-agent-original`.

## Remaining source-backed cause if unresolved

The anomaly is not caused by current document content or missing reviewed markers. The status payload proves current row-level required-doc readiness is clear. The remaining source-backed cause is stale Factory control-plane/projection state that still names `unvalidated_required_docs` or `missing_or_unindexed_docs` outside the dynamic row source:

- Recent project reconciliation event `193741` still reports `metadata.anomalies=["unvalidated_required_docs"]` at log lines 455–482 while no reconciliation task is created in that event.
- Project metadata still records `reconciliation_anomalies=["unvalidated_required_docs"]` at log lines 20458–20460.
- Project metadata still carries obsolete `metadata.g1_documentation_checkout` at log lines 20425–20432: branch `factory/zeus-alpha-research-ledger-core/inc-011-alr-010-r2-pr-first-g1-reconciliation`, commit `dad375f27568c38be771fc597b579d087f034e1d`, PR #20, `not_merged=true`, and stale-primary reason `live_primary_checkout_cannot_be_fast_forwarded_while_Hermes_process_is_running`.
- Dispatch preflight event `193735` denies ALR-020 with blocker `missing_or_unindexed_docs` at log lines 605–620, which contradicts the current dynamic rows where every required G1 doc has `indexed=true` and `blocking=false`.

Therefore the bounded technical cause, if this remains unresolved after PR review, is a Factory control-plane/provenance mismatch: reconciliation/dispatch still consults persisted anomaly or stale checkout/projection metadata instead of recomputing required-doc readiness from the current dynamic `document_status` rows at the verified configured base. The authorized follow-up is a reviewed Factory control-plane repair through normal PR/gates or an approved canonical Factory CLI control path; no direct SQL, primary checkout mutation, deployment, credential access, external connector, messaging action, or trading/risk/paper/live operation is authorized by this documentation recovery.

## Documentation repair and PR-first handoff

R2aj reconstructs only the minimum project-local evidence for the current-base G1 documentation/provenance anomaly: this artifact, the documentation index, the task graph, the tracker, and the G1 QA/security gate notes. The machine-readable reviewed markers on the required G1 documents remain `reviewed: yes` and continue to cite the independent reviewed-docs source chain: PR #36 exact head `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`, Factory gate `794`, source gate `790`, and PR #34 SHA `2476e978c545e24b18ee48844b24eb8c58245ab4`.

The R2aj delivery must be a fresh non-draft GitHub PR against `main`, labeled `agent:zeus`, Zeus-signed, and independently reviewed against the exact final candidate SHA before downstream dispatch relies on this recovery. This worker must not self-approve, merge, deploy, change credentials, mutate the primary checkout, write direct SQL, or activate runtime/external/trading behavior.

---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2cx-current-origin-documentation-index-
run_id: run-1787101322-38d89701
phase: documentation
status: implemented_pending_pr_and_independent_exact_sha_review
validated: yes
reviewed: pending_independent_exact_sha_quality_review
owner: claude-builder
base_commit: b68ec8ad5cf986e5bf4900506820ca978ef0b0c0
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2cx-current-origin-documentatio
branch: factory/zeus-alpha-research-ledger-core/inc-001-r2cx-current-origin-documentatio
created_at: 2026-08-19T01:07:29Z
---

# R2cx — current-origin DOCUMENTATION_INDEX reviewed-state repair

## Scope and boundary

R2cx is a bounded documentation/provenance repair for the canonical G1 entrypoint, `DOCUMENTATION_INDEX.md`. It records the current-origin source-root readback, preserves stale-primary and stale-PR artifacts as audit provenance, and prepares a fresh Zeus-signed `agent:zeus` PR for independent exact-SHA review.

This increment changes only project-local documentation/provenance under `factory/projects/zeus-alpha-research-ledger-core/`. It does not change Agent Core product code, Factory runtime code, migrations, tools, schedulers, providers, credentials, external runtimes, messaging/connectors, deployment, primary-checkout state, task status, direct SQL, trading, risk, paper/live behavior, or ALR-020/product dispatch authority.

## G1 docs and sources consulted

Required entrypoint and applicable G1/control docs read before this repair:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/REQUIREMENTS_ANALYSIS.md`
- `factory/projects/zeus-alpha-research-ledger-core/PATTERN_ANALYSIS.md`
- `factory/projects/zeus-alpha-research-ledger-core/ASSUMPTIONS_AND_OPEN_QUESTIONS.md`
- `factory/projects/zeus-alpha-research-ledger-core/PRD.md`
- `factory/projects/zeus-alpha-research-ledger-core/ADRS.md`
- `factory/projects/zeus-alpha-research-ledger-core/METHODOLOGY_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/G1_REVIEW.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DB_CURRENT_ORIGIN_G1_REVIEWED_STATE_PR_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DC_BOUNDED_G1_REVIEWED_STATE_RECOVERY.md`

## Pre-edit source-root and status readbacks

The assigned worktree was fetched before edits and was exactly current `origin/main`:

```text
branch=factory/zeus-alpha-research-ledger-core/inc-001-r2cx-current-origin-documentatio
HEAD=b68ec8ad5cf986e5bf4900506820ca978ef0b0c0
origin_main=b68ec8ad5cf986e5bf4900506820ca978ef0b0c0
merge_base=b68ec8ad5cf986e5bf4900506820ca978ef0b0c0
ahead_behind=0 0
remote=https://github.com/SiteOneTech/hermes-agent-original.git
```

Allowed Agent Core Factory readback from the assigned worktree:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2cx-status-before.json
```

Readback facts:

```text
output=/tmp/r2cx-status-before.json
bytes=3701926
db_backend=agent_core_postgres
db_path=agent_core_postgres:zeus_agent.factory
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2cx-current-origin-documentatio
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2cx-current-origin-documentatio
factory_status_delegated=false
reconciliation_anomalies=[]
reconciliation_projection_source=current_document_status
reconciliation_required=false
g1_required_count=14
g1_blocking_count=0
DOCUMENTATION_INDEX.md exists=true committed=true indexed=true validated=true reviewed=true blocking=false readiness_source=configured_base_ref base_commit=b68ec8ad5cf986e5bf4900506820ca978ef0b0c0
```

The sanctioned stale-primary readback is retained only as discrepancy/audit evidence, not current configured-base truth:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2cx-status-primary-before.json
```

Primary-root facts:

```text
primary_checkout=/home/jean/Projects/hermes-agent-original
primary_branch=main
primary_head=4eb87e4cd48105af05fe974cf1d493f0e1b57ae1
primary_origin_main=b68ec8ad5cf986e5bf4900506820ca978ef0b0c0
primary_ahead_behind=3 2019
output=/tmp/r2cx-status-primary-before.json
bytes=3687688
metadata_reconciliation_anomalies=["unvalidated_required_docs"]
g1_required_count=14
g1_blocking_count=10
g1_blocking_docs=FACTORY_INTAKE.md,REQUIREMENTS_ANALYSIS.md,PATTERN_ANALYSIS.md,ASSUMPTIONS_AND_OPEN_QUESTIONS.md,PRD.md,ADRS.md,METHODOLOGY_PLAN.md,TECHNICAL_BLUEPRINT.md,TASK_GRAPH.md,SECURITY_GATES.md
DOCUMENTATION_INDEX.md exists=true committed=true indexed=true validated=true reviewed=true blocking=false
```

Therefore the live source-backed condition before this documentation repair is: current configured-base rows already show `DOCUMENTATION_INDEX.md` validated/reviewed/non-blocking, while the stale primary root still emits ten legacy blockers and does not identify `DOCUMENTATION_INDEX.md` as blocking. R2cx does not fabricate a document blocker or mutate G1 reviewed frontmatter. It records the mismatch and binds the current entrypoint state to fresh PR/gate evidence.

## Stale PR and predecessor artifacts retained

- PR #36 head `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` and Factory gate `794` remain the source review chain for the required G1 `reviewed: yes` markers, with source gate `790` / SHA `2476e978c545e24b18ee48844b24eb8c58245ab4`.
- PR #44 is still an open historical/stale R2ae artifact; GitHub readback now shows head `b2e643cc2aab681e682ecc7a8f1569bc79d1dd03`, no merge commit, and it is not current-base evidence for R2cx.
- PR #87 is merged R2db predecessor evidence: head `bd820a57818db852b07ef9c4c69085087c0c1c98`, merge commit `96f0cc70cf9b9da3a21dc1554673fbefdb5c1247`.
- PR #88 is merged R2dc predecessor evidence and current base source: head `20127ee4527e3d773e023420901c78e6a3f8f8b0`, merge commit/current `origin/main` `b68ec8ad5cf986e5bf4900506820ca978ef0b0c0`.

## Repair implemented

1. Added this project-local R2cx provenance artifact.
2. Updated `DOCUMENTATION_INDEX.md` so the canonical project index names the R2cx current-origin readback, the assigned branch/worktree, the exact base SHA, the stale-primary discrepancy, and the PR-first independent-review boundary.
3. Updated `TRACKER.md`, `QA_GATES.md`, `SECURITY_GATES.md`, and `TASK_GRAPH.md` with the R2cx gate/security/tracker provenance so reviewers can reconstruct the decision from repo docs plus Agent Core readbacks.
4. Preserved all required-document `reviewed: yes` frontmatter markers and did not change product/runtime implementation.

## Validation and review handoff

Required local validation before PR handoff:

```text
git diff --check
git diff --name-only origin/main...HEAD
git ls-files --error-unmatch factory/projects/zeus-alpha-research-ledger-core/R2CX_CURRENT_ORIGIN_DOCUMENTATION_INDEX_REVIEWED_STATE_REPAIR.md factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md factory/projects/zeus-alpha-research-ledger-core/TRACKER.md factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2cx-status-final.json
```

The final PR body and Factory gate evidence must name the immutable candidate SHA after the last push, because a commit cannot contain its own hash. Independent exact-SHA review must inspect that final candidate; this worker does not self-approve or merge.

## No-external-operation statement

R2cx used only the assigned worktree, project-local Markdown edits, Git/GitHub readbacks for the approved repository, Claude Code smoke/read-only review, and the sanctioned Factory CLI `status` / `gate record` paths. It did not deploy, merge to `main`, mutate the primary checkout, use direct SQL, access/change credentials, install packages, contact external runtimes, activate connectors/messaging, or perform Vonash/Magnus/VAOS/RAG/KB/broker/trading/risk/paper/live actions.

---
project_id: zeus-alpha-research-ledger-core
phase: documentation
status: pr_first_handoff
validated: yes
reviewed: pending_independent_security_review
owner: codex-builder
reviewer: security-reviewer
task_id: zeus-alpha-research-ledger-core-r2ai-r2-canonical-active-metadata-anomal
run_id: run-1787013644-88acf8f6
base_ref: origin/main
base_commit: c31e937111bba64e478d3c319e896774bf09e40e
source_of_truth: Agent Core Postgres factory.* via canonical Factory CLI
---

# R2ai-R2 canonical active-metadata anomaly repair

## Scope

This record closes the bounded documentation/control-plane increment for the stale structured reconciliation metadata on blocked R2ai. It repairs the project-local truth projection by separating:

1. current configured-base G1 document readiness from Agent Core Factory status;
2. active project-level reconciliation metadata; and
3. historical task/event-level stale anomaly rows that remain audit or rework provenance.

It does not alter product/runtime code, issue `reviewed: yes`, merge, deploy, force-push, rewrite any remote ref, mutate the primary checkout, access credentials, run direct SQL, or contact an external runtime.

## Canonical readbacks used

Only the allowed Factory DB commands were used:

- `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`
- `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory gate record ...`

The status snapshot is `/tmp/r2ai-r2-canonical-active-status-before.json`. It is the resolve-state projection readback for this increment because the hard execution rule for this task limited Factory DB access to `factory status` and `factory gate record` only.

## Worktree and base identity

Git evidence from the assigned worktree:

```text
branch=factory/zeus-alpha-research-ledger-core/inc-019-r2ai-r2-canonical-active-metadat
HEAD=c31e937111bba64e478d3c319e896774bf09e40e
origin_main=c31e937111bba64e478d3c319e896774bf09e40e
merge_base=c31e937111bba64e478d3c319e896774bf09e40e
remote branch before delivery: absent
```

The branch is a current-origin child of `origin/main` `c31e937111bba64e478d3c319e896774bf09e40e`; the remote branch did not exist before this delivery, so the push is a normal new-ref push, not a force rewrite.

## Agent Core backend and status-source readback

Canonical Factory status lines in `/tmp/r2ai-r2-canonical-active-status-before.json` record:

- Lines `450`-`451`: `database=zeus_agent`, `db_backend=agent_core_postgres`.
- Lines `8083`-`8085`: `factory_cli_source_root` and `factory_status_source_root` both equal the assigned worktree `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2ai-r2-canonical-active-metadat`; `factory_status_delegated=false`.
- Lines `21224`-`21227`: active project metadata reports `reconciliation_anomalies=[]`, `reconciliation_projection_source=current_document_status`, and `reconciliation_required=false`.

This is the active anomaly projection for the project. It is clean and sourced from current document status, not from stale task/event text.

## Current configured-base G1 document status

The active configured-base readback is `origin/main` `c31e937111bba64e478d3c319e896774bf09e40e`.

In `/tmp/r2ai-r2-canonical-active-status-before.json`, lines `20639`-`20989` list all 14 `g1_required` documents:

- `FACTORY_INTAKE.md`
- `REQUIREMENTS_ANALYSIS.md`
- `PATTERN_ANALYSIS.md`
- `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`
- `PRD.md`
- `ADRS.md`
- `METHODOLOGY_PLAN.md`
- `TECHNICAL_BLUEPRINT.md`
- `SPRINT_PLAN.md`
- `TASK_GRAPH.md`
- `TRACKER.md`
- `DOCUMENTATION_INDEX.md`
- `QA_GATES.md`
- `SECURITY_GATES.md`

Every row in that configured-base set records:

```text
base_ref=origin/main
base_commit=c31e937111bba64e478d3c319e896774bf09e40e
configured_base_ref_accepted=true
primary_checkout_accepted=false
primary_checkout_rejected_reason=primary_checkout_not_configured_base
primary_head=4eb87e4cd48105af05fe974cf1d493f0e1b57ae1
readiness_source=configured_base_ref
exists=true
committed=true
indexed=true
validated=true
reviewed=true
blocking=false
```

Therefore the current configured-base G1 status is non-blocking. No document frontmatter change is required and no `reviewed` field is changed by this increment.

## Residual task-level stale source

The false/stale projection is not the active project anomaly list. It is the historical R2ai task row.

`/tmp/r2ai-r2-canonical-active-status-before.json` lines `31089`-`31117` record the exact task-level source:

```text
task_id=zeus-alpha-research-ledger-core-r2ai-current-origin-g1-independent-revie
status=blocked
evidence_status=missing
metadata.blocker_source=structured_reconciliation_metadata
metadata.reconciliation_anomaly=unvalidated_required_docs
metadata.resolved_anomaly=unvalidated_required_docs
metadata.last_blocker_classification.action_category=technical_rework
metadata.last_blocker_classification.blocker_category=technical
metadata.last_blocker_classification.requires_human=false
metadata.unblock_reason=resolved_reconciliation_anomaly
metadata.unblocked_by=factory-orchestrator
```

That task row is stale structured reconciliation metadata from the earlier R2ai/R2ai-R1 path. It must remain fail-closed as a historical blocked task until a reviewed control-plane update clears or supersedes it through the approved Factory path. It is not current G1 document content and must not be projected as an active configured-base G1 blocker.

Related stale audit rows are also visible, but they are not the current R2ai-R2 repair target:

- R2ae stale/conflicting task metadata at lines `31347`-`31381` also carries `blocker_source=structured_reconciliation_metadata` and `reconciliation_anomaly=unvalidated_required_docs`.
- The cancelled reconciliation task at lines `32664`-`32882` retains old ten-row `reviewed=false` snapshots and `metadata.g1_documentation_checkout` provenance as audit history.
- Unrelated R2ac technical rework remains a separate blocked task and is not a current G1 document-status blocker for this increment.

## Repair performed in this branch

The project-local repair is documentary/control-plane evidence only:

- Add this artifact as the canonical R2ai-R2 active-metadata repair record.
- Index it in `DOCUMENTATION_INDEX.md`.
- Add the exact status/readback requirements and fail-closed boundaries to `QA_GATES.md` and `SECURITY_GATES.md`.
- Update `TASK_GRAPH.md`, `TRACKER.md`, and `G1_REVIEW.md` so the active projection is truthful: project-level `reconciliation_anomalies=[]`; stale R2ai task metadata is residual task-level provenance; independent security review remains required.

This removes the false project-local projection that the old R2ai task metadata is a current configured-base G1 docs blocker. It does not silently clear the blocked R2ai task, does not convert historical audit evidence into approval, and does not weaken fail-closed behavior.

## Validation evidence

Pre-PR validation for this branch must include:

```text
git diff --check
git diff --name-only origin/main...HEAD
git ls-files --error-unmatch factory/projects/zeus-alpha-research-ledger-core/R2AI_R2_CANONICAL_ACTIVE_METADATA_ANOMALY_REPAIR.md
git ls-files --error-unmatch factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md factory/projects/zeus-alpha-research-ledger-core/TRACKER.md factory/projects/zeus-alpha-research-ledger-core/G1_REVIEW.md
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json
```

Expected result: diff limited to project-local Factory documentation/control-plane evidence; no product/runtime code; status readback remains `agent_core_postgres`, base `c31e937111bba64e478d3c319e896774bf09e40e`, 14/14 G1 required rows non-blocking, active project `reconciliation_anomalies=[]`, residual R2ai blocker sourced only to task-level stale structured metadata.

## PR-first handoff

Delivery must be a fresh non-draft GitHub PR against `main`, labeled `agent:zeus`, with Zeus signature and exact final head SHA. The PR is the handoff for independent exact-SHA security review.

Security review must inspect the final PR head before terminal acceptance. Until that review passes, this repair is not downstream implementation authority and does not unblock product/runtime work by itself.

## Boundary statement

No product implementation, Factory runtime code, direct SQL, credentials, deployment, primary-checkout mutation, force-push/ref rewrite, merge, external runtime/contact, messaging connector, trading, risk, paper/live activation, or `reviewed=yes` change was performed by this increment.

---
document_type: canonical_g1_evidence_repair
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2bl-non-destructive-canonical-g1-eviden
phase: documentation
status: pr_first_review_pending
validated: yes
reviewed: pending
owner: codex-builder
base_ref: origin/main
base_sha: faddaf5afb4c1754e03d8c97dd6706353b5b0865
branch: factory/zeus-alpha-research-ledger-core/inc-001-r2bl-non-destructive-canonical-g
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2bl-non-destructive-canonical-g
pr_url: PENDING_R2BL_PR_URL
---

# R2bl — non-destructive canonical G1 evidence repair

## Scope

R2bl is a bounded documentation/evidence repair for the current Factory G1
`unvalidated_required_docs` projection on project
`zeus-alpha-research-ledger-core`. The work starts from current `origin/main`
`faddaf5afb4c1754e03d8c97dd6706353b5b0865` in the assigned isolated worktree
and changes only project-local Factory evidence/validation files under
`factory/projects/zeus-alpha-research-ledger-core/`.

This increment does not implement Alpha Research Ledger runtime code and does
not close/supersede historical Factory tasks. It records the source-backed
current-base evidence, validates it with a deterministic project-local command,
opens a fresh Zeus-signed PR, and requires independent exact-PR/SHA quality and
security review through canonical Factory gates.

## Immutable base and branch evidence

- Assigned worktree:
  `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2bl-non-destructive-canonical-g`
- Assigned branch:
  `factory/zeus-alpha-research-ledger-core/inc-001-r2bl-non-destructive-canonical-g`
- Fresh base evidence before edits:
  `HEAD = origin/main = merge-base = faddaf5afb4c1754e03d8c97dd6706353b5b0865`.
- Remote branch preflight: `git ls-remote --heads origin
  factory/zeus-alpha-research-ledger-core/inc-001-r2bl-non-destructive-canonical-g`
  returned no ref, so delivery is a normal first push rather than a rewrite.
- Primary checkout remains stale/rejected identity evidence only:
  `/home/jean/Projects/hermes-agent-original` at
  `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`; it was not mutated.

## Canonical Factory status readback

Approved command, from the assigned worktree:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2bl-status-before.json
```

Readback summary from `/tmp/r2bl-status-before.json`:

- `db_backend=agent_core_postgres`, `database=zeus_agent`.
- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2bl-non-destructive-canonical-g`.
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2bl-non-destructive-canonical-g`.
- `factory_status_delegated=false`.
- 14/14 Factory-required G1 rows are `exists=true`, `committed=true`,
  `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false`.
- Every required row is from `readiness_source=configured_base_ref`,
  `base_ref=origin/main`, `base_commit=faddaf5afb4c1754e03d8c97dd6706353b5b0865`,
  `configured_base_ref_accepted=true`.
- Stale primary checkout is rejected on every row with
  `primary_checkout_accepted=false` and
  `primary_checkout_rejected_reason=primary_checkout_not_configured_base`.
- Active project metadata is clean for G1 docs:
  `reconciliation_anomalies=[]`,
  `reconciliation_projection_source=current_document_status`,
  `reconciliation_required=false`, `notion_required=false`, and no active
  `g1_documentation_checkout` / `stale_reconciliation_projection`.

## Exact residual source of the stale anomaly

The current configured-base document rows are not the blocker source. The
remaining source-backed `unvalidated_required_docs` strings are audit/control
projection records from old tasks/events:

1. Active blocked task
   `zeus-alpha-research-ledger-core-r2ai-current-origin-g1-independent-revie`
   still carries `metadata.blocker_source=structured_reconciliation_metadata`,
   `metadata.reconciliation_anomaly=unvalidated_required_docs`, and
   `metadata.resolved_anomaly=unvalidated_required_docs`.
2. Active blocked task
   `zeus-alpha-research-ledger-core-r2ae-bounded-canonical-g1-validation-and`
   carries the same structured residual metadata.
3. Recent `project_reconciled` events still report
   `metadata.anomalies=["unvalidated_required_docs"]`, and event `197858`
   reports dispatch preflight blocker `missing_or_unindexed_docs` for a product
   task, while the current project metadata and row-level document status are
   already clean.

Those records are retained as fail-closed audit history. R2bl does not run
`factory task close`, does not mutate task status, and does not delete or SQL-edit
audit provenance. Any future closure/supersession requires an explicitly
authorized canonical Factory control path with source-backed readback.

## Deterministic validation command

Project-local validator added by this increment:

```bash
python3 factory/projects/zeus-alpha-research-ledger-core/validate_r2bl_g1_evidence.py \
  --status-json /tmp/r2bl-status-before.json \
  --expected-base faddaf5afb4c1754e03d8c97dd6706353b5b0865 \
  --expected-head <final-pr-head-sha> \
  --expected-pr PENDING_R2BL_PR_URL \
  --expected-quality-gate <quality-gate-id> \
  --expected-security-gate <security-gate-id>
```

RED before repair was observed immediately after adding the validator and before
adding this artifact/index/gate/tracker evidence: it returned
`R2BL_G1_EVIDENCE_VALIDATION=FAIL` because the R2bl artifact and required
markers/gates were absent. GREEN is expected only after the fresh PR exists and
independent exact-SHA quality/security gates are present in canonical Factory
status for the final pushed head.

## Delivery and review contract

- Required PR: `PENDING_R2BL_PR_URL` (non-draft, label `agent:zeus`, base
  `main`, Zeus signed-off commit).
- The exact final pushed head SHA is recorded in the PR body and the canonical
  Factory quality/security gate notes after push, because a commit cannot
  contain its own immutable SHA.
- Independent exact-SHA quality review must be recorded by `quality-reviewer`.
- Independent exact-SHA security review must be recorded by `security-reviewer`.
- This artifact is not self-approval and does not authorize a merge.

## No external operation boundary

This increment is documentation/evidence only: no merge, no direct SQL, no
primary-checkout mutation, no force-push, no external runtime, no ALR-020/product
dispatch, no deploy, no credential access/change, no connector/messaging action,
no task-status mutation, and no trading/risk/paper/live action.

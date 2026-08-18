---
document_type: non_destructive_current_base_g1_evidence_recovery
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2az-non-destructive-current-base-g1-evi
phase: documentation
status: implemented_pending_independent_quality_review
validated: yes
reviewed: pending_independent_quality_review
owner: codex-builder
engine: codex
run_id: run-1787026730-8cb835cf
base_ref: origin/main
base_sha: 3b7bc91f2ee1ef603bb512d147c692568c1b465f
branch: factory/zeus-alpha-research-ledger-core/inc-017-r2az-non-destructive-current-bas
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2az-non-destructive-current-bas
canonical_factory_status_json_before: /tmp/r2az-status-before.json
canonical_factory_status_json_after_docs: /tmp/r2az-status-after-docs.json
candidate_sha: recorded_in_pr_and_factory_gate_after_final_push
---

# R2az — non-destructive current-base G1 evidence recovery

## Scope and boundary

This increment performs the bounded R2az recovery for the still-reported
`unvalidated_required_docs` / G1 evidence condition on project
`zeus-alpha-research-ledger-core`.

The repair is documentation/evidence only. It is limited to project-local files
under `factory/projects/zeus-alpha-research-ledger-core/` and preserves the
existing G1 `reviewed: yes` markers exactly as inherited from PR #36 / Factory
gate `794` and source gate `790` / SHA
`2476e978c545e24b18ee48844b24eb8c58245ab4`.

No product/runtime code, Factory runtime code, primary checkout state,
credentials, providers, external runtimes, Vonash, Magnus, VAOS, RAG/KB,
brokers, trading, risk, paper/live activation, deployment, messaging, direct
SQL/psql/psycopg2/ad-hoc database script, rebase, merge, force-push, reset, or
existing remote-ref rewrite is authorized or performed by this increment.

## Canonical inputs read

Read before documentation repair:

- `DOCUMENTATION_INDEX.md` — required G1 entrypoint, controlling status,
  supplemental artifacts, status semantics, and reading order.
- Required G1 docs: `FACTORY_INTAKE.md`, `REQUIREMENTS_ANALYSIS.md`,
  `PATTERN_ANALYSIS.md`, `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, `PRD.md`,
  `ADRS.md`, `METHODOLOGY_PLAN.md`, `TECHNICAL_BLUEPRINT.md`,
  `SPRINT_PLAN.md`, `TASK_GRAPH.md`, `TRACKER.md`, `DOCUMENTATION_INDEX.md`,
  `QA_GATES.md`, and `SECURITY_GATES.md`.
- Control/traceability docs: `G0_REPOSITORY_STRATEGY.md`,
  `REQUIREMENTS_TRACEABILITY.md`, `DATABASE_AND_RUNTIME_CONTRACT.md`, and
  `G1_REVIEW.md`.
- Recent provenance artifacts: `R2CN_BOUNDED_CANONICAL_G1_DOCS_GATE_AND_PR_PROVENANCE_REPAIR.md`,
  `R2AI_R2_NON_DESTRUCTIVE_CURRENT_ORIGIN_G1_RECOVERY.md`,
  `R2AP_PR72_RESIDUAL_G1_TASK_METADATA_RECONCILIATION.md`,
  `R2AS_R2_INDEPENDENT_EXACT_SHA_G1_SOURCE_SELECTION_REVIEW.md`, and
  `R2AX_CURRENT_ORIGIN_FACTORY_CLI_G1_RECOVERY_DISPATCH.md`.
- Canonical Factory DB readback through the only allowed command class for this
  run: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`.

## Fresh current-base worktree identity

Read-only Git evidence after `git fetch origin main --prune`, before edits:

```text
timestamp_utc = 2026-08-18T04:22:43Z
worktree = /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2az-non-destructive-current-bas
branch = factory/zeus-alpha-research-ledger-core/inc-017-r2az-non-destructive-current-bas
HEAD = 3b7bc91f2ee1ef603bb512d147c692568c1b465f
origin/main = 3b7bc91f2ee1ef603bb512d147c692568c1b465f
remote refs/heads/main = 3b7bc91f2ee1ef603bb512d147c692568c1b465f
merge-base(HEAD, origin/main) = 3b7bc91f2ee1ef603bb512d147c692568c1b465f
ahead/behind vs origin/main = 0 / 0
assigned remote branch before push = absent
origin = https://github.com/SiteOneTech/hermes-agent-original.git
```

This establishes a fresh isolated current-base branch. The stale R2ai/R2ae/R2ac
remote refs and PRs are not reused, rebased, reset, force-pushed, or otherwise
mutated.

## Canonical Factory status readback

Command executed from the assigned worktree:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2az-status-before.json
```

Result: exit `0`, Agent Core Postgres (`db_backend=agent_core_postgres`,
`database=zeus_agent`) with source-root provenance equal to the assigned
worktree and `factory_status_delegated=false`.

Current configured-base G1 rows in `/tmp/r2az-status-before.json`:

```text
g1_required_count=14
g1_blocking_count=0
base_commit=3b7bc91f2ee1ef603bb512d147c692568c1b465f
readiness_source=configured_base_ref
configured_base_ref_accepted=true
primary_checkout_accepted=false
primary_checkout_rejected_reason=primary_checkout_not_configured_base
primary_head=4eb87e4cd48105af05fe974cf1d493f0e1b57ae1
```

Every required row reports `exists=true`, `committed=true`, `indexed=true`,
`validated=true`, `reviewed=true`, and `blocking=false`:

```text
FACTORY_INTAKE.md
REQUIREMENTS_ANALYSIS.md
PATTERN_ANALYSIS.md
ASSUMPTIONS_AND_OPEN_QUESTIONS.md
PRD.md
ADRS.md
METHODOLOGY_PLAN.md
TECHNICAL_BLUEPRINT.md
SPRINT_PLAN.md
TASK_GRAPH.md
TRACKER.md
DOCUMENTATION_INDEX.md
QA_GATES.md
SECURITY_GATES.md
```

Current effective project metadata in the same status payload is clean for G1:

```text
reconciliation_anomalies=[]
reconciliation_projection_source=current_document_status
reconciliation_required=false
notion_required=false
notion_sync_required=false
notion_workflow_disabled=true
pr_first_required=true
factory_auto_integration_forbidden=true
```

Therefore the current configured-base G1 document pack is not missing,
unindexed, unvalidated, or unreviewed.

## Exact remaining G1 evidence condition

The current-base deficit is an evidence/projection mismatch outside the dynamic
G1 document rows:

1. Recent Factory events still reported stale `unvalidated_required_docs` even
   after current row-level G1 readiness is clean:
   - event `197638`, `project_reconciled`, `2026-08-18T04:18:33.531987+00:00`,
     `metadata.anomalies=["unvalidated_required_docs"]`;
   - event `197637`, `project_reconciled`, `2026-08-18T04:18:18.914290+00:00`,
     same anomaly;
   - event `197635`, `project_reconciled`, `2026-08-18T04:17:05.629854+00:00`,
     same anomaly.
2. Recent dispatch preflight still denied product execution with stale
   docs-first wording:
   - event `197634`, `dispatch_preflight_denied`, task
     `zeus-alpha-research-ledger-core-alr-020-r2-bounded-pr-first-signature-an`,
     `metadata.blockers=["missing_or_unindexed_docs"]`.
3. Canonical task readback still has two old blocked rows carrying structured
   `unvalidated_required_docs` metadata:
   - `zeus-alpha-research-ledger-core-r2ai-current-origin-g1-independent-revie`
     is `blocked` with `blocker_source=structured_reconciliation_metadata`,
     `reconciliation_anomaly=unvalidated_required_docs`, and
     `resolved_anomaly=unvalidated_required_docs`;
   - `zeus-alpha-research-ledger-core-r2ae-bounded-canonical-g1-validation-and`
     is `blocked` with the same structured anomaly plus historical
     `increment_integration_status=failed` from merge conflicts in
     `DOCUMENTATION_INDEX.md`, `QA_GATES.md`, `TASK_GRAPH.md`, and `TRACKER.md`.
4. The separate blocked R2ac task remains technical rework but carries no
   `reconciliation_anomaly` in current status readback.

Source-backed conclusion: current-base G1 documents are clean at
`origin/main` `3b7bc91f2ee1ef603bb512d147c692568c1b465f`; the remaining
`unvalidated_required_docs` / `missing_or_unindexed_docs` evidence is stale
event/task-level projection tied to old R2ai/R2ae/R2ac history and PR/ref
provenance, not a current document-content defect. This R2az repair records the
current-base evidence without mutating stale remote refs, stale PRs, old blocked
task status, or the primary checkout.

## Documentation repair

This branch makes the current-base R2az evidence independently reviewable by:

1. Adding this artifact with immutable branch/base/status/event/task evidence and
   explicit non-destructive boundaries.
2. Updating `DOCUMENTATION_INDEX.md`, `G1_REVIEW.md`, `TASK_GRAPH.md`,
   `TRACKER.md`, `QA_GATES.md`, and `SECURITY_GATES.md` so reviewers do not
   infer the current G1 state from stale R2ai/R2ae/R2ac refs, PRs, or events.
3. Preserving every existing required-document `reviewed` field and its reviewed
   provenance unchanged.

No follow-up task is created by this worker because the documentation evidence
repair is possible non-destructively in this fresh branch and this run's hard DB
write allowlist permits only `factory status` and `factory gate record`. If a
later closure action must change the old R2ai/R2ae task states, that requires a
separately authorized canonical task-close or reconciler path; `factory gate
record` cannot change task status.

## Validation contract

Executed before PR handoff:

```text
git diff --check
Result: exit 0

HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'document_status_uses_configured_origin_base_when_primary_checkout_stale or document_status_rejects_stale_primary_even_when_primary_docs_are_ready or status_projection_uses_origin_base_not_stale_head_or_task_metadata' -v --tb=short
Result: exit 0, 3 tests passed, 0 failed

/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2az-status-after-docs.json
Result: exit 0
db_backend=agent_core_postgres
database=zeus_agent
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2az-non-destructive-current-bas
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2az-non-destructive-current-bas
factory_status_delegated=false
project_status=active
reconciliation_anomalies=[]
reconciliation_projection_source=current_document_status
g1_required_count=14
g1_blocking_count=0
base_commits=["3b7bc91f2ee1ef603bb512d147c692568c1b465f"]
readiness_sources=["configured_base_ref"]
all_required_ready=true
```

Required final PR/gate handoff:

- Changed files tracked and confined to
  `factory/projects/zeus-alpha-research-ledger-core/`.
- PR is non-draft, labeled `agent:zeus`, normally pushed from this fresh branch,
  and records exact base, head SHA, ancestry, G1 validation and gate readback.
- No self-approval, merge, deployment, direct SQL, primary-checkout mutation,
  force-push/ref rewrite, external runtime, credential, connector/messaging,
  trading/risk/paper/live action, or ALR-020/product dispatch.

## Handoff

Open a Zeus-signed, `agent:zeus` GitHub PR from branch
`factory/zeus-alpha-research-ledger-core/inc-017-r2az-non-destructive-current-bas`
to `main`. The PR body and Factory gate evidence must name exact source/base
commit `3b7bc91f2ee1ef603bb512d147c692568c1b465f`, exact final candidate SHA
after push, current branch provenance, validation commands, G1 status readback,
recent stale event/task condition, and the no-merge/no-direct-SQL/no-primary-
mutation/no-force-push/no-external-runtime boundary. Independent exact-SHA
quality review remains required before downstream dispatch relies on this
recovery.

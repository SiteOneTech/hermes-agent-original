---
document_type: canonical_g1_review_state_source_root_repair
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2bn-canonical-g1-review-state-source-ro
phase: documentation
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending
owner: claude-builder
base_ref: origin/main
base_sha: 9ebaa9e7b44c61bb871ca4da0a838c52e62666b2
branch: factory/zeus-alpha-research-ledger-core/inc-018-r2bn-canonical-g1-review-state-s
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2bn-canonical-g1-review-state-s
run_id: run-1787046385-072b3cc6
pr_url: pending_after_first_push
---

# R2bn — canonical G1 review-state source-root repair

## Scope

R2bn is a bounded documentation/evidence repair for the active G1 review-state
source-root disagreement on project `zeus-alpha-research-ledger-core`. It does
not implement Alpha Research Ledger product/runtime functionality and does not
authorize ALR-020/product dispatch.

This increment changes only project-local evidence, gate documentation, tracker
state, and a deterministic validator under
`factory/projects/zeus-alpha-research-ledger-core/`.

No merge, no direct SQL, no primary-checkout mutation, no force-push, no
external runtime, no deploy, no credential access/change, no connector or
messaging action, no trading/risk/paper/live action, and no ALR-020/product
dispatch are authorized by this increment.

## Evidence consulted

- `DOCUMENTATION_INDEX.md`
- `FACTORY_INTAKE.md`
- `G0_REPOSITORY_STRATEGY.md`
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
- `QA_GATES.md`
- `SECURITY_GATES.md`
- `REQUIREMENTS_TRACEABILITY.md`
- `DATABASE_AND_RUNTIME_CONTRACT.md`
- `R2BM_CANONICAL_G1_DOCS_GATE_SOURCE_ROOT_RECOVERY.md`
- Canonical status snapshot: `/tmp/r2bn-status-before.json`
- Claude Code read-only planning/review session:
  `00a75930-1de0-4b3e-8ccd-eba19748bbc2`

## Current-base identity

Before this documentation repair, the assigned isolated worktree was fetched and
verified read-only:

```text
branch=factory/zeus-alpha-research-ledger-core/inc-018-r2bn-canonical-g1-review-state-s
worktree=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2bn-canonical-g1-review-state-s
HEAD=9ebaa9e7b44c61bb871ca4da0a838c52e62666b2
origin/main=9ebaa9e7b44c61bb871ca4da0a838c52e62666b2
```

`9ebaa9e7b44c61bb871ca4da0a838c52e62666b2` is the current configured base
created by the R2bm integration. Agent Core readback shows R2bm task metadata
with base-before `42c86619b91b3a290462c9582e81499e7de8c4c4`, branch head
`06051d990821bc7127004313ca3458e0394832d8`, base-after
`9ebaa9e7b44c61bb871ca4da0a838c52e62666b2`, quality gate `925`, and
implementation gate `926`.

## Canonical status readback

The allowed Factory DB readback used only the canonical venv CLI from this
assigned worktree source root:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main \
  factory status zeus-alpha-research-ledger-core --json \
  > /tmp/r2bn-status-before.json
```

`/tmp/r2bn-status-before.json` summary:

- `db_backend=agent_core_postgres`, `database=zeus_agent`.
- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2bn-canonical-g1-review-state-s`.
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2bn-canonical-g1-review-state-s`.
- `factory_status_delegated=false`.
- `reconciliation_anomalies=[]`.
- `reconciliation_projection_source=current_document_status`.
- `reconciliation_required=false`.
- `g1_rows=14`, `g1_blockers=0`.
- All 14/14 required G1 rows have
  `exists/committed/indexed/validated/reviewed=true`, `blocking=false`,
  `readiness_source=configured_base_ref`, `base_ref=origin/main`, and
  `base_commit=9ebaa9e7b44c61bb871ca4da0a838c52e62666b2`.
- The stale primary checkout is rejected for every row with
  `primary_checkout_accepted=false` and
  `primary_checkout_rejected_reason=primary_checkout_not_configured_base`.

This proves the current required-document review state is clean when the
Factory status source root is the assigned current-base worktree.

## Reproduced stale review-state source

The current run prompt still reported the stale ten-row review-state blocker:
`G1 readiness: 12/22 documentos sin blocker; blockers=10`, with the same ten
required G1 documents marked `missing=reviewed`:

- `FACTORY_INTAKE.md`
- `REQUIREMENTS_ANALYSIS.md`
- `PATTERN_ANALYSIS.md`
- `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`
- `PRD.md`
- `ADRS.md`
- `METHODOLOGY_PLAN.md`
- `TECHNICAL_BLUEPRINT.md`
- `TASK_GRAPH.md`
- `SECURITY_GATES.md`

That prompt projection is not current document content. The canonical status
snapshot above reports those exact documents reviewed and non-blocking from the
assigned source root at current `origin/main`.

The residual stale source is now isolated to historical/blocked control-plane
evidence:

- R2ai task
  `zeus-alpha-research-ledger-core-r2ai-current-origin-g1-independent-revie`
  remains `blocked` with
  `blocker_source=structured_reconciliation_metadata` and
  `reconciliation_anomaly=unvalidated_required_docs`; security gate `927`
  failed because its branch was stale and had no current PR.
- R2ae task
  `zeus-alpha-research-ledger-core-r2ae-bounded-canonical-g1-validation-and`
  remains `blocked` with
  `blocker_source=structured_reconciliation_metadata`,
  `reconciliation_anomaly=unvalidated_required_docs`, and a recorded failed
  integration conflict; quality gate `928` failed stale PR #44 as conflicting
  against current `origin/main` and reported a canonical ten-row stale-primary
  readback in its notes.
- Historical `project_reconciled` events may still mention
  `unvalidated_required_docs` or `missing_or_unindexed_docs`; those strings are
  audit/projection history only when current configured-base rows are clean.

R2bn does not close, supersede, clear, or mutate those old task rows. The only
allowed Factory DB write surface for this run is `factory gate record`; no
`factory task close`, no `factory project resolve-state`, no direct SQL, no
`psql`, no `psycopg2`, and no ad-hoc database script are authorized.

## Reviewer source-root instruction

Any R2bn reviewer must reproduce G1 readiness from the assigned current-base
worktree, not from the stale primary checkout:

```bash
cd /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2bn-canonical-g1-review-state-s
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main \
  factory status zeus-alpha-research-ledger-core --json
```

The review must first verify:

- `factory_cli_source_root` equals the R2bn worktree.
- `factory_status_source_root` equals the R2bn worktree.
- `factory_status_delegated=false`.
- All 14 required G1 rows are non-blocking from `configured_base_ref` at
  base `9ebaa9e7b44c61bb871ca4da0a838c52e62666b2`.

A stale-primary readback that reports 10/14 `reviewed=false` rows is the defect
being documented; it is not valid current readiness evidence for this task.

## Deterministic validation

R2bn adds `validate_r2bn_g1_evidence.py` so the repair can be checked without
writing to Factory DB. The validator reads a canonical Factory status JSON and
this committed Markdown pack. It fails until a real PR URL, exact final head,
and independent quality gate are provided, so the committed evidence cannot
self-approve.

Expected final invocation after PR push and gate recording:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 \
  factory/projects/zeus-alpha-research-ledger-core/validate_r2bn_g1_evidence.py \
  --project-dir . \
  --status-json /tmp/r2bn-status-final.json \
  --expected-base 9ebaa9e7b44c61bb871ca4da0a838c52e62666b2 \
  --expected-head <final-pr-head-sha> \
  --expected-pr <r2bn-pr-url> \
  --expected-quality-gate <quality-gate-id>
```

## PR-first handoff

R2bn must be delivered by a normal Zeus-signed, non-draft `agent:zeus` PR from
branch
`factory/zeus-alpha-research-ledger-core/inc-018-r2bn-canonical-g1-review-state-s`.

The exact final PR head SHA and the independent quality gate are recorded in the
PR body and Factory gate notes after push, because a commit cannot contain its
own immutable SHA. The PR URL is updated in this artifact after the first push
when GitHub assigns it.

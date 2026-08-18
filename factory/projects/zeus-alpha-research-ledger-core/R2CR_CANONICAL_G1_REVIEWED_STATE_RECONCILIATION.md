---
document_type: canonical_g1_reviewed_state_reconciliation
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2cr-canonical-g1-reviewed-state-reconci
phase: documentation
status: pr_first_candidate_pending_independent_review
validated: yes
reviewed: pending_exact_sha_review
owner: claude-builder
base_ref: origin/main
base_sha: 0db9bed7ed9e8ec4dbefda41f95a335ab82fbbc0
branch: factory/zeus-alpha-research-ledger-core/inc-017-r2cr-canonical-g1-reviewed-state
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2cr-canonical-g1-reviewed-state
run_id: run-1787049536-cdce53bc
pr_url: pending_after_first_push
canonical_status_json: /tmp/r2cr-status-before.json
canonical_status_bytes: 3079912
canonical_status_command: /home/jean/Projects/hermes-agent-original/venv/bin/hermes factory status zeus-alpha-research-ledger-core --json
---

# R2cr — canonical G1 reviewed-state reconciliation

## Scope

R2cr is a bounded documentation/provenance recovery for the active
`unvalidated_required_docs` anomaly after R2bn reached `origin/main`. It does
not implement Alpha Research Ledger product/runtime code and does not authorize
ALR-020 or any downstream runtime dispatch.

This candidate updates only project-local Factory documentation/provenance under
`factory/projects/zeus-alpha-research-ledger-core/`. It does not change product
runtime code, Factory runtime code, tests outside this project pack, credentials,
connectors, deployments, external runtimes, trading/risk/paper/live behavior, or
Factory task status.

No merge, no direct SQL, no primary-checkout mutation, no force-push/ref rewrite,
no stale PR/task mutation, no `factory project resolve-state`, no `factory task
close`, no external runtime execution, and no ALR-020/product dispatch are
authorized by this increment.

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
- `G1_REVIEW.md`
- `R2BN_CANONICAL_G1_REVIEW_STATE_SOURCE_ROOT_REPAIR.md`
- Canonical Agent Core Factory status snapshot: `/tmp/r2cr-status-before.json`
- GitHub PR #80 readback for prior R2bn evidence:
  `https://github.com/SiteOneTech/hermes-agent-original/pull/80`

## Current-base identity

Before documentation edits, the assigned isolated worktree was fetched and
verified read-only:

```text
branch=factory/zeus-alpha-research-ledger-core/inc-017-r2cr-canonical-g1-reviewed-state
worktree=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2cr-canonical-g1-reviewed-state
HEAD=0db9bed7ed9e8ec4dbefda41f95a335ab82fbbc0
origin/main=0db9bed7ed9e8ec4dbefda41f95a335ab82fbbc0
merge-base=0db9bed7ed9e8ec4dbefda41f95a335ab82fbbc0
```

`0db9bed7ed9e8ec4dbefda41f95a335ab82fbbc0` is the R2bn merge commit on
`origin/main`. GitHub readback for PR #80 reports:

```text
state=MERGED
baseRefName=main
baseRefOid=9ebaa9e7b44c61bb871ca4da0a838c52e62666b2
headRefName=factory/zeus-alpha-research-ledger-core/inc-018-r2bn-canonical-g1-review-state-s
headRefOid=5dcf7d14746457148b045e2ed94aed6114054e6d
mergeCommit=0db9bed7ed9e8ec4dbefda41f95a335ab82fbbc0
mergedAt=2026-08-18T10:31:13Z
labels=[agent:zeus]
```

Agent Core event readback also records R2bn integration with
`increment_base_commit_before=9ebaa9e7b44c61bb871ca4da0a838c52e62666b2`,
`increment_branch_commit=5dcf7d14746457148b045e2ed94aed6114054e6d`,
`increment_base_commit_after=0db9bed7ed9e8ec4dbefda41f95a335ab82fbbc0`,
`increment_integrated_by=factory-reviewer`, and
`increment_integration_method=merge_no_ff_push_origin`. This is recorded as
provenance, not as ALR-020/product dispatch authority.

## Canonical Factory status readback

The required readback used only the approved canonical CLI from the assigned
worktree:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/hermes \
  factory status zeus-alpha-research-ledger-core --json \
  > /tmp/r2cr-status-before.json
```

`/tmp/r2cr-status-before.json` summary:

- File size: 3,079,912 bytes.
- `db_backend=agent_core_postgres`, `database=zeus_agent`.
- `factory_cli_source_root=null`.
- `factory_status_source_root=null`, `factory_status_delegated=null`.
- Active project metadata reports
  `reconciliation_anomalies=["unvalidated_required_docs"]`.
- Active project metadata has no `reconciliation_projection_source`.
- Required G1 rows: 14 total; 10 blocking; 4 non-blocking.

The ten canonical status-visible blocking G1 rows are exactly:

| Document | Canonical status evidence |
|---|---|
| `FACTORY_INTAKE.md` | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=false`, `blocking=true` |
| `REQUIREMENTS_ANALYSIS.md` | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=false`, `blocking=true` |
| `PATTERN_ANALYSIS.md` | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=false`, `blocking=true` |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=false`, `blocking=true` |
| `PRD.md` | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=false`, `blocking=true` |
| `ADRS.md` | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=false`, `blocking=true` |
| `METHODOLOGY_PLAN.md` | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=false`, `blocking=true` |
| `TECHNICAL_BLUEPRINT.md` | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=false`, `blocking=true` |
| `TASK_GRAPH.md` | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=false`, `blocking=true` |
| `SECURITY_GATES.md` | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=false`, `blocking=true` |

The four canonical status-visible non-blocking G1 rows are:

| Document | Canonical status evidence |
|---|---|
| `SPRINT_PLAN.md` | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false` |
| `TRACKER.md` | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false` |
| `DOCUMENTATION_INDEX.md` | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false` |
| `QA_GATES.md` | `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false` |

This readback is the current canonical Agent Core Factory truth for R2cr. The
candidate does not claim those ten rows are canonical-status-visible as reviewed.
It records them as still blocking until independent evidence and the approved
control path support a different status projection.

## Project-local frontmatter evidence

The committed `origin/main` G1 documents still carry `reviewed: yes` frontmatter
bound to the historical independent G1 source review chain:

- PR #36: `https://github.com/SiteOneTech/hermes-agent-original/pull/36`
- PR #36 head: `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`
- Factory gate: `794`
- Source reviewed-docs gate: `790`
- Source reviewed-docs SHA: `2476e978c545e24b18ee48844b24eb8c58245ab4`

R2cr preserves those frontmatter markers unchanged. It also preserves the secure
fail-closed interpretation: project-local frontmatter evidence is not enough to
call the canonical Factory status green when the sanctioned Agent Core readback
still exposes ten `reviewed=false` blocking rows.

## Reconciliation decision

R2cr resolves the stale/conflicting provenance in the project documentation by
recording all of these facts together:

1. R2bn PR #80 is no longer a pending PR-first handoff; it is merged as
   `origin/main` commit `0db9bed7ed9e8ec4dbefda41f95a335ab82fbbc0` after
   project-scoped quality gate `929` and Factory reviewer integration.
2. The active R2cr canonical status readback, using the approved `venv/bin/hermes
   factory status` command, still reports exactly ten G1 blockers with
   `reviewed=false` and active anomaly `unvalidated_required_docs`.
3. The four canonical status-visible reviewed rows are only `SPRINT_PLAN.md`,
   `TRACKER.md`, `DOCUMENTATION_INDEX.md`, and `QA_GATES.md`.
4. The existing G1 frontmatter reviewed markers remain source-backed by PR #36 /
   gate `794`, but they are not represented as canonical-status-visible for the
   ten blocking rows in the current readback.
5. This candidate is delivered PR-first from the assigned R2cr branch so an
   independent reviewer can bind the exact pushed candidate SHA, PR URL, status
   readback, and no-merge/no-runtime boundary before any downstream dependency
   relies on it.

## PR-first handoff

R2cr must be delivered by a normal Zeus-signed, non-draft `agent:zeus` PR from
branch
`factory/zeus-alpha-research-ledger-core/inc-017-r2cr-canonical-g1-reviewed-state`.

The PR URL is recorded after the first push because GitHub assigns the PR number.
The exact final PR head SHA and independent review gate are recorded in the PR
body and Factory gate notes after the final push, because a commit cannot contain
its own immutable SHA or a future gate id.

The independent review must verify:

- exact final candidate SHA and base `0db9bed7ed9e8ec4dbefda41f95a335ab82fbbc0`;
- changed paths are confined to
  `factory/projects/zeus-alpha-research-ledger-core/` documentation/provenance;
- canonical status readback `/tmp/r2cr-status-before.json` identifies all ten
  current G1 blockers and the four reviewed non-blocking rows listed above;
- `DOCUMENTATION_INDEX.md`, `TRACKER.md`, `QA_GATES.md`, `SECURITY_GATES.md`,
  `G1_REVIEW.md`, `TASK_GRAPH.md`, and this artifact are mutually consistent;
- no merge, no direct SQL, no primary-checkout mutation, no force-push/ref
  rewrite, no stale task/PR mutation, no external runtime execution, no
  credential change, and no ALR-020/product dispatch occurred.

Until that independent exact-SHA evidence is recorded, R2cr remains a PR-first
candidate and does not clear the canonical G1 reviewed-state blocker by itself.

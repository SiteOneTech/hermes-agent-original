---
document_type: fresh_non_force_g1_delivery_provenance_recovery
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2ae-r1-fresh-non-force-g1-delivery-prov
run_id: run-1787241919-6798e44d
phase: documentation
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending_independent_exact_sha_quality_review
owner: codex-builder
reviewer: quality-reviewer
base_ref: origin/main
base_sha: 71e5e7b2f4ace3b081f9446483784a3c5fb0b981
branch: factory/zeus-alpha-research-ledger-core/inc-001-r2ae-r1-fresh-non-force-g1-deliv
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2ae-r1-fresh-non-force-g1-deliv
created_at: 2026-08-20T12:09:51-04:00
---

# R2ae-R1 — fresh non-force G1 delivery-provenance recovery

## Scope and boundary

R2ae-R1 is a bounded documentation-only recovery for the guard-blocked R2ae
delivery path. It creates a fresh current-origin candidate on the task-assigned
isolated branch/worktree and preserves PR #44 plus the stale R2ae remote branch
as historical evidence only.

This increment changes only project-local evidence under
`factory/projects/zeus-alpha-research-ledger-core/`. It performs no Alpha
Research Ledger product implementation, no Factory runtime/control-plane code
change, no deployment, no credential change, no direct SQL, no primary-checkout
mutation, no stale-PR mutation, no force-push/ref rewrite, no merge, no
broker/trading/risk/paper/live operation, no messaging connector activation and
no external runtime operation.

Agent Core Postgres `factory.*` remains the operational source of truth. Factory
DB interaction in this run is limited to the sanctioned CLI surfaces named in
the task: `factory status` for readback and `factory gate record` for evidence.
No `psql`, `psycopg2`, ad-hoc DB script, `factory task close`, or project-state
mutation command is used by this documentation worker.

## Canonical inputs consulted

Required G1/documentation inputs read from the assigned worktree before edits:

1. `DOCUMENTATION_INDEX.md`
2. `FACTORY_INTAKE.md`
3. `REQUIREMENTS_ANALYSIS.md`
4. `PATTERN_ANALYSIS.md`
5. `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`
6. `PRD.md`
7. `ADRS.md`
8. `METHODOLOGY_PLAN.md`
9. `TECHNICAL_BLUEPRINT.md`
10. `SPRINT_PLAN.md`
11. `TASK_GRAPH.md`
12. `TRACKER.md`
13. `QA_GATES.md`
14. `SECURITY_GATES.md`
15. `G0_REPOSITORY_STRATEGY.md`
16. `R2DG_BOUNDED_G1_EXACT_SHA_INDEPENDENT_REVIEW_RECOVERY.md`
17. `R2DL_G1_DOCUMENTATION_DISPATCH_VALIDATOR_RECOVERY.md`
18. `R2AI_R2_NON_DESTRUCTIVE_CURRENT_ORIGIN_G1_RECOVERY.md`

These inputs preserve the private Zeus boundary, the PR-first/no-auto-merge
contract, and the rule that current configured-base G1 rows are separate from
historical stale-primary, stale-PR, task/event, and failed-gate projection
records.

## Base identity captured before edits

Read-only Git evidence from the assigned isolated worktree after fetching
`origin/main`:

```text
worktree        = /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2ae-r1-fresh-non-force-g1-deliv
branch          = factory/zeus-alpha-research-ledger-core/inc-001-r2ae-r1-fresh-non-force-g1-deliv
remote          = https://github.com/SiteOneTech/hermes-agent-original.git
HEAD            = 71e5e7b2f4ace3b081f9446483784a3c5fb0b981
origin/main     = 71e5e7b2f4ace3b081f9446483784a3c5fb0b981
merge-base      = 71e5e7b2f4ace3b081f9446483784a3c5fb0b981
ahead/behind    = 0 / 0
remote branch   = absent before first push
```

`71e5e7b2f4ace3b081f9446483784a3c5fb0b981` is current `origin/main` at run
start and is the merge commit for R2dl:
`Merge Factory increment zeus-alpha-research-ledger-core-r2dl-g1-documentation-dispatch-validator into main`.
The local primary checkout `/home/jean/Projects/hermes-agent-original` remains
separate and stale for status-source purposes; Factory readback rejects its HEAD
`ac1fdb16051324c490d803b14dd06efffd6f9ad0` as
`primary_checkout_not_configured_base`. This run does not mutate that checkout.

## Canonical Factory status readback

Allowed command, run from the assigned worktree:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2ae-r1-status-before.json
```

Result: exit `0`, saved `/tmp/r2ae-r1-status-before.json`, with:

- `db_backend=agent_core_postgres`
- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2ae-r1-fresh-non-force-g1-deliv`
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2ae-r1-fresh-non-force-g1-deliv`
- `factory_status_delegated=false`
- project `status=active`
- active `reconciliation_anomalies=[]`
- active `reconciliation_projection_source=current_document_status`
- `document_status` rows: 22 total, 14 `g1_required`, 8 lifecycle/PM rows
- G1 required rows: `14`
- G1 blocking rows: `0`
- G1 unreviewed rows: `0`
- `readiness_source=configured_base_ref`
- `base_commit=71e5e7b2f4ace3b081f9446483784a3c5fb0b981`
- `configured_base_ref_accepted=true`
- `primary_checkout_accepted=false`
- `primary_checkout_rejected_reason=primary_checkout_not_configured_base`
- `primary_head=ac1fdb16051324c490d803b14dd06efffd6f9ad0`

All 14 Factory-required G1 rows read back as:

| Document | exists | committed | indexed | validated | reviewed | blocking | readiness_source |
|---|---:|---:|---:|---:|---:|---:|---|
| `FACTORY_INTAKE.md` | true | true | true | true | true | false | configured_base_ref |
| `REQUIREMENTS_ANALYSIS.md` | true | true | true | true | true | false | configured_base_ref |
| `PATTERN_ANALYSIS.md` | true | true | true | true | true | false | configured_base_ref |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | true | true | true | true | true | false | configured_base_ref |
| `PRD.md` | true | true | true | true | true | false | configured_base_ref |
| `ADRS.md` | true | true | true | true | true | false | configured_base_ref |
| `METHODOLOGY_PLAN.md` | true | true | true | true | true | false | configured_base_ref |
| `TECHNICAL_BLUEPRINT.md` | true | true | true | true | true | false | configured_base_ref |
| `SPRINT_PLAN.md` | true | true | true | true | true | false | configured_base_ref |
| `TASK_GRAPH.md` | true | true | true | true | true | false | configured_base_ref |
| `TRACKER.md` | true | true | true | true | true | false | configured_base_ref |
| `DOCUMENTATION_INDEX.md` | true | true | true | true | true | false | configured_base_ref |
| `QA_GATES.md` | true | true | true | true | true | false | configured_base_ref |
| `SECURITY_GATES.md` | true | true | true | true | true | false | configured_base_ref |

The committed frontmatter at `origin/main` also preserves the reviewed source
chain for every required G1 document: `validated: yes`, `reviewed: yes`,
`review_evidence: factory_gate_794`, `reviewed_candidate_sha:
c81547062c5362a7be6f5a1bb2ef9612b29bac9c`, PR #36, source gate `790`, and
source SHA `2476e978c545e24b18ee48844b24eb8c58245ab4`.

## Stale R2ae delivery-provenance readback

The old R2ae delivery target remains historical and must not be force-updated:

```text
PR #44 URL    = https://github.com/SiteOneTech/hermes-agent-original/pull/44
state         = OPEN
isDraft       = false
label         = agent:zeus
base          = main @ b68ec8ad5cf986e5bf4900506820ca978ef0b0c0
head branch   = factory/zeus-alpha-research-ledger-core/inc-019-r2ae-bounded-canonical-g1-valida
head SHA      = b2e643cc2aab681e682ecc7a8f1569bc79d1dd03
head repo     = SiteOneTech/hermes-agent-original
```

Because PR #44 is open on a stale R2ae branch and its base/head do not match the
current R2ae-R1 worktree/base (`71e5e7b2...`), it is retained as audit evidence
only. This run does not push to `inc-019-r2ae...`, does not edit PR #44, does
not close it, and does not force-update it. The assigned R2ae-R1 branch was
absent on origin before first push, so normal creation of that branch is the
non-destructive delivery path.

Agent Core status before this repair also shows the old R2ae task
`zeus-alpha-research-ledger-core-r2ae-bounded-canonical-g1-validation-and` as
`blocked`, with prior gates on that old task including:

- `implementation passed` by `codex-builder` at old PR #44 head
  `b2e643cc2aab681e682ecc7a8f1569bc79d1dd03`.
- `delivery failed` by `codex-builder` because the permitted readback/delivery
  path was blocked.

Those gates are not reused for this fresh current-origin candidate.

## Delivery candidate and review rule

This documentation file cannot contain its own final commit SHA without changing
that SHA. Therefore the exact final candidate head for R2ae-R1 is recorded after
commit/push in the Zeus-signed PR body and Factory gate evidence. Required
delivery properties for the final candidate:

- base branch: `main`
- base SHA at branch creation: `71e5e7b2f4ace3b081f9446483784a3c5fb0b981`
- head branch: `factory/zeus-alpha-research-ledger-core/inc-001-r2ae-r1-fresh-non-force-g1-deliv`
- remote branch creation: normal non-force push only
- PR: fresh non-draft GitHub PR against `main`, labeled `agent:zeus`, with
  `Signed-off-by: Zeus <zeus@sitiouno.com>` in the commit/PR evidence
- final PR head SHA: recorded in the PR body and Factory gate notes after push
- independent exact-SHA quality review: must be recorded by `quality-reviewer`
  against the final PR head before this task is represented as terminally
  accepted

This worker records no self-approval. If independent review is unavailable,
rate-limited, denied, or not exact-SHA-bound, the secure state is bounded rework
or pending review, not a green terminal closure.

## Verification evidence for this docs-only candidate

No production code was necessary, so strict TDD does not apply beyond preserving
no-code scope. Required checks for this candidate are status/readback and Git
diff hygiene:

- `git fetch origin main --prune` → exit `0`; assigned `HEAD`, `origin/main`,
  and merge-base all equal `71e5e7b2f4ace3b081f9446483784a3c5fb0b981`.
- `git ls-remote --heads origin refs/heads/factory/zeus-alpha-research-ledger-core/inc-001-r2ae-r1-fresh-non-force-g1-deliv`
  → no ref before first push.
- Canonical Factory status command above → exit `0`; Agent Core Postgres,
  source roots equal the assigned worktree, 14/14 required G1 rows reviewed and
  non-blocking from `configured_base_ref`.
- GitHub PR #44 readback → open stale historical PR at head
  `b2e643cc2aab681e682ecc7a8f1569bc79d1dd03`; no mutation performed.
- `git diff --check` and scoped changed-path/tracked-file checks are required
  after this project-local evidence update and before PR handoff.

## Bounded handoff

R2ae-R1 resolves delivery provenance only. It does not dispatch ALR-020/product
work, does not close or supersede stale task rows, does not alter the current
G1 reviewed frontmatter markers, and does not rely on Notion as source of truth.
Any remaining `unvalidated_required_docs`, `missing_or_unindexed_docs`, or
validation-task strings must be reconciled only through a source-backed Factory
control path or a separately assigned same-project repair, never by direct SQL,
primary checkout mutation, self-approval, force-push, stale PR mutation, or
external runtime action.

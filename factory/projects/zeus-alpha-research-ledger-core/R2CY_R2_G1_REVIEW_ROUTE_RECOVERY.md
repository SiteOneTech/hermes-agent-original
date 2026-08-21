---
project_id: zeus-alpha-research-ledger-core
phase: g1_recovery
status: implemented_pending_independent_exact_sha_quality_review
validated: yes
reviewed: pending
reviewed_by: quality-reviewer
owner: quality-reviewer
task_id: zeus-alpha-research-ledger-core-r2cy-r2-g1-review-route-recovery
run_id: run-1787284362-117213eb
engine: codex
base_ref: origin/main
base_commit: 5fe25cd7cb78d47afa156f8fde0c6a2c65f00a96
---

# R2cy-R2 — G1 review-route recovery

## Scope

Bounded same-project recovery for the docs-first dispatch loop, executed by
`quality-reviewer` in the assigned isolated worktree
`/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2cy-r2-g1-review-route-recovery`
(branch `factory/zeus-alpha-research-ledger-core/inc-001-r2cy-r2-g1-review-route-recovery`,
engine codex, run `run-1787284362-117213eb`). The worktree starts exactly at
`origin/main` `5fe25cd7cb78d47afa156f8fde0c6a2c65f00a96` (HEAD = origin/main =
merge-base).

Boundary: no product implementation, no primary-checkout mutation, no
merge/deploy, no credential change, no external-runtime access, no direct SQL.
Factory DB interaction is limited to the sanctioned CLI surfaces
`factory status` and `factory gate record`.

## 1. Current canonical G1 document-status readback

Sanctioned command (assigned worktree cwd, canonical venv):

```
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main \
  factory status zeus-alpha-research-ledger-core --json
```

Saved as `/tmp/r2cy-r2-status-before.json` (4,214,579 bytes, exit 0) and
extracted to `/tmp/r2cy-r2-status-summary.json`. Verified fields:

- `db_backend=agent_core_postgres` (canonical Agent Core; SQLite disabled).
- `factory_cli_source_root` = `factory_status_source_root` = assigned worktree.
- `factory_status_delegated=false`.
- 14/14 `g1_required` rows: `exists/committed/indexed/validated/reviewed=true`,
  `blocking=false`, `readiness_source=configured_base_ref`,
  `configured_base_ref_accepted=true`, `base_commit=5fe25cd7cb78d47afa156f8fde0c6a2c65f00a96`.
- `primary_checkout_accepted=false`,
  `primary_checkout_rejected_reason=primary_checkout_not_configured_base`,
  `primary_head=ac1fdb16051324c490d803b14dd06efffd6f9ad0`.
- Active project metadata: `reconciliation_anomalies=[]`,
  `reconciliation_projection_source=current_document_status`,
  `reconciliation_required=false`.

Conclusion: **zero G1 required-document blockers at the current configured base.**
The `G1 readiness: 12/22 sin blocker; blockers=10` line in the run prompt is
the known stale prompt projection (R2bm defect class: prompt `document_status`
lines combined from stale payload rows), not the current canonical readback.

## 2. Exact candidate referenced by R2cy-R1

R2cy-R1 task
`zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re`
(status `ready`, phase `quality_review`) references PR #99:

- URL: https://github.com/SiteOneTech/hermes-agent-original/pull/99
- Title: `fix(factory): reconcile diverged runtime source provenance`
- Head (exact candidate SHA): `ead1aec54288123ff12c049bc4eb0f29d55d288b`
- Head branch: `factory/zeus-alpha-research-ledger-core/inc-021-r2cy-runtime-source-provenance-reconciliation`
- Base: `71e5e7b2f4ace3b081f9446483784a3c5fb0b981` (historical `origin/main`)
- State: OPEN, non-draft, label `agent:zeus`, 1 commit (the head SHA).
- `mergeable=CONFLICTING` (GitHub readback).

Git readback from the assigned worktree:

- `git merge-base --is-ancestor 71e5e7b2f4ace3b081f9446483784a3c5fb0b981 origin/main`
  → true (PR base is an ancestor of current `origin/main`, i.e. the PR is behind).
- `git merge-base --is-ancestor ead1aec54288123ff12c049bc4eb0f29d55d288b origin/main`
  → false (PR head is not in `origin/main`; not merged).
- `git ls-remote origin refs/heads/factory/.../inc-021-r2cy-*` → head
  `ead1aec54288123ff12c049bc4eb0f29d55d288b` (remote branch exists at PR head).
- Local merge simulation:
  `git merge-tree --write-tree ead1aec54288123ff12c049bc4eb0f29d55d288b 5fe25cd7cb78d47afa156f8fde0c6a2c65f00a96`
  → exit 1 with conflict in `tests/hermes_cli/test_factory_increment_integration.py`
  (saved `/tmp/r2cy-r2-mergetree.out`).

## 3. Exact source-backed stale-candidate cause

The candidate cannot be reviewed as a current, source-backed delivery:

1. **Stale base.** PR #99 base `71e5e7b2…` is an ancestor of current
   `origin/main` `5fe25cd7…`; the PR was created before the R2ai-R5 merge
   (`5fe25cd7`, "Merge Factory increment
   zeus-alpha-research-ledger-core-r2ai-r5-…") and is behind current main.
2. **Not mergeable.** GitHub reports `mergeable=CONFLICTING`, and the local
   `git merge-tree --write-tree` against current `origin/main` exits 1 with a
   real conflict in `tests/hermes_cli/test_factory_increment_integration.py`.
   The R2cy-R1 task itself requires "PR metadata (OPEN, non-draft,
   CLEAN/MERGEABLE, agent:zeus)" — the CLEAN/MERGEABLE precondition fails.
3. **Scope already superseded in current main.** PR #99 changes
   `hermes_cli/factory.py` source-provenance classification so a *diverged*
   primary root delegates status/resolve/tick to a configured-base worktree.
   Current `origin/main` already implements this class of behavior with the
   opposite design decision for diverged sources: `test_resolve_state_keeps_diverged_running_source_local`
   (`tests/hermes_cli/test_factory_orchestrator_tick.py:665`) keeps diverged
   running sources local/fail-closed, and the configured-base delegation for
   stale primary roots is covered by `test_project_tick_prefers_configured_base_source_when_invoked_from_stale_primary_root`,
   `test_status_prefers_configured_base_source_when_invoked_from_stale_primary_root`,
   `test_resolve_state_prefers_configured_base_source_when_invoked_from_stale_primary_root`
   (lines 213/365/527). Those behaviors reached `origin/main` through the
   R2cu/R2cv/R2di control-plane repairs. PR #99's diverged-delegation direction
   was deliberately superseded by the fail-closed diverged-local design in main.
4. **Review-route dispatch is still denied by stale preflight projection.**
   Agent Core events for R2cy-R1 show 11 `dispatch_preflight_denied` events,
   the latest `209057` (2026-08-21T03:49:57Z) and `209050`
   (2026-08-21T03:42:00Z), all with
   `blockers=["missing_or_unindexed_docs"]`,
   `runtime_contract="docs_first_factory_product_execution_dispatch"`, while
   the current canonical readback reports 14/14 required G1 rows
   `indexed=true`, `blocking=false`. The dispatch code on `origin/main`
   `5fe25cd7…` still runs the pre-R2da-R2 preflight; the R2da-R2 dispatch fix
   (PR #114, head `fe0b6f80bfad296f78d3ab9a6ac79a31298bb243`, base
   `5fe25cd7…`, `MERGEABLE`, OPEN) is not yet merged into `origin/main`.

## 4. Independent review verdict

The R2cy-R1 candidate (PR #99, exact head `ead1aec54288123ff12c049bc4eb0f29d55d288b`)
is **stale and not mergeable against the current configured base**; the
independent exact-SHA review therefore records **REQUEST_CHANGES** (stale
candidate cause above), not a PASS. No reviewed status is granted to PR #99 or
to this artifact by this run; the artifact itself remains `reviewed: pending`
until independent exact-SHA quality review of the final pushed head records a
verdict.

R2cy-R1 is **not terminalized by this run**: the sanctioned DB-write allowlist
for this task covers only `factory status` and `factory gate record`; closing
or superseding the R2cy-R1 task row requires the explicitly authorized
canonical close/supersede action (or the orchestrator), with this evidence as
readback.

## 5. Smallest successor/rework (exact technical cause)

1. Integrate the R2da-R2 dispatch repair **PR #114**
   (https://github.com/SiteOneTech/hermes-agent-original/pull/114, head
   `fe0b6f80bfad296f78d3ab9a6ac79a31298bb243`, base `5fe25cd7…`, OPEN,
   MERGEABLE, quality gate 1026 passed) so the docs-first preflight stops
   denying provenance-repair review tasks with `missing_or_unindexed_docs`.
2. Re-point or supersede R2cy-R1: its candidate PR #99 is stale/conflicting;
   any fresh review must target either a rebased PR #99 head on current
   `origin/main` reconciled with the fail-closed diverged-local design, or the
   current R2da-R2 PR #114 head as the dispatch-fix candidate.
3. Re-record the exact-SHA review gate only against the final pushed head of
   the re-pointed candidate, with the canonical readback quoted.

## Files changed (this run)

- `factory/projects/zeus-alpha-research-ledger-core/R2CY_R2_G1_REVIEW_ROUTE_RECOVERY.md` (this artifact)
- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md` (index/provenance entry)

## Boundary reaffirmed

No product implementation, no primary-checkout mutation, no merge/deploy, no
credential change, no external-runtime access, no direct SQL, no ALR-020 /
product dispatch. The stale primary checkout
`/home/jean/Projects/hermes-agent-original` at `ac1fdb1605…` was not touched.

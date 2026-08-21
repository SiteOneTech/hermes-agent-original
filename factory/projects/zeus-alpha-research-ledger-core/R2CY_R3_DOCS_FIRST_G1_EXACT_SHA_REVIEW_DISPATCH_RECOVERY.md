---
document_type: review_dispatch_recovery
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2cy-r3-docs-first-g1-exact-sha-review-d
run_id: run-1787290141-626bcabd
phase: g1_recovery
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending_independent_review
owner: quality-reviewer
engine: codex
base_ref: origin/main
base_sha: d231dc46cbd38f3d892a26c236903cbea2a889e0
branch: factory/zeus-alpha-research-ledger-core/inc-001-r2cy-r3-docs-first-g1-exact-sha
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2cy-r3-docs-first-g1-exact-sha
created_at_utc: 2026-08-21T05:45:00Z
---

# R2cy-R3 — docs-first G1 exact-SHA review dispatch technical recovery

## Scope and boundary

This increment independently validates the currently required docs-first G1
exact-SHA review route for project `zeus-alpha-research-ledger-core` before any
product implementation, and routes exactly one bounded same-project technical
rework through the canonical Factory CLI when the dispatch/validation path is
circular. It is a same-project, bounded control-plane/documentation recovery
only.

This run does not implement Alpha Ledger product behavior, does not deploy,
does not merge, does not change credentials, does not mutate the primary
checkout, does not write direct SQL, does not run mutating Factory
project/tick/resolve-state commands, and does not contact or modify external
runtimes/connectors, messaging, Vonash/Magnus/VAOS, RAG/KB, brokers, trading,
risk, paper/live systems, or ALR-020 product dispatch. The only sanctioned
Factory DB surfaces used are `factory status`, `factory gate record`, and
`factory task create` (the single AC3 routing action); the primary checkout
`/home/jean/Projects/hermes-agent-original` at `ac1fdb1605…` was not touched.

## Canonical documents read

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2CY_R2_G1_REVIEW_ROUTE_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R1_DOCS_FIRST_G1_RECOVERY_DISPATCH_ROUTING_REPAIR.md`

Agent Core Postgres `factory.*` remains the source of truth. This Markdown file
records evidence and rationale only; it is not a substitute for Factory state.

## Current-origin identity captured before edits

Read-only Git evidence after `git fetch origin main --prune`, before edits:

```text
worktree    = /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2cy-r3-docs-first-g1-exact-sha
branch      = factory/zeus-alpha-research-ledger-core/inc-001-r2cy-r3-docs-first-g1-exact-sha
remote      = https://github.com/SiteOneTech/hermes-agent-original.git
HEAD        = d231dc46cbd38f3d892a26c236903cbea2a889e0
origin/main = d231dc46cbd38f3d892a26c236903cbea2a889e0
merge-base  = d231dc46cbd38f3d892a26c236903cbea2a889e0
ahead/behind= 0 0
```

`origin/main` `d231dc46cb` is the R2df-R1 docs-first G1 recovery dispatch
routing repair merge (commit `78aa3006fc`, 2026-08-21T05:04:18Z). The primary
checkout remains outside this worktree: `git -C /home/jean/Projects/hermes-agent-original rev-parse HEAD`
→ `ac1fdb16051324c490d803b14dd06efffd6f9ad0`, `4` ahead / `2258` behind
`origin/main`, merge-base `c846ccfbd844c2f8810a26776505ec44a2341914` (diverged,
not an ancestor of current `origin/main`).

## 1. Canonical G1 document-status readback — required-document blocker set

Sanctioned command (assigned worktree cwd, canonical venv):

```
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main \
  factory status zeus-alpha-research-ledger-core --json
```

Saved as `/tmp/r2cy-r3-status-before.json` (4,244,389 bytes, exit 0). Verified
fields:

- `db_backend=agent_core_postgres` (canonical Agent Core; SQLite disabled).
- `factory_cli_source_root` = `factory_status_source_root` = assigned worktree;
  `factory_status_delegated=false`.
- 14/14 `g1_required` rows: `exists/committed/indexed/validated/reviewed=true`,
  `blocking=false`, `readiness_source=configured_base_ref`,
  `configured_base_ref_accepted=true`, `base_commit=d231dc46cbd38f3d892a26c236903cbea2a889e0`.
- `primary_checkout_accepted=false`,
  `primary_checkout_rejected_reason=primary_checkout_not_configured_base`,
  `primary_head=ac1fdb16051324c490d803b14dd06efffd6f9ad0`.
- Active project metadata: `reconciliation_anomalies=[]`,
  `reconciliation_projection_source=current_document_status`,
  `reconciliation_required=false`.

Conclusion: **zero G1 required-document blockers at the current configured
base.** The prompt's `G1 readiness: 12/22 documentos sin blocker; blockers=10`
line is the known stale prompt projection (R2bm defect class), not current
canonical readback.

## 2. Validation-task blocker set — currently required vs stale/superseded

Source-backed Factory status (same JSON) distinguishes:

Currently required for the docs-first G1 exact-SHA review route:

- `zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re`
  (R2cy-R1 — independent exact-SHA quality review of PR #99),
  `status=ready`, `phase=quality_review`, branch
  `factory/zeus-alpha-research-ledger-core/inc-017-r2cy-r1-independent-exact-sha-qu`.
  This is the **only** non-terminal, non-superseded validation row of the
  review route; it became `ready` at 2026-08-20T10:17:16Z.

Stale/superseded validation rows (terminal audit history, NOT currently
required — R2h, R2ai, R2l, R2g, ALR-060 all `status=superseded`; blocked
R2ae-R1/R2ae-bounded/R2ac retain `structured_reconciliation_metadata` as
fail-closed history):

- `zeus-alpha-research-ledger-core-r2h-isolated-independent-g1-exact-sha-re` (superseded)
- `zeus-alpha-research-ledger-core-r2ai-current-origin-g1-independent-revie` (superseded)
- `zeus-alpha-research-ledger-core-r2l-documentation-phase-exact-sha-g1-rev` (superseded)
- `zeus-alpha-research-ledger-core-r2g-renewed-independent-g1-review-of-pr-` (superseded)
- `zeus-alpha-research-ledger-core-alr-060-independent-quality-and-security` (superseded)
- `zeus-alpha-research-ledger-core-r2ae-r1-fresh-non-force-g1-delivery-prov` (blocked)
- `zeus-alpha-research-ledger-core-r2ae-bounded-canonical-g1-validation-and` (blocked)
- `zeus-alpha-research-ledger-core-r2ac-repair-pr-43-canonical-g1-readback-` (blocked)

Product-phase validation rows that are correctly pending (ALR-061/062/063/070,
`todo`) belong to the product chain and are not part of the docs-first review
route.

## 3. Exact candidate PR SHAs and review-route readback

Read-only GitHub readback (`gh pr view --repo SiteOneTech/hermes-agent-original`):

- **PR #99** (R2cy-R1 candidate): `fix(factory): reconcile diverged runtime
  source provenance`, OPEN, non-draft, `agent:zeus`, head
  `ead1aec54288123ff12c049bc4eb0f29d55d288b`, head branch
  `factory/zeus-alpha-research-ledger-core/inc-021-r2cy-runtime-source-provenance-reconciliation`,
  base `71e5e7b2f4ace3b081f9446483784a3c5fb0b981` (ancestor of current
  `origin/main` — stale base). Independently reviewed by R2cy-R2 at exact head
  with Factory gate `1027` = REQUEST_CHANGES (stale candidate; merge-tree
  conflict in `tests/hermes_cli/test_factory_increment_integration.py`);
  scope superseded by the fail-closed diverged-local design in `origin/main`.
  **Stale/superseded — fail-closed.**
- **PR #114** (R2da-R2 successor dispatch repair): `fix(factory): unblock
  docs-first PR review repair`, OPEN, non-draft, `agent:zeus`, head
  `fe0b6f80bfad296f78d3ab9a6ac79a31298bb243`, head branch
  `factory/zeus-alpha-research-ledger-core/inc-001-r2da-r2-repair-docs-first-valida`,
  base `5fe25cd7cb78d47afa156f8fde0c6a2c65f00a96` (ancestor of current
  `origin/main`). Factory gates: implementation `1025` PASS (codex-builder),
  independent exact-SHA quality `1026` PASS (quality-reviewer). The diff is
  confined to `hermes_cli/factory_pg.py` dispatch/validation predicates
  (`_is_docs_first_validation_repair_task`, `_validation_task_readiness_findings`
  superseded-row terminality), focused tests, and project-local docs. **The fix
  is NOT in current `origin/main`: `_is_docs_first_validation_repair_task` has
  zero matches in the current worktree source.**
- **PR #115** (R2cy-R2 evidence): `docs(factory): R2cy-R2 G1 review-route
  recovery evidence`, MERGED 2026-08-21T04:14:46Z, head `c1db1fdfb3714a406de5d701d9c98b8143c5417f`
  (contained in `origin/main` `d231dc46cb`).

## 4. Runtime circularity evidence (source-backed, still active)

Agent Core events after the R2df-R1 merge (merge at 05:04:18Z) still show the
docs-first review dispatch denied:

- Event `209340` (05:22:35Z), `209347` (05:27:18Z), `209352` (05:28:16Z):
  `dispatch_preflight_denied` on
  `zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re`,
  `blockers=["missing_or_unindexed_docs"]`,
  `runtime_contract="docs_first_factory_product_execution_dispatch"`.
- Events `209346`/`209351` (05:27:16Z/05:28:15Z): `dispatch_preflight_denied`
  on `zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation`,
  `unresolved_validation_tasks` naming the currently-required R2cy-R1
  (`status=ready`) plus superseded R2h/R2ai/R2l/R2g/ALR-060 and todo
  ALR-061/062/063/070.

Mechanical cause, verified against current source:
`_dispatch_preflight_blockers()` gates any candidate for which
`_is_docs_first_gated_dispatch_task()` returns true; R2cy-R1 is
`phase=quality_review` with "quality" in its text, so it is gated, and when
`docs_ready=false` (`_g1_document_blockers(project)` non-empty) it is denied
with `missing_or_unindexed_docs`. The running tick still executes from the
stale primary checkout source (`ac1fdb1605…`, pre-R2da-R2 code) whose legacy
resolver reads the primary's ten historical `reviewed=false` G1 blockers, so
`docs_ready=false` persists at runtime even though current configured-base rows
are clean. R2df-R1 (`78aa3006fc`) fixed only the `unresolved_validation_tasks`
class for docs-first repair dispatch; the R2cy-R1 class requires the R2da-R2
fix in PR #114, which is OPEN and not yet integrated.

## 5. Independent exact-SHA verdict (AC2)

- The currently required review-route candidate named by the R2cy-R1 task
  (PR #99 head `ead1aec5…`) is **stale/superseded**: base `71e5e7b2…` is an
  ancestor of current `origin/main`, GitHub mergeability is conflicting against
  current main, and gate `1027` REQUEST_CHANGES is the recorded exact-SHA
  verdict. Fail-closed; no reviewed status is granted.
- The successor dispatch-fix candidate (PR #114 head `fe0b6f80…`) already
  carries independent exact-SHA quality review (gate `1026` PASS, reviewer
  `quality-reviewer`) and implementation evidence (gate `1025`). This run
  independently verified the gate records, the PR state, and the diff scope
  (control-plane predicates + focused tests + project-local docs only); no
  product/runtime/ALR code is touched by the fix. No duplicate gate is
  re-recorded for PR #114; it is cited as the successor candidate whose
  integration is the documented prerequisite (R2cy-R2 §5).
- The R2cy-R3 evidence candidate itself is delivered PR-first (Zeus-signed
  `agent:zeus`) and remains `reviewed: pending_independent_review` until an
  independent reviewer records a task-bound gate against its final pushed head.

## 6. Bounded successor rework routed through Factory CLI (AC3)

Dispatch/validation **is circular at runtime** (a `ready` currently-required
review task is still denied post-R2df-R1), so exactly one bounded same-project
technical rework was created via the canonical Factory CLI
(`hermes factory task create`) to restore docs-first task dispatch:

- Task: integrate successor R2da-R2 dispatch repair PR #114 (head
  `fe0b6f80bfad296f78d3ab9a6ac79a31298bb243`, gates 1025/1026 PASS) into
  `origin/main` and catch up the primary checkout runtime to current
  `origin/main` so the docs-first G1 exact-SHA review route (R2cy-R1) can be
  claimed; then verify with a fresh `factory status` readback and a dispatched
  R2cy-R1 claim that no `missing_or_unindexed_docs` / `unresolved_validation_tasks`
  denial remains for the review route.
- Scope boundary: no product implementation, no deploy, no credential change,
  no external runtime, no direct SQL; merge/integration remains subject to the
  project's no-auto-integration contract and independent gate evidence.

The task row (id, lane, branch/worktree, acceptance criteria) is recorded in
Agent Core via the CLI result and quoted in the Factory gate notes.

## Files changed (this run)

- `factory/projects/zeus-alpha-research-ledger-core/R2CY_R3_DOCS_FIRST_G1_EXACT_SHA_REVIEW_DISPATCH_RECOVERY.md` (this artifact)
- `factory/projects/zeus-alpha-research-ledger-core/validate_r2cy_r3_g1_evidence.py` (deterministic project-local validator)
- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md` (index/provenance entry)
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md` (gate section)
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md` (status entry)

## Boundary reaffirmed

No product implementation, no primary-checkout mutation, no merge/deploy, no
credential change, no external-runtime access, no direct SQL, no ALR-020 /
product dispatch. The stale primary checkout
`/home/jean/Projects/hermes-agent-original` at `ac1fdb1605…` was not touched.

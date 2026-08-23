---
project_id: zeus-alpha-research-ledger-core
increment: r2df-r7-independent-exact-sha-g1-source-root-review
phase: g1_recovery
status: reviewed
validated: yes
reviewed: yes
reviewed_by: quality-reviewer
review_evidence: factory_gate_1052
reviewed_candidate_pr: https://github.com/SiteOneTech/hermes-agent-original/pull/124
reviewed_candidate_sha: 6d1c56c4881621075bbbe5f957e09dce178a10a1
run_id: run-1787445987-599ad5a1
---

# R2df-R7 — independent exact-SHA G1 source-root recovery review of PR #124

## Scope

This run is the bounded same-project technical recovery review of the canonical
G1 source-root mismatch: Factory status invoked from the stale primary checkout
reports `reviewed=false` even though `origin/main` at
`3b6dca81f5633df64f47f5861d0b618adb8f76eb` contains `reviewed: yes` G1
frontmatter. It independently reviews the existing R2df-R6 control-plane fix in
PR #124 at its exact head, validates configured-origin-base resolution against a
stale primary **without changing that checkout**, and records a pass or precise
rework.

Reviewer identity: `quality-reviewer` (isolated Hermes profile
`~/.hermes/profiles/quality-reviewer`), assigned worktree
`/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2df-r7-independent-exact-sha-g1`
on branch
`factory/zeus-alpha-research-ledger-core/inc-001-r2df-r7-independent-exact-sha-g1`
(starting exactly at `origin/main` `3b6dca81…`, HEAD=origin/main=merge-base,
0 ahead / 0 behind, clean).

No product implementation, direct merge, deployment, secret change, external
runtime, messaging, or trading-related action is authorized or performed.

## AC1 — PR #124 identity, base, diff scope, Zeus signature, independent-review identity

Live verification (GitHub REST, not cached view):

- PR #124 `https://github.com/SiteOneTech/hermes-agent-original/pull/124`
  - title: `fix(factory): route docs-first recovery before validation`
  - state: `open`, `is_draft: false`, `merged: false`
  - head ref: `factory/zeus-alpha-research-ledger-core/inc-018-r2df-r6-fail-closed-docs-first-d`
  - **head SHA (live): `6d1c56c4881621075bbbe5f957e09dce178a10a1` — MATCH with the
    exact candidate SHA expected by this task** (also confirmed by
    `git fetch origin pull/124/head` → `refs/remotes/origin/pr-124` =
    `6d1c56c…`, which equals the local r2df-r6 branch head; a stale cached
    `gh pr view` showing an unrelated closed Feb-2026 HuggingFace PR #124 was
    rejected as cache evidence — REST is authoritative).
  - base ref: `main`, base SHA: `3b6dca81f5633df64f47f5861d0b618adb8f76eb`
    (exact current `origin/main`; the sole PR commit's parent is this base —
    `git rev-parse 6d1c56c^` = `3b6dca81…`).
  - `mergeable: true`, `merge_state: clean`
  - labels: `["agent:zeus"]`; body contains `## Exact candidate SHA`,
    `Signed-off-by: Zeus <zeus@sitiouno.com>`; commit author:
    `Zeus <zeus@sitiouno.com>`, message `fix(factory): route docs-first recovery
    before validation` (2026-08-22 20:19 -0400).
  - diff scope (8 files, +354/-20):
    - `hermes_cli/factory_pg.py` (+102/-20)
    - `tests/hermes_cli/test_factory_increment_integration.py` (+82)
    - `factory/projects/zeus-alpha-research-ledger-core/`
      `DOCUMENTATION_INDEX.md` (+3), `QA_GATES.md` (+9),
      `SECURITY_GATES.md` (+8), `TASK_GRAPH.md` (+1), `TRACKER.md` (+1),
      and new `R2DF_R6_FAIL_CLOSED_DOCS_FIRST_DISPATCH_RECOVERY.md` (+148)
- Independent-review identity: this review is performed by `quality-reviewer`
  (role assigned to task
  `zeus-alpha-research-ledger-core-r2df-r7-independent-exact-sha-g1-source-`,
  run `run-1787445987-599ad5a1`) against the exact live head, with its own
  readbacks and test executions — no reuse of R2df-R6 worker evidence.

## AC2 — canonical document-status resolves required G1 docs from configured origin/main; fail-closed preserved

### Canonical readback (assigned worktree, current origin/main code)

Command (cwd = assigned worktree):

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main \
  factory status zeus-alpha-research-ledger-core --json \
  > /tmp/r2df-r7-status-wt.json
```

Result (exit 0; `/tmp/r2df-r7-status-wt.json`, 4,399,587 bytes):

- `db_backend: agent_core_postgres`
- `factory_cli_source_root` = `factory_status_source_root` =
  `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2df-r7-independent-exact-sha-g1`;
  `factory_status_delegated: false`
- 14/14 `g1_required` rows: `exists/committed/indexed/validated/reviewed=true`,
  `blocking=false`, `readiness_source=configured_base_ref`
- per-row: `base_ref=origin/main`, `base_commit=3b6dca81f5633df64f47f5861d0b618adb8f76eb`,
  `configured_base_ref_accepted=true`, `primary_checkout_accepted=false`,
  `primary_checkout_rejected_reason=primary_checkout_not_configured_base`,
  `primary_head=ac1fdb16051324c490d803b14dd06efffd6f9ad0`,
  `primary_path=/home/jean/Projects/hermes-agent-original`

→ The canonical Factory document-status reader resolves the required G1 docs
from configured `origin/main` (`3b6dca81…`), not from the stale primary
checkout files (`ac1fdb1605…`), and the stale primary remains rejected
(fail-closed) exactly as the task premise states.

### RED/GREEN effect of the R2df-R6 fix (same DB, same base, code difference only)

Same sanctioned command run from the PR-head worktree
(`/tmp/r2df-r7-pr124-check`, detached at `6d1c56c…`), saved as
`/tmp/r2df-r7-status-pr.json` (exit 0, `agent_core_postgres`,
`factory_cli_source_root=/tmp/r2df-r7-pr124-check`, `delegated=false`):

| Field (project metadata) | Without fix (worktree r2df-r7, origin/main) | With fix (PR #124 head) |
|---|---|---|
| `reconciliation_anomalies` | `["unvalidated_required_docs"]` | `[]` |
| `reconciliation_required` | `true` | `false` |
| `reconciliation_projection_source` | — | `current_document_status` |
| 14/14 g1_required rows | reviewed, `blocking=false`, `configured_base_ref` | unchanged, same 14 rows |

The fix sources document reconciliation readiness only from current G1 rows
(`_g1_document_blockers` / `_g1_document_blockers_from_rows` in
`hermes_cli/factory_pg.py`), removing the coupling with
`_g1_document_primary_runtime_blockers_from_rows`, so stale-primary/runtime
identity no longer re-presents `unvalidated_required_docs` while the
configured-base content is reviewed/clean; the primary-checkout rejection
(`primary_checkout_not_configured_base`) is untouched and remains fail-closed.

### Fail-closed invariants in the fix

- `_candidate_requires_validation_readiness_before_dispatch` now returns True
  for any candidate with `_has_product_or_runtime_dispatch_scope` (ALR-020…080,
  product/ledger implementation, external runtime, deployment, messaging,
  direct SQL, base-branch integration, trading, risk, paper/live) — those
  scopes stay blocked behind unresolved validation rows.
- `_is_docs_first_repair_dispatch_task` now requires explicit docs terms AND
  repair terms (plus phase g0/g1/docs/planning), and
  `_is_docs_first_gated_dispatch_task` re-gates product/runtime-scope tasks.
- Test assert: `_dispatch_preflight_blockers(r2cw_direct_runtime,
  docs_ready=False, notion_ready=True) == ["missing_or_unindexed_docs"]`
  (fail-closed preserved for the R2cw premature-live-run/direct-integration
  candidate).
- Event `216503` reproduced live in the status payload:
  `dispatch_preflight_denied` for
  `zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation`
  with `unresolved_validation_tasks` + ten validation rows — the exact
  historical denial the fix addresses; the fix does not remove it from audit
  history.

## AC3 — Factory quality gate recorded; boundaries respected

- Factory gate `1052` recorded via the sanctioned CLI:
  `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main
  factory gate record zeus-alpha-research-ledger-core quality passed
  --task-id zeus-alpha-research-ledger-core-r2df-r7-independent-exact-sha-g1-source-
  --reviewer quality-reviewer --notes "…"` and read back from a fresh
  `factory status` (`/tmp/r2df-r7-status-after-gate.json`):
  `gate_id=1052, gate_type=quality, status=passed,
  task_id=zeus-alpha-research-ledger-core-r2df-r7-independent-exact-sha-g1-source-,
  reviewer=quality-reviewer, created_at=2026-08-23T00:50:57Z`.
- Verdict: **PASS with one minor non-blocking finding** (see Findings).
- Boundaries honored: no merge, no primary-checkout mutation (primary left at
  `ac1fdb1605…`), no deploy, no credential change, no direct SQL, no external
  runtime call, no messaging action, no product/trading operation, no
  task-status mutation, no `factory task close`.

## Tests executed (real, on exact PR head `6d1c56c…`)

Worktree: `/tmp/r2df-r7-pr124-check` (git worktree add --detach at the exact
head; removed after this run).

1. Focused regression (the PR's new test):
   `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3
   scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py
   -k routes_only_g1_docs_recovery_before_direct_runtime_scope -v --tb=short`
   → **1/1 passed** (1 file, 1.5s, 48 workers).
2. Related Factory control-plane set:
   `scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py
   tests/hermes_cli/test_factory_control_plane_refactor.py
   tests/hermes_cli/test_factory_orchestrator_tick.py -v --tb=short`
   → **313/313 passed, 0 failed** (3 files, 14.3s, 48 workers).
3. `git diff --check 3b6dca81…...6d1c56c…` → **exit 2**: 5 trailing-whitespace
   lines in `R2DF_R6_FAIL_CLOSED_DOCS_FIRST_DISPATCH_RECOVERY.md` (lines 70–74,
   task-status table rows). The PR body/QA_GATES/TASK_GRAPH state
   "`git diff --check` passed / exit 0" — that claim is inaccurate for the
   current head (minor documentation-evidence discrepancy).

## Findings

1. **[minor, non-blocking] trailing whitespace in the R2df-R6 evidence doc.**
   `factory/projects/zeus-alpha-research-ledger-core/R2DF_R6_FAIL_CLOSED_DOCS_FIRST_DISPATCH_RECOVERY.md`
   lines 70–74 carry trailing whitespace; `git diff --check` exits 2, while the
   PR body and QA_GATES/TASK_GRAPH entries assert `git diff --check` passed.
   Suggested bounded fix before merge: strip the trailing whitespace on those
   five table lines (docs-only change, no behavior impact) and correct/soften
   the "diff --check exit 0" claim in the R2df-R6 gates/PR body, or record this
   discrepancy in the merge evidence. Not a code defect; does not block the
   quality verdict.

2. **[info] cached `gh pr view` hazard.** The first `gh pr view 124` returned a
   stale cached payload for an unrelated closed Feb-2026 HuggingFace PR #124;
   GitHub REST (`gh api repos/SiteOneTech/hermes-agent-original/pulls/124`) and
   `git fetch origin pull/124/head` are the authoritative live sources and
   confirm the real PR #124 head `6d1c56c…` matches the task's expected SHA.

## G1 docs consulted

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
  (full read, including status semantics and required reading order)
- `R2DG_BOUNDED_G1_EXACT_SHA_INDEPENDENT_REVIEW_RECOVERY.md` (predecessor
  review-route recovery, referenced from the index)
- PR #124 project-local artifacts:
  `R2DF_R6_FAIL_CLOSED_DOCS_FIRST_DISPATCH_RECOVERY.md`, `QA_GATES.md`,
  `SECURITY_GATES.md`, `TASK_GRAPH.md`, `TRACKER.md` (diff + full doc)

## Artifacts

- `/tmp/r2df-r7-status-wt.json` — canonical status, assigned worktree (no fix)
- `/tmp/r2df-r7-status-pr.json` — canonical status, PR #124 head (with fix)
- `/tmp/r2df-r7-status-after-gate.json` — post-gate readback (gate 1052)
- This file: `R2DF_R7_INDEPENDENT_EXACT_SHA_G1_SOURCE_ROOT_REVIEW.md`
- Factory gate: `1052` (quality, passed, quality-reviewer)

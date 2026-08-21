---
document_type: current_base_successor_dispatch_repair
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2cy-r3-successor-integrate-r2da-r2-pr-1
run_id: run-1787301432-2282ec0c
phase: g1_recovery
status: implemented_pending_independent_exact_sha_review
validated: yes
reviewed: pending
owner: codex-builder
engine: codex
base_ref: origin/main
base_sha: eb3e3ff48905285812eca4c222fa2155a9282546
branch: factory/zeus-alpha-research-ledger-core/inc-017-r2cy-r3-successor-integrate-r2da
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2cy-r3-successor-integrate-r2da
created_at_utc: 2026-08-21T08:43:28Z
---

# R2cy-R3 successor — current-base R2da dispatch repair

## Scope and boundary

This rework ports the R2da-R2 docs-first dispatch fix from PR #114 onto the
assigned current-base branch because the original PR #114 head is no longer
mergeable against current `origin/main`.

The change is limited to Factory control-plane dispatch predicates, focused
regression tests, and project-local evidence. It does not implement product
Alpha Ledger behavior, deploy, change credentials, mutate the primary checkout,
write direct SQL, run external runtimes, close/supersede task rows, dispatch
ALR-020/product work, or merge to `origin/main`.

## Documents consulted

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2CY_R3_SUCCESSOR_INTEGRATE_R2DA_FAIL_CLOSED_READBACK.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2CY_R3_DOCS_FIRST_G1_EXACT_SHA_REVIEW_DISPATCH_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2CY_R2_G1_REVIEW_ROUTE_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2V_CANONICAL_G1_STATUS_AND_NO_AUTO_MERGE_REPAIR.md`

## PR #114 read-only precondition readback

Live GitHub readback for PR #114:

- URL: https://github.com/SiteOneTech/hermes-agent-original/pull/114
- State: `OPEN`
- Draft: `false`
- Label: `agent:zeus`
- Base: `main` at `5fe25cd7cb78d47afa156f8fde0c6a2c65f00a96`
- Head: `fe0b6f80bfad296f78d3ab9a6ac79a31298bb243`
- Mergeability: `mergeable=CONFLICTING`, `mergeStateStatus=DIRTY`

Canonical Factory status still contains the historical exact-head PR #114
gates:

- Gate `1025`: `implementation` `passed`, reviewer `codex-builder`, task
  `zeus-alpha-research-ledger-core-r2da-r2-repair-docs-first-validation-dea`,
  notes bind PR #114 head `fe0b6f80bfad296f78d3ab9a6ac79a31298bb243`.
- Gate `1026`: `quality` `passed`, reviewer `quality-reviewer`, same task and
  same exact PR #114 head.

Those gates remain useful predecessor evidence, but they do not satisfy the
current-base integration precondition because PR #114 is not mergeable against
current `origin/main`. Local `git merge-tree --write-tree origin/main
refs/remotes/origin/pr/114` exits `1` with conflicts in `DOCUMENTATION_INDEX.md`,
`QA_GATES.md`, and `TRACKER.md`.

## Implementation summary

The current-base successor carries the same bounded code behavior as R2da-R2:

1. `_validation_task_readiness_findings()` treats `status=superseded` validation
   rows as terminal audit history instead of unresolved validation blockers.
2. `_is_docs_first_validation_repair_task()` identifies bounded exact-SHA
   review tasks that repair or verify docs-first G1/documentation/control-plane
   provenance.
3. `_is_docs_first_repair_dispatch_task()` allows those validation repair tasks
   to preempt stale docs-first product gating.
4. `_is_docs_first_gated_dispatch_task()` keeps ordinary product
   implementation, QA, security, delivery, deploy, and release work docs-first
   gated while exempting only the bounded repair/review class above.

## TDD evidence

RED, after adding only the regression tests:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh \
  tests/hermes_cli/test_factory_increment_integration.py \
  -k 'allows_docs_first_pr_review_repair_when_docs_red or validation_readiness_ignores_superseded_historical_validation_task' \
  -v --tb=short
```

Result: exit `1`; 2 selected tests failed as expected:

- `test_claim_next_task_allows_docs_first_pr_review_repair_when_docs_red` returned
  `None` instead of claiming the docs-first PR review repair.
- `test_validation_readiness_ignores_superseded_historical_validation_task`
  returned a `status=superseded` unresolved-validation finding.

GREEN focused:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh \
  tests/hermes_cli/test_factory_increment_integration.py \
  -k 'allows_docs_first_pr_review_repair_when_docs_red or validation_readiness_ignores_superseded_historical_validation_task' \
  -v --tb=short
```

Result: exit `0`; `2 tests passed, 0 failed`.

GREEN related Factory control-plane coverage:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh \
  tests/hermes_cli/test_factory_increment_integration.py \
  tests/hermes_cli/test_factory_control_plane_refactor.py
```

Result: exit `0`; `287 tests passed, 0 failed`.

## Canonical Factory status readback

Command:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main \
  factory status zeus-alpha-research-ledger-core --json \
  > /tmp/r2cy-r3-successor-integrate-r2da-status-after-code.json
```

Readback summary from `/tmp/r2cy-r3-successor-integrate-r2da-status-after-code.json`:

- `db_backend=agent_core_postgres`.
- `factory_cli_source_root` = `factory_status_source_root` = this assigned
  worktree.
- `factory_status_delegated=false`.
- Active project metadata: `reconciliation_anomalies=[]`,
  `reconciliation_projection_source=current_document_status`.
- 14/14 G1-required rows are `reviewed=true`, `indexed=true`, and
  `blocking=false` from `readiness_source=configured_base_ref` at base
  `eb3e3ff48905285812eca4c222fa2155a9282546`.
- R2cy-R1 exact-SHA quality-review task
  `zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re`
  remains `status=ready`, `phase=quality_review`.
- Gates `1025` and `1026` are present as passed predecessor PR #114 evidence,
  not reused as current-base successor review evidence.

## Delivery state and remaining blockers

This branch is the current-base successor to the stale/conflicting PR #114. It
must receive fresh exact-SHA independent quality review against the final pushed
head before it may be merged into `origin/main` or used to catch up the primary
runtime.

The primary checkout `/home/jean/Projects/hermes-agent-original` was not mutated.
The required post-integration tick/claim readback was not executed because the
fresh current-base successor is still pending independent exact-SHA review and
because this worker's hard runtime rule prohibits primary-checkout mutation
before the reviewed integration path is satisfied.

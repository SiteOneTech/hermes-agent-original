---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2av-current-origin-g1-status-projection
phase: documentation
status: current_origin_g1_status_projection_verified
validated: yes
reviewed: pending_independent_quality_review
owner: codex-builder
engine: codex
created_at: 2026-08-17T10:24:54Z
base_ref: origin/main
current_origin_sha: af9fa27eaaaa52ef173f1578fb7f572ce52cebc6
r2au_commit: 1afd37a61a8d21af393e393cb77083adb25b41c7
r2au_pr: https://github.com/SiteOneTech/hermes-agent-original/pull/61
branch: factory/zeus-alpha-research-ledger-core/inc-017-r2av-current-origin-g1-status-pr
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2av-current-origin-g1-status-pr
factory_status_log: /home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786962029-820188-d410.log
---

# R2av — current-origin G1 status projection and isolated CLI recovery

## Scope and boundary

This increment verifies the current-origin Factory G1 document-status projection after R2au PR #61 (`1afd37a61a8d21af393e393cb77083adb25b41c7`) reached `origin/main` through merge commit `af9fa27eaaaa52ef173f1578fb7f572ce52cebc6`.

The repair surface remains bounded to Factory documentation-status projection and project-local evidence. This R2av run performs no product ledger implementation, no merge, no deploy, no credential operation, no direct `factory.*` SQL, no primary-checkout mutation, no external runtime execution, no connector/messaging action, and no trading/risk/paper/live action.

## Canonical inputs read

- `DOCUMENTATION_INDEX.md` — current G1 entrypoint, required reading order, R2au/R2at/R2ap lineage, and reviewed-status semantics.
- `G0_REPOSITORY_STRATEGY.md` — Zeus-only repository strategy, PR-first policy, assigned worktree discipline, and no propagation/runtime authority.
- `FACTORY_INTAKE.md` — Agent Core/Fatory DB source-of-truth hierarchy and no external execution boundary.
- `TECHNICAL_BLUEPRINT.md` — confirms this is a private Zeus-side Agent Core ledger, not a Vonash/trading/runtime connector.
- `QA_GATES.md` and `SECURITY_GATES.md` — current R2au gate requirements, no-direct-SQL/no-primary-mutation/no-external-runtime boundaries.
- `TASK_GRAPH.md`, `TRACKER.md`, and `G1_REVIEW.md` — historical stale-primary 10-blocker evidence, R2au repair evidence, and PR-first handoff requirements.
- `R2AU_CURRENT_ORIGIN_G1_DOCUMENT_STATUS_PROJECTION_REPAIR.md` — controlling R2au RED/GREEN repair and exact Factory status line references.

## Worktree and base identity

Read-only Git verification from the assigned isolated worktree showed:

```text
git status --short --branch
## factory/zeus-alpha-research-ledger-core/inc-017-r2av-current-origin-g1-status-pr...origin/main

git rev-parse HEAD
af9fa27eaaaa52ef173f1578fb7f572ce52cebc6

git rev-parse origin/main
af9fa27eaaaa52ef173f1578fb7f572ce52cebc6

git merge-base HEAD origin/main
af9fa27eaaaa52ef173f1578fb7f572ce52cebc6

git ls-remote origin refs/heads/main
af9fa27eaaaa52ef173f1578fb7f572ce52cebc6	refs/heads/main
```

`git log --oneline -2` confirms `af9fa27eaa` is `Merge Factory increment zeus-alpha-research-ledger-core-r2au-current-origin-g1-document-status-p into main`, with parent repair commit `1afd37a61a` (`fix(factory): resolve stale g1 document projection`).

## Source-backed explanation of the `reviewed=false` projection

The stale 10-blocker projection is not current-origin document content. The project-local review records identify it as stale-primary/runtime evidence:

- `G1_REVIEW.md` lines 136–145 records the stale primary checkout `/home/jean/Projects/hermes-agent-original` at HEAD `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`, running the pre-R2v resolver and reporting 10 required-G1 blockers as `reviewed=false` in `/home/jean/.hermes/profiles/quality-reviewer/cache/terminal-output/out-1786901573-3764810-ead0.log` lines 17420–17729.
- `TRACKER.md` line 32 records the same stale-primary mismatch as historical R2c5 evidence, not current dispatch authority.
- The current R2av status payload still includes immutable historical/reconciler evidence that mentions old required-doc anomalies: events `194724` and `194725` in `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786962029-820188-d410.log` lines 470–480 and 499–509 show `anomalies=["unvalidated_required_docs"]` before the current project projection. Those event rows are audit history.
- The same status payload also retains older gate evidence with `reviewed=false` rows: lines 8556–8770 show a historical `document_status_snapshot` with stale blockers. That snapshot is gate evidence, not the active `projects[0].document_status` projection.

Therefore, the source-backed root cause of the stale `reviewed=false` view is stale primary/runtime or historical event/gate projection data being read as if it were current. It must not override the current configured-base rows.

## Current canonical Factory CLI readback

Approved read path used exactly the canonical CLI against Agent Core Postgres:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status --json zeus-alpha-research-ledger-core
```

The full output is `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786962029-820188-d410.log`.

Current active `projects[0].document_status` readback:

- Lines 20270–20626 contain the 14 `g1_required` document rows.
- Every required row has `base_ref=origin/main`, `base_branch=main`, `base_commit=af9fa27eaaaa52ef173f1578fb7f572ce52cebc6`, `readiness_source=configured_base_ref`, and `configured_base_ref_accepted=true`.
- Stale primary checkout is rejected for every row: `primary_checkout_accepted=false`, `primary_checkout_rejected_reason=primary_checkout_not_configured_base`, `primary_head=4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`.
- All 14 required G1 documents report `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, and `blocking=false`.

Active project metadata readback:

- Lines 20830–20864 show `cleared_g1_document_reconciliation_projection=true`, `cleared_project_metadata_keys=["g1_documentation_checkout"]`, `reconciliation_anomalies=[]`, `reconciliation_projection_source=current_document_status`, and `reconciliation_required=false`.
- `stale_reconciliation_projection` and `g1_documentation_checkout` are absent from the active project metadata projection.

## Test evidence

Focused GREEN verification from the assigned current-origin worktree:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'status_projection_uses_origin_base_not_stale_head_or_task_metadata or status_effective_projection_ignores_stale_unvalidated_docs_when_current_rows_clean or status_effective_projection_fails_closed_when_current_rows_block' -v --tb=short
```

Result: 1 test file, 3 selected tests passed, 0 failed, runner wall 1.9s.

The focused RED reproduction for the current-origin-versus-stale-primary class is the R2au test `test_status_projection_uses_origin_base_not_stale_head_or_task_metadata`, documented in `R2AU_CURRENT_ORIGIN_G1_DOCUMENT_STATUS_PROJECTION_REPAIR.md` lines 56–72. R2av intentionally did not create a second failing code path because the same focused test is already GREEN at exact current `origin/main` `af9fa27eaaaa52ef173f1578fb7f572ce52cebc6`; the R2av delta is source-backed current-origin evidence and PR handoff.

## Delivery handoff

This R2av branch must be delivered as a Zeus-signed GitHub PR labeled `agent:zeus` against `main`. The PR body must name:

- base/current-origin SHA `af9fa27eaaaa52ef173f1578fb7f572ce52cebc6`;
- R2au repair commit `1afd37a61a8d21af393e393cb77083adb25b41c7` and PR #61;
- final R2av candidate SHA after commit/push;
- Factory status output `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786962029-820188-d410.log`;
- test command/result above;
- explicit no direct SQL, no primary-checkout mutation, no merge/deploy/credential/external-runtime/product/trading statement.

Independent quality review and QA Guardian evidence remain required before downstream dispatch relies on this R2av evidence. This worker does not self-approve, merge, deploy, mutate primary checkout, run direct SQL, or contact external runtimes.

---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2eb-g1-dispatcher-preflight-recovery
branch: factory/zeus-alpha-research-ledger-core/inc-000-r2eb-g1-dispatcher-preflight-rec
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-000-r2eb-g1-dispatcher-preflight-rec
base_head_before_commit: 96f0ecd0a5f17d88a513cf986e5e92edadcbbd40
evidence_recorded_at_utc: 2026-08-20T21:09:15Z
status: implementation_green_local
---

# R2eb — G1 dispatcher preflight recovery evidence

## Scope boundary

This increment changes only Factory control-plane routing/preflight behavior plus focused regression evidence. It does not change Alpha Ledger product/runtime code, does not deploy, does not change credentials, does not use direct SQL, does not mutate the primary checkout, and does not perform messaging/external-runtime/trading/risk/paper/live actions.

## Canonical docs read

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/METHODOLOGY_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`

Relevant G1 rules used: docs-first gate, PR-first delivery, no direct SQL, no primary-checkout mutation, no deploy/external runtime, and strict RED -> GREEN proof for control-plane changes.

## Root cause reproduced from canonical Factory status/events

Factory CLI source of truth: Agent Core Postgres `factory.*` via:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`

RED event readback from the status payload showed the real dependency-free R2df documentation task was repeatedly preflight-denied behind downstream validation rows:

- event `207787`, `dispatch_preflight_denied`, task `zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation`, blockers started with `unresolved_validation_tasks` and included downstream validation rows such as `zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re` status `ready`.
- event `207788`, `dispatch_preflight_denied`, task `zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re`, blockers `missing_or_unindexed_docs`.

This is the claimed-null loop class: a dependency-free G1/documentation recovery existed, but downstream review/validation gates could be evaluated first and the documentation recovery itself could be classified as final/downstream validation work when its description used delivery/gate language.

## Code repair

Changed `hermes_cli/factory_pg.py`:

1. `_candidate_requires_validation_readiness_before_dispatch()` now explicitly returns `False` for docs-first repair tasks. A dependency-free G0/G1/documentation/reconciliation recovery cannot be subject to downstream validation readiness gates while it is the mechanism to clear red G1.
2. Added `_docs_first_repair_preempts_downstream_dispatch()` as the shared predicate for red-G1 docs repair priority.
3. `claim_next_review()` now skips review dispatch for a project when red G1 has a dependency-ready docs-first repair task. This prevents the tick from spending the cycle on downstream review denial before the repair can claim.
4. `claim_next_task()` reuses the same predicate when ignoring `review_ready` rows as active blockers for docs-first repair routing.

Regression tests updated in `tests/hermes_cli/test_factory_increment_integration.py`:

- strengthened `test_force_tick_routes_dependency_free_g1_doc_recovery_before_docs_blocked_quality_review` to assert no `dispatch_preflight_denied` event is recorded before the docs recovery claim;
- added `test_docs_first_recovery_is_not_downstream_validation_gated`, using an R2df-like documentation recovery whose text contains `final delivery`, `gate closure`, and `quality review` language.

## Strict TDD evidence

### RED

Command:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k "force_tick_routes_dependency_free_g1_doc_recovery_before_docs_blocked_quality_review or docs_first_recovery_is_not_downstream_validation_gated" -v --tb=short`

Observed before implementation:

- `test_force_tick_routes_dependency_free_g1_doc_recovery_before_docs_blocked_quality_review` failed because `dispatch_preflight_denied` was recorded before docs recovery claim.
- `test_docs_first_recovery_is_not_downstream_validation_gated` failed because `_candidate_requires_validation_readiness_before_dispatch(doc_recovery)` returned `True`.
- Summary: `2 failed, 126 deselected`.

### GREEN focused

Same command after implementation:

- Summary: `1 files, 2 tests passed, 0 failed`.

### GREEN broader relevant suite

Command:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_orchestrator_tick.py -v --tb=short`

Result:

- `tests/hermes_cli/test_factory_orchestrator_tick.py`: `23 passed`.
- `tests/hermes_cli/test_factory_increment_integration.py`: `128 passed`.
- Summary: `2 files, 151 tests passed, 0 failed`.

Command:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_cron_control_plane.py -v --tb=short`

Result:

- Summary: `1 files, 15 tests passed, 0 failed`.

Command:

`git diff --check`

Result: exit `0`, no whitespace errors.

## Canonical H status / resolve-state / tick readback

### Factory status readback

Command:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2eb_status_green.json && python3 /tmp/r2eb_readback.py /tmp/r2eb_status_green.json`

Result summary:

- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-000-r2eb-g1-dispatcher-preflight-rec`
- `db_backend=agent_core_postgres`, `database=zeus_agent`
- project status `active`, `autonomous=True`
- current dynamic document rows: `docs_total=22`, `doc_blockers=0`
- real R2df task: `zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation`, status `todo`, phase `documentation`, priority `19`, dependencies `[]`
- current R2eb task: status `running`, run `run-1787259327-cf9f7413`, worker `solution-architect`

### Resolve-state readback

Command:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory project resolve-state zeus-alpha-research-ledger-core --json > /tmp/r2eb_resolve_green.json && python3 /tmp/r2eb_resolve_readback.py /tmp/r2eb_resolve_green.json`

Result summary:

- action `resolve-state`
- source root: assigned R2eb worktree
- project status `active`
- `active_runs=1`, `pending_gates=0`, `anomalies=[]`
- `monitor.checked=1`, no finished run
- reopened resolved `unvalidated_required_docs` blockers for two stale tasks (`r2ai...` and `r2ae...`)
- supervisor violations/repairs: `[]`
- remaining classified blockers: 2 historical blocked rows, not the R2df docs-first route

### Tick readback

Command:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory project tick zeus-alpha-research-ledger-core --json > /tmp/r2eb_tick_green.json && python3 /tmp/r2eb_tick_readback.py /tmp/r2eb_tick_green.json`

Result summary:

- action `tick`
- source root/script: assigned R2eb worktree and `scripts/factory/factory_orchestrator_tick.py`
- `control_plane_skipped=true`
- `counts.active_runs=1`
- `claimed=null`, `spawned_worker=null`

Interpretation: live tick correctly did not claim another task while this R2eb worker run is still active. This is a single-active-run guard, not the previous R2df downstream-gate denial loop.

### Green routing predicate readback against real R2df row

Command:

`python3 /tmp/r2eb_green_predicate_readback.py`

Result:

- real R2df: status `todo`, phase `documentation`, dependencies `[]`, priority `19`
- `r2df_docs_first_repair=True`
- `r2df_validation_gate_required=False`
- with simulated red G1 preflight, `r2df_docs_first_blockers_when_g1_red=[]`
- with the same red G1 preflight, `r2cy_docs_first_blockers_when_g1_red=['missing_or_unindexed_docs']`
- `docs_first_preempts_downstream=True`

This confirms the routing invariant the live tick cannot exercise while the current R2eb run is active: R2df-style G1/docs recovery is eligible before downstream quality/review/product work under red G1.

## Remaining handoff

- Commit and PR are required before independent exact-SHA review.
- No self-approval, no merge, no deploy.

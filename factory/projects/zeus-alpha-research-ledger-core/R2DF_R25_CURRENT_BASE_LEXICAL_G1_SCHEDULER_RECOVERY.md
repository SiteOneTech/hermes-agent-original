---
project_id: zeus-alpha-research-ledger-core
increment: r2df-r25-current-base-lexical-g1-scheduler-recovery
phase: g1_recovery
status: implemented_pending_pr_review
validated: yes
reviewed: pending
owner: codex-builder
run_id: run-1787695150-26f0eda3
---

# R2df-R25 — current-base lexical G1 scheduler recovery

## Scope and boundary

This increment is a bounded Factory control-plane scheduler/dispatch repair. It changes only:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_increment_integration.py`
- project-local evidence/docs under `factory/projects/zeus-alpha-research-ledger-core/`

Assigned branch/worktree:

- branch: `factory/zeus-alpha-research-ledger-core/inc-05-r2df-r25-current-base-lexical-g1`
- worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-05-r2df-r25-current-base-lexical-g1`
- source/base before edits: `HEAD` = `origin/main` = merge-base = `50a5d59530ae49997a4968e029d8da639bf9a946`
- predecessor local-only evidence: R2df-R24 local commit `37970150a5548328cc9b9dbea542c1826c2230a7`, inspected but not cherry-picked wholesale

No product ledger implementation, QA/security/delivery task closure, deploy, credential change, external runtime action, messaging connector, direct SQL, primary checkout mutation, base-branch integration, trading, risk, paper/live run, force-push, stale PR mutation, self-approval, or merge is authorized by this increment.

## G1 docs consulted

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`

## Current-source readback

Sanctioned Factory readback command from the assigned worktree:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r25-status-after-code.json
```

Summary from `/tmp/r2df-r25-status-after-code.json`:

```text
db_backend=agent_core_postgres
project_status=active
tasks=161
gates=300
runs=300
active task/run observed=zeus-alpha-research-ledger-core-r2df-r25-current-base-lexical-g1-schedul running
g1_required=14
g1_blocking=0
readiness_sources=[configured_base_ref]
reconciliation_anomalies=[]
```

This live readback is status evidence only. The focused RED regression below intentionally sets required G1 docs red in the fixture to prove scheduler behavior while docs-first product work remains denied.

## Code repair

The prior R2df-R24 repair added a broad lexical G0/G1 recovery classifier on a stale branch. This current-base increment carries forward only the minimal applicable predicate:

1. `_has_g0_g1_recovery_terms()` recognizes a task whose phase is structurally `g0_*` or `g1_*` and whose text contains bounded recovery terms such as `scheduler`, `repair`, `recover`, `dispatch`, `bootstrap`, or `source-root`.
2. `_has_structural_product_or_runtime_dispatch_scope()` inspects only structural fields (`task_id`, `title`, `phase`) for ALR/product/runtime/base-integration scopes, so a G1 recovery description may quote prohibited operations as negative boundary evidence without being reclassified as product work.
3. `_is_docs_first_repair_dispatch_task()` uses that lexical G0/G1 recovery predicate before validation/docs-first gates, allowing dependency-ready G1 scheduler recovery to preempt docs-blocked product review rows.
4. Existing full-text product/runtime gating remains unchanged for normal implementation, direct integration, release/reporting, deploy, messaging, direct SQL, external runtime, trading/risk/paper/live, and ALR product work.

## RED / GREEN evidence

Focused RED before production-code repair:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k lexical_g1_scheduler -v --tb=short
```

Observed failure:

```text
FAILED tests/hermes_cli/test_factory_increment_integration.py::test_force_tick_routes_lexical_g1_scheduler_recovery_before_docs_blocked_product_review
assert tick["claimed"] is not None
E   assert None is not None
```

Focused GREEN after repair:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k lexical_g1_scheduler -v --tb=short
```

Result:

```text
1 tests passed, 0 failed
```

Preservation-focused GREEN:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'lexical_g1_scheduler or routes_only_g1_docs_recovery_before_direct_runtime_scope or claim_next_task_keeps_priority_order_when_docs_ready or claimed_null_predicate' -v --tb=short
```

Result:

```text
5 tests passed, 0 failed
```

Validation-readiness preservation GREEN:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'dispatch_validation_readiness_does_not_deadlock_deploy_prerequisite or validation_readiness_allows_dependency_ready_documentation_recovery_with_historical_finalized_wording' -v --tb=short
```

Result:

```text
2 tests passed, 0 failed
```

Related Factory control-plane GREEN:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_control_plane_refactor.py -v --tb=short
```

Result:

```text
291 tests passed, 0 failed
```

Diff hygiene:

```text
git diff --check
```

Result: exit `0`.

## Handoff

This artifact remains `reviewed: pending`. Delivery must be a non-draft Zeus-signed `agent:zeus` PR from the assigned branch against `main`, with final head/base SHA, no-external-execution boundary, and independent exact-SHA quality review. This worker must not merge or self-approve.

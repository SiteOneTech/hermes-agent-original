---
project_id: zeus-alpha-research-ledger-core
increment: r2df-r25-current-base-lexical-g1-scheduler-recovery
phase: g1_recovery
status: implemented_pending_pr_review
validated: yes
reviewed: pending
owner: codex-builder
run_id: run-1787697422-26be708c
prior_failed_gate: factory_gate_1101
---

# R2df-R25 — current-base lexical G1 scheduler recovery

## Scope and boundary

This rework is a bounded Factory control-plane scheduler/dispatch repair. It changes only:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_increment_integration.py`
- project-local evidence/docs under `factory/projects/zeus-alpha-research-ledger-core/`

Assigned branch/worktree:

- branch: `factory/zeus-alpha-research-ledger-core/inc-05-r2df-r25-current-base-lexical-g1`
- worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-05-r2df-r25-current-base-lexical-g1`
- exact base before this increment: `origin/main` / merge-base = `50a5d59530ae49997a4968e029d8da639bf9a946`
- rework starting candidate: `5cca8d6f3a763ff05426ab4cab9568e4e44b62f5`
- predecessor local-only evidence: R2df-R24 local commit `37970150a5548328cc9b9dbea542c1826c2230a7`, inspected but not cherry-picked wholesale

No product ledger implementation, QA/security/delivery task closure, deploy, credential change, external runtime action, messaging connector, direct SQL, primary checkout mutation, base-branch integration, trading, risk, paper/live run, force-push, stale PR mutation, self-approval, or merge is authorized by this increment.

## G1 docs consulted

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`

## Rework finding addressed

Quality gate `1101` blocked the first R2df-R25 candidate because the focused RED test was too synthetic: it used a `demo-*` task ID and did not prove the real Factory row shape whose task ID starts with `zeus-alpha-research-ledger-core-*`. The prior predicate also treated standalone substrings such as `ledger`, `runtime`, `product`, `release`, `reporting`, `risk`, `paper`, `trading`, `messaging`, `deploy`, and `connector` as structural product/runtime signals. That accidentally swallowed the project prefix `zeus-alpha-research-ledger-core` and recreated `claimed=null` even when the task was a dependency-ready lexical `phase=g1_recovery` scheduler recovery.

This rework adds a real-project-shaped regression and narrows `_has_structural_product_or_runtime_dispatch_scope()` so it matches only explicit structural scope markers with word boundaries:

- `alr-\d+`
- `product implementation`
- `ledger implementation`
- `runtime propagation`
- `external runtime`
- `direct integration`
- `origin/main integration`
- `base branch integration`
- `base branch merge`
- `deployment`
- explicit direct-SQL/live/action/market/risk/paper-run/connector phrases

It no longer matches standalone project-prefix words like `ledger`, `runtime`, `product`, `release`, `reporting`, `risk`, `paper`, `trading`, `messaging`, `deploy`, or `connector` by substring alone.

## Current-source readback

Sanctioned Factory readback command from the assigned worktree:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r25-status-after-rework.json
```

Summary from `/tmp/r2df-r25-status-after-rework.json`:

```text
db_backend=agent_core_postgres
project_status=active
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-05-r2df-r25-current-base-lexical-g1
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-05-r2df-r25-current-base-lexical-g1
tasks=161
gates=300
runs=300
g1_required=14
g1_blocking=0
reconciliation_anomalies=[]
```

This live readback is status evidence only. The focused RED regression below intentionally sets required G1 rows red in the fixture to prove scheduler behavior while docs-first product work remains denied.

## RED / GREEN evidence

Focused RED before the rework repair:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k real_project_prefixed_lexical_g1_recovery -v --tb=short
```

Observed failure:

```text
FAILED tests/hermes_cli/test_factory_increment_integration.py::test_force_tick_routes_real_project_prefixed_lexical_g1_recovery_before_product_review
assert tick["claimed"] is not None
E   assert None is not None
```

Focused GREEN after repair:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'real_project_prefixed_lexical_g1_recovery or structural_product_scope' -v --tb=short
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
293 tests passed, 0 failed
```

Diff hygiene:

```text
git diff --check
```

Result: exit `0` after final validation.

## Preserved gates

- Product/review work remains docs-first denied while required G1 rows are red. The real-prefix RED/GREEN fixture proves the product review row records `dispatch_preflight_denied` and is not claimed for review.
- ALR/product/runtime/base-integration scopes remain fail-closed because explicit `alr-\d+` and scope phrases in `task_id`, `title`, or `phase` still classify as structural product/runtime scope.
- Genuine release/reporting/final delivery paths remain validation-readiness gated by `_candidate_requires_validation_readiness_before_dispatch()` and the existing validation-readiness test file.
- The current primary-runtime stale/catch-up condition remains a separate operational dependency when live runtime still executes stale primary code; this rework delivers only the current-base source candidate and does not mutate `/home/jean/Projects/hermes-agent-original`.

## Handoff

This artifact remains `reviewed: pending`. Delivery must stay PR-first through a non-draft Zeus-signed `agent:zeus` PR from the assigned branch against `main`, with final pushed head/base SHA and independent exact-SHA quality review. This worker must not merge or self-approve.

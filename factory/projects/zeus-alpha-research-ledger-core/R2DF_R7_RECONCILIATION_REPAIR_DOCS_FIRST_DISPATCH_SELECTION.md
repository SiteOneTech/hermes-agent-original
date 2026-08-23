---
project_id: zeus-alpha-research-ledger-core
increment: r2df-r7-reconciliation-repair-docs-first-dispatch-selection
phase: g1_recovery
status: implemented_pending_pr_review
validated: yes
reviewed: pending
owner: claude-builder
run_id: run-1787451673-4d4d6b15
---

# R2df-R7 — reconciliation repair docs-first dispatch selection

## Scope

This increment repairs only the Factory dispatch/reconciliation control-plane path where a project tick can record a docs-first product-quality preflight denial before claiming an available G1/documentation recovery task.

Assigned branch/worktree:

- branch: `factory/zeus-alpha-research-ledger-core/inc-001-r2df-r7-reconciliation-repair-do`
- worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2df-r7-reconciliation-repair-do`
- base before edits: `HEAD` = `origin/main` = merge-base = `c8ff95b0daf84ffb5e931d1c9be7593ab406e275`
- remote: `https://github.com/SiteOneTech/hermes-agent-original.git`

No Alpha Ledger product/runtime code, provider client, migration, scheduler, deployment, credential, messaging connector, trading/risk/paper/live path, external runtime, primary checkout state, stale PR/task status, direct SQL, merge, self-approval, or force-push is authorized by this increment.

## G1 docs consulted

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R8_CURRENT_BASE_DOCS_FIRST_DISPATCH_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R7_INDEPENDENT_EXACT_SHA_G1_SOURCE_ROOT_REVIEW.md`

## Live Agent Core readback

Sanctioned readback command from the assigned worktree:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r7-status-after-code.json
```

Summary extracted from `/tmp/r2df-r7-status-after-code.json`:

```text
db_backend=agent_core_postgres database=zeus_agent
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2df-r7-reconciliation-repair-do
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2df-r7-reconciliation-repair-do
project zeus-alpha-research-ledger-core status=active autonomous=true anomalies=[]
g1_required=14 blockers=0
assigned_task=running phase=g1_recovery priority=1 branch=factory/zeus-alpha-research-ledger-core/inc-001-r2df-r7-reconciliation-repair-do worktree=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2df-r7-reconciliation-repair-do
assigned_run=running run_id=run-1787451673-4d4d6b15 worker=claude-builder pid=1729944 started=2026-08-23T02:21:13.685908+00:00
```

The same readback preserves the source-backed pre-repair ordering symptom as audit history:

```text
2026-08-23T02:18:30.482879+00:00 dispatch_preflight_denied task=zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re blockers=["missing_or_unindexed_docs"]
2026-08-23T02:18:28.947997+00:00 dispatch_preflight_denied task=zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation blockers=["unresolved_validation_tasks", ...]
2026-08-23T02:21:13.693667+00:00 task_claimed task=zeus-alpha-research-ledger-core-r2df-r7-reconciliation-repair-docs-first run_id=run-1787451673-4d4d6b15 worker=claude-builder
```

No live `factory project tick`, direct task mutation, `resolve-state`, direct SQL, or task close was run in this worker because the task contract permits Factory DB access only through `factory status` and `factory gate record`.

## Root cause

`force_tick()` calls `claim_next_review()` before `claim_next_task()`. R2ea already made dependency-ready documentation/G1 recovery tasks preempt review-ready product/quality work at selection time, but `claim_next_review()` still recorded `dispatch_preflight_denied` for a docs-first-gated product-quality review row before the tick fell through to the task claim path. In the live ordering condition that side-effect reproduced the claimed-null/product-denial loop even though the recovery task was runnable.

## Code repair

Changed files:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_increment_integration.py`
- project-local evidence docs under `factory/projects/zeus-alpha-research-ledger-core/`

Implementation behavior:

1. `claim_next_review()` now computes `docs_repair_preempts_review` when docs-first is red, not waived, and `_has_dependency_ready_docs_first_repair_task(tasks)` finds a runnable G1/documentation/reconciliation repair task.
2. For review candidates that already have docs-first preflight blockers under that condition, the function skips the product-quality review row without recording a denial side-effect, allowing the same tick to fall through to `claim_next_task()` and claim the recovery.
3. Product gating is not weakened: blocked review rows are still not claimed, normal product implementation/QA/security/delivery work remains docs-first gated, and denials are still recorded when no dependency-ready repair exists.

## RED / GREEN evidence

Focused RED before the code repair:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k test_force_tick_claims_g1_recovery_before_product_preflight_denials -v --tb=short
```

Observed failure:

```text
FAILED tests/hermes_cli/test_factory_increment_integration.py::test_force_tick_claims_g1_recovery_before_product_preflight_denials
AssertionError: assert 'dispatch_preflight_denied' not in joined
```

Focused GREEN after the repair:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k test_force_tick_claims_g1_recovery_before_product_preflight_denials -v --tb=short
```

Result:

```text
1 tests passed, 0 failed
```

Full touched integration file:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -v --tb=short
```

Result:

```text
134 tests passed, 0 failed
```

Related Factory control-plane suite:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_orchestrator_tick.py -v --tb=short
```

Result:

```text
314 tests passed, 0 failed
```

Claude Code independent diff review:

```text
claude-anthropic-code ... --allowedTools 'Read' --max-turns 8 --output-format json > /tmp/r2df-r7-claude-review.json
```

Result excerpt:

```text
success
PASS
No findings; the change removes only a denial side-effect for already-blocked review rows when a runnable G1/documentation repair exists, and the test proves product review/implementation remain unclaimed.
```

## Handoff

This artifact remains `reviewed: pending`. Delivery must be a Zeus-signed non-draft `agent:zeus` PR from the assigned branch against `main`, with the final commit SHA and independent exact-SHA quality review before this task can be represented as reviewed or merged. This worker must not self-approve, merge, deploy, mutate primary checkout, run direct SQL, change credentials, touch external runtime/product systems, or trigger Alpha Ledger product execution.

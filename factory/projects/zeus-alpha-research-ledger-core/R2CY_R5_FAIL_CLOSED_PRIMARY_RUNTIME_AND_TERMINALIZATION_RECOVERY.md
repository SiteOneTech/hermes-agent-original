---
document_type: factory_control_plane_recovery
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2cy-r5-fail-closed-primary-runtime-and-
run_id: run-1787314229-a600cdf5
phase: g1_recovery
status: implemented_pr_first_pending_independent_review
validated: yes
reviewed: pending
owner: devops-release
reviewer: quality-reviewer
engine: claude_code
base_ref: origin/main
base_sha: bd76d2ac360a447b02cdfaa04ddd5501301a2780
branch: factory/zeus-alpha-research-ledger-core/inc-017-r2cy-r5-fail-closed-primary-runt
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2cy-r5-fail-closed-primary-runt
created_at_utc: 2026-08-21T12:25:12Z
---

# R2cy-R5 — fail-closed primary runtime and false-terminalization recovery

## Scope and boundary

This increment changes only the Factory control-plane code and its behavioral
regression tests. It does not mutate or reset the primary checkout, merge `main`,
deploy, touch credentials, run external product/runtime systems, or dispatch
ALR/product work.

The repair addresses two source-backed failure classes:

1. A terminal provider/rate-limit review transcript whose wrapper exits `0` must
   not be finalized as `succeeded`/`done`, must not integrate the increment, and
   must requeue review.
2. Current configured-base G1 rows may prove document content is reviewed, but a
   stale primary checkout/runtime remains a product-dispatch blocker. While the
   primary checkout is not exactly the configured base, product work stays
   fail-closed and only bounded G1/control-plane recovery routes.

## G1 documents consulted

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/REQUIREMENTS_ANALYSIS.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`
- Predecessor evidence artifacts indexed in `DOCUMENTATION_INDEX.md`, especially
  `R2DB_CURRENT_ORIGIN_G1_REVIEWED_STATE_PR_RECOVERY.md`,
  `R2DC_BOUNDED_G1_REVIEWED_STATE_RECOVERY.md`,
  `R2DF_R5_FAIL_CLOSED_REVIEW_TERMINALIZATION_RECOVERY.md`,
  `R2DF_R1_DOCS_FIRST_G1_RECOVERY_DISPATCH_ROUTING_REPAIR.md`, and
  `R2CY_R3_SUCCESSOR_CURRENT_BASE_R2DA_DISPATCH_REPAIR.md`.

## Code changes

- `hermes_cli/factory_pg.py`
  - Adds row-based helpers for G1 document blockers and primary-runtime blockers.
  - Treats `primary_checkout_accepted=false` on G1 rows as not product-ready in
    `_current_g1_required_documents_ready`, status-payload claimability, and
    live dispatch preflight.
  - Keeps documentation/G1/control-plane recovery tasks exempt from product
    docs-first gating, so bounded recovery can route before product work.
  - Extends review-runtime failure recognition to wrapped MiniMax token-plan
    terminal panels (`Plan usage limit reached`, `Token Plan usage limit reached`)
    before review success integration is attempted.
- `tests/hermes_cli/test_factory_increment_integration.py`
  - Adds RED/GREEN coverage for a wrapped token-plan terminal failure with a
    same-task quality gate: no increment integration, run fails, task returns to
    `review_ready`.
  - Adds RED/GREEN coverage for a stale primary-runtime product-dispatch guard:
    product priority is lower-number/higher priority, but bounded G1 recovery is
    claimed first when G1 rows are clean only at configured base and primary is
    rejected.

No source-text inspection tests were added.

## TDD evidence

### RED

Command:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'wrapped_token_plan_terminal_failure or primary_runtime_rejection_routes_g1_recovery'
```

Readback before the implementation:

```text
2 failed, 130 deselected
- test_mark_run_finished_review_success_rejects_wrapped_token_plan_terminal_failure:
  calls == ['task-1'] instead of [] because `_integrate_increment_to_base` ran.
- test_claim_next_task_primary_runtime_rejection_routes_g1_recovery_before_product:
  claimed `demo-alr-020-product` instead of `demo-r2cy-r5-primary-runtime-g1-recovery`.
```

### GREEN focused

Command:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'wrapped_token_plan_terminal_failure or primary_runtime_rejection_routes_g1_recovery'
```

Readback after the implementation:

```text
2 tests passed, 0 failed, 130 deselected
```

### GREEN related Factory control-plane files

Commands:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py
```

Readback:

```text
tests/hermes_cli/test_factory_increment_integration.py: 132 tests passed, 0 failed
tests/hermes_cli/test_factory_orchestrator_tick.py: 23 tests passed, 0 failed
```

The test runner initially failed because this isolated worktree has no local
pytest venv; per project guidance, reruns set
`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3` and
used `scripts/run_tests.sh` rather than direct `pytest`.

## Canonical Factory and runtime evidence

### Before — sanctioned H status from primary checkout

Command:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/hermes factory status zeus-alpha-research-ledger-core --json > /tmp/r2cy-r5-h-status-before.json
```

Readback summary:

```text
db_backend=agent_core_postgres
project.status=active
autonomous_enabled=true
reconciliation_anomalies=['unvalidated_required_docs']
required_g1_rows=14
blocking_g1_rows=10
blockers=FACTORY_INTAKE.md, REQUIREMENTS_ANALYSIS.md, PATTERN_ANALYSIS.md,
  ASSUMPTIONS_AND_OPEN_QUESTIONS.md, PRD.md, ADRS.md, METHODOLOGY_PLAN.md,
  TECHNICAL_BLUEPRINT.md, TASK_GRAPH.md, SECURITY_GATES.md
active_runs=[run-1787314229-a600cdf5]
R2cy-R3 task status=done
R2cy-R3 latest review run run-1787313583-eb0595ef status=succeeded exit_code=0
```

### Before — assigned worktree status from current source

Command:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2cy-r5-worktree-status-before.json
```

Readback summary:

```text
db_backend=agent_core_postgres
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2cy-r5-fail-closed-primary-runt
factory_status_delegated=false
required_g1_rows=14
blocking_g1_rows=0
readiness_source=configured_base_ref
primary_checkout_accepted=false
primary_checkout_rejected_reason=primary_checkout_not_configured_base
primary_head=ac1fdb16051324c490d803b14dd06efffd6f9ad0
base_commit=bd76d2ac360a447b02cdfaa04ddd5501301a2780
R2cy-R3 latest review run run-1787313583-eb0595ef status=succeeded exit_code=0
```

### Resolve-state after repair source

Command:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory project resolve-state zeus-alpha-research-ledger-core --json > /tmp/r2cy-r5-worktree-resolve-after.json
```

Readback summary:

```text
exit=0
factory_project_action_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2cy-r5-fail-closed-primary-runt
active_runs=1
monitor.checked=1
monitor.finished=0
unblocked.false_review_terminalization_recoveries=1
```

After this resolve-state pass, canonical status shows the actual false-terminal
review run recovered:

```text
R2cy-R3 task status=review_ready
run-1787313583-eb0595ef status=failed exit_code=1
false_review_terminalization_run_id=run-1787313583-eb0595ef
reason=review_output_contains_runtime_failure
```

### After — sanctioned H status from primary checkout

Command:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/hermes factory status zeus-alpha-research-ledger-core --json > /tmp/r2cy-r5-h-status-after.json
```

Readback summary:

```text
db_backend=agent_core_postgres
required_g1_rows=14
blocking_g1_rows=10
primary H source still reports the ten legacy reviewed-missing blockers
R2cy-R3 task status=review_ready
run-1787313583-eb0595ef status=failed exit_code=1
```

The primary checkout remains an external runtime prerequisite and was not
mutated/reset by this run.

### After — assigned worktree status and tick

Commands:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2cy-r5-worktree-status-after.json
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory project tick zeus-alpha-research-ledger-core --json > /tmp/r2cy-r5-worktree-tick-after.json
```

Readback summary:

```text
status: 14 required G1 rows, 0 blocking at configured_base_ref
status: 14/14 G1 rows carry primary_checkout_accepted=false,
        primary_checkout_rejected_reason=primary_checkout_not_configured_base,
        primary_head=ac1fdb16051324c490d803b14dd06efffd6f9ad0,
        base_commit=bd76d2ac360a447b02cdfaa04ddd5501301a2780
tick: claimed=null because active_runs=1 (this run); spawned_worker=null;
      monitor.checked=1, monitor.finished=0
```

The tick evidence therefore did not open another increment and did not dispatch
product work. The code-level regression verifies that once the active run is gone,
product work remains fail-closed under the same primary-runtime rejection and a
bounded G1 recovery task routes first.

## Git provenance

Primary checkout readback after this run:

```text
repo=/home/jean/Projects/hermes-agent-original
branch=main
status=## main...origin/main [ahead 4, behind 2819]
HEAD=ac1fdb16051324c490d803b14dd06efffd6f9ad0
origin/main=bd76d2ac360a447b02cdfaa04ddd5501301a2780
merge-base=c846ccfbd844c2f8810a26776505ec44a2341914
ahead/behind=4 2819
```

Assigned worktree pre-commit readback:

```text
repo=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2cy-r5-fail-closed-primary-runt
branch=factory/zeus-alpha-research-ledger-core/inc-017-r2cy-r5-fail-closed-primary-runt
HEAD=bd76d2ac360a447b02cdfaa04ddd5501301a2780
origin/main=bd76d2ac360a447b02cdfaa04ddd5501301a2780
merge-base=bd76d2ac360a447b02cdfaa04ddd5501301a2780
ahead/behind=0 0 before committing this increment
```

## Fail-closed result

- Provider/rate-limit review output is fail-closed before review terminalization
  and before increment integration.
- Product dispatch is fail-closed when the primary runtime is not the configured
  base, even if the configured-base G1 document rows are clean.
- Bounded G1/control-plane recovery remains dispatchable so the project can
  recover without ALR/product work.
- The stale primary checkout remains unmodified and must be caught up through an
  explicitly authorized, reviewed runtime path after PR-first delivery.

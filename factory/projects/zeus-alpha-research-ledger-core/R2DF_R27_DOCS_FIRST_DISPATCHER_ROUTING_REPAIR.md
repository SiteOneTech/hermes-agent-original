---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2df-r27-docs-first-dispatcher-routing-r
phase: documentation
status: implemented
validated: yes
reviewed: pending
owner: codex-builder
run_id: run-1787700947-a2fb30c6
---

# R2df-R27 — docs-first dispatcher routing repair for unreviewed G1 documents

## Scope
This increment repairs only the Hermes Factory control-plane dispatcher inside the assigned isolated worktree:

- Branch: `factory/zeus-alpha-research-ledger-core/inc-07-r2df-r27-docs-first-dispatcher-r`
- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-07-r2df-r27-docs-first-dispatcher-r`
- Base at start of implementation: `origin/main` / `HEAD` / merge-base `50a5d59530ae49997a4968e029d8da639bf9a946`

No primary checkout mutation, direct SQL, merge, deploy, credential change, external runtime contact, messaging connector activation, trading/risk/paper/live action, or ALR product dispatch is authorized by this increment.

## Canonical documents read
The implementation used the project-local G1/documentation context below before code changes:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/METHODOLOGY_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R8_CURRENT_BASE_DOCS_FIRST_DISPATCH_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R1_DOCS_FIRST_G1_RECOVERY_DISPATCH_ROUTING_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DL_G1_DOCUMENTATION_DISPATCH_VALIDATOR_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DI_DOCS_FIRST_FAIL_CLOSED_REVIEW_TERMINALIZATION_AND_DISPATCH_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`

## RED evidence
A focused regression test was added to reproduce the project-shaped failure mode:

- Active autonomous project.
- Zero active task runs.
- Required G1 document rows exist, are indexed, committed, and validated, but are unreviewed (`missing=["reviewed"]`, `blocking=true`).
- A docs-first G1 recovery task is runnable.
- A review-ready docs/control-plane review and product implementation row are also present.

Pre-fix result:

```text
scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k test_force_tick_claims_docs_recovery_before_review_when_g1_docs_unreviewed -v --tb=short
FAILED: expected demo-r2df-r27-unreviewed-g1-docs-recovery, got demo-r2df-independent-docs-first-review
```

That failure showed `force_tick()` could spend the dispatch slot on review before the runnable documentation/G1 recovery task.

## Repair
`hermes_cli/factory_pg.py::claim_next_review()` now skips review dispatch for a project when all of the following are true:

1. docs-first preflight says the project docs are not ready;
2. docs-first has not been waived; and
3. a dependency-ready docs-first repair/reconciliation task is runnable.

The existing `claim_next_task()` docs-first ordering then claims the documentation/G1 recovery task and keeps product/QA/security/delivery/release work fail-closed behind the G1 preflight.

## GREEN evidence
Commands executed from the assigned worktree with the sanctioned test wrapper:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k test_force_tick_claims_docs_recovery_before_review_when_g1_docs_unreviewed -v --tb=short
# 1 passed, 0 failed

HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py
# 134 passed, 0 failed

HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory.py tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_cron_control_plane.py tests/hermes_cli/test_factory_successor_control.py tests/hermes_cli/test_factory_project_reopen.py
# 350 passed, 0 failed
```

`git diff --check` exited 0.

## Agent Core evidence
Sanctioned Factory readback from this worktree after implementation:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json
project_status=active autonomous=true docs_rows=22 g1_required=14 g1_blocking=0
running task: zeus-alpha-research-ledger-core-r2df-r27-docs-first-dispatcher-routing-r documentation codex-builder
```

Factory gate evidence recorded through the sanctioned CLI surface:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory gate record zeus-alpha-research-ledger-core implementation passed --task-id zeus-alpha-research-ledger-core-r2df-r27-docs-first-dispatcher-routing-r --reviewer codex-builder --notes ... --json
{"gate_id": 1103, "project_id": "zeus-alpha-research-ledger-core", "status": "passed"}
```

Verified readback:

```text
gate_id=1103 project_id=zeus-alpha-research-ledger-core task_id=zeus-alpha-research-ledger-core-r2df-r27-docs-first-dispatcher-routing-r gate_type=implementation status=passed reviewer=codex-builder
```

## Review state
This artifact is implementation evidence only. Independent exact-SHA review remains required before task closure/merge. The branch must be delivered PR-first as an `agent:zeus` PR.

---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2d4-phase-explicit-g1-documentation-rec
run_id: run-1788313705-1bf16e75
phase: g1_recovery
status: implemented_pending_pr_and_independent_exact_sha_review
validated: yes
reviewed: pending_independent_exact_sha_review
owner: codex-builder
reviewer: quality-reviewer
base_ref: origin/main
base_sha: 63a866d57bda6a1258de6c93d0f244316f298828
branch: factory/zeus-alpha-research-ledger-core/inc-104-r2d4-documentation-recovery-dispatch-classifier
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-104-r2d4-documentation-recovery-dispatch-classifier
---

# R2d4 — phase-explicit G1 documentation recovery dispatch classifier

## Scope and boundary

R2d4 is a bounded Factory scheduler/control-plane repair for the dispatch-preflight classifier. It ensures a same-project `phase=documentation` or `phase=g1_recovery` G1 documentation/review-evidence recovery task can be claimed while unrelated validation rows are still unresolved, without allowing product, ALR, QA/security, runtime, reporting, delivery, external execution, activation, direct-SQL, messaging, trading/risk, paper/live, deploy, merge, primary-checkout mutation, credential change, or base-branch integration work to run while G1 remains red.

Changed files are limited to:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_control_plane_refactor.py`
- `tests/hermes_cli/test_factory_increment_integration.py`
- project-local evidence under `factory/projects/zeus-alpha-research-ledger-core/`

This increment does not add or change Alpha Research Ledger product/runtime code, providers, migrations, user-facing tools, credentials, external runtimes, messaging connectors, deployments, direct Factory DB state, G1 reviewed frontmatter markers, stale PR/task state, Vonash/Magnus/VAOS/RAG/KB/broker/trading/risk, or paper/live behavior.

## Canonical inputs consulted

Required Factory/G1 inputs read from the assigned worktree before implementation:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`

Agent Core Postgres `factory.*` remains the operational source of truth. This document is project-local evidence and does not substitute for Factory DB gate/readback records.

## Worktree identity

Pre-edit assigned worktree identity:

```text
branch=factory/zeus-alpha-research-ledger-core/inc-104-r2d4-documentation-recovery-dispatch-classifier
HEAD=63a866d57bda6a1258de6c93d0f244316f298828
origin_main=63a866d57bda6a1258de6c93d0f244316f298828
merge_base=63a866d57bda6a1258de6c93d0f244316f298828
```

No primary checkout mutation, merge, deploy, direct SQL, credential change, external runtime, messaging, or product dispatch was used.

## Canonical Factory readback

Sanctioned readback command from the assigned worktree:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2d4-status-final.json
```

Summarized readback:

```text
status_json_bytes=4858649
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-104-r2d4-documentation-recovery-dispatch-classifier
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-104-r2d4-documentation-recovery-dispatch-classifier
factory_status_delegated=false
project_id=zeus-alpha-research-ledger-core
project_status=active
reconciliation_anomalies=[]
g1_required_rows=14
g1_required_blocking_rows=0
task_id=zeus-alpha-research-ledger-core-r2d4-phase-explicit-g1-documentation-rec
task_status=running
task_phase=g1_recovery
task_owner=codex-builder
```

The same status payload preserves both the canonical denial that motivated this repair and the current task claim event:

```text
event_258502 type=dispatch_preflight_denied task=zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation actor=factory-dispatcher blockers=unresolved_validation_tasks + blocked/superseded/ready/todo validation rows
event_258505 type=task_created task=zeus-alpha-research-ledger-core-r2d4-phase-explicit-g1-documentation-rec actor=factory-orchestrator
event_258510 type=task_claimed task=zeus-alpha-research-ledger-core-r2d4-phase-explicit-g1-documentation-rec actor=factory-force-tick message="Task zeus-alpha-research-ledger-core-r2d4-phase-explicit-g1-documentation-rec claimed for codex-builder"
```

No live `tick`, `resolve-state`, task-close, or direct SQL command was run by this worker; the hard write allowlist for this run permitted only `factory status` and `factory gate record` for Factory DB interaction.

## RED reproduction

Focused TDD was verified before the production change. The RED command failed as expected:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'phase_documentation_g1_recovery_bypasses_canonical_258502 or docs_red_preflight_keeps_product_alr_qa_security_runtime_reporting_external_fail_closed' -v --tb=short
Result before production repair: exit 1.
```

The failing focused test reproduced the event-258502 class: a same-project `phase=documentation` G1 document review-evidence restore, with only historical final/gate wording and no G1-recovery metadata, was evaluated behind unrelated validation rows instead of being selected as the recovery prerequisite. The same test set kept product/ALR, activation, and security-review candidates fail-closed while required G1 evidence was red, including the follow-up RED case for `phase=g1_security_review`.

## GREEN repair

Changed behavior in `hermes_cli/factory_pg.py`:

- `_candidate_requires_validation_readiness_before_dispatch()` now bypasses unresolved-validation readiness for explicit G0/G1/documentation/docs/planning control-plane phases when the candidate is not reporting and has no positive product/runtime/ALR/external/direct-SQL scope.
- `_is_docs_first_gated_dispatch_task()` applies the same phase/positive-scope distinction before raw product/runtime text matching, so negative guardrail clauses such as "No product implementation" do not make a documentation recovery rank as downstream product work.
- Existing fail-closed checks for product/runtime/ALR/external/direct-SQL scopes and reporting/QA/security/runtime/delivery paths remain in place.

## Verification

Commands run from the assigned worktree with the hermetic test wrapper:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'phase_documentation_g1_recovery_bypasses_canonical_258502 or docs_red_preflight_keeps_product_alr_qa_security_runtime_reporting_external_fail_closed' -v --tb=short
Result after production repair: exit 0.

HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'phase_documentation_g1_recovery_past_canonical_258502_validation_rows' -v --tb=short
Result: exit 0.

HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_increment_integration.py -v --tb=short
Result: 301 tests passed, 0 failed.

HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -v --tb=short
Result: 24 tests passed, 0 failed.

git diff --check
Result: exit 0.
```

## PR-first handoff

This artifact is candidate evidence. The final commit SHA, pushed branch, PR URL, and Factory gate evidence are recorded after commit/push because a commit cannot contain its own SHA. Independent exact-SHA quality review by a distinct reviewer remains required before merge, task closure, or downstream Factory control relies on this repair.

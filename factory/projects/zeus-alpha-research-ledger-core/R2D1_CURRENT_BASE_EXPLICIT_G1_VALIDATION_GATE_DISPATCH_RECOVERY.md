---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2d1-current-base-explicit-g1-validation
run_id: run-1788301601-db57bb8f
phase: g1_recovery
status: implemented_pending_pr_and_independent_exact_sha_review
validated: yes
reviewed: pending_independent_exact_sha_review
owner: codex-builder
reviewer: quality-reviewer
base_ref: origin/main
base_sha: dde53dbe0207bdbce22d417b32ffd3cb802ab29b
branch: factory/zeus-alpha-research-ledger-core/inc-102-r2d1-current-base-explicit-g1-va
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-102-r2d1-current-base-explicit-g1-va
---

# R2d1 — current-base explicit G1 validation-gate dispatch recovery

## Scope and boundary

R2d1 is a bounded Factory scheduler/control-plane repair. It replaces broad task-text validation-readiness eligibility with explicit G1/documentation recovery phase or metadata signals, so no-product/no-runtime G1/documentation recovery work can be selected while required docs remain red, without opening product, ALR, QA, security, runtime, reporting, delivery, external execution, direct-SQL, messaging, trading/risk, paper/live, deploy, or base-branch integration dispatch.

Changed files are limited to:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_control_plane_refactor.py`
- `tests/hermes_cli/test_factory_increment_integration.py`
- project-local evidence under `factory/projects/zeus-alpha-research-ledger-core/`

This increment does not add or alter Alpha Research Ledger product/runtime code, providers, migrations, user-facing tools, credentials, messaging connectors, deployment behavior, primary checkout state, G1 reviewed frontmatter markers, task status, stale refs/PRs, direct Factory DB state, Vonash/Magnus/VAOS/RAG/KB/broker/trading/risk, or paper/live behavior.

## Canonical inputs consulted

Required Factory/G1 inputs read from the assigned worktree before implementation:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`

Agent Core Postgres `factory.*` remains the operational source of truth. This document is project-local evidence and does not substitute for Factory DB gate/readback records.

## Current-base worktree identity

After `git fetch origin main --prune`, the assigned worktree read back:

```text
branch=factory/zeus-alpha-research-ledger-core/inc-102-r2d1-current-base-explicit-g1-va
HEAD=dde53dbe0207bdbce22d417b32ffd3cb802ab29b
origin_main=dde53dbe0207bdbce22d417b32ffd3cb802ab29b
merge_base=dde53dbe0207bdbce22d417b32ffd3cb802ab29b
ahead_behind=0 0
```

No blocked R44 worktree, protected-branch push path, primary checkout mutation, merge, deploy, direct SQL, external runtime, or product dispatch was used.

## Canonical Factory readback

Sanctioned readback command from the assigned worktree:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2d1-status-final.json
```

Summarized readback:

```text
db_backend=agent_core_postgres
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-102-r2d1-current-base-explicit-g1-va
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-102-r2d1-current-base-explicit-g1-va
factory_status_delegated=false
project_id=zeus-alpha-research-ledger-core
project_status=active
reconciliation_anomalies=[]
task_id=zeus-alpha-research-ledger-core-r2d1-current-base-explicit-g1-validation
task_status=running
task_phase=g1_recovery
task_owner=codex-builder
task_branch=factory/zeus-alpha-research-ledger-core/inc-102-r2d1-current-base-explicit-g1-va
```

Tick/event readback from the same status payload shows this exact run was selected by the canonical tick path:

```text
event_id=257892 type=task_claimed actor=factory-force-tick task=zeus-alpha-research-ledger-core-r2d1-current-base-explicit-g1-validation message=Task zeus-alpha-research-ledger-core-r2d1-current-base-explicit-g1-validation claimed for codex-builder worker=codex-builder run_id=run-1788301601-db57bb8f
run_id=run-1788301601-db57bb8f status=running worker=codex-builder claimed_by=factory-force-tick spawned_by=factory_orchestrator_tick worker_cwd=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-102-r2d1-current-base-explicit-g1-va
```

The same readback preserves the canonical pre-repair denial cause for candidates R2df-R39, R2df-R23, R2df-R17, and R2df documentation recovery:

```text
event_id=257883 type=dispatch_preflight_denied task=zeus-alpha-research-ledger-core-r2df-r39-fail-closed-terminalization-of- blockers=["unresolved_validation_tasks", ...]
event_id=257884 type=dispatch_preflight_denied task=zeus-alpha-research-ledger-core-r2df-r23-fail-closed-review-runtime-fail blockers=["unresolved_validation_tasks", ...]
event_id=257885 type=dispatch_preflight_denied task=zeus-alpha-research-ledger-core-r2df-r17-docs-first-validation-scheduler blockers=["unresolved_validation_tasks", ...]
event_id=257886 type=dispatch_preflight_denied task=zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation blockers=["unresolved_validation_tasks", ...]
```

## RED reproduction

Focused TDD was verified by temporarily reverting only `hermes_cli/factory_pg.py` to the current `origin/main` implementation while keeping the new tests, then restoring the production patch. The RED command failed as expected:

```text
scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'explicit_g1_or_documentation_recovery_signal or explicit_g1_recovery_phase_bypasses_validation_deadlock or docs_red_preflight_keeps_product_alr_qa_security_runtime_reporting_external_fail_closed' -v --tb=short
Result before production repair: 1 passed, 2 failed.
Failures:
- test_validation_readiness_requires_explicit_g1_or_documentation_recovery_signal selected text-only `demo-text-only-g1-docs-recovery` instead of denying it with unresolved validation tasks.
- test_docs_red_preflight_keeps_product_alr_qa_security_runtime_reporting_external_fail_closed returned no `missing_or_unindexed_docs` blockers for a `phase=g1_recovery` product/ALR implementation candidate.
```

This reproduces the actual R2d1 defect class: broad prose/phase matching allowed non-explicit or product-scoped candidates to pass the docs/validation gate, while eligible recovery candidates could be denied by unresolved validation rows in the live control plane.

## GREEN repair

Changed behavior in `hermes_cli/factory_pg.py`:

- Adds explicit documentation-recovery metadata recognition for `documentation_recovery`, `docs_first_recovery`, `g1_documentation_recovery`, and `validation_preflight_recovery`.
- Adds `_has_explicit_g1_or_documentation_recovery_scope()` so the docs-first validation/readiness bypass is tied to G0/G1/documentation/planning phase or structured recovery metadata, not broad task prose alone.
- Narrows `_is_explicit_g1_recovery_task()` to `phase=g1_recovery` or recovery metadata in a G0/G1/documentation/planning phase, rejects validation/reporting tasks, and requires no positive product/runtime scope.
- Reuses positive product/runtime/ALR/direct-SQL/external scope checks for validation-readiness and docs-first preflight classification.
- Keeps product, ALR, QA, security, runtime, reporting, delivery, external execution, messaging, direct-SQL, deploy, trading/risk, paper/live, and base-branch integration fail-closed while docs are red.

A neighboring integration test that intentionally exercises a docs-first quality-review/provenance repair was updated to mark the task with explicit `metadata: {"documentation_recovery": true}`. That preserves the allowed review-repair path while proving it is no longer inferred from text alone.

## Verification

Commands run from the assigned worktree with the hermetic wrapper:

```text
scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'explicit_g1_or_documentation_recovery_signal or explicit_g1_recovery_phase_bypasses_validation_deadlock or docs_red_preflight_keeps_product_alr_qa_security_runtime_reporting_external_fail_closed' -v --tb=short
Result after production repair: 3 tests passed, 0 failed.

scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_increment_integration.py -v --tb=short
Result: 323 tests passed, 0 failed.

git diff --check
Result: exit 0.
```

## PR-first handoff

This artifact is candidate evidence. The final candidate commit SHA, pushed branch, PR URL, and Factory gate evidence are recorded after commit/push because a commit cannot contain its own SHA. Independent exact-SHA review by a distinct reviewer remains required before merge, closure, or downstream Factory control relies on this repair.

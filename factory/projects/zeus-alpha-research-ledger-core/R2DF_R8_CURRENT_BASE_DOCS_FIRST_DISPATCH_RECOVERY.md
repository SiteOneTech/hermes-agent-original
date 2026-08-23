---
project_id: zeus-alpha-research-ledger-core
increment: r2df-r8-current-base-docs-first-dispatch-recovery
phase: g1_recovery
status: implemented_pending_pr_review
validated: yes
reviewed: pending
owner: codex-builder
run_id: run-1787448909-b75dc056
---

# R2df-R8 — current-base docs-first dispatcher recovery

## Scope

This increment ports only the docs-first dispatch repair from stale PR #124 onto the fresh assigned current-base worktree.

Assigned branch/worktree:

- branch: `factory/zeus-alpha-research-ledger-core/inc-001-r2df-r8-current-base-docs-first`
- worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2df-r8-current-base-docs-first`
- current base before edits: `origin/main` = `HEAD` = merge-base = `c57565d655c31fc615b3eaaa082b50cc87ddb4dd`
- source PR provenance: PR #124, open, non-draft, `agent:zeus`, head `6d1c56c4881621075bbbe5f957e09dce178a10a1`, base `3b6dca81f5633df64f47f5861d0b618adb8f76eb`
- predecessor gates read back from Agent Core status: implementation gate `1051` PASS, quality gate `1052` PASS, security gate `1053` PASS for PR #124/R2df-R6/R2df-R7 evidence

No product ledger implementation, QA/security/delivery task closure, deploy, credential change, external runtime action, messaging connector, direct SQL, primary checkout mutation, base-branch integration, trading, risk, paper/live run, force-push, PR #124 mutation, or merge is authorized by this increment.

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
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r8-status-after-code.json
```

Summary from `/tmp/r2df-r8-status-after-code.json`:

```text
db_backend=agent_core_postgres
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2df-r8-current-base-docs-first
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2df-r8-current-base-docs-first
factory_status_delegated=false
g1_required=14
g1_blocked=0
readiness_sources=configured_base_ref
base_commits=c57565d655c31fc615b3eaaa082b50cc87ddb4dd
reconciliation_anomalies=[]
reconciliation_projection_source=current_document_status
cleared_g1_document_reconciliation_projection=true
```

## Code repair

Changed files:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_increment_integration.py`
- project-local evidence docs under `factory/projects/zeus-alpha-research-ledger-core/`

Implementation behavior:

1. `_has_docs_first_repair_terms()` now requires explicit document/G1 readiness plus repair/recovery/provenance/control-plane terms before a task can receive the docs-first recovery bypass.
2. `_has_product_or_runtime_dispatch_scope()` classifies ALR/product/runtime/deploy/messaging/direct-SQL/trading/risk/paper-live/base-integration scopes as sensitive and validation-gated even when their phase uses G1/recovery language.
3. `_candidate_requires_validation_readiness_before_dispatch()` still lets clean docs-first G1 recovery run before unresolved downstream validation rows, but keeps product/runtime scopes fail-closed.
4. `_is_docs_first_gated_dispatch_task()` keeps non-docs G1/recovery scopes preflight-gated instead of treating every `g1_*` phase as documentation repair.
5. `_current_g1_required_documents_ready()` and `_g1_required_status_rows_ready()` separate current document-content readiness from stale-primary/runtime identity, preserving product/runtime fail-closed routing without reintroducing stale `unvalidated_required_docs` projection.

## RED / GREEN evidence

Focused RED before the code repair:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k test_claim_next_task_routes_only_g1_docs_recovery_before_direct_runtime_scope -v
```

Observed failure:

```text
FAILED tests/hermes_cli/test_factory_increment_integration.py::test_claim_next_task_routes_only_g1_docs_recovery_before_direct_runtime_scope
AssertionError: expected demo-r2df-current-base-g1-documentation but selected demo-r2cw-premature-live-run-direct-integration
```

Focused GREEN after the repair:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k test_claim_next_task_routes_only_g1_docs_recovery_before_direct_runtime_scope -v
```

Result:

```text
1 tests passed, 0 failed
```

Related Factory control-plane GREEN:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_orchestrator_tick.py -v --tb=short
```

Result:

```text
313 tests passed, 0 failed
```

## Trailing-whitespace recovery

R2df-R7 gate notes for PR #124 identified five trailing-whitespace lines in `R2DF_R6_FAIL_CLOSED_DOCS_FIRST_DISPATCH_RECOVERY.md` despite the PR #124 implementation note saying `git diff --check` passed. This R8 current-base port does not import that stale evidence file verbatim; the task/status rows are recorded without trailing tabs, and final `git diff --check` must be clean before PR handoff.

## Handoff

This artifact remains `reviewed: pending`. Delivery must be a new non-draft Zeus-signed `agent:zeus` PR from the assigned branch against `main`, with final head/base SHA, no-external-execution statement, and independent exact-SHA quality review plus QA Guardian handoff. This worker must not merge or self-approve.

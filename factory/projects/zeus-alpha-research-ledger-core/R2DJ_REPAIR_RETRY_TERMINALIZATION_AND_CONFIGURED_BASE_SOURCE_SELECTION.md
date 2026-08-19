---
project_id: zeus-alpha-research-ledger-core
increment: r2dj-repair-retry-terminalization-and-configured-base-source-selection
phase: documentation
run_id: run-1787145836-42741487
status: implemented
validated: yes
reviewed: pending
owner: codex-builder
---

# R2dj — repair retry terminalization and configured-base source selection

## Scope

R2dj is a bounded Factory control-plane repair for the post-R2di failure: a sanctioned primary-root Factory CLI readback still showed ten required G1 documents with `reviewed=false` and `reconciliation_anomalies=["unvalidated_required_docs"]`, while the R2di task had terminalized after a quality-review transcript with HTTP 429/provider failures and zero reviewer tool calls.

This increment changes only local Factory control-plane source selection and review-run terminalization behavior in the assigned worktree/branch. It does not dispatch product work, mutate primary checkout, deploy, change credentials, write direct SQL, touch external runtime, or authorize ALR/Vonash/VAOS/RAG/broker/trading activity.

## Canonical documents consulted

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/REQUIREMENTS_ANALYSIS.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DI_DOCS_FIRST_FAIL_CLOSED_REVIEW_TERMINALIZATION_AND_DISPATCH_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DC_BOUNDED_G1_REVIEWED_STATE_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2CV_CURRENT_ORIGIN_G1_DOCUMENTATION_VALIDATION_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2CU_PRIMARY_ROOT_DOCS_FIRST_G1_RESOLVER_REPAIR.md`

## Live pre-change readback evidence

Primary-root sanctioned readback (read-only):

```text
cd /home/jean/Projects/hermes-agent-original
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2dj-primary-status-before.json
jq summary result:
factory_cli_source_root=null
factory_status_source_root=null
factory_status_delegated=null
db_backend=agent_core_postgres
project_status=active
metadata_reconciliation_anomalies=["unvalidated_required_docs"]
g1_count=14
blocking_count=10
blocking_docs=["FACTORY_INTAKE.md","REQUIREMENTS_ANALYSIS.md","PATTERN_ANALYSIS.md","ASSUMPTIONS_AND_OPEN_QUESTIONS.md","PRD.md","ADRS.md","METHODOLOGY_PLAN.md","TECHNICAL_BLUEPRINT.md","TASK_GRAPH.md","SECURITY_GATES.md"]
readiness_sources=[null]
base_commits=[]
```

Primary checkout provenance:

```text
primary_branch=main
primary_HEAD=ac1fdb16051324c490d803b14dd06efffd6f9ad0
primary_origin_main=cc43e6dace789da06d103ba512a3f4863fb0edc9
primary_merge_base=c846ccfbd844c2f8810a26776505ec44a2341914
primary_ahead_behind=4 2243
primary_status=clean
```

Assigned worktree current configured-base readback before code edits:

```text
cd /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-009-r2dj-repair-retry-terminalizatio
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2dj-worktree-status-before.json
jq summary result:
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-009-r2dj-repair-retry-terminalizatio
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-009-r2dj-repair-retry-terminalizatio
factory_status_delegated=false
metadata_reconciliation_anomalies=[]
reconciliation_projection_source=current_document_status
g1_count=14
blocking_count=0
readiness_sources=["configured_base_ref"]
base_commits=["cc43e6dace789da06d103ba512a3f4863fb0edc9"]
```

## Repair summary

1. Review-run terminalization now rejects additional invalid positive review paths before any increment integration:
   - provider/runtime failure transcript lines, including MiniMax/OpenAI-style HTTP 429 and `No tool calls were made during this run` summaries;
   - run metadata proving zero reviewer tool calls, e.g. `reviewer_tool_calls=0`;
   - explicit no-independent-verdict output;
   - task-bound passed review gates whose timestamp predates the review run, preventing historical gate substitution.
2. Failed/invalid review runs remain fail-closed as `review_ready` when retryable review evidence is missing; merge/integration is not called.
3. Stale primary-root `factory status` and resolver-class `factory project resolve-state` no longer fall back to stale primary DB readback when the configured-base source evidence is dirty, ahead, or unavailable. They return a fail-closed error instead.
4. Existing verified configured-base delegation remains intact for clean exact configured-base source roots, and tick retains the same fail-closed behavior.

## RED evidence

Review terminalization RED tests were added and failed on current R2di code because it integrated/closed despite invalid review evidence:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'zero_tool_calls_metadata or no_independent_verdict or historical_task_gate_before_run' -v --tb=short
Result: FAILED, 3 failed.
Failures: zero tool-call metadata, no independent verdict, and historical gate-before-run all called _integrate_increment_to_base and attempted terminal done.
```

Configured-base source-selection RED tests were added and failed on current R2di code because dirty/ahead/unavailable configured-base evidence fell back into the stale backend:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k 'status_fails_closed_when_stale_primary_configured_base or resolve_state_fails_closed_when_stale_primary_configured_base' -v --tb=short
Result: FAILED, 4 failed.
Failures: stale backend used for dirty, unavailable, and ahead configured-base status evidence; stale backend used for dirty resolve-state.
```

## GREEN evidence

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m ruff check hermes_cli/factory.py hermes_cli/factory_pg.py tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_orchestrator_tick.py
Result: All checks passed.
```

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'zero_tool_calls_metadata or no_independent_verdict or historical_task_gate_before_run' -v --tb=short
Result: 3 tests passed, 0 failed.
```

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k 'status_fails_closed_when_stale_primary_configured_base or resolve_state_fails_closed_when_stale_primary_configured_base' -v --tb=short
Result: 4 tests passed, 0 failed.
```

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_orchestrator_tick.py -v --tb=short
Result: 151 tests passed, 0 failed.
```

Final assigned-worktree canonical Factory status readback after code/docs edits:

```text
cd /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-009-r2dj-repair-retry-terminalizatio
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2dj-worktree-status-final.json
jq summary result:
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-009-r2dj-repair-retry-terminalizatio
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-009-r2dj-repair-retry-terminalizatio
factory_status_delegated=false
metadata_reconciliation_anomalies=[]
reconciliation_projection_source=current_document_status
g1_count=14
blocking_count=0
readiness_sources=["configured_base_ref"]
base_commits=["cc43e6dace789da06d103ba512a3f4863fb0edc9"]
```

## Files changed

- `hermes_cli/factory.py`
- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_increment_integration.py`
- `tests/hermes_cli/test_factory_orchestrator_tick.py`
- `factory/projects/zeus-alpha-research-ledger-core/R2DJ_REPAIR_RETRY_TERMINALIZATION_AND_CONFIGURED_BASE_SOURCE_SELECTION.md`
- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`

## Handoff contract

Delivery remains PR-first. The final pushed PR must be non-draft, Zeus-signed, labeled `agent:zeus`, and bind the exact candidate SHA in the PR body. Independent task-bound quality review must record a verdict against that exact SHA before task closure. No merge, direct SQL, deployment, primary checkout mutation, credential change, messaging side effect, external runtime, product dispatch, or trading/risk activity is authorized by this increment.

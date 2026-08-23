---
project_id: zeus-alpha-research-ledger-core
increment: r2df-r6-fail-closed-docs-first-dispatch-recovery
phase: g1_recovery
status: implemented_pending_pr_review
validated: yes
reviewed: pending
owner: codex-builder
run_id: run-1787443181-fc2dd4cf
---

# R2df-R6 — fail-closed docs-first dispatch recovery

## Scope

This increment repairs the Factory control-plane dispatch predicate that can let non-documentation G1/recovery work compete with the docs-first G1/documentation recovery path after canonical tick event `216503`.

The repair is bounded to the assigned worktree and branch:

- worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2df-r6-fail-closed-docs-first-d`
- branch: `factory/zeus-alpha-research-ledger-core/inc-018-r2df-r6-fail-closed-docs-first-d`
- files changed: `hermes_cli/factory_pg.py`, `tests/hermes_cli/test_factory_increment_integration.py`, and project-local Factory evidence docs.

No product ledger implementation, QA/security/delivery task closure, deploy, credential change, external runtime action, messaging connector, direct SQL, primary checkout mutation, base-branch integration, trading, risk, paper/live run, or merge is authorized by this increment.

## Canonical readback used

Required docs read before implementation/review:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/PRD.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`

Factory status evidence was captured with the sanctioned CLI read path:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r6-status-after.json
```

Current readback summary from `/tmp/r2df-r6-status-after.json`:

```text
db_backend=agent_core_postgres
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2df-r6-fail-closed-docs-first-d
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2df-r6-fail-closed-docs-first-d
factory_status_delegated=false
document_rows=22
g1_required=14
g1_blocked=0
readiness_sources=configured_base_ref
base_commits=3b6dca81f5633df64f47f5861d0b618adb8f76eb
project_reconciliation_anomalies=[]
```

Canonical historical tick event reproduced from the same Agent Core status payload:

```text
216503	2026-08-22T23:58:05.739185+00:00	zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation	dispatch_preflight_denied	11	unresolved_validation_tasks
```

The blocker list is `unresolved_validation_tasks` plus ten validation rows, including superseded historical review tasks and current `ready`/`todo` validation tasks. This is the exact audit event that denied the R2df documentation task before it could repair docs readiness.

Current selected task status readback relevant to this increment:

```text
zeus-alpha-research-ledger-core-r2df-r6-fail-closed-docs-first-dispatch-	running	g1_recovery	18	codex-builder	factory-force-tick
zeus-alpha-research-ledger-core-r2cw-fail-closed-recovery-for-premature-	ready	implementation	19	claude-builder	
zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation	todo	documentation	19	codex-builder	
zeus-alpha-research-ledger-core-alr-020-r2-bounded-pr-first-signature-an	ready	implementation	20	claude-builder	
zeus-alpha-research-ledger-core-alr-063-independent-security-and-no-egre	todo	security_review	62	security-reviewer	
zeus-alpha-research-ledger-core-alr-070-live-local-db-and-tool-smoke-wit	todo	qa	70	qa-verifier	
zeus-alpha-research-ledger-core-alr-080-zeus-signed-pr-and-qa-guardian-h	todo	delivery	80	factory-reporter
```

## Exact current-source dispatch predicate

The current-source predicate is in `hermes_cli/factory_pg.py`:

- `_candidate_requires_validation_readiness_before_dispatch()` at `hermes_cli/factory_pg.py:4542` decides whether a candidate must wait behind unresolved validation rows.
- `_is_docs_first_repair_dispatch_task()` at `hermes_cli/factory_pg.py:4666` identifies bounded G1/documentation recovery that may run before validation rows.
- `_is_docs_first_gated_dispatch_task()` at `hermes_cli/factory_pg.py:6763` keeps product/QA/security/delivery/runtime scopes docs-first gated.
- `_current_g1_required_documents_ready()` at `hermes_cli/factory_pg.py:2603` and `_g1_required_status_rows_ready()` at `hermes_cli/factory_pg.py:2642` now keep current G1 document-content readiness separate from stale-primary/runtime identity, so R2cw-style primary/runtime recovery remains separate and product dispatch remains fail-closed.

## Repair

Implementation changes:

1. Added `_has_docs_first_repair_terms()` so G1/documentation recovery bypass is selected only when task text carries explicit documentation/readiness repair terms, not merely because phase starts with `g1`.
2. Added `_has_product_or_runtime_dispatch_scope()` to identify ALR/product/runtime/security-sensitive scopes including external runtime, deployment, messaging, direct SQL, trading, risk, paper/live, and base-branch/direct-integration language.
3. Updated `_candidate_requires_validation_readiness_before_dispatch()` so documentation repair runs before unresolved validation rows, while sensitive product/runtime scopes must still wait.
4. Updated `_is_docs_first_gated_dispatch_task()` so non-docs G1/recovery scopes remain preflight-gated instead of being treated as docs repair.
5. Kept stale-primary/runtime identity separate from current G1 document-content readiness; this preserves R2cw as its own ready recovery and does not conflate it with R2df.

## RED / GREEN evidence

Focused RED before the fix:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k routes_only_g1_docs_recovery_before_direct_runtime_scope -v --tb=short
```

Result before code repair:

```text
FAILED tests/hermes_cli/test_factory_increment_integration.py::test_claim_next_task_routes_only_g1_docs_recovery_before_direct_runtime_scope
AssertionError: expected demo-r2df-current-base-g1-documentation but selected demo-r2cw-premature-live-run-direct-integration
```

Focused GREEN after code repair:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k routes_only_g1_docs_recovery_before_direct_runtime_scope -v --tb=short
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

Whitespace/diff verification:

```text
git diff --check
```

Result: exit `0`.

## Security and delivery boundary

This increment does not execute live `factory project tick`/`resolve-state` mutations from the worker shell because the assigned hard safety allowlist for Factory DB access only permits `factory status` and `factory gate record`. The live event reproduction is therefore read back from canonical Agent Core status, and the tick/dispatch behavior is exercised through the hermetic regression tests above.

Delivery remains PR-first. The PR body must name the final pushed candidate SHA and carry Zeus signature plus `agent:zeus` label. Independent exact-SHA quality review is required before closure. This worker must not merge.

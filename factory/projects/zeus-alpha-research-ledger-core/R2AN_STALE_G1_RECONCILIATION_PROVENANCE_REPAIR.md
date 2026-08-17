---
project_id: zeus-alpha-research-ledger-core
phase: documentation
status: implemented_pending_pr_review
validated: yes
reviewed: no
owner: codex-builder
---

# R2an — stale G1 reconciliation provenance repair

## Scope
Bounded Factory control-plane repair for stale `unvalidated_required_docs` reconciliation provenance. This increment does not change runtime provider/auth, does not mutate the primary checkout, does not deploy, does not alter secrets, and does not contact any external trading/runtime system.

## Source documents read
- `DOCUMENTATION_INDEX.md`
- `G1_DOCUMENT_STATUS_TECHNICAL_RECOVERY.md`
- `R2AM_STALE_PRIMARY_FACTORY_TICK_SOURCE_RESOLUTION_REPAIR.md`
- `R2C6_BOUNDED_CURRENT_ORIGIN_G1_RESOLVER_READBACK_RECOVERY.md`
- `TASK_GRAPH.md`

## Defect reproduced
The RED behavioral test `test_reconciler_resolves_stale_unvalidated_required_docs_from_current_configured_base` builds a stale primary checkout with stale `metadata.g1_documentation_checkout` / reconciliation metadata while the configured base `origin/main` has all required G1 rows non-blocking.

RED command:
`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'stale_unvalidated_required_docs or current_base_unreviewed' -v --tb=short`

Observed RED result before code repair:
- 1 failed, 1 passed.
- Failure: `_resolved_reconciliation_anomaly(...)` returned `None` for stale `unvalidated_required_docs` despite current configured-base G1 rows being non-blocking.

## Repair
`hermes_cli/factory_pg.py::_resolved_reconciliation_anomaly` now handles `unvalidated_required_docs` by consulting the current document-status resolver via `_g1_document_blockers(project)`. The stale task/provenance is resolved only when the live configured-base document-status rows have zero required-G1 blockers. The existing document-status resolver remains fail-closed for missing, dirty/untracked, malformed, unindexed, unvalidated, or unreviewed current documents.

## Verification
GREEN targeted command:
`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'stale_unvalidated_required_docs or current_base_unreviewed' -v --tb=short`

Result: 2 tests passed, 0 failed.

Project-scoped behavioral command:
`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_orchestrator_tick.py -v --tb=short`

Result: 3 files, 274 tests passed, 0 failed.

Factory resolve-state readback:
`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory project resolve-state zeus-alpha-research-ledger-core --json`

Result: exit 0; `unblocked.reopened` included stale `unvalidated_required_docs` blockers and `reconciliation_tasks_created: 0`.

Factory tick readback:
`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory project tick zeus-alpha-research-ledger-core --json`

Result: exit 0; `claimed: null`, `spawned_worker: null`, `needs_attention: false`, and `reconciled[0].anomalies: ["pending_effective_gates"]` with `reconciliation_tasks_created: 0`.

Factory status readback:
`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`

Result: exit 0; full output cached at `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786929179-1632979-c50.log`.
Key readback evidence:
- Latest reconciliation events show `anomalies: ["pending_effective_gates"]`, `reconciliation_tasks_cancelled: []`, `reconciliation_tasks_created: []`.
- Project metadata now records `reconciliation_anomalies: ["pending_effective_gates"]`; `unvalidated_required_docs` is absent.
- `document_status` rows read from `readiness_source: configured_base_ref`, `base_ref: origin/main`, `base_commit: bf422968f9ea73d70d4ac1e8b8bae4af644ce079`, `primary_checkout_accepted: false`, and required G1 rows are non-blocking.

## Delivery boundary
No merge, deploy, credential change, direct SQL, primary-checkout mutation, external runtime call, or trading/paper/live action was performed.

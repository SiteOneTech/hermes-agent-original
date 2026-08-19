---
document_type: docs_first_routing_predicate_repair
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2dk-docs-first-routing-predicate-repair
run_id: run-1787148846-98dcd636
phase: documentation
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending_independent_exact_sha_quality_review
owner: codex-builder
base_ref: origin/main
base_sha: cc43e6dace789da06d103ba512a3f4863fb0edc9
branch: factory/zeus-alpha-research-ledger-core/inc-008-r2dk-docs-first-routing-predicat
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-008-r2dk-docs-first-routing-predicat
created_at: 2026-08-19T14:23:02Z
---

# R2dk — docs-first routing predicate repair

## Scope and boundary

R2dk is a bounded Factory control-plane repair for project
`zeus-alpha-research-ledger-core`. It addresses the routing predicate proven by
Agent Core events `202769` and `202770`: the documentation recovery task R2df was
denied with `unresolved_validation_tasks` while the product task R2cw was
separately denied by docs-first G1 preflight. The repair prevents incidental
handoff/delivery prose inside documentation or reconciliation recovery tasks
from activating final-delivery validation gating.

Changed runtime scope is limited to Factory dispatch predicate logic in
`hermes_cli/factory_pg.py` and deterministic regression coverage in:

- `tests/hermes_cli/test_factory_increment_integration.py`
- `tests/hermes_cli/test_factory_control_plane_refactor.py`

Project-local evidence is recorded in this file plus `DOCUMENTATION_INDEX.md`,
`QA_GATES.md`, `SECURITY_GATES.md`, and `TRACKER.md`.

This increment does not modify Alpha Ledger product/runtime behavior, provider
or model configuration, migrations, tools, schedulers, deployment, credentials,
messaging/connectors, primary checkout state, direct SQL/task status, stale
refs/PRs, Vonash, Magnus, VAOS, RAG/KB, brokers, trading, risk, paper/live, or
any external runtime.

## Canonical documents read before implementation

The required entrypoint and applicable G1/control docs read for this phase were:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/REQUIREMENTS_ANALYSIS.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DG_BOUNDED_G1_EXACT_SHA_INDEPENDENT_REVIEW_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DH_DOCS_FIRST_CURRENT_BASE_G1_REVIEW_STATE_DISPATCH_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DI_DOCS_FIRST_FAIL_CLOSED_REVIEW_TERMINALIZATION_AND_DISPATCH_REPAIR.md`

The active Factory DB/status source remains Agent Core Postgres `factory.*`;
project-local Markdown is evidence and human-readable control documentation,
not a replacement for canonical DB state.

## Current base, worktree and live readback

Captured before implementation:

- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-008-r2dk-docs-first-routing-predicat`
- Branch: `factory/zeus-alpha-research-ledger-core/inc-008-r2dk-docs-first-routing-predicat`
- Remote: `https://github.com/SiteOneTech/hermes-agent-original.git`
- `git rev-parse HEAD`: `cc43e6dace789da06d103ba512a3f4863fb0edc9`
- `git rev-parse origin/main`: `cc43e6dace789da06d103ba512a3f4863fb0edc9`
- `git merge-base HEAD origin/main`: `cc43e6dace789da06d103ba512a3f4863fb0edc9`

Allowed Factory status command from the assigned worktree:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2dk-status-before.json`

Summarized readback from `/tmp/r2dk-status-before.json`:

- `db_backend=agent_core_postgres`
- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-008-r2dk-docs-first-routing-predicat`
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-008-r2dk-docs-first-routing-predicat`
- `factory_status_delegated=false`
- Project status: `active`, `autonomous_enabled=true`
- Active metadata: `reconciliation_anomalies=[]`, `reconciliation_projection_source=current_document_status`
- G1 required rows: `14`; G1 blocker list: `[]`
- R2dk task status: `running`, phase `documentation`, owner `codex-builder`
- R2df task status: `todo`, phase `documentation`, owner `codex-builder`, priority `19`
- R2cw task status: `ready`, phase `implementation`, owner `claude-builder`, priority `19`
- ALR-061/062/063/070 validation tasks remain `todo`

Event readback from the same status payload:

- Event `202769`: `dispatch_preflight_denied` for R2df with
  `unresolved_validation_tasks`, including stale/superseded R2h/R2l/R2g/ALR-060,
  blocked R2ai, and todo ALR-061/062/063/070 validation tasks.
- Event `202770`: `dispatch_preflight_denied` for product R2cw with
  `missing_or_unindexed_docs`.

Post-implementation status was refreshed with the same sanctioned CLI surface:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2dk-status-after.json`

Exact summary command result from `/tmp/r2dk-status-after.json`:

```text
status_json=/tmp/r2dk-status-after.json
db_backend=agent_core_postgres
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-008-r2dk-docs-first-routing-predicat
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-008-r2dk-docs-first-routing-predicat
factory_status_delegated=false
project status=active autonomous=true reconciliation_anomalies=[] projection=current_document_status
g1_required=14
g1_blockers=[]
task zeus-alpha-research-ledger-core-r2dk-docs-first-routing-predicate-repair status=running phase=documentation owner=codex-builder priority=8
task zeus-alpha-research-ledger-core-r2cw-fail-closed-recovery-for-premature- status=ready phase=implementation owner=claude-builder priority=19
task zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation status=todo phase=documentation owner=codex-builder priority=19
event 202770 type=dispatch_preflight_denied task=zeus-alpha-research-ledger-core-r2cw-fail-closed-recovery-for-premature- blockers=["missing_or_unindexed_docs"]
event 202769 type=dispatch_preflight_denied task=zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation blockers=["unresolved_validation_tasks", ...]
```

## Root cause

`_candidate_requires_validation_readiness_before_dispatch()` treated broad
text-only markers such as `final` or `delivery report` in task prose as final
delivery validation markers even when the candidate was a documentation or
reconciliation recovery task. R2df-style tasks must be able to run while G1 is
red because they are the repair path; blocking them on downstream validation
creates a dispatch deadlock. Genuine final delivery/reporting work must still
fail closed until validation tasks are complete.

## Repair

`hermes_cli/factory_pg.py` now:

1. explicitly exempts reconciliation and runtime-bootstrap repair tasks from
   delivery-validation gating;
2. keeps phase-based gating for real delivery/release/final tasks;
3. limits prose-only `delivery report` / `final report` / `gate closure` gating
   to reporter-owned final reporting work in `documentation` or `reporting`
   phases, so incidental delivery handoff evidence in docs-first recovery tasks
   cannot block the recovery path.

The docs-first product preflight remains unchanged: product implementation work
such as R2cw still receives `missing_or_unindexed_docs` while G1 is red.

## TDD evidence

RED command before implementation:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_control_plane_refactor.py -k 'docs_recovery_with_incidental_delivery_text or genuine_delivery_report_when_validation_unresolved or reconciliation_recovery_delivery_prose' -v --tb=short`

RED result:

- `tests/hermes_cli/test_factory_increment_integration.py::test_claim_next_task_claims_docs_recovery_with_incidental_delivery_text_before_product` failed: `assert None is not None`.
- `tests/hermes_cli/test_factory_control_plane_refactor.py::test_dispatch_validation_readiness_exempts_reconciliation_recovery_delivery_prose` failed: `_candidate_requires_validation_readiness_before_dispatch(reconciliation)` returned `True`.
- `tests/hermes_cli/test_factory_increment_integration.py::test_claim_next_task_blocks_genuine_delivery_report_when_validation_unresolved` passed, proving the genuine-delivery fail-closed baseline already existed.

GREEN targeted command after implementation:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_control_plane_refactor.py -k 'docs_recovery_with_incidental_delivery_text or genuine_delivery_report_when_validation_unresolved or reconciliation_recovery_delivery_prose' -v --tb=short`

GREEN targeted result: `2 files, 3 tests passed, 0 failed`.

Broader validation command:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_control_plane_refactor.py -v`

Broader validation result: `2 files, 282 tests passed, 0 failed`.

## Acceptance mapping

- Documentation task with incidental delivery-like prose remains eligible while
  G1 is red and validation tasks are unresolved: covered by
  `test_claim_next_task_claims_docs_recovery_with_incidental_delivery_text_before_product`.
- Reconciliation recovery with incidental `final delivery report` prose remains
  exempt from delivery-validation gating: covered by
  `test_dispatch_validation_readiness_exempts_reconciliation_recovery_delivery_prose`.
- Genuine final delivery work remains fail-closed when validation tasks are
  unresolved: covered by
  `test_claim_next_task_blocks_genuine_delivery_report_when_validation_unresolved` and the pre-existing deploy/final-report predicate test.
- Docs-first product gating remains fail-closed for product work while G1 is red:
  R2cw event `202770` remains the live source-backed product denial evidence;
  this repair does not alter `_dispatch_preflight_blockers()`.

## Delivery state

This candidate is implemented and validated locally but remains
`reviewed: pending` until delivered as a Zeus-signed, non-draft, `agent:zeus`
GitHub PR against `main` and independently reviewed against the exact final PR
head SHA. The worker must not self-approve or merge this PR.

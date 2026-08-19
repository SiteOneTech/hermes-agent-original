---
project_id: zeus-alpha-research-ledger-core
phase: documentation
status: implemented_pending_pr_review
validated: yes
reviewed: pending
owner: codex-builder
task_id: zeus-alpha-research-ledger-core-r2dg-docs-first-dispatch-ordering-recove
branch: factory/zeus-alpha-research-ledger-core/inc-019-r2dg-docs-first-dispatch-orderin
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2dg-docs-first-dispatch-orderin
base_commit: abc164184d588a7a9e5e4838f5a101d9f4e3a0f2
---

# R2dg — docs-first dispatch ordering recovery

## Scope

Bounded Factory control-plane repair for project
`zeus-alpha-research-ledger-core`. The increment fixes only dispatch/preflight
ordering so G1/documentation recovery work can run before product work when
G1/docs or validation projections are red. It does not authorize ALR product
implementation, deployment, credentials, direct SQL, primary-checkout mutation,
external runtime access, messaging, or trading/risk/paper/live activity.

## Canonical readback used

Sanctioned Factory status command, run from the assigned worktree and saved as
`/tmp/r2dg-docs-first-status-before.json`:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`

Evidence from `/tmp/r2dg-docs-first-status-before.pretty.json`:

- Lines 470–493: event `202098`, `dispatch_preflight_denied`, task
  `zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation`,
  blockers start with `unresolved_validation_tasks` and list unresolved or
  historical validation rows.
- Lines 38893–38935: R2df is a same-project documentation task, status `todo`,
  dependencies `[]`, branch
  `factory/zeus-alpha-research-ledger-core/inc-019-r2df-fresh-current-base-g1-docum`.
- Lines 38938–38978: this R2dg run is the claimed/running recovery task on the
  assigned branch/worktree.

The reproduced defect is that R2df's documentation description contains normal
historical wording such as `finalized`, which the validation-readiness gate
classified as final delivery text. The dispatcher then skipped the eligible
G1/documentation recovery, selected a product candidate, denied it with docs-first
preflight, and returned no claim.

## Code repair

`hermes_cli/factory_pg.py` now exempts the same non-product recovery classes from
validation-readiness dispatch gating that docs-first preflight already exempts:

- validation tasks themselves;
- Factory reconciliation tasks;
- explicitly Jean-authorized runtime/bootstrap repair tasks;
- G0/G1, `documentation`, and `planning` phase tasks.

Final delivery/reporting tasks still fail closed on unresolved validation tasks.
Product/QA/security/delivery tasks still fail closed when docs-first preflight
reports missing/unindexed/unvalidated/unreviewed documentation, including stale,
dirty, ahead, or diverged source states covered by existing resolver tests.

## TDD evidence

RED, before the repair:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k test_claim_next_task_claims_documentation_recovery_before_validation_denied_product -v --tb=short`

Result: expected failure, `assert None is not None`; 1 selected test failed. This
reproduced the observed active/autonomous state where a documentation recovery
candidate exists but no claim is made because the validation gate skips it.

GREEN, after the repair:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k test_claim_next_task_claims_documentation_recovery_before_validation_denied_product -v --tb=short`

Result: 1 selected test passed.

Regression file:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -v --tb=short`

Result: 124 tests passed, 0 failed.

Infra note: running `scripts/run_tests.sh` without `HERMES_PYTHON` first failed
because this isolated worktree has no local venv with pytest. No packages were
installed; the canonical shared Hermes venv was used as allowed for verification.

## Boundary and handoff

This increment changes only:

- `hermes_cli/factory_pg.py`;
- `tests/hermes_cli/test_factory_increment_integration.py`;
- project-local evidence docs under
  `factory/projects/zeus-alpha-research-ledger-core/`.

No merge, deploy, force push, primary checkout mutation, direct SQL,
credential/secret operation, external runtime/provider operation, messaging,
Vonash/Magnus/VAOS/RAG/KB/broker/trading/risk/paper/live activity, or ALR product
implementation was performed.

Delivery remains PR-first: push this assigned branch, open a Zeus-signed
`agent:zeus` PR against `main`, and require independent exact-SHA quality review
before Factory treats this recovery as reviewed.

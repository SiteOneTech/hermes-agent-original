---
document_type: repair_docs_first_validation_deadlock
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2da-r2-repair-docs-first-validation-dea
run_id: run-1787281541-de52b795
phase: g1_recovery
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending_independent_review
owner: codex-builder
engine: codex
base_ref: origin/main
base_sha: 5fe25cd7cb78d47afa156f8fde0c6a2c65f00a96
branch: factory/zeus-alpha-research-ledger-core/inc-001-r2da-r2-repair-docs-first-valida
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2da-r2-repair-docs-first-valida
created_at_utc: 2026-08-21T03:20:02Z
---

# R2da-R2 — repair docs-first validation deadlock against PR-first G1 provenance

## Scope and boundary

This increment is a bounded same-project Factory control-plane repair. It fixes
only the docs-first dispatch/validation predicates that made PR-first G1
provenance review work impossible to dispatch while stale or superseded
historical validation rows still appeared in the dispatch preflight projection.
It also records the current Agent Core `factory.*` readback and the exact test
evidence needed for an independent exact-SHA review.

This run does not implement Alpha Ledger product behavior, does not deploy,
does not merge, does not change credentials, does not mutate the primary
checkout, does not write direct SQL, does not run `factory task close`, does
not run mutating Factory project tick/resolve-state commands, and does not
contact or modify external runtimes/connectors, messaging, Vonash/Magnus/VAOS,
RAG/KB, brokers, trading, risk, paper/live systems, or ALR-020 product dispatch.
The only sanctioned Factory DB command used for readback was `factory status`;
`factory gate record` is reserved for final evidence after the PR is pushed.

## Canonical documents read

The worker read the mandatory entrypoint and phase-relevant G1/control-plane
docs before editing:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2EA_DOCS_FIRST_STALE_RUNTIME_DISPATCH_PROVENANCE_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R5_FAIL_CLOSED_REVIEW_TERMINALIZATION_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DL_G1_DOCUMENTATION_DISPATCH_VALIDATOR_RECOVERY.md`

Agent Core Postgres `factory.*` remains the source of truth. This Markdown file
records evidence and rationale only; it is not a substitute for Factory state.

## Current-origin identity captured before edits

Read-only Git evidence after `git fetch origin main --prune`, before this
artifact was created:

```text
worktree    = /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2da-r2-repair-docs-first-valida
branch      = factory/zeus-alpha-research-ledger-core/inc-001-r2da-r2-repair-docs-first-valida
remote      = https://github.com/SiteOneTech/hermes-agent-original.git
HEAD        = 5fe25cd7cb78d47afa156f8fde0c6a2c65f00a96
origin/main = 5fe25cd7cb78d47afa156f8fde0c6a2c65f00a96
merge-base  = 5fe25cd7cb78d47afa156f8fde0c6a2c65f00a96
```

The primary checkout remains outside this worktree and was not mutated.

## Reproduced denial and exact unresolved conditions

Canonical `factory status` was captured from the assigned worktree:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2da-r2-status-before.json
```

Readback and event evidence:

- Source roots: `factory_cli_source_root` and `factory_status_source_root` both
  equal the assigned worktree; `factory_status_delegated=false`.
- Agent Core backend: `db_backend=agent_core_postgres`, `db_path=agent_core_postgres:zeus_agent.factory`.
- Current G1 document rows from `/tmp/r2da-r2-status-after-code.json`: 14/14
  `category=g1_required`, all `exists=true`, `committed=true`, `indexed=true`,
  `validated=true`, `reviewed=true`, `blocking=false`, from
  `readiness_source=configured_base_ref`, `base_commit=5fe25cd7cb78d47afa156f8fde0c6a2c65f00a96`.
- Current ready work includes the existing exact-SHA review task
  `zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re`,
  `status=ready`, `phase=quality_review`, `owner_profile=quality-reviewer`,
  `priority=17`.
- Stale dispatcher evidence in current Factory events:
  - Event `208914` denied R2cy-R1 with `blockers=["missing_or_unindexed_docs"]`.
  - Event `208913` denied R2df with `unresolved_validation_tasks` and explicitly
    treated terminal/superseded historical rows as incomplete, e.g.
    R2h/R2ai/R2l/R2g/ALR-060 with `status=superseded`, plus current R2cy-R1
    still `ready` and future ALR-061/062/063/070 still `todo`.
  - Latest `project_reconciled` events continued to report
    `unvalidated_required_docs` alongside `pending_effective_gates` even though
    the current configured-base G1 document rows are non-blocking.

Root cause at code level:

1. `_validation_task_readiness_findings()` treated `status=superseded` validation
   rows as not complete. Those rows are terminal historical paths by the closed
   Factory task-status contract and must not be required after they are
   superseded. Cancelled rows remain fail-closed unless they point to a completed
   replacement validation task.
2. `_is_docs_first_gated_dispatch_task()` gated the current PR-first G1
   provenance review task R2cy-R1 as if it were product execution because it is
   `phase=quality_review` and mentions G1/docs-first control-plane behavior.
   That review is the evidence-producing repair path; blocking it on the stale
   docs-first projection creates a self-deadlock. Ordinary product
   implementation/quality/security/QA work remains docs-first gated.

Because this run's DB-write allowlist permits only `factory status` and
`factory gate record`, live mutating `factory project tick`/`resolve-state`
commands were not executed. The dispatch/tick behavior is covered by the focused
RED/GREEN unit tests below.

## Implementation repair

Code changed only in Factory control-plane predicates:

- `hermes_cli/factory_pg.py`
  - Added `_is_docs_first_validation_repair_task()` to identify bounded review
    tasks that repair or independently verify docs-first G1 provenance. These
    review tasks are docs-first repair work, not product execution; they can be
    dispatched while stale docs-first projections are being repaired.
  - `_is_docs_first_gated_dispatch_task()` now exempts those docs-first
    validation-repair tasks while preserving the existing gate for normal
    implementation/review/QA/security/product dispatch.
  - `_is_docs_first_repair_dispatch_task()` now recognizes those review repairs
    so they can preempt docs-blocked product work.
  - `_validation_task_readiness_findings()` now ignores `superseded` validation
    tasks as terminal historical rows. `cancelled` validation rows still require
    a completed replacement validation task or remain blocking.

Tests added in `tests/hermes_cli/test_factory_increment_integration.py`:

- `test_claim_next_task_allows_docs_first_pr_review_repair_when_docs_red`
  reproduces the R2cy-R1 class: docs-first preflight red, product work also
  ready, and a PR-first G1/control-plane quality-review repair ready. Before the
  fix, `claim_next_task()` returned `None` and emitted dispatch denial; after
  the fix it claims the review repair and leaves product work unclaimed.
- `test_validation_readiness_ignores_superseded_historical_validation_task`
  reproduces the R2h-class false unresolved condition. Before the fix, a
  superseded historical quality-review task produced
  `status=superseded` unresolved findings; after the fix, it contributes no
  blocker.

## RED/GREEN and validation evidence

Focused RED, before implementation:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'docs_first_pr_review_repair_when_docs_red or superseded_historical_validation_task' -v --tb=short
```

Result: 2 selected tests failed as expected.

- `test_claim_next_task_allows_docs_first_pr_review_repair_when_docs_red`: `assert None is not None`.
- `test_validation_readiness_ignores_superseded_historical_validation_task`: unresolved finding was `validation task ... is not complete; status=superseded`.

Focused GREEN, after implementation:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'docs_first_pr_review_repair_when_docs_red or superseded_historical_validation_task' -v --tb=short
```

Result: 1 file, 2 tests passed, 0 failed.

Related Factory regression GREEN:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_control_plane_refactor.py -v --tb=short
```

Result: 2 files, 286 tests passed, 0 failed.

Canonical Factory readback after code change:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2da-r2-status-after-code.json
```

Result summary from `/tmp/r2da-r2-status-after-code.json`:

```text
db_backend                 = agent_core_postgres
project_status             = active
factory_status_source_root = /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2da-r2-repair-docs-first-valida
factory_status_delegated   = false
g1_required_count          = 14
g1_blocking                = []
g1_reviewed_false          = []
g1_readiness_sources       = ["configured_base_ref"]
g1_base_commits            = ["5fe25cd7cb78d47afa156f8fde0c6a2c65f00a96"]
ready_review_task          = zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re
remaining_runtime_anomaly  = pending_effective_gates before final gate evidence
```

## PR-first evidence and no-external-execution statement

This repair must be delivered by a Zeus-signed non-draft GitHub PR from the
assigned branch, labelled `agent:zeus`, with exact base/head SHA, tests, Factory
readback, and this no-external-execution statement in the PR body. No merge,
deploy, direct SQL, primary-checkout mutation, credential change, external
runtime execution, or ALR product dispatch is authorized by this increment.

After the PR is pushed and independently reviewable, a sanctioned Factory
`implementation` gate record may supersede the older pending implementation gate
projection and leave the next tick free to claim the existing R2cy-R1 quality
review path. If Factory still blocks after that, the remaining condition must be
recorded as a new exact technical blocker rather than opening another broad
increment.

---
project_id: zeus-alpha-research-ledger-core
phase: g1_recovery
status: implemented
validated: yes
reviewed: pending
owner: codex-builder
reviewer: quality-reviewer
---

# R2f6 — G1/docs recovery candidate preflight repair evidence

## Scope

Bounded Factory control-plane repair only. This increment fixes the scheduler validation-readiness classifier that treated explicit same-project `g1_recovery` / documentation-reconciliation candidates as product/final-delivery work when their prose contained terminal words such as `finalize` / `finalized` / `final`.

No product Alpha Ledger implementation, ALR schema/tool work, QA/security delivery work, deploy, messaging, external runtime, broker/trading/risk, paper/live activation, credential change, primary-checkout mutation, direct SQL, or merge was performed by this worker.

## G1 docs consulted

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`

## Source and branch evidence

- Assigned worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-104-r2f6-repair-g1-docs-recovery-can`
- Assigned branch: `factory/zeus-alpha-research-ledger-core/inc-104-r2f6-repair-g1-docs-recovery-can`
- Base SHA before code change: `ac1fdb16051324c490d803b14dd06efffd6f9ad0`
- Code/test candidate SHA: `51ed439126919e73e8ee40174327cff5e00f133f`
- Final evidence commit SHA: recorded by `git rev-parse HEAD` after this evidence file is committed and in the Factory gate notes/final worker response.

## RED evidence

Command:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'validation_readiness_exempts' -v --tb=short
```

Result: expected RED, exit 1. Both new tests failed because `_candidate_requires_validation_readiness_before_dispatch(...)` returned `True` for explicit recovery/control-plane candidates:

- `test_validation_readiness_exempts_explicit_g1_recovery_from_terminal_word_prose` failed: phase `g1_recovery` candidate with terminal-word prose was classified as requiring validation readiness.
- `test_validation_readiness_exempts_structured_documentation_reconciliation_from_terminal_word_prose` failed: phase `documentation` + structured `factory_reconciliation_task=True` / `reconciliation_anomaly=unvalidated_required_docs` was classified as requiring validation readiness.

Command:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'claims_g1_recovery_despite_unresolved_validation_history' -v --tb=short
```

Result: expected RED, exit 1. The new claim-path regression returned `None` instead of claiming the explicit same-project `g1_recovery` candidate while legacy validation rows were unresolved.

## GREEN repair

Implementation file: `hermes_cli/factory_pg.py`.

Repair summary:

- Added `_has_explicit_g1_or_documentation_recovery_scope(candidate)`.
- The new predicate ignores title/description prose and accepts only structured phase or metadata:
  - phases: `g1_recovery`, `g1_documentation_recovery`, `g1_docs_recovery`, `documentation_reconciliation`, `docs_reconciliation`;
  - metadata recovery scope values with the same meanings;
  - documentation/docs phase only when `factory_reconciliation_task is True` and `reconciliation_anomaly` is one of the G1 documentation anomalies (`missing_project_artifact_dir`, `missing_required_docs`, `docs_not_indexed`, `unvalidated_required_docs`, `uncommitted_project_artifacts`).
- `_candidate_requires_validation_readiness_before_dispatch(...)` now returns `False` for that explicit structured recovery scope before broad terminal-word prose checks run.
- Existing fail-closed delivery validation stays intact: `test_dispatch_validation_readiness_does_not_deadlock_deploy_prerequisite` still asserts actual final delivery/reporting work requires validation readiness, while deploy prerequisite work is not deadlocked.

## GREEN verification

Focused repaired tests:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'validation_readiness_exempts or dispatch_validation_readiness' -v --tb=short
```

Result: exit 0, `3 tests passed, 0 failed`.

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'claim_next_task_claims_g1_recovery_despite_unresolved_validation_history or claims_docs_repair_before_preflight_denied_product or keeps_priority_order_when_docs_ready' -v --tb=short
```

Result: exit 0, `3 tests passed, 0 failed`.

Full focused files:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py
```

Result: exit 0, `110 tests passed, 0 failed`.

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py
```

Result: exit 0, `28 tests passed, 0 failed`.

Additional static check:

```bash
git diff --check
```

Result: exit 0.

## Canonical Factory status/readback evidence

Command used, per hard task constraint:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2f6-factory-status.json
```

Readback facts from Agent Core Postgres status output:

- `db_backend=agent_core_postgres`, `database=zeus_agent`.
- Current R2f6 task row: task `zeus-alpha-research-ledger-core-r2f6-repair-g1-docs-recovery-candidate-m`, `phase=g1_recovery`, `status=running`, owner `codex-builder`, reviewer `quality-reviewer`, worktree `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-104-r2f6-repair-g1-docs-recovery-can`.
- Event `269683`: dispatcher denied `zeus-alpha-research-ledger-core-r2df-r17-docs-first-validation-scheduler` with blocker `unresolved_validation_tasks`.
- Event `269684`: dispatcher denied `zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation` with blocker `unresolved_validation_tasks`.
- Event `269685`: dispatcher denied `zeus-alpha-research-ledger-core-r2f4-repair-terminal-run-reconciliation-` with blocker `unresolved_validation_tasks`.
- Event `269686`: forced tick denied normal quality-review candidate `zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re` with blocker `missing_or_unindexed_docs`, preserving fail-closed product/quality dispatch while G1 is red.
- Event `269691`: forced tick claimed this R2f6 `g1_recovery` task for `codex-builder` with run `run-1788532891-0eef52fd`.
- Reconciler events `269689` and `269690` before R2f6 claim show `active_runs=0`, anomaly `unvalidated_required_docs`, and project reconciled as `active`; event `269692` after claim shows `active_runs=1`.
- Document status readback still shows red G1: 10 blocking required docs due `reviewed=false` (`FACTORY_INTAKE.md`, `REQUIREMENTS_ANALYSIS.md`, `PATTERN_ANALYSIS.md`, `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, `PRD.md`, `ADRS.md`, `METHODOLOGY_PLAN.md`, `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`, `SECURITY_GATES.md`). This repair does not waive those blockers; it only permits the bounded control-plane G1/docs recovery route.

## Boundary confirmation

- No direct SQL was run.
- No Factory DB command outside sanctioned `factory status` and later `factory gate record` was used.
- No deployment, external runtime, messaging, credential/secret, broker, trading/risk, or paper/live action was performed.
- No primary checkout mutation was performed; all edits are in the assigned worktree/branch.
- No merge was performed.

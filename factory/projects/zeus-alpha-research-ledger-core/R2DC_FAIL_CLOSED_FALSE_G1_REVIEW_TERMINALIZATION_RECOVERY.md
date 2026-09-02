---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2dc-fail-closed-recovery-for-false-g1-r
run_id: run-1788358319-c4f57f3c
phase: g1_recovery
status: implemented_validated_pending_zeus_pr_and_independent_exact_sha_review
validated: yes
reviewed: pending_independent_exact_sha_review
owner: codex-builder
base_commit: a7e3a54f7ee54e27b4fbdc7ffa2e6808ece0f872
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2dc-fail-closed-recovery-for-fa
branch: factory/zeus-alpha-research-ledger-core/inc-001-r2dc-fail-closed-recovery-for-fa
created_at: 2026-09-02T10:27:27-04:00
updated_at: 2026-09-02T10:27:27-04:00
---

# R2dc — fail-closed recovery for false G1 review terminalization

## Scope and boundary

R2dc repairs only the same-project Factory control-plane behavior for reviewer runtime failures and stale review terminalization. The increment is limited to:

- `hermes_cli/factory_pg.py` review-success/runtime-failure classification and bounded reconciliation recovery.
- `tests/hermes_cli/test_factory_increment_integration.py` focused behavior/regression tests.
- Project-local evidence in this artifact and the documentation index.

This increment performs no ledger product/runtime change, no direct SQL, no primary-checkout mutation, no merge to `main`, no deployment, no credential change, no external runtime, no messaging action, and no trading/risk/paper/live action.

## G1 documents and project sources consulted

Required entrypoint plus applicable G1/control-plane documents were read from the assigned worktree before closing this implementation:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/REQUIREMENTS_ANALYSIS.md`
- `factory/projects/zeus-alpha-research-ledger-core/PATTERN_ANALYSIS.md`
- `factory/projects/zeus-alpha-research-ledger-core/ASSUMPTIONS_AND_OPEN_QUESTIONS.md`
- `factory/projects/zeus-alpha-research-ledger-core/PRD.md`
- `factory/projects/zeus-alpha-research-ledger-core/ADRS.md`
- `factory/projects/zeus-alpha-research-ledger-core/METHODOLOGY_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DC_BOUNDED_G1_REVIEWED_STATE_RECOVERY.md`

## Agent Core evidence used

Sanctioned Factory CLI status readback was captured after the repair from the assigned worktree:

- Command: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2dc-failclosed-status-after-code.json`
- Result: `db_backend=agent_core_postgres`; artifact size `4929228` bytes.
- Current task readback: `zeus-alpha-research-ledger-core-r2dc-fail-closed-recovery-for-false-g1-r` is `status=running`, `phase=g1_recovery`, branch `factory/zeus-alpha-research-ledger-core/inc-001-r2dc-fail-closed-recovery-for-fa`.
- Source false-terminalized task readback: `zeus-alpha-research-ledger-core-r2db-repair-explicit-g1-recovery-dispatc` is still `status=done`, `phase=g1_recovery`, branch `factory/zeus-alpha-research-ledger-core/inc-116-r2db-repair-explicit-g1-recovery`.
- Source review run readback: `run-1788357122-0e455a29` is `status=succeeded`, `exit_code=0`, `reviewer_profile=quality-reviewer`, `run_type=review`, and its output tail contains provider-unreachable evidence: `Hermes can't reach the model provider` and `Messages:       1 (1 user, 0 tool calls)`.
- Branch/source evidence: isolated read-only git check of the R2db worktree found source SHA `4e20592877abca2f0a1e0c4a1e42247d494fb6bc`; `git merge-base --is-ancestor 4e20592877abca2f0a1e0c4a1e42247d494fb6bc origin/main` returned `ancestor=no`.

Per the task's DB-write restriction, this implementation did not run live `resolve-state` or direct SQL against `factory.*`; recovery behavior is exercised hermetically in tests and will be applied by the sanctioned Factory reconciler/control path.

## RED → GREEN behavior evidence

Focused RED behavior tests were added before the production repair and initially failed with exit `1` under the Factory test runner:

- `scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k unintegrated_api_connection_false_terminal_review -v --tb=short` → exit `1` before production repair.
- `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'unintegrated_api_connection_false_terminal_review or provider_unreachable_requeues' -v --tb=short` → exit `1` before production repair.

After the repair, the same focused behavior is green:

- `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'unintegrated_api_connection_false_terminal_review or provider_unreachable_requeues' -v --tb=short`
  - Result: `2 tests passed, 0 failed`, `r2dc_focused_tests=passed`.
- `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'force_tick_uses_explicit_g1_recovery_metadata_before_review_when_docs_red or recovered_g1_docs_task_dispatches_while_product_remains_docs_first_blocked' -v --tb=short`
  - Result: `2 tests passed, 0 failed`, `g1_recovery_routing_tests=passed`.
- `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -v --tb=short`
  - Result: `147 tests passed, 0 failed`, `increment_integration_file=passed`.
- `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -v --tb=short`
  - Result: `161 tests passed, 0 failed`, `control_plane_refactor_file=passed`.
- `git diff --check`
  - Result: exit `0`.

## Repair implemented

The fail-closed contract now requires task-bound independent evidence from real reviewer output before a G1 review can terminalize source work:

1. `mark_run_finished` treats provider-unreachable review output as runtime failure even when it also contains `STATE: DONE` and even when a historical task-bound gate row exists. A failed review run is marked failed, the task is reset to `review_ready`, and increment integration is not invoked.
2. Runtime failure detection now covers `APIConnectionError`, `API failed after 3 retries`, `provider unreachable`, `can't reach the model provider`, and flexible `Messages: 1 (1 user, 0 tool calls)` summary formatting. Prompt-only echoed semantic markers remain non-substantive.
3. Reconciliation can recover an already persisted false terminal state not only when `increment_base_commit_after` equals the current configured base, but also for PR-first/auto-integration-forbidden tasks whose branch/worktree source SHA is clean, exact, and not an ancestor of the current configured base. Recovery metadata records the false terminalization reason, run id, previous status, recovery scope, current base SHA, optional source SHA, and `requires_task_bound_passed_review_gate=true`.
4. Existing G1 recovery routing remains ahead of validation/product/QA/security/delivery work while documentation is red; focused routing tests prove explicit `g1_recovery` and documentation-recovery tasks remain selectable before product work.

## Handoff requirement

Final delivery must be a Zeus-signed GitHub PR against `main`, labeled `agent:zeus`, from branch `factory/zeus-alpha-research-ledger-core/inc-001-r2dc-fail-closed-recovery-for-fa`. The PR body and Factory gate evidence must cite the final exact pushed head SHA. This codex-builder worker does not self-approve, merge, deploy, change credentials, mutate the primary checkout, write direct SQL, or record an independent approval for its own work.

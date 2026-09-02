# R2d7 — G1 preflight terminal-word recovery routing

## Scope

This is project-local evidence for `zeus-alpha-research-ledger-core` and records only the bounded Factory scheduler/control-plane repair requested for R2d7. It does not change Alpha Ledger product behavior, runtime dispatch, credentials, deploy targets, messaging, external runtimes, trading/risk behavior, paper/live activation, direct SQL, merge policy, or the primary checkout.

Assigned branch/worktree:

- Branch: `factory/zeus-alpha-research-ledger-core/inc-103-r2d7-g1-preflight-terminal-word`
- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-103-r2d7-g1-preflight-terminal-word`
- Starting base/HEAD/readback before edits: `origin/main` = `83d6b11c6057c40ec5709fd19685f208403885ce`; `HEAD` = same; merge-base = same; worktree initially clean.

## Documents consulted

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/REQUIREMENTS_ANALYSIS.md`
- `factory/projects/zeus-alpha-research-ledger-core/METHODOLOGY_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DL_G1_DOCUMENTATION_DISPATCH_VALIDATOR_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2D1_CURRENT_BASE_EXPLICIT_G1_VALIDATION_GATE_DISPATCH_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2D6_REPAIR_RECURRENT_G1_RECOVERY_SELF_DENIAL.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R47_ISOLATED_R44_SCHEDULER_FIX_PR_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R48_CURRENT_ORIGIN_R47_CLEAN_WORKTREE_PR_PROVENANCE_RECOVERY.md`

## Root cause

R2d1/R2d6 already made explicit G1/documentation recovery bypass validation-readiness history, while keeping product/runtime/final-stage work fail-closed. The remaining terminal-word class was narrower: a control-plane recovery row can quote historical source-increment terminal evidence such as `source increment not integrated`, `terminal source`, and `origin/main integration` while explicitly saying it is only routing G1 recovery and not product/runtime work. The positive product/runtime classifier treated the quoted source-integration phrase as real runtime/base-integration scope before the G1 recovery route could be accepted, so the dispatcher skipped the repair and moved on to unresolved validation history.

That creates the same self-denial loop: the work required to repair red G1 routing is denied because red-G1 validation rows are unresolved. Product, ALR, QA, security, delivery, runtime, deployment, direct-SQL, messaging, trading/risk, paper/live, and external work must continue to fail closed while G1 is red.

## Repair

Implementation in `hermes_cli/factory_pg.py` adds a narrow historical terminal-source exception to the positive product/runtime classifier:

- recognize terminal-source recovery wording (`source increment not integrated`, `terminal source`, `terminal-word`, `terminalized`, `terminalization`);
- only treat it as non-product scope when the remaining positive product/runtime matches are limited to historical source-integration terms, there are repair/recovery terms, and metadata does not carry product/runtime scope;
- keep raw product/runtime preflight and metadata scope detection unchanged, so ALR/product/runtime/QA/security/delivery/external work still gets `missing_or_unindexed_docs` while G1 is red.

## RED/GREEN evidence

Focused RED test added in `tests/hermes_cli/test_factory_control_plane_refactor.py`:

- `test_explicit_g1_recovery_phase_bypasses_validation_deadlock_with_historical_terminal_source_wording`

The test builds a red-G1 project snapshot with an explicit `phase=g1_recovery` task whose description quotes historical terminal-source/origin-main-integration wording and includes a same-project unresolved `security_review` validation row. Before the repair, the task was not selected; the runner selected the unresolved validation row instead, proving the G1 recovery route was denied by the validation history path.

Commands executed from the assigned worktree:

- RED command before implementation:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 HERMES_TEST_WORKERS=1 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k historical_terminal_source_wording -v --tb=long`
  Result: exit 1; focused test failed as expected, selecting `demo-alr-063-security-review` instead of `demo-r2d7-g1-terminal-word-recovery`.

- Focused GREEN:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 HERMES_TEST_WORKERS=1 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k historical_terminal_source_wording -v --tb=long`
  Result: 1 test passed, 0 failed.

- Focused GREEN plus fail-closed regressions:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 HERMES_TEST_WORKERS=1 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_increment_integration.py -k 'historical_terminal_source_wording or docs_red_preflight_keeps_product_alr_qa_security_runtime_reporting_external_fail_closed or g1_recovery_metadata_scope' -v --tb=long`
  Result: 3 tests passed, 0 failed.

- Related Factory scheduler/control-plane suite:
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 HERMES_TEST_WORKERS=1 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_increment_integration.py`
  Result: 301 tests passed, 0 failed.

## Canonical Agent Core Factory readback

Canonical status was read via the approved Factory CLI only:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json | jq '{project: (.projects[0] | {project_id,status,autonomous_enabled}), claimed_r2d7: ([.tasks[] | select(.task_id == "zeus-alpha-research-ledger-core-r2d7-g1-preflight-terminal-word-recovery") | {task_id,status,phase,owner_profile,engine,branch,worktree_path}] | first), g1_blockers: ([.projects[0].document_status[]? | select((.category == "g1_required") and (.blocking == true)) | {file_name, missing, blocking}] | length)}'`

Readback result:

- project `zeus-alpha-research-ledger-core`: `status=active`, `autonomous_enabled=true`
- current R2d7 task: `status=running`, `phase=g1_recovery`, `owner_profile=codex-builder`, `engine=codex`
- branch/worktree: `factory/zeus-alpha-research-ledger-core/inc-103-r2d7-g1-preflight-terminal-word` / `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-103-r2d7-g1-preflight-terminal-word`
- current G1 blocker count remains `10`, as expected for this bounded preflight recovery.

No live `factory worker dispatch`, direct SQL, product execution, deploy, external runtime, messaging, primary mutation, merge, credential change, or activation was executed. Because runtime dispatch was explicitly out of scope and the task was already `running`, the live proof is limited to approved Factory status readback plus hermetic tests.

## Delivery boundary

Delivery is PR-first only. The branch must be pushed and reviewed independently at the exact final SHA before any merge, deploy, runtime dispatch, product execution, messaging, credential change, direct SQL, trading/risk, paper/live activation, or primary-checkout mutation.

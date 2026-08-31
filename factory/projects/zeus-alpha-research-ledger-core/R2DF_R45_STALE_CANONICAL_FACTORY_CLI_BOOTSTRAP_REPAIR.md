---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2df-r45-stale-canonical-factory-cli-boo
phase: g1_recovery
status: implemented_pending_pr_and_independent_exact_sha_review
validated: yes
reviewed: pending_independent_review
owner: codex-builder
run_id: run-1788145594-0b3b3d0c
branch: factory/zeus-alpha-research-ledger-core/inc-102-r2df-r45-stale-canonical-factory
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-102-r2df-r45-stale-canonical-factory
base_ref: origin/main
base_sha: 75c13a1ce85afc16da3ff708ad7f1d203b892ab4
---

# R2df-R45 — stale canonical Factory CLI bootstrap repair

## Scope boundary

This increment repairs only the Factory CLI/bootstrap/scheduler control-plane path for `zeus-alpha-research-ledger-core-r2df-r45-stale-canonical-factory-cli-boo`.

Allowed work:
- Reproduce that the generated canonical `hermes` console script can import a stale editable primary checkout before Factory source delegation runs.
- Add the smallest Factory-aware bootstrap so `hermes factory ...` console entrypoints re-exec from the current working source tree or a verified configured-base source tree before importing `hermes_cli.main`.
- Preserve current `factory status`, `factory project resolve-state`, and `factory project tick` current-source behavior; keep dirty/unverified configured-base fallbacks fail-closed.

Explicitly not authorized:
- ALR product/runtime implementation, review/QA/product dispatch, deployment, credential/provider changes, messaging, trading/risk/paper/live behavior, direct SQL, primary checkout mutation, merge, force-push, or self-approval.

## Canonical inputs read before implementation

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2AX_CURRENT_ORIGIN_FACTORY_CLI_G1_RECOVERY_DISPATCH.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2AM_STALE_PRIMARY_FACTORY_TICK_SOURCE_RESOLUTION_REPAIR.md`

## Reproduced stale canonical CLI mismatch

Readback from the assigned worktree using the installed primary checkout console script:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/hermes factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r45-canonical-status-before.json
```

Parsed evidence:

```text
factory_cli_source_root=null
factory_status_source_root=null
factory_status_delegated=null
project_status=active
autonomous=true
g1_rows=14
g1_blocking=10
first_blockers=FACTORY_INTAKE.md,REQUIREMENTS_ANALYSIS.md,PATTERN_ANALYSIS.md,ASSUMPTIONS_AND_OPEN_QUESTIONS.md,PRD.md,ADRS.md,METHODOLOGY_PLAN.md,TECHNICAL_BLUEPRINT.md,TASK_GRAPH.md,SECURITY_GATES.md
metadata_anomalies=unvalidated_required_docs
```

The same allowed source-root readback with the canonical interpreter/module path from the assigned worktree reported the current configured-base state instead:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r45-pythonm-status-after.json
```

Parsed evidence:

```text
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-102-r2df-r45-stale-canonical-factory
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-102-r2df-r45-stale-canonical-factory
factory_status_delegated=null
project_status=active
autonomous=true
g1_rows=14
g1_blocking=0
first_blockers=
metadata_anomalies=
```

## Implementation summary

Changed code:
- `hermes_bootstrap.py`
  - Adds `main()` as the generated `hermes` console-script entrypoint.
  - Detects `hermes factory ...` before importing `hermes_cli.main`.
  - Selects a complete Factory source root from the current working tree first, then a clean worktree whose `HEAD` exactly matches `origin/HEAD` or `origin/main` when the running editable source is stale/behind and an ancestor of that base.
  - Re-execs as `sys.executable -m hermes_cli.main ...` with `cwd`, `PYTHONPATH`, `HERMES_PYTHON_SRC_ROOT`, and `HERMES_FACTORY_SOURCE_DELEGATED=1` bound to the selected source root.
  - Does not delegate non-Factory commands and does not fall back after a selected Factory source re-exec fails.
- `pyproject.toml`
  - Changes the `hermes` console script target from `hermes_cli.main:main` to `hermes_bootstrap:main` so the bootstrap runs before `hermes_cli.main` is imported.
- `tests/hermes_cli/test_factory_orchestrator_tick.py`
  - Adds a RED/GREEN regression proving a stale editable primary root with a stale tick returning `claimed=null` is bypassed before `hermes_cli.main` can import stale control-plane code.
- `tests/test_project_metadata.py`
  - Pins the packaging contract that the `hermes` console script enters through `hermes_bootstrap:main`.

## RED/GREEN and validation evidence

RED evidence before implementation:

```text
export HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 && scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k console_entrypoint_delegates_factory_tick_to_configured_base_before_stale_claimed_null -v --tb=short
Result: 1 failed, 23 deselected. Failure: AttributeError: module 'hermes_bootstrap' has no attribute 'main'.
```

GREEN focused validation after implementation:

```text
export HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3; scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k console_entrypoint_delegates_factory_tick_to_configured_base_before_stale_claimed_null -v --tb=short
Result: 1 passed, 0 failed.

export HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3; scripts/run_tests.sh tests/test_project_metadata.py -k hermes_console_script_enters_through_bootstrap -v --tb=short
Result: 1 passed, 0 failed.

export HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3; scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -v --tb=short
Result: 24 passed, 0 failed.

export HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3; scripts/run_tests.sh tests/test_project_metadata.py -v --tb=short
Result: 8 passed, 0 failed.

export HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3; scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'explicit_g1_recovery or r2df_r23_phase_g1_recovery or docs_recovery_before_validation_work_when_docs_are_red' -v --tb=short
Result: 3 passed, 0 failed.

export HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3; scripts/run_tests.sh tests/test_hermes_bootstrap.py -v --tb=short
Result: 13 passed, 6 skipped, 0 failed (Windows-only cases skipped on Linux lane).

git diff --check
Result: exit 0, no whitespace errors.
```

`tests/hermes_cli/test_factory_orchestrator_tick.py` covers the three repaired control-plane source paths: `factory status`, `factory project resolve-state`, and `factory project tick`. The filtered increment-integration run preserves the existing explicit `g1_recovery` ordering contract so a G1 recovery row outranks product/review work while G1/docs are red.

## Post-repair canonical readbacks

Current-source canonical module readback from the assigned worktree:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r45-status-final.json

db_backend=agent_core_postgres
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-102-r2df-r45-stale-canonical-factory
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-102-r2df-r45-stale-canonical-factory
factory_status_delegated=False
g1_required_count=14
g1_blocking_count=0
readiness_sources=configured_base_ref
base_commits=75c13a1ce85afc16da3ff708ad7f1d203b892ab4
metadata_anomalies=[]
metadata_projection_source=current_document_status
task=zeus-alpha-research-ledger-core-r2df-r45-stale-canonical-factory-cli-boo status=running phase=g1_recovery owner=codex-builder
task=zeus-alpha-research-ledger-core-r2df-r39-fail-closed-terminalization-of- status=todo phase=g1_recovery owner=codex-builder
task=zeus-alpha-research-ledger-core-r2df-r23-fail-closed-review-runtime-fail status=todo phase=g1_recovery owner=codex-builder
task=zeus-alpha-research-ledger-core-r2df-r17-docs-first-validation-scheduler status=todo phase=g1_recovery owner=codex-builder
```

Installed-shim readback remains the source-backed technical failure until this PR is reviewed and the console script is regenerated from the repaired `[project.scripts]` metadata. `read_file /home/jean/Projects/hermes-agent-original/venv/bin/hermes` shows the live shim still imports `from hermes_cli.main import main` at line 6, so it cannot execute `hermes_bootstrap.main()` yet without mutating the primary checkout/venv. The same status command through the installed shim therefore still reports the stale primary projection:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/hermes factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r45-installed-shim-status-final.json

factory_cli_source_root=None
factory_status_source_root=None
factory_status_delegated=None
g1_required_count=14
g1_blocking_count=10
blocking_files=FACTORY_INTAKE.md,REQUIREMENTS_ANALYSIS.md,PATTERN_ANALYSIS.md,ASSUMPTIONS_AND_OPEN_QUESTIONS.md,PRD.md,ADRS.md,METHODOLOGY_PLAN.md,TECHNICAL_BLUEPRINT.md,TASK_GRAPH.md,SECURITY_GATES.md
metadata_anomalies=['unvalidated_required_docs']
```

## Live dispatch boundary

No live `factory project tick`, `factory worker dispatch`, `factory project resolve-state`, or task-status mutation was executed by this worker after the repair. This preserves the run's hard DB-write boundary (`factory status` and `factory gate record` only) and avoids opening another increment from this worker. The installed-shim status mismatch above is the source-backed technical failure for AC3 until this PR is reviewed and the console script entrypoint is regenerated from the repaired metadata.

## Delivery and review handoff

Delivery remains PR-first:
- Push only branch `factory/zeus-alpha-research-ledger-core/inc-102-r2df-r45-stale-canonical-factory`.
- Open a non-draft Zeus-signed PR against `main` with label `agent:zeus`.
- Record the immutable final candidate SHA in the PR body/evidence after commit creation.
- Require independent exact-SHA review before any downstream Factory dispatcher treats this bootstrap repair as reviewed.
- No merge, deploy, direct SQL, primary-checkout mutation, credential change, external runtime operation, product dispatch, review dispatch, or ALR task dispatch occurred in this worker run.

---
project_id: zeus-alpha-research-ledger-core
increment: R2aw
status: implemented
validated: yes
reviewed: pending
created_at_utc: 2026-08-17T11:18:14Z
owner: codex-builder
reviewer: quality-reviewer
---

# R2aw — isolated current-origin Factory G1 status recovery

## Scope

Bounded technical recovery for Factory G1 status/readback divergence when a stale primary checkout is present but the operator is executing from a Factory-provisioned isolated worktree based on current `origin/main`.

## Immutable source evidence

- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2aw-isolated-current-origin-fac`
- Branch: `factory/zeus-alpha-research-ledger-core/inc-001-r2aw-isolated-current-origin-fac`
- Starting worktree HEAD: `52df8d7c6599e3ec2ec4559e0139ffd91ec74011`
- Starting `origin/main`: `52df8d7c6599e3ec2ec4559e0139ffd91ec74011`
- Stale primary checkout observed but not mutated: `/home/jean/Projects/hermes-agent-original`, HEAD `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`, branch `main`

Command evidence:

```text
git status --short --branch && git rev-parse HEAD && git rev-parse origin/main && git branch --show-current
# branch: factory/zeus-alpha-research-ledger-core/inc-001-r2aw-isolated-current-origin-fac...origin/main
# HEAD/origin_main: 52df8d7c6599e3ec2ec4559e0139ffd91ec74011
```

## Change summary

- `hermes_cli/factory.py` now resolves a complete Factory source root under the current working directory before running project-specific Factory status delegation or the orchestrator tick. This keeps `hermes factory status` and project tick source execution bound to the isolated worktree when the CLI module was loaded from a stale primary checkout.
- The status delegation is guarded by `HERMES_FACTORY_SOURCE_DELEGATED=1` to avoid recursion.
- Project tick JSON results now include `factory_cli_source_root` and `factory_orchestrator_script` for auditable source provenance.

## RED evidence

Command:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k 'isolated_cwd_source or status_prefers'
```

Result before implementation:

```text
2 failed, 10 deselected
- test_project_tick_prefers_isolated_cwd_source_over_stale_running_module failed because _resolve_orchestrator_script used the stale running module root.
- test_status_prefers_isolated_cwd_source_over_stale_running_module failed because cmd_status used the stale backend instead of delegating to the isolated current-origin worktree source.
```

This reproduced the stale-primary/current-origin invocation divergence without mutating the primary checkout, main, credentials, external runtimes, or Factory DB directly.

## GREEN evidence

Commands:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'document_status or status_projection or status_effective_projection or unvalidated_required_docs'
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status --json zeus-alpha-research-ledger-core | jq -r '<G1 summary filter>'
```

Results:

```text
test_factory_orchestrator_tick.py: 12 passed
test_factory_control_plane_refactor.py selected G1/status tests: 25 passed
factory status summary:
  project_status=active
  metadata_reconciliation_anomalies=[]
  metadata_reconciliation_projection_source=current_document_status
  g1_rows=14
  g1_blockers=0
  readiness_sources=["configured_base_ref"]
  base_commits=["52df8d7c6599e3ec2ec4559e0139ffd91ec74011"]
  primary_heads=["4eb87e4cd48105af05fe974cf1d493f0e1b57ae1"]
  primary_checkout_accepted=[false]
  blocking_documents=[]
```

## Source documents read

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/REQUIREMENTS_ANALYSIS.md`
- `factory/projects/zeus-alpha-research-ledger-core/PRD.md`
- `factory/projects/zeus-alpha-research-ledger-core/ADRS.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2AU_CURRENT_ORIGIN_G1_DOCUMENT_STATUS_PROJECTION_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2AV_CURRENT_ORIGIN_G1_STATUS_PROJECTION_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2AM_STALE_PRIMARY_FACTORY_TICK_SOURCE_RESOLUTION_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2C6_BOUNDED_CURRENT_ORIGIN_G1_RESOLVER_READBACK_RECOVERY.md`

## No external execution statement

No direct SQL, merge, deploy, credential operation, external runtime call, trading/risk/paper/live action, or messaging was performed. Live Factory DB interaction was limited to the allowed `hermes_cli.main factory status` readback path.

---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2ai-r2-persisted-active-metadata-reconc
run_id: run-1787078951-4476c746
phase: documentation
status: implementation_repaired_pending_pr_review
validated: yes
reviewed: pending
---

# R2ai-R2 persisted active metadata reconciliation recovery

## Scope and hard boundaries

This increment is bounded to Factory control-plane reconciliation behavior and project-local evidence for `zeus-alpha-research-ledger-core`. Agent Core Postgres `factory.*` remains the source of truth, but this worker used only the sanctioned Factory CLI readback path for live DB access:

- `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`

No direct SQL, `psql`, `psycopg2`, ad-hoc DB mutation script, migration, primary-checkout mutation, merge, deploy, credential/secret access, messaging/connector call, external runtime, ALR product dispatch, trading/risk/paper/live action, force-push, or main push was performed. Live `factory project resolve-state` and `factory project tick` were not executed because this run's hard DB-write allowlist names only `factory status` and `factory gate record`; those project-action paths are covered by behavioral tests instead.

## Canonical inputs read

Required entrypoint and G1/control documents read before implementation:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2AI_R2_NON_DESTRUCTIVE_CURRENT_ORIGIN_G1_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2AP_PR72_RESIDUAL_G1_TASK_METADATA_RECONCILIATION.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2BM_CANONICAL_G1_DOCS_GATE_SOURCE_ROOT_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2BN_CANONICAL_G1_REVIEW_STATE_SOURCE_ROOT_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2CN_BOUNDED_CANONICAL_G1_DOCS_GATE_AND_PR_PROVENANCE_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2CU_PRIMARY_ROOT_DOCS_FIRST_G1_RESOLVER_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2CV_CURRENT_ORIGIN_G1_DOCUMENTATION_VALIDATION_RECOVERY.md`

Source files traced before editing:

- `hermes_cli/factory.py` — Factory CLI status/project-action/tick source-root selection.
- `hermes_cli/factory_pg.py` — Agent Core Factory Postgres projections/reconciliation.
- `tests/hermes_cli/test_factory_orchestrator_tick.py` — CLI/dashboard project tick source-root behavior.
- `tests/hermes_cli/test_factory_control_plane_refactor.py` — Factory status/reconciler metadata projection behavior.

## Starting identity

After `git fetch origin main --prune` in the assigned worktree:

- Branch: `factory/zeus-alpha-research-ledger-core/inc-024-r2ai-r2-persisted-active-metadat`
- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-024-r2ai-r2-persisted-active-metadat`
- `HEAD=18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc`
- `origin/main=18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc`
- `merge-base=18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc`
- `ahead/behind=0\t0`

## Reproduction and diagnosis

Sanctioned pre-repair status readback saved `/tmp/r2ai-r2-status-fresh-before.json` and exited `0`. Targeted summary:

```text
project=zeus-alpha-research-ledger-core status=active reconciliation_required=False technical_hold=True anomalies=[] projection=current_document_status stale_anomalies=[] source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-024-r2ai-r2-persisted-active-metadat status_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-024-r2ai-r2-persisted-active-metadat delegated=False g1_required_rows=14 g1_blocking=0 base_commits=['18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc'] readiness_sources=['configured_base_ref'] latest_event=199708:project_reconciled:["unvalidated_required_docs"]
```

This reproduced the exact split required by the assignment:

1. The current configured-base/candidate source is clean: all 14 required G1 rows are non-blocking from `readiness_source=configured_base_ref` at base `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc`.
2. Active project readback still carried stale `technical_hold=true` even though the G1 document anomaly projection was clean.
3. The event stream still showed fresh `project_reconciled` events with `unvalidated_required_docs`, proving a mutating reconciler/tick path could still reintroduce stale primary/current-origin evidence even after status/readback source-root repairs.

Root cause in code:

- `factory status` and resolver-class project actions had current-origin/configured-base source-root fallback, but `_resolve_orchestrator_script()` in `hermes_cli/factory.py` selected only the cwd source root or running source root. If invoked from a stale primary root without a current worktree cwd, `factory project tick` could still execute stale primary code and persist a stale `project_reconciled` anomaly.
- `reconcile_project()` and the effective status projection in `hermes_cli/factory_pg.py` cleared stale G1 projection keys after current document rows became non-blocking, but did not clear a recovery-scoped `technical_hold` whose `technical_hold_reason` explicitly named a bounded recovery task that had already reached a positive terminal state. That left `technical_hold=true` visible after `unvalidated_required_docs` was no longer a current document-state blocker.

## Repair implemented

Implementation files changed:

- `hermes_cli/factory.py`
  - `_resolve_orchestrator_script()` now uses the same verified configured-base source-root fallback already used by status/resolver delegation when there is no preferred cwd worktree source. This keeps `project tick` from falling back to stale primary code when a complete clean configured-base worktree is available, and preserves fail-closed behavior through the existing configured-base verifier.
- `hermes_cli/factory_pg.py`
  - Added bounded recovery technical-hold parsing for reasons of the form `... bounded to task <task_id> ...`.
  - Clears only known technical-hold metadata keys (`technical_hold`, `technical_hold_kind`, `technical_hold_reason`, `technical_hold_by`, `technical_hold_at`, and the hold's `reactivation_policy`) when the referenced task exists in a positive terminal status and the current reconciliation findings no longer include a G1 required-doc anomaly.
  - Applies the cleanup both to effective `status` readback and to the persisted metadata expression used by `reconcile_project()` so the next authorized canonical project reconciliation can persist the repaired projection without direct SQL.
  - Leaves unrelated active blockers/fail-closed task rows intact; historical events remain audit history.

Behavioral tests added/updated:

- `tests/hermes_cli/test_factory_orchestrator_tick.py`
  - Adds configured-base fallback coverage for `factory project tick` when the running module is stale and the cwd is not an isolated worktree.
- `tests/hermes_cli/test_factory_control_plane_refactor.py`
  - Adds effective-status projection coverage for resolved bounded recovery technical holds.
  - Adds reconciler persistence coverage proving the metadata update expression removes stale technical-hold keys along with stale G1 projection state.
  - Adds fail-closed helper coverage proving unresolved/non-terminal recovery tasks do not clear a technical hold.

No source-text inspection tests were added.

## RED / GREEN / validation evidence

RED evidence was recorded by saving the implementation diff, temporarily checking out only the implementation files back to base while leaving the new tests present, and running the selected tests with retries disabled. The command exited `1` as expected, then the implementation patch was immediately re-applied:

```text
git diff -- hermes_cli/factory.py hermes_cli/factory_pg.py > /tmp/r2ai-r2-code.patch && git checkout -- hermes_cli/factory.py hermes_cli/factory_pg.py && HERMES_TEST_FILE_RETRIES=0 HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_control_plane_refactor.py -k 'project_tick_prefers_configured_base_source_when_invoked_from_stale_primary_root or status_effective_projection_clears_resolved_recovery_technical_hold or reconcile_clears_resolved_recovery_technical_hold_metadata or resolved_recovery_technical_hold_requires_positive_terminal_task' ; red_status=$? ; git apply /tmp/r2ai-r2-code.patch ; exit $red_status
# exit 1
```

GREEN targeted evidence:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k 'project_tick_prefers_configured_base_source_when_invoked_from_stale_primary_root or project_tick_prefers_isolated_cwd_source_over_stale_running_module'
# exit 0

HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'resolved_recovery_technical_hold or status_effective_projection_clears_resolved_recovery_technical_hold or reconcile_clears_stale_g1_checkout_projection_when_current_docs_nonblocking'
# exit 0

HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_control_plane_refactor.py -k 'project_tick_prefers_configured_base_source_when_invoked_from_stale_primary_root or status_effective_projection_clears_resolved_recovery_technical_hold or reconcile_clears_resolved_recovery_technical_hold_metadata or resolved_recovery_technical_hold_requires_positive_terminal_task'
# exit 0
```

Broader focused GREEN evidence:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_control_plane_refactor.py
# exit 0

git diff --check
# exit 0
```

## Final sanctioned Factory readback

Post-repair sanctioned status readback saved `/tmp/r2ai-r2-status-final.json` and exited `0`. Targeted summary:

```text
project=zeus-alpha-research-ledger-core status=active reconciliation_required=False technical_hold=None anomalies=[] projection=current_document_status stale_anomalies=[] source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-024-r2ai-r2-persisted-active-metadat status_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-024-r2ai-r2-persisted-active-metadat delegated=False g1_required_rows=14 g1_blocking=0 base_commits=['18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc'] readiness_sources=['configured_base_ref'] latest_event=199735:project_reconciled:["unvalidated_required_docs"]
```

Interpretation:

- Current active status readback no longer reports `unvalidated_required_docs` in active `reconciliation_anomalies`.
- Current active status readback no longer reports `technical_hold=true`.
- All 14 required G1 rows remain non-blocking from configured base `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc`.
- Historical event `199735` still records `unvalidated_required_docs`; it is audit/projection history, not current configured-base document readiness. The repaired tick-source path prevents the stale-primary tick path from becoming the future canonical source after this PR is reviewed/merged into the runtime.

## PR and review handoff requirements

This commit must be delivered PR-first from branch `factory/zeus-alpha-research-ledger-core/inc-024-r2ai-r2-persisted-active-metadat` with:

- Zeus signature in the commit/PR.
- GitHub label `agent:zeus`.
- Exact candidate SHA named in the PR body and in Factory gate evidence after push.
- Independent exact-SHA quality/security review recorded after the final candidate SHA is immutable.

This artifact intentionally does not claim independent approval, merge, deploy, primary runtime propagation, direct DB cleanup, or ALR/product dispatch.

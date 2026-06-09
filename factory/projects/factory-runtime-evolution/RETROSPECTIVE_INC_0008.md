# RETROSPECTIVE_INC_0008 — Cron/control-plane restoration

## Trigger

Jean asked Zeus to stop treating the cron failures as a local cleanup and to repair the root cause inside the canonical Factory workflow. The immediate incident was recurring cron error alerts from Factory jobs that imported `hermes_cli.factory_backend` even though `main` did not contain the Factory Runtime Evolution control-plane modules that those scripts were written for.

## Crons audited

| Cron | Functional owner | Purpose | Canonical repo/source | Correct final state |
|---|---|---|---|---|
| `factory-status-sync` | Factory | Emit a JSON projection of Agent Core Factory projects/tasks/gates/runs for dashboard/cron status. | `hermes-agent-original/scripts/factory/factory_status_sync.py` | Active, script-only, local delivery; uses `factory_backend`/Agent Core Postgres only. |
| `factory-reviewer-dispatch` | Factory | Identify `review_ready` / `qa_ready` tasks with missing or invalid independent reviewer assignment. | `hermes-agent-original/scripts/factory/factory_reviewer_dispatch.py` | Active, script-only, local delivery; report-only until dispatch/review claiming is explicitly enabled. |
| `factory-blocker-detector` | Factory L2 supervisor | Classify blocked/orphan Factory tasks, record deterministic events, and create human questions only when truly required. | `hermes-agent-original/scripts/factory/factory_blocker_detector.py` + `hermes_cli.factory_pg` | Reactivable after backend methods/tests exist; no alert loop when no blockers exist. |
| `factory-orchestrator-tick` | Factory L1 tick | Monitor runs, clear resolved blockers, claim review/rework/new tasks, spawn worker process for a claimed run. | `hermes-agent-original/scripts/factory/factory_orchestrator_tick.py` + `hermes_cli.factory_pg` | Reactivable only with single-writer/manual takeover guard and Agent Core `task_runs` schema. |
| `factory-watchdog-alerts` | Factory watchdog | Send concise actionable alerts only for unsuppressed runtime invariants/blockers. | `hermes-agent-original/scripts/factory/factory_watchdog_alerts.py` + `hermes_cli.factory_pg` | Reactivable after blocker/alert APIs exist; stays silent with no unsuppressed alerts. |
| `vapi-postcall-lead-supervisor` | Voice/Sales funnel | Trusted post-call worker that turns Vapi/Sophie commitments into CRM/material/follow-up actions. | `sitiouno-agent-runtime/scripts/vapi_postcall_worker.py` | Active from runtime wrapper/workdir. Not part of Factory control-plane. |
| `customer-intent-supervisor` | CRM customer-service escalation | Scans customer intents raised by constrained ATC/Sophie surface and notifies Zeus/owner for privileged execution. | `sitiouno-agent-runtime/scripts/customer_intent_supervisor.py` | Active from runtime wrapper/workdir. Not part of Factory control-plane. |

## Root cause

1. The live cron scripts expected Factory Runtime Evolution modules (`factory_backend`, `factory_contracts`, expanded `factory_pg`) that existed only in a previous increment branch/worktree, not in `main`.
2. The temporary mitigation patched two scripts and paused three jobs, but it left code split across `~/.hermes/scripts` and an old worktree. That stopped alert spam but did not restore the canonical Factory product.
3. Sales/Voice/CRM cron jobs were mixed in the same cleanup conversation, but their correct ownership is `sitiouno-agent-runtime`; they should remain runtime wrappers and not be folded into Factory.

## Canonical fix

- Restore the Factory Runtime Evolution control-plane modules into the repo-backed source of truth:
  - `hermes_cli/factory_backend.py`
  - `hermes_cli/factory_catalog.py`
  - `hermes_cli/factory_contracts.py`
  - expanded `hermes_cli/factory_pg.py`
  - `db/modules/factory/000003_orchestration_runtime.sql`
- Keep production Factory state in Agent Core Postgres only; SQLite fallback is disabled for runtime/control-plane scripts.
- Promote cron scripts into `scripts/factory/` and make `~/.hermes/scripts/*.py` thin wrappers to repo scripts, mirroring the existing runtime-wrapper pattern for Vapi and customer-intent supervisors.
- Add regression tests for backend selection, blocker classification, watchdog invariants, and script execution against a fake backend.

## Workflow alignment

- Factory crons are part of Factory Runtime Evolution: L1 tick, L2 blocker/supervisor, watchdog/reporting.
- Vapi post-call and customer-intent crons are part of Sales/Voice/CRM workflows. They feed CRM/opportunity/follow-up/owner escalation and should not mutate Factory project state.
- No channel-specific or provider-specific flow becomes a competing Factory/Sales method; cron wrappers only invoke the owning workflow's canonical runtime script.

## Acceptance evidence required

1. Focused pytest file passes: `tests/hermes_cli/test_factory_cron_control_plane.py`.
2. Existing Factory tool tests pass with the canonical Postgres-only backend mocked in unit scope.
3. Real script smokes run against Agent Core Postgres for status/reviewer/blocker/watchdog/orchestrator imports.
4. Cron jobs are resumed only after scripts exit 0 and `cronjob list` shows no enabled job with an error.
5. `~/.hermes/scripts` contains wrappers to repo/runtime source files, not forked logic.

# Factory Runtime Evolution — Concrete Advancement Plan

## Decision context

Jean's correction is canonical: Factory self-improvement is one living product, not scattered mini-projects. The Factory DB now has the canonical project ID `factory-runtime-evolution`; the previous `factory-runtime-remediation` history was absorbed/superseded and repo artifacts now live under `factory/projects/factory-runtime-evolution/`.

The local reference pack is now available at:

```text
/home/jean/reference-repos/factory-workflow-patterns
```

The primary workflow/process design guide is n8n, supported by Temporal, Prefect, LangGraph, BMAD-METHOD, and spec-kit. See `REFERENCE_REPOS.md`.

## Target outcome

Factory Runtime should become a self-improving orchestrator with three loops:

1. L1 mechanical tick: dispatch, monitor, reconcile, claim next task/review/rework.
2. L2 active supervisor: evaluate invariants and repair safe stuck states without waiting for Jean.
3. L3 daily retrospective: analyze incidents, consult reference repos, create increments inside Factory Runtime Evolution, and improve the runtime through branch/PR/gates.

## Non-negotiable invariant

Every autonomous Factory project must be in one explainable state:

- completed/accepted/cancelled;
- active with queued/running worker;
- active with claimable ready/rework/review task;
- intentionally paused with explicit metadata;
- waiting on concrete human question;
- or under supervisor repair with an action already recorded.

Any other combination is RED.

## Immediate plan to advance

### Step 0 — Reconcile the canonical self-improvement project

Status: done in INC-0001 kickoff.

Outcome:

1. Factory DB canonical project ID is `factory-runtime-evolution`.
2. `factory-runtime-remediation` was preserved as historical/superseded evidence, not deleted.
3. Project-local artifacts now live under `factory/projects/factory-runtime-evolution/`.
4. Event recorded: `runtime_evolution_canonicalized`.
5. `REFERENCE_REPOS.md` is linked from this documentation index.

### Step 1 — Create regression test for the current absorbing-state bug

Objective: prove the observed failure cannot recur.

Observed bug:

`agent-core-followup-reminders` is `delivery_hold`, `autonomous_enabled=true`, has blocked task F11, no active run, blocker classified auto-resolvable, and `Poner autónomo` writes resume/reconcile events but returns to `delivery_hold` with `claimed=null`.

Test to add:

```text
tests/hermes_cli/test_factory_canonical_runtime.py::test_delivery_hold_autoresolvable_blocker_reopens_and_dispatches
```

Expected behavior:

1. Seed project in delivery_hold with blocked task and structured/legacy blocker metadata.
2. Seed evidence that blocker resolution condition is now true.
3. Run supervisor/reconcile/dispatch flow.
4. Assert task becomes `review_ready` or `rework`.
5. Assert project becomes dispatchable.
6. Assert a worker/reviewer can be claimed.
7. Assert event records invariant and action taken.

Reference patterns:

- n8n `task-state.ts`: explicit lifecycle and unexpected-state failure.
- n8n `active-executions.ts`: conditional status updates and active execution discipline.
- Prefect `server/schemas/states.py`: terminal states and state metadata.

Definition of Done:

- Test fails before implementation.
- Test name and reference files are cited in the increment plan.

### Step 2 — Add minimal Factory contracts/FSM module

Objective: stop string-state sprawl before more repairs.

Files:

- Create `hermes_cli/factory_contracts.py`.
- Add focused tests in `tests/hermes_cli/test_factory_contracts.py`.

Initial scope only:

- `ProjectStatus`
- `TaskStatus`
- `RunStatus`
- terminal helpers
- dispatchable project statuses
- runnable task statuses
- in-flight task statuses
- invariant enum, e.g. `RED_DELIVERY_HOLD_WITH_BLOCKED_WORK`

Do not rewrite the whole runtime yet. Use contracts to cover the bug class first.

Reference patterns:

- n8n `execution-status.ts`.
- Prefect `StateType` and `TERMINAL_STATES`.

Definition of Done:

- Tests prove closed sets and helper behavior.
- Existing runtime imports constants from contract module for the affected path.

### Step 3 — Implement structured blocker lifecycle for safe repair

Objective: make blockers machine-resolvable or explicitly human.

Files:

- Extend `hermes_cli/factory_pg.py` only where needed.
- Consider adding `factory.blockers` migration only if metadata is insufficient; do not over-migrate before proving need.
- Add tests for legacy blocked metadata and future structured metadata.

Minimum blocker schema:

```json
{
  "blocker_code": "missing_notion_project",
  "category": "documentation",
  "requires_human": false,
  "resolution_strategy": "project_metadata_has_notion_tracker",
  "next_transition": "review_ready"
}
```

Definition of Done:

- A resolved auto-resolvable blocker is reopened automatically.
- A true human blocker creates/updates `factory.human_questions` instead of idling.
- Legacy blocker strings are classified but migrated forward when touched.

### Step 4 — Add L2 active supervisor

Objective: convert watchdog/reporting from passive observation into action.

Files:

- Create `hermes_cli/factory_supervisor.py`.
- Create/replace script `~/.hermes/scripts/factory_supervisor.py` after code is tested.
- Add CLI entry later: `hermes factory supervisor run --json`.

Supervisor evaluates invariants:

- `RED_DELIVERY_HOLD_WITH_BLOCKED_WORK`
- `RED_BLOCKED_AUTORESOLVABLE_NOT_ACTED`
- `RED_ACTIVE_EMPTY`
- `RED_CLAIMED_NULL_REPEATED`
- `YELLOW_WAITING_HUMAN`
- `YELLOW_INTENTIONAL_PAUSED`

Supervisor safe actions:

- reconcile
- resolve blocker
- reopen task to review/rework
- create human question
- force worker tick
- create Factory Runtime Evolution increment if code change is needed

Reference patterns:

- n8n `active-executions.ts` for active execution registry and cleanup.
- Temporal workflow task state machine for retry/attempt semantics.
- Prefect server orchestration rule: state transitions go through authority layer.

Definition of Done:

- Supervisor output is structured JSON.
- Every RED finding has action attempted or human question.
- No alert is emitted with only vague prose.

### Step 5 — Make watchdog and daily report consume supervisor output

Objective: alerts must be useful.

Files:

- `~/.hermes/scripts/factory_watchdog_alerts.py`
- `~/.hermes/scripts/factory_daily_report_markdown.py`
- possibly repo-backed equivalents if scripts are promoted into source control.

Alert contract:

```text
project_id
task_id/gate_id/run_id
invariant violated
cause
action attempted
result
next action
human question only if needed
```

Definition of Done:

- If supervisor fixes issue, report says fixed.
- If supervisor cannot fix, report says why and what question/increment was created.
- No more `claimed=null repeated` alert without project/task/action context.

### Step 6 — Improve Dashboard control plane action

Objective: `Poner autónomo` must not be a blind resume button.

Behavior:

1. Resume project.
2. Run supervisor health check for that project.
3. If safe, repair and dispatch.
4. If not safe, return exact reason and next action.
5. UI shows invariant/action/result, not only unchanged status.

Files:

- `hermes_cli/web_server.py`
- dashboard frontend if needed.

Definition of Done:

- Pressing `Poner autónomo` on the current bug class either dispatches repair or explains the exact blocker.
- API response includes supervisor summary.

### Step 7 — Add daily retrospective self-improvement loop

Objective: make Factory learn from repeated failures.

Retrospective flow:

1. Read events, task_runs, gates, watchdog outputs, daily reports.
2. Group incidents by fingerprint.
3. For every structural gap, consult `REFERENCE_REPOS.md` local pack.
4. Create/update one increment under Factory Runtime Evolution.
5. Write failing test before implementation.
6. Assign worker/reviewer.
7. Record reference files consulted and gate evidence.

Definition of Done:

- Daily retro can create a runtime-evolution increment without creating a new project.
- Repeated incidents become planned increments, not repeated chat complaints.

## Branch/PR policy

Use branches like:

```text
factory/runtime-evolution/inc-0000-canonicalize-project
factory/runtime-evolution/inc-0001-delivery-hold-autoresolvable-regression
factory/runtime-evolution/inc-0002-contracts-fsm
factory/runtime-evolution/inc-0003-blocker-lifecycle
factory/runtime-evolution/inc-0004-active-supervisor
```

Merge policy:

- Auto-merge candidate only if low-risk, tests pass, independent review passes, and no auth/secrets/provider/schema-destructive changes.
- Jean approval required for permissions, secrets/auth/providers, destructive migrations, derived-agent capability boundaries, or public/private surface changes.

## Concrete next move

The next safe action is not to force-close `agent-core-followup-reminders`.

The next safe action is:

1. Reconcile/rename the canonical Factory Runtime Evolution project.
2. Open increment `INC-0001-delivery-hold-autoresolvable-regression`.
3. Add the failing test that reproduces the current `delivery_hold` absorbing state.
4. Implement the smallest structural supervisor/blocker fix that makes that test GREEN.
5. Then rerun the real project through the orchestrator path, not manual status edits.

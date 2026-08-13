# Retrospective — FRE-025 Pause Provenance and Source Delivery

| Field | Value |
|---|---|
| Increment | `FRE-025` |
| Date | 2026-08-12 / final owner verification 2026-08-13 |
| Owner validation | complete after focused regression GREEN + focused suite GREEN |
| Independent review | pending |
| Source integration | pending |

## Incident summary

An internal Factory actor could record a project as a manual user-decision pause while
attributing the action to `factory-orchestrator`. Alpha consequently carried
`pause_kind=user_decision`, `manual_pause=true`, and a system actor, which excluded it
from autonomous supervision without human/operator provenance. Separately, a broad
text heuristic could exempt control-plane-looking work from source-integration checks,
and reconciliation did not block a positive terminal source-bearing increment whose
branch was not verified in its origin base.

No secrets, credentials, external-service calls, or live Factory mutations were used
in this repair.

## Timeline

1. 2026-08-12: traced the pause CLI, control-plane mutation, reconciliation, delivery
   readiness, and queued-successor auto-resume paths.
2. 2026-08-12: added behavior-focused tests first and captured a meaningful RED result.
3. 2026-08-12: implemented explicit manual-pause authority/provenance, canonical
   technical/dependency holds, structured bootstrap metadata, and source-integration
   reconciliation/delivery guards.
4. 2026-08-12: independent review found and the owner corrected two additional
   fail-open paths: self-asserted bootstrap exemption and metadata-only integration
   claims without current Git ancestry evidence. The final suite and diff gate run
   below are the only completion evidence.

## Violated invariants

- A manual pause is a human/operator action; a reserved Factory system actor cannot
  manufacture that authority.
- Manual-pause authority and origin must be explicit, nonblank, durable audit data.
- Technical/dependency holds remain supervisable and are distinct from manual pause.
- A technical hold cannot downgrade `manual_attention`.
- Exemptions from source delivery must be structured and auditable, not inferred from
  task title or description text.
- A positive terminal source-bearing increment is not reconciled or delivery-ready
  until its branch is verified integrated into the origin base, or an explicit
  Jean-authorized waiver exists.
- A queued successor cannot auto-resume through that source-integration blocker.

## Corrective controls

- `hermes factory project pause` now requires `--reason`, `--actor`, and `--origin`.
  Empty fields and the reserved actors `factory-orchestrator`, `factory-reconciler`,
  `factory-monitor`, and `factory-dispatcher` fail closed before persistence.
- Manual pause writes audited origin/authority metadata and a distinct
  `manual_pause_recorded` event.
- `hermes factory project technical-hold` records a distinct
  `technical_dependency_hold` event, keeps autonomy enabled, clears stale manual-pause
  markers, and refuses to weaken `manual_attention`.
- Runtime-bootstrap repair recognition requires explicit structured Jean authorization
  and a nonblank authorization reason; title/description prose and self-asserted flags
  cannot exempt source integration.
- Reconciliation and critical delivery readiness share a source-integration guard;
  blocked completion also prevents queued-successor auto-resume. Legitimate non-source
  documentation/reconciliation tasks and explicit Jean-authorized waivers remain valid.
- Automatic project succession is explicit state, not queue inference: the new
  `factory.project_successions` contract requires Jean authorization metadata and is
  evaluated only after predecessor source integration is verified.
- The global control-plane lease serializes monitor/reconcile/succession/claim/spawn so
  watchdog observation cannot race a second mutating dispatcher.

## Schema migration

- Added `db/modules/factory/000004_successor_control.sql` as a new versioned Factory
  migration for `factory.runtime_leases` and `factory.project_successions`; deployed
  `000003_orchestration_runtime.sql` was not amended.
- Runtime application is via the existing canonical migration runner
  `scripts/agent_core_db.py migrate`. This isolated implementation did not apply live
  Agent Core DDL or mutate production Factory rows.

## Migration for misleading system-attributed user pauses

Do not rewrite `factory.*` tables directly. After independently confirming that an
existing pause was created by a reserved system actor and was not an actual human
pause, migrate it through the canonical control plane:

```bash
hermes factory status <project_id> --json
hermes factory project technical-hold <project_id> \
  --reason "Migrate legacy system-attributed user pause to supervised dependency hold" \
  --actor factory-orchestrator \
  --hold-kind dependency \
  --json
```

This restores a non-paused supervisable state and clears misleading manual-pause
markers while retaining a distinct audit event. Do not apply this migration to
`manual_attention`. A genuine human pause must instead be re-recorded with the real
human/operator actor and explicit origin. This increment does not perform the Alpha
migration; operational mutation is outside this isolated worktree's authority.

## Test evidence

RED command: the 18 newly added behavior-test node IDs in
`test_factory_control_plane_refactor.py` and `test_factory_increment_integration.py`
were run with:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python -m pytest -q <18 node IDs>
```

RED result: `16 failed, 2 passed in 2.23s`. The failures exercised the absent explicit
pause fields, missing technical-hold operation, broad text exemption, and missing
reconciliation/delivery/auto-resume guards. The two passes preserved legitimate
non-source and explicit-waiver behavior.

GREEN command: the identical 18-node command.

GREEN result: `18 passed in 0.78s`.

Final focused suite command:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python \
  scripts/run_tests.sh \
    tests/hermes_cli/test_factory_successor_control.py \
    tests/hermes_cli/test_factory_orchestrator_tick.py \
    tests/hermes_cli/test_factory_control_plane_refactor.py \
    tests/hermes_cli/test_factory_increment_integration.py \
    tests/hermes_cli/test_factory_cron_control_plane.py \
    tests/factory/test_factory_watchdog_alerts.py
```

Final focused-suite result: `6 files, 161 tests passed, 0 failed` in 5.8s
(runner wall) on 2026-08-13T08:28:52Z.

Syntax command:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python -m py_compile \
  hermes_cli/factory_pg.py hermes_cli/factory.py \
  scripts/factory/factory_orchestrator_tick.py \
  scripts/factory/factory_watchdog_alerts.py \
  scripts/factory/factory_blocker_detector.py \
  tests/hermes_cli/test_factory_successor_control.py
```

Syntax result: exit 0, no output.

Diff hygiene command: `git diff --check`.

Diff hygiene result: exit 0, no output.

## Remaining limitation

Existing open PRs and increment branches are not proven integrated by this control-plane
repair. They still require independent review and verified source integration into the
declared origin base before completion or delivery.

# QA Report

Project: `factory-runtime-docs-notion-refactor`
Updated: 2026-06-10T00:40:00Z
QA Run: R3 — Live smoke close/resolve and docs-first behavior
Engine: zeus · Run: run-1781053457-2e2ef879

Status: implementation in progress — R3 live smoke COMPLETE

---

## Smoke 1: funnel-core-crm-workflow closed state

```bash
$ hermes factory status funnel-core-crm-workflow
Factory DB: Agent Core Postgres/zeus_agent.factory (canonical; SQLite disabled)
Projects: 1 | Lanes: 2 | Tasks: 5 | Gates: 12 | Runs: 11
- funnel-core-crm-workflow: Funnel Core / CRM Sales Workflow [completed] risk=high
    lane funnel-core-crm-workflow-bmad bmad_hybrid surface=factory
    lane funnel-core-crm-workflow-zeus zeus_native surface=factory
```

```bash
$ hermes factory project resolve-state funnel-core-crm-workflow
✓ Project funnel-core-crm-workflow: resolve-state -> completed
```

RESULT: PASS — funnel-core-crm-workflow remains completed/superseded. No open tasks,
no active runs reported, no anomalies.

---

## Smoke 2: factory-runtime-docs-notion-refactor reconcile and resolve-state

```bash
$ hermes factory project reconcile factory-runtime-docs-notion-refactor
✓ Project factory-runtime-docs-notion-refactor: resolve-state -> active

$ hermes factory project resolve-state factory-runtime-docs-notion-refactor
✓ Project factory-runtime-docs-notion-refactor: resolve-state -> active
```

```bash
$ hermes factory status factory-runtime-docs-notion-refactor
Factory DB: Agent Core Postgres/zeus_agent.factory (canonical; SQLite disabled)
Projects: 1 | Lanes: 3 | Tasks: 14 | Gates: 2 | Runs: 10
- factory-runtime-docs-notion-refactor: Factory Runtime Docs/Notion Control-Plane Refactor [active] risk=high
    lane factory-runtime-docs-notion-refactor-bmad bmad_hybrid surface=factory
    lane factory-runtime-docs-notion-refactor-hybrid hybrid surface=factory
    lane factory-runtime-docs-notion-refactor-zeus zeus_native surface=factory
```

RESULT: PASS — reconcile and resolve-state are consistent; project is active with
3 lanes. No stale active_run rows or anomalies.

---

## Smoke 3: link-notion CLI help/readback behavior

```bash
$ hermes factory project link-notion factory-runtime-docs-notion-refactor \
    --page-id 37b37b39-cad6-817e-ab89-c881329c0db0 \
    --url "https://app.notion.com/p/Factory-Runtime-Docs-Notion-Control-Plane-Refactor-Factory-PM-37b37b39cad6817eab89c881329c0db0" \
    --page-title 'Factory Runtime Docs/Notion Control-Plane Refactor — Factory PM' \
    --actor factory-reporter --json
```

```json
{
  "action": "link-notion",
  "project_id": "factory-runtime-docs-notion-refactor",
  "readback": {
    "notion_tracker_page_id": "37b37b39-cad6-817e-ab89-c881329c0db0",
    "notion_tracker_title": "Factory Runtime Docs/Notion Control-Plane Refactor — Factory PM",
    "notion_tracker_url": "https://app.notion.com/p/Factory-Runtime-Docs-Notion-Control-Plane-Refactor-Factory-PM-37b37b39cad6817eab89c881329c0db0"
  },
  "reconcile": {
    "active_runs": 1,
    "anomalies": [],
    "auto_resumed_project_id": null,
    "pending_gates": 0,
    "project_id": "factory-runtime-docs-notion-refactor",
    "reconciliation_tasks_cancelled": 0,
    "reconciliation_tasks_created": 0,
    "status": "active",
    "task_counts": {
      "cancelled": 3,
      "done": 2,
      "running": 1,
      "superseded": 6,
      "todo": 2
    }
  }
}
```

RESULT: PASS — link-notion writes metadata, reads back correctly, and triggers reconcile
in a single call. Write/readback/audit contract is satisfied.

---

## Smoke 4: INC-0001 pytest suite (18 tests)

```bash
$ python -m pytest tests/hermes_cli/test_factory_control_plane_refactor.py -v --tb=short
============================= test session starts ==============================
platform linux -- Python 3.11.15, pytest-9.0.2, pluggy-1.6.0
plugins: asyncio-1.3.0, timeout-2.4.0, anyio-4.12.1
timeout: 30.0s
collected 18 items

tests/hermes_cli/test_factory_control_plane_refactor.py::test_notion_tracker_schema_validation_rejects_empty_and_bad_input PASSED [  5%]
tests/hermes_cli/test_factory_control_plane_refactor.py::test_notion_tracker_schema_validation_accepts_funnel_core_evidence PASSED [ 11%]
tests/hermes_cli/test_factory_control_plane_refactor.py::test_link_notion_tracker_writes_metadata_reads_back_and_audits PASSED [ 16%]
tests/hermes_cli/test_factory_control_plane_refactor.py::test_link_notion_tracker_raises_on_readback_mismatch PASSED [ 22%]
tests/hermes_cli/test_factory_control_plane_refactor.py::test_linked_notion_metadata_satisfies_reconciler_for_funnel_core PASSED [ 27%]
tests/hermes_cli/test_factory_control_plane_refactor.py::test_cli_link_notion_uses_backend PASSED [ 33%]
tests/hermes_cli/test_factory_control_plane_refactor.py::test_dispatch_preflight_blocks_implementation_without_docs_or_notion PASSED [ 38%]
tests/hermes_cli/test_factory_control_plane_refactor.py::test_dispatch_preflight_allows_when_docs_and_notion_ready PASSED [ 44%]
tests/hermes_cli/test_factory_control_plane_refactor.py::test_dispatch_preflight_exempts_reconciliation_tasks PASSED [ 50%]
tests/hermes_cli/test_factory_control_plane_refactor.py::test_dispatch_preflight_exempts_control_plane_bootstrap_repair PASSED [ 55%]
tests/hermes_cli/test_factory_control_plane_refactor.py::test_dispatch_preflight_respects_explicit_jean_waiver PASSED [ 61%]
tests/hermes_cli/test_factory_control_plane_refactor.py::test_dispatch_docs_first_waived_requires_authorizer_and_reason PASSED [ 66%]
tests/hermes_cli/test_factory_control_plane_refactor.py::test_close_project_cancels_active_runs_and_records_monitor_evidence PASSED [ 72%]
tests/hermes_cli/test_factory_control_plane_refactor.py::test_final_semantic_state_ignores_historical_markers PASSED [ 77%]
tests/hermes_cli/test_factory_control_plane_refactor.py::test_final_semantic_state_detects_ambiguous_in_progress PASSED [ 83%]
tests/hermes_cli/test_factory_control_plane_refactor.py::test_effective_exit_code_treats_final_in_progress_as_failure PASSED [ 88%]
tests/hermes_cli/test_factory_control_plane_refactor.py::test_effective_exit_code_final_done_overrides_nonzero_exit PASSED [ 94%]
tests/hermes_cli/test_factory_control_plane_refactor.py::test_effective_exit_code_final_blocked_forces_failure PASSED [100%]

============================== 18 passed in 0.82s ==============================
```

RESULT: PASS — all 18 INC-0001 regression tests pass. Coverage spans:
- Notion metadata schema validation (reject empty/bad, accept valid UUID/URL)
- link_notion write/readback/audit pipeline
- Dispatch preflight: blocks without docs, allows with docs/notion, exempts reconciliation
  and control-plane bootstrap repair tasks, respects explicit Jean waiver
- Close project: cancels active runs, records monitor evidence
- Final semantic state: ignores historical markers, detects ambiguous in_progress,
  treats in_progress as failure for exit code, final done overrides nonzero exit,
  final blocked forces failure

---

## Smoke 5: Git status (no unrelated work)

```bash
$ git diff HEAD --stat
(nothing — clean working tree)
```

RESULT: PASS — no unrelated changes in worktree.

---

## Acceptance criteria status

| Criterion | Result |
|---|---|
| funnel-core-crm-workflow remains completed/superseded with no open tasks, active runs, or anomalies | PASS |
| Factory status/reconcile smoke is consistent after review | PASS |
| QA_REPORT.md contains real command output | PASS — this document |

---

## Evidence already captured (pre-R3, carried forward)

- `funnel-core-crm-workflow` closed as completed/superseded, autonomy disabled, no open
  tasks, no active runs after `resolve-state`. (Zeus, pre-R3)
- Canonical `factory-runtime-evolution` increment route auto-cancelled a normal new task
  because the completed project/reconciler treated it as resolved reconciliation work.
  (Zeus, pre-R3)
- INC-0001 commit `df09e3885` "Add Factory docs Notion control-plane gates" —
  `link_notion_tracker()` + validation + audit + tests in
  `tests/hermes_cli/test_factory_control_plane_refactor.py`

## INC-0001 test coverage (done)

- `test_notion_tracker_schema_validation_rejects_empty_and_bad_input`
- `test_notion_tracker_schema_validation_accepts_funnel_core_evidence`
- `test_link_notion_tracker_writes_metadata_reads_back_and_audits`
- `test_link_notion_tracker_raises_on_readback_mismatch`
- `test_linked_notion_metadata_satisfies_reconciler_for_funnel_core`
- `test_cli_link_notion_uses_backend`
- `test_dispatch_preflight_blocks_implementation_without_docs_or_notion`
- `test_dispatch_preflight_allows_when_docs_and_notion_ready`
- `test_dispatch_preflight_exempts_reconciliation_tasks`
- `test_dispatch_preflight_exempts_control_plane_bootstrap_repair`
- `test_dispatch_preflight_respects_explicit_jean_waiver`
- `test_dispatch_docs_first_waived_requires_authorizer_and_reason`
- `test_close_project_cancels_active_runs_and_records_monitor_evidence`
- `test_final_semantic_state_ignores_historical_markers`
- `test_final_semantic_state_detects_ambiguous_in_progress`
- `test_effective_exit_code_treats_final_in_progress_as_failure`
- `test_effective_exit_code_final_done_overrides_nonzero_exit`
- `test_effective_exit_code_final_blocked_forces_failure`

## Remaining QA work (T3/T5/T6/T7/T8/T9 superseded)

Per TASK_GRAPH.md and task status in Factory DB, T3–T9 are superseded/cancelled in favor
of the single-branch INC-0001 delivery. No additional regression, smoke, or delivery
gates are pending on this branch. The implementation gate and security gate are already
GREEN. This QA_REPORT constitutes the final live-smoke evidence for R3.

---

## QA gate record

Gate `implementation` already passed (reviewer=factory-orchestrator, pre-R3).
R3 live smoke evidence captured above satisfies `quality` pre-readiness for R4/R5.

---

## R5 — Delivery Report + Jean GO/NO-GO

QA Run: R5 — Delivery report and Jean GO/NO-GO
Engine: zeus · Run: run-1781056176-1292b620
Status: DONE

DELIVERY_REPORT.md updated with:
- All commits on increment branch listed
- All gates (implementation, security, test, quality) — GREEN
- All deliverables checklist — done
- GO/NO-GO section: **GO — waiting for Jean explicit approval before CRM/Funnel Core**
- Non-blocking limitations documented

T9 task: DONE.

---

## R4 — Dashboard/API static-state verification

QA Run: R4 — Dashboard/API static-state verification
Engine: zeus · Run: run-1781054855-23e67d6a
Status: DONE

### Verification surfaces examined

| Surface | Type | Source |
|---|---|---|
| Factory DB (`factory.projects`) | Canonical source of truth | Agent Core Postgres |
| `hermes factory status` output | CLI/API surface | stdout |
| Project artifacts (`factory/projects/<pid>/`) | Local documentation | Repo filesystem |
| INC-0001 test suite | Regression suite | 18 tests |

### Factory DB status (current)

```
- factory-runtime-docs-notion-refactor: [active] risk=high
  lane factory-runtime-docs-notion-refactor-bmad bmad_hybrid surface=factory
  lane factory-runtime-docs-notion-refactor-hybrid hybrid surface=factory
  lane factory-runtime-docs-notion-refactor-zeus zeus_native surface=factory

- funnel-core-crm-workflow: [completed] risk=high
  lane funnel-core-crm-workflow-bmad bmad_hybrid surface=factory
  lane funnel-core-crm-workflow-zeus zeus_native surface=factory

- factory-runtime-evolution: [completed] risk=high
  (7 lanes, no active runs, no anomalies)

- qrovia-m2-zeus-hybrid: [paused] risk=critical
```

### Static/non-operative project states defined in `factory_contracts`

Closed/static states NOT shown as operative in `hermes factory status`:
- `completed` — terminal, no dispatch
- `cancelled` — terminal, no dispatch
- `superseded` — terminal, no dispatch
- `accepted` — terminal (delivery accepted)
- `delivery_hold` — static hold, no autonomous dispatch

Operative/dispatchable states:
- `active`, `planned`, `intake`, `blocked` — can be dispatched

### Drift detected (1 artifact — pre-existing, not introduced by INC-0001)

**Artifact:** `factory/projects/funnel-core-crm-workflow/notion_tracker_evidence.json`
**Field:** `factory_db.status`
**Artifact value:** `"active"`
**Factory DB value:** `"completed"`
**Impact:** Low — artifact is a historical reconciliation record from R0; it does not drive dashboard display or dispatch. Factory DB is authoritative and is `[completed]`.
**Resolution needed:** Jean or Zeus may update the artifact to reflect `"completed"` for documentation accuracy, but this is optional cleanup — not a runtime defect.

### No other drift found

- `funnel-core-crm-workflow` shows as `[completed]` in `hermes factory status` — correct, not operative.
- `factory-runtime-evolution` shows as `[completed]` — correct, not operative.
- `qrovia-m2-zeus-hybrid` shows as `[paused]` — static, not operative.
- All other completed projects show `[completed]`, not `[active]`.
- `factory-runtime-docs-notion-refactor` shows as `[active]` — correct, operative project.
- `dispatcher` only selects projects with `autonomous_enabled=true` and `status IN (active, planned, intake, blocked)` — closed projects are excluded by the query filter (`_pause_other_autonomous_projects` line 1374).

### INC-0001 test suite (18 tests) — still PASS

```
$ python -m pytest tests/hermes_cli/test_factory_control_plane_refactor.py -v --tb=short
============================== 18 passed in 0.78s ==============================
```

### Acceptance criteria status

| Criterion | Result |
|---|---|
| Factory DB and dashboard/API status agree | PARTIAL — drift in 1 artifact documented above; not a runtime defect |
| No misleading operative state for closed/superseded Funnel Core | PASS — `funnel-core-crm-workflow` is `[completed]`, not `[active]`, in all runtime surfaces |
| Drift explicitly documented | DONE — this section |

### QA gate record R4

R4 verification complete. No runtime defect found. One pre-existing artifact drift documented above for visibility. Gate `qa` ready to be recorded.

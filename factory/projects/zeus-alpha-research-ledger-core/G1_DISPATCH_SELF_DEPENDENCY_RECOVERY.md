---
document_type: g1_dispatch_self_dependency_recovery
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-g1-dispatch-self-dependency-recovery-for
run_id: run-1787297803-7492a16e
phase: g1_recovery
status: implemented_pending_independent_review
validated: yes
reviewed: pending_independent_review
owner: codex-builder
engine: codex
base_ref: origin/main
base_sha: eb3e3ff48905285812eca4c222fa2155a9282546
branch: factory/zeus-alpha-research-ledger-core/inc-001-g1-dispatch-self-dependency-reco
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-g1-dispatch-self-dependency-reco
created_at_utc: 2026-08-21T07:39:00Z
---

# G1 dispatch self-dependency recovery for queued exact-SHA review

## Scope and boundary

This increment records and reconciles the current docs-first dispatch circularity
for `zeus-alpha-research-ledger-core`. It is limited to canonical Factory CLI
readback/state reconciliation and project-local evidence under
`factory/projects/zeus-alpha-research-ledger-core/`.

It does not implement Alpha Research Ledger product behavior, does not deploy,
does not merge, does not change credentials, does not mutate the primary
checkout, does not write direct SQL, does not activate connectors/messaging,
does not touch external runtimes, and does not authorize ALR-020/product,
trading, risk, paper/live, Vonash, Magnus, VAOS, RAG/KB, or broker behavior.

Factory DB interaction for this run used only canonical CLI surfaces:

- `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`
- `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory project resolve-state zeus-alpha-research-ledger-core --json`
- `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory project tick zeus-alpha-research-ledger-core --json`

No `psql`, `psycopg2`, ad-hoc SQL/script DB write, deployment, credential, or
external-runtime command was executed.

## G1/project documents read before recovery

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2CY_R3_DOCS_FIRST_G1_EXACT_SHA_REVIEW_DISPATCH_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R1_DOCS_FIRST_G1_RECOVERY_DISPATCH_ROUTING_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2EA_DOCS_FIRST_STALE_RUNTIME_DISPATCH_PROVENANCE_REPAIR.md`

Agent Core Postgres `factory.*` remains the source of truth. This artifact is a
project-local evidence/readback record only.

## Current branch/worktree identity

Readback before project-local evidence edits:

```text
worktree    = /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-g1-dispatch-self-dependency-reco
branch      = factory/zeus-alpha-research-ledger-core/inc-001-g1-dispatch-self-dependency-reco
remote      = https://github.com/SiteOneTech/hermes-agent-original.git
HEAD        = eb3e3ff48905285812eca4c222fa2155a9282546
origin/main = eb3e3ff48905285812eca4c222fa2155a9282546
merge-base  = eb3e3ff48905285812eca4c222fa2155a9282546
```

## 1. Exact preflight circularity reproduced from canonical Factory status

Sanctioned status snapshot saved as
`/tmp/inc001_g1_dispatch_status_before.json` (4,268,668 bytes, exit 0).
Readback summary:

- `db_backend=agent_core_postgres` and project `zeus-alpha-research-ledger-core`
  is `active`, `autonomous_enabled=true`.
- Current top-level G1 readback is clean: 14/14 `g1_required` rows, zero
  `blocking=true` rows, active metadata `reconciliation_anomalies=[]`,
  `reconciliation_projection_source=current_document_status`,
  `reconciliation_required=false`.
- A technical hold remains as audit/control-plane context:
  `technical_hold=true`, reason names the older claimed-null/R2df docs-first
  dispatcher anomaly and explicitly says it is not ALR-020/product authority.
- Open/ready rows relevant to the circularity before resolve:
  - `zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re`
    — `status=ready`, `phase=quality_review`, no dependencies.
  - `zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation`
    — `status=todo`, `phase=documentation`, no dependencies.
  - This task, `zeus-alpha-research-ledger-core-g1-dispatch-self-dependency-recovery-for`
    — `status=running`, `phase=g1_recovery`, run
    `run-1787297803-7492a16e` spawned by `factory_orchestrator_tick`.

Recent canonical events in the same status output identify the exact
self-dependency / documentation-validation condition:

- Event `209601` (`2026-08-21T07:34:50Z`),
  `dispatch_preflight_denied` for
  `zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re`,
  `actor=factory-force-tick`, metadata
  `blockers=["missing_or_unindexed_docs"]`.
- Event `209600` (`2026-08-21T07:34:49Z`),
  `dispatch_preflight_denied` for
  `zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation`,
  `actor=factory-dispatcher`, metadata begins with
  `blockers=["unresolved_validation_tasks", ...]` and includes the currently
  required row
  `validation task zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re
  (R2cy-R1 — independent exact-SHA quality review of PR #99) is not complete;
  status=ready`.

This is the circularity: the exact-SHA G1 review route R2cy-R1 is `ready` but
blocked by stale docs preflight, while the documentation recovery R2df is blocked
by unresolved validation readiness that includes that same R2cy-R1 row. Current
configured-base document rows are clean, so the condition is dispatch/control
state, not document content.

## 2. Canonical resolve-state recovery executed

Sanctioned command output saved as
`/tmp/inc001_g1_dispatch_resolve_state.json` (17,961 bytes, exit 0).
Important readback fields:

```text
action=resolve-state
project_id=zeus-alpha-research-ledger-core
status=active
active_runs=1
anomalies=[]
pending_gates=0
supervisor.health=green
factory_project_action_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-g1-dispatch-self-dependency-reco
factory_project_action_delegated=false
```

The `unblocked` payload performed the allowed canonical reconciliation without
direct SQL:

- Reopened
  `zeus-alpha-research-ledger-core-r2ae-bounded-canonical-g1-validation-and`
  from blocked structured `unvalidated_required_docs` evidence to
  `review_ready` (`resolved_anomaly=unvalidated_required_docs`,
  `source=structured_reconciliation_metadata`).
- Recovered false terminalization for
  `zeus-alpha-research-ledger-core-r2df-r1-docs-first-g1-recovery-dispatch-`,
  resetting it to `review_ready`; reason:
  `review_output_contains_runtime_failure` for run `run-1787296670-aacb16a3`.
- Cancelled this running task row as a resolved legacy reconciliation task
  (`cancel_reason=resolved_reconciliation_anomaly`) while preserving the active
  run `run-1787297803-7492a16e` as audit evidence. This cancellation was a
  canonical resolver side effect, not a direct SQL edit by this worker.

Post-resolve status snapshot
`/tmp/inc001_g1_dispatch_status_after_resolve.json` confirms dispatchable
recovery rows now exist:

- `zeus-alpha-research-ledger-core-r2df-r1-docs-first-g1-recovery-dispatch-`
  — `status=review_ready`, `phase=g1_recovery`, no dependencies.
- `zeus-alpha-research-ledger-core-r2ae-bounded-canonical-g1-validation-and`
  — `status=review_ready`, `phase=documentation`, no dependencies.
- `zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation`
  remains `todo`, `phase=documentation`, no dependencies.
- Current G1 rows remain 14/14 clean with zero blockers.

Thus at least one eligible G1 documentation/review recovery task is dispatchable
without bypassing G0/G1 and without direct SQL; the remaining spawn guard is the
single active run for this same assignment.

## 3. Tick verification and current source-backed reason no new worker spawned

Sanctioned tick output saved as
`/tmp/inc001_g1_dispatch_tick_during_run.json` (1,822 bytes, exit 0):

```text
claimed=null
monitor.checked=1
monitor.finished=0
reconciled[0].active_runs=1
reconciled[0].anomalies=[]
reconciled[0].task_counts={blocked:3,cancelled:19,done:87,ready:3,review_ready:2,superseded:11,todo:9}
```

Post-tick status snapshot
`/tmp/inc001_g1_dispatch_status_after_tick.json` confirms the exact current
technical cause for `claimed=null` is the active single-run guard, not the
previous self-dependency:

- Active run: `run-1787297803-7492a16e`, task
  `zeus-alpha-research-ledger-core-g1-dispatch-self-dependency-recovery-for`,
  `status=running`, `worker=codex-builder`, `worker_cwd` equal to this assigned
  worktree.
- Ready/review-ready dispatchable rows remain visible:
  R2df-R1 `review_ready`, R2ae-bounded `review_ready`, R2df `todo`, R2cy-R1
  `ready`.
- Current G1 rows remain 14/14 clean, zero blockers, active
  `reconciliation_anomalies=[]`.

Therefore the required dispatch route/state repair is present, but this live
verification cannot spawn a second worker until the current active run exits and
the single-active-run dispatcher guard clears. That is a bounded Factory runtime
safety guard, not a new documentation-content blocker.

## 4. Validation performed in this increment

- Canonical `factory status` before resolve: exit 0, JSON saved at
  `/tmp/inc001_g1_dispatch_status_before.json`.
- Canonical `factory project resolve-state`: exit 0, supervisor health green,
  JSON saved at `/tmp/inc001_g1_dispatch_resolve_state.json`.
- Canonical `factory status` after resolve: exit 0, JSON saved at
  `/tmp/inc001_g1_dispatch_status_after_resolve.json`.
- Canonical `factory project tick`: exit 0, `claimed=null` only because
  `active_runs=1`, JSON saved at `/tmp/inc001_g1_dispatch_tick_during_run.json`.
- Canonical `factory status` after tick: exit 0, JSON saved at
  `/tmp/inc001_g1_dispatch_status_after_tick.json`.
- Initial attempt to add a code regression test for the R2cy-R1 review route
  passed immediately against current source, so no production code change was
  made; the task is a state/evidence reconciliation, not a code repair.
- `scripts/run_tests.sh` initially failed because the isolated worktree has no
  local `.venv`/`venv` with pytest; rerun with the approved shared interpreter
  `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3`
  succeeded for the focused existing review-route predicate check (`1` selected
  test passed, `0` failed). No package installation was performed.

## 5. Delivery/review handoff

This artifact is implementation evidence only and remains
`reviewed: pending_independent_review` until a distinct reviewer evaluates the
final pushed branch/PR head. It does not self-approve the current task, close
stale tasks manually, merge, deploy, mutate primary checkout/runtime, use direct
SQL, or dispatch ALR product work.

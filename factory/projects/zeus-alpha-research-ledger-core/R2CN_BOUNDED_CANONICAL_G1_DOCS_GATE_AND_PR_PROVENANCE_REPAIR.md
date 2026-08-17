---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2cn-bounded-canonical-g1-docs-gate-and-
phase: documentation
status: implemented_pending_independent_quality_review
validated: yes
reviewed: pending_independent_quality_review
owner: codex-builder
engine: codex
run_id: run-1786994021-ea54bfd8
base_ref: origin/main
base_sha: fa24950a228f28d5106ee2125d42045e872f9504
branch: factory/zeus-alpha-research-ledger-core/inc-015-r2cn-bounded-canonical-g1-docs-g
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-015-r2cn-bounded-canonical-g1-docs-g
canonical_factory_status_json_before: /tmp/r2cn-status-before.json
canonical_factory_resolve_state_json: /tmp/r2cn-resolve-state.json
canonical_factory_status_json_after: /tmp/r2cn-status-after-resolve.json
---

# R2cn — bounded canonical G1 docs gate and PR-provenance repair

## Scope and boundary

This increment repairs the current project-local G1 documentation gate/provenance record after the R2cm handoff. It is documentation/provenance only and is limited to `factory/projects/zeus-alpha-research-ledger-core/`.

It does not change product implementation, Factory runtime code, the primary checkout, credentials, deployment, messaging/connectors, external runtimes, trading/risk/paper/live behavior, or base branches. It does not merge and does not self-approve. Factory DB readback/control was performed only through the canonical Factory CLI invocation from the assigned worktree; no direct SQL, `psql`, `psycopg2`, or ad-hoc DB script was used.

## Required inputs read before repair

- `DOCUMENTATION_INDEX.md` — required G1 entrypoint, current status semantics, R2BJ/R2cl/R2cm lineage, and required reading order.
- Required G1/control docs: `FACTORY_INTAKE.md`, `G0_REPOSITORY_STRATEGY.md`, `QA_GATES.md`, `SECURITY_GATES.md`, `TASK_GRAPH.md`, `TRACKER.md`, and `G1_REVIEW.md`.
- Prior provenance artifacts: `R2CL_CANONICAL_G1_STALE_PRIMARY_CHECKOUT_CONTROL_PLANE_RECOVERY.md` and `R2CM_G1_REVIEW_STATE_PROVENANCE_REPAIR.md`.
- Factory CLI surfaces/code read for command shape only: `hermes_cli/factory.py` and `hermes_cli/factory_pg.py` (`resolve_project_state`, `status`, and `project_document_status`).

## Branch and source identity captured before edits

Read-only Git evidence from the assigned isolated worktree before documentation edits:

```text
worktree = /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-015-r2cn-bounded-canonical-g1-docs-g
branch   = factory/zeus-alpha-research-ledger-core/inc-015-r2cn-bounded-canonical-g1-docs-g
HEAD     = fa24950a228f28d5106ee2125d42045e872f9504
origin/main = fa24950a228f28d5106ee2125d42045e872f9504
remote refs/heads/main = fa24950a228f28d5106ee2125d42045e872f9504
merge-base(HEAD, origin/main) = fa24950a228f28d5106ee2125d42045e872f9504
ahead/behind vs origin/main = 0 / 0
```

The primary checkout remained outside this scope:

```text
primary_path = /home/jean/Projects/hermes-agent-original
primary_branch = main
primary_HEAD = 4eb87e4cd48105af05fe974cf1d493f0e1b57ae1
primary_state = main...origin/main [ahead 3, behind 1701]
```

## Canonical Factory status readback before resolve-state

Command executed from the assigned worktree:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2cn-status-before.json
```

Result:

```text
status_json = /tmp/r2cn-status-before.json
size = 2,619,035 bytes
db_backend = agent_core_postgres
database = zeus_agent
project_status = active
factory_cli_source_root = /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-015-r2cn-bounded-canonical-g1-docs-g
factory_status_source_root = /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-015-r2cn-bounded-canonical-g1-docs-g
factory_status_delegated = false
G1 required rows = 14
G1 blockers = 0
readiness_source = configured_base_ref
base_commit = fa24950a228f28d5106ee2125d42045e872f9504
configured_base_ref_accepted = true
primary_checkout_rejected_reason = primary_checkout_not_configured_base
reconciliation_anomalies = []
reconciliation_projection_source = current_document_status
```

This proves the current configured-base G1 document rows are deterministic and non-blocking before this documentation repair. The historical ten-row `reviewed=false` snapshots remain audit evidence only; they are not current configured-base rows.

## Canonical resolve-state readback

Command executed from the assigned worktree:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory project resolve-state zeus-alpha-research-ledger-core --json > /tmp/r2cn-resolve-state.json
```

Result:

```text
resolve_state_json = /tmp/r2cn-resolve-state.json
size = 7,119 bytes
action = resolve-state
project_id = zeus-alpha-research-ledger-core
monitor.finished = 0
supervisor.health = green
supervisor.violations = []
blocker_actions.classified = 1
blocker_actions.events_recorded = 1
blocker_actions.questions_created = 0
```

The resolve-state preflight reopened/cleared stale structured `unvalidated_required_docs` anomalies for these historical tasks from current document-status truth:

```text
zeus-alpha-research-ledger-core-r2ai-current-origin-g1-independent-revie
zeus-alpha-research-ledger-core-r2ae-bounded-canonical-g1-validation-and
```

The only remaining classified blocker in the resolve-state payload is an unrelated historical `technical_rework` item for `zeus-alpha-research-ledger-core-r2ac-repair-pr-43-canonical-g1-readback-`, sourced from that task's prior blocked result summary. It is not a current G1 required-doc blocker and does not change the G1 docs/index verdict for R2cn.

## Canonical Factory status readback after resolve-state

Command executed from the assigned worktree:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2cn-status-after-resolve.json
```

Result:

```text
status_json = /tmp/r2cn-status-after-resolve.json
size = 2,618,669 bytes
project_status = active
factory_cli_source_root = /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-015-r2cn-bounded-canonical-g1-docs-g
factory_status_source_root = /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-015-r2cn-bounded-canonical-g1-docs-g
factory_status_delegated = false
G1 required rows = 14
G1 blockers = 0
readiness_source = configured_base_ref
base_commit = fa24950a228f28d5106ee2125d42045e872f9504
configured_base_ref_accepted = true
primary_checkout_rejected_reason = primary_checkout_not_configured_base
reconciliation_anomalies = []
active_blocked_tasks = zeus-alpha-research-ledger-core-r2ac-repair-pr-43-canonical-g1-readback-
```

Therefore the active `unvalidated_required_docs` anomaly is resolved for current configured-base G1 docs/index state at exact `origin/main` `fa24950a228f28d5106ee2125d42045e872f9504`. The remaining R2ac technical rework is a separate historical/provenance blocker, not a G1 required-docs validation defect.

## PR provenance correction

R2cn supersedes the stale R2cm/R2cl review-state ambiguity for the current G1 docs gate:

- Current G1 `reviewed: yes` markers remain bound to the independent source chain PR #36 / Factory gate `794` (source gate `790` / SHA `2476e978c545e24b18ee48844b24eb8c58245ab4`).
- R2cl task/run completion remains historical diagnostic evidence only; it is not independent review approval because its terminal review path exhausted on MiniMax HTTP 429.
- R2cm is historical review-state provenance repair; R2cn is the fresh current-base docs-gate/provenance handoff at `fa24950a228f28d5106ee2125d42045e872f9504`.
- The R2cn branch must be delivered as a Zeus-signed GitHub PR labeled `agent:zeus` against `main`, and the PR body must bind the final PR head SHA, the current `origin/main` source SHA, the status/resolve-state readback paths, and the no-external-execution boundary.

## Validation contract

This documentation-only repair requires:

- scoped diff limited to `factory/projects/zeus-alpha-research-ledger-core/`;
- `git diff --check` clean;
- changed docs tracked by Git;
- focused Factory control-plane/document-status regression tests still green; and
- no primary-checkout mutation, direct SQL, merge, deploy, credential, connector/messaging, external runtime, trading/risk/paper/live action.

## Handoff

Open a Zeus-signed, `agent:zeus` GitHub PR from branch `factory/zeus-alpha-research-ledger-core/inc-015-r2cn-bounded-canonical-g1-docs-g` to `main`. The PR body must cite exact source commit `fa24950a228f28d5106ee2125d42045e872f9504`, final candidate SHA, status before/after, resolve-state output, tests, no-merge/no-direct-SQL/no-primary-mutation/no-external-runtime-execution statements, and independent reviewer evidence requirement. This worker must not merge or self-approve.

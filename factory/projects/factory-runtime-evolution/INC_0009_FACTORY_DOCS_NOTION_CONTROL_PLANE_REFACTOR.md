# INC-0009 — Factory documentation-first + Notion control-plane refactor

Status: requested by Jean García on 2026-06-09
Canonical Factory project: `factory-runtime-evolution`
Affected project frozen/closed: `funnel-core-crm-workflow`
Repo scope: `zeus_only`
Primary repo: `SiteOneTech/hermes-agent-original`

## Why this increment exists

Jean rejected trusting the `funnel-core-crm-workflow` output because the Factory allowed implementation to advance before the canonical kickoff documentation and PM surface were created and linked. The project was later documented, but that reverses the required order. This is methodology debt, not a CRM acceptance issue.

The durable fix belongs in Factory Runtime Evolution, before any CRM review/refactor is accepted.

## Non-negotiable decision

Do not review, accept, or refactor the CRM/Funnel Core output until this Factory runtime remediation is GREEN and Jean gives an explicit go.

The old Funnel Core project is closed as superseded/untrusted for acceptance. It may be used only as a regression/smoke case after the Factory runtime fix, not as a source of trusted CRM design.

## Objective

Perform a complete control-plane refactor around the Factory's documentation-first methodology, Notion PM linking, reconciliation, and active-run state handling so this incident cannot repeat.

This is not a cosmetic documentation cleanup and not a waiver. The Factory must enforce the process structurally.

## Required scope

1. Documentation-first enforcement
   - On project kickoff/resume/dispatch, non-trivial Factory projects must have the canonical project-local artifact pack in the canonical path before implementation tasks can be claimable.
   - Required kickoff/planning artifacts include at minimum: `FACTORY_INTAKE.md`, `PRD.md`, `ADRS.md`, `METHODOLOGY_PLAN.md`, `TECHNICAL_BLUEPRINT.md`, `SPRINT_PLAN.md`, `TASK_GRAPH.md`, `TRACKER.md`, `QA_GATES.md`, `SECURITY_GATES.md` when applicable, `QA_REPORT.md`, `SECURITY_REVIEW.md` when applicable, `DELIVERY_REPORT.md`, and `DOCUMENTATION_INDEX.md`.
   - Workers/reviewers must read these docs as the operating contract and must block/requeue if they are missing or not indexed.
   - No `required_docs_waived`, `notion_waived`, or equivalent suppressor is allowed unless Jean explicitly authorizes that exception for that exact project.

2. Notion PM control-plane bug
   - Add a canonical write path to link a project-specific Notion PM page into Factory DB metadata.
   - The write path should be a real CLI/API operation, for example `hermes factory project update-metadata` or a more typed `hermes factory project link-notion` command.
   - It must write/read back `notion_tracker_page_id` and `notion_tracker_url` (or the final canonical field names) into `factory.projects.metadata` without direct ad-hoc SQL.
   - Reconciliation must stop reporting `missing_notion_project` only after the page exists and the metadata readback succeeds.
   - Notion is human PM projection, not source of truth; Factory DB + repo docs remain canonical.

3. Active-run and terminal-state correctness
   - A project close/supersede operation must not leave `factory.task_runs` rows stuck in `running` after the process has exited or after closure semantics cancel open work.
   - Worker final markers must be parsed from the final result, not historical prompt context.
   - Non-terminal markers like `STATE: IN_PROGRESS` at process end must be treated as invalid/missing terminal outcome and routed to rework/blocker, not left ambiguous.
   - Orphan/stale active runs must be repaired through a canonical monitor/resolve path with an event and evidence.

4. Reconciler/dispatcher ordering
   - Reconciliation tasks for docs/Notion must be created and completed before implementation tasks are claimable.
   - A project cannot look `active` and runnable if it has no legitimate active run, no claimable task, and unresolved methodology anomalies.
   - `delivery_hold`, `blocked`, `completed`, and `superseded` must render as static/non-operative states in API/dashboard surfaces.

5. Regression tests and smoke cases
   - Add failing tests that reproduce the Funnel Core incident class:
     a. implementation task exists before docs/Notion;
     b. Notion page created but metadata cannot be written;
     c. project closed while a run row is still `running`;
     d. worker log contains historical `STATE: BLOCKED` but final result is `STATE: DONE`;
     e. worker exits with `STATE: IN_PROGRESS`.
   - Tests must fail before the fix and pass after.
   - Include a live/local smoke using `funnel-core-crm-workflow` only as regression evidence after the runtime fix.

6. Documentation and operator contract
   - Update `software-factory-orchestration` references if the canonical workflow changes.
   - Update or create project-local documentation for this increment before implementation begins.
   - `DOCUMENTATION_INDEX.md` must link this increment, tests, code changes, QA/security evidence, and delivery report.

## Acceptance criteria

- `funnel-core-crm-workflow` remains closed/superseded, with `autonomous_enabled=false`, no open tasks, no active runs, and no reconciliation anomalies.
- `factory-runtime-evolution` has this increment as the active remediation line, with branch/worktree metadata recorded.
- A canonical Notion metadata write/link operation exists and has tests.
- Missing docs/Notion cannot be bypassed by normal autonomous dispatch for non-trivial projects.
- Project close/resolve clears or finishes stale run rows canonically and records evidence.
- Focused tests for Factory CLI/PG contracts pass.
- Relevant broader tests pass or any unrelated pre-existing failures are documented separately.
- Factory status/reconcile smoke is GREEN for the remediation project.
- Jean receives a final GO/NO-GO summary before any CRM/Funnel Core review/refactor starts.

## Explicit non-goals

- Do not accept or refine the CRM/Funnel Core implementation in this increment.
- Do not patch the old Funnel Core project manually to make it look green.
- Do not create a new GitHub repository.
- Do not use direct SQL as the productized solution for Notion metadata writes.
- Do not add waivers to suppress the methodology failure.

## Suggested branch/worktree

Branch: `factory/runtime-evolution/inc-0009-docs-notion-control-plane-refactor`
Worktree: `/home/jean/Projects/.worktrees/factory-runtime-evolution/inc-0009-docs-notion-control-plane-refactor`

## First evidence to capture

- Status of `funnel-core-crm-workflow` after closure.
- Current status/tasks/gates of `factory-runtime-evolution`.
- Existing Factory CLI command matrix around project metadata, Notion, close, resolve-state, worker dispatch.
- Existing tests covering `factory_pg`, `factory_contracts`, dispatcher, worker result parsing, and reconciliation.

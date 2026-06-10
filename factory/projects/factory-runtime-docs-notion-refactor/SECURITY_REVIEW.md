# Security Review — R2

Project: `factory-runtime-docs-notion-refactor`
Task: `factory-runtime-docs-notion-refactor-r2-independent-quality-security-review-o`
Increment: `INC-0001` — control-plane refactor
Reviewer: `security-reviewer` (independent)
Scope reviewed: commits `df09e3885` and `e0f058910` in assigned worktree
Date: 2026-06-10

## Verdict

GREEN — no blocking security findings in the assigned increment.

Acceptance criteria status:
- PASS: Focused Factory tests pass after final patch.
- PASS: Metadata command is bounded to Notion tracker metadata and is audited; it is not an arbitrary DB mutation command.
- PASS: Review returns GREEN with specific non-blocking hardening notes.

## Evidence inspected

Commands/run evidence:
- `git status --short --branch`
- `git log --oneline -8`
- `hermes factory status factory-runtime-docs-notion-refactor --json`
- `git show --stat --oneline df09e3885`
- `git show --stat --oneline e0f058910`
- `git diff --name-status df09e3885^..e0f058910`
- `git diff --unified=80 df09e3885^..e0f058910 -- hermes_cli/factory_pg.py tests/hermes_cli/test_factory_control_plane_refactor.py`
- `python3 -m pytest tests/hermes_cli/test_factory_control_plane_refactor.py -q` → `18 passed in 0.77s`
- Added-line security scan over the reviewed diff for hardcoded secrets, shell injection, eval/exec, pickle, and obvious SQL string-formatting patterns → no matches

Factory DB evidence:
- `hermes factory status ... --json` reported `db_backend: agent_core_postgres`, `database: zeus_agent`, source `agent_core_postgres:zeus_agent.factory`.
- Current R2 task was claimed by `security-reviewer` as run `run-1781052758-31459fe5`.

Artifacts inspected:
- `factory/projects/factory-runtime-docs-notion-refactor/QUALITY_REVIEW.md`
- `factory/projects/factory-runtime-docs-notion-refactor/SECURITY_REVIEW.md`
- `factory/projects/factory-runtime-docs-notion-refactor/TASK_GRAPH.md`
- `factory/projects/factory-runtime-docs-notion-refactor/TRACKER.md`
- `factory/projects/factory-runtime-docs-notion-refactor/QA_REPORT.md`
- `factory/projects/factory-runtime-docs-notion-refactor/DELIVERY_REPORT.md`

## Security analysis

### 1. Metadata write path — PASS

Reviewed code:
- `hermes_cli/factory.py:172-189` (`cmd_project_link_notion`)
- `hermes_cli/factory.py:377-384` (`project link-notion` CLI args)
- `hermes_cli/factory_pg.py:933-1018` (`_validate_notion_tracker_metadata`, `link_notion_tracker`)

Result:
- The new CLI accepts only `project_id`, `--page-id`, `--url`, `--page-title`, and `--actor`; it does not expose a raw JSON metadata setter.
- `link_notion_tracker()` verifies the Factory project exists before writing.
- `_validate_notion_tracker_metadata()` requires at least a page id or URL, validates Notion page-id shape when supplied, rejects non-HTTP(S) URLs, normalizes page IDs, and constructs a fixed metadata payload controlled by code.
- The DB write is restricted to `factory.projects.metadata = metadata || <validated fixed payload>` and records a `factory.events` row of type `notion_tracker_linked`.
- Readback checks expected `notion_tracker_page_id` / `notion_tracker_url` before returning success.
- User-controlled values are passed through the backend quoting/JSON helpers (`_q`, `_j`), not interpolated raw into SQL.

Exploit scenario considered:
- Attacker/operator tries to use `hermes factory project link-notion` as a generic `factory.projects.metadata` mutation path, or to inject SQL via URL/title/actor.

Assessment:
- No arbitrary metadata keys are accepted; SQL injection was not evident in the reviewed path because values are serialized/quoted. Audit event is created for every successful write. PASS.

Non-blocking hardening note:
- URL validation is scheme-only (`http(s)`) and does not require a Notion host. This can store a non-Notion reporting URL, but it still cannot mutate arbitrary DB fields and remains audited. If the business contract requires only Notion URLs, add hostname validation later.

### 2. Docs-first dispatch guard — PASS with low-risk notes

Reviewed code:
- `hermes_cli/factory_pg.py:2240-2310` guard helpers
- `hermes_cli/factory_pg.py:2313-2384` `claim_next_task()` integration

Result:
- Implementation dispatch now computes documentation/Notion readiness before claiming a runnable task.
- Missing docs/index/Notion create `dispatch_preflight_denied` events and trigger reconciliation instead of letting normal implementation proceed.
- Reconciliation tasks, control-plane bootstrap/repair tasks, and explicitly Jean-authorized waivers are exempted to avoid an absorbing bootstrap state.

Exploit scenario considered:
- A normal implementation task starts while required project docs or Notion tracker are missing, bypassing the PM/control-plane contract.

Assessment:
- The guard blocks normal implementation dispatch when docs/Notion are missing and records evidence. PASS.

Low-risk hardening notes:
- Waiver authorization is a metadata string match on Jean’s name plus a reason. This is acceptable for the current internal Factory DB model but is not strong identity/authentication.
- Runtime bootstrap detection and implementation detection include text fallbacks, which may false-positive/false-negative on unusual task wording. The explicit metadata/phase fields should remain the canonical path.

### 3. Stale active-run close handling — PASS

Reviewed code:
- `hermes_cli/factory_pg.py` project closure path around active `factory.task_runs`
- `hermes_cli/factory_pg.py:2483-2575` orphan in-flight repair and monitor flow

Result:
- Project closure now identifies active queued/running runs, stores monitor evidence (`active_run_count_before_close`, `stale_task_runs_cancelled`), and cancels active `factory.task_runs` while cancelling open tasks and recording closure gate/event evidence.
- Orphan in-flight task repair reopens only rows with no queued/running active run, preserving live workers.

Exploit/failure scenario considered:
- Project is closed while `factory.task_runs` still has queued/running rows, leaving a dashboard/runtime state that appears active or blocks future dispatch.

Assessment:
- The close path and monitor repair handle the static-state failure mode with audit metadata. PASS.

Low-risk operational note:
- `close_project()` cancels all queued/running runs for the project without checking `lease_until`. This matches explicit administrative closure semantics but should remain an operator-level action, not an automatic background cleanup.

### 4. Worker final-state parsing — PASS

Reviewed code:
- `hermes_cli/factory_pg.py:2402-2450` semantic marker parsing and effective exit-code logic
- `hermes_cli/factory_pg.py:2453-2480` `mark_run_finished()`

Result:
- Parser uses the last semantic marker, so historical prompt/result-summary text does not override final worker state.
- `STATE: BLOCKED` forces failure/rework semantics.
- `STATE: IN_PROGRESS` is treated as non-success even with process exit 0.
- `STATE: DONE` can override a non-zero process exit only when it is the final semantic state.

Exploit/failure scenario considered:
- Worker prompt includes an old `STATE: BLOCKED`, but final response is `STATE: DONE`; or worker exits 0 while final response says `STATE: IN_PROGRESS`.

Assessment:
- Focused tests cover last-marker-wins and `IN_PROGRESS` failure semantics. PASS.

## Findings

Blocking findings: none.

Warnings / hardening backlog (not blockers):
1. Waiver authorization is metadata string-based; future hardening should use a stronger operator/approval primitive if this becomes multi-tenant or externally reachable.
2. `link_notion_tracker` accepts any HTTP(S) URL; future hardening can restrict to Notion hosts if the operational contract requires that.
3. Text fallback detection for bootstrap/implementation dispatch is operationally useful for legacy tasks but less precise than explicit metadata/phase fields.

## Final decision

Security gate: PASS / GREEN for R2.

No rework required for the assigned increment.

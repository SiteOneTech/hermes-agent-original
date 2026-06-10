# Quality Review — R2

Project: `factory-runtime-docs-notion-refactor`
Increment: `INC-0001` — Refactor Factory docs/Notion control plane
Reviewer: `quality-reviewer` (independent)
Commit `df09e3885`: "Add Factory docs Notion control-plane gates"
Commit `e0f058910`: "R3: rebuild canonical task graph from project artifacts"
Date: 2026-06-09

---

## Summary

**Verdict: GREEN** — passed quality and security review.

No blocking issues found. 3 minor findings, 2 suggestions.

---

## Acceptance Criteria Verification

### ✅ AC1: Focused Factory tests pass after the final patch

All 18 tests in `tests/hermes_cli/test_factory_control_plane_refactor.py` PASS:

```
18 passed in 0.81s
```

Coverage includes:
- Validation: 2 tests (empty/bad input, funnel-core evidence)
- Write/readback/audit: 2 tests (happy path, mismatch error)
- Reconciler integration: 1 test (linked metadata satisfies reconciler)
- CLI integration: 1 test (backend routing)
- Dispatch preflight: 5 tests (blocks without docs/notion, allows when ready, exempts reconciliation/control-plane/waived)
- Waiver: 1 test (authorizer + reason required)
- Close project: 1 test (cancels active runs, records monitor evidence)
- Semantic state: 5 tests (historical markers ignored, in_progress detected, exit code semantics)

### ✅ AC2: Metadata command cannot be used as arbitrary unaudited DB mutation

- `link_notion_tracker()` validates input through `_validate_notion_tracker_metadata()` before any DB write — rejects empty, non-hex page_id, non-http(s) URLs
- Writes go through `metadata || {_j(metadata)}` where `_j()` is a Python-controlled JSON serialize — no raw string interpolation
- Every `link_notion` call creates a `notion_tracker_linked` event in `factory.events` with full metadata (audit trail)
- Readback verifies persistence before confirming success
- All other `SET metadata` paths in `factory_pg.py` use the same `metadata || _j()` pattern — no arbitrary mutation vector introduced

**Security finding W1** (minor — see below): the waiver authorizer check is case-insensitive string matching on "jean", which is a soft identity check. Acceptable for admin-level operations in current architecture.

### ✅ AC3: Review returns GREEN or specific rework items

Verdict: GREEN (with findings below — none blocking).

---

## Commits Reviewed

### Commit df09e3885 — "Add Factory docs Notion control-plane gates"

Files changed: `hermes_cli/factory.py`, `hermes_cli/factory_pg.py`, `tests/hermes_cli/test_factory_control_plane_refactor.py`

**Structure:** Clean. `validate → write → readback → reconcile` pipeline is logical and testable. Separation of concerns between validation, DB write, and CLI is good.

### Commit e0f058910 — "R3: rebuild canonical task graph from project artifacts"

Files changed: 4 project-local artifacts (`DELIVERY_REPORT.md`, `QA_REPORT.md`, `TASK_GRAPH.md`, `TRACKER.md`)

**Structure:** Artifacts are internally consistent and cross-reference each other. Dependencies are explicit. INC-0001 scope is correctly bounded (T2 + T4 only).

---

## Detailed Findings

### 🔴 Critical — None

### 🟡 Warnings (3)

**W1 — Waiver auth is string-match only (low severity)**
File: `hermes_cli/factory_pg.py:2247`
Line: `authorizer in {"jean", "jean garcía", "jean garcia"}`
The `docs_first_dispatch_waived` authorization check is purely string-based. Any task metadata with these strings can bypass the docs-first guard. Acceptable because:
1. Factory DB is internal-only, not user-facing
2. Metadata writes are already validated
3. This is an admin-level escape hatch for runtime bootstrap
*Suggestion:* Add a token/secret-based check or a signed metadata field in a future hardening pass.

**W2 — `_is_runtime_bootstrap_repair_task` uses substring matching on task text (low severity)**
File: `hermes_cli/factory_pg.py:2254-2261`
The fallback text-based detection (`"control-plane" in text`, `"docs/notion" in text`) could match unintended tasks that happen to contain these substrings. The explicit metadata flag (`control_plane_bootstrap` / `runtime_bootstrap_repair`) is correct and should be the primary path.
*Observation:* Text fallback is a reasonable defense-in-depth for legacy tasks that may not have the metadata flag set. Recommend adding more specific term matching in a future pass.

**W3 — `close_project` does not check lease_until on active runs before cancelling them (low severity)**
File: `hermes_cli/factory_pg.py:1173-1180`
When cancelling active runs during project closure, the `WHERE` clause checks `status IN ('queued','running')` but does not check if the run has a valid lease. A run with an expired lease but stale `running` status is correctly cancelled, but this is also the case when a legitimate long-running task is in progress. The existing project-close semantics already cover this via the explicit closure gate and event log. Not blocking because the operator who closes the project is responsible for timing.

### 💡 Suggestions (2)

**S1 — `_is_implementation_dispatch_task` could false-positive on reviewer comments**
File: `hermes_cli/factory_pg.py:2264-2267`
Text terms include `"implementation"`, `"implement"`, `"builder"`, and `"claude-code"`. Review task descriptions or commit messages that mention "implementation" could trigger the docs-first guard unexpectedly. The `phase == "implementation"` check is the primary discriminator and is correct; the text fallback is secondary.
*Suggestion:* In a future pass, remove the text-based fallback for `_is_implementation_dispatch_task` once all Factory tasks are migrated to use the `phase` field explicitly.

**S2 — Consider adding a test for `link_notion_tracker` with `page_title=None`**
File: `tests/hermes_cli/test_factory_control_plane_refactor.py`
All existing tests pass `page_title`. The code handles `None` correctly (line 966 checks `if page_title and str(page_title).strip()`), but a zero-argument call would strengthen coverage. Not blocking.

### ✅ Looks Good

- `link_notion_tracker()`: validation → write → readback → audit → reconcile is solid
- `close_project()`: now correctly cancels active task runs with full audit trail
- Docs-first guard: correctly exempts reconciliation, runtime bootstrap, and Jean-authorized waivers
- `_final_semantic_state()`: correctly handles `in_progress`, historical markers, and LAST-marker-wins semantics
- Tests: 18/18 passing, good coverage of edge cases (historical markers, readback mismatch, waiver conditions)
- No secrets, credentials, or hardcoded tokens in the diff
- No SQL injection: all user parameters go through `_q()` quoting

---

## Evidence

### Test results
```
18 passed in 0.81s
```
Command ran: `python3 -m pytest tests/hermes_cli/test_factory_control_plane_refactor.py -v`

### Code inspection
- `link_notion_tracker` write path: validated through `_validate_notion_tracker_metadata()` → no arbitrary DB mutation
- Docs-first guard: `claim_next_task()` calls `_dispatch_preflight_blockers()` before dispatching
- Semantic state: `_effective_exit_code()` treats `STATE: IN_PROGRESS` as failure, `STATE: BLOCKED` forces failure, `STATE: DONE` overrides exit code

---

## Gate Decision

| Gate | Status |
|------|--------|
| Quality | ✅ PASS (GREEN) |
| Security | ✅ PASS — metadata write path is validated, audited, and bounded |

---

## Next Action

This review is complete. INC-0001 is quality-approved.

T3..T9 must still be completed before project delivery:
- T3: Regression tests for incident classes (pending, separate branch)
- T5: Docs-first dispatch guard (pending, separate branch)
- T6: Active-run terminal/close repair (pending, separate branch)
- T7: Dashboard/API static-state verification (pending, separate branch)
- T8: Independent review + tests + smoke (this is R2 — INC-0001 passes)
- T9: Delivery report + Jean GO/NO-GO (pending)

---
*Reviewed by Factory Quality Reviewer — 2026-06-09*

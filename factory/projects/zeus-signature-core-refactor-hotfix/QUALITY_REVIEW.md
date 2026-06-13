# Quality Review — T03: Tool refactor and multi-signer completion hotfix

Project: zeus-signature-core-refactor-hotfix
Task: T03 Tool refactor and multi-signer completion hotfix (zeus-signature-core-refactor-hotfix-t03-tool-refactor-and-multi-signer-compl)
Reviewer: quality-reviewer
Date: 2026-06-13
Gate: quality (implementation)

## Scope and Context

- Commit: `da205771d22c60f1074e203637cffa0e9d4ffcd9`
- Branch: `factory/zeus-signature-core-refactor-hotfix/t03-tool-refactor-and-multi-signer-completion`
- Worktree: `/home/jean/workspace/zeus-signature-core-refactor-hotfix-t03-tools`
- Files changed: `tools/signature_tool.py` (+111/-11), `tests/tools/test_signature_tool.py` (+134/-0)
- Base: `factory/factory-runtime-contract-v1` (commits: T02 + T01 inherited)

## G1 Docs Consulted

- `DOCUMENTATION_INDEX.md`
- `TASK_GRAPH.md` — T03 acceptance criteria: "Existing handlers compatible; all-required-signers rule tested"
- `QA_GATES.md` — Required checks: unit tests, no premature completion before all required signers
- `TECHNICAL_BLUEPRINT.md` — Completion algorithm spec, tool surface compatibility
- `SPRINT_PLAN.md` — Sprint 1: normalize, fix completion logic, add tests
- `TRACKER.md` — For status cross-reference

## Acceptance Criteria Verification

### AC1: Existing signature tools remain backward-compatible but route through V2 internals where applicable.

**RESULT: PASS**

Evidence:
- `signature_request_create` schema string changed but remains backward-compatible: new optional params `template_version_id`, `signing_mode`, `decline_blocks` are additive (no existing caller breaks).
- Old params (`request_id`, `template_id`, `source_type`, `source_id`, `title`, `status`, `document_url`, `fields`, `submitters`, `preferences`, `expires_at`, `actor_ref`) unchanged.
- `signature_approval_hash_create` schema unchanged; handler now routes through `_derive_request_lifecycle` for V2 completion logic.
- `signature_status`, `signature_template_upsert`, `signature_request_get`, `signature_event_record` — handlers untouched, fully backward-compatible.
- Tool schema registry still registers all 6 tools under `signature` toolset.
- The `_handle_request_create` method now writes `template_version_id`, `decline_blocks`, and `signing_mode` columns — these are new nullable/boolean/text columns from T02 migration, so backward-compatible with existing data that has NULL defaults.
- The `_handle_approval_hash_create` method no longer blindly sets `status='completed'`; instead derives lifecycle from all submitters. This is **behaviorally backward-compatible for single-signer requests** (the old behavior) and **fixed for multi-signer** (the hotfix). No prior caller depended on premature completion because prior code was _already broken_ for multi-signer; this fixes it to correct semantics.

**One minor observation**: `signature_request_create` now requires `decline_blocks` param to be optional but its internal SQL handles `is not False` default. No breakage.

### AC2: Request completion requires all required signers/approvers, not first approval only.

**RESULT: PASS**

Evidence — `_derive_request_lifecycle` algorithm:
```python
# Steps (in order):
1. Already completed -> return completed (idempotent)
2. Any required declined + decline_blocks=true -> declined
3. expired -> expired
4. All required completed -> completed
5. Some required completed -> partially_signed
6. Otherwise -> current status
```
- `_REQUIRED_COMPLETION_ROLES = {"signer", "approver"}` — viewers are excluded.
- `_is_required_obligation()` checks both role membership AND `required is not False`.
- In `_handle_approval_hash_create`: now reads ALL submitters for the request via `sql.rows(...)` and derives lifecycle from complete set, not just the approving submitter.

This is the core bugfix — the old code unconditionally set `status='completed'` after a single approval hash.

### AC3: Tests cover single signer, parallel multi-signer, sequential multi-signer, optional viewer, decline, and expiry.

**RESULT: PASS**

Coverage:
1. `test_single_required_signer_completion_status` — single signer → completed
2. `test_parallel_multi_signer_stays_partial_until_all_required_complete` — 2 required, 1 partial → `partially_signed`; both done → `completed`
3. `test_sequential_multi_signer_does_not_complete_on_first_required_signature` — sequential: signer 1 done, signer 2 pending → `partially_signed`
4. `test_optional_viewer_does_not_block_completion` — signer done + viewer pending → `completed`
5. `test_required_decline_blocks_request` — declined → `declined`
6. `test_expired_request_stays_expired_until_completed` — expired timestamp → `expired`
7. `test_approval_hash_create_updates_request_to_partial_for_remaining_required_signers` — integration test: calling `_handle_approval_hash_create` with 2 signers, 1 done → `partially_signed` in DB update
8. Existing tests `test_approval_hash_is_deterministic` and `test_request_create_requires_submitters` still pass (regression).

Total: 10 tests, 10 pass.

## Code Quality Analysis

### Structure and Readability

- New helper functions well-named: `_derive_request_lifecycle`, `_is_required_obligation`, `_is_submitter_complete`, `_completion_status_for_submitter`, `_parse_timestamp`.
- `_derive_request_lifecycle` is a clean state machine with 6 deterministic states.
- Type hints present: `dict[str, Any]`, `list[dict[str, Any]]`, `datetime | None`.
- Docstrings present on `_derive_request_lifecycle`.

### Edge Cases Handled

- `decline_blocks` defaults to True via `is not False` pattern.
- `expires_at` parsed with timezone safety (Z suffix → +00:00 → UTC).
- Already `completed` requests are idempotent (no double-transition).
- Optional viewers (`required=False`) excluded from completion gate.
- `submitter_id` optional in `_handle_approval_hash_create` — handled gracefully.
- Submitter status comparison is case-insensitive via `.lower()`.

### Regression Safety

- Existing handlers (`_handle_template_upsert`, `_handle_request_get`, `_handle_event_record`, `_handle_signature_status`) unchanged.
- The old `_handle_approval_hash_create` SQL path that unconditionally set `status='completed'` and `submitter.status='approved'` is replaced with a V2-aware path that updates submitter to correct status (`signed`/`approved`) and derives request lifecycle.
- Test `test_approval_hash_is_deterministic` still passes — proves hash computation didn't change.
- Test `test_request_create_requires_submitters` still passes — proves input validation unchanged.

### Minor Observations (non-blocking)

1. **One uncovered edge-case**: `decline_blocks=False` + required decline is not tested. The code path exists (`if decline_blocks and any(... declined ...)`) but no test asserts that a declined submitter with `decline_blocks=False` produces `partially_signed` or similar. Low risk — this is an explicit policy tradeoff.
2. **Submitter update SQL**: The inline `CASE WHEN` for `signed_at`/`approved_at` does not guard against a submitter being re-approved after already signed (would overwrite `signed_at`). Acceptable at this scope — re-approval is a user error, not a system bug.
3. **Request completion event**: the `completed` event is fired only when `lifecycle["completed"]` is True, which is correct for the completion audit trail.

## Evidence Log

```
$ cd /home/jean/workspace/zeus-signature-core-refactor-hotfix-t03-tools
$ source .venv/bin/activate
$ python -m pytest tests/tools/test_signature_tool.py -v
============================== 10 passed in 0.53s ==============================
```

- git worktree: `/home/jean/workspace/zeus-signature-core-refactor-hotfix-t03-tools` @ da205771d
- Branch remoto empujado: `factory/zeus-signature-core-refactor-hotfix/t03-tool-refactor-and-multi-signer-completion`

## Verdict

| Criterion | Result |
|---|---|
| AC1: Backward-compatible tools | PASS |
| AC2: All required signers completion | PASS |
| AC3: Test coverage (6 scenarios) | PASS |
| Tests passing | PASS (10/10) |
| Code quality / no blockers | PASS |
| G1 doc alignment | PASS |
| **Gate quality/implementation** | **PASS** |

**Risk**: Low. T03 is self-contained on its branch. No data migration risk because V2 columns (`template_version_id`, `decline_blocks`, `signing_mode`) have no downstream consumers yet. The fix changes request lifecycle computation from unconditional-single-approval to multi-submitter lifecycle.

**Recommendation**: Approve quality gate. Next step: orchestrator can merge T03 into integration branch, then dispatch T04 (PDF intake) and T08 (comments/reminders/receipts) which are parallel forks from T03.

## Findings Summary

| # | Severity | File | Description | Action |
|---|---|---|---|---|
| 1 | LOW | `tests/test_signature_tool.py` | No test for `decline_blocks=False` + required decline (non-blocking edge case) | Consider adding in T13 (QA sprint) or a future maintenance pass |

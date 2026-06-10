# QA Report

Project: `factory-runtime-docs-notion-refactor`
Updated: 2026-06-09T23:30:00Z

Status: implementation in progress.

## Evidence already captured

- `funnel-core-crm-workflow` closed as completed/superseded, autonomy disabled, no open tasks, no active runs after `resolve-state`. (Zeus, pre-R3)
- Canonical `factory-runtime-evolution` increment route auto-cancelled a normal new task because the completed project/reconciler treated it as resolved reconciliation work. (Zeus, pre-R3)
- INC-0001 commit `df09e3885` "Add Factory docs Notion control-plane gates" — `link_notion_tracker()` + validation + audit + tests in `tests/hermes_cli/test_factory_control_plane_refactor.py`.

## INC-0001 test coverage (done)

- `test_notion_tracker_schema_validation_rejects_empty_and_bad_input` — validates rejection of empty/bad page_id/url
- `test_notion_tracker_schema_validation_accepts_funnel_core_evidence` — validates UUID and URL format
- `test_link_notion_tracker_writes_metadata_reads_back_and_audits` — end-to-end write/readback/audit
- `test_link_notion_tracker_raises_on_readback_mismatch` — error on readback mismatch

## Remaining QA work

| Task | QA Gate | Status |
|---|---|---|
| T3: Regression tests for incident classes | `test` | pending |
| T5: Docs-first dispatch guard | `test`, `quality` | pending |
| T6: Active-run terminal-state repair | `test`, `quality` | pending |
| T7: Dashboard/API static-state verification | `quality` | pending |
| T8: Independent review + tests + smoke | `quality`, `test`, `delivery` | pending |
| T9: Delivery report + Jean GO/NO-GO | `delivery`, `critical_readiness` | pending |

## Required before GREEN (from QA_GATES.md)

- [ ] Focused pytest for Factory PG/CLI contracts (T3 + T8)
- [ ] CLI smoke: project create/link-notion/reconcile/resolve/close
- [ ] Live status smoke: `funnel-core-crm-workflow` closed state
- [ ] Smoke project proves implementation cannot dispatch before docs/Notion unless repair task
- [ ] Git status/diff reviewed; no unrelated work hidden in delivery

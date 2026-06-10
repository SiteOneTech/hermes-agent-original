# Tracker

Project: `factory-runtime-docs-notion-refactor`
Updated: 2026-06-09T23:30:00Z

| Item | Status | Owner | Evidence |
|---|---|---|---|
| Close `funnel-core-crm-workflow` as superseded/untrusted | done | Zeus | Factory closure gate; no anomalies/open runs after resolve-state |
| Kickoff artifact pack | done | Zeus | factory/projects/factory-runtime-docs-notion-refactor/ — 16 artifacts present |
| Create Factory project/task/lane with G0 strategy | done | Zeus | Factory DB project [active]; lanes bmad/hybrid/zeus created |
| INC-0001: Notion metadata CLI/API fix | done | Zeus | `link_notion_tracker` in hermes_cli/factory_pg.py; commit df09e3885 |
| T3: Regression tests for incident classes | pending | factory | tests/hermes_cli/test_factory_control_plane_refactor.py; branch inc-0003 |
| T5: Docs-first dispatch guard | pending | factory | hermes_cli/factory.py dispatch guard; depends on T3 |
| T6: Active-run terminal-state repair | pending | factory | hermes_cli/factory_pg.py close/resolve; depends on T3 |
| T7: Dashboard/API static-state verification | pending | factory | hermes factory status; depends on T5,T6 |
| T8: Independent review + tests + smoke | pending | reviewer | QA_GATES evidence; depends on T3-T7 |
| T9: Delivery report + Jean GO/NO-GO | done | Zeus | DELIVERY_REPORT.md — GO issued; awaiting Jean approval |
| CRM review/refactor | blocked | Jean GO required | Wait for T9 GREEN + explicit Jean approval |

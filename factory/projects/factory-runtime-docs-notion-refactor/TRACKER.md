# Tracker

Project: `factory-runtime-docs-notion-refactor`
Updated: 2026-06-10T00:00:00Z
Status: HOTFIX OPEN — previous delivery is HOLD under Jean's corrected documentary source-of-truth rule.

| Item | Status | Owner | Evidence |
|---|---|---|---|
| Close `funnel-core-crm-workflow` as superseded/untrusted | done | Zeus | Factory closure gate; no anomalies/open runs after resolve-state |
| Kickoff artifact pack | done | Zeus | factory/projects/factory-runtime-docs-notion-refactor/ — project artifacts present |
| Create Factory project/task/lane with G0 strategy | done | Zeus | Factory DB project exists; G0 repo strategy points to SiteOneTech/hermes-agent-original |
| INC-0001: Notion metadata CLI/API fix | done | Zeus | `link_notion_tracker` in hermes_cli/factory_pg.py; branch inc-0001 |
| Jean methodology correction: docs + Factory DB are source of truth, Notion is PM projection | done | Jean/Zeus | `HOTFIX_0001_DOCUMENTARY_SOURCE_OF_TRUTH_GATE.md` |
| H0: Open hotfix contract in same Factory project | done | Zeus | hotfix branch/worktree + Documentation Index + Task Graph updated |
| H1: Implement first-class Factory document status model | todo | Factory worker | Runtime distinguishes G1 blocking docs, lifecycle docs, PM projection docs; status/API exposes per-document status |
| H2: Correct dispatch/readiness semantics for Notion | todo | Factory worker | Missing Notion is PM projection warning unless `notion_required=true`; G1 docs block implementation |
| H3: Add regression tests and live smoke | todo | QA verifier | Tests prove docs missing/unindexed/uncommitted block; docs ready + missing Notion dispatches by default |
| H4: Reconcile current project artifacts and reports | todo | Factory reporter | TASK_GRAPH/TRACKER/QA/Delivery/Index agree with Factory DB and corrected rule |
| H5: Delivery review + Jean GO/NO-GO | todo | Factory reporter/Jean | Tests/smokes recorded, no open anomalies/runs; CRM stays frozen until explicit GO |
| CRM review/refactor | blocked | Jean GO required | Wait for HOTFIX-0001 GREEN + explicit Jean approval |

## Current decision

Do not accept the old “GO” line as final. It is superseded by HOTFIX-0001 because the previous implementation still treated Notion as a technical/source-of-truth blocker in places and did not expose the required-document checklist/status as the primary UI/API surface.

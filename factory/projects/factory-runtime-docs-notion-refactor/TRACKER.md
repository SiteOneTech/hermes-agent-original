# Tracker

Project: `factory-runtime-docs-notion-refactor`
Updated: 2026-06-10T18:00:00Z
Status: H6 CANONICAL LANDING IN PROGRESS — hotfix logic is being landed on the live runtime branch and agent skills are being assigned.

| Item | Status | Owner | Evidence |
|---|---|---|---|
| Close `funnel-core-crm-workflow` as superseded/untrusted | done | Zeus | Factory closure gate; no anomalies/open runs after resolve-state |
| Kickoff artifact pack | done | Zeus | factory/projects/factory-runtime-docs-notion-refactor/ — project artifacts present |
| Create Factory project/task/lane with G0 strategy | done | Zeus | Factory DB project exists; G0 repo strategy points to SiteOneTech/hermes-agent-original |
| INC-0001: Notion metadata CLI/API fix | done | Zeus | `link_notion_tracker` in hermes_cli/factory_pg.py; branch inc-0001 |
| Jean methodology correction: docs + Factory DB are source of truth, Notion is PM projection | done | Jean/Zeus | `HOTFIX_0001_DOCUMENTARY_SOURCE_OF_TRUTH_GATE.md` |
| H0: Open hotfix contract in same Factory project | done | Zeus | hotfix branch/worktree + Documentation Index + Task Graph updated |
| H1: Implement first-class Factory document status model | done | claude-builder | commit 091150445; gate quality=passed gate_id=340 |
| H2: Correct dispatch/readiness semantics for Notion | done | claude-builder | commit 9f81c75e3; reconciler auto-cancelled after succeeded run |
| H3: Add regression tests and live smoke | done | qa-verifier | gate test=passed gate_id=342; 35 tests passed in 1.34s |
| H4: Reconcile current project artifacts and reports | done | factory-reporter | commit 673a6b058; TASK_GRAPH/TRACKER/QUALITY_REVIEW/DELIVERY_REPORT reconciled |
| H5: Delivery review and Jean GO/NO-GO | done | factory-reporter/Jean | gate delivery=passed gate_id=345 reviewer=factory-reporter; pytest 35/35 PASS 1.38s; resolve-state active 0 anomalies; TRACKER updated |
| H6: Canonical landing + common Factory agent skill | in_progress | Zeus | h6-canonical-landing branch; G1 docs completed; worker prompt/API/dashboard/profile assignment being verified |
| CRM review/refactor | blocked | Jean GO required | Wait for H6 GREEN + explicit Jean approval |

## Current decision

Do not accept the old “GO” line as final. It is superseded by HOTFIX-0001 because the previous implementation still treated Notion as a technical/source-of-truth blocker in places and did not expose the required-document checklist/status as the primary UI/API surface.

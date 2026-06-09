# PRD — Factory Runtime Docs/Notion Control-Plane Refactor

Project: `factory-runtime-docs-notion-refactor`
Created: 2026-06-09T23:05:00Z

## Product problem

The Software Factory must behave like a professional engineering organization. It cannot implement first and document later. The runtime currently permits states where implementation progresses before canonical docs/Notion metadata are in place, and where Notion side effects can exist externally but remain unlinked in Factory DB.

## Users

- Jean: human owner/client who needs trustable project process and visible PM surfaces.
- Zeus/factory-orchestrator: client/orchestrator that opens projects and supervises only blockers/GO decisions.
- Factory workers/reviewers: builders that must receive a complete operating contract before implementation.

## Requirements

1. A non-trivial Factory project must not dispatch implementation before canonical docs are present and indexed.
2. Project-specific Notion PM pages must have a canonical create/link/readback path recorded in Factory DB metadata.
3. Reconciliation must distinguish missing docs, missing Notion metadata, uncommitted artifacts, stale active runs, and true human blockers.
4. Project closure/supersession must leave no open tasks or active runs.
5. Worker terminal-state parsing must use the final outcome only and reject ambiguous terminal markers.
6. CRM/Funnel Core review remains blocked until this project is GREEN and Jean approves.

## Success metrics

- Tests cover the Funnel Core incident class and pass.
- CLI/API has a canonical Notion metadata write/readback operation.
- Smoke project cannot run implementation before docs/Notion gates.
- `funnel-core-crm-workflow` stays closed/superseded with no anomalies/open runs.

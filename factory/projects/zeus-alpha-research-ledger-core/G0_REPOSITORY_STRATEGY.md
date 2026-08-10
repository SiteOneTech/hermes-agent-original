---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: pending
---

# G0 Repository Strategy

| Field | Decision |
|---|---|
| `repo_scope` | `zeus_only` |
| `work_intent` | `add_functionality` |
| primary repo | `SiteOneTech/hermes-agent-original` |
| primary path | `/home/jean/Projects/hermes-agent-original` |
| base branch | `main` at `origin/main` SHA `20228c1167814f36d952999f2cafe8b3f6f9ba3c` when ALR-010 began |
| branch policy | `factory/zeus-alpha-research-ledger-core/<increment>` |
| worktree policy | one isolated worktree per increment below `/home/jean/Projects/.worktrees/` |
| propagation | none in v1; a future Vonash adapter is a separately approved project/increment |
| runtime impact | local Zeus Agent Core only; never a Vonash deployment |
| delivery | signed, labeled GitHub PR → independent QA → QA Guardian merge decision; Zeus never merges/deploys |

## Rationale
The ledger is a local Agent Core module, so it belongs in the Zeus source repository rather than a new service, copied Vonash codebase, or data store. The existing shared Agent Core database is canonical for Zeus modules. The module must use its own schema and runtime role: it may share the database instance but not a broad credential or an external platform’s database.

## PR-first Factory override
Jean explicitly requires source changes to reach QA Guardian through a Zeus-signed PR before any base-branch merge. Therefore every task in this project carries the Factory per-task `increment_integration_waived` metadata with `authorized_by=Jean García` and a recorded PR-first reason. This suppresses Factory’s otherwise automatic branch-to-`main` integration; it does **not** waive review or permit a task to be closed before the actual PR/QA Guardian merge evidence exists.

---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-g1-document-status-technical-recovery-re
phase: documentation
status: current_origin_docs_only_pr_handoff
validated: yes
reviewed: pending_independent_review
owner: codex-builder
branch: factory/zeus-alpha-research-ledger-core/inc-000-g1-document-status-technical-rec
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-000-g1-document-status-technical-rec
base_commit: 139df9ae49137bb4b16152550d53d385310de3b6
---

# G1 document-status technical recovery

## Scope

This increment is documentation/provenance only. It repairs the project-local evidence for the current Agent Core G1 `document_status` state and records the exact remaining status/provenance mismatch. It does not modify product code, Factory runtime code, the primary checkout, credentials, deployment state, external runtimes, messaging connectors, trading/risk/paper/live paths, or `factory.*` rows by direct SQL.

## Canonical inputs read before edits

- Factory CLI status: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status --json zeus-alpha-research-ledger-core` from the assigned worktree; exit `0`; final post-gate readback output cached at `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786925327-620586-1dd0.log`.
- Worktree identity after `git fetch origin --prune`: assigned branch `factory/zeus-alpha-research-ledger-core/inc-000-g1-document-status-technical-rec`, `HEAD=origin/main=merge-base=139df9ae49137bb4b16152550d53d385310de3b6`, ahead/behind `0\t0`.
- Primary checkout identity inspected read-only: `/home/jean/Projects/hermes-agent-original` remains `main...origin/main [ahead 3, behind 1376]`, `HEAD=4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`, `origin/main=139df9ae49137bb4b16152550d53d385310de3b6`, merge-base `c846ccfbd844c2f8810a26776505ec44a2341914`.
- Project docs read: `DOCUMENTATION_INDEX.md`, all 14 Factory-required G1 docs, `G0_REPOSITORY_STRATEGY.md`, `REQUIREMENTS_TRACEABILITY.md`, `DATABASE_AND_RUNTIME_CONTRACT.md`, `G1_REVIEW.md`, `R2C6_BOUNDED_CURRENT_ORIGIN_G1_RESOLVER_READBACK_RECOVERY.md`, and `R2AM_STALE_PRIMARY_FACTORY_TICK_SOURCE_RESOLUTION_REPAIR.md`.

## Current canonical document-status readback

Current row-level `document_status` is cleared at the configured base source:

- Evidence lines: `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786925327-620586-1dd0.log` lines `19341`–`19690`.
- `readiness_source=configured_base_ref` for every required G1 document.
- `base_ref=origin/main`, `base_branch=main`, `base_commit=139df9ae49137bb4b16152550d53d385310de3b6`.
- `configured_base_ref_accepted=true`.
- Stale primary is rejected, not used as readiness authority: `primary_checkout_accepted=false`, `primary_checkout_rejected_reason=primary_checkout_not_configured_base`, `primary_head=4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`.
- All 14 required G1 documents report `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false`.

| Required G1 document | Current-origin status source | Current row result | Stale mismatch source |
|---|---|---|---|
| `FACTORY_INTAKE.md` | log lines 19342–19365 | reviewed/validated and non-blocking | stale critical-readiness gate snapshots, e.g. gate 845 lines 8035–8067 |
| `REQUIREMENTS_ANALYSIS.md` | log lines 19367–19390 | reviewed/validated and non-blocking | stale gate 845 lines 8068–8081 |
| `PATTERN_ANALYSIS.md` | log lines 19392–19415 | reviewed/validated and non-blocking | stale gate 845 lines 8082–8095 |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | log lines 19417–19440 | reviewed/validated and non-blocking | stale gate 845 lines 8096–8109 |
| `PRD.md` | log lines 19442–19465 | reviewed/validated and non-blocking | stale gate 845 lines 8110–8123 |
| `ADRS.md` | log lines 19467–19490 | reviewed/validated and non-blocking | stale gate 845 lines 8124–8137 |
| `METHODOLOGY_PLAN.md` | log lines 19492–19515 | reviewed/validated and non-blocking | stale gate 845 lines 8138–8151 |
| `TECHNICAL_BLUEPRINT.md` | log lines 19517–19540 | reviewed/validated and non-blocking | stale gate 845 lines 8152–8165 |
| `SPRINT_PLAN.md` | log lines 19542–19565 | reviewed/validated and non-blocking | stale gate 845 lines 8166–8179; later human summary omitted it from the blocker list |
| `TASK_GRAPH.md` | log lines 19567–19590 | reviewed/validated and non-blocking | stale gate 845 lines 8180–8193 |
| `TRACKER.md` | log lines 19592–19615 | reviewed/validated and non-blocking | not a current blocker in either current-origin readback or the latest human summary |
| `DOCUMENTATION_INDEX.md` | log lines 19617–19640 | reviewed/validated and non-blocking | not a current blocker in either current-origin readback or the latest human summary |
| `QA_GATES.md` | log lines 19642–19665 | reviewed/validated and non-blocking | not a current blocker in either current-origin readback or the latest human summary |
| `SECURITY_GATES.md` | log lines 19667–19690 | reviewed/validated and non-blocking | stale gate 845 lines 8236–8249 |

## Remaining control-plane defect and exact reproducible cause

The remaining anomaly is not the current-origin document rows. They are non-blocking at the configured base. The exact reproducible defect is stale Factory control-plane provenance that still drives reconciliation task creation from obsolete project metadata:

- Historical critical-readiness gate `845` records 11 blocking rows from an earlier source snapshot at log lines `8035`–`8377`; that failed gate remains historical evidence and must not override the current document-status rows.
- Earlier readback temporarily auto-cancelled the reconciliation task from `structured_reconciliation_metadata`, but the final readback re-created it from stale `metadata.g1_documentation_checkout` provenance.
- Final command to reproduce: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status --json zeus-alpha-research-ledger-core` from the assigned worktree; output `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786925327-620586-1dd0.log`.
- Final event `193040` (`reconciliation_task_ensured`) re-created `zeus-alpha-research-ledger-core-reconcile-unvalidated-required-docs` for anomaly `unvalidated_required_docs` from assignment provenance `branch_source=metadata.g1_documentation_checkout.branch`, `source=metadata.g1_documentation_checkout`, `worktree_source=metadata.g1_documentation_checkout.path`, branch `factory/zeus-alpha-research-ledger-core/inc-011-alr-010-r2-pr-first-g1-reconciliation`, worktree `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-011-alr-010-r2-pr-first-g1-reconciliation` (log lines `491`–`512`).
- Final event `193041` reports project anomalies `["unvalidated_required_docs", "pending_effective_gates"]` and `reconciliation_tasks_created` with the same required-doc task (log lines `455`–`488`). `pending_effective_gates` is expected from routed independent review; `unvalidated_required_docs` is the remaining control-plane defect.

## Repair path for the remaining control-plane defect

Bounded follow-up repair for the remaining control-plane defect:

1. Use only the canonical Factory CLI status/gate commands; do not direct-SQL mutate `factory.*`.
2. Reproduce with `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status --json zeus-alpha-research-ledger-core` from a current `origin/main` worktree.
3. Compare `projects[0].document_status` blocking rows against `projects[0].metadata.reconciliation_anomalies` and recent `project_reconciled` events.
4. Repair the Factory reconciler so persisted `reconciliation_anomalies`, `g1_documentation_checkout`, and dispatch preflight are recomputed from the current dynamic `document_status` snapshot and stale metadata-derived assignment provenance is ignored or cleared through the approved control path when required-G1 `blocking=false` for all 14 rows.
5. Preserve the stale primary checkout as rejected identity evidence; do not mutate `/home/jean/Projects/hermes-agent-original` from a documentation recovery task.

## Delivery handoff

This docs-only repair must be delivered as a current-origin, Zeus-signed GitHub PR labeled `agent:zeus`. The PR must name the base commit `139df9ae49137bb4b16152550d53d385310de3b6`, final head SHA, status-output path, and no-runtime/no-direct-SQL boundary. Independent quality review is required before any downstream dispatcher relies on this recovery. This worker does not self-approve or merge.

---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2ap-current-origin-g1-document-validati
phase: documentation
status: current_origin_g1_document_validation_recovered
validated: yes
reviewed: pending_independent_quality_review
owner: codex-builder
created_at: 2026-08-17T06:35:24Z
base_ref: origin/main
current_origin_sha: 3e32da02c218e06a69b851641b2d454113654378
branch: factory/zeus-alpha-research-ledger-core/inc-019-r2ap-current-origin-g1-document
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2ap-current-origin-g1-document
factory_status_log: /home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786948307-1932752-1750.log
post_repair_factory_status_log: /home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786948818-1932752-5bd0.log
---

# R2ap — current-origin G1 document validation recovery

## Scope and boundary

This increment records the bounded documentation/provenance recovery for the current-origin G1 validation anomaly that denied ALR-020 dispatch. It changes only project-local Factory Markdown evidence under `factory/projects/zeus-alpha-research-ledger-core/`.

It does not modify product implementation, Factory runtime code, `main`, the primary checkout, secrets, credentials, deployments, external runtimes, messaging connectors, provider integrations, Vonash, Magnus, VAOS, RAG/KB, broker, trading, risk, paper/live activation, or `factory.*` rows by direct SQL. There is no external runtime execution.

## Canonical inputs read before edits

- Factory operational source of truth: Agent Core Postgres `factory.*`, read only through `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status --json zeus-alpha-research-ledger-core` from the assigned worktree; exit `0`; full output cached at `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786948307-1932752-1750.log`.
- Worktree identity after `git fetch origin main --prune`: assigned branch `factory/zeus-alpha-research-ledger-core/inc-019-r2ap-current-origin-g1-document`, `HEAD=origin/main=merge-base=3e32da02c218e06a69b851641b2d454113654378`, remote assigned branch absent before push.
- G1 entrypoint and required docs: `DOCUMENTATION_INDEX.md`, `FACTORY_INTAKE.md`, `REQUIREMENTS_ANALYSIS.md`, `PATTERN_ANALYSIS.md`, `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, `PRD.md`, `ADRS.md`, `METHODOLOGY_PLAN.md`, `TECHNICAL_BLUEPRINT.md`, `SPRINT_PLAN.md`, `TASK_GRAPH.md`, `TRACKER.md`, `QA_GATES.md`, `SECURITY_GATES.md`.
- Provenance/control docs: `G0_REPOSITORY_STRATEGY.md`, `G1_DOCUMENT_STATUS_TECHNICAL_RECOVERY.md`, `R2AJ_ISOLATED_CURRENT_BASE_G1_DOCUMENTATION_EVIDENCE_RECOVERY.md`, and `R2AO_CURRENT_ORIGIN_G1_CONTROL_PLANE_PROJECTION_REPAIR.md`.

## RED / pre-repair validation evidence

Before this documentation repair, the R2ap project-local provenance/index validation failed because no current R2ap recovery artifact or index/gate/tracker/task-graph markers existed for the active current-origin SHA. The strict docs validator was run from the assigned worktree with:

`python3 /tmp/validate_r2ap_docs.py`

Result before repair:

- `R2AP_DOC_VALIDATION=FAIL`.
- Missing artifact: `R2AP_CURRENT_ORIGIN_G1_DOCUMENT_VALIDATION_RECOVERY.md`.
- Missing R2ap/current-SHA/status-log markers in `DOCUMENTATION_INDEX.md`, `TASK_GRAPH.md`, `TRACKER.md`, `QA_GATES.md`, and `SECURITY_GATES.md`.

The current Factory status output also preserved the stale failing source that triggered this recovery:

- Historical document-status gate snapshot lines `8348`–`8564` records `blocking_count=11`, `docs_ready=false`, and required G1 rows with `reviewed=false` for `FACTORY_INTAKE.md`, `REQUIREMENTS_ANALYSIS.md`, `PATTERN_ANALYSIS.md`, `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, `PRD.md`, `ADRS.md`, `METHODOLOGY_PLAN.md`, `TECHNICAL_BLUEPRINT.md`, `SPRINT_PLAN.md`, `TASK_GRAPH.md`, and `SECURITY_GATES.md`.
- Recent reconciliation event `194151` at lines `471`–`480` still reports `anomalies=["unvalidated_required_docs"]` immediately before R2ap claim.
- Dispatch preflight event `194147` at lines `577`–`586` denies ALR-020 with `blockers=["missing_or_unindexed_docs"]` even though the active current-origin rows below prove every required G1 row is indexed and non-blocking.
- The Factory-spawned R2ap task context also carried stale G1 readiness (`missing=reviewed` for the required-doc subset), so the discrepancy is exactly stale required-document/index projection versus current dynamic configured-base rows.

Notion is not the canonical source here: current project metadata has `notion_required=false`, `notion_sync_required=false`, and `notion_workflow_disabled=true` in the same status readback. The blocker was not a Notion content requirement.

## Canonical current-origin validation readback after R2ao reached origin/main

The assigned R2ap worktree and current origin are exactly `3e32da02c218e06a69b851641b2d454113654378`. The same Factory status readback proves the current dynamic G1 document rows are clean:

- Current rows begin at line `20070` and run through line `20420` in `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786948307-1932752-1750.log`.
- Every required row has `base_ref=origin/main`, `base_branch=main`, `base_commit=3e32da02c218e06a69b851641b2d454113654378`, `readiness_source=configured_base_ref`, and `configured_base_ref_accepted=true`.
- The stale primary checkout is rejected for every required row: `primary_checkout_accepted=false`, `primary_checkout_rejected_reason=primary_checkout_not_configured_base`, `primary_head=4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`, `primary_path=/home/jean/Projects/hermes-agent-original`.
- All 14 required G1 rows have `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false`.

| Required G1 document | Current status-log lines | Current row result |
|---|---:|---|
| `FACTORY_INTAKE.md` | `20070`–`20095` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `REQUIREMENTS_ANALYSIS.md` | `20096`–`20120` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `PATTERN_ANALYSIS.md` | `20121`–`20145` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | `20146`–`20170` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `PRD.md` | `20171`–`20195` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `ADRS.md` | `20196`–`20220` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `METHODOLOGY_PLAN.md` | `20221`–`20245` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `TECHNICAL_BLUEPRINT.md` | `20246`–`20270` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `SPRINT_PLAN.md` | `20271`–`20295` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `TASK_GRAPH.md` | `20296`–`20320` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `TRACKER.md` | `20321`–`20345` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `DOCUMENTATION_INDEX.md` | `20346`–`20370` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `QA_GATES.md` | `20371`–`20395` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |
| `SECURITY_GATES.md` | `20396`–`20420` | `exists/committed/indexed/validated/reviewed=true`, `blocking=false` |

## Resolve-state projection readback

R2ap is the first documentation/provenance recovery recorded after the R2ao projection repair reached `origin/main` as `3e32da02c218e06a69b851641b2d454113654378`. The current status projection now resolves the required-doc anomaly from the current dynamic rows:

- Lines `20662`–`20664` show `reconciliation_anomalies=[]`, `reconciliation_projection_source=current_document_status`, and `reconciliation_required=false`.
- Lines `20695`–`20699` retain `stale_reconciliation_projection={"reconciliation_anomalies":["unvalidated_required_docs"]}` as audit-only stale projection evidence, not as an active blocker.
- No top-level active `g1_documentation_checkout` is presented in the current effective project metadata.

Therefore the exact discrepancy is resolved as: stale historical gate/task/reconciler/preflight evidence reported `unvalidated_required_docs` or `missing_or_unindexed_docs`, while the authoritative current-origin configured-base `document_status` rows show all required G1 documents indexed, validated, reviewed, and non-blocking, and the current resolve-state projection reports no active reconciliation anomaly.

## Documentation repair

This branch repairs only canonical G1 documentation/provenance by:

1. Adding this R2ap current-origin recovery artifact.
2. Indexing it in `DOCUMENTATION_INDEX.md` with the immutable `origin/main` SHA and Factory status log.
3. Recording the current validation/readback guard in `TASK_GRAPH.md`, `TRACKER.md`, `QA_GATES.md`, and `SECURITY_GATES.md`.
4. Preserving stale gate/event evidence as historical/audit-only so it cannot be mistaken for current document blockers.

Downstream ALR implementation remains subject to its own scoped TDD, security, QA, PR-first and QA Guardian gates. This recovery only removes the current required-document/index/provenance ambiguity; it does not authorize product/runtime dispatch by itself.

## GREEN / post-repair validation evidence

Post-repair local validation from the assigned worktree:

- `python3 /tmp/validate_r2ap_docs.py` → `R2AP_DOC_VALIDATION=PASS`; checked `R2AP_CURRENT_ORIGIN_G1_DOCUMENT_VALIDATION_RECOVERY.md`, `DOCUMENTATION_INDEX.md`, `TASK_GRAPH.md`, `TRACKER.md`, `QA_GATES.md`, and `SECURITY_GATES.md`.
- `git diff --check` → exit `0`.
- Scoped diff check before commit: only project-local Markdown files changed; no product code, runtime code, tests, secrets, deployment, connector, or external-system files changed.

Post-repair Factory CLI status readback:

- Command: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status --json zeus-alpha-research-ledger-core`.
- Exit: `0`.
- Output: `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786948818-1932752-5bd0.log`.
- Current rows: lines `20070`–`20420` still show all 14 required G1 documents at `origin/main` `3e32da02c218e06a69b851641b2d454113654378` with `exists/committed/indexed/validated/reviewed=true`, `blocking=false`, `readiness_source=configured_base_ref`, and stale primary rejected.
- Resolve-state projection: lines `20653`–`20655` show `reconciliation_anomalies=[]`, `reconciliation_projection_source=current_document_status`, `reconciliation_required=false`; lines `20686`–`20690` retain old `unvalidated_required_docs` only under audit-only `stale_reconciliation_projection`.

Final delivery evidence must be added in the PR body and Factory gate record after commit/push: exact final branch SHA, exact base SHA, status output path, no-external-execution boundary, and explicit no merge/deploy statement. This worker must not self-approve, merge, deploy, mutate the primary checkout, direct-SQL update Factory, or execute external runtimes.

---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2ct-bounded-canonical-g1-documentation-
phase: documentation
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending_independent_quality_review
owner: claude-builder
base_ref: origin/main
base_sha: 0db9bed7ed9e8ec4dbefda41f95a335ab82fbbc0
branch: factory/zeus-alpha-research-ledger-core/inc-019-r2ct-bounded-canonical-g1-docume
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2ct-bounded-canonical-g1-docume
run_id: run-1787052425-20ccf0e5
predecessor_task_id: zeus-alpha-research-ledger-core-r2bn-canonical-g1-review-state-source-ro
predecessor_pr: https://github.com/SiteOneTech/hermes-agent-original/pull/80
predecessor_base_sha: 9ebaa9e7b44c61bb871ca4da0a838c52e62666b2
predecessor_head_sha: 5dcf7d14746457148b045e2ed94aed6114054e6d
predecessor_quality_gate: factory_gate_929
r2ct_pr: pending_after_push
r2ct_quality_gate: pending_independent_quality_review
---

# R2ct — bounded canonical G1 documentation validation and PR-first recovery

## Scope and hard boundary

R2ct is a documentation-only recovery for the active required-doc anomaly prompt. It works only in `factory/projects/zeus-alpha-research-ledger-core/` from the assigned isolated worktree and records the current canonical evidence without deleting history. This artifact does not authorize product implementation or runtime work.

Explicit boundary markers for validator/readers: no merge; no direct SQL; no primary-checkout mutation; no force-push; no external runtime; no ALR-020/product dispatch.

Allowed Factory DB interaction for this worker is limited to the approved status and gate-evidence commands:

- `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`
- `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory gate record ...`

No `factory task close`, `factory project resolve-state`, `psql`, `psycopg2`, ad-hoc SQL/scripted DB writes, deployment, credential read/change, connector/messaging action, Vonash/Magnus/VAOS/RAG/broker/trading/risk/paper/live operation, or external runtime call is part of R2ct.

## Evidence consulted

- `DOCUMENTATION_INDEX.md`
- `QA_GATES.md`
- `SECURITY_GATES.md`
- `TASK_GRAPH.md`
- `TRACKER.md`
- `R2BN_CANONICAL_G1_REVIEW_STATE_SOURCE_ROOT_REPAIR.md`
- `validate_r2bn_g1_evidence.py`
- canonical Factory status JSON captured from this worktree: `/tmp/r2ct-status-before.json`
- GitHub PR #80 readback for `https://github.com/SiteOneTech/hermes-agent-original/pull/80`

## Current configured-base evidence

Before edits, this assigned worktree had `HEAD=origin/main=merge-base=0db9bed7ed9e8ec4dbefda41f95a335ab82fbbc0`, the merge commit for R2bn PR #80. Canonical Factory status captured from this exact worktree reported:

- `db_backend=agent_core_postgres`, `database=zeus_agent`.
- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2ct-bounded-canonical-g1-docume`.
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2ct-bounded-canonical-g1-docume`.
- `factory_status_delegated=false`.
- Active project metadata: `reconciliation_anomalies=[]`, `reconciliation_projection_source=current_document_status`, `reconciliation_required=false`.
- 14/14 required G1 documents are `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false`, `readiness_source=configured_base_ref`, `base_ref=origin/main`, `base_commit=0db9bed7ed9e8ec4dbefda41f95a335ab82fbbc0`, and stale primary rejected with `primary_checkout_not_configured_base`.

The 14 required rows are: `FACTORY_INTAKE.md`, `REQUIREMENTS_ANALYSIS.md`, `PATTERN_ANALYSIS.md`, `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, `PRD.md`, `ADRS.md`, `METHODOLOGY_PLAN.md`, `TECHNICAL_BLUEPRINT.md`, `SPRINT_PLAN.md`, `TASK_GRAPH.md`, `TRACKER.md`, `DOCUMENTATION_INDEX.md`, `QA_GATES.md`, and `SECURITY_GATES.md`.

## Reviewed/validated marker provenance

The required G1 document frontmatter remains machine-readable `validated: yes` and `reviewed: yes`. R2ct does not rewrite those review markers. They remain backed by the independent source review chain already embedded in all 14 docs:

- reviewer identity: `solution-architect`
- review evidence: `factory_gate_794`
- reviewed candidate exact SHA: `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`
- reviewed candidate PR: `https://github.com/SiteOneTech/hermes-agent-original/pull/36`
- reviewed source gate: `factory_gate_790`
- reviewed source SHA: `2476e978c545e24b18ee48844b24eb8c58245ab4`

R2ct adds validation around those markers through `validate_r2ct_g1_evidence.py`; it does not claim a new G1 document-content review of the 14 source docs.

## R2bn predecessor reconciliation

R2bn is now historical predecessor evidence, not the current branch. GitHub readback for PR #80 reports:

- PR URL: `https://github.com/SiteOneTech/hermes-agent-original/pull/80`
- state: `MERGED`
- label: `agent:zeus`
- base branch/head: `main` / `9ebaa9e7b44c61bb871ca4da0a838c52e62666b2`
- head branch/head: `factory/zeus-alpha-research-ledger-core/inc-018-r2bn-canonical-g1-review-state-s` / `5dcf7d14746457148b045e2ed94aed6114054e6d`
- merge commit: `0db9bed7ed9e8ec4dbefda41f95a335ab82fbbc0`

Factory gate `929` is the independent exact-SHA R2bn quality evidence. The gate is project-scoped intentionally to avoid Factory task-scoped auto-integration, but its notes bind task id `zeus-alpha-research-ledger-core-r2bn-canonical-g1-review-state-source-ro`, base `9ebaa9e7b44c61bb871ca4da0a838c52e62666b2`, head `5dcf7d14746457148b045e2ed94aed6114054e6d`, PR #80, reviewer `quality-reviewer`, and the no-merge/no-direct-SQL boundary. It authorizes no ALR-020/product dispatch.

## Candidate readiness versus primary origin/main readiness

Primary origin/main readiness is the current configured-base row readback at `origin/main` `0db9bed7ed9e8ec4dbefda41f95a335ab82fbbc0`: the current configured-base rows are 14/14 non-blocking and active reconciliation metadata is clean.

Candidate readiness is separate and remains tied to the R2ct PR head after push. The R2ct candidate is the branch `factory/zeus-alpha-research-ledger-core/inc-019-r2ct-bounded-canonical-g1-docume`, not PR #80 and not the stale primary checkout. The exact final candidate SHA cannot be embedded inside the commit that defines it; it must be named in the Zeus-signed PR body and in an independent `quality-reviewer` Factory gate record before R2ct can close.

## Residual stale source

The remaining active `unvalidated_required_docs` strings in canonical status are not current document-content failures. They are structured residual metadata on old blocked tasks:

- `zeus-alpha-research-ledger-core-r2ai-current-origin-g1-independent-revie`
- `zeus-alpha-research-ledger-core-r2ae-bounded-canonical-g1-validation-and`

Both retain `blocker_source=structured_reconciliation_metadata` and `reconciliation_anomaly=unvalidated_required_docs`. R2ct preserves those task rows fail-closed; it does not close/supersede tasks or remove history.

## Deterministic validation

R2ct adds `validate_r2ct_g1_evidence.py`. The intended GREEN command after PR push and independent quality gate is:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 factory/projects/zeus-alpha-research-ledger-core/validate_r2ct_g1_evidence.py --project-dir . --status-json /tmp/r2ct-status-after-review.json --expected-base 0db9bed7ed9e8ec4dbefda41f95a335ab82fbbc0 --expected-head <final-r2ct-pr-head-sha> --expected-pr <r2ct-pr-url> --expected-quality-gate <r2ct-quality-gate-id> --predecessor-base 9ebaa9e7b44c61bb871ca4da0a838c52e62666b2 --predecessor-head 5dcf7d14746457148b045e2ed94aed6114054e6d --predecessor-pr https://github.com/SiteOneTech/hermes-agent-original/pull/80 --predecessor-quality-gate 929
```

The validator intentionally fails before the R2ct artifact/index/handoff plus exact PR/gate evidence exist. It checks canonical Factory status, the 14 G1 rows, the source-root identity, the machine-readable frontmatter provenance for all 14 required docs, R2bn PR #80/gate 929 predecessor provenance, R2ct PR/gate notes, and this boundary.

## PR-first handoff

R2ct must be delivered as a Zeus-signed, non-draft GitHub PR against `main`, labeled `agent:zeus`. The PR body and Factory quality gate must name:

- task id `zeus-alpha-research-ledger-core-r2ct-bounded-canonical-g1-documentation-`
- base `0db9bed7ed9e8ec4dbefda41f95a335ab82fbbc0`
- final R2ct candidate SHA after the last push
- R2ct PR URL
- status JSON path
- validator output
- predecessor PR #80 head `5dcf7d14746457148b045e2ed94aed6114054e6d`
- predecessor quality gate `929`
- no merge, no direct SQL, no primary-checkout mutation, no force-push, no external runtime, no ALR-020/product dispatch

R2ct does not self-approve. Completion requires an independent `quality-reviewer` exact-SHA PASS gate recorded before the final handoff.

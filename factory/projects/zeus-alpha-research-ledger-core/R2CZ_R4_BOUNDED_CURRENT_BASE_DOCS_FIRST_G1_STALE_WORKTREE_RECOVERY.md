---
document_type: bounded_current_base_docs_first_g1_stale_worktree_recovery
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2cz-r4-bounded-current-base-docs-first-
run_id: run-1787311367-6f6784b3
phase: documentation
status: implemented_pending_pr_and_independent_quality_review
validated: yes
reviewed: pending_independent_exact_sha_quality_review
owner: codex-builder
engine: codex
base_ref: origin/main
base_sha: bd76d2ac360a447b02cdfaa04ddd5501301a2780
branch: factory/zeus-alpha-research-ledger-core/inc-001-r2cz-r4-bounded-current-base-doc
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2cz-r4-bounded-current-base-doc
created_at_utc: 2026-08-21T11:26:31Z
---

# R2cz-R4 — bounded current-base docs-first G1 stale-worktree recovery

## Scope and boundary

R2cz-R4 is a documentation-only Factory recovery for a stale worker-prompt / stale-worktree G1 projection that still listed ten required documents as missing `reviewed` even though the current Factory implementation and current configured-base document rows are clean.

This increment changes only project-local evidence under `factory/projects/zeus-alpha-research-ledger-core/`. It does not change product/runtime code, Factory runtime code, migrations, tools, schedulers, providers, credentials, messaging/connectors, deployment state, primary checkout state, task status, reviewed frontmatter markers, stale refs/PRs, or any external runtime. It performs no direct SQL, no `factory task close`, no merge, no force-push/ref rewrite, no ALR-020/product dispatch, no trading/risk/paper/live action, and no self-approval.

Agent Core Postgres `factory.*` remains the operational source of truth. Notion is only human projection.

## Canonical documents read

The required entrypoint and G1/control documents read for this documentation phase were:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/REQUIREMENTS_ANALYSIS.md`
- `factory/projects/zeus-alpha-research-ledger-core/REQUIREMENTS_TRACEABILITY.md`
- `factory/projects/zeus-alpha-research-ledger-core/PRD.md`
- `factory/projects/zeus-alpha-research-ledger-core/ADRS.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/G1_REVIEW.md`
- Recent same-class recovery evidence: `R2CX_CURRENT_ORIGIN_DOCUMENTATION_INDEX_REVIEWED_STATE_REPAIR.md`, `R2CY_R3_DOCS_FIRST_G1_EXACT_SHA_REVIEW_DISPATCH_RECOVERY.md`, `R2CY_R3_SUCCESSOR_INTEGRATE_R2DA_FAIL_CLOSED_READBACK.md`, `R2CY_R3_SUCCESSOR_CURRENT_BASE_R2DA_DISPATCH_REPAIR.md`, `R2DF_R5_FAIL_CLOSED_REVIEW_TERMINALIZATION_RECOVERY.md`, and `R2EA_DOCS_FIRST_STALE_RUNTIME_DISPATCH_PROVENANCE_REPAIR.md`.

## Current-base identity

Captured from the assigned isolated worktree after a fresh `git fetch origin main --prune`:

- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2cz-r4-bounded-current-base-doc`
- Branch: `factory/zeus-alpha-research-ledger-core/inc-001-r2cz-r4-bounded-current-base-doc`
- Remote: `https://github.com/SiteOneTech/hermes-agent-original.git`
- `git rev-parse HEAD`: `bd76d2ac360a447b02cdfaa04ddd5501301a2780`
- `git rev-parse origin/main`: `bd76d2ac360a447b02cdfaa04ddd5501301a2780`
- `git merge-base HEAD origin/main`: `bd76d2ac360a447b02cdfaa04ddd5501301a2780`
- Primary checkout `/home/jean/Projects/hermes-agent-original` was not moved or modified.

## Factory implementation readback: frontmatter authority is present

The assigned worktree contains the current Factory implementation that exposes `_document_frontmatter_flag` in `hermes_cli/factory_pg.py`:

- `hermes_cli/factory_pg.py:2014` defines `def _document_frontmatter_flag(file_text: str, flag: str) -> bool | None`.
- `hermes_cli/factory_pg.py:2017-2021` documents the exact safety intent: top-of-file frontmatter is the machine-readable status authority, while historical body prose that quotes stale states such as `reviewed: pending` must not override current frontmatter.
- `hermes_cli/factory_pg.py:2024-2043` parses only the YAML frontmatter window and returns `True` for explicit true values and `False` for pending/unreviewed/unvalidated values.
- `hermes_cli/factory_pg.py:2072-2074` makes `_document_flag_from_text()` use `_document_frontmatter_flag()` before falling back to looser body/index-line heuristics.

This is the specific current-origin Factory behavior required by the R2cz-R4 task. The stale prompt's ten `missing=reviewed` rows are therefore not repaired by changing required-document frontmatter again; the correct bounded repair is evidence/readback against the current source and PR-first handoff.

## Canonical Factory status readback

Allowed status command, run from the assigned current-origin worktree with the canonical venv Python entrypoint:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status --json zeus-alpha-research-ledger-core > /tmp/r2cz-r4-status-before.json
```

Readback summary from `/tmp/r2cz-r4-status-before.json`:

- Output size: `4,302,552` bytes.
- `db_backend=agent_core_postgres`, `database=zeus_agent`.
- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2cz-r4-bounded-current-base-doc`.
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2cz-r4-bounded-current-base-doc`.
- `factory_status_delegated=false`.
- Active project metadata reports `reconciliation_anomalies=[]`, `reconciliation_projection_source=current_document_status`, `reconciliation_required=false`, and `notion_required=false`.
- Exactly 14 `category=g1_required` rows are present.
- All 14 required rows are `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, and `blocking=false`.
- All 14 required rows read from `readiness_source=configured_base_ref`, `base_ref=origin/main`, and `base_commit=bd76d2ac360a447b02cdfaa04ddd5501301a2780`.
- All 14 rows reject the stale primary checkout with `primary_checkout_accepted=false` and `primary_checkout_rejected_reason=primary_checkout_not_configured_base`.

The 14 clean G1-required rows are:

1. `FACTORY_INTAKE.md`
2. `REQUIREMENTS_ANALYSIS.md`
3. `PATTERN_ANALYSIS.md`
4. `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`
5. `PRD.md`
6. `ADRS.md`
7. `METHODOLOGY_PLAN.md`
8. `TECHNICAL_BLUEPRINT.md`
9. `SPRINT_PLAN.md`
10. `TASK_GRAPH.md`
11. `TRACKER.md`
12. `DOCUMENTATION_INDEX.md`
13. `QA_GATES.md`
14. `SECURITY_GATES.md`

The lifecycle rows (`QA_REPORT.md`, `SECURITY_REVIEW.md`, `QUALITY_REVIEW.md`, `DELIVERY_REPORT.md`, `CHANGELOG.md`, `CHANGE_RECORDS.md`, `RETROSPECTIVE.md`) and PM projection row (`NOTION_UPDATE.md`) are absent/not committed and non-blocking; they are not required G1 blockers.

## Required-document frontmatter readback

The current required G1 documents already have top-of-file frontmatter:

- `validated: yes`
- `reviewed: yes`
- `reviewed_by: solution-architect`
- `review_evidence: factory_gate_794`
- `reviewed_candidate_sha: c81547062c5362a7be6f5a1bb2ef9612b29bac9c`
- `reviewed_candidate_pr: https://github.com/SiteOneTech/hermes-agent-original/pull/36`
- `reviewed_source_gate: factory_gate_790`
- `reviewed_source_sha: 2476e978c545e24b18ee48844b24eb8c58245ab4`

R2cz-R4 preserves those reviewed markers unchanged. The machine-readable reviewed status remains bound to the independent PR #36 / gate `794` source chain, not to this implementation worker and not to stale prompt text.

## Stale-projection reconciliation

The R2cz-R4 assignment prompt reported `G1 readiness: 12/22 documentos sin blocker; blockers=10` with `missing=reviewed` for:

`FACTORY_INTAKE.md`, `REQUIREMENTS_ANALYSIS.md`, `PATTERN_ANALYSIS.md`, `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, `PRD.md`, `ADRS.md`, `METHODOLOGY_PLAN.md`, `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`, and `SECURITY_GATES.md`.

That list is stale worker-prompt/control-plane context. It conflicts with the sanctioned current-origin status readback above, which proves every required G1 row is reviewed and non-blocking from `configured_base_ref` at exact base `bd76d2ac360a447b02cdfaa04ddd5501301a2780`. Therefore this repair does not edit the ten required documents' reviewed frontmatter. It records bounded evidence so reviewers and dispatchers can distinguish current configured-base document readiness from historical stale-primary or stale-prompt projections.

## Validation

Local validation for this documentation-only candidate:

- `git fetch origin main --prune` from the assigned worktree: exit `0`; `HEAD=origin/main=merge-base=bd76d2ac360a447b02cdfaa04ddd5501301a2780`.
- Canonical Factory status readback: exit `0`; `/tmp/r2cz-r4-status-before.json` created; 14/14 required G1 rows clean as summarized above.
- Factory implementation source readback: `_document_frontmatter_flag` exists in `hermes_cli/factory_pg.py` and is used before body heuristics.
- Project-local deterministic validator: `factory/projects/zeus-alpha-research-ledger-core/validate_r2cz_r4_g1_evidence.py --status /tmp/r2cz-r4-status-before.json` must exit `0` before PR handoff.
- `git diff --check` must exit `0` before commit/push.

## Delivery and independent review state

R2cz-R4 must be delivered PR-first:

- non-draft GitHub PR against `main`;
- Zeus Signed-off-by commit;
- `agent:zeus` label;
- exact base SHA `bd76d2ac360a447b02cdfaa04ddd5501301a2780`;
- exact final pushed head SHA recorded in the PR body and Factory gate notes after push, because a commit cannot contain its own SHA;
- canonical status readback path and summary;
- explicit boundary: no merge, no deploy, no direct SQL, no primary-checkout mutation, no credential change, no external runtime, no force-push/ref rewrite, no task-status mutation, no product/ALR-020 dispatch.

This artifact remains `reviewed: pending_independent_exact_sha_quality_review`. A distinct `quality-reviewer` must inspect the final PR head and record a source-backed PASS or REQUEST_CHANGES before this task can be represented as reviewed/done. The `codex-builder` implementation worker must not self-approve, impersonate the reviewer, merge the PR, or treat implementation/test evidence as independent quality evidence.

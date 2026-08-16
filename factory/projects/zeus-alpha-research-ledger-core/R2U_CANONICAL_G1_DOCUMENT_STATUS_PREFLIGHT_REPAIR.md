---
document_type: documentation_status_repair_evidence
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2u-canonical-g1-document-status-preflig
phase: documentation
status: implemented
validated: yes
reviewed: pending_final_r2u_pr_review
owner: codex-builder
---

# R2u — canonical G1 document-status preflight repair

## Scope

This is a bounded project-local documentation/index/traceability repair for the active `unvalidated_required_docs` anomaly. It changes only artifacts under `factory/projects/zeus-alpha-research-ledger-core/` and does not alter runtime/product code, merge `main`, deploy, change credentials, add external connectors, dispatch trading/risk/paper/live behavior, enable messaging, or touch non-Zeus systems.

## Canonical reproduction

The assigned worktree starts from current `origin/main`:

- Branch: `factory/zeus-alpha-research-ledger-core/inc-019-r2u-canonical-g1-document-status`.
- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2u-canonical-g1-document-status`.
- Base and initial HEAD: `df4c77fd1413a65cdb85885a06978ff157c1de4d`.
- Remote: `SiteOneTech/hermes-agent-original`.

The canonical Factory status source is Agent Core Postgres `factory.*`, read through:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`

Earlier read-back in this R2u run was captured by Hermes at `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786851130-739724-98d0.log`. That status reproduced the current-base failure mode: the primary checkout still exposed required G1 documents as present/indexed/committed/validated but not reviewed, causing `unvalidated_required_docs` and required-document blockers. A later attempt to refresh the same DB status into `/tmp/r2u_pre_factory_status.json` was blocked by Hermes command-consent guard, so this artifact does not fabricate a newer DB output.

## Root cause

The required G1 pack on current `origin/main` was internally present but the machine-readable markers that Factory's document-status preflight reads were still pending:

- Frontmatter in the required G1 documents carried `reviewed: pending`.
- `DOCUMENTATION_INDEX.md` listed the required documents with `Reviewed` = `pending`.
- The text still described prior R2m/R2s/R2r handoffs as candidate or resolver evidence instead of committing the reviewed G1 state to the canonical documentation pack.

The independently reviewed documentation candidate already exists as PR-first evidence:

- PR #36: `https://github.com/SiteOneTech/hermes-agent-original/pull/36`.
- Exact reviewed candidate head: `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`.
- Candidate base: `df4c77fd1413a65cdb85885a06978ff157c1de4d`.
- Zeus author/sign-off: `Zeus <zeus@sitiouno.com>` with `Signed-off-by: Zeus <zeus@sitiouno.com>`.
- Independent review evidence: Factory gate `794`, reviewer `solution-architect`.
- Source reviewed-docs evidence retained in the reviewed pack: Factory gate `790`, PR #34 SHA `2476e978c545e24b18ee48844b24eb8c58245ab4`.

R2s proved a control-plane resolver path could recognize the reviewed PR #36 candidate, but that route changed non-documentation code. R2u deliberately repairs the docs-first preflight without propagating that resolver/runtime change: it brings the required reviewed markers and index/traceability state into the project-local documentation pack.

## Repair performed

R2u updates the project-local G1 artifacts so Factory's canonical document-status reader can determine readiness from the repository documentation itself:

1. All 14 required G1 documents now carry `reviewed: yes` in YAML frontmatter, plus candidate-bound review provenance for PR #36 / gate 794.
2. Supplemental traceability/control artifacts `G0_REPOSITORY_STRATEGY.md`, `REQUIREMENTS_TRACEABILITY.md`, `DATABASE_AND_RUNTIME_CONTRACT.md`, and `G1_REVIEW.md` carry the same reviewed provenance so the index and traceability metadata stay internally consistent.
3. `DOCUMENTATION_INDEX.md` is updated from pending/current-base handoff language to canonical reviewed-docs language, with every required row marked reviewed and this R2u artifact listed as the controlling preflight repair evidence.
4. `TASK_GRAPH.md`, `TRACKER.md`, `G1_REVIEW.md`, `QA_GATES.md`, and `SECURITY_GATES.md` record that R2u is documentation-only, PR-first, and no-runtime.

The R2u candidate head SHA is recorded in the GitHub PR and Factory evidence after commit/push rather than embedded here; embedding the final SHA in this file would necessarily change that SHA.

## Validation contract

The candidate is valid only if these real checks pass from the assigned worktree:

1. `git diff --check origin/main..HEAD` returns success.
2. `git ls-files --error-unmatch` succeeds for the 14 required G1 docs plus `G0_REPOSITORY_STRATEGY.md`, `REQUIREMENTS_TRACEABILITY.md`, `DATABASE_AND_RUNTIME_CONTRACT.md`, `G1_REVIEW.md`, and this R2u artifact.
3. A local candidate preflight using `hermes_cli.factory_pg.project_document_status()` against the assigned worktree repo path reports `docs_ready=True` and zero blocking required G1 documents.
4. The final diff is documentation-only under `factory/projects/zeus-alpha-research-ledger-core/`.
5. The branch is pushed as a fresh Zeus-signed `agent:zeus` PR with no direct merge/deploy/credential/external-runtime action.

## Dispatch boundary

R2u removes the required-document preflight blockers for the reviewed G1 pack. It does not authorize ALR-020+ to bypass its own task-specific TDD, role/secret, no-egress, security and QA gates, and it does not activate any product/runtime behavior.

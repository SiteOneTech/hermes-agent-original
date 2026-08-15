---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: r2e_current_base_rebase
validated: yes
reviewed: pending_r2e_exact_sha
owner: codex-builder
---

# R2E REBASE VALIDATION — current-base G1 documentation recovery

## Scope
This artifact records the bounded R2e recovery for `zeus-alpha-research-ledger-core-r2e-rebase-the-g1-documentation-reconcil`. It rebases the G1 reviewed-marker documentation delivery onto current canonical `origin/main` using only the assigned branch/worktree:

- branch: `factory/zeus-alpha-research-ledger-core/inc-001-r2e-rebase-the-g1-documentation`
- worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2e-rebase-the-g1-documentation`
- canonical base verified after `git fetch origin --prune`: `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c`
- repo remote: `https://github.com/SiteOneTech/hermes-agent-original.git`

No source/runtime files, credentials, deploy targets, external systems, direct SQL, or `main` branch merge are changed by this artifact.

## PR #20 inspection and supersession rationale
GitHub PR #20 is open, base `main`, head branch `factory/zeus-alpha-research-ledger-core/inc-011-alr-010-r2-pr-first-g1-reconciliation`, head SHA `0d5e72e655009de808da50a430db5ecd28da8efe`, label `agent:zeus`, with no recorded GitHub reviews and no status checks. Its head is not an ancestor of current `origin/main`, whose fetched SHA is `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c`.

Because this worker is explicitly constrained to the assigned R2e branch/worktree and must not modify another branch, the safe path is a successor current-base PR from the assigned branch unless a separate authorized actor updates PR #20. The successor PR must explicitly link PR #20 as superseded current-base evidence.

## Factory evidence inspected
Allowed Factory read path used: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`.

Observed evidence from Agent Core Factory status and recorded gates:

- Anomaly remains `unvalidated_required_docs` because canonical document visibility sees reviewed=false markers in the primary repo path.
- Critical-readiness gate 760 failed with `blocking_count=11`, naming the G1 reviewed-marker visibility blocker.
- Quality gate 758 passed PR #20 head `0d5e72e655009de808da50a430db5ecd28da8efe` but still named the canonical visibility blocker.
- Independent gates 709/710/711 passed exact substantive candidate `3e6c14f8aa368ec6e3623d16640bf4b558ce0c7a`.
- Factory event 174440 records the ALR-020 bounded-local-sessions acceptance correction/read-back; it is metadata evidence only, not implementation authority.
- Factory events 173433 and 173494 record direct ALR-010-R1 integrations into `origin/main`; both remain non-approval audit evidence.

## Local validation commands required for R2e candidate
The current-base candidate is valid only when these checks are recorded against the final commit SHA:

1. `git status --short --branch`
2. `git rev-parse HEAD` and `git rev-parse origin/main`
3. `git diff --check origin/main...HEAD -- factory/projects/zeus-alpha-research-ledger-core`
4. `git diff --name-only origin/main...HEAD -- factory/projects/zeus-alpha-research-ledger-core`
5. `git ls-files --error-unmatch` for all required G1 documents plus `G0_REPOSITORY_STRATEGY.md`, `REQUIREMENTS_TRACEABILITY.md`, `DATABASE_AND_RUNTIME_CONTRACT.md`, `G1_REVIEW.md`, and this file
6. A metadata scan confirming required frontmatter/index `validated: yes` and reviewed markers are observable in the candidate

## Remaining closure constraint
This document is implementation evidence, not independent approval. R2e can be marked terminal only after an independent reviewer records renewed approval or bounded rework against the exact final current-base candidate SHA. Until then the PR-first branch is a candidate, not merge/deploy/runtime authority.

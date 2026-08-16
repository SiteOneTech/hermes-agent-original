---
document_type: dispatchable_canonical_required_doc_validation_evidence
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2af-dispatchable-canonical-required-doc
phase: documentation
status: implemented_pending_independent_review
validated: yes
reviewed: pending_independent_quality_review
owner: codex-builder
base_ref: origin/main
base_sha: 1b6bc0f65d3ad49845d20e056203e3b3702ac2a7
branch: factory/zeus-alpha-research-ledger-core/inc-019-r2af-dispatchable-canonical-requ
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2af-dispatchable-canonical-requ
---

# R2af — dispatchable canonical required-document validation repair

## Scope

R2af is a bounded documentation/status/reconciliation evidence repair for the active `unvalidated_required_docs` dispatch anomaly. It uses only the assigned isolated worktree, committed project-local Markdown, Git/GitHub read-back, and the approved Factory CLI status command.

This increment changes no product/runtime implementation, performs no merge, deploy, credential change, direct SQL, external-runtime call, connector/messaging action, or trading/risk/paper/live operation. It does not dispatch ALR-020+; it only makes the required-document validation cause, current canonical status, and fresh PR handoff explicit for independent G1/QA review.

## Current source identity

Read-back sources used by this worker:

- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2af-dispatchable-canonical-requ`.
- Branch: `factory/zeus-alpha-research-ledger-core/inc-019-r2af-dispatchable-canonical-requ`.
- Repository remote: `https://github.com/SiteOneTech/hermes-agent-original.git`.
- Current local branch/head before this documentation repair: `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7`.
- Current configured base ref: `origin/main` at `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7`.
- `origin/main` commit identity: merge commit `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7`, "Merge Factory increment zeus-alpha-research-ledger-core-r2w-canonical-g1-reviewed-frontmatter-pr into main", parents `b3c32d149d` and `ce79f01596`.
- Approved Factory status command executed from the assigned worktree: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`.
- Hermes saved that full Factory status output at `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786884590-4115045-1490.log`.

## Pre-repair failure evidence and exact cause

The worker prompt and older Factory gate snapshots still exposed stale required-document blockers. The prompt named ten G1 blockers with `missing=reviewed`; the same canonical Factory status output also contains a prior gate snapshot at lines 8127-8342 with the same reviewed=false pattern and a conservative superset of eleven blockers.

For every current prompt blocker, the failure cause is identical: the stale snapshot already had the document present, indexed, committed, and validated; only the `reviewed` flag was false. No prompt blocker was caused by a missing file, missing index row, dirty/untracked artifact, or validation failure.

| Prompt blocker | Exact status cause in stale snapshot |
|---|---|
| `FACTORY_INTAKE.md` | exists=true, indexed=true, committed=true, validated=true, reviewed=false |
| `REQUIREMENTS_ANALYSIS.md` | exists=true, indexed=true, committed=true, validated=true, reviewed=false |
| `PATTERN_ANALYSIS.md` | exists=true, indexed=true, committed=true, validated=true, reviewed=false |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | exists=true, indexed=true, committed=true, validated=true, reviewed=false |
| `PRD.md` | exists=true, indexed=true, committed=true, validated=true, reviewed=false |
| `ADRS.md` | exists=true, indexed=true, committed=true, validated=true, reviewed=false |
| `METHODOLOGY_PLAN.md` | exists=true, indexed=true, committed=true, validated=true, reviewed=false |
| `TECHNICAL_BLUEPRINT.md` | exists=true, indexed=true, committed=true, validated=true, reviewed=false |
| `TASK_GRAPH.md` | exists=true, indexed=true, committed=true, validated=true, reviewed=false |
| `SECURITY_GATES.md` | exists=true, indexed=true, committed=true, validated=true, reviewed=false |

The older gate snapshot additionally included `SPRINT_PLAN.md` with the same reviewed=false tuple, but the R2af task prompt's live G1 block listed `SPRINT_PLAN.md` as ready. R2af therefore treats that gate row as historical stale evidence, not a current blocker.

## Post-repair canonical document-status result

The current project-level `document_status` block in the same approved Factory status output reads the configured base ref directly and reports `readiness_source=configured_base_ref`, `base_ref=origin/main`, `base_commit=1b6bc0f65d3ad49845d20e056203e3b3702ac2a7`, and `configured_base_ref_accepted=true` for every required G1 row.

The canonical current-base required-document blocker set is empty:

| Required G1 document | Current Factory `document_status` at `origin/main` |
|---|---|
| `FACTORY_INTAKE.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `REQUIREMENTS_ANALYSIS.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `PATTERN_ANALYSIS.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `PRD.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `ADRS.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `METHODOLOGY_PLAN.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `TECHNICAL_BLUEPRINT.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `SPRINT_PLAN.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `TASK_GRAPH.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `TRACKER.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `DOCUMENTATION_INDEX.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `QA_GATES.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |
| `SECURITY_GATES.md` | exists=true, committed=true, validated=true, indexed=true, reviewed=true, blocking=false |

## Canonical PR/provenance read-back

GitHub read-back performed through `GH_REPO=SiteOneTech/hermes-agent-original gh pr ...` shows:

- PR #40 is merged and is the source of current `origin/main` merge commit `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7`; it carries the R2w reviewed-frontmatter evidence into the configured base.
- PR #44 (`docs(factory): record R2ae canonical G1 validation`) is open, label `agent:zeus`, head `bb8495a61611cfd9501c00f7a48fda42cfaee61f`, base `main`/`1b6bc0f65d3ad49845d20e056203e3b3702ac2a7`. It is useful current-candidate provenance but is not canonical base because it is unmerged and the task is blocked.
- PR #43 is open, label `agent:zeus`, head `90ca13d0e943f9ec042f595950e4becef0cb673a`, base `main`/`1b6bc0f65d3ad49845d20e056203e3b3702ac2a7`, and changes Factory control-plane code/tests. It is not part of this documentation-only repair and is not a required-document readiness source.
- Project metadata still exposes stale `g1_documentation_checkout` pointing to PR #20 / `dad375f27568c38be771fc597b579d087f034e1d` and stale `reconciliation_anomalies=["unvalidated_required_docs"]`. Those metadata fields are provenance drift to report; they do not override the current configured-base `document_status` rows.

## Repair performed in R2af

R2af makes the dispatchable required-document state truthful, indexed, and reviewable by recording:

1. The exact stale failure cause for every prompt blocker: `reviewed=false` only.
2. The current canonical Factory `document_status` result: all 14 required G1 rows are reviewed/validated/indexed/committed and non-blocking on `origin/main` `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7`.
3. The distinction between current canonical base, open PR candidates (#43/#44), merged historical repairs (#39/#40), and stale metadata (#20/dad375f).
4. A fresh R2af PR-first handoff. The final candidate SHA is recorded in the GitHub PR body after commit/push; embedding it in this file would change the SHA.

## Validation contract

Required verification for this repair:

1. `git diff --check origin/main..HEAD` succeeds.
2. `git diff --name-only origin/main..HEAD` remains limited to `factory/projects/zeus-alpha-research-ledger-core/`.
3. `git ls-files --error-unmatch` succeeds for all 14 required G1 docs plus this R2af evidence artifact and edited project-local evidence docs.
4. Factory status CLI evidence remains available and shows zero current G1 required-document blockers at configured base `origin/main` / `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7`.
5. The pushed branch has a Zeus-signed GitHub PR against `main`, label `agent:zeus`, exact candidate SHA read back from GitHub, and no merge by this worker.

## Dispatch boundary

R2af removes only the required-document validation ambiguity. It does not clear Jean's manual project pause, mutate Factory project metadata directly, merge or close stale PRs, deploy code, activate runtime, or dispatch ALR-020+. Downstream implementation remains blocked until the Factory controller/human policy allows dispatch and each ALR task produces its own TDD/security/QA/PR-first evidence.

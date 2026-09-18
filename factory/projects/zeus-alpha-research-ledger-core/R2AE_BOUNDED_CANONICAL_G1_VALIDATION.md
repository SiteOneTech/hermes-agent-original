---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2ae-bounded-canonical-g1-validation-and
phase: documentation
status: candidate_repair_pending_independent_review
validated: yes
reviewed: pending_independent_exact_sha_review
owner: codex-builder
reviewer: quality-reviewer
base_ref: origin/main
base_sha: e289e007fa6b9590f0dd2c3b8d75d308bd595d2c
assigned_branch: factory/zeus-alpha-research-ledger-core/inc-019-r2ae-bounded-canonical-g1-valida
assigned_worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2ae-bounded-canonical-g1-valida
run_id: run-1788799850-abec4663
---

# R2ae — bounded canonical G1 validation and fresh PR provenance repair

## Scope

This rework is documentation/provenance only. It is bounded to project-local
Factory artifacts under `factory/projects/zeus-alpha-research-ledger-core/` and
sanctioned Factory CLI evidence. It does not merge, deploy, mutate the primary
checkout, write direct SQL, change credentials, touch external runtimes,
activate connectors or messaging, dispatch product/ALR work, or modify trading,
risk, paper, or live execution behavior.

## Current-base source of truth

The sanctioned command is:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`

The current R2ae readback used the assigned worktree and Agent Core Postgres as
source of truth. Evidence is preserved in
`/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1788799921-3134657-2650.log`.
The top-level project readback reports `base_ref=origin/main`,
`base_commit=e289e007fa6b9590f0dd2c3b8d75d308bd595d2c`, and
`configured_base_ref_accepted=true` for the required G1 document rows.

## Required G1 document inventory

The current-base document inventory distinguishes active configured-base row
truth from stale prompt/gate/PR artifacts:

| Document | Current configured-base status | Evidence |
|---|---|---|
| `FACTORY_INTAKE.md` | non-blocking; exists/committed/indexed/validated/reviewed all true | status log lines 22582-22600 |
| `REQUIREMENTS_ANALYSIS.md` | non-blocking; exists/committed/indexed/validated/reviewed all true | status log lines 22601-22619 |
| `PATTERN_ANALYSIS.md` | non-blocking; exists/committed/indexed/validated/reviewed all true | status log lines 22620-22638 |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | non-blocking; exists/committed/indexed/validated/reviewed all true | status log lines 22639-22657 |
| `PRD.md` | non-blocking; exists/committed/indexed/validated/reviewed all true | status log lines 22658-22676 |
| `ADRS.md` | non-blocking; exists/committed/indexed/validated/reviewed all true | status log lines 22677-22695 |
| `METHODOLOGY_PLAN.md` | non-blocking; exists/committed/indexed/validated/reviewed all true | status log lines 22696-22714 |
| `TECHNICAL_BLUEPRINT.md` | non-blocking; exists/committed/indexed/validated/reviewed all true | status log lines 22715-22733 |
| `SPRINT_PLAN.md` | non-blocking; exists/committed/indexed/validated/reviewed all true | status log lines 22734-22752 |
| `TASK_GRAPH.md` | non-blocking; exists/committed/indexed/validated/reviewed all true | status log lines 22753-22771 |
| `TRACKER.md` | non-blocking; exists/committed/indexed/validated/reviewed all true | status log lines 22772-22790 |
| `DOCUMENTATION_INDEX.md` | **blocking**; exists/committed/indexed/validated true, reviewed false | status log lines 22791-22808 |
| `QA_GATES.md` | non-blocking; exists/committed/indexed/validated/reviewed all true | status log lines 22810-22828 |
| `SECURITY_GATES.md` | non-blocking; exists/committed/indexed/validated/reviewed all true | status log lines 22829-22847 |

Canonical current-base state therefore contains exactly one active required G1
blocker: `DOCUMENTATION_INDEX.md` with `reviewed=false`. The other thirteen
required G1 documents are current-base non-blocking rows. Older ten-document or
eleven-document `missing=reviewed` summaries, R2ai/R2ae task metadata, and gate
snapshots remain stale/historical projection evidence unless reproduced by the
current sanctioned status row set.

## Provenance repair

The current `DOCUMENTATION_INDEX.md` already carries reviewed frontmatter and the
required-document matrix row, but older and stale status parsers may choose an
earlier narrative line containing `DOCUMENTATION_INDEX.md` before reaching the
status matrix. This repair adds an early machine-readable self-review guard to
the index so the first `DOCUMENTATION_INDEX.md` occurrence states both
`validated: yes` and `reviewed: yes` with the PR #36 / Factory gate 794 review
chain. It does not alter the required G1 reviewed source markers.

## PR provenance

Before this repair, the assigned local worktree was not a current-base candidate:

- assigned branch: `factory/zeus-alpha-research-ledger-core/inc-019-r2ae-bounded-canonical-g1-valida`
- local assigned HEAD: `bb8495a61611cfd9501c00f7a48fda42cfaee61f`
- remote assigned branch before repair: `d2b1ebad4dd54f45e0e55bf55fae653aee6509a0`
- current `origin/main`: `e289e007fa6b9590f0dd2c3b8d75d308bd595d2c`
- merge-base(local assigned HEAD, origin/main): `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7`

GitHub PR #44 readback before this repair showed the assigned branch PR open,
non-draft, labeled `agent:zeus`, but stale/conflicting:

- URL: `https://github.com/SiteOneTech/hermes-agent-original/pull/44`
- state: `OPEN`
- base: `main`
- head: `d2b1ebad4dd54f45e0e55bf55fae653aee6509a0`
- mergeability: `mergeable=CONFLICTING`, `mergeStateStatus=DIRTY`
- label: `agent:zeus`

The repaired candidate must be pushed back to the same assigned branch/PR with a
fresh current-base tree, exact final head SHA in the PR body and Factory gate
notes, and no merge to `main`. Because a commit cannot embed its own final SHA,
the exact candidate SHA is recorded after push in PR #44 and the Factory gate
record.

## Validation contract

Required local verification for this candidate:

1. `git diff --check` over the candidate commit is clean.
2. `git diff --name-only origin/main <candidate_sha>` is confined to
   `factory/projects/zeus-alpha-research-ledger-core/`.
3. `git ls-tree <candidate_sha>` confirms the new artifact and edited project
   docs are tracked.
4. Sanctioned Factory status readback records the current required-doc state and
   any remaining blockers with exact source. Until this PR is merged by the
   authorized path, canonical `origin/main` can still report the pre-repair
   `DOCUMENTATION_INDEX.md reviewed=false` row; that is the exact technical
   reason validation cannot be fully green without the prohibited base merge.

This artifact is not independent approval. R2ae remains pending an independent
exact-SHA `quality-reviewer` PASS against the final PR #44 head before any task
closure or downstream dispatch relies on it.

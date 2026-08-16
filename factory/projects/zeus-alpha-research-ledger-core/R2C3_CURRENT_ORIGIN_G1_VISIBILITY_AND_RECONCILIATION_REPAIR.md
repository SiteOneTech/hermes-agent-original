---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2c3-current-origin-g1-visibility-and-re
phase: documentation
status: implemented_pending_independent_review
validated: yes
reviewed: pending_independent_quality_review
owner: codex-builder
base_ref: origin/main
current_base_sha: 2a32066398d500d6dac071bd7f2184d47bb3bcb4
branch: factory/zeus-alpha-research-ledger-core/inc-019-r2c3-current-origin-g1-visibility
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2c3-current-origin-g1-visibility
pr_url: https://github.com/SiteOneTech/hermes-agent-original/pull/49
primary_stale_status_log: /home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786895716-2463118-ae50.log
current_origin_status_log: /home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786895883-2463118-cd90.log
post_repair_status_log: /home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786896251-2463118-f710.log
---

# R2c3 — current-origin G1 visibility and reconciliation repair

## Scope

This artifact records the bounded R2c3 documentation repair for the current-origin G1 visibility mismatch. The repair is limited to project-local Markdown under `factory/projects/zeus-alpha-research-ledger-core/`. It performs no product/runtime code change, no base-branch merge, no deployment, no credential operation, no connector/messaging action, no external runtime call, no direct `factory.*` SQL write, and no trading/risk/paper/live behavior.

## Pre-edit branch/worktree identity

Captured before the first R2c3 file edit:

| Field | Value |
|---|---|
| timestamp_utc | `2026-08-16T15:59:28Z` |
| repo_root | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2c3-current-origin-g1-visibility` |
| branch | `factory/zeus-alpha-research-ledger-core/inc-019-r2c3-current-origin-g1-visibility` |
| local_head_before_edits | `2a32066398d500d6dac071bd7f2184d47bb3bcb4` |
| origin_main_before_edits | `2a32066398d500d6dac071bd7f2184d47bb3bcb4` |
| merge_base_before_edits | `2a32066398d500d6dac071bd7f2184d47bb3bcb4` |
| remote | `https://github.com/SiteOneTech/hermes-agent-original.git` |

The assigned branch/worktree was exactly equal to current `origin/main` before edits. This satisfies the fresh isolated current-origin requirement for the R2c3 candidate and explicitly supersedes stale inc-011 / PR #20 lineage as current candidate provenance.

## RED read-back — stale primary checkout/provenance mismatch

The canonical Factory status command was first run with the canonical venv from the stale primary checkout working directory:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status --json zeus-alpha-research-ledger-core
```

It read Agent Core Postgres (`db_backend=agent_core_postgres`, `database=zeus_agent`) and emitted full evidence to `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786895716-2463118-ae50.log`.

That RED read-back is intentionally retained as the failure reproduction:

- Primary checkout `/home/jean/Projects/hermes-agent-original` was on `main` at `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`, while fetched `origin/main` was `2a32066398d500d6dac071bd7f2184d47bb3bcb4`; `git rev-list --left-right --count HEAD...origin/main` returned `3\t1365`.
- The primary checkout's G1 frontmatter still showed `reviewed: pending` for required docs such as `FACTORY_INTAKE.md` and `SECURITY_GATES.md`.
- The status payload's project metadata still retained stale `metadata.g1_documentation_checkout` pointing to PR #20 / `dad375f27568c38be771fc597b579d087f034e1d` on branch `factory/zeus-alpha-research-ledger-core/inc-011-alr-010-r2-pr-first-g1-reconciliation`, with `not_merged=true`.
- Project `document_status` lines 17038–17233 in that log report 10 G1 required blockers with `reviewed=false`: `FACTORY_INTAKE.md`, `REQUIREMENTS_ANALYSIS.md`, `PATTERN_ANALYSIS.md`, `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, `PRD.md`, `ADRS.md`, `METHODOLOGY_PLAN.md`, `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`, and `SECURITY_GATES.md`.

Exact diagnosis: the failed read-back came from a stale local primary checkout/import path and stale PR #20 project metadata, not from the current `origin/main` G1 document source. It must not be used as current candidate evidence, and it must not dispatch ALR-020.

## GREEN read-back — current-origin configured-base source

The same canonical venv command was then run from the assigned current-origin worktree:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status --json zeus-alpha-research-ledger-core
```

It read the same Agent Core Postgres source of truth and emitted full evidence to `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786895883-2463118-cd90.log`.

Project `document_status` lines 17046–17312 in that log show the current resolver reading the verified configured base ref:

- `base_ref=origin/main`
- `base_commit=2a32066398d500d6dac071bd7f2184d47bb3bcb4`
- `configured_base_ref_accepted=true`
- `readiness_source=configured_base_ref`
- all 14 G1 required documents have `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, and `blocking=false`.

The 14 non-blocking G1 required rows are: `FACTORY_INTAKE.md`, `REQUIREMENTS_ANALYSIS.md`, `PATTERN_ANALYSIS.md`, `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, `PRD.md`, `ADRS.md`, `METHODOLOGY_PLAN.md`, `TECHNICAL_BLUEPRINT.md`, `SPRINT_PLAN.md`, `TASK_GRAPH.md`, `TRACKER.md`, `DOCUMENTATION_INDEX.md`, `QA_GATES.md`, and `SECURITY_GATES.md`.

After this documentation repair, the status command was run again from the assigned R2c3 worktree and emitted `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786896251-2463118-f710.log`. Lines 17046–17312 still show the same current-origin configured-base GREEN state for all 14 G1 required rows with `blocking=false`, proving the repair did not introduce a new required-document blocker.

## Documentation repair

R2c3 records the current-origin visibility/reconciliation evidence in this artifact and updates the G1 index/control documents so human and Factory read-backs no longer rely on stale inc-011 / PR #20 lineage as the current candidate. The machine-readable reviewed markers on the required G1 documents remain `reviewed: yes` and continue to cite the independent reviewed-docs source chain: PR #36 exact head `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`, Factory gate `794`, source gate `790`, and PR #34 SHA `2476e978c545e24b18ee48844b24eb8c58245ab4`.

This repair does not mutate Agent Core project metadata directly. The stale metadata is documented as historical/mismatch evidence only; current G1 visibility is the configured-base read-back on `origin/main` `2a32066398d500d6dac071bd7f2184d47bb3bcb4` plus the R2c3 PR-first handoff.

## PR-first handoff

The R2c3 candidate is opened as non-draft GitHub PR #49 (`https://github.com/SiteOneTech/hermes-agent-original/pull/49`) against `main`, labeled `agent:zeus`, Zeus-signed, and awaiting independent exact-SHA review. The final PR body and Factory gate evidence must name the exact final head SHA after the last push. This worker must not self-approve, merge, deploy, change credentials, write direct SQL, or touch any runtime/external/trading path.

R2c3 is a handoff artifact only. It does not authorize base-branch merge, deployment, runtime execution, connector activation, direct Factory DB mutation, downstream ALR implementation, or trading/risk/paper/live behavior.

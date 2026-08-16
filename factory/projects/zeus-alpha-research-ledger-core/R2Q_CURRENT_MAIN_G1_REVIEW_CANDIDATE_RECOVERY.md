---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2q-recover-the-current-main-g1-reviewed
phase: documentation
status: current_main_reviewed_g1_candidate_recovered
validated: yes
reviewed: pending_independent_solution_architect
owner: claude-builder
---

# R2q current-main G1 reviewed-docs candidate recovery

## Scope

This is a bounded project-local documentation/reconciliation candidate. It starts from current `origin/main`, restores a docs-only reviewed-G1 candidate record, and explicitly rejects the invalid R2p review run as completion evidence.

It does not merge to `main`, deploy, change credentials, write direct SQL, alter external runtimes, introduce connectors, trade, activate paper/live behavior, or implement Alpha product runtime code.

## Current-main identity

Read-only Git verification from the assigned isolated worktree established:

- Assigned branch: `factory/zeus-alpha-research-ledger-core/inc-035-r2q-g1-review-candidate-recovery`.
- Assigned worktree root: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-035-r2q-g1-review-candidate-recovery`.
- Repository remote: `https://github.com/SiteOneTech/hermes-agent-original.git` (`origin`).
- Canonical base branch: `origin/main`.
- Exact canonical base SHA used for this R2q recovery: `df4c77fd1413a65cdb85885a06978ff157c1de4d`.
- The R2q branch was initially equal to that base before this documentation-only recovery candidate.

The exact final R2q candidate SHA cannot be embedded inside this committed file without changing the file and therefore changing the commit hash. It must be bound in the PR body, Factory evidence, and independent solution-architect review record after push.

## Reviewed-docs candidate provenance restored

R2q restores candidate-level G1 reviewed markers to the 14 canonical required documents using the latest valid reviewed-docs candidate evidence, not the invalid R2p review run:

- Reviewed candidate PR: `https://github.com/SiteOneTech/hermes-agent-original/pull/34`.
- Reviewed candidate branch: `factory/zeus-alpha-research-ledger-core/inc-024-r2o-reconciliation-apply-indepen`.
- Reviewed candidate SHA: `2476e978c545e24b18ee48844b24eb8c58245ab4`.
- Reviewed candidate base: `df4c77fd1413a65cdb85885a06978ff157c1de4d`.
- Reviewed candidate review evidence: Factory gate `790`, reviewer `quality-reviewer`, PR comment evidence on PR #34.
- Source document review evidence carried by PR #34: Factory gate `789`, reviewer `quality-reviewer`, PR #33 SHA `1e82340dddf52071d14c3c7a00b04b3c17ee2821`.

These markers mean candidate readiness only. They do not assert primary checkout readiness, source merge, production delivery, or ALR-020 dispatch authority by themselves.

## Invalid R2p review evidence rejected

R2p produced PR #35 at head `ef23a73b39057bb07c1f86f21b6cb7f97e43fe62`, base `df4c77fd1413a65cdb85885a06978ff157c1de4d`, label `agent:zeus`. PR #35 changed the Factory control-plane path, not the G1 documentation pack.

The recorded R2p quality-reviewer run is not review evidence:

- Run id: `run-1786840866-90f55f9d`.
- Worker profile: `quality-reviewer`.
- Worker log: `/home/jean/.hermes/factory/runs/run-1786840866-90f55f9d/worker.log`.
- Log lines 365–408 show the session initialized, hit MiniMax OAuth HTTP 429 on all three attempts, wrote a request debug dump, and ended after 15 seconds.
- The same log summary reports `Messages: 1 (1 user, 0 tool calls)`.
- Exit code file `/home/jean/.hermes/factory/runs/run-1786840866-90f55f9d/exit_code.txt` contains `0`, but the provider failure and zero tool calls mean no independent review executed.

A provider failure is blocked/retriable evidence, never completion evidence. R2q therefore does not reuse R2p as a PASS review and does not treat PR #35 as an accepted readiness source.

## Required independent R2q review contract

Before R2q can be considered reviewed or used to unblock canonical Factory state, an independent `solution-architect` review must record PASS or REQUEST_CHANGES against the exact final R2q PR head SHA.

A valid review record must include all of the following:

1. R2q PR number and URL.
2. R2q head branch and exact final candidate SHA after push.
3. R2q base branch `main` and base SHA `df4c77fd1413a65cdb85885a06978ff157c1de4d`.
4. Evidence that the review actually executed: tool calls, files read, diff inspected, and/or commands run.
5. A statement that R2p `run-1786840866-90f55f9d` is invalid completion evidence because it ended on HTTP 429 with zero tool calls.
6. Confirmation that this R2q candidate is docs-only under `factory/projects/zeus-alpha-research-ledger-core/` and preserves no-merge/no-deploy/no-runtime/no-credential boundaries.

If the solution-architect provider fails, times out, or produces zero tool calls, the review remains `BLOCKED` or retriable. It must not be recorded as `DONE` or used to mark the project dispatchable.

## Dispatch hold

No normal ALR-020+ implementation may dispatch until canonical Agent Core Factory state or an explicitly authorized reviewed-candidate path reads back no required G1 blockers, and the R2q exact-SHA review above is validly recorded. This candidate is a recovery handoff, not a merge/deploy/release authorization.

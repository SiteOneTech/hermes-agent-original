---
document_type: current_origin_exact_sha_assigned_branch_delivery_evidence_rework
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2ai-r5-current-origin-exact-sha-assigne
run_id: run-1787277506-7af64ca7
phase: documentation
status: implemented_pending_pr_and_independent_security_review
validated: yes
reviewed: pending_independent_security_review
owner: codex-builder
engine: codex
base_ref: origin/main
base_sha: 96f0ecd0a5f17d88a513cf986e5e92edadcbbd40
branch: factory/zeus-alpha-research-ledger-core/inc-015-r2ai-r5-current-origin-exact-sha
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-015-r2ai-r5-current-origin-exact-sha
failed_security_gate: 1020
created_at_utc: 2026-08-21T02:04:29Z
---

# R2ai-R5 — current-origin exact-SHA assigned-branch delivery-evidence rework

## Scope and boundary

R2ai-R5 is a bounded same-project documentary rework after security gate `1020`
failed. Gate `1020` established that the prior R2ai evidence used a stale base
and did not bind the Factory-assigned branch/worktree to the actual non-draft
`agent:zeus` PR. This increment refreshes the evidence from freshly fetched
current `origin/main`, keeps delivery on the assigned branch, and records the
exact status/readback needed for a distinct independent security review.

Allowed change surface is limited to project-local documentation under
`factory/projects/zeus-alpha-research-ledger-core/` plus sanctioned Factory CLI
status/gate-note evidence. This run does not merge, deploy, change credentials,
mutate the primary checkout, write direct SQL, run `factory task close`, run
`factory project resolve-state`, contact external runtimes/connectors, or perform
broker/trading/risk/paper/live/product-dispatch action.

## Canonical documents read

The worker read the required entrypoint and phase-relevant G1/control docs before
editing:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R5_FAIL_CLOSED_REVIEW_TERMINALIZATION_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2AI_R2_NON_DESTRUCTIVE_CURRENT_ORIGIN_G1_RECOVERY.md`

Agent Core Postgres `factory.*` remains the source of truth. This Markdown file
records the reasoning and exact readback evidence; it does not replace DB state.

## Fresh current-origin identity captured before edits

Read-only Git evidence from the assigned isolated worktree after
`git fetch origin main --prune` and before any documentation edit:

```text
worktree     = /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-015-r2ai-r5-current-origin-exact-sha
branch       = factory/zeus-alpha-research-ledger-core/inc-015-r2ai-r5-current-origin-exact-sha
remote       = https://github.com/SiteOneTech/hermes-agent-original.git
HEAD         = 96f0ecd0a5f17d88a513cf986e5e92edadcbbd40
origin/main  = 96f0ecd0a5f17d88a513cf986e5e92edadcbbd40
merge-base   = 96f0ecd0a5f17d88a513cf986e5e92edadcbbd40
```

The assigned remote branch did not exist before the first R2ai-R5 push:
`git ls-remote origin refs/heads/factory/zeus-alpha-research-ledger-core/inc-015-r2ai-r5-current-origin-exact-sha`
returned no ref. `gh pr list --head` for the assigned branch returned `[]` before
this rework, so no stale PR was reused.

## Failed security gate 1020 readback

Canonical Factory status readback `/tmp/r2ai-r5-status-before.json` preserves the
failed security review notes:

- Gate `1020`, `gate_type=security`, `status=failed`, reviewer
  `security-reviewer`, task
  `zeus-alpha-research-ledger-core-r2ai-current-origin-g1-independent-revie`.
- Gate `1020` notes: current `origin/main` after fetch was
  `96f0ecd0a5f17d88a513cf986e5e92edadcbbd40`, but PR #104/R2ai evidence was
  bound to stale base `71e5e7b2f4ace3b081f9446483784a3c5fb0b981`.
- The same gate records that the assigned branch state and actual PR diverged:
  remote assigned head stayed `70c4bbfe0c66e60bab69bd6b2a3841050ca7a023`, while
  PR #104 was on non-assigned branch
  `factory/zeus-alpha-research-ledger-core/inc-018-r2ai-r3-current-origin-g1-rework`
  at head `6e813710697089582b783ec16c346c95b6e6848d`.
- Required rework from the gate: renew exact-SHA evidence from current
  `origin/main` `96f0ecd0...`, use the approved assigned branch policy, rerun
  canonical Factory status, update PR/gate notes, and preserve reviewed/security
  pending until independent security PASS.

Open historical R2ai PRs observed before this assigned-branch delivery included
#72, #85, #104, and #110. None is the R2ai-R5 assigned branch; they remain stale
or predecessor evidence and are not used as this delivery candidate.

## Canonical Factory CLI status readback

Allowed status command, run from the assigned worktree:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2ai-r5-status-before.json
```

Readback evidence from `/tmp/r2ai-r5-status-before.json`:

```text
exit_code                 = 0
bytes                     = 4184965
db_backend                = agent_core_postgres
database                  = zeus_agent
db_path                   = agent_core_postgres:zeus_agent.factory
factory_cli_source_root   = /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-015-r2ai-r5-current-origin-exact-sha
factory_status_source_root= /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-015-r2ai-r5-current-origin-exact-sha
factory_status_delegated  = false
project_status            = active
current_task_status       = running
current_task_phase        = documentation
```

Current project metadata in the same readback reports
`reconciliation_anomalies=[]`, `reconciliation_projection_source=current_document_status`,
and `reconciliation_required=false`.

Current top-level `document_status` rows in that readback:

- `document_status` rows: `22` total; `14` `g1_required` rows.
- All 14 required rows have `base_commit=96f0ecd0a5f17d88a513cf986e5e92edadcbbd40`.
- All 14 required rows have `readiness_source=configured_base_ref`.
- All 14 required rows have `exists=true`, `committed=true`, `indexed=true`,
  `validated=true`, `reviewed=true`, `blocking=false`.
- `blocking_count=0`; `reviewed_false=[]`; `blocking=[]`.
- Primary checkout is rejected, not mutated:
  `primary_head=ac1fdb16051324c490d803b14dd06efffd6f9ad0`,
  `primary_checkout_accepted=false`,
  `primary_checkout_rejected_reason=primary_checkout_not_configured_base`,
  `primary_worktree_root=/home/jean/Projects/hermes-agent-original`.

Historical gate snapshots inside the status payload still preserve older blocking
document-status snapshots. Those snapshots are audit evidence only; the current
project-level readback above is the current configured-base status for this run.

## Assigned-branch PR delivery contract

This branch must be pushed normally to `origin` and opened as a non-draft GitHub
PR against `main` from the assigned branch:

```text
branch = factory/zeus-alpha-research-ledger-core/inc-015-r2ai-r5-current-origin-exact-sha
base   = main / origin/main @ 96f0ecd0a5f17d88a513cf986e5e92edadcbbd40
label  = agent:zeus
```

A commit cannot contain its own final SHA. Therefore the immutable final pushed
head SHA, PR URL, PR base/head readback, and Factory gate-note ID must be recorded
after the final push in the PR body, the final worker evidence, and the
sanctioned Factory `gate record` notes. Any creation-time PR head or intermediate
head is not the final security-review target unless it matches the latest remote
branch head read back from GitHub.

## Review state and acceptance mapping

- AC: fresh `origin/main` readback before edits — satisfied by the Git readback
  above at `96f0ecd0a5f17d88a513cf986e5e92edadcbbd40`.
- AC: assigned branch/worktree and actual PR use the same source — pending until
  post-push PR readback confirms the non-draft `agent:zeus` PR head equals the
  remote assigned branch head.
- AC: evidence is project-local documentation plus canonical Factory CLI
  readback/gate notes — this artifact, `DOCUMENTATION_INDEX.md`, `QA_GATES.md`,
  `SECURITY_GATES.md`, `TASK_GRAPH.md`, and `TRACKER.md` are the project-local
  evidence surface; `/tmp/r2ai-r5-status-before.json` is readback input only.
- AC: independent security review records PASS only against refreshed exact SHA —
  still pending. This worker records no security PASS and no self-review.
- AC: no merge/deploy/credential/direct-SQL/primary mutation/external runtime or
  trading action — satisfied by scope and command history for this run.

## Validation to run before final handoff

Required checks for this documentation-only rework:

- `git diff --check` must exit `0`.
- Changed paths must stay under
  `factory/projects/zeus-alpha-research-ledger-core/`.
- A final `git fetch origin main` must show `origin/main` still equals
  `96f0ecd0a5f17d88a513cf986e5e92edadcbbd40`; if it changes before review, this
  evidence must be restarted from the new current base.
- Post-push PR readback must show non-draft `agent:zeus`, `baseRefName=main`,
  `headRefName` equal to the assigned branch, and `headRefOid` equal to the
  remote assigned branch SHA.

## Boundary confirmation

This rework preserves all G1 reviewed frontmatter fields as already reviewed by
PR #36/gate `794`; it does not create a new G1 review, does not mark this R2ai-R5
artifact reviewed, and does not approve R2ai security. The secure state after
this worker handoff is `reviewed: pending_independent_security_review` until a
distinct security reviewer records PASS against the final pushed PR head.

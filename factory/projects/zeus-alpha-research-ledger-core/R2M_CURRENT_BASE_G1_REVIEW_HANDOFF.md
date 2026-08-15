---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2m-current-base-g1-documentation-pr-rec
phase: documentation
status: current_base_g1_review_handoff_recorded
validated: yes
reviewed: pending_independent_exact_sha
owner: codex-builder
---

# R2m current-base G1 documentation PR recovery and exact-SHA review handoff

## Scope

This is a bounded project-local documentation recovery on the task-assigned isolated worktree. It recreates the G1 documentation candidate on the current canonical `origin/main`, preserves the canonical R2j/R2k provenance repairs, and prepares a fresh Zeus-signed `agent:zeus` PR for independent exact-SHA review.

This artifact does not mark any required G1 document `reviewed: yes`, does not self-approve, does not merge, does not deploy, does not change credentials, does not write direct SQL, does not alter external runtimes, and does not authorize ALR-020 or later product implementation.

## Current-base identity

Read-only Git verification from `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2m-current-base-g1-documentatio` established:

- Assigned branch: `factory/zeus-alpha-research-ledger-core/inc-001-r2m-current-base-g1-documentatio`.
- Assigned worktree root: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2m-current-base-g1-documentatio`.
- Repository remote: `https://github.com/SiteOneTech/hermes-agent-original.git` (`origin`).
- Canonical base branch: `origin/main`.
- Exact canonical base SHA used for this R2m recovery: `ab08b13669903a87b3d60d6c80231d23d6313782`.
- The R2m branch was initially equal to that base before the R2m handoff artifact updates.

## Canonical provenance incorporated

- `R2J_CANONICAL_STATE_REPAIR.md` remains the canonical historical repair for PR #29 / R2i review-worktree provenance. It proves that the R2i `already_ancestor` attachment must not be used as PR #29 source-merge evidence.
- `R2K_STALE_CANONICAL_G1_PROVENANCE_REPAIR.md` remains the canonical stale-provenance repair. It proves that obsolete Factory metadata pointing to PR #20 / `dad375f27568c38be771fc597b579d087f034e1d` is not active G1 review provenance.
- PR #30 (`c1943efb2b97b54b42bc5eabe858340d8c391116`) and PR #31 (`73b74f03e3c73830f69fb487a7439529190c21c2`) are historical documentation/provenance evidence now present behind the current `origin/main` base. Their existence does not convert any required G1 document to `reviewed: yes`.

## Stale provenance explicitly rejected

The active R2m review target is the fresh PR head produced from this branch after validation and push. Reviewers must not use any of the following as active approval or dispatch evidence:

- stale project metadata that names PR #20 / `dad375f27568c38be771fc597b579d087f034e1d`;
- historical PR #29 head `f61a7275048e2135b2b2729a1b9cdf8713c58866` or its prior PASS reviews;
- R2i review-worktree `already_ancestor` attachments;
- PR #30 or PR #31 merge exposure alone;
- historical planning/predecessor base SHAs such as `20228c1167814f36d952999f2cafe8b3f6f9ba3c`.

## Factory status and G1 hold

The approved Factory status path remains Agent Core Postgres `factory.*` via `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status`. The R2m read-back showed the project on `agent_core_postgres:zeus_agent.factory` with the recurring `unvalidated_required_docs` anomaly and required G1 documents still blocking on `reviewed=false` in canonical status.

Therefore the candidate intentionally keeps required G1 frontmatter and the index at `reviewed: pending`. No normal ALR-020 implementation dispatch is authorized by this recovery task.

## Independent exact-SHA handoff

After local validation and push, the PR body and Factory evidence record must bind review to the exact R2m candidate SHA, base SHA `ab08b13669903a87b3d60d6c80231d23d6313782`, branch, worktree, documentation-only diff, validation commands, and the no-merge/no-deploy/no-external-execution boundaries.

The next valid action is independent PASS/REQUEST_CHANGES review against that exact R2m PR head SHA. This worker records implementation evidence only and leaves the G1 gate `reviewed: pending`.

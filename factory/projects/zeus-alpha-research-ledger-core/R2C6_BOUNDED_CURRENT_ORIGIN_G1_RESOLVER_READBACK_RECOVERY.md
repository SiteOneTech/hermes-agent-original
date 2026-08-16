---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2c6-bounded-current-origin-g1-resolver-
phase: documentation
status: implemented_pending_independent_exact_sha_review
validated: yes
reviewed: pending_independent_review
owner: codex-builder
branch: factory/zeus-alpha-research-ledger-core/inc-001-r2c6-bounded-current-origin-g1-r
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2c6-bounded-current-origin-g1-r
---

# R2c6 — bounded current-origin G1 resolver/readback recovery

## Scope
This increment repairs the Factory G1 `document_status` resolver/readback path only. It does not move, merge, fast-forward, write to, or otherwise repair the primary checkout at `/home/jean/Projects/hermes-agent-original`. It adds no Zeus Alpha Ledger product runtime, provider connector, messaging connector, deployment path, credential path, direct SQL path, trading/risk/paper/live action, or production activation.

The project-local resolver now keeps the configured `origin/main` base as the controlling identity, and only when that configured base is verified and still blocking may it read a separately checked-out reviewed G1 candidate. The candidate must be tied to the exact configured base branch and commit, must be a descendant of that base, must have PR head readback, independent reviewed PASS evidence, a clean tracked artifact state, and machine-readable reviewed/validated G1 document markers. Invalid, dirty, untracked, unavailable, malformed, base-mismatched, or unreviewed candidates fail closed and leave G1 blocking.

## Canonical source and documentation read before implementation
Read/used project-local controlling artifacts:
- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2C4_CANONICAL_G1_DOCUMENT_STATUS_SOURCE_SELECTION_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2V_CANONICAL_G1_STATUS_AND_NO_AUTO_MERGE_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2C5_INDEPENDENT_CURRENT_BASE_G1_REVIEW.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`

Factory source of truth was read only through the approved Factory CLI: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`. No direct `factory.*` SQL was used.

## Divergence reproduction evidence
Git readback captured before final delivery:

Primary checkout `/home/jean/Projects/hermes-agent-original`:
- `git status --short --branch` → `## main...origin/main [ahead 3, behind 1370]`
- `git rev-parse HEAD` → `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`
- `git rev-parse origin/main` → `40a188b23a384901f983e4d959d3ebbecf50b318`
- `git merge-base HEAD origin/main` → `c846ccfbd844c2f8810a26776505ec44a2341914`
- `git rev-list --left-right --count HEAD...origin/main` → `3	1370`

Assigned isolated worktree:
- path: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2c6-bounded-current-origin-g1-r`
- branch: `factory/zeus-alpha-research-ledger-core/inc-001-r2c6-bounded-current-origin-g1-r`
- start HEAD: `40a188b23a384901f983e4d959d3ebbecf50b318`
- start `origin/main`: `40a188b23a384901f983e4d959d3ebbecf50b318`
- start merge-base: `40a188b23a384901f983e4d959d3ebbecf50b318`
- start ahead/behind: `0	0`

Factory CLI exact status readback after the resolver implementation used output cache `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786906211-500656-f450.log`:
- project `document_status` starts at line 17822.
- configured base source: `readiness_source=configured_base_ref`, `base_ref=origin/main`, `base_branch=main`, `base_commit=40a188b23a384901f983e4d959d3ebbecf50b318`.
- stale primary rejected on every G1 row: `primary_checkout_accepted=false`, `primary_checkout_rejected_reason=primary_checkout_not_configured_base`, `primary_head=4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`.
- exact current required-G1 blocker in that status output: `DOCUMENTATION_INDEX.md` at lines 18098–18122 has `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=false`, `blocking=true`.
- representative non-blocking rows at the same configured source: `FACTORY_INTAKE.md` lines 17823–17847, `PRD.md` lines 17923–17947, `SECURITY_GATES.md` lines 18148–18172 all show `reviewed=true`, `blocking=false`.

This evidence intentionally preserves the primary-vs-current-origin mismatch instead of mutating the primary checkout.

## Implementation summary
Files changed:
- `hermes_cli/factory_pg.py`
  - adds normalized branch readback for candidate base evidence;
  - extends reviewed-G1 candidate validation with exact configured-base branch/commit matching and `git merge-base --is-ancestor <configured_base_commit> <candidate_sha>` ancestry validation;
  - only reads candidate document rows after the configured base ref is verified and still has required-G1 blockers;
  - annotates accepted candidate rows with `reviewed_candidate_accepted=true`, candidate branch/SHA/reviewer/PR evidence, and the configured base ref/commit;
  - annotates rejected candidate attempts without clearing configured-base blockers.
- `tests/hermes_cli/test_factory_control_plane_refactor.py`
  - adds current-base candidate fixture coverage with stale primary checkout preserved;
  - adds acceptance and fail-closed tests for accepted reviewed candidates, unavailable candidates, malformed candidate SHA, dirty tracked artifacts, untracked artifacts, and unreviewed candidate docs.

## RED/GREEN and verification evidence
RED evidence:
- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'reads_reviewed_current_base_candidate or rejects_invalid_current_base_candidate or keeps_unreviewed_current_base_candidate' -v --tb=short`
- Expected failure after test introduction and before resolver implementation: 6 selected tests failed. Failure mode: accepted reviewed current-base candidate still returned `readiness_source=configured_base_ref`; invalid candidate rejection fields were absent; unreviewed candidate rows did not read from the candidate. This proved the pre-repair behavior.

GREEN evidence:
- Same targeted command after implementation: 6 selected tests passed, 0 failed, in 3.0s.
- Broader control-plane file: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py` → 148 passed, 0 failed, in 10.4s.
- Related integration/control-plane suite: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_increment_integration.py` → 261 passed, 0 failed, in 10.4s.
- Diff hygiene: `git diff --check` → exit 0, no output.
- Factory CLI readback: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json` → exit 0; exact project `document_status` evidence in `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786906211-500656-f450.log` lines 17822–18172.

## Delivery and independent review handoff
Delivery remains PR-first. The branch `factory/zeus-alpha-research-ledger-core/inc-001-r2c6-bounded-current-origin-g1-r` must be pushed and opened as a Zeus-signed `agent:zeus` pull request. The final candidate SHA is intentionally recorded in the PR body and Factory gate record after commit creation, because a file cannot reliably name the SHA of the commit that contains itself.

Required independent review: exact candidate SHA review by the assigned reviewer before task closure. This worker does not self-approve, merge, deploy, or update the primary checkout.

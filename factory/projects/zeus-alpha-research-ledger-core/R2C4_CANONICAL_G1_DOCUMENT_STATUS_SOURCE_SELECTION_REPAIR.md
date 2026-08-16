---
document_type: control_plane_repair_evidence
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2c4-repair-canonical-g1-document-status
phase: documentation
status: implemented_pending_independent_review
validated: yes
reviewed: pending_independent_quality_review
owner: codex-builder
base_ref: origin/main
base_sha: 2a32066398d500d6dac071bd7f2184d47bb3bcb4
primary_checkout_head: 4eb87e4cd48105af05fe974cf1d493f0e1b57ae1
branch: factory/zeus-alpha-research-ledger-core/inc-019-r2c4-repair-canonical-g1-documen
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2c4-repair-canonical-g1-documen
factory_status_log_after_repair: /home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786899167-3129419-6510.log
---

# R2c4 — canonical G1 document-status source selection repair

## Scope

This bounded documentation/control-plane repair fixes the Factory G1 `document_status` source-selection path. It does not implement Alpha Research Ledger product functionality, does not deploy, does not change credentials, does not write direct SQL, does not touch messaging/connectors, and performs no trading, risk, paper, or live action.

The repair is code-and-evidence only for the Factory control plane:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_control_plane_refactor.py`
- project-local evidence documents under `factory/projects/zeus-alpha-research-ledger-core/`

## Root cause

R2v made `document_status` fall back to the configured base ref when the primary checkout exposed blocking G1 rows. That still left a stale-primary bypass: if the primary checkout was stale but happened to have ready G1 markers, `project_document_status()` returned `readiness_source=primary` before proving that the primary checkout HEAD matched the configured base commit.

That violates the R2c4 requirement: a primary checkout must never be treated as canonical unless its identity equals the configured canonical base source. Otherwise an arbitrary stale checkout can mask the current `origin/main` G1 state.

## RED evidence

Captured from the assigned worktree before the production fix:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k test_document_status_rejects_stale_primary_even_when_primary_docs_are_ready -v --tb=short
```

Result: failed as expected. The new test created a stale primary checkout with `reviewed: yes`, then advanced `origin/main` to `not reviewed yet`. Current code returned no G1 blockers from the stale primary source instead of resolving the configured `origin/main` source.

Failure excerpt:

```text
FAILED tests/hermes_cli/test_factory_control_plane_refactor.py::test_document_status_rejects_stale_primary_even_when_primary_docs_are_ready
E   assert False
E    +  where False = any(... row["blocking"] ...)
```

Live canonical divergence evidence was also recorded using only read-only Git and Factory CLI readback:

- Assigned worktree head/base before edits: `2a32066398d500d6dac071bd7f2184d47bb3bcb4`.
- Primary checkout `/home/jean/Projects/hermes-agent-original` HEAD: `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`.
- Primary checkout `origin/main`: `2a32066398d500d6dac071bd7f2184d47bb3bcb4`.
- Primary `HEAD:factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md` frontmatter: `reviewed: pending`.
- Primary `origin/main:factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md` frontmatter: `reviewed: yes`.
- Factory CLI status before repair emitted current project `document_status` rows with all 14 required G1 docs non-blocking from `readiness_source=configured_base_ref`, but historical reconciler events and metadata still carried the false `unvalidated_required_docs` anomaly. Full log: `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786898868-3129419-3f50.log`.

## Repair implemented

`project_document_status()` now treats a configured base source as authoritative whenever one is explicitly configured by project/base-branch or G0 repository strategy metadata.

Behavior after this repair:

1. For projects without an explicit configured base source, the legacy primary-filesystem behavior remains unchanged.
2. For projects with an explicit configured base source, the resolver verifies the primary checkout identity against the configured base commit.
3. If primary HEAD equals the configured base commit and G1 rows are ready, primary rows are returned with exact identity evidence.
4. If primary HEAD differs from the configured base commit, rows are resolved from the configured base ref (`origin/<base_branch>`) and annotated with `primary_checkout_accepted=false`, `primary_checkout_rejected_reason`, `primary_head`, `primary_branch`, `primary_path`, and `primary_worktree_root`.
5. If the configured base ref cannot be verified, the resolver fails closed by marking G1 rows blocking and recording `configured_base_ref_accepted=false` plus the exact rejection reason.

The resolver still never reads reviewed-candidate PR/worktree metadata as a canonical readiness source.

## GREEN evidence

Focused regression set:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'test_document_status_rejects_stale_primary_even_when_primary_docs_are_ready or test_document_status_uses_configured_origin_base_when_primary_checkout_stale or test_document_status_fails_closed_when_configured_base_ref_lacks_indexed_g1_docs or test_document_status_never_resolves_from_exact_reviewed_g1_candidate' -v --tb=short
```

Result: 4 selected tests passed, 0 failed.

Focused Factory control-plane suite:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_increment_integration.py
```

Result: 2 files passed, 255 tests passed, 0 failed.

Post-repair Factory CLI readback:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json
```

Full log: `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786899167-3129419-6510.log`.

Project `document_status` rows at log lines 17417–17689 show:

- `base_ref=origin/main`
- `base_commit=2a32066398d500d6dac071bd7f2184d47bb3bcb4`
- `readiness_source=configured_base_ref`
- `primary_checkout_accepted=false`
- `primary_checkout_rejected_reason=primary_checkout_not_configured_base`
- `primary_head=4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`
- `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false` for the required G1 rows shown in that range; the remaining required rows continue the same shape immediately after that range.

This proves the stale primary checkout is not treated as canonical, while current `origin/main` remains the deterministic G1 source.

## Delivery contract

- Base ref: `origin/main`.
- Base/source SHA before edits: `2a32066398d500d6dac071bd7f2184d47bb3bcb4`.
- Primary checkout HEAD at repair time: `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`.
- Deliverable branch: `factory/zeus-alpha-research-ledger-core/inc-019-r2c4-repair-canonical-g1-documen`.
- Required PR: Zeus-signed GitHub PR with `agent:zeus` label and exact final head SHA in PR readback/evidence.
- Required independent review: quality reviewer must review the exact pushed PR head SHA before task closure. This codex-builder worker does not self-approve or merge.

## No external operation evidence

This run used local Git readback, the approved Factory status CLI, local file edits, and local tests only. It performed no deploy, no credential change, no direct SQL, no connector/messaging action, no production runtime propagation, and no trading/risk/paper/live action.

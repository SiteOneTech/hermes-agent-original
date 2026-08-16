---
document_type: control_plane_repair_evidence
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2v-canonical-g1-status-and-no-auto-merg
phase: documentation
status: quality_review_passed_gate_804
validated: yes
reviewed: yes
reviewed_by: quality-reviewer
review_evidence: factory_gate_804
reviewed_candidate_sha: 90fcb81abcebc203e16e34e36f4aec0ab1ec6a09
reviewed_candidate_pr: https://github.com/SiteOneTech/hermes-agent-original/pull/39
owner: codex-builder
base_ref: origin/main
base_sha: 50a9a29c4bb7cee39c8ffafa857ce962066e35cb
branch: factory/zeus-alpha-research-ledger-core/inc-005-r2v-canonical-g1-status-and-no-a
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-005-r2v-canonical-g1-status-and-no-a
implementation_commit_sha: 8cd21cfb9a31bcf45998f4bf76db8f5d28606f0c
pull_request: https://github.com/SiteOneTech/hermes-agent-original/pull/39
---

# R2v — canonical G1 status and no-auto-merge contract repair

## Scope

This is a bounded Factory control-plane repair for the R2v documentation-phase run. It changes only Factory status/completion enforcement and matching behavioral tests/docs. It does not implement the alpha ledger product, does not deploy, does not change credentials, does not use direct SQL, does not touch messaging/connectors, and performs no trading/risk/paper/live action.

## Root cause repaired

1. `project_document_status()` treated the primary checkout filesystem as the only readiness source after R2u. When the primary checkout was stale while the configured base ref `origin/main` already carried reviewed G1 docs, Factory reported false `unvalidated_required_docs` blockers.
2. The same code path could accept explicit reviewed-candidate PR/worktree metadata as a readiness source. That was too broad for the current contract: G1 readiness must come from the configured base ref, never from a task branch, PR head, or arbitrary worktree.
3. Increment completion still allowed Factory auto-integration (`merge_no_ff_push_origin` / `increment_integrated`) even for projects with `factory_auto_integration_forbidden=true`.

## Repair implemented

- `hermes_cli/factory_pg.py` now keeps primary checkout rows only when they are already ready. If primary G1 rows block, it resolves and reads the configured origin base ref (`origin/<base_branch>`) directly with `git show <ref>:<project-doc-path>`.
- The base-ref read path verifies the configured base branch/ref exists as a commit, reads `DOCUMENTATION_INDEX.md` and each G1 file from that ref, marks rows with `readiness_source=configured_base_ref`, `base_ref`, `base_branch`, and `base_commit`, and does not checkout, merge, fast-forward, or mutate the primary worktree.
- Missing/unreadable configured base refs fail closed by returning blocking primary rows annotated with `configured_base_ref_accepted=false` and the rejection reason. Base refs that exist but lack committed/indexed/reviewed G1 docs return blocking base-ref rows.
- Candidate PR/worktree metadata is no longer used by `project_document_status()` as a readiness source.
- Project metadata `factory_auto_integration_forbidden=true` now prevents automatic increment integration before any git merge/fetch/worktree operation, and source-integration reconciliation no longer demands base-branch containment for projects that explicitly forbid Factory auto-integration.

## RED evidence observed

Commands were run from the assigned worktree with the main checkout's venv only (no installs):

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'document_status_uses_configured_origin_base_when_primary_checkout_stale or document_status_never_resolves_from_exact_reviewed_g1_candidate or document_status_fails_closed_when_configured_base_ref_lacks_indexed_g1_docs'
```

Result before implementation: failed as expected. The stale-primary test still saw blockers, the reviewed-candidate test incorrectly cleared blockers from a candidate worktree, and the base-ref missing-index test read the primary index instead of the configured base ref.

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'close_task_respects_project_auto_integration_forbidden_without_increment_event'
```

Result before implementation: failed as expected with `ValueError: increment integration failed for task-1: increment worktree does not exist`, proving the forbidden-project guard had not short-circuited before integration worktree handling.

## GREEN evidence observed

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'document_status_uses_configured_origin_base_when_primary_checkout_stale or document_status_never_resolves_from_exact_reviewed_g1_candidate or document_status_fails_closed_when_configured_base_ref_lacks_indexed_g1_docs' && HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'close_task_respects_project_auto_integration_forbidden_without_increment_event'
```

Result after implementation: 3 selected document-status tests passed and 1 selected integration-forbidden test passed.

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_increment_integration.py
```

Result after implementation: 2 files passed, 254 tests passed, 0 failed.

## Delivery and review contract

- Base ref: `origin/main`.
- Base SHA at claim/fetch: `50a9a29c4bb7cee39c8ffafa857ce962066e35cb`.
- Branch: `factory/zeus-alpha-research-ledger-core/inc-005-r2v-canonical-g1-status-and-no-a`.
- PR URL: https://github.com/SiteOneTech/hermes-agent-original/pull/39.
- Exact implementation commit SHA: `8cd21cfb9a31bcf45998f4bf76db8f5d28606f0c`.
- Exact final PR head SHA must be read back from GitHub and Factory gate evidence after this PR-evidence doc refresh; a commit cannot embed its own final SHA without changing that SHA.
- Required independent review: quality reviewer must review the exact pushed PR head SHA and record PASS/REQUEST_CHANGES before task closure. Completed: quality reviewer recorded PASS as Factory gate `804` against head `90fcb81abcebc203e16e34e36f4aec0ab1ec6a09` (PR #39); evidence in `QA_GATES.md` "R2v independent quality review — gate 804 (PASS)".

## No external operation evidence

This run performed only git read/fetch, local file edits, local tests through `scripts/run_tests.sh`, and Factory status readback. It performed no deploy, no credential change, no direct SQL, no connector/messaging action, no production runtime propagation, and no trading/risk/paper/live action.

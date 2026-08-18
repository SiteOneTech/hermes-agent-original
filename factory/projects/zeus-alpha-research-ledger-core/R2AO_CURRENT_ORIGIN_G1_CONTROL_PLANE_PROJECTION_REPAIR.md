---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2ao-repair-current-origin-g1-control-pl
phase: documentation
status: rework_repair_ready_for_pr
validated: yes
reviewed: pending
owner: codex-builder
created_at: 2026-08-17T05:09:36Z
---

# R2ao — current-origin G1 control-plane projection repair

## Scope and boundary

This increment repairs only the Factory control-plane projection that kept stale G1 reconciliation metadata active after canonical current-origin document rows were already clean.

Boundary preserved:

- no Agent Core ledger runtime implementation;
- no external integration, credential, messaging, trading, risk, paper/live, Vonash, Magnus, VAOS, RAG/KB, broker, deploy, merge, or primary-checkout mutation;
- no direct SQL against `factory.*`;
- Factory DB interactions limited to the approved CLI status/gate path.

## Canonical reproduction before repair

Command run from the assigned isolated worktree:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status --json zeus-alpha-research-ledger-core`

Output log:

`/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786943312-610213-4950.log`

Observed discrepancy:

- Lines 19937–20287 show the 14 `g1_required` documents on `base_ref=origin/main`, `base_commit=4a0a6bbaea3b1acaf8e83084c058b831d865d8c4`, all with `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false`, `readiness_source=configured_base_ref`, and `primary_checkout_accepted=false`.
- Lines 20491–20510 still expose obsolete `metadata.g1_documentation_checkout` pointing at PR #20 / commit `dad375f27568c38be771fc597b579d087f034e1d`.
- Lines 20535–20538 still expose persisted `reconciliation_anomalies=["unvalidated_required_docs"]` and `reconciliation_required=true`.
- Lines 473–497 show recent `project_reconciled` event `193910` still reporting `anomalies=["unvalidated_required_docs"]`.
- Lines 714–726 show historical dispatch preflight event `193875` denying ALR-020 with `blockers=["missing_or_unindexed_docs"]` even though the same status readback proves every required G1 row is indexed and non-blocking.

Conclusion: the remaining blocker was stale control-plane/projection metadata, not document content.

## RED evidence

Command:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'unvalidated_required_docs_reconciliation or stale_g1_checkout_projection'`

Result before repair:

- 3 selected tests ran.
- 2 failed, 1 passed.
- `test_unvalidated_required_docs_reconciliation_resolves_from_current_document_status` failed because `_resolved_reconciliation_anomaly(...)` returned `None` for a blocked `unvalidated_required_docs` reconciliation task even when current G1 document blockers were empty.
- `test_reconcile_clears_stale_g1_checkout_projection_when_current_docs_nonblocking` failed because `reconcile_project(...)` did not remove `metadata.g1_documentation_checkout` while writing an empty current anomaly set.

Rework RED command from the same isolated worktree:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'status_effective_projection'`

Rework RED result before the status-projection repair:

- 2 selected tests ran.
- 1 failed, 1 passed.
- `test_status_effective_projection_ignores_stale_unvalidated_docs_when_current_rows_clean` proved the surviving discrepancy: `status()` still surfaced `metadata.reconciliation_anomalies=["unvalidated_required_docs","pending_effective_gates"]` even when the dynamic current `document_status` rows for required G1 docs were all non-blocking.

## Repair

`hermes_cli/factory_pg.py` now:

1. Adds `_current_g1_required_documents_ready(...)` as the single current-row readiness predicate for required G1 docs.
2. Resolves structured `unvalidated_required_docs` blockers in `_resolved_reconciliation_anomaly(...)` when current required G1 rows are non-blocking or explicitly waived.
3. Adds `_stale_g1_projection_metadata_keys(...)` so reconciliation clears obsolete `g1_documentation_checkout` metadata only when the current finding set no longer contains `unvalidated_required_docs` and current G1 rows are clean.
4. Persists `cleared_project_metadata_keys` in reconcile metadata/event/readback for auditability.
5. Adds a readback-only `status()` effective reconciliation projection guard: once already-computed current `document_status` rows prove required G1 docs are clean, `unvalidated_required_docs` and stale top-level `g1_documentation_checkout` provenance are not re-presented to dispatch/watchdog/reviewer consumers; unrelated anomalies such as `pending_effective_gates` remain visible.

This keeps fail-closed behavior: when current required G1 rows still block, `unvalidated_required_docs` remains unresolved.

## GREEN evidence

Targeted behavioral test:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'unvalidated_required_docs_reconciliation or stale_g1_checkout_projection'`

Result after repair:

- 3 selected tests passed, 0 failed.

Rework status-projection behavioral test:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'status_effective_projection'`

- RED before repair: 1 failed, 1 passed.
- GREEN after repair: 2 passed, 0 failed.

Combined R2ao regression focus:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'unvalidated_required_docs_reconciliation or stale_g1_checkout_projection or status_effective_projection'`

- 5 selected tests passed, 0 failed.

Relevant file-level regression suites:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py`

- 154 tests passed, 0 failed.

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py`

- 113 tests passed, 0 failed.

Combined relevant suite:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_increment_integration.py`

- 267 tests passed, 0 failed.

Static diff check:

`git diff --check`

- exit 0.

Canonical Factory CLI readback after rework status-projection repair:

`/home/jean/Projects/hermes-agent-original/venv/bin/python -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`

Output log:

`/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786945412-1157222-a010.log`

- Lines 19979–20329 show all 14 required G1 rows from `base_ref=origin/main`, `base_commit=4a0a6bbaea3b1acaf8e83084c058b831d865d8c4`, `readiness_source=configured_base_ref`, `exists/committed/indexed/validated/reviewed=true`, `blocking=false`, and stale primary checkout rejected.
- Lines 20571–20575 show the effective status projection preserving only `pending_effective_gates` with `reconciliation_projection_source=current_document_status`.
- Lines 20606–20611 retain audit-only `stale_reconciliation_projection` showing the removed previous `unvalidated_required_docs` projection; stale top-level `g1_documentation_checkout` is not re-presented in project metadata.

## Delivery handoff

Candidate PR and exact final candidate SHA are recorded in the PR body and final Factory gate notes after push. Independent security review must review that exact SHA. This increment does not merge or deploy.

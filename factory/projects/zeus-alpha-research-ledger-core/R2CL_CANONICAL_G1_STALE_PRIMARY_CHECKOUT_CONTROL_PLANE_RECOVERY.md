---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2cl-canonical-g1-stale-primary-checkout
phase: documentation
status: evidence_recorded_implementation_blocked_on_operational_dependency
validated: yes
reviewed: pending_independent_quality_review
owner: qa-verifier
engine: zeus
run_id: run-1786988140-ba3fb46e
base_ref: origin/main
base_sha: b260baea223e863b35fe561e6c5d3d77f3a914c9
branch: factory/zeus-alpha-research-ledger-core/inc-000-r2cl-canonical-g1-stale-primary
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-000-r2cl-canonical-g1-stale-primary
factory_status_json_worktree_cwd: /tmp/r2cl-status-wt.json
factory_status_json_primary_cwd: /tmp/r2cl-status-primary.json
---

# R2cl — canonical G1 stale-primary checkout control-plane recovery

## Scope and boundary

Bounded same-project technical recovery: reproduce and resolve the discrepancy where canonical Factory status read from the stale primary checkout `/home/jean/Projects/hermes-agent-original` at `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1` reports ten G1 rows blocking, while immutable `origin/main` `b260baea223e863b35fe561e6c5d3d77f3a914c9` contains `reviewed: yes` frontmatter for every required G1 document.

This increment diagnoses only Factory source-root/base-ref selection and status derivation. It changes project-local Markdown under `factory/projects/zeus-alpha-research-ledger-core/` only. It does not mutate the primary checkout, does not merge, does not write direct SQL to `factory.*`, does not touch credentials, external runtime/connectors/messaging, or trading/risk/paper/live systems.

## Canonical inputs read

- `DOCUMENTATION_INDEX.md` — required entrypoint; current G1 matrix, R2v/R2c4/R2c5/R2c6/R2am/R2ao/R2au/R2aw/R2bb/R2BJ lineage and status semantics.
- `TRACKER.md` — current-state table and prior recovery rows (R2c5 live-runtime mismatch routing, R2c6 divergence evidence).
- `QA_GATES.md`, `G0_REPOSITORY_STRATEGY.md`, `FACTORY_INTAKE.md` — gate/strategy contract (docs-first, no-auto-merge, Zeus-only).
- Prior recovery evidence: `R2C5_INDEPENDENT_CURRENT_BASE_G1_REVIEW.md` (live stale-primary mismatch documented and routed as bounded technical rework), `R2V_CANONICAL_G1_STATUS_AND_NO_AUTO_MERGE_REPAIR.md` (configured-base selection contract), `R2C6_BOUNDED_CURRENT_ORIGIN_G1_RESOLVER_READBACK_RECOVERY.md` (candidate readback).
- Source predicate code: `hermes_cli/factory_pg.py` at `b260baea` — `_configured_base_ref_readback` (line 2133), `_primary_checkout_identity` (line 2175), `project_document_status` (line 2479).

## Current branch/worktree provenance

Read-only Git evidence from the assigned worktree:

```text
branch    = factory/zeus-alpha-research-ledger-core/inc-000-r2cl-canonical-g1-stale-primary
HEAD      = b260baea223e863b35fe561e6c5d3d77f3a914c9
origin/main = b260baea223e863b35fe561e6c5d3d77f3a914c9
merge-base(HEAD, origin/main) = b260baea223e863b35fe561e6c5d3d77f3a914c9
worktree_status = clean before this documentation edit

primary checkout:
branch    = main
HEAD      = 4eb87e4cd48105af05fe974cf1d493f0e1b57ae1
status    = clean (no mutation by this increment)
merge-base(4eb87e4cd4, b260baea) = c846ccfbd844c2f8810a26776505ec44a2341914
ahead (primary-only commits)  = 3
behind (origin-only commits)  = 1696
```

## Reproduction (acceptance criterion 1)

All commands below are read-only. Factory DB was accessed only through the sanctioned
`venv/bin/python3 -m hermes_cli.main factory status` command.

### Frontmatter readback (`git show <ref>:factory/projects/zeus-alpha-research-ledger-core/<doc>`)

| Ref | `validated: yes` | `reviewed: yes` |
|---|---|---|
| `origin/main` `b260baea…` | 14 / 14 | 14 / 14 |
| primary HEAD `4eb87e4cd4…` | 14 / 14 | 0 / 14 (all `reviewed: pending`) |

### Canonical Factory CLI status (row-level, `g1_required` category)

Command (identical for both runs, only cwd differs):

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main \
  factory status zeus-alpha-research-ledger-core --json
```

| Metric | Run from assigned worktree cwd | Run from primary checkout cwd |
|---|---|---|
| CLI source root | worktree (current code `b260baea`) | primary (stale code `4eb87e4cd4`) |
| `document_status` total rows | 22 | 22 |
| `g1_required` rows | 14 | 14 |
| blocking rows | **0 / 14** | **10 / 14** |
| blocking `reviewed=false` rows | 0 | 10 (FACTORY_INTAKE, REQUIREMENTS_ANALYSIS, PATTERN_ANALYSIS, ASSUMPTIONS_AND_OPEN_QUESTIONS, PRD, ADRS, METHODOLOGY_PLAN, TECHNICAL_BLUEPRINT, TASK_GRAPH, SECURITY_GATES) |
| non-blocking rows | 14 | 4 (SPRINT_PLAN, TRACKER, DOCUMENTATION_INDEX, QA_GATES) |
| per-row `readiness_source` | `configured_base_ref` (14/14) | absent (legacy resolver) |
| per-row `base_commit` | `b260baea…` | absent |
| `configured_base_ref_accepted` | true (14/14) | absent |
| `primary_checkout_accepted` | false (14/14) | absent |
| `primary_checkout_rejected_reason` | `primary_checkout_not_configured_base` | absent |
| project `readiness_source` | `primary` (probe), rejected | `primary` |
| `reconciliation_anomalies` | `[]` | `["unvalidated_required_docs"]` |
| `reconciliation_required` | false | true |
| `reconciliation_projection_source` | `current_document_status` | n/a |
| `factory_cli_source_root` / `factory_status_source_root` | assigned worktree path | n/a (pre-R2bb provenance) |
| `factory_status_delegated` | false | n/a |

Evidence payloads: `/tmp/r2cl-status-wt.json` (2,553,496 bytes), `/tmp/r2cl-status-primary.json` (2,539,260 bytes), plus text logs `/tmp/r2cl-status-wt.log` / `/tmp/r2cl-status-primary.log`.

This exactly reproduces the ten-row blocking readback and ties it to the source root that produced it: the stale primary checkout's own committed code and files, not the current committed Factory code.

## Source-root and base-ref selection in current committed code (acceptance criterion 2)

Module resolution is cwd/PYTHONPATH-bound: running the sanctioned interpreter from the primary checkout imports `hermes_cli` from the primary checkout; running it from the assigned worktree imports from the worktree (verified with `python -c "import hermes_cli; print(hermes_cli.__file__)"`).

The current committed code at `origin/main` `b260baea…` (`hermes_cli/factory_pg.py`) implements the following **intentional** selection order in `project_document_status` (line 2479):

1. Read primary-checkout rows (`readiness_source="primary"`).
2. If the project has a configured base source, verify the configured base ref (`_configured_base_ref_readback`, line 2133).
3. Accept the primary checkout **only** when `primary_head == configured base_commit` (`_primary_checkout_identity`, line 2175); otherwise record `primary_checkout_accepted=false`, `primary_checkout_rejected_reason="primary_checkout_not_configured_base"` and read readiness from the configured base ref (`origin/main`) via `git show <base_ref>:<path>` (`readiness_source="configured_base_ref"`, `configured_base_ref_accepted=true`).
4. Only if the configured base still blocks may a reviewed G1 candidate be considered, and it fails closed on any invalid/unreviewed/dirty state (R2c6).

The function docstring states the contract explicitly: *"if the primary checkout is stale or otherwise still exposes G1 blockers, readiness is read from the configured origin base ref"*.

Git lineage of the selection:

```text
5c9eb14563  fix(factory): bind G1 document status to configured base   (R2v)
005a844cb6  fix(factory): bound current-origin G1 candidate readback   (R2c6)
ce66b28e84  fix(factory): resolve reviewed g1 candidate readiness      (R2c6)
```

Neither `primary_checkout_not_configured_base` nor `readiness_source` exists anywhere in `hermes_cli/factory_pg.py` at `4eb87e4cd4…` (verified with `git grep` at that SHA) — the stale primary runs the pre-R2v resolver that reads only the primary repo_path working tree and derives `reviewed` from stale frontmatter/index/metadata, producing the ten blocking rows.

The observed selection is therefore **intentional, committed behavior of current code, already covered by focused regression tests** — not a defect in committed code. Regression suite executed from the assigned worktree via the canonical wrapper:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 \
  scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py \
  -k "configured_origin_base or stale_primary or configured_base_ref or reviewed_g1_candidate or unvalidated_required_docs_reconciliation or clears_stale_g1_checkout_projection or dispatch_preflight_blocks_product_execution"
```

Result (two independent runs): `✓18 | ✗ 0`, `18 tests passed, 0 failed` (runs 4.0s / 3.7s). Covered tests include `test_document_status_uses_configured_origin_base_when_primary_checkout_stale`, `test_document_status_resolves_frontmatter_reviewed_index_from_configured_origin_base`, `test_document_status_rejects_stale_primary_even_when_primary_docs_are_ready`, `test_document_status_fails_closed_when_configured_base_ref_lacks_indexed_g1_docs`, `test_document_status_reads_reviewed_current_base_candidate_without_moving_primary`, `test_reviewed_g1_candidate_fails_closed_*`, `test_unvalidated_required_docs_reconciliation_*`, and `test_reconcile_clears_stale_g1_checkout_projection_when_current_docs_nonblocking`.

Because current committed code is not defective, R2cl recorded no RED-to-GREEN code change. R2cm later corrects the review-state provenance for this conclusion: the R2cl terminal quality-review path exhausted on MiniMax HTTP 429 and did not produce a durable independent verdict, so the “no PR warranted” conclusion is an unreviewed R2cl worker finding, not an approved quality-review outcome.

## R2cm post-merge review-state correction

R2cl was integrated into `origin/main` as merge commit `0ecd9019ba8ec111aaead60a911c9accd854f731`, but the current canonical wrapper readback (`/home/jean/Projects/hermes-agent-original/venv/bin/hermes factory status zeus-alpha-research-ledger-core --json`) still reports `unvalidated_required_docs` with ten required G1 rows blocking on `reviewed=false`: `FACTORY_INTAKE.md`, `REQUIREMENTS_ANALYSIS.md`, `PATTERN_ANALYSIS.md`, `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, `PRD.md`, `ADRS.md`, `METHODOLOGY_PLAN.md`, `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`, and `SECURITY_GATES.md`.

The current `origin/main` documentation pack keeps real reviewed provenance from PR #36 / Factory gate `794` (source gate `790` / PR #34 SHA `2476e978c545e24b18ee48844b24eb8c58245ab4`). R2cm does not alter those G1 `reviewed: yes` markers. The repaired provenance is that R2cl itself remains `reviewed: pending_independent_quality_review`; downstream consumers must not treat R2cl worker completion, terminal auto-finalization, or merge exposure as independent quality approval.

The PR-first R2cm artifact `R2CM_G1_REVIEW_STATE_PROVENANCE_REPAIR.md` is the controlling handoff for this correction. It requires a fresh Zeus-signed `agent:zeus` PR, exact final head SHA, focused resolver tests, and independent exact-SHA review. If the independent review provider rate-limits again, the correction remains pending rather than green.

## No-mutation compliance (acceptance criterion 3)

- No primary-checkout mutation: `git -C /home/jean/Projects/hermes-agent-original status --porcelain` = 0 lines before and after this increment; no `git` write command was executed against it.
- No direct SQL / psql / ad-hoc scripts against `factory.*`; Factory DB touched only via the two sanctioned `factory status` invocations (read-only).
- No merge, no push of `main`, no deploy, no credential access, no external runtime/connector/messaging action, no trading/risk/paper/live operation.
- No packages installed; no environments modified (test run used the existing primary venv via `HERMES_PYTHON`).
- No temporary scripts left inside the repo (scratch evidence lives in `/tmp`).

## Unresolved operational dependency and retained docs-first block (acceptance criterion 4)

The ten-blocking readback is not a defect of committed Factory code; it is the documented stale-runtime condition: the primary checkout `/home/jean/Projects/hermes-agent-original` is 1696 commits behind `origin/main` (3 diverged local commits, merge-base `c846ccfb…`) and still runs the pre-R2v resolver at `4eb87e4cd4…`.

**Unresolved dependency:** the QA Guardian / primary-checkout owner must perform the bounded runtime catch-up of the primary checkout to `origin/main` `b260baea223e863b35fe561e6c5d3d77f3a914c9` (fetch + reset/merge policy decided by that owner; the 3 local-only commits at `4eb87e4cd4…` must be triaged first). This is the same dependency previously routed by R2c5 ("bounded technical rework (runtime catch-up of the primary checkout to origin/main)").

Implementation remains **blocked** behind that explicit operational dependency. This increment records immutable canonical readback evidence only (docs-first block retained); it does not self-approve, merge, or dispatch any downstream implementation.

## Evidence inventory

- `/tmp/r2cl-status-wt.json` — full status payload, worktree cwd (current code, 0/14 blocking).
- `/tmp/r2cl-status-primary.json` — full status payload, primary cwd (stale code, 10/14 blocking).
- `/tmp/r2cl-status-wt.log`, `/tmp/r2cl-status-primary.log` — text summary runs (77 lines each).
- `/tmp/r2cl-factory_pg-at-primary.py` — `hermes_cli/factory_pg.py` at `4eb87e4cd4…` (legacy resolver, no configured-base selection).
- `/tmp/r2cl-index-at-primary.md` — `DOCUMENTATION_INDEX.md` at `4eb87e4cd4…` (index table reviewed-col: yes for all 14).
- `/tmp/r2cl-tests-v.log` — focused regression run log (18✓ / 0✗).
- This document: `R2CL_CANONICAL_G1_STALE_PRIMARY_CHECKOUT_CONTROL_PLANE_RECOVERY.md`.

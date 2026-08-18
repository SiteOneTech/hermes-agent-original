---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2cm-repair-g1-review-state-provenance-a
phase: documentation
status: implemented_pending_independent_quality_review
validated: yes
reviewed: pending_independent_quality_review
owner: claude-builder
engine: claude_code
run_id: run-1786989852-98e47565
base_ref: origin/main
base_sha: 0ecd9019ba8ec111aaead60a911c9accd854f731
branch: factory/zeus-alpha-research-ledger-core/inc-001-r2cm-repair-g1-review-state-prov
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2cm-repair-g1-review-state-prov
canonical_factory_status_json_before: /tmp/r2cm-status-before.json
worktree_module_status_json_before: /tmp/r2cm-status-worktree-module-before.json
---

# R2cm — G1 review-state provenance repair after R2cl rate-limit failure

## Scope and boundary

This increment repairs the project-local documentation and review-state provenance for the R2cl handoff after the terminal quality-review path exhausted on MiniMax HTTP 429 and did not produce a durable independent verdict. It is documentation-only and limited to `factory/projects/zeus-alpha-research-ledger-core/`.

It does not change product code, Factory runtime code, the stale primary checkout, Agent Core `factory.*` rows by direct SQL, credentials, deployment, messaging/connectors, external runtimes, trading/risk/paper/live behavior, or QA Guardian merge state. It does not claim the R2cl review succeeded merely because the worker run was finalized or integrated.

## Required inputs read before repair

- `DOCUMENTATION_INDEX.md` — required entrypoint, G1 matrix, status semantics and R2cl lineage.
- Exact ten canonical blocking G1 docs from the assignment and readback: `FACTORY_INTAKE.md`, `REQUIREMENTS_ANALYSIS.md`, `PATTERN_ANALYSIS.md`, `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, `PRD.md`, `ADRS.md`, `METHODOLOGY_PLAN.md`, `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`, `SECURITY_GATES.md`.
- Control/evidence docs: `G0_REPOSITORY_STRATEGY.md`, `G1_REVIEW.md`, `TRACKER.md`, `QA_GATES.md`, `R2CL_CANONICAL_G1_STALE_PRIMARY_CHECKOUT_CONTROL_PLANE_RECOVERY.md`, `R2C5_INDEPENDENT_CURRENT_BASE_G1_REVIEW.md`, `R2BJ_BOUNDED_CANONICAL_G1_DOCUMENTATION_INDEX_RECOVERY.md`.
- Resolver code/tests: `hermes_cli/factory_pg.py` (`_document_frontmatter_flag`, `_configured_base_ref_readback`, `_primary_checkout_identity`, `project_document_status`) and `tests/hermes_cli/test_factory_control_plane_refactor.py` stale-primary/configured-base coverage.

## Branch and base identity captured before edits

Read-only Git evidence from the assigned worktree before documentation edits:

```text
worktree = /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2cm-repair-g1-review-state-prov
branch   = factory/zeus-alpha-research-ledger-core/inc-001-r2cm-repair-g1-review-state-prov
HEAD     = 0ecd9019ba8ec111aaead60a911c9accd854f731
origin/main = 0ecd9019ba8ec111aaead60a911c9accd854f731
remote   = https://github.com/SiteOneTech/hermes-agent-original.git
status   = clean before this documentation edit
```

The stale primary checkout remains outside this scope:

```text
primary_path = /home/jean/Projects/hermes-agent-original
primary_branch = main
primary_HEAD = 4eb87e4cd48105af05fe974cf1d493f0e1b57ae1
primary_state = main...origin/main [ahead 3, behind 1698]
```

## Canonical Factory readback before repair

The required canonical readback used only the venv wrapper specified for this task:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/hermes factory status zeus-alpha-research-ledger-core --json > /tmp/r2cm-status-before.json
```

Result:

```text
status_json = /tmp/r2cm-status-before.json
size = 2,564,246 bytes
db_backend = agent_core_postgres
database = zeus_agent
project_status = active
R2cl task = done
R2cm task = running
```

Exact ten blocking G1 rows before any edit:

| File | Missing/false field | Status path |
|---|---|---|
| `FACTORY_INTAKE.md` | `reviewed` | `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md` |
| `REQUIREMENTS_ANALYSIS.md` | `reviewed` | `factory/projects/zeus-alpha-research-ledger-core/REQUIREMENTS_ANALYSIS.md` |
| `PATTERN_ANALYSIS.md` | `reviewed` | `factory/projects/zeus-alpha-research-ledger-core/PATTERN_ANALYSIS.md` |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | `reviewed` | `factory/projects/zeus-alpha-research-ledger-core/ASSUMPTIONS_AND_OPEN_QUESTIONS.md` |
| `PRD.md` | `reviewed` | `factory/projects/zeus-alpha-research-ledger-core/PRD.md` |
| `ADRS.md` | `reviewed` | `factory/projects/zeus-alpha-research-ledger-core/ADRS.md` |
| `METHODOLOGY_PLAN.md` | `reviewed` | `factory/projects/zeus-alpha-research-ledger-core/METHODOLOGY_PLAN.md` |
| `TECHNICAL_BLUEPRINT.md` | `reviewed` | `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md` |
| `TASK_GRAPH.md` | `reviewed` | `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md` |
| `SECURITY_GATES.md` | `reviewed` | `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md` |

The same status JSON shows no R2cl/R2cm gate rows. R2cl has only task/run completion readback in this snapshot (`run-1786988140-ba3fb46e` and `run-1786989071-5d01a6b7` are `succeeded`; no quality gate exists for R2cl in the status payload). Therefore R2cl completion/integration is not independent review provenance.

## Resolver diagnosis and actual reviewed provenance

The canonical `venv/bin/hermes` readback above remains red because it reports the current live control-plane projection backed by the stale primary checkout state. The primary checkout at `4eb87e4cd4...` still has `reviewed: pending` frontmatter for all 14 required G1 documents, while current `origin/main` at `0ecd9019...` has `reviewed: yes` for the required G1 pack.

Read-only marker comparison:

```text
origin/main 0ecd9019...: required G1 frontmatter reviewed markers are reviewed: yes
primary HEAD 4eb87e4...: required G1 frontmatter reviewed markers are reviewed: pending
```

Diagnostic worktree-module readback used the same venv Python through the allowed Factory status module path from this assigned worktree:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2cm-status-worktree-module-before.json
```

Result:

```text
status_json = /tmp/r2cm-status-worktree-module-before.json
size = 2,579,372 bytes
all 14 required G1 rows: exists=true, indexed=true, committed=true, validated=true, reviewed=true, blocking=false
readiness_source = configured_base_ref
base_commit = 0ecd9019ba8ec111aaead60a911c9accd854f731
primary_checkout_accepted = false
primary_checkout_rejected_reason = primary_checkout_not_configured_base
active reconciliation_projection_source = current_document_status
```

This confirms the R2cl technical class remains the same: current committed resolver code can read the configured base without mutating primary; the canonical wrapper still exposes the stale primary projection until the primary checkout/runtime source is caught up. R2cm does not change that status field directly.

The reviewed provenance for the existing G1 frontmatter is unchanged and remains the earlier independent source chain, not R2cl:

```text
reviewed_by = solution-architect
review_evidence = factory_gate_794
reviewed_candidate_pr = https://github.com/SiteOneTech/hermes-agent-original/pull/36
reviewed_candidate_sha = c81547062c5362a7be6f5a1bb2ef9612b29bac9c
reviewed_source_gate = factory_gate_790
reviewed_source_sha = 2476e978c545e24b18ee48844b24eb8c58245ab4
```

R2cm therefore does not alter the ten G1 files' `reviewed: yes` markers. Those markers have real independent provenance. The repair is to stop treating R2cl's unfinished/rate-limited review path as a settled review conclusion or as a reason to skip PR-first provenance repair.

## R2cl review-state correction

R2cl's document frontmatter already says `reviewed: pending_independent_quality_review`, but several project-local summaries presented its author finding as terminal: “no code defect, no PR warranted.” After the MiniMax HTTP 429 exhaustion in the terminal quality-review path, that statement must be read only as an unreviewed technical hypothesis from the R2cl worker, not as a completed independent review outcome.

Corrected interpretation:

- R2cl may remain historical diagnostic evidence for the stale-primary resolver/source-root class.
- R2cl is not a completed independent quality review and cannot be used as R2cm/R2cl approval evidence.
- The canonical venv wrapper still reports the ten `reviewed=false` blockers, so the project remains docs-first blocked in the canonical readback until QA Guardian/authorized control-plane work catches up the primary/runtime source or otherwise records an approved readback path.
- This R2cm branch is the PR-first provenance repair. It must receive a real independent exact-SHA review; if that review again hits provider/rate-limit exhaustion, the artifact must remain `reviewed: pending` and not be auto-green.

## Tests and validation contract

Executed focused resolver/document-status validation for this documentation-only repair:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 \
  scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py \
  -k "configured_origin_base or stale_primary or configured_base_ref or reviewed_g1_candidate or unvalidated_required_docs_reconciliation or clears_stale_g1_checkout_projection or dispatch_preflight_blocks_product_execution"
```

Result:

```text
Discovered 1 test files (~119 tests) under ['tests/hermes_cli/test_factory_control_plane_refactor.py']; running with -j 48
[100.0% |   119/~119 | ✓18 | ✗ 0] ✓ tests/hermes_cli/test_factory_control_plane_refactor.py (18✓, 4.0s)
=== Summary: 1 files, 18 tests passed, 0 failed (100% complete) in 4.0s (48 workers) ===
```

This is the focused resolver/document-status suite for the R2cl/R2cm class. It verifies configured-origin-base, stale-primary rejection, reviewed-candidate fail-closed/readback, stale G1 checkout projection cleanup, and dispatch preflight behavior. R2cm adds no production code, so no RED/GREEN code change is expected.

Post-repair canonical status readback was re-run with the required venv wrapper:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/hermes factory status zeus-alpha-research-ledger-core --json > /tmp/r2cm-status-after.json
```

Result: `/tmp/r2cm-status-after.json` is 2,565,476 bytes; status remains truthful/red with `reconciliation_anomalies=["unvalidated_required_docs"]`, `reconciliation_required=true`, and exactly the same ten required G1 rows blocking on `reviewed=false`: `FACTORY_INTAKE.md`, `REQUIREMENTS_ANALYSIS.md`, `PATTERN_ANALYSIS.md`, `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, `PRD.md`, `ADRS.md`, `METHODOLOGY_PLAN.md`, `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`, `SECURITY_GATES.md`.

Post-repair worktree-module diagnostic readback was also re-run:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2cm-status-worktree-module-after.json
```

Result: `/tmp/r2cm-status-worktree-module-after.json` is 2,579,714 bytes; it reports `reconciliation_anomalies=[]`, `reconciliation_projection_source=current_document_status`, `g1_blocking_count=0`, all 14 required G1 rows `reviewed=true`, `blocking=false`, `readiness_source=configured_base_ref`, base `0ecd9019ba8ec111aaead60a911c9accd854f731`, primary rejected as `primary_checkout_not_configured_base`.

## No-mutation compliance

- No primary checkout mutation.
- No direct SQL / psql / psycopg2 / ad-hoc scripts against `factory.*`.
- No merge, deploy, credential access/change, external runtime, connector/messaging, trading/risk/paper/live action.
- No package installation or environment mutation.
- Scratch evidence is in `/tmp`; project changes are versioned Markdown only.

## Handoff

Open a Zeus-signed, `agent:zeus` GitHub PR from branch `factory/zeus-alpha-research-ledger-core/inc-001-r2cm-repair-g1-review-state-prov` to `main`. The PR body must name the exact final head SHA, the canonical red readback `/tmp/r2cm-status-before.json`, focused resolver test output, and the no-merge/no-primary-mutation/no-direct-SQL boundary. QA Guardian remains the mandatory next approval; this worker must not merge.

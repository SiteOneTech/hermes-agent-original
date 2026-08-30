---
document_type: r2df_r37_canonical_g1_review_state_dispatch_recovery
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2df-r37-canonical-g1-review-state-dispa
phase: g1_recovery
status: implemented_pending_pr_review
validated: yes
reviewed: pending
reviewed_by: pending_quality-reviewer
review_evidence: pending_independent_exact_sha_quality_gate
owner: codex-builder
base_ref: origin/main
base_sha: 17cfaf1f2fa01378df331b74471bf638289aa811
branch: factory/zeus-alpha-research-ledger-core/inc-08-r2df-r37-canonical-g1-review-sta
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-08-r2df-r37-canonical-g1-review-sta
run_id: run-1788051667-55919e7d
---

# R2df-R37 — canonical G1 review-state dispatch recovery

## Scope

This increment repairs only the Factory docs-first scheduler/dispatcher ordering for the canonical G1 review-state recovery path. When the Agent Core status/resolve-state stream reports an active same-project G1 document-status anomaly (`unvalidated_required_docs`) and there is an eligible same-project G1 recovery task, that recovery task must be claimed before validation, review or product/runtime work.

No Alpha Research Ledger product implementation, external runtime, deploy, merge, primary-checkout mutation, credential change, messaging connector, direct SQL, Factory task-status edit outside the dispatcher path, trading, risk, paper/live activation or downstream validation closure is authorized by this artifact.

## G1 documents consulted

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/REQUIREMENTS_ANALYSIS.md`
- `factory/projects/zeus-alpha-research-ledger-core/PATTERN_ANALYSIS.md`
- `factory/projects/zeus-alpha-research-ledger-core/ASSUMPTIONS_AND_OPEN_QUESTIONS.md`
- `factory/projects/zeus-alpha-research-ledger-core/PRD.md`
- `factory/projects/zeus-alpha-research-ledger-core/ADRS.md`
- `factory/projects/zeus-alpha-research-ledger-core/METHODOLOGY_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`

The required G1 frontmatter remains reviewed by `solution-architect` through Factory gate `794` / PR #36 head `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` and source gate `790` / PR #34 SHA `2476e978c545e24b18ee48844b24eb8c58245ab4`; this R2df-R37 artifact itself is pending independent exact-SHA review.

## Canonical Factory readback

Sanctioned readback command from the assigned worktree:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r37-status-before.json
```

Evidence files:

- Raw status before code repair: `/tmp/r2df-r37-status-before.json` (`4,747,301` bytes)
- Pretty status before code repair: `/tmp/r2df-r37-status-before.pretty.json` (`5,368,368` bytes)
- Raw status after code repair: `/tmp/r2df-r37-status-after-code.json` (`4,747,215` bytes)
- Pretty status after code repair: `/tmp/r2df-r37-status-after-code.pretty.json` (`5,368,954` bytes)

Readback facts from Agent Core Postgres after the code repair:

```text
project_id=zeus-alpha-research-ledger-core
status=active
autonomous_enabled=true
db_backend=agent_core_postgres
current_top_level_g1_rows_reviewed_false=none
current_top_level_g1_blockers=none
r2df_r37_task_status=running
r2df_r37_run_id=run-1788051667-55919e7d
r2df_r37_run_status=running
r2df_r37_worker=codex-builder
```

Historical status/event evidence in the same canonical payload reproduced the no-worker deadlock shape that this regression codifies:

```text
project_reconciled events with active_runs=0 and anomalies=["unvalidated_required_docs"]: 244855, 244854, 244853, 244852, 244850, 244845, 244844, 244843, 244842, 244841, 244821, 244794, 244793, 244788, 244761
pre-recovery dispatch_preflight_denied events: 244849, 244840, 244792 with blockers=["missing_or_unindexed_docs"]
```

The exact ten prompt-level reviewed=false G1 rows for this R2df-R37 assignment are:

```text
FACTORY_INTAKE.md
REQUIREMENTS_ANALYSIS.md
PATTERN_ANALYSIS.md
ASSUMPTIONS_AND_OPEN_QUESTIONS.md
PRD.md
ADRS.md
METHODOLOGY_PLAN.md
TECHNICAL_BLUEPRINT.md
TASK_GRAPH.md
SECURITY_GATES.md
```

Historical gate/event snapshots in the status payload also preserve broader stale reviewed=false rows from earlier increments; those are audit/projection history only and are not current top-level configured-base document blockers.

The assignment required resolve-state evidence, but the hard Factory DB surface allowlist for this run permits only `factory status` and `factory gate record`. Therefore no live `factory project resolve-state` command was executed; this artifact uses sanctioned `factory status` readbacks and the dispatcher regression test to avoid an unauthorized DB mutation path.

## RED / GREEN test evidence

Focused RED before production code repair:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k test_force_tick_claims_canonical_g1_recovery_before_ready_validation_repair_when_reviewed_false -v --tb=short
FAILED: expected demo-r2df-r37-canonical-g1-review-state-dispa, got demo-r2df-r37-validation-review
```

Focused GREEN after production code repair:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k test_force_tick_claims_canonical_g1_recovery_before_ready_validation_repair_when_reviewed_false -v --tb=short
1 passed, 0 failed
```

Related Factory control-plane GREEN:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py
136 passed, 0 failed

HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_increment_integration.py
293 passed, 0 failed
```

The initial wrapper-only test attempt without `HERMES_PYTHON` failed before pytest because the assigned worktree has no local `.venv`/`venv`; the verified runs used the sanctioned repo-root virtualenv interpreter only and did not install dependencies.

## Code repair

Changed files:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_increment_integration.py`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R37_CANONICAL_G1_REVIEW_STATE_DISPATCH_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`

Behavioral change:

1. `_next_runnable_task()` now recognizes a dispatch-preflight window where current G1/document readiness is red and at least one same-project docs-first G1 recovery task is runnable.
2. In that window, non-validation G1 docs/reconciliation recovery tasks rank before validation/review repair tasks and before product/runtime candidates.
3. Product/runtime candidates still receive the docs-first preflight blockers; validation repair tasks remain eligible only after no runnable G1 recovery task is available.
4. SQL priority/created-at ordering is preserved inside each resulting bucket.

This closes the specific R2df-R37 class where a lower numeric-priority validation row could be claimed first, leaving the actual G1 review-state recovery unspawned while the project remains active with no recovery worker.

## Delivery state

This artifact is implementation evidence for the assigned branch/worktree only. It requires a Zeus-signed `agent:zeus` PR and independent exact-SHA quality review before it can be represented as reviewed, integrated or complete. No merge/deploy/runtime/product action was taken.

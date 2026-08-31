---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2df-r48-current-origin-r47-clean-worktr
run_id: run-1788160940-42e8852a
phase: g1_recovery
status: implemented_pending_pr_and_independent_exact_sha_review
validated: yes
reviewed: pending_independent_exact_sha_review
owner: codex-builder
reviewer: quality-reviewer
base_ref: origin/main
base_sha: 7e26fd60dc73643a7755b227dcf4968b007678bf
branch: factory/zeus-alpha-research-ledger-core/inc-102-r2df-r48-current-origin-r47-recovery
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-102-r2df-r48-current-origin-r47-recovery
---

# R2df-R48 — current-origin R47 clean-worktree PR provenance recovery

## Scope and boundary

R2df-R48 is a bounded Factory scheduler/control-plane recovery. It uses the freshly assigned worktree from current `origin/main`, rejects the older R47 worktree as a delivery/review candidate, and carries forward only the explicit G1/documentation recovery validation-preflight behavior while hardening metadata scope fail-closed detection.

Changed files are limited to:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_increment_integration.py`
- project-local evidence under `factory/projects/zeus-alpha-research-ledger-core/`

This increment does not add or alter Alpha Research Ledger product/runtime code, providers, migrations, tools, schedulers beyond Factory control-plane task classification, credentials, messaging connectors, deployment behavior, external runtime, primary checkout state, G1 reviewed frontmatter markers, task status, R44, PR #138, stale refs/PRs, direct Factory DB state, Vonash/Magnus/VAOS/RAG/KB/broker/trading/risk, or paper/live behavior.

## Canonical inputs consulted

Required Factory/G1 inputs read from the assigned worktree before implementation:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R43_G1_RECOVERY_SELECTION_STARVATION_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R45_STALE_CANONICAL_FACTORY_CLI_BOOTSTRAP_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R47_ISOLATED_R44_SCHEDULER_FIX_PR_RECOVERY.md`

Agent Core Postgres `factory.*` remains the operational source of truth. This document is project-local evidence and does not substitute for Factory DB gate/readback records.

## Current-origin worktree evidence before changes

Fresh `git fetch origin main --prune` and assigned-worktree identity before code edits:

```text
From https://github.com/SiteOneTech/hermes-agent-original
 * branch                  main       -> FETCH_HEAD
branch=factory/zeus-alpha-research-ledger-core/inc-102-r2df-r48-current-origin-r47-recovery
HEAD=7e26fd60dc73643a7755b227dcf4968b007678bf
origin_main=7e26fd60dc73643a7755b227dcf4968b007678bf
merge_base=7e26fd60dc73643a7755b227dcf4968b007678bf
status=
## factory/zeus-alpha-research-ledger-core/inc-102-r2df-r48-current-origin-r47-recovery...origin/main
remote=
origin	https://github.com/SiteOneTech/hermes-agent-original.git (fetch)
origin	https://github.com/SiteOneTech/hermes-agent-original.git (push)
upstream	https://github.com/NousResearch/hermes-agent.git (fetch)
upstream	https://github.com/NousResearch/hermes-agent.git (push)
```

Current `origin/main` includes the R47 merge commit:

```text
7e26fd60dc (HEAD, origin/main, origin/HEAD) Merge Factory increment zeus-alpha-research-ledger-core-r2df-r47-isolated-r44-scheduler-fix-pr-r into main
e3aef1a698 (origin/factory/zeus-alpha-research-ledger-core/inc-101-r2df-r47-isolated-r44-scheduler) fix(factory): recover explicit g1 scheduler preflight
654907e0ca Merge remote-tracking branch 'upstream/main' into resolver/upstream-20260831-054616
```

The previous R47 worktree is not the R48 review/delivery candidate. Read-only identity check during this run:

```text
stale_r47_worktree=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-101-r2df-r47-isolated-r44-scheduler
branch=factory/zeus-alpha-research-ledger-core/inc-101-r2df-r47-isolated-r44-scheduler
HEAD=e3aef1a698cbe88973cd40714ce70ffdb8e98241
origin_main=7e26fd60dc73643a7755b227dcf4968b007678bf
merge_base=e3aef1a698cbe88973cd40714ce70ffdb8e98241
ahead_behind=0	1
status_short=
```

R2df-R48 makes no review or delivery claim from that stale/non-assigned R47 tree.

## Canonical Factory readback

Allowed command from the assigned worktree:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r48-status-before.json
/home/jean/Projects/hermes-agent-original/venv/bin/python -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r48-status-after-code.json
```

Summarized readback before and after code/tests:

```text
db_backend=agent_core_postgres
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-102-r2df-r48-current-origin-r47-recovery
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-102-r2df-r48-current-origin-r47-recovery
factory_status_delegated=false
project_status=active
autonomous_enabled=true
reconciliation_anomalies=[]
g1_required_count=14
g1_blocking_count=0
readiness_sources=["configured_base_ref"]
base_commits=["7e26fd60dc73643a7755b227dcf4968b007678bf"]
task_status=running
task_phase=g1_recovery
task_owner=codex-builder
task_branch=factory/zeus-alpha-research-ledger-core/inc-102-r2df-r48-current-origin-r47-recovery
```

No `psql`, `psycopg2`, ad-hoc DB script, direct SQL, `factory task close`, `factory project tick`, `factory worker dispatch`, merge, deploy, credential change, external runtime, or product dispatch was executed by this worker. Factory DB interaction was limited to sanctioned `factory status` readback before gate recording.

## RED reproduction

The current-origin R47 baseline already contains the explicit recovery path from R44/R47. The R47 artifact records the original RED reproduction against pre-repair code: `test_claim_next_task_allows_metadata_documentation_recovery_past_validation_readiness` selected a metadata-classified no-product/no-runtime G1 documentation recovery while G1 was red, then rejected it solely through `unresolved_validation_tasks`; companion validation/reporting fail-closed coverage showed phase-only `g1_recovery` was too broad.

R2df-R48 adds the missing current-origin fail-closed metadata-scope regression. RED before the code repair:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'metadata_scope_keeps_product_runtime_and_external_work_fail_closed' -v --tb=short
Result: 1 failed, 138 deselected.
Failure: test_g1_recovery_metadata_scope_keeps_product_runtime_and_external_work_fail_closed asserted that metadata {documentation_recovery: true, scope: "ALR-020"} must not be treated as explicit G1 recovery; pre-repair `_is_explicit_g1_recovery_task()` returned True.
```

This proves the R47-style explicit metadata exemption still needed current-origin hardening so structured product/runtime/external/direct-SQL scope cannot bypass validation readiness when task prose is otherwise documentation-like.

## GREEN repair

Changed behavior in `hermes_cli/factory_pg.py`:

- Adds metadata-key normalization for dispatch scope keys.
- Treats positive structured metadata keys such as `direct_sql`, `external_runtime_scope`, `product_scope`, `runtime_scope`, `alr_scope`, `dispatch_scope`, `integration_scope`, `delivery_scope`, `target_scope`, and `work_scope` as product/runtime scope when their values name ALR/product/runtime/deploy/direct-SQL/messaging/trading/risk/paper-live/base-branch integration work.
- Ignores negative guardrail keys (`no_*`, `non_*`, `not_*`, `without_*`) so explicit no-product/no-runtime G1/documentation recovery remains eligible.
- Reuses the existing positive-scope checks in `_is_explicit_g1_recovery_task()` and `_candidate_requires_validation_readiness_before_dispatch()` so the exemption remains explicit phase/metadata-based and restricted to G0/G1/planning/documentation recovery.

Preserved fail-closed behavior:

- Product and ALR scope remain validation-readiness gated.
- QA, quality review, security review, reporting, delivery, deploy, runtime, external execution, messaging, direct-SQL, trading/risk/paper-live, and base-branch integration scopes remain fail-closed.
- The repair does not widen any product/runtime/ALR dispatch path.

## Verification

Commands run from the assigned worktree with the hermetic wrapper:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 HERMES_TEST_WORKERS=1 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'metadata_scope_keeps_product_runtime_and_external_work_fail_closed or metadata_documentation_recovery_past_validation_readiness or g1_recovery_metadata_keeps_validation_and_reporting_work_fail_closed' -v --tb=short
Result: 3 tests passed, 0 failed; FOCUSED_EXIT=0.

HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 HERMES_TEST_WORKERS=1 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_increment_integration.py -v --tb=short
Result: 320 tests passed, 0 failed; RELATED_EXIT=0.

git diff --check
Result: exit 0.
```

## PR-first handoff

This artifact is candidate evidence only. The final candidate commit SHA, pushed branch, PR URL, and Factory gate evidence are recorded after commit/push because a commit cannot contain its own SHA. Independent exact-SHA quality review by a separate reviewer remains required before merge, closure, or downstream Factory control relies on this repair.

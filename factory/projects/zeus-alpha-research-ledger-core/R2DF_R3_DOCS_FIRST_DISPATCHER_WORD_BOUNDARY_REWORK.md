---
document_type: docs_first_dispatcher_word_boundary_rework
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2df-r3-docs-first-dispatcher-word-bound
run_id: run-1787243609-c9aec38d
phase: documentation
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending_independent_exact_sha_quality_review
owner: codex-builder
base_ref: origin/main
base_sha: 71e5e7b2f4ace3b081f9446483784a3c5fb0b981
branch: factory/zeus-alpha-research-ledger-core/inc-018-r2df-r3-docs-first-dispatcher-wo
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2df-r3-docs-first-dispatcher-wo
created_at: 2026-08-20T12:40:56-04:00
---

# R2df-R3 — docs-first dispatcher word-boundary rework

## Scope and boundary

R2df-R3 is a bounded Factory control-plane repair for the validation-readiness dispatch classifier. It changes only:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_control_plane_refactor.py`
- project-local Factory evidence under `factory/projects/zeus-alpha-research-ledger-core/`

No Alpha Ledger product/runtime implementation, provider/model/auth config, database migration, tool registration, scheduler, deployment, credential access, messaging connector, external runtime, primary-checkout mutation, task-status mutation, direct SQL, merge, Vonash, Magnus, VAOS, RAG/KB, broker, trading, risk, paper/live activation, or external-system operation is authorized or performed by this increment.

## Canonical inputs read before implementation

Required G1/documentation inputs consulted from the assigned worktree:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DL_G1_DOCUMENTATION_DISPATCH_VALIDATOR_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DH_DOCS_FIRST_CURRENT_BASE_G1_REVIEW_STATE_DISPATCH_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DI_DOCS_FIRST_FAIL_CLOSED_REVIEW_TERMINALIZATION_AND_DISPATCH_REPAIR.md`

Agent Core Postgres `factory.*` remains the operational source of truth; this file is project-local evidence, not a DB substitute.

## Current base and Factory readback

Current worktree identity before code edits and evidence update:

- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2df-r3-docs-first-dispatcher-wo`
- Branch: `factory/zeus-alpha-research-ledger-core/inc-018-r2df-r3-docs-first-dispatcher-wo`
- Remote: `https://github.com/SiteOneTech/hermes-agent-original.git`
- `git rev-parse HEAD`: `71e5e7b2f4ace3b081f9446483784a3c5fb0b981`
- `git rev-parse origin/main`: `71e5e7b2f4ace3b081f9446483784a3c5fb0b981`
- `git merge-base HEAD origin/main`: `71e5e7b2f4ace3b081f9446483784a3c5fb0b981`

Allowed Factory status command from the assigned worktree:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r3-status-after.json`

Summarized readback:

- Status JSON: `/tmp/r2df-r3-status-after.json` (`4,095,288` bytes)
- `db_backend=agent_core_postgres`, `database=zeus_agent`
- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2df-r3-docs-first-dispatcher-wo`
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2df-r3-docs-first-dispatcher-wo`
- `factory_status_delegated=false`
- `project_id=zeus-alpha-research-ledger-core`, `status=active`
- active `reconciliation_anomalies=["pending_effective_gates"]`
- active `reconciliation_projection_source=current_document_status`
- G1 required rows: `14`
- G1 blocking rows: `0`
- `readiness_source=configured_base_ref`
- `base_commit=71e5e7b2f4ace3b081f9446483784a3c5fb0b981`
- stale primary checkout rejected with `primary_checkout_not_configured_base`
- active R2df-R3 task readback: `status=running`, owner `codex-builder`, reviewer `quality-reviewer`, branch/worktree matching this increment.

## Defect reproduced

R2dl fixed the broad `final` substring path, but the classifier still treated any candidate with explicit final-stage phrases as validation-dependent before checking whether that candidate was itself a documentation/reconciliation recovery. The current R2df recovery context can contain copied historical final-delivery/report/gate-closure wording without being the final report stage.

With unrelated validation work still open, `_next_runnable_task()` skipped the dependency-ready R2df documentation/reconciliation recovery and selected the unresolved validation task instead. That reproduces the docs-first dispatcher deadlock: a recovery needed to reconcile Factory documentation state is held behind validation rows that are not prerequisites for running the recovery.

Focused RED test added before implementation:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'incidental_final_report_language' -v --tb=short`

RED result: `1 failed, 158 deselected`; failure showed the dispatcher selecting `demo-alr-063-security-review` instead of `demo-r2df-docs-first-dispatcher-recovery`.

## Repair

The validation-readiness classifier now checks task kind before final-stage text:

- validation tasks remain dispatchable and do not wait on themselves;
- explicit Factory reconciliation/runtime-bootstrap recovery stays runnable;
- documentation/planning/G0/G1 recovery tasks with word-bounded documentation/recovery terms stay runnable even when their context contains incidental final-report wording;
- final-stage phrases are matched with word-bounded regexes rather than loose substring matches;
- phase-based delivery matching is narrowed from broad `startswith("delivery")` to `phase == "delivery"` or `phase.startswith("delivery_")`.

Preserved fail-closed behavior:

- genuine final delivery/report/release stages still require validation-readiness before dispatch;
- an unresolved validation task is still selected ahead of a final report stage when validation is incomplete;
- docs-first product gating for implementation, QA, security, delivery, deploy, and release work remains in `_dispatch_preflight_blockers()` and was not relaxed;
- active validation tasks themselves remain recognized by `_is_validation_task()` and `_validation_task_readiness_findings()`.

## Verification evidence

RED evidence:

- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'incidental_final_report_language' -v --tb=short`
- Result: `1 failed, 158 deselected`; selected task was `demo-alr-063-security-review` instead of `demo-r2df-docs-first-dispatcher-recovery`.

Focused GREEN evidence after implementation:

- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'validation_readiness' -v --tb=short`
- Result: `4 tests passed, 0 failed`.

Related Factory control-plane GREEN evidence:

- Command: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_increment_integration.py -v`
- Result: `3 files, 305 tests passed, 0 failed`.

Canonical Factory status readback after implementation:

- Command: `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r3-status-after.json`
- Result: exit `0`; Agent Core Postgres, worktree source roots, `factory_status_delegated=false`, 14/14 required G1 rows non-blocking from `configured_base_ref` at base `71e5e7b2f4ace3b081f9446483784a3c5fb0b981`, active `reconciliation_anomalies=["pending_effective_gates"]`.

Diff/tracking validation:

- `git diff --check` must exit `0` before PR handoff.
- Final exact pushed SHA and PR readback are recorded outside this commit because a commit cannot contain its own final SHA.

## Delivery state

This candidate is implemented, validated, and committed as the local delivery candidate, but remains pending push, PR creation, Factory gate evidence, and independent exact-SHA review of the final pushed head. The PR must be non-draft, labeled `agent:zeus`, Zeus-signed, and must record the exact source SHA plus the independent quality-review path (`quality-reviewer` against the final PR head). This artifact does not self-approve, merge, deploy, mutate task status, mutate primary checkout, or authorize ALR-020/product/runtime dispatch.

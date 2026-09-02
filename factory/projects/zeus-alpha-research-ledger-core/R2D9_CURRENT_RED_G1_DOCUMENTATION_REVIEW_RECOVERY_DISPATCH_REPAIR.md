---
document_type: current_red_g1_documentation_review_recovery_dispatch_repair
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2d9-current-red-g1-documentation-review
run_id: run-1788349280-dcfc24f3
phase: g1_recovery
status: implemented_pending_pr_and_independent_exact_sha_review
validated: yes
reviewed: pending_independent_exact_sha_quality_review
owner: codex-builder
base_ref: origin/main
base_sha: a7e3a54f7ee54e27b4fbdc7ffa2e6808ece0f872
branch: factory/zeus-alpha-research-ledger-core/inc-110-r2d9-current-red-g1-documentatio
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-110-r2d9-current-red-g1-documentatio
created_at: 2026-09-02T11:55:30Z
---

# R2d9 — current red-G1 documentation-review recovery dispatch repair

## Scope and boundary

R2d9 is a bounded same-project Factory control-plane scheduler/preflight repair for `zeus-alpha-research-ledger-core`. It addresses the red-G1 condition where docs-first dispatch left eligible documentation-review recovery work unclaimed while product, ALR, QA and delivery rows remained denied.

This increment modifies only Factory scheduler classification and hermetic regression tests:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_increment_integration.py`
- this project-local evidence artifact

No Alpha Ledger product code, merge, deploy, direct SQL, primary checkout mutation, credential change, external runtime, messaging, trading, risk, paper/live activation, or external dispatch is performed or authorized.

## Canonical documents read before implementation

Required G1/project sources used for this increment:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2D1_CURRENT_BASE_EXPLICIT_G1_VALIDATION_GATE_DISPATCH_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2D6_REPAIR_RECURRENT_G1_RECOVERY_SELF_DENIAL.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2D7_G1_PREFLIGHT_TERMINAL_WORD_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R43_G1_RECOVERY_SELECTION_STARVATION_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R47_ISOLATED_R44_SCHEDULER_FIX_PR_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2DF_R48_CURRENT_ORIGIN_R47_CLEAN_WORKTREE_PR_PROVENANCE_RECOVERY.md`

Agent Core Postgres `factory.*` remains the canonical source of truth. This Markdown file is project-local evidence only.

## Worktree and base identity

Readback before final delivery commit:

- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-110-r2d9-current-red-g1-documentatio`
- Branch: `factory/zeus-alpha-research-ledger-core/inc-110-r2d9-current-red-g1-documentatio`
- Remote: `https://github.com/SiteOneTech/hermes-agent-original.git`
- `git rev-parse HEAD`: `a7e3a54f7ee54e27b4fbdc7ffa2e6808ece0f872`
- `git rev-parse origin/main`: `a7e3a54f7ee54e27b4fbdc7ffa2e6808ece0f872`
- `git merge-base HEAD origin/main`: `a7e3a54f7ee54e27b4fbdc7ffa2e6808ece0f872`

The final candidate commit SHA cannot be embedded in the same commit without changing the commit identity; it must be recorded in the Factory gate record, PR body, and final worker evidence after commit creation.

## Canonical Factory status/readback evidence

Allowed status command run from the assigned worktree:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2d9-status-current.json`

Readback facts:

- Raw status path: `/tmp/r2d9-status-current.json`
- Raw status size: `4,849,328` bytes
- `db_backend=agent_core_postgres`
- `factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-110-r2d9-current-red-g1-documentatio`
- `factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-110-r2d9-current-red-g1-documentatio`
- `factory_status_delegated=false`
- Project status: `active`; `autonomous_enabled=true`
- Task counts: `blocked=14,cancelled=27,done=127,ready=3,running=1,superseded=11,todo=12`
- Active runs: `1`
- Current task: `zeus-alpha-research-ledger-core-r2d9-current-red-g1-documentation-review`, `status=running`, `phase=g1_recovery`, `claimed_by=factory-force-tick`, `run_id=run-1788349280-dcfc24f3`, `run_status=running`, `run_commit_sha=null`
- Active metadata readback: `reconciliation_anomalies=[]`, `reconciliation_projection_source=current_document_status`
- Current document rows: `22`; G1 required rows: `14`; G1 required blockers: `0`; missing-reviewed rows: `0`; readiness source: `configured_base_ref`; base commit: `a7e3a54f7ee54e27b4fbdc7ffa2e6808ece0f872`

Status events also preserve the red-G1/no-active-run resolve-state evidence that motivated this run:

- `2026-09-02T11:40:01.49959+00:00` `project_reconciled`: `active_runs=0`, `anomalies=["unvalidated_required_docs"]`, task counts `blocked=14,cancelled=27,done=127,ready=3,superseded=11,todo=12`.
- `2026-09-02T11:41:09.998068+00:00` and `2026-09-02T11:41:12.553148+00:00` `project_reconciled`: `active_runs=0`, `anomalies=["unvalidated_required_docs"]`, task counts include `todo=13` after this recovery task was created.
- `2026-09-02T11:41:19Z` dispatch-preflight events denied product/QA/downstream work (`R2df-R39`, `R2df-R23`, `R2df-R17`, `R2df fresh current-base documentation`) with unresolved validation or missing docs blockers.
- `2026-09-02T11:41:20.361492+00:00` `task_claimed`: `zeus-alpha-research-ledger-core-r2d9-current-red-g1-documentation-review` claimed for `codex-builder`, metadata `run_id=run-1788349280-dcfc24f3`.

No new live `factory project tick` or `factory project resolve-state` command was executed by this worker because the run's DB-write allowlist is limited to `factory status` and `factory gate record`. The readback above comes from the sanctioned `factory status` payload and its Agent Core event/task/run projections.

## Defect reproduced

The failing behavior is a scheduler classification gap, not Alpha Ledger product behavior. A red-G1 project can contain:

- G1 required documents that are not currently dispatch-ready from the docs-first projection.
- Product/ALR/QA/delivery rows that must remain fail-closed.
- A same-project, bounded documentation-review recovery row whose eligibility is expressed by explicit phase/metadata rather than by title/status prose.

Before the repair, the explicit `phase=documentation_review` and `metadata.documentation_review_recovery=true` signal was not included in the G1/documentation recovery predicates. The docs-first preflight therefore treated that bounded recovery row like ordinary Codex/product dispatch noise and allowed `force_tick()` to return `claimed=None` under the red-G1/no-active-run condition.

## Repair

`hermes_cli/factory_pg.py` now treats these explicit structured signals as documentation recovery scope:

- phase signal `documentation_review`
- phase signal `documentation_review_recovery`
- phase signal `docs_review`
- phase signal `docs_review_recovery`
- metadata `documentation_review_recovery=true`
- metadata `g1_documentation_review_recovery=true`
- metadata `docs_review_recovery=true`

The existing fail-closed checks are unchanged for positive product/runtime scope. A candidate carrying the documentation-review recovery metadata plus `scope=ALR-020`, or ordinary product/QA/delivery phases, still receives `missing_or_unindexed_docs` while G1 is red.

## TDD evidence

RED command before implementation:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k test_force_tick_claims_documentation_review_recovery_from_explicit_phase_metadata -v --tb=short`

RED result: `1 failed, 145 deselected`; failure at `assert tick["claimed"] is not None`, proving `force_tick()` returned no claimed task for the explicit documentation-review recovery candidate in the red-G1/no-active-run fixture.

GREEN focused command after implementation:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k test_force_tick_claims_documentation_review_recovery_from_explicit_phase_metadata -v --tb=short`

GREEN focused result: `1 tests passed, 0 failed`.

Broader focused Factory command:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py`

Broader focused result: `146 tests passed, 0 failed`.

Final related Factory validation command after project-local evidence updates:

`git diff --check && HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_control_plane_refactor.py`

Final related Factory validation result: `2 files, 307 tests passed, 0 failed`; `git diff --check` produced no whitespace errors.

## Acceptance mapping

- RED reproduction: `test_force_tick_claims_documentation_review_recovery_from_explicit_phase_metadata` builds a hermetic red-G1 payload with `active_runs=0`, blocker rows missing `reviewed`, product/QA/delivery candidates, and one explicit `phase=documentation_review` + `metadata.documentation_review_recovery=true` recovery task. The pre-repair result is `tick["claimed"] is None`.
- GREEN selection: the repair uses only phase and structured metadata signals; the test title deliberately remains generic (`R2d9 scheduler candidate`) so title/status prose is not the source of eligibility.
- Fail-closed product/ALR/QA/delivery: the same test asserts product, QA, delivery, and an ALR-scoped documentation-review recovery candidate still return `missing_or_unindexed_docs` under red G1.
- Evidence: this artifact records the exact base SHA, current status readback, resolve-state/project-reconciled readbacks, task-claim forced-tick readback, and test commands/results. The exact final candidate SHA is recorded after commit creation in the Factory gate/PR/final response.
- Delivery: PR-first only; no merge, deploy, direct SQL, primary checkout mutation, external runtime, messaging, credential change, product execution, or self-approval.

## Delivery state

This candidate is implemented locally and remains `reviewed: pending` until the assigned branch is pushed as a Zeus-signed `agent:zeus` PR and an independent reviewer records an exact-SHA quality verdict. It is not merged, deployed, or product-authorized by this artifact.

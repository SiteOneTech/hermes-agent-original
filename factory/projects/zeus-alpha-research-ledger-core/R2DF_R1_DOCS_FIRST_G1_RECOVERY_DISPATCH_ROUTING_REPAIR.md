---
document_type: docs_first_g1_recovery_dispatch_routing_repair
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2df-r1-docs-first-g1-recovery-dispatch-
run_id: run-1787285938-9f09faba
phase: g1_recovery
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending
owner: claude-builder
base_ref: origin/main
base_sha: 268d3c8ee7bab61304c7ab05cad22d693c70ba7d
branch: factory/zeus-alpha-research-ledger-core/inc-001-r2df-r1-docs-first-g1-recovery-d
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2df-r1-docs-first-g1-recovery-d
created_at: 2026-08-21T00:00:00Z
---

# R2df-R1 — docs-first G1 recovery dispatch routing repair

## Scope and boundary

R2df-R1 is a bounded Factory control-plane repair for the G1/docs-first dispatcher path. It changes only:

- `hermes_cli/factory_pg.py`
- `tests/hermes_cli/test_factory_increment_integration.py`
- project-local Factory evidence under `factory/projects/zeus-alpha-research-ledger-core/`

No Alpha Ledger product/runtime code, provider/model/auth config, database migration, tool registration, scheduler, deployment, credential access, messaging connector, external runtime, primary checkout mutation, stale ref/PR/task-status mutation, direct SQL, merge, Vonash, Magnus, VAOS, RAG/KB, broker, trading, risk, paper/live activation, or ALR product dispatch is authorized or performed by this increment.

Factory DB interaction for this run stayed within the stated allowlist: sanctioned `factory status` readback only for evidence. Live `factory project tick`, `factory project resolve-state`, direct SQL, and ad-hoc DB scripts were not executed.

## G1 documents read before implementation

The required documentation entrypoint and applicable G1/project docs read for this increment were:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`

These are the project-local docs cited in the final evidence. The historical/status readback below preserves the exact stale G1 blocker set that caused this dispatcher failure; the control-plane code repair does not alter G1 frontmatter or reviewed markers.

## Canonical status reproduction

Sanctioned status command:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2df-r1-status-after.json`

Parsed/readback evidence:

- Output size: `4,231,599` bytes.
- `db_backend=agent_core_postgres`.
- `database=zeus_agent`.
- Project `zeus-alpha-research-ledger-core` is `active`.
- Current task counts from parsed status: `tasks=131`, `ready_tasks=3`.
- Ready normal work remains runnable while docs/review routing is blocked historically: `zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re` (`phase=quality_review`, `claimed_by=None`), `zeus-alpha-research-ledger-core-r2cw-fail-closed-recovery-for-premature-` (`phase=implementation`, `claimed_by=None`), and `zeus-alpha-research-ledger-core-alr-020-r2-bounded-pr-first-signature-an` (`phase=implementation`, `claimed_by=None`).
- Existing documentation recovery remains present and unclaimed: `zeus-alpha-research-ledger-core-r2df-fresh-current-base-g1-documentation`, `phase=documentation`, `status=todo`, `claimed_by=None`.
- This assigned technical repair is the claimed recovery task: `zeus-alpha-research-ledger-core-r2df-r1-docs-first-g1-recovery-dispatch-`, `phase=g1_recovery`, `status=running`, `claimed_by=factory-force-tick`.
- Historical/stale G1 snapshot reproduced by the canonical status output at `/tmp/r2df-r1-status-after.json` lines `13737`-`13950`: `document_status_snapshot.available=true`, `blocking_count=10`, `docs_ready=false`, and the exact `reviewed=false` blocking G1 rows are `FACTORY_INTAKE.md`, `REQUIREMENTS_ANALYSIS.md`, `PATTERN_ANALYSIS.md`, `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, `PRD.md`, `ADRS.md`, `METHODOLOGY_PLAN.md`, `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`, and `SECURITY_GATES.md`; `SPRINT_PLAN.md`, `TRACKER.md`, `DOCUMENTATION_INDEX.md`, and `QA_GATES.md` read back as non-blocking in that same snapshot.
- Recent status readback preserves repeated dispatch/projection failure evidence: events `209147`, `209142`, and `209133` deny the R2cy quality review with `missing_or_unindexed_docs`; events `209146`, `209141`, and `209132` deny existing R2df documentation recovery with `unresolved_validation_tasks`; project reconciler events `209180`, `209153`, `209151`, `209150`, `209148`, and others keep `anomalies=['unvalidated_required_docs']`.

This reproduces the failure mode without mutating Agent Core rows: G1/docs-first is red in historical status evidence, an existing docs recovery is todo/unclaimed, normal ready work exists, and repeated dispatch attempts had returned denial/claimed-null behavior.

## RED reproduction

Command:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'test_claim_next_task_claims_g1_recovery_with_final_gate_wording_before_product_and_validation' -v --tb=short`

Pre-fix result:

- Exit `1`.
- Focused test failed at `tests/hermes_cli/test_factory_increment_integration.py:818` because `factory_pg.claim_next_task("demo", worker="factory-force-tick")` returned `None`.
- The fixture included a red docs-first preflight, a `review_ready` quality-review validation task, a ready implementation/product task, and a dependency-free G1/documentation recovery task whose description quoted a prior final/gate-closure failure. The failure proved the documentation recovery was denied as `unresolved_validation_tasks` instead of being claimed before product/validation work.

## Implementation summary

The repair adds a narrow exemption in `factory_pg._candidate_requires_validation_readiness_before_dispatch()`:

- If a candidate is a docs-first repair dispatch task (`_is_docs_first_repair_dispatch_task(candidate)`), validation-readiness gating returns `False` before final-stage text matching.
- This keeps G1/documentation recovery dispatchable even when the task text quotes historical final-stage/gate-closure failure evidence from the broken run.
- Product implementation, QA/security/release/delivery/final-stage tasks remain docs-first and validation fail-closed when G1 documentation is genuinely missing, unindexed, unreviewed, or invalid.

This changes only routing/classification. It does not mark any document reviewed, approve gates, close tasks, merge branches, or dispatch product/runtime work.

## GREEN validation

Focused GREEN:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'test_claim_next_task_claims_g1_recovery_with_final_gate_wording_before_product_and_validation' -v --tb=short`

Result: `1` selected test passed, `0` failed.

Full increment integration file:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py`

Result: `128` tests passed, `0` failed.

Related Factory control-plane subset:

`HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'dispatch_preflight or validation_readiness or claimed_null or g1'`

Result: `28` selected tests passed, `0` failed.

Whitespace/tracked diff check:

`git diff --check`

Result: exit `0`, no output.

## Delivery and review handoff

R2df-R1 remains PR-first. This artifact is implementation evidence only and is `reviewed: pending` until a distinct independent reviewer performs exact-SHA review of the final pushed PR head. This worker must not self-approve, merge, deploy, write direct SQL, mutate the primary checkout, force-push/rewrite unrelated refs, execute external runtimes, or dispatch ALR product/trading work.

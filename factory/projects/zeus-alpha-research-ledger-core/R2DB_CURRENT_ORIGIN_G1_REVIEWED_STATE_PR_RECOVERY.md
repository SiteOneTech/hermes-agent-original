---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2db-current-origin-g1-reviewed-state-pr
run_id: run-1787085388-2b729f35
phase: documentation
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending_independent_exact_sha_quality_review
owner: codex-builder
base_commit: 18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2db-current-origin-g1-reviewed
branch: factory/zeus-alpha-research-ledger-core/inc-017-r2db-current-origin-g1-reviewed
created_at: 2026-08-18T16:53:48-04:00
---

# R2db — current-origin G1 reviewed-state PR recovery after false terminal security run

## Scope and boundary

R2db repairs the Factory review-run terminalization path that allowed R2da to reach `done` after the actual `quality-reviewer` run exhausted with MiniMax HTTP 429 and produced no reviewer output or tool evidence. The change is bounded to the private Zeus ledger / Factory control-plane and project-local provenance:

- code: `hermes_cli/factory_pg.py`
- regression tests: `tests/hermes_cli/test_factory_increment_integration.py`
- project evidence: this file plus the existing Zeus Alpha Research Ledger Core control docs

No Vonash, Magnus, VAOS, RAG/KB, broker, trading, risk, paper/live, messaging, deployment, credential, external-runtime integration, direct SQL, primary-checkout mutation, merge to main, or task-status mutation is authorized or performed by this increment.

## G1 docs and sources consulted

Required entrypoint and applicable G1/control docs read before implementation:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/REQUIREMENTS_ANALYSIS.md`
- `factory/projects/zeus-alpha-research-ledger-core/PRD.md`
- `factory/projects/zeus-alpha-research-ledger-core/ADRS.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/PATTERN_ANALYSIS.md`
- `factory/projects/zeus-alpha-research-ledger-core/ASSUMPTIONS_AND_OPEN_QUESTIONS.md`
- `factory/projects/zeus-alpha-research-ledger-core/METHODOLOGY_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/G1_REVIEW.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2CM_G1_REVIEW_STATE_PROVENANCE_REPAIR.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2CN_BOUNDED_CANONICAL_G1_DOCS_GATE_AND_PR_PROVENANCE_REPAIR.md`

## Factory status before candidate

Allowed command:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2db-status-before.json
```

Readback evidence:

- output: `/tmp/r2db-status-before.json`
- bytes: `3409655`
- backend: `agent_core_postgres`
- database: `zeus_agent`
- source root: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2db-current-origin-g1-reviewed`
- status source root: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2db-current-origin-g1-reviewed`
- delegated: `false`
- task row: `zeus-alpha-research-ledger-core-r2db-current-origin-g1-reviewed-state-pr` status `running`, branch `factory/zeus-alpha-research-ledger-core/inc-017-r2db-current-origin-g1-reviewed`, worktree as assigned

The canonical status payload accounts for every required G1 document. Before the code candidate, it reported `g1_count=14`, `blocking_count=0`, and `reviewed_false=` empty. No `reviewed=false` document was represented as passing by this readback:

| Document | exists | committed | indexed | validated | reviewed | blocking | source | base |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `FACTORY_INTAKE.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `REQUIREMENTS_ANALYSIS.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `PATTERN_ANALYSIS.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `PRD.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `ADRS.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `METHODOLOGY_PLAN.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `TECHNICAL_BLUEPRINT.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `SPRINT_PLAN.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `TASK_GRAPH.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `TRACKER.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `DOCUMENTATION_INDEX.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `QA_GATES.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `SECURITY_GATES.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |

The assignment prompt's stale G1 readiness list naming ten `missing=reviewed` blockers is preserved as prompt/control-plane context, not current passing evidence. R2db does not reinterpret those rows as green; it relies on the sanctioned Agent Core status payload above and the post-candidate readback below.

## Reproduced false terminalization source

The R2da task row in `/tmp/r2db-status-before.json` shows the defect this increment repairs:

- task: `zeus-alpha-research-ledger-core-r2da-exact-sha-security-gate-949-recover`
- status: `done`
- run: `run-1787084920-98b97d67`
- worker: `quality-reviewer`
- exit: `0`
- output summary includes: `API call failed (attempt 1/3): RateLimitError [HTTP 429]`, `Rate limited after 3 retries`, `API call failed after 3 retries`, and `Messages: 1 (1 user, 0 tool calls)`
- the run was nevertheless summarized as `Final semantic state marker: STATE: DONE; si falla...` and appended `Increment integration completed ... increment_integration_method: already_ancestor`

Gates `950`, `951`, and `952` are historical/evidence-candidate rows for PR #86 / R2ai-R2 metadata reconciliation. They are not accepted by R2db as substitute current-origin review evidence for this task. Gate `951` is project-scoped (`task=null`), and gates `950`/`952` are task-bound to `zeus-alpha-research-ledger-core-r2ai-r2-persisted-active-metadata-reconc`, not `zeus-alpha-research-ledger-core-r2db-current-origin-g1-reviewed-state-pr`.

## Root cause and repair

Root cause: `mark_run_finished()` allowed a positive review-run terminal path from an effective exit code of zero and a final semantic marker, then integrated the increment before requiring task-bound review evidence. In a provider failure log, wrapped prompt text containing `STATE: DONE; si falla...` plus process exit `0` was enough to mark the review run succeeded even though the actual LLM call returned HTTP 429 and produced no tools/output.

Repair:

- Review runs with effective positive exit now pass through `_review_positive_terminal_blocker()` before integration.
- Empty reviewer output blocks with `empty_reviewer_output`.
- Runtime/provider failure transcripts block with `review_output_contains_runtime_failure` when they contain known terminal runtime-failure signatures such as `API call failed after 3 retries`, `RateLimitError [HTTP 429]`, `Rate limited after 3 retries`, `usage limit reached`, or `Messages:       1 (1 user, 0 tool calls)`.
- Positive review-run closure requires a task-bound passed Factory gate for the same `task_id` and an independent review gate type (`architecture`, `critical_readiness`, `delivery`, `quality`, `security`, `spec`, or `test`).
- Missing task-bound positive gate blocks with `review_success_without_task_bound_passed_gate`.
- Blocked review terminalization records the run as `rework`, keeps the task in `review_ready`, and writes an explicit reason that empty output or provider/runtime failure logs cannot mark the task reviewed.

This makes an HTTP 429/empty reviewer output unable to terminalize a task as reviewed, and it prevents project-scoped or different-task gates from being substituted as task-bound review evidence.

## TDD evidence

RED was recorded before production code was changed:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k "mark_run_finished_review_success_requires_task_bound_gate or mark_run_finished_review_429_log_cannot_close_even_when_exit_zero or mark_run_finished_review_success_merges_before_done or mark_run_finished_review_success_reworks_when_merge_fails"
```

Result: exit `1` before implementation, proving the new task-bound gate and HTTP-429 terminalization guards were missing.

GREEN/focused evidence after implementation:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k "mark_run_finished_review_success_requires_task_bound_gate or mark_run_finished_review_429_log_cannot_close_even_when_exit_zero or mark_run_finished_review_success_merges_before_done or mark_run_finished_review_success_reworks_when_merge_fails or mark_run_finished_failed_review_with_wrapped_instruction_remains_rework"
```

Result: `5 tests passed, 0 failed`.

Full targeted file:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py
```

Result: `115 tests passed, 0 failed`.

Related Factory regression set:

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_increment_integration.py
```

Result: `292 tests passed, 0 failed`.

## Factory status after candidate

Allowed command:

```bash
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2db-status-final.json
```

Readback evidence:

- output: `/tmp/r2db-status-final.json`
- bytes: `3409594`
- backend: `agent_core_postgres`
- database: `zeus_agent`
- source root: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2db-current-origin-g1-reviewed`
- status source root: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2db-current-origin-g1-reviewed`
- delegated: `false`
- `g1_count=14`
- `blocking_count=0`
- `reviewed_false=` empty

Every required G1 row after the candidate remains explicitly accounted for and no `reviewed=false` row is represented as passing:

| Document | exists | committed | indexed | validated | reviewed | blocking | source | base |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `FACTORY_INTAKE.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `REQUIREMENTS_ANALYSIS.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `PATTERN_ANALYSIS.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `PRD.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `ADRS.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `METHODOLOGY_PLAN.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `TECHNICAL_BLUEPRINT.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `SPRINT_PLAN.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `TASK_GRAPH.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `TRACKER.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `DOCUMENTATION_INDEX.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `QA_GATES.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |
| `SECURITY_GATES.md` | true | true | true | true | true | false | configured_base_ref | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` |

## Delivery contract

This R2db branch must be pushed and delivered as a Zeus-signed `agent:zeus` PR against `main`. The PR body and Factory gate evidence must name:

- base SHA: `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc`
- final candidate head SHA after push
- this artifact path
- tests above
- before/after Factory status paths
- no-merge/no-deploy/no-direct-SQL/no-primary-mutation/no-credential/no-external-runtime/no-product-dispatch statement

This worker does not self-approve. A separate independent exact-SHA quality/security review gate for `zeus-alpha-research-ledger-core-r2db-current-origin-g1-reviewed-state-pr` is still required before any review-run closure relies on this candidate.

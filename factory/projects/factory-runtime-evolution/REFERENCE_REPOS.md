# Factory Runtime Reference Repositories

> Canonical purpose: this document belongs to the Factory Runtime Evolution line of work. The canonical Factory DB project is now `factory-runtime-evolution`, and repo artifacts live in `factory/projects/factory-runtime-evolution/`. Do not create more mini-projects for runtime bugs; create increments inside this project.

## Local reference pack

Reference repositories are cloned outside the Hermes source tree so we do not vendor third-party code into `hermes-agent-original` or accidentally mix licenses. Factory docs and retrospectives may link to these local paths and cite specific files/commits.

Root path:

```text
/home/jean/reference-repos/factory-workflow-patterns
```

Refresh command:

```bash
BASE=/home/jean/reference-repos/factory-workflow-patterns
for d in n8n temporal prefect langgraph bmad-method spec-kit; do
  branch=$(git -C "$BASE/$d" remote show origin | awk '/HEAD branch/ {print $NF}')
  git -C "$BASE/$d" fetch --depth 1 origin "$branch"
  git -C "$BASE/$d" reset --hard "origin/$branch"
done
```

## Current cloned references

| Reference | Local path | Commit captured | Why Factory keeps it locally |
|---|---|---:|---|
| n8n | `/home/jean/reference-repos/factory-workflow-patterns/n8n` | `0db6a4b7d82c` | Primary guide for workflow/process design: closed execution states, task-runner FSM, active executions, operation reducer, structural validation before execution. |
| Temporal | `/home/jean/reference-repos/factory-workflow-patterns/temporal` | `d06194e96ca3` | Durable execution reference: event history, workflow/task state machines, retries, task queues, timers, signals, replay/resume discipline. |
| Prefect | `/home/jean/reference-repos/factory-workflow-patterns/prefect` | `db66b14dbaea` | Python orchestration reference: server-owned flow state transitions, state schemas, flow/task engines, workers, schedules, events, concurrency/pause/crash behavior. |
| LangGraph | `/home/jean/reference-repos/factory-workflow-patterns/langgraph` | `2b1abc807b28` | Agent workflow reference: state graph, reducers, checkpoints, interrupts/human-in-the-loop, persistence, streaming, resumability. |
| BMAD-METHOD | `/home/jean/reference-repos/factory-workflow-patterns/bmad-method` | `072d0a74587e` | Methodology reference: PRD, architecture, story/dev workflow, correct-course, review discipline. |
| spec-kit | `/home/jean/reference-repos/factory-workflow-patterns/spec-kit` | `7106858c4e63` | Spec-driven repo process reference: constitution, specs, plans, tasks, checklists, agent context. |

## n8n canonical guide files

Use n8n as the first reference when designing Factory workflow runtime behavior.

| n8n file | Local path | Factory pattern to borrow |
|---|---|---|
| Execution status enum | `n8n/packages/workflow/src/execution-status.ts` | Closed status list plus terminal-status helper. Factory should centralize `ProjectStatus`, `TaskStatus`, `RunStatus`, `GateStatus`, and terminal helpers in one contract module. |
| Task runner FSM | `n8n/packages/@n8n/task-runner/src/task-state.ts` | Explicit task lifecycle with documented transitions and fail-fast handler for unexpected states. Factory must not silently idle on uncovered states. |
| AI workflow operation reducer | `n8n/packages/@n8n/ai-workflow-builder.ee/src/utils/operations-processor.ts` | AI proposes typed operations; deterministic reducer applies them sequentially, validates side effects, and clears stale validation. Factory agents should emit typed `FactoryOperation`s instead of direct ad-hoc DB mutations. |
| Active executions | `n8n/packages/cli/src/active-executions.ts` | Active execution registry, concurrency reservation/release, conditional updates such as `requireStatus`, and cleanup when a promise settles. Factory task runs need equivalent idempotent active-run discipline. |
| Workflow structure validation | `n8n/packages/workflow/src/` and workflow validation utilities | Separate structural graph validity from semantic/readiness checks. Factory should separate task graph validity from delivery/readiness/Notion/docs gates. |

## Other reference patterns

| Reference | Key files to inspect first | Factory application |
|---|---|---|
| Temporal | `temporal/service/history/workflow/workflow_task_state_machine.go`, `temporal/service/history/workflow/`, `temporal/common/persistence/` | Durable event history, attempt counters, retries/backoff, workflow task scheduling/started/completed/failed transitions, safe replay/resume. |
| Prefect | `prefect/src/prefect/server/schemas/states.py`, `prefect/src/prefect/server/models/flow_run_states.py`, `prefect/src/prefect/flow_engine.py`, `prefect/src/prefect/task_engine.py` | State schema, terminal-state set, orchestration API as state-transition authority, metadata-before-transition rule, server-vs-local task transition boundary. |
| LangGraph | `langgraph/libs/langgraph/langgraph/graph/state.py`, `langgraph/libs/langgraph/langgraph/runtime.py`, `langgraph/libs/checkpoint-*` | Shared state graph, reducer semantics, checkpoint/resume, interrupt/human-in-the-loop handling for agent workflows. |
| BMAD-METHOD | `.bmad-core/`, `docs/`, workflow/task templates | Methodology layer for PRD→architecture→stories→dev→review→retrospective. Use as method reference, not runtime source of truth. |
| spec-kit | `templates/`, `scripts/`, `specs/` if present | Repo-first spec workflow, constitution/checklist discipline, task breakdown before implementation. |

## Retrospective rule

Before patching Factory runtime code after any stuck project, failed gate, repeated `claimed=null`, stale `delivery_hold`, or methodology drift, the Factory retrospective must include a reference pass:

1. Identify the violated invariant and fingerprint the incident.
2. Search the local reference pack for the closest mature pattern before designing a fix.
3. Cite at least one reference file/commit in the retrospective or increment plan.
4. Decide whether the needed fix is a runtime contract, operation reducer, state machine, active-run/concurrency, checkpoint/resume, methodology, or documentation-process issue.
5. Create/update one increment inside the canonical Factory Runtime Evolution project. Do not create a new mini-project.
6. Write a failing regression test for the incident before implementation.
7. Implement the structural fix, not a one-off project status edit.
8. Record evidence: reference consulted, test added, code changed, gates run, review result, and whether a skill/reference needs updating.

A patch is considered non-canonical if it changes a stuck project directly but cannot explain which runtime invariant failed and which reference pattern guided the structural repair.

## Candidate references intentionally not cloned yet

| Candidate | Reason not in first local pack |
|---|---|
| Dagster | Strong asset orchestration reference, but repo is much larger and more data-platform-specific. Clone only if Factory starts modeling assets/materializations. |
| Airflow | Mature DAG scheduling reference, but less aligned with agentic event-driven repair and human-in-the-loop runtime. |
| Netflix Conductor | Useful microservice orchestration ideas, but the Netflix repo appears less current than Temporal/Prefect/n8n for this Factory problem class. |
| Argo Workflows/Flyte | Useful for Kubernetes-native workflow execution, but not the immediate bottleneck for Zeus Factory's local Agent Core Postgres runtime. |

## How this changes Factory planning

Future Factory Runtime Evolution increments should include a `Reference Patterns Consulted` section with:

```text
Reference: n8n / Temporal / Prefect / LangGraph / BMAD / spec-kit
Local file(s): /home/jean/reference-repos/factory-workflow-patterns/<repo>/<path>
Commit: <short SHA>
Pattern borrowed: <specific concept>
Factory invariant affected: <invariant>
Test proving it: <test path/name>
```

This turns external repos into an active design library for retrospectives and planning, not a passive bookmark list.

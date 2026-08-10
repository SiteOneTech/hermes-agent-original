# Documentation Index — Factory Runtime Evolution — Continuation

| Field | Value |
|---|---|
| Document status | validated:true (implementation-planner, 2026-08-10); reviewed:true (solution-architect, 2026-08-10, planning gate 690) |

## 1. Required G1 documents (canonical control pack)

| File | Purpose | Exists | Indexed | Committed | Validated | Reviewed |
|---|---|---|---|---|---|---|
| `FACTORY_INTAKE.md` | Intake, trigger, G0, scope, intake evidence | yes | yes | yes (this branch) | true (planner) | true (solution-architect, 2026-08-10, planning gate 690) |
| `REQUIREMENTS_ANALYSIS.md` | Durable invariant, FR-1…FR-8, NFRs, traceability | yes | yes | yes | true (planner) | true (solution-architect, 2026-08-10, planning gate 690) |
| `PATTERN_ANALYSIS.md` | Runtime anatomy, failure-mode diagnosis, gap analysis, pattern decisions | yes | yes | yes | true (planner) | true (solution-architect, 2026-08-10, planning gate 690) |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | Assumptions A1–A10, open questions Q1–Q5, non-decisions | yes | yes | yes | true (planner) | true (solution-architect, 2026-08-10, planning gate 690) |
| `PRD.md` | Problem, users, stories, scope C1–C8, acceptance, metrics, non-goals | yes | yes | yes | true (planner) | true (solution-architect, 2026-08-10, planning gate 690) |
| `ADRS.md` | ADR-010-1…010-6 (question lifecycle, re-validation, reopen, allowlist, cron, docs discipline) | yes | yes | yes | true (planner) | true (solution-architect, 2026-08-10, planning gate 690) |
| `METHODOLOGY_PLAN.md` | Hybrid methodology, increment lifecycle, DoR/DoD, gate policy, commands | yes | yes | yes | true (planner) | true (solution-architect, 2026-08-10, planning gate 690) |
| `TECHNICAL_BLUEPRINT.md` | Current-state boundaries (file:line), target architecture, data contracts, test surface | yes | yes | yes | true (planner) | true (solution-architect, 2026-08-10, planning gate 690) |
| `SPRINT_PLAN.md` | Sprints 1–4, owners/reviewers, exit criteria, rollout boundary | yes | yes | yes | true (planner) | true (solution-architect, 2026-08-10, planning gate 690) |
| `TASK_GRAPH.md` | Dependency graph, FRE-010…017 + R1/R2 inventory, per-increment acceptance, parallelization | yes | yes | yes | true (planner) | true (solution-architect, 2026-08-10, planning gate 690) |
| `TRACKER.md` | Task tracker mirroring DB, evidence log, gate log, risk register | yes | yes | yes | true (planner) | true (solution-architect, 2026-08-10, planning gate 690) |
| `DOCUMENTATION_INDEX.md` | This index: canonical builder/reviewer map | yes | yes | yes | true (planner) | true (solution-architect, 2026-08-10, planning gate 690) |
| `QA_GATES.md` | QA criteria per increment, test commands, evidence rules | yes | yes | yes | true (planner) | true (solution-architect, 2026-08-10, planning gate 690) |
| `SECURITY_GATES.md` | Security gates, escalation allowlist, fail-closed rules | yes | yes | yes | true (planner) | true (solution-architect, 2026-08-10, planning gate 690) |

## 2. Lifecycle documents (created as phases advance)

| File | When |
|---|---|
| `QA_REPORT.md` | FRE-011…FRE-014 GREEN evidence; FRE-015 |
| `SECURITY_REVIEW.md` | FRE-012/015 |
| `QUALITY_REVIEW.md` | FRE-015 |
| `DELIVERY_REPORT.md` | FRE-016 |
| `CHANGELOG.md` / `CHANGE_RECORDS.md` | per merged increment (FRE-016) |
| `RETROSPECTIVE.md` | end of sprint / project closure |
| `NOTION_UPDATE.md` | human PM projection, if/when required |

## 3. Source-of-truth hierarchy

1. Agent Core Postgres `factory.*` — operational truth (projects, tasks, runs, gates,
   events, human questions, anomalies).
2. Repo Markdown under `factory/projects/factory-runtime-evolution-continuation/` —
   documentary control pack (this index is the map).
3. Git commits — immutable checkpoint evidence.
4. Notion/dashboard — human PM projection; never a blocker source.

## 4. Directory ownership and reconciliation note

- Canonical directory: `factory/projects/factory-runtime-evolution-continuation/`.
- Owner role: `factory-reporter` maintains the project-local documentary index,
  status notes, and human-readable reconciliation evidence for this directory.
- Source of truth: Agent Core Postgres `zeus_agent.factory` remains operational truth;
  this directory is the repo-local documentary control pack and must not override DB task,
  run, gate, or event state.
- Reconciliation rule: the directory is considered restored only when it exists in the
  repo/worktree being validated, contains this `DOCUMENTATION_INDEX.md`, and the index
  lists the required G1 documents with committed/validated/reviewed status.

## 5. Builder/reviewer reading order

1. `DOCUMENTATION_INDEX.md`
2. `FACTORY_INTAKE.md`
3. `REQUIREMENTS_ANALYSIS.md`
4. `PATTERN_ANALYSIS.md`
5. `ADRS.md`
6. `TECHNICAL_BLUEPRINT.md`
7. `METHODOLOGY_PLAN.md`
8. `SPRINT_PLAN.md`
9. `TASK_GRAPH.md`
10. `QA_GATES.md` + `SECURITY_GATES.md`
11. Task-specific acceptance criteria from Factory DB

## 6. Review status note

Per-document status block: `validated:true` means the planner verified content
consistency against Factory DB evidence, runtime code (baseline `20228c116`), and the
task acceptance criteria. `reviewed:true` means the independent `solution-architect`
review passed on 2026-08-10 via Factory planning gate 690. This document-only
reconciliation replaces the stale negative/pending review markers so the G1 preflight
reflects the already-recorded planning-review gate instead of re-blocking FRE-010.

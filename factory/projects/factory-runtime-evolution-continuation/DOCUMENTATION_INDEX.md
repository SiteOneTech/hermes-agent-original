# Documentation Index — Factory Runtime Evolution — Continuation

| Field | Value |
|---|---|
| Document status | validated: true (implementation-planner, 2026-08-10); reviewed: false — assigned to `solution-architect` |

## 1. Required G1 documents (canonical control pack)

| File | Purpose | Exists | Indexed | Committed | Validated | Reviewed |
|---|---|---|---|---|---|---|
| `FACTORY_INTAKE.md` | Intake, trigger, G0, scope, intake evidence | yes | yes | yes (this branch) | true (planner) | pending → solution-architect |
| `REQUIREMENTS_ANALYSIS.md` | Durable invariant, FR-1…FR-8, NFRs, traceability | yes | yes | yes | true (planner) | pending → solution-architect |
| `PATTERN_ANALYSIS.md` | Runtime anatomy, failure-mode diagnosis, gap analysis, pattern decisions | yes | yes | yes | true (planner) | pending → solution-architect |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | Assumptions A1–A10, open questions Q1–Q5, non-decisions | yes | yes | yes | true (planner) | pending → solution-architect |
| `PRD.md` | Problem, users, stories, scope C1–C8, acceptance, metrics, non-goals | yes | yes | yes | true (planner) | pending → solution-architect |
| `ADRS.md` | ADR-010-1…010-6 (question lifecycle, re-validation, reopen, allowlist, cron, docs discipline) | yes | yes | yes | true (planner) | pending → solution-architect |
| `METHODOLOGY_PLAN.md` | Hybrid methodology, increment lifecycle, DoR/DoD, gate policy, commands | yes | yes | yes | true (planner) | pending → solution-architect |
| `TECHNICAL_BLUEPRINT.md` | Current-state boundaries (file:line), target architecture, data contracts, test surface | yes | yes | yes | true (planner) | pending → solution-architect |
| `SPRINT_PLAN.md` | Sprints 1–4, owners/reviewers, exit criteria, rollout boundary | yes | yes | yes | true (planner) | pending → solution-architect |
| `TASK_GRAPH.md` | Dependency graph, FRE-010…017 + R1/R2 inventory, per-increment acceptance, parallelization | yes | yes | yes | true (planner) | pending → solution-architect |
| `TRACKER.md` | Task tracker mirroring DB, evidence log, gate log, risk register | yes | yes | yes | true (planner) | pending → solution-architect |
| `DOCUMENTATION_INDEX.md` | This index: canonical builder/reviewer map | yes | yes | yes | true (planner) | pending → solution-architect |
| `QA_GATES.md` | QA criteria per increment, test commands, evidence rules | yes | yes | yes | true (planner) | pending → solution-architect |
| `SECURITY_GATES.md` | Security gates, escalation allowlist, fail-closed rules | yes | yes | yes | true (planner) | pending → solution-architect |

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

## 4. Builder/reviewer reading order

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

## 5. Review status note

Per-document status block: `validated: true` means the planner verified content
consistency against Factory DB evidence, runtime code (baseline `20228c116`), and the
task acceptance criteria. `reviewed: pending` is explicit and tracked: the independent
review gate is assigned to `solution-architect` (Factory DB reviewer for FRE-010) and
must pass before any downstream code increment is claimable (fail-closed G1).

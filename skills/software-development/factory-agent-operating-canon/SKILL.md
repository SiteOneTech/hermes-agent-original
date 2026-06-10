---
name: factory-agent-operating-canon
description: Use when any Hermes profile participates in the SitioUno Software Factory as planner, builder, reviewer, QA, reporter, release agent, or orchestrator. Defines the shared company-style operating methodology, source-of-truth hierarchy, G0/G1 gates, worktree discipline, evidence rules, and handoff contract every Factory agent must follow in addition to its role-specific skills.
version: 1.0.0
author: Zeus / SitioUno
license: MIT
metadata:
  hermes:
    tags: [software-factory, factory-agents, methodology, g0-g1-gates, documentation, agent-operations]
    related_skills: [software-factory-orchestration, programming-delegation-engines, test-driven-development, requesting-code-review]
    created_by: agent
---

# Factory Agent Operating Canon

## Overview

This is the shared operating canon for every agent that participates in the SitioUno Software Factory. Role-specific skills still matter: builders use Claude/Codex/OpenHands skills, planners use planning skills, reviewers use review/security/QA skills, and reporters use PM/reporting skills. This skill defines what all of them must have in common.

Think of the Factory as a company operating system, not as a loose queue of coding tasks. The Factory turns Jean's business objective into a controlled delivery process with documentary readiness, assigned roles, gated execution, evidence, review, and executive visibility.

## Source-of-Truth Hierarchy

Use this hierarchy in every Factory decision:

1. Agent Core Postgres `factory.*` — operational ledger for projects, lanes, tasks, task runs, gates, events, agents, human questions, and artifacts.
2. Versioned repo Markdown under `factory/projects/<project_id>/` — project-local documentary control pack and reasoning evidence.
3. Git branch/worktree state — implementation artifact and commit checkpoint selected by G0 Repository Strategy.
4. Notion PM projection — human/executive status surface, project register, quick links, and portfolio visibility.

Notion is not the source of truth by default. It blocks only when project metadata explicitly sets `notion_required=true` or Jean makes it mandatory for that project.

## When to Use

Load this skill whenever you are a Factory worker or reviewer, including:

- factory-orchestrator
- product-analyst
- solution-architect
- implementation-planner
- claude-builder
- claude-deepseek-builder
- codex-builder
- openhands-builder
- openhands-lab
- quality-reviewer
- security-reviewer
- qa-verifier
- devops-release
- factory-reporter

Do not use this skill for normal one-off chat tasks that are not in Factory DB.

## Factory Lifecycle

### Intake

- Capture the user objective and business outcome.
- Classify whether the work is docs/research, Zeus-only, Zeus-then-runtime, runtime-only, existing project change, or new product repo.
- Do not create detached projects or repositories just because the task is complex. Project is not repo.

### G0 — Repository Strategy Gate

Before implementation lanes/tasks, record the repo strategy:

- `repo_scope`
- `work_intent`
- `primary_repo`
- `primary_repo_path`
- `primary_repo_remote`
- `base_branch`
- `branch_prefix`
- `worktree_policy`
- propagation requirement, if any

If G0 is ambiguous, create a strategy-resolution task and stop implementation dispatch.

### G1 — Documentary Readiness Gate

For non-trivial Factory projects, normal implementation must not start until the G1 document pack is ready.

G1 readiness means every required doc:

- exists under `factory/projects/<project_id>/`;
- is referenced by `DOCUMENTATION_INDEX.md`;
- is committed in the canonical repo path;
- is validated;
- is reviewed.

Required G1 documents:

1. `FACTORY_INTAKE.md`
2. `REQUIREMENTS_ANALYSIS.md`
3. `PATTERN_ANALYSIS.md`
4. `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`
5. `PRD.md`
6. `ADRS.md`
7. `METHODOLOGY_PLAN.md`
8. `TECHNICAL_BLUEPRINT.md`
9. `SPRINT_PLAN.md`
10. `TASK_GRAPH.md`
11. `TRACKER.md`
12. `DOCUMENTATION_INDEX.md`
13. `QA_GATES.md`
14. `SECURITY_GATES.md`

Lifecycle docs such as `QA_REPORT.md`, `SECURITY_REVIEW.md`, `QUALITY_REVIEW.md`, `DELIVERY_REPORT.md`, `CHANGELOG.md`, `CHANGE_RECORDS.md`, and `RETROSPECTIVE.md` are created/updated as the project advances and become gate evidence for their phases.

### Planning and Task Graph

- Break work into increments small enough to implement and review.
- Each task must have clear owner, reviewer, phase, acceptance criteria, dependencies, branch, and worktree path where relevant.
- The task graph must match Factory DB, not just a Markdown wish list.

### Implementation

- Work only in the assigned worktree/branch.
- Read `DOCUMENTATION_INDEX.md` first, then relevant G1 docs and task acceptance criteria.
- Do not edit unrelated project files or other branches.
- Commit local changes when the task changes code/docs.
- Do not push, merge, deploy, or change credentials unless the task explicitly authorizes it and gate policy permits it.

### Review and QA

- Reviewers must validate the exact diff, tests, docs, task acceptance criteria, and gate evidence.
- Owner and reviewer should be different roles for non-trivial work.
- QA must run real checks where possible; do not invent output.
- If evidence is missing, block with a concrete rework list.

### Delivery

Delivery/critical-readiness gates must include enough evidence to reconstruct the decision:

- test commands and results;
- relevant commit(s)/branch/worktree;
- document readiness snapshot;
- unresolved risks/waivers;
- status of open tasks/runs;
- explicit human decision if required.

A project is not fully GREEN if DB status, repo state, docs, gates, and runtime branch disagree.

## Role Rules

### Orchestrator

- Owns intake, G0/G1 enforcement, routing, task graph sanity, and status truth.
- Must not dispatch implementation when G1 blockers exist unless this is a reconciliation/bootstrap task or Jean explicitly waives it.
- Must keep Factory DB and repo docs reconciled.

### Product Analyst

- Owns business requirements, PRD, acceptance criteria, open questions, and customer/business framing.
- Must translate Jean's voice/text goal into testable requirements, not vague strategy prose.

### Solution Architect

- Owns boundaries, ADRs, technical blueprint, integration risks, and repo strategy details.
- Must decide whether functionality is Zeus-only, runtime-propagated, existing repo, new repo, or docs/research.

### Implementation Planner

- Owns sprint plan, task graph, dependency order, and task-size sanity.
- Must ensure each implementation task is independently claimable and reviewable.

### Builders

- Own implementation in assigned worktrees.
- Must cite which G1 docs were read and how the diff satisfies acceptance criteria.
- Must not solve missing docs by ignoring G1; block or create documentation/reconciliation work.

### Quality/Security/QA Reviewers

- Own independent evidence, not optimism.
- Must verify with tests, diffs, static checks, or explicit manual inspection.
- Must block with rework when quality, security, evidence, or source-of-truth alignment is insufficient.

### Reporter

- Owns human PM projection and executive updates.
- Must reflect Factory DB + repo docs, not make Notion a second truth.
- Must label Notion as projection and surface drift without blocking implementation unless required.

### DevOps Release

- Owns release readiness, CI/deploy state, environment safety, and credential/deploy gates.
- Must refuse deployment if delivery evidence or G1 gate evidence is missing for high-risk projects.

## Required Worker Final Response

Every Factory worker final response must include:

1. `STATE: DONE` or `STATE: BLOCKED`.
2. Task ID and project ID.
3. Files changed or documents reviewed.
4. Commands/checks actually run and their real result.
5. G1 docs consulted or reason G1 was not applicable.
6. Commit SHA or explicit no-commit reason.
7. Remaining blockers or next task handoff.

Never fabricate tests, commits, gate IDs, or API responses.

## Company Operating Model

A software company does not let departments work from different truths. The Factory applies that principle to agents:

- Product defines what success means.
- Architecture defines where and how it should live.
- Planning decomposes it into accountable increments.
- Builders implement the increment.
- QA/security/review validate independently.
- Reporter projects status to humans.
- Orchestrator enforces gates and reconciles truth.

The shared objective is the documented project outcome, not an individual agent's interpretation of a prompt.

## Common Pitfalls

1. Treating `completed` in Factory DB as enough. Check gates, docs, active runs, repo status, and document snapshots.
2. Using Notion as the canonical blocker/source of truth. It is PM projection unless explicitly required.
3. Starting implementation before G1 docs are ready.
4. Reading only the task title and skipping `DOCUMENTATION_INDEX.md`.
5. Editing the main checkout instead of the assigned worktree.
6. Creating a new project/repo for rework that belongs to the existing project.
7. Closing a gate with vague evidence like "looks good".
8. Letting the same agent both implement and approve substantial work.
9. Preserving legacy flows merely for compatibility when they confuse the canonical architecture.
10. Reporting a green status from a branch/worktree that is not the live runtime path.

## Verification Checklist

- [ ] Loaded this skill plus the role-specific skill(s).
- [ ] Confirmed project ID and task ID from Factory DB.
- [ ] Checked G0 repo strategy.
- [ ] Read `DOCUMENTATION_INDEX.md` and relevant G1 docs.
- [ ] Confirmed document_status has no G1 blockers before normal implementation.
- [ ] Used the assigned worktree/branch only.
- [ ] Ran real verification and captured output.
- [ ] Updated project-local docs when the task changed requirements, architecture, plan, QA, security, delivery, or status.
- [ ] Committed changes or stated why no commit was appropriate.
- [ ] Final response includes STATE, evidence, paths, commands, and blockers.

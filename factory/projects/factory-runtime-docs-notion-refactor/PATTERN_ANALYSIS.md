# Pattern Analysis — Factory Runtime Docs/Notion Control-Plane Refactor

Project: `factory-runtime-docs-notion-refactor`
Document category: G1 required
Owner: solution-architect
Reviewer: quality-reviewer
Validated: yes
Reviewed: yes
Updated: 2026-06-10T17:29:32Z

## Patterns confirmed

### 1. DB + repo docs as canonical dual truth

The durable project state lives in Agent Core Postgres `factory.*`. The reasoning artifacts live as versioned Markdown under `factory/projects/<project_id>/` in the canonical repo selected by G0.

This pattern avoids both extremes:

- DB-only projects without reviewable reasoning artifacts;
- docs-only projects that drift from real task/gate/run state.

### 2. Notion as PM projection

Notion is useful for executive visibility, portfolio register, links, and human PM review. It is not a technical source of truth by default.

The control-plane pattern is:

- missing/stale Notion => PM projection warning;
- `notion_required=true` => blocking requirement;
- Factory DB + repo Markdown => canonical execution truth.

### 3. Gates are evidence snapshots, not vague statuses

A gate row should carry enough evidence to reconstruct the decision. For G1 enforcement, delivery/critical-readiness gates need a document-status snapshot that records document readiness at decision time.

### 4. Dispatch preflight blocks the wrong work early

Implementation dispatch is the hard control point. If G1 docs are missing/unindexed/uncommitted/unvalidated/unreviewed, normal implementation should not be claimed. Exceptions must be explicit Jean-authorized waivers or bootstrap/reconciliation tasks whose purpose is to fix the control plane.

### 5. Worker prompt context must align all roles

Agents have role skills, but a Factory-wide operating canon is still required. Every planner, builder, reviewer, QA agent, reporter, and release agent must understand:

- G0/G1 gates;
- source-of-truth hierarchy;
- worktree isolation;
- evidence and gate closure rules;
- company-style accountability.

## Patterns rejected

- Treating Notion as the default blocker/source of truth.
- Marking a project completed only because all tasks are terminal while documentation has no validated/reviewed evidence.
- Letting completed status hide a recent policy drift without a gate snapshot.
- Creating a detached new project/repo for corrections that belong to the existing Factory project.
- Using ad-hoc patches that bypass the root dispatch/readiness issue.

## Reusable design rule

Factory is a company operating system: the DB is the operational ledger, repo Markdown is the documentary control pack, Notion is the executive projection, and agents are role-specific workers who must all operate from the same policy and artifact pack.

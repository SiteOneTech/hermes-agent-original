# Requirements Analysis — Factory Runtime Docs/Notion Control-Plane Refactor

Project: `factory-runtime-docs-notion-refactor`
Document category: G1 required
Owner: product-analyst
Reviewer: factory-orchestrator
Validated: yes
Reviewed: yes
Updated: 2026-06-10T17:29:32Z

## User requirement

Jean asked the Factory to stop accepting implementation work that is not aligned around canonical project documentation. The runtime must make the documentation process enforceable, not merely aspirational.

The required business outcome is:

- every non-trivial Factory project has a project-local artifact pack before implementation;
- every participating agent knows the Factory operating methodology;
- implementation agents use the canonical docs and task graph as their shared objective;
- Notion stays a PM/human projection unless Jean explicitly makes it mandatory for a project;
- Factory DB plus versioned repo Markdown artifacts remain the source of truth.

## Functional requirements

1. G0 Repository Strategy Gate records whether the project belongs in Zeus, runtime, an existing product repo, a new repo, or docs/research only.
2. G1 Documentary Readiness Gate blocks normal implementation dispatch until all G1 docs exist, are indexed, are committed, and are validated/reviewed.
3. `hermes factory status <project> --json` exposes per-project `document_status` so the CLI, dashboard, and agents can see documentary readiness.
4. Delivery and critical-readiness gates persist a document-status snapshot so a completed project cannot appear GREEN without evidence.
5. Worker prompts include the G1 document entry point and the current document-status summary.
6. All active Factory agent profiles are assigned a common Factory operating skill in addition to their role-specific skills.
7. Dashboard surfaces G1 readiness, not just generic project status.
8. Notion is visible as PM projection drift/warning by default; it blocks only when `notion_required=true`.

## Non-functional requirements

- Use Agent Core Postgres `factory.*`; do not revive SQLite as canonical Factory truth.
- Preserve per-deliverable worktree isolation.
- Avoid repo-wide or website/doc churn when landing the hotfix on current `main`.
- Keep source-controlled skill content tenant-neutral and reusable across Factory agents.
- Keep derived/commercial agent boundaries intact; Factory governance remains Zeus/operator scope.

## Acceptance criteria

- The hotfix logic lands on the live runtime branch used by cron.
- A canonical Factory agent skill exists and is assigned to all active Factory worker profiles.
- `project_document_status()` returns zero G1 blockers for this project after the H6 commit is on the canonical repo path.
- Related pytest suites pass.
- The final delivery gate includes a `document_status_snapshot` in evidence.

# Factory Intake — Runtime Docs/Notion Control-Plane Refactor

Project: `factory-runtime-docs-notion-refactor`
Created: 2026-06-09T23:05:00Z
Source of truth: Agent Core Postgres `factory.*` + repo artifacts.

## Trigger

Jean decided the previous `funnel-core-crm-workflow` output cannot be trusted for acceptance because implementation ran before the canonical project documentation and Notion PM link existed. That project has been closed as superseded/untrusted.

## Request

Open a new Factory remediation/refactor project that fixes the Factory itself before any CRM review/refactor starts.

## Scope

- Documentation-first enforcement.
- Canonical Notion metadata link/write path.
- Active-run terminal-state and stale-run repair.
- Reconciler/dispatcher ordering so implementation cannot jump ahead of required docs/PM gates.
- Regression tests using the Funnel Core incident as a smoke case only.

## Out of scope

- Accepting or refactoring CRM/Funnel Core before this project is GREEN and Jean gives explicit go.
- Waiving Notion/docs requirements to hide the issue.
- New GitHub repository creation.

# Sprint Plan

Project: `factory-runtime-docs-notion-refactor`
Created: 2026-06-09T23:05:00Z

## Sprint 1 — Control-plane remediation

### Story 1 — Failing regression inventory
- Reproduce implementation-before-docs, Notion-created-but-not-linked, close-with-running-row, final-marker parsing, and `STATE: IN_PROGRESS` ambiguity.

### Story 2 — Canonical Notion metadata operation
- Add CLI/API write path with readback and event evidence.

### Story 3 — Documentation-first dispatch guard
- Enforce docs/index/Notion gates before implementation tasks for non-trivial projects.

### Story 4 — Active-run/close/resolve repair
- Ensure closure and resolve-state leave no stale active runs.

### Story 5 — Smoke and delivery
- Use `funnel-core-crm-workflow` as regression evidence only. Produce GO/NO-GO for CRM review.

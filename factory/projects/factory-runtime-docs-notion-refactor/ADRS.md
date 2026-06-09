# ADRs — Factory Runtime Docs/Notion Control-Plane Refactor

Project: `factory-runtime-docs-notion-refactor`
Created: 2026-06-09T23:05:00Z

## ADR-001: New remediation project

Decision: Open a new explicit remediation/refactor project, per Jean's instruction, because the prior CRM project is not trusted for acceptance.

Consequence: The new project owns Factory control-plane remediation. CRM/Funnel Core is frozen until GO.

## ADR-002: Repo strategy

Decision: `zeus_only`, existing repo `SiteOneTech/hermes-agent-original`, branch/worktree per deliverable.

Consequence: No new GitHub repo and no runtime propagation until Factory control-plane fixes are reviewed.

## ADR-003: No waivers as normal path

Decision: `required_docs_waived`, `notion_waived`, `tracker_waived`, or equivalent flags are not allowed as completion shortcuts unless Jean explicitly authorizes that exception for a named project.

## ADR-004: Notion is projection, Factory DB/repo docs are canonical

Decision: Notion is a human PM surface. It must be linked and read back, but Factory DB and repo artifacts remain source of truth.

## ADR-005: Terminal worker outcomes are structured contract

Decision: Runtime must classify worker results using final markers/structured result files, not historical prompt snippets. Ambiguous final markers are not success.

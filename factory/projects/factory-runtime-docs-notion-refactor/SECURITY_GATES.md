# Security Gates

Project: `factory-runtime-docs-notion-refactor`
Created: 2026-06-09T23:05:00Z

## Risks

- Project metadata write path could become arbitrary DB mutation.
- Notion URLs/page IDs can expose human PM surfaces if logged incorrectly.
- Direct SQL bypasses audit trail.
- Runtime workers may mutate wrong projects if metadata update command is too broad.

## Required controls

- Validate allowed metadata fields or provide typed command for Notion only.
- Record actor, event, previous/new metadata, and readback evidence.
- Do not expose secrets.
- Tests cover invalid project ID, empty URL/page ID, and unauthorized field update if generic metadata command is implemented.

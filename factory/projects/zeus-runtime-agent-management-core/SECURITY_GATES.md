---
project_id: zeus-runtime-agent-management-core
project_name: Zeus Runtime Agent Management Core
validated: yes
reviewed: yes
status: draft-ready
---

# Security Gates

## SEC-001 — Secret hygiene
- No secret values committed.
- No secret values printed to stdout/logs/chat.
- No secret values passed as process command-line arguments.
- Generated env files are `0600`.

## SEC-002 — Least privilege
- Runtime agent identity can read own project and shared runtime pack only.
- Runtime agent identity cannot read sibling agent projects or Zeus/fleet secrets.
- Shared pack contains only approved service-level keys.

## SEC-003 — Blast radius review
- Shared SendGrid key must be restricted to mail sending when possible.
- Per-agent categories/custom args should be used for auditability.
- Long-term issue: evaluate per-agent SendGrid subusers/API keys when volume or client isolation requires it.

## SEC-004 — Override safety
- Agent-specific overrides must be explicit and visible in status metadata without revealing values.
- Shared pack must not silently override an agent-specific key.

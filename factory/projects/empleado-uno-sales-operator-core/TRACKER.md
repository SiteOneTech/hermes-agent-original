# TRACKER — Sales Operator Core / Revenue Operator v2

Detailed historical tracker: `website/docs/developer-guide/sales-operator-core/TRACKER-001.md`.

## Current Factory state

| Gate / area | Status | Evidence / note |
|---|---|---|
| Intake | Passed | Jean requested specialized daily seller module for Empleado.uno and future products. |
| Architecture through I8 | Passed historically | Sales Operator Core v1 delivered Agent Core module/tools, no-send dry runs, synthetic pilot smoke, and runtime propagation. |
| I9 planning | In progress in this branch | Rebaseline control pack for Revenue Operator v2 private Kidu cockpit. |
| I9 architecture review | Pending | Reviewer: solution-architect. Must verify safe snapshot/no-send cockpit boundary. |
| I9 implementation | Not started | Must wait for I9 planning/architecture acceptance. |
| I9 quality_review | Not started | Must review implementation diff and UI semantics before security/deploy. |
| I9 security_review | Not started | Must inspect actual artifacts/snapshots for credentials, send paths, synthetic-as-real risks. |
| I9 deploy | Not started | Sandbox/Kidu only. Production remains HOLD. |
| I9 QA browser/post-deploy | Not started | Must verify private cockpit rendering, freshness, provenance, no-send policy panel, and no external action controls. |
| I9 delivery report | Not started | Must summarize branch/commit, tests, sandbox evidence, no-send boundary, and blockers. |

## I9 acceptance tracker

| Acceptance criterion | Current status |
|---|---|
| PRD, ADRS, TECHNICAL_BLUEPRINT, SPRINT_PLAN, TASK_GRAPH, QA_GATES, SECURITY_GATES, TRACKER and DOCUMENTATION_INDEX describe I9 and its no-send boundary. | Covered by this rebaseline branch; verify with content checks. |
| TASK_GRAPH defines mandatory UI phases: implementation, quality_review, security_review, deploy, QA browser/post-deploy, delivery report. | Covered in `TASK_GRAPH.md`. |
| Docs declare private interface uses safe snapshots, contains no credentials, and does not claim synthetic metrics as real results. | Covered across PRD/ADRS/TECHNICAL_BLUEPRINT/QA_GATES/SECURITY_GATES. |

## Active boundary

- Authorized: private Kidu cockpit, safe snapshots, freshness/provenance, real-vs-synthetic labels, outcome supervision, policy/no-send visibility.
- Not authorized: provider enablement, `auto_send`, cold WhatsApp, browser-triggered sends, production deploy, credentials/secrets in UI data, synthetic metrics as real results.

## Open blockers

No product blocker for I9 planning rebaseline. Downstream implementation must not start until the planning/architecture gates accept this updated control pack.

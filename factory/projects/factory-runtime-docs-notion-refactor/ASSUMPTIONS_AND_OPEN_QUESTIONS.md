# Assumptions and Open Questions — Factory Runtime Docs/Notion Control-Plane Refactor

Project: `factory-runtime-docs-notion-refactor`
Document category: G1 required
Owner: factory-orchestrator
Reviewer: Jean / factory-orchestrator
Validated: yes
Reviewed: yes
Updated: 2026-06-10T18:00:00Z

## Resolved assumptions

1. Factory DB and repo Markdown artifacts are the canonical execution truth.
2. Notion is a human PM projection unless project metadata explicitly sets `notion_required=true`.
3. The live runtime branch used by cron must contain the G1 code; a passing hotfix worktree alone is not enough.
4. Every active Factory role needs the shared `factory-agent-operating-canon` skill in addition to its specialist skills.
5. Work must stay in the existing Factory project/repo/worktree lineage unless Jean explicitly requests a separate project or repo.
6. Delivery/critical-readiness gates for high-risk projects must carry documentary readiness evidence, not only a textual GREEN status.

## Open questions intentionally left for future Factory evolution

1. Whether every historical completed Factory project should be re-audited under G1, or only projects marked with the new policy.
2. Whether the dashboard should add a separate G1 drill-down page beyond the compact project card.
3. Whether document validation/review should eventually become a first-class DB table instead of metadata/text-derived status.
4. Whether Notion projection freshness should have SLA thresholds per company/project class.
5. Whether derived commercial runtimes should receive a read-only subset of Factory methodology skills, excluding Zeus-only orchestration controls.

## Current decision for this closure

H6 closes the operational gap for the current Factory runtime by landing the hotfix logic on the live branch, creating and assigning the common Factory agent skill, surfacing `document_status`, adding worker prompt enforcement, completing missing G1 documents, and recording a delivery snapshot after verification.

Historical projects are not automatically reopened unless Jean requests a strict audit or sets project metadata such as `force_reconcile_completed=true`.

# Documentation Index — zeus-signature-core-refactor-hotfix

Project: zeus-signature-core-refactor-hotfix
Owner: Jean García / SitioUno
Created: 2026-06-12T18:09:47-04:00
Status: G1 bootstrap pack complete; implementation not started
Validated: yes — initial Zeus document consistency pass
Reviewed: yes — initial Zeus Factory orchestrator review; independent quality/security review remains a project task before delivery


## Source of Truth

1. Agent Core Postgres `factory.*` tables.
2. This project-local Markdown pack under `factory/projects/zeus-signature-core-refactor-hotfix/`.
3. Git branch/worktree state.
4. Notion PM projection (human reporting surface); repo-local `TRACKER.md` remains agents' canonical tracker.

## Notion PM Projection

- **notion_tracker_url**: https://app.notion.com/p/Zeus-Signature-Core-Refactor-PDF-Signing-Collection-Hotfix-Factory-PM-37e37b39cad6812ea750f19285329717
- **notion_tracker_page_id**: `37e37b39-cad6-812e-a750-f19285329717`
- **Status**: Active — synced post-T06 close (2026-06-13)
- **Owner**: Jean García / Zeus
- Notion is human reporting only; Factory DB + repo Markdown docs stay agents' source of truth.

## Required G1 Docs

| Document | Purpose | Status |
|---|---|---|
| `FACTORY_INTAKE.md` | Intake, scope, G0 summary | present / validated / reviewed |
| `REQUIREMENTS_ANALYSIS.md` | Functional and non-functional requirements | present / validated / reviewed |
| `PATTERN_ANALYSIS.md` | Repo/library research and patterns | present / validated / reviewed |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | Assumptions, decisions, open questions | present / validated / reviewed |
| `PRD.md` | Product requirements | present / validated / reviewed |
| `ADRS.md` | Architecture decisions | present / validated / reviewed |
| `METHODOLOGY_PLAN.md` | Factory method and gates | present / validated / reviewed |
| `TECHNICAL_BLUEPRINT.md` | Technical architecture | present / validated / reviewed |
| `SPRINT_PLAN.md` | Increment plan | present / validated / reviewed |
| `TASK_GRAPH.md` | Task dependencies | present / validated / reviewed |
| `TRACKER.md` | Project-local tracker | present / validated / reviewed |
| `DOCUMENTATION_INDEX.md` | Index and builder entry point | present / validated / reviewed |
| `QA_GATES.md` | QA criteria | present / validated / reviewed |
| `SECURITY_GATES.md` | Security criteria | present / validated / reviewed |
| `QA_REPORT.md` | QA lifecycle evidence | seeded / pending implementation |
| `SECURITY_REVIEW.md` | Security lifecycle evidence | seeded / pending implementation |
| `DELIVERY_REPORT.md` | Delivery lifecycle evidence | seeded / pending implementation |

## Builder Entry Instructions

Before any implementation task, a worker must read this index first, then:

1. `REQUIREMENTS_ANALYSIS.md`
2. `PATTERN_ANALYSIS.md`
3. `ADRS.md`
4. `TECHNICAL_BLUEPRINT.md`
5. `TASK_GRAPH.md`
6. task-specific acceptance criteria from Factory DB

## Repo Research Sources

- DocuSeal: https://github.com/docusealco/docuseal
- DocuSeal on-premises/product features: https://www.docuseal.com/on-premises
- OpenSign: https://github.com/OpenSignLabs/OpenSign
- signature_pad: https://github.com/szimek/signature_pad and https://www.npmjs.com/package/signature_pad
- pdf-lib: https://pdf-lib.js.org/ and https://www.npmjs.com/package/pdf-lib
- PDF.js: https://github.com/mozilla/pdf.js
- PyMuPDF: https://github.com/pymupdf/PyMuPDF

## Files in This Pack

- `FACTORY_INTAKE.md`
- `REQUIREMENTS_ANALYSIS.md`
- `PATTERN_ANALYSIS.md`
- `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`
- `PRD.md`
- `ADRS.md`
- `METHODOLOGY_PLAN.md`
- `TECHNICAL_BLUEPRINT.md`
- `SPRINT_PLAN.md`
- `TASK_GRAPH.md`
- `TRACKER.md`
- `DOCUMENTATION_INDEX.md`
- `QA_GATES.md`
- `SECURITY_GATES.md`
- `QA_REPORT.md`
- `SECURITY_REVIEW.md`
- `DELIVERY_REPORT.md`
- `DB_TASKS.md`


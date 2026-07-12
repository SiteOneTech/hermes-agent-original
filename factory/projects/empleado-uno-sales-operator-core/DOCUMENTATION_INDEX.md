# DOCUMENTATION_INDEX — Sales Operator Core

## Factory-required artifacts

| Artifact | Status |
|---|---|
| `FACTORY_INTAKE.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus |
| `REQUIREMENTS_ANALYSIS.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus |
| `PATTERN_ANALYSIS.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus |
| `PRD.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus |
| `ADRS.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus |
| `METHODOLOGY_PLAN.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus |
| `TECHNICAL_BLUEPRINT.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus |
| `SPRINT_PLAN.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus |
| `TASK_GRAPH.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus |
| `TRACKER.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus |
| `DOCUMENTATION_INDEX.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus |
| `QA_GATES.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus |
| `SECURITY_GATES.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus |
| `IMPLEMENTATION_REPORT.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus |
| `QA_REPORT.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus |
| `SECURITY_REVIEW.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus |
| `DELIVERY_REPORT.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus |
| `I6_IMPLEMENTATION_REPORT.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus |
| `I6_QA_REPORT.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus |
| `I6_SECURITY_REVIEW.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus |

## Detailed source docs

- `docs/sales-operator-core/PRD-001-sales-operator-core.md` — validated: yes; reviewed: yes
- `docs/sales-operator-core/ADR-001-local-sales-operator-core.md` — validated: yes; reviewed: yes
- `docs/sales-operator-core/SPRINT-PLAN-001.md` — validated: yes; reviewed: yes
- `docs/sales-operator-core/TASK-GRAPH-001.md` — validated: yes; reviewed: yes
- `docs/sales-operator-core/TRACKER-001.md` — validated: yes; reviewed: yes
- `docs/sales-operator-core/QA-SECURITY-GATES.md` — validated: yes; reviewed: yes
- `docs/sales-operator-core/DOCUMENTATION_INDEX.md` — validated: yes; reviewed: yes
- `docs/sales-operator-core/CRON-LOOPS-I6.md` — validated: yes; reviewed: yes

## Implementation evidence

- `factory/projects/empleado-uno-sales-operator-core/IMPLEMENTATION_REPORT.md` — implemented: yes; reviewed: yes
- `factory/projects/empleado-uno-sales-operator-core/QA_REPORT.md` — qa: pass/green; reviewed: yes
- `factory/projects/empleado-uno-sales-operator-core/SECURITY_REVIEW.md` — private dashboard pass; roles/secret sync green; autonomous outbound scoped to I6/I7
- `factory/projects/empleado-uno-sales-operator-core/DELIVERY_REPORT.md` — delivery/critical-readiness green; I6 openable
- `factory/projects/empleado-uno-sales-operator-core/I6_IMPLEMENTATION_REPORT.md` — I6 implemented: dry-run cron loops, no-send default, self-contained prompts
- `factory/projects/empleado-uno-sales-operator-core/I6_QA_REPORT.md` — I6 QA pass: 27 tests, migrate/roles, dry-run and wrapper smoke
- `factory/projects/empleado-uno-sales-operator-core/I6_SECURITY_REVIEW.md` — I6 security pass: no providers/senders, dry-run only, Accounting secret fallback fixed
- `factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-dry-run-i6.json` — I6 dry-run evidence: `external_sends=false`, `messages_sent_by_dry_run=0`
- `factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-dry-run-wrapper-i6.json` — I6 wrapper evidence: safe cron/no-agent output artifact
- `factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-dashboard/playwright-report.json` — browser QA: pass
- `factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-dashboard/desktop.png` — visual evidence: desktop
- `factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-dashboard/mobile.png` — visual evidence: mobile

Ownership: Factory DB + repo Markdown are source of truth. Notion is disabled/non-blocking.

## Review note

Planning, the private supervision dashboard, Agent Core schema/tools/seed, browser QA, and I6 dry-run cron loops are validated. Real autonomous outbound remains blocked until channel validation, opt-out automation, rate limits, and live pilot policy gates are implemented in later increments.

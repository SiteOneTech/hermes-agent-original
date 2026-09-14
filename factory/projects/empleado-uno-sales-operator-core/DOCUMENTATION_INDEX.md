# DOCUMENTATION_INDEX — Sales Operator Core / Revenue Operator v2

## Factory-required artifacts

| Artifact | Status | I9 Revenue Operator v2 coverage |
|---|---|---|
| `FACTORY_INTAKE.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus | Historical intake for Sales Operator Core; I9 keeps same project/repo strategy. |
| `REQUIREMENTS_ANALYSIS.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus | Historical requirements; I9 narrows current objective to private cockpit/no-send supervision. |
| `PATTERN_ANALYSIS.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus | Historical patterns remain; I9 adds safe snapshot/private UI pattern. |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus | Historical live-outreach questions remain future blockers, not I9 blockers. |
| `PRD.md` | validated: yes; reviewed: yes; owner: implementation-planner; reviewer: implementation-planner; I9 rebaseline: yes | Defines Revenue Operator v2 private Kidu cockpit, safe snapshots, freshness, real/synthetic labels, outcomes, and no-send boundary. |
| `ADRS.md` | validated: yes; reviewed: yes; owner: implementation-planner; reviewer: implementation-planner; I9 rebaseline: yes | Records ADR-I9: read-only private cockpit over sanitized snapshots; no browser sends/providers. |
| `METHODOLOGY_PLAN.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus | Hybrid Factory method remains; I9 is a planning rebaseline before implementation. |
| `TECHNICAL_BLUEPRINT.md` | validated: yes; reviewed: yes; owner: implementation-planner; reviewer: implementation-planner; I9 rebaseline: yes | Defines snapshot exporter/schema, cockpit UI, policy panel, Kidu sandbox boundary, and verification strategy. |
| `SPRINT_PLAN.md` | validated: yes; reviewed: yes; owner: implementation-planner; reviewer: implementation-planner; I9 rebaseline: yes | Defines phases through implementation, quality_review, security_review, deploy, QA browser/post-deploy, delivery report. |
| `TASK_GRAPH.md` | validated: yes; reviewed: yes; owner: implementation-planner; reviewer: implementation-planner; I9 rebaseline: yes | Contains mandatory UI task graph and owner/input/output/verification rows. |
| `TRACKER.md` | validated: yes; reviewed: yes; owner: implementation-planner; reviewer: implementation-planner; I9 rebaseline: yes | Tracks I9 planning, downstream reviews/deploy/QA/report, and active no-send boundary. |
| `DOCUMENTATION_INDEX.md` | validated: yes; reviewed: yes; owner: implementation-planner; reviewer: implementation-planner; I9 rebaseline: yes | This index maps the updated control pack and I9 boundary. |
| `QA_GATES.md` | validated: yes; reviewed: yes; owner: implementation-planner; reviewer: implementation-planner; I9 rebaseline: yes | Adds QA failures/checklists for freshness, synthetic-vs-real, safe snapshots, no credentials, and no browser sends. |
| `SECURITY_GATES.md` | validated: yes; reviewed: yes; owner: implementation-planner; reviewer: implementation-planner; I9 rebaseline: yes | Adds hard blockers for secrets, provider/auto-send/cold WhatsApp, browser side effects, and synthetic-as-real outcomes. |
| `IMPLEMENTATION_REPORT.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus | Historical through dashboard/I5 evidence; not I9 implementation evidence. |
| `QA_REPORT.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus | Historical QA; I9 browser/post-deploy QA must be new evidence. |
| `SECURITY_REVIEW.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus | Historical private dashboard/security evidence; I9 security review must inspect new artifacts. |
| `DELIVERY_REPORT.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus | Historical delivery; I9 delivery report is a future phase. |
| `I6_IMPLEMENTATION_REPORT.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus | Historical dry-run/no-send cron loops. |
| `I6_QA_REPORT.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus | Historical I6 QA. |
| `I6_SECURITY_REVIEW.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus | Historical I6 no-send security. |
| `I7_IMPLEMENTATION_REPORT.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus | Historical synthetic pilot smoke; I9 must label this data synthetic if surfaced. |
| `I7_QA_REPORT.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus | Historical I7 QA. |
| `I7_SECURITY_REVIEW.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus | Historical synthetic `.test`/no-send security; I9 inherits its labeling rule. |
| `I8_RUNTIME_PROPAGATION_REPORT.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus | Historical runtime propagation; I9 may later propagate only after new gates. |
| `I8_QA_REPORT.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus | Historical runtime QA; I9 needs separate cockpit QA. |
| `I8_SECURITY_REVIEW.md` | validated: yes; reviewed: yes; owner: Zeus; reviewer: Zeus | Historical runtime no-send security; I9 preserves/strengthens it. |

## I9 control-pack summary

Current authorized target: **Revenue Operator v2 private Kidu cockpit** for Empleado.uno.

The private interface must use safe snapshots, show freshness, distinguish real/synthetic/mixed/unknown data, show outcome metrics only with provenance, supervise policy/no-send state, and contain no credentials. Synthetic/test/demo metrics must never be claimed as real customer interest, replies, demos, revenue, CAC, conversion, or sales.

Explicitly not authorized in I9: provider enablement, `auto_send`, cold WhatsApp, browser-triggered external actions, direct provider sends, production deploy, or secrets in UI artifacts.

## Detailed source docs

- `website/docs/developer-guide/sales-operator-core/PRD-001-sales-operator-core.md` — historical product requirements and v1 scope.
- `website/docs/developer-guide/sales-operator-core/ADR-001-local-sales-operator-core.md` — historical architecture decision: local Agent Core schema + Hermes tools.
- `website/docs/developer-guide/sales-operator-core/SPRINT-PLAN-001.md` — historical implementation increments through I8.
- `website/docs/developer-guide/sales-operator-core/TASK-GRAPH-001.md` — historical dependency graph and task inventory through I8.
- `website/docs/developer-guide/sales-operator-core/TRACKER-001.md` — historical gate tracker through I8.
- `website/docs/developer-guide/sales-operator-core/QA-SECURITY-GATES.md` — baseline safety, compliance, QA gates.
- `website/docs/developer-guide/sales-operator-core/DOCUMENTATION_INDEX.md` — baseline documentation index.
- `website/docs/developer-guide/sales-operator-core/CRON-LOOPS-I6.md` — disabled-by-default dry-run cron loops and I6 evidence.
- `website/docs/developer-guide/sales-operator-core/PILOT-SMOKE-I7.md` — synthetic first pilot smoke for Empleado.uno.
- `website/docs/developer-guide/sales-operator-core/RUNTIME-PROPAGATION-I8.md` — propagation report for `sitiouno-agent-runtime`.

## Historical implementation evidence

- `factory/projects/empleado-uno-sales-operator-core/IMPLEMENTATION_REPORT.md` — implemented: yes; reviewed: yes.
- `factory/projects/empleado-uno-sales-operator-core/QA_REPORT.md` — QA: pass/green; reviewed: yes.
- `factory/projects/empleado-uno-sales-operator-core/SECURITY_REVIEW.md` — private dashboard pass; roles/secret sync green; autonomous outbound scoped to I6/I7.
- `factory/projects/empleado-uno-sales-operator-core/DELIVERY_REPORT.md` — delivery/critical-readiness green for historical scope.
- `factory/projects/empleado-uno-sales-operator-core/I6_IMPLEMENTATION_REPORT.md` — I6 dry-run cron loops, no-send default, self-contained prompts.
- `factory/projects/empleado-uno-sales-operator-core/I6_QA_REPORT.md` — I6 QA pass: 27 tests, migrate/roles, dry-run and wrapper smoke.
- `factory/projects/empleado-uno-sales-operator-core/I6_SECURITY_REVIEW.md` — I6 security pass: no providers/senders, dry-run only, Accounting secret fallback fixed.
- `factory/projects/empleado-uno-sales-operator-core/I7_IMPLEMENTATION_REPORT.md` — I7 synthetic 10-lead pack, scoring, attack plans and CRM readback.
- `factory/projects/empleado-uno-sales-operator-core/I7_QA_REPORT.md` — I7 QA pass: 15 targeted tests, migrate/roles, live DB readback and evidence validation.
- `factory/projects/empleado-uno-sales-operator-core/I7_SECURITY_REVIEW.md` — I7 security pass: synthetic `.test` fixtures, `external_sends=false`, `outreach_attempts=0`.
- `factory/projects/empleado-uno-sales-operator-core/I8_RUNTIME_PROPAGATION_REPORT.md` — I8 Sales Operator Core propagated to `SiteOneTech/sitiouno-agent-runtime`.
- `factory/projects/empleado-uno-sales-operator-core/I8_QA_REPORT.md` — I8 QA pass: 46 runtime tests, migrate/roles, live smoke, dry-run, DB readback, dashboard export.
- `factory/projects/empleado-uno-sales-operator-core/I8_SECURITY_REVIEW.md` — I8 security pass: commercial toolset boundary, no privileged tools/raw adapters, `external_sends=false`.
- `factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-dry-run-i6.json` — I6 dry-run evidence: `external_sends=false`, `messages_sent_by_dry_run=0`.
- `factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-dry-run-wrapper-i6.json` — I6 wrapper evidence: safe cron/no-agent output artifact.
- `factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-i7-pilot-smoke.json` — I7 full smoke evidence for synthetic campaign/territory/10 leads/scoring/attack plans/CRM readback.
- `factory/projects/empleado-uno-sales-operator-core/evidence/i7-pilot-fixture-leads.json` — I7 synthetic lead fixture pack (`.test` domains, no-contact).
- `factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-dashboard/playwright-report.json` — historical browser QA: pass.
- `factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-dashboard/desktop.png` — historical visual evidence: desktop.
- `factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-dashboard/mobile.png` — historical visual evidence: mobile.
- Runtime repo `docs/sales-operator-core/evidence/sales-operator-i8-runtime-smoke.json` — I8 runtime smoke evidence: `external_sends=false`, 10 synthetic leads, 10 research/scores/attack plans, 10 drafts, CRM readback.
- Runtime repo `docs/sales-operator-core/evidence/sales-operator-i8-daily-dry-run.json` — I8 runtime dry-run evidence: no external sends/messages.
- Runtime repo `docs/sales-operator-core/evidence/dashboard-user-data/sales_operator_dashboard.json` — I8 private dashboard snapshot.

Ownership: Factory DB + repo Markdown are source of truth. Notion is a human projection only and is non-blocking for this increment.

## Review note

I9 planning rebaseline is the next control-pack step before UI implementation. Real autonomous outbound remains blocked until a later explicit Factory task/gate implements channel validation, opt-out automation, rate limits, source-verified public leads, and live pilot policy approval.

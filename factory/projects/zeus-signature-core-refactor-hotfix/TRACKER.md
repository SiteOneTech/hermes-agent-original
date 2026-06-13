# Tracker — Signature Core Refactor

Project: zeus-signature-core-refactor-hotfix
Owner: Jean García / SitioUno
Created: 2026-06-12T18:09:47-04:00
Status: G1 bootstrap pack complete; implementation not started
Validated: yes — initial Zeus document consistency pass
Reviewed: yes — initial Zeus Factory orchestrator review; independent quality/security review remains a project task before delivery


| Task | Status | Evidence / Notes |
|---|---|---|
| T00 — G1 bootstrap docs + Factory DB | in_progress | Project DB created; docs being generated in `factory/projects/zeus-signature-core-refactor-hotfix` |
| T01 — Code/repo audit | planned | Existing files inspected: signature schema/tool/pdf helper/document-actions/public sandbox |
| T02 — Schema V2 migration | done | Added `db/modules/signature/000002_signature_v2_schema.sql`, registered `signature` in `scripts/agent_core_db.py`, validated with targeted pytest and ephemeral PostgreSQL migration smoke in isolated worktree `/home/jean/workspace/zeus-signature-core-refactor-hotfix-t02-schema` |
| T03 — Tool refactor + multi-signer completion | planned | Known bug: first approval currently completes request |
| T04 — PDF intake/template preparation | planned | Not started |
| T05 — Field placement engine | planned | Not started |
| T06 — Responsive signer UI | planned | Not started |
| T07 — OTP signing/comment/reject integration | planned | Existing document action helper supports OTP policy |
| T08 — Comments/reminders/receipts APIs | planned | Not started |
| T09 — Daily follow-up worker | planned | Not started |
| T10 — Final PDF stamping/certificate | planned | Existing helper only generic first-page stamp; needs multi-field stamping |
| T11 — Copy/hash distribution | planned | Not started |
| T12 — Private dashboard metrics | planned | Existing `/user/` private dashboard pattern available; module page needed |
| T13 — QA | planned | Not started |
| T14 — Security review | planned | Not started |
| T15 — Release/propagation | planned | Not started |

## Current Project State

- Factory DB project: created.
- Documentation pack: in progress in this commit.
- Implementation: not started.
- Risk: critical because this touches public document links, OTP, PII, signatures, PDF artifacts, and business workflows.

# Tracker — Signature Core Refactor

Project: zeus-signature-core-refactor-hotfix
Owner: Jean García / SitioUno
Created: 2026-06-12T18:09:47-04:00
Last updated: 2026-06-18T23:23:43-04:00
Status: IN PROGRESS — T14R2 core approval OTP/token hardening completed locally; T14 security review requeue + T15 release readiness pending
Validated: yes
Reviewed: yes


## Task Status Table

| Task | Status | Branch | Commit | Gate |
|---|---|---|---|---|
| T00 — G1 bootstrap docs + Factory DB | done | — | — | intake ✓ |
| T01 — Code/repo audit | done | `factory/.../t01-current-signature-code-and-route-audit` | — | planning ✓ |
| T02 — Schema V2 migration | done | `factory/.../t02-signature-v2-schema-migration` | — | functional ✓ |
| T03 — Tool refactor + multi-signer completion | done | `factory/.../t03-tool-refactor-and-multi-signer-completion` | `da205771d` | quality ✓ |
| T04 — PDF intake and template preparation | done | `factory/.../t04-pdf-intake-and-template-preparation` | — | functional ✓ |
| T05 — Field placement coordinate engine | done | `factory/.../t05-field-placement-coordinate-engine` | — | functional ✓ |
| T06 — Responsive signer UI (phone + PC) | done | `factory/.../t06-responsive-signer-ui` | `599fcf4c9` | quality ✓ |
| T07 — OTP sign/approve/reject/comment integration | done | `factory/.../t07-otp-sign-approve-reject-comment-integration` | `1acbd0629` | quality ✓ |
| T08 — Reminder and delivery receipt APIs | done | `factory/.../t08-reminder-and-delivery-receipt-apis` | `0da54838a` | functional ✓ |
| T09 — Daily follow-up worker until signed or expired | done | `factory/.../t09-daily-follow-up-worker` | `624ed9996` | functional ✓ |
| T10 — Multi-field final PDF stamping + certificate hashes | done | `factory/.../t10-final-pdf-stamping-certificate-hashes` | `1ab534c2d` | qa ✓ |
| T11 — Send final signed copies + hash validation | done | `factory/.../t11-final-copy-hash-distribution` | `4c7aad7a3` | qa ✓ |
| T12 — Protected private signature dashboard metrics | done | `factory/.../t12-protected-private-signature-dashboard-metrics` | `2ddc75f40` | qa ✓ |
| T13 — End-to-end QA (mobile/desktop PDF/DB reminders) | done | — | — | qa ✓ |
| T14R — Integrated security rework before T14 rerun | done | `factory/.../t14r-main-security-rework` | branch HEAD | local tests ✓ |
| T14R2 — Core approval OTP token hardening | done | `factory/.../t14r2-core-approval-token-otp` | branch HEAD | 48 focused tests + compileall ✓ |
| T14 — Security and privacy review | todo | — | — | — |
| T15 — Release readiness + runtime propagation decision | todo | — | — | — |



## Gates Status

| Gate | Status | Reviewer |
|---|---|---|
| intake | PASSED | factory-orchestrator |
| planning | PASSED | factory-orchestrator |
| architecture | PASSED | factory-orchestrator |
| functional | PASSED | factory-orchestrator |
| quality | PASSED | factory-orchestrator |
| implementation | FAILED | claude-builder |
| critical_readiness | PENDING | factory-orchestrator |
| delivery | PENDING | factory-orchestrator |
| security | PENDING | factory-orchestrator |


## Notion PM Projection

Notion PM page: https://app.notion.com/p/Zeus-Signature-Core-Refactor-PDF-Signing-Collection-Hotfix-Factory-PM-37e37b39cad6812ea750f19285329717
Notion is active as human PM projection; repo-local `TRACKER.md` + Factory DB remain agents' source of truth.

## Source of Truth

Factory DB (`factory.*`) + repo artifacts under `factory/projects/zeus-signature-core-refactor-hotfix/` are the canonical source of truth.

## 2026-06-19 Reactivation / Anti-regression Note

Jean authorized activation after QR Soap closure. Zeus audited the legacy Signature branches against current `origin/main` before reactivation:

- Directly merging `factory/factory-runtime-contract-v1` or old T07/T12/T14 branches would reintroduce broad legacy diffs, including hundreds of deletes/modifications outside Signature Core.
- Reactivation must therefore use a fresh integration branch from current `origin/main`, not the old base branch.
- Scope for T14R: port only the still-missing Signature Core security behavior and tests required by T14: recipient-bound `signer_token` + OTP enforcement, multi-signer completion guard, protected signed/audit PDF downloads, and negative security tests.
- Existing `main` already contains initial Signature Core commits (`c5492841f`, `0f1f1419a`); T14R must not overwrite those with stale branch snapshots.

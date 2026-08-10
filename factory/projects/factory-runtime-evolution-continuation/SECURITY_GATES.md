# Security Gates — Factory Runtime Evolution — Continuation

| Field | Value |
|---|---|
| Document status | validated:true (implementation-planner, 2026-08-10); reviewed:true (solution-architect, 2026-08-10, planning gate 690) |

## 1. Escalation allowlist (only genuine Jean conditions)

A project block may become an actionable Jean question ONLY when it maps to one of
these categories (closed enum `JeanEscalationCategory`, enforced fail-closed in FRE-012):

| Category | Meaning | Evidence required |
|---|---|---|
| `external_authority` | Third-party/regulator/external-system decision **independently verified from the original source** (not inferred from worker prose) | source reference, date, verifier |
| `product_business_scope` | Genuine product/business decision with options only Jean can pick | options, impact, affected scope |
| `security_approval` | Approval no Factory role can grant (routine gates are approved by security-reviewer, NOT this category) | threat/risk note, approver need |
| `payment_credential_access` | Credentials, secrets, payments, or access grants | resource, requester, least-privilege note |
| `bounded_exhausted_repair` | Same task exceeded its deterministic retry ceiling (default 2, `SUPERVISOR_TECHNICAL_REWORK_MAX_RETRIES`) after concrete repair attempts | repair history (attempts, outcomes, timestamps) |

**Explicitly NOT actionable:** generic "requires human decision" prose, stale questions
whose task is no longer blocked, self-generated classifier fallbacks, routine technical
failures, resolved-gate mentions, missing-doc/artifact reconciliation findings
(autonomous repair), or any question without concrete text + options + evidence.

## 2. Fail-closed rules (preserved, never weakened)

- G0: no dispatch when repository strategy has missing fields.
- G1: implementation tasks remain unclaimable while any required readiness marker is
  absent (exists, indexed, committed, validated, reviewed), unless Jean authorizes an
  exception for the exact project.
- Autonomy: `manual_attention`, terminal statuses, and manual-takeover leases force
  autonomy off (`_project_status_forces_autonomy_off`, `_manual_takeover_dispatch_filter`).
- Escalation: missing/invalid category ⇒ autonomous repair path, never a Jean question
  (ADR-010-4).
- Resume: preflight refuses terminal statuses (`terminal_<status>`), manual_attention
  without runnable work, delivery_hold/blocked without runnable work.
- No `required_docs_waived` / `notion_waived` / equivalent suppressors without Jean's
  explicit authorization for that exact project.

## 3. Runtime/DB security requirements (downstream increments)

| Requirement | Rule |
|---|---|
| Write paths | Factory DB writes ONLY through canonical `hermes factory …` CLI / Factory tools. No ad-hoc psql/psycopg2/scripts for `factory.*`. |
| Question lifecycle | Retirement and escalation transitions write `factory.events` rows with metadata (audit trail). No silent deletion of `human_questions` rows. |
| Reopen | `reopen_project()` must record a `reopen` gate, lineage metadata, actor, and timestamp; cancelled/superseded reopen requires Jean approval. No bypass of preflight. |
| Cron | Scripts run repo-backed code via wrappers; no forked logic in `~/.hermes/scripts`; no alert loops (event dedup + idle silence); non-Factory crons stay in `sitiouno-agent-runtime`. |
| Config | No new `HERMES_*` env vars for behavioral settings (config.yaml); `.env` only for secrets. |
| Migrations | No schema-destructive changes without a dedicated migration increment through `db/modules/factory/*` and Jean approval if destructive. |
| Secrets | Never embed credentials/tokens in docs, tests, or scripts; evidence redacts secrets. |

## 4. Security review gates

| Increment | Security gate |
|---|---|
| FRE-010 | Documentary: allowlist defined; no runtime code; no secrets. Review by solution-architect (+ security-reviewer visibility). |
| FRE-011 | Retirement logic cannot delete or weaken audit trail; requeue bounded; no autonomy bypass. security-reviewer review. |
| FRE-012 | Escalation allowlist enforced as closed enum; validation fail-closed; no classifier-only escalation. security-reviewer gate REQUIRED. |
| FRE-013 | Cron wrappers unchanged; no new write surface; idle silence; dedup preserved. devops-release + security-reviewer. |
| FRE-014 | Reopen preflight cannot be bypassed; lineage metadata immutable-by-convention; approval path for cancelled/superseded. security-reviewer + solution-architect. |
| FRE-015 | Independent security review of the whole increment set with real evidence. |
| FRE-017 | Cron resume order + evidence; no credential changes; no prod deploy. devops-release. |

## 5. Delivery boundary

- This project is `zeus_only`: no product-runtime code, no sandbox deploy, no
  production change. Sandbox (`kidu.app` / `/srv/factory/projects/<project>`) applies
  only if a future scope adds a dashboard/UI surface, and production stays HOLD until
  Jean's explicit decision.

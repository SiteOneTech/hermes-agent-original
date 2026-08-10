# ADRs — Factory Runtime Evolution — Continuation

| Field | Value |
|---|---|
| Document status | validated:true (implementation-planner, 2026-08-10); reviewed:true (solution-architect, 2026-08-10, planning gate 690) |

ADR format: status, context, decision, consequences. Decisions below are planning-level
(accepted for downstream increments); each increment confirms or amends its ADRs at
kickoff with the solution-architect.

---

## ADR-010-1 — Human-question lifecycle with evidence retirement

- Status: Accepted (planning)
- Context: `factory.human_questions` rows stay `pending` forever; the supervisor escalates
  to `manual_attention` on ANY pending question without re-validation
  (`factory_pg.py:4584–4586`). Stale/generic/self-generated questions therefore become
  absorbing escalations.
- Decision: Add an explicit question lifecycle on the existing table via `status`
  (`pending → stale | retired | answered`) and metadata, with mandatory `factory.events`
  rows for every transition. Retirement reasons are typed: `stale` (task no longer
  blocked / blocker resolved / question older than TTL), `generic` (no concrete question
  or options after validation), `self_generated` (classifier-produced without verified
  external evidence). Retirement requeues the task as bounded `rework` (or closes it if
  the blocker is resolved) and never marks the project `manual_attention` by itself.
- Consequences: + Deterministic cleanup of absorbing escalations; every retirement is
  auditable. − Requires validation logic in the supervisor path (ADR-010-2) and a TTL
  default (open question Q2); no schema migration required (status + metadata only).

## ADR-010-2 — Re-validate before manual_attention; bounded repair first

- Status: Accepted (planning)
- Context: The supervisor's escalation order is wrong: `pending_questions` short-circuits
  `clear_resolved_blockers` and the bounded requeue path.
- Decision: Reorder `supervisor_health_check()` repair as: (1) monitor/finalize runs,
  (2) clear resolved blockers, (3) classify, (4) bounded requeue of technical rework,
  (5) re-validate pending questions (freshness + task still blocked + escalation
  category), (6) retire invalid questions with events, (7) only then consider
  `manual_attention` — and only for: verified external authority, product/business scope,
  security approval, payment/credential/access, or exhausted bounded repair loop.
  Escalation must include the evidence and category in metadata.
- Consequences: + Premature manual_attention becomes impossible for routine technical
  blocks; invariant allowlist becomes the single escalation gate. − Existing tests that
  assert the current order (`test_supervisor_moves_existing_human_question_to_manual_attention`
  in `tests/hermes_cli/test_factory_control_plane_refactor.py:850`) must be updated as
  RED tests in FRE-011/012.

## ADR-010-3 — Canonical continuation/reopen for the self-improvement lineage

- Status: Accepted (planning)
- Context: Terminal self-improvement projects cannot be resumed (`terminal_<status>`
  preflight block); the orchestrator created a detached successor project
  (`factory-runtime-evolution-continuation`, event 172950) instead of reopening
  `factory-runtime-evolution`.
- Decision: Add `hermes factory project reopen <project_id> [--reason ...]` (alias
  `continue`) as the canonical non-terminal transition for `completed`/`accepted`
  projects that declare a self-improvement lineage (metadata `lineage` or
  `continuation_of`). The operation: records lineage metadata both ways
  (`continuation_of` on the reopened project; `superseded_by_project_id` already
  supported by `close_project()`), creates a `reopen` gate, runs G0/G1 preflight
  (artifact dir + required docs + repo strategy passed), and restores `active` only if
  preflight passes. Intake adds a lineage check: if a terminal project with the same
  lineage exists, propose reopen instead of creating a successor. `cancelled`/`superseded`
  reopen requires explicit Jean approval (open question Q1).
- Consequences: + One living self-improvement product with lineage; detached successor
  projects become a fail-closed exception. − New CLI surface needs tests, docs, and a
  gate policy; product projects keep terminal semantics (no accidental reopen).

## ADR-010-4 — Closed escalation-allowlist enum with fail-closed validation

- Status: Accepted (planning)
- Context: Escalation currently depends on classifier text matching
  (`_BLOCKER_EXTERNAL_OWNER_PHRASES`, `_BLOCKER_HUMAN_DECISION_KEYWORDS`), which is
  noisy and produced the legacy generic-question class.
- Decision: Introduce `JeanEscalationCategory` closed enum in `factory_contracts.py`
  with the five genuine categories (external_authority, product_business_scope,
  security_approval, payment_credential_access, bounded_exhausted_repair). Every
  human question and every `manual_attention` metadata MUST carry exactly one category;
  validation fails closed (⇒ autonomous repair path) when the category is missing,
  unknown, or unsupported by evidence fields. Classifier text matching remains only as a
  hint to build the question draft; it can never authorize escalation alone.
- Consequences: + Deterministic, testable escalation contract; NFR-1 satisfied. −
  Existing classifier outputs (metadata `human_question_source`) need mapping during
  FRE-012; backward-compatible defaults for legacy rows (retire them per ADR-010-1).

## ADR-010-5 — Watchdog/cron single-output contract and incremental global verification

- Status: Accepted (planning)
- Context: INC-0008 restored repo-backed scripts; idle silence is fixed for `claimed=null`
  false positives; global cron verification is pending.
- Decision: The watchdog, blocker detector, and status sync consume the same supervisor
  output contract (project/task/gate/run + invariant + action + result + next action +
  optional human question). Cron resume is incremental and gated: status-sync →
  reviewer-dispatch (report-only) → blocker-detector → watchdog → orchestrator-tick,
  each with real smoke evidence (`hermes cronjob list`, exit 0, zero unexpected alerts).
  Crons never write to Factory DB outside the canonical `factory_pg` APIs and never
  create alert loops (event dedup + idle silence preserved).
- Consequences: + Verified global control plane; regression tests
  (`tests/hermes_cli/test_factory_cron_control_plane.py`) extend. − Requires
  devops-release coordination at FRE-013/017; no product-runtime impact.

## ADR-010-6 — G1 documentation discipline for this project

- Status: Accepted (executing)
- Context: The predecessor's INC-0009 incident (implementation before docs) is the
  canonical anti-pattern; G1 readiness requires exists+indexed+committed+validated+reviewed.
- Decision: This project bootstraps G1 before any code increment; every downstream
  increment updates the affected docs (SPRINT_PLAN, TASK_GRAPH, TRACKER, QA/security
  gates, DELIVERY_REPORT) in the same commit as its code; `DOCUMENTATION_INDEX.md` is
  the canonical map. No `required_docs_waived`-style suppression unless Jean explicitly
  authorizes it for the exact project.
- Consequences: + Fail-closed methodology; + reconciles R1/R2 anomalies. − Slight
  documentation overhead per increment (accepted).

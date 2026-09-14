# PRD — Sales Operator Core / Revenue Operator v2

Canonical historical PRD: `website/docs/developer-guide/sales-operator-core/PRD-001-sales-operator-core.md`.

## I9 authorized objective

I9 rebaselines the project from the completed Sales Operator Core v1/I8 runtime propagation into a **private Kidu cockpit for Revenue Operator v2**. The cockpit is an operator dashboard for Jean/Zeus to supervise revenue work for Empleado.uno without enabling real outbound execution.

The product outcome is visibility and control, not autonomous sending: show pipeline health, lead/revenue outcomes, data freshness, policy status, and no-send supervision from safe snapshots.

## Users

| User | Need | Boundary |
|---|---|---|
| Jean / Zeus | Inspect Revenue Operator state and decide next supervised actions. | Read-only/private cockpit; no browser-triggered external actions. |
| Factory reviewers | Verify no-send, freshness, synthetic-vs-real labeling, and sandbox safety. | Evidence comes from repo docs, safe snapshots, tests, and browser QA. |
| Runtime implementers | Build a reusable inherited cockpit surface later. | Must not inherit Zeus-only Factory/admin internals or credentials. |

## I9 functional requirements

1. The private Kidu cockpit must clearly distinguish **real data** from **synthetic/test/demo data** on every metric group where confusion is possible.
2. Every dashboard snapshot must include freshness/provenance fields such as `generated_at`, source scope, environment, and stale/unknown status.
3. Outcome metrics may be labeled as real only when backed by actual CRM/sales/operator events in the safe snapshot. Synthetic pilot data must be labeled synthetic and must never be counted as real customer interest, replies, demos, revenue, CAC, or conversion.
4. The cockpit must expose policy supervision: channel policy state, opt-out/stop status, rate-limit posture, queue mode, and blockers.
5. The default and I9-authorized mode is **no-send**: draft/supervision only. It may display recommended next actions, but not execute provider sends.
6. The UI must be private/sandbox-oriented for Kidu (`kidu.app` / `*.kidu.app`) and must consume safe exported snapshots only.
7. Safe snapshots must contain no credentials, provider tokens, raw secrets, or privileged Factory/admin internals.

## I9 non-goals / hard boundary

I9 must not:

- enable providers;
- enable `auto_send`;
- send cold WhatsApp messages;
- execute email/SMS/voice/social/WhatsApp actions from the browser;
- create production deployment claims;
- expose credentials or raw provider configuration in UI data;
- present synthetic I7/I8 pilot metrics as real outcomes.

## Data contract for private UI snapshots

Minimum snapshot contract for implementation tasks:

| Field group | Required behavior |
|---|---|
| Snapshot metadata | `generated_at`, exporter version, source environment, source commit if available, and freshness/staleness status. |
| Data classification | Per section or record: `real`, `synthetic`, `mixed`, or `unknown`; mixed/unknown must render visibly. |
| Outcome metrics | Separate real outcomes from synthetic/test fixtures. Unknown provenance cannot be counted as real. |
| Policy state | Show queue mode (`draft_only`/`supervised_send`/blocked), no-send state, opt-out/stop flags, rate-limit posture, and required human gates. |
| Sanitization | No secrets, provider credentials, auth tokens, raw cookies, private keys, or unsafe external-action payloads. |

## Acceptance criteria for I9 planning baseline

- PRD, ADRS, TECHNICAL_BLUEPRINT, SPRINT_PLAN, TASK_GRAPH, QA_GATES, SECURITY_GATES, TRACKER, and DOCUMENTATION_INDEX describe the Revenue Operator v2 private Kidu cockpit and its no-send boundary.
- The task graph defines mandatory UI phases: implementation, quality_review, security_review, deploy, QA browser/post-deploy, and delivery report.
- Control-pack documents declare that the private interface uses safe snapshots, contains no credentials, and never reports synthetic metrics as real results.

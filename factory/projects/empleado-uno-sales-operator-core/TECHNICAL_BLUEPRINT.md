# TECHNICAL_BLUEPRINT — Sales Operator Core / Revenue Operator v2

## I9 target architecture

I9 targets a private Kidu cockpit for Revenue Operator v2. It is a read-only/supervision surface built from sanitized snapshots; it is not an outbound action runtime.

```text
Agent Core Postgres / Sales Operator state
        |
        | controlled exporter / report job
        v
Safe snapshot artifact (JSON/static data, no secrets)
        |
        v
Private Kidu cockpit UI (read-only supervision)
```

## Components in scope for downstream implementation

| Component | Responsibility | I9 boundary |
|---|---|---|
| Snapshot exporter | Produce safe JSON for cockpit sections from Agent Core/sales data. | Must strip credentials, provider tokens, raw secrets, unsafe payloads, and Factory/admin internals. |
| Snapshot schema | Carry metadata, freshness, provenance, and data classification. | `real`, `synthetic`, `mixed`, and `unknown` are explicit states; unknown cannot count as real. |
| Cockpit UI | Render pipeline/outcomes, freshness, policy/no-send state, blockers, and next draft actions. | Read-only; no browser external sends or provider invocations. |
| Policy supervision panel | Show queue mode, opt-out/stop, rate-limit posture, channel gates, no-send lock, and blockers. | May only display/diagnose; cannot unlock channels. |
| QA/browser evidence | Validate rendering and post-deploy sandbox behavior. | Sandbox only; production remains HOLD. |

## Required UI data sections

1. Snapshot header: generated time, environment/source, exporter version, commit/version if available, freshness status.
2. Data provenance banner: real/synthetic/mixed/unknown counts and warning text for synthetic/mixed/unknown data.
3. Revenue/operator outcomes: separated real metrics and synthetic/test metrics; no combined misleading total.
4. Pipeline/funnel state: leads, opportunities, follow-ups, blockers, and human-handoff items with source labels.
5. Policy/no-send supervision: queue mode, external sends disabled/enabled status, required gates, opt-outs/stops, rate-limit state, and channel readiness.
6. Draft next actions: recommendations only, with no external action execution from browser.

## Snapshot safety rules

- Snapshot artifacts must be safe to place under `/srv/factory/artifacts/empleado-uno-sales-operator-core/<run-id>` or project `user-data` for Kidu sandbox review.
- Snapshot artifacts must not include secrets, credentials, cookies, bearer tokens, private keys, provider config values, raw webhook signatures, or broad internal admin state.
- Synthetic/test/demo rows must carry explicit metadata and must remain visually separated from real outcomes.
- Freshness must be visible; stale or missing timestamps become a QA blocker.

## Deployment boundary

The authorized delivery layer for later UI deploy tasks is Kidu sandbox (`kidu.app` / `*.kidu.app`) under the Factory sandbox contract. I9 planning does not deploy. Any subsequent deploy task must use sandbox-only paths and leave production HOLD until Jean explicitly approves production.

## Verification strategy

- Documentation verification: required I9 terms and no-send constraints appear in PRD, ADRS, TECHNICAL_BLUEPRINT, SPRINT_PLAN, TASK_GRAPH, QA_GATES, SECURITY_GATES, TRACKER, and DOCUMENTATION_INDEX.
- Schema/static validation: snapshot examples or live exports must be inspected for `generated_at`, provenance/classification, freshness, policy state, and absence of credential-like fields.
- Browser QA: private cockpit renders classification/freshness/policy/no-send warnings and has no outbound action controls.
- Security review: confirm no credentials in artifacts and no browser path to provider sends.

# QA_GATES — Sales Operator Core / Revenue Operator v2

Detailed historical QA/security gates: `website/docs/developer-guide/sales-operator-core/QA-SECURITY-GATES.md`.

## I9 QA scope

QA for I9 and downstream Revenue Operator v2 cockpit work verifies a private Kidu dashboard that reads safe snapshots, distinguishes real/synthetic data, displays freshness and outcome provenance, supervises policy/no-send state, and does not execute external actions.

## Hard QA failures

- Any metric group combines synthetic/test data with real outcomes without a visible distinction.
- Synthetic pilot data is labeled or implied as real customer interest, replies, demos, revenue, conversion, CAC, or sales.
- Snapshot freshness is missing, stale without warning, or hidden from the operator.
- Snapshot contains credentials, provider tokens, cookies, private keys, or raw secret values.
- UI contains buttons/forms/links that execute WhatsApp/email/SMS/voice/social/provider sends from the browser.
- UI or docs claim provider enablement, `auto_send`, cold WhatsApp, or production launch in I9 scope.
- Private/sandbox cockpit exposes public/customer-facing wording that suggests prospects can access the dashboard.

## Required QA checks by phase

| Phase | QA check | Evidence |
|---|---|---|
| planning | Required docs include I9 scope, no-send boundary, safe snapshots, no credentials, synthetic-vs-real rules. | Content search / diff review. |
| implementation | Snapshot schema includes metadata, freshness, provenance, data classification, and policy/no-send state. | Tests or validation command output. |
| implementation | Cockpit renders real/synthetic/mixed/unknown states and stale/unknown warnings. | Component/browser evidence. |
| quality_review | UI copy and metrics are unambiguous and do not overclaim outcomes. | Review report. |
| security_review | Snapshot and browser behavior have no secret/action-send paths. | Security report. |
| deploy | Deployment is sandbox/Kidu only and production remains HOLD. | Deploy log/URL/artifact evidence. |
| QA browser/post-deploy | Browser QA verifies rendered badges, freshness, policy/no-send panel, and no external action controls. | Browser report/screenshots/logs. |
| delivery report | Final report captures commit, checks, sandbox evidence, no-send status, and blockers. | Delivery report and Factory gate evidence. |

## Snapshot QA checklist

- `generated_at` or equivalent exists and is visible in UI.
- Freshness state is one of fresh/stale/unknown or equivalent and stale/unknown is visually flagged.
- Every outcome metric has provenance: real, synthetic, mixed, or unknown.
- Synthetic/demo/test data is separated from real totals.
- Policy state shows queue mode and no-send status.
- No key names or values indicate credentials/secrets (`token`, `secret`, `password`, `api_key`, `cookie`, private key material, bearer values) in deliverable snapshots.

## Browser QA checklist

- Private cockpit loads from Kidu sandbox target.
- Header/banner identifies environment and data freshness.
- Real/synthetic/mixed/unknown labels are visible without opening dev tools.
- Policy/no-send section states external sends are disabled or blocked unless future gates change it.
- There are no send/approve/send-now controls that trigger external provider actions.
- Post-deploy evidence includes the tested URL, timestamp, commit/artifact, and pass/fail findings.

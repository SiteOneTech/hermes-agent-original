# SECURITY_GATES — Sales Operator Core / Revenue Operator v2

Detailed historical QA/security gates: `website/docs/developer-guide/sales-operator-core/QA-SECURITY-GATES.md`.

## I9 security posture

I9 is a private/sandbox cockpit planning baseline. It authorizes visibility and supervision only. It does **not** authorize provider enablement, `auto_send`, cold WhatsApp, browser-triggered sends, production deployment, or credentials in UI artifacts.

## Hard security blockers

- Any credential, provider token, API key, cookie, private key, webhook secret, bearer token, or password appears in a snapshot, static artifact, browser bundle, screenshot, report, or dashboard copy.
- Browser UI can invoke email/WhatsApp/SMS/voice/social/provider sends or external side-effect actions.
- A dashboard control can change channel policy from blocked/draft to send-enabled.
- Synthetic/test/demo data is represented as real customer engagement, revenue, CAC, replies, demos, or conversion.
- Cold WhatsApp or business-initiated WhatsApp outreach is enabled or implied without a later explicit channel/security gate.
- Production is deployed or represented as launched without Jean's explicit future approval.
- Raw Factory/admin internals or privileged operator tools are exposed to the cockpit user-data artifact.

## Required controls

| Control | Requirement |
|---|---|
| Safe snapshot export | Exporter must sanitize secrets and privileged internals before data reaches Kidu UI. |
| Data provenance | Real/synthetic/mixed/unknown state must be explicit and preserved from snapshot to UI. |
| Freshness | Snapshot timestamp and stale/unknown status must be visible; missing freshness blocks delivery. |
| No-send lock | Queue mode and external-send disabled/blocked state must be visible. |
| Browser action isolation | Browser can display draft recommendations only; no provider side effects. |
| Sandbox-only delivery | Kidu deployment is for review; production stays HOLD. |
| Evidence | Security review must inspect artifacts, not just intent/prose. |

## Credential and artifact inspection expectations

Security review must inspect the actual deliverable artifacts available in the implementation/deploy task:

- snapshot JSON/static data;
- built frontend bundle or rendered source where practical;
- screenshots/browser report;
- deployment metadata/path;
- Factory docs and delivery report.

Any credential-like field/value must be treated as a blocker until removed or proven to be a harmless placeholder in a non-deliverable test fixture. Do not rely on provider defaults or hidden environment variables to keep the UI safe; the artifact itself must be safe.

## Outbound and policy boundary

- Allowed in I9: display policy state, draft next actions, blockers, queue mode, stale/fresh status, and instructions for future supervised action.
- Not allowed in I9: provider connection, provider send, unlock channel gate, send approval, WhatsApp cold outreach, direct external action from browser, or production activation.

## Review handoff

If a later builder needs to change this boundary, they must open a new Factory task/gate with explicit human authorization. Until then, all reviewers must fail changes that relax the no-send boundary.

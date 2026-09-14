# ADRS — Sales Operator Core / Revenue Operator v2

Primary historical ADR: `website/docs/developer-guide/sales-operator-core/ADR-001-local-sales-operator-core.md`.

## ADR-I9 — Private Kidu cockpit via safe snapshots, no-send boundary

Status: proposed for I9 planning gate; ready for solution-architect review.

### Context

Sales Operator Core v1 through I8 delivered Agent Core schema/tools, no-send dry runs, synthetic pilot smoke, and runtime propagation. The authorized I9 objective is not broader outbound automation; it is a private Kidu cockpit that lets Jean/Zeus supervise Revenue Operator v2 safely.

Revenue cockpit data can mix real operational state, synthetic pilot fixtures, and dry-run outputs. Without explicit provenance and freshness, a dashboard could accidentally imply that synthetic tests are real revenue or that provider status means prospect engagement.

### Decision

Build the Revenue Operator v2 private cockpit as a read-only/private UI over **safe exported snapshots**.

- Source of truth remains Agent Core Postgres plus project-local Factory docs/evidence.
- The browser/UI receives sanitized JSON/static snapshot data only; it does not receive database credentials, provider credentials, or Factory/admin secrets.
- The UI must render data classification (`real`, `synthetic`, `mixed`, `unknown`) and freshness/staleness state prominently.
- Outcome metrics must be separated by provenance. Synthetic pilot rows can validate UI behavior but cannot be presented as real customer replies, demos, sales, revenue, CAC, or conversion.
- Policy/no-send status is first-class: queue mode, channel gate state, opt-out/stop posture, rate limits, and external-send blockers must be visible.
- The browser cannot execute outbound actions. Any next action is displayed as a draft/recommendation or links back to a supervised operator flow outside I9.

### Explicit no-send boundary

I9 does not authorize provider enablement, auto-send, cold WhatsApp, direct email/SMS/voice/social/WhatsApp sends, or execution of external actions from the browser. Production remains HOLD until Jean explicitly approves a later deploy/runtime gate.

### Consequences

- Implementation can move fast in Kidu sandbox because the UI is decoupled from live credentials.
- QA and security review must inspect both content and data semantics, not just page rendering.
- Any future runtime propagation must preserve the same snapshot and no-send boundary unless a later Factory task and gate explicitly changes it.
- The cockpit can show blockers and recommendations, but not perform external effects.

### Alternatives rejected for I9

| Alternative | Rejection reason |
|---|---|
| Live browser-to-Agent-Core DB/API with credentials | Unnecessary for I9 and increases secret/leak risk. |
| Provider-backed action buttons | Violates no-send boundary and would require channel/security gates not in scope. |
| Merging synthetic and real metrics into one total | Misleads operators and violates acceptance criteria. |
| Production/public dashboard | The authorized surface is private Kidu sandbox/cockpit, not production launch. |

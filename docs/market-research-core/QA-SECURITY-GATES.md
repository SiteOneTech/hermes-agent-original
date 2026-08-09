# QA and Security Gates — Market Research Core

**Status:** Current concise reference. Controlling QA/security gates: [`factory/projects/zeus-independent-alpha-research/QA_GATES.md`](../../factory/projects/zeus-independent-alpha-research/QA_GATES.md) and [`SECURITY_GATES.md`](../../factory/projects/zeus-independent-alpha-research/SECURITY_GATES.md).

## Required proof
- A typed Zeus↔Magnus message is authenticated, schema-validated, idempotent, auditable and recoverable from transport failure.
- Only research/capability/result/alert types are accepted; tests prove no broker, order, risk, paper/live, promotion, config, credential, code or deployment action can enter via this channel.
- Evidence and Alpha Cards carry provenance, freshness, source terms and the actual data contract; bars are not represented as true footprint/order flow without granular evidence.
- The daily workshop has a 45-minute cap, up to six substantive turns per agent and no more than three cards/topics; it closes with a typed synthesis.
- Reactive alerts are evidence-backed, acknowledgement-driven and non-executing. Synthetic no-send testing proves routing before operational use.
- Source freshness, no acknowledgement, empty cycle, duplicate lineage, mirror failure and redaction behavior are observable.

No passing integration/pilot test authorizes paper/live promotion. That remains governed by Vonash’s existing policy and separate release decision.

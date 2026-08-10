---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: pending
---

# REQUIREMENTS ANALYSIS

## Functional requirements
| ID | Requirement | Enforceable acceptance evidence |
|---|---|---|
| R1 | Persist programs, sources, immutable evidence, research cycles, Alpha Cards, lineage, reviews, experiment-result references and inert handoff packages in `alpha_research`. Collaboration-session/message tables are excluded from v1. | migration constraint/trigger tests + real DB smoke |
| R2 | Preserve source reference, retrieval time, terms/license state, content hash, locator, normalized claim and falsification notes. | DB uniqueness/FK/append-only tests + tool tests |
| R3 | Prevent duplicate evidence and false novelty for parameter variants of an existing mechanism family. | direct-SQL duplicate/lineage-negative tests |
| R4 | Require mechanism, universe, regime/failure regime, data/cost/capacity/no-trade/falsification contract and immutable classifications `research_only`, `unvalidated`, `not_investment_advice` before a card reaches `reviewable`. | DB check/state-transition tests + forbidden-label tests |
| R5 | Record adversarial review separately from the author with a disposition/rejection rationale; review history is append-only. | role/trigger/review handler tests |
| R6 | A daily cycle is local only: it accepts a typed, normalized-evidence batch already present in the ledger; validates source policy/freshness/idempotency; then synthesizes, reviews and closes, including explicit empty/rejected outcomes. It performs no network collection. | deterministic cycle and rejected/stale/empty batch tests |
| R7 | Create only inert handoff packages with `authority_scope=research_only`, `dispatch_state=not_dispatched`, immutable disclaimers and no remote recipient/URL/token/action fields. | serialization/negative-field/direct-SQL tests |
| R8 | Provide small JSON handlers only in a non-default `alpha_research` leaf toolset. | default-toolset absence + exact leaf allowlist tests |
| R9 | Support an adapter-neutral source registry and local normalized-evidence intake. A source cannot be used unless enabled, terms state is approved and its defined freshness policy accepts the evidence. Concrete third-party drivers remain out-of-tree standalone plugin/MCP/CLI deliveries. | source-policy DB and handler-negative tests |
| R10 | Use an Infisical-managed dedicated database runtime secret. Toolset activation fails closed if that reference is absent; no broad-role/fallback DSN is permitted. | role/secret-presence-only activation-negative tests |

## Local evidence intake contract for R6/R9
`evidence_record` accepts a bounded local JSON payload: `source_id`, `source_reference`, `source_locator`, `content_sha256`, `retrieved_at`, `freshness_observed_at`, `normalized_claim`, `falsification_notes`, `cycle_id` and opaque `idempotency_key`. It stores a reference string as data and has no fetch, URL-open, recipient, bearer token, subprocess or remote-DSN capability. The `alpha_research_runtime` role/toolset is the only v1 caller path. Results are `accepted`, `duplicate`, `rejected_source_disabled`, `rejected_terms`, `rejected_stale`, `rejected_malformed` or `rejected_classification`.

## Non-functional requirements
- UTC timestamps, UUID identifiers, payload size limits and SQL-safe structured JSON.
- Append-only evidence/review/handoff audit history: corrections create superseding revisions, never mutation/deletion by the runtime role.
- Idempotent daily cycle key and terminal failure/empty status.
- No runtime dependency on a Vonash URL, issue state, shared secret, external database or external connector.
- Tests are written first for every production behavior and observed failing before implementation.

## Boundary requirements
No function, table, tool, schedule, script or handoff may introduce `trade`, `order`, `broker`, `risk_change`, `promotion`, `paper_activation`, `live_activation`, `deployment`, `credential_export`, `external_message_send`, external HTTP/network egress or cross-system database write behavior. Cards, reviews and handoffs must reject `validated_alpha`, investment advice/recommendation, strategy approval, operational directive and external activation labels/fields.

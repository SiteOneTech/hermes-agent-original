---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: yes
reviewed_by: solution-architect
review_evidence: factory_gate_794
reviewed_candidate_sha: c81547062c5362a7be6f5a1bb2ef9612b29bac9c
reviewed_candidate_pr: https://github.com/SiteOneTech/hermes-agent-original/pull/36
reviewed_source_gate: factory_gate_790
reviewed_source_sha: 2476e978c545e24b18ee48844b24eb8c58245ab4
---

# REQUIREMENTS ANALYSIS

## Functional requirements
| ID | Requirement | Enforceable acceptance evidence |
|---|---|---|
| R1 | Persist programs, sources, immutable evidence, cycles, cards, lineage, reviews, result references, inert handoffs and scheduler readiness in `alpha_research`. Collaboration session/message tables are excluded. | migration object/absence/constraint tests |
| R2 | Preserve immutable source reference and terms-evidence reference, timestamps, exact terms/freshness policy, auditable admin approval/revision provenance, content hash, locator, normalized claim and falsification notes. | contract §2 direct SQL + handler tests |
| R3 | Prevent duplicate evidence and false novelty for parameter variants of an existing mechanism family. | direct SQL duplicate/lineage-negative tests |
| R4 | Require field-by-field typed/bounded mechanism, universe, regime/failure regime, data/cost/capacity/no-trade/falsification input and immutable `research_only`/`unvalidated`/`not_investment_advice` tuple before the only permitted reviewable transition. | contract §1/§3 state/input/tuple tests |
| R5 | Record adversarial review separately from author with immutable research-only classification and rationale. | role/trigger/review tests |
| R6 | Daily cycle consumes a bounded local normalized-evidence batch, validates source policy/freshness/idempotency and closes with accepted/empty/rejected/failed outcome. It never performs network collection. | deterministic cycle/readiness tests |
| R7 | Create only inert packages with fixed research-only/not-dispatched state, fixed typed handoff-list objects, and no recipient/transport/token/URL/action/unknown fields. | contract §3 serialization/negative tests |
| R8 | Provide only JSON handlers in the non-default exact leaf toolset: `alpha_research_status`, `program_create`, `source_submit`, `evidence_record`, `alpha_card_create`, `alpha_card_review`, `cycle_start`, `cycle_close`, `inert_handoff_prepare`, `handoff_list`. | default-absence/exact-allowlist tests |
| R9 | Support exact adapter-neutral source classes and local intake. Concrete provider drivers are out-of-tree standalone integrations. | contract §2 source policy tests |
| R10 | Use only dedicated Infisical local role secret reference; no fallback role/DSN or secret disclosure in persistence/output/log/error/trace. Scheduler stays default-disabled until durable local readiness verifies. | contract §1/§3/§4/§5 tests |

## Normative contracts
- Exact database/role/source/classification/no-egress/scheduler implementation requirements: `DATABASE_AND_RUNTIME_CONTRACT.md`.
- Requirement-to-task/test/reviewer/gate mapping: `REQUIREMENTS_TRACEABILITY.md`.

## Non-functional requirements
- UTC timestamps, UUIDs, bounded payloads and SQL-safe structured JSON.
- Corrections supersede evidence/review records rather than silently mutating them.
- Tests are written first and observed failing for each production behavior.
- No runtime dependency on Vonash URL, shared secret, external DB or connector.

## Boundary requirements
No function, table, tool, schedule, script or handoff may introduce network egress, trade, order, broker, risk change, promotion, paper/live activation, deployment, credential export, external messaging or cross-system DB write. Cards, reviews and handoffs reject validated-alpha, investment advice/recommendation, strategy approval and operational-action fields.

---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: pending
---

# TECHNICAL BLUEPRINT

## Normative implementation reference
`DATABASE_AND_RUNTIME_CONTRACT.md` is binding for ALR-020/030/050. It supplies the exact role/object allowlist, enum values, source freshness predicate, classification tuple, static/runtime no-egress harness and scheduler readiness protocol. This blueprint defines component placement and cross-document architecture; if a summary conflicts with the contract, the contract wins.

## Architecture
```text
local normalized-evidence batch (no network client)
        ↓ source policy / freshness / idempotency validation
alpha_research.source_registry → alpha_research.evidence_items
        ↓
research_programs → research_cycles → alpha_cards → alpha_lineage
                                      ↓              ↓
                                  research_reviews  experiment_result_refs
        ↓
inert_handoff_packages + runtime_readiness (local-only, non-dispatching)
        ↓
chat-first alpha_research JSON tools / non-default leaf toolset
```

## Entities and database invariants
| Entity | Responsibility | Required invariant |
|---|---|---|
| `research_programs` | mandate, owner, universe, local lifecycle | UUID PK; constrained local status and no delete grant |
| `source_registry` | local source class, terms and freshness policy | exact source/terms/freshness enum and check contract in §2; no provider secret/endpoint field |
| `evidence_items` | immutable source record and claim | source FK; unique `(source_id, content_sha256, source_locator)`; supersession FK; insert-only trigger |
| `research_cycles` | idempotent local cycle/outcome | unique `(program_id, cycle_key)`; explicit empty/rejected/failed terminal state |
| `alpha_cards` | research hypothesis/design object | evidence-backed transition function; immutable typed research-only tuple |
| `alpha_lineage` | parent/variant/family relationship | card FKs; no self-parent or duplicate-family relation |
| `research_reviews` | separate skeptical review | reviewer/disposition contract; append-only; immutable typed research-only tuple |
| `experiment_result_refs` | non-authoritative result references | comparability metadata prior to rankable flag |
| `inert_handoff_packages` | deterministic local package | exact allowed-key JSON; immutable typed research-only tuple; fixed not-dispatched state |
| `runtime_readiness` | durable scheduler prerequisites | admin-written, hash-backed, expiring component evidence; runtime read-only |

FKs, checks, unique indexes, triggers and one narrow transition function are authority. Handler validation is supplementary only. No collaboration session/message entity exists in v1.

## Role, source, classification and runtime gates
- **Role model:** `agent_admin` owns DDL; a `LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS` `alpha_research_runtime` role owns no schema object and receives only the table/function grants in contract §1. It has no membership, broad-role fallback, `PUBLIC` access or cross-schema DML.
- **Source intake:** exact allowed source classes are `local_normalized_batch`, `manual_reference_metadata`, `licensed_local_document`. Only `terms_status=approved` plus an exact static/max-age policy permits intake; max-age stale predicate and direct SQL cases are contract §2.
- **Research-only output:** cards, reviews, handoffs and every JSON envelope must carry the exact immutable tuple and must reject the prohibited labels/unknown fields enumerated in contract §3.
- **No egress:** project-owned paths, forbidden dependency/call patterns, database DSN shape and every-handler runtime harness are contract §4. Local DB is the only allowed connection.
- **Scheduler:** config `agent_core.alpha_research.scheduler.enabled` defaults `false`. Exact readiness rows and registration/invocation verifier are contract §5; no cache or fallback is allowed.

## Runtime wiring targets
- `db/modules/alpha_research/000001_alpha_research_schema.sql` — role shell, schema, types, tables, grants/revocations/default privileges, constraints/triggers/functions.
- `scripts/agent_core_db.py`, `hermes_cli/agent_core_sql.py`, `scripts/agent_core_roles.py`, `scripts/zeus-sync-secrets.sh` — migration/role/Infisical reference wiring, never a secret value.
- `tools/alpha_research_tool.py`, `toolsets/alpha_research.py`, `tests/tools/test_alpha_research_tool.py` — exact handlers and leaf registration.
- `scripts/alpha_research_cycle.py`, `tests/scripts/test_alpha_research_cycle.py` — default-disabled cycle and readiness verifier after ALR-070.

## Tool boundary
The leaf allowlist is exactly: `alpha_research_status`, `program_upsert`, `source_upsert`, `evidence_record`, `alpha_card_create`, `alpha_card_review`, `cycle_start`, `cycle_close`, `inert_handoff_prepare`, `handoff_list`. No handler is present in a default toolset. Every handler returns the contract §3 JSON envelope and has no network/recipient/URL/token/execution parameter.

## Future adapter seam
A later separately approved service may read a finalized local handoff through a typed contract. It may not reuse local tables as an external API, cross-write a database or treat a package as operational authority.

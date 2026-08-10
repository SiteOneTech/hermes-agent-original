---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: pending
---

# TECHNICAL BLUEPRINT

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
inert_handoff_packages (local-only, non-dispatching)
        ↓
chat-first alpha_research JSON tools / non-default leaf toolset
```

## Entities and database invariants
| Entity | Responsibility | Required invariant |
|---|---|---|
| `research_programs` | mandate, owner, universe, policy/status | UUID PK; constrained local status vocabulary |
| `source_registry` | source class, terms, policy and freshness | `enabled=true` requires `terms_status=approved`, non-null freshness policy and allowed source class; no provider secret field |
| `evidence_items` | immutable source record and claim | FK to approved source; unique `(source_id, content_sha256, source_locator)`; supersession FK; insert-only runtime trigger |
| `research_cycles` | idempotent daily run/outcome | unique `(program_id, cycle_key)`; terminal outcome is explicit including empty/rejected/failed |
| `alpha_cards` | research hypothesis/design object | evidence-backed state transition; mechanism fingerprint; fixed classification `research_only`/`unvalidated`/`not_investment_advice`; check prevents prohibited status/labels |
| `alpha_lineage` | parent/variant/family relationships | card FKs, unique relation/family guard and no self-parent relation |
| `research_reviews` | skeptical/methodological assessment | author distinct from reviewer where applicable; append-only runtime trigger; constrained disposition |
| `experiment_result_refs` | non-authoritative external result references | comparability metadata required before rankable flag may be true |
| `inert_handoff_packages` | deterministic local serialized package | `authority_scope=research_only`, `dispatch_state=not_dispatched`, immutable disclaimer; no recipient/transport/token/URL/action fields |

Database-level enforcement is required: FKs, checks, unique indexes and runtime-role insert-only triggers are the authority. Handler validation supplements but never substitutes for those constraints. Migration tests directly exercise rejected source state, stale freshness, duplicate evidence, mutation/deletion denial and prohibited card/handoff classifications.

## Role and grant matrix
| Principal | Allowed | Explicitly denied / excluded |
|---|---|---|
| migration/admin principal | owns schema and migration DDL only | not used by JSON handlers or scheduler |
| `alpha_research_runtime` | `USAGE` on `alpha_research`; only required `SELECT`/`INSERT` and narrow lifecycle `UPDATE` on explicitly named mutable tables; sequence usage only where required | `CREATE`, ownership, role membership/inherit escalation, `GRANT`, cross-schema DML, `factory`/`public` mutation, `PUBLIC` grants, FDW/dblink, fallback DSN/role, external DB credentials |
| `agent_runtime` and all other roles | no implicit access | no inherited module role membership or broad schema grant |

The migration must revoke `PUBLIC` schema/table/function privileges, set default privileges so future tables/functions are not exposed, and assert no `alpha_research_runtime` grant outside its allowlist. Tests connect as the runtime role and prove denied writes to `factory`, `public` and every non-allowlisted schema; denied update/delete of append-only evidence/reviews; and no `CREATE`/role escalation.

## Runtime wiring targets
- `db/modules/alpha_research/000001_alpha_research_schema.sql` with role shell, schema, grants, revocations, default privileges and invariants.
- `scripts/agent_core_db.py`, `hermes_cli/agent_core_sql.py`, `scripts/agent_core_roles.py`, `scripts/zeus-sync-secrets.sh`, sanitized runtime env example.
- `tools/alpha_research_tool.py`, `toolsets.py`, `tests/tools/test_alpha_research_tool.py`.
- A daily-cycle script after ALR-070 only; no source client, socket, HTTP, subprocess dispatch or remote DSN.

## Tool boundary
Expected handlers: `alpha_research_status`, `program_upsert`, `source_upsert`, `evidence_record`, `alpha_card_create`, `alpha_card_review`, `cycle_start`, `cycle_close`, `inert_handoff_prepare`, `handoff_list`.

Every handler returns JSON, validates before database calls, uses safe SQL literals and rejects fields/actions outside the research-only allowlist. Tests prove none of these handlers appear in default toolsets; the leaf toolset contains exactly this allowlist. Static/dependency tests reject `requests`, `httpx`, `urllib`, `socket`, broker/Vonash/Magnus/VAOS/KB clients, `APC_INTERNAL_SECRET`, remote DSNs and subprocess network dispatch across tools, scripts and handoff serialization.

## Scheduler activation
Scheduler registration is absent/disabled by default. It becomes locally enabled only when a config gate references successful ALR-070 evidence for schema migration, dedicated role/secret presence, approved local source policy, toolset isolation and synthetic no-egress smoke. Missing prerequisite, failed migration, absent secret, stale/disabled source or failed smoke means no registration/run; tests prove each negative case.

## Future adapter seam
A later system may read a finalized handoff package through a separately approved typed service. It may not reuse these local tables as an external API, cross-write the database or treat a package as an operational directive.

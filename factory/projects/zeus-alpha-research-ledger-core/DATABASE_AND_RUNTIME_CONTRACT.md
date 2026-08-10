---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: pending
---

# DATABASE AND RUNTIME CONTRACT

This is the binding ALR-020/030/050 implementation contract. A handler, migration or scheduler that differs from it fails QA even if unit behavior otherwise passes.

## 1. Principals, role attributes and object grants

### Principals

| Principal | Required attributes | Purpose | Must not be used by |
|---|---|---|---|
| `agent_admin` (existing migration principal) | existing admin lifecycle only | creates schema, types, tables, triggers, functions and grants | JSON tools, scheduler, chat handlers |
| `alpha_research_runtime` | `LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS CONNECTION LIMIT 5`; no memberships; role-level `search_path=alpha_research,pg_catalog` | only runtime identity, via dedicated Infisical secret reference | migration DDL, Factory schema, external DSNs |
| all other runtime roles | no membership in `alpha_research_runtime` | no implicit module authority | access to `alpha_research` unless explicitly added by a later reviewed ADR |

The migration must execute `REVOKE ALL ON SCHEMA alpha_research FROM PUBLIC`, revoke `ALL` on every table/sequence/function from `PUBLIC`, and set default privileges **for the migration owner in `alpha_research`** to revoke `PUBLIC` table, sequence and function privileges. It must grant database `CONNECT` and schema `USAGE` only as needed to the dedicated runtime role; it never alters unrelated schemas’ ownership or grants.

### Runtime table grant allowlist

| Object | `SELECT` | `INSERT` | `UPDATE` | `DELETE` | Notes |
|---|---:|---:|---:|---:|---|
| `research_programs` | yes | yes | yes | no | update limited by status/policy checks |
| `source_registry` | yes | yes | yes | no | update limited by terms/freshness/source-class checks |
| `research_cycles` | yes | yes | yes | no | update limited to terminal lifecycle transition |
| `evidence_items` | yes | yes | no | no | trigger additionally blocks mutation by any non-owner |
| `alpha_cards` | yes | yes | no | no | all lifecycle changes use `transition_alpha_card(uuid, target_status)` only |
| `alpha_lineage` | yes | yes | no | no | no self/family violation |
| `research_reviews` | yes | yes | no | no | append-only trigger additionally blocks mutation by any non-owner |
| `experiment_result_refs` | yes | yes | no | no | references only, never execution results |
| `inert_handoff_packages` | yes | yes | no | no | serialized once, never dispatched |
| `runtime_readiness` | yes | no | no | no | migration/admin writes verified prerequisites |

Runtime has `EXECUTE` only on `transition_alpha_card(uuid, alpha_card_status)` and no other `alpha_research` function. UUIDs are generated server-side, so no runtime sequence grant is expected; any later sequence requires an ADR plus explicit `USAGE`/`SELECT` row in this table. The migration asserts no other grants/functions/memberships using catalog queries.

### Direct-SQL privilege matrix

In a transaction authenticated as `alpha_research_runtime`, tests must prove: allowed operations in the table allowlist succeed; `UPDATE`/`DELETE` on `evidence_items`, `research_reviews`, `alpha_cards`, `alpha_lineage`, `experiment_result_refs` and `inert_handoff_packages` fail; `CREATE TABLE alpha_research.__denied`, `CREATE TABLE public.__denied`, `UPDATE factory.projects SET updated_at=updated_at WHERE false`, `INSERT INTO public.__denied VALUES (1)`, `GRANT`, `CREATE EXTENSION`, `CREATE SERVER`, `CREATE USER`, `SET ROLE agent_admin` and `dblink`/FDW use fail. A catalog-based assertion confirms the runtime role has no DML grant in every non-system/non-`alpha_research` schema and no privilege granted to `PUBLIC` in `alpha_research`.

## 2. Enumerations, source policy and evidence intake

### Allowed source fields

```text
source_class ∈ {local_normalized_batch, manual_reference_metadata, licensed_local_document}
terms_status ∈ {approved, unknown, rejected, expired}
freshness_mode ∈ {static, max_age}
```

`source_registry` has: `source_class`, `terms_status`, `enabled boolean NOT NULL DEFAULT false`, `freshness_mode`, `max_age_seconds`, and an immutable source policy revision identifier. Checks require:

- `enabled=true` only when `terms_status='approved'`;
- `freshness_mode='static'` requires `max_age_seconds IS NULL`;
- `freshness_mode='max_age'` requires `max_age_seconds BETWEEN 60 AND 31536000`;
- disabled/unknown/rejected/expired sources cannot accept evidence;
- no fields for API keys, bearer tokens, endpoints or provider driver configuration.

`evidence_items` requires non-null `retrieved_at`, `freshness_observed_at`, `content_sha256`, `source_locator`, source FK and normalized claim. It checks `freshness_observed_at >= retrieved_at`; the insert trigger rejects a future retrieval/observation time. For `max_age`, the trigger evaluates against database `clock_timestamp()` and rejects when `retrieved_at < clock_timestamp() - make_interval(secs => max_age_seconds)`; equality at the boundary is accepted. `static` accepts a nonfuture retrieved record regardless of age. The trigger also rejects a non-approved/disabled source. The unique key is `(source_id, content_sha256, source_locator)`.

### Deterministic source/evidence negative matrix

Direct SQL and handler tests must cover: invalid source class; enabled+unknown/rejected/expired terms; invalid static/max-age field combinations; max age below/above bounds; disabled source; source with unknown terms; valid max-age record comfortably inside the boundary; stale record at least 60 seconds outside the boundary; future retrieval/observation; observation earlier than retrieval; duplicate `(source, hash, locator)`; evidence update/delete; invalid/missing superseded evidence FK; lineage missing-card/self-parent/duplicate-family relation. Tests use buffered times rather than a timing-racy exact-now fixture; the predicate above is the exact boundary contract.

## 3. Typed research-only contract

Three persisted entities—`alpha_cards`, `research_reviews` and `inert_handoff_packages`—must each contain:

```text
classification_scope alpha_research.classification_scope NOT NULL DEFAULT 'research_only'
validation_state    alpha_research.validation_state    NOT NULL DEFAULT 'unvalidated'
not_investment_advice boolean NOT NULL DEFAULT true
advisory_disclaimer text NOT NULL DEFAULT 'Research only; unvalidated; not investment advice.'
```

`classification_scope` is an enum containing only `research_only`; `validation_state` is an enum containing only `unvalidated`. Checks require the exact tuple above, including `not_investment_advice=true` and the exact disclaimer version. A trigger rejects any later update to those four fields for every persisted carrier; `research_reviews` and handoffs remain entirely append-only. Cards may change lifecycle only through the one named transition function, which cannot alter the tuple.

Every JSON handler output and handoff serialization uses an exact `ResearchOutputEnvelope` with those fields plus `schema_version='alpha_research/v1'`. It rejects omitted, unknown or mismatched classification/disclaimer fields. Handoff JSON has an exact allowed-key schema and rejects `validated_alpha`, `investment_advice`, `recommendation`, `strategy_approved`, `promotion`, `order`, `risk`, `paper_activation`, `live_activation`, `deployment`, `action`, `recipient`, `transport`, `url`, `token` and any unknown operational field.

Tests use direct SQL and handlers to prove rejection for omitted tuple, wrong tuple, attempted tuple mutation, each named prohibited field/label, and external-action payloads across cards, reviews and handoffs.

## 4. No-egress contract

### Static scan

The test scans only project-owned implementation surfaces (not the broader Hermes codebase):

```text
hermes_cli/alpha_research*.py
tools/alpha_research_tool.py
scripts/alpha_research_*.py
db/modules/alpha_research/**
toolsets/alpha_research*.py
tests/**/alpha_research*.py
```

It rejects imports/calls for `requests`, `httpx`, `urllib`, `aiohttp`, `websockets`, `socket`, `ftplib`, `paramiko`, `boto3`, `subprocess`, `os.system`, `asyncio.create_subprocess_exec`, `asyncio.create_subprocess_shell`, broker clients, and Vonash/Magnus/VAOS/APC/RAG/KB client modules. SQL is rejected if it uses `dblink`, `postgres_fdw`, `CREATE SERVER`, `CREATE EXTENSION`, `COPY ... PROGRAM`, remote connection strings or `APC_INTERNAL_SECRET`.

### Runtime harness

A test harness executes every listed JSON handler with a valid fixture and a prohibited-field fixture, plus scheduler readiness evaluation, registration attempt and run invocation. It monkeypatches `socket.socket.connect`, `socket.create_connection`, HTTP transports, subprocess APIs, `os.system` and async subprocess creation to raise `UnexpectedEgress`. The only allowed database connection is the dedicated local DSN parsed from Infisical resolution: exact `host=127.0.0.1`, `port=55430`, `dbname=zeus_agent`, `user=alpha_research_runtime`; URI host/hostaddr overrides and any other host/port/db/user fail before connection. The test fails on every attempted egress—not merely on successful network access.

## 5. Scheduler configuration and durable readiness

Configuration key: `agent_core.alpha_research.scheduler.enabled`, default `false`; it is a non-secret Hermes configuration setting, never an environment fallback. A migration creates `alpha_research.runtime_readiness(component, status, source_commit, evidence_sha256, verified_at, expires_at, verified_by)`; only `agent_admin` writes it. Required components are:

```text
schema_migrated
dedicated_role_secret_verified
approved_source_policy_verified
toolset_isolation_verified
no_egress_smoke_verified
```

`verify_alpha_research_scheduler_readiness()` evaluates at registration **and every invocation** with no cache. It returns true only if config is exactly true and every required component is `passed`, is unexpired, references the current source commit, and has a nonempty evidence hash. Registration calls the verifier before registering; invocation calls it again before reading any cycle input. A false/missing/failed/expired/wrong-commit record produces local `scheduler_not_ready` and performs no run. Tests cover config false/missing, each missing component, failed component, expired evidence, wrong commit, missing evidence hash, missing secret, failed migration and no approved source policy.

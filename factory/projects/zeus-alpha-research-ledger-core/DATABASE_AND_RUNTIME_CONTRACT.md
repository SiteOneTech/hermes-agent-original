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

# DATABASE AND RUNTIME CONTRACT

This is the binding ALR-020/030/050 contract. A migration, handler, tool router or scheduler that differs from it fails QA.

## 1. Principals and exact least privilege

| Principal | Required attributes | Credential / purpose | Explicit exclusions |
|---|---|---|---|
| `agent_admin` | existing admin lifecycle only | DDL, policy approval and readiness records; never a handler/scheduler connection | chat/tools, external runtime, secret output |
| `alpha_research_runtime` | `LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS CONNECTION LIMIT 5`; no memberships; `search_path=alpha_research,pg_catalog` | Infisical-only **author** secret; local intake/card/cycle/handoff authoring | DDL, source approval, review insertion, Factory/public DML, external DSN |
| `alpha_research_reviewer` | same non-privileged attributes, no memberships, same safe search path | separate Infisical-only **reviewer** secret; independent review only | DDL, all card/source/cycle/evidence mutations, scheduler, Factory/public DML, external DSN |
| any other runtime role | no membership in either role | no implicit module authority | all `alpha_research` access absent explicit future ADR |

Migration requirements: revoke all schema/table/sequence/function privileges in `alpha_research` from `PUBLIC`; set default privileges for the migration owner in that schema to revoke `PUBLIC` table/sequence/function access; grant only needed database `CONNECT` and schema `USAGE` to the two dedicated roles; never alter unrelated schema ownership/grants.

### Object grants

| Object | author: SELECT/INSERT/UPDATE/DELETE | reviewer: SELECT/INSERT/UPDATE/DELETE | Enforced write rules |
|---|---|---|---|
| `research_programs` | yes / yes / no / no | yes / no / no / no | author insert only; any amendment is a new superseding program row |
| `source_registry` | yes / yes / no / no | yes / no / no / no | author candidate insert forces `terms_status=unknown`, `enabled=false`, policy revision `1`; only admin can approve/change policy |
| `research_cycles` | yes / yes / no / no | yes / no / no / no | only `transition_research_cycle(uuid, cycle_outcome, text)` changes allowed lifecycle fields |
| `evidence_items` | yes / yes / no / no | yes / no / no / no | append-only trigger; source policy checked on insert |
| `alpha_cards` | yes / yes / no / no | yes / no / no / no | author insert only; only `transition_alpha_card(uuid, alpha_card_status)` changes lifecycle |
| `alpha_lineage` | yes / yes / no / no | yes / no / no / no | insert-only FK/family checks |
| `research_reviews` | yes / no / no / no | yes / yes / no / no | reviewer insert only; append-only and independent-role trigger |
| `experiment_result_refs` | yes / yes / no / no | yes / no / no / no | insert-only references |
| `inert_handoff_packages` | yes / yes / no / no | yes / no / no / no | insert-only fixed package |
| `runtime_readiness` | yes / no / no / no | yes / no / no / no | admin-only writes |

The exact non-default leaf allowlist is `alpha_research_status`, `program_create`, `source_submit`, `evidence_record`, `alpha_card_create`, `alpha_card_review`, `cycle_start`, `cycle_close`, `inert_handoff_prepare`, `handoff_list`; no alias, upsert handler, or default-toolset registration is allowed. `program_create` and `source_submit` are the canonical creation/intake names; `program_submit`, `program_upsert`, `source_create`, `source_register`, `source_upsert`, or any other synonym fail catalog/registration tests.

Author has `EXECUTE` only on `transition_alpha_card(uuid, alpha_card_status)` and `transition_research_cycle(uuid, cycle_outcome, text)` after explicit `REVOKE ALL ON FUNCTION ... FROM PUBLIC` and exact signature grants. Reviewer has no function execution grant. UUIDs are server-generated; no runtime sequence grant exists. The migration asserts catalog-wide that the two roles have no unlisted grant/function/membership and `PUBLIC` has no privilege in `alpha_research`.

### Privilege and policy negative matrix

Tests authenticate as each role. Author allowed inserts above succeed; every table `UPDATE`/`DELETE` fails except updates performed inside the two explicitly granted lifecycle functions. Author `INSERT source_registry` with terms other than `unknown`, `enabled=true`, policy revision not `1`, or unapproved policy fields fails trigger/check; author `UPDATE source_registry` to self-approve/enable/alter freshness/revision fails privilege. Reviewer review insert succeeds only; reviewer card/source/evidence/cycle/handoff writes fail. Both roles must fail `CREATE TABLE alpha_research.__denied`, `CREATE TABLE public.__denied`, `UPDATE factory.projects SET updated_at=updated_at WHERE false`, `GRANT`, `CREATE EXTENSION`, `CREATE SERVER`, `CREATE USER`, `SET ROLE agent_admin` and dblink/FDW use. Catalog tests assert no DML grant in every other non-system schema.

### Lifecycle functions: the only narrowly elevated writes

Both functions are owned by `agent_admin`, declared `SECURITY DEFINER`, and have a function-local fixed `search_path` exactly `pg_catalog, alpha_research`; every referenced relation/type/function is schema-qualified despite that path. `PUBLIC` and reviewer have no `EXECUTE`; author has only the two signatures above. Because `SECURITY DEFINER` makes `current_user` the definer, authorization must use `session_user` only: it must be exactly `alpha_research_runtime` for author transitions or exactly `agent_admin` for the documented repair path. A session authenticated as any broader role and then changed with `SET ROLE` retains its broader `session_user` and is rejected; the implementation must never test `current_user <> session_user` inside the definer body. No other principal, dynamic SQL, caller-supplied identifier, or caller-controlled search path is accepted. The definer body has no network, extension, foreign-data, filesystem, DDL, grant, or cross-schema operation.

`transition_alpha_card(card_id uuid, target alpha_card_status)` locks the one card and verifies its immutable `author_principal` is `alpha_research_runtime`. For the author, the only allowed edges are `draft → reviewable`, `draft → archived`, `revision_requested → reviewable`, and `revision_requested → archived`. An admin repair may only take `draft`, `reviewable`, or `revision_requested` to `archived`; it cannot approve, validate, promote, reopen, or otherwise change a card. The function changes exactly `status`, `status_changed_at`, and `status_changed_by`; it changes no classification tuple, author, program, mechanism, evidence linkage, review, or other card column. It rejects self-transition, any unlisted edge, missing card, wrong author, and every target/value outside the enum.

`transition_research_cycle(cycle_id uuid, target cycle_outcome, summary text)` locks the one cycle, verifies its immutable `author_principal` is `alpha_research_runtime`, and accepts a non-empty UTF-8 `summary` of at most 8,000 characters. For the author, and for recorded admin repair, its only edges are `open → closed`, `open → empty`, `open → rejected`, and `open → failed`. It changes exactly `status` (to the target terminal state), `outcome` (to the same target), `summary`, `closed_at`, and `status_changed_by`; it changes no program, cycle key, author, evidence, or other cycle column. It rejects a non-open source, self-transition, missing cycle, wrong author, invalid target, or null/blank/overlong summary.

Catalog tests assert owner `agent_admin`, `prosecdef=true`, exact `proconfig` search-path setting, exact signatures, and no public/reviewer execution. Direct tests prove each allowed edge and changed-column set; every unlisted edge, direct table update, wrong role, nested/assumed role, mutable-path attempt, cross-owner record, and forbidden definer capability fails. Tests also prove classification and immutable provenance fields survive every function call unchanged.

## 2. Source policy and evidence intake

```text
source_class ∈ {local_normalized_batch, manual_reference_metadata, licensed_local_document}
terms_status ∈ {approved, unknown, rejected, expired}
freshness_mode ∈ {static, max_age}
```

`source_registry` has immutable persisted `source_reference text NOT NULL` and `terms_evidence_reference text NOT NULL`, plus `source_class`, `terms_status`, `enabled boolean NOT NULL DEFAULT false`, `freshness_mode`, `max_age_seconds`, `policy_revision integer NOT NULL DEFAULT 1`, and immutable `submitted_by name NOT NULL DEFAULT session_user`. It has no API key, bearer token, endpoint or provider-driver field. `source_reference` and `terms_evidence_reference` are references only, never fetched/opened by this core, and a trigger rejects their update by every principal including admin. Checks/triggers require:

- `enabled=true` only with `terms_status=approved`;
- `static` means `max_age_seconds IS NULL`; `max_age` means `max_age_seconds BETWEEN 60 AND 31536000`;
- only `agent_admin` may change policy; every policy change increments revision by exactly one and writes one append-only `source_policy_revisions` row containing `source_id`, `revision`, before/after terms/enabled/freshness values, immutable reference snapshots, `changed_by`, `changed_at`, and non-empty `approval_reason`; approval additionally requires `approved_by=agent_admin` and server-set `approved_at`; trigger rejects policy-column change without this provenance, any runtime policy mutation, and any evidence insert from disabled/non-approved source;
- `evidence_items` needs source FK, `content_sha256`, `source_locator`, non-null `retrieved_at`, `freshness_observed_at`, normalized claim and uniqueness `(source_id, content_sha256, source_locator)`;
- trigger rejects future timestamps and `freshness_observed_at < retrieved_at`; for `max_age`, stale means `retrieved_at < clock_timestamp() - make_interval(secs => max_age_seconds)` (exact equality accepted); `static` accepts nonfuture evidence regardless of age.

Direct SQL and handler cases: invalid enums; enabled plus unknown/rejected/expired terms; invalid static/max-age combinations/bounds; runtime self-approval/policy weakening/revision mutation; disabled/unknown source; immutable source/terms-reference update attempts by author and admin; missing/blank/overlong references; approval without admin actor/reason/timestamp or exact +1 revision/audit row; audit-row mutation/delete; fresh buffered record; stale record >=60 seconds beyond bound; future/ordered-wrong timestamps; duplicate; evidence update/delete; missing/invalid supersession; lineage missing-card/self-parent/duplicate relation. Positive approval/revision tests assert immutable references and complete before/after/actor/time/reason provenance. Buffered times avoid timing-racy fixtures while the predicate is exact.

## 3. Cards, independent reviews and typed research-only state

`alpha_cards` has immutable `author_principal name NOT NULL DEFAULT current_user`, and insert trigger requires it to equal `alpha_research_runtime`. Required non-null card fields are: `program_id`, `mechanism`, `mechanism_fingerprint`, `universe`, `regime`, `failure_regime`, `data_contract`, `cost_capacity_assumptions`, `no_trade_conditions`, `falsification_plan`, and one-or-more linked evidence IDs. Card lifecycle enum is `{draft, reviewable, revision_requested, archived}`; no value means validated, approved or promoted.

`research_reviews` has immutable `card_id`, `reviewer_principal name NOT NULL DEFAULT current_user`, `review_type ∈ {adversarial, methodological}`, `disposition ∈ {research_acknowledged, revision_requested, rejected, archived}`, `rationale`, and optional evidence-gap IDs. Insert trigger requires current user/reviewer principal `alpha_research_reviewer`, looks up the card and rejects any equal author/reviewer (plus author-role insertion is denied). No disposition confers investment, strategy, execution or activation authority.

The three persisted output carriers—`alpha_cards`, `research_reviews`, `inert_handoff_packages`—each have exactly:

```text
classification_scope alpha_research.classification_scope NOT NULL DEFAULT 'research_only'
validation_state    alpha_research.validation_state    NOT NULL DEFAULT 'unvalidated'
not_investment_advice boolean NOT NULL DEFAULT true
advisory_disclaimer text NOT NULL DEFAULT 'Research only; unvalidated; not investment advice.'
```

`classification_scope` enum contains only `research_only`; `validation_state` enum contains only `unvalidated`; checks require the exact tuple. Trigger rejects its mutation for every carrier. Reviews/handoffs are otherwise append-only; cards change only via the named lifecycle function, which cannot alter the tuple.

### Exact JSON contracts

Every tool output is exactly this envelope (no extra top-level keys):

```json
{"schema_version":"alpha_research/v1","classification_scope":"research_only","validation_state":"unvalidated","not_investment_advice":true,"advisory_disclaimer":"Research only; unvalidated; not investment advice.","result":{}}
```

`result` keys/types are exact:

| Handler | Accepted input keys | `result` keys |
|---|---|---|
| `alpha_research_status` | optional `program_id` UUID | `program_id` UUID/null, `program_status` string/null, `scheduler_ready` boolean |
| `program_create` | `name` string <=140, `universe` string <=500 | `program_id` UUID, `status`=`draft` |
| `source_submit` | `source_reference` string <=2048, `source_class` enum, `terms_evidence_reference` string <=2048 | `source_id` UUID, `terms_status`=`unknown`, `enabled`=false, `policy_revision`=1 |
| `evidence_record` | `source_id` UUID, `source_reference` string <=2048, `source_locator` string <=2048, `content_sha256` 64 lowercase hex, `retrieved_at` RFC3339 UTC, `freshness_observed_at` RFC3339 UTC, `normalized_claim` string <=8000, `falsification_notes` string <=4000, `cycle_id` UUID, `idempotency_key` UUID | `evidence_id` UUID, `outcome` enum `{accepted,duplicate,rejected_source_disabled,rejected_terms,rejected_stale,rejected_malformed}` |
| `alpha_card_create` | exactly `program_id` UUID; `mechanism` string 1..2000; `mechanism_fingerprint` exactly 64 lowercase hex; `universe` string 1..500; `regime` string 1..1000; `failure_regime` string 1..1000; `data_contract`, `cost_capacity_assumptions`, `no_trade_conditions`, `falsification_plan` each string 1..4000; and `evidence_ids` array of 1..100 distinct UUIDs | `card_id` UUID, `status`=`draft`, `evidence_count` integer 1..100 |
| `alpha_card_review` (reviewer toolset only) | `card_id` UUID, `review_type` enum, `disposition` enum, `rationale` string <=8000, optional `evidence_gap_ids` UUID array | `review_id` UUID, `card_id` UUID, `disposition` enum |
| `cycle_start` | `program_id` UUID, `cycle_key` ISO date | `cycle_id` UUID, `status`=`open` |
| `cycle_close` | `cycle_id` UUID, `outcome` enum `{closed,empty,rejected,failed}`, `summary` string <=8000 | `cycle_id` UUID, `outcome` enum |
| `inert_handoff_prepare` | `program_id` UUID, optional `cycle_id` UUID, `card_ids` UUID array min 1 | `handoff_id` UUID, `authority_scope`=`research_only`, `dispatch_state`=`not_dispatched` |
| `handoff_list` | optional `program_id` UUID | `handoffs` array (max 100) of objects with exactly `handoff_id` UUID, `program_id` UUID, `cycle_id` UUID/null, `card_ids` array of 1..100 distinct UUIDs, `evidence_ids` array of 0..100 distinct UUIDs, `prepared_at` RFC3339 UTC, `authority_scope`=`research_only`, `dispatch_state`=`not_dispatched`, `classification_scope`=`research_only`, `validation_state`=`unvalidated`, `not_investment_advice`=`true`, and `advisory_disclaimer` exact contract text |

Every input must be a JSON object with the table's exact keys: absent required key, `null` where a non-null value is specified, wrong JSON type, out-of-bound string/array, duplicate array member, malformed UUID/time/hash, prohibited key, and unknown key fail before DB access; no coercion is permitted. The outer tool envelope has exactly six top-level keys: `schema_version`, `classification_scope`, `validation_state`, `not_investment_advice`, `advisory_disclaimer`, and `result`. The first five are envelope metadata (one schema key plus four safety keys), not "five classification keys." `inert_handoff_packages.payload` has exactly 12 keys: those five metadata keys plus `authority_scope`, `dispatch_state`, `program_id`, `cycle_id`, `card_ids`, `evidence_ids`, and `prepared_at`; no others. It rejects `validated_alpha`, `investment_advice`, `recommendation`, `strategy_approved`, `promotion`, `order`, `risk`, `paper_activation`, `live_activation`, `deployment`, `action`, `recipient`, `transport`, `url`, `token` and any unknown field. Tests cover every persisted carrier and handler for omission, wrong/mutated tuple, all prohibited fields, unknown fields, wrong types, and missing required fields.

### Secret non-disclosure and deterministic observability tests

Secrets are reference-only: no secret value may be persisted in any ALR table/payload, returned in a tool envelope, emitted to logs/errors/traces/metrics, or passed to handoff/scheduler status text. This applies generically to every value obtained from a secret resolver, DSN credential component, environment secret material, or exception carrying such material; it is not a denylist of known names. Failures expose only fixed error codes and bounded safe identifiers, never a secret value or a serialized connection string. Deterministic negative tests inject a unique synthetic canary through each such boundary and assert its exact value and encoded/serialized representation are absent from every output, persisted row, captured log, exception/error, trace/span/metric attribute, and scheduler result; they also assert redacted fixed error codes. Tests use synthetic references/canaries only and never print or load a real secret.

## 4. No-egress contract

Static no-egress verification takes a recorded `ALR_IMPLEMENTATION_BASE_SHA`, fails if it is absent/not an ancestor or if the implementation worktree is dirty, and runs `git diff --no-ext-diff --unified=0 "$ALR_IMPLEMENTATION_BASE_SHA"...HEAD -- ':!factory/projects/zeus-alpha-research-ledger-core/**'`. It scans **every added line (including the replacement side of every modified line) in every ALR-added or ALR-modified implementation file**, without a path allowlist or shared-wiring exception. The test fails on an unscannable/binary changed implementation file and records the base SHA and changed-file manifest. Before a PR, the base must be revalidated against the then-current canonical base and the manifest regenerated; the historical ALR-010 base is not asserted current. Banned imports/calls: `requests`, `httpx`, `urllib`, `aiohttp`, `websockets`, `socket`, `ftplib`, `paramiko`, `boto3`, `subprocess`, `os.system`, `asyncio.create_subprocess_exec`, `asyncio.create_subprocess_shell`, broker/Vonash/Magnus/VAOS/APC/RAG/KB clients. SQL rejects `dblink`, `postgres_fdw`, `CREATE SERVER`, `CREATE EXTENSION`, `COPY ... PROGRAM`, remote connection strings and `APC_INTERNAL_SECRET`.

Runtime harness executes every handler with one valid and one invalid fixture, each reviewer-only handler under reviewer fixture, and scheduler readiness/registration/invocation. It monkeypatches socket/HTTP transports/subprocess APIs/`os.system`/async process creation to raise `UnexpectedEgress`; every attempt fails. It also invokes each ALR-added shared-wiring function using fake in-memory secret-reference data, never real sync. The only database connection allowed in these tests is parsed dedicated local DSN: `host=127.0.0.1 port=55430 dbname=zeus_agent user` equal to the calling dedicated role; URI host/hostaddr overrides and all other host/port/db/user fail before connection.

## 5. Scheduler configuration/readiness

Config `agent_core.alpha_research.scheduler.enabled` defaults exact boolean `false`; no environment fallback. `runtime_readiness(component,status,source_commit,evidence_sha256,verified_at,expires_at,verified_by)` is admin-written only. Required components: `schema_migrated`, `dedicated_author_secret_verified`, `dedicated_reviewer_secret_verified`, `approved_source_policy_verified`, `toolset_isolation_verified`, `no_egress_smoke_verified`.

`verify_alpha_research_scheduler_readiness()` runs without cache at registration and every invocation. It returns true only when config is exactly true and every component is `passed`, unexpired, current-source-commit matched and hash-backed. Any false/missing/failed/expired/wrong-commit/hashless row returns local `scheduler_not_ready`; registration does not occur and invocation reads no batch. Tests cover config false/missing, each component missing/failed/expired/wrong commit/hashless, both secret references, failed migration and absent approved source.

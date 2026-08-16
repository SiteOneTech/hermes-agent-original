---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_reviewed_candidate_primary_hold
validated: yes
reviewed: yes
reviewed_by: quality-reviewer
review_evidence: factory_gate_790
reviewed_candidate_sha: 2476e978c545e24b18ee48844b24eb8c58245ab4
reviewed_candidate_pr: https://github.com/SiteOneTech/hermes-agent-original/pull/34
reviewed_source_gate: factory_gate_789
reviewed_source_sha: 1e82340dddf52071d14c3c7a00b04b3c17ee2821
---

# SECURITY GATES

`DATABASE_AND_RUNTIME_CONTRACT.md` §§1–5 is the detailed acceptance contract. This gate lists the mandatory pass/fail evidence, not a weaker alternate design.

## Least-privilege gate
- Migration verifies all exact role attributes, zero role memberships, search path, per-object grants, `program_create`/`source_submit` leaf allowlist, `PUBLIC` revocations and default privileges from contract §1.
- A transaction as `alpha_research_runtime` proves each allowlisted operation works and every named direct-SQL denial in contract §1 fails. Catalog assertions prove no DML grant in other user schemas, no `PUBLIC` privilege in `alpha_research`, and the two lifecycle functions' `agent_admin` ownership, `SECURITY DEFINER`, fixed safe search path, exact signatures and execution grants.
- Direct lifecycle tests prove every permitted source→target edge and changed-column set, and deny direct update, unlisted edge, wrong/cross-owner actor, assumed role, mutable search path and all forbidden definer capabilities.
- Dedicated role secret is Infisical-only. Resolver accepts only the exact local DSN shape in contract §4; missing reference/role/allowlist fails before toolset or scheduler activation.

## Source/provenance gate
- Migration and handlers enforce the exact source classes, immutable persisted `source_reference`/`terms_evidence_reference`, terms states, freshness modes, max-age bounds, timestamp predicate, approval/revision provenance and uniqueness/supersession contract in §2.
- Direct SQL and handler suites execute every §2 negative case: source state combinations, immutable-reference mutations including admin attempts, incomplete/non-admin approval provenance, revision-audit mutation, stale/future/malformed time, duplicate, append-only evidence mutation/delete and lineage violation.
- Raw restricted content is never sent to generic memory or an external service. Provider fetch/parse code remains out of tree.

## Typed research-only gate
- `alpha_cards`, `research_reviews`, `inert_handoff_packages` and every JSON envelope implement the exact typed tuple/default/check/immutability contract in §3.
- Direct SQL and handler suites reject omitted/mutated/wrong tuples and every named validated/advice/approval/promotion/operation/activation/unknown field across all three persisted carriers and handoffs; field-by-field `alpha_card_create`, fixed `handoff_list` objects, payload/envelope count and type/bound checks are exact.
- Synthetic-canary tests prove the generic reference-only secret contract: no resolver/DSN/environment secret material appears in a persisted row, output, log, error, trace/span/metric or scheduler status, while fixed redacted errors remain deterministic.

## No-egress/tool isolation gate
- Default toolsets contain none of the ten handlers; the non-default leaf contains exactly `alpha_research_status`, `program_create`, `source_submit`, `evidence_record`, `alpha_card_create`, `alpha_card_review`, `cycle_start`, `cycle_close`, `inert_handoff_prepare`, `handoff_list`.
- Static scan covers every added/replacement line in every ALR-added or ALR-modified implementation diff file from a recorded, ancestor-verified base SHA; no selected-path exception is allowed. It rejects every §4 banned import/SQL pattern and unscannable changed file.
- Runtime harness executes all handlers and scheduler registration/run with outbound socket/HTTP/subprocess denial. Any attempt fails the test; only the exact local Postgres DSN is permitted.

## Scheduler gate
- `agent_core.alpha_research.scheduler.enabled` is false absent explicit configuration.
- Registration and each invocation call the contract §5 verifier without cache. Tests cover every false/missing/failed/expired/wrong-commit readiness component and prove no batch read/run follows `scheduler_not_ready`.

## Failure behavior
All gate failures are structured local rejections. No fallback can enable an external operation, shared runtime role or stale scheduler.

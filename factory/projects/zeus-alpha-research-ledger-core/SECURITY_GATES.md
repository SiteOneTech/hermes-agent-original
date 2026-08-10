---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: pending
---

# SECURITY GATES

`DATABASE_AND_RUNTIME_CONTRACT.md` §§1–5 is the detailed acceptance contract. This gate lists the mandatory pass/fail evidence, not a weaker alternate design.

## Least-privilege gate
- Migration verifies all exact role attributes, zero role memberships, search path, per-object grants, function allowlist, `PUBLIC` revocations and default privileges from contract §1.
- A transaction as `alpha_research_runtime` proves each allowlisted operation works and every named direct-SQL denial in contract §1 fails. Catalog assertions prove no DML grant in other user schemas and no `PUBLIC` privilege in `alpha_research`.
- Dedicated role secret is Infisical-only. Resolver accepts only the exact local DSN shape in contract §4; missing reference/role/allowlist fails before toolset or scheduler activation.

## Source/provenance gate
- Migration and handlers enforce the exact source classes, terms states, freshness modes, max-age bounds, timestamp predicate and uniqueness/supersession contract in §2.
- Direct SQL and handler suites execute every §2 negative case: source state combinations, stale/future/malformed time, duplicate, append-only evidence mutation/delete and lineage violation.
- Raw restricted content is never sent to generic memory or an external service. Provider fetch/parse code remains out of tree.

## Typed research-only gate
- `alpha_cards`, `research_reviews`, `inert_handoff_packages` and every JSON envelope implement the exact typed tuple/default/check/immutability contract in §3.
- Direct SQL and handler suites reject omitted/mutated/wrong tuples and every named validated/advice/approval/promotion/operation/activation/unknown field across all three persisted carriers and handoffs.

## No-egress/tool isolation gate
- Default toolsets contain none of the ten handlers; the non-default leaf contains exactly them.
- Static scan covers every exact project-owned path and banned import/SQL pattern in §4.
- Runtime harness executes all handlers and scheduler registration/run with outbound socket/HTTP/subprocess denial. Any attempt fails the test; only the exact local Postgres DSN is permitted.

## Scheduler gate
- `agent_core.alpha_research.scheduler.enabled` is false absent explicit configuration.
- Registration and each invocation call the contract §5 verifier without cache. Tests cover every false/missing/failed/expired/wrong-commit readiness component and prove no batch read/run follows `scheduler_not_ready`.

## Failure behavior
All gate failures are structured local rejections. No fallback can enable an external operation, shared runtime role or stale scheduler.

---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: pending
---

# SECURITY GATES

## Least-privilege gate
- Migration/admin ownership and `alpha_research_runtime` are separate. The runtime role receives only enumerated `alpha_research` grants; it has no `CREATE`, ownership, membership/inherit escalation, `GRANT`, FDW/dblink or broad Agent Core access.
- Migration revokes `PUBLIC` access and establishes restricted default privileges for future schema objects.
- Direct-role tests connect as `alpha_research_runtime` and prove denied `INSERT`/`UPDATE`/`DELETE` on `factory`, `public` and all non-allowlisted schemas; denied evidence/review mutation/deletion; denied schema creation and privilege escalation.
- Dedicated role credential comes only from Infisical. Missing dedicated reference disables toolset/scheduler activation. There is no sibling/shared-role or fallback DSN pathway.

## Source and provenance gate
- A registry source must be enabled, terms-approved and governed by a non-null freshness policy before local evidence intake accepts it.
- Evidence requires source FK, content hash, locator, UTC retrieval/freshness times and a per-source uniqueness key. Supersession is append-only.
- Direct SQL and handler tests reject disabled, terms-unknown, stale, malformed and duplicate evidence.
- Raw restricted content is never sent to generic memory, Telegram or any external service. Concrete third-party drivers remain out-of-tree and cannot enter this core delivery.

## Research classification gate
- Cards, reviews, tool JSON and handoffs include immutable `research_only`, `unvalidated` and `not_investment_advice` classification/disclaimer fields.
- Database checks and handler validation reject `validated_alpha`, advice/recommendation, strategy approval, promotion, operational directives, risk/order, paper/live activation and external-action fields.
- Handoff packages only serialize local references and fixed disclaimers; `authority_scope=research_only` and `dispatch_state=not_dispatched` are database-enforced.

## No-egress/tool isolation gate
- Exact `alpha_research` tool handlers are absent from default toolsets and present only in the non-default leaf allowlist.
- Static/dependency scans and runtime-negative tests reject network client imports, sockets, remote DSNs, `APC_INTERNAL_SECRET`, broker or Vonash/Magnus/VAOS/RAG/KB clients, outbound messaging and subprocess dispatch in module tools/scripts.
- Local scheduler is disabled by default and cannot register/run without all recorded local prerequisites.

## Failure behavior
Missing role/secret, missing grant, unknown terms, disabled/stale source, malformed/duplicate intake, prohibited classification or unsupported handoff field fails closed into a structured local rejection. No fallback enables external operation.

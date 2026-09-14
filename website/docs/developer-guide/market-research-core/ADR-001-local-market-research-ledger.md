# ADR-001 — Zeus Advisory Ledger with API-mediated Vonash Collaboration

**Status:** Current concise reference. Canonical decisions: [`factory/projects/zeus-independent-alpha-research/ADRS.md`](../../factory/projects/zeus-independent-alpha-research/ADRS.md).

## Decision
Keep a Zeus-owned Postgres advisory ledger separate from the Vonash runtime. Connect Zeus and Magnus through a typed, service-owned research thread/API backed by durable outbox, idempotency and acknowledgement. Telegram is optional transport/mirroring, not the ledger.

## Rationale
Magnus is a real-time runtime CEO/operator, not a coding executor. Zeus needs independent research provenance and red-team capability; Vonash needs ownership of its evaluator, experiment and promotion records. Direct database writes would couple systems, obscure authority, and raise operational risk.

## Boundaries
- Zeus has research-only authority and cannot mutate Vonash execution/risk/paper/live/promotion/configuration/code/deployment surfaces.
- Vonash runtime capability and delivery details are verified by audit before implementation; they are not inferred from this decision.
- Source, repository and KB access are least-privilege, approved, provenance-aware and fail closed when credentials/scope are absent.

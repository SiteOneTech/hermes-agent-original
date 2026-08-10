---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: pending
---

# ASSUMPTIONS AND OPEN QUESTIONS

## Verified inputs at planning time
- The predecessor project has a documentation-only completion record; it did not create a local ledger or enable a connector.
- `hermes-agent-original` provides Agent Core Postgres modules, migrations, JSON tool registration and leaf toolsets.
- The current fetched upstream base is `origin/main` at `20228c1167814f36d952999f2cafe8b3f6f9ba3c`.
- Vonash’s current safe consumer path is a future APC read model; no direct external Zeus identity or secure producer intake is implemented there.
- The existing KB upload flow is not a safe candidate-producer path, and VAOS messaging is not an externally authenticated Zeus boundary.

## Assumptions to verify in ALR-020/070
1. Exact current Agent Core migration/role helper conventions in the implementation base.
2. Existing tool registration and test fixture patterns on the current base SHA.
3. Local Agent Core DB health, migration execution and Infisical secret-sync path without printing secret values.
4. Provider terms, rate limits, permitted universe, and the minimum legal attribution/provenance fields before any source is enabled.

## Deliberately unresolved
- Which paid/read-only provider(s) Jean will authorize after source due diligence.
- Whether FRED, SEC, filings, macro, news or market-data sources will be first active providers.
- Any future Zenith/Vonash read/ingest adapter contract; it is expressly outside v1.

## Rule
Unknown information is stored as an open question or a source status, not replaced with a plausible market claim, endpoint, credential name or capability assertion.

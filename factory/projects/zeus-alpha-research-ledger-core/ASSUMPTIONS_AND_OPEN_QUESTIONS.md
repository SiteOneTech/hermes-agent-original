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

# ASSUMPTIONS AND OPEN QUESTIONS

## Verified inputs at planning time
- The predecessor project has a documentation-only completion record; it did not create a local ledger or enable a connector.
- `hermes-agent-original` provides Agent Core Postgres modules, migrations, JSON tool registration and leaf toolsets.
- `20228c1167814f36d952999f2cafe8b3f6f9ba3c` is the historical ALR-010 merge base recorded when planning began; it is not asserted to be current `origin/main`. Revalidate the canonical base immediately before a PR.
- Vonash’s current safe consumer path is a future APC read model; no direct external Zeus identity or secure producer intake is implemented there.
- The existing KB upload flow is not a safe candidate-producer path, and VAOS messaging is not an externally authenticated Zeus boundary.

## Assumptions to verify in ALR-020/070
1. Exact current Agent Core migration/role helper conventions in the implementation base.
2. Existing tool registration and test fixture patterns on the current base SHA.
3. Local Agent Core DB health, migration execution and Infisical secret-sync path without printing secret values.
4. Provider terms, rate limits, permitted universe, and the minimum legal attribution/provenance fields before any source is enabled.
5. Factory ALR-020 metadata read-back after the required deterministic removal of its incompatible bounded-local-sessions acceptance clause; v1 continues to exclude collaboration session/message entities.

## Deliberately unresolved
- Which paid/read-only provider(s) Jean will authorize after source due diligence.
- Whether FRED, SEC, filings, macro, news or market-data sources will be first active providers.
- Any future Zenith/Vonash read/ingest adapter contract; it is expressly outside v1.

## Rule
Unknown information is stored as an open question or a source status, not replaced with a plausible market claim, endpoint, credential name or capability assertion.

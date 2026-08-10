---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: pending
---

# REQUIREMENTS TRACEABILITY

| Requirement / boundary | Owner task(s) | Enforced behavior | RED then GREEN proof | Independent evidence | Final gate |
|---|---|---|---|---|---|
| R1 schema entities/no collaboration messages | ALR-020 | schema objects/FKs only; no session/message tables | migration object/absence tests | ALR-061 | ALR-070 |
| R2 provenance and append-only evidence | ALR-020/040 | unique hash+locator, source FK, supersession trigger | direct SQL duplicate/update/delete failures | ALR-061/063 | ALR-070 |
| R3 lineage | ALR-020/030 | family/parent checks, no self relation | direct SQL and handler lineage negatives | ALR-061 | ALR-070 |
| R4 card completeness/classification | ALR-020/030 | required fields + research-only checks | invalid transition/validated-alpha tests | ALR-061/063 | ALR-070 |
| R5 separate immutable review | ALR-020/030 | reviewer/disposition checks, append-only review | same-author/mutation rejection tests | ALR-061/063 | ALR-070 |
| R6 local daily cycle | ALR-050 | local batch idempotency, terminal empty/reject/fail | missing/stale/duplicate/empty cycle tests | ALR-062/063 | ALR-070 |
| R7 inert handoff | ALR-020/030/050 | fixed research-only/not-dispatched state | action/URL/token/recipient rejection tests | ALR-061/063 | ALR-070 |
| R8 leaf toolset only | ALR-030 | exact handler allowlist, absent by default | resolver absence/allowlist tests | ALR-062/063 | ALR-070 |
| R9 source policy/intake | ALR-020/040 | approved terms/freshness required | disabled/unknown/stale source tests | ALR-061/063 | ALR-070 |
| R10 dedicated secret/role | ALR-020/030/050 | no fallback; activation disabled | role denial/missing-secret/no-scheduler tests | ALR-063 | ALR-070 |
| no external egress/platform writes | ALR-030/050 | no forbidden imports/DSNs/dispatch | static + runtime-negative tests | ALR-063 | ALR-070 |
| PR-first/QA Guardian | ALR-010..080 | per-task Factory integration waiver | Factory DB/PR evidence check | ALR-061/062 | ALR-080 |

A task cannot mark a requirement satisfied through prose alone: its test and review evidence must cite the exact candidate SHA.

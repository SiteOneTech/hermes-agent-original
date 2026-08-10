---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: pending
---

# REQUIREMENTS TRACEABILITY

| Requirement / boundary | Owner task(s) | Binding contract | RED then GREEN proof | Independent evidence | Final gate |
|---|---|---|---|---|---|
| R1 entities/no session messages | ALR-020 | DB §1/§2/§5 | object/absence/constraint tests | ALR-061 | ALR-070 |
| R2 provenance/append-only | ALR-020/040 | DB §2 | source/evidence direct SQL negatives | ALR-061/063 | ALR-070 |
| R3 lineage | ALR-020/030 | DB §2 | missing/self/duplicate lineage tests | ALR-061 | ALR-070 |
| R4 card completeness/classification | ALR-020/030 | DB §3 | transition/tuple/prohibited-label tests | ALR-061/063 | ALR-070 |
| R5 immutable separate review | ALR-020/030 | DB §1/§3 | role/author/mutation rejection tests | ALR-061/063 | ALR-070 |
| R6 local daily cycle | ALR-050 | DB §5 | local idempotent empty/reject/fail tests | ALR-062/063 | ALR-070 |
| R7 inert handoff | ALR-020/030/050 | DB §3 | fixed state/unknown action field tests | ALR-061/063 | ALR-070 |
| R8 leaf toolset | ALR-030 | DB §4 | default absence/exact allowlist tests | ALR-062/063 | ALR-070 |
| R9 source policy | ALR-020/040 | DB §2 | enum/terms/freshness negatives | ALR-061/063 | ALR-070 |
| R10 secret/role/scheduler | ALR-020/030/050 | DB §1/§4/§5 | role/DSN/readiness negatives | ALR-063 | ALR-070 |
| no egress/platform writes | ALR-030/050 | DB §4 | static + every-handler/scheduler interception harness | ALR-063 | ALR-070 |
| PR-first/QA Guardian | ALR-010..080 | TASK_GRAPH/QA gates | Factory DB + PR evidence | ALR-061/062 | ALR-080 |

No task may mark a requirement satisfied with prose: test/review evidence cites the exact candidate SHA and the listed contract section.

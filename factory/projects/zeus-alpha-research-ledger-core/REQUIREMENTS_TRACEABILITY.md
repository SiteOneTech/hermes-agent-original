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

# REQUIREMENTS TRACEABILITY

| Requirement / boundary | Owner task(s) | Binding contract | RED then GREEN proof | Independent evidence | Final gate |
|---|---|---|---|---|---|
| R1 entities/no session messages | ALR-020 | DB §1/§2/§5; TASK_GRAPH reconciliation | object/absence/constraint tests plus exact Factory acceptance metadata read-back | ALR-061 | ALR-070 |
| R2 immutable provenance/append-only | ALR-020/040 | DB §2 | source/terms-reference immutability and admin approval/revision-audit direct SQL negatives | ALR-061/063 | ALR-070 |
| R3 lineage | ALR-020/030 | DB §2 | missing/self/duplicate lineage tests | ALR-061 | ALR-070 |
| R4 card completeness/classification | ALR-020/030 | DB §1/§3 | lifecycle-edge/changed-column plus bounded input/tuple/prohibited-label tests | ALR-061/063 | ALR-070 |
| R5 immutable separate review | ALR-020/030 | DB §1/§3 | role/author/mutation rejection tests | ALR-061/063 | ALR-070 |
| R6 local daily cycle | ALR-050 | DB §5 | local idempotent empty/reject/fail tests | ALR-062/063 | ALR-070 |
| R7 inert handoff | ALR-020/030/050 | DB §3 | fixed state/typed list/payload-key-count/unknown action field tests | ALR-061/063 | ALR-070 |
| R8 leaf toolset | ALR-030 | DB §1/§4 | default absence/exact `program_create`/`source_submit` allowlist tests | ALR-062/063 | ALR-070 |
| R9 source policy | ALR-020/040 | DB §2 | enum/terms/freshness negatives | ALR-061/063 | ALR-070 |
| R10 secret/role/scheduler | ALR-020/030/050 | DB §1/§3/§4/§5 | role/DSN/readiness plus synthetic-secret redaction negatives | ALR-063 | ALR-070 |
| no egress/platform writes | ALR-030/050 | DB §4 | all-ALR-modified-diff-line static scan + every-handler/scheduler interception harness | ALR-063 | ALR-070 |
| PR-first/QA Guardian + merge reconciliation | ALR-010..080 | G0/TASK_GRAPH/QA gates/G1_REVIEW | Factory DB event/gate evidence, Git ancestry proof, PR/QA evidence where required | ALR-061/062 | ALR-080 |

No task may mark a requirement satisfied with prose: test/review evidence cites the exact candidate SHA and the listed contract section.

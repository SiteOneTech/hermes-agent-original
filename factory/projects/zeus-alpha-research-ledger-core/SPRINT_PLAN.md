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

# SPRINT PLAN

| Increment | Outcome | Dependencies | Exit evidence |
|---|---|---|---|
| ALR-010 | G1 rebaseline + G0 + traceability + gate-695 merge-evidence reconciliation | — | committed corrected docs plus independent exact-SHA spec/security PASS reviews; no reviewed=yes before those reviews |
| ALR-020 | schema, constraints, dedicated role/grants | ALR-010 exact-SHA reviews accepted; ALR-020 acceptance metadata corrected/read back | RED/GREEN migration and direct-role tests |
| ALR-030 | JSON tools + non-default leaf toolset | ALR-020 accepted | tool/allowlist/forbidden-field tests |
| ALR-040 | source policy and adapter-neutral local evidence intake | ALR-030 accepted | source-state/duplicate/stale tests; no third-party driver |
| ALR-050 | default-disabled daily local cycle + inert handoff | ALR-030/040 accepted | no-registration/no-egress/deterministic cycle tests |
| ALR-061 | independent specification/architecture review | ALR-020..050 candidate SHAs ready | requirement-to-SHA review report |
| ALR-062 | independent quality/TDD review | ALR-020..050 candidate SHAs ready | TDD/quality report |
| ALR-063 | independent security/no-egress review | ALR-020..050 candidate SHAs ready | grants/negative/no-egress report |
| ALR-070 | live local DB/tool smoke and cleanup | ALR-061/062/063 accepted | synthetic local smoke evidence |
| ALR-080 | Zeus PR and QA Guardian handoff | ALR-070 accepted | actual labeled PR and QA evidence for final delivery path |

`ALR-060` was canonically superseded by ALR-061/062/063 because one aggregate reviewer task could not demonstrate the required independent review chain.

No increment may absorb Vonash integration, third-party driver source code, live market execution or deployment without new approved scope.

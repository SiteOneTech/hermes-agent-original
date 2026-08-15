---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: yes
---

# SPRINT PLAN

| Increment | Outcome | Dependencies | Exit evidence |
|---|---|---|---|
| ALR-010-R2 | G1 rebaseline + G0 + traceability + gate-695/gate-697 direct-integration reconciliation and PR-first candidate visibility | — | committed corrected docs on assigned branch, Zeus-signed `agent:zeus` PR, independent exact-SHA spec/security PASS reviews; no reviewed=yes before those reviews |
| ALR-020 | schema, constraints, dedicated role/grants | ALR-010-R2 exact-SHA reviews accepted; Zeus PR/review/base-visibility evidence recorded; ALR-020 acceptance metadata corrected/read back | RED/GREEN migration and direct-role tests |
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

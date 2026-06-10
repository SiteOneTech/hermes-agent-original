# Task Graph

Project: `factory-runtime-docs-notion-refactor`
Derived from: `PRD.md`, `SPRINT_PLAN.md`, `ADRS.md`, `TECHNICAL_BLUEPRINT.md`, `DOCUMENTATION_INDEX.md`
Updated: 2026-06-09T23:30:00Z

## Canonical task graph

```
T0  close/freeze affected Funnel Core project
    status: DONE
    evidence: Factory closure gate; funnel-core-crm-workflow closed/completed, no open runs
    owner: Zeus

T1  create docs-first project artifact pack
    status: DONE
    evidence: factory/projects/factory-runtime-docs-notion-refactor/ — 16 artifacts present
    owner: Zeus

T2  create Factory project/task/lane with G0 strategy
    status: DONE
    evidence: Factory DB project factory-runtime-docs-notion-refactor [active]; lanes bmad/hybrid/zeus created
    owner: Zeus

T3  regression tests fail for incident classes
    status: PENDING
    branch: factory/runtime-docs-notion-refactor/inc-0003-regression-tests
    owner: factory
    reviewer: Jean
    phase: implementation
    acceptance:
      - pytest tests/hermes_cli/test_factory_control_plane_refactor.py passes with FakeSql
      - test_notion_tracker_schema_validation_rejects_empty_and_bad_input passes
      - test_notion_tracker_schema_validation_accepts_funnel_core_evidence passes
      - test_link_notion_tracker_writes_metadata_reads_back_and_audits passes
      - test_link_notion_tracker_raises_on_readback_mismatch passes
      - additional regression cases for: close-with-running-row, STATE_IN_PROGRESS ambiguity, dispatch-before-docs
    evidence: tests/hermes_cli/test_factory_control_plane_refactor.py

T4  implement Notion metadata CLI/API write path
    status: DONE
    branch: factory/runtime-docs-notion-refactor/inc-0001-control-plane-refactor
    evidence: hermes_cli/factory_pg.py link_notion_tracker() + _validate_notion_tracker_metadata() + tests
    commit: df09e3885 "Add Factory docs Notion control-plane gates"

T5  implement docs-first dispatch/reconcile guard
    status: PENDING
    branch: factory/runtime-docs-notion-refactor/inc-0005-dispatch-guard
    owner: factory
    reviewer: Jean
    phase: implementation
    depends_on: [T3]
    acceptance:
      - hermes factory dispatch denies implementation tasks when project docs/Notion gates missing
      - narrow runtime-bootstrap repair task IS allowed to dispatch even without docs (self-referential repair)
      - smoke project proves implementation cannot run before docs/Notion unless task is runtime repair
    evidence: hermes_cli/factory.py or hermes_cli/factory_pg.py dispatch guard logic

T6  implement active-run terminal/close repair
    status: PENDING
    branch: factory/runtime-docs-notion-refactor/inc-0006-active-run-repair
    owner: factory
    reviewer: Jean
    phase: implementation
    acceptance:
      - close/resolve-state finalizes active run rows with terminal outcome
      - no stale active_run rows after project close
      - worker outcome parsing uses structured final result, not log snippets
    evidence: hermes_cli/factory_pg.py close/resolve actions

T7  dashboard/API/static-state verification
    status: PENDING
    branch: factory/runtime-docs-notion-refactor/inc-0007-static-state-verification
    owner: factory
    reviewer: Jean
    phase: implementation
    depends_on: [T5, T6]
    acceptance:
      - hermes factory status shows correct project state for factory-runtime-docs-notion-refactor
      - hermes factory status shows funnel-core-crm-workflow closed/completed with no anomalies
      - no misleading static/operative state in dashboard or API serializers
    evidence: hermes factory status output

T8  independent review + tests + smoke
    status: PENDING
    branch: factory/runtime-docs-notion-refactor/inc-0008-review-smoke
    owner: reviewer (Jean or delegated)
    reviewer: Jean
    phase: quality
    depends_on: [T3, T4, T5, T6, T7]
    acceptance:
      - focused pytest for Factory PG/CLI contracts passes
      - CLI smoke: project create/link-notion/reconcile/resolve/close
      - live status smoke: funnel-core-crm-workflow closed state
      - smoke project proves implementation cannot dispatch before docs/Notion unless repair task
      - git status/diff reviewed; no unrelated work
    evidence: pytest output, CLI smoke output

T9  delivery report and Jean GO/NO-GO before CRM work
    status: PENDING
    branch: factory/runtime-docs-notion-refactor/inc-0009-delivery
    owner: factory
    reviewer: Jean
    phase: delivery
    depends_on: [T8]
    acceptance:
      - DELIVERY_REPORT.md updated with GREEN evidence
      - QA_REPORT.md updated with test and smoke evidence
      - SECURITY_REVIEW.md updated with security control evidence
      - NOTION_UPDATE.md updated with readback evidence
      - Jean explicitly approves CRM/Funnel Core review
    evidence: updated artifact files, Jean explicit GO
```

## Dependency summary

- T3 → T5 → T7 → T8 → T9
- T4 is parallel to T3 (INC-0001 already done)
- T6 is parallel to T5 (both depend on T3)
- T8 depends on T3, T4, T5, T6, T7
- T9 depends on T8 and explicit Jean GO

## Reconciliation derivation

Derived from:
- `PRD.md` requirements 1-6
- `SPRINT_PLAN.md` stories 1-5
- `ADRS.md` ADR-001 through ADR-005
- `TECHNICAL_BLUEPRINT.md` sections 1-5
- `DOCUMENTATION_INDEX.md` required artifact pack
- `QA_GATES.md` required before GREEN
- `SECURITY_GATES.md` required controls
- INC-0001 commit `df09e3885` evidence: `link_notion_tracker` + tests implemented

INC-0001 scope: T2 (project create) + T4 (Notion metadata write path). Not T3/T5/T6/T7/T8/T9.

## HOTFIX-0001 task graph — Documentary Source-of-Truth Gate

This hotfix supersedes the previous stale “Notion as gate” delivery claim until corrected. It does not authorize CRM/Funnel Core work.

```
H0  open hotfix contract in same Factory project
    status: DONE
    branch: factory/runtime-docs-notion-refactor/hotfix-doc-source-truth-gate
    evidence: HOTFIX_0001_DOCUMENTARY_SOURCE_OF_TRUTH_GATE.md + DOCUMENTATION_INDEX.md updated
    owner: Zeus

H1  implement first-class Factory document status model
    status: TODO
    phase: implementation
    owner: claude-builder
    reviewer: quality-reviewer
    acceptance:
      - runtime distinguishes G1 blocking docs, lifecycle docs, and PM projection docs
      - Factory status/API exposes per-project document_status with exists/indexed/committed/validated/reviewed/blocking fields
      - DOCUMENTATION_INDEX.md stale status can be detected before acceptance

H2  correct dispatch/readiness semantics for Notion
    status: TODO
    phase: implementation
    owner: claude-builder
    reviewer: quality-reviewer
    depends_on: [H1]
    acceptance:
      - normal implementation dispatch blocks on missing G1 required docs, not on missing Notion by default
      - Notion remains important as PM projection/reporting and can be mandatory only through explicit project metadata
      - critical_readiness/delivery gates do not treat missing Notion as source-of-truth failure unless configured mandatory

H3  add regression tests and live smoke
    status: TODO
    phase: qa
    owner: qa-verifier
    reviewer: factory-orchestrator
    depends_on: [H1, H2]
    acceptance:
      - docs ready + Notion missing => dispatch allowed by default
      - docs missing/unindexed/uncommitted => dispatch/readiness blocked
      - status payload includes document_status
      - lifecycle docs are required at the correct later gates, not before implementation by default

H4  reconcile current project artifacts and reports
    status: TODO
    phase: documentation
    owner: factory-reporter
    reviewer: factory-orchestrator
    depends_on: [H1, H2, H3]
    acceptance:
      - TASK_GRAPH, TRACKER, QUALITY_REVIEW, QA_REPORT, DELIVERY_REPORT, DOCUMENTATION_INDEX agree with Factory DB
      - stale pending lines are corrected or explicitly marked historical/superseded
      - Notion update remains PM projection, not canonical acceptance evidence

H5  delivery review and Jean GO/NO-GO
    status: TODO
    phase: delivery
    owner: factory-reporter
    reviewer: Jean
    depends_on: [H3, H4]
    acceptance:
      - tests/smokes are real and recorded
      - no open tasks/runs/anomalies remain
      - CRM/Funnel Core remains frozen unless Jean explicitly says GO after this hotfix
```

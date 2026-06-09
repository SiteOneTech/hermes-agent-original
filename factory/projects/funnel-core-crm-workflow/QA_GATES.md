# QA Gates — Funnel Core / CRM Sales Workflow

## Gate Matrix

| Gate | Evidence Required | Status |
|------|-------------------|--------|
| Intake | Scope, project ID, Factory DB source confirmed | passed |
| Planning | PRD, ADRs, sprint plan, task graph, Notion page | passed |
| Implementation | FunnelCore, adapter protocol, reference adapter | passed |
| Quality | Code review, consistency checks | passed |
| Test | Unit + integration tests pass | passed |
| Delivery | Smoke tests, delivery report | pending |
| Reconciliation | No missing docs anomalies | in_progress |

## Required Commands

```bash
# Syntax check
python3 -m py_compile agent/crm/funnel_core.py
python3 -m py_compile agent/crm/adapters/base.py
python3 -m py_compile agent/crm/adapters/twenty.py

# Unit tests
python3 -m pytest tests/agent/crm/test_funnel_core.py -v

# Integration tests (requires CRM credentials)
python3 -m pytest tests/agent/crm/test_twenty_adapter.py -v

# Factory status
hermes factory status funnel-core-crm-workflow --json
```

## Hard-Stop Conditions

- Missing required Factory docs.
- Any unit or integration test failing.
- Funnel stages not matching PRD definition.
- Adapter protocol methods missing from reference implementation.

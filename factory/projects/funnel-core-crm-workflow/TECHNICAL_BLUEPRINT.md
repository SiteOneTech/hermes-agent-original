# Technical Blueprint — Funnel Core / CRM Sales Workflow

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Zeus Agent                            │
│  (FunnelCore module — stages, transitions, business rules) │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │    CRMFunnelAdapter Protocol   │
              │  create_lead, update_stage,    │
              │  get_stage, list_opportunities │
              └───────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
   ┌────────────┐     ┌────────────┐    ┌────────────┐
   │ Twenty CRM  │     │ HubSpot CRM │    │ Salesforce  │
   │  Adapter    │     │  Adapter    │    │  Adapter   │
   └────────────┘     └────────────┘    └────────────┘
```

## Funnel Stages

| Stage | Description |
|-------|-------------|
| LEAD | Initial contact or inbound lead |
| QUALIFIED | Lead meets qualification criteria |
| PROPOSAL | Proposal or quote sent |
| NEGOTIATION | Active negotiation |
| CLOSED_WON | Deal won |
| CLOSED_LOST | Deal lost |
| CHURNED | Customer churned post-sale |

## State Machine

Transitions are deterministic. Each transition has:
- `from_stage`: source stage
- `to_stage`: target stage
- `trigger`: event or condition that fires the transition
- `guard`: pre-condition that must be satisfied
- `action`: side effect (event emission, CRM update)

## CRMFunnelAdapter Protocol

```python
class CRMFunnelAdapter(Protocol):
    async def create_lead(self, lead_data: LeadInput) -> Lead: ...
    async def update_stage(self, lead_id: str, stage: FunnelStage) -> Lead: ...
    async def get_stage(self, lead_id: str) -> FunnelStage: ...
    async def list_opportunities(self, pipeline_id: str) -> list[Opportunity]: ...
    async def emit_event(self, event: FunnelEvent) -> None: ...
```

## Files and Locations

| File | Purpose |
|------|---------|
| `agent/crm/funnel_core.py` | FunnelCore module — stages, transitions, rules |
| `agent/crm/adapters/base.py` | CRMFunnelAdapter base class |
| `agent/crm/adapters/twenty.py` | Twenty CRM reference adapter |
| `agent/crm/adapters/__init__.py` | Adapter registry |
| `tests/agent/crm/test_funnel_core.py` | Unit tests for FunnelCore |
| `tests/agent/crm/test_twenty_adapter.py` | Adapter integration tests |

## Runtime Inheritance (`zeus_then_runtime`)

1. FunnelCore is loaded as part of the Zeus agent core.
2. At initialization, the agent resolves the active CRM adapter from config.
3. All funnel operations go through the adapter protocol.
4. The agent never imports CRM-specific code directly.

## Security

- No PII in funnel events beyond lead_id and stage.
- CRM credentials managed via Agent Core secrets, not hardcoded.
- Adapter implementations validate all inputs before CRM API calls.

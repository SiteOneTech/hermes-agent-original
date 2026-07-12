# I7_IMPLEMENTATION_REPORT — First pilot smoke for Empleado.uno

Date: 2026-07-12
Project: `empleado-uno-sales-operator-core`
Task: `empleado-uno-sales-operator-core-i7-first-pilot-smoke-for-empleado-uno`
Owner: Zeus direct operator implementation
Status: implemented

## Scope delivered

I7 delivered the first end-to-end Sales Operator pilot smoke for Empleado.uno without contacting real businesses or invoking outbound providers.

Implemented files:

- `scripts/runtime/sales_operator_i7_pilot_smoke.py`
- `tests/test_sales_operator_i7_pilot_smoke.py`
- `docs/sales-operator-core/PILOT-SMOKE-I7.md`
- `factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-i7-pilot-smoke.json`
- `factory/projects/empleado-uno-sales-operator-core/evidence/i7-pilot-fixture-leads.json`

## Behavior

The script creates a deterministic pilot-smoke batch in Agent Core DB:

- canonical Empleado.uno campaign seed/readback;
- active Medellín / clínicas-estética territory readback;
- 10 clearly marked synthetic `.test` prospects;
- 10 source-backed research snapshots;
- 10 lead scores;
- 10 personalized draft attack plans;
- 10 draft outreach queue rows;
- 1 CRM organization/contact/opportunity/follow-up readback for the top lead;
- daily report and dashboard/dry-run evidence.

Every generated lead and CRM row carries `metadata.i7_smoke=true`, `metadata.synthetic_pilot_fixture=true`, `metadata.not_real_business=true`, and `metadata.external_outbound_allowed=false`.

## Live smoke output

Command:

```bash
python3 scripts/runtime/sales_operator_i7_pilot_smoke.py \
  --format markdown \
  --target factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-i7-pilot-smoke.json
```

Result:

```text
# I7 Sales Operator pilot smoke

- Campaign: `empleado-uno-1000-subscribers-q3-2026`
- Mode: dry-run / no-send
- External sends: disabled
- Providers called: none

Prospects upserted: 10
Research snapshots: 10
Lead scores: 10
Attack plans: 10
Draft outreach queued: 10
CRM follow-up readback: 1 follow-up for `org-i7-pilot-clinica-aurora`
```

Evidence readback summary:

```json
{
  "ok": true,
  "external_sends": false,
  "leads_created": 10,
  "scored_leads": 10,
  "attack_plans": 10,
  "crm_readback_present": true,
  "tool_outputs": 61,
  "fixture_leads_target_exists": true
}
```

## DB readback

```json
{
  "i7_prospects": 10,
  "i7_research": 10,
  "i7_scores": 10,
  "i7_attack_plans": 10,
  "i7_outreach": 10,
  "i7_attempts": 0,
  "i7_open_followups": 1
}
```

## Acceptance criteria mapping

| Acceptance criterion | Evidence |
|---|---|
| Factory evidence includes tool outputs for campaign, territory, 10 scored leads, attack plans and CRM readback. | `sales-operator-i7-pilot-smoke.json` contains `tool_outputs=61`, campaign/territory/source tool results, 10 prospects/research/scores/attack plans/outreach drafts, and CRM timeline readback. |
| No real outbound sends occur in the smoke unless Jean explicitly activates a channel gate. | Evidence has `external_sends=false`, `external_actions_invoked=[]`, `i7_attempts=0`, draft outreach only, and all leads are `.test` synthetic fixtures. |

## G1 docs consulted

- `DOCUMENTATION_INDEX.md`
- `PRD.md` / `docs/sales-operator-core/PRD-001-sales-operator-core.md`
- `SPRINT_PLAN.md` / `docs/sales-operator-core/SPRINT-PLAN-001.md`
- `TASK_GRAPH.md` / `docs/sales-operator-core/TASK-GRAPH-001.md`
- `QA_GATES.md` / `SECURITY_GATES.md`
- `docs/sales-operator-core/CRON-LOOPS-I6.md`

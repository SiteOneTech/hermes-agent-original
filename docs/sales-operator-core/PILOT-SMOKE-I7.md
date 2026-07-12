# PILOT-SMOKE-I7 — Empleado.uno Sales Operator

Date: 2026-07-12
Status: implemented and verified

## Purpose

I7 proves the first pilot-smoke path for Empleado.uno Sales Operator Core:

1. Campaign and priority territory exist.
2. A 10-lead pilot batch can be imported.
3. Each lead can receive research, scoring and a personalized attack plan.
4. Outreach can be queued as draft/supervised without sending.
5. One top lead can bridge into CRM Core with organization/contact/opportunity/follow-up readback.
6. Daily report/dashboard/dry-run evidence remains no-send.

## Safety model

The I7 smoke uses **synthetic** pilot fixtures, not real businesses. Domains are reserved `.test` domains and every row carries metadata indicating:

```json
{
  "i7_smoke": true,
  "synthetic_pilot_fixture": true,
  "not_real_business": true,
  "external_outbound_allowed": false
}
```

No provider action is invoked. The script returns and writes evidence with:

```json
{
  "dry_run": true,
  "external_sends": false,
  "external_actions_invoked": []
}
```

## Command

```bash
python3 scripts/runtime/sales_operator_i7_pilot_smoke.py \
  --format markdown \
  --target factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-i7-pilot-smoke.json
```

## Expected result

```text
Prospects upserted: 10
Research snapshots: 10
Lead scores: 10
Attack plans: 10
Draft outreach queued: 10
CRM follow-up readback: 1 follow-up(s)
External sends: disabled
Providers called: none
```

## Evidence artifacts

- `factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-i7-pilot-smoke.json`
- `factory/projects/empleado-uno-sales-operator-core/evidence/i7-pilot-fixture-leads.json`

## DB readback query summary

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

## Next operational step

I7 does **not** activate real outbound. The next open Factory task is:

```json
{
  "task_id": "empleado-uno-sales-operator-core-i8-runtime-propagation-to-sitiouno-agent-runtime",
  "branch": "factory/empleado-uno-sales-operator-core/inc-090-runtime-propagation-sales-operator-core",
  "worktree_path": "/home/jean/Projects/.worktrees/sitiouno-agent-runtime/inc-090-runtime-propagation-sales-operator-core",
  "repo": "SiteOneTech/sitiouno-agent-runtime"
}
```

That task propagates the reusable Sales Operator Core surface to the runtime repo. Real production pilot contact remains a later channel-gated task that replaces synthetic fixtures with source-verified public businesses while keeping outreach draft-only until explicit approval.

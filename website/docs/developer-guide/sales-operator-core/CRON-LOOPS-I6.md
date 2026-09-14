# CRON-LOOPS-I6 — Sales Operator Core Daily Dry-Run

Date: 2026-07-12
Status: implemented as **dry-run / disabled-by-default**

## Purpose

I6 adds safe cron-loop entrypoints for the Sales Operator Core. The loops produce prioritized daily actions for Empleado.uno without calling any outbound provider.

The default state is intentionally conservative:

- no email sends;
- no WhatsApp sends;
- no SMS sends;
- no voice calls;
- no social DMs;
- no public posts;
- no provider ACK is interpreted as customer interest;
- no DB daily-report write unless `--write-report` is passed explicitly.

## Runtime entrypoints

| Entrypoint | Purpose | Default side effects |
|---|---|---|
| `scripts/runtime/sales_operator_daily_dry_run.py` | Builds the daily prioritized Sales Operator plan from Agent Core DB state. | stdout only; optional local JSON target. |
| `scripts/cron/sales_operator_daily_dry_run.sh` | Cron/no-agent wrapper around the Python script. | stdout + local JSON target. |

## Manual smoke command

```bash
python3 scripts/runtime/sales_operator_daily_dry_run.py \
  --campaign-id empleado-uno-1000-subscribers-q3-2026 \
  --format markdown \
  --target /home/jean/zeus-runtime/delivery-sandbox/user-data/sales_operator_daily_dry_run.json
```

## Self-contained cron specs

These are **not enabled by default**. They are ready for activation after Jean decides the cadence.

### Daily morning brief

- Schedule: `0 8 * * *`
- Mode: `no_agent_safe_script`
- Command:

```bash
/home/jean/Projects/hermes-agent-original/scripts/cron/sales_operator_daily_dry_run.sh \
  --campaign-id empleado-uno-1000-subscribers-q3-2026 \
  --format markdown
```

Self-contained prompt:

> Run the Sales Operator daily brief dry-run for campaign `empleado-uno-1000-subscribers-q3-2026`. Execute the repo script only. Do not send email, WhatsApp, SMS, voice calls, social DMs, posts, or provider actions. Return the script output and highlight blockers if any channel is not supervised/draft-only.

### Follow-up queue dry-run

- Schedule: `*/30 9-18 * * 1-6`
- Mode: `no_agent_safe_script`
- Command:

```bash
/home/jean/Projects/hermes-agent-original/scripts/cron/sales_operator_daily_dry_run.sh \
  --campaign-id empleado-uno-1000-subscribers-q3-2026 \
  --format markdown \
  --queue-limit 100
```

Self-contained prompt:

> Review due Sales Operator follow-up queue items in dry-run mode. Campaign: `empleado-uno-1000-subscribers-q3-2026`. Never execute queued outreach. Print prioritized queue review, approval requirements, and opt-out/rate-limit blockers only.

### Close-of-day report dry-run

- Schedule: `0 17 * * 1-6`
- Mode: `agent_reasoned_report_optional`
- Command:

```bash
/home/jean/Projects/hermes-agent-original/scripts/cron/sales_operator_daily_dry_run.sh \
  --campaign-id empleado-uno-1000-subscribers-q3-2026 \
  --format json
```

Self-contained prompt:

> Generate the Sales Operator close-of-day dry-run report from the JSON produced by the script. Campaign: `empleado-uno-1000-subscribers-q3-2026`. Summarize actions, replies, demos, closes, blockers, and tomorrow priorities. Do not infer customer interest from provider acknowledgements. Do not send outbound messages.

## Optional Hermes cron activation commands

Only run these after explicit activation. Use `deliver="local"` while validating if Jean does not want daily chat messages yet.

```python
cronjob(
  action="create",
  name="Sales Operator daily brief dry-run",
  schedule="0 8 * * *",
  script="/home/jean/Projects/hermes-agent-original/scripts/cron/sales_operator_daily_dry_run.sh",
  no_agent=True,
  deliver="local",
)
```

```python
cronjob(
  action="create",
  name="Sales Operator follow-up queue dry-run",
  schedule="*/30 9-18 * * 1-6",
  script="/home/jean/Projects/hermes-agent-original/scripts/cron/sales_operator_daily_dry_run.sh",
  no_agent=True,
  deliver="local",
)
```

## Acceptance evidence

Live dry-run against Agent Core DB returned:

```json
{"actions": 3, "cron_specs": 3, "dry_run": true, "external_sends": false, "messages_sent_by_dry_run": 0, "ok": true, "top_loop": "lead_discovery_tick"}
```

The top action is to build the first public lead batch for the priority territory because the campaign intentionally still has zero real prospects/contacted clients.

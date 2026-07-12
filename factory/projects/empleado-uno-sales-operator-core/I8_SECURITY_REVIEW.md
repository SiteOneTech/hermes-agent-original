# I8 Security Review — Runtime Propagation

Date: 2026-07-12
Owner: Zeus
Status: PASS

## Security boundary reviewed

I8 propagates Sales Operator Core into `sitiouno-agent-runtime` while preserving derived-agent isolation and commercial tool restrictions.

## Controls verified

| Control | Result |
|---|---|
| Real outbound providers | Not invoked |
| `external_sends` | `false` |
| `external_actions_invoked` | `[]` |
| `outreach_attempts` | `0` |
| Smoke leads | synthetic `.test`, no-contact fixtures |
| Queue rows | `draft` / supervised, human approval required |
| Commercial toolset | Includes Sales Operator tools only; privileged shell/code/file/factory-admin/raw adapters absent |
| Secret handling | No local/ad-hoc secrets generated; dedicated Sales Operator credential optional; fallback uses `sales_runtime` until Infisical provides `SALES_OPERATOR_*` |
| Signature role blocker | Fixed canonically by matching Zeus behavior: `SIGNATURE_DB_RUNTIME_PASSWORD` optional because signature migration creates the role shell |

## Toolset guard evidence

```json
{
  "required_present": [
    "sales_operator_dashboard_snapshot",
    "sales_operator_outreach_enqueue",
    "sales_operator_status"
  ],
  "forbidden_absent": true,
  "commercial_tool_count": 106
}
```

Forbidden tools checked absent from `commercial_operator`:

- `terminal`
- `execute_code`
- `skill_manage`
- `delegate_task`
- `cronjob`
- `crm_twenty_raw_request`

## Remaining future gates before production outbound

- source-verified public leads;
- explicit channel policy for each live channel;
- opt-out/rate-limit/quiet-hours enforcement;
- customer-interest detection from actual customer replies, not provider ACKs;
- supervised approval before any message/call/post is sent.

## Security conclusion

PASS for I8 runtime propagation. The module is available to commercial runtime agents in dry-run/supervised mode and remains fail-closed for outbound.

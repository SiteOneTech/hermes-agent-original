# Security Gates — Factory Runtime Remediation

## Security concerns

| Concern | Control | Status |
|---|---|---|
| Secret leakage in alerts | Alert payloads use task IDs/categories/messages only; no raw logs/secrets | passed |
| Unauthorized DB writes | Runtime writes only through canonical `factory_pg`/CLI path | passed |
| Dispatcher bypasses dependencies | `claim_next_task` still uses dependency checks and single-active-run guard | passed |
| Orphan repair kills live work | Repair only when no queued/running `task_runs` exists | passed |
| Notification spam | Watchdog suppresses repeated alert keys | passed |
| Notion as source of truth drift | Notion is PM/reporting; metadata links page; Factory DB remains canonical | controlled |

## Required security evidence

- No API keys printed in command output.
- Notion token used only through environment; not persisted in repo.
- Alert scripts avoid worker log dumps.
- Human questions contain minimal context.

## Security verdict

GREEN after final reconciliation, provided Notion metadata and required docs are present and no alerts expose sensitive content.

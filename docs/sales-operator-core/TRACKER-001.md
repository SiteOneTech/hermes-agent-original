# Tracker 001 — Sales Operator Core

| Gate | Status | Evidence |
|---|---|---|
| Intake | Passed | Jean requested specialized daily seller module for Empleado.uno and future products. |
| Architecture | Pending | Factory must review PRD/ADR and Agent Core schema design. |
| Planning | Passed | PRD/ADR/Sprint/Task graph/QA/Docs index created. |
| Security | Pending | Must implement anti-spam, opt-out, rate limits, channel validation. |
| Implementation | Pending | DB/tools not implemented yet. |
| Test | Pending | No module tests yet. |
| Delivery | Pending | No live smoke yet. |

## Current assumptions

- Product: Empleado.uno.
- Initial capital: US$5k plus reinvested subscriptions.
- Human team: Jean + possible David closer + limited developer availability.
- Preferred operation: automated research, personalization, follow-up and content; humans only for hot leads/exceptions.

## Open questions for later, not blockers for design

- First territory/vertical assignment from Jean.
- Exact outbound channel availability and limits.
- Whether WhatsApp Cloud, Baileys bridge, SMS, Vapi, SendGrid are approved for this campaign.
- Initial daily budget and allowed outreach volume.

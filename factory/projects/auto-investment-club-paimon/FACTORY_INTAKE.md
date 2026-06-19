# Factory Intake — Auto Investment Club / Paimon

**Project ID:** `auto-investment-club-paimon`  
**Source:** Email from Paimon to Zeus (`zeus@sitiouno.com`, CC Jean) received 2026-06-18; attachment `auto-investment-club-blueprint.md`.  
**Original blueprint copy:** `PAIMON_BLUEPRINT_ORIGINAL.md`  
**Original attachment SHA-256:** `45e11ef12edf2ce3eba36e075afd36913f21c977c2ad42004a66348982f2a5fe`  
**Human owner:** Jean García  
**Operational owner proposed by source brief:** Paimon on `openclaw-miami`  
**Current Factory state requested by Jean:** **PAUSED / NOT AUTONOMOUS**.

## Jean directive

Jean asked Zeus to pass Paimon’s Auto Investment Club blueprint to the SitioUno Factory as a brief, complement it with useful context for future investigation/work, but **not activate autonomous execution yet**:

> “no lo actives aun autónomo déjalo pausado vamos a ir cerrando todos los demás poco a poco para que al activar este que es importante ya tengan el proceso mas probado y refinado.”

## One-line objective

Design and later implement a guarded, auditable, agent-assisted investment research and paper-trading system coordinated by Paimon, with strict risk controls and no live trading until Jean explicitly activates it.

## Business / product framing

The proposed system is not a single monolithic trading bot. It is framed as an “investment club” with specialized agents:

- Macro analyst: market regime and macro signals.
- Technical analyst: indicators, trend/momentum, entry/exit candidates.
- Fundamental analyst: company/ETF/fundamental screens.
- Risk manager: capital allocation, max drawdown, stops, strategy pause rules.
- Trader executor: broker/data API integration.
- Paimon: PM/CIO consolidating signals and reporting to Jean.

The Factory should treat this as a high-risk fintech/automation product with a staged path:

1. Research/design only.
2. Paper trading only.
3. Shadow mode / non-executing signals.
4. Tiny live pilot only after explicit human approval and all safety gates pass.

## Source blueprint summary

Paimon’s attachment proposes:

- Initial capital: about USD 1,944.
- Target: daily recurring income from algorithmic trading.
- Broker/data: Alpaca Markets Algo Trader Plus, estimated USD 99/month.
- Macro data: FRED API.
- Technical/fundamental supplement: Alpha Vantage.
- Storage: existing PostgreSQL on Paimon/openclaw side.
- Orchestration: Paimon / Hermes cron jobs / delegate_task.
- Dashboard: FastAPI + React, local/Tailscale only.
- Credentials: Infisical.
- Deployment: localhost on `openclaw-miami`.

## Factory classification for now

| Dimension | Current decision |
|---|---|
| Repo scope | `docs_or_research_only` for this paused intake record. Re-evaluate before implementation. |
| Work intent | `docs_research` now. Implementation requires new G0 strategy. |
| Risk level | `critical` because it may eventually place real trades and handle financial credentials. |
| Autonomy | `0` / disabled. No autonomous workers should start. |
| Status | Paused intake/backlog. |
| Execution | No trading, no broker credential work, no deployment, no cron activation. |

## Non-negotiable guardrails

1. **No live trading without Jean’s explicit later approval.**
2. **No autonomous execution while this Factory project is paused.**
3. **Paper-trading first.** The first implementation stage must never place live orders.
4. **Broker keys must live only in Infisical** and must start as paper/sandbox credentials.
5. **Kill switch required before any automated order path.** At minimum: global kill switch, per-strategy pause, max-loss circuit breaker, and manual override.
6. **Risk manager must be independent of signal generators.** Signal agents must not directly size or execute orders.
7. **Full audit trail required.** Every signal, rationale, risk decision, order request, fill, rejection, and human override must be persisted.
8. **No “daily income guarantee” framing.** The system may target returns, but all docs/UI must state uncertainty and loss risk.
9. **Tax/compliance review required before live mode.** Frequent trading has tax, margin, settlement, and regulatory implications.
10. **No public dashboard.** Internal only via Tailscale/private network unless Jean explicitly asks otherwise.

## Initial team mission when activated later

When Jean later says to activate/research this project, the first Factory increment should be G1 documentary readiness, not code. The team should produce:

- Requirements analysis and PRD.
- Risk/compliance analysis.
- Broker/data-provider comparison and current-pricing validation.
- Paper-trading architecture.
- Strategy evaluation protocol.
- Backtesting/paper-trading data model.
- Security/secrets architecture.
- Clear activation gates for paper mode and live mode.

## Immediate status

This brief exists so the Factory has the project context ready. It is intentionally not autonomous and should stay parked until Jean explicitly resumes/activates it.

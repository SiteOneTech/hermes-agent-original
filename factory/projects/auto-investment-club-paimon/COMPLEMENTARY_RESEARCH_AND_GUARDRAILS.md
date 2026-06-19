# Complementary Research and Guardrails — Auto Investment Club

This document complements Paimon’s original blueprint with research notes, safety constraints, and work directions for a future Factory team. It is not an approval to execute trades or activate autonomous work.

## Current external research snapshot

### Alpaca market data / trading API

Official Alpaca market-data documentation states:

- The Trading API has Basic and Algo Trader Plus plans.
- Basic equities plan: free, IEX real-time, 30 WebSocket symbols, historical data limited for latest 15 minutes, 200 historical API calls/min.
- Algo Trader Plus: USD 99/month, all US stock exchanges / SIP coverage, unlimited equity WebSocket symbols, no historical 15-minute restriction, 10,000 historical API calls/min.
- Options data and crypto have separate risk disclosures.

Factory implication: before implementation, validate the current Alpaca plan, fees, account type, supported order types, paper-trading API behavior, and data limitations directly from Alpaca docs/API/account.

### FINRA / frequent intraday trading

FINRA’s investor guidance on frequent intraday trading highlights:

- Frequent intraday trading is high risk and can lose some or all investment capital.
- Cash accounts must use settled funds and avoid free-riding/good-faith violations.
- Margin accounts have heightened risk and can lose more than original investment.
- Current guidance emphasizes intraday margin requirements, margin deficits, broker controls, trading costs, tax implications, and risk tolerance.

Factory implication: do not encode assumptions about historical PDT rules without current broker/legal verification. Add a compliance research task before any live-trading path.

### SEC / algorithmic trading risk

SEC materials and enforcement history around algorithmic trading emphasize:

- Algorithmic trading has market-structure and operational-risk concerns.
- If any product ever involves third-party capital or external investors, disclosures and adviser/broker compliance become a major gating issue.
- For Jean-only personal trading, still maintain rigorous auditability, controls, and risk disclosures.

Factory implication: current scope should remain personal/internal unless Jean explicitly expands it. Do not design as an external fund, advisory service, or public investment product.

## Key risks to investigate

| Risk | Why it matters | Required mitigation before live mode |
|---|---|---|
| Real-money loss | Small capital can still suffer severe drawdown. | Paper trading, strict max loss, kill switch, low sizing. |
| False confidence from agents | LLMs can overfit, hallucinate, or rationalize weak signals. | Deterministic strategy rules, backtests, no free-form order execution. |
| Bad data / latency | Missing/delayed data can trigger wrong orders. | Data quality checks, provider status checks, stale-data guard. |
| Broker/API outage | Orders can fail or partially fill. | Idempotent order state, retries with limits, reconciliation jobs. |
| Secrets leakage | Broker keys grant financial access. | Infisical, paper/live key separation, least-privilege runtime. |
| Strategy drift | Agents may change strategy without evidence. | Versioned strategies, change approvals, immutable decision logs. |
| Regulatory/tax exposure | Frequent trading and margin have rules/tax effects. | Compliance/tax checklist, external professional review if needed. |
| Overtrading costs | Fees/spreads/slippage can erase small returns. | Slippage model, minimum edge threshold, trade frequency caps. |
| Autonomy too early | Unproven Factory/runtime could cause operational mistakes. | Keep paused until Jean says Factory process is refined enough. |

## Recommended staged roadmap

### Stage 0 — Parked brief (current)

- Store Paimon’s original blueprint and this complementary brief.
- Create a paused Factory project record.
- Do not dispatch autonomous workers.
- Do not create broker credentials.
- Do not schedule trading cron jobs.

### Stage 1 — Research and G1 readiness

Deliverables:

- `REQUIREMENTS_ANALYSIS.md`
- `PRD.md`
- `ADRS.md`
- `TECHNICAL_BLUEPRINT.md`
- `RISK_AND_COMPLIANCE_REVIEW.md`
- `STRATEGY_EVALUATION_PROTOCOL.md`
- `SECURITY_GATES.md`
- `QA_GATES.md`
- `TASK_GRAPH.md`

Acceptance criteria:

- No code execution beyond research/prototypes.
- External API docs/pricing verified from current sources.
- Explicit paper/live separation designed.
- No unresolved safety blocker hidden as “future work.”

### Stage 2 — Paper-trading platform only

Deliverables:

- Data ingestion for market/macro data.
- Strategy signal engine with deterministic rules.
- Portfolio simulator / paper-trading ledger.
- Dashboard for paper positions and signals.
- Full audit trail.
- Kill switch controls even in paper mode.

Acceptance criteria:

- All broker order calls point to paper/sandbox endpoints.
- Live credentials absent from runtime.
- Tests prove no live order path exists.

### Stage 3 — Shadow mode

Deliverables:

- System generates recommendations only.
- Jean/Paimon can compare recommendations vs actual market outcomes.
- No broker orders, even paper, unless explicitly enabled.

Acceptance criteria:

- At least two weeks of stable paper/shadow performance.
- Drawdown and missed-risk events reviewed.
- Strategy changes tracked.

### Stage 4 — Live pilot (future only, explicit approval)

Prerequisites:

- Jean explicit activation.
- External compliance/tax review if needed.
- Live kill switch verified.
- Maximum per-trade, per-day, per-week, and per-strategy loss limits enforced in code and DB.
- Live credentials isolated and reversible.

## Strategy design recommendations

1. Start with **simple, auditable rules**, not opaque ML.
2. Prefer ETFs/liquid equities for first paper tests.
3. Track benchmark comparisons: SPY buy-and-hold, cash, and each strategy’s own baseline.
4. Store every decision as structured data: signal inputs, decision, confidence, risk adjustment, order recommendation, execution result.
5. Build reporting before live trading: daily PnL, exposure, drawdown, open risk, strategy attribution.

## Data model additions suggested beyond original blueprint

Paimon proposed `macro_data`, `technical_data`, `positions`, `trades`, and `decisions`. Add:

- `strategies`: versioned strategy definitions and parameters.
- `signals`: raw candidate signals from analysts.
- `risk_reviews`: independent risk manager decisions.
- `orders`: intended broker orders before execution.
- `fills`: broker-reported fills.
- `account_snapshots`: cash/equity/buying power snapshots.
- `circuit_breaker_events`: kill switch, max-loss, stale-data, broker outage.
- `human_approvals`: explicit Jean approvals for mode transitions.
- `provider_health`: market data/broker API status.

## Open research questions

1. Is Alpaca the best broker/data stack for this initial small-capital use case?
2. Should the system use cash account, margin account, or paper-only until further notice?
3. How should taxes and trade reporting be exported for Jean/accountant?
4. What exact instruments are allowed at launch: ETFs only, equities, crypto, options?
5. Should crypto be excluded from v1 because Alpaca crypto is not SIPC/FINRA protected?
6. What is the maximum acceptable daily/weekly drawdown for Jean?
7. Does Paimon’s existing PostgreSQL contain anything that should not mix with trading data?
8. Should the dashboard be on Paimon only, Zeus only, or a dedicated private service?
9. Which alerts go to Jean vs Paimon vs Zeus?
10. What evidence threshold lets Jean consider live pilot?

## Factory note

This project is intentionally paused. Future workers must treat this as a brief and research pack, not permission to implement or run a trading system.

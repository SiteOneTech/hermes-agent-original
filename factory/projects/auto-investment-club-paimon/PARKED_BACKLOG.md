# Parked Backlog — Auto Investment Club / Paimon

These are proposed tasks for a future activation. They are intentionally parked. Do not dispatch autonomous workers until Jean explicitly resumes this project.

## T00 — Mature research pack and risk/compliance brief

**Owner profile suggestion:** `product-analyst`  
**Reviewer suggestion:** `security-reviewer`  
**Phase:** research/planning  
**Status:** parked

Acceptance criteria:

- Validate Alpaca, FRED, Alpha Vantage current docs/pricing/limits.
- Produce a concise broker/data/provider comparison.
- Produce `RISK_AND_COMPLIANCE_REVIEW.md` focused on personal/internal trading, margin/cash accounts, taxes, and automated-system risk.
- Explicitly list what is out of scope until live approval.

## T01 — Full G1 documentary readiness pack

**Owner profile suggestion:** `implementation-planner`  
**Reviewer suggestion:** `quality-reviewer`  
**Phase:** planning  
**Status:** parked

Acceptance criteria:

- Create/validate the full G1 document pack: PRD, ADRs, methodology plan, technical blueprint, sprint plan, task graph, tracker, QA/security gates.
- Mark all future implementation tasks with paper-only acceptance criteria unless Jean later approves live mode.
- Ensure every task has explicit evidence requirements.

## T02 — Paper-trading architecture spike

**Owner profile suggestion:** `solution-architect`  
**Reviewer suggestion:** `security-reviewer`  
**Phase:** architecture/spike  
**Status:** parked

Acceptance criteria:

- Design deterministic paper-trading ledger and broker abstraction.
- Prove live credentials are not required for paper mode.
- Design kill-switch and circuit-breaker mechanisms before coding.
- Identify Paimon/openclaw deployment boundaries.

## T03 — Data pipeline prototype plan

**Owner profile suggestion:** `codex-builder` or `claude-builder` after G1  
**Reviewer suggestion:** `qa-verifier`  
**Phase:** implementation/paper-only  
**Status:** parked

Acceptance criteria:

- Only after G1 activation.
- Pull macro/market sample data into local tables or fixtures.
- No live orders and no live broker credentials.
- Unit tests for stale-data and provider-failure behavior.

## T04 — Paper dashboard plan

**Owner profile suggestion:** `claude-builder` after G1  
**Reviewer suggestion:** `qa-verifier`  
**Phase:** implementation/paper-only  
**Status:** parked

Acceptance criteria:

- Private dashboard only.
- Shows portfolio, paper trades, signals, drawdown, kill switches, and audit log.
- Requires no public exposure and no live credential access.

## T05 — Live-readiness gate design

**Owner profile suggestion:** `security-reviewer` + `devops-release`  
**Reviewer suggestion:** Jean/Zeus explicit human decision  
**Phase:** release/security  
**Status:** parked

Acceptance criteria:

- Define exactly what evidence is required before live mode.
- Include human approval record, maximum capital/risk settings, secrets separation, kill-switch smoke test, broker account constraints, and rollback plan.
- No live mode without a recorded Jean decision.

---
project_id: zeus-independent-alpha-research
status: planning
validated: yes
reviewed: yes
owner: solution-architect
---

# Assumptions and Open Questions

## Decisions already made
- Magnus is the runtime CEO/operator of Vonash; Zeus is an independent research advisor.
- Zeus does not trade, alter risk, trigger paper/live, promote strategies, or modify Vonash.
- Cross-system collaboration uses a typed API/thread with durable outbox/acknowledgement; Telegram is an optional visible mirror.
- The daily workshop is bounded at 45 minutes, six substantive turns per agent, and three cards/topics.
- Reactive alerts are research/decision context only, not execution directives.
- The implementation must be Factory-managed and deployed by the Vonash/internal engineering lane after review.

## Verified prior observations
- Vonash already has research, hypothesis, report/directive, scheduling and experiment-related concepts in its canonical substrate.
- A previous directive/report handshake did not provide a dependable typed acknowledgement loop.
- A previously observed research dispatcher was explicitly retired/pruned; it must not be reactivated by changing a database flag.
- A source registry entry marked enabled did not prove deployed credential injection or fresh ingestion.

## Audit-required questions
1. What are the current Vonash repository, branch, service ownership, and deployment topology?
2. Which service/API should own research threads, outbox delivery, acknowledgement and experiment result references?
3. What workload identity, auth scopes, secret delivery path, and egress policy exist for Zeus↔Vonash communication?
4. Which data types are truly present historically and live: bars, trades, quotes, bid/ask volume, aggressor side, depth, options chain/Greeks, macro/news/events?
5. Which evaluators, backtest, paper/shadow, risk, and promotion gates are actually current and supported?
6. What retention/redaction requirements apply to research payloads and Telegram mirrors?
7. What policy owner sets the response objectives for alert severities during market hours?

## Planning rule
Unknowns remain explicit acceptance items in the implementation audit. They must not be filled with plausible endpoint names, credentials, or data claims.

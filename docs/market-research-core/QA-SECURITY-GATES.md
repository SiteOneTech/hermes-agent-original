# QA & Security Gates — Zeus Independent Alpha Research

## Pre-flight gates

- [ ] Project remains `zeus_only`; no Vonash runtime/database deploy target is introduced.
- [ ] Worktree branch is isolated from active refactors.
- [ ] Migration plan includes schema, module registry, dedicated runtime role/credential, grants, indexes, and rollback posture.
- [ ] The market-research toolset cannot silently fall back to a broader Agent Core runtime credential.
- [ ] No secret is placed in code, tests, logs, reports, or chat.

## Research integrity gates

- [ ] Card has mechanism, falsification criterion, required data granularity, costs/execution assumptions, and provenance.
- [ ] Practitioner/social content is labelled ideation-only.
- [ ] Card lineage compares mechanism, not merely its title.
- [ ] Review tests leakage, survivorship bias, data-snooping, regime dependence, capacity, and transaction costs.
- [ ] Result comparison requires identical/specified evaluation gate definitions and temporal windows.

## Collaboration gates

- [ ] Session limit is enforced by code: four substantive agent turns (two per agent) or 45 minutes, whichever occurs first.
- [ ] Only research message types are allowed: `brief`, `question`, `capability_ack`, `critique`, `experiment_request`, `result_reference`, `synthesis`.
- [ ] Forbidden types are rejected: `trade`, `order`, `risk_change`, `promotion`, `paper_activation`, `live_activation`.
- [ ] KB/Slack adapter is read-only, allowlisted, and disabled without explicit connector configuration.
- [ ] Every imported item identifies system, collection/channel, reference, retrieval time, and redaction state.

## Verification gates

- [ ] Unit tests for schema invariants and state machines.
- [ ] Unit tests proving turn/time closure and forbidden message rejection.
- [ ] Tool tests run with an Agent Core test database.
- [ ] Full targeted test suite passes with no type/lint regression.
- [ ] Manual pilot produces one Alpha Card and one completed zero-execution session.

## Stop conditions

Stop and escalate instead of guessing when an external KB/API lacks authentication details, its data usage/license is unclear, experiment results are incomparable, or a requested operation could alter trading/paper/live state.

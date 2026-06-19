# G0 Repository Strategy — Auto Investment Club / Paimon

## Current G0 decision

This paused intake record is **docs/research only**.

| Field | Value |
|---|---|
| `repo_scope` | `docs_or_research_only` |
| `work_intent` | `docs_research` |
| Primary repo for this intake pack | `/home/jean/Projects/hermes-agent-original` |
| Project docs path | `factory/projects/auto-investment-club-paimon/` |
| Base branch | `main` |
| Autonomous execution | Disabled |

## Why this G0 is intentionally narrow

The eventual implementation may belong on `openclaw-miami`, a new dedicated repo, Paimon’s profile, a private service repo, or a runtime/fleet repo. That decision is not safe to make until the Factory team performs the research/G1 phase.

This record exists to preserve the brief and give the Factory a canonical paused project. It does **not** decide the implementation repo yet.

## Future G0 questions before implementation

1. Should the implementation live in a new private repo such as `SiteOneTech/auto-investment-club`?
2. Should code live under Paimon/openclaw only, or also be visible to Zeus Factory?
3. Should the dashboard be standalone, part of SitioUno runtime, or a Paimon-local private service?
4. What branch/worktree policy should be used for paper-trading implementation?
5. Which environment owns the Agent Core DB tables: Paimon local DB, Zeus Agent Core, or dedicated DB?
6. What credential boundary separates paper and live trading?

## Activation rule

Before any implementation task starts, a Factory operator must update/replace this G0 with the chosen implementation strategy and record it in Factory DB. Until then, this project remains a parked research/intake project.

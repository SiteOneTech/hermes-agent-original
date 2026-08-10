---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: pending
---

# TASK GRAPH

## Factory DB reconciliation snapshot
Verified read-only with `hermes factory status zeus-alpha-research-ledger-core --json` against Agent Core Factory DB at `2026-08-10T04:50:09-04:00` (`db_backend=agent_core_postgres`, `database=zeus_agent`). Current ALR-010 is claimed by `implementation-planner`; `ALR-060` is terminal `superseded` and retained only as auditable history, not a live compatibility flow. Every non-terminal source task has the Jean-authorized `increment_integration_waived` metadata that enforces PR-first/QA Guardian delivery rather than Factory direct merge. Factory reconciliation still reports `missing_project_artifact_dir` / `missing_required_docs` until this branch-local pack is pushed, reviewed, PR-handled and exposed on canonical base.

### Required deterministic ALR-020 metadata reconciliation — blocking

The Factory DB currently records an ALR-020 acceptance clause for **bounded local sessions**, while this deliberately bounded v1 contract excludes every collaboration session/message entity. This is a task-plan incompatibility, not permission to expand v1 and not a documentation-only waiver. Before ALR-020 implementation can start, the authorized Factory metadata owner must make and read back a deterministic correction on the ALR-020 task: remove the bounded-local-sessions acceptance clause and replace it with this exact scope statement: `v1 persists programs, sources, immutable evidence, cycles, cards, lineage, reviews, result references, inert handoffs, and scheduler readiness only; collaboration session/message entities are excluded; bounded local normalized-evidence batches are intake, not sessions.` The reconciliation evidence must record task ID, changed acceptance field, old/new literal values, actor/time, and read-back equality to this statement. This task does not alter Factory DB; normal implementation remains blocked until that evidence exists.

| Task ID | Phase / status | Owner → reviewer | Depends on | Branch | Worktree |
|---|---|---|---|---|---|
| `zeus-alpha-research-ledger-core-alr-010-g1-rebaseline-and-local-ledger-c` | planning / claimed | implementation-planner → solution-architect | — | `factory/zeus-alpha-research-ledger-core/inc-010-alr-010-g1-rebaseline-and-local` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-010-alr-010-g1-rebaseline-and-local` |
| `zeus-alpha-research-ledger-core-alr-020-agent-core-schema-and-dedicated-` | implementation / todo | claude-builder → security-reviewer | ALR-010 | `factory/zeus-alpha-research-ledger-core/inc-020-alr-020-agent-core-schema-and-de` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-020-alr-020-agent-core-schema-and-de` |
| `zeus-alpha-research-ledger-core-alr-030-research-ledger-json-tools-and-l` | implementation / todo | codex-builder → quality-reviewer | ALR-020 | `factory/zeus-alpha-research-ledger-core/inc-030-alr-030-research-ledger-json-too` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-030-alr-030-research-ledger-json-too` |
| `zeus-alpha-research-ledger-core-alr-040-source-provenance-adapters-and-r` | implementation / todo | claude-builder → quality-reviewer | ALR-030 | `factory/zeus-alpha-research-ledger-core/inc-040-alr-040-source-provenance-adapte` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-040-alr-040-source-provenance-adapte` |
| `zeus-alpha-research-ledger-core-alr-050-daily-research-cycle-and-inert-h` | implementation / todo | codex-builder → security-reviewer | ALR-030, ALR-040 | `factory/zeus-alpha-research-ledger-core/inc-050-alr-050-daily-research-cycle-and` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-050-alr-050-daily-research-cycle-and` |
| `zeus-alpha-research-ledger-core-alr-060-independent-quality-and-security` | quality_review / superseded | quality-reviewer → security-reviewer | ALR-020..050 | historical branch only | historical worktree only |
| `zeus-alpha-research-ledger-core-alr-061-independent-specification-and-ar` | quality_review / todo | product-analyst → solution-architect | ALR-020..050 | `factory/zeus-alpha-research-ledger-core/inc-060-alr-061-independent-specificatio` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-060-alr-061-independent-specificatio` |
| `zeus-alpha-research-ledger-core-alr-062-independent-quality-and-tdd-revi` | quality_review / todo | quality-reviewer → qa-verifier | ALR-020..050 | `factory/zeus-alpha-research-ledger-core/inc-061-alr-062-independent-quality-and` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-061-alr-062-independent-quality-and` |
| `zeus-alpha-research-ledger-core-alr-063-independent-security-and-no-egre` | security_review / todo | security-reviewer → factory-orchestrator | ALR-020..050 | `factory/zeus-alpha-research-ledger-core/inc-062-alr-063-independent-security-and` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-062-alr-063-independent-security-and` |
| `zeus-alpha-research-ledger-core-alr-070-live-local-db-and-tool-smoke-wit` | qa / todo | qa-verifier → quality-reviewer | ALR-061, ALR-062, ALR-063 | `factory/zeus-alpha-research-ledger-core/inc-070-alr-070-live-local-db-and-tool-s` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-070-alr-070-live-local-db-and-tool-s` |
| `zeus-alpha-research-ledger-core-alr-080-zeus-signed-pr-and-qa-guardian-h` | delivery / todo | factory-reporter → qa-verifier | ALR-070 | `factory/zeus-alpha-research-ledger-core/inc-080-alr-080-zeus-signed-pr-and-qa-gu` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-080-alr-080-zeus-signed-pr-and-qa-gu` |
| `zeus-alpha-research-ledger-core-reconcile-missing-required-docs` | documentation / todo | factory-reporter → factory-orchestrator | — | unassigned | unassigned |

The last row is Factory-generated reconciliation for documents not yet on canonical base. It cannot close an implementation gate by itself; ALR-010’s actual PR/QA evidence resolves the underlying condition.

## Review and delivery contract
- ALR-061 produces a distinct specification/architecture mapping for every requirement and boundary.
- ALR-062 produces distinct TDD/quality evidence.
- ALR-063 produces distinct security/least-privilege/no-egress evidence.
- ALR-070 may start only when all three exact review reports cite the candidate SHA and are accepted.
- Every source increment produces a Zeus-signed `agent:zeus` PR. Its per-task waiver prevents Factory direct integration into `main`; QA Guardian merge evidence is mandatory before terminal closure. Zeus never merges or deploys.
- ALR-020 additionally may not start until the required bounded-local-sessions metadata reconciliation above is recorded and read back exactly; it does not add a collaboration-session implementation task.

## Reconciliation command
```bash
python3 - <<'PY'
from hermes_cli import agent_core_sql as sql
from hermes_cli import factory_pg
print(sql.rows("SELECT task_id, phase, status, owner_profile, reviewer_profile, dependencies, branch, worktree_path FROM factory.tasks WHERE project_id='zeus-alpha-research-ledger-core' ORDER BY priority, created_at", user=factory_pg._user()))
PY
```

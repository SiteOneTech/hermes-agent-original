---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: pending
---

# TASK GRAPH

## Factory DB reconciliation snapshot
Verified read-only during R2 with `hermes factory status zeus-alpha-research-ledger-core --json` against Agent Core Factory DB (`db_backend=agent_core_postgres`, `database=zeus_agent`) and local Git inspection. The baseline ALR-010 task is `done`; `ALR-010-R1` is terminal `superseded` after gate 697; `ALR-010-R2` is the current bounded documentary rework; `ALR-060` is terminal `superseded` and retained only as auditable history, not a live compatibility flow. Factory events `173433` and `173494` record that ALR-010-R1 commits `b9396bcd7d14ee6f212bd0fd0609e468cecf567f` and `6ee8b4fdb886d0834bfbc62c7e152ee35d505e66` were integrated to `main` with `merge_no_ff_push_origin`, producing `origin/main` merge commits `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a` and `9f975acb0625750b8d46648766d1395c89392dca`; both branch commits are ancestors of `origin/main`. These are observed integration anomalies to reconcile, not PR/QA approval or downstream authority. Future non-terminal source tasks retain the Jean-authorized `increment_integration_waived` metadata and must not dispatch until the exact R2 corrected SHA is visible in a Zeus-signed `agent:zeus` PR, independently reviewed, and the ALR-020 task-acceptance conflict below is fixed/read back.

### Required deterministic ALR-020 acceptance metadata reconciliation — blocking

The Factory DB currently records this ALR-020 acceptance literal: `Schema covers programs, sources, immutable evidence, alpha cards, lineage, reviews, cycles, bounded local sessions, result references, and inert handoff packages.` That conflicts with this deliberately bounded v1 contract, which excludes every collaboration session/message entity. This is a task-plan incompatibility, not permission to expand v1 and not a documentation-only waiver. Before ALR-020 implementation can start, the authorized Factory metadata owner must make and read back a deterministic correction on the ALR-020 task: remove the bounded-local-sessions acceptance clause and replace it with this exact scope statement: `v1 persists programs, sources, immutable evidence, cycles, cards, lineage, reviews, result references, inert handoffs, and scheduler readiness only; collaboration session/message entities are excluded; bounded local normalized-evidence batches are intake, not sessions.` The reconciliation evidence must record task ID, changed acceptance field, old/new literal values, actor/time, and read-back equality to this statement using the approved Factory control path. This R2 documentation task does not alter ALR-020 Factory DB metadata; normal implementation remains blocked until that evidence exists.

### Observed ALR-010-R1 base-branch integrations — reconciliation record

- Factory evidence 1: event `173433`, `event_type=increment_integrated`, `increment_integration_method=merge_no_ff_push_origin`, `increment_integrated_by=implementation-planner`, `increment_integrated_at=2026-08-10T09:22:51.090409Z`, `increment_base_commit_before=00e7bb4ab0fcd9013ffa924ce6c5a8ae2c2ae2fc`, `increment_branch_commit=b9396bcd7d14ee6f212bd0fd0609e468cecf567f`, `increment_base_commit_after=e3d04ff94b67e6e21be1d5515bdb71400fbedf0a`.
- Factory evidence 2: event `173494`, `event_type=increment_integrated`, `increment_integration_method=merge_no_ff_push_origin`, `increment_integrated_by=implementation-planner`, `increment_integrated_at=2026-08-10T09:45:17.577998Z`, `increment_base_commit_before=e3d04ff94b67e6e21be1d5515bdb71400fbedf0a`, `increment_branch_commit=6ee8b4fdb886d0834bfbc62c7e152ee35d505e66`, `increment_base_commit_after=9f975acb0625750b8d46648766d1395c89392dca`.
- Git evidence: `git show --no-patch --pretty=format:'%H%n%P%n%s' e3d04ff94b67e6e21be1d5515bdb71400fbedf0a` identifies parents `00e7bb4ab0fcd9013ffa924ce6c5a8ae2c2ae2fc` and `b9396bcd7d14ee6f212bd0fd0609e468cecf567f`; `git show --no-patch --pretty=format:'%H%n%P%n%s' 9f975acb0625750b8d46648766d1395c89392dca` identifies parents `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a` and `6ee8b4fdb886d0834bfbc62c7e152ee35d505e66`; `git merge-base --is-ancestor` returns `0` for both branch commits against `origin/main`.
- Interpretation: the docs must not claim ALR-010-R1 is branch-only, unmerged, or unaffected by a second direct integration. Both merges remain non-approval evidence because gates 695/697 failed and no independent PASS/PR/QA Guardian evidence exists for the corrected R2 candidate.

| Task ID | Phase / status | Owner → reviewer | Depends on | Branch | Worktree |
|---|---|---|---|---|---|
| `zeus-alpha-research-ledger-core-alr-010-g1-rebaseline-and-local-ledger-c` | planning / done | implementation-planner → solution-architect | — | `factory/zeus-alpha-research-ledger-core/inc-010-alr-010-g1-rebaseline-and-local` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-010-alr-010-g1-rebaseline-and-local` |
| `zeus-alpha-research-ledger-core-alr-010-r1-bounded-g1-contract-rework` | planning / superseded | implementation-planner → solution-architect | gates 686/687 request-changes; gates 695/697 direct-integration findings | `factory/zeus-alpha-research-ledger-core/inc-010-alr-010-g1-rebaseline-and-local` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-010-alr-010-g1-rebaseline-and-local` |
| `zeus-alpha-research-ledger-core-alr-010-r2-pr-first-g1-merge-evidence-re` | planning / running | implementation-planner → solution-architect plus independent spec/security reviewers | gate 697 rework; no downstream authority | `factory/zeus-alpha-research-ledger-core/inc-011-alr-010-r2-pr-first-g1-reconciliation` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-011-alr-010-r2-pr-first-g1-reconciliation` |
| `zeus-alpha-research-ledger-core-alr-020-agent-core-schema-and-dedicated-` | implementation / todo | claude-builder → security-reviewer | ALR-010-R2 accepted, PR/review evidence recorded, ALR-020 metadata corrected | `factory/zeus-alpha-research-ledger-core/inc-020-alr-020-agent-core-schema-and-de` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-020-alr-020-agent-core-schema-and-de` |
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

The last row is Factory-generated reconciliation for document-readiness drift. It cannot close an implementation gate by itself; ALR-010-R2 still requires a fresh committed SHA, Zeus-signed `agent:zeus` PR visibility, independent exact-SHA specification/security PASS evidence, and explicit handling of both observed integration anomalies before downstream implementation starts.

## Review and delivery contract
- ALR-061 produces a distinct specification/architecture mapping for every requirement and boundary.
- ALR-062 produces distinct TDD/quality evidence.
- ALR-063 produces distinct security/least-privilege/no-egress evidence.
- ALR-070 may start only when all three exact review reports cite the candidate SHA and are accepted.
- ALR-010-R2 and future source increments must produce a Zeus-signed `agent:zeus` PR and QA Guardian/independent-review evidence before terminal closure. The observed ALR-010-R1 Factory direct integrations are recorded above as gate-695/gate-697 reconciliation evidence, not as a repeatable delivery path or implementation authority.
- ALR-010-R2 resolves only the documentation findings from failed gates 686/687 plus the direct-integration evidence findings from gates 695/697. It does not implement ledger code, alter non-project Factory task metadata, perform another base merge, deploy or grant downstream implementation authority.
- ALR-020 additionally may not start until the required bounded-local-sessions metadata reconciliation above is recorded and read back exactly; it does not add a collaboration-session implementation task.

## Allowed reconciliation command
```bash
hermes factory status zeus-alpha-research-ledger-core --json
```

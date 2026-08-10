---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: yes
---

# TASK GRAPH

## Factory DB reconciliation snapshot
Verified read-only with `hermes factory status zeus-alpha-research-ledger-core --json` against Agent Core Factory DB (`db_backend=agent_core_postgres`, `database=zeus_agent`) and local Git inspection. The baseline ALR-010 task and ALR-010-R2 planning task are `done`; ALR-010-R1 and ALR-060 are terminal `superseded`. The bounded gate-708 recovery is independently accepted on substantive SHA `3e6c14f8aa368ec6e3623d16640bf4b558ce0c7a` by Factory gates 709 (spec), 710 (security) and 711 (quality); this marker commit records that evidence for canonical resolver consumption. ALR-020 is `ready` but remains held by the temporary manual takeover until resolve-state sees the committed markers. Factory events `173433` and `173494` record non-approval direct integrations of ALR-010-R1 commits to `main`; event `174440` records the later, project-local ALR-020 acceptance correction. None grants PR/QA approval, source/runtime authority, merge/deploy authority, or downstream implementation authority.

### Deterministic ALR-020 acceptance metadata reconciliation — completed/read back

Factory event `174440` at `2026-08-10T16:32:37.76002+00:00`, actor `zeus`, corrected the ALR-020 `acceptance_criteria` field through Agent Core Factory DB. The prior literal `Schema covers programs, sources, immutable evidence, alpha cards, lineage, reviews, cycles, bounded local sessions, result references, and inert handoff packages.` is absent on read-back. The exact current literal is `Schema covers programs, sources, immutable evidence, alpha cards, lineage, reviews, cycles, result references, inert handoff packages, and scheduler readiness only; collaboration session/message entities are excluded; bounded local normalized-evidence batches are intake, not sessions.` The event metadata records both literals, actor, reason, no-source-change and no-external-runtime-authority. This fixes the task-plan incompatibility without expanding v1; it is not a source change, QA Guardian approval, or permission to dispatch before the current G1 documentation candidate is independently reviewed.

### Observed ALR-010-R1 base-branch integrations — reconciliation record

- Factory evidence 1: event `173433`, `event_type=increment_integrated`, `increment_integration_method=merge_no_ff_push_origin`, `increment_integrated_by=implementation-planner`, `increment_integrated_at=2026-08-10T09:22:51.090409Z`, `increment_base_commit_before=00e7bb4ab0fcd9013ffa924ce6c5a8ae2c2ae2fc`, `increment_branch_commit=b9396bcd7d14ee6f212bd0fd0609e468cecf567f`, `increment_base_commit_after=e3d04ff94b67e6e21be1d5515bdb71400fbedf0a`.
- Factory evidence 2: event `173494`, `event_type=increment_integrated`, `increment_integration_method=merge_no_ff_push_origin`, `increment_integrated_by=implementation-planner`, `increment_integrated_at=2026-08-10T09:45:17.577998Z`, `increment_base_commit_before=e3d04ff94b67e6e21be1d5515bdb71400fbedf0a`, `increment_branch_commit=6ee8b4fdb886d0834bfbc62c7e152ee35d505e66`, `increment_base_commit_after=9f975acb0625750b8d46648766d1395c89392dca`.
- Git evidence: `git show --no-patch --pretty=format:'%H%n%P%n%s' e3d04ff94b67e6e21be1d5515bdb71400fbedf0a` identifies parents `00e7bb4ab0fcd9013ffa924ce6c5a8ae2c2ae2fc` and `b9396bcd7d14ee6f212bd0fd0609e468cecf567f`; `git show --no-patch --pretty=format:'%H%n%P%n%s' 9f975acb0625750b8d46648766d1395c89392dca` identifies parents `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a` and `6ee8b4fdb886d0834bfbc62c7e152ee35d505e66`; `git merge-base --is-ancestor` returns `0` for both branch commits against `origin/main`.
- Interpretation: the docs must not claim ALR-010-R1 is branch-only, unmerged, or unaffected by a second direct integration. Both merges remain non-approval evidence because gates 695/697 failed and no independent PASS/PR/QA Guardian evidence exists for the corrected R2 candidate.

| Task ID | Phase / status | Owner → reviewer | Depends on | Branch | Worktree |
|---|---|---|---|---|---|
| `zeus-alpha-research-ledger-core-alr-010-g1-rebaseline-and-local-ledger-c` | planning / done | implementation-planner → solution-architect | — | `factory/zeus-alpha-research-ledger-core/inc-010-alr-010-g1-rebaseline-and-local` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-010-alr-010-g1-rebaseline-and-local` |
| `zeus-alpha-research-ledger-core-alr-010-r1-bounded-g1-contract-rework` | planning / superseded | implementation-planner → solution-architect | gates 686/687 request-changes; gates 695/697 direct-integration findings | `factory/zeus-alpha-research-ledger-core/inc-010-alr-010-g1-rebaseline-and-local` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-010-alr-010-g1-rebaseline-and-local` |
| `zeus-alpha-research-ledger-core-alr-010-r2-pr-first-g1-merge-evidence-re` | planning / done | implementation-planner → solution-architect plus independent spec/security reviewers | gate 697 rework; later documentation reconciliation remains separate | `factory/zeus-alpha-research-ledger-core/inc-011-alr-010-r2-pr-first-g1-reconciliation` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-011-alr-010-r2-pr-first-g1-reconciliation` |
| `zeus-alpha-research-ledger-core-alr-020-agent-core-schema-and-dedicated-` | implementation / ready (held) | claude-builder → security-reviewer | current G1 documentation candidate requires fresh independent acceptance; Factory event 174440 read-back retained | `factory/zeus-alpha-research-ledger-core/inc-020-alr-020-agent-core-schema-and-de` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-020-alr-020-agent-core-schema-and-de` |
| `zeus-alpha-research-ledger-core-alr-030-research-ledger-json-tools-and-l` | implementation / todo | codex-builder → quality-reviewer | ALR-020 | `factory/zeus-alpha-research-ledger-core/inc-030-alr-030-research-ledger-json-too` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-030-alr-030-research-ledger-json-too` |
| `zeus-alpha-research-ledger-core-alr-040-source-provenance-adapters-and-r` | implementation / todo | claude-builder → quality-reviewer | ALR-030 | `factory/zeus-alpha-research-ledger-core/inc-040-alr-040-source-provenance-adapte` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-040-alr-040-source-provenance-adapte` |
| `zeus-alpha-research-ledger-core-alr-050-daily-research-cycle-and-inert-h` | implementation / todo | codex-builder → security-reviewer | ALR-030, ALR-040 | `factory/zeus-alpha-research-ledger-core/inc-050-alr-050-daily-research-cycle-and` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-050-alr-050-daily-research-cycle-and` |
| `zeus-alpha-research-ledger-core-alr-060-independent-quality-and-security` | quality_review / superseded | quality-reviewer → security-reviewer | ALR-020..050 | historical branch only | historical worktree only |
| `zeus-alpha-research-ledger-core-alr-061-independent-specification-and-ar` | quality_review / todo | product-analyst → solution-architect | ALR-020..050 | `factory/zeus-alpha-research-ledger-core/inc-060-alr-061-independent-specificatio` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-060-alr-061-independent-specificatio` |
| `zeus-alpha-research-ledger-core-alr-062-independent-quality-and-tdd-revi` | quality_review / todo | quality-reviewer → qa-verifier | ALR-020..050 | `factory/zeus-alpha-research-ledger-core/inc-061-alr-062-independent-quality-and` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-061-alr-062-independent-quality-and` |
| `zeus-alpha-research-ledger-core-alr-063-independent-security-and-no-egre` | security_review / todo | security-reviewer → factory-orchestrator | ALR-020..050 | `factory/zeus-alpha-research-ledger-core/inc-062-alr-063-independent-security-and` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-062-alr-063-independent-security-and` |
| `zeus-alpha-research-ledger-core-alr-070-live-local-db-and-tool-smoke-wit` | qa / todo | qa-verifier → quality-reviewer | ALR-061, ALR-062, ALR-063 | `factory/zeus-alpha-research-ledger-core/inc-070-alr-070-live-local-db-and-tool-s` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-070-alr-070-live-local-db-and-tool-s` |
| `zeus-alpha-research-ledger-core-alr-080-zeus-signed-pr-and-qa-guardian-h` | delivery / todo | factory-reporter → qa-verifier | ALR-070 | `factory/zeus-alpha-research-ledger-core/inc-080-alr-080-zeus-signed-pr-and-qa-gu` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-080-alr-080-zeus-signed-pr-and-qa-gu` |
| `zeus-alpha-research-ledger-core-reconcile-unvalidated-required-docs` | documentation / resolver-driven | factory-reporter → quality-reviewer | gate 708 rework passed gates 709/710/711; committed reviewed markers await canonical resolve-state | existing R2 PR branch | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-011-alr-010-r2-pr-first-g1-reconciliation` |

The last row is Factory-generated reconciliation for document-readiness drift. It resolves only when canonical resolve-state reads this committed marker transition, after which the manual takeover can release and the single-task Factory tick may dispatch ALR-020. The existing Zeus-signed `agent:zeus` PR #20 must remain visible; observed integrations 173433/173494 remain non-approval audit evidence.

## Review and delivery contract
- ALR-061 produces a distinct specification/architecture mapping for every requirement and boundary.
- ALR-062 produces distinct TDD/quality evidence.
- ALR-063 produces distinct security/least-privilege/no-egress evidence.
- ALR-070 may start only when all three exact review reports cite the candidate SHA and are accepted.
- ALR-010-R2 and future source increments must produce a Zeus-signed `agent:zeus` PR and QA Guardian/independent-review evidence before terminal closure. The observed ALR-010-R1 Factory direct integrations are recorded above as gate-695/gate-697 reconciliation evidence, not as a repeatable delivery path or implementation authority.
- The active documentation reconciliation corrects gate 708 findings and records event 174440; it does not implement ledger code, alter non-project Factory task metadata, perform another base merge, deploy or grant downstream implementation authority.
- ALR-020's bounded-local-sessions metadata reconciliation is now recorded and read back exactly in event 174440; this does not add a collaboration-session implementation task or remove the independent G1 review hold.

## Allowed reconciliation command
```bash
hermes factory status zeus-alpha-research-ledger-core --json
```

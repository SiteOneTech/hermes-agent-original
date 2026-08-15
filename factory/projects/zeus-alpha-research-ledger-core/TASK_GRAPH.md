---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: pending
---

# TASK GRAPH

## Factory DB reconciliation snapshot
Verified read-only during R2 with `hermes factory status zeus-alpha-research-ledger-core --json` against Agent Core Factory DB (`db_backend=agent_core_postgres`, `database=zeus_agent`) and local Git inspection. The baseline ALR-010 task is `done`; `ALR-010-R1` is the active bounded rework for gates 686/687 plus gate 695; `ALR-060` is terminal `superseded` and retained only as auditable history, not a live compatibility flow. Factory event `173433` records that ALR-010-R1 commit `b9396bcd7d14ee6f212bd0fd0609e468cecf567f` was integrated to `main` with `merge_no_ff_push_origin`, producing `origin/main` merge commit `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a`; `git merge-base --is-ancestor b9396bcd7d14ee6f212bd0fd0609e468cecf567f origin/main` returned success. This is an observed integration anomaly to reconcile, not PR/QA approval or downstream authority. Future non-terminal source tasks retain the Jean-authorized `increment_integration_waived` metadata and must not dispatch until the exact corrected SHA has independent reviews and the ALR-020 task-acceptance conflict below is fixed/read back.

### Required deterministic ALR-020 acceptance metadata reconciliation — blocking

The Factory DB currently records this ALR-020 acceptance literal: `Schema covers programs, sources, immutable evidence, alpha cards, lineage, reviews, cycles, bounded local sessions, result references, and inert handoff packages.` That conflicts with this deliberately bounded v1 contract, which excludes every collaboration session/message entity. This is a task-plan incompatibility, not permission to expand v1 and not a documentation-only waiver. Before ALR-020 implementation can start, the authorized Factory metadata owner must make and read back a deterministic correction on the ALR-020 task: remove the bounded-local-sessions acceptance clause and replace it with this exact scope statement: `v1 persists programs, sources, immutable evidence, cycles, cards, lineage, reviews, result references, inert handoffs, and scheduler readiness only; collaboration session/message entities are excluded; bounded local normalized-evidence batches are intake, not sessions.` The reconciliation evidence must record task ID, changed acceptance field, old/new literal values, actor/time, and read-back equality to this statement using the approved Factory control path. This R1 task does not alter Factory DB; normal implementation remains blocked until that evidence exists.

### Observed ALR-010-R1 base-branch integration — reconciliation record

- Factory evidence: event `173433`, `event_type=increment_integrated`, `increment_integration_method=merge_no_ff_push_origin`, `increment_integrated_by=implementation-planner`, `increment_integrated_at=2026-08-10T09:22:51.090409Z`, `increment_base_commit_before=00e7bb4ab0fcd9013ffa924ce6c5a8ae2c2ae2fc`, `increment_branch_commit=b9396bcd7d14ee6f212bd0fd0609e468cecf567f`, `increment_base_commit_after=e3d04ff94b67e6e21be1d5515bdb71400fbedf0a`.
- Git evidence: `git show --no-patch --pretty=fuller e3d04ff94b67e6e21be1d5515bdb71400fbedf0a` identifies a merge commit with parents `00e7bb4ab` and `b9396bcd7`; `git merge-base --is-ancestor b9396bcd7d14ee6f212bd0fd0609e468cecf567f origin/main` returns `0`.
- Interpretation: the docs must not claim ALR-010-R1 is branch-only or unmerged. The merge remains non-approval evidence because gate 695 failed and no independent PASS/PR/QA Guardian evidence exists for the corrected candidate.

### R2j PR #29 canonical-state repair

- Actual delivery candidate: SiteOneTech PR #29, still open at head `f61a7275048e2135b2b2729a1b9cdf8713c58866`, base branch `main`, base commit `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c`.
- Current canonical blocker: Agent Core Factory status still reports reconciliation anomaly `unvalidated_required_docs`; the live `document_status` read-back has G1 documents committed/indexed/validated but blocking because `reviewed=false` in the canonical source.
- Provenance correction: R2i gates are valid independent exact-SHA review evidence for PR #29, but their `already_ancestor` increment-integration metadata names the review-only R2i branch commit `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c`, not the PR #29 candidate `f61a7275048e2135b2b2729a1b9cdf8713c58866`. Do not treat that review-worktree attachment as a source merge.
- Handoff: QA Guardian / delivery evidence must bind PR #29 and `qa_guardian_evidence.candidate_commit` to `f61a7275048e2135b2b2729a1b9cdf8713c58866` before any terminal source-delivery conclusion. See `R2J_CANONICAL_STATE_REPAIR.md`.

### R2k stale canonical G1 provenance repair

- Stale active metadata: Agent Core project metadata still points `metadata.g1_documentation_checkout` to PR #20 / `dad375f27568c38be771fc597b579d087f034e1d` on branch `factory/zeus-alpha-research-ledger-core/inc-011-alr-010-r2-pr-first-g1-reconciliation`, with `not_merged=true` and reason `live_primary_checkout_cannot_be_fast_forwarded_while_Hermes_process_is_running`.
- Current R2j source state: PR #30 is `MERGED`, label `agent:zeus`, head `c1943efb2b97b54b42bc5eabe858340d8c391116`, merge commit `83d5ee06ba25859f047469baed223fe88e9467e3`. Agent Core event `188138` records the merge as performed by `factory-reviewer`, not by this R2k worker.
- Divergence to preserve for review: local primary `main` remains `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1` and `git merge-base --is-ancestor c1943efb2b97b54b42bc5eabe858340d8c391116 main` returned exit `1`, while remote `origin/main` is `83d5ee06ba25859f047469baed223fe88e9467e3` and contains R2j. Factory `document_status` still reads required G1 docs as `reviewed=false`, so no implementation dispatch is allowed.
- Renewal handoff: independent reviewers must inspect the exact R2k PR head SHA produced from `factory/zeus-alpha-research-ledger-core/inc-001-r2k-repair-stale-canonical-g1-re`; do not reuse PR #20/dad375f, PR #29/f61a, PR #30/c1943 or R2i `already_ancestor` metadata as review approval for this correction.

### R2m current-base G1 documentation PR recovery

- Current canonical base: `origin/main` fetched at `ab08b13669903a87b3d60d6c80231d23d6313782`; assigned branch `factory/zeus-alpha-research-ledger-core/inc-001-r2m-current-base-g1-documentatio` was initially equal to that base.
- Historical R2m candidate: the fresh R2m branch/PR head after that documentation-only recovery commit and push. R2n now supersedes it as the active review target.
- Incorporated repairs: `R2J_CANONICAL_STATE_REPAIR.md` and `R2K_STALE_CANONICAL_G1_PROVENANCE_REPAIR.md` remain indexed controlling artifacts, but PR #20/dad375f, PR #29/f61a, R2i `already_ancestor`, PR #30/c1943 and PR #31/73b exposure are historical only and cannot dispatch ALR-020.
- Boundary: R2m performs no product implementation, merge, deploy, credential change, direct SQL or external-runtime execution; required G1 docs remain `reviewed: pending`.

### R2n canonical-document validation repair

- Current canonical base: `origin/main` fetched at `df4c77fd1413a65cdb85885a06978ff157c1de4d`; assigned branch `factory/zeus-alpha-research-ledger-core/inc-034-r2n-repair-g1-canonical-document` was initially equal to that base.
- Active candidate: the fresh R2n branch/PR head after this documentation-only correction and push. Independent reviewers must bind PASS/REQUEST_CHANGES to that exact candidate SHA.
- Canonical Factory status: `agent_core_postgres:zeus_agent.factory` still reports `unvalidated_required_docs`; project `repo_path=/home/jean/Projects/hermes-agent-original` reads all 14 required G1 documents as `exists=true`, `indexed=true`, `committed=true`, `validated=true`, `reviewed=false`, `readiness_source=primary`.
- Concrete remaining technical cause: a docs-only branch cannot clear live `document_status` until a PR-first/QA Guardian or authorized metadata reconciliation path points Factory at the independently reviewed R2n exact head. Existing `metadata.g1_documentation_checkout` still names obsolete PR #20 / `dad375f27568c38be771fc597b579d087f034e1d` and is not accepted reviewed-candidate metadata.
- Boundary: R2n performs no product implementation, merge, deploy, credential change, direct SQL or external-runtime execution; required G1 docs remain `reviewed: pending`.

| Task ID | Phase / status | Owner → reviewer | Depends on | Branch | Worktree |
|---|---|---|---|---|---|
| `zeus-alpha-research-ledger-core-alr-010-g1-rebaseline-and-local-ledger-c` | planning / done | implementation-planner → solution-architect | — | `factory/zeus-alpha-research-ledger-core/inc-010-alr-010-g1-rebaseline-and-local` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-010-alr-010-g1-rebaseline-and-local` |
| `zeus-alpha-research-ledger-core-alr-010-r1-bounded-g1-contract-rework` | planning / running at R2 verification | implementation-planner → solution-architect | gates 686/687 request-changes; gate 695 merge-policy reconciliation | `factory/zeus-alpha-research-ledger-core/inc-010-alr-010-g1-rebaseline-and-local` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-010-alr-010-g1-rebaseline-and-local` |
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
| `zeus-alpha-research-ledger-core-r2j-repair-pr-29-g1-canonical-state-evid` | g1_review / done, historical evidence only | codex-builder → qa-verifier | R2i exact-SHA review evidence mismatch | `factory/zeus-alpha-research-ledger-core/inc-001-r2j-repair-pr-29-g1-canonical-st` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2j-repair-pr-29-g1-canonical-st` |
| `zeus-alpha-research-ledger-core-r2k-repair-stale-canonical-g1-review-pro` | documentation / done, historical evidence only | codex-builder → independent reviewer required | stale metadata PR #20/dad375f and non-dispatchable canonical G1 status | `factory/zeus-alpha-research-ledger-core/inc-001-r2k-repair-stale-canonical-g1-re` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2k-repair-stale-canonical-g1-re` |
| `zeus-alpha-research-ledger-core-r2m-current-base-g1-documentation-pr-rec` | documentation / blocked, historical handoff only | codex-builder → independent exact-SHA reviewer required | current-base recovery after R2j/R2k provenance repairs | `factory/zeus-alpha-research-ledger-core/inc-001-r2m-current-base-g1-documentatio` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2m-current-base-g1-documentatio` |
| `zeus-alpha-research-ledger-core-r2n-repair-g1-canonical-document-validat` | documentation / claimed | codex-builder → quality-reviewer | active canonical-document status repair and exact-SHA handoff | `factory/zeus-alpha-research-ledger-core/inc-034-r2n-repair-g1-canonical-document` | `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-034-r2n-repair-g1-canonical-document` |

The reconciliation/documentation rows are audit and handoff rows for document-readiness drift. They cannot close an implementation gate by themselves; ALR-010-R1 still requires exact-SHA independent review evidence and explicit handling of the observed integration anomaly before downstream implementation starts.

## Review and delivery contract
- ALR-061 produces a distinct specification/architecture mapping for every requirement and boundary.
- ALR-062 produces distinct TDD/quality evidence.
- ALR-063 produces distinct security/least-privilege/no-egress evidence.
- ALR-070 may start only when all three exact review reports cite the candidate SHA and are accepted.
- Future source increments must produce a Zeus-signed `agent:zeus` PR and QA Guardian merge evidence before terminal closure. The observed ALR-010-R1 Factory direct integration is recorded above as gate-695 reconciliation evidence, not as a repeatable delivery path or implementation authority.
- R2j adds an explicit guard for review-only branches: an `already_ancestor` record on a reviewer worktree is never proof that the PR candidate it reviewed is merged; source-delivery evidence must bind to the PR head commit.
- R2k adds an explicit guard for stale active metadata: `metadata.g1_documentation_checkout` naming PR #20 / `dad375f27568c38be771fc597b579d087f034e1d` is obsolete and cannot be used to dispatch ALR-020. After PR #31/R2k reached `origin/main`, R2k is historical repair evidence rather than the active review target.
- R2m superseded R2k after current-base recovery, but R2n now supersedes R2m as the active review target: the next valid review target is the exact SHA on the R2n Zeus-signed `agent:zeus` PR based on `origin/main` `df4c77fd1413a65cdb85885a06978ff157c1de4d`; R2k/PR #31 and R2m are historical evidence only.
- ALR-010-R1 resolves only the documentation findings from failed gates 686/687 and the merge-evidence documentation finding from gate 695. It does not implement ledger code, alter Factory task metadata, open a PR, perform another merge, deploy or grant downstream implementation authority.
- ALR-020 additionally may not start until the required bounded-local-sessions metadata reconciliation above is recorded and read back exactly; it does not add a collaboration-session implementation task.

## Allowed reconciliation command
```bash
hermes factory status zeus-alpha-research-ledger-core --json
```

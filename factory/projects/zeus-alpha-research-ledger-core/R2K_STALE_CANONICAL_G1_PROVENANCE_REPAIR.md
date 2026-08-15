---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2k-repair-stale-canonical-g1-review-pro
phase: documentation
status: stale_g1_provenance_repaired
validated: yes
reviewed: pending_independent_exact_sha
owner: codex-builder
---

# R2k stale canonical G1 review provenance repair

## Scope

This is a bounded project-local documentation/provenance repair. It reconciles the stale Factory metadata pointer, live Git PR state, local main-reference state and current G1 document-readiness blocker evidence so a renewed independent exact-SHA review can be dispatched.

This artifact does not mark any required G1 document `reviewed: yes`, does not self-approve, does not merge, does not deploy, does not change credentials, does not write direct SQL, does not alter external runtimes and does not authorize ALR-020 or later implementation.

## Read-only evidence reproduced

Evidence was reproduced from the assigned isolated worktree `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2k-repair-stale-canonical-g1-re` at `2026-08-15T20:01:36Z`.

### Git / GitHub state

- Assigned worktree branch: `factory/zeus-alpha-research-ledger-core/inc-001-r2k-repair-stale-canonical-g1-re`.
- Assigned worktree `HEAD` before this repair: `83d5ee06ba25859f047469baed223fe88e9467e3`; local `origin/main` ref also `83d5ee06ba25859f047469baed223fe88e9467e3`.
- Local primary `main` ref remains `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`; `git merge-base --is-ancestor c1943efb2b97b54b42bc5eabe858340d8c391116 main` returned exit `1`, so that local primary main ref does not contain the R2j repair commit.
- Remote read-back with `git ls-remote origin refs/heads/main refs/pull/29/head refs/pull/29/merge refs/pull/20/head refs/pull/20/merge 'refs/heads/factory/zeus-alpha-research-ledger-core/*'` returned:
  - `refs/heads/main` = `83d5ee06ba25859f047469baed223fe88e9467e3`.
  - R2j branch `factory/zeus-alpha-research-ledger-core/inc-001-r2j-repair-pr-29-g1-canonical-st` = `c1943efb2b97b54b42bc5eabe858340d8c391116`.
  - PR #30 is `MERGED`, head `c1943efb2b97b54b42bc5eabe858340d8c391116`, merge commit `83d5ee06ba25859f047469baed223fe88e9467e3`, label `agent:zeus`.
  - PR #29 remains `OPEN`, head `f61a7275048e2135b2b2729a1b9cdf8713c58866`, base `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c`, label `agent:zeus`.
  - PR #20 head is `5ed1e28f7030af6a01cdb911cef2e5f2740c8777`; historical Factory metadata below still points to PR #20 / `dad375f27568c38be771fc597b579d087f034e1d`, not to the current renewal path.
- Agent Core Factory event `188138` records an already-completed integration by `factory-reviewer`: branch commit `c1943efb2b97b54b42bc5eabe858340d8c391116` into base `main`, base before `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c`, base after `83d5ee06ba25859f047469baed223fe88e9467e3`, method `merge_no_ff_push_origin`, timestamp `2026-08-15T19:45:34.16605+00:00`. R2k did not perform that merge.

### Agent Core Factory state

- `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json` returned canonical backend `agent_core_postgres:zeus_agent.factory` and project anomaly `unvalidated_required_docs`.
- Project metadata still carries stale `metadata.g1_documentation_checkout`:
  - `branch=factory/zeus-alpha-research-ledger-core/inc-011-alr-010-r2-pr-first-g1-reconciliation`
  - `commit=dad375f27568c38be771fc597b579d087f034e1d`
  - `pr_url=https://github.com/SiteOneTech/hermes-agent-original/pull/20`
  - `not_merged=true`
  - `reason=live_primary_checkout_cannot_be_fast_forwarded_while_Hermes_process_is_running`
- Current project `document_status` read-back from the primary source still reports `docs_ready=false`. Every required G1 document in the primary source is `exists=true`, `indexed=true`, `committed=true`, `validated=true`, `reviewed=false`; therefore G1 remains non-dispatchable. The prompt snapshot named ten blockers, while this live full status read-back showed the conservative superset: all 14 required G1 documents are not reviewed in the primary source. In either interpretation, there is no valid implementation dispatch.

## Corrected provenance interpretation

1. `metadata.g1_documentation_checkout` is stale. It points to PR #20 / `dad375f27568c38be771fc597b579d087f034e1d` and must not be used as the current G1 renewal candidate.
2. R2i/R2f exact-SHA reviews for PR #29 remain historical evidence for PR #29 head `f61a7275048e2135b2b2729a1b9cdf8713c58866`, but they do not review this R2k correction and do not prove canonical Factory status is reconciled.
3. R2j repair commit `c1943efb2b97b54b42bc5eabe858340d8c391116` was delivered through PR #30 and is now present in remote `origin/main` via merge commit `83d5ee06ba25859f047469baed223fe88e9467e3`; the local primary `main` ref and Factory metadata/status are still stale relative to that remote state.
4. The next dispatchable review target is the Zeus-signed `agent:zeus` PR created from this R2k branch. Independent reviewers must review the exact R2k PR head SHA after push, not PR #20/dad375f, not the PR #29/f61a candidate and not any review-worktree `already_ancestor` attachment.

## Renewal handoff for independent reviewer

A renewed independent quality/spec/security reviewer can verify this correction by rerunning these commands from the assigned worktree or a fresh checkout:

1. `git rev-parse main` and `git merge-base --is-ancestor c1943efb2b97b54b42bc5eabe858340d8c391116 main; echo $?` to confirm the local primary `main` ref still does not contain R2j.
2. `git ls-remote origin refs/heads/main refs/pull/20/head refs/pull/29/head refs/pull/30/head refs/heads/factory/zeus-alpha-research-ledger-core/inc-001-r2j-repair-pr-29-g1-canonical-st` to verify remote/source refs.
3. `gh pr view 30 --repo SiteOneTech/hermes-agent-original --json number,state,headRefOid,mergeCommit,labels,url` to verify R2j was merged as PR #30 at exact head `c1943efb2b97b54b42bc5eabe858340d8c391116`.
4. `gh pr view <R2K_PR_NUMBER> --repo SiteOneTech/hermes-agent-original --json number,state,headRefOid,baseRefOid,labels,url` to bind the renewed review to the exact R2k correction SHA.
5. `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json` to confirm whether `metadata.g1_documentation_checkout` and `document_status` have been reconciled after this PR.

The renewed reviewer must record PASS/REQUEST_CHANGES against the exact R2k PR head SHA. This worker deliberately leaves every G1 `reviewed` field pending/false and records only implementation evidence.

## Dispatch hold

No normal ALR-020 implementation may dispatch until all of the following are true and read back from Agent Core Factory/Git evidence:

- the project-local G1 pack has independent PASS review evidence against the exact current candidate SHA;
- `metadata.g1_documentation_checkout` no longer points to obsolete PR #20 / `dad375f27568c38be771fc597b579d087f034e1d` as the active renewal source;
- canonical `document_status` reports no required G1 blockers for `reviewed=false`;
- PR-first / QA Guardian evidence binds the reviewed candidate SHA to the accepted source state;
- no reviewer relies on stale R2i `already_ancestor` metadata, stale local `main` state, or a historical PASS from PR #20/PR #29.

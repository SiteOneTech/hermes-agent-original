---
document_type: fail_closed_integration_readback
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2cy-r3-successor-integrate-r2da-r2-pr-1
run_id: run-1787295994-bfc9f859
phase: g1_recovery
status: blocked_pr_114_not_mergeable
validated: yes
reviewed: pending
owner: codex-builder
engine: codex
base_ref: origin/main
base_sha: eb3e3ff48905285812eca4c222fa2155a9282546
branch: factory/zeus-alpha-research-ledger-core/inc-017-r2cy-r3-successor-integrate-r2da
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2cy-r3-successor-integrate-r2da
created_at_utc: 2026-08-21T07:13:33Z
---

# R2cy-R3 successor integrate R2da — fail-closed readback

## Scope and boundary

This run was assigned to integrate the R2da-R2 dispatch repair PR #114 and then
catch up the primary checkout runtime so docs-first G1 exact-SHA review dispatch
can claim the R2cy-R1 review task without `missing_or_unindexed_docs` or
`unresolved_validation_tasks` denials.

The integration did not proceed because the live precondition in the acceptance
criteria failed: PR #114 is no longer mergeable against current `origin/main`.
Per the no-auto-merge contract, a conflicting PR is not merged, force-updated,
rebased, or treated as current reviewed evidence.

No product implementation, deployment, credential change, external runtime,
direct SQL, ALR-020/product dispatch, primary checkout mutation, or stale PR/ref
mutation was performed. The only Factory DB write recorded for this run is the
sanctioned `factory gate record` fail-closed evidence.

## Documents consulted

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/TRACKER.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2CY_R2_G1_REVIEW_ROUTE_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2CY_R3_DOCS_FIRST_G1_EXACT_SHA_REVIEW_DISPATCH_RECOVERY.md`
- `factory/projects/zeus-alpha-research-ledger-core/R2V_CANONICAL_G1_STATUS_AND_NO_AUTO_MERGE_REPAIR.md`

## Read-only evidence

### Assigned worktree/current base

Command:

```text
git fetch origin main --prune && git rev-parse HEAD && git rev-parse origin/main && git merge-base HEAD origin/main && git rev-list --left-right --count HEAD...origin/main
```

Readback:

```text
HEAD        = eb3e3ff48905285812eca4c222fa2155a9282546
origin/main = eb3e3ff48905285812eca4c222fa2155a9282546
merge-base  = eb3e3ff48905285812eca4c222fa2155a9282546
ahead/behind= 0 0
branch      = factory/zeus-alpha-research-ledger-core/inc-017-r2cy-r3-successor-integrate-r2da
```

### Canonical Factory status

Command:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2cy-r3-successor-status-before.json
```

Readback from `/tmp/r2cy-r3-successor-status-before.json`:

- `db_backend=agent_core_postgres`.
- Active project metadata: `reconciliation_anomalies=[]`,
  `reconciliation_projection_source=current_document_status`.
- 14/14 G1-required rows have `exists=true`, `committed=true`, `indexed=true`,
  `validated=true`, `reviewed=true`, `blocking=false`,
  `readiness_source=configured_base_ref`, `base_commit=eb3e3ff48905285812eca4c222fa2155a9282546`.
- Stale primary checkout rows are rejected with
  `primary_checkout_accepted=false`,
  `primary_checkout_rejected_reason=primary_checkout_not_configured_base`.
- `zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re`
  remains `status=ready`.
- Superseded rows R2h/R2ai/R2l/R2g/ALR-060 remain terminal history; blocked
  R2ae-R1/R2ae-bounded/R2ac remain fail-closed history, not current
  requirements.

### PR #114 GitHub readback

Command:

```text
GH_REPO=SiteOneTech/hermes-agent-original gh pr view 114 --json number,state,isDraft,headRefOid,headRefName,baseRefName,author,labels,mergeable,mergeStateStatus,url,title
```

Readback:

```text
number=114
state=OPEN
isDraft=false
author=sitiouno
labels=[agent:zeus]
headRefOid=fe0b6f80bfad296f78d3ab9a6ac79a31298bb243
headRefName=factory/zeus-alpha-research-ledger-core/inc-001-r2da-r2-repair-docs-first-valida
baseRefName=main
mergeable=CONFLICTING
mergeStateStatus=DIRTY
url=https://github.com/SiteOneTech/hermes-agent-original/pull/114
```

This fails the acceptance criterion that PR #114 be `MERGEABLE` against current
`origin/main` before integration.

### PR #114 gate readback

Canonical Factory status contains both current PR #114 gates:

- Gate `1025`: `implementation` `passed`, reviewer `codex-builder`, task
  `zeus-alpha-research-ledger-core-r2da-r2-repair-docs-first-validation-dea`,
  notes bind PR #114 head `fe0b6f80bfad296f78d3ab9a6ac79a31298bb243` and the
  R2da-R2 focused/related tests.
- Gate `1026`: `quality` `passed`, reviewer `quality-reviewer`, same task,
  notes bind the same exact PR #114 head and independent exact-SHA review.

Those gates are valid for the exact PR head, but they do not override the live
mergeability failure against current `origin/main`.

### Local merge simulation

Command:

```text
git fetch origin pull/114/head:refs/remotes/origin/pr/114 --force
git merge-tree --write-tree origin/main refs/remotes/origin/pr/114
```

Readback: exit `1`; conflicts are in project-local documentary files only:

```text
CONFLICT (content): Merge conflict in factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md
CONFLICT (content): Merge conflict in factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md
CONFLICT (content): Merge conflict in factory/projects/zeus-alpha-research-ledger-core/TRACKER.md
```

Code/test files from PR #114 (`hermes_cli/factory_pg.py` and
`tests/hermes_cli/test_factory_increment_integration.py`) auto-merge in the
simulation, but the PR as a whole is not clean/mergeable. A conflict-resolution
or current-base successor would require a new exact head and a fresh independent
review before integration.

### Primary checkout/runtime catch-up

Readback:

```text
git -C /home/jean/Projects/hermes-agent-original status --short --branch
## main...origin/main [ahead 4, behind 2816]
primary_head=ac1fdb16051324c490d803b14dd06efffd6f9ad0
primary_origin_main=eb3e3ff48905285812eca4c222fa2155a9282546
primary_ahead_behind=4 2816
```

The primary checkout was not modified. Runtime catch-up was not attempted
because the PR integration precondition failed first and the hard worker rules
also prohibit mutating the primary checkout outside explicit successful scope.

## Fail-closed result

The requested merge/integration and subsequent tick/claim verification were not
executed. The remaining dependency is one of:

1. rebase or otherwise resolve PR #114 against current `origin/main`, producing a
   new exact PR head and fresh independent quality gate; or
2. create a current-base successor on the assigned Factory path that ports the
   R2da-R2 dispatch predicate/test fix, records RED/GREEN evidence, opens a
   Zeus-signed `agent:zeus` PR, and receives independent exact-SHA review.

Only after that reviewed current-base integration may the primary checkout
runtime be caught up and the R2cy-R1 claim/tick readback be used as closure
evidence.

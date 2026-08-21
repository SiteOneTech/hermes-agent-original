---
document_type: fresh_g1_source_root_frontmatter_readback_repair
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2cy-r6-fresh-g1-source-root-frontmatter
run_id: run-1787317093-baf0203a
phase: documentation
status: implemented_pending_pr_and_independent_review
validated: yes
reviewed: pending
owner: codex-builder
engine: codex
base_ref: origin/main
base_sha: 59199c93dcb3c717997158213ef485847541992e
branch: factory/zeus-alpha-research-ledger-core/inc-001-r2cy-r6-fresh-g1-source-root-fro
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2cy-r6-fresh-g1-source-root-fro
created_at_utc: 2026-08-21T13:09:35Z
---

# R2cy-R6 — fresh G1 source-root frontmatter/readback repair

## Scope and boundary

This increment is a documentation/evidence-only repair for the persistent
`unvalidated_required_docs` projection. It does not change Factory parser code,
Factory runtime code, Alpha Ledger product/runtime code, providers, migrations,
tools, schedulers, credentials, messaging connectors, deployment behavior,
trading/risk/paper/live behavior, the primary checkout, G1 reviewed frontmatter,
stale refs/PRs, task status, or Factory DB state outside the sanctioned
`factory status` / `factory gate record` CLI surfaces.

Agent Core Postgres `factory.*` remains the source of truth. Notion and stale
prompt summaries are audit/projection context only.

## G1 documents and project evidence read

Required entry point and G1/project evidence read before editing:

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/REQUIREMENTS_ANALYSIS.md`
- `factory/projects/zeus-alpha-research-ledger-core/REQUIREMENTS_TRACEABILITY.md`
- `factory/projects/zeus-alpha-research-ledger-core/PRD.md`
- `factory/projects/zeus-alpha-research-ledger-core/ADRS.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/SPRINT_PLAN.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/G1_REVIEW.md`
- Predecessor/readback artifacts indexed in `DOCUMENTATION_INDEX.md`, especially
  `R2CY_R5_FAIL_CLOSED_PRIMARY_RUNTIME_AND_TERMINALIZATION_RECOVERY.md`,
  `R2EA_DOCS_FIRST_STALE_RUNTIME_DISPATCH_PROVENANCE_REPAIR.md`,
  `R2DF_R1_DOCS_FIRST_G1_RECOVERY_DISPATCH_ROUTING_REPAIR.md`,
  `R2CY_R3_DOCS_FIRST_G1_EXACT_SHA_REVIEW_DISPATCH_RECOVERY.md`,
  `R2CY_R3_SUCCESSOR_CURRENT_BASE_R2DA_DISPATCH_REPAIR.md`, and
  `R6_SOURCE_INCREMENT_INTEGRATION_RECONCILIATION.md`.

## Current-origin worktree identity

Read-only Git evidence after `git fetch origin main --prune`, before project docs
were edited:

```text
worktree    = /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2cy-r6-fresh-g1-source-root-fro
branch      = factory/zeus-alpha-research-ledger-core/inc-001-r2cy-r6-fresh-g1-source-root-fro
remote      = https://github.com/SiteOneTech/hermes-agent-original.git
HEAD        = 59199c93dcb3c717997158213ef485847541992e
origin/main = 59199c93dcb3c717997158213ef485847541992e
merge-base  = 59199c93dcb3c717997158213ef485847541992e
ahead/behind= 0 0
factory_pg_parser_blob = 0c7ebe6f6af5084c561aa115bd38a8816bfaaca6
```

The primary checkout `/home/jean/Projects/hermes-agent-original` was not mutated.
The current status rows still record the stale primary checkout as rejected:
`primary_checkout_accepted=false`,
`primary_checkout_rejected_reason=primary_checkout_not_configured_base`, and
`primary_head=ac1fdb16051324c490d803b14dd06efffd6f9ad0`.

## Parser/frontmatter contract reconciled

The current parser/runtime version for this readback is the worktree source at
`59199c93dcb3c717997158213ef485847541992e` with parser source blob
`0c7ebe6f6af5084c561aa115bd38a8816bfaaca6` for
`hermes_cli/factory_pg.py`.

The actual contract read from `hermes_cli/factory_pg.py` is:

- `factory_pg.py:2005-2006` defines true values including `yes`, `validated`,
  `reviewed`, and `approved`, and false values including `pending`,
  `unvalidated`, and `unreviewed`.
- `factory_pg.py:2014-2043` requires top-of-file YAML frontmatter (`---` as the
  first line), scans only the frontmatter window before the closing `---`, and
  treats an explicit pending/unvalidated/unreviewed frontmatter marker as
  fail-closed.
- `factory_pg.py:2066-2078` checks metadata first, then the YAML frontmatter flag,
  then narrow status-table/index declarations. Later body prose that quotes stale
  `reviewed: pending` text does not override current reviewed frontmatter.

No parser behavior defect was reproduced in this current-origin worktree. The
frontmatter contract and the current Agent Core status rows already make the
assignment's ten `missing=reviewed` rows non-blocking when read from the
configured-base source root.

## Canonical Agent Core status readback

Sanctioned command, executed from the assigned worktree with the canonical venv:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main \
  factory status zeus-alpha-research-ledger-core --json \
  > /tmp/r2cy-r6-status-after-docs.json
```

Parsed readback:

```text
file=/tmp/r2cy-r6-status-after-docs.json bytes=4316285
db_backend=agent_core_postgres database=zeus_agent
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2cy-r6-fresh-g1-source-root-fro
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2cy-r6-fresh-g1-source-root-fro delegated=False
g1_required=14 blocking=0
active_reconciliation_anomalies=['unvalidated_required_docs'] reconciliation_required=True
```

Current row-level readback for the ten rows named by the task prompt:

| Prompt row | Current `document_status` readback |
|---|---|
| `FACTORY_INTAKE.md` | `blocking=false`, `reviewed=true`, `validated=true`, `indexed=true`, `committed=true`, `exists=true`, `readiness_source=configured_base_ref`, `base_commit=59199c93dcb3c717997158213ef485847541992e` |
| `REQUIREMENTS_ANALYSIS.md` | `blocking=false`, `reviewed=true`, `validated=true`, `indexed=true`, `committed=true`, `exists=true`, `readiness_source=configured_base_ref`, `base_commit=59199c93dcb3c717997158213ef485847541992e` |
| `PATTERN_ANALYSIS.md` | `blocking=false`, `reviewed=true`, `validated=true`, `indexed=true`, `committed=true`, `exists=true`, `readiness_source=configured_base_ref`, `base_commit=59199c93dcb3c717997158213ef485847541992e` |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | `blocking=false`, `reviewed=true`, `validated=true`, `indexed=true`, `committed=true`, `exists=true`, `readiness_source=configured_base_ref`, `base_commit=59199c93dcb3c717997158213ef485847541992e` |
| `PRD.md` | `blocking=false`, `reviewed=true`, `validated=true`, `indexed=true`, `committed=true`, `exists=true`, `readiness_source=configured_base_ref`, `base_commit=59199c93dcb3c717997158213ef485847541992e` |
| `ADRS.md` | `blocking=false`, `reviewed=true`, `validated=true`, `indexed=true`, `committed=true`, `exists=true`, `readiness_source=configured_base_ref`, `base_commit=59199c93dcb3c717997158213ef485847541992e` |
| `METHODOLOGY_PLAN.md` | `blocking=false`, `reviewed=true`, `validated=true`, `indexed=true`, `committed=true`, `exists=true`, `readiness_source=configured_base_ref`, `base_commit=59199c93dcb3c717997158213ef485847541992e` |
| `TECHNICAL_BLUEPRINT.md` | `blocking=false`, `reviewed=true`, `validated=true`, `indexed=true`, `committed=true`, `exists=true`, `readiness_source=configured_base_ref`, `base_commit=59199c93dcb3c717997158213ef485847541992e` |
| `TASK_GRAPH.md` | `blocking=false`, `reviewed=true`, `validated=true`, `indexed=true`, `committed=true`, `exists=true`, `readiness_source=configured_base_ref`, `base_commit=59199c93dcb3c717997158213ef485847541992e` |
| `SECURITY_GATES.md` | `blocking=false`, `reviewed=true`, `validated=true`, `indexed=true`, `committed=true`, `exists=true`, `readiness_source=configured_base_ref`, `base_commit=59199c93dcb3c717997158213ef485847541992e` |

The same readback also reports the remaining four required G1 rows
`SPRINT_PLAN.md`, `TRACKER.md`, `DOCUMENTATION_INDEX.md`, and `QA_GATES.md` as
non-blocking with `reviewed=true` and `validated=true`, for a total of 14/14
required G1 rows non-blocking.

Historical `blocking_count=10` snapshots still exist inside old gate/event audit
history in the status payload, including a failed critical-readiness gate snapshot
at `/tmp/r2cy-r6-status-after-docs.json` line `14121` and additional old
snapshots at lines `16033`, `16395`, and `22038`. Those rows are not the current
project `document_status` source. They are stale projection/audit evidence and
must not override the current top-level configured-base rows above.

## Resolve-state/readback boundary

This assignment's hard DB rule authorizes only `factory status` and
`factory gate record`. `factory project resolve-state` was therefore **not** run
for R2cy-R6, because that subcommand can mutate Factory reconciliation state and
is outside this run's allowed Factory DB surface. The required non-mutating
readback is the sanctioned `factory status` payload above, which identifies the
source root, parser/runtime source version, stale-primary rejection reason, and
each G1 row.

## Deterministic validation artifact

Project-local validator added:

```text
factory/projects/zeus-alpha-research-ledger-core/validate_r2cy_r6_g1_readback.py
```

Command:

```text
python3 factory/projects/zeus-alpha-research-ledger-core/validate_r2cy_r6_g1_readback.py \
  /tmp/r2cy-r6-status-after-docs.json
```

Result:

```text
R2cy-R6 G1 readback validation: PASS
repo_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2cy-r6-fresh-g1-source-root-fro
runtime_head=59199c93dcb3c717997158213ef485847541992e
configured_base_origin_main=59199c93dcb3c717997158213ef485847541992e
merge_base=59199c93dcb3c717997158213ef485847541992e
factory_pg_parser_blob=0c7ebe6f6af5084c561aa115bd38a8816bfaaca6
status_json=/tmp/r2cy-r6-status-after-docs.json bytes=4316285
db_backend=agent_core_postgres database=zeus_agent
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2cy-r6-fresh-g1-source-root-fro
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2cy-r6-fresh-g1-source-root-fro delegated=False
g1_required=14 blocking=0 prompt_stale_ten_now_nonblocking=10
project_reconciliation_anomalies=['unvalidated_required_docs']
```

## Delivery and review handoff

R2cy-R6 remains PR-first. The branch must be pushed normally to the assigned
remote branch and opened as a non-draft GitHub PR against `main` with label
`agent:zeus`, Zeus `Signed-off-by`, exact final head SHA in the PR body, and a
Factory implementation gate note. This worker records implementation evidence
only and must not self-approve, merge, deploy, mutate the primary checkout,
change credentials, execute external runtimes, write direct SQL, or dispatch
ALR product/trading work.

Independent exact-SHA quality review by a distinct reviewer is required before
this artifact or task can be represented as `reviewed: yes`.

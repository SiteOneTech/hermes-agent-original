# R2ck — Canonical G1 origin/main and PR #68 Delivery Reconciliation

## Purpose

Bounded technical recovery for the active `unvalidated_required_docs` preflight.
Reconciles the current Agent Core Factory `document_status` against immutable
local Git evidence: `origin/main` = `b260baea223e863b35fe561e6c5d3d77f3a914c9`
and the existing R2c candidate = `be56899668acd3bf89503a9fb57d6fef35dcd2dd`.

This is documentation/reconciliation only: no ALR-020 dispatch, no direct merge
or modification of main/PRs, no primary-checkout mutation, no direct SQL, no
credential access, no runtime/connector/messaging action, and no
trading/risk/paper/live activation.

## 1. Worktree identity (immutable, captured before edits)

- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-000-r2ck-canonical-g1-origin-main-an`
- Branch: `factory/zeus-alpha-research-ledger-core/inc-000-r2ck-canonical-g1-origin-main-an`
- HEAD before edits: `b260baea223e863b35fe561e6c5d3d77f3a914c9` (== `origin/main`)
- `git status`: clean; `git log --oneline -1`: `b260baea22 Merge Factory increment zeus-alpha-research-ledger-core-r2bj-bounded-canonical-g1-documentation- into main`
- Remote: `https://github.com/SiteOneTech/hermes-agent-original.git`

## 2. Local Git containment of the R2c candidate (acceptance criterion 2)

- `git merge-base --is-ancestor be56899668acd3bf89503a9fb57d6fef35dcd2dd b260baea223e863b35fe561e6c5d3d77f3a914c9` → exit **1** ⇒ **R2c candidate is NOT contained in `origin/main`**.
- `git merge-base be56899 b260baea` → `b260baea223e863b35fe561e6c5d3d77f3a914c9`; `git merge-base --is-ancestor b260baea be56899` → exit 0 ⇒ candidate is exactly **1 commit ahead** of `origin/main` (directly on top, docs-only).
- `git log --oneline b260baea..be56899` → `be56899668 docs(factory): recover current-origin G1 review evidence`.
- `git show --stat be56899` → 7 files, +230/−2: `DOCUMENTATION_INDEX.md`, `G1_REVIEW.md`, `QA_GATES.md`, new `R2C_TECHNICAL_REWORK_CURRENT_ORIGIN_G1_INDEPENDENT_REVIEW.md`, `SECURITY_GATES.md`, `TASK_GRAPH.md`, `TRACKER.md`. Author `Zeus <zeus@sitiouno.com>`, `Signed-off-by: Zeus`.
- GitHub readback (`gh pr view 68 --json ...`): PR #68 `https://github.com/SiteOneTech/hermes-agent-original/pull/68` — **OPEN**, non-draft, label `agent:zeus`, base `main`, head branch `factory/zeus-alpha-research-ledger-core/inc-001-r2c-technical-rework-current-ori`, head OID `be56899668acd3bf89503a9fb57d6fef35dcd2dd`, `mergedAt: null`, `reviews: []`, `reviewDecision: ""`, `checks: []`.
- Conclusion: PR #68 is the **unintegrated R2c delivery**. Per task contract, an unintegrated candidate or historical gate is NOT current readiness.

## 3. Canonical Factory status readback (acceptance criterion 1)

Command (allowed Factory CLI only, run from the assigned worktree):

```
cd /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-000-r2ck-canonical-g1-origin-main-an
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2ck-status.json
```

Key payload facts (2,532,965 bytes; exit 0):

- `db_backend: agent_core_postgres`; `factory_cli_source_root` / `factory_status_source_root` = the assigned worktree; `factory_status_delegated: false`.
- `document_status`: **22 rows**; all **14 `g1_required` rows** report `exists/committed/indexed/validated/reviewed = true`, `blocking = false`, `readiness_source = configured_base_ref`, `base_commit = b260baea223e863b35fe561e6c5d3d77f3a914c9`, `configured_base_ref_accepted = true`, `primary_checkout_accepted = false` (`primary_checkout_not_configured_base`, primary head `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`).
- Active project metadata: `reconciliation_anomalies: []`, `reconciliation_projection_source: current_document_status`, `reconciliation_required: false`, `cleared_g1_document_reconciliation_projection: true`, `cleared_project_metadata_keys: ["g1_documentation_checkout"]`, `qa_guardian_required: true`, `pr_first_required: true`, `factory_auto_integration_forbidden: true`, `technical_hold: true`, `notion_required: false`.
- Gates: latest for the R2c delivery — gate 888 `implementation` passed (claude-builder), gate 889 `security` passed (security-reviewer). No QA Guardian/independent delivery approval exists for PR #68.

### 3.1 Row-level comparison of the dispatch snapshot vs. immutable Git content

Dispatch-time snapshot embedded in the R2ck task context claimed 10 required docs
BLOCKED `missing=reviewed`: `FACTORY_INTAKE.md`, `REQUIREMENTS_ANALYSIS.md`,
`PATTERN_ANALYSIS.md`, `ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, `PRD.md`, `ADRS.md`,
`METHODOLOGY_PLAN.md`, `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`,
`SECURITY_GATES.md`; and 4 READY: `SPRINT_PLAN.md`, `TRACKER.md`,
`DOCUMENTATION_INDEX.md`, `QA_GATES.md`.

| Doc | origin/main content (worktree HEAD) | Primary checkout content (stale `4eb87e4cd4`) | Current canonical row |
|---|---|---|---|
| FACTORY_INTAKE.md | `validated: yes`, `reviewed: yes` (gate 794 / PR #36 `c8154706…`) | `reviewed: pending` | `blocking=false`, `reviewed=true` |
| REQUIREMENTS_ANALYSIS.md | same | `reviewed: pending` | `blocking=false`, `reviewed=true` |
| PATTERN_ANALYSIS.md | same | `reviewed: pending` | `blocking=false`, `reviewed=true` |
| ASSUMPTIONS_AND_OPEN_QUESTIONS.md | same | `reviewed: pending` | `blocking=false`, `reviewed=true` |
| PRD.md | same | `reviewed: pending` | `blocking=false`, `reviewed=true` |
| ADRS.md | same | `reviewed: pending` | `blocking=false`, `reviewed=true` |
| METHODOLOGY_PLAN.md | same | `reviewed: pending` | `blocking=false`, `reviewed=true` |
| TECHNICAL_BLUEPRINT.md | same | `reviewed: pending` | `blocking=false`, `reviewed=true` |
| TASK_GRAPH.md | same | `reviewed: pending` | `blocking=false`, `reviewed=true` |
| SECURITY_GATES.md | same | `reviewed: pending` | `blocking=false`, `reviewed=true` |
| SPRINT_PLAN.md | `reviewed: yes` | `reviewed: pending` | `blocking=false`, `reviewed=true` |
| TRACKER.md | `reviewed: yes` | `reviewed: pending` | `blocking=false`, `reviewed=true` |
| DOCUMENTATION_INDEX.md | `reviewed: yes` | `reviewed: pending` | `blocking=false`, `reviewed=true` |
| QA_GATES.md | `reviewed: yes` | `reviewed: pending` | `blocking=false`, `reviewed=true` |

Primary-checkout scan: `grep -l "^reviewed: pending" factory/projects/zeus-alpha-research-ledger-core/*.md` → **18 files, zero `reviewed: yes`** at `4eb87e4cd4`.

### 3.2 Exact row-level cause of the discrepancy

The 10 `missing=reviewed` rows in the dispatch snapshot are **not** current
configured-base state. They are the output of the pre-R2v resolver running
against the **stale primary checkout** (`/home/jean/Projects/hermes-agent-original`
at `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`, 1696 commits behind `origin/main`),
where all 18 project docs still carry `reviewed: pending`. The Factory runtime
tick/reconciler that created this task (events `195850`–`195854`,
17:05:33–17:08:40 UTC, actors `factory-force-tick` / `factory-reconciler`) still
runs from that stale source tree, so it projects `unvalidated_required_docs` /
`missing_or_unindexed_docs` even though the Agent Core rows at the configured
base (`b260baea`) are clean. The 4 READY rows correspond to docs whose origin/main
content is reviewed, confirming the snapshot is a mixed stale-primary/current-base
projection — the documented class from `R2C5_INDEPENDENT_CURRENT_BASE_G1_REVIEW.md`,
`R2AV_*`, `R2BB_*`, `R2BJ_*`.

## 4. Defect determination (acceptance criterion 4)

Traced current `origin/main` code (`hermes_cli/factory_pg.py` at `b260baea`):

- `reconciliation_findings` emits `unvalidated_required_docs` only when
  `_g1_document_blockers(project)` is non-empty (rows 2954–2962) — i.e., only from
  current `document_status` rows.
- `_stale_g1_projection_metadata_keys` (2593–2604) clears `g1_documentation_checkout`
  only when rows are clean and the finding is absent.
- `reconcile_project` (4582–4663) writes event `anomalies` from the same `findings`
  and persists `reconciliation_anomalies` accordingly — a single clean run cannot
  produce both `anomalies=[unvalidated_required_docs]` and cleared keys.
- `_project_docs_notion_preflight` / `_dispatch_preflight_blockers` (6536–6564)
  derive `docs_ready` from current rows; with clean rows, `missing_or_unindexed_docs`
  is not produced.

⇒ The residual stale strings are produced by the **stale runtime source tree**
(primary checkout `4eb87e4cd4`), not by current `origin/main` code. No code defect
reproduced at current base; the runtime catch-up of the primary checkout is the
documented bounded rework (R2c5/R2av/R2BB/R2BJ) and is **out of scope** for this
task (primary-checkout mutation forbidden). Therefore: **no RED-to-GREEN repair PR
is delivered by this increment.**

## 5. Pending QA Guardian delivery dependency (exact)

1. **PR #68 independent exact-SHA QA Guardian review** — `https://github.com/SiteOneTech/hermes-agent-original/pull/68`, head `be56899668acd3bf89503a9fb57d6fef35dcd2dd`, base `origin/main` `b260baea223e863b35fe561e6c5d3d77f3a914c9`. Currently OPEN with zero GitHub reviews (`reviewDecision: ""`). Project contract: `qa_guardian_required=true`, `pr_first_required=true`, `factory_auto_integration_forbidden=true`, `technical_hold=true`. Gates 888/889 (implementation/security) are passed but are **not** independent QA Guardian delivery approval. The R2c delivery cannot be integrated and the historical `critical_readiness` failures (gates 854, 845, …) remain the standing gate evidence until QA Guardian approves at the exact head SHA.
2. **Runtime catch-up (separate bounded technical rework)** — primary checkout `4eb87e4cd4` → `origin/main b260baea` so the tick/reconciler/preflight stop projecting stale `reviewed: pending` blockers. Not executable from this task (forbidden primary mutation).
3. **ALR-020 remains non-dispatchable** — the docs-first preflight denial (event `195850`) is policy-correct; ALR-020-R2 task stays `ready` and must not be dispatched by this increment.

## 6. Boundary compliance

No G1 readiness bypass, no task self-approval, no direct merge, no
primary-checkout mutation, no direct SQL (`factory.*` only via the allowed
`factory status` CLI), no credential access, no external runtime/connector/
messaging action, no trading/risk/paper/live activation, no package installs,
no repo-tree temp scripts (helpers live under `/tmp` and are removed).

## 7. Evidence index

- `/tmp/r2ck-status.json` — canonical Factory status payload (worktree-sourced).
- This document — `factory/projects/zeus-alpha-research-ledger-core/R2CK_CANONICAL_G1_ORIGIN_MAIN_PR68_DELIVERY_RECONCILIATION.md`.
- Commands (real output): `git merge-base --is-ancestor …` (exit 1), `git merge-base …`, `git log --oneline b260baea..be56899`, `git show --stat be56899`, `git status`, `gh pr view 68 --json …`, `grep "^reviewed: pending" …` (18 files), worktree doc frontmatter greps.

---
document_type: independent_g1_review_record
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2ai-current-origin-g1-independent-revie
phase: documentation
status: assessed_pending_pr_handoff
validated: yes
reviewed: pending_independent_review
owner: quality-reviewer
base_ref: origin/main
base_sha: 18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc
branch: factory/zeus-alpha-research-ledger-core/inc-018-r2ai-current-origin-g1-independe
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2ai-current-origin-g1-independe
primary_checkout_head_at_review: 4eb87e4cd48105af05fe974cf1d493f0e1b57ae1
---

# R2ai — current-origin G1 independent-review evidence repair (renewed, corrected)

## Scope

Bounded documentation/review rework for the canonical `unvalidated_required_docs`
anomaly on project `zeus-alpha-research-ledger-core`. This increment performs an
independent G1 specification/quality assessment of the required G1 documentation
pack at the exact **current** `origin/main` candidate
`18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc`, records exact-SHA evidence, and
delivers it PR-first on the assigned branch with the `agent:zeus` label (GitHub
PR #85, updated by this rework). It does not modify runtime/product code, does
not merge, does not deploy, does not change credentials, does not write direct
SQL, does not touch Vonash/Magnus/VAOS/RAG/KB/brokers/trading/risk, and does not
call any external runtime. The primary checkout at
`/home/jean/Projects/hermes-agent-original` is not mutated.

This corrected renewal responds to the security-reviewer block recorded in
Factory gate `944` (failed): the previous PR #85 evidence presented the
readback-only reconciliation projection (`reconciliation_anomalies=[]`,
`reconciliation_required=false`) as if the **active persisted project metadata**
were already clean, while the canonical source of truth (`factory.projects`
metadata in Agent Core Postgres) still carries
`reconciliation_anomalies=["unvalidated_required_docs"]` /
`reconciliation_required=true`. This correction records both truths explicitly
and names the exact bounded follow-up task that repairs the persisted metadata
through the authorized Factory CLI/control-plane — never direct SQL.

## Base identity captured before edits

- Assigned worktree:
  `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2ai-current-origin-g1-independe`
- Assigned branch:
  `factory/zeus-alpha-research-ledger-core/inc-018-r2ai-current-origin-g1-independe`
- Branch head at capture: `eb375581c43a6e88739af4fdbe972d2ad6be33d7`
  (merge of the previous R2ai delivery commit `384c56035e…` with current
  `origin/main`; PR #85 head before this correction).
- Remote base ref after `git fetch origin main`: `origin/main` =
  `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` (fetch exit 0).
- `git merge-base HEAD origin/main` = `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc`
  (the PR diff base is exactly current `origin/main`).
- Primary checkout `/home/jean/Projects/hermes-agent-original` HEAD remains
  `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1` (stale; rejected identity only,
  never canonical readiness authority).
- Remote: `origin` = `https://github.com/SiteOneTech/hermes-agent-original.git`
- Work performed from the shared scratch clone
  `/home/jean/.hermes/profiles/quality-reviewer/scratch/r2ai-inc-018-rework`
  (assigned-branch head; guard prohibits git mutations of the live worktree).

## Canonical Factory CLI readback (corrected, two readbacks)

Readback A — current-origin resolver code (the running module is the
assigned-branch tree whose `hermes_cli` code equals current `origin/main`):

```bash
cd /home/jean/.hermes/profiles/quality-reviewer/scratch/r2ai-inc-018-rework
/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status --json zeus-alpha-research-ledger-core
```

Real result: exit `0`; full JSON saved at `/tmp/r2ai_rework_current_code_status.json`
(3,307,704 bytes). Verified fields:

- `factory_cli_source_root` = `factory_status_source_root` =
  `/home/jean/.hermes/profiles/quality-reviewer/scratch/r2ai-inc-018-rework`
- `db_backend=agent_core_postgres`
- `document_status` rows for `category=g1_required` (14 rows):
  `readiness_source=configured_base_ref`,
  `base_commit=18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc`,
  `exists=true`, `committed=true`, `indexed=true`, `validated=true`,
  `reviewed=true`, `blocking=false` — zero required-G1 blockers.
- Every row also reports `primary_checkout_rejected_reason=primary_checkout_not_configured_base`,
  `primary_head=4eb87e4cd48105af05fe974cf1d493f0e1b57ae1` (stale primary rejected).
- Project metadata as presented by this readback:
  `reconciliation_anomalies=[]`, `reconciliation_required=false`,
  **`cleared_g1_document_reconciliation_projection=true`**,
  `cleared_project_metadata_keys=["g1_documentation_checkout"]`,
  `technical_hold=true`,
  `autonomy_disabled_reason=project_status_manual_attention`.

The `cleared_g1_document_reconciliation_projection=true` flag is the resolver's
own proof that this readback is a **readback-only projection**: per
`hermes_cli/factory_pg.py` `_project_status_effective_reconciliation_projection()`
(read-only at lines 2617–2660 of the current origin code), when the dynamic
configured-base rows are clean, the status output strips the persisted stale
`unvalidated_required_docs` anomaly from the **presented** metadata without
mutating the database. The mutating cleanup is the job of `reconcile_project`
(the authorized control-plane path), not of `factory status`.

Readback B — raw/persisted active metadata (canonical CLI invoked from the
stale primary root, running the pre-R2ao resolver that does not apply the
projection):

```bash
cd /home/jean/Projects/hermes-agent-original
./venv/bin/python3 -m hermes_cli.main factory status --json zeus-alpha-research-ledger-core
```

Real result: exit `0`; full JSON saved at `/tmp/r2ai_rework_factory_status.json`
(3,293,528 bytes). The project metadata block in that readback reports the
**persisted active values**:

- `reconciliation_anomalies=["unvalidated_required_docs"]`
- `reconciliation_required=true`
- `cleared_project_metadata_keys=["g1_documentation_checkout"]` (the obsolete
  checkout key was already cleared by the R2ao-era reconcile; the required-doc
  anomaly itself is still persisted)
- `technical_hold=true` with reason: "Canonical resolve-state and forced tick
  both abort while finalizing the active R2ap quality-review run: git -C
  /home/jean/Projects/hermes-agent-original fetch origin main exceeds Factory's
  120-second timeout. Recovery is bounded to task
  zeus-alpha-research-ledger-core-r2aq-bounded-r2ap-completion-reconciliat; no
  auto-integration or main mutation is authorized."
- `autonomy_disabled_reason=project_status_manual_attention`

Canonical read of the combined evidence: **the required G1 document rows are
14/14 clean at the configured base, but the active persisted project metadata
still carries `unvalidated_required_docs` / `reconciliation_required=true`
plus a persisted technical hold**; the current resolver's readback projection
hides the stale metadata value without repairing it. This increment therefore
does **not** claim the active metadata is clean.

## Candidate selection (corrected)

- **Selected immutable candidate SHA**: `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc`
  (current `origin/main`; verified `git cat-file -e` for all 14 required G1
  files at that exact SHA, and frontmatter `reviewed: yes` /
  `review_evidence: factory_gate_794` for every required document at that SHA).
- **Open PR #44 is delivery evidence only, not a reviewable current-origin
  candidate.** Exact source-backed reason (verified with
  `gh pr view 44 --repo SiteOneTech/hermes-agent-original`): PR #44
  `docs(factory): record R2ae canonical G1 validation` is `OPEN`, head
  `768444e33ac64bf238e64c1df4c49fe2020b51a8` on branch
  `factory/zeus-alpha-research-ledger-core/inc-019-r2ae-bounded-canonical-g1-valida`,
  base `bf422968f9ea73d70d4ac1e8b8bae4af644ce079`, label `agent:zeus`,
  `mergeable=CONFLICTING`; `git merge-base --is-ancestor 768444e3… 18ef28e6…`
  exits `1` (head is NOT an ancestor of current `origin/main`). It is preserved
  as historical delivery evidence for the R2ae task, not as the current-origin
  G1 candidate.
- The handoff delivery for this increment is GitHub PR #85
  (`docs(factory): renew R2ai current-origin G1 independent review evidence`),
  OPEN on the assigned branch, label `agent:zeus`, updated by this correction.

## Independent G1 specification/quality assessment — exact-SHA verdicts (corrected)

Reviewer: `quality-reviewer` profile; independent of the codex-builder
implementation rounds. Assessment performed against exact candidate SHA
`18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` (current `origin/main`) using
`git cat-file -e`, frontmatter reads at that SHA, the canonical readbacks A/B
above, and content spot checks (`REQUIREMENTS_ANALYSIS.md` boundary statements,
`DATABASE_AND_RUNTIME_CONTRACT.md` §4 no-egress contract, scheduler default
`false`).

All 14 Factory-required G1 documents verified at the exact SHA:

| Required document | Dispatch snapshot | Exact-SHA verdict at `18ef28e6` |
|---|---|---|
| `FACTORY_INTAKE.md` | BLOCKED missing=reviewed (stale primary projection) | exists/committed/indexed/validated/reviewed=true, blocking=false at configured base; scope/exclusions/successor mandate consistent |
| `REQUIREMENTS_ANALYSIS.md` | BLOCKED missing=reviewed (stale primary projection) | exists/committed/indexed/validated/reviewed=true, blocking=false; boundary requirements consistent with `DATABASE_AND_RUNTIME_CONTRACT.md` |
| `PATTERN_ANALYSIS.md` | BLOCKED missing=reviewed (stale primary projection) | exists/committed/indexed/validated/reviewed=true, blocking=false; no external/provider pattern leaks into core |
| `ASSUMPTIONS_AND_OPEN_QUESTIONS.md` | BLOCKED missing=reviewed (stale primary projection) | exists/committed/indexed/validated/reviewed=true, blocking=false |
| `PRD.md` | BLOCKED missing=reviewed (stale primary projection) | exists/committed/indexed/validated/reviewed=true, blocking=false; release acceptance requires Zeus-signed `agent:zeus` PR, independent reports, QA Guardian merge evidence |
| `ADRS.md` | BLOCKED missing=reviewed (stale primary projection) | exists/committed/indexed/validated/reviewed=true, blocking=false |
| `METHODOLOGY_PLAN.md` | BLOCKED missing=reviewed (stale primary projection) | exists/committed/indexed/validated/reviewed=true, blocking=false |
| `TECHNICAL_BLUEPRINT.md` | BLOCKED missing=reviewed (stale primary projection) | exists/committed/indexed/validated/reviewed=true, blocking=false |
| `SPRINT_PLAN.md` | READY | exists/committed/indexed/validated/reviewed=true, blocking=false |
| `TASK_GRAPH.md` | BLOCKED missing=reviewed (stale primary projection) | exists/committed/indexed/validated/reviewed=true, blocking=false; reconciles Factory DB tasks; ALR-020 acceptance-metadata blocker documented as non-G1 metadata task |
| `TRACKER.md` | READY | exists/committed/indexed/validated/reviewed=true, blocking=false |
| `QA_GATES.md` | READY | exists/committed/indexed/validated/reviewed=true, blocking=false; RED-GREEN/independent-review/delivery gates consistent; gates 832/915/916/925/929 recorded |
| `SECURITY_GATES.md` | BLOCKED missing=reviewed (stale primary projection) | exists/committed/indexed/validated/reviewed=true, blocking=false; least-privilege/source/typed/no-egress/scheduler gates consistent with the contract |
| `DOCUMENTATION_INDEX.md` | READY | exists/committed/indexed/validated/reviewed=true, blocking=false; entrypoint matrix references all required docs and the R2 chain |

Additional controlling artifacts verified tracked at the exact SHA:
`G0_REPOSITORY_STRATEGY.md`, `REQUIREMENTS_TRACEABILITY.md`,
`DATABASE_AND_RUNTIME_CONTRACT.md`, `G1_REVIEW.md`, plus the R2 evidence
records through R2cv.

### Content review notes (spec/quality)

- Frontmatter of all 14 required documents is consistent at the exact SHA:
  `phase: local_advisory_ledger_v1`, `status: g1_rebaseline`,
  `validated: yes`, `reviewed: yes`, with reviewed provenance bound to
  independent gate `794` / PR #36 exact head `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`
  and source gate `790` / SHA `2476e978c545e24b18ee48844b24eb8c58245ab4`;
  R2c5 re-verified at `91aa62b1…` (gate `832`), R2ba at `756ac62a4c`
  (gates `915`/`916`), R2bm/R2bn at `42c86619…`/`9ebaa9e7…` (gates `925`/`929`).
- No required document claims external runtime, trading/risk/paper/live,
  deployment, credential, connector, messaging, or RAG/KB authority.
- `DATABASE_AND_RUNTIME_CONTRACT.md` §4 no-egress contract (banned imports,
  `ALR_IMPLEMENTATION_BASE_SHA` diff scan, scheduler default `false`) is
  consistent with QA_GATES and SECURITY_GATES.
- PR-first / `agent:zeus` / no-auto-merge / QA-Guardian contracts are
  consistently documented across G0, PRD, QA_GATES, SECURITY_GATES and
  TASK_GRAPH; `factory_auto_integration_forbidden=true` in Agent Core.
- The observed ALR-010-R1 direct merge remains recorded as reconciliation
  evidence, not approval.

### Reviewed-status preservation

Per the increment contract, this assessment does not change any required
document's `reviewed` field. The machine-readable reviewed status of the 14
required documents remains exactly as read back from the configured base source
(backed by gates 794/832/915/916/925/929 frontmatter provenance); no
`reviewed: yes` is added, removed or re-issued by this worker. The designated
independent security review for the current candidate SHA remains pending: the
latest security gate recorded for this task is **gate `944` = failed**
(security-reviewer, superseding partial passes `940`–`943` and the earlier
`938`/`939`); this worker does not self-approve.

## Verdict (corrected)

**G1 document contract at exact candidate SHA `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc`:
PASS (quality/specification)** — all 14 required documents exist, are
committed, indexed, validated, reviewed and non-blocking at the configured base
source, and their content is internally consistent with the index, contract,
traceability, QA and security gates. No line-level G1 document failure was
found at this SHA.

**Active persisted project metadata: NOT clean — this increment does not claim
otherwise.** The canonical source of truth still carries
`reconciliation_anomalies=["unvalidated_required_docs"]` /
`reconciliation_required=true` plus a persisted `technical_hold=true`
(zeus, 2026-08-17, reason names the now-`done` task
`zeus-alpha-research-ledger-core-r2aq-bounded-r2ap-completion-reconciliat`;
hold not yet released) and `autonomy_disabled_reason=project_status_manual_attention`.
The current resolver's `cleared_g1_document_reconciliation_projection=true`
proves the readback projection hides the stale persisted value without
repairing it. This is an evidence/provenance blocker at the control-plane
level, not a G1 document-content failure.

**Task closure remains BLOCKED on the exact bounded follow-up:**
`zeus-alpha-research-ledger-core-r2ai-r2-persisted-active-metadata-reconciliat`
— a subsequent authorized Factory run must, through the canonical Factory
CLI/control-plane only (the R2cv-delegated `hermes factory project
resolve-state|reconcile` from a configured-base worktree; **no direct SQL, no
`psql`, no ad-hoc DB script**): (1) verify current configured-base rows remain
14/14 non-blocking, (2) persist the reconciled metadata
(`reconciliation_anomalies=[]`, `reconciliation_required=false`) so the raw
readback no longer needs the projection flag, (3) clear the stale technical
hold after confirming `r2aq` completion evidence, and (4) read back the
persisted metadata clean. This run's DB-write allowlist permits only `factory
status` and `factory gate record`, so it records the follow-up here instead of
creating/closing tasks.

## Boundary confirmation

- Changed paths: only `factory/projects/zeus-alpha-research-ledger-core/`
  project-local documentation/evidence (R2ai record, index, QA gates, security
  gates, tracker rows).
- No runtime/product code change, no primary-checkout mutation, no merge, no
  deploy, no credential change, no direct Factory DB write (only the two
  sanctioned CLI readbacks plus the gate record), no external
  runtime/connector/messaging action, no trading/risk/paper/live action, no
  force-push (branch advances `eb375581c4…` via normal push).
- Delivery is PR-first on the assigned branch as the Zeus-signed `agent:zeus`
  PR #85, updated with this corrected evidence; no merge by this worker.

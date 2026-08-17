---
project_id: zeus-alpha-research-ledger-core
phase: local_advisory_ledger_v1
status: g1_rebaseline
validated: yes
reviewed: yes
reviewed_by: solution-architect
review_evidence: factory_gate_794
reviewed_candidate_sha: c81547062c5362a7be6f5a1bb2ef9612b29bac9c
reviewed_candidate_pr: https://github.com/SiteOneTech/hermes-agent-original/pull/36
reviewed_source_gate: factory_gate_790
reviewed_source_sha: 2476e978c545e24b18ee48844b24eb8c58245ab4
---

# G1 REVIEW RECORD

## Review round 1 — remediated
Independent specification and security reviews required traceability, Factory DB task reconciliation, bounded local collection, removal of collaboration messages, least privilege, DB invariants, typed non-advice state, no-egress proof and disabled scheduler. The first remediation commit `743f4c404` addressed the architecture direction but was not sufficiently exact.

## Review round 2 — security rework incorporated
The second security review returned `REQUEST_CHANGES` because the initial remediation still lacked exact object grants, enum/predicate definitions, carrier-wide typed fields, executable no-egress harness and durable scheduler configuration/readiness state.

This revision adds `DATABASE_AND_RUNTIME_CONTRACT.md`, which now fixes:
- role attributes, per-object operations, function allowlist, `PUBLIC` revocations/default privileges and named direct SQL denials;
- exact source/terms/freshness enums, stale predicate, time/duplicate/supersession/lineage negatives;
- typed fields/defaults/checks/immutability and exact JSON field rejection for cards, reviews and handoffs;
- scanned path/banned-pattern list plus every-handler/scheduler interception harness and local DSN-only check;
- default-false config, readiness-table fields/components, no-cache verifier and all false-path scheduler tests.

## Review round 3 — independent second-pass REQUEST_CHANGES (Gates 686 and 687)

**Candidate provenance reviewed:** committed SHA `29cedbff5dedc13683a03bf32a178711af910eca` (`docs(factory): make alpha research safety contracts executable`) **plus the then-existing uncommitted dirty revision of** `DATABASE_AND_RUNTIME_CONTRACT.md`. The dirty revision is part of the effective review candidate but is not a committed SHA; neither it nor the historical merge base is asserted to be current canonical base.

Read-back source: `hermes factory status zeus-alpha-research-ledger-core --json` from Agent Core Postgres (`db_backend=agent_core_postgres`, `database=zeus_agent`). The real failed gate notes were:

- Gate **686**, `gate_type=spec`, `status=failed`, reviewer `independent-local-spec-review`, timestamp `2026-08-10T07:18:31.071405+00:00`: “Read-only second-pass review of 29cedbff5dedc13683a03bf32a178711af910eca plus the dirty DATABASE_AND_RUNTIME_CONTRACT.md returned REQUEST_CHANGES: exact handler names conflict; transition function/grants conflict; ALR-020 bounded-session acceptance conflicts with the stated scope; current-origin statements are stale. No source, PR, test, or merge evidence claimed.”
- Gate **687**, `gate_type=security`, `status=failed`, reviewer `independent-local-security-review`, timestamp `2026-08-10T07:18:33.063457+00:00`: “Read-only second-pass review of 29cedbff5dedc13683a03bf32a178711af910eca plus the dirty DATABASE_AND_RUNTIME_CONTRACT.md returned REQUEST_CHANGES: reconcile exact tool allowlist; fully type card/handoff schemas; add enforceable secret non-disclosure tests; cover all ALR changed files in no-egress scan; specify secure transition functions; persist immutable source/terms provenance. No source, PR, test, or merge evidence claimed.”

This R1 documentary candidate resolves those bounded findings by requiring: (1) one canonical leaf allowlist using `program_create` and `source_submit`, with named synonym/alias rejection; (2) complete safe-elevation semantics for both lifecycle functions, including owner, `SECURITY DEFINER`, fixed search path, `session_user` authorization, exact edges/columns, grants and catalog/negative proof; (3) deterministic ALR-020 Factory metadata reconciliation because its recorded bounded-local-sessions acceptance conflicts with v1's session/message exclusion; (4) removal of stale “current origin/main” claims in favor of historical-base evidence plus pre-PR revalidation; (5) exact typed/bounded `alpha_card_create`, fixed `handoff_list` objects, and unambiguous envelope/payload key counts with prohibited/unknown-field checks; (6) generic reference-only secret non-disclosure/redaction plus persisted/output/log/error/trace/metric/scheduler negative tests using synthetic canaries only; (7) static no-egress coverage for every ALR-added/modified implementation diff line, including replacement sides of modified lines and unscannable-file failures; and (8) immutable source/terms reference persistence with auditable admin approval/revision provenance and direct SQL/handler tests.

This bounded documentary rework addresses those records only. A revised **committed** candidate must receive new, independent specification and security reviews against its exact SHA. No R1 review is PASS, no G1 frontmatter may become reviewed yes, and no implementation, Factory metadata change, PR, merge, deploy, or normal task dispatch is authorized by this record.

## Review round 4 — merge-policy REQUEST_CHANGES (Gate 695)

**Candidate reviewed:** committed SHA `b9396bcd7d14ee6f212bd0fd0609e468cecf567f` (`docs(factory): resolve ALR G1 second-pass findings`).

Read-back source: `hermes factory status zeus-alpha-research-ledger-core --json` from Agent Core Postgres (`db_backend=agent_core_postgres`, `database=zeus_agent`) plus local Git inspection. The real failed gate note was:

- Gate **695**, `gate_type=spec`, `status=failed`, reviewer `solution-architect`, timestamp `2026-08-10T09:31:33.359633+00:00`: “Review of SHA b9396bcd7: documentary content resolves the bounded Gate 686/687 specification/security findings, but task cannot close because live Factory/Git evidence contradicts the no-merge/PR-first contract. Agent Core Postgres status recorded event 173433 increment_integrated with method merge_no_ff_push_origin for this task, and git shows origin/main at e3d04ff94 is a merge commit with parent b9396bcd7. Rework: reconcile/revert/record authorized handling of the unexpected base-branch merge and update G1_REVIEW/TRACKER/TASK_GRAPH with actual merge evidence before closure; no downstream implementation dispatch until independent reviews inspect exact corrected SHA.”

This R2 correction records the merge fact instead of preserving stale branch-only/no-merge statements: Factory event `173433` integrated branch commit `b9396bcd7d14ee6f212bd0fd0609e468cecf567f` into base `main` using `merge_no_ff_push_origin`, producing `e3d04ff94b67e6e21be1d5515bdb71400fbedf0a`. Git confirms `e3d04ff94` has parents `00e7bb4ab` and `b9396bcd7`, and `b9396bcd7` is an ancestor of `origin/main`.

The correction does **not** claim that the merge was authorized, does not revert it, does not open a PR, does not perform a new merge/deploy, and does not convert any R1/G1 review to PASS. It only reconciles documentation with the Agent Core/Git source of truth so independent reviewers can inspect the exact corrected SHA.

## Review round 5 — R2j canonical-state evidence repair

**Mismatch reproduced:** R2i's independent quality/security review gates cite the actual still-open Zeus-signed PR #29 candidate at `f61a7275048e2135b2b2729a1b9cdf8713c58866` against canonical `main` `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c`, but their attached Factory increment-integration evidence records `increment_integration_method=already_ancestor` for the R2i review branch at `increment_branch_commit=5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c`.

**Correction:** that `already_ancestor` attachment is review-worktree provenance only. It proves the review branch/check-out was already at canonical `main`; it does not prove PR #29 was merged, visible on `main`, or accepted by QA Guardian. The source candidate remains PR #29 head `f61a7275048e2135b2b2729a1b9cdf8713c58866` until the PR-first / QA Guardian path records candidate-bound delivery evidence.

`R2J_CANONICAL_STATE_REPAIR.md` is now the controlling project-local handoff artifact for this mismatch. It names PR #29, its exact head, canonical `main`, the current Factory `document_status` blocker set, the R2i provenance root cause, and the candidate-bound QA Guardian evidence that must be used for any future terminal delivery decision. This R2j repair performs no merge, deployment, credential change, direct SQL, product implementation, external-runtime operation, or `reviewed: yes` conversion.

## Review round 6 — R2k stale canonical provenance repair

**Mismatch reproduced:** live Agent Core project metadata still names `metadata.g1_documentation_checkout` as PR #20 / `dad375f27568c38be771fc597b579d087f034e1d`, while R2j was subsequently delivered through PR #30 at head `c1943efb2b97b54b42bc5eabe858340d8c391116` and remote `origin/main` now reads `83d5ee06ba25859f047469baed223fe88e9467e3`. The local primary `main` ref remains `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1` and does not contain `c1943efb2b97b54b42bc5eabe858340d8c391116` by `git merge-base --is-ancestor ... main` exit `1`.

**Current blocker:** Agent Core `factory status` still reports `unvalidated_required_docs` and `document_status` read-back from the primary source has required G1 documents at `reviewed=false`; this R2k worker does not convert them to `reviewed: yes`.

**Correction:** `R2K_STALE_CANONICAL_G1_PROVENANCE_REPAIR.md` is now the controlling renewal handoff artifact. It explicitly rejects PR #20/dad375f and stale review-worktree attachments as active review provenance, records PR #30/c1943 as historical R2j evidence, and instructs independent reviewers to review the exact head SHA of the R2k Zeus-signed `agent:zeus` PR.

This is implementation/documentation evidence only. It performs no merge, deployment, credential change, direct SQL, product implementation, external-runtime operation, or `reviewed: yes` conversion. No normal ALR-020 work may dispatch until the exact R2k candidate is independently reviewed and canonical Factory metadata/document status are reconciled.

## Review round 7 — R2m current-base exact-SHA handoff

**Current-base recovery:** R2m fetched canonical `origin/main` and recorded exact base `ab08b13669903a87b3d60d6c80231d23d6313782`. The assigned branch/worktree `factory/zeus-alpha-research-ledger-core/inc-001-r2m-current-base-g1-documentatio` was initially equal to that base, then received only project-local documentation updates for current-base review handoff.

**Incorporated repairs:** `R2J_CANONICAL_STATE_REPAIR.md` and `R2K_STALE_CANONICAL_G1_PROVENANCE_REPAIR.md` remain indexed controlling artifacts. PR #20/dad375f, historical PR #29/f61a PASS reviews, R2i review-worktree `already_ancestor` evidence, PR #30/c1943 and PR #31/73b are not active approval or implementation-dispatch evidence.

**Handoff:** the fresh R2m Zeus-signed `agent:zeus` PR was the next review target at that time. R2m left `reviewed: pending` intact and performed no merge, deployment, credential change, direct SQL, product implementation or external-runtime operation.

## Review round 8 — R2u canonical G1 document-status preflight repair

**Current-base reproduction:** R2u starts from current `origin/main` / branch base `df4c77fd1413a65cdb85885a06978ff157c1de4d`. Canonical Factory status read-back in this run reproduced the active `unvalidated_required_docs` failure: the primary repository documentation pack was present/indexed/committed/validated but not machine-read as reviewed.

**Independent review source:** the reviewed G1 pack is bound to the Zeus-signed PR-first candidate PR #36 at exact head `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`, reviewed by `solution-architect` in Factory gate `794`. The reviewed-docs source evidence retained by that candidate is gate `790` / PR #34 SHA `2476e978c545e24b18ee48844b24eb8c58245ab4`.

**Correction:** R2u converts the required G1 document frontmatter and `DOCUMENTATION_INDEX.md` matrix from `reviewed: pending` to `reviewed: yes` with explicit PR/gate/SHA provenance, and records the docs-first repair in `R2U_CANONICAL_G1_DOCUMENT_STATUS_PREFLIGHT_REPAIR.md`. This repairs only documentation/index/traceability state. It does not import the R2s control-plane code path, merge `main`, deploy, change credentials, add connectors, enable messaging, authorize trading/risk/paper/live behavior or dispatch product implementation.

## Review round 9 — R2w reviewed-frontmatter PR recovery

**Current status read-back:** R2w starts from current `origin/main` / worktree head `df79aac9d306c0b055fe88dbde5ebd54d9635e36`. Approved Agent Core Factory status CLI evidence (`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`) was captured in Hermes terminal output `out-1786856760-2035541-e390.log`. Its project `document_status` rows show configured base ref `origin/main`, base commit `df79aac9d306c0b055fe88dbde5ebd54d9635e36`, and `exists=true`, `committed=true`, `validated=true`, `indexed=true`, `reviewed=true`, `blocking=false` for all G1 required documents, including the 11 documents named in the R2w task.

**Correction:** `R2W_CANONICAL_G1_REVIEWED_FRONTMATTER_PR.md` records the PR-first recovery handoff for this canonical reviewed-frontmatter state. The R2w PR must remain Zeus-signed and labeled `agent:zeus`, must name the exact pushed candidate SHA, and must receive independent exact-SHA quality review before task closure. This round does not change runtime/source code, perform a merge, deploy, direct SQL, credential change, connector/messaging action, or trading/risk/paper/live behavior.

## Review round 10 — R2ah current-origin reviewed-marker/index repair

**Current-origin identity captured before edits:** R2ah fetched `origin/main` and verified the assigned branch/worktree before writing files. The worktree `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-019-r2ah-current-origin-g1-reviewed`, branch `factory/zeus-alpha-research-ledger-core/inc-019-r2ah-current-origin-g1-reviewed`, local `HEAD`, `origin/main`, and merge-base were all exactly `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7` before the first R2ah edit.

**Canonical Agent Core read-back:** the approved status command `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json` read Agent Core Postgres (`db_backend=agent_core_postgres`, `database=zeus_agent`) and wrote full evidence to `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786890230-1212346-8c10.log`. Project `document_status` lines 16292–16558 show configured base ref `origin/main`, base commit `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7`, `readiness_source=configured_base_ref`, and `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false` for all 14 G1 required documents.

**Correction:** `R2AH_CURRENT_ORIGIN_G1_REVIEWED_MARKER_REPAIR.md` now records the current-origin branch/worktree identity, the configured-base document-status read-back, and the PR-first handoff. `DOCUMENTATION_INDEX.md` now names exact base `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7` for the current candidate state. The required G1 frontmatter reviewed markers remain machine-readable `reviewed: yes` and still cite their independent source review chain, PR #36 / gate `794` plus gate `790` / PR #34 source evidence.

**Handoff requirement:** the fresh R2ah branch is opened as non-draft Zeus-signed GitHub PR #47 (`https://github.com/SiteOneTech/hermes-agent-original/pull/47`) labeled `agent:zeus` against `main`. The PR body/Factory evidence must name the exact final head SHA after the last push. An independent reviewer must inspect that exact SHA; this R2ah worker does not self-approve, merge, deploy, change credentials, write direct SQL, or touch any runtime/external/trading path.

## Review round 11 — R2c2 autonomous canonical G1 document-status repair

**Current-base identity captured before edits:** R2c2 fetched `origin/main` and verified the assigned worktree before writing files. The worktree `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2c2-autonomous-canonical-g1-doc`, branch `factory/zeus-alpha-research-ledger-core/inc-018-r2c2-autonomous-canonical-g1-doc`, local `HEAD`, `origin/main`, and merge-base were all exactly `dbde1790f8d45f111bc69b3491a1862eafb29fa2` before the first R2c2 edit.

**Canonical Agent Core read-back:** the approved status command `/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json` read Agent Core Postgres (`db_backend=agent_core_postgres`, `database=zeus_agent`) and wrote full evidence to `/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786892903-1813387-f690.log`. Project `document_status` lines 16632–16898 show configured base ref `origin/main`, base commit `dbde1790f8d45f111bc69b3491a1862eafb29fa2`, `readiness_source=configured_base_ref`, and `exists=true`, `committed=true`, `indexed=true`, `validated=true`, `reviewed=true`, `blocking=false` for all 14 G1 required documents. This resolves the current required-document status mismatch at the document-status row level while preserving stale reconciliation/event history as history only.

**Correction:** `R2C2_AUTONOMOUS_CANONICAL_G1_DOCUMENTATION_STATUS_REPAIR.md` now records the current-base branch/worktree identity, the configured-base document-status read-back, and the PR-first handoff. `DOCUMENTATION_INDEX.md` now names exact base `dbde1790f8d45f111bc69b3491a1862eafb29fa2` for the current candidate state. The required G1 frontmatter reviewed markers remain machine-readable `reviewed: yes` and still cite their independent source review chain, PR #36 / gate `794` plus gate `790` / PR #34 source evidence.

**Handoff requirement:** the fresh R2c2 branch is opened as non-draft Zeus-signed GitHub PR #48 (`https://github.com/SiteOneTech/hermes-agent-original/pull/48`) labeled `agent:zeus` against `main`. The PR body/Factory evidence must name the exact final head SHA after the last push. An independent reviewer must inspect that exact SHA; this R2c2 worker does not self-approve, merge, deploy, change credentials, write direct SQL, or touch any runtime/external/trading path.

## Review round 12 — R2c5 independent current-base G1 review and canonical document-status repair

**Current-base identity captured before edits:** the assigned R2c5 worktree
`/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2c5-independent-current-base-g1`,
branch `factory/zeus-alpha-research-ledger-core/inc-001-r2c5-independent-current-base-g1`,
local `HEAD` and `origin/main` were all exactly `91aa62b11f02f69d88f7d8c18c30033edb4b7355`
(the R2c4 merge into main) before the first R2c5 edit.

**Independent review performed:** reviewer `quality-reviewer` reviewed all 14
Factory-required G1 documents at exact base `91aa62b11f02f69d88f7d8c18c30033edb4b7355`
with real readback evidence (Factory gate `832`). Canonical configured-base
readback via the approved CLI run from the assigned worktree (resolver code at
the reviewed base) shows `readiness_source=configured_base_ref`, `base_ref=origin/main`,
`base_commit=91aa62b11f02f69d88f7d8c18c30033edb4b7355`,
`configured_base_ref_accepted=true`, `primary_checkout_accepted=false`,
`primary_checkout_rejected_reason=primary_checkout_not_configured_base`, and
`exists=true`, `committed=true`, `indexed=true`, `validated=true`,
`reviewed=true`, `blocking=false` for all 14 G1 required documents — zero
required-G1 blockers at the configured source (log `/tmp/r2c5_readback_new_resolver.json`,
lines 17420–17770).

**Live runtime mismatch documented and routed:** the running Factory runtime
executes the pre-R2v resolver from the stale primary checkout
`/home/jean/Projects/hermes-agent-original` (HEAD `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`,
1367 commits behind origin/main; working tree files carry `reviewed: pending`),
so its live `document_status` readback still reports 10 required-G1 blockers
(exact output in
`/home/jean/.hermes/profiles/quality-reviewer/cache/terminal-output/out-1786901573-3764810-ead0.log`,
lines 17420–17729). This is routed as bounded technical rework (Factory
runtime catch-up of the primary checkout to `origin/main`); it is not
resolvable by this documentation-only increment, which must not modify the
primary checkout.

**Correction:** `R2C5_INDEPENDENT_CURRENT_BASE_G1_REVIEW.md` records the
exact-SHA independent review evidence; `DOCUMENTATION_INDEX.md` now names
exact base `91aa62b11f02f69d88f7d8c18c30033edb4b7355` and gate `832` for the
current candidate state. The required G1 frontmatter reviewed markers remain
machine-readable `reviewed: yes` and keep their independent source review
chain (PR #36 / gate `794` plus gate `790` / PR #34 source evidence); no
reviewed marker was changed without review evidence (none needed changing —
the R2c5 review re-affirms them at the current base).

**Handoff requirement:** the fresh R2c5 branch is opened as a non-draft
Zeus-signed GitHub PR #51 (`https://github.com/SiteOneTech/hermes-agent-original/pull/51`)
labeled `agent:zeus` against `main`. The PR
body/Factory evidence must name the exact base SHA `91aa62b11` and the exact
final head SHA after the last push. An independent reviewer (task reviewer
`solution-architect`) must inspect that exact SHA; this R2c5 worker does not
self-approve, merge, deploy, change credentials, write direct SQL, or touch
any runtime/external/trading path.

## Review round 13 — current-origin G1 document-status technical recovery

**Current-origin readback:** this recovery starts from assigned worktree
`/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-000-g1-document-status-technical-rec`,
branch `factory/zeus-alpha-research-ledger-core/inc-000-g1-document-status-technical-rec`,
with local `HEAD`, `origin/main`, and merge-base all equal to
`139df9ae49137bb4b16152550d53d385310de3b6` before edits.

**Canonical Agent Core read-back:** the approved status command
`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status --json zeus-alpha-research-ledger-core`
read Agent Core Postgres (`db_backend=agent_core_postgres`, `database=zeus_agent`) and wrote full evidence to
`/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786925327-620586-1dd0.log`.
Project `document_status` lines `19341`–`19690` show configured base ref
`origin/main`, base commit `139df9ae49137bb4b16152550d53d385310de3b6`,
`readiness_source=configured_base_ref`, stale primary checkout rejected, and
`exists=true`, `committed=true`, `indexed=true`, `validated=true`,
`reviewed=true`, `blocking=false` for all 14 required G1 documents.

**Remaining control-plane mismatch:** earlier status payloads exposed stale
persisted provenance: recent reconciliation events listed `unvalidated_required_docs`,
metadata carried `reconciliation_anomalies=["unvalidated_required_docs"]`, and obsolete
`g1_documentation_checkout` pointed at PR #20 / `dad375f27568c38be771fc597b579d087f034e1d`.
Historical gate `845` also recorded old `reviewed=false` rows. The final Agent Core
readback re-created `unvalidated_required_docs` from stale `metadata.g1_documentation_checkout`
assignment provenance (`event_id=193040`, log lines `491`–`512`) even while all 14 current
required-G1 rows are non-blocking; the bounded follow-up is a Factory reconciler repair,
not direct SQL or primary checkout mutation.

**Handoff requirement:** the fresh current-origin branch must be opened as a
Zeus-signed GitHub PR labeled `agent:zeus` against `main`. The PR body/Factory
evidence must name exact base `139df9ae49137bb4b16152550d53d385310de3b6`, final
head SHA, and status-output path. An independent quality reviewer must inspect
that exact SHA; this worker does not self-approve, merge, deploy, change
credentials, write direct SQL, mutate the primary checkout, or touch any
runtime/external/trading path.

## Review round 14 — R2at current-origin G1 documentation validation technical rework

**Current-origin identity captured before edits:** R2at uses assigned worktree
`/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2at-current-origin-g1-documenta`,
branch `factory/zeus-alpha-research-ledger-core/inc-001-r2at-current-origin-g1-documenta`,
with local `HEAD`, `origin/main`, and merge-base all equal to
`a41acdc4820b92a31b7d42d9a9c28e95b875a3d1` before documentation edits.

**Canonical Agent Core read-back:** the approved status command
`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`
read Agent Core Postgres (`db_backend=agent_core_postgres`, `database=zeus_agent`) and wrote full evidence to
`/home/jean/.hermes/profiles/claude-builder/cache/terminal-output/out-1786955910-3629985-7910.log`.
Project `document_status` lines `20184`–`20534` show configured base ref
`origin/main`, base commit `a41acdc4820b92a31b7d42d9a9c28e95b875a3d1`,
`readiness_source=configured_base_ref`, stale primary checkout rejected, and
`exists=true`, `committed=true`, `indexed=true`, `validated=true`,
`reviewed=true`, `blocking=false` for all 14 required G1 documents.

**Remaining stale projection evidence:** recent reconciler events `194478` and
`194477` still list `anomalies=["unvalidated_required_docs"]`, and dispatch-preflight
event `194474` still lists `blockers=["missing_or_unindexed_docs"]`. The same
current status payload reports active `reconciliation_anomalies=[]`,
`reconciliation_projection_source=current_document_status`, and
`reconciliation_required=false`, while the old `unvalidated_required_docs` remains
only under `stale_reconciliation_projection` as audit evidence.

**R2au projection repair supersession:** the R2au repair keeps the same
historical event/task audit boundary but no longer re-presents stale required-doc
projection metadata under active project metadata when current configured-base
G1 rows are clean. Current readback
`/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786959574-145359-db10.log`
shows all 14 required rows non-blocking at lines `20255`–`20604`, active
metadata sourced from `current_document_status` at lines `20808`–`20844`, and no
active `stale_reconciliation_projection` field.

**Handoff requirement:** R2at remains historical validation evidence; the current
R2au branch must be opened as a Zeus-signed GitHub PR labeled `agent:zeus`
against `main`. The PR body/Factory evidence must name exact base
`2b53ee0f14491ff43da7683d475654a03af5d678`, R2at ancestor
`d4ac6d89994adf823bb50b79afe5a39fd204fdfd`, final head SHA, status-output path,
no-auto-merge, and no external runtime execution. An independent quality reviewer
must inspect that exact SHA; this R2au worker does not self-approve, merge,
deploy, change credentials, write direct SQL, mutate the primary checkout, or
touch any runtime/external/trading path.

## Review round 15 — R2av current-origin G1 status projection verification

**Current-origin identity captured before edits:** R2av uses assigned worktree
`/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2av-current-origin-g1-status-pr`,
branch `factory/zeus-alpha-research-ledger-core/inc-017-r2av-current-origin-g1-status-pr`,
with local `HEAD`, `origin/main`, merge-base, and remote `refs/heads/main` all equal to
`af9fa27eaaaa52ef173f1578fb7f572ce52cebc6` before documentation edits. This is the
R2au PR #61 merge commit and contains repair commit
`1afd37a61a8d21af393e393cb77083adb25b41c7`.

**Canonical Agent Core read-back:** the approved status command
`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status --json zeus-alpha-research-ledger-core`
read Agent Core Postgres (`db_backend=agent_core_postgres`, `database=zeus_agent`) and wrote full evidence to
`/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786962029-820188-d410.log`.
Project `document_status` lines `20270`–`20626` show configured base ref
`origin/main`, base commit `af9fa27eaaaa52ef173f1578fb7f572ce52cebc6`,
`readiness_source=configured_base_ref`, stale primary checkout rejected, and
`exists=true`, `committed=true`, `indexed=true`, `validated=true`,
`reviewed=true`, `blocking=false` for all 14 required G1 documents.

**Reviewed=false projection source:** the current status payload still carries old
audit records: recent events `194724`/`194725` list `anomalies=["unvalidated_required_docs"]`,
and older delivery-gate evidence retains stale `document_status_snapshot` rows. Those
records are historical and must not be projected as current dispatch readiness. The
source-backed 10-blocker mismatch remains the stale primary/runtime path documented in
this file's R2c5 section (`/home/jean/Projects/hermes-agent-original` at
`4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`, pre-R2v resolver), not current configured-base
document content.

**Current projection outcome:** active metadata lines `20830`–`20864` report
`reconciliation_anomalies=[]`, `reconciliation_projection_source=current_document_status`,
`reconciliation_required=false`, and `cleared_g1_document_reconciliation_projection=true`.
`R2AV_CURRENT_ORIGIN_G1_STATUS_PROJECTION_RECOVERY.md` records the status lines,
focused GREEN test output, and no-direct-SQL/no-primary-mutation/no-external-runtime
boundary.

**Handoff requirement:** the fresh R2av branch must be opened as a Zeus-signed
GitHub PR labeled `agent:zeus` against `main`. The PR body/Factory evidence must
name exact base `af9fa27eaaaa52ef173f1578fb7f572ce52cebc6`, final head SHA, R2au
repair commit `1afd37a61a8d21af393e393cb77083adb25b41c7`, status-output path,
no-auto-merge, and no external runtime execution. Independent quality review and
QA Guardian evidence remain required; this R2av worker does not self-approve,
merge, deploy, change credentials, write direct SQL, mutate the primary checkout,
or touch any runtime/external/trading path.

## Review round 16 — R2BJ bounded canonical G1 documentation/index technical recovery

**Current-base identity captured before edits:** R2BJ uses assigned worktree
`/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-017-r2bj-bounded-canonical-g1-docume`,
branch `factory/zeus-alpha-research-ledger-core/inc-017-r2bj-bounded-canonical-g1-docume`,
with local `HEAD`, `origin/main`, and merge-base all equal to
`b503ba3b57fd606956d0ebf925c83eda253bdcc5` before documentation edits.

**Canonical Agent Core read-back:** the approved status command
`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`
read Agent Core Postgres (`db_backend=agent_core_postgres`, `database=zeus_agent`) from the assigned worktree source and wrote parsed evidence to
`/tmp/r2bj-status-before.json` plus full terminal output
`/home/jean/.hermes/profiles/codex-builder/cache/terminal-output/out-1786980569-860127-b650.log`.
The active project status reports `factory_cli_source_root` and
`factory_status_source_root` as the assigned worktree, `factory_status_delegated=false`,
`reconciliation_anomalies=[]`, `reconciliation_projection_source=current_document_status`,
`reconciliation_required=false`, `notion_required=false`, and all 14 required G1
documents as `exists=true`, `committed=true`, `indexed=true`, `validated=true`,
`reviewed=true`, `blocking=false` from `readiness_source=configured_base_ref`, base
`b503ba3b57fd606956d0ebf925c83eda253bdcc5`, with stale primary checkout
`4eb87e4cd48105af05fe974cf1d493f0e1b57ae1` rejected.

**Current stale predicate evidence:** event `195559` still records ALR-020-R2
dispatch preflight `blockers=["missing_or_unindexed_docs"]`; events `195563`,
`195562`, and `195560` still record `anomalies=["unvalidated_required_docs"]`;
gate `884` failed stale PR #44/R2ae evidence that is conflicting/dirty against
current `origin/main`. These rows are audit/projection evidence only and do not
override the current configured-base row readback.

**Correction:** `R2BJ_BOUNDED_CANONICAL_G1_DOCUMENTATION_INDEX_RECOVERY.md` records
the exact docs-first predicate, current Factory status readback, required document
locations, stale event/gate source, and no-direct-SQL/no-primary-mutation/no-external-runtime
boundary. `DOCUMENTATION_INDEX.md`, `TASK_GRAPH.md`, `TRACKER.md`, `QA_GATES.md`,
and `SECURITY_GATES.md` index the same current evidence.

**Handoff requirement:** the fresh R2BJ branch must be opened as a Zeus-signed
GitHub PR labeled `agent:zeus` against `main`. The PR body/Factory evidence must
name exact base `b503ba3b57fd606956d0ebf925c83eda253bdcc5`, final head SHA,
status-output path, validation output, no-merge, and no external runtime execution.
Independent quality review remains required; this R2BJ worker does not self-approve,
merge, deploy, change credentials, write direct SQL, mutate the primary checkout,
or touch any runtime/external/trading path.

## Review round 17 — R2c technical rework current-origin G1 independent review evidence recovery

**Current-origin identity captured before edits:** R2c uses assigned worktree
`/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2c-technical-rework-current-ori`,
branch `factory/zeus-alpha-research-ledger-core/inc-001-r2c-technical-rework-current-ori`,
with local `HEAD`, `origin/main`, merge-base, and remote `refs/heads/main` all equal to
`b260baea223e863b35fe561e6c5d3d77f3a914c9` before documentation edits.

**Canonical Agent Core read-back:** the approved status command
`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`
read Agent Core Postgres (`db_backend=agent_core_postgres`, `database=zeus_agent`) from the assigned worktree source and wrote parsed evidence to
`/tmp/r2c-initial-status.json`. The active project status reports
`factory_cli_source_root` and `factory_status_source_root` as the assigned worktree,
`factory_status_delegated=false`, `reconciliation_anomalies=[]`,
`reconciliation_projection_source=current_document_status`, `reconciliation_required=false`,
`notion_required=false`, zero human questions, and all 14 required G1 documents as
`exists=true`, `committed=true`, `indexed=true`, `validated=true`,
`reviewed=true`, `blocking=false` from `readiness_source=configured_base_ref`, base
`b260baea223e863b35fe561e6c5d3d77f3a914c9`, with stale primary checkout
`4eb87e4cd48105af05fe974cf1d493f0e1b57ae1` rejected.

**Independent read-only review evidence:** Claude Code session
`063901ef-304f-41c2-8756-18185d96b4fa` reviewed `DOCUMENTATION_INDEX.md` and all
14 Factory-required G1 documents at exact candidate
`b260baea223e863b35fe561e6c5d3d77f3a914c9`. It returned PASS for requirement
mapping R1–R10, no-authority boundaries, and stale projection classification. This
is review evidence only and not self-approval, merge/deploy/direct-SQL/credential/
external-runtime/connector/messaging/trading/risk/paper/live or downstream ALR
implementation authority.

**Current stale technical predicate:** R2ai gate `857`, R2ae gate `884`, and recent
project reconciliation / dispatch-preflight events still contain historical
`unvalidated_required_docs` / `missing_or_unindexed_docs` strings. Those rows are
technical stale projection/audit evidence when the current configured-base rows are
clean; they must not create a human question or be treated as current document
content blockers.

**Correction:** `R2C_TECHNICAL_REWORK_CURRENT_ORIGIN_G1_INDEPENDENT_REVIEW.md`
records the exact current-origin Factory status readback, documents reviewed,
R1–R10/no-authority mapping, and stale technical-only cause. `DOCUMENTATION_INDEX.md`,
`TASK_GRAPH.md`, `TRACKER.md`, `QA_GATES.md`, `SECURITY_GATES.md`, and this
`G1_REVIEW.md` index the same current evidence.

**Handoff requirement:** the fresh R2c branch must be opened as a Zeus-signed
GitHub PR labeled `agent:zeus` against `main`. The PR body/Factory evidence must
name exact base `b260baea223e863b35fe561e6c5d3d77f3a914c9`, final head SHA,
status-output path, validation output, no-self-approval, no-merge, and no external
runtime execution. This R2c worker does not merge, deploy, change credentials,
write direct SQL, mutate the primary checkout, or touch any runtime/external/trading
path.

## Local documentary verification — non-approval

At `2026-08-10T04:50:09-04:00`, the implementation-planner worker verified the project-local pack from the assigned worktree only. `git ls-files --error-unmatch` confirmed the 14 required G1 documents plus `G0_REPOSITORY_STRATEGY.md`, `REQUIREMENTS_TRACEABILITY.md`, `DATABASE_AND_RUNTIME_CONTRACT.md`, and `G1_REVIEW.md` are tracked. `DOCUMENTATION_INDEX.md` indexes required documents and records explicit validated/reviewed status. `G0_REPOSITORY_STRATEGY.md` records the Zeus-only source repo, `origin/main` reference, assigned branch/worktree policy, PR-first delivery, and predecessor linkage. This is implementation evidence, not an independent specification/security PASS.

## Status
The required G1 pack is now documented as `reviewed: yes` for the R2u candidate using the independent PR #36/gate 794 review chain. This is documentation readiness only: downstream ALR-020+ work remains subject to its own task-specific RED→GREEN, security/no-egress, PR-first delivery and QA gates, and no runtime/product authority is granted by this record.

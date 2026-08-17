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

# SECURITY GATES

`DATABASE_AND_RUNTIME_CONTRACT.md` §§1–5 is the detailed acceptance contract. This gate lists the mandatory pass/fail evidence, not a weaker alternate design.

## Least-privilege gate
- Migration verifies all exact role attributes, zero role memberships, search path, per-object grants, `program_create`/`source_submit` leaf allowlist, `PUBLIC` revocations and default privileges from contract §1.
- A transaction as `alpha_research_runtime` proves each allowlisted operation works and every named direct-SQL denial in contract §1 fails. Catalog assertions prove no DML grant in other user schemas, no `PUBLIC` privilege in `alpha_research`, and the two lifecycle functions' `agent_admin` ownership, `SECURITY DEFINER`, fixed safe search path, exact signatures and execution grants.
- Direct lifecycle tests prove every permitted source→target edge and changed-column set, and deny direct update, unlisted edge, wrong/cross-owner actor, assumed role, mutable search path and all forbidden definer capabilities.
- Dedicated role secret is Infisical-only. Resolver accepts only the exact local DSN shape in contract §4; missing reference/role/allowlist fails before toolset or scheduler activation.

## Source/provenance gate
- Migration and handlers enforce the exact source classes, immutable persisted `source_reference`/`terms_evidence_reference`, terms states, freshness modes, max-age bounds, timestamp predicate, approval/revision provenance and uniqueness/supersession contract in §2.
- Direct SQL and handler suites execute every §2 negative case: source state combinations, immutable-reference mutations including admin attempts, incomplete/non-admin approval provenance, revision-audit mutation, stale/future/malformed time, duplicate, append-only evidence mutation/delete and lineage violation.
- Raw restricted content is never sent to generic memory or an external service. Provider fetch/parse code remains out of tree.

## Typed research-only gate
- `alpha_cards`, `research_reviews`, `inert_handoff_packages` and every JSON envelope implement the exact typed tuple/default/check/immutability contract in §3.
- Direct SQL and handler suites reject omitted/mutated/wrong tuples and every named validated/advice/approval/promotion/operation/activation/unknown field across all three persisted carriers and handoffs; field-by-field `alpha_card_create`, fixed `handoff_list` objects, payload/envelope count and type/bound checks are exact.
- Synthetic-canary tests prove the generic reference-only secret contract: no resolver/DSN/environment secret material appears in a persisted row, output, log, error, trace/span/metric or scheduler status, while fixed redacted errors remain deterministic.

## No-egress/tool isolation gate
- Default toolsets contain none of the ten handlers; the non-default leaf contains exactly `alpha_research_status`, `program_create`, `source_submit`, `evidence_record`, `alpha_card_create`, `alpha_card_review`, `cycle_start`, `cycle_close`, `inert_handoff_prepare`, `handoff_list`.
- Static scan covers every added/replacement line in every ALR-added or ALR-modified implementation diff file from a recorded, ancestor-verified base SHA; no selected-path exception is allowed. It rejects every §4 banned import/SQL pattern and unscannable changed file.
- Runtime harness executes all handlers and scheduler registration/run with outbound socket/HTTP/subprocess denial. Any attempt fails the test; only the exact local Postgres DSN is permitted.

## R2u documentation-status repair gate
- R2u modifies only project-local Markdown artifacts under `factory/projects/zeus-alpha-research-ledger-core/` and imports no runtime/control-plane code, provider dependency, network client, credential path, message connector, deployment path, trading/risk/paper/live behavior or external runtime authority.
- The reviewed G1 markers cite PR #36 head `c81547062c5362a7be6f5a1bb2ef9612b29bac9c` and Factory gate `794`; they are documentation-readiness evidence only and do not grant implementation permission outside the downstream task gates above.

## R2v control-plane repair gate
- R2v is limited to Factory control-plane/document-status and completion enforcement. It must not add runtime provider clients, credential paths, messaging connectors, deployment behavior, trading/risk/paper/live behavior, or product ledger implementation.
- The configured-base-ref status reader may inspect committed Git blobs from the verified origin base ref but must not checkout, fast-forward, merge, or mutate the primary checkout.
- The no-auto-integration guard is a fail-closed safety boundary for projects with `factory_auto_integration_forbidden=true`; such projects require PR-first independent QA rather than Factory branch-to-base integration.

## R2ah documentation-only security gate
- R2ah is limited to current-origin reviewed-marker/index documentation repair under `factory/projects/zeus-alpha-research-ledger-core/` and must not add or alter runtime provider clients, credential paths, messaging connectors, deployment behavior, trading/risk/paper/live behavior, product ledger implementation, or direct Factory DB writes.
- The exact base for this repair is `origin/main` `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7`; the fresh PR is a review handoff only and does not authorize merge, deploy, external runtime execution, or downstream ALR implementation.

## R2c2 documentation-only security gate
- R2c2 is limited to autonomous canonical G1 `document_status` evidence repair under `factory/projects/zeus-alpha-research-ledger-core/` and must not add or alter runtime provider clients, credential paths, messaging connectors, deployment behavior, trading/risk/paper/live behavior, product ledger implementation, or direct Factory DB writes.
- The exact base for this repair is `origin/main` `dbde1790f8d45f111bc69b3491a1862eafb29fa2`; the fresh PR is a review handoff only and does not authorize merge, deploy, external runtime execution, or downstream ALR implementation.

## R2c4 control-plane source-selection security gate
- R2c4 is limited to Factory `document_status` source identity and evidence docs; it must not add or alter runtime provider clients, credential paths, messaging connectors, deployment behavior, trading/risk/paper/live behavior, product ledger implementation, or direct Factory DB writes.
- The configured source for this repair is `origin/main` `2a32066398d500d6dac071bd7f2184d47bb3bcb4`; stale primary checkout HEAD `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1` is recorded only as rejected identity evidence and never as canonical readiness authority.
- Fail-closed behavior is mandatory when configured base identity cannot be verified. No fallback can clear G1 blockers from arbitrary worktree, PR, candidate, metadata, or stale-primary state.

## R2c5 documentation-only independent review security gate
- R2c5 is limited to project-local documentation/index/review-evidence under `factory/projects/zeus-alpha-research-ledger-core/` plus the approved Factory status/gate-record CLI evidence; it must not add or alter runtime provider clients, credential paths, messaging connectors, deployment behavior, trading/risk/paper/live behavior, product ledger implementation, the primary checkout, or direct Factory DB writes.
- The exact base for this review/repair is `origin/main` `91aa62b11f02f69d88f7d8c18c30033edb4b7355`; the fresh PR is a review handoff only and does not authorize merge, deploy, credential change, external runtime execution, or downstream ALR implementation.
- The live runtime mismatch (stale primary checkout at `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1` running the pre-R2v resolver) is evidence to document and route as bounded technical rework, never authority to mutate the primary checkout from this increment.

## R2c6 bounded current-origin resolver security gate
- R2c6 is limited to Factory control-plane G1 `document_status` resolution/readback and project-local evidence docs. It must not add or alter runtime provider clients, credential paths, messaging connectors, deployment behavior, trading/risk/paper/live behavior, product ledger implementation, production promotion, external runtimes, or direct Factory DB writes.
- The resolver may inspect committed Git blobs at the verified configured base ref and may read a separately checked-out candidate only after exact base branch/commit/ancestry, PR head, independent review, and clean artifact-state verification. It must not checkout, fast-forward, merge, write, or otherwise mutate the primary checkout.
- Fail-closed behavior is mandatory for unavailable paths, dirty or untracked artifacts, malformed candidate metadata, stale/base-mismatched candidates, missing independent review, and unreviewed document markers. Such candidates cannot clear G1 blockers.
- The exact current configured base for this repair is `origin/main` `40a188b23a384901f983e4d959d3ebbecf50b318`; primary checkout HEAD `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1` is recorded only as rejected identity evidence.

## R2am stale-primary Factory tick source-resolution security gate
- R2am is limited to Factory CLI/dashboard tick source resolution and project-local evidence docs. It must not add or alter runtime provider clients, credential paths, messaging connectors, deployment behavior, trading/risk/paper/live behavior, product ledger implementation, external runtimes, or direct Factory DB writes.
- Project tick must execute only the orchestrator script in the running `hermes_cli.factory` source tree and must force the subprocess import path to that same source root. It must not trust `~/.hermes/scripts/factory_orchestrator_tick.py` when that wrapper can point to a stale primary checkout.
- Fail-closed behavior is mandatory when the running Factory source provenance is malformed or when the source tree lacks the tick script. No fallback may execute a stale profile wrapper or clear G1 blockers from stale-primary code.
- The exact current configured base for this repair is `origin/main` `b525254809fba0ad46e6b7e9405778c44e64bae9`; primary checkout HEAD `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1` is recorded only as rejected identity evidence.

## G1 document-status technical recovery security gate
- This recovery is limited to current-origin documentation/provenance under `factory/projects/zeus-alpha-research-ledger-core/`. It must not add or alter runtime provider clients, credential paths, messaging connectors, deployment behavior, trading/risk/paper/live behavior, product ledger implementation, external runtimes, primary checkout state, or direct Factory DB writes.
- The exact current configured base for this recovery is `origin/main` `139df9ae49137bb4b16152550d53d385310de3b6`; primary checkout HEAD `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1` is recorded only as rejected identity evidence.
- If stale persisted anomaly metadata remains after current row-level `document_status` is non-blocking, the only authorized follow-up is a bounded Factory control-plane repair through reviewed code/PR/gates or approved Factory CLI gate evidence. No direct SQL, credential access, deploy, runtime call, or primary checkout fast-forward is authorized by this documentation task.

## R2aj isolated current-base G1 documentation evidence recovery security gate
- R2aj is limited to current-base documentation/provenance under `factory/projects/zeus-alpha-research-ledger-core/`. It must not add or alter runtime provider clients, credential paths, messaging connectors, deployment behavior, trading/risk/paper/live behavior, product ledger implementation, external runtimes, primary checkout state, or direct Factory DB writes.
- The exact current configured base for this recovery is `origin/main` `bf422968f9ea73d70d4ac1e8b8bae4af644ce079`; primary checkout HEAD `4eb87e4cd48105af05fe974cf1d493f0e1b57ae1` is recorded only as rejected identity evidence.
- Stale PR #44 and obsolete PR #20 checkout metadata are not current-base evidence. If stale persisted anomaly or dispatch-preflight projection metadata remains after row-level `document_status` is non-blocking, the only authorized follow-up is a bounded Factory control-plane repair through reviewed code/PR/gates or approved Factory CLI gate evidence. No direct SQL, credential access, deploy, runtime call, primary checkout fast-forward, external connector, messaging action, trading, risk mutation, paper/live activation, or self-approval is authorized by this documentation task.

## Scheduler gate
- `agent_core.alpha_research.scheduler.enabled` is false absent explicit configuration.
- Registration and each invocation call the contract §5 verifier without cache. Tests cover every false/missing/failed/expired/wrong-commit readiness component and prove no batch read/run follows `scheduler_not_ready`.

## Failure behavior
All gate failures are structured local rejections. No fallback can enable an external operation, shared runtime role or stale scheduler.

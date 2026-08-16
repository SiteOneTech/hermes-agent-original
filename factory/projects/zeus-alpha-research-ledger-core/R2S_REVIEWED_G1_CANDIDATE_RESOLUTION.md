---
document_type: control_plane_rework_evidence
project_id: zeus-alpha-research-ledger-core
increment: R2s
run_id: run-1786847076-2c2a569e
status: implemented
validated: yes
reviewed: yes
reviewed_by: quality-reviewer
review_evidence: factory_gate_795
---

# R2s — reviewed G1 candidate resolution evidence

## Scope

Bounded control-plane/document-status repair for the recurring `unvalidated_required_docs` anomaly. No product ALR work was dispatched, no merge to `main` was performed, no deploy was performed, no external runtime execution was performed, and no direct SQL write was used.

## Canonical reproduction

Command:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`

Pre-repair evidence:

`/home/jean/.hermes/profiles/claude-builder/cache/terminal-output/out-1786847156-4014464-b1d0.log`

Observed cause:

- `document_status` selected the primary checkout at `/home/jean/Projects/hermes-agent-original`.
- G1 rows had `readiness_source=primary`, `validated=true`, `committed=true`, `indexed=true`, but `reviewed=false`, so the rows were blocking.
- The exact independently reviewed PR #36 candidate existed only in canonical Factory task/gate evidence, not in `project.metadata.reviewed_g1_candidate`.
- The durable candidate review evidence was Factory gate `794` for PR #36 head `c81547062c5362a7be6f5a1bb2ef9612b29bac9c`, base `df4c77fd1413a65cdb85885a06978ff157c1de4d`, reviewer `solution-architect`, branch `factory/zeus-alpha-research-ledger-core/inc-001-r2r-pr-first-recovery-of-the-r2q`.
- A secondary parser issue made candidate `TASK_GRAPH.md` vulnerable to embedded historical prose such as `reviewed=false` overriding the document's own frontmatter/status marker.

## Repair

- `project_document_status()` now accepts canonical Factory `tasks` and `gates` rows from `factory status` and synthesizes a reviewed candidate only when all of these hold:
  - review gate status is passed/approved/success;
  - gate type is a review gate (`architecture`, `quality`, `security`, `spec`, `test`);
  - matching task is terminal-positive, not stale/superseded;
  - gate notes identify an OPEN PR, `agent:zeus`, Zeus author/sign-off, PR number, exact head SHA, and optional base SHA;
  - reviewer is independent from task owner;
  - git readback verifies candidate path, branch, HEAD SHA, cleanliness, artifact cleanliness, and base merge relationship.
- Stale/unreviewed/merged/closed/self-reviewed/mismatched candidates fail closed.
- Explicit document status markers are resolved from the document header before index/prose text so candidate frontmatter can win over embedded historical primary-readback prose.

## Post-repair canonical status

Command:

`/home/jean/Projects/hermes-agent-original/venv/bin/python3 -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json`

Post-repair evidence:

`/home/jean/.hermes/profiles/claude-builder/cache/terminal-output/out-1786848537-4014464-b290.log`

Observed result:

- G1 `document_status` rows use `readiness_source=reviewed_candidate`.
- Candidate fields are `candidate_pr_number=36`, `candidate_sha=c81547062c5362a7be6f5a1bb2ef9612b29bac9c`, `candidate_base_sha=df4c77fd1413a65cdb85885a06978ff157c1de4d`, `candidate_review_evidence_ref=factory_gate_794`, `candidate_reviewer=solution-architect`.
- G1 rows shown in the project `document_status` section are `blocking=false`.

## Tests

RED evidence:

- Gate-backed candidate test failed before implementation: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'factory_gate_candidate or factory_gate_candidates or latest_open_reviewed' -v --tb=short`.
- Frontmatter/parser regression failed before parser fix: `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py -k 'frontmatter_wins_over_embedded_primary_readback_false' -v --tb=short`.

GREEN evidence:

- `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory.py --tb=short` -> 150 passed.
- `git diff --check` -> passed.

## PR and review

- Delivery PR: https://github.com/SiteOneTech/hermes-agent-original/pull/37
- Initial implementation head: `a25562f37a1fa79e4acd4b6dc998b81d49f4f7f2`
- Base: `df4c77fd1413a65cdb85885a06978ff157c1de4d`
- PR label: `agent:zeus`
- Commit signature: `Signed-off-by: Zeus <zeus@sitiouno.com>`
- Independent quality review: Factory gate `795`, reviewer `quality-reviewer`, PASS.
- Implementation evidence gate: Factory gate `796`, reviewer `claude-builder`, PASS.

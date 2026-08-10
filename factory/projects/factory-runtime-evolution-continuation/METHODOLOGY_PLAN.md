# Methodology Plan — Factory Runtime Evolution — Continuation

| Field | Value |
|---|---|
| Document status | validated: true (implementation-planner, 2026-08-10); reviewed: false — assigned to `solution-architect` |

## 1. Methodology

Hybrid Factory methodology, following the operating canon
(`factory-agent-operating-canon`) and the predecessor's proven flow:

- **G0 Repository Strategy** — passed at project creation (event 172950). All
  deliverables use branch prefix `factory/factory-runtime-evolution-continuation/` and
  per-deliverable worktrees under `/home/jean/Projects/.worktrees/...`.
- **G1 Documentary Readiness** — this increment (FRE-010) delivers the full required
  pack. No code increment may become claimable before G1 blocks clear
  (exists + indexed + committed + validated + reviewed).
- **TDD increments** — every downstream increment follows RED→GREEN→REFACTOR with the
  regression test committed in the same increment as the fix (see `QA_GATES.md`).
- **Owner/reviewer separation** — planner/planners own increments; reviewers are
  independent roles (quality-reviewer, security-reviewer, solution-architect,
  qa-verifier, devops-release as assigned in `TASK_GRAPH.md`).
- **PR-first delivery** — branch/worktree per increment, push to
  `SiteOneTech/hermes-agent-original` after local validation, merge to `main` only after
  the increment's gates pass (review + QA/security where applicable).
- **Evidence discipline** — every completed task records real commands + output; no
  fabricated tests, commits, gate IDs, or API responses.

## 2. Increment lifecycle (per downstream increment)

1. Kickoff: read `DOCUMENTATION_INDEX.md` + relevant G1 docs + task acceptance criteria
   from Factory DB.
2. RED: write the failing regression test(s) reproducing the exact gap; run
   `scripts/run_tests.sh tests/hermes_cli/test_<file>.py -k <test>` and capture the FAIL.
3. GREEN: implement the minimal change in `hermes_cli/` and/or `scripts/factory/`; run
   the same test; capture the PASS.
4. REFACTOR: clean up; run the focused file + the broader factory test set
   (`tests/hermes_cli/test_factory*.py`).
5. Docs: update SPRINT_PLAN/TASK_GRAPH/TRACKER/QA or SECURITY gates/DELIVERY_REPORT in
   the same commit.
6. Gate: record gates via `hermes factory gate record` (or the Factory tool equivalent)
   with real evidence; commit; push branch.
7. Review: independent reviewer (assigned per task) checks the exact diff + test
   evidence + acceptance criteria; reviewer gate recorded.
8. Merge to `main` after all gates pass; push `main`; record the merge commit in
   DELIVERY_REPORT/CHANGE_RECORDS.

## 3. Verification commands (standard)

```bash
# Python tests (CI parity — always the wrapper, never bare pytest)
scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py
scripts/run_tests.sh tests/hermes_cli/test_factory_cron_control_plane.py
scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py
scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py

# Factory DB status (read-only)
hermes factory status factory-runtime-evolution-continuation --json

# Cron evidence (after FRE-013/017 resume, via wrappers)
hermes cronjob list
```

## 4. Definition of Ready (DoR) for a downstream increment

- [ ] Increment task exists in Factory DB with owner, reviewer, phase, acceptance
  criteria, branch, worktree path.
- [ ] G1 blockers for this project are cleared (or a Jean-authorized exception exists).
- [ ] RED test(s) identified and reproducible.
- [ ] No product-runtime code without a TDD increment.

## 5. Definition of Done (DoD) for a downstream increment

- [ ] RED test failed before implementation (evidence captured).
- [ ] GREEN after minimal change (evidence captured).
- [ ] Focused + sibling factory test files pass (real output).
- [ ] Project-local docs updated and committed with the code.
- [ ] Branch pushed; reviewer gate passed; QA/security gates passed where assigned.
- [ ] Merge to `main` + push performed only after gates; delivery evidence recorded.
- [ ] `hermes factory status` shows the task closed with evidence and no new anomalies.

## 6. Gate policy

| Gate | Applies to | Owner | Fail-closed behavior |
|---|---|---|---|
| G0 repository strategy | all increments | factory-orchestrator | no dispatch if missing fields |
| G1 documentary readiness | all increments | factory-orchestrator | no implementation if blockers |
| Review gate | every increment | assigned reviewer | rework if evidence insufficient |
| QA gate | code increments | qa-verifier | rework if tests fail / missing |
| Security gate | code increments | security-reviewer | rework/block if escalation allowlist or authz affected |
| Delivery gate | closing increments | devops-release | refuse if evidence or gates missing |

No suppression/waiver of these gates is allowed without Jean's explicit authorization
for the exact project (ADR-010-6).

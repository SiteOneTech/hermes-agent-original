# SPRINT_PLAN — Sales Operator Core / Revenue Operator v2

Detailed historical sprint plan: `website/docs/developer-guide/sales-operator-core/SPRINT-PLAN-001.md`.

## I9 sprint goal

Rebaseline the Factory control pack and downstream task graph for the authorized **Revenue Operator v2 private Kidu cockpit**: a private read-only dashboard that uses safe snapshots, distinguishes real/synthetic data, shows freshness and outcomes, supervises policy/no-send state, and does not enable external sends.

## I9 sprint constraints

- No provider enablement.
- No `auto_send`.
- No cold WhatsApp.
- No execution of external actions from the browser.
- No credentials/secrets in UI snapshots or artifacts.
- No synthetic metrics reported as real outcomes.
- Sandbox/Kidu review only; production remains HOLD until Jean explicitly approves a later gate.

## Planned phases and handoff

| Phase | Owner | Input | Output | Verification / done |
|---|---|---|---|---|
| planning (I9 G1 rebaseline) | implementation-planner | Existing G1 docs, Factory task acceptance, Agent Core Factory status | Updated PRD/ADRS/TECHNICAL_BLUEPRINT/SPRINT_PLAN/TASK_GRAPH/QA_GATES/SECURITY_GATES/TRACKER/DOCUMENTATION_INDEX | Content checks prove I9, no-send, safe snapshots, no credentials, and synthetic-vs-real rules are documented. |
| implementation | builder (assigned by Zeus) | Updated control pack and assigned worktree/branch | Private Kidu cockpit implementation and safe snapshot/export surface | Local build/tests plus snapshot validation; no external sends. |
| quality_review | quality-reviewer | Implementation diff, docs, tests, snapshot samples | Spec/quality review result | Confirms UI satisfies I9 requirements and no unrelated scope. |
| security_review | security-reviewer | Diff, artifacts, snapshot data, resolved UI behavior | Security gate result | Confirms no credentials, no browser send path, no provider enablement, and no synthetic-as-real metrics. |
| deploy | devops-release | Reviewed build artifact and sandbox contract | Kidu sandbox deployment only | Sandbox URL/evidence under `/srv/factory/projects/<project>` or approved Kidu equivalent; production HOLD. |
| QA browser/post-deploy | qa-verifier | Sandbox URL, snapshot artifact, QA gates | Browser QA evidence and post-deploy report | Browser checks verify private cockpit rendering, freshness, real/synthetic labels, policy/no-send supervision, and no action execution controls. |
| delivery report | factory-reporter / Zeus | Gate evidence, commits, sandbox QA, blockers | Delivery report and Factory evidence | Report states branch/commit, commands, sandbox URL if deployed, remaining blockers, and production/no-send status. |

## Definition of done for I9 planning increment

- Control pack docs named in acceptance criteria describe Revenue Operator v2 private Kidu cockpit and no-send boundary.
- TASK_GRAPH includes the mandatory UI phases: implementation, quality_review, security_review, deploy, QA browser/post-deploy, and delivery report.
- QA/SECURITY gates define failure conditions for credentials in snapshots, provider/auto-send activation, browser-triggered sends, stale/missing freshness, and synthetic metrics counted as real.
- Tracker records current state and handoff to solution-architect review.

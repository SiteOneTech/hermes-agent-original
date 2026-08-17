---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2bb-current-base-g1-status-proj
phase: documentation
status: implemented_pending_independent_review
validated: yes
reviewed: pending_independent_quality_review
owner: codex-builder
engine: codex
run_id: run-1786969303-1e25bbda
base_ref: origin/main
current_origin_sha: b05afe59c88cfa7f7dbec0117603b2f052267ce0
pr63: https://github.com/SiteOneTech/hermes-agent-original/pull/63
pr63_base_sha: 52df8d7c6599e3ec2ec4559e0139ffd91ec74011
pr63_head_sha: dcd9c74f252d288269d746ab59079a0221de7a46
branch: factory/zeus-alpha-research-ledger-core/inc-018-r2bb-current-base-g1-status-proj
worktree: /home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2bb-current-base-g1-status-proj
factory_status_json: /tmp/r2bb-status-final.json
---

# R2bb — current-base G1 status projection and PR #63 evidence recovery

## Scope and boundary

This increment repairs only Factory CLI status evidence readback for the current-base G1 status projection after PR #63 / R2aw reached `origin/main`.

It does not implement Alpha Research Ledger runtime/product features, does not mutate `/home/jean/Projects/hermes-agent-original`, does not merge, deploy, change credentials, contact external runtimes, activate connectors/messaging, trade, mutate risk/paper/live state, or write direct SQL to `factory.*`. Live Factory DB use stayed limited to the approved CLI status path.

## Canonical inputs read

- `DOCUMENTATION_INDEX.md` — current G1 entrypoint, reading order, R2au/R2av/R2aw lineage and source-of-truth rule.
- `FACTORY_INTAKE.md` and `G0_REPOSITORY_STRATEGY.md` — Zeus-only scope, PR-first delivery, stale-primary boundary and no runtime propagation.
- `TECHNICAL_BLUEPRINT.md`, `TASK_GRAPH.md`, and `TRACKER.md` — private local ledger architecture, status/projection lineage, and downstream implementation blockers.
- `QA_GATES.md` and `SECURITY_GATES.md` — RED/GREEN, exact-SHA PR handoff, no-direct-SQL/no-primary-mutation/no-external-runtime gates.
- `R2AW_ISOLATED_CURRENT_ORIGIN_FACTORY_G1_STATUS_RECOVERY.md` and GitHub PR #63 — prior repair/evidence for isolated-worktree status source delegation.
- `R2AU_CURRENT_ORIGIN_G1_DOCUMENT_STATUS_PROJECTION_REPAIR.md`, `R2AV_CURRENT_ORIGIN_G1_STATUS_PROJECTION_RECOVERY.md`, `R2AO_CURRENT_ORIGIN_G1_CONTROL_PLANE_PROJECTION_REPAIR.md`, `G1_DOCUMENT_STATUS_TECHNICAL_RECOVERY.md`, and `R2C6_BOUNDED_CURRENT_ORIGIN_G1_RESOLVER_READBACK_RECOVERY.md` — controlling stale-primary/current-origin G1 projection lineage.

## Immutable current-base and PR #63 readback

Read-only Git evidence from the assigned isolated worktree after `git fetch origin main`:

```text
branch=factory/zeus-alpha-research-ledger-core/inc-018-r2bb-current-base-g1-status-proj
HEAD=b05afe59c88cfa7f7dbec0117603b2f052267ce0
origin/main=b05afe59c88cfa7f7dbec0117603b2f052267ce0
merge-base=b05afe59c88cfa7f7dbec0117603b2f052267ce0
remote-main=b05afe59c88cfa7f7dbec0117603b2f052267ce0
primary-main=4eb87e4cd48105af05fe974cf1d493f0e1b57ae1
primary-status=main...origin/main [ahead 3, behind 1692]
```

GitHub PR #63 readback:

```text
number=63
state=MERGED
isDraft=false
url=https://github.com/SiteOneTech/hermes-agent-original/pull/63
baseRefName=main
baseRefOid=52df8d7c6599e3ec2ec4559e0139ffd91ec74011
headRefName=factory/zeus-alpha-research-ledger-core/inc-001-r2aw-isolated-current-origin-fac
headRefOid=dcd9c74f252d288269d746ab59079a0221de7a46
labels=["agent:zeus"]
title=fix(factory): prefer isolated source for G1 status tick
```

`git log --oneline --max-count=2` confirms `origin/main` `b05afe59c8` is the merge commit for R2aw/PR #63 and contains repair commit `dcd9c74f25`.

## Discrepancy reproduced

The stale human/Factory assignment projection still presented G1 as `unvalidated_required_docs` with 10 required documents missing reviewed evidence. The current canonical CLI readback from this isolated current-base worktree does not support that blocker:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2bb-status-before.json
```

Parsed pre-repair status summary:

```text
g1_count=14
g1_blocking_count=0
readiness_sources=["configured_base_ref"]
base_commits=["b05afe59c88cfa7f7dbec0117603b2f052267ce0"]
primary_heads=["4eb87e4cd48105af05fe974cf1d493f0e1b57ae1"]
primary_accepted=[false]
reconciliation_anomalies=[]
reconciliation_projection_source="current_document_status"
has_g1_documentation_checkout=false
has_stale_reconciliation_projection=false
```

Therefore the discrepancy is stale projection/evidence readback, not current document content. The remaining evidence gap was that delegated Factory status JSON did not report which source root produced the status payload, making PR #63's isolated-source guarantee hard to verify from the payload itself.

## RED evidence

Focused RED test added before the repair:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k status_prefers_isolated_cwd_source_over_stale_running_module -v --tb=short
```

Result before implementation: 1 selected test failed with `KeyError: 'factory_cli_source_root'`. The existing delegated status path correctly used the isolated cwd source, but the JSON payload did not expose deterministic status-source provenance.

## Repair

`hermes_cli/factory.py` now annotates Factory status JSON payloads with status-source provenance:

- `factory_cli_source_root`
- `factory_status_source_root`
- `factory_status_delegated`
- `factory_status_delegated_from_source_root` when a stale running module delegates to an isolated cwd source

The delegated subprocess output is parsed only for JSON mode and falls back to the previous stdout/stderr passthrough if the payload is not JSON. Direct status readback from this worktree reports `factory_status_delegated=false` and the assigned worktree as the source root.

## GREEN/current readback evidence

Targeted GREEN:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k status_prefers_isolated_cwd_source_over_stale_running_module -v --tb=short
```

Result: 1 selected test passed, 0 failed.

Current Factory status readback after the repair:

```text
/home/jean/Projects/hermes-agent-original/venv/bin/python -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r2bb-status-final.json
```

Parsed result:

```text
factory_cli_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2bb-current-base-g1-status-proj
factory_status_source_root=/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-018-r2bb-current-base-g1-status-proj
factory_status_delegated=false
g1_count=14
g1_blocking_count=0
readiness_sources=["configured_base_ref"]
base_commits=["b05afe59c88cfa7f7dbec0117603b2f052267ce0"]
primary_heads=["4eb87e4cd48105af05fe974cf1d493f0e1b57ae1"]
primary_accepted=[false]
reconciliation_anomalies=[]
reconciliation_projection_source="current_document_status"
has_g1_documentation_checkout=false
has_stale_reconciliation_projection=false
```

All 14 required G1 rows read back `exists=true`, `indexed=true`, `committed=true`, `validated=true`, `reviewed=true`, `blocking=false` from `readiness_source=configured_base_ref`, while the stale primary checkout remains rejected at `primary_head=4eb87e4cd48105af05fe974cf1d493f0e1b57ae1`.

## Delivery handoff

The final candidate head SHA cannot be written into the same commit that contains this file without changing the SHA. It must be recorded in the Zeus-signed PR body and final worker evidence after commit creation and push. The PR must be non-draft, target `main`, carry label `agent:zeus`, name base `b05afe59c88cfa7f7dbec0117603b2f052267ce0`, name PR #63 base/head evidence above, include RED/GREEN/status readback evidence, and request independent exact-SHA review. This worker must not self-approve, merge, deploy, direct-SQL mutate, mutate primary checkout, change credentials, contact external runtimes, or perform trading/risk/paper/live actions.

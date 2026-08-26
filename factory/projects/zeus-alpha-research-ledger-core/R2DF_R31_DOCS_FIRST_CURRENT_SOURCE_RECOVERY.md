---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-r2df-r31-docs-first-current-source-recov
run_id: run-1787780808-91b168f7
phase: g1_recovery
status: implementation_candidate
owner: codex-builder
validated: yes
reviewed: pending
---

# R2df-R31 — docs-first current-source recovery after R28 premature integration

## Scope and boundaries

This artifact records the bounded Factory control-plane repair for R2df-R31. It does not authorize merge, deploy, credential changes, external runtime/messaging access, ALR/product dispatch, trading/risk/paper/live activity, or direct Factory DB mutation. The work was performed only in the assigned worktree:

`/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-07-r2df-r31-docs-first-current-sour`

Factory DB readback used the allowed Factory CLI path only. No direct SQL was used.

## Canonical documents read before implementation

- `factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-alpha-research-ledger-core/FACTORY_INTAKE.md`
- `factory/projects/zeus-alpha-research-ledger-core/G0_REPOSITORY_STRATEGY.md`
- `factory/projects/zeus-alpha-research-ledger-core/DATABASE_AND_RUNTIME_CONTRACT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md`
- `factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md`
- `factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md`

## Diagnosis

The failing source-root path is the primary-main Factory CLI path behind `/home/jean/Projects/hermes-agent-original/venv/bin/hermes`. A primary checkout on branch `main` can be non-current relative to configured `origin/main` not only when it is a strict ancestor, but also when local commits make it ahead or diverged. Before this repair, `_preferred_configured_base_source_root()` delegated to a clean configured-base worktree only when `running_head` was an ancestor of `origin/main`; ahead/diverged primary-main states returned `None`. `_resolve_orchestrator_script()` then only failed closed for the strict-behind predicate and otherwise allowed tick dispatch from the non-current primary source.

That predicate kept the canonical H path on stale/diverged primary source, so its G1 document readback stayed red and a forced tick could return `claimed=null` even when a dependency-free docs/G1 recovery was the intended next claim. The RED regression now models that exact failure: a diverged primary `main` script returns a red G1 diagnostic and `claimed=None`, while the verified configured-base source has the docs/G1 recovery claim.

## Repair

The repair is intentionally small and source-provenance scoped:

- `hermes_cli/factory.py` now identifies configured-base primary source by normalized branch name (`main` from `origin/main`, `refs/heads/main`, or `refs/remotes/origin/main`) rather than by strict ancestor-only topology.
- When running from primary `main` and `HEAD != origin/main`, status/tick/project resolver actions may use only a complete, clean worktree whose `HEAD` exactly equals configured `origin/main`.
- Isolated feature worktrees remain local because their branch does not normalize to the configured base branch.
- Tick dispatch fails closed if primary `main` is non-current and the configured-base source is unavailable or dirty; it does not fall back to stale/ahead/diverged primary code.

This does not integrate any source increment and does not treat failed, empty, or HTTP-429 provider review output as approval. The existing review-runtime fail-closed tests remain part of the focused verification.

## RED / GREEN evidence

RED regression, before implementation:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k test_project_tick_prefers_configured_base_source_when_primary_main_is_diverged -v --tb=short
Result: FAILED. TypeError: 'NoneType' object is not subscriptable because the diverged-primary tick path returned claimed=None.
```

Fail-closed RED, before the second repair step:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -k test_project_tick_fails_closed_when_primary_main_diverged_and_configured_base_source_is_dirty -v --tb=short
Result: FAILED. The tick attempted to run from diverged/dirty source instead of raising a configured-base source RuntimeError.
```

GREEN focused verification:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_orchestrator_tick.py -v --tb=short
Result: 25 tests passed, 0 failed.
```

Provider-failure / docs-first focused guard verification:

```text
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python3 scripts/run_tests.sh tests/hermes_cli/test_factory_increment_integration.py -k 'r2df_r23 or docs_repair or g1_recovery or review_429_log or provider_failure or 429_rate_limit or wrapped_token_plan_terminal_failure' -v --tb=short
Result: 7 tests passed, 0 failed.
```

Static diff hygiene:

```text
git diff --check
Result: exit 0.
```

## Factory CLI readback evidence

Pre-repair H-path snapshot saved to `/tmp/r2df-r31-h-status-before.json` showed:

```json
{
  "db_backend": "agent_core_postgres",
  "factory_cli_source_root": null,
  "factory_status_source_root": null,
  "factory_status_delegated": null,
  "active_runs": 1,
  "g1_required": 14,
  "g1_blockers": 10,
  "blocking_files": [
    "FACTORY_INTAKE.md",
    "REQUIREMENTS_ANALYSIS.md",
    "PATTERN_ANALYSIS.md",
    "ASSUMPTIONS_AND_OPEN_QUESTIONS.md",
    "PRD.md",
    "ADRS.md",
    "METHODOLOGY_PLAN.md",
    "TECHNICAL_BLUEPRINT.md",
    "TASK_GRAPH.md",
    "SECURITY_GATES.md"
  ],
  "reconciliation_anomalies": ["unvalidated_required_docs"],
  "current_task": {"status": "running", "phase": "g1_recovery", "priority": -7}
}
```

Post-candidate allowed Factory CLI status saved to `/tmp/r2df-r31-status-after.json` before recording the implementation gate showed:

```json
{
  "db_backend": "agent_core_postgres",
  "factory_cli_source_root": "/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-07-r2df-r31-docs-first-current-sour",
  "factory_status_source_root": "/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-07-r2df-r31-docs-first-current-sour",
  "factory_status_delegated": false,
  "active_runs": 1,
  "g1_required": 14,
  "g1_blockers": 0,
  "reconciliation_anomalies": [],
  "projection_source": "current_document_status",
  "current_task": {
    "status": "running",
    "phase": "g1_recovery",
    "priority": -7,
    "owner_profile": "codex-builder",
    "reviewer_profile": "quality-reviewer"
  }
}
```

The active run is this assigned R2df-R31 run; no new increment was opened.

After recording the allowed Factory implementation gate (`factory gate record`) the readback saved to `/tmp/r2df-r31-status-after-gate.json` showed:

```json
{
  "db_backend": "agent_core_postgres",
  "factory_cli_source_root": "/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-07-r2df-r31-docs-first-current-sour",
  "factory_status_source_root": "/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-07-r2df-r31-docs-first-current-sour",
  "factory_status_delegated": false,
  "active_runs": 0,
  "g1_required": 14,
  "g1_blockers": 0,
  "reconciliation_anomalies": [],
  "current_task": {"status": "cancelled", "phase": "g1_recovery", "priority": -7},
  "implementation_gate": {
    "gate_id": 1109,
    "status": "passed",
    "reviewer": "codex-builder",
    "candidate_sha": "346ee7dc171c8fa9e58b384ddda848dd643e081c",
    "pr": "https://github.com/SiteOneTech/hermes-agent-original/pull/132"
  }
}
```

The final task status is preserved as Factory DB readback, not rewritten directly by this worker. The implementation gate is evidence only; it is not the independent exact-SHA quality review required for final approval.

## Delivery contract

Delivery remains PR-first. Required closeout is a Zeus-signed `agent:zeus` PR from branch `factory/zeus-alpha-research-ledger-core/inc-07-r2df-r31-docs-first-current-sour`, followed by independent exact-SHA review. This artifact is implementation evidence only and is not self-approval.

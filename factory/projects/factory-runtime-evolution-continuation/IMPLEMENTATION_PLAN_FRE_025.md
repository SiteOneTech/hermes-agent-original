# FRE-025 Factory Successor Control Implementation Plan

> **For Hermes:** Execute this plan as one isolated Factory increment with TDD and independent review.

**Goal:** Prevent a repaired Factory project from leaving its authorized successor unsupervised or incorrectly terminal, while preserving explicit human pauses and a single global dispatcher.

**Architecture:** Persist successor intent in Agent Core Postgres rather than inferring it from queue position or prose. A lease-backed global tick is the only mutating dispatcher; the watchdog becomes observational. Successor activation is staged (`declared → eligible → dispatching → activated`), and only occurs after the predecessor has reconciled with source delivery verified in `origin/<base>`.

**Tech Stack:** Python 3.11, `hermes_cli.factory_pg`, PostgreSQL `factory` schema, current Factory cron scripts, pytest.

---

### Task 1: Persist the successor and global lease contracts

**Files:**
- Add: `db/modules/factory/000004_successor_control.sql` (new versioned migration; do not amend deployed `000003`)
- Modify: `hermes_cli/factory_pg.py`
- Test: `tests/hermes_cli/test_factory_successor_control.py`

**Acceptance:** Idempotent schema creates `factory.project_successions` and `factory.runtime_leases`; lease acquisition is atomic and expiry-safe; succession declaration requires explicit owner authorization and reason.

### Task 2: Test eligibility before state mutation

**Files:**
- Modify: `hermes_cli/factory_pg.py`
- Test: `tests/hermes_cli/test_factory_successor_control.py`

**Acceptance:** A successor remains inactive when the predecessor is unintegrated, when the successor has an unapproved manual pause, or while a human question / readiness blocker exists. Eligible succession records are auditable and deterministic.

### Task 3: Make the global tick the only mutating dispatcher

**Files:**
- Modify: `hermes_cli/factory_pg.py`
- Modify: `scripts/factory/factory_orchestrator_tick.py`
- Modify: `scripts/factory/factory_watchdog_alerts.py`
- Test: `tests/hermes_cli/test_factory_orchestrator_tick.py`
- Test: `tests/factory/test_factory_watchdog_alerts.py`

**Acceptance:** A held global lease makes a second tick skip without claiming work. The tick performs monitor/reconcile/succession eligibility/claim in order. The watchdog does not write Factory state or launch a competing supervisor.

### Task 4: Make activation evidence post-spawn and rollback-safe

**Files:**
- Modify: `hermes_cli/factory_pg.py`
- Modify: `scripts/factory/factory_orchestrator_tick.py`
- Test: `tests/hermes_cli/test_factory_orchestrator_tick.py`

**Acceptance:** A succession is marked `activated` only after `mark_run_spawned`; a spawn failure returns it to `eligible` with an audit event and no false completion.

### Task 5: Verify the actual Alpha handoff only after code delivery is integrated

**Files:**
- Modify: `factory/projects/factory-runtime-evolution-continuation/RETROSPECTIVE_FRE_025.md`

**Acceptance:** Document exact audit findings, migration/readback, test output, independent review, exact source SHA / PR, and the separate post-integration operation required to register the Factory Runtime → Alpha research-only succession. No trading/risk/capital/Vonash action is enabled.

## Verification

```bash
HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python \
  scripts/run_tests.sh \
    tests/hermes_cli/test_factory_successor_control.py \
    tests/hermes_cli/test_factory_orchestrator_tick.py \
    tests/hermes_cli/test_factory_control_plane_refactor.py \
    tests/hermes_cli/test_factory_increment_integration.py \
    tests/hermes_cli/test_factory_cron_control_plane.py \
    tests/factory/test_factory_watchdog_alerts.py

git diff --check
```

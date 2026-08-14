# QA Gates — Factory Runtime Evolution — Continuation

| Field | Value |
|---|---|
| Document status | baseline reviewed:true (solution-architect, 2026-08-10, planning gate 690); FRE-025 amendment validated:true (implementation owner, 2026-08-12), reviewed:pending |

## 1. General QA principles (repo canon)

- Run Python tests ONLY via `scripts/run_tests.sh` (CI parity: hermetic env, TZ=UTC,
  LANG=C.UTF-8, per-file subprocess isolation). Never bare `pytest`.
- No change-detector tests (catalog snapshots, config version literals, enumeration
  counts). Assert behavior and invariants.
- No tests that read source files. Extract logic into testable functions.
- No fake host OS. Use `@pytest.mark.linux_only` etc. when a test genuinely depends on
  the host.
- E2E over mocks for resolution chains/config propagation/security boundaries: exercise
  real imports against a temp `HERMES_HOME` where applicable.
- Tests must never write to `~/.hermes/` (autouse `_isolate_hermes_home` fixture).

## 2. FRE-010 (this increment) QA gate

Scope: documentation-only; no runtime code. QA gate = documentary verification:

| Check | Command / method | Expected |
|---|---|---|
| 14 required docs exist | `ls factory/projects/factory-runtime-evolution-continuation/` | all 14 files present |
| Docs indexed | `DOCUMENTATION_INDEX.md` §1 | every file listed with status |
| Evidence anchored in runtime | grep line references `factory_pg.py:…` resolve at baseline | citations resolve (verify manually or `git grep`) |
| Docs committed on branch | `git status` / `git log` in worktree | clean tree after commit; docs in branch diff |
| Acceptance criteria coverage | `TASK_GRAPH.md` §3 mapping | all 4 criteria mapped |
| No paused projects treated as incidents | `PATTERN_ANALYSIS.md` §2 note | explicit exclusion statement |

## 3. Downstream increments QA gates (FRE-011…FRE-017)

| Increment | Test command | Expected |
|---|---|---|
| FRE-011 | `scripts/run_tests.sh tests/hermes_cli/test_factory_control_plane_refactor.py` | RED captured before change; GREEN after; file green |
| FRE-011 siblings | `scripts/run_tests.sh tests/hermes_cli/test_factory.py tests/hermes_cli/test_factory_orchestrator_tick.py` | green |
| FRE-012 | `scripts/run_tests.sh tests/hermes_cli/test_factory_escalation_validation.py` | RED→GREEN captured |
| FRE-013 | `scripts/run_tests.sh tests/hermes_cli/test_factory_cron_control_plane.py` | green; watchdog idle-silence asserted |
| FRE-014 | `scripts/run_tests.sh tests/hermes_cli/test_factory_project_reopen.py` + CLI smoke `hermes factory project reopen --help` | green; CLI registered |
| FRE-015 | `scripts/run_tests.sh tests/hermes_cli/test_factory*.py` (full factory set) | all green or documented pre-existing failures |
| FRE-017 | cron smoke per script + `hermes cronjob list` | exit 0; no unexpected alerts; evidence file |
| FRE-025 RED/GREEN | exact behavior-test node selection via the explicitly required venv Python | meaningful RED, then identical selection GREEN |
| FRE-025 focused | `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python scripts/run_tests.sh tests/hermes_cli/test_factory_successor_control.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_cron_control_plane.py tests/factory/test_factory_watchdog_alerts.py` | all pass |
| FRE-025 hygiene | `git diff --check` | no output; exit 0 |
| FRE-027 RED/GREEN | missing-000004 readiness, orchestrator preflight, and module-scoped migration CLI selections via `scripts/run_tests.sh` | meaningful RED, then focused GREEN |
| FRE-027 focused | `HERMES_PYTHON=/home/jean/Projects/hermes-agent-original/venv/bin/python scripts/run_tests.sh tests/hermes_cli/test_factory_successor_control.py tests/hermes_cli/test_factory_orchestrator_tick.py tests/hermes_cli/test_factory_control_plane_refactor.py tests/hermes_cli/test_factory_increment_integration.py tests/hermes_cli/test_factory_cron_control_plane.py tests/factory/test_factory_watchdog_alerts.py tests/scripts/test_agent_core_db_migrations.py tests/hermes_cli/test_agent_core_sql.py tests/hermes_cli/test_factory.py` | all pass |
| FRE-027 scripts/roles | `scripts/run_tests.sh tests/scripts/test_agent_core_roles.py`; `python3 -m py_compile ...`; `git diff --check`; `agent_core_db.py migrate/verify --help` | pass; module-scoped migration path advertised |

## 4. Evidence capture rules

- Record: command, real output (truncated to the relevant section), exit code,
  timestamp, run/task id.
- RED evidence must show the exact failing assertion; GREEN evidence must show the same
  test passing after the change.
- FLAKY results (`⚠ FLAKY` from the runner) are a bug to fix, not evidence to accept.
- Never fabricate output; if a check cannot run (missing dependency/env), report BLOCKER.

## 5. QA ownership

- qa-verifier owns live smoke/E2E evidence (FRE-015/017); quality-reviewer owns spec
  compliance review of diffs; both are independent of the increment owner.
- A QA gate that cannot be satisfied blocks merge (fail-closed), with a concrete rework
  list.

## 6. FRE-025 behavioral acceptance

- Manual pause rejects missing/blank reason, actor, or origin and all reserved Factory
  system actors, while persisting explicit human/operator authority and audited origin.
- Technical/dependency hold remains supervisable, clears manual-pause markers, emits a
  distinct event, and refuses to downgrade `manual_attention`.
- Bootstrap repair is recognized only from explicit structured metadata; title and
  description prose cannot exempt source integration.
- An unintegrated positive terminal source-bearing task creates a reconciliation and
  delivery blocker and prevents queued-successor auto-resume.
- Strong integration evidence, an explicit Jean-authorized waiver, and legitimate
  non-source documentation/reconciliation tasks remain accepted.
- Successor activation is explicit and lease-owned: queue position or project prose cannot
  activate a successor, and watchdog observations cannot spawn a competing mutator.
- Tests assert public behavior and state/event contracts; no source-text snapshots are
  used.

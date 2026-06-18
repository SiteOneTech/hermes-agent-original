"""Regression tests for the canonical Factory cron/control-plane path."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from hermes_cli import factory_backend, factory_pg


ROOT = Path(__file__).resolve().parents[2]


def _load_script(name: str):
    path = ROOT / "scripts" / "factory" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"test_{name}", path)
    assert spec and spec.loader, f"cannot load {path}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_factory_backend_uses_postgres_only(monkeypatch):
    monkeypatch.setattr(factory_pg, "available", lambda: True)

    assert factory_backend.get_backend() is factory_pg
    assert factory_backend.backend_label() == "agent_core_postgres"

    monkeypatch.setattr(factory_pg, "available", lambda: False)
    with pytest.raises(factory_backend.FactoryBackendUnavailable, match="SQLite fallback is disabled"):
        factory_backend.get_backend()


def test_factory_blocker_classifier_covers_blocked_and_orphan_tasks():
    payload = {
        "projects": [{"project_id": "demo", "status": "active", "autonomous_enabled": True}],
        "tasks": [
            {
                "project_id": "demo",
                "lane_id": "demo-hybrid",
                "task_id": "demo-t1",
                "title": "Fix traceback in worker",
                "status": "blocked",
                "result_summary": "pytest failed with AttributeError",
            },
            {
                "project_id": "demo",
                "lane_id": "demo-hybrid",
                "task_id": "demo-t2",
                "title": "Orphan claimed task",
                "status": "claimed",
            },
        ],
        "task_runs": [],
        "gates": [],
        "human_questions": [],
    }

    classified = {item["task_id"]: item for item in factory_pg.classify_factory_blockers(payload)}

    assert classified["demo-t1"]["action_category"] == "technical_rework"
    assert classified["demo-t1"]["requires_human"] is False
    assert classified["demo-t2"]["action_category"] == "stale_orphan_state"
    assert classified["demo-t2"]["recommended_action"] == "repair_orphan_inflight_state"


def test_factory_blocker_classifier_preserves_actionable_human_question():
    payload = {
        "projects": [{"project_id": "demo", "status": "active", "autonomous_enabled": True}],
        "tasks": [
            {
                "project_id": "demo",
                "lane_id": "demo-hybrid",
                "task_id": "demo-delivery",
                "title": "Delivery report",
                "status": "blocked",
                "result_summary": """
                Preview: https://kidu.app/
                Producción: HOLD — decisión de Jean requerida

                Jean must decide:
                - APPROVED: proceed to production
                - HOLD: maintain sandbox only
                - REJECTED: specify rework scope
                """,
            }
        ],
        "task_runs": [],
        "gates": [],
        "human_questions": [],
    }

    [classified] = factory_pg.classify_factory_blockers(payload)

    assert classified["action_category"] == "human_question_required"
    assert classified["requires_human"] is True
    assert "APPROVED" in classified["human_question"]
    assert "HOLD" in classified["human_question"]
    assert "Preview: https://kidu.app/" in classified["human_question"]
    assert classified["human_options"] == ["APPROVED", "HOLD", "REJECTED"]


def test_planning_tasks_are_not_validation_blockers_from_contract_metadata():
    task = {
        "task_id": "demo-planning",
        "title": "Commercial landing redesign and corrected contact",
        "phase": "planning",
        "status": "superseded",
        "owner_profile": "implementation-planner",
        "reviewer_profile": "quality-reviewer",
        "metadata": {
            "evidence": {
                "new_contract": "planning -> implementation -> quality_review -> ui_qa_verification -> sandbox_deploy",
            }
        },
    }

    assert factory_pg._is_validation_task(task) is False


def test_record_factory_blocker_actions_lets_sql_one_add_limit(monkeypatch):
    monkeypatch.setattr(factory_pg, "_SCHEMA_READY", True)
    one_queries = []
    psql_calls = []

    def fake_one(query, **kwargs):
        one_queries.append(query)
        assert "LIMIT 1" not in query.upper()
        return None

    monkeypatch.setattr(factory_pg.sql, "one", fake_one)
    monkeypatch.setattr(factory_pg.sql, "psql", lambda query, **kwargs: psql_calls.append(query))

    result = factory_pg.record_factory_blocker_actions(
        [
            {
                "task_id": "demo-blocked",
                "project_id": "demo",
                "lane_id": "demo-hybrid",
                "title": "Needs owner decision",
                "action_category": "human_question_required",
                "blocker_category": "external_or_owner_decision",
                "recommended_action": "create_human_question_and_notify_owner",
                "requires_human": True,
                "alert_key": "factory:demo:demo-blocked:human_question_required",
                "human_question": "APPROVED / HOLD / REJECTED?",
                "human_options": ["APPROVED", "HOLD", "REJECTED"],
            }
        ],
        payload={"projects": [], "tasks": [], "task_runs": [], "gates": [], "human_questions": []},
    )

    assert result == {"classified": 1, "events_recorded": 1, "questions_created": 1}
    assert len(one_queries) == 1
    assert one_queries[0].startswith("SELECT question_id FROM factory.human_questions WHERE question_id='hq-")
    assert "OR (task_id='demo-blocked' AND status='pending')" in one_queries[0]
    assert len(psql_calls) == 2
    assert "APPROVED / HOLD / REJECTED?" in psql_calls[1]
    assert '["APPROVED", "HOLD", "REJECTED"]' in psql_calls[1]


def test_factory_watchdog_alerts_are_actionable_for_runtime_invariants():
    payload = {
        "projects": [{"project_id": "demo", "status": "delivery_hold", "autonomous_enabled": True}],
        "tasks": [
            {
                "project_id": "demo",
                "lane_id": "demo-hybrid",
                "task_id": "demo-blocked",
                "title": "Blocked delivery task",
                "status": "blocked",
                "updated_at": "2020-01-01T00:00:00Z",
            }
        ],
        "task_runs": [],
        "gates": [],
        "human_questions": [],
    }

    alerts = factory_pg.factory_watchdog_alerts(payload, blocked_minutes=1, claimed_null_rounds=3)
    alert_types = {alert["alert_type"] for alert in alerts}

    assert "delivery_hold_autoresolvable_blocked_work" in alert_types
    assert "cron_claimed_null_repeated" not in alert_types
    assert all(alert.get("message") for alert in alerts)

    runnable_payload = {
        "projects": [{"project_id": "demo", "status": "active", "autonomous_enabled": True}],
        "tasks": [{"project_id": "demo", "task_id": "demo-ready", "status": "todo"}],
        "task_runs": [],
        "gates": [],
        "human_questions": [],
    }
    runnable_alerts = factory_pg.factory_watchdog_alerts(runnable_payload, claimed_null_rounds=3)
    assert {alert["alert_type"] for alert in runnable_alerts} == {"cron_claimed_null_repeated"}

    pending_question_payload = {
        "projects": [{"project_id": "demo", "status": "active", "autonomous_enabled": True}],
        "tasks": [{"project_id": "demo", "task_id": "demo-blocked", "status": "blocked"}],
        "task_runs": [],
        "gates": [],
        "human_questions": [
            {
                "project_id": "demo",
                "task_id": "demo-blocked",
                "question_id": "hq-demo",
                "status": "pending",
                "severity": "high",
                "question": "APPROVED / HOLD / REJECTED?",
                "options": ["APPROVED", "HOLD", "REJECTED"],
            }
        ],
    }
    pending_alerts = factory_pg.factory_watchdog_alerts(pending_question_payload)
    human_alert = next(alert for alert in pending_alerts if alert["alert_type"] == "human_question_pending")
    assert human_alert["jean_question"] == "APPROVED / HOLD / REJECTED?"
    assert human_alert["options"] == ["APPROVED", "HOLD", "REJECTED"]

    dependency_blocked_payload = {
        "projects": [{"project_id": "demo", "status": "active", "autonomous_enabled": True}],
        "tasks": [
            {"project_id": "demo", "task_id": "demo-blocked", "status": "blocked"},
            {"project_id": "demo", "task_id": "demo-next", "status": "todo", "dependencies": ["demo-blocked"]},
        ],
        "task_runs": [],
        "gates": [],
        "human_questions": [],
    }
    dependency_blocked_alerts = factory_pg.factory_watchdog_alerts(dependency_blocked_payload, claimed_null_rounds=3)
    assert "cron_claimed_null_repeated" not in {alert["alert_type"] for alert in dependency_blocked_alerts}


def test_factory_watchdog_progress_stall_alerts_are_deterministic(monkeypatch):
    watchdog = _load_script("factory_watchdog_alerts")
    monkeypatch.setenv("FACTORY_PROGRESS_STALLED_ROUNDS", "1")
    payload = {
        "projects": [{"project_id": "demo", "status": "active", "autonomous_enabled": True}],
        "tasks": [{"project_id": "demo", "task_id": "demo-running", "status": "running"}],
        "task_runs": [{"project_id": "demo", "task_id": "demo-running", "run_id": "run-1", "status": "running"}],
        "gates": [],
        "human_questions": [],
    }
    state = {}

    assert watchdog._progress_stall_alerts(payload, state) == []
    alerts = watchdog._progress_stall_alerts(payload, state)

    assert [alert["alert_type"] for alert in alerts] == ["factory_progress_stalled"]
    assert alerts[0]["supervisor_action"] == "launch_reasoning_supervisor"
    assert alerts[0]["progress_snapshot"]["task_counts"] == {"running": 1}


def test_factory_watchdog_launches_reasoning_supervisor_instead_of_notifying(monkeypatch, tmp_path):
    watchdog = _load_script("factory_watchdog_alerts")
    launched = []

    class FakePopen:
        pid = 4242

        def __init__(self, args, **kwargs):
            launched.append({"args": args, "kwargs": kwargs})

    monkeypatch.setattr(watchdog.subprocess, "Popen", FakePopen)
    monkeypatch.setenv("FACTORY_SUPERVISOR_RUNS_DIR", str(tmp_path / "supervisor-runs"))
    monkeypatch.setenv("FACTORY_SUPERVISOR_HERMES_BIN", "/bin/true")
    payload = {
        "projects": [{"project_id": "demo", "status": "active", "autonomous_enabled": True}],
        "tasks": [{"project_id": "demo", "task_id": "demo-running", "status": "running"}],
        "task_runs": [],
        "gates": [],
        "human_questions": [],
    }
    alert = {
        "alert_key": "factory:demo:progress-stalled:abc",
        "alert_type": "factory_progress_stalled",
        "project_id": "demo",
        "message": "no measurable progress",
    }
    state = {}

    human_alerts = watchdog._route_repairable_alerts([alert], payload, state)

    assert human_alerts == []
    assert len(launched) == 1
    entry = state["supervisor_runs"]["demo"]
    assert entry["status"] == "running"
    prompt = Path(entry["prompt_path"]).read_text(encoding="utf-8")
    assert "SUPERVISOR_STATUS: NEEDS_HUMAN" in prompt
    assert "Jean NO quiere recibir alertas repetidas" in prompt


def test_factory_watchdog_notifies_only_when_supervisor_needs_human(monkeypatch, tmp_path):
    watchdog = _load_script("factory_watchdog_alerts")
    output = tmp_path / "output.log"
    exit_code = tmp_path / "exit_code.txt"
    output.write_text(
        "Investigated.\nSUPERVISOR_STATUS: NEEDS_HUMAN\nSUPERVISOR_SUMMARY: Need owner decision.\nJEAN_QUESTION: ¿Autorizas cambiar el alcance?\n",
        encoding="utf-8",
    )
    exit_code.write_text("0\n", encoding="utf-8")
    monkeypatch.setattr(watchdog, "_is_pid_running", lambda pid: False)
    state = {
        "supervisor_runs": {
            "demo": {
                "run_id": "fsup-demo",
                "project_id": "demo",
                "pid": 999999,
                "output_path": str(output),
                "exit_path": str(exit_code),
                "status": "running",
            }
        }
    }

    alerts = watchdog._refresh_supervisor_runs(state)

    assert [alert["alert_type"] for alert in alerts] == ["factory_reasoning_supervisor_needs_human"]
    assert alerts[0]["jean_question"] == "¿Autorizas cambiar el alcance?"


def test_repo_factory_cron_scripts_run_against_backend(monkeypatch, capsys, tmp_path):
    class FakeBackend:
        def status(self):
            return {
                "db_backend": "fake_postgres",
                "projects": [{"project_id": "demo", "name": "Demo", "status": "active", "autonomous_enabled": True}],
                "tasks": [],
                "gates": [],
                "task_runs": [],
                "alerts": [],
                "agents": [],
                "human_questions": [],
            }

    monkeypatch.setattr(factory_backend, "get_backend", lambda: FakeBackend())
    monkeypatch.setattr(factory_pg, "classify_factory_blockers", lambda payload=None, **kwargs: [])
    monkeypatch.setattr(factory_pg, "record_factory_blocker_actions", lambda classified=None, **kwargs: {"classified": 0, "events_recorded": 0, "questions_created": 0})
    monkeypatch.setattr(factory_pg, "factory_watchdog_alerts", lambda payload=None, **kwargs: [])
    monkeypatch.setenv("FACTORY_WATCHDOG_STATE_PATH", str(tmp_path / "watchdog_alert_state.json"))
    monkeypatch.setenv("FACTORY_PROGRESS_STATE_PATH", str(tmp_path / "watchdog_progress_state.json"))

    for name in ("factory_status_sync", "factory_reviewer_dispatch", "factory_blocker_detector"):
        module = _load_script(name)
        module.main()
        payload = json.loads(capsys.readouterr().out)
        assert payload["job"] == name
        assert payload["db_backend"] == "fake_postgres"

    watchdog = _load_script("factory_watchdog_alerts")
    watchdog.main()
    assert capsys.readouterr().out == ""


def test_factory_cron_scripts_are_repo_canonical_not_local_only():
    scripts_dir = ROOT / "scripts" / "factory"
    expected = {
        "factory_status_sync.py",
        "factory_reviewer_dispatch.py",
        "factory_blocker_detector.py",
        "factory_watchdog_alerts.py",
        "factory_orchestrator_tick.py",
    }

    assert expected <= {path.name for path in scripts_dir.glob("factory_*.py")}
    for script_name in expected:
        source = (scripts_dir / script_name).read_text(encoding="utf-8")
        assert "factory_backend" in source or script_name == "factory_reviewer_dispatch.py"
        assert "/home/jean/.hermes/scripts" not in source

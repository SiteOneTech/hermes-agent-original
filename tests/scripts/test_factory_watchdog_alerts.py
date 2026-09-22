from __future__ import annotations

import importlib.util
from datetime import datetime, timezone
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "factory" / "factory_watchdog_alerts.py"


def _load_watchdog_module():
    spec = importlib.util.spec_from_file_location("factory_watchdog_alerts", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_failed_supervisor_alert_uses_legacy_sent_key_for_cooldown():
    mod = _load_watchdog_module()
    state = {
        "sent": {
            "factory:supervisor:kidu-by-sitiouno:fsup-old:failed:35": mod._iso_now(),
        }
    }
    alerts = [
        {
            "alert_key": "factory:supervisor:kidu-by-sitiouno:failed",
            "alert_type": "factory_reasoning_supervisor_failed",
            "suppress_minutes": 360,
            "legacy_alert_key_prefixes": ["factory:supervisor:kidu-by-sitiouno:fsup-"],
        }
    ]

    assert mod._unsuppressed(alerts, state, suppress_minutes=60) == []
    assert "factory:supervisor:kidu-by-sitiouno:failed" not in state["sent"]


def test_failed_supervisor_completion_alert_threshold_and_stable_key(monkeypatch):
    mod = _load_watchdog_module()
    monkeypatch.delenv("FACTORY_SUPERVISOR_FAILURE_ALERTS", raising=False)
    entry = {"status": "FAILED", "failure_count": 4, "project_id": "kidu-by-sitiouno"}
    assert mod._completion_alert("kidu-by-sitiouno", entry) is None

    entry["failure_count"] = 5
    alert = mod._completion_alert("kidu-by-sitiouno", entry)
    assert alert is not None
    assert alert["alert_key"] == "factory:supervisor:kidu-by-sitiouno:failed"
    assert alert["suppress_minutes"] == 360
    assert alert["legacy_alert_key_prefixes"] == ["factory:supervisor:kidu-by-sitiouno:fsup-"]


def test_supervisor_runner_passes_short_prompt_reference(tmp_path, monkeypatch):
    mod = _load_watchdog_module()
    monkeypatch.setenv("FACTORY_SUPERVISOR_HERMES_BIN", "/bin/echo")
    prompt_path = tmp_path / "prompt.md"
    prompt_path.write_text("x" * 300_000, encoding="utf-8")

    runner = mod._write_supervisor_runner(
        tmp_path,
        prompt_path,
        tmp_path / "output.log",
        tmp_path / "exit_code.txt",
    )
    text = runner.read_text(encoding="utf-8")

    assert "PROMPT=$(cat" not in text
    assert str(prompt_path) in text
    assert len(text) < 2_000

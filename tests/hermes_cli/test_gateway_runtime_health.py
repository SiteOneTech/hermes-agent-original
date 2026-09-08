from datetime import datetime, timedelta, timezone

from hermes_cli.gateway import _runtime_health_lines


def _iso_age(seconds_ago: float) -> str:
    """ISO-8601 UTC timestamp ``seconds_ago`` in the past (drives _marker_is_stale)."""
    return (datetime.now(timezone.utc) - timedelta(seconds=seconds_ago)).isoformat()


_STALE_LINE_PREFIX = "⚠ Stale gateway_state.json:"


def _stale_lines(lines):
    return [ln for ln in lines if ln.startswith(_STALE_LINE_PREFIX)]


def test_runtime_health_lines_flags_stale_running_with_dead_pid(monkeypatch):
    """Stale updated_at + dead PID + 'running' -> contradiction line, no draining line."""
    from gateway import status as status_mod

    monkeypatch.setattr(
        "gateway.status.read_runtime_status",
        lambda: {
            "gateway_state": "running",
            "pid": 4242,
            "start_time": 111,
            "updated_at": _iso_age(600),  # well past the 120s TTL -> stale
            "active_agents": 0,
        },
    )
    # Recorded PID is gone (ungraceful kill); no real process is touched.
    monkeypatch.setattr(status_mod, "_pid_exists", lambda pid: False)
    monkeypatch.setattr(status_mod, "_get_process_start_time", lambda pid: None)

    lines = _runtime_health_lines()

    stale = _stale_lines(lines)
    assert len(stale) == 1, lines
    assert "recorded state 'running'" in stale[0]
    assert "recorded process is gone" in stale[0]
    # The misleading live-state summary must be suppressed.
    assert not any("draining" in ln.lower() for ln in lines), lines


def test_runtime_health_lines_include_fatal_platform_and_startup_reason(monkeypatch):
    monkeypatch.setattr(
        "gateway.status.read_runtime_status",
        lambda: {
            "gateway_state": "startup_failed",
            "exit_reason": "telegram conflict",
            "platforms": {
                "telegram": {
                    "state": "fatal",
                    "error_message": "another poller is active",
                }
            },
        },
    )

    lines = _runtime_health_lines()

    assert "⚠ telegram: another poller is active" in lines
    assert "⚠ Last startup issue: telegram conflict" in lines


def test_runtime_status_running_pid_validates_live_gateway_record(monkeypatch):
    from gateway import status as status_mod

    runtime = {
        "pid": 12345,
        "kind": "hermes-gateway",
        "argv": ["/opt/hermes/hermes_cli/main.py", "gateway", "run", "--replace"],
        "start_time": None,
        "gateway_state": "running",
    }
    monkeypatch.setattr(status_mod, "_pid_exists", lambda pid: pid == 12345)
    monkeypatch.setattr(status_mod, "_get_process_start_time", lambda pid: None)
    # Live cmdline unreadable (Windows / EACCES): identity falls back to the persisted
    # record's own kind+argv. Never read /proc for the fixture PID -- on a dev box 12345
    # can be any real process.
    monkeypatch.setattr(status_mod, "_read_process_cmdline", lambda pid: None)

    assert status_mod.get_runtime_status_running_pid(runtime) == 12345

    # A readable live cmdline wins over the record: a recycled PID now running something
    # else must not be reported as this gateway.
    monkeypatch.setattr(
        status_mod, "_read_process_cmdline", lambda pid: "/usr/bin/python3 /srv/webui/server.py"
    )
    assert status_mod.get_runtime_status_running_pid(runtime) is None



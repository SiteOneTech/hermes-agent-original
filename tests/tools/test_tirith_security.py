"""Tests for the tirith security scanning subprocess wrapper."""

import json
import subprocess
import time
from unittest.mock import MagicMock, patch

import pytest

import tools.tirith_security as _tirith_mod
from tools.tirith_security import check_command_security, ensure_installed


def _reset_state():
    _tirith_mod._install_attempted.clear()
    _tirith_mod._install_threads.clear()
    _tirith_mod._crash_count = 0
    _tirith_mod._circuit_open = False
    _tirith_mod._circuit_open_at = 0.0


@pytest.fixture(autouse=True)
def _reset_tirith_state():
    _reset_state()
    yield
    _reset_state()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_run(returncode=0, stdout="", stderr=""):
    """Build a mock subprocess.CompletedProcess."""
    cp = MagicMock(spec=subprocess.CompletedProcess)
    cp.returncode = returncode
    cp.stdout = stdout
    cp.stderr = stderr
    return cp


def _json_stdout(findings=None, summary=""):
    return json.dumps({"findings": findings or [], "summary": summary})


# ---------------------------------------------------------------------------
# Exit code → action mapping
# ---------------------------------------------------------------------------

class TestExitCodeMapping:
    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_exit_0_allow(self, mock_cfg, mock_run):
        mock_cfg.return_value = {"tirith_enabled": True, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": True}
        mock_run.return_value = _mock_run(0, _json_stdout())
        result = check_command_security("echo hello")
        assert result["action"] == "allow"
        assert result["findings"] == []

    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_exit_1_block_with_findings(self, mock_cfg, mock_run):
        mock_cfg.return_value = {"tirith_enabled": True, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": True}
        findings = [{"rule_id": "homograph_url", "severity": "high"}]
        mock_run.return_value = _mock_run(1, _json_stdout(findings, "homograph detected"))
        result = check_command_security("curl http://gооgle.com")
        assert result["action"] == "block"
        assert len(result["findings"]) == 1
        assert result["summary"] == "homograph detected"

    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_exit_2_warn_with_findings(self, mock_cfg, mock_run):
        mock_cfg.return_value = {"tirith_enabled": True, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": True}
        findings = [{"rule_id": "shortened_url", "severity": "medium"}]
        mock_run.return_value = _mock_run(2, _json_stdout(findings, "shortened URL"))
        result = check_command_security("curl https://bit.ly/abc")
        assert result["action"] == "warn"
        assert len(result["findings"]) == 1
        assert result["summary"] == "shortened URL"


# ---------------------------------------------------------------------------
# JSON parse failure (exit code still wins)
# ---------------------------------------------------------------------------

class TestJsonParseFailure:
    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_exit_1_invalid_json_still_blocks(self, mock_cfg, mock_run):
        mock_cfg.return_value = {"tirith_enabled": True, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": True}
        mock_run.return_value = _mock_run(1, "NOT JSON")
        result = check_command_security("bad command")
        assert result["action"] == "block"
        assert "details unavailable" in result["summary"]

    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_exit_2_invalid_json_still_warns(self, mock_cfg, mock_run):
        mock_cfg.return_value = {"tirith_enabled": True, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": True}
        mock_run.return_value = _mock_run(2, "{broken")
        result = check_command_security("suspicious command")
        assert result["action"] == "warn"
        assert "details unavailable" in result["summary"]

    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_exit_0_invalid_json_allows(self, mock_cfg, mock_run):
        mock_cfg.return_value = {"tirith_enabled": True, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": True}
        mock_run.return_value = _mock_run(0, "NOT JSON")
        result = check_command_security("safe command")
        assert result["action"] == "allow"


# ---------------------------------------------------------------------------
# Operational failures + fail_open
# ---------------------------------------------------------------------------

class TestOSErrorFailOpen:
    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_file_not_found_fail_open(self, mock_cfg, mock_run):
        mock_cfg.return_value = {"tirith_enabled": True, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": True}
        mock_run.side_effect = FileNotFoundError("No such file: tirith")
        result = check_command_security("echo hi")
        assert result["action"] == "allow"
        assert "unavailable" in result["summary"]

    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_permission_error_fail_open(self, mock_cfg, mock_run):
        mock_cfg.return_value = {"tirith_enabled": True, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": True}
        mock_run.side_effect = PermissionError("Permission denied")
        result = check_command_security("echo hi")
        assert result["action"] == "allow"
        assert "unavailable" in result["summary"]

    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_os_error_fail_closed(self, mock_cfg, mock_run):
        mock_cfg.return_value = {"tirith_enabled": True, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": False}
        mock_run.side_effect = FileNotFoundError("No such file: tirith")
        result = check_command_security("echo hi")
        assert result["action"] == "block"
        assert "fail-closed" in result["summary"]


class TestTimeoutFailOpen:
    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_timeout_fail_open(self, mock_cfg, mock_run):
        mock_cfg.return_value = {"tirith_enabled": True, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": True}
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="tirith", timeout=5)
        result = check_command_security("slow command")
        assert result["action"] == "allow"
        assert "timed out" in result["summary"]

    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_timeout_fail_closed(self, mock_cfg, mock_run):
        mock_cfg.return_value = {"tirith_enabled": True, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": False}
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="tirith", timeout=5)
        result = check_command_security("slow command")
        assert result["action"] == "block"
        assert "fail-closed" in result["summary"]


class TestUnknownExitCode:
    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_unknown_exit_code_fail_open(self, mock_cfg, mock_run):
        mock_cfg.return_value = {"tirith_enabled": True, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": True}
        mock_run.return_value = _mock_run(99, "")
        result = check_command_security("cmd")
        assert result["action"] == "allow"
        assert "exit code 99" in result["summary"]

    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_unknown_exit_code_fail_closed(self, mock_cfg, mock_run):
        mock_cfg.return_value = {"tirith_enabled": True, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": False}
        mock_run.return_value = _mock_run(99, "")
        result = check_command_security("cmd")
        assert result["action"] == "block"
        assert "exit code 99" in result["summary"]


# ---------------------------------------------------------------------------
# Circuit breaker: half-open recovery
# ---------------------------------------------------------------------------

def _open_breaker(age_s):
    """Put the breaker in the open state as if it tripped ``age_s`` seconds ago."""
    _tirith_mod._crash_count = _tirith_mod._CRASH_LIMIT
    _tirith_mod._circuit_open = True
    _tirith_mod._circuit_open_at = time.monotonic() - age_s


class TestCircuitBreakerHalfOpen:
    @pytest.mark.parametrize("returncode, action", [(0, "allow"), (1, "block"), (2, "warn")])
    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_completed_probe_after_retry_window_closes_breaker(self, mock_cfg, mock_run, returncode, action):
        """Once the retry window has elapsed, one real scan runs; any verdict (allow/block/warn)
        proves the binary healthy and closes the breaker, so the next command is scanned again."""
        mock_cfg.return_value = _CFG
        _open_breaker(age_s=_tirith_mod._CIRCUIT_RETRY_S + 1)
        mock_run.return_value = _mock_run(returncode, _json_stdout())

        result = check_command_security("echo hi")

        assert result["action"] == action
        assert mock_run.call_count == 1
        assert (_tirith_mod._circuit_open, _tirith_mod._crash_count) == (False, 0)
        # Breaker closed: the following command is scanned rather than short-circuited.
        check_command_security("echo again")
        assert mock_run.call_count == 2

    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_open_breaker_probes_once_per_window_and_failed_probe_rearms(self, mock_cfg, mock_run):
        """Inside the window nothing spawns; after it exactly one probe runs, and a probe that
        fails re-arms the window so the next caller is fail-open without spawning again."""
        mock_cfg.return_value = _CFG
        _open_breaker(age_s=1)
        mock_run.side_effect = OSError("binary gone")

        assert check_command_security("echo hi")["summary"] == "tirith disabled (circuit breaker)"
        assert mock_run.call_count == 0

        _open_breaker(age_s=_tirith_mod._CIRCUIT_RETRY_S + 1)
        assert check_command_security("echo hi")["action"] == "allow"  # probe spawned and failed
        assert mock_run.call_count == 1
        assert _tirith_mod._circuit_open is True
        assert check_command_security("echo hi")["summary"] == "tirith disabled (circuit breaker)"
        assert mock_run.call_count == 1  # re-armed: no second probe inside the fresh window


# ---------------------------------------------------------------------------
# Disabled + path expansion
# ---------------------------------------------------------------------------

class TestDisabled:
    @patch("tools.tirith_security._load_security_config")
    def test_disabled_returns_allow(self, mock_cfg):
        mock_cfg.return_value = {"tirith_enabled": False, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": True}
        result = check_command_security("rm -rf /")
        assert result["action"] == "allow"


class TestPathExpansion:
    def test_tilde_expanded_in_resolve(self):
        """_resolve_tirith_path should expand ~ in configured path."""
        from tools.tirith_security import _resolve_tirith_path
        _tirith_mod._resolved_path = None
        # Explicit path — won't auto-download, just expands and caches miss
        result = _resolve_tirith_path("~/bin/tirith")
        assert "~" not in result, "tilde should be expanded"
        _tirith_mod._resolved_path = None


# ---------------------------------------------------------------------------
# Findings cap + summary cap
# ---------------------------------------------------------------------------

class TestCaps:
    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_findings_capped_at_50(self, mock_cfg, mock_run):
        mock_cfg.return_value = {"tirith_enabled": True, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": True}
        findings = [{"rule_id": f"rule_{i}"} for i in range(100)]
        mock_run.return_value = _mock_run(2, _json_stdout(findings, "many findings"))
        result = check_command_security("cmd")
        assert len(result["findings"]) == 50

    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_summary_capped_at_500(self, mock_cfg, mock_run):
        mock_cfg.return_value = {"tirith_enabled": True, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": True}
        long_summary = "x" * 1000
        mock_run.return_value = _mock_run(2, _json_stdout([], long_summary))
        result = check_command_security("cmd")
        assert len(result["summary"]) == 500

    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_findings_and_summary_capped(self, mock_cfg, mock_run):
        mock_cfg.return_value = {"tirith_enabled": True, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": True}
        findings = [{"rule_id": f"rule_{i}"} for i in range(100)]
        mock_run.return_value = _mock_run(2, _json_stdout(findings, "x" * 1000))
        result = check_command_security("cmd")
        assert len(result["findings"]) == 50
        assert len(result["summary"]) == 500


# ---------------------------------------------------------------------------
# Programming errors propagate
# ---------------------------------------------------------------------------

class TestProgrammingErrors:
    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_attribute_error_propagates(self, mock_cfg, mock_run):
        mock_cfg.return_value = {"tirith_enabled": True, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": True}
        mock_run.side_effect = AttributeError("unexpected bug")
        with pytest.raises(AttributeError):
            check_command_security("cmd")

    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_type_error_propagates(self, mock_cfg, mock_run):
        mock_cfg.return_value = {"tirith_enabled": True, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": True}
        mock_run.side_effect = TypeError("unexpected bug")
        with pytest.raises(TypeError):
            check_command_security("cmd")


# ---------------------------------------------------------------------------
# ensure_installed
# ---------------------------------------------------------------------------

class TestEnsureInstalled:
    @patch("tools.tirith_security._load_security_config")
    def test_disabled_returns_none(self, mock_cfg):
        mock_cfg.return_value = {"tirith_enabled": False, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": True}
        assert ensure_installed() is None

    @patch("tools.tirith_security.shutil.which", return_value="/usr/local/bin/tirith")
    @patch("tools.tirith_security._load_security_config")
    def test_found_on_path_returns_immediately(self, mock_cfg, mock_which):
        mock_cfg.return_value = {"tirith_enabled": True, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": True}
        assert ensure_installed() == "/usr/local/bin/tirith"

    @patch("tools.tirith_security._load_security_config")
    def test_not_found_returns_none(self, mock_cfg, pm_tirith):
        mock_cfg.return_value = {"tirith_enabled": True, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": True}
        with patch("tools.tirith_security.shutil.which", return_value=None), \
             patch("tools.tirith_security.is_platform_supported", return_value=True), \
             patch("tools.tirith_security.threading.Thread") as MockThread:
            mock_thread = MagicMock()
            MockThread.return_value = mock_thread
            result = ensure_installed()
            assert result is None
            # Should have launched background thread
            mock_thread.start.assert_called_once()

    @patch("tools.tirith_security._load_security_config")
    def test_startup_prefetch_can_suppress_install_failure_logs(self, mock_cfg, pm_tirith):
        mock_cfg.return_value = {"tirith_enabled": True, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": True}
        with patch("tools.tirith_security.shutil.which", return_value=None), \
             patch("tools.tirith_security.is_platform_supported", return_value=True), \
             patch("tools.tirith_security.threading.Thread") as MockThread:
            mock_thread = MagicMock()
            MockThread.return_value = mock_thread
            result = ensure_installed(log_failures=False)
            assert result is None
            assert MockThread.call_args.kwargs["kwargs"] == {"log_failures": False}
            mock_thread.start.assert_called_once()


# ---------------------------------------------------------------------------
# Unsupported platform (Windows etc.) — silent fast-path everywhere
# ---------------------------------------------------------------------------

class TestUnsupportedPlatform:
    """When PM has no tirith build for this OS+arch, the entire subsystem
    must stay silent: no install thread, no spawn attempts, no CLI banner. Pattern-matching
    guards still cover the gap; tirith content scanning is just absent."""

    @pytest.mark.parametrize("target, expected", [
        ("linux-x64", True),
        ("win32-x64", False),
        (RuntimeError("unsupported architecture: riscv64"), False),
    ])
    def test_is_platform_supported(self, target, expected):
        # Table inputs, not a host fake: support is PM's per-target mapping.
        current_target = MagicMock(side_effect=[target])
        with patch("pm.current_target", current_target):
            assert _tirith_mod.is_platform_supported() is expected

    @patch("tools.tirith_security._load_security_config")
    def test_ensure_installed_unsupported_returns_none_no_thread(self, mock_cfg, monkeypatch):
        """Unsupported default targets return quietly and never start a PM install thread."""
        import pm

        mock_cfg.return_value = {"tirith_enabled": True, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": True}
        monkeypatch.setattr(pm, "lazy_installs_allowed", lambda: True)
        monkeypatch.setattr(pm, "installed_package", lambda _name: None)
        monkeypatch.setattr("tools.tirith_security.shutil.which", lambda _name: None)
        with (
            patch("tools.tirith_security.is_platform_supported", return_value=False),
            patch("tools.tirith_security.threading.Thread") as MockThread,
        ):
            assert ensure_installed() is None
            MockThread.assert_not_called()

    @patch("tools.tirith_security._load_security_config")
    def test_check_command_security_unsupported_allows_silently(self, mock_cfg):
        """Windows: skip the resolver and spawn entirely — return allow with
        an empty summary so callers can't accidentally surface 'tirith
        unavailable' messaging to the user."""
        mock_cfg.return_value = {"tirith_enabled": True, "tirith_path": "tirith",
                                 "tirith_timeout": 5, "tirith_fail_open": True}
        with patch("tools.tirith_security.is_platform_supported", return_value=False), \
             patch("tools.tirith_security.subprocess.run") as mock_run, \
             patch("tools.tirith_security._resolve_tirith_path") as mock_resolve:
            result = check_command_security("rm -rf /")
            assert result == {"action": "allow", "findings": [], "summary": ""}
            mock_run.assert_not_called()
            mock_resolve.assert_not_called()

    def test_explicit_path_still_honored_on_unsupported_platform(self, tmp_path):
        """If a user explicitly configured a tirith_path (e.g. they built it
        themselves under WSL), the unsupported-platform short-circuit must
        NOT override that — explicit config wins."""
        custom = tmp_path / "tirith"
        custom.write_text("#!/bin/sh\nexit 0\n")
        custom.chmod(0o755)
        with patch("tools.tirith_security.is_platform_supported", return_value=False):
            assert _tirith_mod._resolve_tirith_path(str(custom)) == str(custom)


# ---------------------------------------------------------------------------
# PM-provisioned binary: one install attempt per home, explicit paths never download
# ---------------------------------------------------------------------------

_BARE_CFG = {"tirith_enabled": True, "tirith_path": "tirith",
             "tirith_timeout": 5, "tirith_fail_open": True}


@pytest.fixture
def pm_tirith(monkeypatch):
    """Nothing on PATH, nothing installed yet, lazy installs allowed."""
    import pm

    installed = MagicMock(return_value=None)
    ensure = MagicMock()
    monkeypatch.setattr("tools.tirith_security.shutil.which", lambda _name: None)
    monkeypatch.setattr(pm, "installed_package", installed)
    monkeypatch.setattr(pm, "ensure", ensure)
    monkeypatch.setattr(pm, "lazy_installs_allowed", lambda: True)
    return ensure, installed


class TestPmInstall:
    def test_default_path_installs_through_pm(self, pm_tirith):
        """The default bare 'tirith' is provisioned by PM on a cold scan."""
        ensure, installed = pm_tirith
        ensure.side_effect = lambda *_a, **_k: setattr(
            installed, "return_value", MagicMock(binary="/pm/tirith"))

        assert _tirith_mod._resolve_tirith_path("tirith") == "tirith"
        for thread in _tirith_mod._install_threads.values():
            thread.join(5)
        ensure.assert_called_once_with("tirith")
        assert _tirith_mod._resolve_tirith_path("tirith") == "/pm/tirith"

    def test_failed_install_is_not_retried(self, pm_tirith):
        """After a failed install, subsequent resolves fall back without retrying."""
        ensure, _ = pm_tirith
        ensure.side_effect = RuntimeError("download failed")

        assert _tirith_mod._resolve_tirith_path("tirith") == "tirith"
        for thread in _tirith_mod._install_threads.values():
            thread.join(5)
        assert _tirith_mod._resolve_tirith_path("tirith") == "tirith"
        assert ensure.call_count == 1

    def test_tilde_explicit_path_missing_no_download(self, pm_tirith):
        """An explicit ~/path that doesn't exist must NOT trigger an install."""
        ensure, _ = pm_tirith

        result = _tirith_mod._resolve_tirith_path("~/bin/tirith")

        ensure.assert_not_called()
        assert "~" not in result  # tilde still expanded

    def test_install_proceeds_without_cosign(self, tmp_path):
        """Provenance is optional without cosign: SHA-256 verification alone proceeds."""
        with patch("tools.tirith_security.shutil.which", return_value=None):
            verified, reason = _tirith_mod.verify_release_provenance(tmp_path, MagicMock())
        assert (verified, reason) == (False, "")


# ---------------------------------------------------------------------------
# Background install / non-blocking startup (P2)
# ---------------------------------------------------------------------------

class TestBackgroundInstall:
    def test_ensure_installed_non_blocking(self, pm_tirith):
        """ensure_installed must return immediately when an install is needed."""
        with patch("tools.tirith_security._load_security_config", return_value=_BARE_CFG), \
             patch("tools.tirith_security.is_platform_supported", return_value=True), \
             patch("tools.tirith_security.threading.Thread") as MockThread:
            assert ensure_installed() is None  # not available yet
            MockThread.assert_called_once()
            MockThread.return_value.start.assert_called_once()

    def test_scan_does_not_wait_on_startup_install(self, pm_tirith):
        """A scan during the startup install returns the default instead of installing again."""
        ensure, _ = pm_tirith
        with patch("tools.tirith_security._load_security_config", return_value=_BARE_CFG), \
             patch("tools.tirith_security.is_platform_supported", return_value=True), \
             patch("tools.tirith_security.threading.Thread"):
            ensure_installed()

        assert _tirith_mod._resolve_tirith_path("tirith") == "tirith"
        ensure.assert_not_called()


# ---------------------------------------------------------------------------
# Warn-once dedupe (issue: tirith spawn failed spamming on Windows)
# ---------------------------------------------------------------------------

class TestSpawnWarningDedup:
    """When tirith isn't installed yet (background install in flight, or
    install marked failed), every terminal command spammed an identical
    ``tirith spawn failed: [WinError 2]`` warning to ``errors.log``. The
    dedupe set in ``_warn_once`` collapses repeats by ``(exc class, errno)``
    while still surfacing the first occurrence so users see the failure.
    """

    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_repeated_spawn_failure_logs_once(self, mock_cfg, mock_run, caplog):
        mock_cfg.return_value = {
            "tirith_enabled": True, "tirith_path": "tirith",
            "tirith_timeout": 5, "tirith_fail_open": True,
        }
        mock_run.side_effect = FileNotFoundError("[WinError 2]")
        # Fresh dedupe state — clear any keys left by other tests.
        _tirith_mod._warned_messages.clear()

        with caplog.at_level("WARNING", logger="tools.tirith_security"):
            for i in range(15):
                result = check_command_security("echo hi")
                # Behavior must remain the same on every call —
                # fail-open allow, with the exception captured in summary.
                assert result["action"] == "allow"
                if i < _tirith_mod._CRASH_LIMIT:
                    # Before circuit breaker opens, summary has the exception
                    assert "unavailable" in result["summary"]
                else:
                    # After circuit breaker opens, summary is generic
                    assert "circuit breaker" in result["summary"]

        spawn_warnings = [
            rec for rec in caplog.records
            if "tirith spawn failed" in rec.message
        ]
        assert len(spawn_warnings) == 1, (
            f"expected exactly 1 spawn-failed warning across 15 commands, "
            f"got {len(spawn_warnings)}: {[r.message for r in spawn_warnings]}"
        )

    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_distinct_exception_types_each_log_once(self, mock_cfg, mock_run, caplog):
        """``FileNotFoundError`` and ``PermissionError`` are distinct
        failure modes and each deserves its own first-occurrence log
        line; the dedupe key includes the exception class.

        After _CRASH_LIMIT consecutive failures the circuit breaker opens
        and subsequent calls short-circuit without spawning, so we only
        see the warnings from the first batch."""
        mock_cfg.return_value = {
            "tirith_enabled": True, "tirith_path": "tirith",
            "tirith_timeout": 5, "tirith_fail_open": True,
        }
        with _tirith_mod._warned_lock:
            _tirith_mod._warned_messages.clear()

        with caplog.at_level("WARNING", logger="tools.tirith_security"):
            mock_run.side_effect = FileNotFoundError("[WinError 2]")
            for _ in range(3):
                check_command_security("a")
            # Circuit breaker is now open — switching to PermissionError
            # won't generate a new warning because the function returns
            # before reaching subprocess.run.
            mock_run.side_effect = PermissionError("denied")
            for _ in range(3):
                check_command_security("b")

        spawn_warnings = [
            rec for rec in caplog.records
            if "tirith spawn failed" in rec.message
        ]
        assert len(spawn_warnings) == 1, (
            f"expected 1 warning before circuit breaker opens, "
            f"got {len(spawn_warnings)}"
        )

    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_repeated_timeout_logs_once(self, mock_cfg, mock_run, caplog):
        mock_cfg.return_value = {
            "tirith_enabled": True, "tirith_path": "tirith",
            "tirith_timeout": 5, "tirith_fail_open": True,
        }
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="tirith", timeout=5)
        with _tirith_mod._warned_lock:
            _tirith_mod._warned_messages.clear()

        with caplog.at_level("WARNING", logger="tools.tirith_security"):
            for _ in range(10):
                result = check_command_security("slow")
                assert result["action"] == "allow"

        timeout_warnings = [
            rec for rec in caplog.records
            if "tirith timed out" in rec.message
        ]
        assert len(timeout_warnings) == 1

    @patch("tools.tirith_security._load_security_config")
    def test_path_none_logs_once(self, mock_cfg, caplog):
        """``_resolve_tirith_path`` returning ``None`` (explicit path set
        but resolver returned None — unusual) should not spam the log
        either."""
        mock_cfg.return_value = {
            "tirith_enabled": True, "tirith_path": "tirith",
            "tirith_timeout": 5, "tirith_fail_open": True,
        }
        with _tirith_mod._warned_lock:
            _tirith_mod._warned_messages.clear()

        with patch(
            "tools.tirith_security._resolve_tirith_path", return_value=None
        ):
            with caplog.at_level("WARNING", logger="tools.tirith_security"):
                for _ in range(10):
                    result = check_command_security("echo")
                    assert result["action"] == "allow"
                    assert "tirith path unavailable" in result["summary"]

        none_warnings = [
            rec for rec in caplog.records
            if "tirith path resolved to None" in rec.message
        ]
        assert len(none_warnings) == 1


# ---------------------------------------------------------------------------
# .app TLD suppression (issue #24461)
# ---------------------------------------------------------------------------

_CFG = {"tirith_enabled": True, "tirith_path": "tirith",
        "tirith_timeout": 5, "tirith_fail_open": True}


class TestAppTldSuppression:
    """warn verdicts whose only finding is lookalike_tld/.app are downgraded to allow."""

    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_app_only_warn_downgraded_to_allow(self, mock_cfg, mock_run):
        mock_cfg.return_value = _CFG
        findings = [{"rule_id": "lookalike_tld", "value": ".app",
                     "message": "Domain uses '.app' TLD which can be confused with file extensions"}]
        mock_run.return_value = _mock_run(2, _json_stdout(findings, ".app TLD warning"))
        result = check_command_security("curl https://example.app")
        assert result["action"] == "allow"
        assert result["findings"] == []
        assert result["summary"] == ""

    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_app_tld_in_description_field_also_suppressed(self, mock_cfg, mock_run):
        mock_cfg.return_value = _CFG
        findings = [{"rule_id": "lookalike_tld",
                     "description": "TLD .app looks like a file extension"}]
        mock_run.return_value = _mock_run(2, _json_stdout(findings))
        result = check_command_security("curl https://api.app/v1")
        assert result["action"] == "allow"

    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_mixed_findings_preserve_warn(self, mock_cfg, mock_run):
        """If .app finding is accompanied by another finding, warn is preserved."""
        mock_cfg.return_value = _CFG
        findings = [
            {"rule_id": "lookalike_tld", "value": ".app"},
            {"rule_id": "shortened_url", "severity": "medium"},
        ]
        mock_run.return_value = _mock_run(2, _json_stdout(findings, "mixed"))
        result = check_command_security("curl https://bit.ly/test.app")
        assert result["action"] == "warn"
        assert len(result["findings"]) == 2

    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_non_app_lookalike_tld_preserved(self, mock_cfg, mock_run):
        """lookalike_tld for a non-.app TLD is not suppressed."""
        mock_cfg.return_value = _CFG
        findings = [{"rule_id": "lookalike_tld", "value": ".zip",
                     "message": "TLD .zip can be confused with zip archives"}]
        mock_run.return_value = _mock_run(2, _json_stdout(findings, ".zip TLD warning"))
        result = check_command_security("curl https://victim.zip")
        assert result["action"] == "warn"
        assert len(result["findings"]) == 1

    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_block_verdict_never_suppressed(self, mock_cfg, mock_run):
        """block exit code is never downgraded, even if finding looks like .app."""
        mock_cfg.return_value = _CFG
        findings = [{"rule_id": "lookalike_tld", "value": ".app"}]
        mock_run.return_value = _mock_run(1, _json_stdout(findings, "block"))
        result = check_command_security("curl https://example.app")
        assert result["action"] == "block"

    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_multiple_app_tld_findings_all_suppressed(self, mock_cfg, mock_run):
        """All findings being .app lookalike_tld → allow."""
        mock_cfg.return_value = _CFG
        findings = [
            {"rule_id": "lookalike_tld", "value": ".app"},
            {"rule_id": "lookalike_tld", "tld": ".app"},
        ]
        mock_run.return_value = _mock_run(2, _json_stdout(findings))
        result = check_command_security("curl https://a.app https://b.app")
        assert result["action"] == "allow"


class TestEmojiVariationSelectorSuppression:
    """VS16 after an emoji-capable base is presentation, not obfuscation: no approval prompt."""

    _VS = [{"rule_id": "variation_selector", "severity": "medium"}]

    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_emoji_only_variation_selector_warn_is_downgraded(self, mock_cfg, mock_run):
        mock_cfg.return_value = _CFG
        mock_run.return_value = _mock_run(2, _json_stdout(self._VS, "variation selector"))

        # SMP emoji, Dingbats/Misc Symbols, and BMP singletons outside those blocks (ℹ ▶).
        result = check_command_security('ls "🗞️ Journal/" "✅️ Projects/" "ℹ️ Info/" "▶️ Media/"')

        assert result == {"action": "allow", "findings": [], "summary": ""}

    @pytest.mark.parametrize("command, findings", [
        ("printf 'a️'", _VS),            # VS16 after a letter
        ("printf '0️'", _VS),            # VS16 after a digit (keycap base)
        ("printf 'x󠄀'", _VS),        # a non-VS16 selector
        ('curl https://bit.ly/x --output "🗞️ Journal/file"',  # emoji path + another finding
         _VS + [{"rule_id": "shortened_url", "severity": "medium"}]),
    ])
    @patch("tools.tirith_security.subprocess.run")
    @patch("tools.tirith_security._load_security_config")
    def test_other_selectors_or_mixed_findings_keep_warn(self, mock_cfg, mock_run, command, findings):
        mock_cfg.return_value = _CFG
        mock_run.return_value = _mock_run(2, _json_stdout(findings, "variation selector"))

        result = check_command_security(command)

        assert result["action"] == "warn"
        assert result["findings"] == findings


class TestIsAppTldFinding:
    """Unit tests for the _is_app_tld_finding helper."""

    def setup_method(self):
        from tools.tirith_security import _is_app_tld_finding
        self.fn = _is_app_tld_finding

    def test_matching_value_field(self):
        assert self.fn({"rule_id": "lookalike_tld", "value": ".app"})

    def test_matching_tld_field(self):
        assert self.fn({"rule_id": "lookalike_tld", "tld": ".app"})

    def test_matching_description_field(self):
        assert self.fn({"rule_id": "lookalike_tld",
                        "description": "TLD .app looks like an executable"})

    def test_matching_message_field(self):
        assert self.fn({"rule_id": "lookalike_tld",
                        "message": "Domain uses '.app' TLD"})

    def test_wrong_rule_id(self):
        assert not self.fn({"rule_id": "shortened_url", "value": ".app"})

    def test_non_app_tld(self):
        assert not self.fn({"rule_id": "lookalike_tld", "value": ".zip"})

    def test_no_tld_value_fields(self):
        assert not self.fn({"rule_id": "lookalike_tld", "severity": "low"})

    def test_non_dict_input(self):
        assert not self.fn("not a dict")  # type: ignore[arg-type]

    def test_case_insensitive_match(self):
        assert self.fn({"rule_id": "lookalike_tld", "value": ".APP"})

    @pytest.mark.parametrize("finding, expected", [
        ({"rule_id": "lookalike_tld", "value": ".APP"}, True),   # case-insensitive
        ({"rule_id": "lookalike_tld", "message": "Domain uses '.app' TLD"}, True),
        ({"rule_id": "shortened_url", "value": ".app"}, False),  # wrong rule_id
        ({"rule_id": "lookalike_tld", "value": ".zip"}, False),  # other TLD
    ])
    def test_app_tld_detection(self, finding, expected):
        from tools.tirith_security import _is_app_tld_finding
        assert _is_app_tld_finding(finding) is expected

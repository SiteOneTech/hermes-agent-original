"""Tests for the stat-based special-file guard in read_file_tool.

The name blocklist (_is_blocked_device) catches /dev/* and /proc/* aliases;
_special_file_kind catches the CLASS — any FIFO/socket/device anywhere.
Without it, read_file on a workspace FIFO blocks until the exec timeout.
"""

import json
import os
import socket
import subprocess

import pytest

from tools.file_operations import ShellFileOperations
from tools.file_tools import _special_file_kind, read_file_tool


class TestSpecialFileKind:
    def test_regular_file(self, tmp_path):
        p = tmp_path / "a.txt"
        p.write_text("hi")
        assert _special_file_kind(p) is None

    def test_directory(self, tmp_path):
        assert _special_file_kind(tmp_path) is None

    def test_missing_path(self, tmp_path):
        assert _special_file_kind(tmp_path / "nope") is None

    def test_fifo(self, tmp_path):
        fifo = tmp_path / "p.pipe"
        os.mkfifo(fifo)
        assert "FIFO" in (_special_file_kind(fifo) or "")

    def test_socket(self, tmp_path):
        sock_path = tmp_path / "s.sock"
        s = socket.socket(socket.AF_UNIX)
        try:
            s.bind(str(sock_path))
            assert "socket" in (_special_file_kind(sock_path) or "")
        finally:
            s.close()

    def test_symlink_to_fifo_followed(self, tmp_path):
        fifo = tmp_path / "p.pipe"
        os.mkfifo(fifo)
        link = tmp_path / "innocent.txt"
        link.symlink_to(fifo)
        assert "FIFO" in (_special_file_kind(link) or "")

    def test_char_device(self):
        if not os.path.exists("/dev/null"):
            pytest.skip("no /dev/null")
        assert "character device" in (_special_file_kind("/dev/null") or "")


class TestReadFileToolFifoGuard:
    def test_fifo_read_returns_note_instantly(self, tmp_path, monkeypatch):
        import time

        monkeypatch.setenv("TERMINAL_CWD", str(tmp_path))
        fifo = tmp_path / "live.pipe"
        os.mkfifo(fifo)
        t0 = time.monotonic()
        result = json.loads(read_file_tool(str(fifo)))
        assert time.monotonic() - t0 < 5, "guard must not block on the FIFO"
        assert result["success"] is False
        assert "FIFO" in result["note"]
        assert "no read was attempted" in result["note"]

    def test_regular_file_unaffected(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TERMINAL_CWD", str(tmp_path))
        f = tmp_path / "ok.txt"
        f.write_text("alpha\nbeta\n")
        result = json.loads(read_file_tool(str(f)))
        assert result.get("success", True) is not False
        assert "alpha" in result.get("content", "")


class TestShellFileOperationsSpecialFileGuard:
    def test_remote_like_backend_rejects_fifo_before_pathname_read(self, tmp_path):
        """Every backend must reject a FIFO without ``wc/head/sed`` opening it.

        The simulated environment is deliberately not a LocalEnvironment: the
        shell backend is the only shared boundary for SSH, Docker and similar
        remote filesystems. It executes the generated command for real, while
        rejecting the legacy pathname readers so the regression fails before a
        FIFO can block the test process.
        """
        fifo = tmp_path / "remote.pipe"
        os.mkfifo(fifo)

        class RemoteLikeEnv:
            cwd = str(tmp_path)

            def execute(self, command, **_kwargs):
                assert not any(token in command for token in (
                    "wc -c <", "head -c", "sed -n", "base64 <", "cat ",
                )), f"unsafe pathname read reached remote backend: {command}"
                completed = subprocess.run(
                    command, shell=True, cwd=self.cwd, text=True,
                    capture_output=True, timeout=5,
                )
                return {
                    "output": completed.stdout,
                    "returncode": completed.returncode,
                }

        result = ShellFileOperations(RemoteLikeEnv()).read_file(str(fifo))

        assert result.error is not None
        assert "FIFO" in result.error

    def test_remote_like_backend_rejects_fifo_for_raw_read(self, tmp_path):
        fifo = tmp_path / "raw.pipe"
        os.mkfifo(fifo)

        class RemoteLikeEnv:
            cwd = str(tmp_path)

            def execute(self, command, **_kwargs):
                assert not any(token in command for token in (
                    "wc -c <", "head -c", "sed -n", "base64 <", "cat ",
                )), f"unsafe pathname read reached remote backend: {command}"
                completed = subprocess.run(
                    command, shell=True, cwd=self.cwd, text=True,
                    capture_output=True, timeout=5,
                )
                return {
                    "output": completed.stdout,
                    "returncode": completed.returncode,
                }

        result = ShellFileOperations(RemoteLikeEnv()).read_file_raw(str(fifo))

        assert result.error is not None
        assert "FIFO" in result.error

    def test_remote_like_backend_rejects_fifo_for_bytes_read(self, tmp_path):
        fifo = tmp_path / "bytes.pipe"
        os.mkfifo(fifo)

        class RemoteLikeEnv:
            cwd = str(tmp_path)

            def execute(self, command, **_kwargs):
                assert not any(token in command for token in (
                    "wc -c <", "head -c", "sed -n", "base64 <", "cat ",
                )), f"unsafe pathname read reached remote backend: {command}"
                completed = subprocess.run(
                    command, shell=True, cwd=self.cwd, text=True,
                    capture_output=True, timeout=5,
                )
                return {
                    "output": completed.stdout,
                    "returncode": completed.returncode,
                }

        result = ShellFileOperations(RemoteLikeEnv()).read_file_bytes(str(fifo))

        assert result.error is not None
        assert "FIFO" in result.error

    def test_safe_reader_rejects_oversized_bytes_before_export(self, tmp_path):
        payload = tmp_path / "large.bin"
        payload.write_bytes(b"x" * 32)

        class RemoteLikeEnv:
            cwd = str(tmp_path)

            def execute(self, command, **_kwargs):
                completed = subprocess.run(
                    command, shell=True, cwd=self.cwd, text=True,
                    capture_output=True, timeout=5,
                )
                return {
                    "output": completed.stdout,
                    "returncode": completed.returncode,
                }

        page = ShellFileOperations(RemoteLikeEnv())._read_regular_file_page(
            str(payload), 1, 2**31 - 1, max_bytes=8,
        )

        assert page == {"state": "too_large", "file_size": 32}

    def test_bytes_read_reports_size_limit_from_descriptor(self, tmp_path):
        payload = tmp_path / "limited.bin"
        payload.write_bytes(b"x" * 32)

        class RemoteLikeEnv:
            cwd = str(tmp_path)

            def execute(self, command, **_kwargs):
                completed = subprocess.run(
                    command, shell=True, cwd=self.cwd, text=True,
                    capture_output=True, timeout=5,
                )
                return {
                    "output": completed.stdout,
                    "returncode": completed.returncode,
                }

        result = ShellFileOperations(RemoteLikeEnv()).read_file_bytes(
            str(payload), max_bytes=8,
        )

        assert result.file_size == 32
        assert result.error == "File is too large (32 bytes, limit is 8)"

    def test_safe_reader_returns_metadata_without_exporting_binary_content(self, tmp_path):
        payload = tmp_path / "large.png"
        payload.write_bytes(b"\x89PNG\r\n\x1a\n" + b"x" * 65_536)

        class RemoteLikeEnv:
            cwd = str(tmp_path)

            def execute(self, command, **_kwargs):
                completed = subprocess.run(
                    command, shell=True, cwd=self.cwd, text=True,
                    capture_output=True, timeout=5,
                )
                return {
                    "output": completed.stdout,
                    "returncode": completed.returncode,
                }

        page = ShellFileOperations(RemoteLikeEnv())._read_regular_file_page(
            str(payload), 1, 1, metadata_only=True,
        )

        assert page == {"state": "regular", "file_size": 65_544}

    def test_backend_without_python_fails_closed_without_pathname_fallback(self):
        commands = []

        class NoPythonEnv:
            cwd = "/tmp"

            def execute(self, command, **_kwargs):
                commands.append(command)
                return {"output": "command not found", "returncode": 127}

        result = ShellFileOperations(NoPythonEnv()).read_file("notes.txt")

        assert result.error == (
            "Safe file reader requires Python in the target environment; "
            "no insecure shell fallback was used."
        )
        assert len(commands) == 2
        assert all(command.startswith(("python3 -c", "python -c")) for command in commands)

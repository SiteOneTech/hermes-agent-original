"""A terminal environment that cannot run commands (container still starting, removed out-of-band,
transport down) must surface as an environment error, never as "File not found": the model trusts
a false negative for the rest of the session (#44750).

Reads travel through the safe reader (``_read_regular_file_page``): one ``python3 -c`` snippet
whose reply is ``<marker>{json}<marker>`` with a per-call ``__HERMES_SR_...__`` marker. A healthy
environment answers that snippet; a dead one never produces the marker."""

import json
import re

import pytest

from tools.file_operations import ShellFileOperations

_SR_MARKER = re.compile(r"__HERMES_SR_[0-9a-f]{32}__")


def _safe_reader_reply(command: str, payload: dict) -> str:
    """The safe reader's one-line reply for ``command``'s marker."""
    marker = _SR_MARKER.search(command).group(0)
    return marker + json.dumps(payload, separators=(",", ":")) + marker + "\n"


class _DeadEnv:
    cwd = "/workspace"

    def execute(self, command: str, cwd=None, **kwargs) -> dict:
        return {"output": "Error: container is not running", "returncode": 125}


class _HealthyEmptyEnv:
    """Runs commands fine; the filesystem has no files."""
    cwd = "/workspace"

    def __init__(self):
        self.commands = []

    def execute(self, command: str, cwd=None, **kwargs) -> dict:
        self.commands.append(command)
        if command.startswith("python3 -c ") and _SR_MARKER.search(command):
            return {"output": _safe_reader_reply(command, {"state": "missing"}), "returncode": 0}
        if command.startswith("test -e"):
            return {"output": "not_found\n", "returncode": 0}
        if command.startswith("echo "):
            return {"output": command[5:].strip() + "\n", "returncode": 0}
        return {"output": "", "returncode": 1}


class _NoPythonEnv:
    """Runs shell commands fine but has no interpreter: the safe reader must fail closed
    (no ``[ -f ]``/``wc``/``head``/``sed``/``cat`` fallback) instead of guessing."""
    cwd = "/workspace"

    def __init__(self):
        self.commands = []

    def execute(self, command: str, cwd=None, **kwargs) -> dict:
        self.commands.append(command)
        if command.startswith(("python3 -c ", "python -c ")):
            name = command.split(" ", 1)[0]
            return {"output": f"bash: {name}: command not found\n", "returncode": 127}
        return {"output": "", "returncode": 0}


@pytest.mark.parametrize("op", ["read_file", "read_file_raw", "read_file_bytes", "search"])
def test_dead_environment_is_reported_as_unavailable_not_missing(op):
    ops = ShellFileOperations(_DeadEnv())
    result = getattr(ops, op)("pattern", "state") if op == "search" else getattr(ops, op)("state/notes.md")
    assert result.error and "File not found" not in result.error and "environment unavailable" in result.error.lower()


@pytest.mark.parametrize("op", ["read_file", "read_file_raw", "read_file_bytes"])
def test_healthy_environment_still_reports_missing_files(op):
    env = _HealthyEmptyEnv()
    result = getattr(ShellFileOperations(env), op)("state/notes.md")
    assert result.error and "File not found" in result.error
    # The verdict came from the safe reader's ``missing`` state, in one snippet.
    snippets = [c for c in env.commands if _SR_MARKER.search(c)]
    assert len(snippets) == 1 and snippets[0].startswith("python3 -c ")


@pytest.mark.parametrize("op", ["read_file", "read_file_raw", "read_file_bytes"])
def test_environment_without_python_fails_closed_not_missing(op):
    env = _NoPythonEnv()
    result = getattr(ShellFileOperations(env), op)("state/notes.md")
    assert result.error and "File not found" not in result.error
    assert "requires Python" in result.error
    # python3 then python were tried; nothing else touched the pathname.
    assert [c.split(" ", 1)[0] for c in env.commands] == ["python3", "python"]

"""Windows UTF-8 bootstrap for Hermes entry points (no-op on POSIX).

Windows binds stdio to the console code page (cp1252), so ``print("café")`` raises
``UnicodeEncodeError``, and Python children inherit the same default unless
``PYTHONUTF8``/``PYTHONIOENCODING`` are set. Import this module first in every entry
point (``hermes``, ``hermes-agent``, ``hermes-acp``, ``gateway.run``, ``batch_runner``,
``cron/scheduler``). It does NOT re-exec with ``-X utf8``: ``open()`` in the current
process still needs an explicit ``encoding="utf-8"`` (ruff ``PLW1514``). POSIX is left
alone deliberately — users' ``LANG``/``LC_*`` choices are respected.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

_IS_WINDOWS = sys.platform == "win32"
_bootstrap_applied = False


def apply_windows_utf8_bootstrap() -> bool:
    """Apply the Windows UTF-8 bootstrap once; True only when it was applied this call."""
    global _bootstrap_applied

    if not _IS_WINDOWS or _bootstrap_applied:
        return False

    # setdefault() so a user can opt out with PYTHONUTF8=0 / PYTHONIOENCODING=...
    os.environ.setdefault("PYTHONUTF8", "1")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

    # os.environ changes don't rebind streams bound at interpreter startup, so
    # reconfigure them in-process. errors="replace" keeps a non-UTF-8 legacy
    # pipe on stdin from crashing us (U+FFFD instead of an exception).
    # Non-TextIOWrapper streams (BytesIO in tests, embedded hosts) have no
    # reconfigure(): skip — the env-var fix for children is the bigger win.
    for stream_name in ("stdout", "stderr", "stdin"):
        reconfigure = getattr(getattr(sys, stream_name, None), "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass  # closed, or replaced with something non-reconfigurable

    _bootstrap_applied = True
    return True


def suppress_platform_ver_console() -> None:
    """Stub ``platform._syscmd_ver`` on Windows — decode-crash + console-flash guard.

    ``platform.win32_ver()`` (reached via ``platform.platform()``, which the OpenAI SDK
    calls) shells out ``cmd /c ver`` with ``shell=True`` and no ``CREATE_NO_WINDOW``: a
    windowless parent (pythonw gateway, slash/kanban workers) flashes a console per call,
    and Python 3.11.0/3.11.1 (no ``encoding="locale"`` fix) strict-utf-8-decodes the OEM
    code page output under PEP 540 mode and raises (#69413). Returning the inputs makes
    ``win32_ver()`` fall back to ``sys.getwindowsversion()`` — same data, no subprocess.
    Mirrors ``hermes_cli._subprocess_compat.suppress_platform_ver_console`` for callers
    that never import ``hermes_cli.main``; double application is harmless.
    """
    if not _IS_WINDOWS:
        return
    try:
        import platform

        if hasattr(platform, "_syscmd_ver"):
            def _quiet_syscmd_ver(system="", release="", version="",
                                  supported_platforms=("win32", "win16", "dos")):
                return system, release, version

            platform._syscmd_ver = _quiet_syscmd_ver
    except Exception:
        pass  # hardening only — never break an entry point


def harden_import_path(src_root: str | None = None) -> None:
    """Stop a package in the current directory from shadowing Hermes modules.

    Hermes ships top-level modules with common names (``utils``, ``proxy``, ``ui``); a
    project with its own ``utils/`` launched from its directory would win the import.
    The cwd reaches ``sys.path`` as ``""``/``"."`` (script/``-m`` launches) AND as an
    absolute path (venv activation, PYTHONPATH), so both are handled: relative forms are
    dropped and the Hermes root is *relocated* to the front, not merely inserted when
    absent. ``src_root`` defaults to this module's directory (the repo root for every
    shipped entry point), so no spawner env var is required.
    """
    root = src_root or os.environ.get("HERMES_PYTHON_SRC_ROOT") or os.path.dirname(
        os.path.abspath(__file__)
    )

    sys.path[:] = [p for p in sys.path if p not in ("", ".")]

    root_abs = os.path.abspath(root)
    sys.path[:] = [p for p in sys.path if os.path.abspath(p) != root_abs]
    sys.path.insert(0, root)


def activate_durable_lazy_target() -> None:
    """Put the durable lazy-install dir (``HERMES_LAZY_INSTALL_TARGET``) on ``sys.path``.

    Immutable Docker images seal the venv and redirect lazy installs to the data volume;
    packages installed there on a previous run must be importable before any backend
    imports its SDK. Appends to the END of ``sys.path`` so the core venv always wins name
    collisions (see ``tools.lazy_deps``). Never raises; unset target is a no-op.
    """
    if not os.environ.get("HERMES_LAZY_INSTALL_TARGET", "").strip():
        return
    try:
        from tools import lazy_deps
        lazy_deps.activate_durable_lazy_target()
    except Exception:
        pass  # a failed activation just leaves the backend reporting itself unavailable


def _factory_command_requested(argv: list[str] | tuple[str, ...] | None = None) -> bool:
    """Return whether the console entry point is about to run ``hermes factory``.

    Generated console scripts start outside the user's current working
    directory, so editable installs can import a stale primary checkout before
    the Factory CLI has a chance to delegate to the current source tree.  Keep
    this parser dependency-free and deliberately tiny: it only needs to find the
    first Hermes subcommand after global profile flags.
    """

    args = list(sys.argv[1:] if argv is None else argv)
    skip_next = False
    for arg in args:
        if skip_next:
            skip_next = False
            continue
        if arg == "--":
            return False
        if arg in {"-p", "--profile"}:
            skip_next = True
            continue
        if arg.startswith("--profile="):
            continue
        if arg.startswith("-"):
            continue
        return arg == "factory"
    return False


def _factory_source_root_is_complete(source_root: Path) -> bool:
    return all(
        (source_root / rel_path).is_file()
        for rel_path in (
            Path("hermes_cli") / "main.py",
            Path("hermes_cli") / "factory.py",
            Path("hermes_cli") / "factory_pg.py",
            Path("scripts") / "factory" / "factory_orchestrator_tick.py",
        )
    )


def _bootstrap_source_root() -> Path | None:
    try:
        root = Path(__file__).resolve().parent
    except Exception:
        return None
    return root if _factory_source_root_is_complete(root) else None


def _find_cwd_factory_source_root() -> Path | None:
    try:
        cwd = Path.cwd().resolve()
    except Exception:
        return None
    for candidate in (cwd, *cwd.parents):
        if _factory_source_root_is_complete(candidate):
            return candidate
    return None


def _same_source_root(left: Path, right: Path) -> bool:
    try:
        return left.resolve() == right.resolve()
    except Exception:
        return os.path.realpath(str(left)) == os.path.realpath(str(right))


def _git_probe_source_root(source_root: Path, *args: str, timeout: int = 10) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(source_root), *args],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except Exception:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _git_check_source_root(source_root: Path, *args: str, timeout: int = 10) -> bool | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(source_root), *args],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except Exception:
        return None
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    return None


def _origin_default_base_ref(source_root: Path) -> tuple[str, str] | None:
    if _git_probe_source_root(source_root, "rev-parse", "--is-inside-work-tree") != "true":
        return None
    candidates: list[str] = []
    origin_head = _git_probe_source_root(source_root, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    if origin_head:
        candidates.append(origin_head)
    candidates.append("origin/main")
    seen: set[str] = set()
    for base_ref in candidates:
        if not base_ref or base_ref in seen:
            continue
        seen.add(base_ref)
        base_commit = _git_probe_source_root(source_root, "rev-parse", "--verify", f"{base_ref}^{{commit}}")
        if base_commit:
            return base_ref, base_commit
    return None


def _git_worktree_entries(source_root: Path) -> list[dict[str, str]]:
    output = _git_probe_source_root(source_root, "worktree", "list", "--porcelain", timeout=15)
    if not output:
        return []
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in output.splitlines():
        if raw_line.startswith("worktree "):
            if current:
                entries.append(current)
            current = {"path": raw_line.split(" ", 1)[1]}
        elif current is not None and raw_line.startswith("HEAD "):
            current["head"] = raw_line.split(" ", 1)[1]
        elif current is not None and raw_line.startswith("branch "):
            current["branch"] = raw_line.split(" ", 1)[1]
    if current:
        entries.append(current)
    return entries


def _source_root_is_clean(source_root: Path) -> bool:
    status = _git_probe_source_root(source_root, "status", "--porcelain", timeout=15)
    return status == ""


def _preferred_configured_base_factory_source_root(running_source_root: Path) -> Path | None:
    base = _origin_default_base_ref(running_source_root)
    if base is None:
        return None
    _base_ref, base_commit = base
    running_head = _git_probe_source_root(running_source_root, "rev-parse", "HEAD")
    if not running_head or running_head == base_commit:
        return None
    if _git_check_source_root(running_source_root, "merge-base", "--is-ancestor", running_head, base_commit) is not True:
        return None
    candidates: list[Path] = []
    for entry in _git_worktree_entries(running_source_root):
        if entry.get("head") != base_commit:
            continue
        raw_path = entry.get("path")
        if not raw_path:
            continue
        try:
            candidate = Path(raw_path).expanduser().resolve()
        except Exception:
            continue
        if _same_source_root(candidate, running_source_root):
            continue
        if not _factory_source_root_is_complete(candidate):
            continue
        if not _source_root_is_clean(candidate):
            continue
        candidates.append(candidate)
    if not candidates:
        return None
    return sorted(candidates, key=lambda path: str(path))[0]


def _preferred_factory_entrypoint_source_root(running_source_root: Path) -> Path | None:
    cwd_source_root = _find_cwd_factory_source_root()
    if cwd_source_root is not None and not _same_source_root(cwd_source_root, running_source_root):
        return cwd_source_root
    return _preferred_configured_base_factory_source_root(running_source_root)


def _factory_source_env(source_root: Path) -> dict[str, str]:
    env = {**os.environ}
    pythonpath = str(source_root)
    if env.get("PYTHONPATH"):
        pythonpath = f"{pythonpath}{os.pathsep}{env['PYTHONPATH']}"
    env["PYTHONPATH"] = pythonpath
    env["HERMES_PYTHON_SRC_ROOT"] = str(source_root)
    env["HERMES_FACTORY_SOURCE_DELEGATED"] = "1"
    return env


def _delegate_factory_entrypoint_if_needed() -> bool:
    """Re-exec ``hermes factory`` from the current/configured source root.

    This runs before importing ``hermes_cli.main``.  That ordering matters for
    console scripts installed from an editable primary checkout: importing the
    stale entrypoint first can make ``factory status`` and ``factory project
    tick`` read/dispatch from obsolete control-plane code even when a clean
    configured-base worktree is available.
    """

    if os.environ.get("HERMES_FACTORY_SOURCE_DELEGATED") == "1":
        return False
    if not _factory_command_requested():
        return False
    running_source_root = _bootstrap_source_root()
    if running_source_root is None:
        return False
    source_root = _preferred_factory_entrypoint_source_root(running_source_root)
    if source_root is None:
        return False
    argv = [sys.executable, "-m", "hermes_cli.main", *sys.argv[1:]]
    env = _factory_source_env(source_root)
    os.chdir(source_root)
    os.execvpe(sys.executable, argv, env)
    return True


def _run_hermes_main():
    from hermes_cli.main import main as hermes_main

    return hermes_main()


def main():
    """Console-script entry point with a Factory source-root bootstrap."""

    if _delegate_factory_entrypoint_if_needed():
        return None
    return _run_hermes_main()


# Apply on import — entry points only need ``import hermes_bootstrap`` first.
apply_windows_utf8_bootstrap()
suppress_platform_ver_console()
activate_durable_lazy_target()

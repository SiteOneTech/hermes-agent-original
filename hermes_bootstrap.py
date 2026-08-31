"""Windows UTF-8 bootstrap for Hermes entry points.

Python on Windows has two long-standing text-encoding footguns:

1. ``sys.stdout`` / ``sys.stderr`` are bound to the console code page
   (``cp1252`` on US-locale installs), so ``print("café")`` crashes with
   ``UnicodeEncodeError: 'charmap' codec can't encode character``.

2. Child processes spawned via ``subprocess`` don't know to use UTF-8
   unless ``PYTHONUTF8`` and/or ``PYTHONIOENCODING`` are set in their
   environment — so any Python subprocess (the execute_code sandbox,
   delegation children, linter subprocesses, etc.) inherits the same
   cp1252 defaults and hits the same UnicodeEncodeError.

This module fixes both on Windows *only* — POSIX is untouched.  It
should be imported at the very top of every Hermes entry point
(``hermes``, ``hermes-agent``, ``hermes-acp``, ``python -m gateway.run``,
``batch_runner.py``, ``cron/scheduler.py``) before any other imports
that might do file I/O or print to stdout.

What this module does on Windows:

  - Sets ``os.environ["PYTHONUTF8"] = "1"`` (PEP 540 UTF-8 mode) so
    every child process we spawn uses UTF-8 for ``open()`` and stdio.
  - Sets ``os.environ["PYTHONIOENCODING"] = "utf-8"`` for belt-and-
    suspenders — some tools read this instead of / in addition to
    ``PYTHONUTF8``.
  - Reconfigures ``sys.stdout`` / ``sys.stderr`` to UTF-8 in the current
    process, using the ``reconfigure()`` API (Python 3.7+).  This fixes
    ``print("café")`` in the parent without a re-exec.

What this module does NOT do:

  - It does not re-exec Python with ``-X utf8``, so ``open()`` calls in
    the *current* process still default to locale encoding.  Those need
    an explicit ``encoding="utf-8"`` at the call site (lint rule
    ``PLW1514`` / ``PYI058``).  Ruff is the right tool for that sweep.

What this module does on POSIX:

  - Nothing.  POSIX systems are already UTF-8 by default in 99% of cases,
    and we don't want to touch ``LANG``/``LC_*`` behavior that users may
    have configured intentionally.  If someone hits a C/POSIX locale on
    Linux, they can export ``PYTHONUTF8=1`` themselves — we won't override.

Idempotent: safe to call multiple times.  ``_bootstrap_once`` guards
against double-reconfigure.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

_IS_WINDOWS = sys.platform == "win32"
_bootstrap_applied = False


def apply_windows_utf8_bootstrap() -> bool:
    """Apply the Windows UTF-8 bootstrap if we're on Windows.

    Returns True if bootstrap was applied (i.e. we're on Windows and
    haven't already done this), False otherwise.  The return value is
    advisory — callers normally don't need it, but tests may want to
    assert the path was taken.

    Idempotent: subsequent calls after the first are a no-op.
    """
    global _bootstrap_applied

    if not _IS_WINDOWS:
        return False
    if _bootstrap_applied:
        return False

    # 1. Child processes inherit these and run in UTF-8 mode.
    #    We use setdefault() rather than overwriting so the user can
    #    explicitly opt out by setting PYTHONUTF8=0 in their environment
    #    (or PYTHONIOENCODING=something-else) if they really want to.
    os.environ.setdefault("PYTHONUTF8", "1")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

    # 2. Reconfigure the current process's stdio to UTF-8.  Needed
    #    because os.environ changes don't retroactively rebind sys.stdout
    #    — those were bound at interpreter startup based on the console
    #    code page.  ``reconfigure`` is a TextIOWrapper method since 3.7.
    #
    #    errors="replace" means that if we ever *read* something from
    #    stdin that isn't UTF-8 (unlikely but possible with piped input
    #    from legacy tools), we'll get U+FFFD replacement chars rather
    #    than a crash.  Output is pure UTF-8.
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None:
            continue
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            # Not a TextIOWrapper (could be redirected to a BytesIO in
            # tests, or a non-standard stream in some embedded cases).
            # Skip silently — the env-var fix is still in effect for
            # child processes, which is the bigger win.
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            # Already closed, or someone replaced it with something
            # non-reconfigurable.  Non-fatal.
            pass

    # stdin is reconfigured separately with errors="replace" too — input
    # from a legacy pipe shouldn't crash the process.
    stdin = getattr(sys, "stdin", None)
    if stdin is not None:
        reconfigure = getattr(stdin, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass

    _bootstrap_applied = True
    return True


def suppress_platform_ver_console() -> None:
    """Stub ``platform._syscmd_ver`` on Windows — decode-crash + flash guard.

    CPython's ``platform.win32_ver()`` (reached via ``platform.uname()`` /
    ``platform.platform()``, which the OpenAI SDK touches for its
    platform headers) shells out ``cmd /c ver``. Two failure modes:

    - **Console flash**: the ``check_output(..., shell=True)`` call has no
      ``CREATE_NO_WINDOW``, so a windowless parent (pythonw gateway, slash
      workers, kanban workers) flashes a visible console per call.
    - **UnicodeDecodeError on Python 3.11.0/3.11.1**: those micros lack
      CPython's ``encoding="locale"`` fix (added 3.11.2), so under PEP 540
      UTF-8 mode (which we enable above) the ``ver`` output — OEM code page
      bytes on localized Windows — is strict-utf-8 decoded and raises,
      crashing ``platform.platform()`` in any process that inherits
      ``PYTHONUTF8=1`` (issue #69413).

    Stubbing ``_syscmd_ver`` to return its inputs makes ``win32_ver()`` hit
    its documented fallback and read the version from
    ``sys.getwindowsversion()`` — same data, in-process, no subprocess.
    Mirrors ``hermes_cli._subprocess_compat.suppress_platform_ver_console``
    (kept there for callers that don't import bootstrap); double
    application is harmless. Lives here so EVERY entry point gets it —
    ``tui_gateway/slash_worker.py``, ``tui_gateway/entry.py``,
    ``run_agent.py``, ``batch_runner.py``, and ``cli.py`` import only
    ``hermes_bootstrap``, never ``hermes_cli.main``.
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
        # Hardening only — never let it break an entry point.
        pass


def harden_import_path(src_root: str | None = None) -> None:
    """Stop a package in the current directory from shadowing Hermes modules.

    Hermes ships top-level modules with common names (``utils``, ``proxy``,
    ``ui``).  Python always seeds ``sys.path`` with the current directory, so
    launching an entry point from a project that has its own ``utils/`` package
    makes ``from utils import ...`` resolve to the *user's* package and crash
    with an ImportError before the gateway can even start.

    The current directory reaches ``sys.path`` two ways, and a complete guard
    has to handle both:

      - As the empty string ``""`` (or ``"."``) that Python inserts at
        ``sys.path[0]`` for ``-m`` / script launches.
      - As its own *absolute* path, when a venv activation or a project that
        adds itself to ``PYTHONPATH`` puts the directory there explicitly.

    We drop the relative forms outright, then force the real Hermes source root
    to the front — relocating it ahead of any absolute cwd entry rather than
    only inserting when absent, so an absolute cwd path can't keep winning.

    ``src_root`` defaults to the directory this module lives in, which is the
    repository root for every shipped entry point, so the guard is
    self-sufficient and does not depend on the spawner exporting an env var.
    """
    root = src_root or os.environ.get("HERMES_PYTHON_SRC_ROOT") or os.path.dirname(
        os.path.abspath(__file__)
    )

    sys.path[:] = [p for p in sys.path if p not in ("", ".")]

    root_abs = os.path.abspath(root)
    sys.path[:] = [p for p in sys.path if os.path.abspath(p) != root_abs]
    sys.path.insert(0, root)


def activate_durable_lazy_target() -> None:
    """Put the durable lazy-install dir on ``sys.path`` if one is configured.

    On immutable Docker images the agent venv is sealed and lazy installs
    are redirected to a writable dir on the data volume
    (``HERMES_LAZY_INSTALL_TARGET``, e.g. ``/opt/data/lazy-packages``).
    Packages installed there on a previous run must be importable on this
    run, so we activate the dir here — at the very first import, before any
    backend module imports its SDK.

    The activation appends to the END of ``sys.path`` so the core venv
    always wins name collisions (see ``tools.lazy_deps`` for the full
    security rationale). Never raises; a missing/empty target is a no-op.
    """
    if not os.environ.get("HERMES_LAZY_INSTALL_TARGET", "").strip():
        return
    try:
        from tools import lazy_deps
        lazy_deps.activate_durable_lazy_target()
    except Exception:
        # Bootstrap must never crash an entry point. If activation fails the
        # backend simply reports itself unavailable, exactly as before.
        pass


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


# Apply on import — entry points just need ``import hermes_bootstrap``
# (or ``from hermes_bootstrap import apply_windows_utf8_bootstrap``) at
# the very top of their module, before importing anything else.  The
# import side effect does the right thing.
apply_windows_utf8_bootstrap()
suppress_platform_ver_console()

# Activate the durable lazy-install target (immutable Docker images) so
# packages installed into the data volume on a previous run are importable
# this run, before any backend module imports its SDK. No-op when unset.
activate_durable_lazy_target()

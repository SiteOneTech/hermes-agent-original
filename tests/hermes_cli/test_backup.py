"""Tests for hermes backup and import commands."""

import json
import os
import sqlite3
import stat
import zipfile
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _no_real_gateway_service(monkeypatch):
    """run_import() auto-installs the gateway service post-restore; tests must
    never touch the host's systemd/launchd. Individual tests re-patch these to
    assert the wiring."""
    import hermes_cli.gateway as gateway_mod

    monkeypatch.setattr(gateway_mod, "ensure_gateway_service", lambda **kw: False)
    monkeypatch.setattr(gateway_mod, "_is_service_running", lambda: False)


def _advance_backup_clock(seconds: float = 1.1) -> None:
    """Skew hermes_cli.backup's datetime forward instead of sleeping.

    Snapshot ids have 1-second resolution; tests that need two distinct
    timestamps previously slept >1s. This installs (once) a datetime shim in
    the backup module whose now() adds a cumulative offset, then bumps it.
    """
    import datetime as _dt

    import hermes_cli.backup as _backup

    shim = getattr(_backup.datetime, "_hermes_test_shim", None)
    if shim is None:
        class _ShimDatetime(_dt.datetime):
            _hermes_test_shim = True
            _offset = _dt.timedelta(0)

            @classmethod
            def now(cls, tz=None):  # noqa: D102
                return _dt.datetime.now(tz) + cls._offset

        _backup.datetime = _ShimDatetime
        shim = _ShimDatetime
    else:
        shim = _backup.datetime
    shim._offset += _dt.timedelta(seconds=seconds)

def _make_hermes_tree(root: Path) -> None:
    """Create a realistic ~/.hermes directory structure for testing."""
    (root / "config.yaml").write_text("model:\n  provider: openrouter\n")
    (root / ".env").write_text("OPENROUTER_API_KEY=sk-test-123\n")
    for db_name in ("memory_store.db", "hermes_state.db"):
        with sqlite3.connect(root / db_name) as conn:
            conn.execute("CREATE TABLE sample (value TEXT)")
            conn.execute("INSERT INTO sample VALUES ('test')")

    # Sessions
    (root / "sessions").mkdir(exist_ok=True)
    (root / "sessions" / "abc123.json").write_text("{}")

    # Skills
    (root / "skills").mkdir(exist_ok=True)
    (root / "skills" / "my-skill").mkdir()
    (root / "skills" / "my-skill" / "SKILL.md").write_text("# My Skill\n")

    # Skins
    (root / "skins").mkdir(exist_ok=True)
    (root / "skins" / "cyber.yaml").write_text("name: cyber\n")

    # Cron
    (root / "cron").mkdir(exist_ok=True)
    (root / "cron" / "jobs.json").write_text("[]")

    # Memories
    (root / "memories").mkdir(exist_ok=True)
    (root / "memories" / "notes.json").write_text("{}")

    # Profiles
    (root / "profiles").mkdir(exist_ok=True)
    (root / "profiles" / "coder").mkdir()
    (root / "profiles" / "coder" / "config.yaml").write_text("model:\n  provider: anthropic\n")
    (root / "profiles" / "coder" / ".env").write_text("ANTHROPIC_API_KEY=sk-ant-123\n")

    # hermes-agent repo (should be EXCLUDED)
    (root / "hermes-agent").mkdir(exist_ok=True)
    (root / "hermes-agent" / "run_agent.py").write_text("# big file\n")
    (root / "hermes-agent" / ".git").mkdir()
    (root / "hermes-agent" / ".git" / "HEAD").write_text("ref: refs/heads/main\n")

    # __pycache__ (should be EXCLUDED)
    (root / "plugins").mkdir(exist_ok=True)
    (root / "plugins" / "__pycache__").mkdir()
    (root / "plugins" / "__pycache__" / "mod.cpython-312.pyc").write_bytes(b"\x00")

    # PID files (should be EXCLUDED)
    (root / "gateway.pid").write_text("12345")

    # Logs (should be included)
    (root / "logs").mkdir(exist_ok=True)
    (root / "logs" / "agent.log").write_text("log line\n")


def _symlink_file_or_skip(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target)
    except OSError as exc:
        pytest.skip(f"symlinks unavailable in test environment: {exc}")


# ---------------------------------------------------------------------------
# _should_exclude tests
# ---------------------------------------------------------------------------

class TestShouldExclude:
    def test_excludes_hermes_agent(self):
        from hermes_cli.backup import _should_exclude
        assert _should_exclude(Path("hermes-agent/run_agent.py"))
        assert _should_exclude(Path("hermes-agent/.git/HEAD"))

    def test_excludes_pycache(self):
        from hermes_cli.backup import _should_exclude
        assert _should_exclude(Path("plugins/__pycache__/mod.cpython-312.pyc"))

    def test_excludes_pyc_files(self):
        from hermes_cli.backup import _should_exclude
        assert _should_exclude(Path("some/module.pyc"))

    def test_excludes_pid_files(self):
        from hermes_cli.backup import _should_exclude
        assert _should_exclude(Path("gateway.pid"))
        assert _should_exclude(Path("cron.pid"))

    def test_excludes_checkpoints(self):
        """checkpoints/ is session-local trajectory cache — hash-keyed,
        regenerated per-session, won't port to another machine anyway."""
        from hermes_cli.backup import _should_exclude
        assert _should_exclude(Path("checkpoints/abc123/trajectory.json"))
        assert _should_exclude(Path("checkpoints/deadbeef/step_0001.json"))

    def test_excludes_backups_dir(self):
        """backups/ is excluded so pre-update backups don't nest exponentially."""
        from hermes_cli.backup import _should_exclude
        assert _should_exclude(Path("backups/pre-update-2026-04-27-063400.zip"))

    def test_excludes_state_snapshots_dir(self):
        """state-snapshots/ is excluded for the same reason as backups/: every
        quick / pre-update snapshot holds its own copy of state.db, so zipping
        the tree would ship the DB once per retained snapshot."""
        from hermes_cli.backup import _EXCLUDED_DIRS, _QUICK_SNAPSHOTS_DIR, _should_exclude
        assert _QUICK_SNAPSHOTS_DIR in _EXCLUDED_DIRS
        assert _should_exclude(Path(_QUICK_SNAPSHOTS_DIR) / "20260814-203829-2026-08-15" / "state.db")
        assert _should_exclude(Path(_QUICK_SNAPSHOTS_DIR) / "20260814-203829-2026-08-15" / "manifest.json")
        # Named profiles accumulate snapshots too.
        assert _should_exclude(Path("profiles/coder") / _QUICK_SNAPSHOTS_DIR / "x" / "state.db")
        # The live DB is still backed up.
        assert not _should_exclude(Path("state.db"))

    def test_excludes_sqlite_sidecars(self):
        """SQLite WAL/SHM/journal sidecars must not ship alongside the
        safe-copied .db — pairing a fresh snapshot with stale sidecar state
        produces a torn restore."""
        from hermes_cli.backup import _should_exclude
        assert _should_exclude(Path("state.db-wal"))
        assert _should_exclude(Path("state.db-shm"))
        assert _should_exclude(Path("state.db-journal"))
        assert _should_exclude(Path("memory_store.db-wal"))
        # The .db itself is still included (and safe-copied separately)
        assert not _should_exclude(Path("state.db"))

    def test_includes_config(self):
        from hermes_cli.backup import _should_exclude
        assert not _should_exclude(Path("config.yaml"))

    def test_includes_env(self):
        from hermes_cli.backup import _should_exclude
        assert not _should_exclude(Path(".env"))

    def test_includes_skills(self):
        from hermes_cli.backup import _should_exclude
        assert not _should_exclude(Path("skills/my-skill/SKILL.md"))

    def test_includes_profiles(self):
        from hermes_cli.backup import _should_exclude
        assert not _should_exclude(Path("profiles/coder/config.yaml"))

    def test_includes_sessions(self):
        from hermes_cli.backup import _should_exclude
        assert not _should_exclude(Path("sessions/abc.json"))

    def test_includes_logs(self):
        from hermes_cli.backup import _should_exclude
        assert not _should_exclude(Path("logs/agent.log"))

    def test_includes_nested_hermes_agent_in_skills(self):
        """skills/autonomous-ai-agents/hermes-agent/ must NOT be excluded —
        only the root-level hermes-agent/ repo is skipped."""
        from hermes_cli.backup import _should_exclude
        assert not _should_exclude(Path("skills/autonomous-ai-agents/hermes-agent/SKILL.md"))
        assert not _should_exclude(Path("skills/autonomous-ai-agents/hermes-agent/sub/item.txt"))

    @pytest.mark.parametrize(
        "rel",
        [
            "plugins/my-plugin/.venv/lib/python3.12/site-packages/x/__init__.py",
            "plugins/my-plugin/venv/bin/python",
            "mcp/server/site-packages/pkg/mod.py",
            ".cache/uv/wheels/abc.whl",
            "plugins/p/.cache/pip/http/deadbeef",
            ".tox/py312/log.txt",
            ".nox/tests/bin/pytest",
            "plugins/p/.pytest_cache/v/cache/lastfailed",
            ".mypy_cache/3.12/agent.meta.json",
            ".ruff_cache/0.4.0/abc",
        ],
    )
    def test_excludes_regeneratable_dependency_and_cache_dirs(self, rel):
        """Python dep trees and tool caches under HERMES_HOME must be skipped —
        these are what balloon a backup to hundreds of thousands of files."""
        from hermes_cli.backup import _should_exclude
        assert _should_exclude(Path(rel))

    def test_does_not_exclude_curator_archive(self):
        """skills/.archive/ holds restorable archived skills and MUST survive
        a backup — it is intentionally NOT in the exclusion set."""
        from hermes_cli.backup import _should_exclude
        assert not _should_exclude(Path("skills/.archive/old-skill/SKILL.md"))

    def test_does_not_exclude_legit_files_resembling_cache_names(self):
        """Only directory-component matches are excluded; a normal file is kept."""
        from hermes_cli.backup import _should_exclude
        assert not _should_exclude(Path("skills/my-skill/venv-notes.md"))
        assert not _should_exclude(Path("memories/cache.json"))

    def test_excludes_managed_runtime_trees_at_root(self):
        """models/, runtimes/, and node/ at a profile-home root hold
        re-downloadable GGUF weights and runtime binaries that reach
        hundreds of GB — zipping them is the 20-minute-hang symptom."""
        from hermes_cli.backup import _should_exclude
        assert _should_exclude(Path("models/Qwen3.6-27B-Q4_K_M.gguf"))
        assert _should_exclude(Path("models/assets/mmproj.gguf"))
        assert _should_exclude(Path("runtimes/llamacpp/b10362/cuda/ggml-cuda.dll"))
        assert _should_exclude(Path("node/node.exe"))
        # Named profiles download their own copies.
        assert _should_exclude(Path("profiles/clean/models/big.gguf"))
        assert _should_exclude(Path("profiles/clean/runtimes/llamacpp/x.dll"))

    def test_keeps_nested_dirs_named_like_runtime_trees(self):
        """A deeper directory that happens to be called models/ or node/ is
        user data (a skill's assets, project files) and must survive."""
        from hermes_cli.backup import _should_exclude
        assert not _should_exclude(Path("skills/mlops/models/notes.md"))
        assert not _should_exclude(Path("scratch/node/index.js"))
        assert not _should_exclude(Path("profiles/clean/skills/x/models/a.txt"))

    def test_excludes_desktop_emergency_state_db_baks(self):
        """The desktop updater's pre-flight drops timestamped
        state.db.pre-update-emergency-*.bak files at the HERMES_HOME root —
        backup artifacts in the same class as backups/, so a full backup
        must not re-ship them."""
        from hermes_cli.backup import _should_exclude
        assert _should_exclude(
            Path("state.db.pre-update-emergency-2026-08-15T04-55-33-619Z.bak")
        )
        assert _should_exclude(
            Path("profiles/coder/state.db.pre-update-emergency-2026-08-15T04-55-33-619Z.bak")
        )
        # Other .bak files are user data and stay.
        assert not _should_exclude(Path("config.yaml.bak"))


# ---------------------------------------------------------------------------
# _iter_backup_files tests
# ---------------------------------------------------------------------------

class TestIterBackupFiles:
    def test_manual_and_automatic_paths_share_one_walk(self, tmp_path):
        """Both backup entry points must select the identical file set.

        Before the walks were unified, the automatic pre-update path pruned
        ``hermes-agent`` at ANY depth, silently dropping nested skill dirs
        like ``skills/autonomous-ai-agents/hermes-agent/`` that the manual
        path preserved. One shared iterator makes that drift impossible;
        this test pins the contract."""
        from hermes_cli.backup import _iter_backup_files

        root = tmp_path / ".hermes"
        root.mkdir()
        _make_hermes_tree(root)

        # The case the old automatic walk got wrong: a nested dir named
        # hermes-agent holding real skill content.
        nested = root / "skills" / "autonomous-ai-agents" / "hermes-agent"
        nested.mkdir(parents=True)
        (nested / "SKILL.md").write_text("# nested skill\n")

        # A root-level managed runtime tree that both paths must prune.
        (root / "models").mkdir()
        (root / "models" / "big.gguf").write_bytes(b"\x00" * 64)

        out_path = tmp_path / "out.zip"
        selected = {str(rel) for _, rel in _iter_backup_files(root, out_path)}

        rel_nested = str(Path("skills/autonomous-ai-agents/hermes-agent/SKILL.md"))
        assert rel_nested in selected
        assert str(Path("models/big.gguf")) not in selected
        assert not any(s.startswith("hermes-agent") for s in selected)

    def test_skipped_dirs_collected_for_summary(self, tmp_path):
        from hermes_cli.backup import _iter_backup_files

        root = tmp_path / ".hermes"
        root.mkdir()
        _make_hermes_tree(root)
        (root / "models").mkdir()
        (root / "models" / "big.gguf").write_bytes(b"\x00")

        skipped: set = set()
        list(_iter_backup_files(root, tmp_path / "out.zip", skipped))
        assert "models" in skipped
        assert "hermes-agent" in skipped

# ---------------------------------------------------------------------------
# Backup tests
# ---------------------------------------------------------------------------

class TestBackup:
    def test_creates_zip(self, tmp_path, monkeypatch):
        """Backup creates a valid zip containing expected files."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        _make_hermes_tree(hermes_home)

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        # get_default_hermes_root needs this
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        out_zip = tmp_path / "backup.zip"
        args = Namespace(output=str(out_zip))

        from hermes_cli.backup import run_backup
        run_backup(args)

        assert out_zip.exists()
        with zipfile.ZipFile(out_zip, "r") as zf:
            names = zf.namelist()
            # Config should be present
            assert "config.yaml" in names
            assert ".env" in names
            # Skills
            assert "skills/my-skill/SKILL.md" in names
            # Profiles
            assert "profiles/coder/config.yaml" in names
            assert "profiles/coder/.env" in names
            # Sessions
            assert "sessions/abc123.json" in names
            # Logs
            assert "logs/agent.log" in names
            # Skins
            assert "skins/cyber.yaml" in names

    def test_failed_sqlite_backup_never_raw_copies_live_wal_db(self, tmp_path, monkeypatch, capsys):
        """A failed backup() must not silently archive the stale main DB file.

        Keep a real, uncheckpointed WAL transaction live so a raw copy of only
        ``state.db`` would be a valid-looking but torn snapshot.
        """
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        (hermes_home / "config.yaml").write_text("model: test\n")
        db_path = hermes_home / "state.db"

        writer = sqlite3.connect(db_path)
        writer.execute("PRAGMA journal_mode=WAL")
        writer.execute("PRAGMA wal_autocheckpoint=0")
        writer.execute("CREATE TABLE events (value TEXT)")
        writer.commit()
        writer.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        writer.execute("INSERT INTO events VALUES ('only-in-wal')")
        writer.commit()
        assert Path(f"{db_path}-wal").stat().st_size > 0

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        import hermes_cli.backup as backup_mod
        real_connect = backup_mod.sqlite3.connect

        class FailingBackupConnection:
            def __init__(self, connection):
                self._connection = connection

            def backup(self, _destination):
                raise sqlite3.OperationalError("forced backup failure")

            def close(self):
                self._connection.close()

        def connect_with_failed_backup(database, *args, **kwargs):
            connection = real_connect(database, *args, **kwargs)
            if str(database).startswith(f"file:{db_path}"):
                return FailingBackupConnection(connection)
            return connection

        monkeypatch.setattr(backup_mod.sqlite3, "connect", connect_with_failed_backup)
        out_zip = tmp_path / "backup.zip"
        try:
            backup_mod.run_backup(Namespace(output=str(out_zip)))
        finally:
            writer.close()

        with zipfile.ZipFile(out_zip) as zf:
            assert "config.yaml" in zf.namelist()
            assert "state.db" not in zf.namelist()

        output = capsys.readouterr().out
        assert "Backup incomplete" in output
        assert "state.db: SQLite safe copy failed" in output
        assert "Restore with:" not in output

    def test_db_snapshots_staged_beside_output_zip(self, tmp_path, monkeypatch):
        """SQLite staging temp files must be created on the output zip's
        filesystem (dir=out_path.parent), NOT the system /tmp default — a
        small tmpfs there silently drops large DBs from the backup (#35376)."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        _make_hermes_tree(hermes_home)

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        out_dir = tmp_path / "external-drive"
        out_dir.mkdir()
        out_zip = out_dir / "backup.zip"
        args = Namespace(output=str(out_zip))

        import hermes_cli.backup as backup_mod
        staged_dirs = []
        real_ntf = backup_mod.tempfile.NamedTemporaryFile

        def _spy(*a, **kw):
            staged_dirs.append(kw.get("dir"))
            return real_ntf(*a, **kw)

        monkeypatch.setattr(backup_mod.tempfile, "NamedTemporaryFile", _spy)
        backup_mod.run_backup(args)

        # At least one .db was staged, and every staging call targeted the
        # output zip's directory rather than the system temp default.
        assert staged_dirs, "no SQLite snapshot was staged"
        assert all(d == str(out_dir) for d in staged_dirs), staged_dirs

    def test_pre_update_db_snapshots_staged_beside_output_zip(self, tmp_path, monkeypatch):
        """The pre-update/pre-migration zip path (_write_full_zip_backup) must
        also stage SQLite snapshots beside its output zip, not in /tmp."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        _make_hermes_tree(hermes_home)

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        out_zip = hermes_home / "backups" / "pre-update-test.zip"
        out_zip.parent.mkdir(parents=True, exist_ok=True)

        import hermes_cli.backup as backup_mod
        staged_dirs = []
        real_ntf = backup_mod.tempfile.NamedTemporaryFile

        def _spy(*a, **kw):
            staged_dirs.append(kw.get("dir"))
            return real_ntf(*a, **kw)

        monkeypatch.setattr(backup_mod.tempfile, "NamedTemporaryFile", _spy)
        result = backup_mod._write_full_zip_backup(out_zip, hermes_home)

        assert result is not None
        assert staged_dirs, "no SQLite snapshot was staged"
        assert all(d == str(out_zip.parent) for d in staged_dirs), staged_dirs

    def test_excludes_hermes_agent(self, tmp_path, monkeypatch):
        """Backup does NOT include hermes-agent/ directory."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        _make_hermes_tree(hermes_home)

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        out_zip = tmp_path / "backup.zip"
        args = Namespace(output=str(out_zip))

        from hermes_cli.backup import run_backup
        run_backup(args)

        with zipfile.ZipFile(out_zip, "r") as zf:
            names = zf.namelist()
            agent_files = [n for n in names if "hermes-agent" in n]
            assert agent_files == [], f"hermes-agent files leaked into backup: {agent_files}"

    def test_excludes_dependency_and_cache_trees(self, tmp_path, monkeypatch):
        """A plugin venv / site-packages / pip cache under HERMES_HOME must be
        pruned by the walk, while real data (skills, config) is preserved.
        This is the regression guard for the ballooning-backup bug."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        _make_hermes_tree(hermes_home)

        # Simulate the heavy regeneratable trees that ballooned the backup.
        venv_pkg = hermes_home / "plugins" / "heavy" / ".venv" / "lib" / "site-packages" / "dep"
        venv_pkg.mkdir(parents=True)
        (venv_pkg / "__init__.py").write_text("# dep\n")
        pip_cache = hermes_home / ".cache" / "uv" / "wheels"
        pip_cache.mkdir(parents=True)
        (pip_cache / "abc.whl").write_bytes(b"\x00")

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        out_zip = tmp_path / "backup.zip"
        from hermes_cli.backup import run_backup
        run_backup(Namespace(output=str(out_zip)))

        with zipfile.ZipFile(out_zip, "r") as zf:
            names = zf.namelist()
        leaked = [n for n in names if ".venv" in n or "site-packages" in n or ".cache" in n]
        assert leaked == [], f"regeneratable trees leaked into backup: {leaked}"
        # Real data still present.
        assert "skills/my-skill/SKILL.md" in names
        assert "config.yaml" in names

    def test_includes_nested_hermes_agent_in_skills(self, tmp_path, monkeypatch):
        """Backup includes skills/.../hermes-agent/ but NOT root hermes-agent/."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        _make_hermes_tree(hermes_home)

        # Add a nested hermes-agent directory inside skills (like the real layout)
        nested = hermes_home / "skills" / "autonomous-ai-agents" / "hermes-agent"
        nested.mkdir(parents=True)
        (nested / "SKILL.md").write_text("# Hermes Agent Skill\n")
        (nested / "sub").mkdir()
        (nested / "sub" / "item.txt").write_text("nested content\n")

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        out_zip = tmp_path / "backup.zip"
        args = Namespace(output=str(out_zip))

        from hermes_cli.backup import run_backup
        run_backup(args)

        with zipfile.ZipFile(out_zip, "r") as zf:
            names = zf.namelist()
            # Root hermes-agent must be excluded
            root_agent = [n for n in names if n.startswith("hermes-agent/")]
            assert root_agent == [], f"root hermes-agent leaked: {root_agent}"
            # Nested skill hermes-agent must be included
            assert "skills/autonomous-ai-agents/hermes-agent/SKILL.md" in names
            assert "skills/autonomous-ai-agents/hermes-agent/sub/item.txt" in names

    def test_excludes_pycache(self, tmp_path, monkeypatch):
        """Backup does NOT include __pycache__ dirs."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        _make_hermes_tree(hermes_home)

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        out_zip = tmp_path / "backup.zip"
        args = Namespace(output=str(out_zip))

        from hermes_cli.backup import run_backup
        run_backup(args)

        with zipfile.ZipFile(out_zip, "r") as zf:
            names = zf.namelist()
            pycache_files = [n for n in names if "__pycache__" in n]
            assert pycache_files == []

    def test_excludes_pid_files(self, tmp_path, monkeypatch):
        """Backup does NOT include PID files."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        _make_hermes_tree(hermes_home)

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        out_zip = tmp_path / "backup.zip"
        args = Namespace(output=str(out_zip))

        from hermes_cli.backup import run_backup
        run_backup(args)

        with zipfile.ZipFile(out_zip, "r") as zf:
            names = zf.namelist()
            pid_files = [n for n in names if n.endswith(".pid")]
            assert pid_files == []

    def test_default_output_path(self, tmp_path, monkeypatch):
        """When no output path given, zip goes to ~/hermes-backup-*.zip."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        (hermes_home / "config.yaml").write_text("model: test\n")

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        args = Namespace(output=None)

        from hermes_cli.backup import run_backup
        run_backup(args)

        # Should exist in home dir
        zips = list(tmp_path.glob("hermes-backup-*.zip"))
        assert len(zips) == 1

    def test_skips_symlinked_files(self, tmp_path, monkeypatch):
        """Backup must not dereference symlinks and leak files outside HERMES_HOME."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        _make_hermes_tree(hermes_home)
        outside = tmp_path / "outside-secret.txt"
        outside.write_text("outside secret\n")
        _symlink_file_or_skip(hermes_home / "skills" / "outside-link.txt", outside)

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        out_zip = tmp_path / "backup.zip"
        args = Namespace(output=str(out_zip))

        from hermes_cli.backup import run_backup
        run_backup(args)

        with zipfile.ZipFile(out_zip, "r") as zf:
            names = zf.namelist()
            assert "skills/outside-link.txt" not in names
            assert all(zf.read(name) != b"outside secret\n" for name in names)

    def test_state_snapshots_not_nested_into_backup(self, tmp_path, monkeypatch):
        """A quick snapshot left under state-snapshots/ must not be re-shipped
        by the full backup — each snapshot already holds a copy of state.db, so
        nesting them multiplies the archive by (1 + retained snapshots)."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        _make_hermes_tree(hermes_home)
        with sqlite3.connect(hermes_home / "state.db") as conn:
            conn.execute("CREATE TABLE sessions (id TEXT PRIMARY KEY)")
            conn.execute("INSERT INTO sessions VALUES ('s1')")

        from hermes_cli.backup import _QUICK_SNAPSHOTS_DIR, create_quick_snapshot, run_backup

        # Real producer, so the layout under state-snapshots/ is whatever the
        # code actually writes (manifest.json + state.db copy + ...).
        snap_id = create_quick_snapshot(hermes_home=hermes_home)
        assert snap_id and (hermes_home / _QUICK_SNAPSHOTS_DIR / snap_id / "state.db").exists()

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        out_zip = tmp_path / "backup.zip"
        run_backup(Namespace(output=str(out_zip)))

        with zipfile.ZipFile(out_zip, "r") as zf:
            names = zf.namelist()
        assert not any(n.startswith(_QUICK_SNAPSHOTS_DIR + "/") for n in names), names
        # Exactly one state.db in the archive: the live one.
        assert [n for n in names if n == "state.db" or n.endswith("/state.db")] == ["state.db"]


# ---------------------------------------------------------------------------
# _validate_backup_zip tests
# ---------------------------------------------------------------------------

class TestValidateBackupZip:
    def _make_zip(self, zip_path: Path, filenames: list[str]) -> None:
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name in filenames:
                zf.writestr(name, "dummy")

    def test_state_db_passes(self, tmp_path):
        """A zip containing state.db is accepted as a valid Hermes backup."""
        from hermes_cli.backup import _validate_backup_zip
        zip_path = tmp_path / "backup.zip"
        self._make_zip(zip_path, ["state.db", "sessions/abc.json"])
        with zipfile.ZipFile(zip_path, "r") as zf:
            ok, reason = _validate_backup_zip(zf)
        assert ok, reason

    def test_old_wrong_db_name_fails(self, tmp_path):
        """A zip with only hermes_state.db (old wrong name) is rejected."""
        from hermes_cli.backup import _validate_backup_zip
        zip_path = tmp_path / "old.zip"
        self._make_zip(zip_path, ["hermes_state.db", "memory_store.db"])
        with zipfile.ZipFile(zip_path, "r") as zf:
            ok, reason = _validate_backup_zip(zf)
        assert not ok

    def test_config_yaml_passes(self, tmp_path):
        """A zip containing config.yaml is accepted (existing behaviour preserved)."""
        from hermes_cli.backup import _validate_backup_zip
        zip_path = tmp_path / "backup.zip"
        self._make_zip(zip_path, ["config.yaml", "skills/x/SKILL.md"])
        with zipfile.ZipFile(zip_path, "r") as zf:
            ok, reason = _validate_backup_zip(zf)
        assert ok, reason


# ---------------------------------------------------------------------------
# Import tests
# ---------------------------------------------------------------------------

class TestImport:
    def _make_backup_zip(self, zip_path: Path, files: dict[str, str | bytes]) -> None:
        """Create a test zip with given files."""
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                if isinstance(content, bytes):
                    zf.writestr(name, content)
                else:
                    zf.writestr(name, content)

    def test_import_auto_installs_gateway_service(self, tmp_path, monkeypatch):
        """After a restore, run_import brings the gateway service up without
        prompting — restored cron jobs and bot tokens must not sit dormant
        (the install-then-import dead-gateway bug)."""
        import hermes_cli.gateway as gateway_mod

        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        calls = []
        monkeypatch.setattr(
            gateway_mod, "ensure_gateway_service",
            lambda **kw: calls.append(kw) or True,
        )
        monkeypatch.setattr(gateway_mod, "_is_service_running", lambda: False)

        zip_path = tmp_path / "backup.zip"
        self._make_backup_zip(zip_path, {"config.yaml": "model: test\n"})

        from hermes_cli.backup import run_import
        run_import(Namespace(zipfile=str(zip_path), force=True))

        assert calls and calls[0].get("context") == "import"

    def test_import_skips_service_when_already_running(self, tmp_path, monkeypatch):
        """A live gateway is left alone — no reinstall churn during import."""
        import hermes_cli.gateway as gateway_mod

        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        calls = []
        monkeypatch.setattr(
            gateway_mod, "ensure_gateway_service",
            lambda **kw: calls.append(kw) or True,
        )
        monkeypatch.setattr(gateway_mod, "_is_service_running", lambda: True)

        zip_path = tmp_path / "backup.zip"
        self._make_backup_zip(zip_path, {"config.yaml": "model: test\n"})

        from hermes_cli.backup import run_import
        run_import(Namespace(zipfile=str(zip_path), force=True))

        assert not calls

    def test_import_survives_service_layer_import_failure(self, tmp_path, monkeypatch, capsys):
        """If the service helpers can't even be reached, import still completes
        and prints the manual fallback."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        import hermes_cli.gateway as gateway_mod

        def boom():
            raise RuntimeError("service layer unavailable")

        monkeypatch.setattr(gateway_mod, "_is_service_running", boom)

        zip_path = tmp_path / "backup.zip"
        self._make_backup_zip(zip_path, {"config.yaml": "model: test\n"})

        from hermes_cli.backup import run_import
        run_import(Namespace(zipfile=str(zip_path), force=True))

        out = capsys.readouterr().out
        assert "Done. Your Hermes configuration has been restored." in out
        assert "hermes gateway install" in out

    def test_restores_files(self, tmp_path, monkeypatch):
        """Import extracts files into hermes home."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        zip_path = tmp_path / "backup.zip"
        self._make_backup_zip(zip_path, {
            "config.yaml": "model:\n  provider: openrouter\n",
            ".env": "OPENROUTER_API_KEY=sk-test\n",
            "skills/my-skill/SKILL.md": "# My Skill\n",
            "profiles/coder/config.yaml": "model:\n  provider: anthropic\n",
        })

        args = Namespace(zipfile=str(zip_path), force=True)

        from hermes_cli.backup import run_import
        run_import(args)

        assert (hermes_home / "config.yaml").read_text() == "model:\n  provider: openrouter\n"
        assert (hermes_home / ".env").read_text() == "OPENROUTER_API_KEY=sk-test\n"
        assert (hermes_home / "skills" / "my-skill" / "SKILL.md").read_text() == "# My Skill\n"
        assert (hermes_home / "profiles" / "coder" / "config.yaml").exists()

    def test_strips_hermes_prefix(self, tmp_path, monkeypatch):
        """Import strips .hermes/ prefix if all entries share it."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        zip_path = tmp_path / "backup.zip"
        self._make_backup_zip(zip_path, {
            ".hermes/config.yaml": "model: test\n",
            ".hermes/skills/a/SKILL.md": "# A\n",
        })

        args = Namespace(zipfile=str(zip_path), force=True)

        from hermes_cli.backup import run_import
        run_import(args)

        assert (hermes_home / "config.yaml").read_text() == "model: test\n"
        assert (hermes_home / "skills" / "a" / "SKILL.md").read_text() == "# A\n"

    def test_rejects_empty_zip(self, tmp_path, monkeypatch):
        """Import rejects an empty zip."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        zip_path = tmp_path / "empty.zip"
        with zipfile.ZipFile(zip_path, "w"):
            pass  # empty

        args = Namespace(zipfile=str(zip_path), force=True)

        from hermes_cli.backup import run_import
        with pytest.raises(SystemExit):
            run_import(args)

    def test_rejects_non_hermes_zip(self, tmp_path, monkeypatch):
        """Import rejects a zip that doesn't look like a hermes backup."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        zip_path = tmp_path / "random.zip"
        self._make_backup_zip(zip_path, {
            "some/random/file.txt": "hello",
            "another/thing.json": "{}",
        })

        args = Namespace(zipfile=str(zip_path), force=True)

        from hermes_cli.backup import run_import
        with pytest.raises(SystemExit):
            run_import(args)

    def test_blocks_path_traversal(self, tmp_path, monkeypatch):
        """Import blocks zip entries with path traversal."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        zip_path = tmp_path / "evil.zip"
        # Include a marker file so validation passes
        self._make_backup_zip(zip_path, {
            "config.yaml": "model: test\n",
            "../../etc/passwd": "root:x:0:0\n",
        })

        args = Namespace(zipfile=str(zip_path), force=True)

        from hermes_cli.backup import run_import
        run_import(args)

        # config.yaml should be restored
        assert (hermes_home / "config.yaml").exists()
        # traversal file should NOT exist outside hermes home
        assert not (tmp_path / "etc" / "passwd").exists()

    def test_preserves_live_gateway_state(self, tmp_path, monkeypatch):
        """Import must not overwrite the target's gateway_state.json.

        The backup carries the *source* machine's gateway run/desired state.
        Restoring it onto a hosted container drives the boot reconciler off
        stale/foreign state and leaves the gateway stuck "starting",
        disconnecting it from the Nous portal (NS-508). The live file wins.
        """
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        # The target (e.g. hosted container) already has its own live state.
        live_state = '{"gateway_state": "running", "desired_state": "running"}'
        (hermes_home / "gateway_state.json").write_text(live_state)

        zip_path = tmp_path / "backup.zip"
        self._make_backup_zip(zip_path, {
            "config.yaml": "model: test\n",
            # A backup from a laptop where the gateway was stopped.
            "gateway_state.json": '{"gateway_state": "stopped", "desired_state": "stopped"}',
        })

        args = Namespace(zipfile=str(zip_path), force=True)

        from hermes_cli.backup import run_import
        run_import(args)

        # config.yaml is restored normally...
        assert (hermes_home / "config.yaml").read_text() == "model: test\n"
        # ...but the live gateway_state.json is untouched.
        assert (hermes_home / "gateway_state.json").read_text() == live_state

    def test_does_not_seed_gateway_state_when_absent(self, tmp_path, monkeypatch):
        """A backup's gateway_state.json is dropped, not written, when the
        target has none — a foreign state must never seed the reconciler."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        zip_path = tmp_path / "backup.zip"
        self._make_backup_zip(zip_path, {
            "config.yaml": "model: test\n",
            "gateway_state.json": '{"gateway_state": "stopped"}',
        })

        args = Namespace(zipfile=str(zip_path), force=True)

        from hermes_cli.backup import run_import
        run_import(args)

        assert (hermes_home / "config.yaml").exists()
        assert not (hermes_home / "gateway_state.json").exists()

    def test_preserves_per_profile_gateway_state(self, tmp_path, monkeypatch):
        """The skip is matched by basename, so a named profile's
        gateway_state.json (profiles/<name>/gateway_state.json) is preserved
        the same way the root profile's is."""
        hermes_home = tmp_path / ".hermes"
        (hermes_home / "profiles" / "coder").mkdir(parents=True)
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        live_state = '{"gateway_state": "running"}'
        (hermes_home / "profiles" / "coder" / "gateway_state.json").write_text(live_state)

        zip_path = tmp_path / "backup.zip"
        self._make_backup_zip(zip_path, {
            "config.yaml": "model: test\n",
            "profiles/coder/config.yaml": "model: anthropic\n",
            "profiles/coder/gateway_state.json": '{"gateway_state": "stopped"}',
        })

        args = Namespace(zipfile=str(zip_path), force=True)

        from hermes_cli.backup import run_import
        run_import(args)

        # Profile config is restored, but its live gateway state is preserved.
        assert (hermes_home / "profiles" / "coder" / "config.yaml").read_text() == "model: anthropic\n"
        assert (
            hermes_home / "profiles" / "coder" / "gateway_state.json"
        ).read_text() == live_state

    def test_preserves_runtime_pid_and_process_files(self, tmp_path, monkeypatch):
        """gateway.pid / cron.pid / gateway.lock / processes.json from a backup
        reference the source machine's process namespace and must never be
        written over the target's."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        # Live runtime files belonging to the target's own processes.
        (hermes_home / "gateway.pid").write_text("4242")
        (hermes_home / "processes.json").write_text('{"live": true}')

        zip_path = tmp_path / "backup.zip"
        self._make_backup_zip(zip_path, {
            "config.yaml": "model: test\n",
            "gateway.pid": "9999",
            "cron.pid": "8888",
            "gateway.lock": "7777",
            "processes.json": '{"stale": true}',
        })

        args = Namespace(zipfile=str(zip_path), force=True)

        from hermes_cli.backup import run_import
        run_import(args)

        # Live runtime files are untouched; the backup's foreign ones never land.
        assert (hermes_home / "gateway.pid").read_text() == "4242"
        assert (hermes_home / "processes.json").read_text() == '{"live": true}'
        # cron.pid / gateway.lock had no live copy and were not seeded.
        assert not (hermes_home / "cron.pid").exists()
        assert not (hermes_home / "gateway.lock").exists()

    def test_confirmation_prompt_abort(self, tmp_path, monkeypatch):
        """Import aborts when user says no to confirmation."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        # Pre-existing config triggers the confirmation
        (hermes_home / "config.yaml").write_text("existing: true\n")
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        zip_path = tmp_path / "backup.zip"
        self._make_backup_zip(zip_path, {
            "config.yaml": "model: restored\n",
        })

        args = Namespace(zipfile=str(zip_path), force=False)

        from hermes_cli.backup import run_import
        with patch("builtins.input", return_value="n"):
            run_import(args)

        # Original config should be unchanged
        assert (hermes_home / "config.yaml").read_text() == "existing: true\n"

    def test_force_skips_confirmation(self, tmp_path, monkeypatch):
        """Import with --force skips confirmation and overwrites."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        (hermes_home / "config.yaml").write_text("existing: true\n")
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        zip_path = tmp_path / "backup.zip"
        self._make_backup_zip(zip_path, {
            "config.yaml": "model: restored\n",
        })

        args = Namespace(zipfile=str(zip_path), force=True)

        from hermes_cli.backup import run_import
        run_import(args)

        assert (hermes_home / "config.yaml").read_text() == "model: restored\n"

    def test_missing_file_exits(self, tmp_path, monkeypatch):
        """Import exits with error for nonexistent file."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))

        args = Namespace(zipfile=str(tmp_path / "nonexistent.zip"), force=True)

        from hermes_cli.backup import run_import
        with pytest.raises(SystemExit):
            run_import(args)

    @pytest.mark.skipif(os.name != "posix", reason="POSIX file permissions only")
    def test_restores_secret_files_with_0600_perms(self, tmp_path, monkeypatch):
        """Secret files must end up at 0600 after restore (zipfile drops mode bits)."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        zip_path = tmp_path / "backup.zip"
        self._make_backup_zip(zip_path, {
            "config.yaml": "model: openrouter\n",
            ".env": "OPENROUTER_API_KEY=sk-secret\n",
            "auth.json": '{"providers": {"nous": "token"}}',
            "state.db": b"SQLite format 3\x00",
            "profiles/coder/.env": "ANTHROPIC_API_KEY=sk-ant-secret\n",
        })

        args = Namespace(zipfile=str(zip_path), force=True)

        from hermes_cli.backup import run_import
        run_import(args)

        for rel in (".env", "auth.json", "state.db", "profiles/coder/.env"):
            mode = (hermes_home / rel).stat().st_mode & 0o777
            assert mode == 0o600, f"{rel} restored with mode {oct(mode)}, expected 0o600"


# ---------------------------------------------------------------------------
# Round-trip test
# ---------------------------------------------------------------------------

class TestRoundTrip:
    def test_backup_then_import(self, tmp_path, monkeypatch):
        """Full round-trip: backup -> import to a new location -> verify."""
        # Source
        src_home = tmp_path / "source" / ".hermes"
        src_home.mkdir(parents=True)
        _make_hermes_tree(src_home)

        monkeypatch.setenv("HERMES_HOME", str(src_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path / "source")

        # Backup
        out_zip = tmp_path / "roundtrip.zip"
        from hermes_cli.backup import run_backup, run_import

        run_backup(Namespace(output=str(out_zip)))
        assert out_zip.exists()

        # Import into a different location
        dst_home = tmp_path / "dest" / ".hermes"
        dst_home.mkdir(parents=True)
        monkeypatch.setenv("HERMES_HOME", str(dst_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path / "dest")

        run_import(Namespace(zipfile=str(out_zip), force=True))

        # Verify key files
        assert (dst_home / "config.yaml").read_text() == "model:\n  provider: openrouter\n"
        assert (dst_home / ".env").read_text() == "OPENROUTER_API_KEY=sk-test-123\n"
        assert (dst_home / "skills" / "my-skill" / "SKILL.md").exists()
        assert (dst_home / "profiles" / "coder" / "config.yaml").exists()
        assert (dst_home / "sessions" / "abc123.json").exists()
        assert (dst_home / "logs" / "agent.log").exists()

        # hermes-agent should NOT be present
        assert not (dst_home / "hermes-agent").exists()
        # __pycache__ should NOT be present
        assert not (dst_home / "plugins" / "__pycache__").exists()
        # PID files should NOT be present
        assert not (dst_home / "gateway.pid").exists()


# ---------------------------------------------------------------------------
# Validate / detect-prefix unit tests
# ---------------------------------------------------------------------------

class TestFormatSize:
    def test_bytes(self):
        from hermes_cli.backup import _format_size
        assert _format_size(512) == "512 B"

    def test_kilobytes(self):
        from hermes_cli.backup import _format_size
        assert "KB" in _format_size(2048)

    def test_megabytes(self):
        from hermes_cli.backup import _format_size
        assert "MB" in _format_size(5 * 1024 * 1024)

    def test_gigabytes(self):
        from hermes_cli.backup import _format_size
        assert "GB" in _format_size(3 * 1024 ** 3)

    def test_terabytes(self):
        from hermes_cli.backup import _format_size
        assert "TB" in _format_size(2 * 1024 ** 4)


class TestValidation:
    def test_validate_with_config(self):
        """Zip with config.yaml passes validation."""
        import io
        from hermes_cli.backup import _validate_backup_zip

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("config.yaml", "test")
        buf.seek(0)
        with zipfile.ZipFile(buf, "r") as zf:
            ok, reason = _validate_backup_zip(zf)
        assert ok

    def test_validate_with_env(self):
        """Zip with .env passes validation."""
        import io
        from hermes_cli.backup import _validate_backup_zip

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr(".env", "KEY=val")
        buf.seek(0)
        with zipfile.ZipFile(buf, "r") as zf:
            ok, reason = _validate_backup_zip(zf)
        assert ok

    def test_validate_rejects_random(self):
        """Zip without hermes markers fails validation."""
        import io
        from hermes_cli.backup import _validate_backup_zip

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("random/file.txt", "hello")
        buf.seek(0)
        with zipfile.ZipFile(buf, "r") as zf:
            ok, reason = _validate_backup_zip(zf)
        assert not ok

    def test_detect_prefix_hermes(self):
        """Detects .hermes/ prefix wrapping all entries."""
        import io
        from hermes_cli.backup import _detect_prefix

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr(".hermes/config.yaml", "test")
            zf.writestr(".hermes/skills/a/SKILL.md", "skill")
        buf.seek(0)
        with zipfile.ZipFile(buf, "r") as zf:
            assert _detect_prefix(zf) == ".hermes/"

    def test_detect_prefix_none(self):
        """No prefix when entries are at root."""
        import io
        from hermes_cli.backup import _detect_prefix

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("config.yaml", "test")
            zf.writestr("skills/a/SKILL.md", "skill")
        buf.seek(0)
        with zipfile.ZipFile(buf, "r") as zf:
            assert _detect_prefix(zf) == ""

    def test_detect_prefix_only_dirs(self):
        """Prefix detection returns empty for zip with only directory entries."""
        import io
        from hermes_cli.backup import _detect_prefix

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            # Only directory entries (trailing slash)
            zf.writestr(".hermes/", "")
            zf.writestr(".hermes/skills/", "")
        buf.seek(0)
        with zipfile.ZipFile(buf, "r") as zf:
            assert _detect_prefix(zf) == ""


# ---------------------------------------------------------------------------
# Edge case tests for uncovered paths
# ---------------------------------------------------------------------------

class TestBackupEdgeCases:
    def test_nonexistent_hermes_home(self, tmp_path, monkeypatch):
        """Backup exits when hermes home doesn't exist."""
        fake_home = tmp_path / "nonexistent" / ".hermes"
        monkeypatch.setenv("HERMES_HOME", str(fake_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path / "nonexistent")

        args = Namespace(output=str(tmp_path / "out.zip"))

        from hermes_cli.backup import run_backup
        with pytest.raises(SystemExit):
            run_backup(args)

    def test_output_is_directory(self, tmp_path, monkeypatch):
        """When output path is a directory, zip is created inside it."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        (hermes_home / "config.yaml").write_text("model: test\n")

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        out_dir = tmp_path / "backups"
        out_dir.mkdir()

        args = Namespace(output=str(out_dir))

        from hermes_cli.backup import run_backup
        run_backup(args)

        zips = list(out_dir.glob("hermes-backup-*.zip"))
        assert len(zips) == 1

    def test_output_without_zip_suffix(self, tmp_path, monkeypatch):
        """Output path without .zip gets suffix appended."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        (hermes_home / "config.yaml").write_text("model: test\n")

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        out_path = tmp_path / "mybackup.tar"
        args = Namespace(output=str(out_path))

        from hermes_cli.backup import run_backup
        run_backup(args)

        # Should have .tar.zip suffix
        assert (tmp_path / "mybackup.tar.zip").exists()

    def test_empty_hermes_home(self, tmp_path, monkeypatch):
        """Backup handles empty hermes home (no files to back up)."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        # Only excluded dirs, no actual files
        (hermes_home / "__pycache__").mkdir()
        (hermes_home / "__pycache__" / "foo.pyc").write_bytes(b"\x00")

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        args = Namespace(output=str(tmp_path / "out.zip"))

        from hermes_cli.backup import run_backup
        run_backup(args)

        # No zip should be created
        assert not (tmp_path / "out.zip").exists()

    def test_permission_error_during_backup(self, tmp_path, monkeypatch):
        """Backup handles permission errors gracefully."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        (hermes_home / "config.yaml").write_text("model: test\n")

        # Create an unreadable file
        bad_file = hermes_home / "secret.db"
        bad_file.write_text("data")
        bad_file.chmod(0o000)

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        out_zip = tmp_path / "out.zip"
        args = Namespace(output=str(out_zip))

        from hermes_cli.backup import run_backup
        try:
            run_backup(args)
        finally:
            # Restore permissions for cleanup
            bad_file.chmod(0o644)

        # Zip should still be created with the readable files
        assert out_zip.exists()

    def test_pre1980_timestamp_skipped(self, tmp_path, monkeypatch):
        """Backup skips files with pre-1980 timestamps (ZIP limitation)."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        (hermes_home / "config.yaml").write_text("model: test\n")

        # Create a file with epoch timestamp (1970-01-01)
        old_file = hermes_home / "ancient.txt"
        old_file.write_text("old data")
        os.utime(old_file, (0, 0))

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        out_zip = tmp_path / "out.zip"
        args = Namespace(output=str(out_zip))

        from hermes_cli.backup import run_backup
        run_backup(args)

        # Zip should still be created with the valid files
        assert out_zip.exists()
        with zipfile.ZipFile(out_zip, "r") as zf:
            names = zf.namelist()
            assert "config.yaml" in names
            # The pre-1980 file should be skipped, not crash the backup
            assert "ancient.txt" not in names

    def test_skips_output_zip_inside_hermes(self, tmp_path, monkeypatch):
        """Backup skips its own output zip if it's inside hermes root."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        (hermes_home / "config.yaml").write_text("model: test\n")

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        # Output inside hermes home
        out_zip = hermes_home / "backup.zip"
        args = Namespace(output=str(out_zip))

        from hermes_cli.backup import run_backup
        run_backup(args)

        # The zip should exist but not contain itself
        assert out_zip.exists()
        with zipfile.ZipFile(out_zip, "r") as zf:
            assert "backup.zip" not in zf.namelist()


class TestImportEdgeCases:
    def _make_backup_zip(self, zip_path: Path, files: dict[str, str | bytes]) -> None:
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)

    def test_not_a_zip(self, tmp_path, monkeypatch):
        """Import rejects a non-zip file."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))

        not_zip = tmp_path / "fake.zip"
        not_zip.write_text("this is not a zip")

        args = Namespace(zipfile=str(not_zip), force=True)

        from hermes_cli.backup import run_import
        with pytest.raises(SystemExit):
            run_import(args)

    def test_eof_during_confirmation(self, tmp_path, monkeypatch):
        """Import handles EOFError during confirmation prompt."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        (hermes_home / "config.yaml").write_text("existing\n")
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        zip_path = tmp_path / "backup.zip"
        self._make_backup_zip(zip_path, {"config.yaml": "new\n"})

        args = Namespace(zipfile=str(zip_path), force=False)

        from hermes_cli.backup import run_import
        with patch("builtins.input", side_effect=EOFError):
            with pytest.raises(SystemExit):
                run_import(args)

    def test_keyboard_interrupt_during_confirmation(self, tmp_path, monkeypatch):
        """Import handles KeyboardInterrupt during confirmation prompt."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        (hermes_home / ".env").write_text("KEY=val\n")
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        zip_path = tmp_path / "backup.zip"
        self._make_backup_zip(zip_path, {"config.yaml": "new\n"})

        args = Namespace(zipfile=str(zip_path), force=False)

        from hermes_cli.backup import run_import
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            with pytest.raises(SystemExit):
                run_import(args)

    def test_permission_error_during_import(self, tmp_path, monkeypatch):
        """Import handles permission errors during extraction."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        # Create a read-only directory so extraction fails
        locked_dir = hermes_home / "locked"
        locked_dir.mkdir()
        locked_dir.chmod(0o555)

        zip_path = tmp_path / "backup.zip"
        self._make_backup_zip(zip_path, {
            "config.yaml": "model: test\n",
            "locked/secret.txt": "data",
        })

        args = Namespace(zipfile=str(zip_path), force=True)

        from hermes_cli.backup import run_import
        try:
            run_import(args)
        finally:
            locked_dir.chmod(0o755)

        # config.yaml should still be restored despite the error
        assert (hermes_home / "config.yaml").exists()

    def test_progress_with_many_files(self, tmp_path, monkeypatch):
        """Import shows progress with 500+ files."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        zip_path = tmp_path / "big.zip"
        files = {"config.yaml": "model: test\n"}
        for i in range(600):
            files[f"sessions/s{i:04d}.json"] = "{}"

        self._make_backup_zip(zip_path, files)

        args = Namespace(zipfile=str(zip_path), force=True)

        from hermes_cli.backup import run_import
        run_import(args)

        assert (hermes_home / "config.yaml").exists()
        assert (hermes_home / "sessions" / "s0599.json").exists()


class _ExplodingMember:
    """Zip member whose stream dies mid-restore (ENOSPC / corrupt member).

    Both the pre-fix ``dst.write(src.read())`` and the atomic
    ``shutil.copyfileobj`` path pull bytes through ``read()``, so injecting
    here exercises whichever implementation is in the tree.
    """

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False

    def read(self, *args):
        raise OSError(28, "No space left on device")

    def close(self):
        pass


def _break_member(monkeypatch, failing_member: str) -> None:
    """Make ``ZipFile.open`` hand back a dying stream for one member only."""
    real_open = zipfile.ZipFile.open

    def _patched(self, name, *args, **kwargs):
        filename = name.filename if isinstance(name, zipfile.ZipInfo) else name
        if filename == failing_member:
            return _ExplodingMember()
        return real_open(self, name, *args, **kwargs)

    monkeypatch.setattr(zipfile.ZipFile, "open", _patched)


class TestImportAtomicWrites:
    """`hermes import` must never leave a user's file truncated.

    The pre-fix code did ``open(target, "wb")`` then ``dst.write(src.read())``,
    which zeroes the existing file *before* any replacement bytes exist. These
    tests pin the invariant for both restore branches: the HERMES_HOME branch
    and the ``_external/`` branch that writes into third-party configs under
    the user's home.
    """

    def _zip(self, zip_path: Path, files: dict) -> None:
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)

    def test_failed_member_leaves_existing_file_intact(self, tmp_path, monkeypatch):
        """A dying member must not destroy the file it was replacing."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        original = "model: original\napi_key: keep-me\n"
        (hermes_home / "config.yaml").write_text(original)
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        zip_path = tmp_path / "backup.zip"
        self._zip(zip_path, {"config.yaml": "model: replacement\n", "state.db": ""})
        _break_member(monkeypatch, "config.yaml")

        from hermes_cli.backup import run_import
        run_import(Namespace(zipfile=str(zip_path), force=True))

        # Pre-fix this file is 0 bytes: the truncate landed, the write did not.
        assert (hermes_home / "config.yaml").read_text() == original
        # And the aborted write must not litter the directory it staged in.
        assert list(hermes_home.glob(".config.yaml.*")) == []

    def test_failed_external_member_leaves_existing_file_intact(self, tmp_path, monkeypatch):
        """Same invariant on the `_external/` branch, which writes outside HERMES_HOME."""
        dst_home = tmp_path / "dst"
        dst_home.mkdir()
        hermes_home = dst_home / ".hermes"
        hermes_home.mkdir()
        honcho = dst_home / ".honcho"
        honcho.mkdir()
        original = '{"peer":"original"}'
        (honcho / "config.json").write_text(original)

        zip_path = tmp_path / "backup.zip"
        self._zip(zip_path, {
            "config.yaml": "model: {}\n",
            "_external/.honcho/config.json": '{"peer":"replacement"}',
        })

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: dst_home)
        _break_member(monkeypatch, "_external/.honcho/config.json")

        from hermes_cli.backup import run_import
        run_import(Namespace(zipfile=str(zip_path), force=True))

        assert (honcho / "config.json").read_text() == original
        assert list(honcho.glob(".config.json.*")) == []

    @pytest.mark.skipif(os.name != "posix", reason="POSIX symlinks")
    def test_symlinked_target_keeps_its_symlink(self, tmp_path, monkeypatch):
        """A symlinked target is written through, not replaced by a regular file.

        Guards the atomic rewrite against a naive ``os.replace``, which would
        detach dotfiles-managed deployments (GitHub #16743). ``atomic_replace``
        resolves the link first.
        """
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        store = hermes_home / "store"
        store.mkdir()
        real = store / "config.yaml"
        real.write_text("model: original\n")
        link = hermes_home / "config.yaml"
        link.symlink_to(real)

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        zip_path = tmp_path / "backup.zip"
        self._zip(zip_path, {"config.yaml": "model: restored\n", "state.db": ""})

        from hermes_cli.backup import run_import
        run_import(Namespace(zipfile=str(zip_path), force=True))

        assert link.is_symlink(), "import replaced the symlink with a regular file"
        assert real.read_text() == "model: restored\n"

    @pytest.mark.skipif(os.name != "posix", reason="POSIX symlinks")
    def test_symlinked_external_target_keeps_its_symlink(self, tmp_path, monkeypatch):
        """Same guard on the `_external/` branch — the realistic dotfiles case."""
        dst_home = tmp_path / "dst"
        dst_home.mkdir()
        hermes_home = dst_home / ".hermes"
        hermes_home.mkdir()
        dotfiles = dst_home / "dotfiles"
        dotfiles.mkdir()
        real = dotfiles / "honcho.json"
        real.write_text('{"peer":"original"}')
        honcho = dst_home / ".honcho"
        honcho.mkdir()
        link = honcho / "config.json"
        link.symlink_to(real)

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: dst_home)

        zip_path = tmp_path / "backup.zip"
        self._zip(zip_path, {
            "config.yaml": "model: {}\n",
            "_external/.honcho/config.json": '{"peer":"restored"}',
        })

        from hermes_cli.backup import run_import
        run_import(Namespace(zipfile=str(zip_path), force=True))

        assert link.is_symlink(), "import replaced the symlink with a regular file"
        assert real.read_text() == '{"peer":"restored"}'

    @pytest.mark.skipif(os.name != "posix", reason="POSIX file modes")
    def test_restore_preserves_existing_file_mode(self, tmp_path, monkeypatch):
        """Staging through mkstemp must not silently tighten restored files to 0600.

        ``tempfile.mkstemp`` creates at 0600; the mode of the file being
        replaced has to survive the publish, or Docker/NAS installs that rely
        on broader permissions break on restore.
        """
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        target = hermes_home / "config.yaml"
        target.write_text("model: original\n")
        os.chmod(target, 0o644)
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        zip_path = tmp_path / "backup.zip"
        self._zip(zip_path, {"config.yaml": "model: restored\n", "state.db": ""})

        from hermes_cli.backup import run_import
        run_import(Namespace(zipfile=str(zip_path), force=True))

        assert target.read_text() == "model: restored\n"
        assert (target.stat().st_mode & 0o777) == 0o644

    @pytest.mark.skipif(os.name != "posix", reason="POSIX ownership")
    def test_restore_preserves_existing_file_owner(self, tmp_path, monkeypatch):
        """A root-run import must not re-own the user's files to root.

        ``os.replace`` swaps in a temp file owned by the *writing* user, so a
        ``sudo hermes import`` onto a user-owned (or Docker/NAS volume-owned)
        HERMES_HOME would hand every restored file to root. The uid/gid is
        forced so the assertion does not require running as root.
        """
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        target = hermes_home / "config.yaml"
        target.write_text("model: original\n")
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        zip_path = tmp_path / "backup.zip"
        self._zip(zip_path, {"config.yaml": "model: restored\n", "state.db": ""})

        chown_calls: list[tuple[Path, int, int]] = []
        monkeypatch.setattr(
            "hermes_cli.backup._preserve_file_owner",
            lambda p: (123, 456) if Path(p).exists() else None,
        )
        monkeypatch.setattr(
            "utils.os.chown",
            lambda path, uid, gid: chown_calls.append((Path(path), uid, gid)),
        )

        from hermes_cli.backup import run_import
        run_import(Namespace(zipfile=str(zip_path), force=True))

        assert target.read_text() == "model: restored\n"
        # config.yaml pre-existed, so its owner is captured and re-applied;
        # state.db is newly created, so there is no prior owner to restore.
        assert chown_calls == [(target, 123, 456)]

    @pytest.mark.skipif(not hasattr(os, "fchmod"), reason="needs fchmod present to remove it")
    def test_mode_is_applied_before_the_replace_without_fchmod(self, tmp_path, monkeypatch):
        """Covers the Windows branch: no ``fchmod``, so ``chmod`` the temp path.

        Applying the mode only *after* ``atomic_replace`` leaves the published
        file at mkstemp's 0600 until that chmod lands (and permanently if the
        process dies in between), and ``atomic_replace``'s EXDEV/EBUSY
        ``shutil.copystat`` fallback would copy 0600 onto the target. Mirrors
        the transit-window fix ``atomic_yaml_write`` already carries.
        """
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        target = hermes_home / "config.yaml"
        target.write_text("model: original\n")
        os.chmod(target, 0o644)
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        zip_path = tmp_path / "backup.zip"
        self._zip(zip_path, {"config.yaml": "model: restored\n", "state.db": ""})

        import hermes_cli.backup as backup_mod

        real_replace = backup_mod.atomic_replace
        staged_modes: list[int] = []

        def spying_replace(tmp, dst):
            if Path(dst).name == "config.yaml":
                staged_modes.append(os.stat(tmp).st_mode & 0o777)
            return real_replace(tmp, dst)

        monkeypatch.delattr(os, "fchmod")
        monkeypatch.setattr(backup_mod, "atomic_replace", spying_replace)

        from hermes_cli.backup import run_import
        run_import(Namespace(zipfile=str(zip_path), force=True))

        # Without the pre-replace chmod this reads 0o600 (mkstemp's mode).
        assert staged_modes == [0o644]
        assert (target.stat().st_mode & 0o777) == 0o644

    @pytest.mark.skipif(os.name != "posix", reason="POSIX setuid/setgid bits")
    def test_restore_does_not_carry_setuid_onto_archive_content(
        self, tmp_path, monkeypatch
    ):
        """An imported member must not inherit a privileged target's identity.

        ``_preserve_file_mode`` returns ``stat.S_IMODE``, i.e. all twelve bits,
        so a target sitting at 0o6755 hands setuid/setgid straight back to a
        file whose contents now come from the zip.  Whoever produced the
        archive would then get whatever that file executes as.  The other
        ``utils`` writers can preserve the full mode safely because they
        re-serialize content this process produced; ``hermes import`` is the
        one write path where the bytes are untrusted, and it is also the path
        that documents ``sudo`` use for owner preservation.

        The sibling assertions in this class mask with ``& 0o777``, which
        discards exactly the bits at issue, so this failure is invisible to
        them.
        """
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        target = hermes_home / "helper.sh"
        target.write_text("#!/bin/sh\necho original\n")
        os.chmod(target, 0o6755)
        if stat.S_IMODE(target.stat().st_mode) != 0o6755:
            pytest.skip("filesystem refuses setuid/setgid on a user-owned file")
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        zip_path = tmp_path / "backup.zip"
        self._zip(
            zip_path,
            {"helper.sh": "#!/bin/sh\necho attacker\n", "state.db": ""},
        )

        import hermes_cli.backup as backup_mod

        real_replace = backup_mod.atomic_replace
        staged_modes: list[int] = []

        def spying_replace(tmp, dst):
            if Path(dst).name == "helper.sh":
                staged_modes.append(stat.S_IMODE(os.stat(tmp).st_mode))
            return real_replace(tmp, dst)

        monkeypatch.setattr(backup_mod, "atomic_replace", spying_replace)

        from hermes_cli.backup import run_import
        run_import(Namespace(zipfile=str(zip_path), force=True))

        published = stat.S_IMODE(target.stat().st_mode)
        assert target.read_text() == "#!/bin/sh\necho attacker\n"
        assert not published & stat.S_ISUID, (
            f"archive content kept the target's setuid bit (mode 0o{published:o})"
        )
        assert not published & stat.S_ISGID, (
            f"archive content kept the target's setgid bit (mode 0o{published:o})"
        )
        # The ordinary permission bits are still preserved — this drops the
        # elevated bits, it does not fall back to mkstemp's 0600.
        assert published == 0o755
        # And there must be no transient elevation either: the temp file is
        # chmod'd before the replace, so it must never carry the bits.
        assert staged_modes == [0o755], (
            f"the staged temp file was elevated before publish: {staged_modes}"
        )


# ---------------------------------------------------------------------------
# Profile restoration tests
# ---------------------------------------------------------------------------

class TestProfileRestoration:
    def _make_backup_zip(self, zip_path: Path, files: dict[str, str | bytes]) -> None:
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)

    def test_import_creates_profile_wrappers(self, tmp_path, monkeypatch):
        """Import auto-creates wrapper scripts for restored profiles."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        # Mock the wrapper dir to be inside tmp_path
        wrapper_dir = tmp_path / ".local" / "bin"
        wrapper_dir.mkdir(parents=True)

        zip_path = tmp_path / "backup.zip"
        self._make_backup_zip(zip_path, {
            "config.yaml": "model:\n  provider: openrouter\n",
            "profiles/coder/config.yaml": "model:\n  provider: anthropic\n",
            "profiles/coder/.env": "ANTHROPIC_API_KEY=sk-test\n",
            "profiles/researcher/config.yaml": "model:\n  provider: deepseek\n",
        })

        args = Namespace(zipfile=str(zip_path), force=True)

        from hermes_cli.backup import run_import
        run_import(args)

        # Profile directories should exist
        assert (hermes_home / "profiles" / "coder" / "config.yaml").exists()
        assert (hermes_home / "profiles" / "researcher" / "config.yaml").exists()

        # Wrapper scripts should be created
        assert (wrapper_dir / "coder").exists()
        assert (wrapper_dir / "researcher").exists()

        # Wrappers should contain the right content
        coder_wrapper = (wrapper_dir / "coder").read_text()
        assert "hermes -p coder" in coder_wrapper

    def test_import_skips_profile_dirs_without_config(self, tmp_path, monkeypatch):
        """Import doesn't create wrappers for profile dirs without config."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        wrapper_dir = tmp_path / ".local" / "bin"
        wrapper_dir.mkdir(parents=True)

        zip_path = tmp_path / "backup.zip"
        self._make_backup_zip(zip_path, {
            "config.yaml": "model: test\n",
            "profiles/valid/config.yaml": "model: test\n",
            "profiles/empty/readme.txt": "nothing here\n",
        })

        args = Namespace(zipfile=str(zip_path), force=True)

        from hermes_cli.backup import run_import
        run_import(args)

        # Only valid profile should get a wrapper
        assert (wrapper_dir / "valid").exists()
        assert not (wrapper_dir / "empty").exists()

    def test_import_without_profiles_module(self, tmp_path, monkeypatch):
        """Import gracefully handles missing profiles module (fresh install)."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        zip_path = tmp_path / "backup.zip"
        self._make_backup_zip(zip_path, {
            "config.yaml": "model: test\n",
            "profiles/coder/config.yaml": "model: test\n",
        })

        args = Namespace(zipfile=str(zip_path), force=True)

        # Simulate profiles module not being available
        original_import = __builtins__.__import__ if hasattr(__builtins__, '__import__') else __import__

        def fake_import(name, *a, **kw):
            if name == "hermes_cli.profiles":
                raise ImportError("no profiles module")
            return original_import(name, *a, **kw)

        from hermes_cli.backup import run_import
        with patch("builtins.__import__", side_effect=fake_import):
            run_import(args)

        # Files should still be restored even if wrappers can't be created
        assert (hermes_home / "profiles" / "coder" / "config.yaml").exists()


# ---------------------------------------------------------------------------
# SQLite safe copy tests
# ---------------------------------------------------------------------------

class TestSafeCopyDb:
    def test_copies_valid_database(self, tmp_path):
        from hermes_cli.backup import _safe_copy_db
        src = tmp_path / "test.db"
        dst = tmp_path / "copy.db"

        conn = sqlite3.connect(str(src))
        conn.execute("CREATE TABLE t (x INTEGER)")
        conn.execute("INSERT INTO t VALUES (42)")
        conn.commit()
        conn.close()

        result = _safe_copy_db(src, dst)
        assert result is True

        conn = sqlite3.connect(str(dst))
        rows = conn.execute("SELECT x FROM t").fetchall()
        conn.close()
        assert rows == [(42,)]

    def test_copies_wal_mode_database(self, tmp_path):
        from hermes_cli.backup import _safe_copy_db
        src = tmp_path / "wal.db"
        dst = tmp_path / "copy.db"

        conn = sqlite3.connect(str(src))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("CREATE TABLE t (x TEXT)")
        conn.execute("INSERT INTO t VALUES ('wal-test')")
        conn.commit()
        conn.close()

        result = _safe_copy_db(src, dst)
        assert result is True

        conn = sqlite3.connect(str(dst))
        rows = conn.execute("SELECT x FROM t").fetchall()
        conn.close()
        assert rows == [("wal-test",)]

    def test_aborts_when_source_remains_busy_past_deadline(
        self, tmp_path, monkeypatch
    ):
        from hermes_cli import backup as backup_mod

        src = tmp_path / "locked.db"
        dst = tmp_path / "copy.db"
        src.touch()
        dst.write_bytes(b"partial")

        clock = iter((100.0, 100.5, 101.1))

        class FakeSourceConnection:
            def backup(self, _destination, *, pages, progress, sleep):
                assert pages > 0
                assert sleep > 0
                progress(sqlite3.SQLITE_BUSY, 0, 1)
                progress(sqlite3.SQLITE_BUSY, 0, 1)

            def close(self):
                pass

        destination_closed = []

        class FakeDestinationConnection:
            def close(self):
                destination_closed.append(True)

        connections = iter((FakeSourceConnection(), FakeDestinationConnection()))
        real_unlink = Path.unlink

        def assert_closed_before_unlink(path, *args, **kwargs):
            assert destination_closed
            return real_unlink(path, *args, **kwargs)

        connect_calls = []

        def fake_connect(*args, **kwargs):
            connect_calls.append((args, kwargs))
            return next(connections)

        monkeypatch.setattr(backup_mod.sqlite3, "connect", fake_connect)
        monkeypatch.setattr(backup_mod.time, "monotonic", lambda: next(clock))
        monkeypatch.setattr(Path, "unlink", assert_closed_before_unlink)

        assert backup_mod._safe_copy_db(src, dst, timeout_seconds=1.0) is False
        assert connect_calls[0][1]["timeout"] == 0.0
        assert not dst.exists()


    def test_locked_source_fails_fast_not_hang(self, tmp_path):
        import subprocess
        import sys
        import time

        from hermes_cli.backup import _safe_copy_db
        src = tmp_path / "locked.db"
        dst = tmp_path / "copy.db"

        conn = sqlite3.connect(str(src))
        conn.execute("CREATE TABLE t (x INTEGER)")
        conn.commit()
        conn.close()

        # Hold an EXCLUSIVE transaction in a separate process. POSIX file
        # locks only conflict across processes, so an in-process connection
        # cannot reproduce the "database is locked" condition.
        holder = (
            "import sqlite3, time\n"
            f"c = sqlite3.connect({str(src)!r})\n"
            "c.execute('BEGIN EXCLUSIVE')\n"
            "print('LOCKED', flush=True)\n"
            "time.sleep(60)\n"
        )
        proc = subprocess.Popen(
            [sys.executable, "-c", holder],
            stdout=subprocess.PIPE,
            text=True,
        )
        try:
            assert proc.stdout is not None
            assert proc.stdout.readline().strip() == "LOCKED"
            started = time.monotonic()
            result = _safe_copy_db(src, dst)
            elapsed = time.monotonic() - started
            assert result is False
            # The busy timeout is 5s, so a fast failure lands around there.
            # The regression this guards against is backup() retrying
            # SQLITE_BUSY forever, which would never return at all.
            assert elapsed < 30
        finally:
            proc.kill()
            proc.wait()


    def test_is_zeroed_sqlite_file_detects_nul_header(self, tmp_path):
        from hermes_cli.backup import is_zeroed_sqlite_file
        p = tmp_path / "state.db"
        p.write_bytes(bytes(4096))  # all NULs
        assert is_zeroed_sqlite_file(p) is True

    def test_is_zeroed_sqlite_file_rejects_valid_db(self, tmp_path):
        from hermes_cli.backup import is_zeroed_sqlite_file
        p = tmp_path / "ok.db"
        conn = sqlite3.connect(str(p))
        conn.execute("CREATE TABLE t (x INT)")
        conn.commit()
        conn.close()
        assert is_zeroed_sqlite_file(p) is False

    def test_is_zeroed_sqlite_file_empty_file(self, tmp_path):
        from hermes_cli.backup import is_zeroed_sqlite_file
        p = tmp_path / "empty.db"
        p.write_bytes(b"")
        # Empty state.db is the total-loss form of the zeroed-file signature.
        assert is_zeroed_sqlite_file(p) is True


# ---------------------------------------------------------------------------
# Quick state snapshot tests
# ---------------------------------------------------------------------------

class TestQuickSnapshot:
    @pytest.fixture
    def hermes_home(self, tmp_path):
        """Create a fake HERMES_HOME with critical state files."""
        home = tmp_path / ".hermes"
        home.mkdir()
        (home / "config.yaml").write_text("model:\n  provider: openrouter\n")
        (home / ".env").write_text("OPENROUTER_API_KEY=test-key-123\n")
        (home / "auth.json").write_text('{"providers": {}}\n')
        (home / "channel_aliases.json").write_text(
            '{"whatsapp": {"120363408391911677@g.us": "general"}}\n'
        )
        (home / "cron").mkdir()
        (home / "cron" / "jobs.json").write_text('{"jobs": []}\n')

        # Real SQLite database
        db_path = home / "state.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE sessions (id TEXT PRIMARY KEY, data TEXT)")
        conn.execute("INSERT INTO sessions VALUES ('s1', 'hello world')")
        conn.commit()
        conn.close()
        return home

    def test_creates_snapshot(self, hermes_home):
        from hermes_cli.backup import create_quick_snapshot
        snap_id = create_quick_snapshot(hermes_home=hermes_home)
        assert snap_id is not None
        snap_dir = hermes_home / "state-snapshots" / snap_id
        assert snap_dir.is_dir()
        assert (snap_dir / "manifest.json").exists()

    def test_label_in_id(self, hermes_home):
        from hermes_cli.backup import create_quick_snapshot
        snap_id = create_quick_snapshot(label="before-upgrade", hermes_home=hermes_home)
        assert "before-upgrade" in snap_id

    def test_state_db_safely_copied(self, hermes_home):
        from hermes_cli.backup import create_quick_snapshot
        snap_id = create_quick_snapshot(hermes_home=hermes_home)
        db_copy = hermes_home / "state-snapshots" / snap_id / "state.db"
        assert db_copy.exists()
        conn = sqlite3.connect(str(db_copy))
        rows = conn.execute("SELECT * FROM sessions").fetchall()
        conn.close()
        assert len(rows) == 1
        assert rows[0] == ("s1", "hello world")

    def test_failed_state_db_copy_is_loud(self, hermes_home, monkeypatch, capsys):
        """#68474: unreadable state.db must not look like a silent success."""
        from hermes_cli import backup as backup_mod

        def boom(src, dst):
            return False

        monkeypatch.setattr(backup_mod, "_safe_copy_db", boom)
        snap_id = backup_mod.create_quick_snapshot(hermes_home=hermes_home)
        err = capsys.readouterr().out
        assert "SQLite safe copy FAILED" in err or "CRITICAL" in err
        assert "state.db" in err
        # Other small files may still snapshot
        if snap_id:
            manifest = (hermes_home / "state-snapshots" / snap_id / "manifest.json")
            assert manifest.exists()
            data = json.loads(manifest.read_text(encoding="utf-8"))
            assert "state.db" not in data.get("files", {})
            assert "state.db" in data.get("failed_dbs", [])

    def test_copies_nested_files(self, hermes_home):
        from hermes_cli.backup import create_quick_snapshot
        snap_id = create_quick_snapshot(hermes_home=hermes_home)
        assert (hermes_home / "state-snapshots" / snap_id / "cron" / "jobs.json").exists()

    def test_restore_refused_db_is_not_counted(self, hermes_home, monkeypatch):
        """A refused live-safe restore (holder detected, backup leg failed) must
        not be counted as a restored file — `hermes import` reports it, and
        /snapshot restore must not claim success for that file either."""
        import hermes_cli.backup as backup_mod
        from hermes_cli.backup import create_quick_snapshot, restore_quick_snapshot

        snap_id = create_quick_snapshot(hermes_home=hermes_home)
        monkeypatch.setattr(backup_mod, "_safe_restore_db", lambda src, dst: False)
        restored_log: list[str] = []
        real_info = backup_mod.logger.info
        monkeypatch.setattr(
            backup_mod.logger, "info",
            lambda msg, *a, **kw: restored_log.append(msg % a if a else msg) or real_info(msg, *a, **kw),
        )

        restore_quick_snapshot(snap_id, hermes_home=hermes_home)

        manifest = json.loads(
            (backup_mod._quick_snapshot_root(hermes_home) / snap_id / "manifest.json").read_text()
        )
        non_db = [rel for rel in manifest.get("files", {}) if not rel.endswith(".db")]
        summary = [line for line in restored_log if line.startswith("Restored ")]
        assert summary, restored_log
        assert summary[-1].startswith(f"Restored {len(non_db)} files"), summary[-1]

    def test_restore_state_db_live_connection(self, hermes_home):
        """Restoring state.db must update data visible through a live connection.

        Regression test for #65942: when state.db is open with a live SQLite
        connection (as happens with the gateway, dashboard, or another CLI
        session), the restore must write pages through the backup API so the
        live connection sees the restored data instead of stale cached pages
        from a replaced inode.
        """
        from hermes_cli.backup import create_quick_snapshot, restore_quick_snapshot
        snap_id = create_quick_snapshot(hermes_home=hermes_home)

        # Open a live connection (simulating gateway/dashboard).
        live_conn = sqlite3.connect(str(hermes_home / "state.db"))
        live_conn.execute("PRAGMA journal_mode=wal")
        # Insert data AFTER the snapshot — this is what must be reverted.
        live_conn.execute("INSERT INTO sessions VALUES ('s2', 'new-data')")
        live_conn.commit()

        rows_before = live_conn.execute("SELECT * FROM sessions").fetchall()
        assert len(rows_before) == 2

        # Restore — the live connection stays open during restore.
        result = restore_quick_snapshot(snap_id, hermes_home=hermes_home)
        assert result is True

        # The live connection must see the restored (single-row) state.
        # A fresh connection would trivially work; the live one is the test.
        rows_after = live_conn.execute("SELECT * FROM sessions").fetchall()
        live_conn.close()
        assert len(rows_after) == 1, (
            f"Live connection still sees {len(rows_after)} rows after restore "
            f"(expected 1); the extra row 's2' should have been reverted."
        )

    def test_copies_discord_recovery_ledger(self, hermes_home):
        from hermes_cli.backup import create_quick_snapshot

        gateway_dir = hermes_home / "gateway"
        gateway_dir.mkdir()
        ledger = gateway_dir / "discord_message_recovery.db"
        conn = sqlite3.connect(ledger)
        conn.execute("CREATE TABLE handled (message_id TEXT PRIMARY KEY)")
        conn.execute("INSERT INTO handled VALUES ('123')")
        conn.commit()
        conn.close()

        snap_id = create_quick_snapshot(hermes_home=hermes_home)

        copied = hermes_home / "state-snapshots" / snap_id / "gateway" / ledger.name
        assert copied.exists()
        conn = sqlite3.connect(copied)
        assert conn.execute("SELECT message_id FROM handled").fetchall() == [("123",)]
        conn.close()

    def test_copies_channel_aliases(self, hermes_home):
        from hermes_cli.backup import create_quick_snapshot
        snap_id = create_quick_snapshot(hermes_home=hermes_home)
        copied = hermes_home / "state-snapshots" / snap_id / "channel_aliases.json"
        assert copied.exists()
        assert "120363408391911677@g.us" in copied.read_text()

    def test_missing_files_skipped(self, hermes_home):
        from hermes_cli.backup import create_quick_snapshot
        snap_id = create_quick_snapshot(hermes_home=hermes_home)
        with open(hermes_home / "state-snapshots" / snap_id / "manifest.json") as f:
            meta = json.load(f)
        # gateway_state.json etc. don't exist in fixture
        assert "gateway_state.json" not in meta["files"]

    def test_empty_home_returns_none(self, tmp_path):
        from hermes_cli.backup import create_quick_snapshot
        empty = tmp_path / "empty"
        empty.mkdir()
        assert create_quick_snapshot(hermes_home=empty) is None

    def test_max_file_size_skips_oversized_file(self, hermes_home, capsys):
        """Files above the cap are skipped with a warning; small files
        (the pairing/cron data the snapshot exists for) still land."""
        from hermes_cli.backup import create_quick_snapshot
        # state.db in the fixture is a few KB — cap below it
        cap = 1024
        snap_id = create_quick_snapshot(
            hermes_home=hermes_home, max_file_size=cap
        )
        assert snap_id is not None
        snap_dir = hermes_home / "state-snapshots" / snap_id
        assert not (snap_dir / "state.db").exists()
        # Small files still captured
        assert (snap_dir / "cron" / "jobs.json").exists()
        with open(snap_dir / "manifest.json") as f:
            meta = json.load(f)
        assert "state.db" not in meta["files"]
        out = capsys.readouterr().out
        assert "skipping state.db" in out
        assert "exceeds" in out

    def test_max_file_size_none_copies_everything(self, hermes_home):
        """Default (no cap) preserves manual /snapshot behavior."""
        from hermes_cli.backup import create_quick_snapshot
        snap_id = create_quick_snapshot(hermes_home=hermes_home, max_file_size=None)
        assert (hermes_home / "state-snapshots" / snap_id / "state.db").exists()

    def test_max_file_size_under_cap_copies(self, hermes_home):
        from hermes_cli.backup import create_quick_snapshot
        snap_id = create_quick_snapshot(
            hermes_home=hermes_home, max_file_size=1 << 30
        )
        assert (hermes_home / "state-snapshots" / snap_id / "state.db").exists()

    def test_list_snapshots(self, hermes_home):
        from hermes_cli.backup import create_quick_snapshot, list_quick_snapshots
        id1 = create_quick_snapshot(label="first", hermes_home=hermes_home)
        id2 = create_quick_snapshot(label="second", hermes_home=hermes_home)

        snaps = list_quick_snapshots(hermes_home=hermes_home)
        assert len(snaps) == 2
        assert snaps[0]["id"] == id2  # most recent first
        assert snaps[1]["id"] == id1

    def test_list_limit(self, hermes_home):
        from hermes_cli.backup import create_quick_snapshot, list_quick_snapshots
        for i in range(5):
            create_quick_snapshot(label=f"s{i}", hermes_home=hermes_home)
        snaps = list_quick_snapshots(limit=3, hermes_home=hermes_home)
        assert len(snaps) == 3

    def test_restore_config(self, hermes_home):
        from hermes_cli.backup import create_quick_snapshot, restore_quick_snapshot
        snap_id = create_quick_snapshot(hermes_home=hermes_home)

        (hermes_home / "config.yaml").write_text("model:\n  provider: anthropic\n")
        assert "anthropic" in (hermes_home / "config.yaml").read_text()

        result = restore_quick_snapshot(snap_id, hermes_home=hermes_home)
        assert result is True
        assert "openrouter" in (hermes_home / "config.yaml").read_text()

    def test_restore_state_db(self, hermes_home):
        from hermes_cli.backup import create_quick_snapshot, restore_quick_snapshot
        snap_id = create_quick_snapshot(hermes_home=hermes_home)

        conn = sqlite3.connect(str(hermes_home / "state.db"))
        conn.execute("INSERT INTO sessions VALUES ('s2', 'new')")
        conn.commit()
        conn.close()

        restore_quick_snapshot(snap_id, hermes_home=hermes_home)

        conn = sqlite3.connect(str(hermes_home / "state.db"))
        rows = conn.execute("SELECT * FROM sessions").fetchall()
        conn.close()
        assert len(rows) == 1

    def test_restore_nonexistent(self, hermes_home):
        from hermes_cli.backup import restore_quick_snapshot
        assert restore_quick_snapshot("nonexistent", hermes_home=hermes_home) is False

    def test_auto_prune(self, hermes_home):
        from hermes_cli.backup import create_quick_snapshot, list_quick_snapshots, _QUICK_DEFAULT_KEEP
        for i in range(_QUICK_DEFAULT_KEEP + 5):
            create_quick_snapshot(label=f"snap-{i:03d}", hermes_home=hermes_home)
        snaps = list_quick_snapshots(limit=100, hermes_home=hermes_home)
        assert len(snaps) <= _QUICK_DEFAULT_KEEP

    def test_manual_prune(self, hermes_home):
        from hermes_cli.backup import create_quick_snapshot, prune_quick_snapshots, list_quick_snapshots
        for i in range(10):
            create_quick_snapshot(label=f"s{i}", hermes_home=hermes_home)
        deleted = prune_quick_snapshots(keep=3, hermes_home=hermes_home)
        assert deleted == 7
        assert len(list_quick_snapshots(hermes_home=hermes_home)) == 3

    def test_snapshot_includes_pairing_directories(self, hermes_home):
        """Pairing JSONs live outside state.db — snapshot must capture them
        recursively (generic + per-platform) so approved-user lists survive
        disasters like #15733."""
        from hermes_cli.backup import create_quick_snapshot

        # Generic pairing store (new location)
        (hermes_home / "platforms" / "pairing").mkdir(parents=True)
        (hermes_home / "platforms" / "pairing" / "telegram-approved.json").write_text(
            '{"12345": {"user_name": "alice"}}'
        )
        (hermes_home / "platforms" / "pairing" / "discord-approved.json").write_text(
            '{"67890": {"user_name": "bob"}}'
        )
        # Legacy pairing store (old location)
        (hermes_home / "pairing").mkdir()
        (hermes_home / "pairing" / "matrix-approved.json").write_text(
            '{"@charlie:server": {"user_name": "charlie"}}'
        )
        # Feishu's separate JSON
        (hermes_home / "feishu_comment_pairing.json").write_text(
            '{"doc_abc": {"allow_from": ["user_xyz"]}}'
        )

        snap_id = create_quick_snapshot(hermes_home=hermes_home)
        assert snap_id is not None

        snap_dir = hermes_home / "state-snapshots" / snap_id
        assert (snap_dir / "platforms" / "pairing" / "telegram-approved.json").exists()
        assert (snap_dir / "platforms" / "pairing" / "discord-approved.json").exists()
        assert (snap_dir / "pairing" / "matrix-approved.json").exists()
        assert (snap_dir / "feishu_comment_pairing.json").exists()

        with open(snap_dir / "manifest.json") as f:
            meta = json.load(f)
        files = meta["files"]
        assert "platforms/pairing/telegram-approved.json" in files
        assert "platforms/pairing/discord-approved.json" in files
        assert "pairing/matrix-approved.json" in files
        assert "feishu_comment_pairing.json" in files

    def test_restore_recovers_pairing_data(self, hermes_home):
        """After restore, deleted pairing files reappear with original content."""
        from hermes_cli.backup import create_quick_snapshot, restore_quick_snapshot

        pairing_dir = hermes_home / "platforms" / "pairing"
        pairing_dir.mkdir(parents=True)
        approved = pairing_dir / "telegram-approved.json"
        approved.write_text('{"12345": {"user_name": "alice"}}')
        feishu = hermes_home / "feishu_comment_pairing.json"
        feishu.write_text('{"doc_abc": {"allow_from": ["user_xyz"]}}')

        snap_id = create_quick_snapshot(hermes_home=hermes_home)
        assert snap_id is not None

        # Simulate the disaster — user loses both pairing files.
        approved.unlink()
        feishu.unlink()
        assert not approved.exists()
        assert not feishu.exists()

        assert restore_quick_snapshot(snap_id, hermes_home=hermes_home) is True
        assert approved.exists()
        assert '"alice"' in approved.read_text()
        assert feishu.exists()
        assert '"user_xyz"' in feishu.read_text()

    def test_empty_pairing_dir_does_not_fail(self, hermes_home):
        """An empty pairing directory should be silently skipped."""
        from hermes_cli.backup import create_quick_snapshot

        (hermes_home / "platforms" / "pairing").mkdir(parents=True)
        # Directory exists but contains no files.
        snap_id = create_quick_snapshot(hermes_home=hermes_home)
        # Other state still present → snapshot succeeds.
        assert snap_id is not None

# ---------------------------------------------------------------------------
# Pre-update backup (hermes update safety net)
# ---------------------------------------------------------------------------

    # -- security: path traversal regression coverage -----------------------
    # Per @egilewski audit on PR #9217: restore_quick_snapshot must reject
    # malicious snapshot_id values (the directory selector) AND malicious
    # rel paths inside the manifest (the per-file selector). Both surfaces
    # need explicit regression tests because they validate independent
    # traversal vectors.

    def test_restore_rejects_snapshot_id_traversal(self, hermes_home):
        """restore_quick_snapshot must reject snapshot_id values that
        contain path separators, POSIX traversal entries, or are empty.
        These are rejected on the input string before any filesystem
        lookup, so the guard cannot be bypassed by arranging a directory
        layout that would otherwise satisfy ``snap_dir.is_dir()``.

        Regression for the path-traversal surface where ``root /
        snapshot_id`` could resolve above the snapshots root."""
        from hermes_cli.backup import restore_quick_snapshot

        hostile_ids = [
            "../../etc",                # parent traversal
            "../outside",               # single parent
            "..",                       # bare parent dir
            ".",                        # bare current dir
            "subdir/snap",              # forward slash
            "subdir\\snap",           # backslash (Windows-style)
            "",                         # empty string
        ]
        for hostile in hostile_ids:
            assert restore_quick_snapshot(
                hostile, hermes_home=hermes_home
            ) is False, f"hostile snapshot_id was not rejected: {hostile!r}"

    def test_restore_rejects_manifest_rel_traversal(self, hermes_home):
        """A snapshot whose manifest.json contains a rel path that escapes
        the snapshot directory (e.g. ``../../outside.txt``) must skip that
        entry rather than restoring outside HERMES_HOME."""
        from hermes_cli.backup import create_quick_snapshot, restore_quick_snapshot

        snap_id = create_quick_snapshot(hermes_home=hermes_home)
        assert snap_id is not None
        snap_dir = hermes_home / "state-snapshots" / snap_id

        # Inject a traversal entry into manifest.json AND seed the source
        # file outside the snapshot directory so a vulnerable implementation
        # would actually write something at the escaped destination.
        manifest_path = snap_dir / "manifest.json"
        with open(manifest_path) as f:
            meta = json.load(f)
        meta["files"]["../../outside.txt"] = 9
        with open(manifest_path, "w") as f:
            json.dump(meta, f)

        # Source: ../../outside.txt resolves above the snapshot root.
        # Place a payload there so we can detect a successful escape.
        escape_src = snap_dir.parent.parent / "outside.txt"
        escape_src.write_text("pwned-source")

        # Pre-condition: the destination must not exist before restore.
        escape_dst = hermes_home.parent.parent / "outside.txt"
        assert not escape_dst.exists()

        # Restore should succeed for legitimate files but skip the hostile
        # entry. We don't assert on the return value (other legitimate
        # entries may still restore); we assert on the file-system effect.
        restore_quick_snapshot(snap_id, hermes_home=hermes_home)

        assert not escape_dst.exists(), (
            f"manifest rel traversal escaped HERMES_HOME: {escape_dst} exists"
        )

        # Cleanup the seeded escape source so the test is hermetic.
        escape_src.unlink()

    def test_oversized_db_suppresses_pruning(self, hermes_home, capsys):
        """#68805: an oversized state.db skipped for size must suppress
        pruning so the older complete snapshot (containing the only
        recoverable database) is preserved.

        Reproduces the reviewer's scenario: keep=1 + a state.db exceeding
        the size cap → the new snapshot omits state.db, failed_dbs stays
        empty (the file wasn't unreadable, just too large), and without
        tracking oversized_skipped the older complete snapshot would be
        pruned — losing the only recovery copy.
        """
        import json
        from hermes_cli.backup import create_quick_snapshot, list_quick_snapshots

        # First snapshot: complete (state.db is small, under any cap)
        first_id = create_quick_snapshot(label="complete", hermes_home=hermes_home)
        assert first_id is not None
        first_dir = hermes_home / "state-snapshots" / first_id
        assert (first_dir / "state.db").exists()

        _advance_backup_clock()

        # Second snapshot: state.db exceeds the 1024-byte cap → skipped for
        # size, but small config files (32-54 bytes) still land in the manifest.
        second_id = create_quick_snapshot(
            label="oversized", hermes_home=hermes_home, max_file_size=1024, keep=1
        )
        assert second_id is not None
        second_dir = hermes_home / "state-snapshots" / second_id
        assert not (second_dir / "state.db").exists()

        # Manifest must record the oversized skip
        with open(second_dir / "manifest.json") as f:
            meta = json.load(f)
        assert "state.db" in meta.get("oversized_skipped", [])

        # CRITICAL: the first (complete) snapshot must survive pruning
        # because the second snapshot is incomplete (oversized state.db).
        all_snaps = list_quick_snapshots(limit=100, hermes_home=hermes_home)
        snap_ids = {s["id"] for s in all_snaps}
        assert first_id in snap_ids, (
            f"Complete snapshot {first_id} was pruned by an incomplete "
            f"(oversized) snapshot — the recovery copy was lost!"
        )
        assert second_id in snap_ids

        out = capsys.readouterr().out
        assert "skipping state.db" in out.lower() or "skipping snapshot prune" in out.lower()


class TestQuickSnapshotProjectsKanban:
    """Regression for #52889: projects.db / kanban.db must survive an upgrade.

    Both are per-profile user-created stores outside the git checkout. If they
    are not in the pre-update snapshot, the post-update ``CREATE TABLE IF NOT
    EXISTS`` runs against a missing file and every project / board row is lost.
    """

    @pytest.fixture
    def hermes_home(self, tmp_path):
        home = tmp_path / ".hermes"
        home.mkdir()
        # Minimal critical file so the snapshot is non-empty.
        (home / "config.yaml").write_text("model:\n  provider: openrouter\n")

        for name, table, row in (
            ("projects.db", "projects", ("p1", "demo")),
            ("kanban.db", "tasks", ("t1", "todo")),
        ):
            conn = sqlite3.connect(str(home / name))
            conn.execute(f"CREATE TABLE {table} (id TEXT PRIMARY KEY, data TEXT)")
            conn.execute(f"INSERT INTO {table} VALUES (?, ?)", row)
            conn.commit()
            conn.close()
        return home

    def test_in_quick_state_files(self):
        from hermes_cli.backup import _QUICK_STATE_FILES
        # All per-profile user-created stores that the upgrade can wipe.
        for name in (
            "projects.db", "kanban.db", "kanban/boards",
            "response_store.db", "memory_store.db", "verification_evidence.db",
        ):
            assert name in _QUICK_STATE_FILES, name

    def test_projects_db_snapshotted(self, hermes_home):
        from hermes_cli.backup import create_quick_snapshot
        snap_id = create_quick_snapshot(hermes_home=hermes_home)
        copy = hermes_home / "state-snapshots" / snap_id / "projects.db"
        assert copy.exists()
        conn = sqlite3.connect(str(copy))
        rows = conn.execute("SELECT * FROM projects").fetchall()
        conn.close()
        assert rows == [("p1", "demo")]

    def test_kanban_db_snapshotted(self, hermes_home):
        from hermes_cli.backup import create_quick_snapshot
        snap_id = create_quick_snapshot(hermes_home=hermes_home)
        copy = hermes_home / "state-snapshots" / snap_id / "kanban.db"
        assert copy.exists()
        conn = sqlite3.connect(str(copy))
        rows = conn.execute("SELECT * FROM tasks").fetchall()
        conn.close()
        assert rows == [("t1", "todo")]

    def test_restore_recreates_emptied_projects_db(self, hermes_home):
        from hermes_cli.backup import create_quick_snapshot, restore_quick_snapshot
        snap_id = create_quick_snapshot(hermes_home=hermes_home)

        # Simulate the upgrade wiping the store back to an empty schema.
        conn = sqlite3.connect(str(hermes_home / "projects.db"))
        conn.execute("DELETE FROM projects")
        conn.commit()
        conn.close()

        assert restore_quick_snapshot(snap_id, hermes_home=hermes_home) is True
        conn = sqlite3.connect(str(hermes_home / "projects.db"))
        rows = conn.execute("SELECT * FROM projects").fetchall()
        conn.close()
        assert rows == [("p1", "demo")]

    def test_non_default_kanban_board_snapshotted(self, hermes_home):
        """#52889 completeness: non-default boards live at
        <root>/kanban/boards/<slug>/kanban.db, not <root>/kanban.db. The
        ``kanban/boards`` dir entry must capture them too, or multi-board
        users still lose every board except ``default`` on upgrade."""
        from hermes_cli.backup import create_quick_snapshot, restore_quick_snapshot

        board_dir = hermes_home / "kanban" / "boards" / "work"
        board_dir.mkdir(parents=True)
        conn = sqlite3.connect(str(board_dir / "kanban.db"))
        conn.execute("CREATE TABLE tasks (id TEXT PRIMARY KEY, data TEXT)")
        conn.execute("INSERT INTO tasks VALUES (?, ?)", ("w1", "ship"))
        conn.commit()
        conn.close()

        snap_id = create_quick_snapshot(hermes_home=hermes_home)
        copy = (
            hermes_home / "state-snapshots" / snap_id
            / "kanban" / "boards" / "work" / "kanban.db"
        )
        assert copy.exists(), "non-default board kanban.db was not snapshotted"

        # Simulate the upgrade wiping the board, then restore it.
        conn = sqlite3.connect(str(board_dir / "kanban.db"))
        conn.execute("DELETE FROM tasks")
        conn.commit()
        conn.close()

        assert restore_quick_snapshot(snap_id, hermes_home=hermes_home) is True
        conn = sqlite3.connect(str(board_dir / "kanban.db"))
        rows = conn.execute("SELECT * FROM tasks").fetchall()
        conn.close()
        assert rows == [("w1", "ship")]

    def test_additional_per_profile_dbs_round_trip(self, hermes_home):
        """#52889 completeness: response_store.db (conversation history),
        memory_store.db (holographic memory) and verification_evidence.db are
        the same upgrade-wiped data-loss class as projects.db and must also be
        snapshotted + restored."""
        from hermes_cli.backup import create_quick_snapshot, restore_quick_snapshot

        seeded = {
            "response_store.db": ("responses", ("r1", "hello")),
            "memory_store.db": ("facts", ("f1", "the sky is blue")),
            "verification_evidence.db": ("verification_events", ("v1", "passed")),
        }
        for name, (table, row) in seeded.items():
            conn = sqlite3.connect(str(hermes_home / name))
            conn.execute(f"CREATE TABLE {table} (id TEXT PRIMARY KEY, data TEXT)")
            conn.execute(f"INSERT INTO {table} VALUES (?, ?)", row)
            conn.commit()
            conn.close()

        snap_id = create_quick_snapshot(hermes_home=hermes_home)
        # Wipe every store (the upgrade failure), then restore.
        for name, (table, _row) in seeded.items():
            conn = sqlite3.connect(str(hermes_home / name))
            conn.execute(f"DELETE FROM {table}")
            conn.commit()
            conn.close()

        assert restore_quick_snapshot(snap_id, hermes_home=hermes_home) is True
        for name, (table, row) in seeded.items():
            conn = sqlite3.connect(str(hermes_home / name))
            rows = conn.execute(f"SELECT * FROM {table}").fetchall()
            conn.close()
            assert rows == [row], name

    def test_board_workspaces_and_attachments_are_skipped(self, hermes_home):
        """#52889 W3: the kanban/boards walk must capture board DBs + metadata
        but SKIP the heavy regenerable workspaces/ and attachments/ subtrees so
        snapshots don't bloat (×20 retained)."""
        from hermes_cli.backup import create_quick_snapshot

        board = hermes_home / "kanban" / "boards" / "work"
        (board / "workspaces" / "scratch").mkdir(parents=True)
        (board / "attachments" / "t1").mkdir(parents=True)
        conn = sqlite3.connect(str(board / "kanban.db"))
        conn.execute("CREATE TABLE tasks (id TEXT PRIMARY KEY, data TEXT)")
        conn.commit()
        conn.close()
        (board / "board.json").write_text('{"name": "work"}')
        (board / "workspaces" / "scratch" / "big.bin").write_bytes(b"x" * 4096)
        (board / "attachments" / "t1" / "file.bin").write_bytes(b"y" * 4096)

        snap_id = create_quick_snapshot(hermes_home=hermes_home)
        snap = hermes_home / "state-snapshots" / snap_id / "kanban" / "boards" / "work"
        # Board db + metadata captured...
        assert (snap / "kanban.db").exists()
        assert (snap / "board.json").exists()
        # ...but the heavy subtrees skipped.
        assert not (snap / "workspaces" / "scratch" / "big.bin").exists()
        assert not (snap / "attachments" / "t1" / "file.bin").exists()

    def test_board_db_copied_wal_safely(self, hermes_home, monkeypatch):
        """#52889 W2: a non-default board's .db (dir-branch) must go through the
        WAL-safe _safe_copy_db, not a raw shutil.copy2, so an open WAL doesn't
        produce an inconsistent copy."""
        import hermes_cli.backup as bk
        from hermes_cli.backup import create_quick_snapshot

        board = hermes_home / "kanban" / "boards" / "work"
        board.mkdir(parents=True)
        conn = sqlite3.connect(str(board / "kanban.db"))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("CREATE TABLE tasks (id TEXT PRIMARY KEY, data TEXT)")
        conn.execute("INSERT INTO tasks VALUES ('w1', 'ship')")
        conn.commit()
        conn.close()

        called = {"db": []}
        real = bk._safe_copy_db

        def _spy(src, dst):
            called["db"].append(str(src))
            return real(src, dst)

        monkeypatch.setattr(bk, "_safe_copy_db", _spy)
        snap_id = create_quick_snapshot(hermes_home=hermes_home)
        # The board db was copied via _safe_copy_db (not raw copy).
        assert any(s.endswith("boards/work/kanban.db") for s in called["db"]), called["db"]
        copy = hermes_home / "state-snapshots" / snap_id / "kanban" / "boards" / "work" / "kanban.db"
        rows = sqlite3.connect(str(copy)).execute("SELECT * FROM tasks").fetchall()
        assert rows == [("w1", "ship")]


class TestPreUpdateBackup:
    """Tests for create_pre_update_backup — the auto-backup ``hermes update``
    runs before touching anything."""

    def test_failed_sqlite_snapshot_removes_incomplete_archive(self, tmp_path, monkeypatch):
        """The non-interactive full-zip helper must fail the entire archive
        rather than return success after omitting a live WAL database."""
        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir()
        (hermes_home / "config.yaml").write_text("model: test\n")
        db_path = hermes_home / "state.db"

        writer = sqlite3.connect(db_path)
        writer.execute("PRAGMA journal_mode=WAL")
        writer.execute("PRAGMA wal_autocheckpoint=0")
        writer.execute("CREATE TABLE events (value TEXT)")
        writer.commit()
        writer.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        writer.execute("INSERT INTO events VALUES ('only-in-wal')")
        writer.commit()
        assert Path(f"{db_path}-wal").stat().st_size > 0

        import hermes_cli.backup as backup_mod
        real_connect = backup_mod.sqlite3.connect

        class FailingBackupConnection:
            def __init__(self, connection):
                self._connection = connection

            def backup(self, _destination):
                raise sqlite3.OperationalError("forced backup failure")

            def close(self):
                self._connection.close()

        def connect_with_failed_backup(database, *args, **kwargs):
            connection = real_connect(database, *args, **kwargs)
            if str(database).startswith(f"file:{db_path}"):
                return FailingBackupConnection(connection)
            return connection

        monkeypatch.setattr(backup_mod.sqlite3, "connect", connect_with_failed_backup)
        out_zip = tmp_path / "pre-update.zip"
        try:
            result = backup_mod._write_full_zip_backup(out_zip, hermes_home)
        finally:
            writer.close()

        assert result is None
        assert not out_zip.exists()

    @pytest.fixture
    def hermes_home(self, tmp_path):
        root = tmp_path / ".hermes"
        root.mkdir()
        _make_hermes_tree(root)
        return root

    def test_creates_backup_under_backups_dir(self, hermes_home):
        from hermes_cli.backup import create_pre_update_backup
        out = create_pre_update_backup(hermes_home=hermes_home)
        assert out is not None
        assert out.exists()
        assert out.parent == hermes_home / "backups"
        assert out.name.startswith("pre-update-")
        assert out.suffix == ".zip"

    def test_backup_contents_match_full_backup(self, hermes_home):
        """Pre-update backup should include the same user data that
        ``hermes backup`` would, and should exclude the same directories."""
        from hermes_cli.backup import create_pre_update_backup
        out = create_pre_update_backup(hermes_home=hermes_home)
        assert out is not None
        with zipfile.ZipFile(out) as zf:
            names = set(zf.namelist())
        # User data present
        assert "config.yaml" in names
        assert ".env" in names
        assert "sessions/abc123.json" in names
        assert "skills/my-skill/SKILL.md" in names
        assert "profiles/coder/config.yaml" in names
        # hermes-agent repo excluded
        assert not any(n.startswith("hermes-agent/") for n in names)
        # __pycache__ excluded
        assert not any("__pycache__" in n for n in names)
        # pid files excluded
        assert "gateway.pid" not in names

    def test_does_not_recurse_into_prior_backups(self, hermes_home):
        """The ``backups/`` directory must be excluded so that each backup
        doesn't grow exponentially by including all prior backups."""
        from hermes_cli.backup import create_pre_update_backup
        # First backup
        out1 = create_pre_update_backup(hermes_home=hermes_home)
        assert out1 is not None
        # Second backup — must not include the first
        out2 = create_pre_update_backup(hermes_home=hermes_home)
        assert out2 is not None
        with zipfile.ZipFile(out2) as zf:
            names = zf.namelist()
        assert not any(n.startswith("backups/") for n in names), (
            f"Pre-update backup recursed into backups/ — leaked: "
            f"{[n for n in names if n.startswith('backups/')]}"
        )

    def test_pre_update_zip_does_not_nest_the_pre_update_snapshot(self, hermes_home):
        """``hermes update`` in ``full`` mode takes the quick snapshot *before*
        the full zip, so the zip walk sees the snapshot it just made. It must
        skip it — otherwise every pre-update zip ships state.db twice."""
        from hermes_cli.backup import (
            _QUICK_SNAPSHOTS_DIR,
            create_pre_update_backup,
            create_quick_snapshot,
        )
        with sqlite3.connect(hermes_home / "state.db") as conn:
            conn.execute("CREATE TABLE sessions (id TEXT PRIMARY KEY)")

        snap_id = create_quick_snapshot(label="pre-update", hermes_home=hermes_home)
        assert snap_id and (hermes_home / _QUICK_SNAPSHOTS_DIR / snap_id / "state.db").exists()

        out = create_pre_update_backup(hermes_home=hermes_home)
        assert out is not None
        with zipfile.ZipFile(out) as zf:
            names = zf.namelist()
        assert "state.db" in names
        assert not any(n.startswith(_QUICK_SNAPSHOTS_DIR + "/") for n in names), names


    def test_rotation_keeps_only_n(self, hermes_home):
        """After more than ``keep`` backups are created, older ones are
        pruned automatically."""
        from hermes_cli.backup import create_pre_update_backup

        created = []
        for _ in range(5):
            out = create_pre_update_backup(hermes_home=hermes_home, keep=3)
            created.append(out)
            _advance_backup_clock()

        remaining = sorted(
            p.name for p in (hermes_home / "backups").iterdir()
            if p.name.startswith("pre-update-")
        )
        assert len(remaining) == 3
        # Oldest two should have been pruned
        assert created[0].name not in remaining
        assert created[1].name not in remaining
        # Newest three should remain
        assert created[4].name in remaining

    def test_rotation_preserves_manual_files(self, hermes_home):
        """Hand-dropped zips in ``backups/`` must not be touched by
        rotation — it only prunes files matching ``pre-update-*.zip``."""
        import time as _t
        from hermes_cli.backup import create_pre_update_backup

        (hermes_home / "backups").mkdir(exist_ok=True)
        manual = hermes_home / "backups" / "my-manual.zip"
        manual.write_bytes(b"manual backup")

        for _ in range(5):
            create_pre_update_backup(hermes_home=hermes_home, keep=2)
            _t.sleep(1.05)

        assert manual.exists(), "Manual backup zip was incorrectly pruned"

    def test_returns_none_if_root_missing(self, tmp_path):
        from hermes_cli.backup import create_pre_update_backup
        assert create_pre_update_backup(hermes_home=tmp_path / "does-not-exist") is None

    def test_keep_zero_does_not_delete_freshly_created_backup(self, hermes_home):
        """Regression: ``backup_keep: 0`` previously triggered ``backups[0:]``
        in the pruner — wiping the just-created zip and leaving the user
        with no recovery point.  The floor (keep>=1) preserves the new file
        regardless of misconfiguration; users who don't want backups should
        set ``pre_update_backup: false`` instead.
        """
        from hermes_cli.backup import create_pre_update_backup
        out = create_pre_update_backup(hermes_home=hermes_home, keep=0)
        assert out is not None
        assert out.exists(), (
            "keep=0 silently deleted the freshly-created backup; floor "
            "should preserve the just-written file."
        )

    def test_keep_negative_does_not_delete_freshly_created_backup(self, hermes_home):
        """Mirror coverage: any value <1 should be floored, not literally
        applied as a slice index."""
        from hermes_cli.backup import create_pre_update_backup
        out = create_pre_update_backup(hermes_home=hermes_home, keep=-3)
        assert out is not None
        assert out.exists()

    def test_keep_zero_still_prunes_older_backups(self, hermes_home):
        """The floor preserves the new backup but should NOT regress the
        rotation behaviour for older zips: a third call with keep=0 must
        still remove pre-existing backups beyond the (floored) limit of 1.
        """
        import time as _t
        from hermes_cli.backup import create_pre_update_backup

        first = create_pre_update_backup(hermes_home=hermes_home, keep=5)
        _t.sleep(1.05)
        second = create_pre_update_backup(hermes_home=hermes_home, keep=5)
        _t.sleep(1.05)
        third = create_pre_update_backup(hermes_home=hermes_home, keep=0)

        remaining = {
            p.name for p in (hermes_home / "backups").iterdir()
            if p.name.startswith("pre-update-")
        }
        assert third.name in remaining, "Floor must preserve the new backup"
        assert first.name not in remaining and second.name not in remaining, (
            f"keep=0 floor of 1 should still prune older backups; "
            f"remaining={remaining}"
        )

    def test_skips_symlinked_files(self, hermes_home, tmp_path):
        """Pre-update backups must not dereference symlinks outside HERMES_HOME."""
        from hermes_cli.backup import create_pre_update_backup

        outside = tmp_path / "outside-secret.txt"
        outside.write_text("outside secret\n")
        _symlink_file_or_skip(hermes_home / "skills" / "outside-link.txt", outside)

        out = create_pre_update_backup(hermes_home=hermes_home)
        assert out is not None
        with zipfile.ZipFile(out) as zf:
            names = zf.namelist()
            assert "skills/outside-link.txt" not in names
            assert all(zf.read(name) != b"outside secret\n" for name in names)


class TestRunPreUpdateBackup:
    """Tests for the ``_run_pre_update_backup`` wrapper in main.py —
    covers the consolidated off/quick/full mode gate, CLI flags, and
    user-facing output."""

    @pytest.fixture
    def hermes_home(self, tmp_path, monkeypatch):
        root = tmp_path / ".hermes"
        root.mkdir()
        _make_hermes_tree(root)
        # Point HERMES_HOME at the temp dir so config + backup paths resolve here
        monkeypatch.setenv("HERMES_HOME", str(root))
        # Make Path.home() point at tmp_path for anything that uses it
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        # Config reads resolve HERMES_HOME dynamically and their caches are
        # keyed by config path. Do not remove shared modules from sys.modules:
        # other test modules may retain imports from the existing module object.
        return root

    @staticmethod
    def _set_mode(hermes_home, value):
        import yaml
        (hermes_home / "config.yaml").write_text(yaml.safe_dump({
            "_config_version": 22,
            "updates": {"pre_update_backup": value},
        }))

    @staticmethod
    def _zips(hermes_home):
        d = hermes_home / "backups"
        return list(d.glob("pre-update-*.zip")) if d.exists() else []

    @staticmethod
    def _snaps(hermes_home):
        d = hermes_home / "state-snapshots"
        return [p for p in d.iterdir() if p.is_dir()] if d.exists() else []

    def test_default_creates_quick_snapshot_only(self, hermes_home, capsys):
        """With no config, the default mode is ``quick``: a state snapshot is
        created but NOT the full zip."""
        from hermes_cli.main import _run_pre_update_backup
        snap_id = _run_pre_update_backup(Namespace(no_backup=False, backup=False))
        out = capsys.readouterr().out
        assert snap_id is not None
        assert "Pre-update snapshot" in out
        assert "Creating pre-update backup" not in out
        assert self._snaps(hermes_home)
        assert not self._zips(hermes_home)

    def test_backup_flag_forces_full(self, hermes_home, capsys):
        """--backup forces the full zip (plus quick snapshot) for one run."""
        from hermes_cli.main import _run_pre_update_backup
        snap_id = _run_pre_update_backup(Namespace(no_backup=False, backup=True))
        out = capsys.readouterr().out
        assert snap_id is not None
        assert "Pre-update snapshot" in out
        assert "Creating pre-update backup" in out
        assert "Saved:" in out
        assert "hermes import" in out
        assert len(self._zips(hermes_home)) == 1

    def test_no_backup_flag_skips_everything(self, hermes_home, capsys):
        """--no-backup skips BOTH the quick snapshot and the zip."""
        from hermes_cli.main import _run_pre_update_backup
        snap_id = _run_pre_update_backup(Namespace(no_backup=True, backup=False))
        out = capsys.readouterr().out
        assert snap_id is None
        assert "skipped (--no-backup)" in out
        assert "Pre-update snapshot" not in out
        assert not self._snaps(hermes_home)
        assert not self._zips(hermes_home)

    def test_config_off_disables_everything_silently(self, hermes_home, capsys):
        """pre_update_backup: off — an explicit opt-out disables the quick
        snapshot too (it previously ran unconditionally), with no output."""
        self._set_mode(hermes_home, "off")
        from hermes_cli.main import _run_pre_update_backup
        snap_id = _run_pre_update_backup(Namespace(no_backup=False, backup=False))
        out = capsys.readouterr().out
        assert snap_id is None
        assert out == ""
        assert not self._snaps(hermes_home)
        assert not self._zips(hermes_home)

    def test_legacy_false_maps_to_off(self, hermes_home, capsys):
        """Legacy boolean ``false`` (the old zip opt-out) now means off."""
        self._set_mode(hermes_home, False)
        from hermes_cli.main import _run_pre_update_backup
        snap_id = _run_pre_update_backup(Namespace(no_backup=False, backup=False))
        assert snap_id is None
        assert capsys.readouterr().out == ""
        assert not self._snaps(hermes_home)
        assert not self._zips(hermes_home)

    def test_legacy_true_maps_to_full(self, hermes_home, capsys):
        """Legacy boolean ``true`` (the old always-zip opt-in) means full."""
        self._set_mode(hermes_home, True)
        from hermes_cli.main import _run_pre_update_backup
        snap_id = _run_pre_update_backup(Namespace(no_backup=False, backup=False))
        out = capsys.readouterr().out
        assert snap_id is not None
        assert "Creating pre-update backup" in out
        assert "Saved:" in out
        assert len(self._zips(hermes_home)) == 1

    def test_config_full_mode(self, hermes_home, capsys):
        self._set_mode(hermes_home, "full")
        from hermes_cli.main import _run_pre_update_backup
        snap_id = _run_pre_update_backup(Namespace(no_backup=False, backup=False))
        out = capsys.readouterr().out
        assert snap_id is not None
        assert "Pre-update snapshot" in out
        assert "Creating pre-update backup" in out
        assert len(self._zips(hermes_home)) == 1

    def test_config_quick_mode(self, hermes_home, capsys):
        self._set_mode(hermes_home, "quick")
        from hermes_cli.main import _run_pre_update_backup
        snap_id = _run_pre_update_backup(Namespace(no_backup=False, backup=False))
        out = capsys.readouterr().out
        assert snap_id is not None
        assert "Pre-update snapshot" in out
        assert "Creating pre-update backup" not in out
        assert not self._zips(hermes_home)

    def test_unknown_mode_falls_back_to_quick(self, hermes_home, capsys):
        self._set_mode(hermes_home, "bogus-mode")
        from hermes_cli.main import _run_pre_update_backup
        snap_id = _run_pre_update_backup(Namespace(no_backup=False, backup=False))
        out = capsys.readouterr().out
        assert snap_id is not None
        assert "Pre-update snapshot" in out
        assert not self._zips(hermes_home)

    def test_no_backup_flag_overrides_full_config(self, hermes_home, capsys):
        """--no-backup wins even when config says full."""
        self._set_mode(hermes_home, "full")
        from hermes_cli.main import _run_pre_update_backup
        snap_id = _run_pre_update_backup(Namespace(no_backup=True, backup=False))
        out = capsys.readouterr().out
        assert snap_id is None
        assert "skipped (--no-backup)" in out
        assert not self._snaps(hermes_home)
        assert not self._zips(hermes_home)

    def test_backup_flag_overrides_off_config(self, hermes_home, capsys):
        """--backup wins over config off for a single run."""
        self._set_mode(hermes_home, "off")
        from hermes_cli.main import _run_pre_update_backup
        snap_id = _run_pre_update_backup(Namespace(no_backup=False, backup=True))
        out = capsys.readouterr().out
        assert snap_id is not None
        assert "Creating pre-update backup" in out
        assert len(self._zips(hermes_home)) == 1


# ---------------------------------------------------------------------------
# Pre-migration backup (hermes claw migrate safety net)
# ---------------------------------------------------------------------------

class TestPreMigrationBackup:
    """Tests for create_pre_migration_backup — the auto-backup
    ``hermes claw migrate`` runs before mutating ~/.hermes/."""

    @pytest.fixture
    def hermes_home(self, tmp_path):
        root = tmp_path / ".hermes"
        root.mkdir()
        _make_hermes_tree(root)
        return root

    def test_creates_backup_under_backups_dir(self, hermes_home):
        from hermes_cli.backup import create_pre_migration_backup
        out = create_pre_migration_backup(hermes_home=hermes_home)
        assert out is not None
        assert out.exists()
        # Shares the backups/ directory with pre-update backups so `hermes
        # import` and the update-backup listing both pick them up.
        assert out.parent == hermes_home / "backups"
        assert out.name.startswith("pre-migration-")
        assert out.suffix == ".zip"

    def test_backup_uses_shared_exclusion_rules(self, hermes_home):
        """Pre-migration backup reuses the same exclusion rules as
        ``hermes backup`` / ``create_pre_update_backup`` — no drift."""
        from hermes_cli.backup import create_pre_migration_backup
        out = create_pre_migration_backup(hermes_home=hermes_home)
        assert out is not None
        with zipfile.ZipFile(out) as zf:
            names = set(zf.namelist())
        # User data present
        assert "config.yaml" in names
        assert ".env" in names
        assert "skills/my-skill/SKILL.md" in names
        # Same exclusions as the shared helper
        assert not any(n.startswith("hermes-agent/") for n in names)
        assert not any("__pycache__" in n for n in names)
        assert "gateway.pid" not in names

    def test_restorable_with_hermes_import(self, hermes_home, tmp_path):
        """The zip produced by pre-migration backup must be a valid Hermes
        backup — `hermes import` should accept it."""
        from hermes_cli.backup import create_pre_migration_backup, _validate_backup_zip
        out = create_pre_migration_backup(hermes_home=hermes_home)
        assert out is not None
        with zipfile.ZipFile(out) as zf:
            valid, _reason = _validate_backup_zip(zf)
        assert valid, "pre-migration zip failed _validate_backup_zip"

    def test_does_not_recurse_into_prior_backups(self, hermes_home):
        from hermes_cli.backup import create_pre_migration_backup
        out1 = create_pre_migration_backup(hermes_home=hermes_home)
        assert out1 is not None
        out2 = create_pre_migration_backup(hermes_home=hermes_home)
        assert out2 is not None
        with zipfile.ZipFile(out2) as zf:
            names = zf.namelist()
        assert not any(n.startswith("backups/") for n in names)

    def test_rotation_keeps_only_n(self, hermes_home):
        import time as _t
        from hermes_cli.backup import create_pre_migration_backup

        created = []
        for _ in range(7):
            out = create_pre_migration_backup(hermes_home=hermes_home, keep=3)
            if out is not None:
                created.append(out)
            _t.sleep(1.05)  # timestamp resolution

        remaining = sorted((hermes_home / "backups").glob("pre-migration-*.zip"))
        assert len(remaining) <= 3, f"expected <=3 backups retained, got {len(remaining)}"

    def test_missing_hermes_home_returns_none(self, tmp_path):
        """Fresh install with no ~/.hermes yet — nothing to back up."""
        from hermes_cli.backup import create_pre_migration_backup
        missing = tmp_path / "does-not-exist"
        out = create_pre_migration_backup(hermes_home=missing)
        assert out is None

    def test_does_not_touch_pre_update_backups(self, hermes_home):
        """Pre-migration rotation must only prune pre-migration-*.zip files,
        leaving pre-update-*.zip backups untouched."""
        from hermes_cli.backup import create_pre_update_backup, create_pre_migration_backup
        update_backup = create_pre_update_backup(hermes_home=hermes_home, keep=5)
        assert update_backup is not None and update_backup.exists()
        # Spin up a lot of migration backups with keep=1
        for _ in range(3):
            out = create_pre_migration_backup(hermes_home=hermes_home, keep=1)
            assert out is not None
            _advance_backup_clock()
        # Update backup must still be there
        assert update_backup.exists(), "pre-migration rotation wrongly pruned the pre-update backup"


# ---------------------------------------------------------------------------
# Cron jobs auto-restore after silent migration loss (issue #34600)
# ---------------------------------------------------------------------------

class TestRestoreCronJobsIfEmptied:
    """`hermes update` config migration can leave cron/jobs.json valid-but-empty,
    silently dropping every scheduled job. `restore_cron_jobs_if_emptied` is the
    post-migration safety net that restores from the pre-update snapshot."""

    @staticmethod
    def _seed_jobs(path: Path, jobs):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"jobs": jobs}))

    def _make_snapshot(self, hermes_home: Path, label="pre-update"):
        from hermes_cli.backup import create_quick_snapshot
        return create_quick_snapshot(label=label, hermes_home=hermes_home, keep=5)

    def test_restores_when_emptied_after_migration(self, tmp_path):
        from hermes_cli.backup import restore_cron_jobs_if_emptied
        hermes_home = tmp_path / ".hermes"
        jobs_path = hermes_home / "cron" / "jobs.json"
        # Pre-update: 3 real jobs.
        self._seed_jobs(jobs_path, [{"id": "a"}, {"id": "b"}, {"id": "c"}])
        snap_id = self._make_snapshot(hermes_home)
        assert snap_id

        # Migration silently empties the file (valid JSON, zero jobs).
        jobs_path.write_text(json.dumps({"jobs": []}))

        result = restore_cron_jobs_if_emptied(snap_id, hermes_home=hermes_home)
        assert result is not None
        assert result["restored"] is True
        assert result["job_count"] == 3
        assert result["snapshot_id"] == snap_id

        # The live file now has the jobs back.
        restored = json.loads(jobs_path.read_text())
        assert len(restored["jobs"]) == 3

    def test_noop_when_live_file_still_has_jobs(self, tmp_path):
        from hermes_cli.backup import restore_cron_jobs_if_emptied
        hermes_home = tmp_path / ".hermes"
        jobs_path = hermes_home / "cron" / "jobs.json"
        self._seed_jobs(jobs_path, [{"id": "a"}, {"id": "b"}])
        snap_id = self._make_snapshot(hermes_home)

        # Healthy path: file unchanged after update.
        result = restore_cron_jobs_if_emptied(snap_id, hermes_home=hermes_home)
        assert result is None

    def test_restores_when_partial_job_loss(self, tmp_path):
        """Desktop scheduler overwrites jobs.json with its own small set,
        losing tool-created crons while keeping desktop-tracked ones."""
        from hermes_cli.backup import restore_cron_jobs_if_emptied
        hermes_home = tmp_path / ".hermes"
        jobs_path = hermes_home / "cron" / "jobs.json"
        # Pre-update: 19 jobs (18 tool-created + 1 desktop watchdog).
        self._seed_jobs(
            jobs_path,
            [{"id": f"job-{i}"} for i in range(19)],
        )
        snap_id = self._make_snapshot(hermes_home)
        assert snap_id

        # Desktop scheduler overwrites with only its own 1 job.
        jobs_path.write_text(json.dumps({"jobs": [{"id": "desktop-watchdog"}]}))

        result = restore_cron_jobs_if_emptied(snap_id, hermes_home=hermes_home)
        assert result is not None
        assert result["restored"] is True
        assert result["job_count"] == 19

        # The live file now has all 19 jobs back.
        restored = json.loads(jobs_path.read_text())
        assert len(restored["jobs"]) == 19

    def test_noop_when_snapshot_had_no_jobs(self, tmp_path):
        from hermes_cli.backup import restore_cron_jobs_if_emptied
        hermes_home = tmp_path / ".hermes"
        jobs_path = hermes_home / "cron" / "jobs.json"
        # Pre-update genuinely had zero jobs; current is also empty.
        self._seed_jobs(jobs_path, [])
        snap_id = self._make_snapshot(hermes_home)
        jobs_path.write_text(json.dumps({"jobs": []}))

        result = restore_cron_jobs_if_emptied(snap_id, hermes_home=hermes_home)
        assert result is None

    def test_bom_live_file_still_counted(self, tmp_path):
        """A UTF-8 BOM on the live jobs.json (Windows editors) must not make
        _count_cron_jobs report None — that would silently disable the
        auto-restore safety net. utf-8-sig matches cron/jobs.load_jobs."""
        from hermes_cli.backup import _count_cron_jobs, restore_cron_jobs_if_emptied
        hermes_home = tmp_path / ".hermes"
        jobs_path = hermes_home / "cron" / "jobs.json"
        self._seed_jobs(jobs_path, [{"id": "a"}, {"id": "b"}, {"id": "c"}])
        snap_id = self._make_snapshot(hermes_home)
        assert snap_id

        # Migration empties the file AND a Windows editor leaves a BOM.
        jobs_path.write_bytes(b"\xef\xbb\xbf" + json.dumps({"jobs": []}).encode())
        assert _count_cron_jobs(jobs_path) == 0  # not None

        result = restore_cron_jobs_if_emptied(snap_id, hermes_home=hermes_home)
        assert result is not None
        assert result["restored"] is True
        assert result["job_count"] == 3

    def test_noop_when_live_file_unreadable(self, tmp_path):
        """An unparseable live file is left alone — that's a different failure
        mode the user should see, not silently overwrite."""
        from hermes_cli.backup import restore_cron_jobs_if_emptied
        hermes_home = tmp_path / ".hermes"
        jobs_path = hermes_home / "cron" / "jobs.json"
        self._seed_jobs(jobs_path, [{"id": "a"}])
        snap_id = self._make_snapshot(hermes_home)
        jobs_path.write_text("{ this is not valid json")

        result = restore_cron_jobs_if_emptied(snap_id, hermes_home=hermes_home)
        assert result is None
        # File left untouched.
        assert jobs_path.read_text() == "{ this is not valid json"

    def test_noop_when_snapshot_id_missing(self, tmp_path):
        from hermes_cli.backup import restore_cron_jobs_if_emptied
        hermes_home = tmp_path / ".hermes"
        jobs_path = hermes_home / "cron" / "jobs.json"
        self._seed_jobs(jobs_path, [])
        assert restore_cron_jobs_if_emptied(None, hermes_home=hermes_home) is None
        assert restore_cron_jobs_if_emptied("", hermes_home=hermes_home) is None

    def test_restores_legacy_bare_list_snapshot_shape(self, tmp_path):
        """A legacy snapshot storing a bare JSON list (not {"jobs": [...]}) is
        still counted and restored."""
        from hermes_cli.backup import restore_cron_jobs_if_emptied
        hermes_home = tmp_path / ".hermes"
        jobs_path = hermes_home / "cron" / "jobs.json"
        jobs_path.parent.mkdir(parents=True, exist_ok=True)
        jobs_path.write_text(json.dumps([{"id": "a"}, {"id": "b"}]))
        snap_id = self._make_snapshot(hermes_home)

        jobs_path.write_text(json.dumps({"jobs": []}))
        result = restore_cron_jobs_if_emptied(snap_id, hermes_home=hermes_home)
        assert result is not None
        assert result["job_count"] == 2


# ---------------------------------------------------------------------------
# config.yaml model/provider + MoA auto-restore after silent update rewrite
# (issue #64160)
# ---------------------------------------------------------------------------

class TestRestoreConfigModelSettingsIfRewritten:
    """Restore only user-set model settings that an update silently rewrote."""

    USER_CONFIG = (
        "_config_version: 39\n"
        "model:\n"
        "  provider: custom\n"
        "  default: zyphra/zamba-3-large\n"
        "  base_url: https://api.zyphra.example/v1\n"
        "moa:\n"
        "  enabled: true\n"
        "  presets:\n"
        "    council:\n"
        "      aggregator: {provider: custom, model: zyphra/zamba-3-large}\n"
        "custom_unknown_key:\n"
        "  hello: world\n"
    )

    def _make_snapshot(self, hermes_home: Path, label="pre-update"):
        from hermes_cli.backup import create_quick_snapshot
        return create_quick_snapshot(label=label, hermes_home=hermes_home, keep=5)

    def _seed(self, hermes_home: Path) -> Path:
        hermes_home.mkdir(parents=True, exist_ok=True)
        cfg = hermes_home / "config.yaml"
        cfg.write_text(self.USER_CONFIG, encoding="utf-8")
        return cfg

    def test_restores_rewritten_provider_and_dropped_moa(self, tmp_path):
        import yaml
        from hermes_cli.backup import restore_config_model_settings_if_rewritten

        hermes_home = tmp_path / ".hermes"
        cfg = self._seed(hermes_home)
        snap_id = self._make_snapshot(hermes_home)
        assert snap_id
        cfg.write_text(
            "_config_version: 39\nmodel:\n  provider: deepseek\n  default: deepseek-chat\n",
            encoding="utf-8",
        )

        result = restore_config_model_settings_if_rewritten(
            snap_id, hermes_home=hermes_home
        )
        assert result is not None
        assert result["restored"] is True
        assert result["snapshot_id"] == snap_id
        assert "model.provider" in result["keys"]
        assert "model.default" in result["keys"]
        assert "moa" in result["keys"]

        after = yaml.safe_load(cfg.read_text(encoding="utf-8"))
        assert after["model"]["provider"] == "custom"
        assert after["model"]["default"] == "zyphra/zamba-3-large"
        assert after["model"]["base_url"] == "https://api.zyphra.example/v1"
        assert after["moa"]["enabled"] is True
        assert after["moa"]["presets"]["council"]["aggregator"]["model"] == (
            "zyphra/zamba-3-large"
        )

    def test_noop_when_config_untouched(self, tmp_path):
        from hermes_cli.backup import restore_config_model_settings_if_rewritten

        hermes_home = tmp_path / ".hermes"
        cfg = self._seed(hermes_home)
        snap_id = self._make_snapshot(hermes_home)
        before = cfg.read_text(encoding="utf-8")

        result = restore_config_model_settings_if_rewritten(
            snap_id, hermes_home=hermes_home
        )
        assert result is None
        assert cfg.read_text(encoding="utf-8") == before

    def test_preserves_legitimate_update_writes(self, tmp_path):
        import yaml
        from hermes_cli.backup import restore_config_model_settings_if_rewritten

        hermes_home = tmp_path / ".hermes"
        cfg = self._seed(hermes_home)
        snap_id = self._make_snapshot(hermes_home)
        cfg.write_text(
            "_config_version: 40\n"
            "new_section:\n  added: true\n"
            "model:\n  provider: deepseek\n",
            encoding="utf-8",
        )

        result = restore_config_model_settings_if_rewritten(
            snap_id, hermes_home=hermes_home
        )
        assert result is not None
        after = yaml.safe_load(cfg.read_text(encoding="utf-8"))
        assert after["model"]["provider"] == "custom"
        assert after["_config_version"] == 40
        assert after["new_section"] == {"added": True}

    def test_noop_when_user_never_set_protected_keys(self, tmp_path):
        from hermes_cli.backup import restore_config_model_settings_if_rewritten

        hermes_home = tmp_path / ".hermes"
        hermes_home.mkdir(parents=True)
        cfg = hermes_home / "config.yaml"
        cfg.write_text("_config_version: 39\nagent: {}\n", encoding="utf-8")
        snap_id = self._make_snapshot(hermes_home)
        cfg.write_text(
            "_config_version: 39\nmodel:\n  provider: deepseek\n", encoding="utf-8"
        )
        result = restore_config_model_settings_if_rewritten(
            snap_id, hermes_home=hermes_home
        )
        assert result is None

    def test_noop_on_unreadable_live_config(self, tmp_path):
        from hermes_cli.backup import restore_config_model_settings_if_rewritten

        hermes_home = tmp_path / ".hermes"
        cfg = self._seed(hermes_home)
        snap_id = self._make_snapshot(hermes_home)
        cfg.write_text(": not [valid yaml", encoding="utf-8")
        result = restore_config_model_settings_if_rewritten(
            snap_id, hermes_home=hermes_home
        )
        assert result is None
        assert cfg.read_text(encoding="utf-8") == ": not [valid yaml"

    def test_noop_without_snapshot_id(self, tmp_path):
        from hermes_cli.backup import restore_config_model_settings_if_rewritten

        assert restore_config_model_settings_if_rewritten(
            "", hermes_home=tmp_path / ".hermes"
        ) is None


# ---------------------------------------------------------------------------
# Memory-provider external paths (~/.honcho, ~/.hindsight, ...) — captured via
# MemoryProvider.backup_paths() and restored to their original home-relative
# location, NOT under HERMES_HOME. (backup/import cycle data-loss fix)
# ---------------------------------------------------------------------------

class TestMemoryProviderExternalPaths:
    def _make_min_tree(self, hermes_home: Path) -> None:
        hermes_home.mkdir(parents=True, exist_ok=True)
        (hermes_home / "config.yaml").write_text("model:\n  provider: openrouter\n")
        (hermes_home / ".env").write_text("OPENROUTER_API_KEY=sk-test\n")
        (hermes_home / "state.db").write_bytes(b"x")

    def test_backup_captures_external_paths_under_external_prefix(self, tmp_path, monkeypatch):
        """Provider state under ~/.honcho is archived beneath _external/,
        encoded relative to the home directory."""
        hermes_home = tmp_path / ".hermes"
        self._make_min_tree(hermes_home)
        # External provider state living OUTSIDE HERMES_HOME.
        honcho = tmp_path / ".honcho"
        honcho.mkdir()
        (honcho / "config.json").write_text('{"peer":"alice"}')
        (honcho / "sub").mkdir()
        (honcho / "sub" / "x.json").write_text('{"a":1}')

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        import hermes_cli.backup as backup_mod
        monkeypatch.setattr(
            backup_mod, "_collect_memory_provider_external_paths", lambda: [honcho]
        )

        out_zip = tmp_path / "backup.zip"
        backup_mod.run_backup(Namespace(output=str(out_zip)))

        with zipfile.ZipFile(out_zip) as zf:
            names = set(zf.namelist())
        assert "_external/.honcho/config.json" in names
        assert "_external/.honcho/sub/x.json" in names
        # In-home files still present.
        assert "config.yaml" in names

    def test_backup_skips_external_paths_outside_home(self, tmp_path, monkeypatch):
        """A declared path outside the home dir is not portable and must be
        skipped, never archived."""
        hermes_home = tmp_path / ".hermes"
        self._make_min_tree(hermes_home)
        outside = tmp_path.parent / "outside-home-secret"
        outside.mkdir(exist_ok=True)
        (outside / "leak.json").write_text('{"secret":1}')

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        import hermes_cli.backup as backup_mod
        monkeypatch.setattr(
            backup_mod, "_collect_memory_provider_external_paths", lambda: [outside]
        )

        out_zip = tmp_path / "backup.zip"
        backup_mod.run_backup(Namespace(output=str(out_zip)))

        with zipfile.ZipFile(out_zip) as zf:
            names = set(zf.namelist())
        assert not any(n.startswith("_external/") for n in names)
        assert not any("leak.json" in n for n in names)
        (outside / "leak.json").unlink()
        outside.rmdir()

    def test_import_restores_external_to_home_relative_location(self, tmp_path, monkeypatch):
        """_external/ members restore to ~/<relpath>, not under HERMES_HOME,
        and credential-shaped files get 0600."""
        dst_home = tmp_path / "dst"
        dst_home.mkdir()
        hermes_home = dst_home / ".hermes"
        hermes_home.mkdir()

        zip_path = tmp_path / "backup.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("config.yaml", "model: {}\n")
            zf.writestr(".env", "X=1\n")
            zf.writestr("state.db", "")
            zf.writestr("_external/.honcho/config.json", '{"peer":"bob"}')

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: dst_home)

        from hermes_cli.backup import run_import
        run_import(Namespace(zipfile=str(zip_path), force=True))

        restored = dst_home / ".honcho" / "config.json"
        assert restored.exists()
        assert restored.read_text() == '{"peer":"bob"}'
        # Credential-shaped file tightened.
        assert (restored.stat().st_mode & 0o777) == 0o600
        # External state did NOT leak into HERMES_HOME.
        assert not (hermes_home / "_external").exists()

    def test_import_blocks_external_path_traversal(self, tmp_path, monkeypatch):
        """A malicious _external/ member that escapes the home dir is blocked."""
        dst_home = tmp_path / "dst"
        dst_home.mkdir()
        hermes_home = dst_home / ".hermes"
        hermes_home.mkdir()
        sentinel = tmp_path / "PWNED"

        zip_path = tmp_path / "backup.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("config.yaml", "model: {}\n")
            zf.writestr(".env", "X=1\n")
            zf.writestr("state.db", "")
            zf.writestr("_external/../../PWNED", "pwned")

        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setattr(Path, "home", lambda: dst_home)

        from hermes_cli.backup import run_import
        run_import(Namespace(zipfile=str(zip_path), force=True))

        assert not sentinel.exists()

    def test_abc_backup_paths_defaults_empty(self):
        """The ABC default returns [] so providers opt in explicitly."""
        from agent.memory_provider import MemoryProvider

        class _Dummy(MemoryProvider):
            @property
            def name(self):
                return "dummy"

            def is_available(self):
                return True

            def initialize(self, session_id, **kwargs):
                pass

            def get_tool_schemas(self):
                return []

        assert _Dummy().backup_paths() == []

    def test_honcho_provider_declares_global_config_dir(self, tmp_path, monkeypatch):
        """The honcho provider's backup_paths() resolves to ~/.honcho."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        from plugins.memory.honcho import HonchoMemoryProvider

        paths = HonchoMemoryProvider().backup_paths()
        assert str(tmp_path / ".honcho") in paths

    def test_hindsight_provider_declares_legacy_dir(self, tmp_path, monkeypatch):
        """The hindsight provider's backup_paths() resolves to ~/.hindsight."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        from plugins.memory.hindsight import HindsightMemoryProvider

        paths = HindsightMemoryProvider().backup_paths()
        assert str(tmp_path / ".hindsight") in paths

# ---------------------------------------------------------------------------
# run_import: HERMES_HOME override handling (issue #99839)
# ---------------------------------------------------------------------------

class TestImportHonorsHermesHomeOverride:
    """`hermes import` must restore into the home the command runs under.

    Resolving the target through get_default_hermes_root() maps a profile
    home (<root>/profiles/<name>) back to <root>: the import then overwrites
    the live root's config.yaml while the profile directory stays empty —
    exactly what "Target:" printed it would NOT do.
    """

    def _make_backup_zip(self, tmp_path):
        import zipfile

        src_root = tmp_path / "src-home"
        src_root.mkdir()
        (src_root / "config.yaml").write_text("model:\n  provider: anthropic\n")
        (src_root / ".env").write_text("ANTHROPIC_API_KEY=sk-test\n")
        zip_path = tmp_path / "backup.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.write(src_root / "config.yaml", "config.yaml")
            zf.write(src_root / ".env", ".env")
        return zip_path

    def test_import_targets_named_profile_home(self, tmp_path, monkeypatch):
        """HERMES_HOME=<root>/profiles/<name> must restore INTO the profile,
        not into <root> (which would clobber the live root config)."""
        root = tmp_path / "hermes-root"
        profile = root / "profiles" / "coder"
        profile.mkdir(parents=True)
        # Live root config that must survive untouched.
        (root / "config.yaml").write_text("model:\n  provider: openai\n")

        monkeypatch.setenv("HERMES_HOME", str(profile))
        from hermes_constants import get_hermes_home

        assert get_hermes_home() == profile

        zip_path = self._make_backup_zip(tmp_path)

        import argparse

        from hermes_cli.backup import run_import

        args = argparse.Namespace(zipfile=str(zip_path), force=True)
        run_import(args)

        assert (profile / "config.yaml").read_text() == (
            "model:\n  provider: anthropic\n"
        )
        assert (root / "config.yaml").read_text() == "model:\n  provider: openai\n"

    def test_import_skips_gateway_install_for_non_default_home(
        self, tmp_path, monkeypatch
    ):
        """A restore into a sandbox must not silently start a second gateway
        pointed at it — the profile/sandbox gateway would shadow the default
        service installed by the primary install."""
        native_default = tmp_path / "native-default"
        sandbox = tmp_path / "sandbox-home"
        sandbox.mkdir(parents=True)
        # Live default install markers.
        native_default.mkdir()
        (native_default / "config.yaml").write_text("model:\n  provider: openai\n")

        monkeypatch.setenv("HERMES_HOME", str(sandbox))

        import argparse

        import hermes_constants
        from hermes_cli import backup as backup_mod

        monkeypatch.setattr(
            backup_mod,
            "_get_platform_default_hermes_home",
            lambda: native_default,
        )

        calls = []
        monkeypatch.setattr(
            "hermes_cli.gateway.ensure_gateway_service",
            lambda *a, **kw: calls.append(kw),
        )
        monkeypatch.setattr(
            "hermes_cli.gateway._is_service_running",
            lambda: False,
        )

        zip_path = self._make_backup_zip(tmp_path)
        args = argparse.Namespace(zipfile=str(zip_path), force=True)
        backup_mod.run_import(args)

        assert calls == [], "gateway must not be auto-installed for a sandbox restore"

    def test_import_installs_gateway_when_default_home_is_target(
        self, tmp_path, monkeypatch
    ):
        """Restoring into the default home keeps the auto-install behavior."""
        native_default = tmp_path / "native-default"
        native_default.mkdir()
        monkeypatch.setenv("HERMES_HOME", str(native_default))

        import argparse

        from hermes_cli import backup as backup_mod

        monkeypatch.setattr(
            backup_mod,
            "_get_platform_default_hermes_home",
            lambda: native_default,
        )

        calls = []
        monkeypatch.setattr(
            "hermes_cli.gateway.ensure_gateway_service",
            lambda *a, **kw: calls.append(kw),
        )
        monkeypatch.setattr(
            "hermes_cli.gateway._is_service_running",
            lambda: False,
        )

        zip_path = self._make_backup_zip(tmp_path)
        args = argparse.Namespace(zipfile=str(zip_path), force=True)
        backup_mod.run_import(args)

        assert calls and calls[0].get("context") == "import"


# ---------------------------------------------------------------------------
# Live session database import (issue #100960)
# ---------------------------------------------------------------------------

def _write_session_db(path: Path, sessions: int, messages_per_session: int) -> None:
    """Create a minimal Hermes-shaped session database at *path*."""
    conn = sqlite3.connect(str(path))
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS sessions "
            "(session_id TEXT PRIMARY KEY, message_count INTEGER)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS messages "
            "(id INTEGER PRIMARY KEY, session_id TEXT, content TEXT)"
        )
        for s in range(sessions):
            sid = f"sess-{s}"
            conn.execute(
                "INSERT INTO sessions VALUES (?, ?)", (sid, messages_per_session)
            )
            for m in range(messages_per_session):
                conn.execute(
                    "INSERT INTO messages (session_id, content) VALUES (?, ?)",
                    (sid, f"{sid}-msg-{m}"),
                )
        conn.commit()
    finally:
        conn.close()


class TestImportLiveSessionDatabase:
    """`hermes import` must not swap the inode of a database Hermes holds open.

    Publishing state.db with a rename leaves any live gateway/dashboard/WebUI
    connection reading and writing the unlinked inode, so its sessions vanish
    from the database everyone else opens and nothing is logged (#100960).
    """

    def _zip_with_db(self, zip_path: Path, db_path: Path) -> None:
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.write(db_path, "state.db")

    def _prepare(self, tmp_path, monkeypatch, live=(3, 4), backup=(2, 2)):
        home = tmp_path / ".hermes"
        home.mkdir()
        monkeypatch.setenv("HERMES_HOME", str(home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        live_db = home / "state.db"
        _write_session_db(live_db, *live)

        staged = tmp_path / "backup-state.db"
        _write_session_db(staged, *backup)
        zip_path = tmp_path / "backup.zip"
        self._zip_with_db(zip_path, staged)
        return home, live_db, zip_path

    def test_live_holder_sees_imported_rows(self, tmp_path, monkeypatch):
        """A connection open across the import converges on the imported data."""
        from hermes_cli.backup import run_import

        home, live_db, zip_path = self._prepare(tmp_path, monkeypatch)

        holder = sqlite3.connect(str(live_db))
        # Read first so the connection has cached pages of the pre-import file.
        assert holder.execute("SELECT COUNT(*) FROM messages").fetchone()[0] == 12
        inode_before = os.stat(live_db).st_ino

        try:
            run_import(Namespace(zipfile=str(zip_path), force=True))
            assert holder.execute("SELECT COUNT(*) FROM messages").fetchone()[0] == 4
        finally:
            holder.close()

        assert os.stat(live_db).st_ino == inode_before
        assert _count_rows(live_db) == (2, 4)

    def test_older_backup_reports_replaced_sessions(self, tmp_path, monkeypatch, capsys):
        """Importing a backup that predates recorded work says what it dropped."""
        from hermes_cli.backup import run_import

        home, live_db, zip_path = self._prepare(tmp_path, monkeypatch)
        run_import(Namespace(zipfile=str(zip_path), force=True))

        out = capsys.readouterr().out
        assert "Session data replaced by older backup contents" in out
        assert "3 session(s) / 12 message(s) -> 2 / 4" in out

    def test_newer_backup_reports_nothing(self, tmp_path, monkeypatch, capsys):
        """No warning when the import does not shrink the database."""
        from hermes_cli.backup import run_import

        home, live_db, zip_path = self._prepare(
            tmp_path, monkeypatch, live=(1, 1), backup=(3, 4)
        )
        run_import(Namespace(zipfile=str(zip_path), force=True))

        out = capsys.readouterr().out
        assert "Session data replaced by older backup contents" not in out

    def test_refused_restore_is_reported_and_leaves_db_intact(
        self, tmp_path, monkeypatch, capsys
    ):
        """A refused live-safe restore is a warning, not a counted success."""
        import hermes_cli.backup as backup_mod

        home, live_db, zip_path = self._prepare(tmp_path, monkeypatch)
        monkeypatch.setattr(backup_mod, "_safe_restore_db", lambda src, dst: False)

        backup_mod.run_import(Namespace(zipfile=str(zip_path), force=True))

        out = capsys.readouterr().out
        assert "files skipped" in out
        assert "state.db" in out
        # The pre-import database is still the one on disk.
        assert _count_rows(live_db) == (3, 12)

    def test_sidecar_members_are_not_installed_beside_a_restored_db(
        self, tmp_path, monkeypatch
    ):
        """A `state.db-wal` member from an old/hand-built archive must not be
        os.replace'd next to the page-restored database: it describes a
        different image and SQLite would replay it on the next open."""
        from hermes_cli.backup import run_import

        home, live_db, zip_path = self._prepare(tmp_path, monkeypatch)
        with zipfile.ZipFile(zip_path, "a") as zf:
            zf.writestr("state.db-wal", b"foreign-wal-from-archive")
            zf.writestr("state.db-shm", b"foreign-shm")
            zf.writestr("state.db-journal", b"foreign-journal")

        run_import(Namespace(zipfile=str(zip_path), force=True))

        for suffix, payload in (
            ("-wal", b"foreign-wal-from-archive"),
            ("-shm", b"foreign-shm"),
            ("-journal", b"foreign-journal"),
        ):
            sidecar = live_db.with_name("state.db" + suffix)
            assert not sidecar.exists() or sidecar.read_bytes() != payload, suffix
        assert _count_rows(live_db) == (2, 4)

    def test_missing_target_takes_the_plain_publish(self, tmp_path, monkeypatch):
        """A fresh install has no inode to preserve; the member still lands."""
        from hermes_cli.backup import run_import

        home = tmp_path / ".hermes"
        home.mkdir()
        monkeypatch.setenv("HERMES_HOME", str(home))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        staged = tmp_path / "backup-state.db"
        _write_session_db(staged, 2, 3)
        zip_path = tmp_path / "backup.zip"
        self._zip_with_db(zip_path, staged)

        run_import(Namespace(zipfile=str(zip_path), force=True))
        assert _count_rows(home / "state.db") == (2, 6)


def _count_rows(db_path: Path) -> tuple[int, int]:
    conn = sqlite3.connect(str(db_path))
    try:
        return (
            conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0],
            conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0],
        )
    finally:
        conn.close()

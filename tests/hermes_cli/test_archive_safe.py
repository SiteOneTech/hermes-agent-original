"""Tests for the shared safe archive read/write helpers.

``make_targz`` backs both ``hermes profile export`` and ``hermes kanban
export``. Archive extraction must reject hostile or oversized inputs without
writing a partial destination, and a failed archive write must preserve an
existing destination.
"""

from __future__ import annotations

import io
import sys
import tarfile
from pathlib import Path

import pytest

_WORKTREE = Path(__file__).resolve().parents[2]
if str(_WORKTREE) not in sys.path:
    sys.path.insert(0, str(_WORKTREE))

from hermes_cli import archive_safe
from hermes_cli.archive_safe import make_targz


def _write_archive(path: Path, files: dict[str, bytes], *, symlink: str | None = None) -> None:
    with tarfile.open(path, "w:gz") as tf:
        root = tarfile.TarInfo("payload")
        root.type = tarfile.DIRTYPE
        tf.addfile(root)
        for name, content in files.items():
            member = tarfile.TarInfo(f"payload/{name}")
            member.size = len(content)
            tf.addfile(member, io.BytesIO(content))
        if symlink is not None:
            member = tarfile.TarInfo("payload/link")
            member.type = tarfile.SYMTYPE
            member.linkname = symlink
            tf.addfile(member)


def test_rejects_archives_over_member_count_without_writes(tmp_path, monkeypatch):
    archive = tmp_path / "many.tar.gz"
    _write_archive(archive, {"one": b"1", "two": b"2"})
    destination = tmp_path / "out"
    monkeypatch.setattr(archive_safe, "MAX_ARCHIVE_MEMBERS", 2)

    with pytest.raises(ValueError, match="too many members"):
        archive_safe.safe_extract_targz(archive, destination)

    assert not destination.exists()


def test_rejects_oversized_member_without_writes(tmp_path, monkeypatch):
    archive = tmp_path / "large-member.tar.gz"
    _write_archive(archive, {"large": b"12345"})
    destination = tmp_path / "out"
    monkeypatch.setattr(archive_safe, "MAX_ARCHIVE_MEMBER_BYTES", 4)

    with pytest.raises(ValueError, match="member exceeds expanded size limit"):
        archive_safe.safe_extract_targz(archive, destination)

    assert not destination.exists()


def test_rejects_oversized_total_without_writes(tmp_path, monkeypatch):
    archive = tmp_path / "large-total.tar.gz"
    _write_archive(archive, {"one": b"1234", "two": b"5678"})
    destination = tmp_path / "out"
    monkeypatch.setattr(archive_safe, "MAX_ARCHIVE_MEMBER_BYTES", 8)
    monkeypatch.setattr(archive_safe, "MAX_ARCHIVE_TOTAL_BYTES", 7)

    with pytest.raises(ValueError, match="total expanded size limit"):
        archive_safe.safe_extract_targz(archive, destination)

    assert not destination.exists()


def test_late_hostile_member_leaves_no_partial_destination(tmp_path):
    archive = tmp_path / "late-link.tar.gz"
    _write_archive(archive, {"safe.txt": b"safe"}, symlink="/etc/passwd")
    destination = tmp_path / "out"

    with pytest.raises(ValueError, match="Unsupported archive member"):
        archive_safe.safe_extract_targz(archive, destination)

    assert not destination.exists()


def test_root_scan_enforces_the_same_member_limit(tmp_path, monkeypatch):
    archive = tmp_path / "many.tar.gz"
    _write_archive(archive, {"one": b"1", "two": b"2"})
    monkeypatch.setattr(archive_safe, "MAX_ARCHIVE_MEMBERS", 2)

    with pytest.raises(ValueError, match="too many members"):
        archive_safe.archive_root_dirs(archive)


def _stage_source(tmp_path: Path) -> None:
    payload = tmp_path / "src" / "inner"
    payload.mkdir(parents=True)
    (payload / "file.txt").write_text("hello")


def test_make_targz_preserves_existing_file_on_mid_write_failure(tmp_path, monkeypatch):
    _stage_source(tmp_path)
    base = str(tmp_path / "out")
    archive_path = Path(f"{base}.tar.gz")
    sentinel = b"PRE-EXISTING ARCHIVE THAT MUST SURVIVE A FAILED RE-EXPORT"
    archive_path.write_bytes(sentinel)

    def _boom(self, *a, **k):
        raise RuntimeError("simulated failure mid-add (disk full / permission loss)")

    monkeypatch.setattr(tarfile.TarFile, "add", _boom)

    with pytest.raises(RuntimeError):
        make_targz(base, str(tmp_path), "src")

    assert archive_path.read_bytes() == sentinel, (
        "a mid-write failure must not truncate/replace a pre-existing archive"
    )
    leftovers = [p for p in tmp_path.iterdir() if p.name.startswith(".archive_")]
    assert leftovers == [], f"temp file was not cleaned up on failure: {leftovers}"


def test_make_targz_round_trips_content(tmp_path):
    _stage_source(tmp_path)
    base = str(tmp_path / "out")

    result = make_targz(base, str(tmp_path), "src")

    assert result == f"{base}.tar.gz"
    with tarfile.open(result, "r:gz") as tf:
        names = sorted(m.name for m in tf.getmembers())
        assert "src/inner/file.txt" in names
        member = tf.extractfile("src/inner/file.txt")
        assert member is not None
        assert member.read() == b"hello"


def test_make_targz_overwrites_existing_file_on_success(tmp_path):
    _stage_source(tmp_path)
    base = str(tmp_path / "out")
    archive_path = Path(f"{base}.tar.gz")
    archive_path.write_bytes(b"stale archive from a previous export")

    make_targz(base, str(tmp_path), "src")

    with tarfile.open(archive_path, "r:gz") as tf:
        assert "src/inner/file.txt" in {m.name for m in tf.getmembers()}

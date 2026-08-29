from __future__ import annotations

import io
import tarfile
from pathlib import Path

import pytest

from hermes_cli import archive_safe


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

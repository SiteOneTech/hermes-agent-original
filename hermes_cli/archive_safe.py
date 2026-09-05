"""Safe ``tar.gz`` primitives shared by the profile and kanban transfer paths."""

from __future__ import annotations

import os
import shutil
import tarfile
import tempfile
from contextlib import suppress
from pathlib import Path, PurePosixPath, PureWindowsPath


# Expanded-data limits. These are intentionally generous enough for profile
# workspaces and kanban attachment bundles, while putting a finite ceiling on
# gzip/tar bombs before any archive bytes reach the requested destination.
MAX_ARCHIVE_MEMBERS = 25_000
MAX_ARCHIVE_MEMBER_BYTES = 1024 * 1024 * 1024  # 1 GiB
MAX_ARCHIVE_TOTAL_BYTES = 5 * 1024 * 1024 * 1024  # 5 GiB
_COPY_CHUNK_BYTES = 1024 * 1024


def normalize_archive_parts(member_name: str) -> list[str]:
    """Return safe path parts for an archive member, or raise ``ValueError``.

    Rejects absolute paths (POSIX and Windows, including drive letters), empty names, and any ``..``
    component. Backslashes are folded to ``/`` first so a Windows-authored archive can't smuggle a
    separator past the POSIX parse.
    """
    normalized_name = member_name.replace("\\", "/")
    posix_path = PurePosixPath(normalized_name)
    windows_path = PureWindowsPath(member_name)
    parts = [part for part in posix_path.parts if part not in {"", "."}]
    if (not normalized_name or posix_path.is_absolute() or windows_path.is_absolute()
            or windows_path.drive or not parts or ".." in parts):
        raise ValueError(f"Unsafe archive member path: {member_name}")
    return parts


def make_targz(base: str, root_dir: str, base_dir: str) -> str:
    """Create ``<base>.tar.gz`` of ``root_dir/base_dir`` in GNU tar format.

    Writes to a sibling temp file and renames onto the archive path only after it is fully written.
    """
    archive_path = f"{base}.tar.gz"
    dest_dir = os.path.dirname(archive_path) or "."
    fd, tmp_path = tempfile.mkstemp(dir=dest_dir, prefix=".archive_", suffix=".tar.gz.tmp")
    try:
        with os.fdopen(fd, "wb") as f, \
                tarfile.open(fileobj=f, mode="w:gz", format=tarfile.GNU_FORMAT) as tf:
            tf.add(str(Path(root_dir) / base_dir), arcname=base_dir)
        os.replace(tmp_path, archive_path)
    except BaseException:
        with suppress(OSError):
            os.unlink(tmp_path)
        raise
    return archive_path


def _validated_members(tf: tarfile.TarFile) -> list[tuple[tarfile.TarInfo, list[str]]]:
    """Read and validate every header without writing archive contents."""
    validated: list[tuple[tarfile.TarInfo, list[str]]] = []
    total_bytes = 0

    for count, member in enumerate(tf, start=1):
        if count > MAX_ARCHIVE_MEMBERS:
            raise ValueError(
                f"Archive has too many members (limit: {MAX_ARCHIVE_MEMBERS})"
            )

        parts = normalize_archive_parts(member.name)
        if not (member.isdir() or member.isfile()):
            raise ValueError(f"Unsupported archive member type: {member.name}")

        if member.isfile():
            size = int(member.size)
            if size < 0:
                raise ValueError(f"Invalid archive member size: {member.name}")
            if size > MAX_ARCHIVE_MEMBER_BYTES:
                raise ValueError(
                    "Archive member exceeds expanded size limit "
                    f"({MAX_ARCHIVE_MEMBER_BYTES} bytes): {member.name}"
                )
            total_bytes += size
            if total_bytes > MAX_ARCHIVE_TOTAL_BYTES:
                raise ValueError(
                    "Archive exceeds total expanded size limit "
                    f"({MAX_ARCHIVE_TOTAL_BYTES} bytes)"
                )

        validated.append((member, parts))

    return validated


def _copy_bounded_member(
    extracted,
    target: Path,
    member: tarfile.TarInfo,
    total_written: list[int],
) -> None:
    """Copy one regular member while re-enforcing expanded byte limits."""
    member_written = 0
    with extracted, open(target, "wb") as dst:
        while True:
            chunk = extracted.read(_COPY_CHUNK_BYTES)
            if not chunk:
                break
            member_written += len(chunk)
            total_written[0] += len(chunk)
            if member_written > MAX_ARCHIVE_MEMBER_BYTES:
                raise ValueError(
                    "Archive member exceeds expanded size limit during extraction: "
                    f"{member.name}"
                )
            if total_written[0] > MAX_ARCHIVE_TOTAL_BYTES:
                raise ValueError(
                    "Archive exceeds total expanded size limit during extraction"
                )
            dst.write(chunk)

    if member_written != member.size:
        raise ValueError(
            f"Archive member size changed during extraction: {member.name}"
        )


def _install_staged_tree(staged: Path, destination: Path) -> None:
    """Land a fully extracted tree, atomically for absent/empty destinations."""
    if not destination.exists():
        staged.replace(destination)
        return
    if not destination.is_dir():
        raise ValueError(f"Archive destination is not a directory: {destination}")

    try:
        next(destination.iterdir())
    except StopIteration:
        destination.rmdir()
        staged.replace(destination)
        return

    # Compatibility for callers that deliberately extract into a populated
    # staging tree. All hostile-input and read failures have already settled
    # in the private tree before this merge begins.
    shutil.copytree(staged, destination, dirs_exist_ok=True)


def safe_extract_targz(archive: Path, destination: Path) -> None:
    """Extract ``archive`` into ``destination`` without path escapes or links.

    Only directories and regular files are extracted; symlinks, hardlinks, and device nodes raise
    rather than being silently skipped, so a tampered archive fails the import instead of landing a
    partial tree. Headers are validated and expanded-size capped BEFORE any byte reaches
    ``destination``, and the tree is staged in a sibling temp dir so a rejected archive cannot leave
    a partial result behind.
    """
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        prefix=".hermes_extract_", dir=destination.parent
    ) as tmpdir:
        staged = Path(tmpdir) / "tree"
        staged.mkdir()

        with tarfile.open(archive, "r:gz") as tf:
            members = _validated_members(tf)
            total_written = [0]
            for member, parts in members:
                target = staged.joinpath(*parts)
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue

                target.parent.mkdir(parents=True, exist_ok=True)
                extracted = tf.extractfile(member)
                if extracted is None:
                    raise ValueError(f"Cannot read archive member: {member.name}")

                _copy_bounded_member(extracted, target, member, total_written)
                with suppress(OSError):
                    os.chmod(target, member.mode & 0o777)

        _install_staged_tree(staged, destination)


def archive_root_dirs(archive: Path) -> set[str]:
    """Return the archive's top-level directory names.

    Transfer archives carry exactly one root directory, which names the thing being imported.
    Inspecting before extraction lets the caller resolve the target name (and refuse a malformed
    archive) without first mutating a live tree.
    """
    with tarfile.open(archive, "r:gz") as tf:
        return {
            parts[0]
            for member, parts in _validated_members(tf)
            if len(parts) > 1 or member.isdir()
        }


def copy_regular_files(src: Path, dst: Path) -> int:
    """Copy the regular files under ``src`` into ``dst``, skipping symlinks; return the count.

    Used on the *export* side so a symlink planted in an attachments or logs tree can't pull an
    arbitrary file into the archive. A missing ``src`` copies nothing.
    """
    if not src.is_dir():
        return 0
    copied = 0
    for entry in sorted(src.rglob("*")):
        if entry.is_symlink() or not entry.is_file():
            continue
        target = dst / entry.relative_to(src)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(entry, target)
        copied += 1
    return copied

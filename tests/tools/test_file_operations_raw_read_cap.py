"""read_file_raw's size cap and the V4A operations that must still work past it.

Fork note: this module used to assert upstream's transport internals
(``_probe_regular_file`` / ``_read_exact_bytes(max_bytes=...)``). The Zeus fork
reads through a single validated descriptor instead (``_read_regular_file_page``:
one ``os.open`` + ``fstat`` on THAT descriptor, then a capped scan), so a stale
pre-read size probe — upstream's ``stale_size=True`` case — is not a state this
architecture can reach: there is no separate probe to go stale. The cap is
enforced inside the same descriptor read, which is what these tests assert.
"""

import pytest

from tools.environments.local import LocalEnvironment
from tools.file_operations import ShellFileOperations


def test_raw_read_cap_with_real_file(tmp_path, monkeypatch):
    import tools.file_operations as operations

    monkeypatch.setattr(operations, "_RAW_READ_MAX_BYTES", 64)
    target = tmp_path / "large.log"
    target.write_text("a" * 1024, encoding="utf-8")
    ops = ShellFileOperations(LocalEnvironment(cwd=str(tmp_path)))
    result = ops.read_file_raw(str(target))
    assert result.error and "too large" in result.error
    assert not result.content


def test_raw_read_cap_stops_the_transfer_near_the_cap(tmp_path, monkeypatch):
    """The cap must bound the bytes that cross the transport, not just the verdict:
    a 64 KiB file under a 64-byte cap may not be shipped in full and then rejected."""
    import tools.file_operations as operations

    monkeypatch.setattr(operations, "_RAW_READ_MAX_BYTES", 64)
    target = tmp_path / "large.log"
    target.write_text("a" * 65536, encoding="utf-8")
    ops = ShellFileOperations(LocalEnvironment(cwd=str(tmp_path)))

    payloads = []
    real_snippet = ops._run_python_snippet

    def recording_snippet(snippet, *args, **kwargs):
        out = real_snippet(snippet, *args, **kwargs)
        payloads.append(len(getattr(out, "stdout", "") or ""))
        return out

    monkeypatch.setattr(ops, "_run_python_snippet", recording_snippet)
    result = ops.read_file_raw(str(target))
    assert result.error and "too large" in result.error
    assert not result.content
    # The reply carries at most a clamped sample plus the metadata line, never 64 KiB.
    assert payloads and max(payloads) < 8192


@pytest.mark.parametrize("size", [0, 1, 63])
def test_capped_read_still_returns_files_under_the_cap(tmp_path, monkeypatch, size):
    import tools.file_operations as operations

    monkeypatch.setattr(operations, "_RAW_READ_MAX_BYTES", 64)
    target = tmp_path / "small.log"
    target.write_text("a" * size, encoding="utf-8")
    ops = ShellFileOperations(LocalEnvironment(cwd=str(tmp_path)))
    result = ops.read_file_raw(str(target))
    assert not result.error, result.error
    assert result.content == "a" * size


def test_v4a_delete_removes_an_oversized_file(tmp_path, monkeypatch):
    """Delete needs no content, so a file past the raw-read cap is still deletable."""
    import tools.file_operations as operations
    from tools.patch_parser import apply_v4a_operations, parse_v4a_patch

    monkeypatch.setattr(operations, "_RAW_READ_MAX_BYTES", 64)
    target = tmp_path / "large.log"
    target.write_text("a" * 1024, encoding="utf-8")
    ops = ShellFileOperations(LocalEnvironment(cwd=str(tmp_path)))
    operations_, err = parse_v4a_patch(f"*** Begin Patch\n*** Delete File: {target}\n*** End Patch\n")
    assert err is None
    result = apply_v4a_operations(operations_, ops)
    assert result.success, result.error
    assert not target.exists()


def test_v4a_add_does_not_overwrite_an_oversized_file(tmp_path, monkeypatch):
    """The cap error is a read failure, not "missing": an Add over a file past the cap is refused."""
    import tools.file_operations as operations
    from tools.patch_parser import apply_v4a_operations, parse_v4a_patch

    monkeypatch.setattr(operations, "_RAW_READ_MAX_BYTES", 64)
    target = tmp_path / "large.log"
    target.write_text("a" * 1024, encoding="utf-8")
    ops = ShellFileOperations(LocalEnvironment(cwd=str(tmp_path)))
    patch = f"*** Begin Patch\n*** Add File: {target}\n+new\n*** End Patch\n"
    operations_, err = parse_v4a_patch(patch)
    assert err is None
    result = apply_v4a_operations(operations_, ops)
    assert not result.success and "too large" in result.error
    assert target.read_text(encoding="utf-8") == "a" * 1024


def test_v4a_second_delete_of_an_oversized_file_is_refused(tmp_path, monkeypatch):
    """The cap exemption follows the patch's own overlay: a file this patch already deleted is gone."""
    import tools.file_operations as operations
    from tools.patch_parser import apply_v4a_operations, parse_v4a_patch

    monkeypatch.setattr(operations, "_RAW_READ_MAX_BYTES", 64)
    target = tmp_path / "large.log"
    target.write_text("a" * 1024, encoding="utf-8")
    ops = ShellFileOperations(LocalEnvironment(cwd=str(tmp_path)))
    patch = f"*** Begin Patch\n*** Delete File: {target}\n*** Delete File: {target}\n*** End Patch\n"
    operations_, err = parse_v4a_patch(patch)
    assert err is None
    result = apply_v4a_operations(operations_, ops)
    assert not result.success
    assert target.exists()


def test_v4a_delete_reads_an_oversized_file_once(tmp_path, monkeypatch):
    """Validation keeps the first read's cap verdict instead of reading the file a second time."""
    import tools.file_operations as operations
    from tools.patch_parser import _validate_operations, parse_v4a_patch

    monkeypatch.setattr(operations, "_RAW_READ_MAX_BYTES", 64)
    target = tmp_path / "large.log"
    target.write_text("a" * 1024, encoding="utf-8")
    ops = ShellFileOperations(LocalEnvironment(cwd=str(tmp_path)))
    reads = []
    real_read = ops.read_file_raw
    monkeypatch.setattr(ops, "read_file_raw", lambda path: reads.append(path) or real_read(path))
    operations_, err = parse_v4a_patch(f"*** Begin Patch\n*** Delete File: {target}\n*** End Patch\n")
    assert err is None
    assert _validate_operations(operations_, ops) == []
    assert len(reads) == 1

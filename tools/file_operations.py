#!/usr/bin/env python3
"""File operations (read, write, patch, search) over any terminal backend.

Every operation is a shell command run through the backend's ``execute()``, so one
implementation serves every environment (local, docker, ssh, modal, ...). Companions:
``file_operations_common`` (result dataclasses, text helpers), ``file_operations_lint``
(LintMixin), ``file_operations_search`` (SearchMixin).
"""

import base64
import binascii
import os
import re
import stat
import sys
import difflib
import hashlib
import json
import logging
import secrets
import unicodedata
from abc import ABC, abstractmethod
from typing import Optional, Dict
from pathlib import Path

from tools.binary_extensions import BINARY_EXTENSIONS
from agent.file_safety import get_write_denied_error
from tools.file_operations_common import (
    ExecuteResult, PatchResult, ReadResult, SearchResult, WriteResult,
    _UTF8_BOM, _detect_line_ending, _has_bom, _normalize_line_endings, _strip_bom,
    _strip_terminal_fence_leaks, normalize_read_pagination, normalize_search_pagination)
from tools.file_operations_lint import LINTERS_INPROC, LintMixin, _FAIL_CLOSED_INPROC_EXTS
from tools.file_operations_search import SearchMixin

logger = logging.getLogger(__name__)

# Controller home; SearchMixin reads it (tests monkeypatch it here).
_HOME = str(Path.home())

# --- Binary-content identification -------------------------------------------

_MAGIC_SIGNATURES: tuple = (
    # (prefix bytes, human name) — ordered, first match wins. Longest
    # prefixes for a shared first byte come first.
    (b"\x89PNG\r\n\x1a\n", "PNG image data"),
    (b"\xff\xd8\xff", "JPEG image data"),
    (b"GIF87a", "GIF image data"),
    (b"GIF89a", "GIF image data"),
    (b"RIFF", "RIFF container (WAV/AVI/WebP family)"),
    (b"%PDF-", "PDF document"),
    (b"PK\x03\x04", "ZIP archive (also docx/xlsx/jar/apk)"),
    (b"PK\x05\x06", "ZIP archive (empty)"),
    (b"\x1f\x8b", "gzip compressed data"),
    (b"BZh", "bzip2 compressed data"),
    (b"\xfd7zXZ\x00", "xz compressed data"),
    (b"7z\xbc\xaf\x27\x1c", "7-Zip archive"),
    (b"\x7fELF", "ELF executable"),
    (b"MZ", "Windows PE executable"),
    (b"\xcf\xfa\xed\xfe", "Mach-O executable (64-bit)"),
    (b"\xca\xfe\xba\xbe", "Mach-O universal binary / Java class"),
    (b"SQLite format 3\x00", "SQLite database"),
    (b"OggS", "Ogg container"),
    (b"fLaC", "FLAC audio"),
    (b"ID3", "MP3 audio (ID3 tag)"),
    (b"\x00\x00\x00", "ISO media container (MP4/MOV family)"),  # ftyp at +4
    (b"BM", "BMP image data"),
    (b"II*\x00", "TIFF image data (little-endian)"),
    (b"MM\x00*", "TIFF image data (big-endian)"),
)


def identify_binary_bytes(sample: bytes) -> str:
    """Best-effort human name for binary content from its magic bytes; never raises.
    The ISO-media entry additionally requires ``ftyp`` at offset 4 (three leading
    NULs alone are too weak a signature)."""
    for prefix, name in _MAGIC_SIGNATURES:
        if sample.startswith(prefix):
            if name.startswith("ISO media") and sample[4:8] != b"ftyp":
                continue
            return name
    return "unknown binary"


def describe_binary_file(sample: Optional[bytes], file_size: int) -> str:
    """One-line binary-file refusal naming the TYPE ("PNG image data, 4.1 KB"), so the
    model gets what-is-this in one read instead of hunting for tools it may lack."""
    kind = identify_binary_bytes(sample or b"")
    if file_size >= 1024 * 1024:
        size = f"{file_size / (1024 * 1024):.1f} MB"
    elif file_size >= 1024:
        size = f"{file_size / 1024:.1f} KB"
    else:
        size = f"{file_size} bytes"
    return f"Binary file ({kind}, {size}) — cannot display as text."


class FileOperations(ABC):
    """Abstract interface for file operations across terminal backends."""

    @abstractmethod
    def read_file(self, path: str, offset: int = 1, limit: int = 2000) -> ReadResult:
        """Read a file with pagination support."""

    @abstractmethod
    def read_file_raw(self, path: str) -> ReadResult:
        """Whole file as a plain string: no pagination, line numbers or clamping."""

    @abstractmethod
    def write_file(self, path: str, content: str, pre_content: Optional[str] = None) -> WriteResult:
        """Write content to a file, creating directories as needed."""

    @abstractmethod
    def patch_replace(self, path: str, old_string: str, new_string: str,
                      replace_all: bool = False) -> PatchResult:
        """Replace text in a file using fuzzy matching."""

    @abstractmethod
    def patch_v4a(self, patch_content: str) -> PatchResult:
        """Apply a V4A format patch."""

    @abstractmethod
    def delete_file(self, path: str) -> WriteResult:
        """Delete a file. Returns WriteResult with .error set on failure."""

    @abstractmethod
    def move_file(self, src: str, dst: str) -> WriteResult:
        """Move/rename a file. Returns WriteResult with .error set on failure."""

    @abstractmethod
    def search(self, pattern: str, path: str = ".", target: str = "content",
               file_glob: Optional[str] = None, limit: int = 50, offset: int = 0,
               output_mode: str = "content", context: int = 0,
               order: str = "discovery") -> SearchResult:
        """Search for content or files."""


# --- Shell-based implementation ----------------------------------------------

# Image extensions (subset of binary that we can return as base64)
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.ico'}

# Echoed by the compound write probe when the path does not exist. A compound
# command only reports its *last* exit status, so the missing-file signal
# travels in-band.
MISSING_SENTINEL = "__hermes_missing__"

_WRITE_SENTINEL_PREFIX = "__HERMES_WF_"

# Safe reader (``_read_regular_file_page``). Every shell-backed read runs ONE Python
# snippet in the target environment that opens with O_NONBLOCK, fstat()s the
# descriptor it just opened and reads through that same descriptor. Without an
# interpreter the read fails closed: a ``[ -f ]`` check followed by ``wc``/``head``/
# ``sed``/``cat`` re-resolves the pathname (TOCTOU) and blocks on a FIFO or device.
_SAFE_FILE_READER_PYTHON_ERROR = (
    "Safe file reader requires Python in the target environment; "
    "no insecure shell fallback was used.")
_SAFE_READER_BAD_PAYLOAD = "Safe file reader returned invalid encoded data."
_SAFE_READ_MARKER_PREFIX = "__HERMES_SR_"
_SAMPLE_BYTES = 1000          # leading bytes that drive binary detection
_THROUGH_EOF = 2**31 - 1      # ``end_line`` meaning "every line"

# Body of the safe-reader snippet; ``_read_regular_file_page`` prepends the
# parameters (``m``, ``p``, ``offset``, ``end_line``, ``max_bytes``, ``metadata_only``,
# ``clamp``, ``SAMPLE``) as Python literals. ``scan`` mirrors ``_read_file_native``
# byte for byte: 1 MiB chunks, each selected line clamped to ``clamp`` bytes before
# its newline, ``total`` counting newlines plus a final unterminated line. Output is
# a single ``<m>{json}<m>`` line; file bytes travel only base64-encoded inside it.
_SAFE_READ_SNIPPET = r'''
import base64, errno, json, os, stat
def kind(mode):
    for test, name in ((stat.S_ISDIR, 'directory'), (stat.S_ISFIFO, 'FIFO'), (stat.S_ISSOCK, 'socket'),
                       (stat.S_ISCHR, 'character device'), (stat.S_ISBLK, 'block device')):
        if test(mode):
            return name
    return 'special file'
def scan(f):
    page, total, lineno, kept, partial = [], 0, 1, 0, False
    while True:
        chunk = f.read(1 << 20)
        if not chunk:
            break
        if lineno > end_line:
            total += chunk.count(b'\n')
            partial = chunk[-1:] != b'\n'
            continue
        pos, n = 0, len(chunk)
        while pos < n:
            nl = chunk.find(b'\n', pos)
            end = n if nl < 0 else nl
            wanted = offset <= lineno <= end_line
            if wanted:
                room = end - pos if clamp is None else min(end - pos, max(clamp - kept, 0))
                if room:
                    page.append(chunk[pos:pos + room])
                kept += end - pos
            if nl < 0:
                partial = True
                break
            if wanted:
                page.append(b'\n')
            total, lineno, kept, partial, pos = total + 1, lineno + 1, 0, False, nl + 1
    return b''.join(page), total + (1 if partial else 0)
flags = os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_NOCTTY', 0) | getattr(os, 'O_BINARY', 0)
try:
    fd = os.open(p, flags)
except OSError as exc:
    if exc.errno in (errno.ENOENT, errno.ENOTDIR):
        out = {'state': 'missing'}
    elif exc.errno == errno.ENXIO:
        try:
            what = kind(os.stat(p).st_mode)  # naming only: the open was refused, nothing is read
        except OSError:
            what = 'socket or device'
        out = {'state': 'not_regular', 'kind': what}
    else:
        out = {'state': 'error', 'message': str(exc)}
else:
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            out = {'state': 'not_regular', 'kind': kind(st.st_mode)}
        elif max_bytes is not None and st.st_size > max_bytes:
            out = {'state': 'too_large', 'file_size': st.st_size}
        elif metadata_only:
            out = {'state': 'regular', 'file_size': st.st_size}
        else:
            f = os.fdopen(fd, 'rb')
            fd = None
            with f:
                sample = f.read(SAMPLE)
                f.seek(0)
                page, total = scan(f) if offset <= end_line else (b'', 0)
            out = {'state': 'regular', 'file_size': st.st_size, 'total_lines': total,
                   'sample': base64.b64encode(sample).decode('ascii'),
                   'page': base64.b64encode(page).decode('ascii')}
    except Exception as exc:
        out = {'state': 'error', 'message': str(exc)}
    finally:
        if fd is not None:
            os.close(fd)
print(m + json.dumps(out, separators=(',', ':')) + m)
'''


def _file_kind(mode: int) -> str:
    """Human name for a non-regular ``st_mode`` (same wording as the snippet's ``kind``)."""
    for test, name in ((stat.S_ISDIR, "directory"), (stat.S_ISFIFO, "FIFO"),
                       (stat.S_ISSOCK, "socket"), (stat.S_ISCHR, "character device"),
                       (stat.S_ISBLK, "block device")):
        if test(mode):
            return name
    return "special file"

def _new_sentinel(prefix: str) -> str:
    """Per-call separator line for a compound shell probe. 128 random bits make a
    collision with file content negligible; the underscores keep the token outside
    the base64 alphabet, so a sentinel leaking into a sample segment fails base64
    validation instead of decoding into bytes."""
    return f"{prefix}{secrets.token_hex(16)}__"


def _split_segments(output: str, sentinel: str) -> list[str]:
    """Split compound-probe stdout on its sentinel lines. Every producer (``wc``,
    ``base64``, ``cut``) newline-terminates or prints nothing, so the separator is
    always ``sentinel + "\n"`` on its own line; the text after the final sentinel
    is the status segment."""
    return output.split(sentinel + "\n")


class ShellFileOperations(LintMixin, SearchMixin, FileOperations):
    """File operations over any terminal backend exposing ``execute(command, cwd)``
    returning ``{"output": str, "returncode": int}``.

    cwd rule: every ``_exec`` prefers the LIVE ``env.cwd`` so a ``cd`` run via the
    terminal tool is picked up immediately; the init-time ``self.cwd`` is only a
    fallback for envs that don't track cwd (using it for every call once made
    patches "succeed" with a plausible diff while landing in the wrong directory).

    Reads need ``python3`` (or ``python``) in the target environment: the descriptor-
    level O_NONBLOCK/fstat/S_ISREG validation of ``_read_regular_file_page`` cannot be
    replaced by a pathname shell fallback, so without an interpreter reads fail closed.
    """

    def __init__(self, terminal_env, cwd: str = None):
        self.env = terminal_env
        # Never os.getcwd(): that is the HOST path, absent inside container backends.
        self.cwd = cwd or getattr(terminal_env, 'cwd', None) or \
                   getattr(getattr(terminal_env, 'config', None), 'cwd', None) or "/"
        # Ordinary executables: bool cache (hits AND misses). rg is special — it has
        # an off-PATH resolver and may be installed mid-session — so only successful
        # rg resolutions are cached (see SearchMixin._resolve_command).
        self._command_cache: Dict[str, bool] = {}
        self._rg_resolution_cache: Dict[str, str] = {}
        self._rg_modified_capability: Dict[str, Optional[str]] = {}

    def _exec(self, command: str, cwd: str = None, timeout: int = None,
              stdin_data: str = None) -> ExecuteResult:
        """Run ``command`` on the backend. cwd: explicit arg → live ``env.cwd`` →
        init-time ``self.cwd``. ``stdin_data`` is piped (bypasses ARG_MAX)."""
        kwargs = {}
        if timeout:
            kwargs['timeout'] = timeout
        if stdin_data is not None:
            kwargs['stdin_data'] = stdin_data
        effective_cwd = cwd or getattr(self.env, 'cwd', None) or self.cwd
        result = self.env.execute(command, cwd=effective_cwd, **kwargs)
        exit_code = result.get("returncode", 0)
        # A stdin write failure with a clean child exit is still a failure: the
        # child never received the input.
        if result.get("stdin_error") and exit_code == 0:
            exit_code = 1
        return ExecuteResult(stdout=result.get("output", ""), exit_code=exit_code)

    def _has_command(self, cmd: str) -> bool:
        """Check if a command exists in the environment (cached); rg goes through
        the resolver so a mid-session install becomes visible."""
        if cmd == "rg":
            return self._resolve_command(cmd) is not None
        if cmd not in self._command_cache:
            result = self._exec(f"command -v {cmd} >/dev/null 2>&1 && echo 'yes'")
            self._command_cache[cmd] = result.stdout.strip() == 'yes'
        return self._command_cache[cmd]

    def _cat(self, path: str) -> ExecuteResult:
        """``cat`` the file with stderr silenced (missing file → non-zero exit)."""
        return self._exec(f"cat {self._escape_shell_arg(path)} 2>/dev/null")

    def _head(self, path: str, nbytes: int) -> ExecuteResult:
        return self._exec(f"head -c {nbytes} {self._escape_shell_arg(path)} 2>/dev/null")

    def _run_python_snippet(self, snippet: str) -> ExecuteResult:
        """Run ``snippet`` via the backend's ``python3``, retrying with ``python`` when
        the ``python3`` name never reached an interpreter (Windows / older systems)."""
        result = self._exec(f"python3 -c {self._escape_shell_arg(snippet)}")
        if result.exit_code != 0 and self._interpreter_missing(result):
            result = self._exec(f"python -c {self._escape_shell_arg(snippet)}")
        return result

    @staticmethod
    def _interpreter_missing(result: ExecuteResult) -> bool:
        """Whether a ``python* -c`` attempt never ran an interpreter: the shell's 127,
        its wording (``command not found`` / ``not found`` / Windows' ``not recognized``)
        or the interpreter name echoed back in the complaint."""
        text = (result.stdout or "").lower()
        return (result.exit_code == 127 or "not found" in text
                or "not recognized" in text or "python3" in text)

    @staticmethod
    def _python_path(path: str) -> str:
        """``path`` as the backend's Python (a native binary) sees it: on Windows the
        Git Bash ``/c/Users/x`` form becomes ``C:/Users/x``; identical elsewhere."""
        from tools.environments.local import _IS_WINDOWS, _msys_to_windows_path
        return _msys_to_windows_path(path).replace("\\", "/") if _IS_WINDOWS and path else path

    @staticmethod
    def _decode_base64_sample(text: str) -> Optional[bytes]:
        """Decode one base64 segment of the compound write probe (``head -c 3 | base64``).
        Whitespace-joins the text first (``base64`` wraps at 76 columns); anything that
        is not clean base64 fails validation → None (no ``base64`` binary)."""
        encoded = "".join(_strip_terminal_fence_leaks(text).split())
        if not encoded:
            return b""
        if not re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", encoded):
            return None
        try:
            return base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError):
            return None

    @staticmethod
    def _is_likely_binary_bytes(sample: bytes) -> bool:
        """Byte-layer binary detection: text iff valid UTF-8, allowing one incomplete
        multibyte sequence at the very end (artifact of the byte-boundary cut).
        NUL bytes or mid-stream invalid UTF-8 stay read-only so a read→edit→write
        round-trip never rewrites undecodable bytes as U+FFFD; a file that
        legitimately CONTAINS U+FFFD is valid UTF-8 and reads as text.

        See #80308.
        """
        if not sample:
            return False
        if b"\x00" in sample:
            return True
        try:
            sample.decode("utf-8")
            return False
        except UnicodeDecodeError as exc:
            # UTF-8 sequences are at most 4 bytes: an error starting in the
            # last 3 bytes with a clean prefix is a boundary cut, not binary.
            if exc.start >= len(sample) - 3:
                try:
                    sample[: exc.start].decode("utf-8")
                    return False
                except UnicodeDecodeError:
                    pass
            return True

    def _is_likely_binary(self, path: str, content_sample: str = None) -> bool:
        """Legacy text-layer binary check: extension, else >30% non-printable chars."""
        if os.path.splitext(path)[1].lower() in BINARY_EXTENSIONS:
            return True
        if content_sample:
            # Undecodable bytes arrive as U+FFFD ("printable", so the ratio misses
            # them); treat as binary so a round-trip can't write back mojibake.
            if "\ufffd" in content_sample[:1000]:
                return True
            non_printable = sum(1 for c in content_sample[:1000] if ord(c) < 32 and c not in '\n\r\t')
            return non_printable / min(len(content_sample), 1000) > 0.30
        return False

    def _is_image(self, path: str) -> bool:
        return os.path.splitext(path)[1].lower() in IMAGE_EXTENSIONS

    def _add_line_numbers(self, content: str, start_line: int = 1) -> str:
        """Prefix each line with a compact ``<n>|`` gutter, clamping long lines. Not
        fixed-width: padding cost ~16% more tokens per line for no accuracy gain in
        A/B, while dropping numbers regressed line-referencing."""
        from tools.tool_output_limits import get_max_line_length
        max_line_length = get_max_line_length()
        return '\n'.join(
            f"{i}|{line if len(line) <= max_line_length else line[:max_line_length] + '... [truncated]'}"
            for i, line in enumerate(content.split('\n'), start=start_line))

    def _expand_path(self, path: str) -> str:
        """Expand ``~`` / ``~user`` via the backend's shell (its HOME, not the
        host's). Must run BEFORE shell escaping — ~ doesn't expand in quotes."""
        if not path or not path.startswith('~'):
            return path
        result = self._exec("echo $HOME")
        if result.exit_code == 0 and result.stdout.strip():
            home = result.stdout.strip()
            if path == '~':
                return home
            if path.startswith('~/'):
                return home + path[1:]
            # ~username: validate and expand ONLY that token, so neither "~; rm -rf /"
            # nor "~user/$(malicious)" reaches the shell.
            rest = path[1:]
            slash_idx = rest.find('/')
            username = rest[:slash_idx] if slash_idx >= 0 else rest
            if username and re.fullmatch(r'[a-zA-Z0-9._-]+', username):
                expand_result = self._exec(f"echo ~{username}")
                if expand_result.exit_code == 0 and expand_result.stdout.strip():
                    return expand_result.stdout.strip() + path[1 + len(username):]
        return path

    def _escape_shell_arg(self, arg: str) -> str:
        """Single-quote ``arg`` for the shell. On Windows, native drive paths and
        mixed MSYS leftovers are first rewritten to the Git Bash ``/c/Users/x``
        form via the env-layer ``_bash_safe_path`` (bash eats backslashes; MSYS
        mangles drive paths), so shell file ops and the terminal ``cd`` agree."""
        from tools.environments.local import _bash_safe_path
        return "'" + _bash_safe_path(arg).replace("'", "'\"'\"'") + "'"

    def _escape_native_tool_arg(self, arg: str) -> str:
        """Quote a path for a NATIVE Windows binary (rg, node, git ...): those don't
        understand the MSYS ``/c/...`` form and Hermes disables MSYS argument
        conversion, so nothing translates it back (→ ``os error 3``). ``C:/Users/x``
        is accepted by every layer. Identical to ``_escape_shell_arg`` off Windows."""
        from tools.environments.local import _IS_WINDOWS, _msys_to_windows_path
        if _IS_WINDOWS and arg:
            arg = _msys_to_windows_path(arg).replace("\\", "/")
        return "'" + arg.replace("'", "'\"'\"'") + "'"

    def _atomic_write(self, path: str, content: str) -> "ExecuteResult":
        """Write ``content`` atomically: stdin → temp file in the SAME directory →
        ``mv -f`` (same-FS rename; cross-device ``mv`` is copy+unlink, NOT atomic).
        ``mkdir -p`` folded in. Exit 0 = swap happened; non-zero = original intact.

        Symlink targets are resolved first (replacing the link would orphan the
        target) and the temp dir recomputed from the RESOLVED target. Existing
        target: mode copied via ``stat`` (GNU ``-c%a`` / BSD ``-f%Lp``) + ``chmod``
        (``chmod --reference`` is GNU-only). New target: ``chmod "=rw"`` AFTER cat
        gives umask-default perms instead of mktemp's 0600 — not ``$(umask)``
        arithmetic (zsh parses leading-zero constants as decimal), quoted so zsh
        doesn't =word-expand. ``trap ... EXIT`` removes the temp on every failure.
        """
        q_path = self._escape_shell_arg(path)
        q_parent = self._escape_shell_arg(os.path.dirname(path) or ".")
        tmpl = self._escape_shell_arg(".hermes-tmp.XXXXXX")
        script = (
            "set -e; "
            # One shell script, fully quoted. Notes: - `mkdir -p "$d"` is folded in here so the parent
            # directory is created in the same subprocess that writes the temp file — saves one entire
            # subprocess spawn vs. a separate mkdir call. - `mktemp` lands the temp in the target's own dir
            # (-p) so `mv` is same-FS atomic; we fall back to a PID-stamped name if the backend lacks mktemp
            # (rare; busybox/macOS/Linux all ship it). - `chmod --reference` is GNU-only, so we read the
            # octal mode with `stat` (GNU `-c%a` or BSD `-f%Lp`) and `chmod` it explicitly; silent
            # best-effort — a perms-copy failure must not abort the write (the file then lands at mktemp's
            # 0600, same as pre-fix). - brand-new targets get `chmod "=rw"` — the POSIX who-less symbolic
            # form, which sets rw minus the process umask (e.g. 0644 under umask 022) instead of mktemp's
            # hardcoded 0600 (#70856). Deliberately NOT shell arithmetic on `$(umask)`: zsh (reachable via
            # _find_bash's $SHELL fallback) parses leading-zero constants as decimal and silently computes a
            # garbage mode, while `chmod "=rw"` is spec-identical in bash/dash/ash/zsh and degrades to 0600
            # (pre-fix behavior) if an exotic chmod rejects it. - `trap ... EXIT` guarantees the temp is
            # removed on every error path (cat failure, mv failure, signal) but NOT after a successful mv
            # (the temp no longer exists by then). - we `cat >` the temp, then `mv -f` it over the target.
            f"d={q_parent}; t={q_path}; "
            'if [ -L "$t" ]; then '
            'rt="$(readlink -f "$t" 2>/dev/null || realpath "$t" 2>/dev/null || true)"; '
            '[ -n "$rt" ] && { t="$rt"; d="$(dirname "$t")"; }; '
            "fi; "
            'mkdir -p "$d"; '
            'tmp="$(mktemp -p "$d" ' + tmpl + ' 2>/dev/null '
            '|| mktemp "$d/.hermes-tmp.$$.XXXXXX" 2>/dev/null '
            '|| { tmp="$d/.hermes-tmp.$$"; : > "$tmp" && echo "$tmp"; })"; '
            '[ -n "$tmp" ] || { echo "atomic write: could not create temp file" >&2; exit 1; }; '
            "trap 'rm -f \\\"$tmp\\\"' EXIT; "
            'if [ -e "$t" ]; then '
            'm="$(stat -c%a "$t" 2>/dev/null || stat -f%Lp "$t" 2>/dev/null || true)"; '
            '[ -n "$m" ] && chmod "$m" "$tmp" 2>/dev/null || true; '
            "fi; "
            'cat > "$tmp"; '
            # new file: umask-default perms instead of mktemp's 0600 (#70856). Runs AFTER cat so a
            # write-masking umask can't EACCES the stream; quoted "=rw" so zsh doesn't =word-expand it.
            'if [ ! -e "$t" ]; then chmod "=rw" "$tmp" 2>/dev/null || true; fi; '
            'mv -f "$tmp" "$t"; '
            "trap - EXIT")
        return self._exec(script, stdin_data=content)

    def _file_has_bom(self, path: str, pre_content: Optional[str] = None) -> bool:
        """Whether the on-disk file starts with a UTF-8 BOM. ALWAYS probes disk:
        ``pre_content`` usually comes from ``read_file_raw``, which strips BOMs, so
        trusting it would silently drop the marker on rewrite. Missing → False."""
        head_result = self._head(path, 3)
        return head_result.exit_code == 0 and _has_bom(head_result.stdout)

    def _unified_diff(self, old_content: str, new_content: str, filename: str) -> str:
        return ''.join(difflib.unified_diff(
            old_content.splitlines(keepends=True), new_content.splitlines(keepends=True),
            fromfile=f"a/{filename}", tofile=f"b/{filename}"))

    # --- READ ---------------------------------------------------------------

    @staticmethod
    def _not_regular_error(path: str, kind: Optional[str] = None) -> ReadResult:
        """Error for a path that exists but is not a regular file (``kind`` names what
        it is when known). Reading it could block indefinitely, so nothing did."""
        what = f"it is a {kind}" if kind else "directory, FIFO, socket, or device"
        return ReadResult(error=(
            f"Cannot read '{path}': not a regular file ({what}). "
            "Reading it could block indefinitely."))

    def _env_unavailable_error(self, path: str) -> ReadResult:
        return ReadResult(error=(f"Terminal environment unavailable: could not stat {path} "
                                 "(the sandbox may still be starting or was removed). Retry shortly."))

    def _read_regular_file_page(self, path: str, offset: int, end_line: int, *,
                                max_bytes: Optional[int] = None, metadata_only: bool = False,
                                line_clamp_bytes: Optional[int] = None) -> dict:
        """Read lines ``offset..end_line`` of ``path`` through ONE descriptor in the
        target environment. The backend may be a container or a remote host, so no
        host-side ``os.stat`` can protect it: the snippet opens with ``O_NONBLOCK`` (a
        writer-less FIFO or a device cannot stall the open), ``fstat``s the descriptor
        it just opened, accepts only ``S_ISREG`` and reads through that same descriptor;
        no pathname is re-resolved between the check and the read.

        States: ``{"state": "regular", "file_size", "total_lines", "sample", "page"}``
        (``sample``/``page`` base64; ``page`` holds the selected lines exactly as stored,
        each clamped to ``line_clamp_bytes`` before its newline; ``end_line < offset``
        requests no page and skips the line scan), ``regular`` with only ``file_size``
        when ``metadata_only``, ``too_large`` (+``file_size``, before any byte is
        exported) when the file exceeds ``max_bytes``, ``not_regular`` (+``kind``),
        ``missing``, ``error`` (+``message``) and, when no reply came back at all,
        ``no_python`` or ``env_unavailable``.

        Wire protocol: one ``<marker>{json}<marker>`` line with a per-call random
        marker. Anything else the backend prints (banners, fence leaks, an echoed
        command) is ignored, and file bytes only travel base64-encoded inside the JSON,
        so no raw content ever reaches the shell or the parser."""
        marker = _new_sentinel(_SAFE_READ_MARKER_PREFIX)
        snippet = (
            f"m = {marker!r}\n"
            f"p = {self._python_path(path)!r}\n"
            f"offset = {int(offset)}\n"
            f"end_line = {int(end_line)}\n"
            f"max_bytes = {None if max_bytes is None else int(max_bytes)!r}\n"
            f"metadata_only = {bool(metadata_only)!r}\n"
            f"clamp = {None if line_clamp_bytes is None else int(line_clamp_bytes)!r}\n"
            f"SAMPLE = {_SAMPLE_BYTES}\n"
        ) + _SAFE_READ_SNIPPET
        result = self._run_python_snippet(snippet)
        stdout = _strip_terminal_fence_leaks(result.stdout or "")
        for match in re.finditer(re.escape(marker) + r"(\{.*?\})" + re.escape(marker), stdout):
            try:
                payload = json.loads(match.group(1))
            except ValueError:
                continue
            if isinstance(payload, dict) and isinstance(payload.get("state"), str):
                return payload
        if self._interpreter_missing(result):
            return {"state": "no_python"}
        return {"state": "env_unavailable"}

    def _page_for_text_read(self, path: str, offset: int, end_line: int,
                            line_clamp_bytes: Optional[int] = None) -> tuple[dict, bool, bool]:
        """``(page, is_image, ext_binary)`` for a text read. Images and known-binary
        extensions never inline content: the descriptor is still validated, but only
        metadata (images) or the magic-byte sample (binaries) crosses the transport."""
        is_image = self._is_image(path)
        ext_binary = os.path.splitext(path)[1].lower() in BINARY_EXTENSIONS
        if is_image:
            page = self._read_regular_file_page(path, 1, 0, metadata_only=True)
        elif ext_binary:
            page = self._read_regular_file_page(path, 1, 0)  # sample only, no line scan
        else:
            page = self._read_regular_file_page(
                path, offset, end_line, line_clamp_bytes=line_clamp_bytes)
        return page, is_image, ext_binary

    def _page_error(self, path: str, page: dict) -> Optional[ReadResult]:
        """ReadResult for a safe-reader state no reader can proceed from (interpreter
        missing, environment unavailable, non-regular file, OS error); None for
        ``regular``/``missing``/``too_large``, which each reader handles itself."""
        state = page.get("state")
        if state == "no_python":
            return ReadResult(error=_SAFE_FILE_READER_PYTHON_ERROR)
        if state == "env_unavailable":
            return self._env_unavailable_error(path)
        if state == "not_regular":
            return self._not_regular_error(path, page.get("kind"))
        if state == "error":
            return ReadResult(error=f"Failed to read file: {page.get('message', 'unknown error')}")
        return None

    @staticmethod
    def _page_int(page: dict, key: str) -> int:
        value = page.get(key, 0)
        return value if isinstance(value, int) and not isinstance(value, bool) else 0

    @staticmethod
    def _page_bytes(page: dict, key: str) -> Optional[bytes]:
        """Decode one base64 field of a safe-reader page; None when malformed."""
        value = page.get(key, "")
        if not isinstance(value, str):
            return None
        try:
            return base64.b64decode(value, validate=True)
        except (ValueError, binascii.Error):
            return None

    # UTF-16 rescue: trust a BOM first, then zero-byte PARITY (not density, so
    # mixed Latin/CJK still detects): zeros at odd indices → UTF-16 LE, at even
    # → BE; both parities or a single zero → real binary. Legacy 8-bit
    # encodings (GBK, Big5) are never guessed — a wrong silent guess is worse
    # than a clear refusal.
    # UTF-16 rescue constants (ported from MoonshotAI/kimi-code#2647, detection derived from VS Code's
    # encoding sniffer): sample the leading bytes; trust a BOM first, then a zero-byte parity heuristic —
    # zeros clustering at odd indices mean UTF-16 LE (`0xAA 0x00`), at even indices UTF-16 BE (`0x00 0xAA`).
    _UTF16_MAX_BYTES = 10 * 1024 * 1024
    _UTF16_SAMPLE_BYTES = 512

    def _try_read_utf16(self, path: str, offset: int, limit: int,
                        file_size: int) -> "Optional[ReadResult]":
        """Read ``path`` as UTF-16 transcoded to UTF-8, or None (caller falls back
        to the binary-file error). Skips known-binary extensions and files over
        10 MiB. ``path`` must already be expanded. Same descriptor discipline as
        ``_read_regular_file_page``: open O_NONBLOCK, fstat, S_ISREG, then read that fd."""
        if os.path.splitext(path)[1].lower() in BINARY_EXTENSIONS or file_size > self._UTF16_MAX_BYTES:
            return None
        snippet = (
            "import sys, json, os, stat\n"
            f"p = {self._python_path(path)!r}\n"
            f"offset = {int(offset)}\n"
            f"limit = {int(limit)}\n"
            f"MAX = {self._UTF16_MAX_BYTES}\n"
            f"SAMPLE = {self._UTF16_SAMPLE_BYTES}\n"
            "try:\n"
            "    fd = os.open(p, os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0)"
            " | getattr(os, 'O_NOCTTY', 0) | getattr(os, 'O_BINARY', 0))\n"
            "    with os.fdopen(fd, 'rb') as f:\n"
            "        st = os.fstat(f.fileno())\n"
            "        if not stat.S_ISREG(st.st_mode) or st.st_size > MAX:\n"
            "            print('HERMES_UTF16:NO'); sys.exit(0)\n"
            "        data = f.read()\n"
            "    sample = data[:SAMPLE]\n"
            "    enc = None\n"
            "    if sample[:2] == b'\\xfe\\xff':\n"
            "        enc = 'utf-16-be'\n"
            "    elif sample[:2] == b'\\xff\\xfe':\n"
            "        enc = 'utf-16-le'\n"
            "    else:\n"
            "        odd = sum(1 for i in range(1, len(sample), 2) if sample[i] == 0)\n"
            "        even = sum(1 for i in range(0, len(sample), 2) if sample[i] == 0)\n"
            "        if even == 0 and odd >= 2:\n"
            "            enc = 'utf-16-le'\n"
            "        elif odd == 0 and even >= 2:\n"
            "            enc = 'utf-16-be'\n"
            "    if enc is None:\n"
            "        print('HERMES_UTF16:NO'); sys.exit(0)\n"
            "    text = data.decode(enc, 'replace')\n"
            "    if text[:1] == '\\ufeff':\n"
            "        text = text[1:]\n"
            "    text = text.replace('\\r\\n', '\\n')\n"
            "    lines = text.split('\\n')\n"
            "    total = len(lines)\n"
            "    sel = lines[offset - 1: offset - 1 + limit]\n"
            "    out = {'total_lines': total, 'encoding': enc,\n"
            "           'content': '\\n'.join(sel)}\n"
            "    print('HERMES_UTF16:OK')\n"
            "    print(json.dumps(out, ensure_ascii=True))\n"
            "except Exception:\n"
            "    print('HERMES_UTF16:NO'); sys.exit(0)\n")
        result = self._run_python_snippet(snippet)
        stdout = _strip_terminal_fence_leaks(result.stdout or "")
        marker = stdout.find("HERMES_UTF16:OK")
        if result.exit_code != 0 or marker < 0:
            return None
        payload = stdout[marker + len("HERMES_UTF16:OK"):].strip()
        try:
            data = json.loads(payload.split("\n", 1)[0] if "\n" in payload else payload)
            content = data["content"]
            total_lines = int(data["total_lines"])
            encoding = str(data.get("encoding", "utf-16"))
        except (ValueError, KeyError, TypeError):
            return None
        end_line = offset + limit - 1
        truncated = total_lines > end_line
        hint_parts = [f"Transcoded from {encoding.upper()} to UTF-8 for display. "
                      "Text edits via patch/write_file would re-encode as UTF-8."]
        if truncated:
            hint_parts.append(
                f"Use offset={end_line + 1} to continue reading "
                f"(showing {offset}-{end_line} of {total_lines} lines)")
        return ReadResult(
            content=self._add_line_numbers(content, offset), total_lines=total_lines,
            file_size=file_size, truncated=truncated, hint=" ".join(hint_parts))

    def read_file(self, path: str, offset: int = 1, limit: int = 2000) -> ReadResult:
        """Read a file with pagination, binary detection, and line numbers.

        ``offset`` is 1-indexed; ``limit`` is clamped by ``normalize_read_pagination``.
        On a local POSIX environment the read never touches the shell
        (``_read_file_native``); everywhere else one Python snippet in the target
        environment answers every question the read needs through a single validated
        descriptor (``_read_file_shell``). Both paths produce identical results.
        """
        path = self._expand_path(path)  # before shell escaping: ~ doesn't expand in quotes
        offset, limit = normalize_read_pagination(offset, limit)
        if self._native_read_enabled():
            return self._read_file_native(path, offset, limit)
        return self._read_file_shell(path, offset, limit)

    def _read_file_shell(self, path: str, offset: int, limit: int) -> ReadResult:
        """``read_file`` over the backend's Python (``path`` expanded, pagination
        normalized): one ``_read_regular_file_page`` round-trip, then the shared
        binary / UTF-16 / assembly steps."""
        from tools.tool_output_limits import get_max_line_length
        end_line = offset + limit - 1
        page, is_image, ext_binary = self._page_for_text_read(
            path, offset, end_line, line_clamp_bytes=4 * get_max_line_length() + 1)
        failure = self._page_error(path, page)
        if failure is not None:
            return failure
        if page["state"] == "missing":
            return self._read_file_missing(path, offset, limit)
        file_size = self._page_int(page, "file_size")
        if is_image:
            return self._image_redirect_result(file_size)
        sample_bytes = self._page_bytes(page, "sample")
        page_bytes = self._page_bytes(page, "page")
        if sample_bytes is None or page_bytes is None:
            return ReadResult(error=_SAFE_READER_BAD_PAYLOAD)
        if ext_binary or self._is_likely_binary_bytes(sample_bytes):
            return self._read_binary_file(path, offset, limit, file_size, sample_bytes)
        # The page holds the lines exactly as stored (no ``cut`` newline artifact),
        # so there is nothing for ``file_ends_with_newline`` to correct.
        read_output = _strip_terminal_fence_leaks(page_bytes.decode("utf-8", errors="replace"))
        return self._assemble_read_result(
            read_output, offset=offset, end_line=end_line,
            total_lines=self._page_int(page, "total_lines"), file_size=file_size,
            file_ends_with_newline=None)

    def _native_read_enabled(self) -> bool:
        """Whether ``read_file`` and ``search_files`` may bypass the shell: only POSIX + ``LocalEnvironment``
        (file is on this host, path already native; Windows keeps the shell path since
        file_operations holds Git-Bash-style paths there). ``HERMES_NATIVE_FILE_READ=0``
        turns the fast path off."""
        flag = os.environ.get("HERMES_NATIVE_FILE_READ", "1").strip().lower()
        if flag in ("0", "false", "no", "off"):
            return False
        # Same "is this env the local host" test the LSP path uses; isinstance is
        # microseconds and self.env is never rebound, so nothing to memoize.
        return sys.platform != "win32" and self._lsp_local_only()

    def _read_file_native(self, path: str, offset: int, limit: int) -> ReadResult:
        """``read_file`` without a shell — same contract as the shell path, byte for
        byte. ``os.stat`` is the ``[ -f ]`` guard (a stat, never an open, so FIFOs and
        devices are refused before anything touches them); the first 1000 bytes drive
        the byte-layer binary check; the page is produced exactly as
        ``sed -n 'a,bp' | cut -b1-N`` prints it (each line clamped to N bytes and
        newline-terminated) then decoded with errors="replace" like the transport.
        One chunked pass counts lines and collects the page, so neither the file nor
        a pathological line is ever held whole. ``path`` is already expanded; any
        unexpected OSError hands over to the shell path."""
        import stat as _stat

        full = path if os.path.isabs(path) else os.path.join(
            getattr(self.env, "cwd", None) or self.cwd, path)
        flags = (os.O_RDONLY | getattr(os, "O_NONBLOCK", 0)
                 | getattr(os, "O_NOCTTY", 0) | getattr(os, "O_BINARY", 0))
        try:
            fd = os.open(full, flags)
        except (FileNotFoundError, NotADirectoryError):
            return self._read_file_missing(path, offset, limit)
        except OSError:
            return self._read_file_shell(path, offset, limit)

        try:
            # Validate the exact descriptor that will be read. A separate stat(path)
            # followed by open(path) lets an attacker swap a regular file for a FIFO
            # or device in-between; O_NONBLOCK keeps even that open from stalling.
            st = os.fstat(fd)
            if not _stat.S_ISREG(st.st_mode):
                return self._not_regular_error(path, _file_kind(st.st_mode))
            file_size = st.st_size
            if self._is_image(path):
                return self._image_redirect_result(file_size)

            from tools.tool_output_limits import get_max_line_length
            clamp = 4 * get_max_line_length() + 1
            end_line = offset + limit - 1

            page: list[bytes] = []
            total_lines = 0
            lineno = 1              # the line currently being scanned
            kept = bytearray()      # first ``clamp`` bytes of that line
            have_partial = False    # that line has bytes but no newline yet
            last_byte = b""
            with os.fdopen(fd, "rb") as fh:
                fd = None  # fh owns the descriptor from this point.
                sample = fh.read(1000)
                ext_binary = os.path.splitext(path)[1].lower() in BINARY_EXTENSIONS
                if ext_binary or self._is_likely_binary_bytes(sample):
                    return self._read_binary_file(path, offset, limit, file_size, sample)
                fh.seek(0)
                while True:
                    chunk = fh.read(1 << 20)
                    if not chunk:
                        break
                    last_byte = chunk[-1:]
                    if lineno > end_line:
                        # Past the window: only the line count and trailing byte
                        # are needed, so let memchr do it instead of per-line work.
                        total_lines += chunk.count(b"\n")
                        have_partial = chunk[-1:] != b"\n"
                        continue
                    pos, n = 0, len(chunk)
                    while pos < n:
                        nl = chunk.find(b"\n", pos)
                        in_page = offset <= lineno <= end_line
                        if nl < 0:
                            if in_page and len(kept) < clamp:
                                kept += chunk[pos:pos + (clamp - len(kept))]
                            have_partial = True
                            break
                        if in_page:
                            if len(kept) < clamp:
                                kept += chunk[pos:min(nl, pos + (clamp - len(kept)))]
                            page.append(bytes(kept) + b"\n")
                        kept = bytearray()
                        have_partial = False
                        total_lines += 1
                        lineno += 1
                        pos = nl + 1
        except OSError:
            return self._read_file_shell(path, offset, limit)
        finally:
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass
        if have_partial:
            # ``wc -l`` counts separators, not a final unterminated line. Keep
            # pagination/hints aligned with what `sed` exposes to the caller.
            total_lines += 1
            if offset <= lineno <= end_line:
                # ``sed`` prints a final line that lacks a newline; ``cut`` adds one.
                page.append(bytes(kept) + b"\n")

        read_output = _strip_terminal_fence_leaks(b"".join(page).decode("utf-8", errors="replace"))
        return self._assemble_read_result(
            read_output, offset=offset, end_line=end_line, total_lines=total_lines,
            file_size=file_size,
            file_ends_with_newline=(last_byte == b"\n") if file_size else None)

    @staticmethod
    def _image_redirect_result(file_size: int) -> ReadResult:
        return ReadResult(
            is_image=True, is_binary=True, file_size=file_size,
            hint=(
                "Image file detected. Automatically redirected to vision_analyze tool. "
                "Use vision_analyze with this file path to inspect the image contents."))

    def _read_file_missing(self, path: str, offset: int, limit: int) -> ReadResult:
        """Not-found recovery shared by every read path. Unicode-equivalent spellings
        (NFC/NFD, confusable spaces/quotes) render identically, so the model can never
        discover the byte mismatch by retyping — retrying is the tool's job. No
        equivalent spelling → suggest similar files."""
        variant = self._unicode_variant_match(path)
        if variant is not None:
            result = self.read_file(variant, offset=offset, limit=limit)
            note = (
                f"Note: '{path}' not found byte-for-byte; resolved to "
                f"the unicode-equivalent file '{variant}' (invisible "
                "encoding difference: NFC/NFD or special space/quote "
                "characters).")
            result.hint = f"{note} {result.hint}" if result.hint else note
            return result
        return self._suggest_similar_files(path)

    def _read_binary_file(self, path: str, offset: int, limit: int,
                          file_size: int, sample_bytes: Optional[bytes]) -> ReadResult:
        """Binary branch shared by every read path: UTF-16 text (Notepad, PowerShell
        ``>``) trips the binary guard; transcode it, else refuse with the type name.

        UTF-16 rescue (ported from MoonshotAI/kimi-code#2647): the terminal env decodes stdout as UTF-8 with
        errors="replace", so a UTF-16 text file (Windows Notepad .txt, PowerShell `>` redirects) arrives
        mangled with U+FFFD and trips the binary guard. Probe the raw bytes via the backend's Python and
        transcode to UTF-8 when a BOM or the zero-byte parity heuristic identifies UTF-16.
        """
        utf16_result = self._try_read_utf16(path, offset, limit, file_size)
        if utf16_result is not None:
            return utf16_result
        return ReadResult(
            is_binary=True, file_size=file_size,
            error=describe_binary_file(sample_bytes, file_size))

    def _assemble_read_result(self, read_output: str, *, offset: int, end_line: int,
                              total_lines: int, file_size: int,
                              file_ends_with_newline: Optional[bool]) -> ReadResult:
        """Turn a raw ``sed | cut`` page into the final ``ReadResult``. Shared by every
        read path so the BOM strip, pagination hint, ``cut`` newline-artifact fix and
        the ambiguous-silence guards never drift apart. ``file_ends_with_newline`` is
        None when the caller could not tell (artifact left alone, as before)."""
        if offset == 1:  # only the first chunk can carry a BOM (byte 0)
            read_output, _ = _strip_bom(read_output)
        truncated = total_lines > end_line
        hint = None
        if truncated:
            hint = f"Use offset={end_line + 1} to continue reading (showing {offset}-{end_line} of {total_lines} lines)"

        # ``cut`` always newline-terminates, so a file without a trailing newline
        # would grow a phantom empty last line; strip it when the last byte says so.
        if not truncated and read_output.endswith('\n') and file_ends_with_newline is False:
            read_output = read_output[:-1]

        # Empty content is indistinguishable from a broken tool: name the dead end.
        if file_size == 0:
            return ReadResult(content="", total_lines=0, file_size=0, hint="File is empty (0 bytes).")
        if offset > total_lines > 0:
            return ReadResult(
                content="", total_lines=total_lines, file_size=file_size,
                hint=(
                    f"Note: offset {offset} is beyond the end of the file "
                    f"({total_lines} lines total). Retry with offset <= "
                    f"{total_lines}."))
        return ReadResult(
            content=self._add_line_numbers(read_output, offset), total_lines=total_lines,
            file_size=file_size, truncated=truncated, hint=hint)

    # Confusable characters seen in real filenames, collapsed after NFC.
    _CONFUSABLES = (
        ("\u202f", " "),  # narrow no-break space (macOS screenshots)
        ("\u00a0", " "),  # no-break space
        ("\u2019", "'"),  # right single quotation mark (Finder)
        ("\u2018", "'"),  # left single quotation mark
    )

    def _unicode_variant_match(self, path: str) -> Optional[str]:
        """On-disk spelling of a file whose name is unicode-equivalent to ``path``
        (NFC/NFD, confusable spaces/quotes). Returns the entry only when EXACTLY one
        matches — several candidates = homoglyph collision, guessing would read the
        wrong file."""
        dir_path = os.path.dirname(path) or "."
        filename = os.path.basename(path)
        if not filename:
            return None

        def _canon(name: str) -> str:
            out = unicodedata.normalize("NFC", name)
            for src, dst in self._CONFUSABLES:
                out = out.replace(src, dst)
            return out

        target = _canon(filename)
        ls_result = self._exec(f"ls -1 {self._escape_shell_arg(dir_path)} 2>/dev/null")
        if ls_result.exit_code != 0 or not ls_result.stdout.strip():
            return None
        candidates = [
            entry for entry in _strip_terminal_fence_leaks(ls_result.stdout).splitlines()
            if entry and entry != filename and _canon(entry) == target]
        if len(candidates) == 1:
            return os.path.join(dir_path, candidates[0]) if dir_path != "." or "/" in path else candidates[0]
        return None

    def _suggest_similar_files(self, path: str) -> ReadResult:
        """"File not found" result listing up to 5 similar names from the same directory."""
        dir_path = os.path.dirname(path) or "."
        filename = os.path.basename(path)
        basename_no_ext = os.path.splitext(filename)[0].lower()
        ext = os.path.splitext(filename)[1].lower()
        lower_name = filename.lower()
        ls_result = self._exec(f"ls -1 {self._escape_shell_arg(dir_path)} 2>/dev/null | head -50")
        scored: list = []  # (score, filepath) — higher is better
        if ls_result.exit_code == 0 and ls_result.stdout.strip():
            for f in ls_result.stdout.strip().split('\n'):
                if not f:
                    continue
                lf = f.lower()
                score = 0
                if lf == lower_name:
                    score = 100
                elif os.path.splitext(f)[0].lower() == basename_no_ext:  # config.yml vs config.yaml
                    score = 90
                elif lf.startswith(lower_name) or lower_name.startswith(lf):
                    score = 70
                elif lower_name in lf:
                    score = 60
                elif lf in lower_name and len(lf) > 2:
                    score = 40
                elif ext and os.path.splitext(f)[1].lower() == ext:
                    common = set(lower_name) & set(lf)
                    if len(common) >= max(len(lower_name), len(lf)) * 0.4:
                        score = 30
                # Near-miss spelling (AGENT.md -> AGENTS.md) the substring checks miss.
                if score == 0 and difflib.SequenceMatcher(None, lower_name, lf).ratio() >= 0.8:
                    score = 50
                if score > 0:
                    scored.append((score, os.path.join(dir_path, f)))
        scored.sort(key=lambda x: -x[0])
        return ReadResult(error=f"File not found: {path}", similar_files=[fp for _, fp in scored[:5]])

    def read_file_raw(self, path: str) -> ReadResult:
        """Whole file as a plain string (no pagination/line numbers/clamping) through
        the same validated descriptor as ``read_file``; patch/V4A rely on it."""
        path = self._expand_path(path)
        page, is_image, ext_binary = self._page_for_text_read(path, 1, _THROUGH_EOF)
        failure = self._page_error(path, page)
        if failure is not None:
            return failure
        if page["state"] == "missing":
            return self._suggest_similar_files(path)
        file_size = self._page_int(page, "file_size")
        if is_image:
            return ReadResult(is_image=True, is_binary=True, file_size=file_size)
        sample_bytes = self._page_bytes(page, "sample")
        content_bytes = self._page_bytes(page, "page")
        if sample_bytes is None or content_bytes is None:
            return ReadResult(error=_SAFE_READER_BAD_PAYLOAD)
        if ext_binary or self._is_likely_binary_bytes(sample_bytes):
            return ReadResult(is_binary=True, file_size=file_size,
                              error=describe_binary_file(sample_bytes, file_size))
        # Strip a leading BOM (a phantom U+FEFF defeats an exact first-line match);
        # write_file re-probes disk and restores it.
        raw_content, _ = _strip_bom(content_bytes.decode("utf-8", errors="replace"))
        return ReadResult(content=raw_content, file_size=file_size)

    def read_file_bytes(self, path: str, max_bytes: Optional[int] = None) -> ReadResult:
        """Binary-safe bytes (as base64) through one validated descriptor. ``max_bytes``
        is enforced against the descriptor's size before any byte is exported."""
        path = self._expand_path(path)
        page = self._read_regular_file_page(path, 1, _THROUGH_EOF, max_bytes=max_bytes)
        failure = self._page_error(path, page)
        if failure is not None:
            return failure
        if page["state"] == "missing":
            return ReadResult(error=f"File not found: {path}")
        file_size = self._page_int(page, "file_size")
        if page["state"] == "too_large":
            return ReadResult(
                file_size=file_size,
                error=f"File is too large ({file_size:,} bytes, limit is {max_bytes:,})")
        if self._page_bytes(page, "page") is None:
            return ReadResult(error=f"Backend returned invalid binary data for: {path}")
        return ReadResult(base64_content=page["page"], file_size=file_size, is_binary=True)

    def delete_file(self, path: str) -> WriteResult:
        """Delete a single file (directories rejected) via the backend's ``python -c``
        so one code path works on local/docker/ssh AND Windows shells (no ``rm``)."""
        path = self._expand_path(path)
        denied = get_write_denied_error(path, verb="Delete")
        if denied:
            return WriteResult(error=denied)
        # Path baked in via repr() for shell-independent quoting; no
        # ``unlink(missing_ok=True)`` (a 3.7 remote interpreter lacks it).
        snippet = (
            "import shutil, pathlib, sys\n"
            f"p = pathlib.Path({path!r})\n"
            "recursive = False\n"
            "try:\n"
            "    if p.is_dir() and not p.is_symlink():\n"
            "        if recursive:\n"
            "            shutil.rmtree(p)\n"
            "        else:\n"
            "            print('is a directory: ' + str(p), file=sys.stderr); sys.exit(2)\n"
            "    else:\n"
            "        p.unlink()\n"
            "except FileNotFoundError:\n"
            "    pass\n"
            "except Exception as exc:\n"
            "    print(str(exc), file=sys.stderr); sys.exit(1)\n")
        result = self._run_python_snippet(snippet)
        if result.exit_code != 0:
            return WriteResult(error=f"Failed to delete {path}: {(result.stdout or '').strip() or 'unknown error'}")
        return WriteResult()

    def move_file(self, src: str, dst: str) -> WriteResult:
        src = self._expand_path(src)
        dst = self._expand_path(dst)
        for p in (src, dst):
            denied = get_write_denied_error(p, verb="Move")
            if denied:
                return WriteResult(error=denied)
        result = self._exec(f"mv {self._escape_shell_arg(src)} {self._escape_shell_arg(dst)}")
        if result.exit_code != 0:
            return WriteResult(error=f"Failed to move {src} -> {dst}: {result.stdout}")
        return WriteResult()

    # --- WRITE --------------------------------------------------------------

    # Lone surrogates OUTSIDE the surrogateescape range (U+DC80-U+DCFF round-trips
    # through the pipe; anything else can't be encoded at all).
    _LONE_SURROGATE_RE = re.compile(r"[\ud800-\udc7f\udd00-\udfff]")

    def _reject_unencodable(self, path: str, content: str) -> Optional[WriteResult]:
        """Refuse content with a lone surrogate BEFORE any subprocess: letting it
        reach the pipe spawns a child that hangs or truncates the target via
        empty-stdin ``cat``. A regex scan needs no encode."""
        m = self._LONE_SURROGATE_RE.search(content)
        if m:
            return WriteResult(error=(
                f"Refusing to write '{path}': content contains a lone "
                f"surrogate character ({m.group(0)!r}) that cannot be "
                "encoded as UTF-8. The file was NOT created or modified."))
        return None

    @staticmethod
    def _fail_closed_syntax_error(path: str, ext: str, content: str) -> Optional[WriteResult]:
        """Fail-closed pre-write gate for ``_FAIL_CLOSED_INPROC_EXTS`` (JSON/YAML/TOML):
        a structured-format write that doesn't parse is a corrupt write, so refuse
        before any bytes touch disk. Checked against the RAW content, before the
        BOM/CRLF shims (post-shim linting would false-positive on a BOM-marked file)."""
        linter = LINTERS_INPROC.get(ext) if ext in _FAIL_CLOSED_INPROC_EXTS else None
        if linter is None:
            return None
        ok, err = linter(content)
        if ok or err == "__SKIP__":
            return None
        return WriteResult(error=(
            f"Refusing to write '{path}': candidate content fails "
            f"{ext} syntax validation ({err}). The file was "
            "NOT created or modified. Fix the content and retry."))

    def _write_probe_cmd(self, path: str, sentinel: str, body: Optional[str]) -> str:
        """One shell command for the on-disk questions ``write_file`` asks. Two
        segments closed by a ``sentinel`` line: base64 of the first three bytes (BOM
        detection at the byte layer, same on-disk truth as ``_file_has_bom``), then
        ``body``: ``"cat"`` for the full text when pre-content is wanted, ``"sample"``
        for the 4 KB line-ending sample, or None for nothing. Gated on ``[ -f ]`` so a
        FIFO/device never reaches ``head``/``cat``; a missing path echoes ``MISSING_SENTINEL``."""
        arg = self._escape_shell_arg(path)
        if body == "cat":
            body_cmd = f"cat {arg} 2>/dev/null"
        elif body == "sample":
            body_cmd = f"head -c 4096 {arg} 2>/dev/null"
        else:
            body_cmd = ":"
        return (
            f"if [ -f {arg} ]; then "
            f"head -c 3 {arg} 2>/dev/null | base64 2>/dev/null; echo {sentinel}; "
            f"{body_cmd}; "
            f"else echo {MISSING_SENTINEL}; fi")

    def _probe_write_target(self, path: str, pre_content: Optional[str], want_pre: bool,
                            ) -> tuple[bool, Optional[str], Optional[str]]:
        """``(has_bom, pre_content, original_line_ending)`` for ``path`` in ONE
        round-trip (replaces ``cat`` when pre-content is wanted, a ``head -c 4096``
        line-ending sample and a ``head -c 3`` BOM check). Semantics unchanged:
        pre-content is read only when wanted and not supplied; the line ending comes
        from pre-content when there is any, else from the sample; the BOM always comes
        from disk. An unparseable reply falls back to the separate probes."""
        if want_pre and pre_content is None:
            body_mode: Optional[str] = "cat"
        elif not pre_content:
            body_mode = "sample"
        else:
            body_mode = None

        sentinel = _new_sentinel(_WRITE_SENTINEL_PREFIX)
        probe = self._exec(self._write_probe_cmd(path, sentinel, body_mode))
        output = probe.stdout or ""
        if sentinel not in output:
            if _strip_terminal_fence_leaks(output).strip() == MISSING_SENTINEL:
                ending = _detect_line_ending(pre_content) if pre_content else None
                return False, pre_content, ending
            logger.debug(
                "write_file: pre-write probe reply for %s has no sentinel "
                "(exit %s, %d chars); falling back to sequential probes",
                path, probe.exit_code, len(output))
            return self._probe_write_target_sequential(path, pre_content, want_pre)

        segments = _split_segments(output, sentinel)
        if probe.exit_code != 0 or len(segments) != 2:
            logger.debug(
                "write_file: pre-write probe for %s returned exit %s with %d "
                "segments (want 2); falling back to sequential probes",
                path, probe.exit_code, len(segments))
            return self._probe_write_target_sequential(path, pre_content, want_pre)
        head_seg, body = segments

        head_bytes = self._decode_base64_sample(head_seg)
        if head_bytes is None:
            # No clean base64 on this shell; ask the way we used to.
            logger.debug(
                "write_file: no usable base64 head for %s; paying one extra "
                "round-trip for the BOM probe", path)
            has_bom = self._file_has_bom(path, pre_content)
        else:
            has_bom = head_bytes.startswith(_UTF8_BOM.encode("utf-8"))

        if body_mode == "cat" and body:
            pre_content = body
        if pre_content:
            ending = _detect_line_ending(pre_content)
        elif body_mode == "sample" and body:
            ending = _detect_line_ending(body)
        else:
            ending = None
        return has_bom, pre_content, ending

    def _probe_write_target_sequential(self, path: str, pre_content: Optional[str], want_pre: bool,
                                       ) -> tuple[bool, Optional[str], Optional[str]]:
        """Pre-compound form of ``_probe_write_target``: one exec per question. A
        failed ``cat`` leaves pre_content None so the lint-delta and LSP consumers
        degrade gracefully."""
        if want_pre and pre_content is None:
            read_result = self._cat(path)
            if read_result.exit_code == 0 and read_result.stdout:
                pre_content = read_result.stdout
        if pre_content:
            ending = _detect_line_ending(pre_content)
        else:
            head = self._head(path, 4096)
            ending = _detect_line_ending(head.stdout) if head.exit_code == 0 and head.stdout else None
        return self._file_has_bom(path, pre_content), pre_content, ending

    def _verify_written_hash(self, path: str, content_bytes: bytes) -> tuple[Optional[bool], Optional[WriteResult]]:
        """Compare the on-disk sha256 to the intended bytes: ``(verified, error)``.
        The explicit flag saves the model a confirming re-read; a mismatch is a hard
        error. ``verified`` is None when the hash could not be taken."""
        try:
            hash_result = self._exec(f"sha256sum {self._escape_shell_arg(path)} 2>/dev/null")
            if hash_result.exit_code == 0 and hash_result.stdout.strip():
                disk_sha = hash_result.stdout.strip().split()[0]
                if disk_sha != hashlib.sha256(content_bytes).hexdigest():
                    return False, WriteResult(error=(
                        f"Post-write verification failed for {path}: on-disk "
                        "content hash differs from the intended write. The "
                        "write did not persist correctly — re-read the file "
                        "and retry."))
                return True, None
        except Exception:
            pass
        return None, None

    def write_file(self, path: str, content: str, pre_content: Optional[str] = None) -> WriteResult:
        """Write content atomically, creating parent directories as needed.

        Order: deny list → lone-surrogate refusal → fail-closed syntax gate on the
        CANDIDATE content (JSON/YAML/TOML) → one compound on-disk probe
        (pre-content when wanted, CRLF, BOM; see ``_probe_write_target``) →
        CRLF/BOM preservation → LSP baseline snapshot → atomic write (content rides
        stdin: no ARG_MAX limit) → sha256 verification → lint delta → LSP
        diagnostics when syntax is clean. ``pre_content``: pre-edit content the
        caller already has (skips the read); BOM detection always probes disk.
        """
        path = self._expand_path(path)
        denied = get_write_denied_error(path)
        if denied:
            return WriteResult(error=denied)
        refused = self._reject_unencodable(path, content)
        if refused is not None:
            return refused
        ext = os.path.splitext(path)[1].lower()
        refused = self._fail_closed_syntax_error(path, ext, content)
        if refused is not None:
            return refused

        # Pre-content is read only for extensions in the UNION of in-process lint and
        # LSP coverage (keeps the hot path fast for binaries).
        want_pre = ext in LINTERS_INPROC or self._lsp_handles_extension(ext)
        has_bom, pre_content, original_ending = self._probe_write_target(path, pre_content, want_pre)
        # read_file strips the BOM and models send bare-LF text, so a round-trip would
        # otherwise normalize CRLF files and drop the BOM (prepend only when absent).
        if original_ending == "\r\n":
            content = _normalize_line_endings(content, "\r\n")
        if has_bom and not _has_bom(content):
            content = _UTF8_BOM + content
        # Best-effort snapshot so the LSP tier reports only this edit's diagnostics.
        self._snapshot_lsp_baseline(path)
        # ``dirs_created`` means "parent dirs ensured" (mkdir -p is folded into
        # _atomic_write; its failure surfaces as the atomic-write error below).
        dirs_created = bool(os.path.dirname(path))
        # surrogateescape is the exact inverse of the decode that may have produced
        # this content, so these are the bytes on disk; the early rejection above
        # guarantees this cannot raise.
        content_bytes = content.encode("utf-8", "surrogateescape")
        write_result = self._atomic_write(path, content)
        if write_result.exit_code != 0:
            return WriteResult(error=f"Failed to write file: {write_result.stdout}")
        content_verified, verify_error = self._verify_written_hash(path, content_bytes)
        if verify_error is not None:
            return verify_error

        lint_result = self._check_lint_delta(path, pre_content=pre_content, post_content=content)
        # LSP diagnostics are a separate channel, fired only when the syntax tier is
        # clean (no point asking an LSP about a file that won't parse).
        lsp_diagnostics: Optional[str] = None
        if lint_result.success or lint_result.skipped:
            lsp_diagnostics = self._maybe_lsp_diagnostics(path, pre_content=pre_content, post_content=content) or None
        return WriteResult(
            bytes_written=len(content_bytes), dirs_created=dirs_created, verified=content_verified,
            lint=lint_result.to_dict() if lint_result else None, lsp_diagnostics=lsp_diagnostics)

    # --- PATCH (replace mode) -----------------------------------------------

    def _no_match_result(self, path: str, content: str, old_string: str,
                         new_string: str, match_count: int, error: Optional[str]) -> PatchResult:
        """PatchResult for a failed fuzzy match. Already-applied detection first: the
        most common production failure is a re-send of an edit that already landed,
        and a success-shaped no-op stops the model burning turns on re-reads.
        Otherwise attach a best-effort "Did you mean?" snippet to the error."""
        from tools.fuzzy_match import format_no_match_hint, is_already_applied
        if is_already_applied(content, old_string, new_string):
            return PatchResult(
                success=True, no_change=True,
                note=(
                    f"File already contains the target text — the edit "
                    f"appears to be already applied to {path}. No write "
                    "performed; do not re-send this patch."))
        err_msg = error or f"Could not find match for old_string in {path}"
        try:
            err_msg += format_no_match_hint(err_msg, match_count, old_string, content)
        except Exception:
            pass
        return PatchResult(error=err_msg)

    def _verify_patch_persisted(self, path: str, new_content: str) -> Optional[PatchResult]:
        """Re-read ``path`` and confirm the intended bytes landed; error result or None.
        Catches silent persistence failures (FS oddities, races, truncated pipe).
        Line endings are normalized first (Windows text-mode ``open()`` writes LF as
        CRLF) and the re-read's BOM stripped (``new_content`` is the BOM-less
        string we matched against)."""
        verify_result = self._cat(path)
        if verify_result.exit_code != 0:
            return PatchResult(error=f"Post-write verification failed: could not re-read {path}")
        bomless, _ = _strip_bom(verify_result.stdout)
        on_disk = bomless.replace("\r\n", "\n").replace("\r", "\n")
        intended = new_content.replace("\r\n", "\n").replace("\r", "\n")
        if on_disk != intended:
            return PatchResult(error=(
                f"Post-write verification failed for {path}: on-disk content "
                f"differs from intended write "
                f"(wrote {len(intended)} chars, read back "
                f"{len(on_disk)} chars after normalizing line endings). "
                "The patch did not persist. Re-read the file and try again."))
        return None

    def patch_replace(self, path: str, old_string: str, new_string: str,
                      replace_all: bool = False) -> PatchResult:
        """Replace text in a file using fuzzy matching (``old_string`` must be
        unique unless ``replace_all``). Returns a PatchResult with diff + lint."""
        path = self._expand_path(path)
        denied = get_write_denied_error(path)
        if denied:
            return PatchResult(error=denied)
        read_result = self._cat(path)
        if read_result.exit_code != 0:
            return PatchResult(error=f"Failed to read file: {path}")
        # Match and diff on BOM-stripped content (a phantom U+FEFF defeats an exact
        # first-line match); the raw read becomes write_file's pre_content.
        raw_content = read_result.stdout
        content, _ = _strip_bom(raw_content)

        from tools.fuzzy_match import fuzzy_find_and_replace
        new_content, match_count, _strategy, error = fuzzy_find_and_replace(
            content, old_string, new_string, replace_all)
        if error or match_count == 0:
            return self._no_match_result(path, content, old_string, new_string, match_count, error)
        # Models send bare-LF old/new strings; normalize the substituted region to
        # the file's ending so CRLF files stay consistent.
        file_ending = _detect_line_ending(content)
        if file_ending:
            new_content = _normalize_line_endings(new_content, file_ending)
        write_result = self.write_file(path, new_content, pre_content=raw_content)
        if write_result.error:
            return PatchResult(error=f"Failed to write changes: {write_result.error}")
        verify_error = self._verify_patch_persisted(path, new_content)
        if verify_error is not None:
            return verify_error
        lint_result = self._check_lint_delta(path, pre_content=content, post_content=new_content)
        return PatchResult(
            success=True, diff=self._unified_diff(content, new_content, path), files_modified=[path],
            lint=lint_result.to_dict() if lint_result else None,
            # From the internal write_file call, whose baseline was the pre-patch content.
            lsp_diagnostics=write_result.lsp_diagnostics)

    def patch_v4a(self, patch_content: str) -> PatchResult:
        """Apply a V4A format patch (``*** Begin Patch`` / ``*** Update File:`` /
        ``@@ hint @@`` hunks / ``*** End Patch``)."""
        from tools.patch_parser import parse_v4a_patch, apply_v4a_operations
        operations, parse_error = parse_v4a_patch(patch_content)
        if parse_error:
            return PatchResult(error=f"Failed to parse patch: {parse_error}")
        return apply_v4a_operations(operations, self)

    # --- SEARCH -------------------------------------------------------------

    def search(self, pattern: str, path: str = ".", target: str = "content",
               file_glob: Optional[str] = None, limit: int = 50, offset: int = 0,
               output_mode: str = "content", context: int = 0,
               order: str = "discovery") -> SearchResult:
        """Search for content (regex, ``target="content"``) or files (glob,
        ``target="files"``). ``output_mode``: "content", "files_only" or "count";
        ``context``: lines of context around matches; ``order``: file-search
        ordering — fast "discovery" or exact "modified" time."""
        offset, limit = normalize_search_pagination(offset, limit)
        if target == "files" and order not in {"discovery", "modified"}:
            return SearchResult(
                error=(f"Invalid file search order {order!r}; expected "
                       "'discovery' or 'modified'."))
        path = self._expand_path(path)
        exists_probe = self._path_exists_probe(path)
        if "exists" not in exists_probe and "not_found" not in exists_probe:
            return SearchResult(error=(f"Terminal environment unavailable: could not stat {path} "
                                       "(the sandbox may still be starting or was removed). Retry shortly."))
        if "not_found" in exists_probe:
            # Models often pass several paths in one string: search the parts that exist.
            multi = self._try_multi_path_search(
                pattern, path, target, file_glob, limit, offset, output_mode, context, order)
            if multi is not None:
                return multi
            return self._path_not_found_result(path)
        result = self._dispatch_search(pattern, path, target, file_glob, limit, offset,
                                       output_mode, context, order)
        exclusions = self._macos_search_exclusions(path)
        if exclusions and not result.error:
            skipped = ", ".join(item.split("/")[-1] for item in exclusions)
            result.warning = (
                "Skipped macOS protected folders during broad search to avoid "
                f"an unattended privacy prompt: {skipped}. Search a protected "
                "folder directly when access is intentional.")
        return result


# ---- BEGIN PLUGIN-COMPAT (revert-scheduled; see COMPAT_MANIFEST.md) ----
# Names external plugins imported from this module before the Sep 2026 decomposition.
# Internal code MUST NOT use these (scripts/check_compat_pointers.py fails CI if it does).
# The whole block is removed by reverting the commit that added it.
from typing import Any  # noqa: F401,E402
from typing import ClassVar  # noqa: F401,E402
from typing import List  # noqa: F401,E402
from agent.file_safety import build_write_denied_paths  # noqa: F401,E402
from agent.file_safety import build_write_denied_prefixes  # noqa: F401,E402
from dataclasses import dataclass  # noqa: F401,E402
from dataclasses import field  # noqa: F401,E402
import posixpath  # noqa: F401,E402
import threading  # noqa: F401,E402

MAX_LINES = 2000

MAX_LINE_LENGTH = 2000

WRITE_DENIED_PATHS = build_write_denied_paths(_HOME)

WRITE_DENIED_PREFIXES = build_write_denied_prefixes(_HOME)


_PLUGIN_COMPAT_LAZY = {
    'DEFAULT_READ_LIMIT': ('tools.file_operations_common', 'DEFAULT_READ_LIMIT'),
    'DEFAULT_READ_OFFSET': ('tools.file_operations_common', 'DEFAULT_READ_OFFSET'),
    'DEFAULT_SEARCH_LIMIT': ('tools.file_operations_common', 'DEFAULT_SEARCH_LIMIT'),
    'DEFAULT_SEARCH_OFFSET': ('tools.file_operations_common', 'DEFAULT_SEARCH_OFFSET'),
    'LINTERS': ('tools.file_operations_lint', 'LINTERS'),
    'LintResult': ('tools.file_operations_common', 'LintResult'),
    'MAX_FILE_SIZE': ('tools.transcription_common', 'MAX_FILE_SIZE'),
    'SEARCH_PRUNE_DIR_NAMES': ('agent.search_policy', 'SEARCH_PRUNE_DIR_NAMES'),
    'SearchMatch': ('tools.file_operations_common', 'SearchMatch'),
    'build_write_denied_paths': ('agent.file_safety', 'build_write_denied_paths'),
    'build_write_denied_prefixes': ('agent.file_safety', 'build_write_denied_prefixes'),
    'tool_interrupt': ('tools', 'interrupt'),
}


def __getattr__(name):  # PEP 562 — lazy so no import cycles
    target = _PLUGIN_COMPAT_LAZY.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    import importlib
    from hermes_cli.plugin_compat import warn_once
    warn_once(__name__, name, *target)
    return getattr(importlib.import_module(target[0]), target[1])
# ---- END PLUGIN-COMPAT ----

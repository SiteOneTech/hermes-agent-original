#!/usr/bin/env python3
"""Fail when production code, skills, docs or prompts hard-code a literal ``/tmp`` path.

``/tmp`` is not portable: Termux has no ``/tmp`` at all, native Windows has no such directory,
macOS aliases it to ``/private/tmp`` (breaking naive path comparisons), and on most Linux
distributions it is a RAM-backed tmpfs that fills under Hermes load. Hermes resolves scratch
space through one helper (``hermes_constants.get_scratch_dir()`` → ``HERMES_HOME/cache/scratch``,
which every Hermes process also exports as ``TMPDIR``/``TMP``/``TEMP``), and prompts + skills
must steer the model the same way, because a literal ``/tmp`` in a SKILL.md or system prompt
becomes a literal ``/tmp`` in the model's shell commands on every platform.

Flags any line containing a ``/tmp`` path token (``/tmp``, ``/tmp/...``) in the scanned trees.
Automatically NOT flagged (no marker needed):

  ${TMPDIR:-/tmp}            shell fallback idiom: TMPDIR wins where it is set
  /var/tmp, /private/tmp     different directories, not the bare ``/tmp`` root
  tmpfs, tmp_path, ~/tmp     not a ``/tmp`` path at all
  code comments, docstrings  they describe code; nothing there reaches a shell or the model
                             (Markdown prose is NOT exempt: docs and skills are read by both)

Opt out of one line with ``no-tmp: ok — <why>`` on that line or on the line directly above it
(``# no-tmp: ok — ...`` in Python/shell, ``<!-- no-tmp: ok — ... -->`` in Markdown). Legitimate
reasons: the code *detects* ``/tmp`` (path-alias checks, security denylists, the scratch-dir
resolver's own POSIX fallback) or the text explains why ``/tmp`` is wrong. "It works on my
machine" is not one.

``_BASELINE`` maps files that already carried literals when this check landed to their hit
count. It is a burn-down list, not a policy: fix the file (or mark the lines) and drop the
entry. A baseline file gaining hits fails the check; an entry that overstates a file (partly or
fully burned down) is reported as an advisory so parallel clean-ups never turn CI red — refresh
it with ``--print-baseline`` (``--strict-baseline`` turns those advisories into failures).

Scope: every first-party ``.py .sh .ts .tsx .js .mjs .cjs .md .mdx .txt .yaml .yml .json .toml``
file except tests (``tests/``, ``tests-js/``, ``__tests__/``, ``e2e/``, ``test_*.py``,
``*.test.ts`` ...), ``evals/``, CI workflows (``.github/`` runs on Linux runners), container
build files (``Dockerfile*``, ``docker/``), generated lockfiles and the translated docs mirror
(``website/i18n/``, regenerated from the English source).

Run: python scripts/check_no_tmp_literals.py [--all] [--print-baseline] [paths...]
  --all              ignore ``_BASELINE`` and report every hit (burn-down view)
  --print-baseline   print a ``_BASELINE`` literal matching the current tree
  --strict-baseline  fail on stale/overstated ``_BASELINE`` entries too
Exit 1 on any violation, 0 when clean.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import re
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SELF = Path(__file__).resolve()

MARKER = "no-tmp: ok"

SCAN_SUFFIXES = {
    ".py", ".sh", ".bash", ".ts", ".tsx", ".js", ".mjs", ".cjs",
    ".md", ".mdx", ".txt", ".yaml", ".yml", ".json", ".toml",
}

# Pruned at every depth.
SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", "build", "dist", ".worktrees",
    "tests", "tests-js", "__tests__", "e2e", "evals", "docker", "MagicMock",
    ".pytest_cache", ".ruff_cache", ".mypy_cache", "coverage", "target",
}
# Pruned only directly under the repo root.
ROOT_SKIP_DIRS = {".github"}
# Pruned as repo-relative paths.
SKIP_REL_DIRS = {Path("website/i18n"), Path("website/build"), Path("website/node_modules")}

SKIP_FILE_NAMES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "uv.lock", "poetry.lock"}
SKIP_FILE_PATTERNS = (
    re.compile(r"^test_.*\.py$"),
    re.compile(r"_test\.py$"),
    re.compile(r"^conftest\.py$"),
    re.compile(r"\.(test|spec)\.(ts|tsx|js|mjs|cjs)$"),
    re.compile(r"^Dockerfile(\..*)?$"),
)

# A `/tmp` path token: not glued to a preceding path/word char (`/var/tmp`, `~/tmp`, `a/tmp`),
# not the `${TMPDIR:-/tmp}` fallback idiom, and not followed by a word char (`/tmpfs`).
_TMP_TOKEN = re.compile(r"(?<![\w./~\\-])(?<!:-)/tmp(?![\w-])")


_LINE_COMMENT_PREFIX = {
    ".sh": ("#",), ".bash": ("#",), ".yaml": ("#",), ".yml": ("#",), ".toml": ("#",),
    ".ts": ("//", "/*", "*"), ".tsx": ("//", "/*", "*"), ".js": ("//", "/*", "*"),
    ".mjs": ("//", "/*", "*"), ".cjs": ("//", "/*", "*"),
}
_TRAILING_COMMENT = {".py": "#", ".sh": "#", ".bash": "#", ".yaml": "#", ".yml": "#", ".toml": "#",
                     ".ts": "//", ".tsx": "//", ".js": "//", ".mjs": "//", ".cjs": "//"}


def _python_comment_and_docstring_spans(text: str) -> tuple[dict[int, int], set[int]]:
    """(line -> column where a `#` comment starts, lines inside doc-strings) via tokenize/ast.

    Comments and docstrings *describe* code; a `/tmp` there cannot reach a shell or the model, so
    they stay out of the count (prompt strings, defaults and command templates are what matters).
    """
    import ast
    import io
    import tokenize

    comments: dict[int, int] = {}
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT:
                comments[tok.start[0]] = tok.start[1]
    except (tokenize.TokenError, SyntaxError, IndentationError):
        pass
    doc_lines: set[int] = set()
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # scanned files' own SyntaxWarnings are not our business
            tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return comments, doc_lines
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
                    and isinstance(body[0].value.value, str):
                doc_lines.update(range(body[0].lineno, (body[0].end_lineno or body[0].lineno) + 1))
    return comments, doc_lines


def _iter_lines_with_hits(text: str, suffix: str = ""):
    prev_marked = False
    comments: dict[int, int] = {}
    doc_lines: set[int] = set()
    if suffix == ".py":
        comments, doc_lines = _python_comment_and_docstring_spans(text)
    prefixes = _LINE_COMMENT_PREFIX.get(suffix, ())
    trailing = _TRAILING_COMMENT.get(suffix)
    for lineno, line in enumerate(text.splitlines(), start=1):
        marked = MARKER in line
        try:
            match = _TMP_TOKEN.search(line)
            if not match or marked or prev_marked or lineno in doc_lines:
                continue
            stripped = line.lstrip()
            if prefixes and stripped.startswith(prefixes):
                continue  # whole-line comment
            if suffix == ".py":
                if lineno in comments and match.start() >= comments[lineno]:
                    continue  # inside a trailing `#` comment (tokenize-exact: not a `#` in a string)
            elif trailing:
                cut = line.find(trailing)
                if 0 <= cut < match.start() and not re.search(r"""["'`]""", line[:cut]):
                    continue  # trailing comment on a line with no string literal before it
            yield lineno, line
        finally:
            prev_marked = marked


def _skip_file(path: Path) -> bool:
    if path == SELF or path.suffix not in SCAN_SUFFIXES or path.name in SKIP_FILE_NAMES:
        return True
    return any(p.search(path.name) for p in SKIP_FILE_PATTERNS)


def _git_ignored(root: Path) -> set[Path]:
    """Ignored/untracked-by-.gitignore paths (runner artifacts such as ``test_durations.json``)
    are build products, not sources; a scan that reads them fails on whatever the last test
    run wrote. Empty when *root* is not a git checkout."""
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--others", "--ignored", "--exclude-standard", "-z"],
            capture_output=True, text=True, check=True, stdin=subprocess.DEVNULL,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return set()
    return {root / rel for rel in out.split("\0") if rel}


def iter_files(root: Path | None = None):
    root = (root or ROOT).resolve()
    ignored = _git_ignored(root)
    for dirpath, dirnames, filenames in os.walk(root):
        here = Path(dirpath)
        rel_here = here.relative_to(root) if here != root else Path()
        excluded = SKIP_DIRS | (ROOT_SKIP_DIRS if here == root else set())
        dirnames[:] = sorted(
            d for d in dirnames if d not in excluded and (rel_here / d) not in SKIP_REL_DIRS
        )
        for filename in sorted(filenames):
            path = here / filename
            if path not in ignored and not _skip_file(path):
                yield path


def scan(paths=None, root: Path | None = None) -> dict[str, list[tuple[int, str]]]:
    """Repo-relative POSIX path -> [(lineno, line)] for every file with at least one hit."""
    root = (root or ROOT).resolve()
    hits: dict[str, list[tuple[int, str]]] = {}
    files = list(paths) if paths else list(iter_files(root))
    for path in files:
        path = Path(path).resolve()
        if paths and _skip_file(path):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        found = list(_iter_lines_with_hits(text, path.suffix))
        if found:
            try:
                rel = path.relative_to(root).as_posix()
            except ValueError:
                rel = str(path)
            hits[rel] = found
    return hits


# Files that carried literal /tmp paths when this check landed, with their hit counts.
# Burn-down list: fix or mark, then delete the entry. Regenerate with --print-baseline.
_BASELINE: dict[str, int] = {
    # a tree listing inside a fenced code block; an inline marker would render on the page
    "factory/projects/factory-runtime-evolution/QA_REPORT.md": 1,
    "factory/projects/funnel-core-crm-workflow/R0_NOTION_TRACKER_RECONCILIATION.md": 4,
    "factory/projects/funnel-core-crm-workflow/notion_tracker_evidence.json": 3,
    "factory/projects/zeus-alpha-research-ledger-core/DOCUMENTATION_INDEX.md": 65,
    "factory/projects/zeus-alpha-research-ledger-core/G1_REVIEW.md": 13,
    "factory/projects/zeus-alpha-research-ledger-core/QA_GATES.md": 26,
    "factory/projects/zeus-alpha-research-ledger-core/R2AI_R2_NON_DESTRUCTIVE_CURRENT_ORIGIN_G1_RECOVERY.md": 4,
    "factory/projects/zeus-alpha-research-ledger-core/R2AI_R5_CURRENT_ORIGIN_EXACT_SHA_ASSIGNED_BRANCH_DELIVERY_EVIDENCE_REWORK.md": 4,
    "factory/projects/zeus-alpha-research-ledger-core/R2AM_STALE_PRIMARY_FACTORY_TICK_SOURCE_RESOLUTION_REPAIR.md": 1,
    "factory/projects/zeus-alpha-research-ledger-core/R2AP_CURRENT_ORIGIN_G1_DOCUMENT_VALIDATION_RECOVERY.md": 2,
    "factory/projects/zeus-alpha-research-ledger-core/R2AP_PR72_RESIDUAL_G1_TASK_METADATA_RECONCILIATION.md": 7,
    "factory/projects/zeus-alpha-research-ledger-core/R2AS_R2_INDEPENDENT_EXACT_SHA_G1_SOURCE_SELECTION_REVIEW.md": 4,
    "factory/projects/zeus-alpha-research-ledger-core/R2AT_CURRENT_ORIGIN_G1_DOCUMENTATION_VALIDATION_REWORK.md": 2,
    "factory/projects/zeus-alpha-research-ledger-core/R2AU_CURRENT_ORIGIN_G1_DOCUMENT_STATUS_PROJECTION_REPAIR.md": 2,
    "factory/projects/zeus-alpha-research-ledger-core/R2AX_CURRENT_ORIGIN_FACTORY_CLI_G1_RECOVERY_DISPATCH.md": 2,
    "factory/projects/zeus-alpha-research-ledger-core/R2AZ_NON_DESTRUCTIVE_CURRENT_BASE_G1_EVIDENCE_RECOVERY.md": 5,
    "factory/projects/zeus-alpha-research-ledger-core/R2BA_CURRENT_BASE_G1_INDEPENDENT_REVIEW_AND_REVIEW_STATE_REPAIR.md": 1,
    "factory/projects/zeus-alpha-research-ledger-core/R2BB_CURRENT_BASE_G1_STATUS_PROJECTION_PR63_EVIDENCE_RECOVERY.md": 3,
    "factory/projects/zeus-alpha-research-ledger-core/R2BJ_BOUNDED_CANONICAL_G1_DOCUMENTATION_INDEX_RECOVERY.md": 4,
    "factory/projects/zeus-alpha-research-ledger-core/R2BL_NON_DESTRUCTIVE_CANONICAL_G1_EVIDENCE_REPAIR.md": 3,
    "factory/projects/zeus-alpha-research-ledger-core/R2BM_CANONICAL_G1_DOCS_GATE_SOURCE_ROOT_RECOVERY.md": 6,
    "factory/projects/zeus-alpha-research-ledger-core/R2BN_CANONICAL_G1_REVIEW_STATE_SOURCE_ROOT_REPAIR.md": 4,
    "factory/projects/zeus-alpha-research-ledger-core/R2C5_INDEPENDENT_CURRENT_BASE_G1_REVIEW.md": 1,
    "factory/projects/zeus-alpha-research-ledger-core/R2CL_CANONICAL_G1_STALE_PRIMARY_CHECKOUT_CONTROL_PLANE_RECOVERY.md": 10,
    "factory/projects/zeus-alpha-research-ledger-core/R2CM_G1_REVIEW_STATE_PROVENANCE_REPAIR.md": 12,
    "factory/projects/zeus-alpha-research-ledger-core/R2CN_BOUNDED_CANONICAL_G1_DOCS_GATE_AND_PR_PROVENANCE_REPAIR.md": 9,
    "factory/projects/zeus-alpha-research-ledger-core/R2CT_BOUNDED_CANONICAL_G1_DOCUMENTATION_VALIDATION_PR_FIRST_RECOVERY.md": 2,
    "factory/projects/zeus-alpha-research-ledger-core/R2CV_CURRENT_ORIGIN_G1_DOCUMENTATION_VALIDATION_RECOVERY.md": 6,
    "factory/projects/zeus-alpha-research-ledger-core/R2CX_CURRENT_ORIGIN_DOCUMENTATION_INDEX_REVIEWED_STATE_REPAIR.md": 5,
    "factory/projects/zeus-alpha-research-ledger-core/R2CY_R2_G1_REVIEW_ROUTE_RECOVERY.md": 3,
    "factory/projects/zeus-alpha-research-ledger-core/R2CY_R3_DOCS_FIRST_G1_EXACT_SHA_REVIEW_DISPATCH_RECOVERY.md": 1,
    "factory/projects/zeus-alpha-research-ledger-core/R2CY_R3_SUCCESSOR_CURRENT_BASE_R2DA_DISPATCH_REPAIR.md": 2,
    "factory/projects/zeus-alpha-research-ledger-core/R2CY_R3_SUCCESSOR_INTEGRATE_R2DA_FAIL_CLOSED_READBACK.md": 2,
    "factory/projects/zeus-alpha-research-ledger-core/R2CY_R5_FAIL_CLOSED_PRIMARY_RUNTIME_AND_TERMINALIZATION_RECOVERY.md": 6,
    "factory/projects/zeus-alpha-research-ledger-core/R2CY_R6_FRESH_G1_SOURCE_ROOT_FRONTMATTER_READBACK_REPAIR.md": 5,
    "factory/projects/zeus-alpha-research-ledger-core/R2D1_CURRENT_BASE_EXPLICIT_G1_VALIDATION_GATE_DISPATCH_RECOVERY.md": 1,
    "factory/projects/zeus-alpha-research-ledger-core/R2D6_REPAIR_RECURRENT_G1_RECOVERY_SELF_DENIAL.md": 3,
    "factory/projects/zeus-alpha-research-ledger-core/R2DB_CURRENT_ORIGIN_G1_REVIEWED_STATE_PR_RECOVERY.md": 5,
    "factory/projects/zeus-alpha-research-ledger-core/R2DC_BOUNDED_G1_REVIEWED_STATE_RECOVERY.md": 5,
    "factory/projects/zeus-alpha-research-ledger-core/R2DC_FAIL_CLOSED_FALSE_G1_REVIEW_TERMINALIZATION_RECOVERY.md": 1,
    "factory/projects/zeus-alpha-research-ledger-core/R2DF_R16_RECOVER_EXPIRED_QUEUED_R15_G1_DISPATCH.md": 2,
    "factory/projects/zeus-alpha-research-ledger-core/R2DF_R1_DOCS_FIRST_G1_RECOVERY_DISPATCH_ROUTING_REPAIR.md": 2,
    "factory/projects/zeus-alpha-research-ledger-core/R2DF_R43_G1_RECOVERY_SELECTION_STARVATION_REPAIR.md": 2,
    "factory/projects/zeus-alpha-research-ledger-core/R2DF_R45_STALE_CANONICAL_FACTORY_CLI_BOOTSTRAP_REPAIR.md": 4,
    "factory/projects/zeus-alpha-research-ledger-core/R2DF_R47_ISOLATED_R44_SCHEDULER_FIX_PR_RECOVERY.md": 2,
    "factory/projects/zeus-alpha-research-ledger-core/R2DF_R48_CURRENT_ORIGIN_R47_CLEAN_WORKTREE_PR_PROVENANCE_RECOVERY.md": 2,
    "factory/projects/zeus-alpha-research-ledger-core/R2DF_R5_FAIL_CLOSED_REVIEW_TERMINALIZATION_RECOVERY.md": 2,
    "factory/projects/zeus-alpha-research-ledger-core/R2DF_R7_INDEPENDENT_EXACT_SHA_G1_SOURCE_ROOT_REVIEW.md": 10,
    "factory/projects/zeus-alpha-research-ledger-core/R2DF_R8_CURRENT_BASE_DOCS_FIRST_DISPATCH_RECOVERY.md": 2,
    "factory/projects/zeus-alpha-research-ledger-core/R2DG_BOUNDED_G1_EXACT_SHA_INDEPENDENT_REVIEW_RECOVERY.md": 3,
    "factory/projects/zeus-alpha-research-ledger-core/R2DH_DOCS_FIRST_CURRENT_BASE_G1_REVIEW_STATE_DISPATCH_RECOVERY.md": 3,
    "factory/projects/zeus-alpha-research-ledger-core/R2DI_DOCS_FIRST_FAIL_CLOSED_REVIEW_TERMINALIZATION_AND_DISPATCH_REPAIR.md": 2,
    "factory/projects/zeus-alpha-research-ledger-core/R2DL_G1_DOCUMENTATION_DISPATCH_VALIDATOR_RECOVERY.md": 2,
    "factory/projects/zeus-alpha-research-ledger-core/R2EA_DOCS_FIRST_STALE_RUNTIME_DISPATCH_PROVENANCE_REPAIR.md": 2,
    "factory/projects/zeus-alpha-research-ledger-core/R2U_CANONICAL_G1_DOCUMENT_STATUS_PREFLIGHT_REPAIR.md": 1,
    "factory/projects/zeus-alpha-research-ledger-core/R6_SOURCE_INCREMENT_INTEGRATION_RECONCILIATION.md": 22,
    "factory/projects/zeus-alpha-research-ledger-core/SECURITY_GATES.md": 2,
    "factory/projects/zeus-alpha-research-ledger-core/TASK_GRAPH.md": 31,
    "factory/projects/zeus-alpha-research-ledger-core/TRACKER.md": 37,
    "factory/projects/zeus-signature-core-refactor-hotfix/QUALITY_REVIEW.md": 1,
    "optional-skills/media/video-intel-pipeline/SKILL.md": 9,
    "scripts/runtime/publish_delivery_sandbox.py": 1,
    "skills/devops/kanban-worker/SKILL.md": 1,
    "website/docs/getting-started/nix-setup.md": 1,
}


def _format_baseline(hits: dict[str, list]) -> str:
    body = "".join(f'    "{rel}": {len(found)},\n' for rel, found in sorted(hits.items()))
    return "_BASELINE: dict[str, int] = {\n" + body + "}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("paths", nargs="*", help="files to check (default: whole repo)")
    ap.add_argument("--all", action="store_true", help="ignore _BASELINE; report every hit")
    ap.add_argument("--print-baseline", action="store_true", help="print a _BASELINE for the current tree")
    ap.add_argument("--strict-baseline", action="store_true", help="also fail when _BASELINE overstates a file")
    args = ap.parse_args(argv)

    hits = scan(args.paths or None)
    if args.print_baseline:
        print(_format_baseline(hits))
        return 0

    baseline = {} if (args.all or args.paths) else _BASELINE
    problems: list[str] = []
    advisories: list[str] = []
    total = 0
    for rel in sorted(hits):
        found = hits[rel]
        allowed = baseline.get(rel)
        if allowed is not None and len(found) <= allowed:
            if len(found) < allowed:
                advisories.append(f"{rel}: {len(found)} literal /tmp path(s) left, _BASELINE says {allowed}")
            continue
        for lineno, line in found:
            total += 1
            problems.append(f"{rel}:{lineno}: {line.strip()[:160]}")
    for rel in sorted(baseline):
        if rel not in hits:
            advisories.append(f"{rel}: listed in _BASELINE but clean (or gone)")
    if advisories:
        print("advisory — _BASELINE in scripts/check_no_tmp_literals.py is stale; regenerate it with "
              "--print-baseline (fewer hits than listed is progress, not a failure):")
        print("\n".join("  " + a for a in advisories))
    if args.strict_baseline and advisories:
        problems.extend(advisories)

    if not problems:
        print("no literal /tmp paths outside the baseline")
        return 0
    print("\n".join(problems))
    print(
        f"\n{total} literal /tmp path(s) flagged. Resolve scratch space through "
        f"hermes_constants.get_scratch_dir() (or $TMPDIR / tempfile, which Hermes points there), tell the "
        f"model to do the same in skills and prompts, or mark a deliberate line with `{MARKER} — <why>` (same line or the line above). "
        f"See scripts/check_no_tmp_literals.py."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Validate R2cy-R6 G1 source-root/frontmatter readback evidence.

Usage:
  python factory/projects/zeus-alpha-research-ledger-core/validate_r2cy_r6_g1_readback.py /tmp/r2cy-r6-status.json
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ID = "zeus-alpha-research-ledger-core"
ARTIFACT_DIR = Path("factory/projects") / PROJECT_ID
REQUIRED_G1_DOCS = (
    "FACTORY_INTAKE.md",
    "REQUIREMENTS_ANALYSIS.md",
    "PATTERN_ANALYSIS.md",
    "ASSUMPTIONS_AND_OPEN_QUESTIONS.md",
    "PRD.md",
    "ADRS.md",
    "METHODOLOGY_PLAN.md",
    "TECHNICAL_BLUEPRINT.md",
    "SPRINT_PLAN.md",
    "TASK_GRAPH.md",
    "TRACKER.md",
    "DOCUMENTATION_INDEX.md",
    "QA_GATES.md",
    "SECURITY_GATES.md",
)
PROMPT_STALE_TEN = (
    "FACTORY_INTAKE.md",
    "REQUIREMENTS_ANALYSIS.md",
    "PATTERN_ANALYSIS.md",
    "ASSUMPTIONS_AND_OPEN_QUESTIONS.md",
    "PRD.md",
    "ADRS.md",
    "METHODOLOGY_PLAN.md",
    "TECHNICAL_BLUEPRINT.md",
    "TASK_GRAPH.md",
    "SECURITY_GATES.md",
)
TRUE_VALUES = {"true", "yes", "y", "1", "passed", "validated", "reviewed", "approved"}


def _repo_root() -> Path:
    # script path: <repo>/factory/projects/<project>/validate_r2cy_r6_g1_readback.py
    return Path(__file__).resolve().parents[3]


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        capture_output=True,
        check=False,
        timeout=20,
    )
    if result.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def _frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if not lines or lines[0].strip() != "---":
        raise AssertionError(f"{path} has no top-of-file YAML frontmatter")
    values: dict[str, str] = {}
    for line in lines[1:80]:
        if line.strip() == "---":
            return values
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip().lower()] = value.strip().strip("'\"").split("#", 1)[0].strip().lower()
    raise AssertionError(f"{path} frontmatter did not close within 80 lines")


def _is_true(value: str | None) -> bool:
    return str(value or "").strip().lower() in TRUE_VALUES


def main() -> int:
    if len(sys.argv) != 2:
        print((__doc__ or "").strip(), file=sys.stderr)
        return 2
    repo = _repo_root()
    status_path = Path(sys.argv[1]).resolve()
    status = json.loads(status_path.read_text(encoding="utf-8"))
    projects = [p for p in status.get("projects") or [] if p.get("project_id") == PROJECT_ID]
    if len(projects) != 1:
        raise AssertionError(f"expected one {PROJECT_ID} project row, got {len(projects)}")
    project = projects[0]
    rows = project.get("document_status") or []
    g1_rows = [row for row in rows if row.get("category") == "g1_required"]
    by_name = {row.get("file_name"): row for row in g1_rows}
    missing = sorted(set(REQUIRED_G1_DOCS) - set(by_name))
    if missing:
        raise AssertionError(f"missing G1 status rows: {missing}")

    head = _git(repo, "rev-parse", "HEAD")
    origin_main = _git(repo, "rev-parse", "origin/main")
    merge_base = _git(repo, "merge-base", "HEAD", "origin/main")
    factory_pg_blob = _git(repo, "rev-parse", "HEAD:hermes_cli/factory_pg.py")

    if merge_base != origin_main:
        raise AssertionError(f"branch is not based on current origin/main: merge_base={merge_base} origin_main={origin_main}")
    if status.get("db_backend") != "agent_core_postgres":
        raise AssertionError(f"unexpected db_backend={status.get('db_backend')!r}")
    expected_root = str(repo)
    if status.get("factory_cli_source_root") != expected_root:
        raise AssertionError(f"factory_cli_source_root={status.get('factory_cli_source_root')!r} expected {expected_root!r}")
    if status.get("factory_status_source_root") != expected_root:
        raise AssertionError(f"factory_status_source_root={status.get('factory_status_source_root')!r} expected {expected_root!r}")
    if status.get("factory_status_delegated") is not False:
        raise AssertionError(f"factory_status_delegated={status.get('factory_status_delegated')!r}; expected False")

    bad_rows: list[str] = []
    for doc in REQUIRED_G1_DOCS:
        row = by_name[doc]
        row_flags = {
            "exists": row.get("exists"),
            "committed": row.get("committed"),
            "indexed": row.get("indexed"),
            "validated": row.get("validated"),
            "reviewed": row.get("reviewed"),
            "blocking": row.get("blocking"),
            "readiness_source": row.get("readiness_source"),
            "base_commit": row.get("base_commit"),
        }
        if not all(row_flags[key] is True for key in ("exists", "committed", "indexed", "validated", "reviewed")):
            bad_rows.append(f"{doc} row flags not all true: {row_flags}")
        if row_flags["blocking"] is not False:
            bad_rows.append(f"{doc} blocking={row_flags['blocking']}")
        if row_flags["readiness_source"] != "configured_base_ref":
            bad_rows.append(f"{doc} readiness_source={row_flags['readiness_source']!r}")
        if row_flags["base_commit"] != origin_main:
            bad_rows.append(f"{doc} base_commit={row_flags['base_commit']!r} origin_main={origin_main}")

        fm = _frontmatter(repo / ARTIFACT_DIR / doc)
        if not _is_true(fm.get("validated")) or not _is_true(fm.get("reviewed")):
            bad_rows.append(f"{doc} frontmatter validated={fm.get('validated')!r} reviewed={fm.get('reviewed')!r}")
    if bad_rows:
        raise AssertionError("\n".join(bad_rows))

    stale_nonblocking = [doc for doc in PROMPT_STALE_TEN if by_name[doc].get("blocking") is False and by_name[doc].get("reviewed") is True]
    if tuple(stale_nonblocking) != PROMPT_STALE_TEN:
        raise AssertionError(f"prompt stale ten did not all read back non-blocking/reviewed: {stale_nonblocking}")

    print("R2cy-R6 G1 readback validation: PASS")
    print(f"repo_root={repo}")
    print(f"runtime_head={head}")
    print(f"configured_base_origin_main={origin_main}")
    print(f"merge_base={merge_base}")
    print(f"factory_pg_parser_blob={factory_pg_blob}")
    print(f"status_json={status_path} bytes={status_path.stat().st_size}")
    print(f"db_backend={status.get('db_backend')} database={status.get('database')}")
    print(f"factory_cli_source_root={status.get('factory_cli_source_root')}")
    print(f"factory_status_source_root={status.get('factory_status_source_root')} delegated={status.get('factory_status_delegated')}")
    print(f"g1_required={len(g1_rows)} blocking=0 prompt_stale_ten_now_nonblocking={len(stale_nonblocking)}")
    print(f"project_reconciliation_anomalies={project.get('metadata', {}).get('reconciliation_anomalies')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

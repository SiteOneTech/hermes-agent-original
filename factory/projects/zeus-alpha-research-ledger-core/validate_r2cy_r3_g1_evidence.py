#!/usr/bin/env python3
"""Validate R2cy-R3 docs-first G1 exact-SHA review dispatch recovery evidence.

Read-only validator (no Factory DB writes). It validates a Factory status JSON
captured with the approved CLI from the assigned R2cy-R3 worktree plus the
committed project-local Markdown pack. It fails if:

- the status payload is not Agent Core Postgres from the assigned worktree;
- the 14 required G1 rows are not clean from current configured origin/main;
- active project metadata is not reconciliation-clean;
- the stale primary checkout is not rejected as not-configured-base;
- the artifact does not record the exact candidate SHAs (PR #99 stale head,
  PR #114 successor head), the gate 1025/1026/1027 evidence, and the boundary;
- the bounded successor rework task (AC3) is not present in the payload.

Usage:
  validate_r2cy_r3_g1_evidence.py --status /tmp/r2cy-r3-status-before.json
      [--project-dir factory/projects/zeus-alpha-research-ledger-core]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, NoReturn

PROJECT_ID = "zeus-alpha-research-ledger-core"
TASK_ID = "zeus-alpha-research-ledger-core-r2cy-r3-docs-first-g1-exact-sha-review-d"
REWORK_TASK_PREFIX = "zeus-alpha-research-ledger-core-r2cy-r3-successor-integrate-r2da-r2-pr-1"
ARTIFACT = "R2CY_R3_DOCS_FIRST_G1_EXACT_SHA_REVIEW_DISPATCH_RECOVERY.md"
EXPECTED_SOURCE_ROOT = "/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2cy-r3-docs-first-g1-exact-sha"
REQUIRED_DOCS = [
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
]
ARTIFACT_MARKERS = [
    "d231dc46cbd38f3d892a26c236903cbea2a889e0",           # exact current base
    "ead1aec54288123ff12c049bc4eb0f29d55d288b",           # stale PR #99 head
    "fe0b6f80bfad296f78d3ab9a6ac79a31298bb243",           # successor PR #114 head
    "gate `1026`",                                        # PR #114 exact-SHA quality
    "gate `1025`",                                        # PR #114 implementation
    "gate `1027`",                                        # PR #99 REQUEST_CHANGES
    "missing_or_unindexed_docs",
    "r2cy-r1-independent-exact-sha-quality-re",
    "no merge",
    "no direct SQL",
    "no primary-checkout mutation",
    "no ALR-020",
]
BOUNDARY_MARKERS = [
    "no merge",
    "no direct SQL",
    "no primary-checkout mutation",
    "no external runtime",
    "no ALR-020",
]


def _fail(msg: str) -> NoReturn:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def _load_status(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive CLI error path
        _fail(f"cannot read status JSON {path}: {exc}")


def validate_status(payload: dict[str, Any], source_root: str) -> None:
    if payload.get("db_backend") != "agent_core_postgres":
        _fail(f"db_backend={payload.get('db_backend')!r}, expected agent_core_postgres")
    if payload.get("factory_cli_source_root") != source_root:
        _fail(f"factory_cli_source_root={payload.get('factory_cli_source_root')!r}")
    if payload.get("factory_status_source_root") != source_root:
        _fail(f"factory_status_source_root={payload.get('factory_status_source_root')!r}")
    if payload.get("factory_status_delegated") is not False:
        _fail(f"factory_status_delegated={payload.get('factory_status_delegated')!r}, expected false")

    projects = [p for p in payload.get("projects", []) if p.get("project_id") == PROJECT_ID]
    if len(projects) != 1:
        _fail(f"expected exactly one project row for {PROJECT_ID}, got {len(projects)}")
    project = projects[0]

    rows = [r for r in project.get("document_status", []) if r.get("category") == "g1_required"]
    if len(rows) != len(REQUIRED_DOCS):
        _fail(f"expected {len(REQUIRED_DOCS)} g1_required rows, got {len(rows)}")
    for row in rows:
        name = row.get("file_name")
        if name not in REQUIRED_DOCS:
            _fail(f"unexpected g1_required row {name!r}")
        for key in ("exists", "committed", "indexed", "validated", "reviewed"):
            if row.get(key) is not True:
                _fail(f"{name}: {key}={row.get(key)!r}, expected true")
        if row.get("blocking") is not False:
            _fail(f"{name}: blocking={row.get('blocking')!r}, expected false")
        if row.get("readiness_source") != "configured_base_ref":
            _fail(f"{name}: readiness_source={row.get('readiness_source')!r}")
        if row.get("base_commit") != "d231dc46cbd38f3d892a26c236903cbea2a889e0":
            _fail(f"{name}: base_commit={row.get('base_commit')!r}")
        if row.get("primary_checkout_accepted") is not False:
            _fail(f"{name}: primary_checkout_accepted={row.get('primary_checkout_accepted')!r}")

    meta = project.get("metadata") or {}
    if meta.get("reconciliation_anomalies") != []:
        _fail(f"reconciliation_anomalies={meta.get('reconciliation_anomalies')!r}, expected []")
    if meta.get("reconciliation_projection_source") != "current_document_status":
        _fail(f"reconciliation_projection_source={meta.get('reconciliation_projection_source')!r}")
    if meta.get("reconciliation_required") is not False:
        _fail(f"reconciliation_required={meta.get('reconciliation_required')!r}, expected false")

    tasks = payload.get("tasks", [])
    r2cy_r1 = [t for t in tasks if t.get("task_id") == "zeus-alpha-research-ledger-core-r2cy-r1-independent-exact-sha-quality-re"]
    if len(r2cy_r1) != 1 or r2cy_r1[0].get("status") != "ready":
        _fail("R2cy-R1 quality-review task must exist and be status=ready in the payload")
    rework = [t for t in tasks if str(t.get("task_id", "")).startswith(REWORK_TASK_PREFIX)]
    if len(rework) != 1:
        _fail(f"expected exactly one routed successor rework task starting with {REWORK_TASK_PREFIX!r}, got {len(rework)}")


def validate_artifact(project_dir: Path) -> None:
    artifact = project_dir / ARTIFACT
    if not artifact.exists():
        _fail(f"artifact missing: {artifact}")
    text = artifact.read_text(encoding="utf-8")
    for marker in ARTIFACT_MARKERS:
        if marker not in text:
            _fail(f"artifact missing marker {marker!r}")
    for marker in BOUNDARY_MARKERS:
        if marker not in text:
            _fail(f"artifact missing boundary marker {marker!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", required=True, help="Factory status JSON from the approved CLI")
    parser.add_argument(
        "--project-dir",
        default="factory/projects/zeus-alpha-research-ledger-core",
        help="project-local docs directory",
    )
    args = parser.parse_args()

    payload = _load_status(Path(args.status))
    validate_status(payload, EXPECTED_SOURCE_ROOT)
    validate_artifact(Path(args.project_dir))

    print(f"OK: {TASK_ID} evidence validated ({len(REQUIRED_DOCS)}/14 required G1 rows clean, "
          "rework task present, artifact markers verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

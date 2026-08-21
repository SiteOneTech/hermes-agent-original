#!/usr/bin/env python3
"""Validate R2cz-R4 bounded current-base docs-first G1 evidence.

Read-only validator. It validates a Factory status JSON captured with the
sanctioned CLI from the assigned R2cz-R4 worktree plus the project-local
Markdown pack. It performs no Factory DB writes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, NoReturn

PROJECT_ID = "zeus-alpha-research-ledger-core"
TASK_ID = "zeus-alpha-research-ledger-core-r2cz-r4-bounded-current-base-docs-first-"
ARTIFACT = "R2CZ_R4_BOUNDED_CURRENT_BASE_DOCS_FIRST_G1_STALE_WORKTREE_RECOVERY.md"
FACTORY_SOURCE = "hermes_cli/factory_pg.py"
EXPECTED_BASE = "bd76d2ac360a447b02cdfaa04ddd5501301a2780"
EXPECTED_SOURCE_ROOT = "/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2cz-r4-bounded-current-base-doc"
SOURCE_REVIEWER = "solution-architect"
SOURCE_REVIEW_GATE = "factory_gate_794"
SOURCE_REVIEW_SHA = "c81547062c5362a7be6f5a1bb2ef9612b29bac9c"
SOURCE_REVIEW_PR = "https://github.com/SiteOneTech/hermes-agent-original/pull/36"
SOURCE_REVIEWED_DOCS_GATE = "factory_gate_790"
SOURCE_REVIEWED_DOCS_SHA = "2476e978c545e24b18ee48844b24eb8c58245ab4"
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
REPAIR_DOCS = [
    ARTIFACT,
    "DOCUMENTATION_INDEX.md",
    "TASK_GRAPH.md",
    "TRACKER.md",
    "QA_GATES.md",
    "SECURITY_GATES.md",
    "G1_REVIEW.md",
]
BOUNDARY_MARKERS = [
    "merge",
    "deploy",
    "direct SQL",
    "primary-checkout mutation",
    "external runtime",
    "force-push",
    "dispatch",
]
ARTIFACT_MARKERS = [
    TASK_ID,
    EXPECTED_BASE,
    EXPECTED_SOURCE_ROOT,
    "_document_frontmatter_flag",
    "/tmp/r2cz-r4-status-before.json",
    "14/14 required G1 rows",
    "reviewed: pending_independent_exact_sha_quality_review",
    "quality-reviewer",
]


def _fail(message: str) -> NoReturn:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def _load_status(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive CLI error path
        _fail(f"cannot read status JSON {path}: {exc}")


def _project(payload: dict[str, Any]) -> dict[str, Any]:
    projects = [p for p in payload.get("projects", []) if p.get("project_id") == PROJECT_ID]
    if len(projects) != 1:
        _fail(f"expected exactly one project {PROJECT_ID}, got {len(projects)}")
    return projects[0]


def _frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        _fail(f"{path.name} missing YAML frontmatter")
    end = text.find("\n---", 4)
    if end < 0:
        _fail(f"{path.name} has unterminated YAML frontmatter")
    metadata: dict[str, str] = {}
    for raw in text[4:end].splitlines():
        if not raw.strip() or raw.lstrip().startswith("#") or ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        metadata[key.strip()] = value.strip().strip("'\"")
    return metadata


def validate_status(payload: dict[str, Any]) -> None:
    if payload.get("db_backend") != "agent_core_postgres":
        _fail(f"db_backend={payload.get('db_backend')!r}, expected agent_core_postgres")
    if payload.get("database") != "zeus_agent":
        _fail(f"database={payload.get('database')!r}, expected zeus_agent")
    if payload.get("factory_cli_source_root") != EXPECTED_SOURCE_ROOT:
        _fail(f"factory_cli_source_root={payload.get('factory_cli_source_root')!r}")
    if payload.get("factory_status_source_root") != EXPECTED_SOURCE_ROOT:
        _fail(f"factory_status_source_root={payload.get('factory_status_source_root')!r}")
    if payload.get("factory_status_delegated") is not False:
        _fail(f"factory_status_delegated={payload.get('factory_status_delegated')!r}, expected false")

    project = _project(payload)
    metadata = project.get("metadata") or {}
    if metadata.get("reconciliation_anomalies") != []:
        _fail(f"reconciliation_anomalies={metadata.get('reconciliation_anomalies')!r}, expected []")
    if metadata.get("reconciliation_projection_source") != "current_document_status":
        _fail(f"reconciliation_projection_source={metadata.get('reconciliation_projection_source')!r}")
    if metadata.get("reconciliation_required") is not False:
        _fail(f"reconciliation_required={metadata.get('reconciliation_required')!r}, expected false")

    rows = [row for row in project.get("document_status", []) if row.get("category") == "g1_required"]
    if len(rows) != len(REQUIRED_DOCS):
        _fail(f"expected {len(REQUIRED_DOCS)} g1_required rows, got {len(rows)}")
    by_name = {str(row.get("file_name")): row for row in rows}
    if set(by_name) != set(REQUIRED_DOCS):
        _fail(f"g1_required row set mismatch: {sorted(by_name)}")
    for name in REQUIRED_DOCS:
        row = by_name[name]
        for key in ("exists", "committed", "indexed", "validated", "reviewed"):
            if row.get(key) is not True:
                _fail(f"{name}: {key}={row.get(key)!r}, expected true")
        if row.get("blocking") is not False:
            _fail(f"{name}: blocking={row.get('blocking')!r}, expected false")
        if row.get("readiness_source") != "configured_base_ref":
            _fail(f"{name}: readiness_source={row.get('readiness_source')!r}")
        if row.get("base_ref") != "origin/main":
            _fail(f"{name}: base_ref={row.get('base_ref')!r}")
        if row.get("base_commit") != EXPECTED_BASE:
            _fail(f"{name}: base_commit={row.get('base_commit')!r}")
        if row.get("configured_base_ref_accepted") is not True:
            _fail(f"{name}: configured base not accepted")
        if row.get("primary_checkout_accepted") is not False:
            _fail(f"{name}: stale primary accepted")
        if row.get("primary_checkout_rejected_reason") != "primary_checkout_not_configured_base":
            _fail(f"{name}: stale primary rejection reason missing")


def validate_frontmatter(project_dir: Path) -> None:
    for name in REQUIRED_DOCS:
        path = project_dir / name
        if not path.exists():
            _fail(f"missing required document {name}")
        fm = _frontmatter(path)
        expected = {
            "validated": "yes",
            "reviewed": "yes",
            "reviewed_by": SOURCE_REVIEWER,
            "review_evidence": SOURCE_REVIEW_GATE,
            "reviewed_candidate_sha": SOURCE_REVIEW_SHA,
            "reviewed_candidate_pr": SOURCE_REVIEW_PR,
            "reviewed_source_gate": SOURCE_REVIEWED_DOCS_GATE,
            "reviewed_source_sha": SOURCE_REVIEWED_DOCS_SHA,
        }
        for key, value in expected.items():
            if fm.get(key) != value:
                _fail(f"{name}: frontmatter {key}={fm.get(key)!r}, expected {value!r}")


def validate_docs(project_dir: Path) -> None:
    repo_root = project_dir.parents[2]
    factory_source = repo_root / FACTORY_SOURCE
    source_text = factory_source.read_text(encoding="utf-8")
    if "def _document_frontmatter_flag" not in source_text:
        _fail("Factory implementation does not expose _document_frontmatter_flag")
    if "_document_frontmatter_flag(file_text, flag)" not in source_text:
        _fail("Factory implementation does not use _document_frontmatter_flag in document status parsing")

    for name in REPAIR_DOCS:
        path = project_dir / name
        if not path.exists():
            _fail(f"missing repair doc {name}")
        text = path.read_text(encoding="utf-8")
        if name == ARTIFACT:
            for marker in ARTIFACT_MARKERS:
                if marker not in text:
                    _fail(f"artifact missing marker {marker!r}")
        if name in {ARTIFACT, "QA_GATES.md", "SECURITY_GATES.md"}:
            for marker in BOUNDARY_MARKERS:
                if marker not in text:
                    _fail(f"{name} missing boundary marker {marker!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", required=True, help="Factory status JSON captured with sanctioned CLI")
    parser.add_argument(
        "--project-dir",
        default="factory/projects/zeus-alpha-research-ledger-core",
        help="project-local docs directory",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir)
    payload = _load_status(Path(args.status))
    validate_status(payload)
    validate_frontmatter(project_dir)
    validate_docs(project_dir)
    print(
        "OK: R2cz-R4 evidence validated "
        f"({len(REQUIRED_DOCS)}/14 required G1 rows clean, frontmatter preserved, "
        "_document_frontmatter_flag present, project-local markers verified)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

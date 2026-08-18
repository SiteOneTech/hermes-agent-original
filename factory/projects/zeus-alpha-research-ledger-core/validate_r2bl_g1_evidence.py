#!/usr/bin/env python3
"""Validate R2bl current-base G1 evidence without touching Factory DB.

This project-local validator is intentionally deterministic: it only reads the
status JSON captured by the approved Factory CLI and the committed Markdown
pack in this checkout. It fails if evidence is stale, unreviewed, from a wrong
base, missing a fresh PR/head binding, or missing independent gate records.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ID = "zeus-alpha-research-ledger-core"
TASK_ID = "zeus-alpha-research-ledger-core-r2bl-non-destructive-canonical-g1-eviden"
ARTIFACT = "R2BL_NON_DESTRUCTIVE_CANONICAL_G1_EVIDENCE_REPAIR.md"
EXPECTED_SOURCE_ROOT = "/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2bl-non-destructive-canonical-g"
ALLOWED_RESIDUAL_TASKS = {
    "zeus-alpha-research-ledger-core-r2ai-current-origin-g1-independent-revie",
    "zeus-alpha-research-ledger-core-r2ae-bounded-canonical-g1-validation-and",
}
TERMINAL_STATUSES = {"done", "superseded", "cancelled", "canceled", "verified", "accepted"}
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
]
BOUNDARY_MARKERS = [
    "no merge",
    "no direct SQL",
    "no primary-checkout mutation",
    "no force-push",
    "no external runtime",
    "no ALR-020/product dispatch",
]


def _load_status(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive CLI error path
        raise AssertionError(f"cannot load status JSON {path}: {exc}") from exc


def _project(data: dict[str, Any]) -> dict[str, Any]:
    for project in data.get("projects") or []:
        if project.get("project_id") == PROJECT_ID:
            return project
    raise AssertionError(f"project {PROJECT_ID} not found in status JSON")


def _frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError(f"{path.name} missing YAML frontmatter")
    end = text.find("\n---", 4)
    if end < 0:
        raise AssertionError(f"{path.name} has unterminated YAML frontmatter")
    metadata: dict[str, str] = {}
    for raw in text[4:end].splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"\'')
    return metadata


def _require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _gate(data: dict[str, Any], gate_id: int) -> dict[str, Any] | None:
    for gate in data.get("gates") or []:
        if gate.get("gate_id") == gate_id:
            return gate
    return None


def validate(args: argparse.Namespace) -> list[str]:
    root = Path(args.project_dir).resolve()
    project_dir = root / "factory" / "projects" / PROJECT_ID
    failures: list[str] = []
    data = _load_status(Path(args.status_json))
    project = _project(data)
    metadata = project.get("metadata") or {}

    _require(data.get("db_backend") == "agent_core_postgres", "status db_backend is not agent_core_postgres", failures)
    _require(data.get("database") == "zeus_agent", "status database is not zeus_agent", failures)
    _require(data.get("factory_cli_source_root") == EXPECTED_SOURCE_ROOT, "status factory_cli_source_root is not assigned R2bl worktree", failures)
    _require(data.get("factory_status_source_root") == EXPECTED_SOURCE_ROOT, "status factory_status_source_root is not assigned R2bl worktree", failures)
    _require(data.get("factory_status_delegated") is False, "status unexpectedly delegated away from assigned worktree", failures)

    rows = [row for row in project.get("document_status") or [] if row.get("category") == "g1_required"]
    by_name = {str(row.get("file_name")): row for row in rows}
    _require(set(by_name) == set(REQUIRED_DOCS), f"required G1 row set mismatch: {sorted(by_name)}", failures)
    for name in REQUIRED_DOCS:
        row = by_name.get(name) or {}
        for key in ("exists", "committed", "indexed", "validated", "reviewed"):
            _require(row.get(key) is True, f"{name} status {key} is not true", failures)
        _require(row.get("blocking") is False, f"{name} is still blocking", failures)
        _require(row.get("readiness_source") == "configured_base_ref", f"{name} readiness_source is not configured_base_ref", failures)
        _require(row.get("base_ref") == "origin/main", f"{name} base_ref is not origin/main", failures)
        _require(row.get("base_commit") == args.expected_base, f"{name} base_commit is not expected current base", failures)
        _require(row.get("configured_base_ref_accepted") is True, f"{name} configured base not accepted", failures)
        _require(row.get("primary_checkout_accepted") is False, f"{name} stale primary accepted", failures)
        _require(row.get("primary_checkout_rejected_reason") == "primary_checkout_not_configured_base", f"{name} stale primary rejection reason missing", failures)

    _require(metadata.get("reconciliation_anomalies") == [], "active project metadata reconciliation_anomalies is not clean", failures)
    _require(metadata.get("reconciliation_projection_source") == "current_document_status", "active project metadata not sourced from current_document_status", failures)
    _require(metadata.get("reconciliation_required") is False, "active project metadata still requires reconciliation", failures)
    _require(metadata.get("g1_documentation_checkout") in (None, {}), "stale g1_documentation_checkout is still active metadata", failures)
    _require(metadata.get("stale_reconciliation_projection") in (None, {}), "stale reconciliation projection is active metadata", failures)

    active_unvalidated: set[str] = set()
    for task in data.get("tasks") or []:
        if task.get("status") in TERMINAL_STATUSES:
            continue
        encoded = json.dumps(task, sort_keys=True, ensure_ascii=False)
        if "unvalidated_required_docs" not in encoded and "missing_or_unindexed_docs" not in encoded:
            continue
        task_id = str(task.get("task_id"))
        task_metadata = task.get("metadata") or {}
        if task_id == TASK_ID:
            _require("unvalidated_required_docs" not in json.dumps(task_metadata, sort_keys=True), "R2bl task itself carries unvalidated_required_docs metadata", failures)
            continue
        active_unvalidated.add(task_id)
        _require(task_id in ALLOWED_RESIDUAL_TASKS, f"unexpected active stale required-doc task {task_id}", failures)
        _require(task_metadata.get("blocker_source") == "structured_reconciliation_metadata", f"{task_id} blocker_source is not structured_reconciliation_metadata", failures)
        _require(task_metadata.get("reconciliation_anomaly") == "unvalidated_required_docs", f"{task_id} reconciliation_anomaly mismatch", failures)
    _require(active_unvalidated == ALLOWED_RESIDUAL_TASKS, f"residual stale task set mismatch: {sorted(active_unvalidated)}", failures)

    artifact_path = project_dir / ARTIFACT
    _require(artifact_path.exists(), f"missing {ARTIFACT}", failures)
    for name in REQUIRED_DOCS:
        doc_path = project_dir / name
        _require(doc_path.exists(), f"missing required doc {name}", failures)
        if doc_path.exists():
            fm = _frontmatter(doc_path)
            _require(fm.get("validated") == "yes", f"{name} frontmatter validated is not yes", failures)
            _require(fm.get("reviewed") == "yes", f"{name} frontmatter reviewed is not yes", failures)
            _require(fm.get("review_evidence") == "factory_gate_794", f"{name} source review evidence changed", failures)
    index_text = _text(project_dir / "DOCUMENTATION_INDEX.md")
    for name in REQUIRED_DOCS:
        _require(f"`{name}`" in index_text, f"DOCUMENTATION_INDEX does not index {name}", failures)

    # Project-local Markdown can name the immutable base and PR URL before the
    # post-push review gates exist. The exact final head/gate binding is
    # validated from canonical Factory status below so we do not create an
    # impossible self-referential commit that must contain its own SHA/gate ids.
    expected_markers = [args.expected_base, args.expected_pr]
    for name in REPAIR_DOCS:
        path = project_dir / name
        _require(path.exists(), f"missing repair doc {name}", failures)
        if path.exists():
            text = _text(path)
            for marker in expected_markers:
                _require(marker in text, f"{name} missing marker {marker}", failures)
    artifact_text = _text(artifact_path) if artifact_path.exists() else ""
    for marker in BOUNDARY_MARKERS:
        _require(marker in artifact_text, f"{ARTIFACT} missing boundary marker '{marker}'", failures)
    _require("structured_reconciliation_metadata" in artifact_text, f"{ARTIFACT} does not name structured residual source", failures)
    _require("R2ai" in artifact_text and "R2ae" in artifact_text, f"{ARTIFACT} does not name the residual stale tasks", failures)
    _require("14/14" in artifact_text, f"{ARTIFACT} does not record 14/14 G1 rows", failures)

    quality_gate = _gate(data, args.expected_quality_gate)
    security_gate = _gate(data, args.expected_security_gate)
    _require(quality_gate is not None, f"quality gate {args.expected_quality_gate} absent from status JSON", failures)
    _require(security_gate is not None, f"security gate {args.expected_security_gate} absent from status JSON", failures)
    for gate, gate_type, reviewer in ((quality_gate, "quality", "quality-reviewer"), (security_gate, "security", "security-reviewer")):
        if not gate:
            continue
        notes = str(gate.get("notes") or "")
        _require(gate.get("project_id") == PROJECT_ID, f"gate {gate.get('gate_id')} project mismatch", failures)
        _require(gate.get("task_id") == TASK_ID, f"gate {gate.get('gate_id')} task mismatch", failures)
        _require(gate.get("gate_type") == gate_type, f"gate {gate.get('gate_id')} type mismatch", failures)
        _require(gate.get("status") == "passed", f"gate {gate.get('gate_id')} did not pass", failures)
        _require(gate.get("reviewer") == reviewer, f"gate {gate.get('gate_id')} reviewer mismatch", failures)
        _require(args.expected_head in notes, f"gate {gate.get('gate_id')} notes missing head SHA", failures)
        _require(args.expected_pr in notes, f"gate {gate.get('gate_id')} notes missing PR URL", failures)
        _require(args.expected_base in notes, f"gate {gate.get('gate_id')} notes missing base SHA", failures)
        _require("no direct SQL" in notes and "no merge" in notes, f"gate {gate.get('gate_id')} notes missing safety boundary", failures)

    if args.expected_head == args.expected_base:
        failures.append("expected head equals base; no repaired commit was validated")
    if not re.fullmatch(r"[0-9a-f]{40}", args.expected_head):
        failures.append("expected head is not a 40-character SHA")
    if not re.fullmatch(r"[0-9a-f]{40}", args.expected_base):
        failures.append("expected base is not a 40-character SHA")
    if not re.fullmatch(r"https://github\.com/SiteOneTech/hermes-agent-original/pull/[0-9]+", args.expected_pr):
        failures.append("expected PR URL is not a SiteOneTech PR URL")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", default=".", help="Repository root for the assigned worktree")
    parser.add_argument("--status-json", required=True, help="Factory status JSON captured with the approved CLI")
    parser.add_argument("--expected-base", required=True, help="Exact current origin/main base SHA")
    parser.add_argument("--expected-head", required=True, help="Exact final pushed PR head SHA")
    parser.add_argument("--expected-pr", required=True, help="Exact non-draft GitHub PR URL")
    parser.add_argument("--expected-quality-gate", required=True, type=int, help="Canonical Factory quality gate id")
    parser.add_argument("--expected-security-gate", required=True, type=int, help="Canonical Factory security gate id")
    args = parser.parse_args()
    failures = validate(args)
    if failures:
        print("R2BL_G1_EVIDENCE_VALIDATION=FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("R2BL_G1_EVIDENCE_VALIDATION=PASS")
    print(f"project={PROJECT_ID}")
    print(f"base={args.expected_base}")
    print(f"head={args.expected_head}")
    print(f"pr={args.expected_pr}")
    print(f"quality_gate=factory_gate_{args.expected_quality_gate}")
    print(f"security_gate=factory_gate_{args.expected_security_gate}")
    print("required_g1_rows=14/14 reviewed non-blocking from configured_base_ref")
    return 0


if __name__ == "__main__":
    sys.exit(main())

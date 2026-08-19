#!/usr/bin/env python3
"""Validate R2dg bounded G1 exact-SHA independent-review recovery evidence.

Read-only validator (no Factory DB writes). It validates a Factory status
JSON captured with the approved CLI from the assigned R2dg worktree plus the
committed project-local Markdown pack. It fails if G1 rows are not clean from
current configured origin/main, if the 14 required document frontmatter
markers lose their independent PR #36/gate 794 provenance, if the R2dg
quality gate is not bound to the exact candidate, or if the residual
dispatch blocker evidence is not recorded.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ID = "zeus-alpha-research-ledger-core"
TASK_ID = "zeus-alpha-research-ledger-core-r2dg-bounded-g1-exact-sha-independent-re"
ARTIFACT = "R2DG_BOUNDED_G1_EXACT_SHA_INDEPENDENT_REVIEW_RECOVERY.md"
EXPECTED_SOURCE_ROOT = "/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/inc-001-r2dg-bounded-g1-exact-sha-indepe"
SOURCE_REVIEWER = "solution-architect"
SOURCE_REVIEW_GATE = "factory_gate_794"
SOURCE_REVIEW_SHA = "c81547062c5362a7be6f5a1bb2ef9612b29bac9c"
SOURCE_REVIEW_PR = "https://github.com/SiteOneTech/hermes-agent-original/pull/36"
SOURCE_REVIEWED_DOCS_GATE = "factory_gate_790"
SOURCE_REVIEWED_DOCS_SHA = "2476e978c545e24b18ee48844b24eb8c58245ab4"
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
CANDIDATE_MARKERS = [
    "candidate readiness",
    "base readiness",
    "stale primary",
    "configured_base_ref",
    "rate-limited R2ai path",
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
    project = data.get("project") or {}
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


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def _gate(data: dict[str, Any], gate_id: int) -> dict[str, Any] | None:
    for gate in data.get("gates") or []:
        if gate.get("gate_id") == gate_id:
            return gate
    return None


def _validate_current_document_rows(
    project: dict[str, Any],
    expected_base: str,
    failures: list[str],
) -> None:
    rows = [row for row in project.get("document_status") or [] if row.get("category") == "g1_required"]
    row_names = [str(row.get("file_name")) for row in rows]
    duplicate_names = sorted({name for name in row_names if row_names.count(name) > 1})
    _require(len(rows) == len(REQUIRED_DOCS), f"required G1 row count is {len(rows)}, expected {len(REQUIRED_DOCS)}", failures)
    _require(not duplicate_names, f"duplicate required G1 rows found: {duplicate_names}", failures)
    by_name = {str(row.get("file_name")): row for row in rows}
    _require(set(by_name) == set(REQUIRED_DOCS), f"required G1 row set mismatch: {sorted(by_name)}", failures)
    for name in REQUIRED_DOCS:
        row = by_name.get(name) or {}
        for key in ("exists", "committed", "indexed", "validated", "reviewed"):
            _require(row.get(key) is True, f"{name} status {key} is not true", failures)
        _require(row.get("blocking") is False, f"{name} is still blocking", failures)
        _require(row.get("readiness_source") == "configured_base_ref", f"{name} readiness_source is not configured_base_ref", failures)
        _require(row.get("base_ref") == "origin/main", f"{name} base_ref is not origin/main", failures)
        _require(row.get("base_commit") == expected_base, f"{name} base_commit is not expected current base", failures)
        _require(row.get("configured_base_ref_accepted") is True, f"{name} configured base not accepted", failures)
        _require(row.get("primary_checkout_accepted") is False, f"{name} stale primary accepted", failures)
        _require(
            row.get("primary_checkout_rejected_reason") == "primary_checkout_not_configured_base",
            f"{name} stale primary rejection reason missing",
            failures,
        )


def _validate_required_doc_frontmatter(project_dir: Path, failures: list[str]) -> None:
    for name in REQUIRED_DOCS:
        doc_path = project_dir / name
        _require(doc_path.exists(), f"missing required doc {name}", failures)
        if not doc_path.exists():
            continue
        fm = _frontmatter(doc_path)
        _require(fm.get("validated") == "yes", f"{name} frontmatter validated is not yes", failures)
        _require(fm.get("reviewed") == "yes", f"{name} frontmatter reviewed is not yes", failures)
        _require(fm.get("reviewed_by") == SOURCE_REVIEWER, f"{name} reviewed_by is not {SOURCE_REVIEWER}", failures)
        _require(fm.get("review_evidence") == SOURCE_REVIEW_GATE, f"{name} source review evidence changed", failures)
        _require(fm.get("reviewed_candidate_sha") == SOURCE_REVIEW_SHA, f"{name} reviewed_candidate_sha changed", failures)
        _require(fm.get("reviewed_candidate_pr") == SOURCE_REVIEW_PR, f"{name} reviewed_candidate_pr changed", failures)
        _require(fm.get("reviewed_source_gate") == SOURCE_REVIEWED_DOCS_GATE, f"{name} reviewed_source_gate changed", failures)
        _require(fm.get("reviewed_source_sha") == SOURCE_REVIEWED_DOCS_SHA, f"{name} reviewed_source_sha changed", failures)


def _validate_active_metadata(project: dict[str, Any], failures: list[str]) -> None:
    metadata = project.get("metadata") or {}
    _require(metadata.get("reconciliation_anomalies") == [], "active project metadata reconciliation_anomalies is not clean", failures)
    _require(
        metadata.get("reconciliation_projection_source") in (None, "current_document_status"),
        "active project metadata has stale reconciliation_projection_source",
        failures,
    )
    _require(metadata.get("reconciliation_required") is False, "active project metadata still requires reconciliation", failures)


def _validate_residual_tasks(data: dict[str, Any], failures: list[str]) -> None:
    active_unvalidated: set[str] = set()
    for task in data.get("tasks") or []:
        if task.get("status") in TERMINAL_STATUSES:
            continue
        # Residual anomaly detection scans structured task METADATA only.
        # Task description/acceptance prose may legitimately quote the
        # historical strings (e.g. R2df describes the R2ae blocker) without
        # carrying active anomaly state.
        task_metadata = task.get("metadata") or {}
        encoded_metadata = json.dumps(task_metadata, sort_keys=True, ensure_ascii=False)
        if "unvalidated_required_docs" not in encoded_metadata and "missing_or_unindexed_docs" not in encoded_metadata:
            continue
        task_id = str(task.get("task_id"))
        if task_id == TASK_ID:
            _require(
                "unvalidated_required_docs" not in encoded_metadata,
                f"{task_id} carries unvalidated_required_docs metadata",
                failures,
            )
            continue
        active_unvalidated.add(task_id)
        _require(task_id in ALLOWED_RESIDUAL_TASKS, f"unexpected active stale required-doc task {task_id}", failures)
        _require(
            task_metadata.get("blocker_source") == "structured_reconciliation_metadata",
            f"{task_id} blocker_source is not structured_reconciliation_metadata",
            failures,
        )
        _require(
            task_metadata.get("reconciliation_anomaly") == "unvalidated_required_docs",
            f"{task_id} reconciliation_anomaly mismatch",
            failures,
        )
    _require(active_unvalidated == ALLOWED_RESIDUAL_TASKS, f"residual stale task set mismatch: {sorted(active_unvalidated)}", failures)


def _validate_repair_docs(project_dir: Path, args: argparse.Namespace, failures: list[str]) -> None:
    # A commit cannot contain its own SHA (canonical project rule: the exact
    # final PR head SHA belongs in the PR body and Factory gate records). The
    # docs therefore cite the base SHA, the PR URL, the evidence commit SHA,
    # and the gate id; the PR head itself is verified via GitHub readback and
    # the gate notes.
    expected_markers = [
        args.expected_base,
        args.expected_evidence_head,
        args.expected_pr,
        str(args.expected_quality_gate),
    ]
    for name in REPAIR_DOCS:
        path = project_dir / name
        _require(path.exists(), f"missing repair doc {name}", failures)
        if not path.exists():
            continue
        text = _text(path)
        for marker in expected_markers:
            _require(marker in text, f"{name} missing marker {marker}", failures)
    index_text = _text(project_dir / "DOCUMENTATION_INDEX.md")
    for name in REQUIRED_DOCS:
        _require(f"`{name}`" in index_text, f"DOCUMENTATION_INDEX does not index {name}", failures)

    artifact_path = project_dir / ARTIFACT
    artifact_text = _text(artifact_path) if artifact_path.exists() else ""
    normalized = _normalized_text(artifact_text).lower()
    for marker in BOUNDARY_MARKERS:
        _require(marker.lower() in normalized, f"{ARTIFACT} missing boundary marker '{marker}'", failures)
    for marker in CANDIDATE_MARKERS:
        _require(marker.lower() in normalized, f"{ARTIFACT} missing candidate/base marker '{marker}'", failures)
    _require("9ea2756e6bfbce9d07c7ce32319a8b64bd8cea15" in normalized, f"{ARTIFACT} does not name exact candidate SHA", failures)
    _require("14/14" in normalized, f"{ARTIFACT} does not record 14/14 G1 rows", failures)
    _require("security-reviewer" in normalized, f"{ARTIFACT} does not name independent security owner", failures)
    _require("unresolved_validation_tasks" in normalized or "dispatch-preflight" in normalized, f"{ARTIFACT} does not record dispatch blocker evidence", failures)


def _validate_r2dg_quality_gate(data: dict[str, Any], args: argparse.Namespace, failures: list[str]) -> None:
    quality_gate = _gate(data, args.expected_quality_gate)
    _require(quality_gate is not None, f"quality gate {args.expected_quality_gate} absent from status JSON", failures)
    if not quality_gate:
        return
    notes = str(quality_gate.get("notes") or "")
    _require(quality_gate.get("project_id") == PROJECT_ID, f"gate {quality_gate.get('gate_id')} project mismatch", failures)
    _require(quality_gate.get("task_id") in (None, TASK_ID), f"gate {quality_gate.get('gate_id')} task mismatch", failures)
    _require(quality_gate.get("gate_type") == "quality", f"gate {quality_gate.get('gate_id')} type mismatch", failures)
    _require(quality_gate.get("status") == "passed", f"gate {quality_gate.get('gate_id')} did not pass", failures)
    _require(quality_gate.get("reviewer") == "quality-reviewer", f"gate {quality_gate.get('gate_id')} reviewer mismatch", failures)
    for marker in (TASK_ID, args.expected_base, args.expected_evidence_head, args.expected_pr):
        _require(marker in notes, f"gate {quality_gate.get('gate_id')} notes missing {marker}", failures)
    _require("no direct SQL" in notes and "no merge" in notes, f"gate {quality_gate.get('gate_id')} notes missing safety boundary", failures)


def validate(args: argparse.Namespace) -> list[str]:
    root = Path(args.project_dir).resolve()
    project_dir = root / "factory" / "projects" / PROJECT_ID
    failures: list[str] = []
    data = _load_status(Path(args.status_json))
    project = _project(data)

    _require(data.get("db_backend") == "agent_core_postgres", "status db_backend is not agent_core_postgres", failures)
    _require(data.get("database") == "zeus_agent", "status database is not zeus_agent", failures)

    _validate_current_document_rows(project, args.expected_base, failures)
    _validate_required_doc_frontmatter(project_dir, failures)
    _validate_active_metadata(project, failures)
    _validate_residual_tasks(data, failures)
    _validate_repair_docs(project_dir, args, failures)
    _validate_r2dg_quality_gate(data, args, failures)

    for attr in ("expected_base", "expected_evidence_head"):
        value = getattr(args, attr)
        if not re.fullmatch(r"[0-9a-f]{40}", value):
            failures.append(f"{attr} is not a 40-character SHA")
    if args.expected_evidence_head == args.expected_base:
        failures.append("expected evidence head equals base; no R2dg commit was validated")
    if not re.fullmatch(r"https://github\.com/SiteOneTech/hermes-agent-original/pull/[0-9]+", args.expected_pr):
        failures.append("expected_pr is not a SiteOneTech PR URL")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", default=".", help="Repository root for the assigned worktree")
    parser.add_argument("--status-json", required=True, help="Factory status JSON captured with the approved CLI")
    parser.add_argument("--expected-base", required=True, help="Exact current origin/main base SHA for R2dg")
    parser.add_argument("--expected-evidence-head", required=True, help="Exact R2dg evidence commit SHA (PR head as recorded in gate notes)")
    parser.add_argument("--expected-pr", required=True, help="Exact non-draft R2dg GitHub PR URL")
    parser.add_argument("--expected-quality-gate", required=True, type=int, help="Canonical Factory quality gate id for R2dg")
    args = parser.parse_args()
    failures = validate(args)
    if failures:
        print("R2DG_G1_EVIDENCE_VALIDATION=FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("R2DG_G1_EVIDENCE_VALIDATION=PASS")
    print(f"project={PROJECT_ID}")
    print(f"base={args.expected_base}")
    print(f"evidence_head={args.expected_evidence_head}")
    print(f"pr={args.expected_pr}")
    print(f"quality_gate=factory_gate_{args.expected_quality_gate}")
    print("required_g1_rows=14/14 reviewed non-blocking from configured_base_ref")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Canonical Factory status sync.

Reads only Agent Core Postgres through factory_backend. Emits a deterministic
JSON snapshot for dashboards/cron; no SQLite fallback.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
if REPO.exists() and str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

DONE = {"done", "completed", "verified", "cancelled", "superseded"}
ACTIVE_RUNS = {"queued", "running"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _counts(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key) or "unknown")
        out[value] = out.get(value, 0) + 1
    return out


def main() -> None:
    try:
        from hermes_cli import factory_backend

        db = factory_backend.get_backend()
        payload = db.status()
        projects = payload.get("projects", [])
        tasks = payload.get("tasks", [])
        gates = payload.get("gates", [])
        runs = payload.get("task_runs", [])
        alerts = payload.get("alerts", [])
        summaries = []
        for project in projects:
            pid = project["project_id"]
            ptasks = [t for t in tasks if t.get("project_id") == pid]
            pruns = [r for r in runs if r.get("project_id") == pid and str(r.get("status")) in ACTIVE_RUNS]
            palerts = [a for a in alerts if a.get("project_id") == pid]
            summaries.append(
                {
                    "project_id": pid,
                    "name": project.get("name"),
                    "status": project.get("status"),
                    "autonomous_enabled": project.get("autonomous_enabled"),
                    "task_counts": _counts(ptasks, "status"),
                    "open_tasks": len([t for t in ptasks if str(t.get("status")) not in DONE]),
                    "active_runs": len(pruns),
                    "current_run": pruns[0] if pruns else None,
                    "alerts": len(palerts),
                }
            )
        report = {
            "job": "factory_status_sync",
            "db_backend": payload.get("db_backend"),
            "timestamp": _now(),
            "summary": {
                "projects": len(projects),
                "tasks": len(tasks),
                "gates": len(gates),
                "active_runs": len([r for r in runs if str(r.get("status")) in ACTIVE_RUNS]),
                "alerts": len(alerts),
            },
            "projects": summaries,
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
    except Exception as exc:
        print(json.dumps({"job": "factory_status_sync", "error": str(exc), "timestamp": _now()}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()

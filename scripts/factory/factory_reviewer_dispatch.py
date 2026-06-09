#!/usr/bin/env python3
"""Canonical Factory reviewer dispatch report.

No project-specific cron and no SQLite: scans Factory DB for review-ready tasks
and reports whether independent reviewers are assigned.
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


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _cross_review_engine(engine: str) -> str:
    return {"claude_code": "codex", "codex": "claude_code", "openhands": "claude_code", "zeus": "codex"}.get(engine, "codex")


def main() -> None:
    try:
        from hermes_cli import factory_backend

        db = factory_backend.get_backend()
        payload = db.status()
        agents = payload.get("agents", [])
        agent_ids = {a.get("agent_id") for a in agents}
        review_tasks = [
            t for t in payload.get("tasks", [])
            if str(t.get("status") or "") in {"review_ready", "qa_ready", "review_pending_human"}
        ]
        pending: list[dict[str, Any]] = []
        ready: list[dict[str, Any]] = []
        for task in review_tasks:
            reviewer = task.get("reviewer_agent_id") or task.get("reviewer_profile")
            if reviewer and reviewer in agent_ids and reviewer != (task.get("owner_agent_id") or task.get("owner_profile")):
                ready.append({"task_id": task.get("task_id"), "project_id": task.get("project_id"), "title": task.get("title"), "reviewer": reviewer})
            else:
                suggested_engine = _cross_review_engine(str(task.get("engine") or "zeus"))
                pending.append(
                    {
                        "task_id": task.get("task_id"),
                        "project_id": task.get("project_id"),
                        "title": task.get("title"),
                        "implementer": task.get("owner_agent_id") or task.get("owner_profile"),
                        "suggested_review_engine": suggested_engine,
                        "suggested_reviewers": [a.get("agent_id") for a in agents if a.get("preferred_engine") == suggested_engine],
                    }
                )
        print(json.dumps({
            "job": "factory_reviewer_dispatch",
            "db_backend": payload.get("db_backend"),
            "timestamp": _now(),
            "summary": {"tasks_ready_for_review": len(review_tasks), "pending_reviewer_assignment": len(pending), "ready_with_reviewer": len(ready)},
            "pending_reviewer_assignment": pending,
            "ready_with_reviewer": ready,
        }, ensure_ascii=False, indent=2))
    except Exception as exc:
        print(json.dumps({"job": "factory_reviewer_dispatch", "error": str(exc), "timestamp": _now()}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()

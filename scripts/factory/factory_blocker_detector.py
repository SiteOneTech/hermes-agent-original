#!/usr/bin/env python3
"""Canonical Factory blocker detector.

Classifies blocked/stuck Factory tasks from Agent Core Postgres only, records
runtime actions, and creates human_questions only when a human decision is truly
indispensable. No SQLite and no project-specific paths.
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


def _counts(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key) or "unknown")
        out[value] = out.get(value, 0) + 1
    return out


def main() -> None:
    try:
        from hermes_cli import factory_backend, factory_pg

        db = factory_backend.get_backend()
        payload = db.status()
        classified = factory_pg.classify_factory_blockers(payload)
        action_result = factory_pg.record_factory_blocker_actions(classified, payload=payload)
        # Refresh after actions/questions so alert logic sees any question rows just created.
        payload_after = db.status()
        alerts = factory_pg.factory_watchdog_alerts(payload_after)
        report = {
            "job": "factory_blocker_detector",
            "db_backend": payload_after.get("db_backend"),
            "timestamp": _now(),
            "summary": {
                "classified": len(classified),
                "action_categories": _counts(classified, "action_category"),
                "blocker_categories": _counts(classified, "blocker_category"),
                "questions_created": action_result.get("questions_created", 0),
                "alerts": len(alerts),
            },
            "action_result": action_result,
            "blocked_tasks": classified,
            "alerts": alerts,
            "needs_attention": bool(alerts or any(item.get("requires_human") for item in classified)),
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
    except Exception as exc:
        print(json.dumps({"job": "factory_blocker_detector", "error": str(exc), "timestamp": _now()}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()

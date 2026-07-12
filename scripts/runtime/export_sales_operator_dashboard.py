#!/usr/bin/env python3
"""Export a safe Sales Operator dashboard snapshot for the OTP-protected /user surface.

The delivery sandbox has no DB credentials. This host-side script runs inside the
Hermes runtime context, queries Agent Core through the Sales Operator tool, and
writes a redacted JSON snapshot to the sandbox user-data directory.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.sales_operator_tool import _handle_dashboard_snapshot  # noqa: E402


def _payload(raw: str) -> dict[str, Any]:
    data = json.loads(raw)
    if not data.get("ok"):
        raise SystemExit(data.get("error") or raw[:1000])
    return data


def export_snapshot(target: Path, campaign_id: str | None, prospect_limit: int, report_limit: int) -> dict[str, Any]:
    snapshot = _payload(_handle_dashboard_snapshot({
        "campaign_id": campaign_id,
        "prospect_limit": prospect_limit,
        "report_limit": report_limit,
    }))
    snapshot["generated_at"] = datetime.now(timezone.utc).isoformat()
    snapshot["redaction"] = {
        "scope": "private-user-dashboard-safe-snapshot",
        "notes": "No provider secrets or raw runtime credentials are included.",
    }
    target.mkdir(parents=True, exist_ok=True)
    output = target / "sales_operator_dashboard.json"
    tmp = output.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(output)
    output.chmod(0o644)
    return {"output": str(output), "summary": snapshot.get("summary", {}), "campaign": snapshot.get("campaign")}


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Sales Operator dashboard JSON into delivery sandbox user-data")
    parser.add_argument("--target", type=Path, required=True, help="Delivery sandbox user-data directory")
    parser.add_argument("--campaign-id", default=None)
    parser.add_argument("--prospect-limit", type=int, default=50)
    parser.add_argument("--report-limit", type=int, default=30)
    args = parser.parse_args()
    result = export_snapshot(args.target, args.campaign_id, args.prospect_limit, args.report_limit)
    print(json.dumps({"ok": True, **result}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

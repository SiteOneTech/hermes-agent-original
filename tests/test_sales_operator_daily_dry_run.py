import json
import sys
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parents[1] / "scripts" / "runtime"
sys.path.insert(0, str(RUNTIME_DIR))
from scripts.runtime import sales_operator_daily_dry_run as dry_run


def _snapshot(prospects=0, research=0, attack_plans=0, open_outreach=0, attempts=0):
    return {
        "ok": True,
        "campaign": {
            "campaign_id": "empleado-uno-1000-subscribers-q3-2026",
            "product_name": "Empleado.uno",
            "referral_code": "zeus",
        },
        "summary": {
            "prospects": prospects,
            "contacted_clients": 0,
            "research_snapshots": research,
            "attack_plans": attack_plans,
            "open_outreach": open_outreach,
            "attempts": attempts,
            "daily_reports": 1,
            "territories": 1,
        },
        "channels": [
            {"channel": "email", "status": "active", "mode": "supervised_send", "daily_limit": 25, "requires_human_approval": True},
            {"channel": "whatsapp_current", "status": "draft_only", "mode": "draft_only", "daily_limit": 0, "requires_human_approval": True},
        ],
        "territories": [
            {"country": "Colombia", "city": "Medellín", "vertical": "clínicas/estética", "status": "active", "priority": 95}
        ],
        "reports": [{"report_date": "2026-07-12", "work_summary": "Jornada 0"}],
        "prospects": [],
        "graph": [],
    }


def test_build_daily_dry_run_prioritizes_first_public_lead_batch_and_never_sends():
    result = dry_run.build_daily_dry_run(_snapshot(prospects=0), [], generated_at=dry_run.datetime(2026, 7, 12, tzinfo=dry_run.timezone.utc))

    assert result["ok"] is True
    assert result["dry_run"] is True
    assert result["external_sends"] is False
    assert result["metrics"]["external_messages_sent_by_dry_run"] == 0
    assert result["priority_actions"][0]["loop"] == "lead_discovery_tick"
    assert result["priority_actions"][0]["target"]["source_policy"] == "public_business_sources_only"
    assert all(action["external_send"] is False for action in result["priority_actions"])
    assert all(spec["enabled_by_default"] is False for spec in result["cron_specs"])
    assert "Do not send" in result["cron_specs"][0]["self_contained_prompt"]


def test_build_daily_dry_run_reviews_queue_without_provider_execution():
    queue = [
        {
            "outreach_id": "q1",
            "prospect_id": "p1",
            "prospect_name": "Clínica Demo",
            "channel": "email",
            "status": "draft",
            "requires_approval": True,
            "approval_status": "pending",
            "policy_mode": "supervised_send",
        }
    ]

    result = dry_run.build_daily_dry_run(_snapshot(prospects=1, research=1, attack_plans=1, open_outreach=1), queue)
    queue_actions = [a for a in result["priority_actions"] if a["loop"] == "follow_up_queue_dry_run"]

    assert queue_actions
    assert queue_actions[0]["target"]["queue_rows_reviewed"] == 1
    assert queue_actions[0]["target"]["approval_required"] == 1
    assert "external_send_disabled_by_i6_dry_run" in queue_actions[0]["blockers"]
    assert result["safety"]["external_message_senders_called"] is False


def test_run_daily_dry_run_default_does_not_write_report(monkeypatch, tmp_path):
    calls = {"report": 0}

    monkeypatch.setattr(dry_run, "load_snapshot", lambda campaign_id, prospect_limit, report_limit: _snapshot(prospects=0))
    monkeypatch.setattr(dry_run, "load_queue_rows", lambda campaign_id, limit=50: [])

    def fake_write_report(*args, **kwargs):
        calls["report"] += 1
        return {"ok": True}

    monkeypatch.setattr(dry_run, "write_report_from_dry_run", fake_write_report)
    target = tmp_path / "dry-run.json"

    result = dry_run.run_daily_dry_run(
        campaign_id="empleado-uno-1000-subscribers-q3-2026",
        prospect_limit=5,
        report_limit=5,
        queue_limit=5,
        target=target,
    )

    assert calls["report"] == 0
    assert target.exists()
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["dry_run"] is True
    assert result["safety"]["db_writes_by_default"] is False


def test_run_daily_dry_run_write_report_requires_explicit_flag(monkeypatch):
    calls = {"report": 0}

    monkeypatch.setattr(dry_run, "load_snapshot", lambda campaign_id, prospect_limit, report_limit: _snapshot(prospects=1, research=0))
    monkeypatch.setattr(dry_run, "load_queue_rows", lambda campaign_id, limit=50: [])

    def fake_write_report(payload, report_date=None):
        calls["report"] += 1
        assert payload["external_sends"] is False
        return {"ok": True, "report": {"report_date": report_date}}

    monkeypatch.setattr(dry_run, "write_report_from_dry_run", fake_write_report)

    result = dry_run.run_daily_dry_run(
        campaign_id="empleado-uno-1000-subscribers-q3-2026",
        prospect_limit=5,
        report_limit=5,
        queue_limit=5,
        write_report=True,
        report_date="2026-07-12",
    )

    assert calls["report"] == 1
    assert result["report_write"]["report"]["report_date"] == "2026-07-12"

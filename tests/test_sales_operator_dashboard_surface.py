import json
import sys
import types
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parents[1] / "scripts" / "runtime"
sys.path.insert(0, str(RUNTIME_DIR))
from scripts.runtime import export_sales_operator_dashboard as exporter
from scripts.runtime import publish_delivery_sandbox as publisher


def _server_module(tmp_path):
    module = types.ModuleType("generated_delivery_server_sales_operator")
    exec(publisher.SERVER_PY, module.__dict__)
    setattr(module, "EVENT_DIR", tmp_path / "events")
    setattr(module, "PUBLIC_DIR", tmp_path / "public")
    setattr(module, "USER_DATA_DIR", tmp_path / "user-data")
    getattr(module, "USER_DATA_DIR").mkdir(parents=True)
    setattr(module, "ALLOWED_HOSTS", set())
    return module


def test_sales_operator_dashboard_renders_snapshot(tmp_path):
    server = _server_module(tmp_path)
    (server.USER_DATA_DIR / "sales_operator_dashboard.json").write_text(
        json.dumps(
            {
                "campaign": {
                    "product_name": "Empleado.uno",
                    "target_subscribers": 1000,
                    "referral_code": "zeus",
                    "bonus_offer": "50% extra en créditos",
                },
                "summary": {
                    "prospects": 2,
                    "contacted_clients": 1,
                    "research_snapshots": 2,
                    "attack_plans": 1,
                    "open_outreach": 1,
                    "attempts": 1,
                    "daily_reports": 1,
                    "territories": 1,
                },
                "channels": [{"channel": "email", "status": "active", "mode": "supervised_send", "daily_limit": 25, "requires_human_approval": True, "notes": "solo personalizado"}],
                "territories": [{"country": "Colombia", "city": "Medellín", "vertical": "clínicas/estética", "status": "active", "priority": 95}],
                "reports": [{"report_date": "2026-07-12", "work_summary": "Jornada 0", "actions_taken": ["seed"], "learnings": ["no spam"], "next_actions": ["investigar"], "retrospective": "fail-closed"}],
                "prospects": [{"name": "Clínica Demo", "city": "Medellín", "vertical": "clínicas/estética", "status": "contacted", "fit_score": 86, "contact_name": "Ana", "next_action": "demo"}],
                "graph": [{"report_date": "2026-07-12", "prospects_researched": 2, "attacks_prepared": 1, "messages_sent": 1, "responses": 0, "wins": 0}],
                "generated_at": "2026-07-12T00:00:00Z",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    html = server._sales_operator_dashboard_page({"user_id": "qa"})

    assert "Empleado.uno activo" in html
    assert "Sales Operator Core" in html
    assert "Jornadas de trabajo" in html
    assert "CRM rápido" in html
    assert "Clínica Demo" in html
    assert "salesOperatorChart" in html


def test_export_sales_operator_dashboard_snapshot_writes_safe_json(tmp_path, monkeypatch):
    def fake_snapshot(args):
        assert args["campaign_id"] == "empleado-uno"
        return json.dumps({"ok": True, "campaign": {"campaign_id": "empleado-uno"}, "summary": {"prospects": 1}, "channels": [], "territories": [], "reports": [], "prospects": [], "graph": []})

    monkeypatch.setattr(exporter, "_handle_dashboard_snapshot", fake_snapshot)

    result = exporter.export_snapshot(tmp_path, "empleado-uno", prospect_limit=10, report_limit=5)
    data = json.loads(Path(result["output"]).read_text(encoding="utf-8"))

    assert data["campaign"]["campaign_id"] == "empleado-uno"
    assert data["summary"]["prospects"] == 1
    assert data["generated_at"]
    assert data["redaction"]["scope"] == "private-user-dashboard-safe-snapshot"

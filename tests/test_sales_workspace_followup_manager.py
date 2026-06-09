import importlib.util
from pathlib import Path


def load_manager():
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "runtime" / "sales_workspace_followup_manager.py"
    spec = importlib.util.spec_from_file_location("sales_workspace_followup_manager", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_needs_escalation_for_rejection_annoyance_pdf_and_button_bugs():
    manager = load_manager()

    assert manager.needs_escalation("no sirve aceptar y no se lee la descripcion en el pdf") is True
    assert manager.needs_escalation("el botón de rechazar no hace nada") is True
    assert manager.needs_escalation("estoy molesto con la factura") is True
    assert manager.needs_escalation("lo rechazo", "rejected") is True
    assert manager.needs_escalation("gracias, ya funcionó") is False


def test_process_sales_comments_inserts_visible_agent_reply_and_marks_customer_event(monkeypatch):
    manager = load_manager()
    statements = []
    updates = []
    refreshes = []
    followups = []

    row = {
        "workspace_id": "workspace-1",
        "public_token": "token-1",
        "public_url": "https://zeus-sandbox.kidu.app/w/token-1/",
        "document_type": "quote",
        "document_id": "quote-1",
        "customer_email": "client@example.com",
        "customer_name": "Cliente",
        "status": "commented",
        "workspace_metadata": {"public_document_number": "Q-1"},
        "workspace_event_id": 77,
        "event_type": "commented",
        "actor_type": "customer",
        "actor_ref": "client@example.com",
        "comment": "ya funcionó, gracias",
        "event_metadata": {},
    }

    monkeypatch.setattr(manager, "pending_sales_customer_events", lambda: [row])

    def fake_statement_one(statement, **kwargs):
        statements.append(statement)
        if "crm.follow_ups" in statement:
            followups.append(statement)
            return {"follow_up_id": "fu-1"}
        return {"workspace_event_id": 88}

    monkeypatch.setattr(manager.sql, "statement_one", fake_statement_one)
    monkeypatch.setattr(manager.sql, "psql", lambda statement, **kwargs: updates.append(statement))
    monkeypatch.setattr(manager, "refresh_sales_comments_json", lambda workspace_id, public_token: refreshes.append((workspace_id, public_token)) or "comments.json")

    messages = manager.process_sales_comments()

    assert messages == []
    assert followups == []
    assert statements
    assert "'commented', 'agent'" in statements[0]
    assert "Zeus de SitioUno" in statements[0]
    assert "reply_to_event_id" in statements[0]
    assert updates and "agent_responded" in updates[0]
    assert refreshes == [("workspace-1", "token-1")]


def test_process_sales_comments_escalates_rejections_and_customer_issues(monkeypatch):
    manager = load_manager()
    statements = []
    updates = []
    refreshes = []

    row = {
        "workspace_id": "workspace-1",
        "public_token": "token-1",
        "public_url": "https://zeus-sandbox.kidu.app/w/token-1/",
        "document_type": "quote",
        "document_id": "quote-1",
        "customer_email": "client@example.com",
        "customer_name": "Cliente",
        "status": "pending",
        "workspace_metadata": {"public_document_number": "Q-1"},
        "workspace_event_id": 78,
        "event_type": "commented",
        "actor_type": "customer",
        "actor_ref": "client@example.com",
        "comment": "no sirve aceptar y el PDF está descuadrado",
        "event_metadata": {},
    }

    monkeypatch.setattr(manager, "pending_sales_customer_events", lambda: [row])
    monkeypatch.setattr(manager.sql, "statement_one", lambda statement, **kwargs: statements.append(statement) or {"workspace_event_id": 89, "follow_up_id": "fu-1"})
    monkeypatch.setattr(manager.sql, "psql", lambda statement, **kwargs: updates.append(statement))
    monkeypatch.setattr(manager, "refresh_sales_comments_json", lambda workspace_id, public_token: refreshes.append((workspace_id, public_token)) or "comments.json")

    messages = manager.process_sales_comments()

    assert len(messages) == 1
    assert "Escalación en Q-1" in messages[0]
    assert any("crm.follow_ups" in statement for statement in statements)
    assert any("escalated_to_owner" in statement for statement in statements)
    assert updates and "escalated_to_owner" in updates[0]
    assert refreshes == [("workspace-1", "token-1")]

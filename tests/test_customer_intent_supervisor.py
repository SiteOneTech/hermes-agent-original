import scripts.customer_intent_supervisor as supervisor


def test_customer_intent_supervisor_formats_owner_alert():
    payload = {
        "count": 1,
        "intents": [
            {
                "intent_id": "intent-123",
                "priority": "high",
                "intent_type": "formal_quote",
                "channel": "whatsapp",
                "contact_name": "Ella",
                "contact_phone": "+15612983762",
                "summary": "Quiere personalizar documentos comerciales",
                "required_action": "Revisar alcance y preparar propuesta",
                "source_ref": "wamid.test",
                "recent_interactions": [
                    {"summary": "Preguntó por facturas y propuestas personalizadas"}
                ],
            }
        ],
    }

    alert = supervisor.format_alert(payload)

    assert "Customer Intent Supervisor" in alert
    assert "intent-123" in alert
    assert "Ella" in alert
    assert "No ejecuté acciones" in alert
    assert "completed" in alert


def test_customer_intent_supervisor_marks_notified_without_status_change(monkeypatch):
    captured = []

    def fake_statement_one(statement, *, user=None):
        captured.append((statement, user))
        return {"intent_id": "intent-123"}

    monkeypatch.setattr(supervisor.sql, "statement_one", fake_statement_one)
    monkeypatch.setattr(supervisor.sql, "runtime_env", lambda: {"CRM_DB_RUNTIME_USER": "crm_runtime"})

    count = supervisor.mark_notified([{"intent_id": "intent-123"}])

    assert count == 1
    statement, user = captured[0]
    assert user == "crm_runtime"
    assert "supervisor_notified_at" in statement
    assert "supervisor_notification_count" in statement
    assert "status" not in statement.lower().split("set", 1)[1].split("where", 1)[0]


def test_customer_intent_supervisor_fetch_pending_can_filter_recently_notified(monkeypatch):
    captured = {}

    def fake_rows(statement, *, user=None):
        captured["statement"] = statement
        captured["user"] = user
        return []

    monkeypatch.setattr(supervisor.sql, "rows", fake_rows)
    monkeypatch.setattr(supervisor.sql, "runtime_env", lambda: {"CRM_DB_RUNTIME_USER": "crm_runtime"})

    result = supervisor.fetch_pending(10, only_alertable=True, renotify_minutes=45)

    assert result == []
    assert captured["user"] == "crm_runtime"
    assert "supervisor_notified_at" in captured["statement"]
    assert "45 * interval '1 minute'" in captured["statement"]

import importlib.util
from pathlib import Path


def _load_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "runtime" / "ingest_delivery_events.py"
    spec = importlib.util.spec_from_file_location("ingest_delivery_events", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_comment_does_not_regress_final_workspace_status():
    ingest = _load_module()

    assert ingest._status_for_event("commented", "approved") is None
    assert ingest._status_for_event("opened", "rejected") is None
    assert ingest._status_for_event("commented", "viewed") == "commented"
    assert ingest._status_for_event("approved", "commented") == "approved"


def test_ingest_uses_canonical_document_action_sets():
    ingest = _load_module()

    assert "commented" in ingest.SALES_EVENT_TYPES
    assert "document_action_unlocked" in ingest.SALES_EVENT_TYPES
    assert "document_action_otp_requested" in ingest.SALES_EVENT_TYPES
    assert "approved" in ingest.FINAL_SALES_STATUS
    assert "rejected" in ingest.FINAL_RECEIPT_STATUS
    assert "signed" in ingest.EVENT_TYPES_WITH_OWNER_ACTION


def test_document_access_activity_updates_viewed_status():
    ingest = _load_module()

    assert ingest._status_for_event("document_action_unlocked", "pending") == "viewed"
    assert ingest._status_for_event("document_action_otp_requested", "pending") is None


def test_load_events_keeps_document_access_activity_statuses(tmp_path):
    ingest = _load_module()
    events_path = tmp_path / "events.jsonl"
    events_path.write_text(
        "\n".join([
            '{"event_id":"otp-1","event_type":"document_action_otp_requested","status":"pending_otp_dispatch"}',
            '{"event_id":"unlock-1","event_type":"document_action_unlocked","status":"active"}',
            '{"event_id":"noise-1","event_type":"user_session_started","status":"active"}',
        ]),
        encoding="utf-8",
    )

    loaded = ingest.load_events(events_path)

    assert [event["event_id"] for event in loaded] == ["otp-1", "unlock-1"]


def test_signed_sales_document_ingest_notifies_owner(tmp_path, monkeypatch):
    ingest = _load_module()
    workspace = {
        "workspace_id": "workspace-sign-1",
        "document_type": "signature_request",
        "document_id": "sig-req-1",
        "status": "viewed",
        "customer_name": "Smart ISP",
        "public_token": None,
    }
    statements = []
    notifications = []

    def fake_one(query, *, user=None):
        if "sales.customer_workspace_events" in query:
            return None
        if "sales.customer_workspaces" in query:
            return workspace
        if "crm.follow_ups" in query:
            return None
        return None

    def fake_statement_one(statement, *, user=None):
        statements.append(statement)
        if "crm.follow_ups" in statement:
            return {"follow_up_id": "follow-up-1"}
        if "sales.customer_workspace_events" in statement:
            return {"workspace_event_id": "event-1"}
        return {}

    monkeypatch.setattr(ingest.sql, "one", fake_one)
    monkeypatch.setattr(ingest.sql, "statement_one", fake_statement_one)
    monkeypatch.setattr(ingest.sql, "rows", lambda *args, **kwargs: [])
    monkeypatch.setattr(
        ingest,
        "_send_owner_notification",
        lambda message, metadata: notifications.append((message, metadata)) or {"ok": True, "target": "telegram"},
        raising=False,
    )

    result = ingest.ingest_sales_event(
        {
            "event_id": "signed-event-1",
            "event_type": "signed",
            "deliverable_id": "sig-req-1",
            "actor_type": "customer",
            "actor_ref": "david@example.com",
            "status": "pending_agent_ingest",
            "metadata": {
                "workspace_id": "workspace-sign-1",
                "public_document_number": "Acta Smart ISP",
                "signer_name": "David Piza",
                "signature_request_id": "sig-req-1",
            },
        },
        tmp_path,
    )

    assert result == "sales:ingested"
    assert any("crm.follow_ups" in statement for statement in statements)
    assert notifications
    message, metadata = notifications[0]
    assert "Documento firmado" in message
    assert "Acta Smart ISP" in message
    assert "David Piza" in message
    assert metadata["delivery_event_id"] == "signed-event-1"
    assert metadata["event_type"] == "signed"


def test_generic_signed_document_event_notifies_owner_without_sales_or_receipt(monkeypatch):
    ingest = _load_module()
    statements = []
    notifications = []

    def fake_one(query, *, user=None):
        if "crm.follow_ups" in query:
            return None
        return None

    def fake_statement_one(statement, *, user=None):
        statements.append(statement)
        if "crm.follow_ups" in statement:
            return {"follow_up_id": "follow-up-generic"}
        return {}

    monkeypatch.setattr(ingest.sql, "one", fake_one)
    monkeypatch.setattr(ingest.sql, "statement_one", fake_statement_one)
    monkeypatch.setattr(
        ingest,
        "_send_owner_notification",
        lambda message, metadata: notifications.append((message, metadata)) or {"ok": True, "target": "telegram"},
        raising=False,
    )

    result = ingest.ingest_owner_document_event({
        "event_id": "signed-generic-1",
        "event_type": "signed",
        "deliverable_id": "signature-request-1",
        "actor_type": "customer",
        "actor_ref": "ana@example.com",
        "status": "pending_agent_ingest",
        "metadata": {
            "public_document_number": "Contrato Comercial 2026",
            "signer_name": "Ana Cliente",
            "signature_request_id": "signature-request-1",
        },
    })

    assert result == "owner_document:ingested"
    assert any("crm.follow_ups" in statement for statement in statements)
    assert notifications
    assert "Contrato Comercial 2026" in notifications[0][0]
    assert "Ana Cliente" in notifications[0][0]


def test_main_invokes_generic_signed_document_adapter(tmp_path, monkeypatch):
    ingest = _load_module()
    events_path = tmp_path / "events.jsonl"
    events_path.write_text(
        '{"event_id":"signed-main-1","event_type":"signed","deliverable_id":"signature-request-main","status":"pending_agent_ingest","metadata":{"signature_request_id":"signature-request-main","signer_name":"Cliente Main"}}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(ingest, "ingest_stripe_event", lambda event: None)
    monkeypatch.setattr(ingest, "ingest_sales_event", lambda event, public_root: None)
    monkeypatch.setattr(ingest, "ingest_receipt_event", lambda event, public_root: None)
    calls = []
    monkeypatch.setattr(ingest, "ingest_owner_document_event", lambda event: calls.append(event["event_id"]) or "owner_document:ingested")

    assert ingest.main(["--events", str(events_path), "--public-root", str(tmp_path)]) == 0
    assert calls == ["signed-main-1"]


def test_one_bad_adapter_event_does_not_block_sales_comment_ingest(tmp_path, monkeypatch):
    ingest = _load_module()
    events_path = tmp_path / "events.jsonl"
    events_path.write_text(
        "\n".join(
            [
                '{"event_id":"stripe-1","event_type":"stripe_webhook","status":"pending_agent_ingest","metadata":{"stripe_event":{"id":"evt_bad","type":"checkout.session.completed"}}}',
                '{"event_id":"comment-1","event_type":"commented","deliverable_id":"quote-1","status":"pending_agent_ingest","comment":"Cliente comentó","metadata":{"workspace_id":"workspace-quote-1"}}',
            ]
        ),
        encoding="utf-8",
    )
    calls = []

    def bad_stripe(_event):
        raise RuntimeError("stripe adapter exploded")

    def sales_event(event, _public_root):
        if event.get("event_type") != "commented":
            return None
        calls.append(event["event_id"])
        return "sales:ingested"

    monkeypatch.setattr(ingest, "ingest_stripe_event", bad_stripe)
    monkeypatch.setattr(ingest, "ingest_sales_event", sales_event)
    monkeypatch.setattr(ingest, "ingest_receipt_event", lambda *_args, **_kwargs: None)

    assert ingest.main(["--events", str(events_path), "--public-root", str(tmp_path), "--quiet"]) == 0
    assert calls == ["comment-1"]

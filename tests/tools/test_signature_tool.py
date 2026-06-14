from __future__ import annotations

import json

import toolsets
from tools import signature_tool


def _loads(result: str) -> dict:
    return json.loads(result)


def test_signature_toolset_registered():
    tools = toolsets.resolve_toolset("signature")
    assert "signature_status" in tools
    assert "signature_request_create" in tools
    assert "signature_approval_hash_create" in tools
    assert "signature_completed_pdf_record" in tools
    assert "signature_final_copies_send" in tools


def test_approval_hash_is_deterministic(monkeypatch):
    request = {
        "request_id": "req-1",
        "source_type": "quote",
        "source_id": "quote-1",
        "title": "Quote 1",
        "document_url": "https://example.test/doc.pdf",
        "document_hash_sha256": "doc-hash",
    }
    inserted = []

    def fake_one(query, *, user=None):
        if "FROM signature.document_requests" in query:
            return request
        if "event_hash FROM signature.events" in query:
            return {"event_hash": "prev-hash"}
        return None

    def fake_statement_one(query, *, user=None):
        inserted.append(query)
        if "INSERT INTO signature.approvals" in query:
            return {"approval_id": "approval-1", "approval_hash": "stored"}
        if "INSERT INTO signature.events" in query:
            return {"signature_event_id": len(inserted), "event_hash": "event-hash"}
        return {}

    monkeypatch.setattr(signature_tool.sql, "one", fake_one)
    monkeypatch.setattr(signature_tool.sql, "statement_one", fake_statement_one)
    monkeypatch.setattr(signature_tool.sql, "psql", lambda *a, **k: None)

    args = {
        "approval_id": "approval-1",
        "request_id": "req-1",
        "submitter_id": "sub-1",
        "signature_text": "Jean Garcia",
        "signature_image_sha256": "sig-hash",
        "document_hash_sha256": "doc-hash",
        "ip_address": "127.0.0.1",
        "user_agent": "pytest",
        "signed_at": "2026-06-01T00:00:00Z",
        "actor_ref": "jean@example.test",
    }
    first = _loads(signature_tool._handle_approval_hash_create(args))
    second = _loads(signature_tool._handle_approval_hash_create(args))
    assert first["ok"] is True
    assert second["ok"] is True
    assert first["approval_hash"] == second["approval_hash"]
    assert len(first["approval_hash"]) == 64
    assert any("INSERT INTO signature.approvals" in query for query in inserted)


def test_request_create_requires_submitters():
    result = _loads(signature_tool._handle_request_create({"title": "No signers"}))
    assert result["error"]
    assert "submitters" in result["error"]


def test_final_copies_registers_receipts_for_each_signer_and_escalates_failures(monkeypatch):
    request = {
        "request_id": "req-1",
        "status": "completed",
        "completed_document_url": "https://example.test/final.pdf",
        "audit_url": "https://example.test/audit.pdf",
        "document_hash_sha256": "o" * 64,
        "metadata": {"completed_pdf_sha256": "f" * 64, "audit_pdf_sha256": "a" * 64},
    }
    submitters = [
        {"submitter_id": "sub-1", "role": "signer", "name": "Jean", "email": "jean@example.test", "phone": None, "metadata": {}},
        {"submitter_id": "sub-2", "role": "approver", "name": "Maria", "email": None, "phone": "+15550002", "metadata": {"final_copy_channel": "sms"}},
        {"submitter_id": "viewer-1", "role": "viewer", "name": "Viewer", "email": "viewer@example.test", "phone": None, "metadata": {}},
    ]
    statements = []
    events = []

    def fake_one(query, *, user=None):
        if "FROM signature.document_requests" in query:
            return request
        return None

    def fake_rows(query, *, user=None):
        assert "FROM signature.submitters" in query
        return submitters

    def fake_statement_one(query, *, user=None):
        statements.append(query)
        if "INSERT INTO signature.delivery_receipts" in query:
            return {"delivery_receipt_id": len(statements), "status": "stored"}
        if "INSERT INTO signature.events" in query:
            return {"event_hash": "event"}
        return {}

    monkeypatch.setattr(signature_tool.sql, "one", fake_one)
    monkeypatch.setattr(signature_tool.sql, "rows", fake_rows)
    monkeypatch.setattr(signature_tool.sql, "statement_one", fake_statement_one)
    monkeypatch.setattr(signature_tool, "_record_event", lambda *args, **kwargs: events.append((args, kwargs)) or {"event_hash": "event"})

    result = _loads(signature_tool._handle_final_copies_send({
        "request_id": "req-1",
        "delivery_results": [
            {"submitter_id": "sub-1", "status": "sent", "channel": "email", "provider_message_id": "mail-1"},
            {"submitter_id": "sub-2", "status": "failed", "channel": "sms", "error": "carrier rejected"},
        ],
        "certificate_summary": {"certificate_id": "cert-1"},
        "approval_hashes": ["p" * 64],
    }))

    assert result["ok"] is True
    assert len(result["deliveries"]) == 2
    assert {item["submitter_id"] for item in result["deliveries"]} == {"sub-1", "sub-2"}
    assert result["deliveries"][0]["validation_summary"]["final_document_sha256"] == "f" * 64
    assert result["retry_actions"] == [{"submitter_id": "sub-2", "channel": "sms", "recipient": "+15550002", "reason": "carrier rejected"}]
    joined = "\n".join(statements)
    assert joined.count("INSERT INTO signature.delivery_receipts") == 2
    assert "final_copy" in joined
    assert "final_document_sha256" in joined
    assert any(event[1]["event_type"] == "final_copy_sent" for event in events)
    assert any(event[1]["event_type"] == "final_copy_failed" for event in events)
    assert any(event[1]["event_type"] == "owner_escalation" for event in events)


def test_final_copies_require_completed_request(monkeypatch):
    monkeypatch.setattr(signature_tool.sql, "one", lambda query, *, user=None: {"request_id": "req-1", "status": "sent", "metadata": {}})

    result = _loads(signature_tool._handle_final_copies_send({"request_id": "req-1"}))

    assert result["error"]
    assert "completed" in result["error"]

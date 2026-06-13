from __future__ import annotations

import json

import pytest

import toolsets
from tools import signature_tool


def _loads(result: str) -> dict:
    return json.loads(result)


def test_signature_toolset_registered():
    tools = toolsets.resolve_toolset("signature")
    assert "signature_status" in tools
    assert "signature_request_create" in tools
    assert "signature_approval_hash_create" in tools
    assert "signature_recipient_action_record" in tools


def test_approval_hash_is_deterministic(monkeypatch):
    request = {
        "request_id": "req-1",
        "source_type": "quote",
        "source_id": "quote-1",
        "title": "Quote 1",
        "document_url": "https://example.test/doc.pdf",
        "document_hash_sha256": "doc-hash",
        "status": "sent",
    }
    submitter = {
        "submitter_id": "sub-1",
        "request_id": "req-1",
        "status": "sent",
        "role": "approver",
        "email": "jean@example.test",
        "token_hash_sha256": signature_tool._sha256_text("token-1"),
    }
    inserted = []

    def fake_one(query, *, user=None):
        if "FROM signature.document_requests" in query:
            return request
        if "FROM signature.submitters" in query:
            return submitter
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
        "signer_token": "token-1",
        "otp_verified": True,
        "otp_challenge_id": "challenge-1",
        "otp_target_hash": signature_tool._sha256_text("jean@example.test"),
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


def test_approval_hash_fails_closed_without_recipient_otp(monkeypatch):
    monkeypatch.setattr(signature_tool.sql, "one", lambda *a, **k: {"request_id": "req-1", "status": "sent"})

    result = _loads(signature_tool._handle_approval_hash_create({"request_id": "req-1", "signer_token": "token-1"}))

    assert result["error"] == "otp_required"


def test_recipient_action_rejects_wrong_signer_token(monkeypatch):
    request = {"request_id": "req-1", "status": "sent"}

    def fake_one(query, *, user=None):
        if "FROM signature.document_requests" in query:
            return request
        if "FROM signature.submitters" in query:
            return None
        return None

    monkeypatch.setattr(signature_tool.sql, "one", fake_one)

    result = _loads(signature_tool._handle_recipient_action_record({
        "request_id": "req-1",
        "action": "sign",
        "signer_token": "wrong-token",
        "otp_verified": True,
        "otp_challenge_id": "challenge-1",
        "otp_target_hash": signature_tool._sha256_text("jean@example.test"),
    }))

    assert result["error"] == "invalid_signer_token"


@pytest.mark.parametrize("request_row", [
    {"request_id": "req-1", "status": "completed"},
    {"request_id": "req-1", "status": "cancelled"},
    {"request_id": "req-1", "status": "expired"},
    {"request_id": "req-1", "status": "sent", "expires_at": "2000-01-01T00:00:00Z"},
])
def test_recipient_action_rejects_closed_requests(monkeypatch, request_row):
    def fake_one(query, *, user=None):
        if "FROM signature.document_requests" in query:
            return request_row
        return None

    monkeypatch.setattr(signature_tool.sql, "one", fake_one)

    result = _loads(signature_tool._handle_recipient_action_record({
        "request_id": "req-1",
        "action": "approve",
        "signer_token": "token-1",
        "otp_verified": True,
        "otp_challenge_id": "challenge-1",
        "otp_target_hash": signature_tool._sha256_text("jean@example.test"),
    }))

    assert result["error"] == "request_not_actionable"


def test_comment_and_rejection_reason_are_persisted_and_audited(monkeypatch):
    request = {"request_id": "req-1", "status": "sent"}
    submitter = {
        "submitter_id": "sub-1",
        "request_id": "req-1",
        "status": "sent",
        "role": "signer",
        "email": "jean@example.test",
        "phone": None,
        "token_hash_sha256": signature_tool._sha256_text("token-1"),
    }
    inserted = []

    def fake_one(query, *, user=None):
        if "FROM signature.document_requests" in query:
            return request
        if "FROM signature.submitters" in query:
            return submitter
        if "event_hash FROM signature.events" in query:
            return {"event_hash": "prev"}
        return None

    def fake_statement_one(query, *, user=None):
        inserted.append(query)
        if "INSERT INTO signature.comments" in query:
            return {"comment_id": "comment-1", "scope": "field", "field_id": "field-1", "body": "No acepto"}
        if "INSERT INTO signature.events" in query:
            return {"signature_event_id": len(inserted), "event_hash": "event-hash"}
        return {}

    monkeypatch.setattr(signature_tool.sql, "one", fake_one)
    monkeypatch.setattr(signature_tool.sql, "statement_one", fake_statement_one)
    monkeypatch.setattr(signature_tool.sql, "psql", lambda query, *, user=None: inserted.append(query))

    result = _loads(signature_tool._handle_recipient_action_record({
        "request_id": "req-1",
        "action": "reject",
        "signer_token": "token-1",
        "comment": "No acepto",
        "field_id": "field-1",
        "otp_verified": True,
        "otp_challenge_id": "challenge-1",
        "otp_target_hash": signature_tool._sha256_text("jean@example.test"),
        "actor_ref": "jean@example.test",
    }))

    assert result["ok"] is True
    assert result["action"] == "rejected"
    assert any("INSERT INTO signature.comments" in query and "field-1" in query for query in inserted)
    assert any("INSERT INTO signature.events" in query and "declined" in query for query in inserted)

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

    def fake_rows(query, *, user=None):
        if "FROM signature.submitters" in query:
            return [{"submitter_id": "sub-1", "role": "approver", "required": True, "status": "approved"}]
        return []

    monkeypatch.setattr(signature_tool.sql, "one", fake_one)
    monkeypatch.setattr(signature_tool.sql, "rows", fake_rows)
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


def test_single_required_signer_completion_status():
    request = {"status": "sent", "decline_blocks": True, "expires_at": None}
    submitters = [{"role": "signer", "required": True, "status": "signed"}]

    state = signature_tool._derive_request_lifecycle(request, submitters)

    assert state["status"] == "completed"
    assert state["completed"] is True


def test_parallel_multi_signer_stays_partial_until_all_required_complete():
    request = {"status": "sent", "decline_blocks": True, "expires_at": None, "signing_mode": "parallel"}
    submitters = [
        {"role": "signer", "required": True, "status": "signed", "signing_order": 1},
        {"role": "approver", "required": True, "status": "pending", "signing_order": 1},
    ]

    partial = signature_tool._derive_request_lifecycle(request, submitters)
    submitters[1]["status"] = "approved"
    complete = signature_tool._derive_request_lifecycle(request, submitters)

    assert partial["status"] == "partially_signed"
    assert partial["completed"] is False
    assert complete["status"] == "completed"
    assert complete["completed"] is True


def test_sequential_multi_signer_does_not_complete_on_first_required_signature():
    request = {"status": "sent", "decline_blocks": True, "expires_at": None, "signing_mode": "sequential"}
    submitters = [
        {"role": "signer", "required": True, "status": "signed", "signing_order": 1},
        {"role": "signer", "required": True, "status": "pending", "signing_order": 2},
    ]

    state = signature_tool._derive_request_lifecycle(request, submitters)

    assert state["status"] == "partially_signed"
    assert state["completed"] is False


def test_optional_viewer_does_not_block_completion():
    request = {"status": "sent", "decline_blocks": True, "expires_at": None}
    submitters = [
        {"role": "signer", "required": True, "status": "signed"},
        {"role": "viewer", "required": False, "status": "pending"},
    ]

    state = signature_tool._derive_request_lifecycle(request, submitters)

    assert state["status"] == "completed"
    assert state["completed"] is True


def test_required_decline_blocks_request():
    request = {"status": "sent", "decline_blocks": True, "expires_at": None}
    submitters = [{"role": "signer", "required": True, "status": "declined"}]

    state = signature_tool._derive_request_lifecycle(request, submitters)

    assert state["status"] == "declined"
    assert state["completed"] is False


def test_expired_request_stays_expired_until_completed():
    request = {"status": "sent", "decline_blocks": True, "expires_at": "2000-01-01T00:00:00Z"}
    submitters = [{"role": "signer", "required": True, "status": "pending"}]

    state = signature_tool._derive_request_lifecycle(request, submitters)

    assert state["status"] == "expired"
    assert state["completed"] is False



def test_approval_hash_create_updates_request_to_partial_for_remaining_required_signers(monkeypatch):
    request = {
        "request_id": "req-2",
        "source_type": "quote",
        "source_id": "quote-2",
        "title": "Quote 2",
        "document_url": "https://example.test/doc.pdf",
        "document_hash_sha256": "doc-hash",
        "status": "sent",
        "decline_blocks": True,
        "expires_at": None,
    }
    submitters = [
        {"submitter_id": "sub-1", "role": "signer", "required": True, "status": "pending"},
        {"submitter_id": "sub-2", "role": "signer", "required": True, "status": "pending"},
    ]
    statements = []

    def fake_one(query, *, user=None):
        if "FROM signature.document_requests" in query:
            return request
        if "FROM signature.submitters" in query and "submitter_id" in query:
            return submitters[0]
        if "event_hash FROM signature.events" in query:
            return {"event_hash": "prev-hash"}
        return None

    def fake_rows(query, *, user=None):
        if "FROM signature.submitters" in query:
            return [{**submitters[0], "status": "signed"}, submitters[1]]
        return []

    def fake_statement_one(query, *, user=None):
        statements.append(query)
        if "INSERT INTO signature.approvals" in query:
            return {"approval_id": "approval-2", "approval_hash": "stored"}
        if "INSERT INTO signature.events" in query:
            return {"signature_event_id": len(statements), "event_hash": "event-hash"}
        return {}

    monkeypatch.setattr(signature_tool.sql, "one", fake_one)
    monkeypatch.setattr(signature_tool.sql, "rows", fake_rows)
    monkeypatch.setattr(signature_tool.sql, "statement_one", fake_statement_one)
    monkeypatch.setattr(signature_tool.sql, "psql", lambda query, *a, **k: statements.append(query))

    result = _loads(signature_tool._handle_approval_hash_create({"request_id": "req-2", "submitter_id": "sub-1"}))

    assert result["ok"] is True
    assert result["request_status"] == "partially_signed"
    joined = "\n".join(statements)
    assert "status='completed'" not in joined
    assert "status='partially_signed'" in joined

from __future__ import annotations

import json

import toolsets
from tools import signature_tool
from tools.registry import registry


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
            return [{"submitter_id": "sub-1", "role": "approver", "required": True, "status": "approved", "token_hash_sha256": signature_tool._sha256_text("recipient-token")}]
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
        "signer_token": "recipient-token",
        "otp_verified": True,
        "otp_challenge_id": "challenge-1",
        "otp_channel_id": "email",
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


def test_approval_hash_create_rejects_request_id_only(monkeypatch):
    monkeypatch.setattr(
        signature_tool.sql,
        "one",
        lambda query, *, user=None: {"request_id": "req-only", "status": "sent"}
        if "FROM signature.document_requests" in query
        else None,
    )
    monkeypatch.setattr(signature_tool.sql, "statement_one", lambda *a, **k: (_ for _ in ()).throw(AssertionError("approval insert must not run")))

    result = _loads(signature_tool._handle_approval_hash_create({"request_id": "req-only"}))

    assert result["error"]
    assert "signer_token" in result["error"]


def test_approval_hash_create_rejects_submitter_without_otp(monkeypatch):
    request = {"request_id": "req-no-otp", "status": "sent"}
    submitter = {
        "submitter_id": "sub-1",
        "request_id": "req-no-otp",
        "role": "signer",
        "required": True,
        "status": "pending",
        "token_hash_sha256": signature_tool._sha256_text("recipient-token"),
    }

    def fake_one(query, *, user=None):
        if "FROM signature.document_requests" in query:
            return request
        if "FROM signature.submitters" in query:
            return submitter
        return None

    monkeypatch.setattr(signature_tool.sql, "one", fake_one)
    monkeypatch.setattr(signature_tool.sql, "statement_one", lambda *a, **k: (_ for _ in ()).throw(AssertionError("approval insert must not run")))

    result = _loads(signature_tool._handle_approval_hash_create({"request_id": "req-no-otp", "submitter_id": "sub-1", "signer_token": "recipient-token"}))

    assert result["error"]
    assert "OTP proof" in result["error"]


def test_approval_hash_create_rejects_wrong_signer_token(monkeypatch):
    request = {"request_id": "req-wrong-token", "status": "sent"}
    submitter = {
        "submitter_id": "sub-1",
        "request_id": "req-wrong-token",
        "role": "signer",
        "required": True,
        "status": "pending",
        "token_hash_sha256": signature_tool._sha256_text("recipient-token"),
    }

    def fake_one(query, *, user=None):
        if "FROM signature.document_requests" in query:
            return request
        if "FROM signature.submitters" in query:
            return submitter
        return None

    monkeypatch.setattr(signature_tool.sql, "one", fake_one)
    monkeypatch.setattr(signature_tool.sql, "statement_one", lambda *a, **k: (_ for _ in ()).throw(AssertionError("approval insert must not run")))

    result = _loads(signature_tool._handle_approval_hash_create({
        "request_id": "req-wrong-token",
        "submitter_id": "sub-1",
        "signer_token": "wrong-token",
        "otp_verified": True,
        "otp_challenge_id": "challenge-1",
    }))

    assert result["error"]
    assert "signer_token" in result["error"]


def test_approval_hash_create_rejects_terminal_request_before_mutations(monkeypatch):
    writes = []

    def fake_one(query, *, user=None):
        if "FROM signature.document_requests" in query:
            return {"request_id": "req-terminal", "status": "completed"}
        if "FROM signature.submitters" in query:
            return {
                "submitter_id": "sub-terminal",
                "request_id": "req-terminal",
                "role": "signer",
                "required": True,
                "status": "pending",
                "token_hash_sha256": signature_tool._sha256_text("recipient-token"),
            }
        return None

    monkeypatch.setattr(signature_tool.sql, "one", fake_one)
    monkeypatch.setattr(signature_tool.sql, "rows", lambda *a, **k: [])
    monkeypatch.setattr(
        signature_tool.sql,
        "statement_one",
        lambda *a, **k: writes.append(a[0]) or (_ for _ in ()).throw(AssertionError("write must not run")),
    )
    monkeypatch.setattr(
        signature_tool.sql,
        "psql",
        lambda *a, **k: writes.append(a[0]) or (_ for _ in ()).throw(AssertionError("status update must not run")),
    )

    result = _loads(signature_tool._handle_approval_hash_create({
        "request_id": "req-terminal",
        "submitter_id": "sub-terminal",
        "signer_token": "recipient-token",
        "otp_verified": True,
        "otp_challenge_id": "challenge-terminal",
    }))

    assert result["error"]
    assert "terminal" in result["error"]
    assert "completed" in result["error"]
    assert writes == []


def test_approval_hash_create_rejects_caller_declared_privileged_bypass(monkeypatch):
    request = {"request_id": "req-priv", "status": "sent"}
    writes = []

    def fake_one(query, *, user=None):
        if "FROM signature.document_requests" in query:
            return request
        return None

    monkeypatch.setattr(signature_tool.sql, "one", fake_one)
    monkeypatch.setattr(signature_tool.sql, "rows", lambda *a, **k: [])
    monkeypatch.setattr(
        signature_tool.sql,
        "statement_one",
        lambda *a, **k: writes.append(a[0]) or (_ for _ in ()).throw(AssertionError("approval insert must not run")),
    )
    monkeypatch.setattr(
        signature_tool.sql,
        "psql",
        lambda *a, **k: writes.append(a[0]) or (_ for _ in ()).throw(AssertionError("status update must not run")),
    )

    result = _loads(signature_tool._handle_approval_hash_create({
        "request_id": "req-priv",
        "internal_completion": True,
        "privileged_completion": True,
        "actor_type": "agent",
        "actor_ref": "normal-tool-caller",
    }))

    assert result["error"]
    assert "signer_token" in result["error"]
    assert writes == []


def test_signature_approval_hash_schema_does_not_expose_privileged_bypass_args():
    entry = registry.get_entry("signature_approval_hash_create")
    assert entry is not None
    props = entry.schema["function"]["parameters"]["properties"]

    assert "internal_completion" not in props
    assert "privileged_completion" not in props


def test_event_record_rejects_terminal_signed_event_before_event_write(monkeypatch):
    writes = []

    def fake_one(query, *, user=None):
        if "FROM signature.document_requests" in query:
            return {"request_id": "req-terminal", "status": "declined"}
        return None

    monkeypatch.setattr(signature_tool.sql, "one", fake_one)
    monkeypatch.setattr(
        signature_tool.sql,
        "statement_one",
        lambda *a, **k: writes.append(a[0]) or (_ for _ in ()).throw(AssertionError("event insert must not run")),
    )

    result = _loads(signature_tool._handle_event_record({
        "request_id": "req-terminal",
        "submitter_id": "sub-1",
        "event_type": "signed",
        "actor_type": "customer",
    }))

    assert result["error"]
    assert "terminal" in result["error"]
    assert "declined" in result["error"]
    assert writes == []


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


def test_optional_viewer_does_not_block_completion():
    request = {"status": "sent", "decline_blocks": True, "expires_at": None}
    submitters = [
        {"role": "signer", "required": True, "status": "signed"},
        {"role": "viewer", "required": False, "status": "pending"},
    ]

    state = signature_tool._derive_request_lifecycle(request, submitters)

    assert state["status"] == "completed"
    assert state["completed"] is True


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
        {"submitter_id": "sub-1", "role": "signer", "required": True, "status": "pending", "token_hash_sha256": signature_tool._sha256_text("recipient-token")},
        {"submitter_id": "sub-2", "role": "signer", "required": True, "status": "pending", "token_hash_sha256": signature_tool._sha256_text("other-token")},
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

    result = _loads(signature_tool._handle_approval_hash_create({
        "request_id": "req-2",
        "submitter_id": "sub-1",
        "signer_token": "recipient-token",
        "otp_verified": True,
        "otp_challenge_id": "challenge-2",
        "otp_channel_id": "email",
    }))

    assert result["ok"] is True
    assert result["request_status"] == "partially_signed"
    joined = "\n".join(statements)
    assert "status='completed'" not in joined
    assert "status='partially_signed'" in joined


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
        {"submitter_id": "sub-2", "role": "approver", "name": "Maria", "email": None, "phone": "+155****0002", "metadata": {"final_copy_channel": "sms"}},
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
    assert result["retry_actions"] == [{"submitter_id": "sub-2", "channel": "sms", "recipient": "+155****0002", "reason": "carrier rejected"}]
    joined = "\n".join(statements)
    assert joined.count("INSERT INTO signature.delivery_receipts") == 2
    assert "final_copy" in joined
    assert "final_document_sha256" in joined
    assert any(event[1]["event_type"] == "final_copy_sent" for event in events)
    assert any(event[1]["event_type"] == "final_copy_failed" for event in events)
    assert any(event[1]["event_type"] == "owner_escalation" for event in events)

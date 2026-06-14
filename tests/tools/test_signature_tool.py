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
    assert "signature_delivery_receipt_record" in tools
    assert "signature_reminder_policy_upsert" in tools
    assert "signature_reminder_attempt_record" in tools
    assert "signature_followup_due" in tools
    assert "signature_completed_pdf_record" in tools


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


def test_delivery_receipt_record_is_idempotent_and_records_failure(monkeypatch):
    statements = []
    events = []

    def fake_statement_one(query, *, user=None):
        statements.append(query)
        if "INSERT INTO signature.delivery_receipts" in query:
            return {
                "delivery_receipt_id": "receipt-1",
                "receipt_type": "otp",
                "status": "failed",
                "error_message": "provider timeout",
                "idempotency_key": "otp:req-1:sub-1:abc",
            }
        if "INSERT INTO signature.events" in query:
            events.append(query)
            return {"signature_event_id": len(events), "event_hash": "event-hash"}
        return {}

    monkeypatch.setattr(signature_tool.sql, "statement_one", fake_statement_one)
    monkeypatch.setattr(signature_tool.sql, "one", lambda *a, **k: {"event_hash": "prev-hash"})

    result = _loads(signature_tool._handle_delivery_receipt_record({
        "request_id": "req-1",
        "submitter_id": "sub-1",
        "receipt_type": "otp",
        "channel": "email",
        "recipient": "jean@example.test",
        "provider_message_id": "abc",
        "status": "failed",
        "error_message": "provider timeout",
        "idempotency_key": "otp:req-1:sub-1:abc",
    }))

    assert result["ok"] is True
    assert result["receipt"]["status"] == "failed"
    insert_sql = next(query for query in statements if "INSERT INTO signature.delivery_receipts" in query)
    assert "ON CONFLICT (idempotency_key) DO UPDATE" in insert_sql
    assert "error_message=EXCLUDED.error_message" in insert_sql
    assert events


def test_reminder_policy_upsert_stores_cadence_due_attempts_and_escalation(monkeypatch):
    statements = []

    def fake_statement_one(query, *, user=None):
        statements.append(query)
        if "INSERT INTO signature.reminder_policies" in query:
            return {
                "reminder_policy_id": "policy-1",
                "request_id": "req-1",
                "cadence": "daily",
                "next_due_at": "2026-06-15T09:00:00Z",
                "max_attempts": 5,
                "escalation_settings": {"owner_after_attempts": 3},
            }
        if "INSERT INTO signature.events" in query:
            return {"signature_event_id": 1, "event_hash": "event-hash"}
        return {}

    monkeypatch.setattr(signature_tool.sql, "statement_one", fake_statement_one)
    monkeypatch.setattr(signature_tool.sql, "one", lambda *a, **k: {"event_hash": "prev-hash"})

    result = _loads(signature_tool._handle_reminder_policy_upsert({
        "request_id": "req-1",
        "cadence": "daily",
        "next_due_at": "2026-06-15T09:00:00Z",
        "max_attempts": 5,
        "escalation_settings": {"owner_after_attempts": 3, "near_expiry_hours": 24},
    }))

    assert result["ok"] is True
    assert result["policy"]["cadence"] == "daily"
    insert_sql = next(query for query in statements if "INSERT INTO signature.reminder_policies" in query)
    assert "cadence" in insert_sql
    assert "next_due_at" in insert_sql
    assert "max_attempts" in insert_sql
    assert "escalation_settings" in insert_sql
    assert "ON CONFLICT (request_id) DO UPDATE" in insert_sql


def test_reminder_attempt_record_is_idempotent_and_updates_next_due(monkeypatch):
    statements = []

    def fake_statement_one(query, *, user=None):
        statements.append(query)
        if "INSERT INTO signature.reminder_attempts" in query:
            return {
                "reminder_attempt_id": "attempt-1",
                "status": "failed",
                "error_message": "sms rejected",
                "idempotency_key": "rem:req-1:sub-1:20260615",
            }
        if "INSERT INTO signature.delivery_receipts" in query:
            return {"delivery_receipt_id": "receipt-1", "status": "failed"}
        if "INSERT INTO signature.events" in query:
            return {"signature_event_id": 1, "event_hash": "event-hash"}
        return {}

    monkeypatch.setattr(signature_tool.sql, "statement_one", fake_statement_one)
    monkeypatch.setattr(signature_tool.sql, "one", lambda *a, **k: {"event_hash": "prev-hash"})

    result = _loads(signature_tool._handle_reminder_attempt_record({
        "request_id": "req-1",
        "submitter_id": "sub-1",
        "channel": "sms",
        "recipient": "+15551234567",
        "status": "failed",
        "error_message": "sms rejected",
        "provider_message_id": "sms-1",
        "idempotency_key": "rem:req-1:sub-1:20260615",
        "next_due_at": "2026-06-16T09:00:00Z",
    }))

    assert result["ok"] is True
    assert result["attempt"]["status"] == "failed"
    attempt_sql = next(query for query in statements if "INSERT INTO signature.reminder_attempts" in query)
    assert "ON CONFLICT (idempotency_key) DO UPDATE" in attempt_sql
    assert "error_message=EXCLUDED.error_message" in attempt_sql
    assert any("UPDATE signature.reminder_policies" in query for query in statements)
    assert any("INSERT INTO signature.delivery_receipts" in query for query in statements)


def test_followup_due_records_one_daily_reminder_and_advances_policy(monkeypatch):
    rows_queries = []
    attempts = []
    receipts = []
    events = []

    due_row = {
        "reminder_policy_id": "policy-1",
        "request_id": "req-1",
        "submitter_id": "sub-1",
        "email": "signer@example.test",
        "phone": None,
        "next_due_at": "2026-06-15T09:00:00Z",
        "cadence": "daily",
        "max_attempts": 5,
        "attempt_count": 1,
        "failed_attempts": 0,
        "escalation_settings": {"near_expiry_hours": 48, "owner_after_failures": 3},
        "expires_at": "2026-06-20T09:00:00Z",
    }

    def fake_rows(query, *, user=None):
        rows_queries.append(query)
        return [due_row]

    def fake_statement_one(query, *, user=None):
        if "INSERT INTO signature.reminder_attempts" in query:
            attempts.append(query)
            return {"reminder_attempt_id": len(attempts), "status": "queued", "idempotency_key": "key-1"}
        if "INSERT INTO signature.delivery_receipts" in query:
            receipts.append(query)
            return {"delivery_receipt_id": len(attempts), "status": "queued"}
        if "INSERT INTO signature.events" in query:
            events.append(query)
            return {"signature_event_id": len(events), "event_hash": "event-hash"}
        if "UPDATE signature.reminder_policies" in query:
            return {"reminder_policy_id": "policy-1", "next_due_at": "2026-06-16T09:00:00Z"}
        return {}

    monkeypatch.setattr(signature_tool.sql, "rows", fake_rows)
    monkeypatch.setattr(signature_tool.sql, "statement_one", fake_statement_one)
    monkeypatch.setattr(signature_tool.sql, "one", lambda *a, **k: {"event_hash": "prev-hash"})

    result = _loads(signature_tool._handle_followup_due({"now": "2026-06-15T09:00:00Z"}))

    assert result["ok"] is True
    assert result["processed"] == 1
    assert result["reminders"][0]["submitter_id"] == "sub-1"
    assert result["reminders"][0]["channel"] == "email"
    assert attempts
    assert "scheduled_for" in attempts[0]
    assert receipts and "receipt:" in receipts[0]
    assert any("r.status IN ('sent','viewed','partially_signed')" in query for query in rows_queries)
    assert result["policy_updates"][0]["next_due_at"] == "2026-06-16T09:00:00Z"


def test_followup_due_escalates_owner_for_near_expiry_and_failures(monkeypatch):
    events = []
    due_rows = [
        {
            "reminder_policy_id": "policy-1",
            "request_id": "req-1",
            "submitter_id": "sub-1",
            "email": "signer@example.test",
            "phone": None,
            "next_due_at": "2026-06-15T09:00:00Z",
            "cadence": "daily",
            "max_attempts": 5,
            "attempt_count": 3,
            "failed_attempts": 3,
            "escalation_settings": {"near_expiry_hours": 48, "owner_after_failures": 3},
            "expires_at": "2026-06-16T08:00:00Z",
        }
    ]

    def fake_statement_one(query, *, user=None):
        if "INSERT INTO signature.reminder_attempts" in query:
            return {"reminder_attempt_id": 1, "status": "queued", "idempotency_key": "key-1"}
        if "INSERT INTO signature.delivery_receipts" in query:
            return {"delivery_receipt_id": 1, "status": "queued"}
        if "INSERT INTO signature.events" in query:
            events.append(query)
            return {"signature_event_id": len(events), "event_hash": "event-hash"}
        if "UPDATE signature.reminder_policies" in query:
            return {"reminder_policy_id": "policy-1", "next_due_at": "2026-06-16T09:00:00Z"}
        return {}

    monkeypatch.setattr(signature_tool.sql, "rows", lambda *a, **k: due_rows)
    monkeypatch.setattr(signature_tool.sql, "statement_one", fake_statement_one)
    monkeypatch.setattr(signature_tool.sql, "one", lambda *a, **k: {"event_hash": "prev-hash"})

    result = _loads(signature_tool._handle_followup_due({"now": "2026-06-15T09:00:00Z"}))

    assert result["ok"] is True
    assert sorted(result["escalations"][0]["reasons"]) == ["near_expiry", "repeated_delivery_failures"]
    assert any("owner_escalated" in query for query in events)

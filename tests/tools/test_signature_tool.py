from __future__ import annotations

import hashlib
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
    assert "signature_pdf_intake" in tools
    assert "signature_template_prepare" in tools


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


def test_pdf_intake_registers_source_hash_page_count_and_render_metadata(tmp_path, monkeypatch):
    pdf_path = tmp_path / "contract.pdf"
    pdf_bytes = b"%PDF-1.4\n1 0 obj<</Type /Page>>endobj\n2 0 obj<</Type /Page>>endobj\n%%EOF"
    pdf_path.write_bytes(pdf_bytes)
    statements = []

    def fake_statement_one(query, *, user=None):
        statements.append(query)
        if "INSERT INTO signature.attachments" in query:
            return {
                "attachment_id": "signature-attachment-contract-pdf",
                "sha256": hashlib.sha256(pdf_bytes).hexdigest(),
                "byte_size": len(pdf_bytes),
                "mime_type": "application/pdf",
            }
        return {}

    monkeypatch.setattr(signature_tool.sql, "statement_one", fake_statement_one)

    result = _loads(signature_tool._handle_pdf_intake({"pdf_path": str(pdf_path), "request_id": "req-1"}))

    assert result["ok"] is True
    assert result["source_pdf"]["sha256"] == hashlib.sha256(pdf_bytes).hexdigest()
    assert result["source_pdf"]["mime_type"] == "application/pdf"
    assert result["source_pdf"]["byte_size"] == len(pdf_bytes)
    assert result["source_pdf"]["page_count"] == 2
    assert result["render"]["preview_status"] in {"metadata_only", "rendered"}
    joined = "\n".join(statements)
    assert "INSERT INTO signature.attachments" in joined
    assert "source_pdf" in joined


def test_pdf_intake_rejects_non_pdf(tmp_path):
    text_path = tmp_path / "contract.txt"
    text_path.write_text("not a pdf")

    result = _loads(signature_tool._handle_pdf_intake({"pdf_path": str(text_path)}))

    assert result["error"]
    assert "PDF" in result["error"]


def test_template_prepare_asks_missing_questions_before_creating_version(monkeypatch):
    called = []
    monkeypatch.setattr(signature_tool.sql, "statement_one", lambda *a, **k: called.append(a[0]))

    result = _loads(signature_tool._handle_template_prepare({
        "name": "Contrato ad hoc",
        "source_document_attachment_id": "att-1",
        "document_sha256": "a" * 64,
        "fields": [],
        "submitters": [],
    }))

    assert result["ok"] is True
    assert result["ready"] is False
    assert result["template_version"] is None
    assert {question["missing"] for question in result["questions"]} == {"submitters", "fields", "deadline"}
    assert called == []


def test_template_prepare_creates_ad_hoc_template_version_with_source_hash_and_schema_version(monkeypatch):
    statements = []

    def fake_one(query, *, user=None):
        if "max(version_number)" in query:
            return {"version_number": 2}
        return None

    def fake_statement_one(query, *, user=None):
        statements.append(query)
        if "INSERT INTO signature.templates" in query:
            return {"template_id": "template-ad-hoc-contract", "name": "Ad hoc contract"}
        if "INSERT INTO signature.template_versions" in query:
            return {
                "template_version_id": "template-ad-hoc-contract-v3",
                "template_id": "template-ad-hoc-contract",
                "version_number": 3,
                "document_sha256": "b" * 64,
                "field_schema": [{"field_id": "sig-1"}],
                "metadata": {"field_schema_version": "signature-field-schema-v1"},
            }
        if "INSERT INTO signature.field_placements" in query:
            return {"field_id": "sig-1"}
        return {}

    monkeypatch.setattr(signature_tool.sql, "one", fake_one)
    monkeypatch.setattr(signature_tool.sql, "statement_one", fake_statement_one)

    result = _loads(signature_tool._handle_template_prepare({
        "name": "Ad hoc contract",
        "source_document_attachment_id": "att-1",
        "document_sha256": "b" * 64,
        "deadline": "2026-07-01T00:00:00Z",
        "fields": [{
            "field_id": "sig-1",
            "role": "client",
            "field_type": "signature",
            "label": "Firma cliente",
            "page_number": 1,
            "x": 100,
            "y": 200,
            "width": 180,
            "height": 60,
            "x_pct": 0.1,
            "y_pct": 0.2,
            "w_pct": 0.3,
            "h_pct": 0.1,
        }],
        "submitters": [{"role": "client", "name": "Jean", "email": "jean@example.test"}],
        "created_by": "zeus",
    }))

    assert result["ok"] is True
    assert result["ready"] is True
    assert result["questions"] == []
    assert result["template_version"]["document_sha256"] == "b" * 64
    assert result["template_version"]["metadata"]["field_schema_version"] == "signature-field-schema-v1"
    joined = "\n".join(statements)
    assert "INSERT INTO signature.template_versions" in joined
    assert "source_document_attachment_id" in joined
    assert "INSERT INTO signature.field_placements" in joined


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

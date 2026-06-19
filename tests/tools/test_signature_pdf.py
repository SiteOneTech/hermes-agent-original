from __future__ import annotations

import sys
from pathlib import Path

from pypdf import PdfReader
from reportlab.pdfgen import canvas

from tools import signature_pdf
from tools.signature_pdf import sha256_file, stamp_signed_pdf


class FakeRect:
    def __init__(self, x0, y0, x1, y1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1


class FakePage:
    def __init__(self):
        self.rect = FakeRect(0, 0, 612, 792)
        self.operations = []

    def draw_rect(self, rect, **kwargs):
        self.operations.append(("draw_rect", (rect.x0, rect.y0, rect.x1, rect.y1), kwargs))

    def insert_text(self, point, text, **kwargs):
        self.operations.append(("insert_text", point, text, kwargs))

    def insert_textbox(self, rect, text, **kwargs):
        self.operations.append(("insert_textbox", (rect.x0, rect.y0, rect.x1, rect.y1), text, kwargs))


class FakeDoc:
    last_saved_docs = []

    def __init__(self, path=None):
        self.path = path
        self.pages = [FakePage()]
        self.page_count = 1

    def __getitem__(self, index):
        return self.pages[index]

    def new_page(self, width=612, height=792):
        page = FakePage()
        page.rect = FakeRect(0, 0, width, height)
        self.pages.append(page)
        self.page_count = len(self.pages)
        return page

    def save(self, path, **kwargs):
        payload = []
        for page in self.pages:
            payload.extend(repr(op) for op in page.operations)
        Path(path).write_bytes("\n".join(payload).encode("utf-8"))
        FakeDoc.last_saved_docs.append(self)

    def close(self):
        pass


class FakeFitz:
    Rect = FakeRect

    @staticmethod
    def open(path=None):
        return FakeDoc(path)


def test_stamp_signed_pdf_renders_all_configured_fields_and_returns_audit_attachment(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "fitz", FakeFitz)
    FakeDoc.last_saved_docs.clear()
    input_pdf = tmp_path / "input.pdf"
    output_pdf = tmp_path / "completed.pdf"
    audit_pdf = tmp_path / "audit.pdf"
    # Intentionally not a real PDF: this forces the R&D PyMuPDF fallback path so
    # the legacy fake-fitz test still validates configured field rendering.
    input_pdf.write_bytes(b"original pdf bytes")

    result = signature_pdf.stamp_signed_pdf(
        input_pdf=input_pdf,
        output_pdf=output_pdf,
        audit_pdf=audit_pdf,
        request_id="req-1",
        source_id="contract-1",
        signer="Jean Garcia",
        signed_at="2026-06-01T00:00:00Z",
        approval_hash="a" * 64,
        approval_hashes=["a" * 64, "b" * 64],
        document_hash="d" * 64,
        submitted_fields=[
            {"field_id": "name", "label": "Nombre", "value": "Jean Garcia", "page": 0, "rect": [10, 20, 110, 50]},
            {"field_id": "signature", "type": "signature", "signature_text": "JG", "page": 0, "rect": [120, 20, 220, 60]},
        ],
        event_chain=[
            {"signature_event_id": 1, "event_type": "created", "event_hash": "h1", "previous_event_hash": None},
            {"signature_event_id": 2, "event_type": "approved", "event_hash": "h2", "previous_event_hash": "h1"},
        ],
    )

    assert result["pdf_backend"] == "pymupdf-rd-fallback"
    assert result["original_sha256"] == signature_pdf.sha256_file(input_pdf)
    assert result["final_sha256"] == signature_pdf.sha256_file(output_pdf)
    assert result["audit_sha256"] == signature_pdf.sha256_file(audit_pdf)
    assert {a["kind"] for a in result["attachments"]} == {"completed_pdf", "audit_pdf"}
    assert result["visual_qa_evidence"]["field_count"] == 2
    assert len(result["visual_qa_evidence"]["rendered_fields"]) == 2
    completed_text = output_pdf.read_text("utf-8")
    audit_text = audit_pdf.read_text("utf-8")
    assert "Nombre: Jean Garcia" in completed_text
    assert "Firma: JG" in completed_text
    assert "Hash SHA-256 del PDF final firmado" in audit_text
    assert "Resumen de cadena de eventos" in audit_text
    assert "h1" in audit_text and "h2" in audit_text


def _loads(result: str) -> dict:
    import json

    return json.loads(result)


def test_completed_pdf_record_stores_completed_and_audit_attachments(monkeypatch):
    from tools import signature_tool

    statements = []
    events = []

    monkeypatch.setattr(signature_tool.sql, "one", lambda query, *, user=None: {"request_id": "req-1"} if "document_requests" in query else None)

    def fake_statement_one(query, *, user=None):
        statements.append(query)
        if "INSERT INTO signature.attachments" in query:
            return {"attachment_id": "att", "kind": "completed_pdf", "sha256": "c" * 64}
        return {}

    monkeypatch.setattr(signature_tool.sql, "statement_one", fake_statement_one)
    monkeypatch.setattr(signature_tool.sql, "psql", lambda query, *, user=None: statements.append(query))
    monkeypatch.setattr(signature_tool, "_record_event", lambda *args, **kwargs: events.append((args, kwargs)) or {"event_hash": "event"})

    result = _loads(signature_tool._handle_completed_pdf_record({
        "request_id": "req-1",
        "completed_pdf": {"storage_path": "/tmp/completed.pdf", "filename": "completed.pdf", "sha256": "c" * 64, "byte_size": 10},
        "audit_pdf": {"storage_path": "/tmp/audit.pdf", "filename": "audit.pdf", "sha256": "a" * 64, "byte_size": 20},
        "original_sha256": "o" * 64,
        "final_sha256": "c" * 64,
        "approval_hashes": ["p" * 64],
        "visual_qa_evidence": {"field_count": 2},
    }))

    assert result["ok"] is True
    joined = "\n".join(statements)
    assert "INSERT INTO signature.attachments" in joined
    assert "completed_pdf" in joined
    assert "audit_pdf" in joined
    assert "completed_document_url" in joined
    assert events and events[0][1]["event_type"] == "completed"


def _sample_pdf(path: Path) -> None:
    c = canvas.Canvas(str(path), pagesize=(612, 792))
    c.setFont("Helvetica", 12)
    c.drawString(72, 720, "Contrato de prueba SitioUno")
    c.save()


def test_stamp_signed_pdf_uses_open_stack_and_adds_audit_page(tmp_path: Path):
    input_pdf = tmp_path / "input.pdf"
    output_pdf = tmp_path / "signed.pdf"
    _sample_pdf(input_pdf)

    document_hash = sha256_file(input_pdf)
    result = stamp_signed_pdf(
        input_pdf=input_pdf,
        output_pdf=output_pdf,
        request_id="req-test-1",
        source_id="quote-test-1",
        signer="Jean García",
        signed_at="2026-06-19T12:00:00+00:00",
        approval_hash="a" * 64,
        document_hash=document_hash,
        event_id="evt-test-1",
    )

    assert result["pdf_backend"] == "pypdf-reportlab"
    assert output_pdf.exists()
    assert result["signed_sha256"] == sha256_file(output_pdf)
    reader = PdfReader(str(output_pdf))
    assert len(reader.pages) == 2
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    assert "FIRMADO DIGITALMENTE" in extracted
    assert "Certificado de aprobación" in extracted

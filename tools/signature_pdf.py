"""PDF stamping helpers for Signature Core completed documents.

This module intentionally has no runtime dependency on the signing database. It takes
an already-approved PDF plus approval evidence and writes a visible signed PDF with
all configured fields rendered into their PDF rectangles. It can also generate a
separate audit/certificate PDF that includes hashes which cannot be embedded into
self-hashing artifacts (notably the final completed-PDF SHA-256).

Commercial runtime policy: prefer the permissive/open `pypdf` + `reportlab`
backend. PyMuPDF/fitz is kept only as a research/dev fallback for legacy local
workflows and tests.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any


_FIELD_FILL = (0.93, 1.0, 0.95)
_FIELD_STROKE = (0.02, 0.38, 0.18)
_TEXT_COLOR = (0, 0, 0)
_MUTED_COLOR = (0.25, 0.25, 0.25)
_BRAND_COLOR = (0.02, 0.28, 0.16)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _format_signed_at(value: str | None) -> str:
    if not value:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return value.replace("T", " ").replace("+00:00", " UTC")


def _default_audit_text() -> str:
    return (
        "Este PDF fue actualizado automáticamente después de recibir la aprobación del firmante. "
        "La evidencia queda persistida en Signature Core con hashes de aprobación, SHA-256 del documento original "
        "y eventos encadenados. El SHA-256 final del PDF completado se registra en el audit PDF separado porque "
        "un archivo no puede contener su propio hash final sin invalidarlo."
    )


def _load_fitz():
    try:
        import fitz  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:  # pragma: no cover - depends on deployment extras
        raise RuntimeError(
            "Open PDF dependencies (`pypdf` + `reportlab`) are required for commercial runtime; "
            "PyMuPDF/fitz is only an R&D fallback and is not installed here."
        ) from exc
    return fitz


def _page_index(field: dict[str, Any]) -> int:
    if field.get("page") is not None:
        return max(0, int(field["page"]))
    if field.get("page_index") is not None:
        return max(0, int(field["page_index"]))
    if field.get("page_number") is not None:
        return max(0, int(field["page_number"]) - 1)
    return 0


def _rect_values(field: dict[str, Any]) -> tuple[float, float, float, float]:
    rect = field.get("rect") or field.get("rectangle") or field.get("pdf_rect")
    if isinstance(rect, dict):
        x = float(rect.get("x", rect.get("left", rect.get("x0", 0))))
        y = float(rect.get("y", rect.get("top", rect.get("y0", 0))))
        if "x1" in rect and "y1" in rect:
            return x, y, float(rect["x1"]), float(rect["y1"])
        width = float(rect.get("width", rect.get("w", 180)))
        height = float(rect.get("height", rect.get("h", 42)))
        return x, y, x + width, y + height
    if isinstance(rect, (list, tuple)) and len(rect) == 4:
        return float(rect[0]), float(rect[1]), float(rect[2]), float(rect[3])
    raise ValueError(f"field {field.get('field_id') or field.get('name') or '<unknown>'} is missing a configured PDF rectangle")


def _field_rect(fitz: Any, field: dict[str, Any]):
    x0, y0, x1, y1 = _rect_values(field)
    return fitz.Rect(x0, y0, x1, y1)


def _field_value(field: dict[str, Any]) -> str:
    field_type = str(field.get("type") or field.get("field_type") or "text").lower()
    if field_type in {"signature", "initials"}:
        value = field.get("signature_text") or field.get("value") or field.get("text") or "Firmado"
    elif field_type in {"checkbox", "check"}:
        value = "☑" if field.get("value") in (True, "true", "1", "yes", "on", "checked") else "☐"
    else:
        value = field.get("value") or field.get("text") or ""
    return str(value)


def _field_label(field: dict[str, Any]) -> str:
    field_type = str(field.get("type") or field.get("field_type") or "text").lower()
    if field.get("label"):
        return str(field["label"])
    if field_type == "signature":
        return "Firma"
    if field_type == "initials":
        return "Iniciales"
    return str(field.get("field_id") or field.get("name") or "Campo")


def _write_textbox(page: Any, rect: Any, text: str, *, fontsize: float = 9, fontname: str = "helv", color: tuple = _TEXT_COLOR) -> None:
    if hasattr(page, "insert_textbox"):
        page.insert_textbox(rect, text, fontsize=fontsize, fontname=fontname, color=color)
    else:  # pragma: no cover - compatibility with very old fitz-like APIs
        page.insert_text((rect.x0 + 4, rect.y0 + fontsize + 4), text, fontsize=fontsize, fontname=fontname, color=color)


def _wrap_text(text: str, max_chars: int = 95) -> list[str]:
    lines: list[str] = []
    line = ""
    for word in str(text).split():
        candidate = f"{line} {word}".strip()
        if len(candidate) > max_chars and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines or [""]


def _draw_reportlab_wrapped(canvas_obj: Any, text: str, *, x: float, y: float, max_chars: int = 95, leading: float = 12, font: str = "Helvetica", size: float = 9) -> None:
    canvas_obj.setFont(font, size)
    current_y = y
    for line in _wrap_text(text, max_chars=max_chars):
        canvas_obj.drawString(x, current_y, line)
        current_y -= leading


def _draw_submitted_fields_pymupdf(doc: Any, fitz: Any, submitted_fields: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rendered: list[dict[str, Any]] = []
    for idx, field in enumerate(submitted_fields, start=1):
        page_index = _page_index(field)
        if page_index >= doc.page_count:
            raise ValueError(f"field {field.get('field_id') or idx} targets page {page_index}, but PDF has {doc.page_count} pages")
        rect = _field_rect(fitz, field)
        page = doc[page_index]
        label = _field_label(field)
        value = _field_value(field)
        field_type = str(field.get("type") or field.get("field_type") or "text").lower()
        display = f"{label}: {value}" if label else value
        page.draw_rect(rect, color=_FIELD_STROKE, fill=_FIELD_FILL, width=1.0)
        _write_textbox(page, rect, display, fontsize=float(field.get("font_size") or (12 if field_type == "signature" else 9)), fontname="helv", color=_TEXT_COLOR)
        rendered.append({
            "field_id": field.get("field_id") or field.get("name") or f"field-{idx}",
            "label": label,
            "type": field_type,
            "page": page_index,
            "rect": [rect.x0, rect.y0, rect.x1, rect.y1],
            "value_preview": value[:80],
            "submitter_id": field.get("submitter_id"),
        })
    return rendered


def _draw_submitted_fields_reportlab(writer: Any, PdfReader: Any, canvas: Any, submitted_fields: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rendered: list[dict[str, Any]] = []
    fields_by_page: dict[int, list[tuple[int, dict[str, Any]]]] = {}
    for idx, field in enumerate(submitted_fields, start=1):
        fields_by_page.setdefault(_page_index(field), []).append((idx, field))

    for page_index, page_fields in fields_by_page.items():
        if page_index >= len(writer.pages):
            raise ValueError(f"field {page_fields[0][1].get('field_id') or page_fields[0][0]} targets page {page_index}, but PDF has {len(writer.pages)} pages")
        page = writer.pages[page_index]
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)
        buffer = BytesIO()
        overlay = canvas.Canvas(buffer, pagesize=(page_width, page_height))
        for idx, field in page_fields:
            x0, y0, x1, y1 = _rect_values(field)
            width = max(1.0, x1 - x0)
            height = max(1.0, y1 - y0)
            # Factory field coordinates follow the PyMuPDF/top-left convention;
            # ReportLab draws from bottom-left, so flip y around page height.
            draw_y = page_height - y1
            label = _field_label(field)
            value = _field_value(field)
            field_type = str(field.get("type") or field.get("field_type") or "text").lower()
            display = f"{label}: {value}" if label else value
            font_size = float(field.get("font_size") or (12 if field_type == "signature" else 9))
            overlay.setStrokeColorRGB(*_FIELD_STROKE)
            overlay.setFillColorRGB(*_FIELD_FILL)
            overlay.rect(x0, draw_y, width, height, stroke=1, fill=1)
            overlay.setFillColorRGB(*_TEXT_COLOR)
            _draw_reportlab_wrapped(overlay, display, x=x0 + 4, y=draw_y + height - font_size - 4, max_chars=max(12, int(width / max(font_size * 0.45, 1))), leading=font_size + 2, size=font_size)
            rendered.append({
                "field_id": field.get("field_id") or field.get("name") or f"field-{idx}",
                "label": label,
                "type": field_type,
                "page": page_index,
                "rect": [x0, y0, x1, y1],
                "value_preview": value[:80],
                "submitter_id": field.get("submitter_id"),
            })
        overlay.save()
        buffer.seek(0)
        page.merge_page(PdfReader(buffer).pages[0])
    return rendered


def _draw_legacy_stamp_reportlab(page: Any, PdfReader: Any, canvas: Any, *, signer_text: str, signed_at_text: str, approval_hash: str, document_hash: str) -> tuple[list[float], BytesIO]:
    page_width = float(page.mediabox.width)
    page_height = float(page.mediabox.height)
    stamp_width = 234
    stamp_height = 113
    stamp_x = max(36, page_width - 270)
    stamp_y = 42
    buffer = BytesIO()
    overlay = canvas.Canvas(buffer, pagesize=(page_width, page_height))
    overlay.setStrokeColorRGB(*_FIELD_STROKE)
    overlay.setFillColorRGB(*_FIELD_FILL)
    overlay.rect(stamp_x, stamp_y, stamp_width, stamp_height, stroke=1, fill=1)
    overlay.setFillColorRGB(0.02, 0.32, 0.14)
    overlay.setFont("Helvetica-Bold", 12)
    overlay.drawString(stamp_x + 12, stamp_y + stamp_height - 24, "FIRMADO DIGITALMENTE")
    overlay.setFillColorRGB(*_TEXT_COLOR)
    overlay.setFont("Helvetica", 9.5)
    overlay.drawString(stamp_x + 12, stamp_y + stamp_height - 47, f"Por: {signer_text[:42]}")
    overlay.setFont("Helvetica", 8.5)
    overlay.drawString(stamp_x + 12, stamp_y + stamp_height - 64, f"Fecha: {signed_at_text[:34]}")
    overlay.setFont("Courier", 8)
    overlay.drawString(stamp_x + 12, stamp_y + stamp_height - 84, f"Hash aprobación: {approval_hash[:18]}…")
    overlay.drawString(stamp_x + 12, stamp_y + stamp_height - 100, f"Hash documento: {document_hash[:18]}…")
    overlay.save()
    buffer.seek(0)
    page.merge_page(PdfReader(buffer).pages[0])
    # Return PyMuPDF/top-left-style rect metadata for compatibility.
    return [stamp_x, page_height - stamp_y - stamp_height, stamp_x + stamp_width, page_height - stamp_y], buffer


def _add_completion_page_reportlab(writer: Any, PdfReader: Any, canvas: Any, *, request_id: str, source_id: str, signer_text: str, signed_at_text: str, document_hash: str, approval_hashes: list[str], event_chain: list[dict[str, Any]], disclaimer: str | None) -> None:
    buffer = BytesIO()
    audit = canvas.Canvas(buffer, pagesize=(612, 792))
    audit.setStrokeColorRGB(*_BRAND_COLOR)
    audit.rect(36, 36, 540, 720, stroke=1, fill=0)
    audit.setFillColorRGB(*_BRAND_COLOR)
    audit.setFont("Helvetica-Bold", 18)
    audit.drawString(56, 714, "Certificado de aprobación y firma digital")
    audit.setFillColorRGB(*_MUTED_COLOR)
    audit.setFont("Helvetica", 11)
    audit.drawString(56, 682, "SitioUno / Zeus Signature Core")
    details = [
        ("Documento", source_id or request_id),
        ("Solicitud de firma", request_id),
        ("Firmante", signer_text),
        ("Fecha de firma", signed_at_text),
        ("Hash SHA-256 del documento original/aprobado", document_hash),
        ("Hashes SHA-256 de aprobación", ", ".join(approval_hashes) or "N/A"),
    ]
    y = 642
    for label, value in details:
        audit.setFillColorRGB(*_MUTED_COLOR)
        audit.setFont("Helvetica", 9)
        audit.drawString(56, y, label)
        audit.setFillColorRGB(*_TEXT_COLOR)
        _draw_reportlab_wrapped(audit, str(value), x=230, y=y, max_chars=70, leading=10, size=8.4)
        y -= 46 if len(str(value)) < 80 else 62
    audit.setFillColorRGB(*_BRAND_COLOR)
    audit.setFont("Helvetica", 10)
    audit.drawString(56, y + 10, "Resumen de cadena de eventos")
    y -= 22
    audit.setFillColorRGB(*_TEXT_COLOR)
    for event in event_chain[:8]:
        summary = f"#{event.get('signature_event_id', '?')} {event.get('event_type', '?')} hash={str(event.get('event_hash', ''))[:18]} prev={str(event.get('previous_event_hash') or '')[:18] or 'ROOT'}"
        audit.setFont("Courier", 7.8)
        audit.drawString(56, y, summary[:120])
        y -= 22
    audit.setFillColorRGB(0.1, 0.1, 0.1)
    _draw_reportlab_wrapped(audit, disclaimer or _default_audit_text(), x=56, y=132, max_chars=105, leading=11, size=8.5)
    audit.save()
    buffer.seek(0)
    writer.add_page(PdfReader(buffer).pages[0])


def _write_audit_pdf_reportlab(*, canvas: Any, audit_pdf: Path, request_id: str, source_id: str, signer_text: str, signed_at_text: str, original_sha: str, final_sha: str, document_hash: str, approval_hashes: list[str], event_chain: list[dict[str, Any]], visual_qa_evidence: dict[str, Any]) -> None:
    audit_pdf.parent.mkdir(parents=True, exist_ok=True)
    audit = canvas.Canvas(str(audit_pdf), pagesize=(612, 792))
    audit.setStrokeColorRGB(*_BRAND_COLOR)
    audit.rect(36, 36, 540, 720, stroke=1, fill=0)
    audit.setFillColorRGB(*_BRAND_COLOR)
    audit.setFont("Helvetica-Bold", 18)
    audit.drawString(56, 716, "Audit PDF — Signature Core")
    details = [
        ("Documento", source_id or request_id),
        ("Solicitud de firma", request_id),
        ("Firmante", signer_text),
        ("Fecha de firma", signed_at_text),
        ("Hash SHA-256 del PDF original de entrada", original_sha),
        ("Hash SHA-256 del documento aprobado", document_hash),
        ("Hash SHA-256 del PDF final firmado", final_sha),
        ("Hashes SHA-256 de aprobación", ", ".join(approval_hashes) or "N/A"),
    ]
    y = 672
    for label, value in details:
        audit.setFillColorRGB(*_MUTED_COLOR)
        audit.setFont("Helvetica", 9)
        audit.drawString(56, y, label)
        audit.setFillColorRGB(*_TEXT_COLOR)
        _draw_reportlab_wrapped(audit, str(value), x=245, y=y, max_chars=64, leading=10, size=8)
        y -= 46 if len(str(value)) < 80 else 62
    audit.setFillColorRGB(*_BRAND_COLOR)
    audit.setFont("Helvetica", 10)
    audit.drawString(56, y + 8, "Resumen de cadena de eventos")
    y -= 20
    audit.setFillColorRGB(*_TEXT_COLOR)
    for event in event_chain[:10]:
        summary = f"#{event.get('signature_event_id', '?')} {event.get('event_type', '?')} hash={event.get('event_hash', '')} prev={event.get('previous_event_hash') or 'ROOT'}"
        audit.setFont("Courier", 7.2)
        audit.drawString(56, y, summary[:130])
        y -= 22
    qa = json.dumps(visual_qa_evidence, ensure_ascii=False, sort_keys=True)
    audit.setFillColorRGB(*_BRAND_COLOR)
    audit.setFont("Helvetica", 10)
    audit.drawString(56, 150, "Evidencia visual QA")
    audit.setFillColorRGB(*_TEXT_COLOR)
    _draw_reportlab_wrapped(audit, qa[:1200], x=56, y=132, max_chars=110, leading=9, font="Courier", size=7.2)
    audit.save()


def _add_completion_page_pymupdf(doc: Any, fitz: Any, *, request_id: str, source_id: str, signer_text: str, signed_at_text: str, document_hash: str, approval_hashes: list[str], event_chain: list[dict[str, Any]], disclaimer: str | None) -> None:
    audit = doc.new_page(width=612, height=792)
    audit.draw_rect(fitz.Rect(36, 36, 576, 756), color=_BRAND_COLOR, width=1.2)
    audit.insert_text((56, 78), "Certificado de aprobación y firma digital", fontsize=18, fontname="helv", color=_BRAND_COLOR)
    audit.insert_text((56, 110), "SitioUno / Zeus Signature Core", fontsize=11, fontname="helv", color=_MUTED_COLOR)
    details = [
        ("Documento", source_id or request_id),
        ("Solicitud de firma", request_id),
        ("Firmante", signer_text),
        ("Fecha de firma", signed_at_text),
        ("Hash SHA-256 del documento original/aprobado", document_hash),
        ("Hashes SHA-256 de aprobación", ", ".join(approval_hashes) or "N/A"),
    ]
    y = 150
    for label, value in details:
        audit.insert_text((56, y), label, fontsize=9, fontname="helv", color=_MUTED_COLOR)
        _write_textbox(audit, fitz.Rect(230, y - 12, 548, y + 36), str(value), fontsize=8.4, fontname="helv", color=_TEXT_COLOR)
        y += 46 if len(str(value)) < 80 else 62
    audit.insert_text((56, y + 10), "Resumen de cadena de eventos", fontsize=10, fontname="helv", color=_BRAND_COLOR)
    y += 32
    for event in event_chain[:8]:
        summary = f"#{event.get('signature_event_id', '?')} {event.get('event_type', '?')} hash={str(event.get('event_hash', ''))[:18]} prev={str(event.get('previous_event_hash') or '')[:18] or 'ROOT'}"
        _write_textbox(audit, fitz.Rect(56, y, 548, y + 22), summary, fontsize=7.8, fontname="cour", color=_TEXT_COLOR)
        y += 22
    _write_textbox(audit, fitz.Rect(56, 660, 548, 735), disclaimer or _default_audit_text(), fontsize=8.5, fontname="helv", color=(0.1, 0.1, 0.1))


def _write_audit_pdf_pymupdf(*, fitz: Any, audit_pdf: Path, request_id: str, source_id: str, signer_text: str, signed_at_text: str, original_sha: str, final_sha: str, document_hash: str, approval_hashes: list[str], event_chain: list[dict[str, Any]], visual_qa_evidence: dict[str, Any]) -> None:
    audit_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    page.draw_rect(fitz.Rect(36, 36, 576, 756), color=_BRAND_COLOR, width=1.2)
    page.insert_text((56, 76), "Audit PDF — Signature Core", fontsize=18, fontname="helv", color=_BRAND_COLOR)
    details = [
        ("Documento", source_id or request_id),
        ("Solicitud de firma", request_id),
        ("Firmante", signer_text),
        ("Fecha de firma", signed_at_text),
        ("Hash SHA-256 del PDF original de entrada", original_sha),
        ("Hash SHA-256 del documento aprobado", document_hash),
        ("Hash SHA-256 del PDF final firmado", final_sha),
        ("Hashes SHA-256 de aprobación", ", ".join(approval_hashes) or "N/A"),
    ]
    y = 120
    for label, value in details:
        page.insert_text((56, y), label, fontsize=9, fontname="helv", color=_MUTED_COLOR)
        _write_textbox(page, fitz.Rect(245, y - 12, 548, y + 36), str(value), fontsize=8, fontname="helv", color=_TEXT_COLOR)
        y += 46 if len(str(value)) < 80 else 62
    page.insert_text((56, y + 8), "Resumen de cadena de eventos", fontsize=10, fontname="helv", color=_BRAND_COLOR)
    y += 30
    for event in event_chain[:10]:
        summary = f"#{event.get('signature_event_id', '?')} {event.get('event_type', '?')} hash={event.get('event_hash', '')} prev={event.get('previous_event_hash') or 'ROOT'}"
        _write_textbox(page, fitz.Rect(56, y, 548, y + 30), summary, fontsize=7.2, fontname="cour", color=_TEXT_COLOR)
        y += 28
    qa = json.dumps(visual_qa_evidence, ensure_ascii=False, sort_keys=True)
    page.insert_text((56, 650), "Evidencia visual QA", fontsize=10, fontname="helv", color=_BRAND_COLOR)
    _write_textbox(page, fitz.Rect(56, 670, 548, 738), qa[:1200], fontsize=7.2, fontname="cour", color=_TEXT_COLOR)
    doc.save(str(audit_pdf), garbage=4, deflate=True)
    doc.close()


def _final_result(*, input_path: Path, output_path: Path, audit_path: Path | None, original_sha: str, final_sha: str, audit_sha: str | None, document_hash: str, approval_hashes: list[str], rendered_fields: list[dict[str, Any]], chain: list[dict[str, Any]], pdf_backend: str) -> dict[str, Any]:
    visual_qa_evidence = {
        "field_count": len(rendered_fields),
        "rendered_fields": rendered_fields,
        "certificate_page": True,
        "event_count": len(chain),
        "approval_hash_count": len(approval_hashes),
        "pdf_backend": pdf_backend,
    }
    attachments = [{
        "kind": "completed_pdf",
        "filename": output_path.name,
        "mime_type": "application/pdf",
        "storage_path": str(output_path),
        "byte_size": output_path.stat().st_size,
        "sha256": final_sha,
        "metadata": {"original_sha256": original_sha, "document_hash_sha256": document_hash, "approval_hashes": approval_hashes, "visual_qa_evidence": visual_qa_evidence, "pdf_backend": pdf_backend},
    }]
    if audit_path and audit_sha:
        attachments.append({
            "kind": "audit_pdf",
            "filename": audit_path.name,
            "mime_type": "application/pdf",
            "storage_path": str(audit_path),
            "byte_size": audit_path.stat().st_size,
            "sha256": audit_sha,
            "metadata": {"original_sha256": original_sha, "final_sha256": final_sha, "document_hash_sha256": document_hash, "approval_hashes": approval_hashes, "event_chain_summary": chain, "visual_qa_evidence": visual_qa_evidence, "pdf_backend": pdf_backend},
        })
    return {
        "input": str(input_path),
        "output": str(output_path),
        "audit_output": str(audit_path) if audit_path else None,
        "original_sha256": original_sha,
        "signed_sha256": final_sha,
        "final_sha256": final_sha,
        "audit_sha256": audit_sha,
        "byte_size": output_path.stat().st_size,
        "attachments": attachments,
        "visual_qa_evidence": visual_qa_evidence,
        "pdf_backend": pdf_backend,
    }


def _stamp_signed_pdf_open_stack(*, input_path: Path, output_path: Path, audit_path: Path | None, request_id: str, source_id: str, signer_text: str, signed_at_text: str, approval_hash: str, document_hash: str, all_approval_hashes: list[str], chain: list[dict[str, Any]], submitted_fields: list[dict[str, Any]], disclaimer: str | None, original_sha: str) -> dict[str, Any]:
    from pypdf import PdfReader, PdfWriter  # type: ignore[import-not-found]
    from reportlab.pdfgen import canvas  # type: ignore[import-not-found]

    writer = PdfWriter(clone_from=str(input_path))
    if not writer.pages:
        raise ValueError("PDF has no pages")

    rendered_fields = _draw_submitted_fields_reportlab(writer, PdfReader, canvas, submitted_fields)
    if not rendered_fields:
        rect, _ = _draw_legacy_stamp_reportlab(writer.pages[0], PdfReader, canvas, signer_text=signer_text, signed_at_text=signed_at_text, approval_hash=approval_hash, document_hash=document_hash)
        rendered_fields.append({"field_id": "legacy-completion-stamp", "label": "Sello", "type": "stamp", "page": 0, "rect": rect, "value_preview": signer_text[:80], "submitter_id": None})

    _add_completion_page_reportlab(writer, PdfReader, canvas, request_id=request_id, source_id=source_id, signer_text=signer_text, signed_at_text=signed_at_text, document_hash=document_hash, approval_hashes=all_approval_hashes, event_chain=chain, disclaimer=disclaimer)

    if output_path.resolve() == input_path.resolve():
        tmp = output_path.with_suffix(output_path.suffix + ".tmp")
        with tmp.open("wb") as fh:
            writer.write(fh)
        os.replace(tmp, output_path)
    else:
        with output_path.open("wb") as fh:
            writer.write(fh)

    final_sha = sha256_file(output_path)
    visual_preview = {"field_count": len(rendered_fields), "rendered_fields": rendered_fields, "certificate_page": True, "event_count": len(chain), "approval_hash_count": len(all_approval_hashes), "pdf_backend": "pypdf-reportlab"}
    audit_sha = None
    if audit_path:
        _write_audit_pdf_reportlab(canvas=canvas, audit_pdf=audit_path, request_id=request_id, source_id=source_id, signer_text=signer_text, signed_at_text=signed_at_text, original_sha=original_sha, final_sha=final_sha, document_hash=document_hash, approval_hashes=all_approval_hashes, event_chain=chain, visual_qa_evidence=visual_preview)
        audit_sha = sha256_file(audit_path)

    return _final_result(input_path=input_path, output_path=output_path, audit_path=audit_path, original_sha=original_sha, final_sha=final_sha, audit_sha=audit_sha, document_hash=document_hash, approval_hashes=all_approval_hashes, rendered_fields=rendered_fields, chain=chain, pdf_backend="pypdf-reportlab")


def _stamp_signed_pdf_pymupdf_fallback(*, input_path: Path, output_path: Path, audit_path: Path | None, request_id: str, source_id: str, signer_text: str, signed_at_text: str, approval_hash: str, document_hash: str, all_approval_hashes: list[str], chain: list[dict[str, Any]], submitted_fields: list[dict[str, Any]], disclaimer: str | None, original_sha: str) -> dict[str, Any]:
    fitz = _load_fitz()
    doc = fitz.open(str(input_path))
    if doc.page_count < 1:
        raise ValueError("PDF has no pages")

    rendered_fields = _draw_submitted_fields_pymupdf(doc, fitz, submitted_fields)
    if not rendered_fields:
        page = doc[0]
        rect = page.rect
        stamp = fitz.Rect(rect.x1 - 270, rect.y1 - 155, rect.x1 - 36, rect.y1 - 42)
        page.draw_rect(stamp, color=_FIELD_STROKE, fill=_FIELD_FILL, width=1.4)
        page.insert_text((stamp.x0 + 12, stamp.y0 + 22), "FIRMADO DIGITALMENTE", fontsize=12, fontname="helv", color=(0.02, 0.32, 0.14))
        page.insert_text((stamp.x0 + 12, stamp.y0 + 45), f"Por: {signer_text[:42]}", fontsize=9.5, fontname="helv", color=_TEXT_COLOR)
        page.insert_text((stamp.x0 + 12, stamp.y0 + 62), f"Fecha: {signed_at_text[:34]}", fontsize=8.5, fontname="helv", color=_TEXT_COLOR)
        page.insert_text((stamp.x0 + 12, stamp.y0 + 82), f"Hash aprobación: {approval_hash[:18]}…", fontsize=8, fontname="cour", color=_TEXT_COLOR)
        page.insert_text((stamp.x0 + 12, stamp.y0 + 98), f"Hash documento: {document_hash[:18]}…", fontsize=8, fontname="cour", color=_TEXT_COLOR)
        rendered_fields.append({"field_id": "legacy-completion-stamp", "label": "Sello", "type": "stamp", "page": 0, "rect": [stamp.x0, stamp.y0, stamp.x1, stamp.y1], "value_preview": signer_text[:80], "submitter_id": None})

    _add_completion_page_pymupdf(doc, fitz, request_id=request_id, source_id=source_id, signer_text=signer_text, signed_at_text=signed_at_text, document_hash=document_hash, approval_hashes=all_approval_hashes, event_chain=chain, disclaimer=disclaimer)

    if output_path.resolve() == input_path.resolve():
        tmp = output_path.with_suffix(output_path.suffix + ".tmp")
        doc.save(str(tmp), garbage=4, deflate=True)
        doc.close()
        os.replace(tmp, output_path)
    else:
        doc.save(str(output_path), garbage=4, deflate=True)
        doc.close()

    final_sha = sha256_file(output_path)
    visual_preview = {"field_count": len(rendered_fields), "rendered_fields": rendered_fields, "certificate_page": True, "event_count": len(chain), "approval_hash_count": len(all_approval_hashes), "pdf_backend": "pymupdf-rd-fallback"}
    audit_sha = None
    if audit_path:
        _write_audit_pdf_pymupdf(fitz=fitz, audit_pdf=audit_path, request_id=request_id, source_id=source_id, signer_text=signer_text, signed_at_text=signed_at_text, original_sha=original_sha, final_sha=final_sha, document_hash=document_hash, approval_hashes=all_approval_hashes, event_chain=chain, visual_qa_evidence=visual_preview)
        audit_sha = sha256_file(audit_path)

    return _final_result(input_path=input_path, output_path=output_path, audit_path=audit_path, original_sha=original_sha, final_sha=final_sha, audit_sha=audit_sha, document_hash=document_hash, approval_hashes=all_approval_hashes, rendered_fields=rendered_fields, chain=chain, pdf_backend="pymupdf-rd-fallback")


def stamp_signed_pdf(
    *,
    input_pdf: str | Path,
    output_pdf: str | Path,
    request_id: str,
    source_id: str = "",
    signer: str,
    signed_at: str | None,
    approval_hash: str,
    document_hash: str,
    event_id: str = "",
    disclaimer: str | None = None,
    submitted_fields: list[dict[str, Any]] | None = None,
    approval_hashes: list[str] | None = None,
    event_chain: list[dict[str, Any]] | None = None,
    audit_pdf: str | Path | None = None,
) -> dict[str, Any]:
    """Write a visibly signed PDF and return attachment-ready metadata.

    `submitted_fields` must contain configured PDF rectangles (`rect`,
    `rectangle`, or `pdf_rect`) and optional page/page_number coordinates. Every
    submitted field is rendered into the requested rectangle before the
    completion certificate page is appended.
    """
    input_path = Path(input_pdf)
    output_path = Path(output_pdf)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path = Path(audit_pdf) if audit_pdf else None

    original_sha = sha256_file(input_path)
    signed_at_text = _format_signed_at(signed_at)
    signer_text = signer.strip() or "Firmante"
    all_approval_hashes: list[str] = list(dict.fromkeys(str(h) for h in [approval_hash, *(approval_hashes or [])] if h))
    chain = list(event_chain or [])
    if event_id and not chain:
        chain.append({"signature_event_id": event_id, "event_type": "approved", "event_hash": event_id, "previous_event_hash": None})
    fields = submitted_fields or []

    common = {
        "input_path": input_path,
        "output_path": output_path,
        "audit_path": audit_path,
        "request_id": request_id,
        "source_id": source_id,
        "signer_text": signer_text,
        "signed_at_text": signed_at_text,
        "approval_hash": approval_hash,
        "document_hash": document_hash,
        "all_approval_hashes": all_approval_hashes,
        "chain": chain,
        "submitted_fields": fields,
        "disclaimer": disclaimer,
        "original_sha": original_sha,
    }
    try:
        return _stamp_signed_pdf_open_stack(**common)
    except Exception:
        # Preserve R&D/local compatibility with existing PyMuPDF-only test and
        # document-worker environments, but do not make fitz the commercial path.
        return _stamp_signed_pdf_pymupdf_fallback(**common)


def _load_json_arg(value: str | None, default: Any) -> Any:
    if not value:
        return default
    path = Path(value)
    if path.exists():
        return json.loads(path.read_text("utf-8"))
    return json.loads(value)


def main() -> None:
    parser = argparse.ArgumentParser(description="Stamp a Signature Core PDF as signed")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--audit-output", default="")
    parser.add_argument("--request-id", required=True)
    parser.add_argument("--source-id", default="")
    parser.add_argument("--signer", required=True)
    parser.add_argument("--signed-at", default="")
    parser.add_argument("--approval-hash", required=True)
    parser.add_argument("--approval-hashes", default="")
    parser.add_argument("--document-hash", required=True)
    parser.add_argument("--event-id", default="")
    parser.add_argument("--submitted-fields", default="", help="JSON array or path to JSON file with submitted fields and PDF rectangles")
    parser.add_argument("--event-chain", default="", help="JSON array or path to JSON file with audit event-chain rows")
    args = parser.parse_args()
    result = stamp_signed_pdf(
        input_pdf=args.input,
        output_pdf=args.output,
        audit_pdf=args.audit_output or None,
        request_id=args.request_id,
        source_id=args.source_id,
        signer=args.signer,
        signed_at=args.signed_at,
        approval_hash=args.approval_hash,
        approval_hashes=_load_json_arg(args.approval_hashes, []),
        document_hash=args.document_hash,
        event_id=args.event_id,
        submitted_fields=_load_json_arg(args.submitted_fields, []),
        event_chain=_load_json_arg(args.event_chain, []),
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

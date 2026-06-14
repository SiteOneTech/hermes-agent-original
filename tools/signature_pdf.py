"""PDF stamping helpers for Signature Core completed documents.

This module intentionally has no runtime dependency on the signing database. It takes
an already-approved PDF plus approval evidence and writes a visible signed PDF with
all configured fields rendered into their PDF rectangles. It can also generate a
separate audit/certificate PDF that includes hashes which cannot be embedded into
self-hashing artifacts (notably the final completed-PDF SHA-256).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


_FIELD_FILL = (0.93, 1.0, 0.95)
_FIELD_STROKE = (0.02, 0.38, 0.18)
_TEXT_COLOR = (0, 0, 0)
_MUTED_COLOR = (0.25, 0.25, 0.25)


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


def _load_fitz():
    try:
        import fitz  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:  # pragma: no cover - depends on deployment extras
        raise RuntimeError("PyMuPDF (`fitz`) is required to stamp signed PDFs") from exc
    return fitz


def _page_index(field: dict[str, Any]) -> int:
    if field.get("page") is not None:
        return max(0, int(field["page"]))
    if field.get("page_index") is not None:
        return max(0, int(field["page_index"]))
    if field.get("page_number") is not None:
        return max(0, int(field["page_number"]) - 1)
    return 0


def _field_rect(fitz: Any, field: dict[str, Any]):
    rect = field.get("rect") or field.get("rectangle") or field.get("pdf_rect")
    if isinstance(rect, dict):
        x = float(rect.get("x", rect.get("left", rect.get("x0", 0))))
        y = float(rect.get("y", rect.get("top", rect.get("y0", 0))))
        if "x1" in rect and "y1" in rect:
            return fitz.Rect(x, y, float(rect["x1"]), float(rect["y1"]))
        width = float(rect.get("width", rect.get("w", 180)))
        height = float(rect.get("height", rect.get("h", 42)))
        return fitz.Rect(x, y, x + width, y + height)
    if isinstance(rect, (list, tuple)) and len(rect) == 4:
        return fitz.Rect(float(rect[0]), float(rect[1]), float(rect[2]), float(rect[3]))
    raise ValueError(f"field {field.get('field_id') or field.get('name') or '<unknown>'} is missing a configured PDF rectangle")


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


def _draw_submitted_fields(doc: Any, fitz: Any, submitted_fields: list[dict[str, Any]]) -> list[dict[str, Any]]:
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


def _add_completion_page(
    doc: Any,
    fitz: Any,
    *,
    request_id: str,
    source_id: str,
    signer_text: str,
    signed_at_text: str,
    document_hash: str,
    approval_hashes: list[str],
    event_chain: list[dict[str, Any]],
    disclaimer: str | None,
) -> None:
    audit = doc.new_page(width=612, height=792)
    audit.draw_rect(fitz.Rect(36, 36, 576, 756), color=(0.02, 0.28, 0.16), width=1.2)
    audit.insert_text((56, 78), "Certificado de aprobación y firma digital", fontsize=18, fontname="helv", color=(0.02, 0.28, 0.16))
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
    audit.insert_text((56, y + 10), "Resumen de cadena de eventos", fontsize=10, fontname="helv", color=(0.02, 0.28, 0.16))
    y += 32
    for event in event_chain[:8]:
        summary = f"#{event.get('signature_event_id', '?')} {event.get('event_type', '?')} hash={str(event.get('event_hash', ''))[:18]} prev={str(event.get('previous_event_hash') or '')[:18] or 'ROOT'}"
        _write_textbox(audit, fitz.Rect(56, y, 548, y + 22), summary, fontsize=7.8, fontname="cour", color=_TEXT_COLOR)
        y += 22
    audit_text = disclaimer or (
        "Este PDF fue actualizado automáticamente después de recibir la aprobación del firmante. "
        "La evidencia queda persistida en Signature Core con hashes de aprobación, SHA-256 del documento original "
        "y eventos encadenados. El SHA-256 final del PDF completado se registra en el audit PDF separado porque "
        "un archivo no puede contener su propio hash final sin invalidarlo."
    )
    _write_textbox(audit, fitz.Rect(56, 660, 548, 735), audit_text, fontsize=8.5, fontname="helv", color=(0.1, 0.1, 0.1))


def _write_audit_pdf(
    *,
    fitz: Any,
    audit_pdf: Path,
    request_id: str,
    source_id: str,
    signer_text: str,
    signed_at_text: str,
    original_sha: str,
    final_sha: str,
    document_hash: str,
    approval_hashes: list[str],
    event_chain: list[dict[str, Any]],
    visual_qa_evidence: dict[str, Any],
) -> None:
    audit_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    page.draw_rect(fitz.Rect(36, 36, 576, 756), color=(0.02, 0.28, 0.16), width=1.2)
    page.insert_text((56, 76), "Audit PDF — Signature Core", fontsize=18, fontname="helv", color=(0.02, 0.28, 0.16))
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
    page.insert_text((56, y + 8), "Resumen de cadena de eventos", fontsize=10, fontname="helv", color=(0.02, 0.28, 0.16))
    y += 30
    for event in event_chain[:10]:
        summary = f"#{event.get('signature_event_id', '?')} {event.get('event_type', '?')} hash={event.get('event_hash', '')} prev={event.get('previous_event_hash') or 'ROOT'}"
        _write_textbox(page, fitz.Rect(56, y, 548, y + 30), summary, fontsize=7.2, fontname="cour", color=_TEXT_COLOR)
        y += 28
    qa = json.dumps(visual_qa_evidence, ensure_ascii=False, sort_keys=True)
    page.insert_text((56, 650), "Evidencia visual QA", fontsize=10, fontname="helv", color=(0.02, 0.28, 0.16))
    _write_textbox(page, fitz.Rect(56, 670, 548, 738), qa[:1200], fontsize=7.2, fontname="cour", color=_TEXT_COLOR)
    doc.save(str(audit_pdf), garbage=4, deflate=True)
    doc.close()


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
    fitz = _load_fitz()
    input_path = Path(input_pdf)
    output_path = Path(output_pdf)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    original_sha = sha256_file(input_path)
    doc = fitz.open(str(input_path))
    if doc.page_count < 1:
        raise ValueError("PDF has no pages")

    signed_at_text = _format_signed_at(signed_at)
    signer_text = signer.strip() or "Firmante"
    all_approval_hashes: list[str] = list(dict.fromkeys(str(h) for h in [approval_hash, *(approval_hashes or [])] if h))
    chain = list(event_chain or [])
    if event_id and not chain:
        chain.append({"signature_event_id": event_id, "event_type": "approved", "event_hash": event_id, "previous_event_hash": None})

    rendered_fields = _draw_submitted_fields(doc, fitz, submitted_fields or [])

    # Backward-compatible visible completion stamp when no explicit field exists.
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

    _add_completion_page(
        doc,
        fitz,
        request_id=request_id,
        source_id=source_id,
        signer_text=signer_text,
        signed_at_text=signed_at_text,
        document_hash=document_hash,
        approval_hashes=all_approval_hashes,
        event_chain=chain,
        disclaimer=disclaimer,
    )

    if output_path.resolve() == input_path.resolve():
        tmp = output_path.with_suffix(output_path.suffix + ".tmp")
        doc.save(str(tmp), garbage=4, deflate=True)
        doc.close()
        os.replace(tmp, output_path)
    else:
        doc.save(str(output_path), garbage=4, deflate=True)
        doc.close()

    final_sha = sha256_file(output_path)
    visual_qa_evidence = {
        "field_count": len(rendered_fields),
        "rendered_fields": rendered_fields,
        "certificate_page": True,
        "event_count": len(chain),
        "approval_hash_count": len(all_approval_hashes),
    }
    audit_sha = None
    audit_path = Path(audit_pdf) if audit_pdf else None
    if audit_path:
        _write_audit_pdf(
            fitz=fitz,
            audit_pdf=audit_path,
            request_id=request_id,
            source_id=source_id,
            signer_text=signer_text,
            signed_at_text=signed_at_text,
            original_sha=original_sha,
            final_sha=final_sha,
            document_hash=document_hash,
            approval_hashes=all_approval_hashes,
            event_chain=chain,
            visual_qa_evidence=visual_qa_evidence,
        )
        audit_sha = sha256_file(audit_path)

    attachments = [{
        "kind": "completed_pdf",
        "filename": output_path.name,
        "mime_type": "application/pdf",
        "storage_path": str(output_path),
        "byte_size": output_path.stat().st_size,
        "sha256": final_sha,
        "metadata": {"original_sha256": original_sha, "document_hash_sha256": document_hash, "approval_hashes": all_approval_hashes, "visual_qa_evidence": visual_qa_evidence},
    }]
    if audit_path and audit_sha:
        attachments.append({
            "kind": "audit_pdf",
            "filename": audit_path.name,
            "mime_type": "application/pdf",
            "storage_path": str(audit_path),
            "byte_size": audit_path.stat().st_size,
            "sha256": audit_sha,
            "metadata": {"original_sha256": original_sha, "final_sha256": final_sha, "document_hash_sha256": document_hash, "approval_hashes": all_approval_hashes, "event_chain_summary": chain, "visual_qa_evidence": visual_qa_evidence},
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
    }


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

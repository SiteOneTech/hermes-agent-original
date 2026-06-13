"""PDF stamping helpers for Signature Core completed documents.

This module intentionally has no runtime dependency on the signing database. It takes
an already-approved PDF plus approval evidence and writes a visible signed PDF with
an audit page. The caller remains responsible for persisting the completed artifact
in Signature Core, usually as `signature.attachments.kind = 'completed_pdf'`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _as_float(mapping: dict[str, Any], key: str, default: float | None = None) -> float:
    value = mapping.get(key, default)
    if value is None:
        raise ValueError(f"{key} is required")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{key} must be a finite number")
    return result


def _page_size(page: dict[str, Any]) -> tuple[float, float]:
    width = _as_float(page, "width")
    height = _as_float(page, "height")
    if width <= 0 or height <= 0:
        raise ValueError("page width and height must be positive")
    return width, height


def normalize_field_coordinates(field: dict[str, Any], page: dict[str, Any]) -> dict[str, Any]:
    """Normalize top-left PDF point coordinates for responsive PDF overlays.

    Signature Core stores `x`, `y`, `width`, and `height` as PDF points using a
    top-left origin because that is the coordinate system exposed by most PDF.js
    overlay UIs. `pdf_y_bottom` is derived for renderers such as ReportLab or
    pdf-lib APIs that draw from a bottom-left PDF origin.
    """
    page_width, page_height = _page_size(page)
    x = _as_float(field, "x", 0)
    y = _as_float(field, "y", 0)
    width = _as_float(field, "width")
    height = _as_float(field, "height")
    if x < 0 or y < 0:
        raise ValueError("field x and y must be non-negative")
    if width <= 0 or height <= 0:
        raise ValueError("field width and height must be positive")
    if x + width > page_width or y + height > page_height:
        raise ValueError("field rectangle must fit inside the PDF page")

    return {
        **field,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "x_pct": x / page_width,
        "y_pct": y / page_height,
        "w_pct": width / page_width,
        "h_pct": height / page_height,
        "pdf_y_bottom": page_height - y - height,
    }


def viewport_to_pdf_points(
    overlay: dict[str, Any],
    page: dict[str, Any],
    *,
    viewport: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Convert normalized or pixel viewport overlay coordinates to PDF points."""
    page_width, page_height = _page_size(page)
    if viewport:
        viewport_width, viewport_height = _page_size(viewport)
        x_pct = _as_float(overlay, "x_px") / viewport_width
        y_pct = _as_float(overlay, "y_px") / viewport_height
        w_pct = _as_float(overlay, "w_px") / viewport_width
        h_pct = _as_float(overlay, "h_px") / viewport_height
    else:
        x_pct = _as_float(overlay, "x_pct")
        y_pct = _as_float(overlay, "y_pct")
        w_pct = _as_float(overlay, "w_pct")
        h_pct = _as_float(overlay, "h_pct")
    for key, value in {"x_pct": x_pct, "y_pct": y_pct, "w_pct": w_pct, "h_pct": h_pct}.items():
        if not 0 <= value <= 1:
            raise ValueError(f"{key} must be between 0 and 1")
    if w_pct <= 0 or h_pct <= 0:
        raise ValueError("w_pct and h_pct must be positive")
    return {
        **overlay,
        "x": round(x_pct * page_width, 10),
        "y": round(y_pct * page_height, 10),
        "width": round(w_pct * page_width, 10),
        "height": round(h_pct * page_height, 10),
        "x_pct": x_pct,
        "y_pct": y_pct,
        "w_pct": w_pct,
        "h_pct": h_pct,
    }


def _match_anchor_text(anchor_text: str, text_matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    needle = anchor_text.casefold().strip()
    return [match for match in text_matches if needle and needle in str(match.get("text") or "").casefold()]


def resolve_anchor_placement(
    field: dict[str, Any],
    text_matches: list[dict[str, Any]],
    *,
    page: dict[str, Any],
    manual_override: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve anchor-text placement or report ambiguity for human override.

    Ambiguous anchors intentionally do not silently pick a rectangle. A caller can
    pass `anchor_occurrence` (1-based among matching anchors) or explicit
    `manual_override` coordinates to make placement deterministic.
    """
    if manual_override:
        resolved = normalize_field_coordinates({**field, **manual_override}, page)
        metadata = {**(field.get("metadata") or {}), "manual_override": True}
        return {**resolved, "placement_status": "manual_override", "metadata": metadata}

    anchor_text = str(field.get("anchor_text") or "").strip()
    if not anchor_text:
        return {**normalize_field_coordinates(field, page), "placement_status": "manual"}

    matches = _match_anchor_text(anchor_text, text_matches)
    if not matches:
        return {**field, "placement_status": "anchor_not_found", "anchor_candidates": []}

    occurrence = field.get("anchor_occurrence")
    if occurrence is None and len(matches) > 1:
        return {**field, "placement_status": "ambiguous_anchor", "anchor_candidates": matches}
    selected_index = int(occurrence or 1) - 1
    if selected_index < 0 or selected_index >= len(matches):
        return {**field, "placement_status": "anchor_occurrence_not_found", "anchor_candidates": matches}

    match = matches[selected_index]
    match_page = match.get("page") or {
        "width": match.get("page_width", page.get("width")),
        "height": match.get("page_height", page.get("height")),
    }
    _, match_page_height = _page_size(match_page)
    bbox = match.get("bbox") or {}
    bbox_x = _as_float(bbox, "x")
    bbox_y = _as_float(bbox, "y")
    bbox_height = _as_float(bbox, "height", 0)
    bbox_origin = str(match.get("bbox_origin") or field.get("anchor_bbox_origin") or "top_left").lower()
    if bbox_origin in {"bottom_left", "pdf_bottom_left"}:
        bbox_top_y = match_page_height - bbox_y - bbox_height
    elif bbox_origin in {"top_left", "viewport_top_left"}:
        bbox_top_y = bbox_y
    else:
        raise ValueError("bbox_origin must be top_left or bottom_left")
    x = bbox_x + float(field.get("anchor_offset_x") or 0)
    y = bbox_top_y + bbox_height + float(field.get("anchor_offset_y") or 0)
    resolved = normalize_field_coordinates(
        {
            **field,
            "page_number": int(match.get("page_number") or field.get("page_number") or 1),
            "x": x,
            "y": y,
            "width": _as_float(field, "width"),
            "height": _as_float(field, "height"),
            "anchor_bbox": bbox,
            "anchor_occurrence": selected_index + 1,
        },
        match_page,
    )
    metadata = {**(field.get("metadata") or {}), "anchor_match_text": match.get("text"), "anchor_bbox_origin": bbox_origin}
    return {**resolved, "placement_status": "anchored", "metadata": metadata}


def render_field_placement_fixture(
    *,
    output_pdf: str | Path,
    page: dict[str, Any],
    fields: list[dict[str, Any]],
) -> dict[str, Any]:
    """Render a deterministic PDF fixture showing field rectangles.

    This is a lightweight visual QA artifact for the coordinate engine. It uses
    ReportLab, which is already present in the Hermes test environment, and keeps
    page compression disabled so tests can assert the fixture contains field IDs.
    """
    try:
        from reportlab.lib.colors import HexColor
        from reportlab.pdfgen import canvas
    except ModuleNotFoundError as exc:  # pragma: no cover - depends on deployment extras
        raise RuntimeError("ReportLab is required to render field placement fixtures") from exc

    page_width, page_height = _page_size(page)
    output_path = Path(output_pdf)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=(page_width, page_height), pageCompression=0)
    pdf.setTitle("Signature Core field placement fixture")
    pdf.setStrokeColor(HexColor("#075985"))
    pdf.setFillColor(HexColor("#f0f9ff"))
    pdf.rect(0, 0, page_width, page_height, stroke=1, fill=1)
    rendered_fields: list[dict[str, Any]] = []
    for field in fields:
        normalized = normalize_field_coordinates(field, page)
        rendered_fields.append(normalized)
        pdf.setStrokeColor(HexColor("#16a34a"))
        pdf.setFillColor(HexColor("#dcfce7"))
        pdf.rect(normalized["x"], normalized["pdf_y_bottom"], normalized["width"], normalized["height"], stroke=1, fill=1)
        pdf.setFillColor(HexColor("#111827"))
        pdf.drawString(normalized["x"] + 4, normalized["pdf_y_bottom"] + max(8, normalized["height"] - 14), str(field.get("field_id") or "field"))
        pdf.drawString(normalized["x"] + 4, normalized["pdf_y_bottom"] + 8, str(field.get("label") or field.get("field_type") or "field"))
    pdf.showPage()
    pdf.save()
    return {
        "output": str(output_path),
        "field_count": len(rendered_fields),
        "fields": rendered_fields,
        "sha256": sha256_file(output_path),
        "byte_size": output_path.stat().st_size,
    }


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
) -> dict[str, Any]:
    """Write a visibly signed PDF and return output metadata.

    The original `document_hash` should be the hash of the exact document that was
    approved by the signer. The signed output receives its own SHA-256 for the
    completed artifact record.
    """
    try:
        import fitz  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:  # pragma: no cover - depends on deployment extras
        raise RuntimeError("PyMuPDF (`fitz`) is required to stamp signed PDFs") from exc

    input_path = Path(input_pdf)
    output_path = Path(output_pdf)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    original_sha = sha256_file(input_path)
    doc = fitz.open(str(input_path))
    if doc.page_count < 1:
        raise ValueError("PDF has no pages")

    signed_at_text = _format_signed_at(signed_at)
    signer_text = signer.strip() or "Firmante"

    page = doc[0]
    rect = page.rect
    stamp = fitz.Rect(rect.x1 - 270, rect.y1 - 155, rect.x1 - 36, rect.y1 - 42)
    page.draw_rect(stamp, color=(0.02, 0.38, 0.18), fill=(0.93, 1.0, 0.95), width=1.4)
    page.insert_text((stamp.x0 + 12, stamp.y0 + 22), "FIRMADO DIGITALMENTE", fontsize=12, fontname="helv", color=(0.02, 0.32, 0.14))
    page.insert_text((stamp.x0 + 12, stamp.y0 + 45), f"Por: {signer_text[:42]}", fontsize=9.5, fontname="helv", color=(0, 0, 0))
    page.insert_text((stamp.x0 + 12, stamp.y0 + 62), f"Fecha: {signed_at_text[:34]}", fontsize=8.5, fontname="helv", color=(0, 0, 0))
    page.insert_text((stamp.x0 + 12, stamp.y0 + 82), f"Hash aprobación: {approval_hash[:18]}…", fontsize=8, fontname="cour", color=(0, 0, 0))
    page.insert_text((stamp.x0 + 12, stamp.y0 + 98), f"Hash documento: {document_hash[:18]}…", fontsize=8, fontname="cour", color=(0, 0, 0))

    audit = doc.new_page(width=612, height=792)
    audit.draw_rect(fitz.Rect(36, 36, 576, 756), color=(0.02, 0.28, 0.16), width=1.2)
    audit.insert_text((56, 78), "Certificado de aprobación y firma digital", fontsize=18, fontname="helv", color=(0.02, 0.28, 0.16))
    audit.insert_text((56, 110), "SitioUno / Zeus Signature Core", fontsize=11, fontname="helv", color=(0.25, 0.25, 0.25))

    details = [
        ("Documento", source_id or request_id),
        ("Solicitud de firma", request_id),
        ("Firmante", signer_text),
        ("Fecha de firma", signed_at_text),
        ("Hash SHA-256 del documento aprobado", document_hash),
        ("Hash SHA-256 de aprobación", approval_hash),
        ("Evento sandbox", event_id or "N/A"),
    ]
    y = 150
    for label, value in details:
        audit.insert_text((56, y), label, fontsize=9, fontname="helv", color=(0.25, 0.25, 0.25))
        audit.insert_textbox(fitz.Rect(210, y - 12, 548, y + 30), str(value), fontsize=9, fontname="helv", color=(0, 0, 0))
        y += 44 if len(str(value)) < 60 else 58

    audit_text = disclaimer or (
        "Este PDF fue actualizado automáticamente después de recibir la aprobación "
        "del firmante en el workspace público. La evidencia de aprobación queda "
        "persistida en Signature Core con hash de aprobación y eventos encadenados. "
        "Este sello visual no sustituye todavía una firma cualificada PAdES/TSA; "
        "representa evidencia interna de aprobación digital."
    )
    audit.insert_textbox(fitz.Rect(56, 565, 548, 650), audit_text, fontsize=9, fontname="helv", color=(0.1, 0.1, 0.1))

    if output_path.resolve() == input_path.resolve():
        tmp = output_path.with_suffix(output_path.suffix + ".tmp")
        doc.save(str(tmp), garbage=4, deflate=True)
        doc.close()
        os.replace(tmp, output_path)
    else:
        doc.save(str(output_path), garbage=4, deflate=True)
        doc.close()

    return {
        "input": str(input_path),
        "output": str(output_path),
        "original_sha256": original_sha,
        "signed_sha256": sha256_file(output_path),
        "byte_size": output_path.stat().st_size,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Stamp a Signature Core PDF as signed")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--request-id", required=True)
    parser.add_argument("--source-id", default="")
    parser.add_argument("--signer", required=True)
    parser.add_argument("--signed-at", default="")
    parser.add_argument("--approval-hash", required=True)
    parser.add_argument("--document-hash", required=True)
    parser.add_argument("--event-id", default="")
    args = parser.parse_args()
    result = stamp_signed_pdf(
        input_pdf=args.input,
        output_pdf=args.output,
        request_id=args.request_id,
        source_id=args.source_id,
        signer=args.signer,
        signed_at=args.signed_at,
        approval_hash=args.approval_hash,
        document_hash=args.document_hash,
        event_id=args.event_id,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

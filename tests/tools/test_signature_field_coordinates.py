from __future__ import annotations

import json

from tools import signature_pdf, signature_tool


def _loads(result: str) -> dict:
    return json.loads(result)


def test_pdf_points_and_normalized_viewport_coordinates_round_trip():
    field = {
        "field_id": "field-sig",
        "page_number": 1,
        "x": 72,
        "y": 144,
        "width": 216,
        "height": 54,
    }
    page = {"width": 612, "height": 792}

    normalized = signature_pdf.normalize_field_coordinates(field, page)
    round_tripped = signature_pdf.viewport_to_pdf_points(normalized, page)

    assert normalized["x_pct"] == 72 / 612
    assert normalized["y_pct"] == 144 / 792
    assert normalized["w_pct"] == 216 / 612
    assert normalized["h_pct"] == 54 / 792
    assert normalized["pdf_y_bottom"] == 792 - 144 - 54
    assert round_tripped["x"] == 72
    assert round_tripped["y"] == 144
    assert round_tripped["width"] == 216
    assert round_tripped["height"] == 54


def test_viewport_pixel_coordinates_convert_to_pdf_points_and_back():
    page = {"width": 612, "height": 792}
    viewport = {"width": 306, "height": 396}
    overlay = {"x_px": 36, "y_px": 72, "w_px": 108, "h_px": 27}

    pdf = signature_pdf.viewport_to_pdf_points(overlay, page, viewport=viewport)
    normalized = signature_pdf.normalize_field_coordinates(pdf, page)

    assert pdf["x"] == 72
    assert pdf["y"] == 144
    assert pdf["width"] == 216
    assert pdf["height"] == 54
    assert normalized["x_pct"] == 72 / 612
    assert normalized["pdf_y_bottom"] == 594


def test_anchor_text_ambiguity_requires_occurrence_or_manual_override():
    matches = [
        {"page_number": 1, "text": "Cliente", "bbox": {"x": 100, "y": 200, "width": 80, "height": 12}},
        {"page_number": 1, "text": "Cliente", "bbox": {"x": 100, "y": 360, "width": 80, "height": 12}},
    ]

    ambiguous = signature_pdf.resolve_anchor_placement(
        {"field_id": "name-1", "anchor_text": "Cliente", "width": 160, "height": 24},
        matches,
        page={"width": 612, "height": 792},
    )
    selected = signature_pdf.resolve_anchor_placement(
        {"field_id": "name-1", "anchor_text": "Cliente", "anchor_occurrence": 2, "width": 160, "height": 24},
        matches,
        page={"width": 612, "height": 792},
    )
    manual = signature_pdf.resolve_anchor_placement(
        {"field_id": "name-1", "anchor_text": "Cliente", "width": 160, "height": 24},
        matches,
        page={"width": 612, "height": 792},
        manual_override={"x": 300, "y": 420, "width": 150, "height": 30, "page_number": 1},
    )

    assert ambiguous["placement_status"] == "ambiguous_anchor"
    assert len(ambiguous["anchor_candidates"]) == 2
    assert selected["placement_status"] == "anchored"
    assert selected["anchor_occurrence"] == 2
    assert selected["x"] == 100
    assert selected["y"] == 372
    assert manual["placement_status"] == "manual_override"
    assert manual["x"] == 300
    assert manual["metadata"]["manual_override"] is True


def test_anchor_text_can_convert_bottom_left_bboxes_and_match_page_size():
    selected = signature_pdf.resolve_anchor_placement(
        {"field_id": "name-1", "anchor_text": "Cliente", "width": 160, "height": 24},
        [{
            "page_number": 2,
            "text": "Cliente",
            "bbox_origin": "bottom_left",
            "page": {"width": 400, "height": 500},
            "bbox": {"x": 50, "y": 100, "width": 80, "height": 12},
        }],
        page={"width": 612, "height": 792},
    )

    assert selected["placement_status"] == "anchored"
    assert selected["page_number"] == 2
    assert selected["y"] == 400
    assert selected["pdf_y_bottom"] == 76
    assert selected["x_pct"] == 50 / 400
    assert selected["metadata"]["anchor_bbox_origin"] == "bottom_left"


def test_coordinate_engine_rejects_non_finite_numbers():
    for bad_value in ["nan", "inf", "-inf"]:
        try:
            signature_pdf.normalize_field_coordinates(
                {"x": bad_value, "y": 0, "width": 10, "height": 10},
                {"width": 100, "height": 100},
            )
        except ValueError as exc:
            assert "finite" in str(exc)
        else:  # pragma: no cover - explicit assertion path for bad validation
            raise AssertionError(f"accepted non-finite coordinate: {bad_value}")


def test_signature_template_field_upsert_stores_converted_coordinates_and_anchor_resolution(monkeypatch):
    statements = []

    def fake_statement_one(query, *, user=None):
        statements.append(query)
        return {
            "field_id": "sig-anchored",
            "template_version_id": "template-v1",
            "x": "100.0000",
            "y": "372.0000",
            "x_pct": "0.163399",
            "anchor_text": "Cliente",
            "anchor_occurrence": 2,
        }

    monkeypatch.setattr(signature_tool.sql, "statement_one", fake_statement_one)

    result = _loads(signature_tool._handle_template_field_upsert({
        "template_version_id": "template-v1",
        "page": {"width": 612, "height": 792},
        "field": {
            "field_id": "sig-anchored",
            "role": "client",
            "field_type": "signature",
            "label": "Firma cliente",
            "anchor_text": "Cliente",
            "anchor_occurrence": 2,
            "width": 160,
            "height": 48,
        },
        "text_matches": [
            {"page_number": 1, "text": "Cliente", "bbox": {"x": 100, "y": 200, "width": 80, "height": 12}},
            {"page_number": 1, "text": "Cliente", "bbox": {"x": 100, "y": 360, "width": 80, "height": 12}},
        ],
    }))

    assert result["ok"] is True
    assert result["placement"]["placement_status"] == "anchored"
    assert result["placement"]["x"] == 100
    assert result["placement"]["y"] == 372
    assert result["placement"]["x_pct"] == 100 / 612
    joined = "\n".join(statements)
    assert "INSERT INTO signature.field_placements" in joined
    assert "100.0" in joined
    assert "372.0" in joined
    assert "0.163398" in joined or "0.163399" in joined
    assert "Cliente" in joined


def test_rendered_pdf_field_fixture_contains_placement_marks(tmp_path):
    output = tmp_path / "field-placement-fixture.pdf"

    result = signature_pdf.render_field_placement_fixture(
        output_pdf=output,
        page={"width": 612, "height": 792},
        fields=[{
            "field_id": "field-sig",
            "label": "Firma cliente",
            "x": 72,
            "y": 144,
            "width": 216,
            "height": 54,
        }],
    )

    assert result["output"] == str(output)
    assert result["field_count"] == 1
    assert result["fields"][0]["pdf_y_bottom"] == 594
    data = output.read_bytes()
    assert data.startswith(b"%PDF-")
    assert b"field-sig" in data
    assert b"Firma cliente" in data

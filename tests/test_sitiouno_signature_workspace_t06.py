from scripts.runtime.sitiouno_document_workspace import render_signature_workspace


def test_signature_workspace_renders_responsive_pdf_overlay_and_progress():
    html = render_signature_workspace(
        document_title="Acta de entrega Smart ISP",
        pdf_url="/download/demo/acta.pdf",
        download_url="/download/demo/acta.pdf",
        deliverable_id="demo",
        public_token="tok_demo",
        signer_name="David Piza",
        document_hash="abc123def456",
        fields=[
            {"field_id": "signature_1", "type": "signature", "label": "Firma", "page_number": 1, "x_pct": 58, "y_pct": 72, "w_pct": 28, "h_pct": 10},
            {"field_id": "name_1", "type": "text", "label": "Nombre", "page_number": 1, "x_pct": 15, "y_pct": 72, "w_pct": 35, "h_pct": 7},
        ],
    )

    assert '<meta name="viewport" content="width=device-width, initial-scale=1"' in html
    assert 'class="signer-shell"' in html
    assert 'class="pdf-stage"' in html
    assert 'class="field-layer"' in html
    assert 'data-field-id="signature_1"' in html
    assert 'data-field-type="signature"' in html
    assert 'data-page-number="1"' in html
    assert 'left: 58.000%' in html
    assert 'width: 28.000%' in html
    assert 'aria-label="Campo Firma, página 1"' in html
    assert 'class="signer-progress"' in html
    assert 'id="signatureCanvas"' in html
    assert 'resizeSignatureCanvas' in html
    assert 'window.devicePixelRatio' in html
    assert "orientationchange" in html
    assert "localStorage.setItem(storageKey" in html
    assert "restoreSavedSignature" in html
    assert '@media (max-width: 760px)' in html
    assert 'position: sticky' in html
    assert 'touch-action: none' in html


def test_signature_workspace_exposes_safe_document_actions_payloads():
    html = render_signature_workspace(
        document_title="Acta de entrega Smart ISP",
        pdf_url="/download/demo/acta.pdf",
        download_url="/download/demo/acta.pdf",
        deliverable_id="demo",
        public_token="tok_demo",
        signer_name="David Piza",
        document_hash="abc123def456",
        fields=[],
    )

    assert 'event_type: "signed"' in html
    assert 'event_type: "rejected"' in html
    assert 'event_type: "approved"' in html
    assert 'event_type: "commented"' in html
    assert 'id="approveDocument"' in html
    assert 'id="commentDocument"' in html
    assert 'id="helpDocument"' in html
    assert 'comment: reason.trim()' in html
    assert 'comment: comment.trim()' in html
    assert 'deliverable_id: "demo"' in html
    assert 'public_token: "tok_demo"' in html
    assert 'fetch("/api/document-actions"' in html

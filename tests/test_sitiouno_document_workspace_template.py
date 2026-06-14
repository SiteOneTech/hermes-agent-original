import sys
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parents[1] / "scripts" / "runtime"
sys.path.insert(0, str(RUNTIME_DIR))

from scripts.runtime import sitiouno_document_workspace as template


def test_signature_workspace_uses_canonical_commercial_template_and_fixed_otp_boxes():
    html = template.render_signature_workspace(
        token="sig_token_1234567890abcdef",
        request_id="signature-request-1",
        submitter_id="submitter-1",
        public_document_number="ACTA-001",
        title="Firma del acta de entrega",
        document_label="Acta de entrega final y cierre de proyecto",
        project_label="Sistema Smart ISP / Totalcom",
        recipient_name="David Piza",
        recipient_email="david@example.com",
        client_name="Totalcom",
        document_url="https://zeus-sandbox.kidu.app/download/token/doc.pdf",
        document_hash_sha256="d04c9a7f6a1ac36ed48043d142472cb23d22c69b58fe419022c6e8e26eda594e",
    )

    assert "/assets/sitiouno-logo-blue-on-white-1600x320.png" in html
    assert "--bg:#f5f7fb" in html
    assert "#06110d" not in html
    assert "var(--green)" not in html
    assert html.count("class='otp-digit'") == 6
    assert "function updateVerifyState()" in html
    assert "otpValue().length === 6" in html
    assert "Validar y abrir documento" in html
    assert "document.body.className='unlocked'" in html
    assert "iframe.dataset.src" in html
    assert "Hash SHA-256" not in html.split("<section class='gate'", 1)[1].split("</section>", 1)[0]
    assert "class='hash-value'" in html
    assert "overflow-wrap:anywhere" in html

"""Responsive SitioUno document signing workspace renderer.

This module is intentionally HTML-only and dependency-light because delivery
sandbox workspaces are static public artifacts. Server-side systems remain the
authority for OTP validation, audit events, and final PDF stamping.
"""
from __future__ import annotations

import html
import json
from typing import Any


def _e(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _pct(value: Any, default: float = 0.0) -> str:
    number = _number(value, default)
    return f"{max(0.0, min(100.0, number)):.3f}%"


def _field_value(field: dict[str, Any], *keys: str, default: float = 0.0) -> Any:
    for key in keys:
        if field.get(key) is not None:
            return field[key]
    return default


def _field_markup(fields: list[dict[str, Any]]) -> str:
    if not fields:
        fields = [
            {"field_id": "signer_name", "type": "text", "label": "Nombre del firmante", "x": 12, "y": 70, "width": 34, "height": 7},
            {"field_id": "signature", "type": "signature", "label": "Firma", "x": 52, "y": 68, "width": 36, "height": 13},
        ]
    parts: list[str] = []
    for field in fields:
        field_id = _e(field.get("field_id") or field.get("id") or "field")
        field_type = _e(field.get("type") or "text")
        label = _e(field.get("label") or field_type.title())
        page = _e(field.get("page_number") or field.get("page") or 1)
        style = "; ".join(
            [
                f"left: {_pct(_field_value(field, 'x_pct', 'x', default=10))}",
                f"top: {_pct(_field_value(field, 'y_pct', 'y', default=70))}",
                f"width: {_pct(_field_value(field, 'w_pct', 'width', default=30))}",
                f"height: {_pct(_field_value(field, 'h_pct', 'height', default=8))}",
            ]
        )
        parts.append(
            f'<button class="overlay-field overlay-field--{field_type}" type="button" '
            f'data-field-id="{field_id}" data-field-type="{field_type}" data-page-number="{page}" '
            f'aria-label="Campo {label}, página {page}" style="{style}">'
            f'<span>{label}</span></button>'
        )
    return "\n          ".join(parts)


def render_signature_workspace(
    *,
    document_title: str,
    pdf_url: str,
    download_url: str,
    deliverable_id: str,
    public_token: str,
    signer_name: str,
    document_hash: str,
    fields: list[dict[str, Any]] | None = None,
) -> str:
    """Return a static responsive signing workspace HTML document."""

    title = _e(document_title)
    pdf = _e(pdf_url)
    download = _e(download_url)
    signer = _e(signer_name)
    digest = _e(document_hash)
    field_html = _field_markup(fields or [])
    deliverable_json = json.dumps(str(deliverable_id), ensure_ascii=False)
    token_json = json.dumps(str(public_token), ensure_ascii=False)

    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} · SitioUno</title>
  <style>
    :root {{
      color-scheme: light;
      --su-blue: #155eef;
      --su-blue-dark: #0f3fb5;
      --su-ink: #102033;
      --su-muted: #667085;
      --su-line: #d9e2f2;
      --su-bg: #f4f7fb;
      --su-card: #ffffff;
      --su-ok: #12b76a;
      --su-danger: #d92d20;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; color: var(--su-ink); background: linear-gradient(180deg, #f8fbff 0%, var(--su-bg) 100%); }}
    .signer-shell {{ min-height: 100vh; display: grid; grid-template-rows: auto 1fr; }}
    .workspace-header {{ display: flex; gap: 18px; align-items: center; justify-content: space-between; padding: 18px clamp(16px, 4vw, 42px); border-bottom: 1px solid var(--su-line); background: rgba(255,255,255,.94); backdrop-filter: blur(12px); position: sticky; top: 0; z-index: 20; }}
    .brand {{ display: flex; align-items: center; gap: 12px; font-weight: 800; letter-spacing: -.03em; }}
    .brand-mark {{ width: 38px; height: 38px; border-radius: 12px; background: var(--su-blue); color: white; display: grid; place-items: center; font-weight: 900; }}
    .workspace-header h1 {{ margin: 0; font-size: clamp(1.05rem, 2.5vw, 1.45rem); line-height: 1.15; }}
    .workspace-header p {{ margin: 4px 0 0; color: var(--su-muted); font-size: .94rem; }}
    .workspace-grid {{ width: min(1440px, 100%); margin: 0 auto; padding: clamp(14px, 3vw, 32px); display: grid; grid-template-columns: minmax(0, 1fr) minmax(320px, 400px); gap: clamp(16px, 3vw, 28px); align-items: start; }}
    .pdf-stage {{ background: #e8eef8; border: 1px solid var(--su-line); border-radius: 24px; min-height: min(82vh, 980px); padding: clamp(10px, 2vw, 18px); box-shadow: 0 18px 60px rgba(16,32,51,.12); }}
    .pdf-page {{ position: relative; width: min(980px, 100%); min-height: 72vh; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 12px 40px rgba(16,32,51,.14); }}
    .pdf-frame {{ width: 100%; height: 72vh; min-height: 620px; border: 0; display: block; background: white; }}
    .field-layer {{ position: absolute; inset: 0; pointer-events: none; }}
    .overlay-field {{ position: absolute; pointer-events: auto; display: flex; align-items: center; justify-content: center; border: 2px dashed rgba(21,94,239,.75); border-radius: 12px; background: rgba(21,94,239,.10); color: var(--su-blue-dark); font-weight: 800; min-height: 44px; cursor: pointer; transition: transform .18s ease, background .18s ease, border-color .18s ease; }}
    .overlay-field:focus-visible, .overlay-field:hover {{ transform: translateY(-1px); background: rgba(21,94,239,.18); outline: 3px solid rgba(21,94,239,.22); }}
    .overlay-field--signature {{ border-style: solid; background: rgba(18,183,106,.12); border-color: rgba(18,183,106,.82); color: #067647; }}
    .side-panel {{ display: grid; gap: 16px; }}
    .panel-card {{ background: var(--su-card); border: 1px solid var(--su-line); border-radius: 22px; padding: 20px; box-shadow: 0 12px 36px rgba(16,32,51,.08); }}
    .signer-progress {{ display: grid; gap: 12px; }}
    .progress-step {{ display: grid; grid-template-columns: 28px 1fr; gap: 10px; align-items: start; color: var(--su-muted); }}
    .progress-step strong {{ color: var(--su-ink); display: block; }}
    .progress-dot {{ width: 28px; height: 28px; border-radius: 999px; display: grid; place-items: center; background: #e7f0ff; color: var(--su-blue); font-weight: 900; }}
    .signature-pad-wrap {{ display: grid; gap: 10px; }}
    #signatureCanvas {{ width: 100%; height: 180px; border: 2px solid var(--su-line); border-radius: 16px; background: #fff; touch-action: none; box-shadow: inset 0 0 0 1px rgba(21,94,239,.05); }}
    .button-row {{ display: flex; gap: 10px; flex-wrap: wrap; }}
    .btn {{ appearance: none; border: 0; min-height: 46px; padding: 12px 16px; border-radius: 999px; font-weight: 800; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; justify-content: center; gap: 8px; }}
    .btn-primary {{ background: var(--su-blue); color: white; box-shadow: 0 10px 24px rgba(21,94,239,.28); }}
    .btn-secondary {{ background: #eef4ff; color: var(--su-blue-dark); }}
    .btn-danger {{ background: #fff1f0; color: var(--su-danger); }}
    .hash {{ overflow-wrap: anywhere; color: var(--su-muted); font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .78rem; }}
    .mobile-action-bar {{ display: none; }}
    @media (max-width: 1000px) {{
      .workspace-grid {{ grid-template-columns: 1fr; }}
      .side-panel {{ grid-row: 1; }}
      .pdf-stage {{ min-height: auto; }}
      .pdf-frame {{ min-height: 540px; height: 64vh; }}
    }}
    @media (max-width: 760px) {{
      .workspace-header {{ align-items: flex-start; position: static; }}
      .workspace-grid {{ padding: 10px; gap: 12px; }}
      .panel-card {{ border-radius: 18px; padding: 16px; }}
      .pdf-stage {{ padding: 8px; border-radius: 18px; }}
      .pdf-page {{ border-radius: 12px; min-height: 60vh; }}
      .pdf-frame {{ min-height: 460px; height: 60vh; }}
      .overlay-field {{ min-height: 52px; font-size: .9rem; }}
      #signatureCanvas {{ height: 220px; }}
      .mobile-action-bar {{ position: sticky; bottom: 0; z-index: 30; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; padding: 12px; border-top: 1px solid var(--su-line); background: rgba(255,255,255,.96); backdrop-filter: blur(10px); }}
      .side-panel .button-row.primary-actions {{ display: none; }}
    }}
  </style>
</head>
<body>
  <main class="signer-shell">
    <header class="workspace-header">
      <div class="brand">
        <div class="brand-mark">SU</div>
        <div>
          <h1>{title}</h1>
          <p>Firmante: {signer}</p>
        </div>
      </div>
      <a class="btn btn-secondary" href="{download}" target="_blank" rel="noopener">Descargar PDF</a>
    </header>

    <section class="workspace-grid">
      <div class="pdf-stage" aria-label="Documento para revisar y firmar">
        <div class="pdf-page">
          <iframe class="pdf-frame" src="{pdf}" title="Vista PDF del documento"></iframe>
          <div class="field-layer" aria-label="Campos del documento">
          {field_html}
          </div>
        </div>
      </div>

      <aside class="side-panel" aria-label="Panel de firma">
        <section class="panel-card">
          <h2>Progreso de firma</h2>
          <div class="signer-progress">
            <div class="progress-step"><span class="progress-dot">1</span><span><strong>Revisa el documento</strong>Confirma nombres, páginas y campos resaltados.</span></div>
            <div class="progress-step"><span class="progress-dot">2</span><span><strong>Dibuja tu firma</strong>El canvas se ajusta a pantallas Retina y cambios de orientación.</span></div>
            <div class="progress-step"><span class="progress-dot">3</span><span><strong>Envía la decisión</strong>La acción se audita contra el token público del documento.</span></div>
          </div>
        </section>

        <section class="panel-card signature-pad-wrap">
          <h2>Firma manuscrita</h2>
          <canvas id="signatureCanvas" aria-label="Lienzo para dibujar firma"></canvas>
          <div class="button-row">
            <button class="btn btn-secondary" type="button" id="clearSignature">Limpiar</button>
            <button class="btn btn-secondary" type="button" id="fitSignature">Reajustar canvas</button>
          </div>
        </section>

        <section class="panel-card">
          <h2>Acciones</h2>
          <p class="hash">SHA-256: {digest}</p>
          <div class="button-row primary-actions">
            <button class="btn btn-primary" type="button" id="signDocument">Firmar documento</button>
            <button class="btn btn-secondary" type="button" id="approveDocument">Aprobar</button>
            <button class="btn btn-secondary" type="button" id="commentDocument">Comentar</button>
            <button class="btn btn-secondary" type="button" id="helpDocument">Solicitar ayuda</button>
            <button class="btn btn-danger" type="button" id="rejectDocument">Rechazar</button>
          </div>
        </section>
      </aside>
    </section>

    <nav class="mobile-action-bar" aria-label="Acciones móviles">
      <button class="btn btn-primary" type="button" data-mobile-action="sign">Firmar</button>
      <button class="btn btn-secondary" type="button" data-mobile-action="comment">Comentar</button>
      <button class="btn btn-danger" type="button" data-mobile-action="reject">Rechazar</button>
    </nav>
  </main>

  <script>
    const canvas = document.getElementById("signatureCanvas");
    const ctx = canvas.getContext("2d");
    const storageKey = "signature-progress:" + {token_json} + ":" + {deliverable_json};
    let drawing = false;

    function resizeSignatureCanvas() {{
      const ratio = Math.max(window.devicePixelRatio || 1, 1);
      const rect = canvas.getBoundingClientRect();
      const previous = canvas.toDataURL();
      canvas.width = Math.max(1, Math.floor(rect.width * ratio));
      canvas.height = Math.max(1, Math.floor(rect.height * ratio));
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
      ctx.lineWidth = 2.4;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      ctx.strokeStyle = "#102033";
      if (previous && previous.length > 100) {{
        const img = new Image();
        img.onload = () => ctx.drawImage(img, 0, 0, rect.width, rect.height);
        img.src = previous;
      }}
    }}

    function point(event) {{
      const rect = canvas.getBoundingClientRect();
      const touch = event.touches && event.touches[0];
      const source = touch || event;
      return {{ x: source.clientX - rect.left, y: source.clientY - rect.top }};
    }}
    function startDraw(event) {{ event.preventDefault(); drawing = true; const p = point(event); ctx.beginPath(); ctx.moveTo(p.x, p.y); }}
    function moveDraw(event) {{ if (!drawing) return; event.preventDefault(); const p = point(event); ctx.lineTo(p.x, p.y); ctx.stroke(); }}
    function endDraw() {{
      if (!drawing) return;
      drawing = false;
      try {{ localStorage.setItem(storageKey, canvas.toDataURL("image/png")); }} catch (error) {{}}
    }}

    function restoreSavedSignature() {{
      let saved = "";
      try {{ saved = localStorage.getItem(storageKey) || ""; }} catch (error) {{}}
      if (!saved) return;
      const rect = canvas.getBoundingClientRect();
      const img = new Image();
      img.onload = () => ctx.drawImage(img, 0, 0, rect.width, rect.height);
      img.src = saved;
    }}

    canvas.addEventListener("pointerdown", startDraw);
    canvas.addEventListener("pointermove", moveDraw);
    window.addEventListener("pointerup", endDraw);
    window.addEventListener("resize", resizeSignatureCanvas);
    window.addEventListener("orientationchange", () => setTimeout(resizeSignatureCanvas, 120));
    document.getElementById("fitSignature").addEventListener("click", resizeSignatureCanvas);
    document.getElementById("clearSignature").addEventListener("click", () => {{ ctx.clearRect(0, 0, canvas.width, canvas.height); try {{ localStorage.removeItem(storageKey); }} catch (error) {{}}; }});

    async function submitDocumentAction(payload) {{
      payload.metadata = Object.assign({{}}, payload.metadata || {{}}, {{
        signer_name: {json.dumps(str(signer_name), ensure_ascii=False)},
        signature_data_url: canvas.toDataURL("image/png"),
        viewport: {{ width: window.innerWidth, height: window.innerHeight, devicePixelRatio: window.devicePixelRatio || 1 }}
      }});
      const response = await fetch("/api/document-actions", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify(payload)
      }});
      if (!response.ok) {{
        const data = await response.json().catch(() => ({{}}));
        alert(data.error === "otp_required" ? "Se requiere OTP para completar esta acción." : "No se pudo registrar la acción.");
        return;
      }}
      alert("Acción registrada para auditoría.");
    }}

    function signDocumentAction() {{
      return submitDocumentAction({{
        event_type: "signed",
        deliverable_id: {deliverable_json},
        public_token: {token_json},
        metadata: {{ action_source: "responsive_signature_workspace" }}
      }});
    }}

    function rejectDocumentAction() {{
      const reason = window.prompt("Motivo del rechazo (requerido para auditoría)") || "";
      if (!reason.trim()) return;
      return submitDocumentAction({{
        event_type: "rejected",
        deliverable_id: {deliverable_json},
        public_token: {token_json},
        metadata: {{ action_source: "responsive_signature_workspace", comment: reason.trim() }},
        comment: reason.trim()
      }});
    }}

    function approveDocumentAction() {{
      return submitDocumentAction({{
        event_type: "approved",
        deliverable_id: {deliverable_json},
        public_token: {token_json},
        metadata: {{ action_source: "responsive_signature_workspace" }}
      }});
    }}

    function commentDocumentAction() {{
      const comment = window.prompt("Comentario para el agente") || "";
      if (!comment.trim()) return;
      return submitDocumentAction({{
        event_type: "commented",
        deliverable_id: {deliverable_json},
        public_token: {token_json},
        metadata: {{ action_source: "responsive_signature_workspace", comment: comment.trim() }},
        comment: comment.trim()
      }});
    }}

    function helpDocumentAction() {{
      return submitDocumentAction({{
        event_type: "commented",
        deliverable_id: {deliverable_json},
        public_token: {token_json},
        metadata: {{ action_source: "responsive_signature_workspace", comment: "Solicito ayuda con la firma" }},
        comment: "Solicito ayuda con la firma"
      }});
    }}

    document.getElementById("signDocument").addEventListener("click", signDocumentAction);
    document.getElementById("approveDocument").addEventListener("click", approveDocumentAction);
    document.getElementById("commentDocument").addEventListener("click", commentDocumentAction);
    document.getElementById("helpDocument").addEventListener("click", helpDocumentAction);
    document.getElementById("rejectDocument").addEventListener("click", rejectDocumentAction);
    document.querySelector('[data-mobile-action="sign"]').addEventListener("click", signDocumentAction);
    document.querySelector('[data-mobile-action="comment"]').addEventListener("click", commentDocumentAction);
    document.querySelector('[data-mobile-action="reject"]').addEventListener("click", rejectDocumentAction);
    resizeSignatureCanvas();
    restoreSavedSignature();

  </script>
</body>
</html>
"""

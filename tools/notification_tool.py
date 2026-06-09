"""Generic notification tools with provider adapters.

Notification Core exposes provider-neutral tool contracts. SendGrid is the first
email adapter for marketing and business notifications, but callers should use
these generic tools instead of binding conversation flows directly to SendGrid.
"""
from __future__ import annotations

import json
import os
import html
import urllib.error
import urllib.request
from typing import Any

from hermes_cli import agent_core_sql as sql
from tools.registry import registry, tool_error

SENDGRID_API_BASE = "https://api.sendgrid.com"


def _ok(**fields: Any) -> str:
    return json.dumps({"ok": True, **fields}, ensure_ascii=False, sort_keys=True)


def _err(exc: Exception | str) -> str:
    return tool_error(str(exc))


def _env() -> dict[str, str]:
    return {**os.environ, **sql.runtime_env()}


def _sendgrid_api_key() -> str:
    return _env().get("SENDGRID_API_KEY") or ""


def _sendgrid_from_email() -> str:
    env = _env()
    return env.get("SENDGRID_FROM_EMAIL") or env.get("NOTIFICATION_FROM_EMAIL") or ""


def _sendgrid_from_name() -> str:
    env = _env()
    return _sanitize_public_identity_text(env.get("SENDGRID_FROM_NAME") or env.get("NOTIFICATION_FROM_NAME") or "Zeus de SitioUno")




def _sanitize_public_identity_text(value: Any) -> str:
    text = str(value or "")
    replacements = {
        "Agente Hermes": "Zeus de SitioUno",
        "Hermes Agent": "Zeus de SitioUno",
        "Hermes-Agent": "Zeus de SitioUno",
        "Hermes": "Zeus de SitioUno",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def _is_sitiouno_public_email(payload: dict[str, Any]) -> bool:
    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    business_id = str(metadata.get("business_id") or metadata.get("brand") or "").strip().lower()
    return business_id in {"sitiouno", "sitio_uno", "siteone"}


def _wrap_sitiouno_email_html(subject: str, html_body: str) -> str:
    body = _sanitize_public_identity_text(html_body)
    safe_subject = html.escape(_sanitize_public_identity_text(subject), quote=True)
    if "data-sitiouno-email-template" in body:
        return body
    return f"""<!doctype html>
<html lang=\"es\">
  <head>
    <meta charset=\"utf-8\"/>
    <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"/>
    <title>{safe_subject}</title>
  </head>
  <body style=\"margin:0;padding:0;background:#f4f7fb;color:#0f172a;font-family:Inter,Arial,Helvetica,sans-serif;\">
    <div style=\"display:none;max-height:0;overflow:hidden;color:transparent;opacity:0;\">Mensaje seguro de Zeus de SitioUno.</div>
    <table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"background:#f4f7fb;padding:28px 12px;\" data-sitiouno-email-template=\"v1\">
      <tr>
        <td align=\"center\">
          <table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"max-width:640px;background:#ffffff;border:1px solid #e2e8f0;border-radius:22px;overflow:hidden;box-shadow:0 18px 50px rgba(15,23,42,.10);\">
            <tr>
              <td style=\"background:linear-gradient(135deg,#0b3b75,#0f6fb8);padding:24px 28px;color:#ffffff;\">
                <div style=\"font-size:12px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;opacity:.86;\">SitioUno</div>
                <div style=\"font-size:26px;line-height:1.15;font-weight:850;margin-top:8px;\">{safe_subject}</div>
                <div style=\"font-size:13px;line-height:1.5;opacity:.88;margin-top:10px;\">Atendido por Zeus de SitioUno</div>
              </td>
            </tr>
            <tr>
              <td style=\"padding:28px;color:#0f172a;font-size:15px;line-height:1.62;\">
                {body}
              </td>
            </tr>
            <tr>
              <td style=\"padding:18px 28px;background:#f8fafc;border-top:1px solid #e2e8f0;color:#64748b;font-size:12px;line-height:1.5;\">
                <strong style=\"color:#0f172a;\">SitioUno Inc.</strong><br/>
                Comunicación segura enviada por Zeus de SitioUno. Si no esperabas este mensaje, puedes ignorarlo o responder a este correo.
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""

def _check_notifications() -> bool:
    # Keep the tool visible even if SendGrid is missing so the agent can return
    # a graceful adapter-unavailable result rather than hiding the capability.
    return True


def _sendgrid_request(path: str, body: dict[str, Any]) -> dict[str, Any]:
    key = _sendgrid_api_key()
    if not key:
        return {
            "ok": False,
            "configured": False,
            "adapter": "sendgrid",
            "status": "unavailable",
            "error": "SendGrid adapter is not configured. Set SENDGRID_API_KEY via Infisical/runtime env.",
        }
    url = f"{SENDGRID_API_BASE}{path}"
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        method="POST",
        data=data,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            payload = json.loads(raw) if raw else None
            return {"ok": 200 <= resp.status < 300, "configured": True, "adapter": "sendgrid", "status": resp.status, "data": payload}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload: Any = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            payload = raw
        return {"ok": False, "configured": True, "adapter": "sendgrid", "status": exc.code, "error": payload}
    except Exception as exc:
        return {"ok": False, "configured": True, "adapter": "sendgrid", "status": "error", "error": str(exc)}


def _email_adapter_send(payload: dict[str, Any]) -> dict[str, Any]:
    to_email = str(payload.get("to_email") or "").strip()
    public_sitiouno = _is_sitiouno_public_email(payload)
    subject = str(payload.get("subject") or "").strip()
    if public_sitiouno:
        subject = _sanitize_public_identity_text(subject)
    if not to_email:
        raise ValueError("to_email is required")
    if not subject:
        raise ValueError("subject is required")
    from_email = _sendgrid_from_email()
    if not _sendgrid_api_key() or not from_email:
        missing = "SENDGRID_API_KEY" if not _sendgrid_api_key() else "SENDGRID_FROM_EMAIL"
        return {
            "ok": False,
            "configured": False,
            "adapter": "sendgrid",
            "status": "unavailable",
            "error": f"SendGrid adapter is not configured. Set {missing} via Infisical/runtime env.",
        }
    content = []
    if payload.get("text"):
        text_value = str(payload["text"])
        if public_sitiouno:
            text_value = _sanitize_public_identity_text(text_value)
        content.append({"type": "text/plain", "value": text_value})
    if payload.get("html"):
        html_value = str(payload["html"])
        if public_sitiouno:
            html_value = _wrap_sitiouno_email_html(subject, html_value)
        content.append({"type": "text/html", "value": html_value})
    if not content:
        raise ValueError("text or html is required")
    to_entry = {"email": to_email}
    if payload.get("to_name"):
        to_entry["name"] = str(payload["to_name"])
    body: dict[str, Any] = {
        "personalizations": [{"to": [to_entry]}],
        "from": {"email": from_email, "name": _sendgrid_from_name()},
        "subject": subject,
        "content": content,
    }
    if payload.get("metadata") and isinstance(payload["metadata"], dict):
        body["custom_args"] = {str(k): str(v) for k, v in payload["metadata"].items() if v is not None}
    result = _sendgrid_request("/v3/mail/send", body)
    return {"adapter": "sendgrid", **result}


def _handle_email_send(args: dict, **_kwargs) -> str:
    try:
        return _ok(result=_email_adapter_send(args))
    except Exception as exc:
        return _err(exc)


def _handle_notification_status(args: dict, **_kwargs) -> str:
    try:
        return _ok(adapters={"sendgrid": {"configured": bool(_sendgrid_api_key() and _sendgrid_from_email()), "from_email": _sendgrid_from_email() or None}})
    except Exception as exc:
        return _err(exc)


def _schema(name: str, description: str, props: dict, required: list[str] | None = None) -> dict:
    return {"type": "function", "function": {"name": name, "description": description, "parameters": {"type": "object", "properties": props, "required": required or []}}}


registry.register(name="notification_status", toolset="notifications", schema=_schema("notification_status", "Return provider-neutral notification adapter status.", {}), handler=_handle_notification_status, check_fn=_check_notifications, emoji="✉️")
registry.register(name="notification_email_send", toolset="notifications", schema=_schema("notification_email_send", "Send an email through the configured provider-neutral notification adapter. SendGrid is currently the email adapter.", {"to_email": {"type": "string"}, "to_name": {"type": "string"}, "subject": {"type": "string"}, "text": {"type": "string"}, "html": {"type": "string"}, "metadata": {"type": "object"}}, ["to_email", "subject"]), handler=_handle_email_send, check_fn=_check_notifications, emoji="✉️")

#!/usr/bin/env python3
"""Dispatch OTP messages queued by the public delivery sandbox.

The delivery sandbox intentionally has no WhatsApp/Telegram secrets. It writes
OTP requests to otp_outbox.jsonl; this trusted Hermes-side script sends pending
codes through registered gateway channels and records delivered event_ids.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import shlex
import time
from pathlib import Path


def load_runtime_secrets_env() -> None:
    """Load Zeus runtime secrets for script-only cron runs.

    The gateway/dashboard systemd units receive /home/jean/.hermes/runtime-secrets.env,
    but Hermes no_agent cron scripts run as plain subprocesses. Without this, the
    OTP dispatcher sees Telegram/SendGrid as unconfigured even though the live
    gateway is healthy.
    """
    env_path = Path(os.environ.get("HERMES_RUNTIME_SECRETS_ENV", "/home/jean/.hermes/runtime-secrets.env"))
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        try:
            parsed = shlex.split(line, comments=False, posix=True)
        except ValueError:
            parsed = [line]
        if not parsed:
            continue
        assignment = parsed[0]
        if assignment.startswith("export "):
            assignment = assignment.split(" ", 1)[1]
        if "=" not in assignment:
            continue
        name, value = assignment.split("=", 1)
        name = name.strip()
        if name and name not in os.environ:
            os.environ[name] = value


load_runtime_secrets_env()

from tools import notification_tool
from tools.send_message_tool import send_message_tool

OTP_RE = re.compile(r"\b(\d{6})\b")


def sanitize_public_message(message: str) -> str:
    """Keep queued customer-facing OTP copy on the SitioUno public identity."""
    text = notification_tool._sanitize_public_identity_text(message)
    text = text.replace("Tu código Zeus para ", "Tu código de Zeus de SitioUno para ")
    text = text.replace("Tu código Zeus de SitioUno para ", "Tu código de Zeus de SitioUno para ")
    text = text.replace(" para approved ", " para aceptar ")
    text = text.replace(" para rejected ", " para rechazar ")
    return text


def load_state(event_dir: Path) -> dict:
    path = event_dir / "user_auth_state.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def challenge_is_current(event_dir: Path, item: dict) -> bool:
    """Skip stale queued OTPs so delayed email cannot send a code the UI no longer validates."""
    challenge_id = str(item.get("challenge_id") or "")
    if not challenge_id:
        return True
    state = load_state(event_dir)
    challenge = (state.get("challenges") or {}).get(challenge_id)
    if not isinstance(challenge, dict):
        return False
    if int(challenge.get("expires_at", 0)) <= int(time.time()):
        return False
    if int(challenge.get("attempts", 0)) >= 5:
        return False
    return True


def email_address_from_target(target: str) -> str | None:
    value = target.split(":", 1)[1] if target.startswith("email:") else target
    return value if "@" in value else None


def document_label_from_message(item: dict, message: str) -> str:
    raw_metadata = item.get("metadata")
    metadata: dict = raw_metadata if isinstance(raw_metadata, dict) else {}
    for key in ("public_document_number", "quote_number", "invoice_number", "document_number"):
        value = metadata.get(key)
        if value:
            return str(value)
    match = re.search(r"documento\s+([^\s.]+)", message, re.IGNORECASE)
    if match:
        return match.group(1)
    return str(item.get("deliverable_id") or "documento seguro")


def purpose_label_for_otp(item: dict) -> str:
    purpose = str(item.get("event_type") or item.get("purpose") or "validación")
    return {
        "unlock": "validar tu identidad",
        "approved": "aceptar la cotización",
        "rejected": "rechazar el documento",
        "signed": "firmar el documento",
    }.get(purpose, "validar este documento")


def subject_for_otp(item: dict, message: str) -> str:
    doc = document_label_from_message(item, message)
    if str(item.get("event_type") or item.get("purpose") or "") == "unlock":
        return f"Código de Zeus de SitioUno para validar identidad — {doc}"
    return f"Código de Zeus de SitioUno — {doc}"


def otp_from_message(message: str) -> str:
    match = OTP_RE.search(message)
    if not match:
        raise ValueError("OTP message must include a 6-digit code")
    return match.group(1)


def render_sitiouno_otp_email_text(item: dict, safe_message: str) -> str:
    otp = otp_from_message(safe_message)
    doc = document_label_from_message(item, safe_message)
    purpose = purpose_label_for_otp(item)
    return (
        f"Tu código de Zeus de SitioUno para {purpose} en el documento {doc} es:\n\n"
        f"{otp}\n\n"
        "Expira en 10 minutos. No compartas el código.\n"
        "Este código valida tu identidad en un documento seguro de SitioUno."
    )


def render_sitiouno_otp_email_html(item: dict, safe_message: str) -> str:
    otp = otp_from_message(safe_message)
    doc = html.escape(document_label_from_message(item, safe_message), quote=True)
    purpose = html.escape(purpose_label_for_otp(item), quote=True)
    digit_boxes = "".join(
        f'<span class="sitiouno-otp-digit" style="display:inline-block;width:44px;height:52px;line-height:52px;text-align:center;border:1px solid #d9dee8;border-radius:14px;background:#ffffff;color:#111827;font-size:28px;font-weight:900;letter-spacing:.02em;margin:0 4px;box-shadow:0 8px 18px rgba(16,24,40,.08);">{html.escape(digit)}</span>'
        for digit in otp
    )
    return f"""
<div data-sitiouno-otp-template="v1">
  <p style="margin:0 0 14px;color:#0f172a;">Usa este código para {purpose} en el documento seguro de SitioUno.</p>
  <div style="border:1px solid #d9dee8;border-radius:20px;background:#f8fafc;padding:18px;text-align:center;margin:18px 0;">
    <div style="font-size:12px;text-transform:uppercase;letter-spacing:.12em;color:#667085;font-weight:800;margin-bottom:10px;">Código de verificación</div>
    <div role="text" aria-label="Código OTP {html.escape(otp, quote=True)}" style="white-space:nowrap;">{digit_boxes}</div>
    <div style="font-size:13px;color:#667085;margin-top:12px;">Expira en 10 minutos.</div>
  </div>
  <div style="border-left:4px solid #0f62fe;padding-left:12px;margin:16px 0;color:#475467;font-size:14px;line-height:1.55;">
    Documento: <strong style="color:#111827;">{doc}</strong><br/>
    Canal validado: este mismo correo.
  </div>
  <p style="margin:14px 0 0;color:#475467;">No compartas el código. SitioUno nunca te pedirá reenviarlo fuera del enlace seguro.</p>
</div>""".strip()


def send_email_otp(item: dict, target_email: str, message: str) -> dict:
    safe_message = sanitize_public_message(message)
    subject = subject_for_otp(item, safe_message)
    text = render_sitiouno_otp_email_text(item, safe_message)
    html_body = render_sitiouno_otp_email_html(item, safe_message)
    return notification_tool._email_adapter_send(
        {
            "to_email": target_email,
            "to_name": item.get("recipient_label") or item.get("label") or "Cliente",
            "subject": subject,
            "text": text,
            "html": html_body,
            "metadata": {
                "business_id": "sitiouno",
                "source": "otp_outbox_dispatcher",
                "template": "sitiouno_otp_v1",
                "otp_event_id": item.get("event_id"),
                "challenge_id": item.get("challenge_id"),
                "deliverable_id": item.get("deliverable_id"),
                "event_type": item.get("event_type"),
            },
        }
    )


def load_sent(path: Path) -> set[str]:
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return {str(x) for x in data}
    except Exception:
        pass
    return set()


def save_sent(path: Path, sent: set[str]) -> None:
    path.write_text(json.dumps(sorted(sent), ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-dir", default="/home/jean/zeus-runtime/delivery-sandbox/events")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    event_dir = Path(args.event_dir)
    outbox = event_dir / "otp_outbox.jsonl"
    sent_path = event_dir / "otp_outbox_sent.json"
    sent = load_sent(sent_path)
    dispatched = 0
    errors: list[dict[str, str]] = []

    if not outbox.exists():
        print(json.dumps({"ok": True, "dispatched": 0, "errors": []}, ensure_ascii=False))
        return

    for line in outbox.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        event_id = str(item.get("event_id") or "")
        if not event_id or event_id in sent:
            continue
        target = str(item.get("target") or "")
        message = str(item.get("message") or "")
        if not target or not message:
            errors.append({"event_id": event_id, "error": "missing_target_or_message"})
            continue
        if not challenge_is_current(event_dir, item):
            # Mark stale queued OTPs as handled so an old email cannot arrive after
            # a newer challenge and produce the “right-looking code, wrong challenge” UX.
            sent.add(event_id)
            continue
        target_email = email_address_from_target(target)
        if args.dry_run:
            dispatched += 1
            continue
        if target_email:
            result = send_email_otp(item, target_email, message)
        else:
            result_raw = send_message_tool({"action": "send", "target": target, "message": sanitize_public_message(message)})
            try:
                result = json.loads(result_raw)
            except Exception:
                result = {"raw": result_raw}
        if isinstance(result, dict) and (result.get("error") or result.get("ok") is False):
            errors.append({"event_id": event_id, "error": str(result.get("error") or result)})
            continue
        sent.add(event_id)
        dispatched += 1

    if not args.dry_run:
        save_sent(sent_path, sent)
    print(json.dumps({"ok": not errors, "dispatched": dispatched, "errors": errors}, ensure_ascii=False))


if __name__ == "__main__":
    main()

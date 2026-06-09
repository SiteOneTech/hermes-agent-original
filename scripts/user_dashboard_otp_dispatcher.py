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
import re
import time
from pathlib import Path

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


def subject_for_otp(item: dict, message: str) -> str:
    doc = "documento seguro"
    match = re.search(r"documento\s+([^\s.]+)", message, re.IGNORECASE)
    if match:
        doc = match.group(1)
    purpose = str(item.get("event_type") or item.get("purpose") or "validación")
    if purpose == "unlock":
        return f"Código de Zeus de SitioUno para validar identidad — {doc}"
    return f"Código de Zeus de SitioUno — {doc}"


def send_email_otp(item: dict, target_email: str, message: str) -> dict:
    safe_message = sanitize_public_message(message)
    subject = subject_for_otp(item, safe_message)
    text = safe_message + "\n\nEste código valida tu identidad en un documento seguro de SitioUno. No compartas el código."
    html_body = (
        "<p>" + html.escape(safe_message) + "</p>"
        "<p>Este código valida tu identidad en un documento seguro de SitioUno. No compartas el código.</p>"
    )
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

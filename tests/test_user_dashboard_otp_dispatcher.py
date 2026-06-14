import importlib.util
import json
import time
from pathlib import Path


def load_dispatcher():
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "user_dashboard_otp_dispatcher.py"
    spec = importlib.util.spec_from_file_location("user_dashboard_otp_dispatcher", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_email_otp_uses_sendgrid_notification_adapter_and_sitiouno_identity(monkeypatch):
    dispatcher = load_dispatcher()
    calls = []

    def fake_send(payload):
        calls.append(payload)
        return {"ok": True, "adapter": "sendgrid", "status": 202, "configured": True}

    monkeypatch.setattr(dispatcher.notification_tool, "_email_adapter_send", fake_send)
    item = {
        "event_id": "evt-otp",
        "challenge_id": "challenge-1",
        "deliverable_id": "quote-1",
        "event_type": "unlock",
    }

    result = dispatcher.send_email_otp(
        item,
        "client@example.com",
        "Tu código Hermes para validar identidad en el documento Q-01016 es: 123456. Expira en 10 minutos.",
    )

    assert result["ok"] is True
    assert calls
    payload = calls[0]
    rendered = payload["subject"] + payload["text"] + payload["html"]
    assert payload["to_email"] == "client@example.com"
    assert payload["metadata"]["business_id"] == "sitiouno"
    assert payload["metadata"]["source"] == "otp_outbox_dispatcher"
    assert "Hermes" not in rendered
    assert "Zeus de SitioUno" in rendered
    assert "123456" in payload["text"]
    assert payload["metadata"]["template"] == "sitiouno_otp_v1"
    assert 'data-sitiouno-otp-template="v1"' in payload["html"]
    assert payload["html"].count('class="sitiouno-otp-digit"') == 6
    assert "es: 123456" not in payload["html"]
    assert "No compartas el código" in payload["html"]


def test_challenge_is_current_rejects_missing_expired_or_attempted_challenges(tmp_path):
    dispatcher = load_dispatcher()
    now = int(time.time())
    state_path = tmp_path / "user_auth_state.json"

    state_path.write_text(
        json.dumps(
            {
                "challenges": {
                    "current": {"expires_at": now + 300, "attempts": 0},
                    "expired": {"expires_at": now - 1, "attempts": 0},
                    "attempted": {"expires_at": now + 300, "attempts": 5},
                }
            }
        ),
        encoding="utf-8",
    )

    assert dispatcher.challenge_is_current(tmp_path, {"challenge_id": "current"}) is True
    assert dispatcher.challenge_is_current(tmp_path, {"challenge_id": "expired"}) is False
    assert dispatcher.challenge_is_current(tmp_path, {"challenge_id": "attempted"}) is False
    assert dispatcher.challenge_is_current(tmp_path, {"challenge_id": "missing"}) is False

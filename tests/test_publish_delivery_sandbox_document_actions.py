import json
import sys
import types
import hashlib
import hmac
import time
from io import BytesIO
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parents[1] / "scripts" / "runtime"
sys.path.insert(0, str(RUNTIME_DIR))
from scripts.runtime import publish_delivery_sandbox as publisher


def _server_module(tmp_path):
    runtime_dir = Path(__file__).resolve().parents[1] / "scripts" / "runtime"
    sys.path.insert(0, str(runtime_dir))
    module = types.ModuleType("generated_delivery_server")
    exec(publisher.SERVER_PY, module.__dict__)
    module.EVENT_DIR = tmp_path / "events"
    module.PUBLIC_DIR = tmp_path / "public"
    module.USER_DATA_DIR = tmp_path / "user-data"
    module.ALLOWED_HOSTS = set()
    return module


def test_generated_server_document_action_policy_and_private_recipient(tmp_path):
    server = _server_module(tmp_path)
    token = "A" * 24
    workspace = server.PUBLIC_DIR / "w" / token
    workspace.mkdir(parents=True)
    (workspace / "index.html").write_text("quote-1", encoding="utf-8")
    private = server.USER_DATA_DIR / "workspace-recipients"
    private.mkdir(parents=True)
    (private / f"{token}.json").write_text(
        json.dumps({"recipient": {"channel_id": "whatsapp", "target": "+130****0000", "label": "WhatsApp"}}),
        encoding="utf-8",
    )

    assert server.document_action_requires_otp("commented") is False
    assert server.document_action_requires_otp("unlock") is True
    assert server.document_action_requires_otp("approved") is True
    assert server.document_action_requires_otp("rejected") is True
    assert server.document_action_requires_otp("signed") is True
    assert server._workspace_matches_token(token, "quote-1", {"quote_id": "quote-1"}) is True
    assert server._document_action_recipient(token)["target"] == "+130****0000"


def test_generated_server_rejects_signed_action_without_otp_session(tmp_path):
    server = _server_module(tmp_path)
    token = "S" * 24
    workspace = server.PUBLIC_DIR / "w" / token
    workspace.mkdir(parents=True)
    (workspace / "index.html").write_text("quote-otp", encoding="utf-8")
    handler = _FakeJsonPostHandler({
        "token": token,
        "deliverable_id": "quote-otp",
        "event_type": "signed",
        "metadata": {"quote_id": "quote-otp"},
    })

    server._handle_document_action(handler)

    assert handler.status == 401
    response = json.loads(handler.wfile.getvalue().split(b"\r\n\r\n")[-1] or handler.wfile.getvalue())
    assert response["error"] == "otp_required"


def test_generated_server_rejects_wrong_signer_token_for_document_action(tmp_path):
    server = _server_module(tmp_path)
    real_token = "R" * 24
    wrong_token = "W" * 24
    workspace = server.PUBLIC_DIR / "w" / real_token
    workspace.mkdir(parents=True)
    (workspace / "index.html").write_text("quote-token", encoding="utf-8")
    handler = _FakeJsonPostHandler({
        "token": wrong_token,
        "deliverable_id": "quote-token",
        "event_type": "commented",
        "metadata": {"quote_id": "quote-token"},
    })

    server._handle_document_action(handler)

    assert handler.status == 422
    response = json.loads(handler.wfile.getvalue().split(b"\r\n\r\n")[-1] or handler.wfile.getvalue())
    assert response["error"] == "invalid_document_action"


def test_generated_server_queue_otp_omits_plaintext_code_and_message(tmp_path):
    server = _server_module(tmp_path)
    server._queue_otp(
        {
            "challenge_id": "challenge-1",
            "user_id": "client@example.com",
            "channel_id": "email",
            "target": "client@example.com",
            "purpose": "document_action",
            "event_type": "approved",
            "deliverable_id": "quote-1",
            "token_ref": "abc...",
            "message": "Código para aprobar: 123456",
            "message_template": "document_action_otp",
            "message_context": {"action": "aprobar", "document": "quote-1"},
        },
        "123456",
    )

    outbox = server._outbox_path().read_text(encoding="utf-8").splitlines()
    assert "123456" not in outbox[-1]
    assert "Código para aprobar" not in outbox[-1]
    payload = json.loads(outbox[-1])
    assert "message" not in payload
    assert "otp" not in payload
    assert "otp_code" not in payload
    assert payload["purpose"] == "document_action"
    assert payload["event_type"] == "approved"
    assert payload["message_template"] == "document_action_otp"
    assert payload["message_context"] == {"action": "aprobar", "document": "quote-1"}
    assert payload["dispatch_ref"]


def test_generated_server_document_action_challenge_state_omits_plaintext_message_and_otp(tmp_path):
    server = _server_module(tmp_path)
    token = "D" * 24
    workspace = server.PUBLIC_DIR / "w" / token
    workspace.mkdir(parents=True)
    (workspace / "workspace.json").write_text(json.dumps({"deliverable_id": "quote-1"}), encoding="utf-8")

    challenge_id = server._create_document_action_challenge(
        {
            "token": token,
            "deliverable_id": "quote-1",
            "event_type": "approved",
            "metadata": {"quote_id": "quote-1", "quote_number": "Q-1"},
        },
        {"channel_id": "email", "target": "client@example.com"},
    )

    state_text = server._state_path().read_text(encoding="utf-8")
    assert challenge_id in state_text
    assert "Tu código" not in state_text
    assert "Expira en 10 minutos" not in state_text
    assert "otp_hash" in state_text

    outbox_text = server._outbox_path().read_text(encoding="utf-8")
    assert "Tu código" not in outbox_text
    assert "Expira en 10 minutos" not in outbox_text


def test_generated_server_rejects_terminal_document_action_before_otp_outbox(tmp_path):
    server = _server_module(tmp_path)
    token = "T" * 24
    workspace = server.PUBLIC_DIR / "w" / token
    workspace.mkdir(parents=True)
    (workspace / "workspace.json").write_text(
        json.dumps({"deliverable_id": "quote-terminal", "status": "completed"}),
        encoding="utf-8",
    )
    private = server.USER_DATA_DIR / "workspace-recipients"
    private.mkdir(parents=True)
    (private / f"{token}.json").write_text(
        json.dumps({"recipient": {"channel_id": "email", "target": "client@example.com"}, "status": "completed"}),
        encoding="utf-8",
    )
    handler = _FakeJsonPostHandler({
        "token": token,
        "deliverable_id": "quote-terminal",
        "event_type": "signed",
        "metadata": {"quote_id": "quote-terminal"},
    })

    server._handle_document_action_request_otp(handler)

    assert handler.status == 409
    response = json.loads(handler.wfile.getvalue().split(b"\r\n\r\n")[-1] or handler.wfile.getvalue())
    assert response["error"] == "terminal_document_status"
    assert not server._outbox_path().exists()


def test_generated_server_revalidates_terminal_status_before_verified_action_queue(tmp_path):
    server = _server_module(tmp_path)
    token = "V" * 24
    workspace = server.PUBLIC_DIR / "w" / token
    workspace.mkdir(parents=True)
    (workspace / "workspace.json").write_text(json.dumps({"deliverable_id": "quote-verify"}), encoding="utf-8")
    private = server.USER_DATA_DIR / "workspace-recipients"
    private.mkdir(parents=True)
    (private / f"{token}.json").write_text(
        json.dumps({"recipient": {"channel_id": "email", "target": "client@example.com"}}),
        encoding="utf-8",
    )
    challenge_id = server._create_document_action_challenge(
        {"token": token, "deliverable_id": "quote-verify", "event_type": "signed", "metadata": {"quote_id": "quote-verify"}},
        {"channel_id": "email", "target": "client@example.com"},
    )
    state = server._load_state()
    state["challenges"][challenge_id]["otp_hash"] = server._hash(f"{challenge_id}:123456")
    server._save_state(state)
    (workspace / "workspace.json").write_text(json.dumps({"deliverable_id": "quote-verify", "status": "expired"}), encoding="utf-8")
    handler = _FakeJsonPostHandler({"challenge_id": challenge_id, "otp": "123456"})

    server._handle_document_action_verify_otp(handler)

    assert handler.status == 409
    response = json.loads(handler.wfile.getvalue().split(b"\r\n\r\n")[-1] or handler.wfile.getvalue())
    assert response["error"] == "terminal_document_status"
    assert not server._audit_path().exists()


def test_generated_server_document_action_unlock_session_rejects_terminal_workspace_action(tmp_path):
    server = _server_module(tmp_path)
    token = "U" * 24
    workspace = server.PUBLIC_DIR / "w" / token
    workspace.mkdir(parents=True)
    (workspace / "workspace.json").write_text(
        json.dumps({"deliverable_id": "quote-unlock", "status": "cancelled", "metadata": {"action_policy": "otp_unlock"}}),
        encoding="utf-8",
    )
    action_token = server._create_document_action_session(
        token=token,
        deliverable_id="quote-unlock",
        recipient={"channel_id": "email", "target": "client@example.com"},
    )
    handler = _FakeJsonPostHandler({
        "token": token,
        "deliverable_id": "quote-unlock",
        "event_type": "approved",
        "action_token": action_token,
        "metadata": {"quote_id": "quote-unlock"},
    })

    server._handle_document_action(handler)

    assert handler.status == 409
    response = json.loads(handler.wfile.getvalue().split(b"\r\n\r\n")[-1] or handler.wfile.getvalue())
    assert response["error"] == "terminal_document_status"
    assert not server._audit_path().exists()


def test_generated_server_document_action_unlock_session_gates_workspace_actions(tmp_path):
    server = _server_module(tmp_path)
    token = "B" * 24
    workspace = server.PUBLIC_DIR / "w" / token
    workspace.mkdir(parents=True)
    (workspace / "workspace.json").write_text(
        json.dumps({"deliverable_id": "quote-1", "metadata": {"action_policy": "otp_unlock"}}),
        encoding="utf-8",
    )
    recipient = {"channel_id": "email:client@example.com", "target": "client@example.com"}

    assert server._workspace_requires_action_unlock(token) is True
    action_token = server._create_document_action_session(token=token, deliverable_id="quote-1", recipient=recipient)
    session = server._valid_document_action_session(action_token, token=token, deliverable_id="quote-1")

    assert session["channel_id"] == "email:client@example.com"
    assert session["target_hash"] == server._hash("client@example.com")
    assert server._valid_document_action_session(action_token, token=token, deliverable_id="quote-2") is None


class _FakeStripeHandler:
    def __init__(self, raw_body: bytes, signature: str):
        self.headers = {"Content-Length": str(len(raw_body)), "Stripe-Signature": signature, "User-Agent": "stripe-test"}
        self.rfile = BytesIO(raw_body)
        self.wfile = BytesIO()
        self.client_address = ("127.0.0.1", 12345)
        self.status = None
        self.response_headers = []

    def send_response(self, status):
        self.status = status

    def send_header(self, key, value):
        self.response_headers.append((key, value))

    def end_headers(self):
        pass


class _FakeGetHandler:
    def __init__(self, cookie: str | None = None):
        self.headers = {"Cookie": cookie or "", "Host": "example.test", "User-Agent": "pytest"}
        self.rfile = BytesIO()
        self.wfile = BytesIO()
        self.client_address = ("127.0.0.1", 12345)
        self.status = None
        self.response_headers = []

    def send_response(self, status):
        self.status = status

    def send_header(self, key, value):
        self.response_headers.append((key, value))

    def end_headers(self):
        self.wfile.write(b"\r\n\r\n")


class _FakeJsonPostHandler:
    def __init__(self, payload: dict):
        raw = json.dumps(payload).encode("utf-8")
        self.headers = {"Content-Length": str(len(raw)), "Content-Type": "application/json", "Host": "example.test", "User-Agent": "pytest"}
        self.rfile = BytesIO(raw)
        self.wfile = BytesIO()
        self.client_address = ("127.0.0.1", 12345)
        self.status = None
        self.response_headers = []

    def send_response(self, status):
        self.status = status

    def send_header(self, key, value):
        self.response_headers.append((key, value))

    def end_headers(self):
        self.wfile.write(b"\r\n\r\n")


def _header(handler: _FakeGetHandler, key: str) -> str | None:
    return next((value for name, value in handler.response_headers if name.lower() == key.lower()), None)


def test_generated_server_stripe_webhook_queues_signed_event(tmp_path):
    server = _server_module(tmp_path)
    server.STRIPE_WEBHOOK_SECRET = "whsec_test"
    payload = {
        "id": "evt_test_123",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123",
                "object": "checkout.session",
                "client_reference_id": "pay-1",
                "metadata": {"payment_request_id": "pay-1", "invoice_id": "invoice-1"},
                "customer_email": "payer@example.com",
                "billing_details": {"name": "Private Payer"},
            }
        },
    }
    raw = json.dumps(payload, separators=(",", ":")).encode()
    timestamp = int(time.time())
    digest = hmac.new(b"whsec_test", str(timestamp).encode() + b"." + raw, hashlib.sha256).hexdigest()
    handler = _FakeStripeHandler(raw, f"t={timestamp},v1={digest}")

    server._handle_stripe_webhook(handler)

    assert handler.status == 200
    response = json.loads(handler.wfile.getvalue().split(b"\r\n\r\n")[-1] or handler.wfile.getvalue())
    assert response["status"] == "queued"
    events = server._audit_path().read_text(encoding="utf-8").splitlines()
    queued = json.loads(events[-1])
    assert queued["event_type"] == "stripe_webhook"
    assert queued["deliverable_id"] == "invoice-1"
    assert queued["metadata"]["stripe_event_id"] == "evt_test_123"
    assert queued["metadata"]["stripe_event"]["type"] == "checkout.session.completed"
    assert "customer_email" not in queued["metadata"]["stripe_event"]["data"]["object"]
    assert "billing_details" not in queued["metadata"]["stripe_event"]["data"]["object"]


def test_generated_server_stripe_webhook_rejects_bad_signature(tmp_path):
    server = _server_module(tmp_path)
    server.STRIPE_WEBHOOK_SECRET = "whsec_test"
    handler = _FakeStripeHandler(b'{"id":"evt_bad"}', "t=123,v1=bad")

    server._handle_stripe_webhook(handler)

    assert handler.status == 400


def test_generated_nginx_downloads_are_not_public_static_files():
    download_block = publisher.NGINX_CONF.split("location /download/", 1)[1].split("location /w/", 1)[0]

    assert "proxy_pass http://delivery-sandbox-events:8080" in download_block
    assert "try_files" not in download_block


def test_protected_download_rejects_direct_and_wrong_artifact_token(tmp_path):
    server = _server_module(tmp_path)
    workspace_token = "C" * 24
    relative_path = f"{workspace_token}/signed.pdf"
    artifact = server.PUBLIC_DIR / "download" / relative_path
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(b"signed pdf")

    direct = _FakeGetHandler()
    server._handle_protected_download(direct, f"/download/{relative_path}", {})
    assert direct.status == 401

    wrong = _FakeGetHandler()
    server._handle_protected_download(wrong, f"/download/{relative_path}", {"artifact_token": ["wrong-token"]})
    assert wrong.status == 403

    allowed = _FakeGetHandler()
    scoped_token = server._artifact_access_token(workspace_token, relative_path)
    server._handle_protected_download(allowed, f"/download/{relative_path}", {"artifact_token": [scoped_token]})
    assert allowed.status == 200
    assert b"signed pdf" in allowed.wfile.getvalue()


def test_signature_dashboard_requires_otp_session(tmp_path):
    server = _server_module(tmp_path)
    handler = _FakeGetHandler()

    server._handle_user_get(handler, "/user/signatures/", {})

    assert handler.status == 303
    assert _header(handler, "Location") == "/user/login"


def test_signature_dashboard_renders_protected_metrics_and_status(tmp_path, monkeypatch):
    server = _server_module(tmp_path)
    data_dir = server.USER_DATA_DIR
    data_dir.mkdir(parents=True)
    (data_dir / "signature_dashboard.json").write_text(json.dumps({
        "summary": {
            "active": 3,
            "pending": 5,
            "expiring": 2,
            "completed": 8,
            "declined": 1,
            "reminders": 4,
            "copy_receipts": 7,
            "hash_status": "verified",
        },
        "processes": [
            {"title": "Contrato Qrovia", "status": "pending", "pending_signers": 2, "hash_status": "verified", "expires_at": "2026-06-20"},
            {"title": "NDA Flexipos", "status": "declined", "pending_signers": 0, "hash_status": "missing", "expires_at": "2026-06-18"},
        ],
    }), encoding="utf-8")
    monkeypatch.setattr(server, "_session_from_request", lambda handler: {"user_id": "jean", "channel_id": "whatsapp"})
    handler = _FakeGetHandler(cookie="session=ok")

    server._handle_user_get(handler, "/user/signatures/", {})

    html = handler.wfile.getvalue().decode("utf-8")
    assert handler.status == 200
    assert "Dashboard de firmas" in html
    for label in ["Activas", "Pendientes", "Por vencer", "Completadas", "Declinadas", "Recordatorios", "Copias", "Hash"]:
        assert label in html
    assert "Contrato Qrovia" in html
    assert "NDA Flexipos" in html
    assert "verified" in html

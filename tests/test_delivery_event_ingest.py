import importlib.util
from pathlib import Path


def _load_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "runtime" / "ingest_delivery_events.py"
    spec = importlib.util.spec_from_file_location("ingest_delivery_events", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_comment_does_not_regress_final_workspace_status():
    ingest = _load_module()

    assert ingest._status_for_event("commented", "approved") is None
    assert ingest._status_for_event("opened", "rejected") is None
    assert ingest._status_for_event("commented", "viewed") == "commented"
    assert ingest._status_for_event("approved", "commented") == "approved"


def test_ingest_uses_canonical_document_action_sets():
    ingest = _load_module()

    assert "commented" in ingest.SALES_EVENT_TYPES
    assert "document_action_unlocked" in ingest.SALES_EVENT_TYPES
    assert "document_action_otp_requested" in ingest.SALES_EVENT_TYPES
    assert "approved" in ingest.FINAL_SALES_STATUS
    assert "rejected" in ingest.FINAL_RECEIPT_STATUS
    assert "signed" in ingest.EVENT_TYPES_WITH_OWNER_ACTION


def test_document_access_activity_updates_viewed_status():
    ingest = _load_module()

    assert ingest._status_for_event("document_action_unlocked", "pending") == "viewed"
    assert ingest._status_for_event("document_action_otp_requested", "pending") is None


def test_load_events_keeps_document_access_activity_statuses(tmp_path):
    ingest = _load_module()
    events_path = tmp_path / "events.jsonl"
    events_path.write_text(
        "\n".join([
            '{"event_id":"otp-1","event_type":"document_action_otp_requested","status":"pending_otp_dispatch"}',
            '{"event_id":"unlock-1","event_type":"document_action_unlocked","status":"active"}',
            '{"event_id":"noise-1","event_type":"user_session_started","status":"active"}',
        ]),
        encoding="utf-8",
    )

    loaded = ingest.load_events(events_path)

    assert [event["event_id"] for event in loaded] == ["otp-1", "unlock-1"]


def test_one_bad_adapter_event_does_not_block_sales_comment_ingest(tmp_path, monkeypatch):
    ingest = _load_module()
    events_path = tmp_path / "events.jsonl"
    events_path.write_text(
        "\n".join(
            [
                '{"event_id":"stripe-1","event_type":"stripe_webhook","status":"pending_agent_ingest","metadata":{"stripe_event":{"id":"evt_bad","type":"checkout.session.completed"}}}',
                '{"event_id":"comment-1","event_type":"commented","deliverable_id":"quote-1","status":"pending_agent_ingest","comment":"Cliente comentó","metadata":{"workspace_id":"workspace-quote-1"}}',
            ]
        ),
        encoding="utf-8",
    )
    calls = []

    def bad_stripe(_event):
        raise RuntimeError("stripe adapter exploded")

    def sales_event(event, _public_root):
        if event.get("event_type") != "commented":
            return None
        calls.append(event["event_id"])
        return "sales:ingested"

    monkeypatch.setattr(ingest, "ingest_stripe_event", bad_stripe)
    monkeypatch.setattr(ingest, "ingest_sales_event", sales_event)
    monkeypatch.setattr(ingest, "ingest_receipt_event", lambda *_args, **_kwargs: None)

    assert ingest.main(["--events", str(events_path), "--public-root", str(tmp_path), "--quiet"]) == 0
    assert calls == ["comment-1"]

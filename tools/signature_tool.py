"""Agent-native Signature Core tools backed by Agent Core DB.

Signature Core is the canonical local module for document requests, public
signing links, signature/approval capture, append-only audit events, and
approval hashes. Dedicated e-signature suites (DocuSeal, OpenSign, DocuSign,
Dropbox Sign, etc.) are adapters; the local Agent Core DB remains the source of
truth for Zeus-style single-tenant agents.
"""
from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from hermes_cli import agent_core_sql as sql
from tools.registry import registry, tool_error

SIGNATURE_METADATA_DESCRIPTION = (
    "Optional JSON metadata. Keep it generic and tenant-neutral: business_id, "
    "owner_id, source_channel, external_ref, labels, notes."
)


def _ok(**fields: Any) -> str:
    return json.dumps({"ok": True, **fields}, ensure_ascii=False, sort_keys=True)


def _err(exc: Exception | str) -> str:
    return tool_error(str(exc))


def _user() -> str:
    return sql.runtime_env().get("SIGNATURE_DB_RUNTIME_USER", "signature_runtime")


def _check_signature() -> bool:
    try:
        if not sql.enabled():
            return False
        sql.psql("SELECT 1;", user=_user())
        return True
    except Exception:
        return False


def _q(value: Any) -> str:
    return sql.quote_literal(value)


def _j(value: Any) -> str:
    return sql.quote_jsonb(value)


def _slug(prefix: str, value: str) -> str:
    return f"{prefix}-{sql.slugify(value)}"


def _token() -> str:
    return secrets.token_urlsafe(32)


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


_REQUIRED_COMPLETION_ROLES = {"signer", "approver"}
_COMPLETE_SUBMITTER_STATUSES = {"signed", "approved"}


def _is_required_obligation(submitter: dict[str, Any]) -> bool:
    return submitter.get("role") in _REQUIRED_COMPLETION_ROLES and submitter.get("required") is not False


def _is_submitter_complete(submitter: dict[str, Any]) -> bool:
    return str(submitter.get("status") or "").lower() in _COMPLETE_SUBMITTER_STATUSES


def _completion_status_for_submitter(submitter: dict[str, Any] | None) -> str:
    if (submitter or {}).get("role") == "signer":
        return "signed"
    return "approved"


def _derive_request_lifecycle(request: dict[str, Any], submitters: list[dict[str, Any]]) -> dict[str, Any]:
    """Derive aggregate request status from required signer/approver obligations.

    Optional viewers and owner/agent observers never block completion. A request
    only becomes completed after every required signer/approver reaches signed or
    approved status.
    """
    current_status = str(request.get("status") or "sent")
    required_submitters = [submitter for submitter in submitters if _is_required_obligation(submitter)]
    completed_required = [submitter for submitter in required_submitters if _is_submitter_complete(submitter)]
    decline_blocks = request.get("decline_blocks") is not False

    if current_status == "completed":
        return {"status": "completed", "completed": True, "required_count": len(required_submitters), "completed_required_count": len(completed_required)}

    if decline_blocks and any(str(submitter.get("status") or "").lower() == "declined" for submitter in required_submitters):
        return {"status": "declined", "completed": False, "required_count": len(required_submitters), "completed_required_count": len(completed_required)}

    expires_at = _parse_dt(request.get("expires_at"))
    if expires_at and expires_at <= datetime.now(timezone.utc):
        return {"status": "expired", "completed": False, "required_count": len(required_submitters), "completed_required_count": len(completed_required)}

    if required_submitters and len(completed_required) == len(required_submitters):
        return {"status": "completed", "completed": True, "required_count": len(required_submitters), "completed_required_count": len(completed_required)}

    if completed_required:
        return {"status": "partially_signed", "completed": False, "required_count": len(required_submitters), "completed_required_count": len(completed_required)}

    return {"status": current_status, "completed": False, "required_count": len(required_submitters), "completed_required_count": 0}


def _event_hash(request_id: str, event_type: str, actor_ref: str | None, payload: Any, previous_hash: str | None) -> str:
    material = _canonical_json({
        "request_id": request_id,
        "event_type": event_type,
        "actor_ref": actor_ref,
        "payload": payload or {},
        "previous_hash": previous_hash,
    })
    return _sha256_text(material)


def _request_url(slug: str) -> str:
    base = (sql.runtime_env().get("SIGNATURE_WORKSPACE_BASE_URL") or "https://zeus-sandbox.kidu.app/sign").rstrip("/")
    return f"{base}/{slug}"


def _record_event(
    request_id: str,
    *,
    submitter_id: str | None = None,
    event_type: str,
    actor_type: str = "system",
    actor_ref: str | None = None,
    payload: dict[str, Any] | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    previous = sql.one(
        f"SELECT event_hash FROM signature.events WHERE request_id={_q(request_id)} ORDER BY signature_event_id DESC",
        user=_user(),
    )
    previous_hash = (previous or {}).get("event_hash")
    event_hash = _event_hash(request_id, event_type, actor_ref, payload or {}, previous_hash)
    return sql.statement_one(f"""
      INSERT INTO signature.events (request_id, submitter_id, event_type, actor_type, actor_ref, ip_address, user_agent, event_payload, previous_event_hash, event_hash, metadata)
      VALUES ({_q(request_id)}, {_q(submitter_id)}, {_q(event_type)}, {_q(actor_type)}, {_q(actor_ref)}, {_q(ip_address)}, {_q(user_agent)}, {_j(payload or {})}, {_q(previous_hash)}, {_q(event_hash)}, {_j(metadata or {})})
      RETURNING *
    """, user=_user())


def _handle_signature_status(args: dict, **_kwargs) -> str:
    try:
        counts = sql.one("""
          SELECT
            (SELECT count(*) FROM signature.templates) AS templates,
            (SELECT count(*) FROM signature.document_requests) AS requests,
            (SELECT count(*) FROM signature.submitters) AS submitters,
            (SELECT count(*) FROM signature.events) AS events,
            (SELECT count(*) FROM signature.approvals) AS approvals,
            (SELECT count(*) FROM signature.attachments) AS attachments,
            (SELECT count(*) FROM signature.reminder_policies) AS reminder_policies,
            (SELECT count(*) FROM signature.reminder_attempts) AS reminder_attempts,
            (SELECT count(*) FROM signature.delivery_receipts) AS delivery_receipts
        """, user=_user())
        return _ok(db_backend="agent_core_postgres", counts=counts)
    except Exception as exc:
        return _err(exc)


def _handle_template_upsert(args: dict, **_kwargs) -> str:
    try:
        name = str(args.get("name") or "").strip()
        if not name:
            raise ValueError("name is required")
        template_id = args.get("template_id") or _slug("signature-template", name)
        row = sql.statement_one(f"""
          INSERT INTO signature.templates (template_id, name, document_url, fields, submitters, preferences, metadata, created_at, updated_at)
          VALUES ({_q(template_id)}, {_q(name)}, {_q(args.get('document_url'))}, {_j(args.get('fields') or [])}, {_j(args.get('submitters') or [])}, {_j(args.get('preferences') or {})}, {_j(args.get('metadata') or {})}, now(), now())
          ON CONFLICT (template_id) DO UPDATE SET name=EXCLUDED.name, document_url=EXCLUDED.document_url, fields=EXCLUDED.fields, submitters=EXCLUDED.submitters, preferences=EXCLUDED.preferences, metadata=EXCLUDED.metadata, updated_at=now()
          RETURNING *
        """, user=_user())
        return _ok(template=row)
    except Exception as exc:
        return _err(exc)


def _handle_request_create(args: dict, **_kwargs) -> str:
    try:
        title = str(args.get("title") or "").strip()
        if not title:
            raise ValueError("title is required")
        submitters = args.get("submitters") or []
        if not isinstance(submitters, list) or not submitters:
            raise ValueError("submitters must be a non-empty list")
        request_id = args.get("request_id") or _slug("signature-request", f"{args.get('source_type') or 'document'}-{args.get('source_id') or title}")
        template = None
        if args.get("template_id"):
            template = sql.one(f"SELECT * FROM signature.templates WHERE template_id={_q(args.get('template_id'))}", user=_user())
            if not template:
                raise ValueError("template_id not found")
        fields = args.get("fields") if args.get("fields") is not None else (template or {}).get("fields") or []
        template_submitters = (template or {}).get("submitters") or []
        request = sql.statement_one(f"""
          INSERT INTO signature.document_requests (request_id, template_id, template_version_id, source_type, source_id, title, status, document_url, fields_snapshot, submitters_snapshot, preferences, metadata, expires_at, decline_blocks, signing_mode, created_at, updated_at)
          VALUES ({_q(request_id)}, {_q(args.get('template_id'))}, {_q(args.get('template_version_id'))}, {_q(args.get('source_type'))}, {_q(args.get('source_id'))}, {_q(title)}, {_q(args.get('status') or 'draft')}, {_q(args.get('document_url') or (template or {}).get('document_url'))}, {_j(fields)}, {_j(template_submitters or submitters)}, {_j(args.get('preferences') or (template or {}).get('preferences') or {})}, {_j(args.get('metadata') or {})}, {_q(args.get('expires_at'))}::timestamptz, {_q(args.get('decline_blocks') is not False)}::boolean, {_q(args.get('signing_mode') or 'parallel')}, now(), now())
          ON CONFLICT (request_id) DO UPDATE SET template_id=EXCLUDED.template_id, template_version_id=EXCLUDED.template_version_id, source_type=EXCLUDED.source_type, source_id=EXCLUDED.source_id, title=EXCLUDED.title, status=EXCLUDED.status, document_url=EXCLUDED.document_url, fields_snapshot=EXCLUDED.fields_snapshot, submitters_snapshot=EXCLUDED.submitters_snapshot, preferences=EXCLUDED.preferences, metadata=EXCLUDED.metadata, expires_at=EXCLUDED.expires_at, decline_blocks=EXCLUDED.decline_blocks, signing_mode=EXCLUDED.signing_mode, updated_at=now()
          RETURNING *
        """, user=_user())
        sql.psql(f"DELETE FROM signature.submitters WHERE request_id={_q(request_id)};", user=_user())
        saved_submitters = []
        for idx, sub in enumerate(submitters, start=1):
            token = _token()
            slug = secrets.token_urlsafe(18)
            submitter_id = sub.get("submitter_id") or _slug("signature-submitter", f"{request_id}-{sub.get('email') or sub.get('name') or idx}")
            saved = sql.statement_one(f"""
              INSERT INTO signature.submitters (submitter_id, request_id, role, signing_order, name, email, phone, slug, token_hash_sha256, status, required, metadata)
              VALUES ({_q(submitter_id)}, {_q(request_id)}, {_q(sub.get('role') or 'signer')}, {int(sub.get('signing_order') or idx)}, {_q(sub.get('name'))}, {_q(sub.get('email'))}, {_q(sub.get('phone'))}, {_q(slug)}, {_q(_sha256_text(token))}, {_q(sub.get('status') or 'pending')}, {_q(sub.get('required') is not False)}::boolean, {_j(sub.get('metadata') or {})})
              RETURNING *
            """, user=_user())
            saved_submitters.append({**(saved or {}), "signing_url": _request_url(slug), "token": token})
        _record_event(request_id, event_type="created", actor_type="agent", actor_ref=args.get("actor_ref") or "agent", payload={"submitters": len(saved_submitters)}, metadata=args.get("metadata") or {})
        return _ok(request=request, submitters=saved_submitters)
    except Exception as exc:
        return _err(exc)


def _handle_request_get(args: dict, **_kwargs) -> str:
    try:
        request_id = str(args.get("request_id") or "").strip()
        if not request_id:
            raise ValueError("request_id is required")
        request = sql.one(f"SELECT * FROM signature.document_requests WHERE request_id={_q(request_id)}", user=_user())
        if not request:
            raise ValueError("request not found")
        submitters = sql.rows(f"SELECT * FROM signature.submitters WHERE request_id={_q(request_id)} ORDER BY signing_order, created_at", user=_user())
        events = sql.rows(f"SELECT * FROM signature.events WHERE request_id={_q(request_id)} ORDER BY signature_event_id", user=_user())
        approvals = sql.rows(f"SELECT * FROM signature.approvals WHERE request_id={_q(request_id)} ORDER BY signed_at", user=_user())
        reminder_policies = sql.rows(f"SELECT * FROM signature.reminder_policies WHERE request_id={_q(request_id)} ORDER BY created_at", user=_user())
        reminder_attempts = sql.rows(f"SELECT * FROM signature.reminder_attempts WHERE request_id={_q(request_id)} ORDER BY attempted_at DESC, created_at DESC", user=_user())
        delivery_receipts = sql.rows(f"SELECT * FROM signature.delivery_receipts WHERE request_id={_q(request_id)} ORDER BY created_at DESC", user=_user())
        return _ok(request=request, submitters=submitters, events=events, approvals=approvals, reminder_policies=reminder_policies, reminder_attempts=reminder_attempts, delivery_receipts=delivery_receipts)
    except Exception as exc:
        return _err(exc)


def _handle_event_record(args: dict, **_kwargs) -> str:
    try:
        request_id = str(args.get("request_id") or "").strip()
        event_type = str(args.get("event_type") or "").strip()
        if not request_id or not event_type:
            raise ValueError("request_id and event_type are required")
        event = _record_event(
            request_id,
            submitter_id=args.get("submitter_id"),
            event_type=event_type,
            actor_type=args.get("actor_type") or "agent",
            actor_ref=args.get("actor_ref"),
            payload=args.get("event_payload") or {},
            ip_address=args.get("ip_address"),
            user_agent=args.get("user_agent"),
            metadata=args.get("metadata") or {},
        )
        return _ok(event=event)
    except Exception as exc:
        return _err(exc)


def _handle_approval_hash_create(args: dict, **_kwargs) -> str:
    try:
        request_id = str(args.get("request_id") or "").strip()
        if not request_id:
            raise ValueError("request_id is required")
        request = sql.one(f"SELECT * FROM signature.document_requests WHERE request_id={_q(request_id)}", user=_user())
        if not request:
            raise ValueError("request not found")
        approval_id = args.get("approval_id") or _slug("signature-approval", f"{request_id}-{args.get('submitter_id') or args.get('actor_ref') or 'approval'}")
        context = {
            "request_id": request_id,
            "submitter_id": args.get("submitter_id"),
            "source_type": args.get("source_type") or request.get("source_type"),
            "source_id": args.get("source_id") or request.get("source_id"),
            "title": request.get("title"),
            "document_url": request.get("document_url"),
            "document_hash_sha256": args.get("document_hash_sha256") or request.get("document_hash_sha256"),
            "signature_text": args.get("signature_text"),
            "signature_image_sha256": args.get("signature_image_sha256"),
            "signed_at": args.get("signed_at"),
            "ip_address": args.get("ip_address"),
            "user_agent": args.get("user_agent"),
            "metadata": args.get("metadata") or {},
        }
        approval_hash = args.get("approval_hash") or _sha256_text(_canonical_json(context))
        submitter = None
        if args.get("submitter_id"):
            submitter = sql.one(f"SELECT * FROM signature.submitters WHERE submitter_id={_q(args.get('submitter_id'))}", user=_user())
        submitter_status = _completion_status_for_submitter(submitter)
        approval = sql.statement_one(f"""
          INSERT INTO signature.approvals (approval_id, request_id, submitter_id, source_type, source_id, approval_context, signature_text, signature_image_sha256, document_hash_sha256, approval_hash, ip_address, user_agent, signed_at, metadata)
          VALUES ({_q(approval_id)}, {_q(request_id)}, {_q(args.get('submitter_id'))}, {_q(context['source_type'])}, {_q(context['source_id'])}, {_j(context)}, {_q(args.get('signature_text'))}, {_q(args.get('signature_image_sha256'))}, {_q(context['document_hash_sha256'])}, {_q(approval_hash)}, {_q(args.get('ip_address'))}, {_q(args.get('user_agent'))}, COALESCE({_q(args.get('signed_at'))}::timestamptz, now()), {_j(args.get('metadata') or {})})
          ON CONFLICT (approval_id) DO UPDATE SET approval_context=EXCLUDED.approval_context, signature_text=EXCLUDED.signature_text, signature_image_sha256=EXCLUDED.signature_image_sha256, document_hash_sha256=EXCLUDED.document_hash_sha256, approval_hash=EXCLUDED.approval_hash, ip_address=EXCLUDED.ip_address, user_agent=EXCLUDED.user_agent, signed_at=EXCLUDED.signed_at, metadata=EXCLUDED.metadata
          RETURNING *
        """, user=_user())
        if args.get("submitter_id"):
            sql.psql(f"""
              UPDATE signature.submitters
              SET status={_q(submitter_status)},
                  signed_at=CASE WHEN {_q(submitter_status)}='signed' THEN COALESCE({_q(args.get('signed_at'))}::timestamptz, now()) ELSE signed_at END,
                  approved_at=CASE WHEN {_q(submitter_status)}='approved' THEN COALESCE({_q(args.get('signed_at'))}::timestamptz, now()) ELSE approved_at END,
                  ip_address=COALESCE({_q(args.get('ip_address'))}, ip_address),
                  user_agent=COALESCE({_q(args.get('user_agent'))}, user_agent),
                  updated_at=now()
              WHERE submitter_id={_q(args.get('submitter_id'))};
            """, user=_user())
        submitters = sql.rows(f"SELECT * FROM signature.submitters WHERE request_id={_q(request_id)} ORDER BY signing_order, created_at", user=_user())
        lifecycle = _derive_request_lifecycle(request, submitters)
        completed = lifecycle["completed"]
        sql.psql(f"""
          UPDATE signature.document_requests
          SET status={_q(lifecycle['status'])},
              approval_hash=CASE WHEN {str(completed).lower()} THEN COALESCE({_q(approval_hash)}, approval_hash) ELSE approval_hash END,
              document_hash_sha256=COALESCE({_q(context['document_hash_sha256'])}, document_hash_sha256),
              completed_at=CASE WHEN {str(completed).lower()} THEN COALESCE(completed_at, now()) ELSE completed_at END,
              last_activity_at=now(),
              updated_at=now()
          WHERE request_id={_q(request_id)};
        """, user=_user())
        event_type = "signed" if submitter_status == "signed" else "approved"
        event = _record_event(request_id, submitter_id=args.get("submitter_id"), event_type=event_type, actor_type=args.get("actor_type") or "customer", actor_ref=args.get("actor_ref"), payload={"approval_id": approval_id, "approval_hash": approval_hash, "context": context, "request_status": lifecycle["status"]}, ip_address=args.get("ip_address"), user_agent=args.get("user_agent"), metadata=args.get("metadata") or {})
        _record_event(request_id, submitter_id=args.get("submitter_id"), event_type="hash_created", actor_type="system", actor_ref="signature_core", payload={"approval_hash": approval_hash, "approval_id": approval_id}, metadata=args.get("metadata") or {})
        if completed:
            _record_event(request_id, submitter_id=args.get("submitter_id"), event_type="completed", actor_type="system", actor_ref="signature_core", payload={"approval_hash": approval_hash, "required_count": lifecycle["required_count"]}, metadata=args.get("metadata") or {})
        return _ok(approval=approval, approval_hash=approval_hash, event=event, request_status=lifecycle["status"], lifecycle=lifecycle)
    except Exception as exc:
        return _err(exc)


def _receipt_event_type(receipt_type: str, status: str) -> str:
    if status == "failed":
        return "delivery_failed"
    return {
        "invitation": "invitation_sent",
        "otp": "otp_sent",
        "reminder": "reminder_sent",
        "final_copy": "final_copy_sent",
    }.get(receipt_type, "delivery_receipt_recorded")


def _handle_delivery_receipt_record(args: dict, **_kwargs) -> str:
    try:
        request_id = str(args.get("request_id") or "").strip()
        receipt_type = str(args.get("receipt_type") or "").strip()
        channel = str(args.get("channel") or "").strip()
        status = str(args.get("status") or "").strip() or "sent"
        allowed_receipts = {"invitation", "otp", "reminder", "final_copy"}
        allowed_statuses = {"queued", "sent", "delivered", "failed", "bounced"}
        if not request_id:
            raise ValueError("request_id is required")
        if receipt_type not in allowed_receipts:
            raise ValueError(f"receipt_type must be one of {sorted(allowed_receipts)}")
        if not channel:
            raise ValueError("channel is required")
        if status not in allowed_statuses:
            raise ValueError(f"status must be one of {sorted(allowed_statuses)}")
        idempotency_key = args.get("idempotency_key") or _sha256_text(_canonical_json({
            "request_id": request_id,
            "submitter_id": args.get("submitter_id"),
            "receipt_type": receipt_type,
            "channel": channel,
            "recipient": args.get("recipient"),
            "provider_message_id": args.get("provider_message_id"),
        }))
        receipt = sql.statement_one(f"""
          INSERT INTO signature.delivery_receipts (request_id, submitter_id, receipt_type, channel, recipient, provider_message_id, status, error_message, delivered_at, idempotency_key, metadata, created_at, updated_at)
          VALUES ({_q(request_id)}, {_q(args.get('submitter_id'))}, {_q(receipt_type)}, {_q(channel)}, {_q(args.get('recipient'))}, {_q(args.get('provider_message_id'))}, {_q(status)}, {_q(args.get('error_message'))}, {_q(args.get('delivered_at'))}::timestamptz, {_q(idempotency_key)}, {_j(args.get('metadata') or {})}, now(), now())
          ON CONFLICT (idempotency_key) DO UPDATE SET status=EXCLUDED.status, error_message=EXCLUDED.error_message, delivered_at=COALESCE(EXCLUDED.delivered_at, signature.delivery_receipts.delivered_at), metadata=signature.delivery_receipts.metadata || EXCLUDED.metadata, updated_at=now()
          RETURNING *
        """, user=_user())
        event = _record_event(
            request_id,
            submitter_id=args.get("submitter_id"),
            event_type=_receipt_event_type(receipt_type, status),
            actor_type=args.get("actor_type") or "system",
            actor_ref=args.get("actor_ref") or "signature_core",
            payload={
                "delivery_receipt_id": (receipt or {}).get("delivery_receipt_id"),
                "receipt_type": receipt_type,
                "channel": channel,
                "recipient": args.get("recipient"),
                "provider_message_id": args.get("provider_message_id"),
                "status": status,
                "error_message": args.get("error_message"),
                "idempotency_key": idempotency_key,
            },
            metadata=args.get("metadata") or {},
        )
        return _ok(receipt=receipt, event=event)
    except Exception as exc:
        return _err(exc)


def _handle_reminder_policy_upsert(args: dict, **_kwargs) -> str:
    try:
        request_id = str(args.get("request_id") or "").strip()
        cadence = str(args.get("cadence") or "").strip()
        max_attempts = int(args.get("max_attempts") or 0)
        if not request_id:
            raise ValueError("request_id is required")
        if not cadence:
            raise ValueError("cadence is required")
        if not args.get("next_due_at"):
            raise ValueError("next_due_at is required")
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        policy_id = args.get("reminder_policy_id") or _slug("signature-reminder-policy", request_id)
        policy = sql.statement_one(f"""
          INSERT INTO signature.reminder_policies (reminder_policy_id, request_id, cadence, next_due_at, max_attempts, escalation_settings, enabled, metadata, created_at, updated_at)
          VALUES ({_q(policy_id)}, {_q(request_id)}, {_q(cadence)}, {_q(args.get('next_due_at'))}::timestamptz, {max_attempts}, {_j(args.get('escalation_settings') or {})}, {str(bool(args.get('enabled', True))).lower()}, {_j(args.get('metadata') or {})}, now(), now())
          ON CONFLICT (request_id) DO UPDATE SET cadence=EXCLUDED.cadence, next_due_at=EXCLUDED.next_due_at, max_attempts=EXCLUDED.max_attempts, escalation_settings=EXCLUDED.escalation_settings, enabled=EXCLUDED.enabled, metadata=signature.reminder_policies.metadata || EXCLUDED.metadata, updated_at=now()
          RETURNING *
        """, user=_user())
        event = _record_event(request_id, event_type="reminder_policy_updated", actor_type=args.get("actor_type") or "agent", actor_ref=args.get("actor_ref") or "agent", payload={"reminder_policy_id": policy_id, "cadence": cadence, "next_due_at": args.get("next_due_at"), "max_attempts": max_attempts, "escalation_settings": args.get("escalation_settings") or {}}, metadata=args.get("metadata") or {})
        return _ok(policy=policy, event=event)
    except Exception as exc:
        return _err(exc)


def _handle_reminder_attempt_record(args: dict, **_kwargs) -> str:
    try:
        request_id = str(args.get("request_id") or "").strip()
        channel = str(args.get("channel") or "").strip()
        status = str(args.get("status") or "").strip() or "sent"
        if not request_id:
            raise ValueError("request_id is required")
        if not channel:
            raise ValueError("channel is required")
        if status not in {"queued", "sent", "delivered", "failed", "bounced"}:
            raise ValueError("status must be queued, sent, delivered, failed, or bounced")
        policy = sql.one(f"SELECT * FROM signature.reminder_policies WHERE request_id={_q(request_id)}", user=_user()) or {}
        idempotency_key = args.get("idempotency_key") or _sha256_text(_canonical_json({
            "request_id": request_id,
            "submitter_id": args.get("submitter_id"),
            "channel": channel,
            "recipient": args.get("recipient"),
            "provider_message_id": args.get("provider_message_id"),
            "scheduled_for": args.get("scheduled_for") or args.get("next_due_at"),
        }))
        attempt = sql.statement_one(f"""
          INSERT INTO signature.reminder_attempts (reminder_policy_id, request_id, submitter_id, channel, recipient, provider_message_id, status, error_message, scheduled_for, attempted_at, idempotency_key, metadata, created_at, updated_at)
          VALUES ({_q(args.get('reminder_policy_id') or policy.get('reminder_policy_id'))}, {_q(request_id)}, {_q(args.get('submitter_id'))}, {_q(channel)}, {_q(args.get('recipient'))}, {_q(args.get('provider_message_id'))}, {_q(status)}, {_q(args.get('error_message'))}, {_q(args.get('scheduled_for'))}::timestamptz, COALESCE({_q(args.get('attempted_at'))}::timestamptz, now()), {_q(idempotency_key)}, {_j(args.get('metadata') or {})}, now(), now())
          ON CONFLICT (idempotency_key) DO UPDATE SET status=EXCLUDED.status, error_message=EXCLUDED.error_message, provider_message_id=COALESCE(EXCLUDED.provider_message_id, signature.reminder_attempts.provider_message_id), metadata=signature.reminder_attempts.metadata || EXCLUDED.metadata, updated_at=now()
          RETURNING *
        """, user=_user())
        policy_update = None
        if args.get("next_due_at"):
            policy_update = sql.statement_one(f"""
              UPDATE signature.reminder_policies
              SET next_due_at={_q(args.get('next_due_at'))}::timestamptz, updated_at=now()
              WHERE request_id={_q(request_id)}
              RETURNING *
            """, user=_user())
        receipt = json.loads(_handle_delivery_receipt_record({
            "request_id": request_id,
            "submitter_id": args.get("submitter_id"),
            "receipt_type": "reminder",
            "channel": channel,
            "recipient": args.get("recipient"),
            "provider_message_id": args.get("provider_message_id"),
            "status": status,
            "error_message": args.get("error_message"),
            "idempotency_key": f"receipt:{idempotency_key}",
            "metadata": {"reminder_attempt_id": (attempt or {}).get("reminder_attempt_id"), **(args.get("metadata") or {})},
            "actor_type": args.get("actor_type") or "system",
            "actor_ref": args.get("actor_ref") or "signature_core",
        }))
        return _ok(attempt=attempt, policy=policy_update, receipt=receipt.get("receipt"))
    except Exception as exc:
        return _err(exc)


def _parse_dt(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    parsed = datetime.fromisoformat(text)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _next_due_for_cadence(current_due: Any, cadence: str) -> str:
    base = _parse_dt(current_due) or datetime.now(timezone.utc)
    normalized = (cadence or "daily").strip().lower()
    if normalized in {"daily", "1d", "24h", "every_day"}:
        delta = timedelta(days=1)
    elif normalized in {"weekly", "7d"}:
        delta = timedelta(days=7)
    else:
        delta = timedelta(days=1)
    return _iso(base + delta)


def _recipient_channel(row: dict[str, Any], default_channel: str | None = None) -> tuple[str, str | None]:
    if default_channel:
        recipient = row.get("email") if default_channel == "email" else row.get("phone")
        return default_channel, recipient or row.get("email") or row.get("phone")
    if row.get("email"):
        return "email", row.get("email")
    if row.get("phone"):
        return "sms", row.get("phone")
    return "in_app", row.get("submitter_id")


def _due_followup_rows(now_sql: str, limit: int) -> list[dict[str, Any]]:
    return sql.rows(f"""
      SELECT
        p.reminder_policy_id,
        p.request_id,
        p.cadence,
        p.next_due_at,
        p.max_attempts,
        p.escalation_settings,
        r.status AS request_status,
        r.expires_at,
        s.submitter_id,
        s.status AS submitter_status,
        s.email,
        s.phone,
        s.name,
        COALESCE(attempts.attempt_count, 0) AS attempt_count,
        COALESCE(attempts.failed_attempts, 0) AS failed_attempts
      FROM signature.reminder_policies p
      JOIN signature.document_requests r ON r.request_id = p.request_id
      JOIN signature.submitters s ON s.request_id = p.request_id
      LEFT JOIN LATERAL (
        SELECT
          count(*) AS attempt_count,
          count(*) FILTER (WHERE status IN ('failed','bounced')) AS failed_attempts
        FROM signature.reminder_attempts ra
        WHERE ra.request_id = p.request_id
          AND (ra.submitter_id = s.submitter_id OR ra.submitter_id IS NULL)
      ) attempts ON true
      WHERE p.enabled = true
        AND p.next_due_at <= {now_sql}::timestamptz
        AND r.status IN ('sent','viewed','partially_signed')
        AND (r.expires_at IS NULL OR r.expires_at > {now_sql}::timestamptz)
        AND s.status IN ('pending','sent','viewed')
        AND COALESCE(attempts.attempt_count, 0) < p.max_attempts
      ORDER BY p.next_due_at ASC, r.created_at ASC, s.signing_order ASC
      LIMIT {limit}
    """, user=_user())


def _escalation_reasons(row: dict[str, Any], now: datetime, delivery_status: str) -> list[str]:
    settings = row.get("escalation_settings") or {}
    near_expiry_hours = int(settings.get("near_expiry_hours") or 0)
    owner_after_failures = int(settings.get("owner_after_failures") or settings.get("owner_after_attempts") or 0)
    failed_attempts = int(row.get("failed_attempts") or 0)
    if delivery_status in {"failed", "bounced"}:
        failed_attempts += 1
    reasons: list[str] = []
    expires_at = _parse_dt(row.get("expires_at"))
    if near_expiry_hours > 0 and expires_at and expires_at <= now + timedelta(hours=near_expiry_hours):
        reasons.append("near_expiry")
    if owner_after_failures > 0 and failed_attempts >= owner_after_failures:
        reasons.append("repeated_delivery_failures")
    return reasons


def _handle_followup_due(args: dict, **_kwargs) -> str:
    try:
        now = _parse_dt(args.get("now")) or datetime.now(timezone.utc)
        now_text = _iso(now)
        now_sql = _q(now_text)
        limit = max(1, min(int(args.get("limit") or 50), 500))
        delivery_status = str(args.get("delivery_status") or "queued").strip()
        if delivery_status not in {"queued", "sent", "delivered", "failed", "bounced"}:
            raise ValueError("delivery_status must be queued, sent, delivered, failed, or bounced")
        rows = _due_followup_rows(now_sql, limit)
        reminders: list[dict[str, Any]] = []
        policy_updates: list[dict[str, Any]] = []
        escalations: list[dict[str, Any]] = []
        touched_policies: set[str] = set()
        for row in rows:
            channel, recipient = _recipient_channel(row, args.get("channel"))
            scheduled_for = row.get("next_due_at") or now_text
            next_due_at = _next_due_for_cadence(scheduled_for, row.get("cadence") or "daily")
            idempotency_key = _sha256_text(_canonical_json({
                "worker": "signature_followup_due",
                "request_id": row.get("request_id"),
                "submitter_id": row.get("submitter_id"),
                "reminder_policy_id": row.get("reminder_policy_id"),
                "scheduled_for": str(scheduled_for),
            }))
            attempt_result = json.loads(_handle_reminder_attempt_record({
                "request_id": row.get("request_id"),
                "submitter_id": row.get("submitter_id"),
                "reminder_policy_id": row.get("reminder_policy_id"),
                "channel": channel,
                "recipient": recipient,
                "status": delivery_status,
                "error_message": args.get("error_message"),
                "scheduled_for": scheduled_for,
                "attempted_at": now_text,
                "idempotency_key": idempotency_key,
                "metadata": {"worker": "signature_followup_due", "policy_next_due_at": str(scheduled_for)},
                "actor_type": "system",
                "actor_ref": "signature_followup_worker",
            }))
            if attempt_result.get("error"):
                raise ValueError(attempt_result["error"])
            reminders.append({
                "request_id": row.get("request_id"),
                "submitter_id": row.get("submitter_id"),
                "channel": channel,
                "recipient": recipient,
                "status": delivery_status,
                "scheduled_for": str(scheduled_for),
                "next_due_at": next_due_at,
                "attempt": attempt_result.get("attempt"),
            })
            policy_id = str(row.get("reminder_policy_id") or "")
            if policy_id and policy_id not in touched_policies:
                updated = sql.statement_one(f"""
                  UPDATE signature.reminder_policies
                  SET next_due_at={_q(next_due_at)}::timestamptz, updated_at=now()
                  WHERE reminder_policy_id={_q(policy_id)}
                  RETURNING *
                """, user=_user())
                policy_updates.append(updated or {"reminder_policy_id": policy_id, "next_due_at": next_due_at})
                touched_policies.add(policy_id)
            reasons = _escalation_reasons(row, now, delivery_status)
            if reasons:
                event = _record_event(
                    str(row.get("request_id")),
                    submitter_id=row.get("submitter_id"),
                    event_type="owner_escalated",
                    actor_type="system",
                    actor_ref="signature_followup_worker",
                    payload={
                        "reasons": reasons,
                        "reminder_policy_id": row.get("reminder_policy_id"),
                        "failed_attempts": row.get("failed_attempts"),
                        "expires_at": row.get("expires_at"),
                    },
                    metadata={"worker": "signature_followup_due"},
                )
                escalations.append({"request_id": row.get("request_id"), "submitter_id": row.get("submitter_id"), "reasons": reasons, "event": event})
        return _ok(processed=len(reminders), reminders=reminders, policy_updates=policy_updates, escalations=escalations)
    except Exception as exc:
        return _err(exc)


def _artifact_id(request_id: str, kind: str, sha256: str | None) -> str:
    return _slug("signature-attachment", f"{request_id}-{kind}-{(sha256 or '')[:16] or 'artifact'}")


def _require_artifact(name: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    if not value.get("sha256") or not value.get("storage_path"):
        raise ValueError(f"{name}.sha256 and {name}.storage_path are required")
    return value


def _insert_attachment(request_id: str, artifact: dict[str, Any], *, kind: str, metadata: dict[str, Any]) -> dict[str, Any] | None:
    attachment_id = artifact.get("attachment_id") or _artifact_id(request_id, kind, artifact.get("sha256"))
    return sql.statement_one(f"""
      INSERT INTO signature.attachments (attachment_id, request_id, submitter_id, kind, filename, mime_type, storage_path, public_url, byte_size, sha256, width, height, metadata)
      VALUES ({_q(attachment_id)}, {_q(request_id)}, {_q(artifact.get('submitter_id'))}, {_q(kind)}, {_q(artifact.get('filename'))}, {_q(artifact.get('mime_type') or 'application/pdf')}, {_q(artifact.get('storage_path'))}, {_q(artifact.get('public_url'))}, {_q(artifact.get('byte_size'))}, {_q(artifact.get('sha256'))}, {_q(artifact.get('width'))}, {_q(artifact.get('height'))}, {_j({**(artifact.get('metadata') or {}), **metadata})})
      ON CONFLICT (attachment_id) DO UPDATE SET filename=EXCLUDED.filename, mime_type=EXCLUDED.mime_type, storage_path=EXCLUDED.storage_path, public_url=EXCLUDED.public_url, byte_size=EXCLUDED.byte_size, sha256=EXCLUDED.sha256, width=EXCLUDED.width, height=EXCLUDED.height, metadata=EXCLUDED.metadata
      RETURNING attachment_id, kind, filename, storage_path, public_url, byte_size, sha256, metadata
    """, user=_user())


def _handle_completed_pdf_record(args: dict, **_kwargs) -> str:
    try:
        request_id = str(args.get("request_id") or "").strip()
        if not request_id:
            raise ValueError("request_id is required")
        request = sql.one(f"SELECT * FROM signature.document_requests WHERE request_id={_q(request_id)}", user=_user())
        if not request:
            raise ValueError("request not found")
        completed_pdf = _require_artifact("completed_pdf", args.get("completed_pdf"))
        audit_pdf = _require_artifact("audit_pdf", args.get("audit_pdf"))
        evidence = {
            "original_sha256": args.get("original_sha256"),
            "final_sha256": args.get("final_sha256") or completed_pdf.get("sha256"),
            "approval_hashes": args.get("approval_hashes") or [],
            "event_chain_summary": args.get("event_chain_summary") or [],
            "visual_qa_evidence": args.get("visual_qa_evidence") or {},
        }
        completed = _insert_attachment(request_id, completed_pdf, kind="completed_pdf", metadata=evidence)
        audit = _insert_attachment(request_id, audit_pdf, kind="audit_pdf", metadata=evidence)
        sql.psql(f"""
          UPDATE signature.document_requests
          SET completed_document_url=COALESCE({_q(completed_pdf.get('public_url') or completed_pdf.get('storage_path'))}, completed_document_url),
              audit_url=COALESCE({_q(audit_pdf.get('public_url') or audit_pdf.get('storage_path'))}, audit_url),
              document_hash_sha256=COALESCE({_q(args.get('original_sha256'))}, document_hash_sha256),
              metadata=metadata || {_j({'completed_pdf_sha256': completed_pdf.get('sha256'), 'audit_pdf_sha256': audit_pdf.get('sha256'), 'visual_qa_evidence': evidence['visual_qa_evidence']})},
              updated_at=now()
          WHERE request_id={_q(request_id)};
        """, user=_user())
        event = _record_event(request_id, event_type="completed", actor_type="system", actor_ref="signature_core", payload={"completed_pdf_sha256": completed_pdf.get("sha256"), "audit_pdf_sha256": audit_pdf.get("sha256"), "approval_hashes": evidence["approval_hashes"], "visual_qa_evidence": evidence["visual_qa_evidence"]}, metadata=evidence)
        return _ok(completed_pdf=completed, audit_pdf=audit, event=event)

    except Exception as exc:
        return _err(exc)


def _submitter_channel(submitter: dict[str, Any], delivery_result: dict[str, Any] | None) -> str:
    if delivery_result and delivery_result.get("channel"):
        return str(delivery_result["channel"])
    metadata = submitter.get("metadata") or {}
    if metadata.get("final_copy_channel"):
        return str(metadata["final_copy_channel"])
    if metadata.get("delivery_channel"):
        return str(metadata["delivery_channel"])
    if submitter.get("email"):
        return "email"
    if submitter.get("phone"):
        return "sms"
    return "manual"


def _submitter_recipient(submitter: dict[str, Any], channel: str) -> str | None:
    if channel in {"email", "mail"}:
        return submitter.get("email") or submitter.get("phone")
    if channel in {"sms", "whatsapp", "phone"}:
        return submitter.get("phone") or submitter.get("email")
    return submitter.get("email") or submitter.get("phone") or submitter.get("name")


def _normalise_delivery_results(value: Any) -> dict[str, dict[str, Any]]:
    if not value:
        return {}
    if isinstance(value, dict):
        items = value.values()
    elif isinstance(value, list):
        items = value
    else:
        raise ValueError("delivery_results must be a list or object")
    results: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict) or not item.get("submitter_id"):
            raise ValueError("each delivery result must include submitter_id")
        results[str(item["submitter_id"])] = item
    return results


def _final_copy_validation_summary(request: dict[str, Any], args: dict[str, Any]) -> dict[str, Any]:
    metadata = request.get("metadata") or {}
    final_sha256 = args.get("final_sha256") or args.get("completed_pdf_sha256") or metadata.get("completed_pdf_sha256")
    if not final_sha256:
        raise ValueError("final_sha256 or request metadata.completed_pdf_sha256 is required")
    final_document_url = args.get("completed_pdf_url") or request.get("completed_document_url")
    if not final_document_url:
        raise ValueError("completed_pdf_url or request.completed_document_url is required")
    return {
        "final_document_url": final_document_url,
        "final_document_sha256": final_sha256,
        "audit_url": args.get("audit_pdf_url") or request.get("audit_url"),
        "audit_pdf_sha256": args.get("audit_pdf_sha256") or metadata.get("audit_pdf_sha256"),
        "original_document_sha256": args.get("original_sha256") or request.get("document_hash_sha256"),
        "approval_hashes": args.get("approval_hashes") or metadata.get("approval_hashes") or [],
        "event_chain_summary": args.get("event_chain_summary") or metadata.get("event_chain_summary") or [],
        "certificate_summary": args.get("certificate_summary") or metadata.get("certificate_summary") or {},
    }


def _insert_delivery_receipt(
    request_id: str,
    submitter: dict[str, Any],
    *,
    channel: str,
    recipient: str | None,
    status: str,
    provider_message_id: str | None,
    error: str | None,
    payload: dict[str, Any],
    metadata: dict[str, Any],
) -> dict[str, Any] | None:
    idempotency_key = _sha256_text(_canonical_json({
        "request_id": request_id,
        "submitter_id": submitter.get("submitter_id"),
        "receipt_type": "final_copy",
        "channel": channel,
        "recipient": recipient,
        "provider_message_id": provider_message_id,
        "payload": payload,
    }))
    merged_metadata = {"payload": payload, **metadata}
    return sql.statement_one(f"""
      INSERT INTO signature.delivery_receipts (request_id, submitter_id, receipt_type, channel, recipient, provider_message_id, status, error_message, delivered_at, idempotency_key, metadata, created_at, updated_at)
      VALUES ({_q(request_id)}, {_q(submitter.get('submitter_id'))}, 'final_copy', {_q(channel)}, {_q(recipient)}, {_q(provider_message_id)}, {_q(status)}, {_q(error)}, CASE WHEN {_q(status)} IN ('sent','delivered') THEN now() ELSE NULL END, {_q(idempotency_key)}, {_j(merged_metadata)}, now(), now())
      ON CONFLICT (idempotency_key) DO UPDATE SET status=EXCLUDED.status, error_message=EXCLUDED.error_message, delivered_at=COALESCE(EXCLUDED.delivered_at, signature.delivery_receipts.delivered_at), metadata=signature.delivery_receipts.metadata || EXCLUDED.metadata, updated_at=now()
      RETURNING *
    """, user=_user())


def _handle_final_copies_send(args: dict, **_kwargs) -> str:
    try:
        request_id = str(args.get("request_id") or "").strip()
        if not request_id:
            raise ValueError("request_id is required")
        request = sql.one(f"SELECT * FROM signature.document_requests WHERE request_id={_q(request_id)}", user=_user())
        if not request:
            raise ValueError("request not found")
        if request.get("status") != "completed" and not args.get("allow_non_completed"):
            raise ValueError("final copies can only be sent after the request is completed")
        validation_summary = _final_copy_validation_summary(request, args)
        submitters = sql.rows(f"SELECT * FROM signature.submitters WHERE request_id={_q(request_id)} ORDER BY signing_order, created_at", user=_user())
        signers = [sub for sub in submitters if sub.get("role") in {"signer", "approver"}]
        if not signers:
            raise ValueError("request has no signer/approver submitters")
        result_by_submitter = _normalise_delivery_results(args.get("delivery_results"))
        deliveries = []
        retry_actions = []
        for submitter in signers:
            submitter_id = str(submitter.get("submitter_id"))
            delivery_result = result_by_submitter.get(submitter_id, {})
            channel = _submitter_channel(submitter, delivery_result)
            recipient = delivery_result.get("recipient") or _submitter_recipient(submitter, channel)
            status = str(delivery_result.get("status") or args.get("default_status") or "queued")
            error = delivery_result.get("error")
            provider_message_id = delivery_result.get("provider_message_id") or delivery_result.get("message_id")
            payload = {
                "subject": args.get("subject") or "Final signed document and SHA-256 validation",
                "message": args.get("message") or "Your final signed document is ready. Validate it with the included SHA-256 summary.",
                "validation_summary": validation_summary,
            }
            receipt = _insert_delivery_receipt(
                request_id,
                submitter,
                channel=channel,
                recipient=recipient,
                status=status,
                provider_message_id=provider_message_id,
                error=error,
                payload=payload,
                metadata={"delivery_result": delivery_result, "retry_policy": args.get("retry_policy") or {}},
            )
            event_type = "final_copy_failed" if status == "failed" else "final_copy_sent"
            _record_event(
                request_id,
                submitter_id=submitter_id,
                event_type=event_type,
                actor_type="system",
                actor_ref="signature_core",
                payload={"channel": channel, "recipient": recipient, "status": status, "error": error, "validation_summary": validation_summary},
                metadata={"delivery_type": "final_copy", "provider_message_id": provider_message_id},
            )
            delivery = {
                "submitter_id": submitter_id,
                "channel": channel,
                "recipient": recipient,
                "status": status,
                "provider_message_id": provider_message_id,
                "error": error,
                "validation_summary": validation_summary,
                "receipt": receipt,
            }
            deliveries.append(delivery)
            if status == "failed":
                retry_action = {"submitter_id": submitter_id, "channel": channel, "recipient": recipient, "reason": error or "delivery failed"}
                retry_actions.append(retry_action)
        if retry_actions:
            _record_event(
                request_id,
                event_type="owner_escalation",
                actor_type="system",
                actor_ref="signature_core",
                payload={"reason": "final_copy_delivery_failed", "retry_actions": retry_actions, "owner_channel": args.get("owner_escalation_channel")},
                metadata={"delivery_type": "final_copy"},
            )
        return _ok(deliveries=deliveries, retry_actions=retry_actions, validation_summary=validation_summary)
    except Exception as exc:
        return _err(exc)


def _handle_dashboard_metrics(args: dict, **_kwargs) -> str:
    try:
        limit = max(1, min(int(args.get("limit") or 25), 100))
        expiring_days = max(1, min(int(args.get("expiring_days") or 7), 90))
        summary = sql.one(f"""
          SELECT
            count(*) FILTER (WHERE r.status IN ('sent','viewed','partially_signed')) AS active,
            count(*) FILTER (WHERE s.status IN ('pending','sent','viewed','started')) AS pending,
            count(DISTINCT r.request_id) FILTER (WHERE r.expires_at IS NOT NULL AND r.expires_at <= now() + interval '{expiring_days} days' AND r.status NOT IN ('completed','declined','expired','cancelled')) AS expiring,
            count(DISTINCT r.request_id) FILTER (WHERE r.status='completed' AND r.completed_at >= date_trunc('month', now())) AS completed,
            count(DISTINCT r.request_id) FILTER (WHERE r.status='declined') AS declined,
            (SELECT count(*) FROM signature.reminder_attempts) AS reminders,
            (SELECT count(*) FROM signature.delivery_receipts WHERE receipt_type='final_copy') AS copy_receipts,
            count(DISTINCT r.request_id) FILTER (WHERE COALESCE(r.metadata->>'completed_pdf_sha256', '') <> '' OR COALESCE(r.approval_hash, '') <> '' OR EXISTS (SELECT 1 FROM signature.attachments a WHERE a.request_id=r.request_id AND COALESCE(a.sha256, '') <> '')) AS hash_verified,
            count(DISTINCT r.request_id) FILTER (WHERE r.status='completed' AND COALESCE(r.metadata->>'completed_pdf_sha256', '') = '' AND COALESCE(r.approval_hash, '') = '' AND NOT EXISTS (SELECT 1 FROM signature.attachments a WHERE a.request_id=r.request_id AND COALESCE(a.sha256, '') <> '')) AS hash_missing
          FROM signature.document_requests r
          LEFT JOIN signature.submitters s ON s.request_id = r.request_id
        """, user=_user()) or {}
        processes = sql.rows(f"""
          SELECT
            r.request_id,
            r.title,
            r.status,
            r.expires_at,
            count(s.submitter_id) FILTER (WHERE s.status IN ('pending','sent','viewed','started')) AS pending_signers,
            count(ra.reminder_attempt_id) AS reminders,
            count(dr.delivery_receipt_id) FILTER (WHERE dr.receipt_type='final_copy') AS copy_receipts,
            CASE
              WHEN COALESCE(r.metadata->>'completed_pdf_sha256', '') <> '' OR COALESCE(r.approval_hash, '') <> '' OR count(a.attachment_id) FILTER (WHERE COALESCE(a.sha256, '') <> '') > 0 THEN 'verified'
              WHEN r.status='completed' THEN 'missing'
              ELSE 'pending'
            END AS hash_status
          FROM signature.document_requests r
          LEFT JOIN signature.submitters s ON s.request_id = r.request_id
          LEFT JOIN signature.reminder_attempts ra ON ra.request_id = r.request_id
          LEFT JOIN signature.delivery_receipts dr ON dr.request_id = r.request_id
          LEFT JOIN signature.attachments a ON a.request_id = r.request_id
          GROUP BY r.request_id, r.title, r.status, r.expires_at, r.metadata, r.approval_hash
          ORDER BY r.updated_at DESC NULLS LAST, r.created_at DESC
          LIMIT {limit}
        """, user=_user())
        hash_missing = int(summary.get("hash_missing") or 0)
        summary = {
            "active": int(summary.get("active") or 0),
            "pending": int(summary.get("pending") or 0),
            "expiring": int(summary.get("expiring") or 0),
            "completed": int(summary.get("completed") or 0),
            "declined": int(summary.get("declined") or 0),
            "reminders": int(summary.get("reminders") or 0),
            "copy_receipts": int(summary.get("copy_receipts") or 0),
            "hash_verified": int(summary.get("hash_verified") or 0),
            "hash_missing": hash_missing,
            "hash_status": "attention_required" if hash_missing else "verified",
        }
        return _ok(summary=summary, processes=processes)
    except Exception as exc:
        return _err(exc)


def _schema(name: str, description: str, props: dict, required: list[str] | None = None) -> dict:
    return {"type": "function", "function": {"name": name, "description": description, "parameters": {"type": "object", "properties": props, "required": required or []}}}


def _meta_props() -> dict[str, Any]:
    return {"metadata": {"type": "object", "description": SIGNATURE_METADATA_DESCRIPTION}}


registry.register(name="signature_status", toolset="signature", schema=_schema("signature_status", "Return Signature Core row counts and DB backend.", {}), handler=_handle_signature_status, check_fn=_check_signature, emoji="✍️")
registry.register(name="signature_template_upsert", toolset="signature", schema=_schema("signature_template_upsert", "Create or update a reusable e-signature template with fields/submitter roles.", {"template_id": {"type": "string"}, "name": {"type": "string"}, "document_url": {"type": "string"}, "fields": {"type": "array", "items": {"type": "object"}}, "submitters": {"type": "array", "items": {"type": "object"}}, "preferences": {"type": "object"}, **_meta_props()}, ["name"]), handler=_handle_template_upsert, check_fn=_check_signature, emoji="✍️")
registry.register(name="signature_request_create", toolset="signature", schema=_schema("signature_request_create", "Create a document/signature request with opaque signer links and field snapshots.", {"request_id": {"type": "string"}, "template_id": {"type": "string"}, "source_type": {"type": "string"}, "source_id": {"type": "string"}, "title": {"type": "string"}, "status": {"type": "string"}, "document_url": {"type": "string"}, "fields": {"type": "array", "items": {"type": "object"}}, "submitters": {"type": "array", "items": {"type": "object"}}, "preferences": {"type": "object"}, "expires_at": {"type": "string"}, "actor_ref": {"type": "string"}, **_meta_props()}, ["title", "submitters"]), handler=_handle_request_create, check_fn=_check_signature, emoji="✍️")
registry.register(name="signature_request_get", toolset="signature", schema=_schema("signature_request_get", "Read a signature request with submitters, audit events, and approvals.", {"request_id": {"type": "string"}}, ["request_id"]), handler=_handle_request_get, check_fn=_check_signature, emoji="✍️")
registry.register(name="signature_event_record", toolset="signature", schema=_schema("signature_event_record", "Append an audit event to a signature request with a chained event hash.", {"request_id": {"type": "string"}, "submitter_id": {"type": "string"}, "event_type": {"type": "string"}, "actor_type": {"type": "string"}, "actor_ref": {"type": "string"}, "ip_address": {"type": "string"}, "user_agent": {"type": "string"}, "event_payload": {"type": "object"}, **_meta_props()}, ["request_id", "event_type"]), handler=_handle_event_record, check_fn=_check_signature, emoji="✍️")
registry.register(name="signature_approval_hash_create", toolset="signature", schema=_schema("signature_approval_hash_create", "Create a canonical approval record and SHA-256 approval hash for a signed/approved document.", {"approval_id": {"type": "string"}, "request_id": {"type": "string"}, "submitter_id": {"type": "string"}, "source_type": {"type": "string"}, "source_id": {"type": "string"}, "signature_text": {"type": "string"}, "signature_image_sha256": {"type": "string"}, "document_hash_sha256": {"type": "string"}, "approval_hash": {"type": "string"}, "ip_address": {"type": "string"}, "user_agent": {"type": "string"}, "signed_at": {"type": "string"}, "actor_type": {"type": "string"}, "actor_ref": {"type": "string"}, **_meta_props()}, ["request_id"]), handler=_handle_approval_hash_create, check_fn=_check_signature, emoji="✍️")
registry.register(name="signature_delivery_receipt_record", toolset="signature", schema=_schema("signature_delivery_receipt_record", "Record an idempotent invitation, OTP, reminder, or final-copy delivery receipt with provider status/failure details.", {"request_id": {"type": "string"}, "submitter_id": {"type": "string"}, "receipt_type": {"type": "string", "enum": ["invitation", "otp", "reminder", "final_copy"]}, "channel": {"type": "string"}, "recipient": {"type": "string"}, "provider_message_id": {"type": "string"}, "status": {"type": "string", "enum": ["queued", "sent", "delivered", "failed", "bounced"]}, "error_message": {"type": "string"}, "delivered_at": {"type": "string"}, "idempotency_key": {"type": "string"}, "actor_type": {"type": "string"}, "actor_ref": {"type": "string"}, **_meta_props()}, ["request_id", "receipt_type", "channel"]), handler=_handle_delivery_receipt_record, check_fn=_check_signature, emoji="✍️")
registry.register(name="signature_reminder_policy_upsert", toolset="signature", schema=_schema("signature_reminder_policy_upsert", "Create/update per-request reminder policy with cadence, next due timestamp, max attempts, and escalation settings.", {"reminder_policy_id": {"type": "string"}, "request_id": {"type": "string"}, "cadence": {"type": "string"}, "next_due_at": {"type": "string"}, "max_attempts": {"type": "integer"}, "escalation_settings": {"type": "object"}, "enabled": {"type": "boolean"}, "actor_type": {"type": "string"}, "actor_ref": {"type": "string"}, **_meta_props()}, ["request_id", "cadence", "next_due_at", "max_attempts"]), handler=_handle_reminder_policy_upsert, check_fn=_check_signature, emoji="✍️")
registry.register(name="signature_reminder_attempt_record", toolset="signature", schema=_schema("signature_reminder_attempt_record", "Record an idempotent reminder attempt, failure details, optional next_due_at update, and matching reminder delivery receipt.", {"request_id": {"type": "string"}, "submitter_id": {"type": "string"}, "reminder_policy_id": {"type": "string"}, "channel": {"type": "string"}, "recipient": {"type": "string"}, "provider_message_id": {"type": "string"}, "status": {"type": "string", "enum": ["queued", "sent", "delivered", "failed", "bounced"]}, "error_message": {"type": "string"}, "scheduled_for": {"type": "string"}, "attempted_at": {"type": "string"}, "next_due_at": {"type": "string"}, "idempotency_key": {"type": "string"}, "actor_type": {"type": "string"}, "actor_ref": {"type": "string"}, **_meta_props()}, ["request_id", "channel"]), handler=_handle_reminder_attempt_record, check_fn=_check_signature, emoji="✍️")
registry.register(name="signature_followup_due", toolset="signature", schema=_schema("signature_followup_due", "Run the Signature Core daily follow-up worker: find due pending signers, queue one reminder per policy window, advance next_due_at, and record owner escalations for near-expiry or repeated failures.", {"now": {"type": "string"}, "limit": {"type": "integer"}, "channel": {"type": "string", "enum": ["email", "sms", "in_app"]}, "delivery_status": {"type": "string", "enum": ["queued", "sent", "delivered", "failed", "bounced"]}, "error_message": {"type": "string"}}, []), handler=_handle_followup_due, check_fn=_check_signature, emoji="✍️")
registry.register(name="signature_completed_pdf_record", toolset="signature", schema=_schema("signature_completed_pdf_record", "Store completed PDF and audit PDF attachment metadata with SHA-256 hashes and visual QA evidence.", {"request_id": {"type": "string"}, "completed_pdf": {"type": "object"}, "audit_pdf": {"type": "object"}, "original_sha256": {"type": "string"}, "final_sha256": {"type": "string"}, "approval_hashes": {"type": "array", "items": {"type": "string"}}, "event_chain_summary": {"type": "array", "items": {"type": "object"}}, "visual_qa_evidence": {"type": "object"}}, ["request_id", "completed_pdf", "audit_pdf"]), handler=_handle_completed_pdf_record, check_fn=_check_signature, emoji="✍️")
registry.register(name="signature_final_copies_send", toolset="signature", schema=_schema("signature_final_copies_send", "Record final signed-copy delivery to every signer/approver with final document link, SHA-256 validation summary, per-channel receipts, and retry/escalation actions for failures.", {"request_id": {"type": "string"}, "completed_pdf_url": {"type": "string"}, "completed_pdf_sha256": {"type": "string"}, "final_sha256": {"type": "string"}, "audit_pdf_url": {"type": "string"}, "audit_pdf_sha256": {"type": "string"}, "original_sha256": {"type": "string"}, "approval_hashes": {"type": "array", "items": {"type": "string"}}, "event_chain_summary": {"type": "array", "items": {"type": "object"}}, "certificate_summary": {"type": "object"}, "delivery_results": {"type": "array", "items": {"type": "object"}}, "default_status": {"type": "string"}, "retry_policy": {"type": "object"}, "owner_escalation_channel": {"type": "string"}, "allow_non_completed": {"type": "boolean"}, "subject": {"type": "string"}, "message": {"type": "string"}}, ["request_id"]), handler=_handle_final_copies_send, check_fn=_check_signature, emoji="✍️")
registry.register(name="signature_dashboard_metrics", toolset="signature", schema=_schema("signature_dashboard_metrics", "Return private Signature Core dashboard metrics: active, pending, expiring, completed, declined, reminders, final-copy receipts, and hash status.", {"limit": {"type": "integer"}, "expiring_days": {"type": "integer"}}, []), handler=_handle_dashboard_metrics, check_fn=_check_signature, emoji="✍️")

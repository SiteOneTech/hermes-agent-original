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
from datetime import datetime, timezone
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
            (SELECT count(*) FROM signature.attachments) AS attachments
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
          INSERT INTO signature.document_requests (request_id, template_id, source_type, source_id, title, status, document_url, fields_snapshot, submitters_snapshot, preferences, metadata, expires_at, created_at, updated_at)
          VALUES ({_q(request_id)}, {_q(args.get('template_id'))}, {_q(args.get('source_type'))}, {_q(args.get('source_id'))}, {_q(title)}, {_q(args.get('status') or 'draft')}, {_q(args.get('document_url') or (template or {}).get('document_url'))}, {_j(fields)}, {_j(template_submitters or submitters)}, {_j(args.get('preferences') or (template or {}).get('preferences') or {})}, {_j(args.get('metadata') or {})}, {_q(args.get('expires_at'))}::timestamptz, now(), now())
          ON CONFLICT (request_id) DO UPDATE SET template_id=EXCLUDED.template_id, source_type=EXCLUDED.source_type, source_id=EXCLUDED.source_id, title=EXCLUDED.title, status=EXCLUDED.status, document_url=EXCLUDED.document_url, fields_snapshot=EXCLUDED.fields_snapshot, submitters_snapshot=EXCLUDED.submitters_snapshot, preferences=EXCLUDED.preferences, metadata=EXCLUDED.metadata, expires_at=EXCLUDED.expires_at, updated_at=now()
          RETURNING *
        """, user=_user())
        sql.psql(f"DELETE FROM signature.submitters WHERE request_id={_q(request_id)};", user=_user())
        saved_submitters = []
        for idx, sub in enumerate(submitters, start=1):
            token = _token()
            slug = secrets.token_urlsafe(18)
            submitter_id = sub.get("submitter_id") or _slug("signature-submitter", f"{request_id}-{sub.get('email') or sub.get('name') or idx}")
            saved = sql.statement_one(f"""
              INSERT INTO signature.submitters (submitter_id, request_id, role, signing_order, name, email, phone, slug, token_hash_sha256, status, metadata)
              VALUES ({_q(submitter_id)}, {_q(request_id)}, {_q(sub.get('role') or 'signer')}, {int(sub.get('signing_order') or idx)}, {_q(sub.get('name'))}, {_q(sub.get('email'))}, {_q(sub.get('phone'))}, {_q(slug)}, {_q(_sha256_text(token))}, {_q(sub.get('status') or 'pending')}, {_j(sub.get('metadata') or {})})
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
        comments = sql.rows(f"SELECT * FROM signature.comments WHERE request_id={_q(request_id)} ORDER BY created_at, comment_id", user=_user())
        return _ok(request=request, submitters=submitters, events=events, approvals=approvals, comments=comments)
    except Exception as exc:
        return _err(exc)


SIGNATURE_ACTIONS = {
    "sign": "signed",
    "signed": "signed",
    "approve": "approved",
    "approved": "approved",
    "reject": "rejected",
    "rejected": "rejected",
    "decline": "rejected",
    "declined": "rejected",
    "comment": "commented",
    "commented": "commented",
}
OTP_REQUIRED_SIGNATURE_ACTIONS = {"signed", "approved", "rejected"}
CLOSED_REQUEST_STATUSES = {"completed", "declined", "expired", "cancelled"}
CLOSED_SUBMITTER_STATUSES = {"signed", "approved", "declined", "expired", "cancelled"}


def _normalize_signature_action(value: Any) -> str | None:
    return SIGNATURE_ACTIONS.get(str(value or "").strip().lower())


def _event_type_for_signature_action(action: str) -> str:
    return "declined" if action == "rejected" else action


def _status_for_signature_action(action: str) -> str:
    return "declined" if action == "rejected" else action


def _parse_dt(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _request_actionable(request: dict[str, Any]) -> bool:
    if str(request.get("status") or "").strip().lower() in CLOSED_REQUEST_STATUSES:
        return False
    expires_at = _parse_dt(request.get("expires_at"))
    return not (expires_at and expires_at <= datetime.now(timezone.utc))


def _recipient_target(submitter: dict[str, Any], actor_ref: Any = None) -> str | None:
    for key in ("email", "phone"):
        value = str(submitter.get(key) or "").strip().lower()
        if value:
            return value
    value = str(actor_ref or submitter.get("name") or "").strip().lower()
    return value or None


def _recipient_target_hash(submitter: dict[str, Any], actor_ref: Any = None) -> str | None:
    target = _recipient_target(submitter, actor_ref)
    return _sha256_text(target) if target else None


def _load_request_for_action(request_id: str) -> dict[str, Any]:
    request = sql.one(f"SELECT * FROM signature.document_requests WHERE request_id={_q(request_id)}", user=_user())
    if not request:
        raise ValueError("request_not_found")
    if not _request_actionable(request):
        raise ValueError("request_not_actionable")
    return request


def _require_recipient_otp(args: dict[str, Any], submitter: dict[str, Any] | None = None) -> None:
    if args.get("otp_verified") is not True or not str(args.get("otp_challenge_id") or "").strip():
        raise ValueError("otp_required")
    if submitter is not None:
        expected = _recipient_target_hash(submitter, args.get("actor_ref"))
        actual = str(args.get("otp_target_hash") or "").strip()
        if not expected or not actual or actual != expected:
            raise ValueError("otp_not_bound_to_recipient")


def _load_submitter_for_token(request_id: str, signer_token: Any) -> dict[str, Any]:
    token = str(signer_token or "").strip()
    if not token:
        raise ValueError("signer_token_required")
    submitter = sql.one(
        f"SELECT * FROM signature.submitters WHERE request_id={_q(request_id)} AND token_hash_sha256={_q(_sha256_text(token))}",
        user=_user(),
    )
    if not submitter:
        raise ValueError("invalid_signer_token")
    if str(submitter.get("status") or "").strip().lower() in CLOSED_SUBMITTER_STATUSES:
        raise ValueError("submitter_not_actionable")
    return submitter


def _validate_recipient_action(args: dict[str, Any]) -> tuple[str, dict[str, Any], dict[str, Any]]:
    request_id = str(args.get("request_id") or "").strip()
    action = _normalize_signature_action(args.get("action") or args.get("event_type") or "approved")
    if not request_id:
        raise ValueError("request_id is required")
    if not action:
        raise ValueError("invalid_signature_action")
    request = _load_request_for_action(request_id)
    if action in OTP_REQUIRED_SIGNATURE_ACTIONS:
        _require_recipient_otp(args)
    submitter = _load_submitter_for_token(request_id, args.get("signer_token"))
    if action in OTP_REQUIRED_SIGNATURE_ACTIONS:
        _require_recipient_otp(args, submitter)
    return action, request, submitter


def _comment_body(args: dict[str, Any], action: str) -> str | None:
    value = str(args.get("rejection_reason") or args.get("comment") or "").strip()
    if action == "rejected" and not value:
        raise ValueError("rejection_reason_required")
    return value[:4000] if value else None


def _record_comment_if_present(args: dict[str, Any], action: str, submitter: dict[str, Any]) -> dict[str, Any] | None:
    body = _comment_body(args, action)
    if not body:
        return None
    request_id = str(args.get("request_id") or "").strip()
    field_id = str(args.get("field_id") or "").strip() or None
    scope = "field" if field_id else "request"
    comment_id = args.get("comment_id") or _slug("signature-comment", f"{request_id}-{submitter.get('submitter_id')}-{field_id or 'request'}-{_sha256_text(body)[:12]}")
    return sql.statement_one(f"""
      INSERT INTO signature.comments (comment_id, request_id, submitter_id, field_id, scope, body, reason_type, visibility, trusted_identity, actor_type, actor_ref, ip_address, user_agent, metadata)
      VALUES ({_q(comment_id)}, {_q(request_id)}, {_q(submitter.get('submitter_id'))}, {_q(field_id)}, {_q(scope)}, {_q(body)}, {_q('rejection' if action == 'rejected' else args.get('reason_type'))}, {_q(args.get('visibility') or 'owner')}, {str(bool(args.get('otp_verified'))).lower()}, {_q(args.get('actor_type') or 'customer')}, {_q(args.get('actor_ref'))}, {_q(args.get('ip_address'))}, {_q(args.get('user_agent'))}, {_j(args.get('metadata') or {})})
      ON CONFLICT (comment_id) DO UPDATE SET body=EXCLUDED.body, metadata=EXCLUDED.metadata
      RETURNING *
    """, user=_user())


def _update_recipient_status(request_id: str, submitter_id: str, action: str, args: dict[str, Any]) -> None:
    status = _status_for_signature_action(action)
    if action == "commented":
        return
    timestamp_column = "declined_at" if status == "declined" else "signed_at"
    request_status = "declined" if status == "declined" else "partially_signed"
    sql.psql(f"""
      UPDATE signature.submitters
      SET status={_q(status)}, {timestamp_column}=COALESCE({_q(args.get('signed_at'))}::timestamptz, now()), ip_address=COALESCE({_q(args.get('ip_address'))}, ip_address), user_agent=COALESCE({_q(args.get('user_agent'))}, user_agent), updated_at=now()
      WHERE submitter_id={_q(submitter_id)};
      WITH required AS (
        SELECT count(*) FILTER (WHERE role IN ('signer','approver') AND status NOT IN ('signed','approved')) AS remaining_required
        FROM signature.submitters
        WHERE request_id={_q(request_id)}
      )
      UPDATE signature.document_requests
      SET status=CASE WHEN {_q(status)}='declined' THEN 'declined' WHEN (SELECT remaining_required FROM required)=0 THEN 'completed' ELSE {_q(request_status)} END,
          completed_at=CASE WHEN {_q(status)}<>'declined' AND (SELECT remaining_required FROM required)=0 THEN COALESCE(completed_at, now()) ELSE completed_at END,
          updated_at=now()
      WHERE request_id={_q(request_id)};
    """, user=_user())


def _handle_recipient_action_record(args: dict, **_kwargs) -> str:
    try:
        action, _request, submitter = _validate_recipient_action(args)
        comment = _record_comment_if_present(args, action, submitter)
        _update_recipient_status(str(args.get("request_id") or "").strip(), str(submitter.get("submitter_id") or ""), action, args)
        payload = {
            "action": action,
            "field_id": args.get("field_id"),
            "comment_id": (comment or {}).get("comment_id"),
            "comment": (comment or {}).get("body"),
            "otp_challenge_id": args.get("otp_challenge_id") if action in OTP_REQUIRED_SIGNATURE_ACTIONS else None,
        }
        event = _record_event(
            str(args.get("request_id") or "").strip(),
            submitter_id=submitter.get("submitter_id"),
            event_type=_event_type_for_signature_action(action),
            actor_type=args.get("actor_type") or "customer",
            actor_ref=args.get("actor_ref"),
            payload=payload,
            ip_address=args.get("ip_address"),
            user_agent=args.get("user_agent"),
            metadata=args.get("metadata") or {},
        )
        return _ok(action=action, submitter_id=submitter.get("submitter_id"), comment=comment, event=event)
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
        secured_args = {**args, "action": "approved"}
        _action, request, submitter = _validate_recipient_action(secured_args)
        submitter_id = submitter.get("submitter_id")
        approval_id = args.get("approval_id") or _slug("signature-approval", f"{request_id}-{submitter_id or args.get('actor_ref') or 'approval'}")
        context = {
            "request_id": request_id,
            "submitter_id": submitter_id,
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
        approval = sql.statement_one(f"""
          INSERT INTO signature.approvals (approval_id, request_id, submitter_id, source_type, source_id, approval_context, signature_text, signature_image_sha256, document_hash_sha256, approval_hash, ip_address, user_agent, signed_at, metadata)
          VALUES ({_q(approval_id)}, {_q(request_id)}, {_q(submitter_id)}, {_q(context['source_type'])}, {_q(context['source_id'])}, {_j(context)}, {_q(args.get('signature_text'))}, {_q(args.get('signature_image_sha256'))}, {_q(context['document_hash_sha256'])}, {_q(approval_hash)}, {_q(args.get('ip_address'))}, {_q(args.get('user_agent'))}, COALESCE({_q(args.get('signed_at'))}::timestamptz, now()), {_j(args.get('metadata') or {})})
          ON CONFLICT (approval_id) DO UPDATE SET approval_context=EXCLUDED.approval_context, signature_text=EXCLUDED.signature_text, signature_image_sha256=EXCLUDED.signature_image_sha256, document_hash_sha256=EXCLUDED.document_hash_sha256, approval_hash=EXCLUDED.approval_hash, ip_address=EXCLUDED.ip_address, user_agent=EXCLUDED.user_agent, signed_at=EXCLUDED.signed_at, metadata=EXCLUDED.metadata
          RETURNING *
        """, user=_user())
        _update_recipient_status(request_id, str(submitter_id or ""), "approved", args)
        sql.psql(f"""
          UPDATE signature.document_requests
          SET approval_hash={_q(approval_hash)},
              document_hash_sha256=COALESCE({_q(context['document_hash_sha256'])}, document_hash_sha256),
              updated_at=now()
          WHERE request_id={_q(request_id)};
        """, user=_user())
        event = _record_event(request_id, submitter_id=submitter_id, event_type="approved", actor_type=args.get("actor_type") or "customer", actor_ref=args.get("actor_ref"), payload={"approval_id": approval_id, "approval_hash": approval_hash, "context": context, "otp_challenge_id": args.get("otp_challenge_id")}, ip_address=args.get("ip_address"), user_agent=args.get("user_agent"), metadata=args.get("metadata") or {})
        _record_event(request_id, submitter_id=submitter_id, event_type="hash_created", actor_type="system", actor_ref="signature_core", payload={"approval_hash": approval_hash, "approval_id": approval_id}, metadata=args.get("metadata") or {})
        return _ok(approval=approval, approval_hash=approval_hash, event=event)
    except Exception as exc:
        return _err(exc)


def _schema(name: str, description: str, props: dict, required: list[str] | None = None) -> dict:
    return {"type": "function", "function": {"name": name, "description": description, "parameters": {"type": "object", "properties": props, "required": required or []}}}


def _meta_props() -> dict[str, Any]:
    return {"metadata": {"type": "object", "description": SIGNATURE_METADATA_DESCRIPTION}}


registry.register(name="signature_status", toolset="signature", schema=_schema("signature_status", "Return Signature Core row counts and DB backend.", {}), handler=_handle_signature_status, check_fn=_check_signature, emoji="✍️")
registry.register(name="signature_template_upsert", toolset="signature", schema=_schema("signature_template_upsert", "Create or update a reusable e-signature template with fields/submitter roles.", {"template_id": {"type": "string"}, "name": {"type": "string"}, "document_url": {"type": "string"}, "fields": {"type": "array", "items": {"type": "object"}}, "submitters": {"type": "array", "items": {"type": "object"}}, "preferences": {"type": "object"}, **_meta_props()}, ["name"]), handler=_handle_template_upsert, check_fn=_check_signature, emoji="✍️")
registry.register(name="signature_request_create", toolset="signature", schema=_schema("signature_request_create", "Create a document/signature request with opaque signer links and field snapshots.", {"request_id": {"type": "string"}, "template_id": {"type": "string"}, "source_type": {"type": "string"}, "source_id": {"type": "string"}, "title": {"type": "string"}, "status": {"type": "string"}, "document_url": {"type": "string"}, "fields": {"type": "array", "items": {"type": "object"}}, "submitters": {"type": "array", "items": {"type": "object"}}, "preferences": {"type": "object"}, "expires_at": {"type": "string"}, "actor_ref": {"type": "string"}, **_meta_props()}, ["title", "submitters"]), handler=_handle_request_create, check_fn=_check_signature, emoji="✍️")
registry.register(name="signature_request_get", toolset="signature", schema=_schema("signature_request_get", "Read a signature request with submitters, audit events, approvals, and comments.", {"request_id": {"type": "string"}}, ["request_id"]), handler=_handle_request_get, check_fn=_check_signature, emoji="✍️")
registry.register(name="signature_event_record", toolset="signature", schema=_schema("signature_event_record", "Append an audit event to a signature request with a chained event hash.", {"request_id": {"type": "string"}, "submitter_id": {"type": "string"}, "event_type": {"type": "string"}, "actor_type": {"type": "string"}, "actor_ref": {"type": "string"}, "ip_address": {"type": "string"}, "user_agent": {"type": "string"}, "event_payload": {"type": "object"}, **_meta_props()}, ["request_id", "event_type"]), handler=_handle_event_record, check_fn=_check_signature, emoji="✍️")
registry.register(name="signature_recipient_action_record", toolset="signature", schema=_schema("signature_recipient_action_record", "Record a recipient-bound Signature Core action. Sign/approve/reject require signer token plus verified OTP; comments/rejection reasons are persisted and audited with request/field scope.", {"request_id": {"type": "string"}, "action": {"type": "string", "description": "sign, approve, reject, or comment"}, "signer_token": {"type": "string"}, "otp_verified": {"type": "boolean"}, "otp_challenge_id": {"type": "string"}, "otp_target_hash": {"type": "string"}, "field_id": {"type": "string"}, "comment": {"type": "string"}, "rejection_reason": {"type": "string"}, "ip_address": {"type": "string"}, "user_agent": {"type": "string"}, "actor_type": {"type": "string"}, "actor_ref": {"type": "string"}, **_meta_props()}, ["request_id", "action", "signer_token"]), handler=_handle_recipient_action_record, check_fn=_check_signature, emoji="✍️")
registry.register(name="signature_approval_hash_create", toolset="signature", schema=_schema("signature_approval_hash_create", "Create a canonical approval record and SHA-256 approval hash for a signed/approved document. Requires signer token plus recipient-bound verified OTP.", {"approval_id": {"type": "string"}, "request_id": {"type": "string"}, "signer_token": {"type": "string"}, "otp_verified": {"type": "boolean"}, "otp_challenge_id": {"type": "string"}, "otp_target_hash": {"type": "string"}, "source_type": {"type": "string"}, "source_id": {"type": "string"}, "signature_text": {"type": "string"}, "signature_image_sha256": {"type": "string"}, "document_hash_sha256": {"type": "string"}, "approval_hash": {"type": "string"}, "ip_address": {"type": "string"}, "user_agent": {"type": "string"}, "signed_at": {"type": "string"}, "actor_type": {"type": "string"}, "actor_ref": {"type": "string"}, **_meta_props()}, ["request_id", "signer_token"]), handler=_handle_approval_hash_create, check_fn=_check_signature, emoji="✍️")

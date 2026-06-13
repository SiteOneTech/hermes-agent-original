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
import mimetypes
import re
import secrets
from datetime import UTC, datetime
from pathlib import Path
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
_FIELD_SCHEMA_VERSION = "signature-field-schema-v1"
_VALID_FIELD_TYPES = {"signature", "initials", "name", "date", "text", "long_comment", "checkbox", "select", "attachment", "internal_note"}


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _pdf_page_count_metadata(path: Path) -> dict[str, Any]:
    """Return page count and render metadata without making PyMuPDF mandatory."""
    try:
        import fitz  # type: ignore[import-not-found]

        doc = fitz.open(str(path))
        try:
            pages = []
            for page_index in range(doc.page_count):
                rect = doc[page_index].rect
                pages.append({
                    "page_number": page_index + 1,
                    "width": float(rect.width),
                    "height": float(rect.height),
                    "rotation": int(doc[page_index].rotation),
                })
            return {"page_count": int(doc.page_count), "pages": pages, "renderer": "pymupdf", "preview_status": "metadata_only"}
        finally:
            doc.close()
    except Exception:
        data = path.read_bytes()
        page_count = len(re.findall(rb"/Type\s*/Page(?!s)\b", data))
        if page_count < 1:
            raise ValueError("PDF page count could not be determined")
        return {"page_count": page_count, "pages": [], "renderer": "pdf-token-scan", "preview_status": "metadata_only"}


def _render_pdf_previews(path: Path, preview_dir: Path | None, max_pages: int) -> dict[str, Any]:
    metadata = _pdf_page_count_metadata(path)
    if not preview_dir:
        return metadata
    try:
        import fitz  # type: ignore[import-not-found]

        preview_dir.mkdir(parents=True, exist_ok=True)
        doc = fitz.open(str(path))
        previews = []
        try:
            for page_index in range(min(doc.page_count, max_pages)):
                page = doc[page_index]
                pixmap = page.get_pixmap(matrix=fitz.Matrix(1.0, 1.0), alpha=False)
                preview_path = preview_dir / f"{path.stem}-page-{page_index + 1}.png"
                pixmap.save(str(preview_path))
                previews.append({
                    "page_number": page_index + 1,
                    "path": str(preview_path),
                    "mime_type": "image/png",
                    "byte_size": preview_path.stat().st_size,
                    "sha256": _sha256_file(preview_path),
                    "width": pixmap.width,
                    "height": pixmap.height,
                })
        finally:
            doc.close()
        return {**metadata, "renderer": "pymupdf", "preview_status": "rendered", "previews": previews}
    except Exception as exc:
        return {**metadata, "preview_status": "metadata_only", "preview_error": str(exc)}


def _mime_for_pdf(path: Path) -> str:
    guessed = mimetypes.guess_type(str(path))[0]
    return guessed if guessed == "application/pdf" else "application/pdf"


def _template_missing_questions(args: dict[str, Any]) -> list[dict[str, str]]:
    questions: list[dict[str, str]] = []
    if not args.get("submitters"):
        questions.append({
            "missing": "submitters",
            "question": "¿Quiénes deben firmar o aprobar este PDF? Indica nombre, email/teléfono, rol, orden y si cada uno es obligatorio u opcional.",
        })
    if not args.get("fields"):
        questions.append({
            "missing": "fields",
            "question": "¿Qué campos necesita recolectar el PDF y dónde van? Indica tipo de campo, rol, página y coordenadas o frase/ancla aproximada.",
        })
    if not args.get("deadline") and not args.get("expires_at"):
        questions.append({
            "missing": "deadline",
            "question": "¿Cuál es la fecha límite/expiración y la cadencia de recordatorios para esta recolección de firmas?",
        })
    return questions


def _normalize_field(field: dict[str, Any], template_version_id: str, idx: int) -> dict[str, Any]:
    field_type = str(field.get("field_type") or "").strip() or "signature"
    if field_type not in _VALID_FIELD_TYPES:
        raise ValueError(f"unsupported field_type: {field_type}")
    normalized = {
        "field_id": field.get("field_id") or _slug("signature-field", f"{template_version_id}-{field.get('role') or 'signer'}-{field_type}-{idx}"),
        "role": field.get("role") or "signer",
        "field_type": field_type,
        "label": field.get("label") or field_type.replace("_", " ").title(),
        "required": field.get("required") is not False,
        "page_number": int(field.get("page_number") or 1),
        "x": float(field.get("x") if field.get("x") is not None else 0),
        "y": float(field.get("y") if field.get("y") is not None else 0),
        "width": float(field.get("width") if field.get("width") is not None else 180),
        "height": float(field.get("height") if field.get("height") is not None else 48),
        "rotation": float(field.get("rotation") or 0),
        "x_pct": float(field.get("x_pct") if field.get("x_pct") is not None else 0),
        "y_pct": float(field.get("y_pct") if field.get("y_pct") is not None else 0),
        "w_pct": float(field.get("w_pct") if field.get("w_pct") is not None else 0.25),
        "h_pct": float(field.get("h_pct") if field.get("h_pct") is not None else 0.06),
        "anchor_text": field.get("anchor_text"),
        "anchor_occurrence": field.get("anchor_occurrence"),
        "anchor_bbox": field.get("anchor_bbox"),
        "anchor_strategy": field.get("anchor_strategy"),
        "anchor_tolerance": field.get("anchor_tolerance"),
        "validation": field.get("validation") or {},
        "appearance": field.get("appearance") or {},
        "metadata": field.get("metadata") or {},
    }
    if normalized["page_number"] < 1:
        raise ValueError("field page_number must be >= 1")
    for key in ("x_pct", "y_pct", "w_pct", "h_pct"):
        if not 0 <= normalized[key] <= 1:
            raise ValueError(f"{key} must be between 0 and 1")
    if normalized["width"] <= 0 or normalized["height"] <= 0:
        raise ValueError("field width and height must be positive")
    return normalized


def _parse_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    if isinstance(value, str):
        candidate = value.strip()
        if not candidate:
            return None
        if candidate.endswith("Z"):
            candidate = f"{candidate[:-1]}+00:00"
        try:
            parsed = datetime.fromisoformat(candidate)
        except ValueError:
            return None
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
    return None


def _is_required_obligation(submitter: dict[str, Any]) -> bool:
    return submitter.get("role") in _REQUIRED_COMPLETION_ROLES and submitter.get("required") is not False


def _is_submitter_complete(submitter: dict[str, Any]) -> bool:
    return str(submitter.get("status") or "").lower() in _COMPLETE_SUBMITTER_STATUSES


def _completion_status_for_submitter(submitter: dict[str, Any] | None) -> str:
    if (submitter or {}).get("role") == "signer":
        return "signed"
    return "approved"


def _derive_request_lifecycle(request: dict[str, Any], submitters: list[dict[str, Any]]) -> dict[str, Any]:
    """Derive aggregate request status from V2 submitter obligations."""
    current_status = str(request.get("status") or "sent")
    required_submitters = [submitter for submitter in submitters if _is_required_obligation(submitter)]
    completed_required = [submitter for submitter in required_submitters if _is_submitter_complete(submitter)]
    decline_blocks = request.get("decline_blocks") is not False

    if current_status == "completed":
        return {"status": "completed", "completed": True, "required_count": len(required_submitters), "completed_required_count": len(completed_required)}

    if decline_blocks and any(str(submitter.get("status") or "").lower() == "declined" for submitter in required_submitters):
        return {"status": "declined", "completed": False, "required_count": len(required_submitters), "completed_required_count": len(completed_required)}

    expires_at = _parse_timestamp(request.get("expires_at"))
    if expires_at and expires_at <= datetime.now(UTC):
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


def _handle_pdf_intake(args: dict, **_kwargs) -> str:
    try:
        raw_path = str(args.get("pdf_path") or args.get("source_path") or "").strip()
        if not raw_path:
            raise ValueError("pdf_path is required")
        pdf_path = Path(raw_path).expanduser().resolve()
        if not pdf_path.exists() or not pdf_path.is_file():
            raise ValueError("PDF file not found")
        with pdf_path.open("rb") as fh:
            header = fh.read(5)
        if header != b"%PDF-":
            raise ValueError("source must be a PDF file")

        render = _render_pdf_previews(
            pdf_path,
            Path(str(args["preview_dir"])).expanduser().resolve() if args.get("preview_dir") else None,
            int(args.get("max_preview_pages") or 3),
        )
        sha256 = _sha256_file(pdf_path)
        byte_size = pdf_path.stat().st_size
        metadata = {
            **(args.get("metadata") or {}),
            "purpose": "source_pdf",
            "page_count": render["page_count"],
            "render": render,
            "source_filename": pdf_path.name,
        }
        attachment_id = args.get("attachment_id") or _slug("signature-attachment", pdf_path.name)
        attachment = sql.statement_one(f"""
          INSERT INTO signature.attachments (attachment_id, request_id, kind, filename, mime_type, storage_path, byte_size, sha256, metadata, created_at)
          VALUES ({_q(attachment_id)}, {_q(args.get('request_id'))}, 'file', {_q(pdf_path.name)}, {_q(_mime_for_pdf(pdf_path))}, {_q(str(pdf_path))}, {byte_size}, {_q(sha256)}, {_j(metadata)}, now())
          ON CONFLICT (attachment_id) DO UPDATE SET request_id=EXCLUDED.request_id, kind=EXCLUDED.kind, filename=EXCLUDED.filename, mime_type=EXCLUDED.mime_type, storage_path=EXCLUDED.storage_path, byte_size=EXCLUDED.byte_size, sha256=EXCLUDED.sha256, metadata=EXCLUDED.metadata
          RETURNING *
        """, user=_user())
        return _ok(
            source_pdf={
                "attachment_id": attachment_id,
                "path": str(pdf_path),
                "filename": pdf_path.name,
                "mime_type": _mime_for_pdf(pdf_path),
                "byte_size": byte_size,
                "sha256": sha256,
                "page_count": render["page_count"],
                "attachment": attachment,
            },
            render=render,
        )
    except Exception as exc:
        return _err(exc)


def _handle_template_prepare(args: dict, **_kwargs) -> str:
    try:
        name = str(args.get("name") or "").strip()
        if not name:
            raise ValueError("name is required")
        source_attachment_id = str(args.get("source_document_attachment_id") or args.get("source_pdf_attachment_id") or "").strip()
        document_sha256 = str(args.get("document_sha256") or "").strip()
        if not source_attachment_id:
            raise ValueError("source_document_attachment_id is required")
        if not re.fullmatch(r"[0-9a-fA-F]{64}", document_sha256):
            raise ValueError("document_sha256 must be a SHA-256 hex digest")

        questions = _template_missing_questions(args)
        if questions:
            return _ok(ready=False, questions=questions, template=None, template_version=None)

        template_id = args.get("template_id") or _slug("signature-template", name)
        template = sql.statement_one(f"""
          INSERT INTO signature.templates (template_id, name, document_url, fields, submitters, preferences, metadata, created_at, updated_at)
          VALUES ({_q(template_id)}, {_q(name)}, {_q(args.get('document_url'))}, {_j(args.get('fields') or [])}, {_j(args.get('submitters') or [])}, {_j(args.get('preferences') or {})}, {_j(args.get('metadata') or {})}, now(), now())
          ON CONFLICT (template_id) DO UPDATE SET name=EXCLUDED.name, document_url=EXCLUDED.document_url, fields=EXCLUDED.fields, submitters=EXCLUDED.submitters, preferences=EXCLUDED.preferences, metadata=EXCLUDED.metadata, updated_at=now()
          RETURNING *
        """, user=_user())
        current = sql.one(f"SELECT coalesce(max(version_number), 0) AS version_number FROM signature.template_versions WHERE template_id={_q(template_id)}", user=_user()) or {}
        version_number = int(current.get("version_number") or 0) + 1
        template_version_id = args.get("template_version_id") or f"{template_id}-v{version_number}"
        normalized_fields = [_normalize_field(field, template_version_id, idx) for idx, field in enumerate(args.get("fields") or [], start=1)]
        version_metadata = {
            **(args.get("metadata") or {}),
            "source_document_sha256": document_sha256,
            "field_schema_version": _FIELD_SCHEMA_VERSION,
            "deadline": args.get("deadline") or args.get("expires_at"),
        }
        template_version = sql.statement_one(f"""
          INSERT INTO signature.template_versions (template_version_id, template_id, version_number, source_document_attachment_id, document_sha256, status, field_schema, submitter_schema, preparation_notes, metadata, created_by, created_at, activated_at)
          VALUES ({_q(template_version_id)}, {_q(template_id)}, {version_number}, {_q(source_attachment_id)}, {_q(document_sha256)}, {_q(args.get('status') or 'draft')}, {_j(normalized_fields)}, {_j(args.get('submitters') or [])}, {_q(args.get('preparation_notes'))}, {_j(version_metadata)}, {_q(args.get('created_by') or args.get('actor_ref'))}, now(), CASE WHEN {_q(args.get('status') == 'active')}::boolean THEN now() ELSE NULL END)
          ON CONFLICT (template_version_id) DO UPDATE SET source_document_attachment_id=EXCLUDED.source_document_attachment_id, document_sha256=EXCLUDED.document_sha256, status=EXCLUDED.status, field_schema=EXCLUDED.field_schema, submitter_schema=EXCLUDED.submitter_schema, preparation_notes=EXCLUDED.preparation_notes, metadata=EXCLUDED.metadata
          RETURNING *
        """, user=_user())
        placements = []
        for field in normalized_fields:
            placement = sql.statement_one(f"""
              INSERT INTO signature.field_placements (field_id, template_version_id, role, field_type, label, required, page_number, x, y, width, height, rotation, x_pct, y_pct, w_pct, h_pct, anchor_text, anchor_occurrence, anchor_bbox, anchor_strategy, anchor_tolerance, validation, appearance, metadata, created_at, updated_at)
              VALUES ({_q(field['field_id'])}, {_q(template_version_id)}, {_q(field['role'])}, {_q(field['field_type'])}, {_q(field['label'])}, {_q(field['required'])}::boolean, {field['page_number']}, {field['x']}, {field['y']}, {field['width']}, {field['height']}, {field['rotation']}, {field['x_pct']}, {field['y_pct']}, {field['w_pct']}, {field['h_pct']}, {_q(field['anchor_text'])}, {_q(field['anchor_occurrence'])}::integer, {_j(field['anchor_bbox'])}, {_q(field['anchor_strategy'])}, {_q(field['anchor_tolerance'])}::numeric, {_j(field['validation'])}, {_j(field['appearance'])}, {_j(field['metadata'])}, now(), now())
              ON CONFLICT (field_id) DO UPDATE SET template_version_id=EXCLUDED.template_version_id, role=EXCLUDED.role, field_type=EXCLUDED.field_type, label=EXCLUDED.label, required=EXCLUDED.required, page_number=EXCLUDED.page_number, x=EXCLUDED.x, y=EXCLUDED.y, width=EXCLUDED.width, height=EXCLUDED.height, rotation=EXCLUDED.rotation, x_pct=EXCLUDED.x_pct, y_pct=EXCLUDED.y_pct, w_pct=EXCLUDED.w_pct, h_pct=EXCLUDED.h_pct, anchor_text=EXCLUDED.anchor_text, anchor_occurrence=EXCLUDED.anchor_occurrence, anchor_bbox=EXCLUDED.anchor_bbox, anchor_strategy=EXCLUDED.anchor_strategy, anchor_tolerance=EXCLUDED.anchor_tolerance, validation=EXCLUDED.validation, appearance=EXCLUDED.appearance, metadata=EXCLUDED.metadata, updated_at=now()
              RETURNING *
            """, user=_user())
            placements.append(placement)
        return _ok(ready=True, questions=[], template=template, template_version=template_version, field_placements=placements, field_schema_version=_FIELD_SCHEMA_VERSION)
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
        return _ok(request=request, submitters=submitters, events=events, approvals=approvals)
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


def _schema(name: str, description: str, props: dict, required: list[str] | None = None) -> dict:
    return {"type": "function", "function": {"name": name, "description": description, "parameters": {"type": "object", "properties": props, "required": required or []}}}


def _meta_props() -> dict[str, Any]:
    return {"metadata": {"type": "object", "description": SIGNATURE_METADATA_DESCRIPTION}}


registry.register(name="signature_status", toolset="signature", schema=_schema("signature_status", "Return Signature Core row counts and DB backend.", {}), handler=_handle_signature_status, check_fn=_check_signature, emoji="✍️")
registry.register(name="signature_template_upsert", toolset="signature", schema=_schema("signature_template_upsert", "Create or update a reusable e-signature template with fields/submitter roles.", {"template_id": {"type": "string"}, "name": {"type": "string"}, "document_url": {"type": "string"}, "fields": {"type": "array", "items": {"type": "object"}}, "submitters": {"type": "array", "items": {"type": "object"}}, "preferences": {"type": "object"}, **_meta_props()}, ["name"]), handler=_handle_template_upsert, check_fn=_check_signature, emoji="✍️")
registry.register(name="signature_pdf_intake", toolset="signature", schema=_schema("signature_pdf_intake", "Register a source PDF for Signature Core intake, computing SHA-256, page count, MIME/size, and preview render metadata or PNG previews when preview_dir is provided.", {"pdf_path": {"type": "string"}, "request_id": {"type": "string"}, "attachment_id": {"type": "string"}, "preview_dir": {"type": "string"}, "max_preview_pages": {"type": "integer"}, **_meta_props()}, ["pdf_path"]), handler=_handle_pdf_intake, check_fn=_check_signature, emoji="📄")
registry.register(name="signature_template_prepare", toolset="signature", schema=_schema("signature_template_prepare", "Ask targeted missing signer/field/deadline questions or create an ad-hoc Signature Core template version from an intaken PDF and field schema.", {"template_id": {"type": "string"}, "template_version_id": {"type": "string"}, "name": {"type": "string"}, "source_document_attachment_id": {"type": "string"}, "document_sha256": {"type": "string"}, "document_url": {"type": "string"}, "fields": {"type": "array", "items": {"type": "object"}}, "submitters": {"type": "array", "items": {"type": "object"}}, "deadline": {"type": "string"}, "expires_at": {"type": "string"}, "status": {"type": "string", "enum": ["draft", "active", "archived"]}, "preferences": {"type": "object"}, "preparation_notes": {"type": "string"}, "created_by": {"type": "string"}, "actor_ref": {"type": "string"}, **_meta_props()}, ["name", "source_document_attachment_id", "document_sha256"]), handler=_handle_template_prepare, check_fn=_check_signature, emoji="📄")
registry.register(name="signature_request_create", toolset="signature", schema=_schema("signature_request_create", "Create a document/signature request with opaque signer links and field snapshots.", {"request_id": {"type": "string"}, "template_id": {"type": "string"}, "template_version_id": {"type": "string"}, "source_type": {"type": "string"}, "source_id": {"type": "string"}, "title": {"type": "string"}, "status": {"type": "string"}, "document_url": {"type": "string"}, "fields": {"type": "array", "items": {"type": "object"}}, "submitters": {"type": "array", "items": {"type": "object"}}, "preferences": {"type": "object"}, "expires_at": {"type": "string"}, "signing_mode": {"type": "string", "enum": ["parallel", "sequential", "mixed"]}, "decline_blocks": {"type": "boolean"}, "actor_ref": {"type": "string"}, **_meta_props()}, ["title", "submitters"]), handler=_handle_request_create, check_fn=_check_signature, emoji="✍️")
registry.register(name="signature_request_get", toolset="signature", schema=_schema("signature_request_get", "Read a signature request with submitters, audit events, and approvals.", {"request_id": {"type": "string"}}, ["request_id"]), handler=_handle_request_get, check_fn=_check_signature, emoji="✍️")
registry.register(name="signature_event_record", toolset="signature", schema=_schema("signature_event_record", "Append an audit event to a signature request with a chained event hash.", {"request_id": {"type": "string"}, "submitter_id": {"type": "string"}, "event_type": {"type": "string"}, "actor_type": {"type": "string"}, "actor_ref": {"type": "string"}, "ip_address": {"type": "string"}, "user_agent": {"type": "string"}, "event_payload": {"type": "object"}, **_meta_props()}, ["request_id", "event_type"]), handler=_handle_event_record, check_fn=_check_signature, emoji="✍️")
registry.register(name="signature_approval_hash_create", toolset="signature", schema=_schema("signature_approval_hash_create", "Create a canonical approval record and SHA-256 approval hash for a signed/approved document.", {"approval_id": {"type": "string"}, "request_id": {"type": "string"}, "submitter_id": {"type": "string"}, "source_type": {"type": "string"}, "source_id": {"type": "string"}, "signature_text": {"type": "string"}, "signature_image_sha256": {"type": "string"}, "document_hash_sha256": {"type": "string"}, "approval_hash": {"type": "string"}, "ip_address": {"type": "string"}, "user_agent": {"type": "string"}, "signed_at": {"type": "string"}, "actor_type": {"type": "string"}, "actor_ref": {"type": "string"}, **_meta_props()}, ["request_id"]), handler=_handle_approval_hash_create, check_fn=_check_signature, emoji="✍️")

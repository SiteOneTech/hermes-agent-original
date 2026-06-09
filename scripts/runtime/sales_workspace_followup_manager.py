#!/usr/bin/env python3
"""Sales workspace customer-comment responder/escalator.

Public delivery sandboxes only spool customer actions. After ingestion into
Sales Core this trusted runtime step turns customer comments/rejections into a
visible chat-style agent response and, when needed, an owner escalation.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from hermes_cli import agent_core_sql as sql

SALES_USER = os.getenv("SALES_DB_RUNTIME_USER") or sql.runtime_env().get("SALES_DB_RUNTIME_USER", "sales_runtime")
CRM_USER = os.getenv("CRM_DB_RUNTIME_USER") or sql.runtime_env().get("CRM_DB_RUNTIME_USER", "crm_runtime")
PUBLIC_ROOT = Path(os.getenv("DELIVERY_PUBLIC_ROOT", "/home/jean/zeus-runtime/delivery-sandbox/public"))
AGENT_PUBLIC_NAME = "Zeus de SitioUno"

ESCALATION_WORDS = {
    "rechaza",
    "rechazo",
    "rechazar",
    "molestia",
    "molesto",
    "molesta",
    "no sirve",
    "no funciona",
    "no hace nada",
    "error",
    "descuadr",
    "pdf",
    "firma",
    "aceptar",
    "boton",
    "botón",
    "pago",
    "factura",
    "legal",
    "incorrecto",
    "cambiar",
    "cambio",
    "disputa",
    "urgente",
}


def q(value: Any) -> str:
    return sql.quote_literal(value)


def j(value: Any) -> str:
    return sql.quote_jsonb(value)


def needs_escalation(comment: str, event_type: str = "commented") -> bool:
    """Return True when the customer message needs Zeus/owner attention."""
    if event_type == "rejected":
        return True
    text = (comment or "").strip().lower()
    return any(word in text for word in ESCALATION_WORDS)


def document_label(row: dict[str, Any]) -> str:
    raw_metadata = row.get("workspace_metadata")
    metadata: dict[str, Any] = raw_metadata if isinstance(raw_metadata, dict) else {}
    return (
        metadata.get("public_document_number")
        or metadata.get("quote_number")
        or metadata.get("invoice_number")
        or row.get("document_id")
        or row.get("workspace_id")
        or "documento"
    )


def make_sales_reply(row: dict[str, Any], *, escalated: bool) -> str:
    label = document_label(row)
    if escalated:
        return (
            f"Gracias por avisarnos. Registré tu comentario sobre {label} y lo escalé para revisión prioritaria "
            "antes de hacer cambios comerciales o documentales. Te responderemos por este mismo canal."
        )
    return (
        f"Gracias, recibimos tu comentario sobre {label}. Zeus de SitioUno lo está revisando; "
        "si requiere un ajuste del documento, quedará registrado aquí y te avisaremos el siguiente paso."
    )


def pending_sales_customer_events() -> list[dict[str, Any]]:
    return sql.rows(
        """
        SELECT w.workspace_id, w.public_token, w.public_url, w.document_type, w.document_id,
               w.customer_email, w.customer_name, w.status, w.metadata AS workspace_metadata,
               e.workspace_event_id, e.event_type, e.actor_type, e.actor_ref, e.comment,
               e.metadata AS event_metadata, e.occurred_at
        FROM sales.customer_workspaces w
        JOIN sales.customer_workspace_events e ON e.workspace_id=w.workspace_id
        WHERE e.event_type IN ('commented', 'rejected')
          AND COALESCE(e.actor_type, '') <> 'agent'
          AND COALESCE(e.metadata->>'agent_responded', 'false') <> 'true'
          AND COALESCE(e.metadata->>'escalated_to_owner', 'false') <> 'true'
        ORDER BY e.occurred_at ASC, e.workspace_event_id ASC
        """,
        user=SALES_USER,
    )


def mark_sales_event(event_id: int, patch: dict[str, Any]) -> None:
    sql.psql(
        f"""
        UPDATE sales.customer_workspace_events
        SET metadata = COALESCE(metadata, '{{}}'::jsonb) || {j(patch)}
        WHERE workspace_event_id={int(event_id)}
        """,
        user=SALES_USER,
    )


def insert_sales_agent_comment(workspace_id: str, reply_to_event_id: int, comment: str, metadata: dict[str, Any]) -> int | None:
    row = sql.statement_one(
        f"""
        INSERT INTO sales.customer_workspace_events (workspace_id, event_type, actor_type, actor_ref, comment, metadata, occurred_at)
        SELECT {q(workspace_id)}, 'commented', 'agent', {q(AGENT_PUBLIC_NAME)}, {q(comment)}, {j(metadata)}, now()
        WHERE NOT EXISTS (
          SELECT 1 FROM sales.customer_workspace_events
          WHERE workspace_id={q(workspace_id)}
            AND actor_type='agent'
            AND metadata->>'reply_to_event_id'={q(str(reply_to_event_id))}
        )
        RETURNING workspace_event_id
        """,
        user=SALES_USER,
    )
    return int(row["workspace_event_id"]) if row and row.get("workspace_event_id") is not None else None


def create_owner_follow_up(row: dict[str, Any], reason: str) -> dict[str, Any] | None:
    customer = row.get("customer_name") or row.get("customer_email") or row.get("actor_ref") or "Cliente"
    summary = f"Revisar comentario/escalación de {customer} en {document_label(row)}: {(row.get('comment') or '').strip()}"
    return sql.statement_one(
        f"""
        INSERT INTO crm.follow_ups (organization_id, contact_id, opportunity_id, due_at, summary, status, priority, assignee, metadata, created_at, updated_at)
        SELECT NULL, NULL, NULL, now(), {q(summary)}, 'open', 'high', 'agent',
               {j({'workspace_id': row.get('workspace_id'), 'workspace_event_id': row.get('workspace_event_id'), 'document_type': row.get('document_type'), 'document_id': row.get('document_id'), 'reason': reason, 'source': 'sales_workspace_followup_manager'})},
               now(), now()
        WHERE NOT EXISTS (
          SELECT 1 FROM crm.follow_ups
          WHERE metadata->>'source'='sales_workspace_followup_manager'
            AND metadata->>'workspace_event_id'={q(str(row.get('workspace_event_id')))}
        )
        RETURNING *
        """,
        user=CRM_USER,
    )


def refresh_sales_comments_json(workspace_id: str, public_token: str | None) -> str | None:
    if not public_token:
        return None
    rows = sql.rows(
        f"""
        SELECT workspace_event_id AS id, event_type, actor_type, actor_ref, comment, metadata,
               to_char(occurred_at AT TIME ZONE 'America/New_York', 'YYYY-MM-DD HH24:MI') AS occurred_at
        FROM sales.customer_workspace_events
        WHERE workspace_id={q(workspace_id)}
        ORDER BY occurred_at ASC, workspace_event_id ASC
        """,
        user=SALES_USER,
    )
    path = PUBLIC_ROOT / "w" / str(public_token) / "comments.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"events": rows}, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return str(path)


def process_sales_comments() -> list[str]:
    owner_notifications: list[str] = []
    for row in pending_sales_customer_events():
        event_id = int(row["workspace_event_id"])
        event_type = str(row.get("event_type") or "commented")
        comment = row.get("comment") or ""
        escalated = needs_escalation(comment, event_type)
        reply = make_sales_reply(row, escalated=escalated)
        reply_event_id = insert_sales_agent_comment(
            row["workspace_id"],
            event_id,
            reply,
            {
                "reply_to_event_id": event_id,
                "auto_response": True,
                "source": "sales_workspace_followup_manager",
                "escalated_to_owner": escalated,
                "customer_event_type": event_type,
            },
        )
        patch = {
            "agent_responded": True,
            "agent_response_event_id": reply_event_id,
            "agent_responded_at": datetime.now(timezone.utc).isoformat(),
        }
        if escalated:
            reason = "rejection_or_customer_issue_requires_owner_attention"
            create_owner_follow_up(row, reason)
            patch.update({"escalated_to_owner": True, "escalation_reason": reason})
            owner_notifications.append(
                f"Escalación en {document_label(row)}: {row.get('customer_name') or row.get('actor_ref') or 'Cliente'} dijo: “{comment}”. Link: {row.get('public_url') or row.get('workspace_id')}"
            )
        mark_sales_event(event_id, patch)
        refresh_sales_comments_json(row["workspace_id"], row.get("public_token"))
    return owner_notifications


if __name__ == "__main__":
    for message in process_sales_comments():
        print(message)

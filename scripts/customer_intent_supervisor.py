#!/usr/bin/env python3
"""Deterministic customer-intent supervisor for the SitioUno owner/supervisor.

Sophie/front-office agents write restricted customer requests into
``crm.customer_intents``. This script is intentionally deterministic and safe:

* it never sends customer messages/emails,
* never creates quotes, invoices, docs, signatures, payments, or calendar events,
* never marks work completed,
* only detects pending intents, emits an owner-side alert, and records an
  idempotency timestamp in metadata so cron does not spam the same intent.

Hermes cron should run it in ``no_agent=True`` mode. Empty stdout means no alert.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hermes_cli import agent_core_sql as sql  # noqa: E402


SUPERVISOR_NAME = "customer-intent-supervisor"


def _runtime_user() -> str:
    return sql.runtime_env().get("CRM_DB_RUNTIME_USER", "crm_runtime")


def _q(value: Any) -> str:
    return sql.quote_literal(value)


def _limit(value: Any, default: int = 10, maximum: int = 50) -> int:
    try:
        n = int(value or default)
    except Exception:
        n = default
    return max(1, min(maximum, n))


def _renotify_minutes(value: Any, default: int = 60) -> int:
    try:
        n = int(value or default)
    except Exception:
        n = default
    return max(5, min(24 * 60, n))


def fetch_pending(
    limit: int,
    *,
    only_alertable: bool = False,
    renotify_minutes: int = 60,
) -> list[dict[str, Any]]:
    """Return pending customer intents ordered by priority/age.

    ``only_alertable`` filters out intents that were already reported recently.
    This is the cron/no-agent mode: alert once, then re-alert only after the
    configured interval if the owner has not processed it yet.
    """
    clauses = ["ci.status = 'pending'"]
    if only_alertable:
        minutes = _renotify_minutes(renotify_minutes)
        clauses.append(f"""
          (
            (ci.metadata->>'supervisor_notified_at') IS NULL
            OR (ci.metadata->>'supervisor_notified_at')::timestamptz
               < now() - ({minutes} * interval '1 minute')
          )
        """)
    where = " AND ".join(f"({clause})" for clause in clauses)
    return sql.rows(f"""
      SELECT ci.intent_id, ci.status, ci.priority, ci.intent_type, ci.channel,
             ci.conversation_ref, ci.source_ref, ci.customer_request_raw,
             ci.summary, ci.required_action, ci.assigned_to, ci.due_at,
             ci.created_at, ci.metadata,
             ci.organization_id, o.name AS organization_name,
             ci.contact_id, c.full_name AS contact_name, c.email AS contact_email, c.phone AS contact_phone,
             ci.opportunity_id, opp.title AS opportunity_title, opp.stage AS opportunity_stage,
             ci.interaction_id
      FROM crm.customer_intents ci
      LEFT JOIN crm.contacts c ON c.contact_id = ci.contact_id
      LEFT JOIN crm.organizations o ON o.organization_id = ci.organization_id
      LEFT JOIN crm.opportunities opp ON opp.opportunity_id = ci.opportunity_id
      WHERE {where}
      ORDER BY
        CASE ci.priority WHEN 'urgent' THEN 0 WHEN 'high' THEN 1 WHEN 'normal' THEN 2 ELSE 3 END,
        ci.created_at ASC
      LIMIT {_limit(limit)}
    """, user=_runtime_user())


def fetch_recent_context(intent: dict[str, Any], limit: int = 5) -> list[dict[str, Any]]:
    clauses: list[str] = []
    if intent.get("contact_id"):
        clauses.append(f"i.contact_id = {_q(intent['contact_id'])}")
    if intent.get("organization_id"):
        clauses.append(f"i.organization_id = {_q(intent['organization_id'])}")
    if intent.get("opportunity_id"):
        clauses.append(f"i.opportunity_id = {_q(intent['opportunity_id'])}")
    if not clauses:
        return []
    where = " OR ".join(clauses)
    return sql.rows(f"""
      SELECT i.interaction_id, i.channel, i.direction, i.summary, i.occurred_at, i.actor, i.metadata
      FROM crm.interactions i
      WHERE {where}
      ORDER BY i.occurred_at DESC
      LIMIT {_limit(limit, default=5, maximum=10)}
    """, user=_runtime_user())


def build_payload(
    limit: int,
    *,
    only_alertable: bool = False,
    renotify_minutes: int = 60,
) -> dict[str, Any] | None:
    intents = fetch_pending(
        limit,
        only_alertable=only_alertable,
        renotify_minutes=renotify_minutes,
    )
    if not intents:
        return None
    for intent in intents:
        intent["recent_interactions"] = fetch_recent_context(intent)
    return {
        "kind": "pending_customer_intents",
        "supervisor": SUPERVISOR_NAME,
        "count": len(intents),
        "instructions": [
            "This deterministic supervisor only alerts; it does not execute customer actions.",
            "Zeus/owner must review CRM context before acting.",
            "Do not mark completed until the requested action is actually executed and evidence is verified.",
            "If action is ambiguous or unsafe, mark blocked with a concise reason and notify the owner/supervisor if appropriate.",
            "After processing, update the intent via customer_intent_update and record CRM interaction evidence.",
        ],
        "intents": intents,
    }


def mark_notified(intents: list[dict[str, Any]]) -> int:
    """Mark intents as owner-notified without changing their work status."""
    count = 0
    for intent in intents:
        intent_id = str(intent.get("intent_id") or "").strip()
        if not intent_id:
            continue
        row = sql.statement_one(f"""
          UPDATE crm.customer_intents
          SET metadata = metadata || jsonb_build_object(
                'supervisor_notified_at', now()::text,
                'supervisor_notified_by', {_q(SUPERVISOR_NAME)},
                'supervisor_notification_count',
                  COALESCE((metadata->>'supervisor_notification_count')::int, 0) + 1
              ),
              updated_at = now()
          WHERE intent_id = {_q(intent_id)}
          RETURNING intent_id
        """, user=_runtime_user())
        if row:
            count += 1
    return count


def _short(value: Any, max_chars: int = 240) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"


def format_alert(payload: dict[str, Any]) -> str:
    intents = list(payload.get("intents") or [])
    count = int(payload.get("count") or len(intents))
    lines = [
        f"🚨 **Customer Intent Supervisor:** {count} solicitud(es) de cliente pendientes de revisión.",
        "",
        "No ejecuté acciones: esto es una alerta determinística para que Zeus/owner revise, ejecute con tools privilegiadas si procede, verifique evidencia y luego actualice el intent.",
    ]
    for idx, intent in enumerate(intents, start=1):
        contact_bits = [
            intent.get("contact_name"),
            intent.get("contact_phone"),
            intent.get("contact_email"),
        ]
        contact = " / ".join(str(bit) for bit in contact_bits if bit)
        if not contact:
            contact = "contacto no identificado"
        lines.extend([
            "",
            f"{idx}. `{intent.get('intent_id')}` — **{intent.get('priority') or 'normal'}** / {intent.get('intent_type') or 'other'} / {intent.get('channel') or 'unknown'}",
            f"   - Contacto: {contact}",
            f"   - Resumen: {_short(intent.get('summary'))}",
        ])
        required_action = _short(intent.get("required_action"))
        if required_action:
            lines.append(f"   - Acción requerida: {required_action}")
        source_ref = intent.get("source_ref") or intent.get("conversation_ref")
        if source_ref:
            lines.append(f"   - Ref: `{_short(source_ref, 120)}`")
        recent = intent.get("recent_interactions") or []
        if recent:
            last = recent[0]
            lines.append(f"   - Último contexto CRM: {_short(last.get('summary'), 180)}")
    lines.extend([
        "",
        "Siguiente paso canónico: Zeus procesa cada intent explícitamente, registra evidencia CRM, y solo entonces lo marca `completed`, `blocked` o `cancelled`.",
    ])
    return "\n".join(lines).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Deterministic customer-intent supervisor for the SitioUno owner/supervisor.")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--renotify-minutes", type=int, default=60)
    parser.add_argument("--all-pending", action="store_true", help="Ignore notification idempotency filter.")
    parser.add_argument("--no-mark-notified", action="store_true", help="Do not update supervisor_notified_at metadata.")
    parser.add_argument("--json", action="store_true", help="Print compact JSON payload instead of Markdown alert.")
    parser.add_argument("--pretty", action="store_true", help="Print pretty JSON payload instead of Markdown alert.")
    args = parser.parse_args()

    payload = build_payload(
        args.limit,
        only_alertable=not args.all_pending,
        renotify_minutes=args.renotify_minutes,
    )
    if not payload:
        return

    if args.pretty or args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True))
        return

    if not args.no_mark_notified:
        marked = mark_notified(list(payload.get("intents") or []))
        payload["supervisor_marked_notified"] = marked
    print(format_alert(payload))


if __name__ == "__main__":
    main()

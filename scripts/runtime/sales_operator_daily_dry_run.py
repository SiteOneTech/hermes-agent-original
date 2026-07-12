#!/usr/bin/env python3
"""Sales Operator Core daily dry-run and cron-loop planner.

This is the safe I6 operator loop for Empleado.uno/SitioUno sales work. It
builds the daily prioritized action plan from Agent Core DB state and prints it
without sending email, WhatsApp, SMS, voice calls, social DMs, posts, or any
other external outbound action.

Default behavior is dry-run/no-send/no-report-write. Writing a daily report is
an explicit local DB side effect gated behind ``--write-report``; external sends
are never performed by this script.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hermes_cli import agent_core_sql as sql  # noqa: E402
from tools.sales_operator_tool import (  # noqa: E402
    _handle_daily_report_create,
    _handle_dashboard_snapshot,
    _user,
)

DEFAULT_CAMPAIGN_ID = "empleado-uno-1000-subscribers-q3-2026"
READ_ONLY_SEND_MODES = {"draft_only", "content_only", "research_only", "planned", "inbound", "supervised_send"}
BLOCKED_STATUSES = {"blocked", "cancelled", "opted_out", "unsubscribed"}
QUEUE_ACTIVE_STATUSES = {"draft", "queued", "approved", "blocked"}


def _payload(raw: str) -> dict[str, Any]:
    data = json.loads(raw)
    if not data.get("ok"):
        raise RuntimeError(data.get("error") or raw[:1000])
    return data


def _int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def _safe_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [value]


def load_snapshot(campaign_id: str | None, prospect_limit: int, report_limit: int) -> dict[str, Any]:
    return _payload(
        _handle_dashboard_snapshot(
            {
                "campaign_id": campaign_id,
                "prospect_limit": prospect_limit,
                "report_limit": report_limit,
            }
        )
    )


def load_queue_rows(campaign_id: str, limit: int = 50) -> list[dict[str, Any]]:
    limit = max(1, min(200, int(limit or 50)))
    return sql.rows(
        f"""
        SELECT
          q.outreach_id,
          q.prospect_id,
          p.name AS prospect_name,
          p.city,
          p.country,
          p.vertical,
          p.fit_score,
          p.priority,
          p.next_action,
          p.next_action_at,
          q.attack_plan_id,
          q.channel,
          q.status,
          q.scheduled_at,
          q.requires_approval,
          q.approval_status,
          q.message_subject,
          q.provider_ref,
          q.metadata,
          cp.mode AS policy_mode,
          cp.status AS policy_status,
          cp.daily_limit AS policy_daily_limit,
          cp.requires_human_approval AS policy_requires_human_approval
        FROM sales_operator.outreach_queue q
        LEFT JOIN sales_operator.prospects p ON p.prospect_id=q.prospect_id
        LEFT JOIN sales_operator.channel_policies cp ON cp.campaign_id=q.campaign_id AND cp.channel=q.channel
        WHERE q.campaign_id={sql.quote_literal(campaign_id)}
          AND q.status = ANY(ARRAY{sorted(QUEUE_ACTIVE_STATUSES)}::text[])
        ORDER BY
          CASE q.status WHEN 'blocked' THEN 0 WHEN 'approved' THEN 1 WHEN 'queued' THEN 2 ELSE 3 END,
          q.scheduled_at NULLS FIRST,
          q.updated_at DESC
        LIMIT {limit}
        """,
        user=_user(),
    )


def _action(priority: int, loop: str, title: str, reason: str, *, target: dict[str, Any] | None = None, blockers: list[str] | None = None) -> dict[str, Any]:
    return {
        "priority": priority,
        "loop": loop,
        "title": title,
        "reason": reason,
        "target": target or {},
        "blockers": blockers or [],
        "dry_run_only": True,
        "external_send": False,
        "requires_human_approval": True,
    }


def _top_territory(territories: list[dict[str, Any]]) -> dict[str, Any]:
    if not territories:
        return {}
    return sorted(territories, key=lambda row: (-_int(row.get("priority")), row.get("country") or "", row.get("city") or ""))[0]


def _channel_gate_summary(channels: list[dict[str, Any]]) -> dict[str, Any]:
    by_channel: dict[str, dict[str, Any]] = {}
    unsafe_auto_send: list[str] = []
    dry_run_modes: list[str] = []
    for row in channels:
        channel = str(row.get("channel") or "unknown")
        mode = str(row.get("mode") or row.get("status") or "draft_only")
        requires = bool(row.get("requires_human_approval"))
        by_channel[channel] = {
            "status": row.get("status"),
            "mode": mode,
            "daily_limit": _int(row.get("daily_limit")),
            "requires_human_approval": requires,
            "dry_run_enforced": True,
        }
        if mode == "auto_send" and not requires:
            unsafe_auto_send.append(channel)
        else:
            dry_run_modes.append(channel)
    return {
        "channels": by_channel,
        "unsafe_auto_send_channels": unsafe_auto_send,
        "dry_run_channels": sorted(dry_run_modes),
        "external_sends_allowed_by_this_script": False,
    }


def build_cron_specs(campaign_id: str) -> list[dict[str, Any]]:
    script = "/home/jean/Projects/hermes-agent-original/scripts/cron/sales_operator_daily_dry_run.sh"
    base = f"{script} --campaign-id {campaign_id}"
    return [
        {
            "name": "sales-operator-daily-brief-dry-run",
            "schedule": "0 8 * * *",
            "mode": "no_agent_safe_script",
            "enabled_by_default": False,
            "command": base + " --format markdown",
            "self_contained_prompt": (
                "Run the Sales Operator daily brief dry-run for campaign "
                f"{campaign_id}. Execute the repo script only. Do not send email, WhatsApp, SMS, voice calls, social DMs, posts, or provider actions. "
                "Return the script output and highlight blockers if any channel is not supervised/draft-only."
            ),
        },
        {
            "name": "sales-operator-follow-up-queue-dry-run",
            "schedule": "*/30 9-18 * * 1-6",
            "mode": "no_agent_safe_script",
            "enabled_by_default": False,
            "command": base + " --format markdown --queue-limit 100",
            "self_contained_prompt": (
                "Review due Sales Operator follow-up queue items in dry-run mode. "
                f"Campaign: {campaign_id}. Never execute queued outreach. Print prioritized queue review, approval requirements, and opt-out/rate-limit blockers only."
            ),
        },
        {
            "name": "sales-operator-close-report-dry-run",
            "schedule": "0 17 * * 1-6",
            "mode": "agent_reasoned_report_optional",
            "enabled_by_default": False,
            "command": base + " --format json",
            "self_contained_prompt": (
                "Generate the Sales Operator close-of-day dry-run report from the JSON produced by the script. "
                f"Campaign: {campaign_id}. Summarize actions, replies, demos, closes, blockers, and tomorrow priorities. "
                "Do not infer customer interest from provider acknowledgements. Do not send outbound messages."
            ),
        },
    ]


def build_daily_dry_run(snapshot: dict[str, Any], queue_rows: list[dict[str, Any]], *, generated_at: datetime | None = None) -> dict[str, Any]:
    generated_at = generated_at or datetime.now(timezone.utc)
    campaign = snapshot.get("campaign") or {}
    campaign_id = campaign.get("campaign_id") or DEFAULT_CAMPAIGN_ID
    summary = snapshot.get("summary") or {}
    channels = _safe_list(snapshot.get("channels"))
    territories = _safe_list(snapshot.get("territories"))
    prospects = _safe_list(snapshot.get("prospects"))
    reports = _safe_list(snapshot.get("reports"))

    metrics = {
        "prospects": _int(summary.get("prospects")),
        "contacted_clients": _int(summary.get("contacted_clients")),
        "research_snapshots": _int(summary.get("research_snapshots")),
        "attack_plans": _int(summary.get("attack_plans")),
        "open_outreach": _int(summary.get("open_outreach")),
        "attempts": _int(summary.get("attempts")),
        "daily_reports": _int(summary.get("daily_reports")),
        "territories": _int(summary.get("territories")),
        "queue_rows_reviewed": len(queue_rows),
        "external_messages_sent_by_dry_run": 0,
    }
    gate = _channel_gate_summary(channels)
    actions: list[dict[str, Any]] = []
    top_territory = _top_territory(territories)

    if metrics["prospects"] == 0:
        actions.append(
            _action(
                100,
                "lead_discovery_tick",
                "Construir el primer lote público de leads del territorio prioritario",
                "La campaña todavía no tiene prospects; el siguiente avance comercial real es descubrir leads públicos y guardar evidencia antes de cualquier contacto.",
                target={"territory": top_territory, "suggested_batch_size": 10, "source_policy": "public_business_sources_only"},
            )
        )
    if metrics["research_snapshots"] < metrics["prospects"]:
        actions.append(
            _action(
                92,
                "enrichment_tick",
                "Completar research snapshots de prospects sin investigación",
                "Cada prospect debe tener evidencia pública, señales de dolor, canales públicos y nivel de incertidumbre antes de scoring/outreach.",
                target={"missing_research_count": metrics["prospects"] - metrics["research_snapshots"]},
            )
        )
    if metrics["attack_plans"] < metrics["research_snapshots"]:
        actions.append(
            _action(
                86,
                "attack_plan_tick",
                "Preparar attack plans personalizados para prospects investigados",
                "Los mensajes deben ser específicos por negocio y mantener Empleado.uno como empleado IA, no chatbot genérico.",
                target={"missing_attack_plans": metrics["research_snapshots"] - metrics["attack_plans"]},
            )
        )
    if queue_rows or metrics["open_outreach"]:
        blocked = [row for row in queue_rows if str(row.get("status")) in BLOCKED_STATUSES or str(row.get("policy_mode") or "") in {"planned", "research_only", "content_only"}]
        approvals = [row for row in queue_rows if bool(row.get("requires_approval")) or str(row.get("approval_status") or "") != "approved"]
        actions.append(
            _action(
                78,
                "follow_up_queue_dry_run",
                "Revisar cola de outreach sin ejecutar envíos",
                "Hay acciones en cola; I6 solo prioriza, valida política y prepara aprobaciones. No ejecuta proveedores.",
                target={"queue_rows_reviewed": len(queue_rows), "approval_required": len(approvals), "blocked_or_non_sendable": len(blocked)},
                blockers=["external_send_disabled_by_i6_dry_run"],
            )
        )
    if metrics["attempts"] > 0:
        actions.append(
            _action(
                70,
                "reply_audit_tick",
                "Auditar replies/evidencia de intentos previos sin inferir interés por ACK",
                "Provider ACK, delivered o recorded no equivale a interés del cliente; solo una respuesta humana actualiza la etapa.",
                target={"attempts_to_audit": metrics["attempts"]},
            )
        )
    else:
        actions.append(
            _action(
                54,
                "reply_audit_tick",
                "Mantener auditoría de replies en espera",
                "No hay intentos registrados todavía; el auditor permanece listo pero sin adaptadores de inbox activos para leer.",
                target={"attempts_to_audit": 0},
                blockers=["no_prior_attempts"],
            )
        )

    actions.append(
        _action(
            50,
            "daily_brief",
            "Generar brief diario supervisado para Jean",
            "El brief resume pipeline, blockers y prioridades; no activa canales ni proveedores.",
            target={"latest_report_date": (reports[0] or {}).get("report_date") if reports else None},
        )
    )

    if gate["unsafe_auto_send_channels"]:
        actions.insert(
            0,
            _action(
                110,
                "safety_gate",
                "Bloquear cualquier canal auto_send hasta revisión humana",
                "El dry-run detectó un canal auto_send sin aprobación humana. I6 no ejecuta outbound y debe elevar gate de seguridad.",
                target={"channels": gate["unsafe_auto_send_channels"]},
                blockers=["unsafe_auto_send_policy_detected"],
            ),
        )

    actions = sorted(actions, key=lambda row: (-_int(row.get("priority")), row.get("loop") or ""))
    loops = {
        "lead_discovery_tick": "Dry-run recommendation only; use public business sources and store source evidence before import.",
        "enrichment_tick": "Dry-run recommendation only; no scraping abuse, no private channels, no inferred private data.",
        "follow_up_queue_dry_run": "Reviews queue/policies only; never calls providers or marks messages as sent.",
        "reply_audit_tick": "Audits recorded evidence only; provider ACK is not customer interest.",
        "daily_brief": "Produces a report/brief for Jean; writing DB report requires explicit --write-report.",
    }
    return {
        "ok": True,
        "dry_run": True,
        "external_sends": False,
        "campaign_id": campaign_id,
        "campaign": campaign,
        "generated_at": generated_at.isoformat(),
        "metrics": metrics,
        "channel_gate_summary": gate,
        "priority_actions": actions,
        "cron_loops": loops,
        "cron_specs": build_cron_specs(campaign_id),
        "safety": {
            "default_state": "disabled_or_dry_run",
            "external_message_senders_called": False,
            "db_writes_by_default": False,
            "allowed_side_effects_by_default": ["stdout", "optional_local_json_target"],
            "blocked_external_channels": ["email", "whatsapp", "sms", "voice", "social_dm", "public_post"],
        },
    }


def write_report_from_dry_run(dry_run: dict[str, Any], report_date: str | None = None) -> dict[str, Any]:
    report_date = report_date or date.today().isoformat()
    actions = dry_run.get("priority_actions") or []
    metrics = dict(dry_run.get("metrics") or {})
    metrics["dry_run"] = True
    metrics["external_messages_sent"] = 0
    payload = {
        "campaign_id": dry_run["campaign_id"],
        "report_date": report_date,
        "work_summary": "Daily Sales Operator dry-run: se priorizaron acciones comerciales sin ejecutar envíos externos.",
        "discoveries": [a["reason"] for a in actions if a.get("loop") in {"lead_discovery_tick", "enrichment_tick"}],
        "actions_taken": [
            {
                "loop": a.get("loop"),
                "title": a.get("title"),
                "dry_run_only": True,
                "external_send": False,
            }
            for a in actions
        ],
        "learnings": ["I6 prioriza acciones y valida políticas; el envío externo permanece fail-closed."],
        "blockers": sorted({b for a in actions for b in (a.get("blockers") or [])}),
        "next_actions": [a.get("title") for a in actions[:5]],
        "metrics": metrics,
        "retrospective": "Dry-run seguro completado. No se llamó ningún proveedor externo.",
    }
    report = _payload(_handle_daily_report_create(payload))
    return report


def run_daily_dry_run(
    *,
    campaign_id: str | None,
    prospect_limit: int,
    report_limit: int,
    queue_limit: int,
    write_report: bool = False,
    report_date: str | None = None,
    target: Path | None = None,
) -> dict[str, Any]:
    snapshot = load_snapshot(campaign_id, prospect_limit, report_limit)
    campaign = snapshot.get("campaign") or {}
    resolved_campaign_id = campaign.get("campaign_id") or campaign_id or DEFAULT_CAMPAIGN_ID
    queue_rows = load_queue_rows(resolved_campaign_id, queue_limit) if campaign else []
    dry_run = build_daily_dry_run(snapshot, queue_rows)
    if write_report:
        dry_run["report_write"] = write_report_from_dry_run(dry_run, report_date)
    if target:
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(target.suffix + ".tmp")
        tmp.write_text(json.dumps(dry_run, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp.replace(target)
        target.chmod(0o644)
    return dry_run


def render_markdown(dry_run: dict[str, Any]) -> str:
    campaign = dry_run.get("campaign") or {}
    product = campaign.get("product_name") or dry_run.get("campaign_id")
    metrics = dry_run.get("metrics") or {}
    lines = [
        f"# Sales Operator daily dry-run — {product}",
        "",
        f"Generated: `{dry_run.get('generated_at')}`",
        "",
        "## Safety",
        "",
        "- External sends: **disabled**",
        "- Providers called: **none**",
        "- Default DB writes: **none** unless `--write-report` is passed",
        "- Provider ACK must not be treated as customer interest",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key in ["prospects", "research_snapshots", "attack_plans", "open_outreach", "attempts", "contacted_clients", "daily_reports", "territories", "queue_rows_reviewed", "external_messages_sent_by_dry_run"]:
        lines.append(f"| {key} | {metrics.get(key, 0)} |")
    lines.extend(["", "## Prioritized actions", ""])
    for i, action in enumerate(dry_run.get("priority_actions") or [], start=1):
        blockers = ", ".join(action.get("blockers") or []) or "none"
        lines.extend(
            [
                f"{i}. **P{action.get('priority')} — {action.get('title')}**",
                f"   - Loop: `{action.get('loop')}`",
                f"   - Reason: {action.get('reason')}",
                f"   - External send: `{action.get('external_send')}`",
                f"   - Blockers: {blockers}",
            ]
        )
    lines.extend(["", "## Cron specs — disabled by default", ""])
    for spec in dry_run.get("cron_specs") or []:
        lines.extend(
            [
                f"- **{spec['name']}** `{spec['schedule']}`",
                f"  - Enabled by default: `{spec['enabled_by_default']}`",
                f"  - Command: `{spec['command']}`",
                f"  - Prompt: {spec['self_contained_prompt']}",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Sales Operator daily dry-run; never sends external messages.")
    parser.add_argument("--campaign-id", default=DEFAULT_CAMPAIGN_ID)
    parser.add_argument("--prospect-limit", type=int, default=50)
    parser.add_argument("--report-limit", type=int, default=14)
    parser.add_argument("--queue-limit", type=int, default=50)
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--target", type=Path, help="Optional local JSON artifact path to write; not an external send.")
    parser.add_argument("--write-report", action="store_true", help="Explicitly write/update a local sales_operator.daily_reports row.")
    parser.add_argument("--report-date", help="Date for --write-report, YYYY-MM-DD. Defaults to today.")
    args = parser.parse_args()

    dry_run = run_daily_dry_run(
        campaign_id=args.campaign_id,
        prospect_limit=args.prospect_limit,
        report_limit=args.report_limit,
        queue_limit=args.queue_limit,
        write_report=args.write_report,
        report_date=args.report_date,
        target=args.target,
    )
    if args.format == "json":
        print(json.dumps(dry_run, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_markdown(dry_run), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

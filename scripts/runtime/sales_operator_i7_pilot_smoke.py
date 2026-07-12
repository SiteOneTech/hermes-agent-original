#!/usr/bin/env python3
"""I7 first pilot smoke for the Empleado.uno Sales Operator Core.

The smoke creates a deterministic, synthetic pilot batch in Agent Core DB:

- canonical Empleado.uno campaign and active Medellín / clínicas-estética territory;
- 10 clearly marked synthetic prospects with source-backed fixture evidence;
- research snapshots, lead scores, attack plans, and draft outreach queue rows;
- one CRM organization/contact/opportunity/follow-up readback for the top pilot lead;
- daily report/dashboard/dry-run evidence.

It never sends email, WhatsApp, SMS, voice calls, social DMs, posts, or provider
requests. The generated prospects use RFC 2606 ``.test`` domains and metadata
``synthetic_pilot_fixture=true`` so they cannot be mistaken for real businesses.
"""
from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hermes_cli import agent_core_sql as sql  # noqa: E402
from tools import crm_tool  # noqa: E402
from tools import sales_operator_tool as so_tool  # noqa: E402
from scripts.runtime import sales_operator_daily_dry_run as dry_run  # noqa: E402

DEFAULT_CAMPAIGN_ID = "empleado-uno-1000-subscribers-q3-2026"
DEFAULT_TERRITORY_ID = "so-territory-empleado-uno-i7-medellin-clinicas-estetica"
DEFAULT_SOURCE_ID = "so-source-i7-synthetic-pilot-fixture-pack"
DEFAULT_REPORT_ID = "so-report-empleado-uno-i7-pilot-smoke"
I7_METADATA = {
    "business_id": "sitiouno",
    "product_id": "empleado-uno",
    "campaign_id": DEFAULT_CAMPAIGN_ID,
    "i7_smoke": True,
    "synthetic_pilot_fixture": True,
    "not_real_business": True,
    "external_outbound_allowed": False,
    "source_policy": "manual_synthetic_fixture_no_contact",
}
FORBIDDEN_EXTERNAL_ACTIONS = (
    "email_send",
    "whatsapp_send",
    "sms_send",
    "voice_call",
    "social_dm",
    "public_post",
    "provider_call",
)


def _payload(raw: str) -> dict[str, Any]:
    data = json.loads(raw)
    if not data.get("ok"):
        raise RuntimeError(data.get("error") or raw[:1000])
    return data


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def _q(value: Any) -> str:
    return sql.quote_literal(value)


def fixture_leads() -> list[dict[str, Any]]:
    """Return the deterministic synthetic pilot lead pack.

    The leads are intentionally realistic enough to exercise the sales operator
    workflow, but they are not real businesses and all domains use ``.test``.
    """
    base: list[dict[str, Any]] = [
        {
            "slug": "clinica-aurora",
            "name": "I7 PILOTO — Clínica Aurora Medellín",
            "micro_vertical": "clínica estética facial",
            "pain_points": ["alto volumen de preguntas repetidas por WhatsApp", "agenda de valoración dependiente de recepción", "seguimiento manual a pacientes interesados"],
            "public_channels": ["web", "instagram", "whatsapp_visible_fixture"],
            "score": 90,
            "cta": "probar un empleado IA que responda preguntas frecuentes y agende valoraciones",
        },
        {
            "slug": "estetica-botanica",
            "name": "I7 PILOTO — Estética Botánica Laureles",
            "micro_vertical": "spa y estética corporal",
            "pain_points": ["consultas por disponibilidad de cabinas", "promociones manuales", "recordatorios de citas sin automatizar"],
            "public_channels": ["instagram", "whatsapp_visible_fixture"],
            "score": 84,
            "cta": "ver un demo de recepción IA para promociones y citas",
        },
        {
            "slug": "spa-altavista",
            "name": "I7 PILOTO — Spa Médico Altavista",
            "micro_vertical": "spa médico",
            "pain_points": ["leads preguntan por paquetes", "necesita filtro antes de consulta", "respuestas fuera de horario"],
            "public_channels": ["web", "email_fixture"],
            "score": 80,
            "cta": "activar una ruta de diagnóstico y agenda sin saturar al equipo",
        },
        {
            "slug": "dermatologia-rio",
            "name": "I7 PILOTO — Centro Dermatológico Río",
            "micro_vertical": "dermatología estética",
            "pain_points": ["dudas previas a procedimientos", "triage básico antes de cita", "seguimiento posterior lento"],
            "public_channels": ["web", "instagram", "email_fixture"],
            "score": 88,
            "cta": "probar respuestas guiadas y agendamiento para valoración",
        },
        {
            "slug": "odontoestetica-poblado",
            "name": "I7 PILOTO — Odontoestética Poblado",
            "micro_vertical": "odontología estética",
            "pain_points": ["cotizaciones iniciales repetidas", "preguntas por financiación", "agenda de evaluación"],
            "public_channels": ["web", "whatsapp_visible_fixture"],
            "score": 76,
            "cta": "mostrar cómo el empleado IA precalifica y agenda evaluación",
        },
        {
            "slug": "laser-primavera",
            "name": "I7 PILOTO — Clínica Láser Primavera",
            "micro_vertical": "depilación láser",
            "pain_points": ["preguntas frecuentes por zonas y sesiones", "recordatorios de paquetes", "leads de promociones"],
            "public_channels": ["instagram", "whatsapp_visible_fixture"],
            "score": 82,
            "cta": "demo de empleado IA para responder paquetes y reservar valoración",
        },
        {
            "slug": "beauty-manila",
            "name": "I7 PILOTO — Beauty Studio Manila",
            "micro_vertical": "beauty studio",
            "pain_points": ["agenda fragmentada", "mensajes fuera de horario", "promociones por temporada"],
            "public_channels": ["instagram"],
            "score": 70,
            "cta": "ver una prueba de agenda y respuesta automática supervisada",
        },
        {
            "slug": "rehab-estetica-norte",
            "name": "I7 PILOTO — Rehabilitación Estética Norte",
            "micro_vertical": "postoperatorio y estética funcional",
            "pain_points": ["seguimiento de pacientes", "instrucciones repetidas", "triage de dudas comunes"],
            "public_channels": ["web", "email_fixture"],
            "score": 78,
            "cta": "probar un flujo IA para seguimiento y dudas frecuentes",
        },
        {
            "slug": "wellness-belen",
            "name": "I7 PILOTO — Centro Wellness Belén",
            "micro_vertical": "wellness y medicina estética",
            "pain_points": ["canales dispersos", "consultas de horarios", "clientes preguntan por combos"],
            "public_channels": ["web", "instagram", "whatsapp_visible_fixture"],
            "score": 74,
            "cta": "demo para centralizar respuestas y agenda en un empleado IA",
        },
        {
            "slug": "integral-envigado",
            "name": "I7 PILOTO — Estética Integral Envigado",
            "micro_vertical": "estética integral área metropolitana",
            "pain_points": ["captura de leads desde redes", "confirmación de citas", "falta de seguimiento estructurado"],
            "public_channels": ["instagram", "whatsapp_visible_fixture"],
            "score": 86,
            "cta": "probar seguimiento IA sin enviar mensajes masivos",
        },
    ]
    leads: list[dict[str, Any]] = []
    for item in base:
        domain = f"i7-{item['slug']}.test"
        leads.append(
            {
                **item,
                "prospect_id": f"so-prospect-i7-{item['slug']}",
                "attack_plan_id": f"so-plan-i7-{item['slug']}-email",
                "outreach_id": f"so-outreach-i7-{item['slug']}-email-draft",
                "domain": domain,
                "website": f"https://{domain}/",
                "country": "Colombia",
                "city": "Medellín",
                "vertical": "clínicas/estética",
                "contact_name": f"Contacto Piloto {item['slug'].replace('-', ' ').title()}",
                "contact_email": f"contacto@{domain}",
                "priority": "hot" if item["score"] >= 80 else "warm",
            }
        )
    return leads


def _clean_previous_i7_rows(campaign_id: str) -> None:
    """Delete only rows explicitly marked as I7 synthetic smoke artifacts."""
    prospect_ids = [lead["prospect_id"] for lead in fixture_leads()]
    ids_sql = ", ".join(_q(pid) for pid in prospect_ids)
    so_user = so_tool._user()
    sql.psql(
        f"""
        DELETE FROM sales_operator.outreach_queue WHERE campaign_id={_q(campaign_id)} AND metadata->>'i7_smoke'='true';
        DELETE FROM sales_operator.attack_plans WHERE campaign_id={_q(campaign_id)} AND metadata->>'i7_smoke'='true';
        DELETE FROM sales_operator.lead_scores WHERE metadata->>'i7_smoke'='true' OR prospect_id IN ({ids_sql});
        DELETE FROM sales_operator.research_snapshots WHERE metadata->>'i7_smoke'='true' OR prospect_id IN ({ids_sql});
        """,
        user=so_user,
    )
    # CRM runtime intentionally has no DELETE privilege.  This one-shot smoke
    # cleanup uses the scoped Agent Core migration/admin role and only removes
    # rows explicitly marked as I7 synthetic artifacts.
    sql.psql(
        """
        DELETE FROM crm.follow_ups WHERE metadata->>'i7_smoke'='true';
        DELETE FROM crm.interactions WHERE metadata->>'i7_smoke'='true';
        """,
        user="agent_admin",
    )


def _call(label: str, handler: Callable[[dict[str, Any]], str], args: dict[str, Any], log: list[dict[str, Any]]) -> dict[str, Any]:
    raw = handler(args)
    payload = _payload(raw)
    log.append({"label": label, "args": _jsonable(args), "result": _jsonable(payload)})
    return payload


def _lead_metadata(lead: dict[str, Any], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        **I7_METADATA,
        "lead_slug": lead["slug"],
        "fixture_domain": lead["domain"],
        "uncertainty": "synthetic fixture; not a real public business; do not contact",
        **(extra or {}),
    }


def _research_args(lead: dict[str, Any], source_id: str) -> dict[str, Any]:
    return {
        "prospect_id": lead["prospect_id"],
        "source_id": source_id,
        "summary": (
            f"Fixture I7 para {lead['micro_vertical']} en Medellín. Señales simuladas: "
            f"{'; '.join(lead['pain_points'])}. No es un negocio real y no debe contactarse."
        ),
        "pain_points": [{"signal": p, "confidence": "fixture"} for p in lead["pain_points"]],
        "public_channels": [{"channel": c, "value": lead["domain"], "confidence": "fixture"} for c in lead["public_channels"]],
        "comparison_arguments": [
            {"argument": "Empleado.uno atiende como empleado IA, no chatbot genérico.", "fit": "alto"},
            {"argument": "Canales de estética suelen necesitar respuesta fuera de horario y agenda.", "fit": "medio-alto"},
        ],
        "evidence": [
            {
                "source": "factory/projects/empleado-uno-sales-operator-core/evidence/i7-pilot-fixture-leads.json",
                "type": "synthetic_fixture_pack",
                "lead_slug": lead["slug"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            {
                "source": "RFC2606 .test domain",
                "domain": lead["domain"],
                "type": "non_real_reserved_domain_guardrail",
            },
        ],
        "metadata": _lead_metadata(lead),
    }


def _score_args(lead: dict[str, Any]) -> dict[str, Any]:
    score = lead["score"]
    return {
        "prospect_id": lead["prospect_id"],
        "score": score,
        "score_band": "hot" if score >= 80 else "warm" if score >= 60 else "watch",
        "reasons": [
            {"factor": "vertical_fit", "value": "clínicas/estética matches first pilot territory", "points": 25},
            {"factor": "contactability_fixture", "value": "synthetic public-channel fixture present", "points": 15},
            {"factor": "pain_urgency", "value": ", ".join(lead["pain_points"][:2]), "points": score - 40},
        ],
        "metadata": _lead_metadata(lead),
    }


def _attack_plan_args(campaign_id: str, lead: dict[str, Any]) -> dict[str, Any]:
    body = (
        f"Hola, soy Zeus de SitioUno. Estoy preparando pilotos de Empleado.uno para negocios de estética en Medellín. "
        f"Vi un caso como {lead['name']} donde normalmente se repiten preguntas sobre {lead['pain_points'][0]}. "
        f"La idea no es venderte una plataforma técnica sino mostrarte un empleado IA que responde, filtra y agenda. "
        f"¿Te gustaría ver un demo corto adaptado a {lead['micro_vertical']}?"
    )
    return {
        "attack_plan_id": lead["attack_plan_id"],
        "campaign_id": campaign_id,
        "prospect_id": lead["prospect_id"],
        "plan_status": "draft",
        "primary_channel": "email",
        "message_subject": "Demo Empleado.uno para estética en Medellín",
        "message_body": body,
        "value_prop": f"{lead['cta']}; mantener agenda/respuestas sin saturar recepción.",
        "objections": [
            {"objection": "ya respondemos por WhatsApp", "reply": "Empleado.uno no reemplaza al equipo: filtra repetidos y agenda cuando el equipo no puede."},
            {"objection": "no quiero automatización fría", "reply": "El piloto mantiene tono humano y aprobación supervisada antes de tocar clientes."},
        ],
        "assets": [
            {"type": "demo", "url": "https://empleado.uno/", "note": "Demo pública/canónica; verificar antes de enviar en un canal real."}
        ],
        "next_step": "Supervisor debe revisar el draft; no enviar sin channel gate explícito.",
        "metadata": _lead_metadata(lead, {"no_price_quote_in_first_touch": True}),
    }


def _outreach_args(campaign_id: str, lead: dict[str, Any], scheduled_at: str) -> dict[str, Any]:
    attack = _attack_plan_args(campaign_id, lead)
    return {
        "outreach_id": lead["outreach_id"],
        "campaign_id": campaign_id,
        "prospect_id": lead["prospect_id"],
        "attack_plan_id": lead["attack_plan_id"],
        "channel": "email",
        "status": "draft",
        "scheduled_at": scheduled_at,
        "message_subject": attack["message_subject"],
        "message_body": attack["message_body"],
        "requires_approval": True,
        "approval_status": "pending",
        "metadata": _lead_metadata(lead, {"queued_by": "i7_pilot_smoke", "no_provider_called": True}),
    }


def _assert_no_external_send(evidence: dict[str, Any]) -> None:
    if evidence.get("external_sends") is not False:
        raise AssertionError("I7 smoke evidence must explicitly have external_sends=false")
    actions = evidence.get("external_actions_invoked") or []
    forbidden = [action for action in actions if action in FORBIDDEN_EXTERNAL_ACTIONS]
    if forbidden:
        raise AssertionError(f"Forbidden external actions invoked: {forbidden}")
    dry_metrics = (evidence.get("daily_dry_run") or {}).get("metrics") or {}
    if dry_metrics.get("external_messages_sent_by_dry_run") not in (0, None):
        raise AssertionError("Dry-run reported external sends")


def run_i7_pilot_smoke(
    *,
    campaign_id: str = DEFAULT_CAMPAIGN_ID,
    target: str | None = None,
    clean_fixtures: bool = True,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or datetime.now(timezone.utc)
    report_date = generated_at.date().isoformat()
    scheduled_at = (generated_at + timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0).isoformat()
    follow_up_at = (generated_at + timedelta(days=1)).replace(hour=15, minute=0, second=0, microsecond=0).isoformat()
    tool_outputs: list[dict[str, Any]] = []
    leads = fixture_leads()

    if clean_fixtures:
        _clean_previous_i7_rows(campaign_id)

    seed = _call(
        "sales_operator_seed_empleado_uno",
        so_tool._handle_seed_empleado_uno,
        {"campaign_id": campaign_id, "report_date": report_date, "target_subscribers": 1000, "budget_amount": 5000, "referral_code": "zeus"},
        tool_outputs,
    )
    territory = _call(
        "sales_operator_territory_upsert_i7_focus",
        so_tool._handle_territory_upsert,
        {
            "territory_id": DEFAULT_TERRITORY_ID,
            "campaign_id": campaign_id,
            "country": "Colombia",
            "city": "Medellín",
            "vertical": "clínicas/estética",
            "status": "active",
            "priority": 99,
            "source_notes": "I7 first pilot smoke focus territory; synthetic/no-contact fixture batch.",
            "metadata": {**I7_METADATA, "territory_focus": True},
        },
        tool_outputs,
    )
    territory_id = territory["territory"]["territory_id"]
    source = _call(
        "sales_operator_lead_source_upsert_i7_fixture_pack",
        so_tool._handle_lead_source_upsert,
        {
            "source_id": DEFAULT_SOURCE_ID,
            "campaign_id": campaign_id,
            "source_type": "manual_synthetic_fixture",
            "source_name": "I7 synthetic Medellín clínicas/estética pilot pack",
            "url": "repo://factory/projects/empleado-uno-sales-operator-core/evidence/i7-pilot-fixture-leads.json",
            "status": "active",
            "last_scanned_at": generated_at.isoformat(),
            "metadata": I7_METADATA,
        },
        tool_outputs,
    )
    source_id = source["source"]["source_id"]

    prospect_results: list[dict[str, Any]] = []
    research_results: list[dict[str, Any]] = []
    score_results: list[dict[str, Any]] = []
    attack_plan_results: list[dict[str, Any]] = []
    outreach_results: list[dict[str, Any]] = []

    for lead in leads:
        prospect = _call(
            "sales_operator_prospect_upsert",
            so_tool._handle_prospect_upsert,
            {
                "prospect_id": lead["prospect_id"],
                "campaign_id": campaign_id,
                "territory_id": territory_id,
                "name": lead["name"],
                "domain": lead["domain"],
                "website": lead["website"],
                "country": lead["country"],
                "city": lead["city"],
                "vertical": lead["vertical"],
                "status": "researched",
                "fit_score": lead["score"],
                "priority": lead["priority"],
                "next_action": "review_draft_attack_plan_no_send",
                "next_action_at": scheduled_at,
                "metadata": _lead_metadata(lead),
            },
            tool_outputs,
        )["prospect"]
        prospect_results.append(prospect)
        research_results.append(_call("sales_operator_research_record", so_tool._handle_research_record, _research_args(lead, source_id), tool_outputs)["research"])
        score_results.append(_call("sales_operator_score_record", so_tool._handle_score_record, _score_args(lead), tool_outputs)["score"])
        attack_plan_results.append(_call("sales_operator_attack_plan_upsert", so_tool._handle_attack_plan_upsert, _attack_plan_args(campaign_id, lead), tool_outputs)["attack_plan"])
        outreach_results.append(_call("sales_operator_outreach_enqueue_draft_no_send", so_tool._handle_outreach_enqueue, _outreach_args(campaign_id, lead, scheduled_at), tool_outputs)["outreach"])

    top_lead = leads[0]
    org_id = f"org-i7-pilot-{top_lead['slug']}"
    contact_id = f"contact-i7-pilot-{top_lead['slug']}"
    opportunity_id = f"opp-i7-pilot-empleado-uno-{top_lead['slug']}"
    crm_org = _call(
        "crm_organization_upsert_i7_fixture",
        crm_tool._handle_org_upsert,
        {
            "organization_id": org_id,
            "name": top_lead["name"],
            "domain": top_lead["domain"],
            "email": top_lead["contact_email"],
            "website": top_lead["website"],
            "status": "pilot_fixture",
            "metadata": _lead_metadata(top_lead, {"crm_bridge_smoke": True}),
        },
        tool_outputs,
    )["organization"]
    crm_contact = _call(
        "crm_contact_upsert_i7_fixture",
        crm_tool._handle_contact_upsert,
        {
            "contact_id": contact_id,
            "organization_id": org_id,
            "full_name": top_lead["contact_name"],
            "email": top_lead["contact_email"],
            "title": "Contacto sintético de pilot smoke",
            "status": "pilot_fixture",
            "source": "sales_operator_i7_pilot_smoke",
            "metadata": _lead_metadata(top_lead, {"crm_bridge_smoke": True}),
        },
        tool_outputs,
    )["contact"]
    crm_opp = _call(
        "crm_opportunity_upsert_i7_fixture",
        crm_tool._handle_opportunity_upsert,
        {
            "opportunity_id": opportunity_id,
            "organization_id": org_id,
            "contact_id": contact_id,
            "title": "Empleado.uno pilot smoke — demo estética Medellín",
            "stage": "qualified",
            "value_amount": 80,
            "currency": "USD",
            "expected_close_date": (generated_at + timedelta(days=14)).date().isoformat(),
            "status": "open",
            "metadata": _lead_metadata(top_lead, {"crm_bridge_smoke": True, "monthly_plan_fixture": "Profesional 80 USD reference only; not sent as quote"}),
        },
        tool_outputs,
    )["opportunity"]
    _call(
        "sales_operator_prospect_upsert_link_crm_ids",
        so_tool._handle_prospect_upsert,
        {
            "prospect_id": top_lead["prospect_id"],
            "campaign_id": campaign_id,
            "territory_id": territory_id,
            "organization_id": org_id,
            "contact_id": contact_id,
            "opportunity_id": opportunity_id,
            "name": top_lead["name"],
            "domain": top_lead["domain"],
            "website": top_lead["website"],
            "country": top_lead["country"],
            "city": top_lead["city"],
            "vertical": top_lead["vertical"],
            "status": "crm_linked_fixture",
            "fit_score": top_lead["score"],
            "priority": top_lead["priority"],
            "next_action": "crm_follow_up_created_no_send",
            "next_action_at": follow_up_at,
            "metadata": _lead_metadata(top_lead, {"crm_bridge_smoke": True}),
        },
        tool_outputs,
    )
    crm_interaction = _call(
        "crm_interaction_record_i7_fixture_note",
        crm_tool._handle_interaction_record,
        {
            "organization_id": org_id,
            "contact_id": contact_id,
            "opportunity_id": opportunity_id,
            "channel": "internal_note",
            "direction": "note",
            "summary": "I7 pilot smoke: synthetic Sales Operator lead bridged to CRM. No outbound message sent.",
            "occurred_at": generated_at.isoformat(),
            "actor": "Zeus",
            "metadata": _lead_metadata(top_lead, {"crm_bridge_smoke": True}),
        },
        tool_outputs,
    )["interaction"]
    crm_follow_up = _call(
        "crm_follow_up_create_i7_fixture",
        crm_tool._handle_follow_up_create,
        {
            "organization_id": org_id,
            "contact_id": contact_id,
            "opportunity_id": opportunity_id,
            "due_at": follow_up_at,
            "summary": "I7 smoke follow-up: revisar draft de demo Empleado.uno para estética; no enviar sin gate de canal.",
            "status": "open",
            "priority": "high",
            "assignee": "Zeus",
            "metadata": _lead_metadata(top_lead, {"crm_bridge_smoke": True, "no_send_without_gate": True}),
        },
        tool_outputs,
    )["follow_up"]
    crm_timeline = _call(
        "crm_customer_timeline_i7_readback",
        crm_tool._handle_customer_timeline,
        {"organization_id": org_id, "contact_id": contact_id, "opportunity_id": opportunity_id, "limit": 20},
        tool_outputs,
    )

    report = _call(
        "sales_operator_daily_report_create_i7",
        so_tool._handle_daily_report_create,
        {
            "report_id": DEFAULT_REPORT_ID,
            "campaign_id": campaign_id,
            "report_date": report_date,
            "work_summary": "I7 pilot smoke completado con 10 leads sintéticos/no-contact, scoring, attack plans draft, cola supervisada y CRM readback de un lead.",
            "discoveries": [
                {"item": "Los fixtures prueban la vertical Medellín clínicas/estética sin tocar negocios reales."},
                {"item": "Email queda en supervised_send/draft; WhatsApp oficial sigue planned."},
            ],
            "actions_taken": [
                {"item": "Seed/campaign/territory validated"},
                {"item": "10 prospects synthetic fixtures upserted"},
                {"item": "10 research snapshots, 10 scores, 10 attack plans, 10 draft outreach queue rows"},
                {"item": "1 CRM org/contact/opportunity/follow-up read back"},
            ],
            "learnings": [
                {"item": "The pilot flow can populate real DB evidence while preserving no-send safety."},
            ],
            "blockers": [
                {"item": "No real outbound until explicit channel/security gate."},
                {"item": "Pilot fixtures are not real leads; next production increment must replace them with source-verified public businesses."},
            ],
            "next_actions": [
                {"item": "If Jean approves, gather 10 real public businesses for the same territory and keep outreach draft-only."},
                {"item": "Validate public demo URL before any real message is sent."},
            ],
            "metrics": {
                "prospects_researched": len(research_results),
                "attacks_prepared": len(attack_plan_results),
                "messages_sent": 0,
                "responses": 0,
                "wins": 0,
                "crm_followups_created": 1,
                "draft_outreach_queued": len(outreach_results),
            },
            "retrospective": "I7 proves the first pilot smoke path end-to-end without external sends. All contact artifacts are drafts pending human/channel gate.",
        },
        tool_outputs,
    )["report"]

    dashboard = _payload(so_tool._handle_dashboard_snapshot({"campaign_id": campaign_id, "prospect_limit": 20, "report_limit": 10}))
    daily = dry_run.run_daily_dry_run(campaign_id=campaign_id, prospect_limit=20, report_limit=10, queue_limit=50, write_report=False)

    verification = {
        "campaign_present": bool(seed.get("campaign")),
        "territory_id": territory["territory"]["territory_id"],
        "source_id": source["source"]["source_id"],
        "prospects_upserted": len(prospect_results),
        "research_snapshots_created": len(research_results),
        "scores_created": len(score_results),
        "attack_plans_created": len(attack_plan_results),
        "draft_outreach_queued": len(outreach_results),
        "crm_readback": {
            "organization_id": crm_org["organization_id"],
            "contact_id": crm_contact["contact_id"],
            "opportunity_id": crm_opp["opportunity_id"],
            "interaction_id": crm_interaction["interaction_id"],
            "follow_up_id": crm_follow_up["follow_up_id"],
            "timeline_interactions": len(crm_timeline.get("interactions") or []),
            "timeline_follow_ups": len(crm_timeline.get("follow_ups") or []),
            "timeline_opportunities": len(crm_timeline.get("opportunities") or []),
        },
        "dashboard_summary": dashboard.get("summary") or {},
        "daily_dry_run_metrics": daily.get("metrics") or {},
    }

    evidence = {
        "ok": True,
        "increment": "I7 First pilot smoke for Empleado.uno",
        "campaign_id": campaign_id,
        "generated_at": generated_at.isoformat(),
        "dry_run": True,
        "external_sends": False,
        "external_actions_invoked": [],
        "fixture_policy": {
            "synthetic_only": True,
            "reserved_test_domains": True,
            "no_real_businesses_contacted": True,
            "no_provider_called": True,
            "crm_rows_marked_pilot_fixture": True,
        },
        "acceptance": {
            "campaign": seed.get("campaign"),
            "territory": territory.get("territory"),
            "leads_required": 10,
            "leads_created": len(prospect_results),
            "scored_leads": len(score_results),
            "attack_plans": len(attack_plan_results),
            "crm_readback_present": verification["crm_readback"]["timeline_follow_ups"] >= 1,
            "no_real_outbound": True,
        },
        "fixture_leads": leads,
        "created": {
            "prospects": prospect_results,
            "research_snapshots": research_results,
            "scores": score_results,
            "attack_plans": attack_plan_results,
            "draft_outreach_queue": outreach_results,
            "crm": {
                "organization": crm_org,
                "contact": crm_contact,
                "opportunity": crm_opp,
                "interaction": crm_interaction,
                "follow_up": crm_follow_up,
                "timeline": crm_timeline,
            },
            "daily_report": report,
        },
        "dashboard_snapshot": dashboard,
        "daily_dry_run": daily,
        "verification": verification,
        "tool_outputs": tool_outputs,
    }
    _assert_no_external_send(evidence)

    if target:
        target_path = Path(target).expanduser()
        if not target_path.is_absolute():
            target_path = REPO_ROOT / target_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        fixture_path = target_path.parent / "i7-pilot-fixture-leads.json"
        evidence["target"] = str(target_path)
        evidence["fixture_leads_target"] = str(fixture_path)
        fixture_path.write_text(
            json.dumps(
                {
                    "ok": True,
                    "campaign_id": campaign_id,
                    "generated_at": generated_at.isoformat(),
                    "synthetic_only": True,
                    "reserved_test_domains": True,
                    "external_sends": False,
                    "leads": _jsonable(leads),
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        target_path.write_text(json.dumps(_jsonable(evidence), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return evidence


def render_markdown(evidence: dict[str, Any]) -> str:
    verification = evidence["verification"]
    crm = verification["crm_readback"]
    lines = [
        "# I7 Sales Operator pilot smoke",
        "",
        f"- Campaign: `{evidence['campaign_id']}`",
        f"- Generated: `{evidence['generated_at']}`",
        "- Mode: **dry-run / no-send**",
        "- External sends: **disabled**",
        "- Providers called: **none**",
        "",
        "## Acceptance summary",
        "",
        f"- Prospects upserted: **{verification['prospects_upserted']}**",
        f"- Research snapshots: **{verification['research_snapshots_created']}**",
        f"- Lead scores: **{verification['scores_created']}**",
        f"- Attack plans: **{verification['attack_plans_created']}**",
        f"- Draft outreach queued: **{verification['draft_outreach_queued']}**",
        f"- CRM follow-up readback: **{crm['timeline_follow_ups']} follow-up(s)** for `{crm['organization_id']}`",
        "",
        "## Guardrail",
        "",
        "All leads are synthetic `.test` pilot fixtures and every outbound artifact is a draft pending channel/security gate.",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run I7 Empleado.uno Sales Operator pilot smoke")
    parser.add_argument("--campaign-id", default=DEFAULT_CAMPAIGN_ID)
    parser.add_argument("--target", default="factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-i7-pilot-smoke.json")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    parser.add_argument("--no-clean-fixtures", action="store_true", help="Do not delete previous rows marked i7_smoke=true before inserting")
    args = parser.parse_args(argv)

    evidence = run_i7_pilot_smoke(campaign_id=args.campaign_id, target=args.target, clean_fixtures=not args.no_clean_fixtures)
    if args.format == "markdown":
        sys.stdout.write(render_markdown(evidence))
    else:
        sys.stdout.write(json.dumps(_jsonable(evidence), ensure_ascii=False, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

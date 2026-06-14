"""Zeus Runtime Agent Management tools.

This module exposes the first Zeus-side control-plane tools for runtime-agent
onboarding. Sophie uses these tools after payment and Jean deploy authorization
to gather client configuration data conversationally, fill an internal form, and
generate the build/actuation report Zeus uses to configure the runtime agent.
"""
from __future__ import annotations

import json
import re
from copy import deepcopy
from typing import Any

from hermes_cli import agent_core_sql as sql
from tools.registry import registry, tool_error


AGENT_MANAGEMENT_METADATA_DESCRIPTION = (
    "Optional JSON metadata. Keep it generic and tenant-neutral: business_id, "
    "client_id, source_channel, external_ref, labels, notes."
)

SOPHIE_ONBOARDING_SPEAKER = "Sophie de SitioUno — Onboarding Specialist"

ONBOARDING_REQUIRED_FIELDS = [
    "business.name",
    "business.description",
    "business.country",
    "owner.name",
    "owner.primary_channel",
    "proposal_feedback.liked",
    "proposal_feedback.buying_reason",
    "operations.current_process",
    "operations.top_pain_points",
    "agent_expectations.main_jobs",
]

ONBOARDING_FIELD_PROMPTS = {
    "business.name": "Para comenzar, ¿cómo se llama tu empresa o marca comercial?",
    "business.description": "Cuéntame en tus palabras qué hace tu negocio, qué vendes o qué servicio prestas actualmente.",
    "business.country": "¿En qué país/ciudad opera principalmente tu negocio y en qué zona horaria debemos configurar el agente?",
    "owner.name": "¿Cuál es el nombre de la persona responsable con la que el agente debe identificarse internamente?",
    "owner.primary_channel": "¿Cuál será tu canal principal para operar con el agente: WhatsApp, llamadas, email, Telegram u otro?",
    "proposal_feedback.liked": "De la propuesta que viste de SitioUno, ¿qué fue lo que más te gustó o te hizo pensar que este agente puede ayudarte?",
    "proposal_feedback.buying_reason": "¿Cuál fue la razón principal por la que decidiste avanzar y pagar por el agente?",
    "operations.current_process": "Hoy, ¿cómo atiendes clientes, cotizaciones, agenda, pagos y seguimiento? Descríbeme el proceso actual aunque sea manual.",
    "operations.top_pain_points": "¿Cuáles son los 3 problemas operativos que más quieres que el agente te quite de encima?",
    "agent_expectations.main_jobs": "Si el agente ya estuviera activo mañana, ¿cuáles serían sus tareas principales durante una semana normal?",
}

DEFAULT_AGENT_CLASS_PACKS = {
    "generic_smb": {
        "display_name": "Agente SMB general",
        "feature_packs": ["crm", "calendar", "quotes", "invoices", "notifications", "followups"],
        "required_shared_capabilities": ["sendgrid_email"],
    },
    "cleaning_business": {
        "display_name": "Agente para servicios de limpieza",
        "feature_packs": ["crm", "calendar", "quotes", "field_service_followups", "notifications"],
        "required_shared_capabilities": ["sendgrid_email"],
    },
    "accounting_office": {
        "display_name": "Agente para oficina contable",
        "feature_packs": ["crm", "calendar", "document_intake", "accounting_lite", "notifications"],
        "required_shared_capabilities": ["sendgrid_email"],
    },
}

SECRET_LIKE_KEY_RE = re.compile(
    r"(api[_-]?key|token|secret|password|passwd|credential|client[_-]?secret|private[_-]?key|access[_-]?key|refresh[_-]?token|authorization|bearer)",
    re.IGNORECASE,
)
AUTHORIZATION_BEARER_RE = re.compile(r"(?i)\bauthorization\b\s*[:=]\s*bearer\s+[^\s,;]+")
BARE_BEARER_RE = re.compile(r"(?i)\bbearer\s+[^\s,;]+")
SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(api[_ -]?key|token|secret|password|passwd|credential|client[_ -]?secret|private[_ -]?key)\b\s*[:=]\s*[^\s,;]+"
)
REDACTED_REFERENCE = "[REDACTED_REFERENCE]"
REDACTED_FIELD = "[REDACTED_FIELD]"


def _ok(**fields: Any) -> str:
    return json.dumps({"ok": True, **fields}, ensure_ascii=False, sort_keys=True)


def _err(exc: Exception | str) -> str:
    return tool_error(str(exc))


def _user() -> str:
    return sql.runtime_env().get("AGENT_MANAGEMENT_DB_RUNTIME_USER", "agent_management_runtime")


def _q(v: Any) -> str:
    return sql.quote_literal(v)


def _j(v: Any) -> str:
    return sql.quote_jsonb(v)


def _slug(prefix: str, value: str) -> str:
    return f"{prefix}-{sql.slugify(value)}"


def _check_agent_management() -> bool:
    try:
        if not sql.enabled():
            return False
        proc = sql.psql(
            "SELECT to_regclass('agent_management.onboarding_sessions') IS NOT NULL;",
            user=_user(),
        )
        return proc.stdout.strip().lower() in {"t", "true"}
    except Exception:
        return False


def _secret_like_path(path: str, key: str) -> str | None:
    if SECRET_LIKE_KEY_RE.search(key):
        return f"{path}.{key}" if path else key
    return None


def _validate_no_secret_like_keys(value: Any, *, path: str = "payload") -> None:
    """Reject secret-looking keys before onboarding data reaches Agent Core.

    Sophie may record that a provider/secret is needed, but raw API keys,
    passwords, tokens, client secrets, credentials, and authorization headers
    belong in Infisical/runtime setup — never in conversational onboarding JSON.
    """
    if isinstance(value, dict):
        for key, nested in value.items():
            key_text = str(key)
            secret_path = _secret_like_path(path, key_text)
            if secret_path:
                raise ValueError(
                    f"secret-like field {secret_path!r} must not be stored in onboarding; use Infisical/runtime secret setup"
                )
            _validate_no_secret_like_keys(nested, path=f"{path}.{key_text}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _validate_no_secret_like_keys(nested, path=f"{path}[{index}]")


def _redact_secret_like_text(value: str) -> str:
    redacted = AUTHORIZATION_BEARER_RE.sub(f"authorization={REDACTED_REFERENCE}", value)
    redacted = BARE_BEARER_RE.sub(f"bearer {REDACTED_REFERENCE}", redacted)
    return SECRET_ASSIGNMENT_RE.sub(lambda match: f"{match.group(1)}={REDACTED_REFERENCE}", redacted)


def _redact_onboarding_payload(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, nested in value.items():
            key_text = str(key)
            if SECRET_LIKE_KEY_RE.search(key_text):
                redacted[key_text] = REDACTED_FIELD
            else:
                redacted[key_text] = _redact_onboarding_payload(nested)
        return redacted
    if isinstance(value, list):
        return [_redact_onboarding_payload(item) for item in value]
    if isinstance(value, str):
        return _redact_secret_like_text(value)
    return value


def _sanitize_onboarding_input(value: Any, *, path: str = "payload") -> Any:
    _validate_no_secret_like_keys(value, path=path)
    return _redact_onboarding_payload(value)


def _redact_session_row(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(row, dict):
        return row
    redacted = dict(row)
    for key, value in list(redacted.items()):
        if isinstance(value, str):
            redacted[key] = _redact_secret_like_text(value)
    if "form_data" in redacted:
        redacted["form_data"] = _redact_onboarding_payload(redacted["form_data"])
    if "metadata" in redacted:
        redacted["metadata"] = _redact_onboarding_payload(redacted["metadata"])
    return redacted


def _dot_get(data: dict[str, Any], dotted: str) -> Any:
    current: Any = data
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _has_answer(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def _missing_required_fields(form_data: dict[str, Any]) -> list[str]:
    return [field for field in ONBOARDING_REQUIRED_FIELDS if not _has_answer(_dot_get(form_data, field))]


def _merge_form_data(existing: dict[str, Any] | None, patch: dict[str, Any] | None) -> dict[str, Any]:
    """Deep-merge an onboarding form patch without losing prior answers."""
    result: dict[str, Any] = deepcopy(existing or {})
    incoming = patch or {}
    for key, value in incoming.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge_form_data(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def _compose_next_prompt(form_data: dict[str, Any] | None, *, channel: str = "chat") -> dict[str, Any]:
    data = form_data or {}
    missing = _missing_required_fields(data)
    if not missing:
        return {
            "complete": True,
            "speaker": SOPHIE_ONBOARDING_SPEAKER,
            "channel": channel,
            "next_field": None,
            "missing_fields": [],
            "customer_prompt": "Perfecto. Ya tengo la información mínima para preparar el informe interno de configuración del agente.",
        }
    field = missing[0]
    return {
        "complete": False,
        "speaker": SOPHIE_ONBOARDING_SPEAKER,
        "channel": channel,
        "next_field": field,
        "missing_fields": missing,
        "customer_prompt": ONBOARDING_FIELD_PROMPTS.get(field, f"Necesito completar el dato: {field}. ¿Me ayudas con esa información?"),
    }


def _extract_list(value: Any) -> list[Any]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _section(form_data: dict[str, Any], name: str) -> dict[str, Any]:
    value = form_data.get(name)
    return value if isinstance(value, dict) else {}


def _build_onboarding_report(session: dict[str, Any], form_data: dict[str, Any]) -> dict[str, Any]:
    safe_form_data = _redact_onboarding_payload(form_data)
    business = _section(safe_form_data, "business")
    owner = _section(safe_form_data, "owner")
    feedback = _section(safe_form_data, "proposal_feedback")
    operations = _section(safe_form_data, "operations")
    expectations = _section(safe_form_data, "agent_expectations")
    channels = _section(safe_form_data, "channels")
    class_id = session.get("agent_class") or business.get("agent_class") or "generic_smb"
    class_pack = DEFAULT_AGENT_CLASS_PACKS.get(str(class_id), DEFAULT_AGENT_CLASS_PACKS["generic_smb"])
    missing = _missing_required_fields(safe_form_data)
    return {
        "status": "needs_more_intake" if missing else "ready_for_zeus_build_review",
        "session_id": session.get("session_id"),
        "agent_class": class_id,
        "client_name": session.get("client_name") or owner.get("name"),
        "missing_required_fields": missing,
        "zeus_build_brief": {
            "client_business": business.get("name"),
            "business_description": business.get("description"),
            "country": business.get("country"),
            "timezone": business.get("timezone"),
            "owner_name": owner.get("name"),
            "primary_channel": owner.get("primary_channel"),
            "agent_class_display_name": class_pack.get("display_name"),
        },
        "commercial_context": {
            "what_client_liked": feedback.get("liked"),
            "buying_reason": feedback.get("buying_reason"),
            "promised_outcomes": _extract_list(feedback.get("promised_outcomes")),
            "sensitive_expectations": _extract_list(feedback.get("sensitive_expectations")),
        },
        "current_operation": {
            "current_process": operations.get("current_process"),
            "top_pain_points": _extract_list(operations.get("top_pain_points")),
            "manual_bottlenecks": _extract_list(operations.get("manual_bottlenecks")),
        },
        "desired_agent_behavior": {
            "main_jobs": _extract_list(expectations.get("main_jobs")),
            "tone": expectations.get("tone"),
            "allowed_actions": _extract_list(expectations.get("allowed_actions")),
            "needs_approval_for": _extract_list(expectations.get("needs_approval_for")),
        },
        "channel_and_assets": {
            "whatsapp": channels.get("whatsapp"),
            "email": channels.get("email"),
            "phone": channels.get("phone"),
            "website": channels.get("website"),
            "brand_assets": _extract_list(channels.get("brand_assets")),
        },
        "recommended_feature_packs": class_pack.get("feature_packs", []),
        "required_shared_capabilities": class_pack.get("required_shared_capabilities", []),
        "recommended_build_sequence": [
            "verify_payment_and_deploy_authorization",
            "create_or_update_agent_registry_record",
            "configure_runtime_agent",
            "apply_agent_class_pack",
            "sync_agent_and_shared_secret_packs",
            "run_channel_and_notification_smoke_tests",
            "activate_customer_success_guidance",
        ],
        "raw_form_data": safe_form_data,
    }


def _build_actuation_plan(session: dict[str, Any], form_data: dict[str, Any]) -> dict[str, Any]:
    safe_form_data = _redact_onboarding_payload(form_data)
    expectations = _section(safe_form_data, "agent_expectations")
    jobs = _extract_list(expectations.get("main_jobs"))
    return {
        "session_id": session.get("session_id"),
        "agent_class": session.get("agent_class") or "generic_smb",
        "human_intervention_policy": "agent_first_escalate_only_on_exception",
        "objective": "Acompañar al cliente desde la activación hasta uso autónomo sin intervención humana rutinaria.",
        "customer_success_goals": jobs,
        "phases": [
            {
                "phase": "orientation",
                "owner_agent": "Sophie Onboarding",
                "goal": "Explicar al cliente cómo hablarle al agente, qué tareas puede delegar y qué datos faltan por confirmar.",
                "customer_action": "Responder preguntas guiadas y confirmar prioridades operativas.",
            },
            {
                "phase": "activation_smoke",
                "owner_agent": "Runtime Activation Agent",
                "goal": "Validar canales, identidad pública, agenda, CRM, notificaciones y primer caso de uso real.",
                "customer_action": "Enviar o aprobar un ejemplo real de atención/cotización/agenda.",
            },
            {
                "phase": "guided_first_week",
                "owner_agent": "Customer Success Agent",
                "goal": "Proponer tareas diarias concretas, revisar si el cliente está usando el agente y corregir fricción temprano.",
                "customer_action": "Usar el agente para casos reales y reportar bloqueos en el mismo chat.",
            },
            {
                "phase": "autonomous_operation",
                "owner_agent": "Supervisor Agent",
                "goal": "Monitorear salud, tickets, oportunidades de mejora y excepciones sin pedir intervención humana salvo riesgo o decisión comercial.",
                "customer_action": "Operar normalmente y aprobar acciones sensibles cuando el agente lo solicite.",
            },
        ],
        "escalation_rules": [
            "Escalar a Zeus si falta un secreto/canal crítico o falla un smoke test.",
            "Escalar a Jean solo si requiere decisión comercial, permiso de deploy, pricing fuera de política, o riesgo legal/financiero.",
            "No pedir intervención humana para preguntas repetibles de uso; Sophie/Customer Success debe guiar al cliente.",
        ],
    }


def _session_or_error(session_id: str) -> dict[str, Any]:
    row = sql.one(
        f"SELECT * FROM agent_management.onboarding_sessions WHERE session_id={_q(session_id)}",
        user=_user(),
    )
    if not row:
        raise ValueError(f"onboarding session not found: {session_id}")
    return row


def _handle_onboarding_start(args: dict, **_kwargs) -> str:
    try:
        deploy_authorized_by = str(args.get("deploy_authorized_by") or "").strip()
        if not deploy_authorized_by:
            raise ValueError("deploy_authorized_by is required")
        if args.get("payment_received") is not True:
            raise ValueError("payment_received=true is required before onboarding")
        client_name = str(args.get("client_name") or args.get("business_name") or "").strip()
        if not client_name:
            raise ValueError("client_name is required")
        session_id = args.get("session_id") or _slug("onb", f"{client_name}-{args.get('agent_class') or 'generic_smb'}")
        initial_form = _sanitize_onboarding_input(
            args.get("initial_form_data") if isinstance(args.get("initial_form_data"), dict) else {},
            path="initial_form_data",
        )
        metadata = _sanitize_onboarding_input(args.get("metadata") or {}, path="metadata")
        existing = sql.one(
            f"SELECT * FROM agent_management.onboarding_sessions WHERE session_id={_q(session_id)}",
            user=_user(),
        )
        if existing:
            current_form = existing.get("form_data") if isinstance(existing.get("form_data"), dict) else {}
            current_metadata = existing.get("metadata") if isinstance(existing.get("metadata"), dict) else {}
            merged_form = _merge_form_data(current_form, initial_form)
            merged_metadata = _merge_form_data(current_metadata, metadata)
            row = sql.statement_one(
                f"""
                UPDATE agent_management.onboarding_sessions
                SET client_name={_q(client_name)},
                    client_contact={_q(args.get('client_contact') or existing.get('client_contact'))},
                    agent_class={_q(args.get('agent_class') or existing.get('agent_class') or 'generic_smb')},
                    status='intake_active',
                    deploy_authorized_by={_q(deploy_authorized_by)},
                    payment_reference={_q(args.get('payment_reference') or existing.get('payment_reference'))},
                    source_channel={_q(args.get('source_channel') or existing.get('source_channel') or 'chat')},
                    form_data={_j(merged_form)},
                    metadata={_j(merged_metadata)},
                    updated_at=now()
                WHERE session_id={_q(session_id)}
                RETURNING *
                """,
                user=_user(),
            )
        else:
            row = sql.statement_one(
                f"""
                INSERT INTO agent_management.onboarding_sessions (
                  session_id, client_name, client_contact, agent_class, status,
                  deploy_authorized_by, payment_reference, source_channel, form_data, metadata, created_at, updated_at
                ) VALUES (
                  {_q(session_id)}, {_q(client_name)}, {_q(args.get('client_contact'))}, {_q(args.get('agent_class') or 'generic_smb')},
                  'intake_active', {_q(deploy_authorized_by)}, {_q(args.get('payment_reference'))}, {_q(args.get('source_channel') or 'chat')},
                  {_j(initial_form)}, {_j(metadata)}, now(), now()
                )
                RETURNING *
                """,
                user=_user(),
            )
        row_form = row.get("form_data") if isinstance(row, dict) and isinstance(row.get("form_data"), dict) else initial_form
        prompt = _compose_next_prompt(row_form, channel=args.get("source_channel") or "chat")
        return _ok(session=_redact_session_row(row), next_prompt=prompt)
    except Exception as exc:
        return _err(exc)


def _handle_onboarding_form_update(args: dict, **_kwargs) -> str:
    try:
        session_id = str(args.get("session_id") or "").strip()
        if not session_id:
            raise ValueError("session_id is required")
        patch = args.get("form_patch")
        if not isinstance(patch, dict) or not patch:
            raise ValueError("form_patch is required")
        patch = _sanitize_onboarding_input(patch, path="form_patch")
        session = _session_or_error(session_id)
        current = session.get("form_data") if isinstance(session.get("form_data"), dict) else {}
        merged = _merge_form_data(current, patch)
        row = sql.statement_one(
            f"""
            UPDATE agent_management.onboarding_sessions
            SET form_data={_j(merged)}, updated_at=now()
            WHERE session_id={_q(session_id)}
            RETURNING *
            """,
            user=_user(),
        )
        sql.statement_one(
            f"""
            INSERT INTO agent_management.onboarding_events (session_id, actor, event_type, payload, source_channel, created_at)
            VALUES ({_q(session_id)}, {_q(args.get('actor') or SOPHIE_ONBOARDING_SPEAKER)}, 'form_update', {_j({'patch_keys': sorted(patch.keys()), 'message_received': bool(args.get('message'))})}, {_q(args.get('source_channel') or session.get('source_channel') or 'chat')}, now())
            RETURNING *
            """,
            user=_user(),
        )
        prompt = _compose_next_prompt(merged, channel=args.get("source_channel") or session.get("source_channel") or "chat")
        return _ok(session=_redact_session_row(row), next_prompt=prompt, missing_required_fields=prompt["missing_fields"])
    except Exception as exc:
        return _err(exc)


def _handle_onboarding_next_prompt(args: dict, **_kwargs) -> str:
    try:
        if isinstance(args.get("form_data"), dict):
            form_data = _redact_onboarding_payload(args["form_data"])
            channel = args.get("channel") or "chat"
        else:
            session_id = str(args.get("session_id") or "").strip()
            if not session_id:
                raise ValueError("session_id or form_data is required")
            session = _session_or_error(session_id)
            form_data = session.get("form_data") if isinstance(session.get("form_data"), dict) else {}
            channel = args.get("channel") or session.get("source_channel") or "chat"
        return _ok(next_prompt=_compose_next_prompt(form_data, channel=channel))
    except Exception as exc:
        return _err(exc)


def _handle_onboarding_report_generate(args: dict, **_kwargs) -> str:
    try:
        session_id = str(args.get("session_id") or "").strip()
        if not session_id:
            raise ValueError("session_id is required")
        session = _session_or_error(session_id)
        form_data = session.get("form_data") if isinstance(session.get("form_data"), dict) else {}
        report = _build_onboarding_report(session, form_data)
        report_type = "zeus_build_report"
        row = sql.statement_one(
            f"""
            INSERT INTO agent_management.onboarding_reports (session_id, report_type, status, report, created_by, created_at, updated_at)
            VALUES ({_q(session_id)}, {_q(report_type)}, {_q(report['status'])}, {_j(report)}, {_q(args.get('created_by') or 'zeus')}, now(), now())
            ON CONFLICT (session_id, report_type) DO UPDATE SET
              status=EXCLUDED.status,
              report=EXCLUDED.report,
              created_by=EXCLUDED.created_by,
              updated_at=now()
            RETURNING *
            """,
            user=_user(),
        )
        sql.statement_one(
            f"""
            UPDATE agent_management.onboarding_sessions
            SET status={_q('report_ready' if not report['missing_required_fields'] else 'intake_active')}, updated_at=now()
            WHERE session_id={_q(session_id)}
            RETURNING *
            """,
            user=_user(),
        )
        return _ok(report_record=row, report=report)
    except Exception as exc:
        return _err(exc)


def _handle_actuation_plan_generate(args: dict, **_kwargs) -> str:
    try:
        session_id = str(args.get("session_id") or "").strip()
        if not session_id:
            raise ValueError("session_id is required")
        session = _session_or_error(session_id)
        form_data = session.get("form_data") if isinstance(session.get("form_data"), dict) else {}
        plan = _build_actuation_plan(session, form_data)
        row = sql.statement_one(
            f"""
            INSERT INTO agent_management.onboarding_reports (session_id, report_type, status, report, created_by, created_at, updated_at)
            VALUES ({_q(session_id)}, 'actuation_plan', 'ready', {_j(plan)}, {_q(args.get('created_by') or 'zeus')}, now(), now())
            ON CONFLICT (session_id, report_type) DO UPDATE SET
              status=EXCLUDED.status,
              report=EXCLUDED.report,
              created_by=EXCLUDED.created_by,
              updated_at=now()
            RETURNING *
            """,
            user=_user(),
        )
        return _ok(plan_record=row, actuation_plan=plan)
    except Exception as exc:
        return _err(exc)


def _schema(name: str, description: str, props: dict, required: list[str] | None = None) -> dict:
    return {
        "name": name,
        "description": description,
        "parameters": {"type": "object", "properties": props, "required": required or []},
    }


registry.register(
    name="agent_mgmt_onboarding_start",
    toolset="agent_management",
    schema=_schema(
        "agent_mgmt_onboarding_start",
        "Start or reopen a post-payment Sophie onboarding session after Jean/deploy authorization. Creates the internal form record and returns Sophie's next question.",
        {
            "client_name": {"type": "string"},
            "client_contact": {"type": "string"},
            "business_name": {"type": "string"},
            "agent_class": {"type": "string"},
            "payment_received": {"type": "boolean"},
            "payment_reference": {"type": "string"},
            "deploy_authorized_by": {"type": "string"},
            "source_channel": {"type": "string"},
            "initial_form_data": {"type": "object"},
            "metadata": {"type": "object", "description": AGENT_MANAGEMENT_METADATA_DESCRIPTION},
        },
        ["client_name", "payment_received", "deploy_authorized_by"],
    ),
    handler=_handle_onboarding_start,
    check_fn=_check_agent_management,
    emoji="🧭",
)

registry.register(
    name="agent_mgmt_onboarding_form_update",
    toolset="agent_management",
    schema=_schema(
        "agent_mgmt_onboarding_form_update",
        "Merge new conversational answers into an onboarding form. Sophie should call this after each meaningful client answer; it never prints or stores secrets directly.",
        {
            "session_id": {"type": "string"},
            "form_patch": {"type": "object"},
            "actor": {"type": "string"},
            "source_channel": {"type": "string"},
            "message": {"type": "string"},
        },
        ["session_id", "form_patch"],
    ),
    handler=_handle_onboarding_form_update,
    check_fn=_check_agent_management,
    emoji="🧾",
)

registry.register(
    name="agent_mgmt_onboarding_next_prompt",
    toolset="agent_management",
    schema=_schema(
        "agent_mgmt_onboarding_next_prompt",
        "Return Sophie's next customer-facing onboarding question based on missing required fields. Accepts either session_id or raw form_data.",
        {"session_id": {"type": "string"}, "form_data": {"type": "object"}, "channel": {"type": "string"}},
    ),
    handler=_handle_onboarding_next_prompt,
    check_fn=_check_agent_management,
    emoji="💬",
)

registry.register(
    name="agent_mgmt_onboarding_report_generate",
    toolset="agent_management",
    schema=_schema(
        "agent_mgmt_onboarding_report_generate",
        "Generate and persist the internal Zeus build report from a completed or in-progress Sophie onboarding session.",
        {"session_id": {"type": "string"}, "created_by": {"type": "string"}},
        ["session_id"],
    ),
    handler=_handle_onboarding_report_generate,
    check_fn=_check_agent_management,
    emoji="📋",
)

registry.register(
    name="agent_mgmt_actuation_plan_generate",
    toolset="agent_management",
    schema=_schema(
        "agent_mgmt_actuation_plan_generate",
        "Generate the post-onboarding agent-first actuation guidance plan for activation, first-week coaching, autonomous operation, and exception escalation.",
        {"session_id": {"type": "string"}, "created_by": {"type": "string"}},
        ["session_id"],
    ),
    handler=_handle_actuation_plan_generate,
    check_fn=_check_agent_management,
    emoji="🗺️",
)

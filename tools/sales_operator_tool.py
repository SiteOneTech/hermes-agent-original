"""Sales Operator Core tools backed by Agent Core DB.

This module is the reusable commercial operator for SitioUno agents: campaigns,
territories, source-backed research, lead scoring, personalized attack plans,
policy-gated outreach, daily retrospectives, and CRM/Funnel Core bridge IDs.
Outbound starts supervised/fail-closed by policy; provider ACK is evidence, not
customer interest.
"""
from __future__ import annotations

import json
from datetime import date
from typing import Any

from hermes_cli import agent_core_sql as sql
from tools.registry import registry, tool_error

SALES_OPERATOR_METADATA_DESCRIPTION = (
    "Optional JSON metadata. Keep it generic and tenant-neutral: business_id, "
    "product_id, campaign_id, source_channel, external_ref, labels, notes."
)


def _ok(**fields: Any) -> str:
    return json.dumps({"ok": True, **fields}, ensure_ascii=False, sort_keys=True)


def _err(exc: Exception | str) -> str:
    return tool_error(str(exc))


def _user() -> str:
    env = sql.runtime_env()
    if env.get("SALES_OPERATOR_DB_RUNTIME_PASSWORD") or env.get("SALES_OPERATOR_DATABASE_URL"):
        return env.get("SALES_OPERATOR_DB_RUNTIME_USER", "sales_operator_runtime")
    return env.get("SALES_DB_RUNTIME_USER", "sales_runtime")


def _check_sales_operator() -> bool:
    try:
        if not sql.enabled():
            return False
        sql.psql("SELECT 1;", user=_user())
        return True
    except Exception:
        return False


def _q(v: Any) -> str:
    return sql.quote_literal(v)


def _j(v: Any) -> str:
    return sql.quote_jsonb(v)


def _slug(prefix: str, value: str) -> str:
    return f"{prefix}-{sql.slugify(value)}"


def _num(v: Any, default: str = "NULL") -> str:
    if v is None or v == "":
        return default
    try:
        return repr(float(v))
    except (TypeError, ValueError):
        raise ValueError(f"Invalid numeric value: {v!r}")


def _int(v: Any, default: str = "NULL") -> str:
    if v is None or v == "":
        return default
    try:
        return str(int(v))
    except (TypeError, ValueError):
        raise ValueError(f"Invalid integer value: {v!r}")


def _bool(v: Any, default: bool = False) -> str:
    if v is None or v == "":
        v = default
    return "TRUE" if bool(v) else "FALSE"


def _limit(v: Any, default: int = 20, maximum: int = 100) -> int:
    try:
        n = int(v or default)
    except Exception:
        n = default
    return max(1, min(maximum, n))


def _payload(raw: str) -> dict[str, Any]:
    data = json.loads(raw)
    if not data.get("ok"):
        raise RuntimeError(data.get("error") or raw[:1000])
    return data


def _campaign_id(args: dict[str, Any]) -> str:
    campaign_id = str(args.get("campaign_id") or "").strip()
    if campaign_id:
        return campaign_id
    product_id = str(args.get("product_id") or args.get("product_name") or "campaign").strip()
    return _slug("so-campaign", product_id)


def _handle_campaign_upsert(args: dict, **_kwargs) -> str:
    try:
        product_name = str(args.get("product_name") or "").strip()
        if not product_name:
            raise ValueError("product_name is required")
        campaign_id = _campaign_id(args)
        product_id = str(args.get("product_id") or sql.slugify(product_name)).strip()
        row = sql.statement_one(f"""
          INSERT INTO sales_operator.campaigns (
            campaign_id, product_id, product_name, business_id, status,
            target_subscribers, target_deadline, budget_amount, currency,
            referral_code, bonus_offer, positioning, metadata, created_at, updated_at
          ) VALUES (
            {_q(campaign_id)}, {_q(product_id)}, {_q(product_name)}, {_q(args.get('business_id') or 'sitiouno')}, {_q(args.get('status') or 'active')},
            {_int(args.get('target_subscribers'))}, {_q(args.get('target_deadline'))}, {_num(args.get('budget_amount'))}, {_q(args.get('currency') or 'USD')},
            {_q(args.get('referral_code') or 'zeus')}, {_q(args.get('bonus_offer'))}, {_q(args.get('positioning'))}, {_j(args.get('metadata') or {})}, now(), now()
          )
          ON CONFLICT (campaign_id) DO UPDATE SET
            product_id=EXCLUDED.product_id, product_name=EXCLUDED.product_name, business_id=EXCLUDED.business_id,
            status=EXCLUDED.status, target_subscribers=EXCLUDED.target_subscribers, target_deadline=EXCLUDED.target_deadline,
            budget_amount=EXCLUDED.budget_amount, currency=EXCLUDED.currency, referral_code=EXCLUDED.referral_code,
            bonus_offer=EXCLUDED.bonus_offer, positioning=EXCLUDED.positioning, metadata=EXCLUDED.metadata, updated_at=now()
          RETURNING *
        """, user=_user())
        return _ok(campaign=row)
    except Exception as exc:
        return _err(exc)


def _handle_territory_upsert(args: dict, **_kwargs) -> str:
    try:
        for field in ("campaign_id", "country", "city", "vertical"):
            if not str(args.get(field) or "").strip():
                raise ValueError(f"{field} is required")
        territory_id = args.get("territory_id") or _slug("so-territory", f"{args['campaign_id']}-{args['country']}-{args['city']}-{args['vertical']}")
        row = sql.statement_one(f"""
          INSERT INTO sales_operator.territories (territory_id, campaign_id, country, city, vertical, status, priority, source_notes, metadata, created_at, updated_at)
          VALUES ({_q(territory_id)}, {_q(args.get('campaign_id'))}, {_q(args.get('country'))}, {_q(args.get('city'))}, {_q(args.get('vertical'))}, {_q(args.get('status') or 'planned')}, {_int(args.get('priority'), '50')}, {_q(args.get('source_notes'))}, {_j(args.get('metadata') or {})}, now(), now())
          ON CONFLICT (campaign_id, country, city, vertical) DO UPDATE SET status=EXCLUDED.status, priority=EXCLUDED.priority, source_notes=EXCLUDED.source_notes, metadata=EXCLUDED.metadata, updated_at=now()
          RETURNING *
        """, user=_user())
        return _ok(territory=row)
    except Exception as exc:
        return _err(exc)


def _handle_channel_policy_upsert(args: dict, **_kwargs) -> str:
    try:
        campaign_id = str(args.get("campaign_id") or "").strip()
        channel = str(args.get("channel") or "").strip()
        if not campaign_id:
            raise ValueError("campaign_id is required")
        if not channel:
            raise ValueError("channel is required")
        policy_id = args.get("policy_id") or _slug("so-policy", f"{campaign_id}-{channel}")
        row = sql.statement_one(f"""
          INSERT INTO sales_operator.channel_policies (policy_id, campaign_id, channel, status, mode, daily_limit, requires_human_approval, notes, metadata, created_at, updated_at)
          VALUES ({_q(policy_id)}, {_q(campaign_id)}, {_q(channel)}, {_q(args.get('status') or 'draft_only')}, {_q(args.get('mode') or 'draft_only')}, {_int(args.get('daily_limit'), '0')}, {_bool(args.get('requires_human_approval'), True)}, {_q(args.get('notes'))}, {_j(args.get('metadata') or {})}, now(), now())
          ON CONFLICT (campaign_id, channel) DO UPDATE SET status=EXCLUDED.status, mode=EXCLUDED.mode, daily_limit=EXCLUDED.daily_limit, requires_human_approval=EXCLUDED.requires_human_approval, notes=EXCLUDED.notes, metadata=EXCLUDED.metadata, updated_at=now()
          RETURNING *
        """, user=_user())
        return _ok(policy=row)
    except Exception as exc:
        return _err(exc)


def _handle_lead_source_upsert(args: dict, **_kwargs) -> str:
    try:
        for field in ("campaign_id", "source_type", "source_name"):
            if not str(args.get(field) or "").strip():
                raise ValueError(f"{field} is required")
        source_id = args.get("source_id") or _slug("so-source", f"{args['campaign_id']}-{args['source_type']}-{args['source_name']}")
        row = sql.statement_one(f"""
          INSERT INTO sales_operator.lead_sources (source_id, campaign_id, source_type, source_name, url, status, last_scanned_at, metadata, created_at, updated_at)
          VALUES ({_q(source_id)}, {_q(args.get('campaign_id'))}, {_q(args.get('source_type'))}, {_q(args.get('source_name'))}, {_q(args.get('url'))}, {_q(args.get('status') or 'active')}, {_q(args.get('last_scanned_at'))}, {_j(args.get('metadata') or {})}, now(), now())
          ON CONFLICT (source_id) DO UPDATE SET source_type=EXCLUDED.source_type, source_name=EXCLUDED.source_name, url=EXCLUDED.url, status=EXCLUDED.status, last_scanned_at=EXCLUDED.last_scanned_at, metadata=EXCLUDED.metadata, updated_at=now()
          RETURNING *
        """, user=_user())
        return _ok(source=row)
    except Exception as exc:
        return _err(exc)


def _handle_prospect_upsert(args: dict, **_kwargs) -> str:
    try:
        campaign_id = str(args.get("campaign_id") or "").strip()
        name = str(args.get("name") or "").strip()
        if not campaign_id:
            raise ValueError("campaign_id is required")
        if not name:
            raise ValueError("name is required")
        prospect_id = args.get("prospect_id") or _slug("so-prospect", f"{campaign_id}-{args.get('domain') or args.get('website') or name}")
        row = sql.statement_one(f"""
          INSERT INTO sales_operator.prospects (
            prospect_id, campaign_id, territory_id, organization_id, contact_id, opportunity_id,
            name, domain, website, country, city, vertical, status, fit_score, priority,
            next_action, next_action_at, last_contact_at, metadata, created_at, updated_at
          ) VALUES (
            {_q(prospect_id)}, {_q(campaign_id)}, {_q(args.get('territory_id'))}, {_q(args.get('organization_id'))}, {_q(args.get('contact_id'))}, {_q(args.get('opportunity_id'))},
            {_q(name)}, {_q(args.get('domain'))}, {_q(args.get('website'))}, {_q(args.get('country'))}, {_q(args.get('city'))}, {_q(args.get('vertical'))}, {_q(args.get('status') or 'discovered')}, {_num(args.get('fit_score'))}, {_q(args.get('priority') or 'normal')},
            {_q(args.get('next_action'))}, {_q(args.get('next_action_at'))}, {_q(args.get('last_contact_at'))}, {_j(args.get('metadata') or {})}, now(), now()
          )
          ON CONFLICT (prospect_id) DO UPDATE SET
            campaign_id=EXCLUDED.campaign_id, territory_id=EXCLUDED.territory_id, organization_id=EXCLUDED.organization_id,
            contact_id=EXCLUDED.contact_id, opportunity_id=EXCLUDED.opportunity_id, name=EXCLUDED.name, domain=EXCLUDED.domain,
            website=EXCLUDED.website, country=EXCLUDED.country, city=EXCLUDED.city, vertical=EXCLUDED.vertical, status=EXCLUDED.status,
            fit_score=EXCLUDED.fit_score, priority=EXCLUDED.priority, next_action=EXCLUDED.next_action,
            next_action_at=EXCLUDED.next_action_at, last_contact_at=EXCLUDED.last_contact_at, metadata=EXCLUDED.metadata, updated_at=now()
          RETURNING *
        """, user=_user())
        return _ok(prospect=row)
    except Exception as exc:
        return _err(exc)


def _handle_research_record(args: dict, **_kwargs) -> str:
    try:
        prospect_id = str(args.get("prospect_id") or "").strip()
        summary = str(args.get("summary") or "").strip()
        if not prospect_id:
            raise ValueError("prospect_id is required")
        if not summary:
            raise ValueError("summary is required")
        row = sql.statement_one(f"""
          INSERT INTO sales_operator.research_snapshots (prospect_id, source_id, summary, pain_points, public_channels, comparison_arguments, evidence, researched_at, metadata)
          VALUES ({_q(prospect_id)}, {_q(args.get('source_id'))}, {_q(summary)}, {_j(args.get('pain_points') or [])}, {_j(args.get('public_channels') or [])}, {_j(args.get('comparison_arguments') or [])}, {_j(args.get('evidence') or [])}, COALESCE({_q(args.get('researched_at'))}::timestamptz, now()), {_j(args.get('metadata') or {})})
          RETURNING *
        """, user=_user())
        sql.psql(f"UPDATE sales_operator.prospects SET status=CASE WHEN status='discovered' THEN 'researched' ELSE status END, updated_at=now() WHERE prospect_id={_q(prospect_id)};", user=_user())
        return _ok(research=row)
    except Exception as exc:
        return _err(exc)


def _score_band(score: Any) -> str:
    value = float(score or 0)
    if value >= 80:
        return "hot"
    if value >= 60:
        return "warm"
    if value >= 35:
        return "watch"
    return "low"


def _handle_score_record(args: dict, **_kwargs) -> str:
    try:
        prospect_id = str(args.get("prospect_id") or "").strip()
        if not prospect_id:
            raise ValueError("prospect_id is required")
        score_value = args.get("score")
        score_literal = _num(score_value, "0")
        band = str(args.get("score_band") or _score_band(score_value))
        row = sql.statement_one(f"""
          INSERT INTO sales_operator.lead_scores (prospect_id, score, score_band, reasons, computed_at, metadata)
          VALUES ({_q(prospect_id)}, {score_literal}, {_q(band)}, {_j(args.get('reasons') or [])}, COALESCE({_q(args.get('computed_at'))}::timestamptz, now()), {_j(args.get('metadata') or {})})
          RETURNING *
        """, user=_user())
        sql.psql(f"UPDATE sales_operator.prospects SET fit_score={score_literal}, priority=CASE WHEN {_q(band)} IN ('hot','warm') THEN {_q(band)} ELSE priority END, updated_at=now() WHERE prospect_id={_q(prospect_id)};", user=_user())
        return _ok(score=row)
    except Exception as exc:
        return _err(exc)


def _handle_attack_plan_upsert(args: dict, **_kwargs) -> str:
    try:
        for field in ("campaign_id", "prospect_id", "message_body"):
            if not str(args.get(field) or "").strip():
                raise ValueError(f"{field} is required")
        attack_plan_id = args.get("attack_plan_id") or _slug("so-plan", f"{args['prospect_id']}-{args.get('primary_channel') or 'email'}")
        row = sql.statement_one(f"""
          INSERT INTO sales_operator.attack_plans (attack_plan_id, campaign_id, prospect_id, plan_status, primary_channel, message_subject, message_body, value_prop, objections, assets, next_step, metadata, created_at, updated_at)
          VALUES ({_q(attack_plan_id)}, {_q(args.get('campaign_id'))}, {_q(args.get('prospect_id'))}, {_q(args.get('plan_status') or 'draft')}, {_q(args.get('primary_channel') or 'email')}, {_q(args.get('message_subject'))}, {_q(args.get('message_body'))}, {_q(args.get('value_prop'))}, {_j(args.get('objections') or [])}, {_j(args.get('assets') or [])}, {_q(args.get('next_step'))}, {_j(args.get('metadata') or {})}, now(), now())
          ON CONFLICT (attack_plan_id) DO UPDATE SET plan_status=EXCLUDED.plan_status, primary_channel=EXCLUDED.primary_channel, message_subject=EXCLUDED.message_subject, message_body=EXCLUDED.message_body, value_prop=EXCLUDED.value_prop, objections=EXCLUDED.objections, assets=EXCLUDED.assets, next_step=EXCLUDED.next_step, metadata=EXCLUDED.metadata, updated_at=now()
          RETURNING *
        """, user=_user())
        return _ok(attack_plan=row)
    except Exception as exc:
        return _err(exc)


def _handle_outreach_enqueue(args: dict, **_kwargs) -> str:
    try:
        for field in ("campaign_id", "prospect_id", "channel", "message_body"):
            if not str(args.get(field) or "").strip():
                raise ValueError(f"{field} is required")
        policy = sql.one(f"SELECT * FROM sales_operator.channel_policies WHERE campaign_id={_q(args.get('campaign_id'))} AND channel={_q(args.get('channel'))}", user=_user())
        if not policy:
            raise ValueError("channel policy is required before outreach can be queued")
        policy_mode = str(policy.get("mode") or policy.get("status") or "draft_only")
        auto_send_allowed = policy_mode == "auto_send" and not bool(policy.get("requires_human_approval"))
        requires_approval = args.get("requires_approval")
        if requires_approval is None:
            requires_approval = not auto_send_allowed
        status = str(args.get("status") or "draft")
        if policy_mode in {"draft_only", "content_only", "research_only", "planned"} and status not in {"draft", "blocked"}:
            status = "draft"
        outreach_id = args.get("outreach_id") or _slug("so-outreach", f"{args['prospect_id']}-{args['channel']}-{args.get('scheduled_at') or 'draft'}")
        row = sql.statement_one(f"""
          INSERT INTO sales_operator.outreach_queue (outreach_id, campaign_id, prospect_id, attack_plan_id, channel, status, scheduled_at, message_subject, message_body, requires_approval, approval_status, provider_ref, metadata, created_at, updated_at)
          VALUES ({_q(outreach_id)}, {_q(args.get('campaign_id'))}, {_q(args.get('prospect_id'))}, {_q(args.get('attack_plan_id'))}, {_q(args.get('channel'))}, {_q(status)}, {_q(args.get('scheduled_at'))}, {_q(args.get('message_subject'))}, {_q(args.get('message_body'))}, {_bool(requires_approval, True)}, {_q(args.get('approval_status') or ('approved' if not requires_approval else 'pending'))}, {_q(args.get('provider_ref'))}, {_j({**(args.get('metadata') or {}), 'policy_mode': policy_mode})}, now(), now())
          ON CONFLICT (outreach_id) DO UPDATE SET status=EXCLUDED.status, scheduled_at=EXCLUDED.scheduled_at, message_subject=EXCLUDED.message_subject, message_body=EXCLUDED.message_body, requires_approval=EXCLUDED.requires_approval, approval_status=EXCLUDED.approval_status, provider_ref=EXCLUDED.provider_ref, metadata=EXCLUDED.metadata, updated_at=now()
          RETURNING *
        """, user=_user())
        return _ok(outreach=row, policy=policy, auto_send_allowed=auto_send_allowed)
    except Exception as exc:
        return _err(exc)


def _handle_outreach_attempt_record(args: dict, **_kwargs) -> str:
    try:
        channel = str(args.get("channel") or "").strip()
        if not channel:
            raise ValueError("channel is required")
        row = sql.statement_one(f"""
          INSERT INTO sales_operator.outreach_attempts (outreach_id, campaign_id, prospect_id, channel, direction, provider_status, outcome, evidence, occurred_at, notes, metadata)
          VALUES ({_q(args.get('outreach_id'))}, {_q(args.get('campaign_id'))}, {_q(args.get('prospect_id'))}, {_q(channel)}, {_q(args.get('direction') or 'outbound')}, {_q(args.get('provider_status') or 'recorded')}, {_q(args.get('outcome') or 'unknown')}, {_j(args.get('evidence') or {})}, COALESCE({_q(args.get('occurred_at'))}::timestamptz, now()), {_q(args.get('notes'))}, {_j(args.get('metadata') or {})})
          RETURNING *
        """, user=_user())
        if args.get("outreach_id"):
            sql.psql(f"UPDATE sales_operator.outreach_queue SET status={_q(args.get('queue_status') or 'sent')}, provider_ref=COALESCE(provider_ref, {_q(args.get('provider_ref'))}), updated_at=now() WHERE outreach_id={_q(args.get('outreach_id'))};", user=_user())
        if args.get("prospect_id"):
            status = "contacted" if str(args.get("outcome") or "").lower() in {"sent", "delivered", "replied", "effective_contact"} else None
            sql.psql(f"UPDATE sales_operator.prospects SET last_contact_at=now(), status=COALESCE({_q(status)}, status), updated_at=now() WHERE prospect_id={_q(args.get('prospect_id'))};", user=_user())
        return _ok(attempt=row)
    except Exception as exc:
        return _err(exc)


def _handle_daily_report_create(args: dict, **_kwargs) -> str:
    try:
        campaign_id = str(args.get("campaign_id") or "").strip()
        work_summary = str(args.get("work_summary") or "").strip()
        if not campaign_id:
            raise ValueError("campaign_id is required")
        if not work_summary:
            raise ValueError("work_summary is required")
        report_date = str(args.get("report_date") or date.today().isoformat())
        report_id = args.get("report_id") or _slug("so-report", f"{campaign_id}-{report_date}")
        row = sql.statement_one(f"""
          INSERT INTO sales_operator.daily_reports (report_id, campaign_id, report_date, work_summary, discoveries, actions_taken, learnings, blockers, next_actions, metrics, retrospective, created_at)
          VALUES ({_q(report_id)}, {_q(campaign_id)}, {_q(report_date)}, {_q(work_summary)}, {_j(args.get('discoveries') or [])}, {_j(args.get('actions_taken') or [])}, {_j(args.get('learnings') or [])}, {_j(args.get('blockers') or [])}, {_j(args.get('next_actions') or [])}, {_j(args.get('metrics') or {})}, {_q(args.get('retrospective'))}, now())
          ON CONFLICT (campaign_id, report_date) DO UPDATE SET work_summary=EXCLUDED.work_summary, discoveries=EXCLUDED.discoveries, actions_taken=EXCLUDED.actions_taken, learnings=EXCLUDED.learnings, blockers=EXCLUDED.blockers, next_actions=EXCLUDED.next_actions, metrics=EXCLUDED.metrics, retrospective=EXCLUDED.retrospective
          RETURNING *
        """, user=_user())
        return _ok(report=row)
    except Exception as exc:
        return _err(exc)


def _active_campaign_id(args: dict[str, Any]) -> str | None:
    if args.get("campaign_id"):
        return str(args.get("campaign_id"))
    row = sql.one("SELECT campaign_id FROM sales_operator.campaigns WHERE status='active' ORDER BY updated_at DESC, created_at DESC", user=_user())
    return row.get("campaign_id") if row else None


def _handle_dashboard_snapshot(args: dict, **_kwargs) -> str:
    try:
        campaign_id = _active_campaign_id(args)
        if not campaign_id:
            return _ok(db_backend="agent_core_postgres", campaign=None, summary={}, channels=[], territories=[], reports=[], prospects=[], graph=[])
        prospect_limit = _limit(args.get("prospect_limit"), 20, 100)
        report_limit = _limit(args.get("report_limit"), 14, 90)
        campaign = sql.one(f"SELECT * FROM sales_operator.campaigns WHERE campaign_id={_q(campaign_id)}", user=_user())
        summary = sql.one(f"""
          SELECT
            (SELECT count(*) FROM sales_operator.prospects WHERE campaign_id={_q(campaign_id)}) AS prospects,
            (SELECT count(*) FROM sales_operator.prospects WHERE campaign_id={_q(campaign_id)} AND status IN ('contacted','responded','qualified','won')) AS contacted_clients,
            (SELECT count(*) FROM sales_operator.research_snapshots r JOIN sales_operator.prospects p ON p.prospect_id=r.prospect_id WHERE p.campaign_id={_q(campaign_id)}) AS research_snapshots,
            (SELECT count(*) FROM sales_operator.attack_plans WHERE campaign_id={_q(campaign_id)}) AS attack_plans,
            (SELECT count(*) FROM sales_operator.outreach_queue WHERE campaign_id={_q(campaign_id)} AND status IN ('draft','approved','queued')) AS open_outreach,
            (SELECT count(*) FROM sales_operator.outreach_attempts WHERE campaign_id={_q(campaign_id)}) AS attempts,
            (SELECT count(*) FROM sales_operator.daily_reports WHERE campaign_id={_q(campaign_id)}) AS daily_reports,
            (SELECT count(*) FROM sales_operator.territories WHERE campaign_id={_q(campaign_id)}) AS territories
        """, user=_user())
        channels = sql.rows(f"SELECT channel, status, mode, daily_limit, requires_human_approval, notes, metadata FROM sales_operator.channel_policies WHERE campaign_id={_q(campaign_id)} ORDER BY channel", user=_user())
        territories = sql.rows(f"SELECT territory_id, country, city, vertical, status, priority, metadata FROM sales_operator.territories WHERE campaign_id={_q(campaign_id)} ORDER BY priority DESC, country, city, vertical", user=_user())
        reports = sql.rows(f"SELECT report_id, report_date, work_summary, discoveries, actions_taken, learnings, blockers, next_actions, metrics, retrospective, created_at FROM sales_operator.daily_reports WHERE campaign_id={_q(campaign_id)} ORDER BY report_date DESC LIMIT {report_limit}", user=_user())
        prospects = sql.rows(f"""
          SELECT
            p.prospect_id, p.name, p.domain, p.website, p.country, p.city, p.vertical, p.status, p.fit_score, p.priority,
            p.organization_id, p.contact_id, p.opportunity_id, p.next_action, p.next_action_at, p.last_contact_at, p.metadata,
            o.name AS organization_name, c.full_name AS contact_name, c.email AS contact_email, c.phone AS contact_phone,
            opp.stage AS opportunity_stage, opp.status AS opportunity_status, opp.value_amount AS opportunity_value,
            (SELECT count(*) FROM sales_operator.research_snapshots r WHERE r.prospect_id=p.prospect_id) AS research_count,
            (SELECT count(*) FROM sales_operator.outreach_attempts a WHERE a.prospect_id=p.prospect_id) AS attempt_count
          FROM sales_operator.prospects p
          LEFT JOIN crm.organizations o ON o.organization_id=p.organization_id
          LEFT JOIN crm.contacts c ON c.contact_id=p.contact_id
          LEFT JOIN crm.opportunities opp ON opp.opportunity_id=p.opportunity_id
          WHERE p.campaign_id={_q(campaign_id)}
          ORDER BY p.updated_at DESC
          LIMIT {prospect_limit}
        """, user=_user())
        graph = sql.rows(f"""
          SELECT report_date,
                 COALESCE(NULLIF(metrics->>'prospects_researched','')::numeric, 0) AS prospects_researched,
                 COALESCE(NULLIF(metrics->>'attacks_prepared','')::numeric, 0) AS attacks_prepared,
                 COALESCE(NULLIF(metrics->>'messages_sent','')::numeric, 0) AS messages_sent,
                 COALESCE(NULLIF(metrics->>'responses','')::numeric, 0) AS responses,
                 COALESCE(NULLIF(metrics->>'wins','')::numeric, 0) AS wins
          FROM sales_operator.daily_reports
          WHERE campaign_id={_q(campaign_id)}
          ORDER BY report_date ASC
          LIMIT {report_limit}
        """, user=_user())
        return _ok(db_backend="agent_core_postgres", campaign=campaign, summary=summary or {}, channels=channels, territories=territories, reports=reports, prospects=prospects, graph=graph)
    except Exception as exc:
        return _err(exc)


def _handle_status(args: dict, **_kwargs) -> str:
    try:
        counts = sql.one("""
          SELECT
            (SELECT count(*) FROM sales_operator.campaigns) AS campaigns,
            (SELECT count(*) FROM sales_operator.territories) AS territories,
            (SELECT count(*) FROM sales_operator.prospects) AS prospects,
            (SELECT count(*) FROM sales_operator.research_snapshots) AS research_snapshots,
            (SELECT count(*) FROM sales_operator.outreach_queue) AS outreach_queue,
            (SELECT count(*) FROM sales_operator.outreach_attempts) AS outreach_attempts,
            (SELECT count(*) FROM sales_operator.daily_reports) AS daily_reports
        """, user=_user())
        snapshot = _payload(_handle_dashboard_snapshot({"campaign_id": args.get("campaign_id"), "prospect_limit": 5, "report_limit": 5}))
        return _ok(db_backend="agent_core_postgres", counts=counts, active_campaign=snapshot.get("campaign"), summary=snapshot.get("summary"), channels=snapshot.get("channels"))
    except Exception as exc:
        return _err(exc)


def _handle_seed_empleado_uno(args: dict, **_kwargs) -> str:
    try:
        campaign_id = str(args.get("campaign_id") or "empleado-uno-1000-subscribers-q3-2026")
        campaign = _payload(_handle_campaign_upsert({
            "campaign_id": campaign_id,
            "product_id": "empleado-uno",
            "product_name": "Empleado.uno",
            "business_id": "sitiouno",
            "status": "active",
            "target_subscribers": args.get("target_subscribers", 1000),
            "target_deadline": args.get("target_deadline"),
            "budget_amount": args.get("budget_amount", 5000),
            "currency": "USD",
            "referral_code": args.get("referral_code") or "zeus",
            "bonus_offer": "Bono early adopter: 50% extra de créditos según el plan si confirma el registro por correo.",
            "positioning": "Empleado IA multicanal para pymes hispanohablantes. No vender como chatbot ni plataforma técnica.",
            "metadata": {
                "objective": "1000 subscribers in 3 months as stretch target",
                "source": "sales_operator_seed_empleado_uno",
                "initial_focus": ["Medellín clínicas/estética", "Lima restaurantes/delivery", "Bogotá educación/cursos", "CDMX restaurantes/clínicas"],
                "pricing_warning": "Resolve public pricing consistency before paid traffic.",
            },
        }))
        territories = []
        for country, city, vertical, priority in [
            ("Colombia", "Medellín", "clínicas/estética", 95),
            ("Perú", "Lima", "restaurantes/delivery", 90),
            ("Colombia", "Bogotá", "educación/cursos", 85),
            ("México", "CDMX", "restaurantes/clínicas", 80),
            ("Ecuador", "Quito", "inmobiliarias", 70),
        ]:
            territories.append(_payload(_handle_territory_upsert({"campaign_id": campaign_id, "country": country, "city": city, "vertical": vertical, "status": "active" if priority >= 90 else "planned", "priority": priority}))["territory"])
        policies = []
        for channel, status, mode, limit, approval, notes in [
            ("web_agent", "active", "inbound", 0, False, "La página de Empleado.uno ya tiene un agente que atiende y explica."),
            ("email", "active", "supervised_send", 25, True, "Enviar solo mensajes personalizados y registrar evidencia."),
            ("content_platforms", "active", "content_only", 5, False, "Artículos transparentes como creadores, sin testimonios falsos."),
            ("research_search", "active", "research_only", 0, False, "Búsqueda nativa/Tavily/fuentes públicas para enriquecer leads."),
            ("voice_sophie", "supervised", "supervised_send", 10, True, "Llamadas/citas con Jean solo para leads o partners interesados."),
            ("whatsapp_current", "draft_only", "draft_only", 0, True, "No usar como canal oficial masivo; preparar mensajes y activar solo si está aprobado."),
            ("whatsapp_official", "planned", "planned", 0, True, "Se activará cuando Meta Cloud API/WhatsApp oficial esté listo."),
        ]:
            policies.append(_payload(_handle_channel_policy_upsert({"campaign_id": campaign_id, "channel": channel, "status": status, "mode": mode, "daily_limit": limit, "requires_human_approval": approval, "notes": notes}))["policy"])
        sources = []
        for source_type, source_name, url in [
            ("website", "Empleado.uno web and vertical pages", "https://www.empleado.uno/"),
            ("comparison", "Comparativo público agregado a la web", "https://www.empleado.uno/"),
            ("public_search", "Google/search/public directories", None),
            ("content", "Early adopter articles and founder posts", None),
            ("partner", "Agencias que usan competidores", None),
        ]:
            sources.append(_payload(_handle_lead_source_upsert({"campaign_id": campaign_id, "source_type": source_type, "source_name": source_name, "url": url}))["source"])
        experiment = sql.statement_one(f"""
          INSERT INTO sales_operator.experiments (experiment_id, campaign_id, name, hypothesis, status, channel, metric, results, metadata, created_at, updated_at)
          VALUES ({_q('so-exp-empleado-uno-early-adopter')}, {_q(campaign_id)}, 'Early adopter 50% extra credits', 'El bono de 50% extra en créditos mejora confirmaciones por correo sin bajar precio público.', 'planned', 'email/content', 'confirmed_registrations', '{{}}'::jsonb, {_j({'bonus': '50_percent_extra_credits_manual_process'})}, now(), now())
          ON CONFLICT (experiment_id) DO UPDATE SET hypothesis=EXCLUDED.hypothesis, status=EXCLUDED.status, channel=EXCLUDED.channel, metric=EXCLUDED.metric, metadata=EXCLUDED.metadata, updated_at=now()
          RETURNING *
        """, user=_user())
        report = _payload(_handle_daily_report_create({
            "campaign_id": campaign_id,
            "report_date": args.get("report_date") or date.today().isoformat(),
            "work_summary": "Jornada 0: Sales Operator Core activado en modo supervisado. Se registró campaña Empleado.uno, territorios iniciales, canales activos, política fail-closed y bono early adopter.",
            "discoveries": ["La venta debe posicionarse como Empleado IA, no chatbot.", "Hay que estudiar el nuevo cuadro comparativo público de la web antes de mensajes masivos.", "WhatsApp oficial queda como canal planned; se arranca con búsqueda, contenido, web agent, email supervisado y voz/citas."],
            "actions_taken": ["Creada campaña base.", "Creadas políticas por canal.", "Creadas fuentes de leads y experimento de bono 50% extra créditos."],
            "learnings": ["El dashboard debe separar prospects investigados, clientes realmente contactados y cierres confirmados por Jean/correo."],
            "blockers": ["Resolver consistencia de precios antes de pauta paga fuerte.", "WhatsApp oficial pendiente."],
            "next_actions": ["Investigar comparativo público en la web.", "Construir primer lote de leads Medellín clínicas/estética.", "Publicar/registrar primeras ideas de artículos transparentes para early adopters."],
            "metrics": {"prospects_researched": 0, "attacks_prepared": 0, "messages_sent": 0, "responses": 0, "wins": 0},
            "retrospective": "Arranque correcto: primero control, medición y seguridad; luego volumen. No hay clientes contactados aún desde este módulo.",
        }))["report"]
        return _ok(campaign=campaign["campaign"], territories=territories, policies=policies, sources=sources, experiment=experiment, report=report)
    except Exception as exc:
        return _err(exc)


def _schema(name: str, description: str, props: dict, required: list[str] | None = None) -> dict:
    return {"type": "function", "function": {"name": name, "description": description, "parameters": {"type": "object", "properties": props, "required": required or []}}}


def _meta_props() -> dict[str, Any]:
    return {"metadata": {"type": "object", "description": SALES_OPERATOR_METADATA_DESCRIPTION}}


_COMMON_IDS = {
    "campaign_id": {"type": "string"},
    "prospect_id": {"type": "string"},
    "territory_id": {"type": "string"},
    "organization_id": {"type": "string"},
    "contact_id": {"type": "string"},
    "opportunity_id": {"type": "string"},
}

registry.register(name="sales_operator_status", toolset="sales_operator", schema=_schema("sales_operator_status", "Return Sales Operator Core health, counts, active campaign, channel policies and summary.", {"campaign_id": {"type": "string"}}), handler=_handle_status, check_fn=_check_sales_operator, emoji="📈")
registry.register(name="sales_operator_campaign_upsert", toolset="sales_operator", schema=_schema("sales_operator_campaign_upsert", "Create or update a Sales Operator campaign for a product.", {"campaign_id": {"type": "string"}, "product_id": {"type": "string"}, "product_name": {"type": "string"}, "business_id": {"type": "string"}, "status": {"type": "string"}, "target_subscribers": {"type": "integer"}, "target_deadline": {"type": "string"}, "budget_amount": {"type": "number"}, "currency": {"type": "string"}, "referral_code": {"type": "string"}, "bonus_offer": {"type": "string"}, "positioning": {"type": "string"}, **_meta_props()}, ["product_name"]), handler=_handle_campaign_upsert, check_fn=_check_sales_operator, emoji="📈")
registry.register(name="sales_operator_seed_empleado_uno", toolset="sales_operator", schema=_schema("sales_operator_seed_empleado_uno", "Seed the canonical Empleado.uno campaign, territories, channel policies, lead sources, experiment and initial daily report.", {"campaign_id": {"type": "string"}, "target_subscribers": {"type": "integer"}, "target_deadline": {"type": "string"}, "budget_amount": {"type": "number"}, "referral_code": {"type": "string"}, "report_date": {"type": "string"}}), handler=_handle_seed_empleado_uno, check_fn=_check_sales_operator, emoji="📈")
registry.register(name="sales_operator_territory_upsert", toolset="sales_operator", schema=_schema("sales_operator_territory_upsert", "Create or update a country/city/vertical territory for a campaign.", {"territory_id": {"type": "string"}, "campaign_id": {"type": "string"}, "country": {"type": "string"}, "city": {"type": "string"}, "vertical": {"type": "string"}, "status": {"type": "string"}, "priority": {"type": "integer"}, "source_notes": {"type": "string"}, **_meta_props()}, ["campaign_id", "country", "city", "vertical"]), handler=_handle_territory_upsert, check_fn=_check_sales_operator, emoji="📈")
registry.register(name="sales_operator_channel_policy_upsert", toolset="sales_operator", schema=_schema("sales_operator_channel_policy_upsert", "Create or update a channel policy. Outbound remains draft/supervised unless policy explicitly allows auto_send.", {"policy_id": {"type": "string"}, "campaign_id": {"type": "string"}, "channel": {"type": "string"}, "status": {"type": "string"}, "mode": {"type": "string"}, "daily_limit": {"type": "integer"}, "requires_human_approval": {"type": "boolean"}, "notes": {"type": "string"}, **_meta_props()}, ["campaign_id", "channel"]), handler=_handle_channel_policy_upsert, check_fn=_check_sales_operator, emoji="📈")
registry.register(name="sales_operator_lead_source_upsert", toolset="sales_operator", schema=_schema("sales_operator_lead_source_upsert", "Create or update a source used for public lead discovery or content/partner acquisition.", {"source_id": {"type": "string"}, "campaign_id": {"type": "string"}, "source_type": {"type": "string"}, "source_name": {"type": "string"}, "url": {"type": "string"}, "status": {"type": "string"}, "last_scanned_at": {"type": "string"}, **_meta_props()}, ["campaign_id", "source_type", "source_name"]), handler=_handle_lead_source_upsert, check_fn=_check_sales_operator, emoji="📈")
registry.register(name="sales_operator_prospect_upsert", toolset="sales_operator", schema=_schema("sales_operator_prospect_upsert", "Create or update a researched prospect linked to CRM Core IDs when available.", {"prospect_id": {"type": "string"}, **_COMMON_IDS, "name": {"type": "string"}, "domain": {"type": "string"}, "website": {"type": "string"}, "country": {"type": "string"}, "city": {"type": "string"}, "vertical": {"type": "string"}, "status": {"type": "string"}, "fit_score": {"type": "number"}, "priority": {"type": "string"}, "next_action": {"type": "string"}, "next_action_at": {"type": "string"}, "last_contact_at": {"type": "string"}, **_meta_props()}, ["campaign_id", "name"]), handler=_handle_prospect_upsert, check_fn=_check_sales_operator, emoji="📈")
registry.register(name="sales_operator_research_record", toolset="sales_operator", schema=_schema("sales_operator_research_record", "Record source-backed research for a prospect: summary, pain points, public channels, arguments and evidence.", {"prospect_id": {"type": "string"}, "source_id": {"type": "string"}, "summary": {"type": "string"}, "pain_points": {"type": "array", "items": {"type": "object"}}, "public_channels": {"type": "array", "items": {"type": "object"}}, "comparison_arguments": {"type": "array", "items": {"type": "object"}}, "evidence": {"type": "array", "items": {"type": "object"}}, "researched_at": {"type": "string"}, **_meta_props()}, ["prospect_id", "summary"]), handler=_handle_research_record, check_fn=_check_sales_operator, emoji="📈")
registry.register(name="sales_operator_score_record", toolset="sales_operator", schema=_schema("sales_operator_score_record", "Record a lead score and score reasons for a prospect.", {"prospect_id": {"type": "string"}, "score": {"type": "number"}, "score_band": {"type": "string"}, "reasons": {"type": "array", "items": {"type": "object"}}, "computed_at": {"type": "string"}, **_meta_props()}, ["prospect_id", "score"]), handler=_handle_score_record, check_fn=_check_sales_operator, emoji="📈")
registry.register(name="sales_operator_attack_plan_upsert", toolset="sales_operator", schema=_schema("sales_operator_attack_plan_upsert", "Create or update a personalized attack plan for one prospect.", {"attack_plan_id": {"type": "string"}, "campaign_id": {"type": "string"}, "prospect_id": {"type": "string"}, "plan_status": {"type": "string"}, "primary_channel": {"type": "string"}, "message_subject": {"type": "string"}, "message_body": {"type": "string"}, "value_prop": {"type": "string"}, "objections": {"type": "array", "items": {"type": "object"}}, "assets": {"type": "array", "items": {"type": "object"}}, "next_step": {"type": "string"}, **_meta_props()}, ["campaign_id", "prospect_id", "message_body"]), handler=_handle_attack_plan_upsert, check_fn=_check_sales_operator, emoji="📈")
registry.register(name="sales_operator_outreach_enqueue", toolset="sales_operator", schema=_schema("sales_operator_outreach_enqueue", "Queue a supervised/draft outreach item according to channel policy. Does not send by itself.", {"outreach_id": {"type": "string"}, "campaign_id": {"type": "string"}, "prospect_id": {"type": "string"}, "attack_plan_id": {"type": "string"}, "channel": {"type": "string"}, "status": {"type": "string"}, "scheduled_at": {"type": "string"}, "message_subject": {"type": "string"}, "message_body": {"type": "string"}, "requires_approval": {"type": "boolean"}, "approval_status": {"type": "string"}, "provider_ref": {"type": "string"}, **_meta_props()}, ["campaign_id", "prospect_id", "channel", "message_body"]), handler=_handle_outreach_enqueue, check_fn=_check_sales_operator, emoji="📈")
registry.register(name="sales_operator_outreach_attempt_record", toolset="sales_operator", schema=_schema("sales_operator_outreach_attempt_record", "Record provider/customer evidence for an outreach attempt. Provider ACK is not customer interest.", {"attempt_id": {"type": "integer"}, "outreach_id": {"type": "string"}, "campaign_id": {"type": "string"}, "prospect_id": {"type": "string"}, "channel": {"type": "string"}, "direction": {"type": "string"}, "provider_status": {"type": "string"}, "outcome": {"type": "string"}, "provider_ref": {"type": "string"}, "queue_status": {"type": "string"}, "evidence": {"type": "object"}, "occurred_at": {"type": "string"}, "notes": {"type": "string"}, **_meta_props()}, ["channel"]), handler=_handle_outreach_attempt_record, check_fn=_check_sales_operator, emoji="📈")
registry.register(name="sales_operator_daily_report_create", toolset="sales_operator", schema=_schema("sales_operator_daily_report_create", "Create or update the daily work report and retrospective for the Sales Operator campaign.", {"report_id": {"type": "string"}, "campaign_id": {"type": "string"}, "report_date": {"type": "string"}, "work_summary": {"type": "string"}, "discoveries": {"type": "array", "items": {"type": "object"}}, "actions_taken": {"type": "array", "items": {"type": "object"}}, "learnings": {"type": "array", "items": {"type": "object"}}, "blockers": {"type": "array", "items": {"type": "object"}}, "next_actions": {"type": "array", "items": {"type": "object"}}, "metrics": {"type": "object"}, "retrospective": {"type": "string"}}, ["campaign_id", "work_summary"]), handler=_handle_daily_report_create, check_fn=_check_sales_operator, emoji="📈")
registry.register(name="sales_operator_dashboard_snapshot", toolset="sales_operator", schema=_schema("sales_operator_dashboard_snapshot", "Return a safe dashboard snapshot for the active Sales Operator campaign, including summaries, channels, daily reports, graph data, and CRM-linked prospects.", {"campaign_id": {"type": "string"}, "prospect_limit": {"type": "integer"}, "report_limit": {"type": "integer"}}), handler=_handle_dashboard_snapshot, check_fn=_check_sales_operator, emoji="📈")

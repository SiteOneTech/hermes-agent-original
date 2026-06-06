"""Agent-native CRM tools backed by Agent Core DB, with optional Twenty adapter.

CRM Core is the canonical local source for Zeus-style agents.  External CRMs
(Twenty first, Odoo/Lago/etc. later) are adapters linked through
``crm.external_links``; agents should use these generic tools instead of binding
conversation logic directly to vendor object models.
"""
from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from hermes_cli import agent_core_sql as sql
from tools.registry import registry, tool_error


CRM_METADATA_DESCRIPTION = (
    "Optional JSON metadata. Keep it generic and tenant-neutral: business_id, "
    "owner_id, source_channel, external_ref, labels, notes."
)

SOCIAL_PROFILE_DESCRIPTION = (
    "Structured social/contact-channel profiles for this contact. Each item may "
    "include platform, handle, external_id/user_id, profile_url, display_name, "
    "is_primary, status, and metadata. Store personal social identities here; "
    "do not bury them only in metadata."
)


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------

def _ok(**fields: Any) -> str:
    return json.dumps({"ok": True, **fields}, ensure_ascii=False, sort_keys=True)


def _err(exc: Exception | str) -> str:
    return tool_error(str(exc))


def _check_crm() -> bool:
    try:
        if not sql.enabled():
            return False
        sql.psql("SELECT 1;", user=sql.runtime_env().get("CRM_DB_RUNTIME_USER", "crm_runtime"))
        return True
    except Exception:
        return False


def _user() -> str:
    return sql.runtime_env().get("CRM_DB_RUNTIME_USER", "crm_runtime")


def _q(v: Any) -> str:
    return sql.quote_literal(v)


def _j(v: Any) -> str:
    return sql.quote_jsonb(v)


def _stable_id(prefix: str, *parts: Any) -> str:
    material = "|".join(str(p or "") for p in parts)
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def _slug(prefix: str, value: str) -> str:
    return f"{prefix}-{sql.slugify(value)}"


def _num(v: Any, default: str = "NULL") -> str:
    if v is None or v == "":
        return default
    try:
        # Normalize to a PostgreSQL numeric literal and reject arbitrary text so
        # user-provided numbers cannot become SQL fragments.
        return repr(float(v))
    except (TypeError, ValueError):
        raise ValueError(f"Invalid numeric value: {v!r}")


def _limit(v: Any, default: int = 20, maximum: int = 100) -> int:
    try:
        n = int(v or default)
    except Exception:
        n = default
    return max(1, min(maximum, n))


def _bool_sql(v: Any, default: bool = False) -> str:
    if v is None or v == "":
        return "TRUE" if default else "FALSE"
    if isinstance(v, str):
        value = v.strip().lower()
        if value in {"1", "true", "yes", "y", "on"}:
            return "TRUE"
        if value in {"0", "false", "no", "n", "off"}:
            return "FALSE"
    return "TRUE" if bool(v) else "FALSE"


def _normalize_platform(value: Any) -> str:
    return str(value or "").strip().lower().lstrip("@")


def _normalize_handle(value: Any) -> str | None:
    raw = str(value or "").strip()
    return raw or None


def _social_profile_id(args: dict[str, Any]) -> str:
    return args.get("social_profile_id") or _stable_id(
        "social",
        args.get("contact_id"),
        _normalize_platform(args.get("platform")),
        args.get("external_id") or args.get("handle") or args.get("profile_url"),
    )


def _status_clause(status: str | None, alias: str = "") -> str:
    if not status:
        return "TRUE"
    prefix = f"{alias}." if alias else ""
    return f"{prefix}status = {_q(status)}"


def _link_external(local_type: str, local_id: str, provider: str, external_type: str,
                   external_id: str, external_url: str | None = None,
                   metadata: dict[str, Any] | None = None) -> dict[str, Any] | None:
    return sql.statement_one(f"""
      INSERT INTO crm.external_links (local_type, local_id, provider, external_type, external_id, external_url, sync_status, last_synced_at, metadata)
      VALUES ({_q(local_type)}, {_q(local_id)}, {_q(provider)}, {_q(external_type)}, {_q(external_id)}, {_q(external_url)}, 'linked', now(), {_j(metadata or {})})
      ON CONFLICT (local_type, local_id, provider, external_type)
      DO UPDATE SET external_id=EXCLUDED.external_id, external_url=EXCLUDED.external_url, sync_status='linked', last_synced_at=now(), metadata=EXCLUDED.metadata, updated_at=now()
      RETURNING *
    """, user=_user())


# ---------------------------------------------------------------------------
# Twenty adapter helpers
# ---------------------------------------------------------------------------

def _twenty_base_url() -> str:
    env = sql.runtime_env()
    return (env.get("TWENTY_BASE_URL") or env.get("CRM_TWENTY_BASE_URL") or os.getenv("TWENTY_BASE_URL") or "").rstrip("/")


def _twenty_api_key() -> str:
    env = sql.runtime_env()
    return env.get("TWENTY_API_KEY") or env.get("CRM_TWENTY_API_KEY") or os.getenv("TWENTY_API_KEY") or ""


def _twenty_enabled() -> bool:
    return bool(_twenty_base_url() and _twenty_api_key())


def _twenty_request(method: str, path: str, body: dict[str, Any] | None = None,
                    query: dict[str, Any] | None = None) -> dict[str, Any]:
    base = _twenty_base_url()
    key = _twenty_api_key()
    if not base or not key:
        return {"ok": False, "configured": False, "error": "Twenty adapter is not configured. Set TWENTY_BASE_URL and TWENTY_API_KEY via Infisical/runtime env."}

    url = f"{base}/{path.lstrip('/')}"
    if query:
        clean = {k: v for k, v in query.items() if v is not None}
        if clean:
            url += "?" + urllib.parse.urlencode(clean)
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json", "Accept": "application/json"}
    req = urllib.request.Request(url=url, method=method.upper(), data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            payload = json.loads(raw) if raw else None
            return {"ok": True, "status": resp.status, "url": url, "data": payload}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload: Any = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            payload = raw
        return {"ok": False, "status": exc.code, "url": url, "error": payload}
    except Exception as exc:
        return {"ok": False, "url": url, "error": str(exc)}


def _twenty_record_id(payload: Any) -> str | None:
    if isinstance(payload, dict):
        for key in ("id", "recordId"):
            if payload.get(key):
                return str(payload[key])
        for key in ("data", "createCompany", "updateCompany", "createPerson", "updatePerson", "createOpportunity", "updateOpportunity"):
            if key in payload:
                found = _twenty_record_id(payload[key])
                if found:
                    return found
        for value in payload.values():
            if isinstance(value, dict):
                found = _twenty_record_id(value)
                if found:
                    return found
    return None

def _twenty_link(value: Any) -> dict[str, Any] | None:
    if not value:
        return None
    url = str(value).strip()
    if not url:
        return None
    if "://" not in url:
        url = f"https://{url}"
    return {"primaryLinkLabel": "", "primaryLinkUrl": url, "secondaryLinks": []}


def _sync_twenty(local_type: str, local_id: str, external_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Create a record in Twenty and store the external link.

    Twenty generates schema-per-tenant REST endpoints; the object path is passed
    in as plural lower-case names such as ``companies`` or ``people``.
    """
    existing = sql.one(
        f"SELECT * FROM crm.external_links WHERE local_type={_q(local_type)} AND local_id={_q(local_id)} AND provider='twenty' AND external_type={_q(external_type)}",
        user=_user(),
    )
    if existing and existing.get("external_id"):
        result = _twenty_request("PATCH", f"/rest/{external_type}/{existing['external_id']}", payload)
        external_id = existing["external_id"]
    else:
        result = _twenty_request("POST", f"/rest/{external_type}", payload)
        external_id = _twenty_record_id(result.get("data"))

    if result.get("ok") and external_id:
        _link_external(local_type, local_id, "twenty", external_type, external_id, metadata={"payload": payload})
    return {"adapter": "twenty", "external_type": external_type, "external_id": external_id, "result": result}


# ---------------------------------------------------------------------------
# Core CRM handlers
# ---------------------------------------------------------------------------

def _handle_org_upsert(args: dict, **_kwargs) -> str:
    try:
        name = str(args.get("name") or "").strip()
        if not name:
            raise ValueError("name is required")
        oid = args.get("organization_id") or _slug("org", args.get("domain") or name)
        row = sql.statement_one(f"""
          INSERT INTO crm.organizations (organization_id, name, domain, phone, email, website, status, metadata, created_at, updated_at)
          VALUES ({_q(oid)}, {_q(name)}, {_q(args.get('domain'))}, {_q(args.get('phone'))}, {_q(args.get('email'))}, {_q(args.get('website'))}, {_q(args.get('status') or 'active')}, {_j(args.get('metadata') or {})}, now(), now())
          ON CONFLICT (organization_id) DO UPDATE SET name=EXCLUDED.name, domain=EXCLUDED.domain, phone=EXCLUDED.phone, email=EXCLUDED.email, website=EXCLUDED.website, status=EXCLUDED.status, metadata=EXCLUDED.metadata, updated_at=now()
          RETURNING *
        """, user=_user())
        sync = None
        if args.get("sync_twenty"):
            sync = _sync_twenty("organization", oid, "companies", {
                "name": name,
                "domainName": _twenty_link(args.get("website") or args.get("domain")),
                "address": args.get("metadata", {}).get("address") if isinstance(args.get("metadata"), dict) else None,
            })
        return _ok(organization=row, twenty=sync)
    except Exception as exc:
        return _err(exc)


def _handle_contact_social_upsert(args: dict, **_kwargs) -> str:
    try:
        contact_id = str(args.get("contact_id") or "").strip()
        platform = _normalize_platform(args.get("platform"))
        if not contact_id or not platform:
            raise ValueError("contact_id and platform are required")
        handle = _normalize_handle(args.get("handle"))
        external_id = str(args.get("external_id") or "").strip() or None
        profile_url = str(args.get("profile_url") or "").strip() or None
        if not any([handle, external_id, profile_url]):
            raise ValueError("handle, external_id, or profile_url is required")
        payload = {**args, "contact_id": contact_id, "platform": platform, "handle": handle, "external_id": external_id, "profile_url": profile_url}
        sid = _social_profile_id(payload)
        row = sql.statement_one(f"""
          INSERT INTO crm.contact_social_profiles (social_profile_id, contact_id, platform, handle, external_id, profile_url, display_name, status, is_primary, metadata, created_at, updated_at)
          VALUES ({_q(sid)}, {_q(contact_id)}, {_q(platform)}, {_q(handle)}, {_q(external_id)}, {_q(profile_url)}, {_q(args.get('display_name'))}, {_q(args.get('status') or 'active')}, {_bool_sql(args.get('is_primary'))}, {_j(args.get('metadata') or {})}, now(), now())
          ON CONFLICT (social_profile_id) DO UPDATE SET contact_id=EXCLUDED.contact_id, platform=EXCLUDED.platform, handle=EXCLUDED.handle, external_id=EXCLUDED.external_id, profile_url=EXCLUDED.profile_url, display_name=EXCLUDED.display_name, status=EXCLUDED.status, is_primary=EXCLUDED.is_primary, metadata=EXCLUDED.metadata, updated_at=now()
          RETURNING *
        """, user=_user())
        if args.get("is_primary"):
            social_profile_id = (row or {}).get("social_profile_id")
            sql.psql(f"""
              UPDATE crm.contact_social_profiles
              SET is_primary = FALSE, updated_at = now()
              WHERE contact_id={_q(contact_id)} AND platform={_q(platform)} AND social_profile_id <> {_q(social_profile_id)}
            """, user=_user())
        return _ok(social_profile=row)
    except Exception as exc:
        return _err(exc)


def _upsert_contact_social_profiles(contact_id: str, profiles: Any) -> list[dict[str, Any]]:
    if profiles in (None, ""):
        return []
    if not isinstance(profiles, list):
        raise ValueError("social_profiles must be a list")
    rows = []
    for profile in profiles:
        if not isinstance(profile, dict):
            raise ValueError("each social profile must be an object")
        payload = {**profile, "contact_id": profile.get("contact_id") or contact_id}
        result = json.loads(_handle_contact_social_upsert(payload))
        if not result.get("ok"):
            raise ValueError(result.get("error") or "failed to upsert social profile")
        rows.append(result["social_profile"])
    return rows


def _handle_contact_upsert(args: dict, **_kwargs) -> str:
    try:
        full_name = str(args.get("full_name") or "").strip()
        if not full_name:
            raise ValueError("full_name is required")
        cid = args.get("contact_id") or _slug("contact", args.get("email") or full_name)
        row = sql.statement_one(f"""
          INSERT INTO crm.contacts (contact_id, organization_id, full_name, email, phone, title, status, source, metadata, created_at, updated_at)
          VALUES ({_q(cid)}, {_q(args.get('organization_id'))}, {_q(full_name)}, {_q(args.get('email'))}, {_q(args.get('phone'))}, {_q(args.get('title'))}, {_q(args.get('status') or 'active')}, {_q(args.get('source'))}, {_j(args.get('metadata') or {})}, now(), now())
          ON CONFLICT (contact_id) DO UPDATE SET organization_id=EXCLUDED.organization_id, full_name=EXCLUDED.full_name, email=EXCLUDED.email, phone=EXCLUDED.phone, title=EXCLUDED.title, status=EXCLUDED.status, source=EXCLUDED.source, metadata=EXCLUDED.metadata, updated_at=now()
          RETURNING *
        """, user=_user())
        social_profiles = _upsert_contact_social_profiles(cid, args.get("social_profiles"))
        sync = None
        if args.get("sync_twenty"):
            first, _, last = full_name.partition(" ")
            sync = _sync_twenty("contact", cid, "people", {
                "name": {"firstName": first, "lastName": last},
                "emails": {"primaryEmail": args.get("email")} if args.get("email") else None,
                "phones": {"primaryPhoneNumber": args.get("phone")} if args.get("phone") else None,
                "jobTitle": args.get("title"),
            })
        return _ok(contact=row, social_profiles=social_profiles, twenty=sync)
    except Exception as exc:
        return _err(exc)


def _handle_opportunity_upsert(args: dict, **_kwargs) -> str:
    try:
        title = str(args.get("title") or "").strip()
        if not title:
            raise ValueError("title is required")
        oid = args.get("opportunity_id") or _slug("opp", f"{args.get('organization_id') or args.get('contact_id') or ''}-{title}")
        row = sql.statement_one(f"""
          INSERT INTO crm.opportunities (opportunity_id, organization_id, contact_id, title, stage, value_amount, currency, expected_close_date, status, metadata, created_at, updated_at)
          VALUES ({_q(oid)}, {_q(args.get('organization_id'))}, {_q(args.get('contact_id'))}, {_q(title)}, {_q(args.get('stage') or 'lead')}, {_num(args.get('value_amount'))}, {_q(args.get('currency') or 'USD')}, {_q(args.get('expected_close_date'))}::date, {_q(args.get('status') or 'open')}, {_j(args.get('metadata') or {})}, now(), now())
          ON CONFLICT (opportunity_id) DO UPDATE SET organization_id=EXCLUDED.organization_id, contact_id=EXCLUDED.contact_id, title=EXCLUDED.title, stage=EXCLUDED.stage, value_amount=EXCLUDED.value_amount, currency=EXCLUDED.currency, expected_close_date=EXCLUDED.expected_close_date, status=EXCLUDED.status, metadata=EXCLUDED.metadata, updated_at=now()
          RETURNING *
        """, user=_user())
        sync = None
        if args.get("sync_twenty"):
            local_stage = str(args.get("stage") or "lead").strip().lower()
            twenty_stage = {
                "lead": "NEW",
                "new": "NEW",
                "qualified": "SCREENING",
                "screening": "SCREENING",
                "meeting": "MEETING",
                "proposal": "PROPOSAL",
                "negotiation": "PROPOSAL",
                "won": "CUSTOMER",
                "customer": "CUSTOMER",
            }.get(local_stage, local_stage.upper())
            sync = _sync_twenty("opportunity", oid, "opportunities", {
                "name": title,
                "amount": {"amountMicros": int(float(args.get("value_amount") or 0) * 1_000_000), "currencyCode": args.get("currency") or "USD"},
                "stage": twenty_stage,
            })
        return _ok(opportunity=row, twenty=sync)
    except Exception as exc:
        return _err(exc)


def _handle_product_upsert(args: dict, **_kwargs) -> str:
    try:
        name = str(args.get("name") or "").strip()
        if not name:
            raise ValueError("name is required")
        pid = args.get("product_id") or _slug("product", args.get("sku") or name)
        row = sql.statement_one(f"""
          INSERT INTO crm.products (product_id, sku, name, description, unit_price, currency, status, metadata, created_at, updated_at)
          VALUES ({_q(pid)}, {_q(args.get('sku'))}, {_q(name)}, {_q(args.get('description'))}, {_num(args.get('unit_price'))}, {_q(args.get('currency') or 'USD')}, {_q(args.get('status') or 'active')}, {_j(args.get('metadata') or {})}, now(), now())
          ON CONFLICT (product_id) DO UPDATE SET sku=EXCLUDED.sku, name=EXCLUDED.name, description=EXCLUDED.description, unit_price=EXCLUDED.unit_price, currency=EXCLUDED.currency, status=EXCLUDED.status, metadata=EXCLUDED.metadata, updated_at=now()
          RETURNING *
        """, user=_user())
        return _ok(product=row)
    except Exception as exc:
        return _err(exc)


def _quote_totals(items: list[dict[str, Any]]) -> tuple[float, float, float]:
    subtotal = 0.0
    tax_amount = 0.0
    for item in items:
        qty = float(item.get("quantity") or 1)
        price = float(item.get("unit_price") or 0)
        tax_rate = float(item.get("tax_rate") or 0)
        line = qty * price
        subtotal += line
        tax_amount += line * tax_rate
    return subtotal, tax_amount, subtotal + tax_amount


def _handle_quote_create(args: dict, **_kwargs) -> str:
    try:
        title = str(args.get("title") or "").strip()
        if not title:
            raise ValueError("title is required")
        items = args.get("items") or []
        if not isinstance(items, list):
            raise ValueError("items must be a list")
        qid = args.get("quote_id") or _slug("quote", f"{args.get('organization_id') or args.get('contact_id') or ''}-{title}")
        subtotal, tax_amount, total = _quote_totals(items)
        quote = sql.statement_one(f"""
          INSERT INTO crm.quotes (quote_id, organization_id, contact_id, opportunity_id, title, status, valid_until, currency, subtotal, tax_amount, total, metadata, created_at, updated_at)
          VALUES ({_q(qid)}, {_q(args.get('organization_id'))}, {_q(args.get('contact_id'))}, {_q(args.get('opportunity_id'))}, {_q(title)}, {_q(args.get('status') or 'draft')}, {_q(args.get('valid_until'))}::date, {_q(args.get('currency') or 'USD')}, {subtotal}, {tax_amount}, {total}, {_j(args.get('metadata') or {})}, now(), now())
          ON CONFLICT (quote_id) DO UPDATE SET organization_id=EXCLUDED.organization_id, contact_id=EXCLUDED.contact_id, opportunity_id=EXCLUDED.opportunity_id, title=EXCLUDED.title, status=EXCLUDED.status, valid_until=EXCLUDED.valid_until, currency=EXCLUDED.currency, subtotal=EXCLUDED.subtotal, tax_amount=EXCLUDED.tax_amount, total=EXCLUDED.total, metadata=EXCLUDED.metadata, updated_at=now()
          RETURNING *
        """, user=_user())
        sql.psql(f"DELETE FROM crm.quote_items WHERE quote_id={_q(qid)};", user=_user())
        saved_items = []
        for item in items:
            qty = float(item.get("quantity") or 1)
            price = float(item.get("unit_price") or 0)
            tax_rate = float(item.get("tax_rate") or 0)
            line_total = qty * price * (1 + tax_rate)
            saved_items.append(sql.statement_one(f"""
              INSERT INTO crm.quote_items (quote_id, product_id, description, quantity, unit_price, tax_rate, line_total, metadata)
              VALUES ({_q(qid)}, {_q(item.get('product_id'))}, {_q(item.get('description') or item.get('name') or 'Item')}, {qty}, {price}, {tax_rate}, {line_total}, {_j(item.get('metadata') or {})})
              RETURNING *
            """, user=_user()))
        return _ok(quote=quote, items=saved_items)
    except Exception as exc:
        return _err(exc)


def _handle_invoice_create(args: dict, **_kwargs) -> str:
    try:
        title = str(args.get("title") or "").strip()
        if not title:
            quote_id = args.get("quote_id")
            if quote_id:
                qrow = sql.one(f"SELECT * FROM crm.quotes WHERE quote_id={_q(quote_id)}", user=_user())
                title = qrow.get("title") if qrow else "Invoice"
            else:
                title = "Invoice"
        iid = args.get("invoice_id") or _slug("invoice", f"{args.get('quote_id') or args.get('organization_id') or ''}-{title}")
        quote = sql.one(f"SELECT * FROM crm.quotes WHERE quote_id={_q(args.get('quote_id'))}", user=_user()) if args.get("quote_id") else None
        organization_id = args.get("organization_id") or (quote or {}).get("organization_id")
        contact_id = args.get("contact_id") or (quote or {}).get("contact_id")
        subtotal = args.get("subtotal", (quote or {}).get("subtotal", 0))
        tax_amount = args.get("tax_amount", (quote or {}).get("tax_amount", 0))
        total = args.get("total", (quote or {}).get("total", 0))
        row = sql.statement_one(f"""
          INSERT INTO crm.invoices (invoice_id, quote_id, organization_id, contact_id, title, status, issue_date, due_date, currency, subtotal, tax_amount, total, metadata, created_at, updated_at)
          VALUES ({_q(iid)}, {_q(args.get('quote_id'))}, {_q(organization_id)}, {_q(contact_id)}, {_q(title)}, {_q(args.get('status') or 'draft')}, COALESCE({_q(args.get('issue_date'))}::date, CURRENT_DATE), {_q(args.get('due_date'))}::date, {_q(args.get('currency') or (quote or {}).get('currency') or 'USD')}, {_num(subtotal, '0')}, {_num(tax_amount, '0')}, {_num(total, '0')}, {_j(args.get('metadata') or {})}, now(), now())
          ON CONFLICT (invoice_id) DO UPDATE SET quote_id=EXCLUDED.quote_id, organization_id=EXCLUDED.organization_id, contact_id=EXCLUDED.contact_id, title=EXCLUDED.title, status=EXCLUDED.status, issue_date=EXCLUDED.issue_date, due_date=EXCLUDED.due_date, currency=EXCLUDED.currency, subtotal=EXCLUDED.subtotal, tax_amount=EXCLUDED.tax_amount, total=EXCLUDED.total, metadata=EXCLUDED.metadata, updated_at=now()
          RETURNING *
        """, user=_user())
        return _ok(invoice=row)
    except Exception as exc:
        return _err(exc)


def _handle_relationship_upsert(args: dict, **_kwargs) -> str:
    try:
        for field in ("source_type", "source_id", "target_type", "target_id", "relationship_type"):
            if not args.get(field):
                raise ValueError(f"{field} is required")
        rid = args.get("relationship_id") or _slug("rel", f"{args['source_type']}-{args['source_id']}-{args['relationship_type']}-{args['target_type']}-{args['target_id']}")
        row = sql.statement_one(f"""
          INSERT INTO crm.relationships (relationship_id, source_type, source_id, target_type, target_id, relationship_type, strength, status, notes, metadata, created_at, updated_at)
          VALUES ({_q(rid)}, {_q(args.get('source_type'))}, {_q(args.get('source_id'))}, {_q(args.get('target_type'))}, {_q(args.get('target_id'))}, {_q(args.get('relationship_type'))}, {_num(args.get('strength'))}, {_q(args.get('status') or 'active')}, {_q(args.get('notes'))}, {_j(args.get('metadata') or {})}, now(), now())
          ON CONFLICT (source_type, source_id, target_type, target_id, relationship_type) DO UPDATE SET strength=EXCLUDED.strength, status=EXCLUDED.status, notes=EXCLUDED.notes, metadata=EXCLUDED.metadata, updated_at=now()
          RETURNING *
        """, user=_user())
        return _ok(relationship=row)
    except Exception as exc:
        return _err(exc)


def _handle_interaction_record(args: dict, **_kwargs) -> str:
    try:
        summary = str(args.get("summary") or "").strip()
        channel = str(args.get("channel") or "note").strip()
        if not summary:
            raise ValueError("summary is required")
        row = sql.statement_one(f"""
          INSERT INTO crm.interactions (organization_id, contact_id, opportunity_id, channel, direction, summary, occurred_at, actor, metadata)
          VALUES ({_q(args.get('organization_id'))}, {_q(args.get('contact_id'))}, {_q(args.get('opportunity_id'))}, {_q(channel)}, {_q(args.get('direction') or 'note')}, {_q(summary)}, COALESCE({_q(args.get('occurred_at'))}::timestamptz, now()), {_q(args.get('actor'))}, {_j(args.get('metadata') or {})})
          RETURNING *
        """, user=_user())
        follow_up = None
        follow_up_operation = None
        if args.get("follow_up_at") and args.get("follow_up_summary"):
            dedupe_key = _follow_up_dedupe_key({
                "organization_id": args.get("organization_id"),
                "contact_id": args.get("contact_id"),
                "opportunity_id": args.get("opportunity_id"),
                "summary": args.get("follow_up_summary"),
                "due_at": args.get("follow_up_at"),
            })
            fu_args = {
                "organization_id": args.get("organization_id"),
                "contact_id": args.get("contact_id"),
                "opportunity_id": args.get("opportunity_id"),
                "due_at": args.get("follow_up_at"),
                "summary": args.get("follow_up_summary"),
                "priority": args.get("follow_up_priority") or "normal",
                "assignee": args.get("actor"),
                "metadata": {"source_interaction_id": row.get("interaction_id") if row else None, "dedupe_key": dedupe_key},
            }
            existing = sql.one(f"""
              SELECT * FROM crm.follow_ups
              WHERE metadata @> {_j({"dedupe_key": dedupe_key})}::jsonb
              LIMIT 1
            """, user=_user())
            if existing:
                follow_up = existing
                follow_up_operation = "exists"
            else:
                fu_row = sql.statement_one(f"""
                  INSERT INTO crm.follow_ups (organization_id, contact_id, opportunity_id, due_at, summary, priority, assignee, metadata)
                  VALUES ({_q(args.get('organization_id'))}, {_q(args.get('contact_id'))}, {_q(args.get('opportunity_id'))}, {_q(args.get('follow_up_at'))}::timestamptz, {_q(args.get('follow_up_summary'))}, {_q(args.get('follow_up_priority') or 'normal')}, {_q(args.get('actor'))}, {_j({"source_interaction_id": row.get("interaction_id") if row else None, "dedupe_key": dedupe_key})})
                  RETURNING *
                """, user=_user())
                follow_up = fu_row
                follow_up_operation = "created"
        return _ok(interaction=row, follow_up=follow_up, follow_up_operation=follow_up_operation)
    except Exception as exc:
        return _err(exc)


def _follow_up_dedupe_key(args: dict) -> str:
    dedupe_parts = [args.get(k) for k in ("organization_id", "contact_id", "opportunity_id")]
    dedupe_parts.append(args.get("summary", ""))
    dedupe_parts.append(args.get("due_at", ""))
    return _stable_id("crm_fu", *dedupe_parts)


def _upsert_follow_up_by_dedupe(args: dict, dedupe_key: str, extra_metadata: dict | None = None) -> dict | None:
    """Look up an existing CRM follow-up by dedupe_key in metadata, or INSERT.

    Returns the row dict, or None on no-op.
    """
    existing = sql.one(f"""
      SELECT * FROM crm.follow_ups
      WHERE metadata @> {_j({"dedupe_key": dedupe_key})}::jsonb
      LIMIT 1
    """, user=_user())
    if existing:
        return existing

    metadata = dict(args.get("metadata") or {})
    metadata["dedupe_key"] = dedupe_key
    if extra_metadata:
        metadata.update(extra_metadata)

    return sql.statement_one(f"""
      INSERT INTO crm.follow_ups (organization_id, contact_id, opportunity_id, due_at, summary, status, priority, assignee, metadata, created_at, updated_at)
      VALUES ({_q(args.get('organization_id'))}, {_q(args.get('contact_id'))}, {_q(args.get('opportunity_id'))}, {_q(args.get('due_at'))}::timestamptz, {_q(args.get('summary'))}, {_q(args.get('status') or 'open')}, {_q(args.get('priority') or 'normal')}, {_q(args.get('assignee'))}, {_j(metadata)}, now(), now())
      RETURNING *
    """, user=_user())


def _find_activity_by_dedupe(dedupe_key: str) -> str | None:
    """Look up an activity in activity.activities by dedupe_key.

    Returns the activity_id or None if not found.
    """
    try:
        from tools import activity_tool
        result = json.loads(activity_tool._handle_activity_list({"dedupe_key": dedupe_key, "limit": 1}))
        if result.get("ok") and result.get("activities"):
            return result["activities"][0].get("activity_id")
    except Exception:
        pass
    return None


def _handle_follow_up_create(args: dict, **_kwargs) -> str:
    try:
        if not args.get("due_at") or not args.get("summary"):
            raise ValueError("due_at and summary are required")
        # Build a stable dedupe_key from CRM identifiers so repeated calls
        # with the same from-IDs + summary produce one row.
        dedupe_key = _follow_up_dedupe_key(args)

        existing = sql.one(f"""
          SELECT * FROM crm.follow_ups
          WHERE metadata @> {_j({"dedupe_key": dedupe_key})}::jsonb
          LIMIT 1
        """, user=_user())
        if existing:
            # Look up the activity that was created during the first call.
            # We stored dedupe_key in the activity's dedupe_key column, so
            # we can find it via activity_tool._handle_activity_list.
            existing_activity_id = _find_activity_by_dedupe(dedupe_key)
            return _ok(
                follow_up=existing,
                activity_id=existing_activity_id,
                operation="exists",
                dedupe_key=dedupe_key,
            )

        metadata = dict(args.get("metadata") or {})
        metadata["dedupe_key"] = dedupe_key

        row = sql.statement_one(f"""
          INSERT INTO crm.follow_ups (organization_id, contact_id, opportunity_id, due_at, summary, status, priority, assignee, metadata, created_at, updated_at)
          VALUES ({_q(args.get('organization_id'))}, {_q(args.get('contact_id'))}, {_q(args.get('opportunity_id'))}, {_q(args.get('due_at'))}::timestamptz, {_q(args.get('summary'))}, {_q(args.get('status') or 'open')}, {_q(args.get('priority') or 'normal')}, {_q(args.get('assignee'))}, {_j(metadata)}, now(), now())
          RETURNING *
        """, user=_user())

        backref = {"crm_follow_up_id": row.get("follow_up_id"), "crm_table": "crm.follow_ups"}
        activity_metadata = {
            **backref,
            **(args.get("metadata") or {}),
        }
        link_metadata = {
            "crm_follow_up_id": row.get("follow_up_id"),
            "crm_table": "crm.follow_ups",
            "source": "crm_follow_up_create",
        }

        # Bridge to universal Activity Layer: create an activity + link it back to
        # the CRM follow-up as a legacy_follow_up reference.
        # Import lazily so module-level circular deps don't block loading.
        from tools import activity_tool

        act_payload = json.loads(activity_tool._handle_activity_upsert({
            "activity_type": "follow_up",
            "title": args.get("summary"),
            "description": args.get("summary"),
            "status": args.get("status") or "open",
            "priority": args.get("priority") or "normal",
            "due_at": args.get("due_at"),
            "assignee_id": args.get("assignee"),
            "owner_id": args.get("assignee") or args.get("actor", "zeus"),
            "source": "crm",
            "source_ref": f"crm.follow_ups/{row.get('follow_up_id')}",
            "dedupe_key": dedupe_key,
            "metadata": activity_metadata,
            "evidence": {"crm_bridge": "crm_follow_up_create", "crm_follow_up_id": row.get("follow_up_id")},
        }))
        if act_payload.get("ok"):
            activity_id = act_payload.get("activity_id")
            link_payload = {
                "activity_id": activity_id,
                "target_type": "custom",
                "target_id": f"crm.follow_ups/{row.get('follow_up_id')}",
                "relationship_type": "legacy_follow_up",
                "target_schema": "crm",
                "target_table": "follow_ups",
                "metadata": link_metadata,
            }
            activity_tool._handle_activity_link(link_payload)
            # Also link the activity to each CRM entity present so that
            # crm_customer_timeline (which queries activity_timeline by
            # target_type="contact"/"organization"/"opportunity") can find it.
            for entity_type, entity_id in [
                ("contact", args.get("contact_id")),
                ("organization", args.get("organization_id")),
                ("opportunity", args.get("opportunity_id")),
            ]:
                if entity_id:
                    activity_tool._handle_activity_link({
                        "activity_id": activity_id,
                        "target_type": entity_type,
                        "target_id": entity_id,
                        "relationship_type": "context",
                        "metadata": {"crm_bridge": "crm_follow_up_create", "crm_follow_up_id": row.get("follow_up_id")},
                    })

        return _ok(
            follow_up=row,
            activity_id=(act_payload or {}).get("activity_id"),
            operation="created",
            dedupe_key=dedupe_key,
        )
    except Exception as exc:
        return _err(exc)


def _handle_crm_search(args: dict, **_kwargs) -> str:
    try:
        query = str(args.get("query") or "").strip()
        limit = _limit(args.get("limit"))
        pattern = f"%{query}%"
        contacts = sql.rows(f"""
          SELECT DISTINCT c.*
          FROM crm.contacts c
          LEFT JOIN crm.contact_social_profiles sp ON sp.contact_id = c.contact_id
          WHERE ({_q(query)} = ''
             OR c.full_name ILIKE {_q(pattern)}
             OR c.email ILIKE {_q(pattern)}
             OR c.phone ILIKE {_q(pattern)}
             OR sp.handle ILIKE {_q(pattern)}
             OR sp.external_id ILIKE {_q(pattern)}
             OR sp.platform ILIKE {_q(pattern)})
          ORDER BY c.updated_at DESC
          LIMIT {limit}
        """, user=_user())
        orgs = sql.rows(f"SELECT * FROM crm.organizations WHERE ({_q(query)} = '' OR name ILIKE {_q(pattern)} OR domain ILIKE {_q(pattern)} OR email ILIKE {_q(pattern)}) ORDER BY updated_at DESC LIMIT {limit}", user=_user())
        opportunities = sql.rows(f"SELECT * FROM crm.opportunities WHERE ({_q(query)} = '' OR title ILIKE {_q(pattern)}) ORDER BY updated_at DESC LIMIT {limit}", user=_user())
        products = sql.rows(f"SELECT * FROM crm.products WHERE ({_q(query)} = '' OR name ILIKE {_q(pattern)} OR sku ILIKE {_q(pattern)}) ORDER BY updated_at DESC LIMIT {limit}", user=_user())
        return _ok(contacts=contacts, organizations=orgs, opportunities=opportunities, products=products)
    except Exception as exc:
        return _err(exc)


def _handle_customer_timeline(args: dict, **_kwargs) -> str:
    try:
        org = args.get("organization_id")
        contact = args.get("contact_id")
        opportunity = args.get("opportunity_id")
        if not any([org, contact, opportunity]):
            raise ValueError("organization_id, contact_id, or opportunity_id is required")
        limit = _limit(args.get("limit"), default=50, maximum=200)
        where = []
        if org:
            where.append(f"organization_id={_q(org)}")
        if contact:
            where.append(f"contact_id={_q(contact)}")
        if opportunity:
            where.append(f"opportunity_id={_q(opportunity)}")
        condition = " OR ".join(where)
        interactions = sql.rows(f"SELECT * FROM crm.interactions WHERE {condition} ORDER BY occurred_at DESC LIMIT {limit}", user=_user())
        opportunities = sql.rows(f"SELECT * FROM crm.opportunities WHERE {condition} ORDER BY updated_at DESC LIMIT {limit}", user=_user())
        quotes = sql.rows(f"SELECT * FROM crm.quotes WHERE {condition} ORDER BY updated_at DESC LIMIT {limit}", user=_user())
        invoices = sql.rows(f"SELECT * FROM crm.invoices WHERE ({' OR '.join([w for w in where if 'opportunity_id' not in w]) or 'FALSE'}) ORDER BY updated_at DESC LIMIT {limit}", user=_user())
        follow_ups = sql.rows(f"SELECT * FROM crm.follow_ups WHERE {condition} ORDER BY due_at ASC LIMIT {limit}", user=_user())
        relationships = sql.rows(f"SELECT * FROM crm.relationships WHERE (source_id IN ({_q(org)}, {_q(contact)}, {_q(opportunity)}) OR target_id IN ({_q(org)}, {_q(contact)}, {_q(opportunity)})) ORDER BY updated_at DESC LIMIT {limit}", user=_user())
        social_profiles = []
        if contact:
            social_profiles = sql.rows(f"SELECT * FROM crm.contact_social_profiles WHERE contact_id={_q(contact)} ORDER BY is_primary DESC, updated_at DESC LIMIT {limit}", user=_user())
        # Also pull activity-layer activities linked to the same CRM entities.
        # Use the activity_timeline helper for consistency.
        from tools import activity_tool
        timeline_candidates = []
        for entity_type, entity_id in [("contact", contact), ("organization", org), ("opportunity", opportunity)]:
            if entity_id:
                try:
                    tl = json.loads(activity_tool._handle_activity_timeline({"target_type": entity_type, "target_id": entity_id, "limit": limit}))
                    if tl.get("ok"):
                        timeline_candidates.extend(tl.get("activities", []))
                except Exception:
                    pass
        activities = sorted(timeline_candidates, key=lambda a: a.get("due_at") or a.get("updated_at") or "", reverse=True)[:limit]
        return _ok(interactions=interactions, opportunities=opportunities, quotes=quotes, invoices=invoices, follow_ups=follow_ups, relationships=relationships, social_profiles=social_profiles, activities=activities)
    except Exception as exc:
        return _err(exc)


def _handle_crm_status(args: dict, **_kwargs) -> str:
    try:
        counts = sql.one("""
          SELECT
            (SELECT count(*) FROM crm.organizations) AS organizations,
            (SELECT count(*) FROM crm.contacts) AS contacts,
            (SELECT count(*) FROM crm.contact_social_profiles) AS contact_social_profiles,
            (SELECT count(*) FROM crm.opportunities) AS opportunities,
            (SELECT count(*) FROM crm.interactions) AS interactions,
            (SELECT count(*) FROM crm.relationships) AS relationships,
            (SELECT count(*) FROM crm.products) AS products,
            (SELECT count(*) FROM crm.quotes) AS quotes,
            (SELECT count(*) FROM crm.invoices) AS invoices,
            (SELECT count(*) FROM crm.follow_ups WHERE status='open') AS open_follow_ups,
            (SELECT count(*) FROM crm.external_links) AS external_links
        """, user=_user())
        return _ok(db_backend="agent_core_postgres", counts=counts, adapters={"twenty": {"configured": _twenty_enabled(), "base_url": _twenty_base_url() or None}})
    except Exception as exc:
        return _err(exc)


def _handle_twenty_sync(args: dict, **_kwargs) -> str:
    try:
        local_type = str(args.get("local_type") or "")
        local_id = str(args.get("local_id") or "")
        if not local_id:
            raise ValueError("local_id is required")
        if local_type == "organization":
            row = sql.one(f"SELECT * FROM crm.organizations WHERE organization_id={_q(local_id)}", user=_user())
            if not row:
                raise ValueError("organization not found")
            sync = _sync_twenty("organization", local_id, "companies", {"name": row["name"], "domainName": row.get("domain") or row.get("website")})
        elif local_type == "contact":
            row = sql.one(f"SELECT * FROM crm.contacts WHERE contact_id={_q(local_id)}", user=_user())
            if not row:
                raise ValueError("contact not found")
            first, _, last = row["full_name"].partition(" ")
            sync = _sync_twenty("contact", local_id, "people", {"name": {"firstName": first, "lastName": last}, "emails": {"primaryEmail": row.get("email")} if row.get("email") else None, "phones": {"primaryPhoneNumber": row.get("phone")} if row.get("phone") else None, "jobTitle": row.get("title")})
        elif local_type == "opportunity":
            row = sql.one(f"SELECT * FROM crm.opportunities WHERE opportunity_id={_q(local_id)}", user=_user())
            if not row:
                raise ValueError("opportunity not found")
            sync = _sync_twenty("opportunity", local_id, "opportunities", {"name": row["title"], "stage": row.get("stage")})
        else:
            raise ValueError("local_type must be organization, contact, or opportunity")
        return _ok(sync=sync)
    except Exception as exc:
        return _err(exc)


# ---------------------------------------------------------------------------
# Tool schemas / registration
# ---------------------------------------------------------------------------

def _schema(name: str, description: str, props: dict, required: list[str] | None = None) -> dict:
    return {"type": "function", "function": {"name": name, "description": description, "parameters": {"type": "object", "properties": props, "required": required or []}}}


def _meta_props() -> dict[str, Any]:
    return {"metadata": {"type": "object", "description": CRM_METADATA_DESCRIPTION}}


def _social_profile_props() -> dict[str, Any]:
    return {
        "social_profile_id": {"type": "string"},
        "contact_id": {"type": "string"},
        "platform": {"type": "string", "description": "Social platform/channel, e.g. telegram, whatsapp, x, linkedin, instagram."},
        "handle": {"type": "string"},
        "external_id": {"type": "string", "description": "Platform user_id/chat_id or other stable external identifier."},
        "profile_url": {"type": "string"},
        "display_name": {"type": "string"},
        "status": {"type": "string"},
        "is_primary": {"type": "boolean"},
        **_meta_props(),
    }


registry.register(name="crm_status", toolset="crm", schema=_schema("crm_status", "Return CRM Core row counts, DB backend, and adapter configuration status.", {}), handler=_handle_crm_status, check_fn=_check_crm, emoji="👥")
registry.register(name="crm_organization_upsert", toolset="crm", schema=_schema("crm_organization_upsert", "Create or update a CRM organization/company in Agent Core DB. Optionally sync to Twenty.", {"organization_id": {"type": "string"}, "name": {"type": "string"}, "domain": {"type": "string"}, "phone": {"type": "string"}, "email": {"type": "string"}, "website": {"type": "string"}, "status": {"type": "string"}, "sync_twenty": {"type": "boolean"}, **_meta_props()}, ["name"]), handler=_handle_org_upsert, check_fn=_check_crm, emoji="👥")
registry.register(name="crm_contact_social_upsert", toolset="crm", schema=_schema("crm_contact_social_upsert", "Create or update a structured social/contact-channel profile for a CRM contact.", _social_profile_props(), ["contact_id", "platform"]), handler=_handle_contact_social_upsert, check_fn=_check_crm, emoji="👥")
registry.register(name="crm_contact_upsert", toolset="crm", schema=_schema("crm_contact_upsert", "Create or update a CRM contact/person. Use organization_id to attach it to a company. Optionally sync to Twenty.", {"contact_id": {"type": "string"}, "organization_id": {"type": "string"}, "full_name": {"type": "string"}, "email": {"type": "string"}, "phone": {"type": "string"}, "title": {"type": "string"}, "status": {"type": "string"}, "source": {"type": "string"}, "social_profiles": {"type": "array", "description": SOCIAL_PROFILE_DESCRIPTION, "items": {"type": "object", "properties": _social_profile_props()}}, "sync_twenty": {"type": "boolean"}, **_meta_props()}, ["full_name"]), handler=_handle_contact_upsert, check_fn=_check_crm, emoji="👥")
registry.register(name="crm_opportunity_upsert", toolset="crm", schema=_schema("crm_opportunity_upsert", "Create or update a sales opportunity/pipeline record.", {"opportunity_id": {"type": "string"}, "organization_id": {"type": "string"}, "contact_id": {"type": "string"}, "title": {"type": "string"}, "stage": {"type": "string"}, "value_amount": {"type": "number"}, "currency": {"type": "string"}, "expected_close_date": {"type": "string", "description": "YYYY-MM-DD"}, "status": {"type": "string"}, "sync_twenty": {"type": "boolean"}, **_meta_props()}, ["title"]), handler=_handle_opportunity_upsert, check_fn=_check_crm, emoji="👥")
registry.register(name="crm_product_upsert", toolset="crm", schema=_schema("crm_product_upsert", "Create or update a product/service catalog item for quotes and invoices.", {"product_id": {"type": "string"}, "sku": {"type": "string"}, "name": {"type": "string"}, "description": {"type": "string"}, "unit_price": {"type": "number"}, "currency": {"type": "string"}, "status": {"type": "string"}, **_meta_props()}, ["name"]), handler=_handle_product_upsert, check_fn=_check_crm, emoji="👥")
registry.register(name="crm_quote_create", toolset="crm", schema=_schema("crm_quote_create", "Create or replace a quote with line items. Totals are computed from items.", {"quote_id": {"type": "string"}, "organization_id": {"type": "string"}, "contact_id": {"type": "string"}, "opportunity_id": {"type": "string"}, "title": {"type": "string"}, "status": {"type": "string"}, "valid_until": {"type": "string", "description": "YYYY-MM-DD"}, "currency": {"type": "string"}, "items": {"type": "array", "items": {"type": "object"}}, **_meta_props()}, ["title"]), handler=_handle_quote_create, check_fn=_check_crm, emoji="👥")
registry.register(name="crm_invoice_create", toolset="crm", schema=_schema("crm_invoice_create", "Create or update an invoice, optionally from an existing quote.", {"invoice_id": {"type": "string"}, "quote_id": {"type": "string"}, "organization_id": {"type": "string"}, "contact_id": {"type": "string"}, "title": {"type": "string"}, "status": {"type": "string"}, "issue_date": {"type": "string", "description": "YYYY-MM-DD"}, "due_date": {"type": "string", "description": "YYYY-MM-DD"}, "currency": {"type": "string"}, "subtotal": {"type": "number"}, "tax_amount": {"type": "number"}, "total": {"type": "number"}, **_meta_props()}), handler=_handle_invoice_create, check_fn=_check_crm, emoji="👥")
registry.register(name="crm_relationship_upsert", toolset="crm", schema=_schema("crm_relationship_upsert", "Record a relationship edge between CRM objects (e.g. partner, decision-maker, competitor, owner, referral).", {"relationship_id": {"type": "string"}, "source_type": {"type": "string"}, "source_id": {"type": "string"}, "target_type": {"type": "string"}, "target_id": {"type": "string"}, "relationship_type": {"type": "string"}, "strength": {"type": "number"}, "status": {"type": "string"}, "notes": {"type": "string"}, **_meta_props()}, ["source_type", "source_id", "target_type", "target_id", "relationship_type"]), handler=_handle_relationship_upsert, check_fn=_check_crm, emoji="👥")
registry.register(name="crm_interaction_record", toolset="crm", schema=_schema("crm_interaction_record", "Record a CRM interaction/note/call/message and optionally schedule a follow-up.", {"organization_id": {"type": "string"}, "contact_id": {"type": "string"}, "opportunity_id": {"type": "string"}, "channel": {"type": "string"}, "direction": {"type": "string"}, "summary": {"type": "string"}, "occurred_at": {"type": "string"}, "actor": {"type": "string"}, "follow_up_at": {"type": "string"}, "follow_up_summary": {"type": "string"}, "follow_up_priority": {"type": "string"}, **_meta_props()}, ["summary"]), handler=_handle_interaction_record, check_fn=_check_crm, emoji="👥")
registry.register(name="crm_follow_up_create", toolset="crm", schema=_schema("crm_follow_up_create", "Create a follow-up task tied to a contact, organization, or opportunity.", {"organization_id": {"type": "string"}, "contact_id": {"type": "string"}, "opportunity_id": {"type": "string"}, "due_at": {"type": "string"}, "summary": {"type": "string"}, "status": {"type": "string"}, "priority": {"type": "string"}, "assignee": {"type": "string"}, **_meta_props()}, ["due_at", "summary"]), handler=_handle_follow_up_create, check_fn=_check_crm, emoji="👥")
registry.register(name="crm_customer_timeline", toolset="crm", schema=_schema("crm_customer_timeline", "Return the relationship timeline for a customer/contact/opportunity: interactions, opportunities, quotes, invoices, follow-ups, relationships.", {"organization_id": {"type": "string"}, "contact_id": {"type": "string"}, "opportunity_id": {"type": "string"}, "limit": {"type": "integer"}}), handler=_handle_customer_timeline, check_fn=_check_crm, emoji="👥")
registry.register(name="crm_search", toolset="crm", schema=_schema("crm_search", "Search CRM contacts, organizations, opportunities, and products.", {"query": {"type": "string"}, "limit": {"type": "integer"}}), handler=_handle_crm_search, check_fn=_check_crm, emoji="👥")
registry.register(name="crm_twenty_sync", toolset="crm", schema=_schema("crm_twenty_sync", "Sync a local organization/contact/opportunity to the configured Twenty workspace and store the external link.", {"local_type": {"type": "string", "enum": ["organization", "contact", "opportunity"]}, "local_id": {"type": "string"}}, ["local_type", "local_id"]), handler=_handle_twenty_sync, check_fn=_check_crm, emoji="👥")
registry.register(name="crm_twenty_raw_request", toolset="crm", schema=_schema("crm_twenty_raw_request", "Advanced escape hatch for Twenty REST endpoints. Use only after preferring canonical CRM tools.", {"method": {"type": "string", "enum": ["GET", "POST", "PATCH", "DELETE"]}, "path": {"type": "string"}, "body": {"type": "object"}, "query": {"type": "object"}}, ["method", "path"]), handler=lambda args, **_kw: json.dumps(_twenty_request(args["method"], args["path"], args.get("body"), args.get("query")), ensure_ascii=False, sort_keys=True), check_fn=_check_crm, emoji="👥")

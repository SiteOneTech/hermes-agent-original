from scripts.runtime import sales_operator_i7_pilot_smoke as smoke


def test_i7_fixture_pack_is_synthetic_and_non_contactable():
    leads = smoke.fixture_leads()

    assert len(leads) == 10
    assert {lead["country"] for lead in leads} == {"Colombia"}
    assert {lead["city"] for lead in leads} == {"Medellín"}
    assert {lead["vertical"] for lead in leads} == {"clínicas/estética"}
    assert all(lead["domain"].endswith(".test") for lead in leads)
    assert all(lead["website"].startswith("https://i7-") for lead in leads)
    assert all(lead["prospect_id"].startswith("so-prospect-i7-") for lead in leads)


def test_i7_metadata_marks_every_lead_as_no_send_fixture():
    lead = smoke.fixture_leads()[0]
    metadata = smoke._lead_metadata(lead)

    assert metadata["i7_smoke"] is True
    assert metadata["synthetic_pilot_fixture"] is True
    assert metadata["not_real_business"] is True
    assert metadata["external_outbound_allowed"] is False
    assert "do not contact" in metadata["uncertainty"]


def test_i7_assertion_rejects_external_send_evidence():
    try:
        smoke._assert_no_external_send(
            {
                "external_sends": True,
                "external_actions_invoked": ["email_send"],
                "daily_dry_run": {"metrics": {"external_messages_sent_by_dry_run": 1}},
            }
        )
    except AssertionError as exc:
        assert "external_sends=false" in str(exc) or "Forbidden external actions" in str(exc)
    else:  # pragma: no cover - explicit guardrail failure path
        raise AssertionError("I7 smoke accepted external send evidence")


def test_i7_render_markdown_reports_no_send_summary():
    evidence = {
        "campaign_id": smoke.DEFAULT_CAMPAIGN_ID,
        "generated_at": "2026-07-12T00:00:00+00:00",
        "verification": {
            "prospects_upserted": 10,
            "research_snapshots_created": 10,
            "scores_created": 10,
            "attack_plans_created": 10,
            "draft_outreach_queued": 10,
            "crm_readback": {"timeline_follow_ups": 1, "organization_id": "org-i7-pilot-clinica-aurora"},
        },
    }

    rendered = smoke.render_markdown(evidence)

    assert "dry-run / no-send" in rendered
    assert "Prospects upserted: **10**" in rendered
    assert "Providers called: **none**" in rendered

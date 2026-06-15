from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_zeus_dashboard_custom_routes_and_branding_are_present():
    app = (ROOT / "web/src/App.tsx").read_text(encoding="utf-8")
    index = (ROOT / "web/index.html").read_text(encoding="utf-8")

    assert "Zeus Agent - Dashboard" in index
    assert "const FACTORY_NAV_ITEM" in app
    assert "partitionSidebarNav(builtinNav, manifests, [FACTORY_NAV_ITEM])" in app
    # Factory belongs under Plugins as a built-in plugin item, not in the core nav.
    core_nav = app.split("const builtinNav", 1)[1].split("const FACTORY_NAV_ITEM", 1)[0]
    assert 'to: "/factory"' not in core_nav


def test_profiles_page_surfaces_profile_capabilities_as_compact_disclosures():
    profiles = (ROOT / "web/src/pages/ProfilesPage.tsx").read_text(encoding="utf-8")
    api = (ROOT / "web/src/lib/api.ts").read_text(encoding="utf-8")

    assert '"profile-su"' in profiles
    assert "ProfileCapabilityDisclosure" in profiles
    assert "profileCapabilitySummary" in profiles
    assert "data-profile-capabilities" in profiles
    assert "data-profile-capability-list" in profiles
    assert 'aria-label={`${label}: ${summary.total} configured`}' in profiles
    assert 'className="relative overflow-hidden"' in profiles
    assert 'className="fixed z-[120]' in profiles
    assert "profileCapabilityChips" not in profiles
    assert "toolChips.visible.map" not in profiles
    assert "skillChips.visible.map" not in profiles
    assert "toolsets: string[];" in api
    assert "assigned_skills: string[];" in api
    assert "skill_names: string[];" in api


def test_zeus_profile_bootstrap_script_is_canonical_and_non_destructive():
    script = (ROOT / "scripts/bootstrap_zeus_profiles.py").read_text(encoding="utf-8")

    assert "PROFILE_SPECS" in script
    assert "profile-su" in script
    assert "factory-orchestrator" in script
    assert "sophie-atc" in script
    assert "NO_BUNDLED_SKILLS_MARKER" in script
    assert "--apply" in script
    assert "--check" in script
    assert "description_auto: false" in script

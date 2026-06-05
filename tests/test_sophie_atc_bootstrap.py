from scripts.customer_service.bootstrap_sophie_atc import bootstrap_sophie_atc_profile


def test_bootstrap_sophie_atc_profile_writes_isolated_profile(tmp_path):
    result = bootstrap_sophie_atc_profile(
        profiles_root=str(tmp_path),
        model="test-model",
        provider="test-provider",
        force=True,
    )
    profile = tmp_path / "sophie-atc"

    assert result["profile"] == "sophie-atc"
    assert (profile / "SOUL.md").is_file()
    assert (profile / "profile.yaml").is_file()
    assert (profile / "config.yaml").is_file()
    assert (profile / "skills/customer-service/sophie-atc/SKILL.md").is_file()
    assert "test-model" in (profile / "config.yaml").read_text(encoding="utf-8")
    assert "test-provider" in (profile / "config.yaml").read_text(encoding="utf-8")
    assert "customer_service" in (profile / "config.yaml").read_text(encoding="utf-8")
    assert "Sophie de SitioUno" in (profile / "profile.yaml").read_text(encoding="utf-8")
    assert "Sin ejecución privilegiada" in (profile / "skills/customer-service/sophie-atc/SKILL.md").read_text(encoding="utf-8")

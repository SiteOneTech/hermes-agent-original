"""Regression coverage for the Factory profile bootstrap script."""

import runpy
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = REPO_ROOT / "scripts" / "factory" / "bootstrap_profiles.py"


def test_configure_profile_reads_yaml_as_utf8(monkeypatch, tmp_path):
    """Bootstrap must decode profile YAML consistently on Windows and Linux."""
    profiles_root = tmp_path / "profiles"
    profile_dir = profiles_root / "worker"
    profile_dir.mkdir(parents=True)
    config_path = profile_dir / "config.yaml"
    config_path.write_text("agent:\n  name: Café\n", encoding="utf-8")
    namespace = runpy.run_path(str(BOOTSTRAP))

    real_read_text = Path.read_text
    calls = []

    def capture_read_text(path, *args, **kwargs):
        calls.append((path, args, kwargs))
        return real_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", capture_read_text)

    namespace["configure_profile"](
        "worker",
        {
            "name": "Café",
            "description": "test profile",
            "mission": "exercise encoding boundary",
            "outputs": ["TEST.md"],
            "skills": ["/test-driven-development"],
            "toolsets": ["terminal"],
        },
        profiles_root,
    )

    config_call = next(call for call in calls if call[0] == config_path)
    assert config_call[2]["encoding"] == "utf-8"
    assert "Café" in config_path.read_text(encoding="utf-8")

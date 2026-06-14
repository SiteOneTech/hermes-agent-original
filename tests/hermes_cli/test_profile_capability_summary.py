from pathlib import Path

import yaml


def _write_skill(root: Path, name: str) -> None:
    skill_dir = root / "skills" / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {name}\n---\n\n# {name}\n",
        encoding="utf-8",
    )


def test_profile_capabilities_read_toolsets_assigned_and_enabled_skills(tmp_path):
    from hermes_cli.profiles import _read_profile_capabilities

    profile_dir = tmp_path / "profiles" / "profile-su"
    profile_dir.mkdir(parents=True)
    (profile_dir / "config.yaml").write_text(
        yaml.safe_dump(
            {
                "toolsets": ["terminal", "file", "factory"],
                "skills": {
                    "assigned": ["factory-agent-operating-canon", "calendar-agenda-queries"],
                    "disabled": ["disabled-skill"],
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    _write_skill(profile_dir, "factory-agent-operating-canon")
    _write_skill(profile_dir, "calendar-agenda-queries")
    _write_skill(profile_dir, "disabled-skill")

    capabilities = _read_profile_capabilities(profile_dir)

    assert capabilities["toolsets"] == ["terminal", "file", "factory"]
    assert capabilities["assigned_skills"] == [
        "factory-agent-operating-canon",
        "calendar-agenda-queries",
    ]
    assert capabilities["skill_names"] == [
        "calendar-agenda-queries",
        "factory-agent-operating-canon",
    ]


def test_profile_capabilities_fall_back_to_platform_toolsets(tmp_path):
    from hermes_cli.profiles import _read_profile_capabilities

    profile_dir = tmp_path / "profiles" / "qa-verifier"
    profile_dir.mkdir(parents=True)
    (profile_dir / "config.yaml").write_text(
        yaml.safe_dump(
            {
                "platform_toolsets": {"cli": ["browser", "vision"]},
                "skills": {"assigned": ["factory-agent-operating-canon"]},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    _write_skill(profile_dir, "factory-agent-operating-canon")

    capabilities = _read_profile_capabilities(profile_dir)

    assert capabilities["toolsets"] == ["browser", "vision"]
    assert capabilities["assigned_skills"] == ["factory-agent-operating-canon"]
    assert capabilities["skill_names"] == ["factory-agent-operating-canon"]


def test_profile_to_dict_surfaces_capability_arrays(tmp_path):
    from hermes_cli.profiles import ProfileInfo
    from hermes_cli.web_server import _profile_to_dict

    info = ProfileInfo(
        name="profile-su",
        path=tmp_path,
        is_default=False,
        gateway_running=False,
        skill_count=2,
        toolsets=["terminal", "factory"],
        assigned_skills=["calendar-agenda-queries"],
        skill_names=["calendar-agenda-queries", "repo-origin-sync"],
    )

    payload = _profile_to_dict(info)

    assert payload["toolsets"] == ["terminal", "factory"]
    assert payload["assigned_skills"] == ["calendar-agenda-queries"]
    assert payload["skill_names"] == ["calendar-agenda-queries", "repo-origin-sync"]

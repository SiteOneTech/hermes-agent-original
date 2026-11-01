"""Regression coverage for the static coding posture."""


def test_coding_posture_keeps_legacy_todo_after_homeassistant_left_core():
    """Home Assistant is catalog-owned; coding still accepts the legacy todo alias."""
    from toolsets import TOOLSETS

    coding_tools = TOOLSETS["coding"]["tools"]
    assert "todo" in coding_tools
    assert not any(tool.startswith("ha_") for tool in coding_tools)

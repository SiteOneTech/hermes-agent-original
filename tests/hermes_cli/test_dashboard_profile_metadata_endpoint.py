"""Dashboard profile visual metadata endpoints."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from hermes_cli import web_server

pytestmark = pytest.mark.xdist_group("dashboard_profile_metadata_app_state")


@pytest.fixture
def dashboard_client(tmp_path, monkeypatch):
    home = tmp_path / ".hermes"
    home.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(home))
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    prev_host = getattr(web_server.app.state, "bound_host", None)
    prev_port = getattr(web_server.app.state, "bound_port", None)
    prev_required = getattr(web_server.app.state, "auth_required", None)
    web_server.app.state.bound_host = "127.0.0.1"
    web_server.app.state.bound_port = 9119
    web_server.app.state.auth_required = False

    client = TestClient(web_server.app, base_url="http://127.0.0.1:9119")
    headers = {"X-Hermes-Session-Token": web_server._SESSION_TOKEN}
    yield client, headers

    web_server.app.state.bound_host = prev_host
    web_server.app.state.bound_port = prev_port
    web_server.app.state.auth_required = prev_required


def test_dashboard_updates_default_profile_visual_metadata(dashboard_client):
    client, headers = dashboard_client

    response = client.put(
        "/api/profiles/default/metadata",
        json={
            "display_name": "Sophie de SitioUno",
            "avatar_path": "/agent-avatars/sophie-atc.webp",
        },
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {"ok": True}

    profiles_response = client.get("/api/profiles", headers=headers)
    assert profiles_response.status_code == 200
    default = {
        profile["name"]: profile for profile in profiles_response.json()["profiles"]
    }["default"]
    assert default["display_name"] == "Sophie de SitioUno"
    assert default["avatar_path"] == "/agent-avatars/sophie-atc.webp"


def test_dashboard_updates_named_profile_avatar_metadata(dashboard_client):
    from hermes_cli import profiles as profiles_mod

    client, headers = dashboard_client
    profiles_mod.create_profile("builder", no_alias=True, no_skills=True)

    response = client.put(
        "/api/profiles/builder/metadata",
        json={"avatar_path": "/agent-avatars/claude-builder.webp"},
        headers=headers,
    )

    assert response.status_code == 200

    profiles_response = client.get("/api/profiles", headers=headers)
    builder = {
        profile["name"]: profile for profile in profiles_response.json()["profiles"]
    }["builder"]
    assert builder["display_name"] == ""
    assert builder["avatar_path"] == "/agent-avatars/claude-builder.webp"


def test_dashboard_rejects_profile_avatar_outside_agent_avatars(dashboard_client):
    client, headers = dashboard_client

    response = client.put(
        "/api/profiles/default/metadata",
        json={"avatar_path": "https://example.com/avatar.png"},
        headers=headers,
    )

    assert response.status_code == 400

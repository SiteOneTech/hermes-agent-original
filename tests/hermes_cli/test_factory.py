import argparse
import json
from pathlib import Path

from hermes_cli import factory
from hermes_cli.factory_catalog import FACTORY_AGENTS, slugify


def test_factory_catalog_seeds_expected_agent_roster():
    agent_ids = {agent[0] for agent in FACTORY_AGENTS}
    agent_by_id = {agent[0]: agent for agent in FACTORY_AGENTS}
    assert len(agent_ids) == 15
    assert "factory-orchestrator" in agent_ids
    assert "claude-builder" in agent_ids
    assert "claude-deepseek-builder" in agent_ids
    assert "codex-builder" in agent_ids
    assert "openhands-builder" in agent_ids
    assert "openhands-lab" in agent_ids
    assert "ux-ui-designer" in agent_ids
    assert "quality-reviewer" in agent_ids
    assert "terminal" in agent_by_id["factory-reporter"][4]
    assert "factory-sandbox-kidu" in agent_by_id["qa-verifier"][5]
    assert "factory-sandbox-kidu" in agent_by_id["devops-release"][5]


def test_factory_sandbox_kidu_skill_is_bundled_for_assigned_profiles():
    repo_root = Path(__file__).resolve().parents[2]
    assert (repo_root / "skills" / "devops" / "factory-sandbox-kidu" / "SKILL.md").exists()


def test_factory_slugify_is_stable_for_project_ids():
    assert slugify("Agent Core Personal CRM / Follow-up / Reminders") == "agent-core-personal-crm-follow-up-reminders"


def test_factory_cli_parser_has_no_legacy_sqlite_db_option():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    factory_parser = factory.add_parser(subparsers)

    option_dests = {action.dest for action in factory_parser._actions}
    assert "db" not in option_dests


def test_factory_cli_project_create_uses_canonical_backend(monkeypatch, capsys):
    calls = {}

    class FakeBackend:
        @staticmethod
        def create_project(name, **kwargs):
            calls["name"] = name
            calls["kwargs"] = kwargs
            return {
                "project_id": kwargs["project_id"],
                "lanes": [
                    {
                        "lane_id": "demo-factory-hybrid",
                        "methodology": kwargs["methodology"],
                        "execution_surface": "factory",
                        "branch": "factory/demo-factory/hybrid",
                    }
                ],
            }

    monkeypatch.setattr("hermes_cli.factory_backend.get_backend", lambda: FakeBackend)
    args = argparse.Namespace(
        name="Demo Factory",
        project_id="demo-factory",
        repo_path=None,
        repo_remote=None,
        base_branch=None,
        human_owner="Jean García",
        summary=None,
        risk_level="medium",
        autonomy_level=3,
        methodology="hybrid",
        no_default_lanes=False,
        json=True,
    )

    assert factory.cmd_project_create(args) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["project_id"] == "demo-factory"
    assert payload["lanes"][0]["execution_surface"] == "factory"
    assert calls["kwargs"]["methodology"] == "hybrid"

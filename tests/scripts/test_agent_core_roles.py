from hermes_cli import agent_core_sql
from scripts import agent_core_roles


def test_ensure_login_role_alters_existing_nologin_roles_to_login(monkeypatch):
    captured = {}

    def fake_run_psql(env, database, sql):
        captured["database"] = database
        captured["sql"] = sql
        return ""

    monkeypatch.setattr(agent_core_roles, "run_psql", fake_run_psql)

    agent_core_roles.ensure_login_role(
        {"AGENT_MANAGEMENT_DB_RUNTIME_USER": "agent_management_runtime", "AGENT_MANAGEMENT_DB_RUNTIME_PASSWORD": "pw"},
        "AGENT_MANAGEMENT_DB_RUNTIME_USER",
        "AGENT_MANAGEMENT_DB_RUNTIME_PASSWORD",
    )

    assert captured["database"] == "postgres"
    assert "ALTER ROLE " in captured["sql"]
    assert " LOGIN PASSWORD " in captured["sql"]


def test_agent_management_runtime_password_falls_back_to_agent_runtime_password():
    env = {"AGENT_DATABASE_URL": "postgresql://agent_runtime:samplepw@127.0.0.1:55430/zeus_agent"}

    agent_core_roles._fill_passwords_from_urls(env)
    agent_core_roles._apply_shared_runtime_password_fallbacks(env)

    assert env["AGENT_DB_RUNTIME_PASSWORD"] == "samplepw"
    assert env["AGENT_MANAGEMENT_DB_RUNTIME_PASSWORD"] == "samplepw"


def test_agent_management_dedicated_password_wins_over_shared_fallback():
    env = {
        "AGENT_DB_RUNTIME_PASSWORD": "basepw",
        "AGENT_MANAGEMENT_DB_RUNTIME_PASSWORD": "dedicatedpw",
    }

    agent_core_roles._apply_shared_runtime_password_fallbacks(env)
    agent_core_sql._apply_shared_runtime_password_fallbacks(env)

    assert env["AGENT_MANAGEMENT_DB_RUNTIME_PASSWORD"] == "dedicatedpw"

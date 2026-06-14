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

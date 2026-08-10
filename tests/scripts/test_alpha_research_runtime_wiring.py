from __future__ import annotations

from hermes_cli import agent_core_sql
from scripts import agent_core_roles


AUTHOR_URL = "postgresql://alpha_research_runtime:authorpw@127.0.0.1:55430/zeus_agent"
REVIEWER_URL = "postgresql://alpha_research_reviewer:reviewerpw@127.0.0.1:55430/zeus_agent"


def test_alpha_research_uses_dedicated_infisical_urls_without_shared_password_fallback():
    assert agent_core_sql.DEFAULTS["ALPHA_RESEARCH_DB_RUNTIME_USER"] == "alpha_research_runtime"
    assert agent_core_sql.DEFAULTS["ALPHA_RESEARCH_DB_REVIEWER_USER"] == "alpha_research_reviewer"
    assert agent_core_roles.DEFAULTS["ALPHA_RESEARCH_DB_RUNTIME_USER"] == "alpha_research_runtime"
    assert agent_core_roles.DEFAULTS["ALPHA_RESEARCH_DB_REVIEWER_USER"] == "alpha_research_reviewer"

    broad_env = {
        "AGENT_DB_RUNTIME_PASSWORD": "broad-agent-secret",
        "FACTORY_DB_RUNTIME_PASSWORD": "broad-factory-secret",
    }
    agent_core_roles._apply_shared_runtime_password_fallbacks(broad_env)
    agent_core_sql._apply_shared_runtime_password_fallbacks(broad_env)
    assert "ALPHA_RESEARCH_DB_RUNTIME_PASSWORD" not in broad_env
    assert "ALPHA_RESEARCH_DB_REVIEWER_PASSWORD" not in broad_env

    dedicated_env = {
        "ALPHA_RESEARCH_DATABASE_URL": AUTHOR_URL,
        "ALPHA_RESEARCH_REVIEWER_DATABASE_URL": REVIEWER_URL,
    }
    agent_core_roles._fill_passwords_from_urls(dedicated_env)
    agent_core_sql._fill_passwords_from_urls(dedicated_env)
    assert dedicated_env["ALPHA_RESEARCH_DB_RUNTIME_PASSWORD"] == "authorpw"
    assert dedicated_env["ALPHA_RESEARCH_DB_REVIEWER_PASSWORD"] == "reviewerpw"

    assert "ALPHA_RESEARCH_DB_RUNTIME_PASSWORD" in agent_core_roles.SECRET_KEYS
    assert "ALPHA_RESEARCH_DB_REVIEWER_PASSWORD" in agent_core_roles.SECRET_KEYS
    assert "ALPHA_RESEARCH_DB_RUNTIME_PASSWORD" not in agent_core_roles.OPTIONAL_RUNTIME_PASSWORD_KEYS
    assert "ALPHA_RESEARCH_DB_REVIEWER_PASSWORD" not in agent_core_roles.OPTIONAL_RUNTIME_PASSWORD_KEYS
    assert "ALPHA_RESEARCH_DB_RUNTIME_PASSWORD" not in agent_core_roles.SHARED_RUNTIME_PASSWORD_FALLBACKS
    assert "ALPHA_RESEARCH_DB_REVIEWER_PASSWORD" not in agent_core_roles.SHARED_RUNTIME_PASSWORD_FALLBACKS
    assert "ALPHA_RESEARCH_DB_RUNTIME_PASSWORD" not in agent_core_sql.SHARED_RUNTIME_PASSWORD_FALLBACKS
    assert "ALPHA_RESEARCH_DB_REVIEWER_PASSWORD" not in agent_core_sql.SHARED_RUNTIME_PASSWORD_FALLBACKS


def test_alpha_research_role_rotation_emits_least_privilege_role_sql(monkeypatch):
    captured: list[tuple[str, str]] = []

    def fake_run_psql(env, database, sql):
        captured.append((database, sql))
        return ""

    monkeypatch.setattr(agent_core_roles, "run_psql", fake_run_psql)
    env = {
        "AGENT_DB_CONTAINER": "agent-postgres",
        "AGENT_DB_ADMIN_USER": "agent_admin",
        "ALPHA_RESEARCH_DB_RUNTIME_USER": "alpha_research_runtime",
        "ALPHA_RESEARCH_DB_RUNTIME_PASSWORD": "authorpw",
        "ALPHA_RESEARCH_DB_REVIEWER_USER": "alpha_research_reviewer",
        "ALPHA_RESEARCH_DB_REVIEWER_PASSWORD": "reviewerpw",
    }

    agent_core_roles.ensure_alpha_research_roles(env)

    assert {database for database, _ in captured} == {"postgres"}
    rendered_sql = "\n".join(sql for _, sql in captured)
    for role, password in (
        ("alpha_research_runtime", "authorpw"),
        ("alpha_research_reviewer", "reviewerpw"),
    ):
        assert role in rendered_sql
        assert password in rendered_sql

    for clause in (
        " LOGIN ",
        " NOSUPERUSER ",
        " NOCREATEDB ",
        " NOCREATEROLE ",
        " NOINHERIT ",
        " NOREPLICATION ",
        " NOBYPASSRLS ",
        " CONNECTION LIMIT 5",
        "ALTER ROLE alpha_research_runtime SET search_path = alpha_research, pg_catalog",
        "ALTER ROLE alpha_research_reviewer SET search_path = alpha_research, pg_catalog",
    ):
        assert clause in rendered_sql

    assert "IN ROLE" not in rendered_sql
    assert "GRANT alpha_research" not in rendered_sql
    assert "broad-agent-secret" not in rendered_sql
    assert "broad-factory-secret" not in rendered_sql

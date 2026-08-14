from __future__ import annotations

from hermes_cli import agent_core_sql


def test_statement_one_accepts_a_trailing_statement_delimiter(monkeypatch):
    emitted: list[str] = []

    def fake_json_query(sql: str, **_kwargs):
        emitted.append(sql)
        return {"lease_key": "factory-control-plane"}

    monkeypatch.setattr(agent_core_sql, "json_query", fake_json_query)

    result = agent_core_sql.statement_one(
        "INSERT INTO factory.runtime_leases(lease_key) VALUES ('factory-control-plane') RETURNING lease_key;"
    )

    assert result == {"lease_key": "factory-control-plane"}
    assert emitted == [
        "WITH q AS (INSERT INTO factory.runtime_leases(lease_key) VALUES ('factory-control-plane') RETURNING lease_key) "
        "SELECT to_jsonb(q)::text FROM q LIMIT 1;"
    ]

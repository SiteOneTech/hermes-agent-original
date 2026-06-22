from __future__ import annotations

import json

import pytest
import toolsets
from tools import fitness_tool


def _loads(result: str) -> dict:
    return json.loads(result)


def test_fitness_toolset_registered():
    tools = toolsets.resolve_toolset("fitness")
    assert "fitness_status" in tools
    assert "fitness_profile_upsert" in tools
    assert "fitness_food_search" in tools
    assert "fitness_nutrition_day_summary" in tools
    assert "fitness_routine_create" in tools
    assert "fitness_workout_set_log" in tools
    assert "fitness_progress_summary" in tools


def test_numeric_validator_rejects_sql_fragments():
    with pytest.raises(ValueError):
        fitness_tool._num("1; DROP TABLE fitness.profiles")


def test_profile_upsert_requires_display_name_or_profile_id():
    result = _loads(fitness_tool._handle_profile_upsert({}))
    assert result["error"]
    assert "display_name" in result["error"]


def test_nutrition_log_requires_profile_and_food_description():
    result = _loads(fitness_tool._handle_nutrition_log_create({"profile_id": "p1", "calories": 100}))
    assert result["error"]
    assert "food_id" in result["error"] or "description" in result["error"]


def test_routine_create_preserves_structured_days(monkeypatch):
    captured: list[str] = []

    def fake_statement_one(statement: str, *, user: str | None = None):
        captured.append(statement)
        if "INSERT INTO fitness.routines" in statement:
            return {"routine_id": "routine-demo", "title": "Demo", "plan": {}}
        if "INSERT INTO fitness.routine_days" in statement:
            return {"routine_day_id": "day-demo"}
        if "INSERT INTO fitness.routine_exercises" in statement:
            return {"routine_exercise_id": 1}
        raise AssertionError(statement)

    monkeypatch.setattr(fitness_tool.sql, "statement_one", fake_statement_one)
    monkeypatch.setattr(fitness_tool.sql, "psql", lambda *a, **kw: None)
    result = _loads(fitness_tool._handle_routine_create({
        "profile_id": "profile-demo",
        "title": "Demo",
        "goal_type": "strength",
        "days": [{"name": "Full body", "exercises": [{"exercise_id": "ex-squat", "sets": 3, "target_reps_min": 5, "target_reps_max": 8, "target_rir": 2}]}],
    }))
    assert result["ok"] is True
    assert result["routine"]["routine_id"] == "routine-demo"
    assert any("fitness.routine_exercises" in statement for statement in captured)


def test_workout_set_log_computes_volume_and_estimated_1rm(monkeypatch):
    statements: list[str] = []

    def fake_statement_one(statement: str, *, user: str | None = None):
        statements.append(statement)
        return {"workout_set_id": 1, "volume_load": 500, "estimated_1rm": 116.666667}

    monkeypatch.setattr(fitness_tool.sql, "statement_one", fake_statement_one)
    result = _loads(fitness_tool._handle_workout_set_log({
        "session_id": "sess-1",
        "exercise_id": "ex-bench",
        "set_index": 1,
        "weight_kg": 100,
        "reps": 5,
        "rpe": 8,
        "rir": 2,
    }))
    assert result["ok"] is True
    assert result["set"]["volume_load"] == 500
    assert any("estimated_1rm" in statement for statement in statements)


def test_progress_summary_queries_expected_sections(monkeypatch):
    monkeypatch.setattr(fitness_tool.sql, "one", lambda statement, *, user=None: {"days": 7, "avg_calories": 2100, "latest_weight_kg": 80})
    monkeypatch.setattr(fitness_tool.sql, "rows", lambda statement, *, user=None: [{"activity_type": "strength", "sessions": 3}])
    result = _loads(fitness_tool._handle_progress_summary({"profile_id": "p1", "start_date": "2026-01-01", "end_date": "2026-01-07"}))
    assert result["ok"] is True
    assert "summary" in result
    assert "latest_body_metric" in result
    assert "training" in result


def test_body_metric_log_accepts_smart_scale_composition(monkeypatch):
    captured: list[str] = []

    monkeypatch.setattr(fitness_tool.sql, "one", lambda *a, **kw: None)

    def fake_statement_one(statement: str, *, user: str | None = None):
        captured.append(statement)
        return {"body_metric_id": 42, "weight_kg": 113.8, "bmi": 33.3, "body_condition_score": 62}

    monkeypatch.setattr(fitness_tool.sql, "statement_one", fake_statement_one)
    result = _loads(fitness_tool._handle_body_metric_log_create({
        "profile_id": "jean-garcia",
        "weight_kg": 113.8,
        "body_fat_pct": 23.9,
        "bmi": 33.3,
        "body_condition_score": 62,
        "skeletal_muscle_pct": 40.3,
        "water_pct": 55.2,
        "protein_pct": 16.2,
        "visceral_fat_index": 9,
        "bone_mass_pct": 4.0,
        "bmr_kcal": 2241,
        "biological_age_years": 55,
        "fat_weight_kg": 27.2,
        "body_fat_mass_index": 5,
        "fat_free_mass_kg": 86.6,
        "metadata": {"idempotency_key": "scale-2026-06-22"},
    }))
    assert result["ok"] is True
    assert result["body_metric"]["bmi"] == 33.3
    statement = "\n".join(captured)
    assert "body_condition_score" in statement
    assert "skeletal_muscle_pct" in statement
    assert "fat_free_mass_kg" in statement
    assert "ON CONFLICT (profile_id, (btrim(metadata->>'idempotency_key')))" in statement


def test_body_metric_log_uses_atomic_idempotent_upsert(monkeypatch):
    captured: list[str] = []

    monkeypatch.setattr(fitness_tool.sql, "one", lambda *a, **kw: {"body_metric_id": 7})

    def fake_statement_one(statement: str, *, user: str | None = None):
        captured.append(statement)
        return {"body_metric_id": 7, "weight_kg": 113.8, "bmi": 33.3}

    monkeypatch.setattr(fitness_tool.sql, "statement_one", fake_statement_one)
    result = _loads(fitness_tool._handle_body_metric_log_create({
        "profile_id": "jean-garcia",
        "weight_kg": 113.8,
        "metadata": {"idempotency_key": " scale-2026-06-22 "},
    }))
    assert result["ok"] is True
    assert result["idempotent"] is True
    statement = "\n".join(captured)
    assert "ON CONFLICT (profile_id, (btrim(metadata->>'idempotency_key')))" in statement
    assert "DO UPDATE SET" in statement
    assert "weight_kg=COALESCE(EXCLUDED.weight_kg, fitness.body_metrics.weight_kg)" in statement
    assert "bmi=COALESCE(EXCLUDED.bmi, fitness.body_metrics.bmi)" in statement
    assert "metadata=fitness.body_metrics.metadata || EXCLUDED.metadata" in statement
    assert '"idempotency_key": "scale-2026-06-22"' in statement


def test_body_metric_log_ignores_blank_idempotency_key(monkeypatch):
    captured: list[str] = []

    def fail_one(*_args, **_kwargs):
        raise AssertionError("blank idempotency keys should not trigger lookup")

    monkeypatch.setattr(fitness_tool.sql, "one", fail_one)

    def fake_statement_one(statement: str, *, user: str | None = None):
        captured.append(statement)
        return {"body_metric_id": 8, "weight_kg": 113.8}

    monkeypatch.setattr(fitness_tool.sql, "statement_one", fake_statement_one)
    result = _loads(fitness_tool._handle_body_metric_log_create({
        "profile_id": "jean-garcia",
        "weight_kg": 113.8,
        "metadata": {"idempotency_key": "   "},
    }))
    assert result["ok"] is True
    statement = "\n".join(captured)
    assert "ON CONFLICT" not in statement
    assert '"idempotency_key"' not in statement

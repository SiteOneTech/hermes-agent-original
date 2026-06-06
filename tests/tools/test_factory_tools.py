import json
import uuid

import model_tools


def _payload(result: str) -> dict:
    return json.loads(result)


def test_factory_toolset_exposes_factory_tools():
    tools = model_tools.get_tool_definitions(enabled_toolsets=["factory"], quiet_mode=True)
    names = {tool["function"]["name"] for tool in tools}

    assert "factory_project_create" in names
    assert "factory_lane_create" in names
    assert "factory_task_create" in names
    assert "factory_gate_record" in names
    assert "factory_status" in names


def test_factory_tools_create_project_status_and_gate(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes"))
    project_id = f"tool-factory-test-{uuid.uuid4().hex[:8]}"

    created = _payload(
        model_tools.handle_function_call(
            "factory_project_create",
            {"name": "Tool Factory Test", "project_id": project_id},
        )
    )
    assert created["ok"] is True
    assert {lane["lane_id"] for lane in created["lanes"]} == {
        f"{project_id}-zeus",
        f"{project_id}-bmad",
    }

    task = _payload(
        model_tools.handle_function_call(
            "factory_task_create",
            {
                "project_id": project_id,
                "lane_id": f"{project_id}-zeus",
                "title": "Prepare implementation plan",
                "owner_agent_id": "implementation-planner",
                "reviewer_agent_id": "quality-reviewer",
                "acceptance_criteria": ["Plan is persisted"],
            },
        )
    )
    assert task["ok"] is True
    assert task["task_id"].startswith(f"{project_id}-prepare-implementation-plan")

    gate = _payload(
        model_tools.handle_function_call(
            "factory_gate_record",
            {
                "project_id": project_id,
                "task_id": task["task_id"],
                "gate_type": "planning",
                "status": "passed",
                "reviewer": "quality-reviewer",
                "notes": "Test evidence accepted",
            },
        )
    )
    assert gate["ok"] is True
    assert gate["status"] == "passed"

    status = _payload(model_tools.handle_function_call("factory_status", {"project_id": project_id}))
    assert status["ok"] is True
    assert [project["project_id"] for project in status["projects"]] == [project_id]
    assert [item["status"] for item in status["gates"]] == ["passed"]

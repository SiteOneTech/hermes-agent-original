from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_orchestrator_module():
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "scripts" / "factory" / "factory_orchestrator_tick.py"
    spec = importlib.util.spec_from_file_location("factory_orchestrator_tick_under_test", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_spawn_worker_uses_current_python_module_not_path_hermes(monkeypatch, tmp_path):
    module = _load_orchestrator_module()

    monkeypatch.setattr(module, "_home", lambda: tmp_path)
    monkeypatch.setattr(
        module,
        "_prepare_worktree",
        lambda _payload, _claim: {"ready": True, "cwd": str(tmp_path), "reason": "test"},
    )

    captured: dict[str, object] = {}

    class FakePopen:
        pid = 12345

        def __init__(self, argv, **kwargs):
            captured["argv"] = argv
            captured["kwargs"] = kwargs

    monkeypatch.setattr(module.subprocess, "Popen", FakePopen)

    class FakeDB:
        def mark_run_spawned(self, run_id, *, process_id, log_path, prompt_path):
            captured["mark_run_spawned"] = {
                "run_id": run_id,
                "process_id": process_id,
                "log_path": log_path,
                "prompt_path": prompt_path,
            }

        def update_run_metadata(self, run_id, metadata):
            captured["metadata"] = metadata

    payload = {
        "projects": [
            {
                "project_id": "demo-project",
                "name": "Demo Project",
                "repo_path": str(tmp_path),
                "metadata": {"repo_strategy": {"primary_repo_path": str(tmp_path), "base_branch": "main"}},
            }
        ],
        "tasks": [],
        "gates": [],
    }
    claim = {
        "run_id": "run-test",
        "worker_profile": "implementation-planner",
        "task": {
            "project_id": "demo-project",
            "task_id": "task-test",
            "title": "Planning task",
            "phase": "planning",
            "engine": "zeus",
            "status": "claimed",
            "branch": "factory/demo/inc-001",
            "worktree_path": str(tmp_path),
            "acceptance_criteria": [],
            "dependencies": [],
        },
    }

    result = module._spawn_worker(FakeDB(), payload, claim)

    argv = captured["argv"]
    assert argv[:2] == [sys.executable, "-c"]
    wrapper = argv[2]
    assert "sys.executable, '-m', 'hermes_cli.main'" in wrapper
    assert "['hermes'" not in wrapper
    assert "--profile" in wrapper
    assert "implementation-planner" in wrapper
    assert result["pid"] == 12345
    assert captured["mark_run_spawned"]["process_id"] == 12345
    assert captured["metadata"]["worker_cwd"] == str(tmp_path)


def test_prepare_worktree_starts_new_increment_from_origin_base(monkeypatch, tmp_path):
    module = _load_orchestrator_module()
    repo = tmp_path / "repo"
    repo.mkdir()
    worktree = tmp_path / "worktrees" / "inc-001"
    calls: list[list[str]] = []

    def fake_run(argv, **kwargs):
        calls.append([str(part) for part in argv])
        if "rev-parse" in argv:
            return module.subprocess.CompletedProcess(argv, 0, stdout="true\n", stderr="")
        if "fetch" in argv:
            return module.subprocess.CompletedProcess(argv, 0, stdout="", stderr="")
        if "worktree" in argv and "add" in argv:
            return module.subprocess.CompletedProcess(argv, 0, stdout="", stderr="")
        return module.subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    payload = {
        "projects": [
            {
                "project_id": "demo",
                "repo_path": str(repo),
                "metadata": {"repo_strategy": {"primary_repo_path": str(repo), "base_branch": "main"}},
            }
        ]
    }
    claim = {"task": {"project_id": "demo", "branch": "factory/demo/inc-001", "worktree_path": str(worktree)}}

    result = module._prepare_worktree(payload, claim)

    assert result["ready"] is True
    assert result["base_ref"] == "origin/main"
    assert any(call[:5] == ["git", "-C", str(repo), "fetch", "origin"] and call[5] == "main" for call in calls)
    assert any(call[:7] == ["git", "-C", str(repo), "worktree", "add", "-B", "factory/demo/inc-001"] and call[-1] == "origin/main" for call in calls)

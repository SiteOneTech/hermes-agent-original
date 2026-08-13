from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import pytest

from hermes_cli import factory
def _load_orchestrator_module():
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "scripts" / "factory" / "factory_orchestrator_tick.py"
    spec = importlib.util.spec_from_file_location("factory_orchestrator_tick_under_test", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module



def test_factory_cli_requires_explicit_jean_successor_authorization(monkeypatch, capsys):
    captured: dict[str, object] = {}

    class FakeBackend:
        def declare_project_succession(self, predecessor, successor, **kwargs):
            captured["predecessor"] = predecessor
            captured["successor"] = successor
            captured.update(kwargs)
            return {"succession_id": 42, "predecessor_project_id": predecessor, "successor_project_id": successor}

    monkeypatch.setattr(factory, "_backend", lambda _args: FakeBackend())
    args = argparse.Namespace(
        project_id="factory-runtime",
        successor_project_id="alpha",
        actor="Jean",
        reason="Factory green permits research-only Alpha under a single worker",
        allow_auto_resume=True,
        json=True,
    )

    assert factory.cmd_project_declare_successor(args) == 0
    assert captured["predecessor"] == "factory-runtime"
    assert captured["successor"] == "alpha"
    assert captured["declared_by"] == "Jean"
    assert captured["authorization"] == {
        "authorized_by": "Jean",
        "reason": "Factory green permits research-only Alpha under a single worker",
        "allow_auto_resume": True,
    }
    assert '"succession_id": 42' in capsys.readouterr().out


def test_factory_cli_successor_parser_requires_explicit_flag():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest="root")
    factory.add_parser(subs)

    parsed = parser.parse_args([
        "factory", "project", "declare-successor", "factory-runtime", "alpha",
        "--actor", "Jean", "--reason", "Factory green",
    ])
    assert parsed.allow_auto_resume is False


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



def test_spawn_worker_terminates_new_process_when_run_registration_fails(monkeypatch, tmp_path):
    module = _load_orchestrator_module()
    monkeypatch.setattr(module, "_home", lambda: tmp_path)
    monkeypatch.setattr(module, "_prepare_worktree", lambda *_args: {"ready": True, "cwd": str(tmp_path), "reason": "test"})

    class FakePopen:
        pid = 54321

        def __init__(self, *_args, **_kwargs):
            pass

        def wait(self, *, timeout):
            return 0

    terminated: list[int] = []
    monkeypatch.setattr(module.subprocess, "Popen", FakePopen)
    monkeypatch.setattr(module.os, "killpg", lambda pid, _signal: terminated.append(pid))

    class FailingDB:
        def mark_run_spawned(self, *_args, **_kwargs):
            raise RuntimeError("Agent Core write failed")

        def update_run_metadata(self, *_args, **_kwargs):
            raise AssertionError("must not write metadata after failed run registration")

    payload = {"projects": [{"project_id": "demo", "repo_path": str(tmp_path), "metadata": {}}], "tasks": [], "gates": []}
    claim = {"run_id": "run-failing", "worker_profile": "implementation-planner", "task": {"project_id": "demo", "task_id": "t1", "title": "test", "phase": "implementation", "branch": "factory/demo/t1", "worktree_path": str(tmp_path)}}

    with pytest.raises(RuntimeError, match="Agent Core write failed"):
        module._spawn_worker(FailingDB(), payload, claim)

    assert terminated == [54321]


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

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

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


def test_orchestrator_tick_reports_migration_readiness_before_claim_or_spawn(monkeypatch, capsys):
    module = _load_orchestrator_module()
    calls: list[str] = []

    class MissingFactoryMigration(RuntimeError):
        diagnostic = {
            "ready": False,
            "module": "factory",
            "missing_migrations": ["000004"],
            "apply_command": "python scripts/agent_core_db.py migrate --module factory",
            "verify_command": "python scripts/agent_core_db.py verify --module factory",
        }

    class FakeDB:
        def ensure_runtime_schema(self):
            calls.append("ensure_runtime_schema")
            raise MissingFactoryMigration(
                "Factory migration readiness failed: run python scripts/agent_core_db.py migrate --module factory"
            )

        def status(self, *_args, **_kwargs):
            calls.append("status")
            return {
                "db_backend": "agent_core_postgres",
                "projects": [],
                "tasks": [],
                "lanes": [],
                "gates": [],
                "events": [],
                "artifacts": [],
                "task_runs": [],
                "human_questions": [],
                "agents": [],
            }

        def force_tick(self, *_args, **_kwargs):
            calls.append("force_tick")
            return {"skipped": True, "claimed": None, "monitor": {}, "unblocked": [], "reconciled": []}

    monkeypatch.setattr("hermes_cli.factory_backend.get_backend", lambda: FakeDB())
    monkeypatch.setattr(module, "_spawn_worker", lambda *_args, **_kwargs: calls.append("spawn_worker"))

    with pytest.raises(SystemExit) as exc:
        module.main()

    assert exc.value.code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["error_type"] == "factory_migration_readiness_failed"
    assert payload["migration_readiness"]["missing_migrations"] == ["000004"]
    assert "migrate --module factory" in payload["error"]
    assert calls == ["ensure_runtime_schema"]


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



def test_task_prompt_uses_current_python_for_factory_cli():
    module = _load_orchestrator_module()
    payload = {
        "projects": [{
            "project_id": "demo-project",
            "name": "Demo Project",
            "repo_path": "/repo",
            "metadata": {"repo_strategy": {"primary_repo_path": "/repo", "base_branch": "main"}},
            "document_status": [],
        }],
        "tasks": [],
        "gates": [],
    }
    claim = {
        "run_id": "run-test",
        "task": {
            "project_id": "demo-project",
            "task_id": "task-test",
            "title": "Documentation reconciliation",
            "phase": "documentation",
            "engine": "zeus",
            "status": "claimed",
            "acceptance_criteria": [],
            "dependencies": [],
        },
    }

    prompt = module._task_prompt(payload, claim)

    assert f"`{sys.executable} -m hermes_cli.main factory status`" in prompt
    assert f"`{sys.executable} -m hermes_cli.main factory gate record`" in prompt
    assert "`hermes factory" not in prompt


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

    class FakeProcess:
        pid = 54321

        def children(self, *, recursive: bool):
            assert recursive is True
            return []

        def terminate(self):
            terminated.append(self.pid)

        def kill(self):
            raise AssertionError("worker should exit during the graceful wait")

    class FakePsutil:
        class NoSuchProcess(Exception):
            pass

        @staticmethod
        def Process(pid):
            assert pid == 54321
            return FakeProcess()

        @staticmethod
        def wait_procs(processes, *, timeout):
            assert timeout == 5
            return processes, []

    monkeypatch.setitem(sys.modules, "psutil", FakePsutil)
    monkeypatch.setattr(
        module.os,
        "killpg",
        lambda *_args: (_ for _ in ()).throw(AssertionError("POSIX killpg must not be used")),
    )

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


def test_spawn_worker_fails_closed_when_worktree_preparation_is_unavailable(monkeypatch, tmp_path):
    module = _load_orchestrator_module()

    monkeypatch.setattr(module, "_home", lambda: tmp_path)
    preparation = {
        "ready": False,
        "reason": "missing_repo_branch_or_worktree",
        "cwd": str(tmp_path / "live-checkout-must-not-run-worker"),
    }
    monkeypatch.setattr(module, "_prepare_worktree", lambda _payload, _claim: preparation)

    class NoPopen:
        def __init__(self, *_args, **_kwargs):
            raise AssertionError("worker must not launch without an isolated worktree")

    monkeypatch.setattr(module.subprocess, "Popen", NoPopen)
    captured: dict[str, Any] = {}

    class FakeDB:
        def mark_run_finished(self, run_id, *, exit_code, output_summary):
            captured["finished"] = {
                "run_id": run_id,
                "exit_code": exit_code,
                "output_summary": output_summary,
            }

        def update_run_metadata(self, run_id, metadata):
            captured["metadata"] = {"run_id": run_id, **metadata}

    payload = {
        "projects": [{"project_id": "demo-project", "repo_path": str(tmp_path)}],
        "tasks": [],
        "gates": [],
    }
    claim = {
        "run_id": "run-no-worktree",
        "worker_profile": "factory-reporter",
        "task": {
            "project_id": "demo-project",
            "task_id": "reconcile-docs",
            "title": "Reconcile docs",
            "phase": "documentation",
            "engine": "zeus",
            "status": "claimed",
            "branch": None,
            "worktree_path": None,
            "acceptance_criteria": [],
            "dependencies": [],
        },
    }

    result = module._spawn_worker(FakeDB(), payload, claim)

    assert result["spawned"] is False
    assert result["worktree_preparation"] == preparation
    assert "missing_repo_branch_or_worktree" in result["reason"]
    assert captured["finished"]["run_id"] == "run-no-worktree"
    assert captured["finished"]["exit_code"] == 1
    assert "worktree preflight failed" in captured["finished"]["output_summary"]
    assert captured["metadata"]["worktree_preparation"] == preparation
    assert captured["metadata"]["dispatch_refused_reason"] == "missing_repo_branch_or_worktree"
    assert captured["metadata"]["dispatch_refused"] is True
    assert captured["metadata"]["technical_block"] is True
    assert captured["metadata"]["technical_block_reason"] == "worktree_preflight_unavailable"
    assert captured["metadata"]["worker_cwd"] is None

    summary = captured["finished"]["output_summary"]
    assert summary.splitlines()[0] == "STATE: BLOCKED"
    assert "Technical block: worktree preflight failed" in summary
    assert "No worker was launched and no fallback cwd was used." in summary
    assert "worktree_preflight_evidence" in summary
    assert '"ready": false' in summary

    preflight_path = Path(captured["metadata"]["worktree_preflight_path"])
    assert preflight_path.is_file()
    preflight_evidence = json.loads(preflight_path.read_text(encoding="utf-8"))
    assert preflight_evidence["ready"] is False
    assert preflight_evidence["reason"] == "missing_repo_branch_or_worktree"
    assert preflight_evidence["worktree_preparation"] == preparation
    assert Path(captured["metadata"]["exit_path"]).read_text(encoding="utf-8") == "1"


def test_prepare_existing_worktree_rejects_branch_mismatch(monkeypatch, tmp_path):
    module = _load_orchestrator_module()
    repo = tmp_path / "repo"
    worktree = tmp_path / "worktrees" / "inc-001"
    repo.mkdir()
    worktree.mkdir(parents=True)

    def fake_run(argv, **_kwargs):
        if "--is-inside-work-tree" in argv:
            return module.subprocess.CompletedProcess(argv, 0, stdout="true\n", stderr="")
        if "--git-common-dir" in argv:
            return module.subprocess.CompletedProcess(argv, 0, stdout=str(repo / ".git") + "\n", stderr="")
        if "--show-toplevel" in argv:
            return module.subprocess.CompletedProcess(argv, 0, stdout=str(worktree) + "\n", stderr="")
        if "--git-dir" in argv:
            return module.subprocess.CompletedProcess(argv, 0, stdout=str(repo / ".git" / "worktrees" / "inc-001") + "\n", stderr="")
        if "branch" in argv and "--show-current" in argv:
            return module.subprocess.CompletedProcess(argv, 0, stdout="factory/demo/other\n", stderr="")
        return module.subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    payload = {
        "projects": [{
            "project_id": "demo",
            "repo_path": str(repo),
            "metadata": {"repo_strategy": {"primary_repo_path": str(repo), "base_branch": "main"}},
        }],
    }
    claim = {"task": {"project_id": "demo", "branch": "factory/demo/inc-001", "worktree_path": str(worktree)}}

    result = module._prepare_worktree(payload, claim)

    assert result["ready"] is False
    assert result["reason"] == "worktree_branch_mismatch"


def test_prepare_existing_worktree_rejects_subdirectory_not_worktree_root(monkeypatch, tmp_path):
    module = _load_orchestrator_module()
    repo = tmp_path / "repo"
    assigned_subdirectory = repo / "subdirectory-not-a-worktree"
    repo.mkdir()
    assigned_subdirectory.mkdir()

    def fake_run(argv, **_kwargs):
        if "--is-inside-work-tree" in argv:
            return module.subprocess.CompletedProcess(argv, 0, stdout="true\n", stderr="")
        if "--git-common-dir" in argv:
            return module.subprocess.CompletedProcess(argv, 0, stdout=str(repo / ".git") + "\n", stderr="")
        if "--show-toplevel" in argv:
            return module.subprocess.CompletedProcess(argv, 0, stdout=str(repo) + "\n", stderr="")
        if "branch" in argv and "--show-current" in argv:
            return module.subprocess.CompletedProcess(argv, 0, stdout="factory/demo/inc-001\n", stderr="")
        return module.subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    payload = {
        "projects": [{
            "project_id": "demo",
            "repo_path": str(repo),
            "metadata": {"repo_strategy": {"primary_repo_path": str(repo), "base_branch": "main"}},
        }],
    }
    claim = {"task": {"project_id": "demo", "branch": "factory/demo/inc-001", "worktree_path": str(assigned_subdirectory)}}

    result = module._prepare_worktree(payload, claim)

    assert result["ready"] is False
    assert result["reason"] == "worktree_path_not_repository_root"


def test_prepare_existing_worktree_rejects_primary_checkout(monkeypatch, tmp_path):
    module = _load_orchestrator_module()
    repo = tmp_path / "repo"
    repo.mkdir()

    def fake_run(argv, **_kwargs):
        if "--is-inside-work-tree" in argv:
            return module.subprocess.CompletedProcess(argv, 0, stdout="true\n", stderr="")
        if "--git-common-dir" in argv:
            return module.subprocess.CompletedProcess(argv, 0, stdout=str(repo / ".git") + "\n", stderr="")
        if "--show-toplevel" in argv:
            return module.subprocess.CompletedProcess(argv, 0, stdout=str(repo) + "\n", stderr="")
        if "--git-dir" in argv:
            return module.subprocess.CompletedProcess(argv, 0, stdout=str(repo / ".git") + "\n", stderr="")
        if "branch" in argv and "--show-current" in argv:
            return module.subprocess.CompletedProcess(argv, 0, stdout="factory/demo/inc-001\n", stderr="")
        return module.subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    payload = {
        "projects": [{
            "project_id": "demo",
            "repo_path": str(repo),
            "metadata": {"repo_strategy": {"primary_repo_path": str(repo), "base_branch": "main"}},
        }],
    }
    claim = {"task": {"project_id": "demo", "branch": "factory/demo/inc-001", "worktree_path": str(repo)}}

    result = module._prepare_worktree(payload, claim)

    assert result["ready"] is False
    assert result["reason"] == "worktree_path_not_isolated"


def test_prepare_existing_real_linked_worktree_is_accepted(tmp_path):
    module = _load_orchestrator_module()
    repo = tmp_path / "repo"
    worktree = tmp_path / "worktrees" / "inc-001"
    branch = "factory/demo/inc-001"
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True, text=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "factory-test@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Factory Test"], check=True)
    (repo / "README.md").write_text("factory test\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "README.md"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "initial"], check=True, capture_output=True, text=True)
    worktree.parent.mkdir(parents=True)
    subprocess.run(["git", "-C", str(repo), "worktree", "add", "-b", branch, str(worktree), "HEAD"], check=True, capture_output=True, text=True)

    payload = {
        "projects": [{
            "project_id": "demo",
            "repo_path": str(repo),
            "metadata": {"repo_strategy": {"primary_repo_path": str(repo), "base_branch": "main"}},
        }],
    }
    claim = {"task": {"project_id": "demo", "branch": branch, "worktree_path": str(worktree)}}

    result = module._prepare_worktree(payload, claim)

    assert result["ready"] is True
    assert result["reason"] == "worktree_exists"
    assert result["cwd"] == str(worktree)


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

from __future__ import annotations

import argparse
import importlib.util
import json
import os
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


def _write_complete_factory_source(root: Path, marker: str) -> None:
    (root / "hermes_cli").mkdir(parents=True, exist_ok=True)
    (root / "scripts" / "factory").mkdir(parents=True, exist_ok=True)
    (root / "hermes_cli" / "main.py").write_text(f"# {marker} main\n", encoding="utf-8")
    (root / "hermes_cli" / "factory.py").write_text(f"# {marker} factory cli\n", encoding="utf-8")
    (root / "hermes_cli" / "factory_pg.py").write_text(f"# {marker} factory backend\n", encoding="utf-8")
    (root / "scripts" / "factory" / "factory_orchestrator_tick.py").write_text(
        f"print('{{\"source\": \"{marker}\"}}')\n",
        encoding="utf-8",
    )


def _git_env() -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    return env


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        env=_git_env(),
    ).stdout.strip()


def _make_stale_primary_with_configured_base_worktree(tmp_path: Path) -> tuple[Path, Path, str, str]:
    origin = tmp_path / "origin.git"
    primary = tmp_path / "primary-root"
    updater = tmp_path / "updater"
    current_worktree = tmp_path / "configured-base-source"

    subprocess.run(["git", "init", "--bare", str(origin)], check=True, capture_output=True, text=True, env=_git_env())
    subprocess.run(["git", "clone", str(origin), str(primary)], check=True, capture_output=True, text=True, env=_git_env())
    _git(primary, "config", "user.email", "factory@example.com")
    _git(primary, "config", "user.name", "Factory Test")
    _write_complete_factory_source(primary, "stale-primary")
    _git(primary, "add", "hermes_cli", "scripts")
    _git(primary, "commit", "-m", "stale primary factory source")
    stale_sha = _git(primary, "rev-parse", "HEAD")
    _git(primary, "branch", "-M", "main")
    _git(primary, "push", "origin", "main")
    _git(origin, "symbolic-ref", "HEAD", "refs/heads/main")

    subprocess.run(["git", "clone", str(origin), str(updater)], check=True, capture_output=True, text=True, env=_git_env())
    _git(updater, "checkout", "main")
    _git(updater, "config", "user.email", "factory@example.com")
    _git(updater, "config", "user.name", "Factory Test")
    _write_complete_factory_source(updater, "configured-base")
    _git(updater, "add", "hermes_cli", "scripts")
    _git(updater, "commit", "-m", "configured base factory source")
    current_sha = _git(updater, "rev-parse", "HEAD")
    _git(updater, "push", "origin", "main")
    _git(primary, "fetch", "origin", "main:refs/remotes/origin/main")
    _git(primary, "worktree", "add", "--detach", str(current_worktree), "origin/main")
    return primary, current_worktree, stale_sha, current_sha



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


def test_project_tick_uses_running_source_tree_not_profile_wrapper(monkeypatch, tmp_path):
    stale_wrapper = tmp_path / ".hermes" / "scripts" / "factory_orchestrator_tick.py"
    stale_wrapper.parent.mkdir(parents=True)
    stale_wrapper.write_text(
        "SCRIPT = '/home/jean/Projects/hermes-agent-original/scripts/factory/factory_orchestrator_tick.py'\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    captured: dict[str, Any] = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = [str(part) for part in argv]
        captured["kwargs"] = kwargs
        return factory.subprocess.CompletedProcess(
            argv,
            0,
            stdout=json.dumps({"job": "factory_orchestrator_tick", "source": "running_tree"}),
            stderr="",
        )

    monkeypatch.setattr(factory.subprocess, "run", fake_run)

    result = factory._run_orchestrator_script("demo-project")

    running_root = Path(factory.__file__).resolve().parents[1]
    expected_script = running_root / "scripts" / "factory" / "factory_orchestrator_tick.py"
    assert result["source"] == "running_tree"
    assert result["factory_cli_source_root"] == str(running_root)
    assert result["factory_orchestrator_script"] == str(expected_script)
    assert captured["argv"] == [sys.executable, str(expected_script)]
    assert captured["argv"][1] != str(stale_wrapper)
    assert captured["kwargs"]["cwd"] == str(running_root)
    env = captured["kwargs"]["env"]
    assert env["FACTORY_TICK_PROJECT_ID"] == "demo-project"
    assert env["PYTHONPATH"].split(os.pathsep)[0] == str(running_root)


def test_project_tick_prefers_isolated_cwd_source_over_stale_running_module(monkeypatch, tmp_path):
    stale_primary = tmp_path / "stale-primary" / "hermes_cli" / "factory.py"
    stale_primary.parent.mkdir(parents=True)
    stale_primary.write_text("# stale primary module\n", encoding="utf-8")
    (stale_primary.parents[1] / "scripts" / "factory").mkdir(parents=True)
    (stale_primary.parents[1] / "scripts" / "factory" / "factory_orchestrator_tick.py").write_text(
        "print('{\"source\": \"stale-primary\"}')\n",
        encoding="utf-8",
    )
    worktree = tmp_path / "current-origin-worktree"
    (worktree / "hermes_cli").mkdir(parents=True)
    (worktree / "scripts" / "factory").mkdir(parents=True)
    (worktree / "hermes_cli" / "main.py").write_text("# current main\n", encoding="utf-8")
    (worktree / "hermes_cli" / "factory.py").write_text("# current factory cli\n", encoding="utf-8")
    (worktree / "hermes_cli" / "factory_pg.py").write_text("# current factory backend\n", encoding="utf-8")
    current_tick = worktree / "scripts" / "factory" / "factory_orchestrator_tick.py"
    current_tick.write_text("print('{}')\n", encoding="utf-8")
    monkeypatch.chdir(worktree)
    monkeypatch.setattr(factory, "__file__", str(stale_primary))

    captured: dict[str, Any] = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = [str(part) for part in argv]
        captured["kwargs"] = kwargs
        return factory.subprocess.CompletedProcess(
            argv,
            0,
            stdout=json.dumps({"job": "factory_orchestrator_tick", "source": "cwd_worktree"}),
            stderr="",
        )

    monkeypatch.setattr(factory.subprocess, "run", fake_run)

    result = factory._run_orchestrator_script("demo-project")

    assert result["source"] == "cwd_worktree"
    assert result["factory_cli_source_root"] == str(worktree)
    assert result["factory_orchestrator_script"] == str(current_tick)
    assert captured["argv"] == [sys.executable, str(current_tick)]
    assert captured["kwargs"]["cwd"] == str(worktree)
    assert captured["kwargs"]["env"]["PYTHONPATH"].split(os.pathsep)[0] == str(worktree)


def test_project_tick_prefers_configured_base_source_when_invoked_from_stale_primary_root(monkeypatch, tmp_path):
    primary, current_worktree, stale_sha, current_sha = _make_stale_primary_with_configured_base_worktree(tmp_path)
    monkeypatch.chdir(primary)
    monkeypatch.setattr(factory, "__file__", str(primary / "hermes_cli" / "factory.py"))
    assert _git(primary, "rev-parse", "HEAD") == stale_sha
    assert _git(primary, "rev-parse", "origin/main") == current_sha

    current_tick = current_worktree / "scripts" / "factory" / "factory_orchestrator_tick.py"
    captured: dict[str, Any] = {}
    real_run = factory.subprocess.run

    def fake_run(argv, **kwargs):
        argv_text = [str(part) for part in argv]
        if argv_text[:2] == [sys.executable, str(current_tick)]:
            captured["argv"] = argv_text
            captured["kwargs"] = kwargs
            return factory.subprocess.CompletedProcess(
                argv,
                0,
                stdout=json.dumps({"job": "factory_orchestrator_tick", "source": "configured-base"}),
                stderr="",
            )
        if argv_text[:2] == [sys.executable, str(primary / "scripts" / "factory" / "factory_orchestrator_tick.py")]:
            raise AssertionError("stale primary orchestrator must not be used for tick dispatch")
        return real_run(argv, **kwargs)

    monkeypatch.setattr(factory.subprocess, "run", fake_run)

    result = factory._run_orchestrator_script("demo-project")

    assert result["source"] == "configured-base"
    assert result["factory_cli_source_root"] == str(current_worktree)
    assert result["factory_orchestrator_script"] == str(current_tick)
    assert captured["argv"] == [sys.executable, str(current_tick)]
    assert captured["kwargs"]["cwd"] == str(current_worktree)
    env = captured["kwargs"]["env"]
    assert env["FACTORY_TICK_PROJECT_ID"] == "demo-project"
    assert env["PYTHONPATH"].split(os.pathsep)[0] == str(current_worktree)


def test_project_tick_fails_closed_when_configured_base_source_is_dirty(monkeypatch, tmp_path):
    primary, current_worktree, stale_sha, current_sha = _make_stale_primary_with_configured_base_worktree(tmp_path)
    (current_worktree / "hermes_cli" / "factory_pg.py").write_text("# dirty configured-base source\n", encoding="utf-8")
    monkeypatch.chdir(primary)
    monkeypatch.setattr(factory, "__file__", str(primary / "hermes_cli" / "factory.py"))
    assert _git(primary, "rev-parse", "HEAD") == stale_sha
    assert _git(primary, "rev-parse", "origin/main") == current_sha

    real_run = factory.subprocess.run

    def fake_run(argv, **kwargs):
        argv_text = [str(part) for part in argv]
        if argv_text[:1] == ["git"]:
            return real_run(argv, **kwargs)
        raise AssertionError("tick dispatch must fail closed instead of running stale or dirty source")

    monkeypatch.setattr(factory.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="configured-base source"):
        factory._run_orchestrator_script("demo-project")


def test_project_tick_fails_closed_when_running_source_provenance_unavailable(monkeypatch, tmp_path):
    stale_wrapper = tmp_path / ".hermes" / "scripts" / "factory_orchestrator_tick.py"
    stale_wrapper.parent.mkdir(parents=True)
    stale_wrapper.write_text("print('{}')\n", encoding="utf-8")
    fake_factory = tmp_path / "installed_without_repo_scripts" / "hermes_cli" / "factory.py"
    fake_factory.parent.mkdir(parents=True)
    fake_factory.write_text("# fake installed module without repo script\n", encoding="utf-8")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(factory, "__file__", str(fake_factory))
    monkeypatch.setattr(
        factory.subprocess,
        "run",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("must not run a stale profile wrapper")),
    )

    with pytest.raises(RuntimeError, match="running Hermes source"):
        factory._run_orchestrator_script("demo-project")


def test_project_tick_fails_closed_when_running_source_provenance_malformed(monkeypatch, tmp_path):
    stale_wrapper = tmp_path / ".hermes" / "scripts" / "factory_orchestrator_tick.py"
    stale_wrapper.parent.mkdir(parents=True)
    stale_wrapper.write_text("print('{}')\n", encoding="utf-8")
    fake_factory = tmp_path / "not_hermes_cli" / "factory.py"
    fake_factory.parent.mkdir(parents=True)
    fake_factory.write_text("# malformed module provenance\n", encoding="utf-8")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(factory, "__file__", str(fake_factory))
    monkeypatch.setattr(
        factory.subprocess,
        "run",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("must not run a stale profile wrapper")),
    )

    with pytest.raises(RuntimeError, match="source provenance malformed"):
        factory._run_orchestrator_script("demo-project")


def test_status_prefers_isolated_cwd_source_over_stale_running_module(monkeypatch, tmp_path, capsys):
    stale_primary = tmp_path / "stale-primary" / "hermes_cli" / "factory.py"
    stale_primary.parent.mkdir(parents=True)
    stale_primary.write_text("# stale primary module\n", encoding="utf-8")
    worktree = tmp_path / "current-origin-worktree"
    (worktree / "hermes_cli").mkdir(parents=True)
    (worktree / "scripts" / "factory").mkdir(parents=True)
    (worktree / "hermes_cli" / "main.py").write_text("# current main\n", encoding="utf-8")
    (worktree / "hermes_cli" / "factory.py").write_text("# current factory cli\n", encoding="utf-8")
    (worktree / "hermes_cli" / "factory_pg.py").write_text("# current factory backend\n", encoding="utf-8")
    (worktree / "scripts" / "factory" / "factory_orchestrator_tick.py").write_text("print('{}')\n", encoding="utf-8")
    monkeypatch.chdir(worktree)
    monkeypatch.setattr(factory, "__file__", str(stale_primary))

    captured: dict[str, Any] = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = [str(part) for part in argv]
        captured["kwargs"] = kwargs
        return factory.subprocess.CompletedProcess(
            argv,
            0,
            stdout=json.dumps({"projects": [{"project_id": "demo", "document_status": []}]}),
            stderr="",
        )

    monkeypatch.setattr(factory.subprocess, "run", fake_run)
    monkeypatch.setattr(factory, "_backend", lambda _args: (_ for _ in ()).throw(AssertionError("stale backend must not be used")))

    rc = factory.cmd_status(argparse.Namespace(project_id="demo", json=True))

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["projects"][0]["project_id"] == "demo"
    assert payload["factory_cli_source_root"] == str(worktree)
    assert payload["factory_status_source_root"] == str(worktree)
    assert payload["factory_status_delegated"] is True
    assert payload["factory_status_delegated_from_source_root"] == str(stale_primary.parents[1])
    assert captured["argv"] == [
        sys.executable,
        "-m",
        "hermes_cli.main",
        "factory",
        "status",
        "demo",
        "--json",
    ]
    assert captured["kwargs"]["cwd"] == str(worktree)
    assert captured["kwargs"]["env"]["PYTHONPATH"].split(os.pathsep)[0] == str(worktree)
    assert captured["kwargs"]["env"]["HERMES_FACTORY_SOURCE_DELEGATED"] == "1"


def test_status_prefers_configured_base_source_when_invoked_from_stale_primary_root(monkeypatch, tmp_path, capsys):
    primary, current_worktree, stale_sha, current_sha = _make_stale_primary_with_configured_base_worktree(tmp_path)
    monkeypatch.chdir(primary)
    monkeypatch.setattr(factory, "__file__", str(primary / "hermes_cli" / "factory.py"))
    assert _git(primary, "rev-parse", "HEAD") == stale_sha
    assert _git(primary, "rev-parse", "origin/main") == current_sha

    captured: dict[str, Any] = {}
    real_run = factory.subprocess.run

    def fake_run(argv, **kwargs):
        argv_text = [str(part) for part in argv]
        if argv_text[:5] == [sys.executable, "-m", "hermes_cli.main", "factory", "status"]:
            captured["argv"] = argv_text
            captured["kwargs"] = kwargs
            return factory.subprocess.CompletedProcess(
                argv,
                0,
                stdout=json.dumps(
                    {
                        "projects": [
                            {
                                "project_id": "demo",
                                "document_status": [
                                    {
                                        "file_name": "PRD.md",
                                        "category": "g1_required",
                                        "blocking": False,
                                        "reviewed": True,
                                        "readiness_source": "configured_base_ref",
                                        "base_commit": current_sha,
                                    }
                                ],
                            }
                        ],
                        "events": [
                            {
                                "event_type": "project_reconciled",
                                "metadata": {"anomalies": ["unvalidated_required_docs"]},
                            }
                        ],
                    }
                ),
                stderr="",
            )
        return real_run(argv, **kwargs)

    monkeypatch.setattr(factory.subprocess, "run", fake_run)
    monkeypatch.setattr(
        factory,
        "_backend",
        lambda _args: (_ for _ in ()).throw(AssertionError("stale primary backend must not be used")),
    )

    rc = factory.cmd_status(argparse.Namespace(project_id="demo", json=True))

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["factory_cli_source_root"] == str(current_worktree)
    assert payload["factory_status_source_root"] == str(current_worktree)
    assert payload["factory_status_delegated"] is True
    assert payload["factory_status_delegated_from_source_root"] == str(primary)
    assert payload["projects"][0]["document_status"][0]["readiness_source"] == "configured_base_ref"
    assert payload["projects"][0]["document_status"][0]["base_commit"] == current_sha
    assert captured["argv"] == [
        sys.executable,
        "-m",
        "hermes_cli.main",
        "factory",
        "status",
        "demo",
        "--json",
    ]
    assert captured["kwargs"]["cwd"] == str(current_worktree)
    env = captured["kwargs"]["env"]
    assert env["PYTHONPATH"].split(os.pathsep)[0] == str(current_worktree)
    assert env["HERMES_FACTORY_SOURCE_DELEGATED"] == "1"


def test_status_keeps_primary_readback_when_configured_base_source_is_unverified(monkeypatch, tmp_path, capsys):
    primary, current_worktree, _stale_sha, _current_sha = _make_stale_primary_with_configured_base_worktree(tmp_path)
    (current_worktree / "hermes_cli" / "factory_pg.py").write_text("# dirty configured-base source\n", encoding="utf-8")
    monkeypatch.chdir(primary)
    monkeypatch.setattr(factory, "__file__", str(primary / "hermes_cli" / "factory.py"))

    real_run = factory.subprocess.run

    def fake_run(argv, **kwargs):
        argv_text = [str(part) for part in argv]
        if argv_text[:5] == [sys.executable, "-m", "hermes_cli.main", "factory", "status"]:
            raise AssertionError("dirty configured-base source must not be used")
        return real_run(argv, **kwargs)

    class FakeBackend:
        @staticmethod
        def status(project_id):
            return {
                "projects": [
                    {
                        "project_id": project_id,
                        "document_status": [
                            {
                                "file_name": "PRD.md",
                                "category": "g1_required",
                                "blocking": True,
                                "reviewed": False,
                                "readiness_source": "primary",
                            }
                        ],
                    }
                ]
            }

    monkeypatch.setattr(factory.subprocess, "run", fake_run)
    monkeypatch.setattr(factory, "_backend", lambda _args: FakeBackend())

    rc = factory.cmd_status(argparse.Namespace(project_id="demo", json=True))

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["factory_cli_source_root"] == str(primary)
    assert payload["factory_status_source_root"] == str(primary)
    assert payload["factory_status_delegated"] is False
    assert payload["projects"][0]["document_status"][0]["blocking"] is True


def test_status_keeps_running_source_when_it_is_ahead_of_configured_base(monkeypatch, tmp_path, capsys):
    primary, current_worktree, _stale_sha, _current_sha = _make_stale_primary_with_configured_base_worktree(tmp_path)
    _git(primary, "merge", "--ff-only", "origin/main")
    (primary / "hermes_cli" / "factory.py").write_text("# ahead feature source\n", encoding="utf-8")
    _git(primary, "add", "hermes_cli/factory.py")
    _git(primary, "commit", "-m", "feature branch factory source")
    assert _git(primary, "rev-parse", "HEAD") != _git(primary, "rev-parse", "origin/main")
    assert _git(current_worktree, "rev-parse", "HEAD") == _git(primary, "rev-parse", "origin/main")
    monkeypatch.chdir(primary)
    monkeypatch.setattr(factory, "__file__", str(primary / "hermes_cli" / "factory.py"))

    real_run = factory.subprocess.run

    def fake_run(argv, **kwargs):
        argv_text = [str(part) for part in argv]
        if argv_text[:5] == [sys.executable, "-m", "hermes_cli.main", "factory", "status"]:
            raise AssertionError("ahead running source must not delegate to the configured-base worktree")
        return real_run(argv, **kwargs)

    class FakeBackend:
        @staticmethod
        def status(project_id):
            return {"projects": [{"project_id": project_id, "document_status": []}]}

    monkeypatch.setattr(factory.subprocess, "run", fake_run)
    monkeypatch.setattr(factory, "_backend", lambda _args: FakeBackend())

    rc = factory.cmd_status(argparse.Namespace(project_id="demo", json=True))

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["factory_cli_source_root"] == str(primary)
    assert payload["factory_status_source_root"] == str(primary)
    assert payload["factory_status_delegated"] is False


def test_resolve_state_prefers_configured_base_source_when_invoked_from_stale_primary_root(monkeypatch, tmp_path, capsys):
    primary, current_worktree, stale_sha, current_sha = _make_stale_primary_with_configured_base_worktree(tmp_path)
    monkeypatch.chdir(primary)
    monkeypatch.setattr(factory, "__file__", str(primary / "hermes_cli" / "factory.py"))
    assert _git(primary, "rev-parse", "HEAD") == stale_sha
    assert _git(primary, "rev-parse", "origin/main") == current_sha

    captured: dict[str, Any] = {}
    real_run = factory.subprocess.run

    def fake_run(argv, **kwargs):
        argv_text = [str(part) for part in argv]
        if argv_text[:6] == [sys.executable, "-m", "hermes_cli.main", "factory", "project", "resolve-state"]:
            captured["argv"] = argv_text
            captured["kwargs"] = kwargs
            return factory.subprocess.CompletedProcess(
                argv,
                0,
                stdout=json.dumps(
                    {
                        "action": "resolve-state",
                        "project_id": "demo",
                        "anomalies": [],
                        "unblocked": {"anomalies": []},
                    }
                ),
                stderr="",
            )
        return real_run(argv, **kwargs)

    monkeypatch.setattr(factory.subprocess, "run", fake_run)
    monkeypatch.setattr(
        factory,
        "_backend",
        lambda _args: (_ for _ in ()).throw(AssertionError("stale primary backend must not be used")),
    )

    rc = factory.cmd_project_action(
        argparse.Namespace(factory_project_command="resolve-state", project_id="demo", json=True)
    )

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["action"] == "resolve-state"
    assert payload["project_id"] == "demo"
    assert payload["factory_cli_source_root"] == str(current_worktree)
    assert payload["factory_project_action_source_root"] == str(current_worktree)
    assert payload["factory_project_action_delegated"] is True
    assert payload["factory_project_action_delegated_from_source_root"] == str(primary)
    assert captured["argv"] == [
        sys.executable,
        "-m",
        "hermes_cli.main",
        "factory",
        "project",
        "resolve-state",
        "demo",
        "--json",
    ]
    assert captured["kwargs"]["cwd"] == str(current_worktree)
    env = captured["kwargs"]["env"]
    assert env["PYTHONPATH"].split(os.pathsep)[0] == str(current_worktree)
    assert env["HERMES_FACTORY_SOURCE_DELEGATED"] == "1"


def test_resolve_state_keeps_primary_readback_when_configured_base_source_is_dirty(monkeypatch, tmp_path, capsys):
    primary, current_worktree, _stale_sha, _current_sha = _make_stale_primary_with_configured_base_worktree(tmp_path)
    (current_worktree / "hermes_cli" / "factory_pg.py").write_text("# dirty configured-base source\n", encoding="utf-8")
    monkeypatch.chdir(primary)
    monkeypatch.setattr(factory, "__file__", str(primary / "hermes_cli" / "factory.py"))

    real_run = factory.subprocess.run

    def fake_run(argv, **kwargs):
        argv_text = [str(part) for part in argv]
        if argv_text[:6] == [sys.executable, "-m", "hermes_cli.main", "factory", "project", "resolve-state"]:
            raise AssertionError("dirty configured-base source must not be used")
        return real_run(argv, **kwargs)

    class FakeBackend:
        @staticmethod
        def control_action(project_id, action):
            return {"action": action, "project_id": project_id, "anomalies": ["unvalidated_required_docs"]}

    monkeypatch.setattr(factory.subprocess, "run", fake_run)
    monkeypatch.setattr(factory, "_backend", lambda _args: FakeBackend())

    rc = factory.cmd_project_action(
        argparse.Namespace(factory_project_command="resolve-state", project_id="demo", json=True)
    )

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["factory_cli_source_root"] == str(primary)
    assert payload["factory_project_action_source_root"] == str(primary)
    assert payload["factory_project_action_delegated"] is False
    assert payload["anomalies"] == ["unvalidated_required_docs"]


def test_resolve_state_keeps_ahead_running_source_local(monkeypatch, tmp_path, capsys):
    primary, current_worktree, _stale_sha, _current_sha = _make_stale_primary_with_configured_base_worktree(tmp_path)
    _git(primary, "merge", "--ff-only", "origin/main")
    (primary / "hermes_cli" / "factory.py").write_text("# ahead feature source\n", encoding="utf-8")
    _git(primary, "add", "hermes_cli/factory.py")
    _git(primary, "commit", "-m", "feature branch factory source")
    assert _git(primary, "rev-parse", "HEAD") != _git(primary, "rev-parse", "origin/main")
    assert _git(current_worktree, "rev-parse", "HEAD") == _git(primary, "rev-parse", "origin/main")
    monkeypatch.chdir(primary)
    monkeypatch.setattr(factory, "__file__", str(primary / "hermes_cli" / "factory.py"))

    real_run = factory.subprocess.run

    def fake_run(argv, **kwargs):
        argv_text = [str(part) for part in argv]
        if argv_text[:6] == [sys.executable, "-m", "hermes_cli.main", "factory", "project", "resolve-state"]:
            raise AssertionError("ahead running source must not delegate to the configured-base worktree")
        return real_run(argv, **kwargs)

    class FakeBackend:
        @staticmethod
        def control_action(project_id, action):
            return {"action": action, "project_id": project_id, "anomalies": ["local_ahead_source"]}

    monkeypatch.setattr(factory.subprocess, "run", fake_run)
    monkeypatch.setattr(factory, "_backend", lambda _args: FakeBackend())

    rc = factory.cmd_project_action(
        argparse.Namespace(factory_project_command="resolve-state", project_id="demo", json=True)
    )

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["factory_cli_source_root"] == str(primary)
    assert payload["factory_project_action_source_root"] == str(primary)
    assert payload["factory_project_action_delegated"] is False
    assert payload["anomalies"] == ["local_ahead_source"]


def test_resolve_state_keeps_diverged_running_source_local(monkeypatch, tmp_path, capsys):
    primary, current_worktree, _stale_sha, current_sha = _make_stale_primary_with_configured_base_worktree(tmp_path)
    (primary / "hermes_cli" / "factory.py").write_text("# diverged feature source\n", encoding="utf-8")
    _git(primary, "add", "hermes_cli/factory.py")
    _git(primary, "commit", "-m", "diverged branch factory source")
    ancestor = subprocess.run(
        ["git", "-C", str(primary), "merge-base", "--is-ancestor", "HEAD", "origin/main"],
        check=False,
        capture_output=True,
        text=True,
        env=_git_env(),
    )
    assert ancestor.returncode == 1
    assert _git(current_worktree, "rev-parse", "HEAD") == current_sha
    monkeypatch.chdir(primary)
    monkeypatch.setattr(factory, "__file__", str(primary / "hermes_cli" / "factory.py"))

    real_run = factory.subprocess.run

    def fake_run(argv, **kwargs):
        argv_text = [str(part) for part in argv]
        if argv_text[:6] == [sys.executable, "-m", "hermes_cli.main", "factory", "project", "resolve-state"]:
            raise AssertionError("diverged running source must not delegate to the configured-base worktree")
        return real_run(argv, **kwargs)

    class FakeBackend:
        @staticmethod
        def control_action(project_id, action):
            return {"action": action, "project_id": project_id, "anomalies": ["local_diverged_source"]}

    monkeypatch.setattr(factory.subprocess, "run", fake_run)
    monkeypatch.setattr(factory, "_backend", lambda _args: FakeBackend())

    rc = factory.cmd_project_action(
        argparse.Namespace(factory_project_command="resolve-state", project_id="demo", json=True)
    )

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["factory_cli_source_root"] == str(primary)
    assert payload["factory_project_action_source_root"] == str(primary)
    assert payload["factory_project_action_delegated"] is False
    assert payload["anomalies"] == ["local_diverged_source"]


def test_resolve_state_prefers_isolated_cwd_source_over_stale_running_module(monkeypatch, tmp_path, capsys):
    stale_primary = tmp_path / "stale-primary" / "hermes_cli" / "factory.py"
    stale_primary.parent.mkdir(parents=True)
    stale_primary.write_text("# stale primary module\n", encoding="utf-8")
    worktree = tmp_path / "current-origin-worktree"
    (worktree / "hermes_cli").mkdir(parents=True)
    (worktree / "scripts" / "factory").mkdir(parents=True)
    (worktree / "hermes_cli" / "main.py").write_text("# current main\n", encoding="utf-8")
    (worktree / "hermes_cli" / "factory.py").write_text("# current factory cli\n", encoding="utf-8")
    (worktree / "hermes_cli" / "factory_pg.py").write_text("# current factory backend\n", encoding="utf-8")
    (worktree / "scripts" / "factory" / "factory_orchestrator_tick.py").write_text("print('{}')\n", encoding="utf-8")
    monkeypatch.chdir(worktree)
    monkeypatch.setattr(factory, "__file__", str(stale_primary))

    captured: dict[str, Any] = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = [str(part) for part in argv]
        captured["kwargs"] = kwargs
        return factory.subprocess.CompletedProcess(
            argv,
            0,
            stdout=json.dumps({"action": "resolve-state", "project_id": "demo", "blockers": []}),
            stderr="",
        )

    monkeypatch.setattr(factory.subprocess, "run", fake_run)
    monkeypatch.setattr(factory, "_backend", lambda _args: (_ for _ in ()).throw(AssertionError("stale backend must not be used")))

    rc = factory.cmd_project_action(argparse.Namespace(factory_project_command="resolve-state", project_id="demo", json=True))

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["action"] == "resolve-state"
    assert payload["project_id"] == "demo"
    assert payload["factory_cli_source_root"] == str(worktree)
    assert payload["factory_project_action_source_root"] == str(worktree)
    assert payload["factory_project_action_delegated"] is True
    assert payload["factory_project_action_delegated_from_source_root"] == str(stale_primary.parents[1])
    assert captured["argv"] == [
        sys.executable,
        "-m",
        "hermes_cli.main",
        "factory",
        "project",
        "resolve-state",
        "demo",
        "--json",
    ]
    assert captured["kwargs"]["cwd"] == str(worktree)
    assert captured["kwargs"]["env"]["PYTHONPATH"].split(os.pathsep)[0] == str(worktree)
    assert captured["kwargs"]["env"]["HERMES_FACTORY_SOURCE_DELEGATED"] == "1"


def test_resolve_state_delegation_failure_does_not_fall_back_to_stale_backend(monkeypatch, tmp_path, capsys):
    stale_primary = tmp_path / "stale-primary" / "hermes_cli" / "factory.py"
    stale_primary.parent.mkdir(parents=True)
    stale_primary.write_text("# stale primary module\n", encoding="utf-8")
    worktree = tmp_path / "current-origin-worktree"
    (worktree / "hermes_cli").mkdir(parents=True)
    (worktree / "scripts" / "factory").mkdir(parents=True)
    (worktree / "hermes_cli" / "main.py").write_text("# current main\n", encoding="utf-8")
    (worktree / "hermes_cli" / "factory.py").write_text("# current factory cli\n", encoding="utf-8")
    (worktree / "hermes_cli" / "factory_pg.py").write_text("# current factory backend\n", encoding="utf-8")
    (worktree / "scripts" / "factory" / "factory_orchestrator_tick.py").write_text("print('{}')\n", encoding="utf-8")
    monkeypatch.chdir(worktree)
    monkeypatch.setattr(factory, "__file__", str(stale_primary))

    def fake_run(argv, **kwargs):
        return factory.subprocess.CompletedProcess(
            argv,
            2,
            stdout="",
            stderr="current-origin resolve failed\n",
        )

    monkeypatch.setattr(factory.subprocess, "run", fake_run)
    monkeypatch.setattr(factory, "_backend", lambda _args: (_ for _ in ()).throw(AssertionError("stale backend must not be used")))

    rc = factory.cmd_project_action(argparse.Namespace(factory_project_command="resolve-state", project_id="demo", json=True))

    captured = capsys.readouterr()
    assert rc == 2
    assert captured.out == ""
    assert "current-origin resolve failed" in captured.err


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

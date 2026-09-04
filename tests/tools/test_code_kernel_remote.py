"""Remote session kernels (tools/code_kernel_remote.py) — hermes-agent#96873.

These tests drive execute_in_remote_kernel against a scripted fake env that
implements the same contract as docker/ssh/modal envs (run-to-completion
execute()), with canned outputs for the spawn/liveness/cell round-trips.
The REAL end-to-end behavior (actual detached processes, real files, real
kill) was verified live on Windows against a bash-backed env; these tests
pin the host-side protocol logic: spawn parsing, liveness handling,
state_lost/state_reset reporting, fail-open, and owner isolation.
"""
import json
import os
import sys
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from tools.code_kernel_remote import (
    _REMOTE_KERNELS,
    _REMOTE_KERNELS_LOCK,
    RemoteKernel,
    execute_in_remote_kernel,
    shutdown_all_remote_kernels,
    shutdown_remote_kernels_for_owner,
)


class ScriptedEnv:
    """Contract-faithful fake: answers env.execute() from a script table.

    Handlers are (substring, callable) pairs checked in order; the callable
    receives the command and returns the result dict.
    """

    def __init__(self, handlers):
        self.handlers = handlers
        self.commands = []

    def get_temp_dir(self):
        return "/tmp"

    def execute(self, command, cwd=None, timeout=None):
        self.commands.append(command)
        for needle, handler in self.handlers:
            if needle in command:
                return handler(command)
        return {"output": "", "returncode": 0}


def _spawn_ok_handlers(cell_results):
    """Handlers for a healthy kernel: spawn returns PID, liveness ALIVE,
    cat of a cell result file returns the next canned payload."""
    results = list(cell_results)

    def cat_handler(command):
        if results:
            return {"output": json.dumps(results.pop(0)), "returncode": 0}
        return {"output": "", "returncode": 0}

    return [
        ("nohup", lambda c: {"output": "PID:4242\n", "returncode": 0}),
        ("kill -0", lambda c: {"output": "ALIVE\n", "returncode": 0}),
        ("cat ", cat_handler),
    ]


def _cell(status="ok", stdout="", execution_count=1, **kw):
    payload = {
        "id": "000001", "status": status, "stdout": stdout, "stderr": "",
        "stdout_clipped": False, "stderr_clipped": False, "traceback": "",
        "execution_count": execution_count,
    }
    payload.update(kw)
    return payload


def _run(env, code="print(1)", *, task="t1", reset=False, timeout=10):
    return execute_in_remote_kernel(
        code, env=env, env_type="ssh", task_env_id=task,
        sandbox_tools=frozenset({"read_file"}), timeout=timeout,
        max_tool_calls=5, reset=reset,
    )


class RemoteKernelBase(unittest.TestCase):
    def setUp(self):
        shutdown_all_remote_kernels()
        # No approval session key in tests → owner falls back to task id,
        # which is exactly the isolation-by-key behavior under test.
        self._ship = patch(
            "tools.code_execution_tool._ship_file_to_remote",
        )
        self._ship.start()
        self._poll = patch(
            "tools.code_execution_tool._rpc_poll_loop",
        )
        self._poll.start()

    def tearDown(self):
        self._ship.stop()
        self._poll.stop()
        shutdown_all_remote_kernels()


class TestSpawnAndReuse(RemoteKernelBase):
    def test_first_call_spawns_second_reuses(self):
        env = ScriptedEnv(_spawn_ok_handlers(
            [_cell(stdout="one\n"), _cell(stdout="two\n", execution_count=2)],
        ))
        first = _run(env)
        self.assertEqual(first["status"], "success", first)
        self.assertFalse(first["kernel"]["reused"])
        second = _run(env)
        self.assertTrue(second["kernel"]["reused"])
        self.assertEqual(second["kernel"]["execution_count"], 2)
        # Exactly one spawn happened.
        self.assertEqual(
            sum(1 for c in env.commands if "nohup" in c), 1,
        )

    def test_spawn_failure_fails_open(self):
        env = ScriptedEnv([
            ("nohup", lambda c: {"output": "sh: cannot fork\n", "returncode": 1}),
        ])
        self.assertIsNone(_run(env))
        self.assertEqual(len(_REMOTE_KERNELS), 0)

    def test_reset_kills_and_respawns(self):
        env = ScriptedEnv(_spawn_ok_handlers([_cell(), _cell()]))
        _run(env)
        result = _run(env, reset=True)
        self.assertTrue(result["kernel"].get("state_reset"))
        self.assertFalse(result["kernel"]["reused"])
        self.assertEqual(sum(1 for c in env.commands if "nohup" in c), 2)

    def test_same_owner_cells_are_serialized_for_the_full_lifecycle(self):
        first_cat = threading.Event()
        release_first = threading.Event()
        second_cat = threading.Event()
        cat_calls = [0]

        def cat_handler(command):
            cat_calls[0] += 1
            if cat_calls[0] == 1:
                first_cat.set()
                release_first.wait(2)
                return {"output": json.dumps(_cell(stdout="one\n")), "returncode": 0}
            second_cat.set()
            return {
                "output": json.dumps(_cell(stdout="two\n", execution_count=2)),
                "returncode": 0,
            }

        env = ScriptedEnv([
            ("nohup", lambda c: {"output": "PID:4242\n", "returncode": 0}),
            ("kill -0", lambda c: {"output": "ALIVE\n", "returncode": 0}),
            ("cat ", cat_handler),
        ])
        results = []
        first = threading.Thread(target=lambda: results.append(_run(env)))
        second = threading.Thread(target=lambda: results.append(_run(env)))
        first.start()
        self.assertTrue(first_cat.wait(2))
        second.start()
        try:
            self.assertFalse(second_cat.wait(0.2))
        finally:
            release_first.set()
            first.join(3)
            second.join(3)

        self.assertFalse(first.is_alive())
        self.assertFalse(second.is_alive())
        self.assertEqual([result["status"] for result in results], ["success", "success"])


class TestDeathDetection(RemoteKernelBase):
    def test_dead_kernel_is_reported_and_respawned(self):
        env = ScriptedEnv(_spawn_ok_handlers([_cell(), _cell()]))
        _run(env)
        # Flip liveness to dead for the next probe only.
        original = env.handlers
        env.handlers = [("kill -0", lambda c: {"output": "", "returncode": 1})] \
            + [h for h in original if h[0] != "kill -0"]
        # Restore ALIVE after the respawn's own probe would run: the spawn
        # path probes liveness once — make the dead answer one-shot.
        state = {"dead_probes": 0}

        def flaky_liveness(command):
            state["dead_probes"] += 1
            if state["dead_probes"] == 1:
                return {"output": "", "returncode": 1}
            return {"output": "ALIVE\n", "returncode": 0}

        env.handlers = [("kill -0", flaky_liveness)] + \
            [h for h in original if h[0] != "kill -0"]
        result = _run(env)
        self.assertEqual(result["status"], "success", result)
        self.assertTrue(result["kernel"].get("state_lost"))
        self.assertIn("state from earlier calls was lost",
                      result["kernel"].get("note", ""))

    def test_cell_timeout_kills_kernel_and_reports(self):
        # cat never returns a result file → cell deadline expires.
        env = ScriptedEnv([
            ("nohup", lambda c: {"output": "PID:77\n", "returncode": 0}),
            ("kill -0", lambda c: {"output": "ALIVE\n", "returncode": 0}),
            ("cat ", lambda c: {"output": "", "returncode": 0}),
        ])
        result = _run(env, timeout=2)
        self.assertEqual(result["status"], "timeout")
        self.assertTrue(result["kernel"]["state_lost"])
        self.assertEqual(len(_REMOTE_KERNELS), 0)
        # The kernel was actually killed on the remote.
        self.assertTrue(any("kill " in c for c in env.commands))

    def test_remote_interrupt_result_kills_kernel_and_reports_interrupted(self):
        env = ScriptedEnv([
            ("nohup", lambda c: {"output": "PID:77\n", "returncode": 0}),
            ("kill -0", lambda c: {"output": "ALIVE\n", "returncode": 0}),
            ("cat ", lambda c: {"output": "[Command interrupted]", "returncode": 130}),
        ])

        result = _run(env)

        self.assertEqual(result["status"], "interrupted")
        self.assertTrue(result["kernel"]["state_lost"])
        self.assertEqual(len(_REMOTE_KERNELS), 0)
        self.assertTrue(any("kill " in c for c in env.commands))

    def test_thread_interrupt_kills_an_existing_kernel(self):
        env = ScriptedEnv(_spawn_ok_handlers([_cell(), _cell()]))
        _run(env)

        with patch("tools.interrupt.is_interrupted", return_value=True):
            result = _run(env)

        self.assertEqual(result["status"], "interrupted")
        self.assertTrue(result["kernel"]["state_lost"])
        self.assertEqual(len(_REMOTE_KERNELS), 0)
        self.assertTrue(any("kill " in c for c in env.commands))

    def test_thread_interrupt_sends_kill_outside_the_interrupted_thread(self):
        from tools.interrupt import is_interrupted, set_interrupt

        class InterruptAwareEnv(ScriptedEnv):
            kill_was_sent = False

            def execute(self, command, cwd=None, timeout=None):
                if command.startswith("pkill"):
                    if is_interrupted():
                        return {"output": "[Command interrupted]", "returncode": 130}
                    self.kill_was_sent = True
                return super().execute(command, cwd=cwd, timeout=timeout)

        env = InterruptAwareEnv(_spawn_ok_handlers([_cell()]))
        _run(env)
        tid = threading.current_thread().ident
        set_interrupt(True, tid)
        try:
            result = _run(env)
        finally:
            set_interrupt(False, tid)

        self.assertEqual(result["status"], "interrupted")
        self.assertTrue(env.kill_was_sent)


class TestOwnershipIsolation(RemoteKernelBase):
    def test_delegated_children_get_their_own_remote_kernels(self):
        """Same invariant as local (#94647 review fix): the child context
        qualifier must key a DIFFERENT remote kernel."""
        from agent.delegation_context import delegated_child_context

        env = ScriptedEnv(_spawn_ok_handlers([_cell(), _cell()]))
        _run(env, task="conv")
        with delegated_child_context("child-9"):
            _run(env, task="conv")
        # Two distinct kernels, two spawns.
        self.assertEqual(len(_REMOTE_KERNELS), 2)
        self.assertEqual(sum(1 for c in env.commands if "nohup" in c), 2)

    def test_owner_disposal_reaps_only_that_owner(self):
        env = ScriptedEnv(_spawn_ok_handlers([_cell(), _cell()]))
        _run(env, task="owner-a")
        _run(env, task="owner-b")
        self.assertEqual(len(_REMOTE_KERNELS), 2)
        shutdown_remote_kernels_for_owner("owner-a")
        self.assertEqual(len(_REMOTE_KERNELS), 1)
        remaining_owner = next(iter(_REMOTE_KERNELS))[0]
        self.assertEqual(remaining_owner, "owner-b")

    def test_live_remote_kernels_are_capped_lru_across_owners(self):
        env = ScriptedEnv(_spawn_ok_handlers([_cell() for _ in range(4)]))
        with patch(
            "tools.code_execution_tool._load_config",
            return_value={"max_session_kernels": 2, "kernel_idle_timeout": 1800},
        ):
            for index in range(4):
                _run(env, task=f"owner-{index}")

        self.assertEqual({key[0] for key in _REMOTE_KERNELS}, {"owner-2", "owner-3"})
        self.assertEqual(len(_REMOTE_KERNELS), 2)

    def test_idle_remote_kernels_are_reaped_on_the_next_call(self):
        env = ScriptedEnv(_spawn_ok_handlers([_cell(), _cell()]))
        _run(env, task="owner-a")
        stale = next(iter(_REMOTE_KERNELS.values()))
        stale.last_used -= 10

        with patch(
            "tools.code_execution_tool._load_config",
            return_value={"max_session_kernels": 4, "kernel_idle_timeout": 1},
        ):
            _run(env, task="owner-b")

        self.assertNotIn("owner-a", {key[0] for key in _REMOTE_KERNELS})
        self.assertIn("owner-b", {key[0] for key in _REMOTE_KERNELS})


class TestIdleReapAndCapEviction(RemoteKernelBase):
    """Unlike local session kernels, remote kernels had no idle-reap or
    process-wide cap: _REMOTE_KERNELS grew one entry per distinct
    (owner, env_type, task_env_id) that was never revisited, for the life
    of the gateway process."""

    def test_idle_expired_kernel_is_reaped_on_next_call(self):
        env = ScriptedEnv(_spawn_ok_handlers([_cell(), _cell()]))
        execute_in_remote_kernel(
            "print(1)", env=env, env_type="ssh", task_env_id="stale",
            sandbox_tools=frozenset(), timeout=10, max_tool_calls=5,
            reset=False, idle_exit=1800,
        )
        self.assertEqual(len(_REMOTE_KERNELS), 1)
        # Backdate the kernel's last_used past the idle window — simulates
        # a key that is never revisited again.
        for kernel in _REMOTE_KERNELS.values():
            kernel.last_used -= 2000
        # A call for a DIFFERENT key must reap the stale entry on entry,
        # without ever touching or reviving it.
        execute_in_remote_kernel(
            "print(1)", env=env, env_type="ssh", task_env_id="fresh",
            sandbox_tools=frozenset(), timeout=10, max_tool_calls=5,
            reset=False, idle_exit=1800,
        )
        owners = {key[0] for key in _REMOTE_KERNELS}
        self.assertNotIn("stale", owners)
        self.assertIn("fresh", owners)

    def test_over_cap_evicts_least_recently_used(self):
        with patch("tools.code_kernel._lifecycle_limits", return_value=(2, 1800)):
            env = ScriptedEnv(_spawn_ok_handlers([_cell() for _ in range(10)]))
            for i in range(3):
                execute_in_remote_kernel(
                    "print(1)", env=env, env_type="ssh", task_env_id=f"owner-{i}",
                    sandbox_tools=frozenset(), timeout=10, max_tool_calls=5,
                    reset=False, idle_exit=1800,
                )
            self.assertEqual(len(_REMOTE_KERNELS), 2)
            owners = {key[0] for key in _REMOTE_KERNELS}
            self.assertNotIn("owner-0", owners)
            self.assertIn("owner-1", owners)
            self.assertIn("owner-2", owners)

    def test_eviction_skips_kernels_with_a_running_cell(self):
        """Cap eviction must never kill a kernel mid-cell (the local-kernel
        race from hermes-agent#101861): a busy kernel stays put and a
        settled one goes instead, even if the busy one is older."""
        import threading

        gate = threading.Event()
        cell_is_running = threading.Event()

        def slow_cat(command):
            cell_is_running.set()
            gate.wait(10)
            return {"output": json.dumps(_cell()), "returncode": 0}

        busy_env = ScriptedEnv([
            ("nohup", lambda c: {"output": "PID:4242\n", "returncode": 0}),
            ("kill -0", lambda c: {"output": "ALIVE\n", "returncode": 0}),
            ("cat ", slow_cat),
        ])
        with patch("tools.code_kernel._lifecycle_limits", return_value=(1, 1800)):
            worker = threading.Thread(target=_run, args=(busy_env,), kwargs={"task": "busy"})
            worker.start()
            self.assertTrue(cell_is_running.wait(2))
            with _REMOTE_KERNELS_LOCK:
                self.assertTrue(any(k.attached for k in _REMOTE_KERNELS.values()))
            env = ScriptedEnv(_spawn_ok_handlers([_cell()]))
            _run(env, task="settled")
            owners = {key[0] for key in _REMOTE_KERNELS}
            self.assertIn("busy", owners)
            gate.set()
            worker.join(10)
        self.assertFalse(any("kill 4242" in c for c in busy_env.commands))

    def test_new_kernel_is_attached_before_another_owner_can_evict_it(self):
        """A freshly spawned kernel must not be evictable before its first
        cell is attached by the owner that created it."""
        busy_spawned = threading.Event()
        busy_paused = threading.Event()
        settled_reached_eviction = threading.Event()
        release_busy = threading.Event()
        busy_cell_started = threading.Event()
        finish_busy_cell = threading.Event()
        killed = []
        real_monotonic = time.monotonic
        locks = {}
        lifecycle_calls = {"settled": 0}

        busy_kernel = RemoteKernel(
            env=ScriptedEnv([]), env_type="ssh", kernel_dir="/tmp/busy",
            pid="101", rpc_token="busy", owner="busy", created=0, last_used=0,
        )
        settled_kernel = RemoteKernel(
            env=ScriptedEnv([]), env_type="ssh", kernel_dir="/tmp/settled",
            pid="202", rpc_token="settled", owner="settled", created=0, last_used=0,
        )

        def _spawn(_env, _env_type, owner, task_env_id, _tools, *, idle_exit):
            if task_env_id == "busy":
                busy_spawned.set()
                return busy_kernel
            return settled_kernel

        def _clock():
            if (
                threading.current_thread().name == "busy-owner"
                and busy_spawned.is_set()
                and not busy_paused.is_set()
            ):
                busy_paused.set()
                release_busy.wait(3)
            return real_monotonic()

        def _limits():
            if threading.current_thread().name == "settled-owner":
                lifecycle_calls["settled"] += 1
                if lifecycle_calls["settled"] == 2:
                    settled_reached_eviction.set()
            return 1, 1800

        def _release_after_old_interleaving():
            # Before the fix, settled reaches eviction while busy is published
            # but unattached. After the fix it waits on the registry lock until
            # this watchdog releases busy, which is then non-evictable.
            settled_reached_eviction.wait(1)
            time.sleep(0.1)
            release_busy.set()

        def _run_cell(kernel, *_args, **_kwargs):
            if kernel is busy_kernel:
                busy_cell_started.set()
                finish_busy_cell.wait(3)
            return {"status": "success"}

        results = []
        with (
            patch("tools.code_kernel._resolve_owner", side_effect=lambda task: task),
            patch("tools.code_kernel._lifecycle_limits", side_effect=_limits),
            patch("tools.code_kernel_remote._owner_lock", side_effect=lambda key: locks.setdefault(key, threading.Lock())),
            patch("tools.code_kernel_remote._spawn_remote_kernel", side_effect=_spawn),
            patch("tools.code_kernel_remote._run_remote_cell", side_effect=_run_cell),
            patch("tools.code_kernel_remote._kill", side_effect=lambda kernel: killed.append(kernel.pid)),
            patch("tools.code_kernel_remote.time.monotonic", side_effect=_clock),
        ):
            busy_worker = threading.Thread(
                target=lambda: results.append(_run(ScriptedEnv([]), task="busy")),
                name="busy-owner",
            )
            settled_worker = threading.Thread(
                target=lambda: results.append(_run(ScriptedEnv([]), task="settled")),
                name="settled-owner",
            )
            releaser = threading.Thread(target=_release_after_old_interleaving)
            busy_worker.start()
            self.assertTrue(busy_paused.wait(2))
            settled_worker.start()
            releaser.start()
            settled_worker.join(5)
            self.assertFalse(settled_worker.is_alive())
            self.assertTrue(busy_cell_started.wait(2))
            finish_busy_cell.set()
            busy_worker.join(5)
            releaser.join(2)

        self.assertFalse(busy_worker.is_alive())
        self.assertFalse(settled_worker.is_alive())
        self.assertNotIn("101", killed)
        self.assertEqual({key[0] for key in _REMOTE_KERNELS}, {"busy", "settled"})
        self.assertEqual([result["status"] for result in results], ["success", "success"])


class TestDispatchIntegration(unittest.TestCase):
    """_execute_remote prefers the kernel and falls open to per-call."""

    def test_execute_remote_uses_kernel_result(self):
        from tools.code_execution_tool import _execute_remote

        fake = {
            "status": "success", "stdout": "kernel says hi\n", "stderr": "",
            "traceback": "", "tool_calls_made": 0,
            "kernel": {"reused": True, "remote": True, "execution_count": 3},
        }
        env = ScriptedEnv([
            ("command -v python3", lambda c: {"output": "OK\n", "returncode": 0}),
        ])
        with patch("tools.code_execution_tool._load_config",
                   return_value={"timeout": 30, "max_tool_calls": 5}), \
             patch("tools.code_execution_tool._get_or_create_env",
                   return_value=(env, "ssh")), \
             patch("tools.code_kernel_remote.execute_in_remote_kernel",
                   return_value=fake):
            result = json.loads(_execute_remote("print()", "t", ["read_file"]))
        self.assertEqual(result["status"], "success")
        self.assertIn("kernel says hi", result["output"])
        self.assertEqual(result["kernel"]["execution_count"], 3)

    def test_execute_remote_falls_open_to_per_call(self):
        from tools.code_execution_tool import _execute_remote
        from unittest.mock import MagicMock

        env = ScriptedEnv([
            ("command -v python3", lambda c: {"output": "OK\n", "returncode": 0}),
            ("python3 script.py", lambda c: {"output": "per-call ran\n",
                                             "returncode": 0}),
        ])
        with patch("tools.code_execution_tool._load_config",
                   return_value={"timeout": 30, "max_tool_calls": 5}), \
             patch("tools.code_execution_tool._get_or_create_env",
                   return_value=(env, "ssh")), \
             patch("tools.code_kernel_remote.execute_in_remote_kernel",
                   return_value=None), \
             patch("tools.code_execution_tool._ship_file_to_remote"), \
             patch("tools.code_execution_tool.threading.Thread",
                   return_value=MagicMock()):
            result = json.loads(_execute_remote("print()", "t", ["read_file"]))
        self.assertEqual(result["status"], "success")
        self.assertIn("per-call ran", result["output"])

    def test_execute_remote_surfaces_runner_clipping_metadata(self):
        from tools.code_execution_tool import _execute_remote

        fake = {
            "status": "success",
            "stdout": "captured head",
            "stderr": "captured error",
            "traceback": "",
            "stdout_clipped": True,
            "stderr_clipped": True,
            "stdout_bytes_total": 90_000,
            "stderr_bytes_total": 20_000,
            "tool_calls_made": 0,
            "kernel": {"reused": False, "remote": True, "execution_count": 1},
        }
        env = ScriptedEnv([
            ("command -v python3", lambda c: {"output": "OK\n", "returncode": 0}),
        ])
        with patch("tools.code_execution_tool._load_config", return_value={"timeout": 30, "max_tool_calls": 5}), \
             patch("tools.code_execution_tool._get_or_create_env", return_value=(env, "ssh")), \
             patch("tools.code_kernel_remote.execute_in_remote_kernel", return_value=fake):
            result = json.loads(_execute_remote("print()", "t", ["read_file"]))

        self.assertTrue(result["stdout_truncated"])
        self.assertTrue(result["stderr_truncated"])
        self.assertEqual(result["stdout_bytes_total"], 90_000)
        self.assertIn("remote kernel clipped", result["warning"])


if __name__ == "__main__":
    unittest.main()

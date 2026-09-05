"""Session-persistent kernels for REMOTE terminal backends (docker/ssh/modal).

Remote backends offer one primitive — ``env.execute(cmd)``, run-to-completion
— so the three things the local kernel gets from owning a child are rebuilt:
a detached runner (``nohup ... &``, PID recorded, ``kill -0`` probed per cell);
a file-based CELL protocol in the kernel dir (``cell_req_NNNNNN.json`` /
``cell_res_NNNNNN.json``), sibling to the unchanged file-based TOOL-RPC protocol
(req_/res_) whose host-side ``_rpc_poll_loop`` starts per cell with the calling
thread's context (= per-cell tool authority); and death detection — a failed
liveness probe reads as *kernel died: state lost* and the next call respawns,
never a hung poll (every wait is bounded by the cell timeout).

Same invariants as local: owner = approval session key with the ``::child::``
qualifier (one resolver in tools.code_kernel), same generated tool stubs, same
output post-processing in the caller. ``reset=true`` kills and respawns. Spawn
failure fails OPEN to the per-call path with a note.
"""
from __future__ import annotations

import atexit
import json
import logging
import secrets
import shlex
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from tools.code_kernel import KernelRegistry

logger = logging.getLogger(__name__)

# A fixed lock stripe serializes registry selection, spawn/reset/liveness, the complete cell
# protocol, and result retirement for one owner key. Fixed stripes avoid an unbounded side
# registry of locks after many short sessions.
_REMOTE_OWNER_LOCKS = tuple(threading.Lock() for _ in range(64))

# Host poll interval for a cell result file; each poll is one env.execute round-trip
# (0.1-0.4s on ssh/docker), so this is a floor, not a rate.
_CELL_POLL_INTERVAL = 0.5

# The remote runner: a forever-loop that polls for cell request files, execs them in one
# persistent namespace, writes response files. Pure files + stdlib only (transport-agnostic);
# cells and tool-RPC share the kernel dir under distinct prefixes. It deliberately does NOT
# reuse tools.code_kernel's RUNNER_CELL_SOURCE: the host folds the runner's OWN clipping into
# the reply's truncation metadata, which needs the pre-clip byte totals per stream that the
# shared cell core does not report.
REMOTE_KERNEL_RUNNER_SOURCE = '''\
"""Auto-generated Hermes REMOTE session-kernel runner (file cell protocol)."""
import contextlib
import io
import json
import os
import sys
import time
import traceback

KDIR = os.environ["HERMES_KERNEL_DIR"]
CELLS = os.path.join(KDIR, "cells")
CAPTURE_LIMIT = {capture_limit}
IDLE_EXIT_SECONDS = {idle_exit}

GLOBALS = {{"__name__": "__main__", "__builtins__": __builtins__}}


def _bounded(text):
    encoded = text.encode("utf-8", errors="replace")
    total_bytes = len(encoded)
    if total_bytes <= CAPTURE_LIMIT:
        return text, False, total_bytes
    return encoded[:CAPTURE_LIMIT].decode("utf-8", errors="replace"), True, total_bytes


def main():
    execution_count = 0
    last_activity = time.time()
    while True:
        pending = sorted(
            f for f in os.listdir(CELLS)
            if f.startswith("cell_req_") and f.endswith(".json")
        )
        if not pending:
            if time.time() - last_activity > IDLE_EXIT_SECONDS:
                return  # self-reap: nobody is talking to us anymore
            time.sleep(0.2)
            continue
        for name in pending:
            req_path = os.path.join(CELLS, name)
            try:
                with open(req_path, "r", encoding="utf-8") as f:
                    request = json.load(f)
            except Exception:
                # Partially-written request (ship in progress): retry next tick.
                continue
            os.remove(req_path)
            last_activity = time.time()
            execution_count += 1
            out, err = io.StringIO(), io.StringIO()
            status = "ok"
            trace = ""
            try:
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    exec(compile(request["code"], "<cell>", "exec"), GLOBALS)
            except SystemExit as exc:
                status = "exit"
                trace = "SystemExit: " + repr(exc.code)
            except BaseException:
                status = "error"
                trace = traceback.format_exc()
            stdout_text, stdout_clipped, stdout_bytes_total = _bounded(out.getvalue())
            stderr_text, stderr_clipped, stderr_bytes_total = _bounded(err.getvalue())
            payload = {{
                "id": request.get("id", ""),
                "status": status,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "stdout_clipped": stdout_clipped,
                "stderr_clipped": stderr_clipped,
                "stdout_bytes_total": stdout_bytes_total,
                "stderr_bytes_total": stderr_bytes_total,
                "traceback": trace,
                "execution_count": execution_count,
            }}
            res_name = name.replace("cell_req_", "cell_res_")
            tmp = os.path.join(CELLS, res_name + ".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False)
            os.replace(tmp, os.path.join(CELLS, res_name))
            if status == "exit":
                return


if __name__ == "__main__":
    main()
'''


def _sh(env, cmd: str, timeout: int = 15) -> str:
    """Run *cmd* on the remote from ``/`` and return its output text."""
    result = env.execute(cmd, cwd="/", timeout=timeout)
    return (result.get("output", "") if isinstance(result, dict) else "") or ""


@dataclass
class RemoteKernel:
    """Host-side record of one detached remote kernel process."""

    env: Any
    env_type: str
    kernel_dir: str
    pid: str
    rpc_token: str
    owner: str
    created: float = field(default_factory=time.monotonic)
    last_used: float = field(default_factory=time.monotonic)
    execution_count: int = 0
    cell_seq: int = 0
    # Cells currently running on this kernel. Reap/evict skip attached
    # kernels: killing one mid-cell tears the runner out from under a live
    # poll loop (same guard as tools.code_kernel, hermes-agent#101861).
    attached: int = 0

    def sh(self, cmd: str, timeout: int = 15) -> str:
        return _sh(self.env, cmd, timeout)

    def is_alive(self) -> bool:
        """Bounded liveness probe: kill -0 through the transport. Any transport failure counts
        as dead — a dropped ssh connection and a dead runner are indistinguishable from here,
        and both have the same correct answer (respawn)."""
        try:
            return "ALIVE" in self.sh(f"kill -0 {shlex.quote(self.pid)} 2>/dev/null && echo ALIVE")
        except Exception:
            return False


def _kernel_key(owner: str, env_type: str, task_env_id: str) -> Tuple:
    return (owner, "remote", env_type, task_env_id)


def _owner_lock(key: Tuple) -> threading.Lock:
    return _REMOTE_OWNER_LOCKS[hash(key) % len(_REMOTE_OWNER_LOCKS)]


# Registry + lock shared-shape with code_kernel; teardown runs outside the lock. Teardown goes
# through the module-level _kill so the interrupt-safe cleanup below stays the only kill seam.
_REGISTRY = KernelRegistry(lambda kernel: _kill(kernel))
_REMOTE_KERNELS: Dict[Tuple, "RemoteKernel"] = _REGISTRY.kernels
_REMOTE_KERNELS_LOCK = _REGISTRY.lock


def _run_cleanup_command(kernel: RemoteKernel, command: str) -> None:
    """Run teardown even when the calling tool thread is interrupted."""
    from tools.interrupt import is_interrupted

    errors: list[BaseException] = []

    def run() -> None:
        try:
            kernel.env.execute(command, cwd="/", timeout=15)
        except BaseException as exc:
            errors.append(exc)

    if not is_interrupted():
        run()
        return

    # Environment.execute cooperatively aborts any command issued on an
    # interrupted thread. Teardown is the exception: run it on a fresh daemon
    # thread whose interrupt state is clean, otherwise the remote runner would
    # survive the interrupted cell we are reporting as killed.
    worker = threading.Thread(target=run, daemon=True)
    worker.start()
    worker.join(timeout=16)
    if worker.is_alive():
        logger.debug("remote kernel cleanup command did not settle in time")
    elif errors:
        raise errors[0]


def _kill(kernel: RemoteKernel) -> None:
    """Best-effort kill of the runner and its subprocesses, then rm -rf."""
    try:
        _run_cleanup_command(
            kernel,
            # Kill the runner's process group if the shell gave it one,
            # falling back to the single PID.
            f"pkill -TERM -P {shlex.quote(kernel.pid)} 2>/dev/null; "
            f"kill {shlex.quote(kernel.pid)} 2>/dev/null; true",
        )
    except Exception:
        logger.debug("remote kernel kill failed (transport?)", exc_info=True)
    try:
        _run_cleanup_command(
            kernel,
            f"rm -rf {shlex.quote(kernel.kernel_dir)}",
        )
    except Exception:
        logger.debug("remote kernel dir cleanup failed", exc_info=True)


def shutdown_all_remote_kernels() -> None:
    _REGISTRY.shutdown()


def shutdown_remote_kernels_for_owner(owner: str) -> None:
    """Session-boundary disposal — wired to the same clear_session hook as
    local kernels, so /new and session close reap both kinds."""
    if owner:
        _REGISTRY.shutdown(owner)


def _reap_unlocked(idle_timeout: int) -> List["RemoteKernel"]:
    """Pop idle-expired, unattached remote kernels; caller tears them down outside the lock. The
    runner self-exits after the same idle window, so this clears the HOST-side entry — without it
    the map grew one entry per never-revisited (owner, env_type, task_env_id) for the gateway's life."""
    now = time.monotonic()
    doomed = [key for key, kernel in _REMOTE_KERNELS.items()
              if kernel.attached == 0 and now - kernel.last_used > idle_timeout]
    return [_REMOTE_KERNELS.pop(key) for key in doomed]


def _evict_over_cap_unlocked(keep: Tuple) -> List["RemoteKernel"]:
    """Pop least-recently-used unattached remote kernels beyond the process-wide cap (the same
    ``max_session_kernels`` bound as local kernels, applied independently to this map)."""
    from tools.code_kernel import _lifecycle_limits
    cap, _ = _lifecycle_limits()
    if len(_REMOTE_KERNELS) <= cap:
        return []
    by_age = sorted((key for key in _REMOTE_KERNELS if key != keep and _REMOTE_KERNELS[key].attached == 0),
                    key=lambda key: _REMOTE_KERNELS[key].last_used)
    return [_REMOTE_KERNELS.pop(key) for key in by_age[: len(_REMOTE_KERNELS) - cap]]


atexit.register(shutdown_all_remote_kernels)


def _spawn_remote_kernel(env, env_type: str, owner: str, task_env_id: str,
                         sandbox_tools: frozenset, *, idle_exit: int) -> Optional[RemoteKernel]:
    """Start a detached kernel runner on the remote. None on failure (dir removed)."""
    from tools.code_execution_tool import (
        MAX_STDOUT_BYTES, _ship_file_to_remote, _env_temp_dir, generate_hermes_tools_module,
    )
    kernel_dir = f"{_env_temp_dir(env)}/hermes_rkernel_{uuid.uuid4().hex[:12]}"
    q_dir = shlex.quote(kernel_dir)
    kernel = None
    try:
        _sh(env, f"mkdir -p {q_dir}/cells {q_dir}/rpc")
        rpc_token = secrets.token_urlsafe(32)
        _ship_file_to_remote(env, f"{kernel_dir}/kernel_runner.py", REMOTE_KERNEL_RUNNER_SOURCE.format(
            capture_limit=MAX_STDOUT_BYTES, idle_exit=idle_exit))
        _ship_file_to_remote(env, f"{kernel_dir}/hermes_tools.py",
                             generate_hermes_tools_module(list(sandbox_tools), transport="file"))
        env_prefix = (f"HERMES_KERNEL_DIR={q_dir} HERMES_RPC_DIR={shlex.quote(kernel_dir + '/rpc')} "
                      f"HERMES_RPC_TOKEN={shlex.quote(rpc_token)} PYTHONDONTWRITEBYTECODE=1 PYTHONPATH={q_dir}")
        started = _sh(env, f"cd {q_dir} && nohup env {env_prefix} python3 kernel_runner.py "
                           f"> {q_dir}/runner.log 2>&1 & echo PID:$!", timeout=20)
        pid = next((line.strip()[4:].strip() for line in started.splitlines()
                    if line.strip().startswith("PID:")), "")
        if not pid.isdigit():
            logger.warning("remote kernel spawn returned no PID: %r", started)
        else:
            candidate = RemoteKernel(env=env, env_type=env_type, kernel_dir=kernel_dir,
                                     pid=pid, rpc_token=rpc_token, owner=owner)
            if candidate.is_alive():
                kernel = candidate
            else:
                # Died instantly (missing python3 was pre-checked by the caller,
                # so this is unexpected) — surface the runner log.
                try:
                    logger.warning("remote kernel died at spawn: %s",
                                   _sh(env, f"cat {q_dir}/runner.log", timeout=10)[:500])
                except Exception:
                    pass
    except Exception:
        logger.warning("remote kernel spawn failed", exc_info=True)
    if kernel is None:
        try:
            _sh(env, f"rm -rf {q_dir}")
        except Exception:
            pass
    return kernel


def execute_in_remote_kernel(
    code: str,
    *,
    env,
    env_type: str,
    task_env_id: str,
    sandbox_tools: frozenset,
    timeout: int,
    max_tool_calls: int,
    reset: bool,
    idle_exit: int = 1800,
) -> Optional[Dict[str, Any]]:
    """Run one cell in the owner's remote kernel.

    Returns the raw cell result dict (caller does output post-processing),
    or ``None`` when no kernel could be spawned — the caller falls open to
    the per-call path. ``state_lost`` / ``state_reset`` / ``reused`` ride in
    the ``kernel`` sub-dict, matching the local kernel's result shape.
    """
    from tools.code_kernel import _resolve_owner

    owner = _resolve_owner(task_env_id)
    key = _kernel_key(owner, env_type, task_env_id)
    with _owner_lock(key):
        return _execute_in_remote_kernel_locked(
            code,
            env=env,
            env_type=env_type,
            task_env_id=task_env_id,
            sandbox_tools=sandbox_tools,
            timeout=timeout,
            max_tool_calls=max_tool_calls,
            reset=reset,
            idle_exit=idle_exit,
            owner=owner,
            key=key,
        )


def _interrupted_result(*, reused: bool, tool_calls_made: int = 0) -> Dict[str, Any]:
    return {
        "status": "interrupted",
        "stdout": "",
        "stderr": "",
        "traceback": "",
        "tool_calls_made": tool_calls_made,
        "kernel": {
            "reused": reused,
            "remote": True,
            "ended": True,
            "state_lost": True,
            "note": (
                "Cell interrupted; the remote session kernel was killed and "
                "its state was lost. The next call starts a fresh kernel."
            ),
        },
    }


def _execute_in_remote_kernel_locked(
    code: str,
    *,
    env,
    env_type: str,
    task_env_id: str,
    sandbox_tools: frozenset,
    timeout: int,
    max_tool_calls: int,
    reset: bool,
    idle_exit: int,
    owner: str,
    key: Tuple,
) -> Optional[Dict[str, Any]]:
    """Execute while the owner-key lock is held for the full cell lifecycle."""
    from tools.code_kernel import _lifecycle_limits
    from tools.interrupt import is_interrupted

    state_lost = False
    state_reset = False
    _, configured_idle = _lifecycle_limits()
    idle_exit = configured_idle

    with _REMOTE_KERNELS_LOCK:
        had_current = key in _REMOTE_KERNELS
        expired = _reap_unlocked(idle_exit)
        kernel = _REMOTE_KERNELS.get(key)
    if had_current and kernel is None:
        state_lost = True
    for doomed in expired:
        _kill(doomed)

    if kernel is not None and reset:
        _REGISTRY.discard(key, kernel)
        kernel = None
        state_reset = True

    if is_interrupted():
        if kernel is not None:
            _REGISTRY.discard(key, kernel)
        return _interrupted_result(reused=kernel is not None)

    if kernel is not None and not kernel.is_alive():
        # Transport drop, container restart, self-reaped on idle, OOM — all the same answer:
        # report the loss, respawn fresh (the kill is then only best-effort dir cleanup;
        # the process is already gone).
        _REGISTRY.discard(key, kernel)
        kernel = None
        state_lost = True
        if is_interrupted():
            return _interrupted_result(reused=True)

    reused = kernel is not None
    spawned = False
    if kernel is None:
        kernel = _spawn_remote_kernel(
            env, env_type, owner, task_env_id, sandbox_tools,
            idle_exit=idle_exit,
        )
        if kernel is None:
            return None  # fail open to per-call
        spawned = True

    # A newly created kernel is published and attached under one registry
    # lock. Another owner can enforce the process-wide cap concurrently, so
    # publishing it first would expose a brief but real eviction window before
    # its first cell starts.
    with _REMOTE_KERNELS_LOCK:
        kernel.attached += 1
        if spawned:
            _REMOTE_KERNELS[key] = kernel
        kernel.last_used = time.monotonic()
        evicted = _evict_over_cap_unlocked(keep=key)
    for doomed in evicted:
        _kill(doomed)
    try:
        return _run_remote_cell(
            kernel, key, code, env=env, task_env_id=task_env_id,
            sandbox_tools=sandbox_tools, timeout=timeout,
            max_tool_calls=max_tool_calls, reused=reused,
            state_reset=state_reset, state_lost=state_lost,
        )
    finally:
        with _REMOTE_KERNELS_LOCK:
            kernel.attached -= 1
            kernel.last_used = time.monotonic()


def _run_remote_cell(
    kernel: RemoteKernel,
    key: Tuple,
    code: str,
    *,
    env,
    task_env_id: str,
    sandbox_tools: frozenset,
    timeout: int,
    max_tool_calls: int,
    reused: bool,
    state_reset: bool,
    state_lost: bool,
) -> Dict[str, Any]:
    from tools.code_execution_tool import (
        _rpc_poll_loop,
        _ship_file_to_remote,
    )
    from tools.interrupt import is_interrupted
    from tools.thread_context import propagate_context_to_thread
    kernel.cell_seq += 1
    seq = f"{kernel.cell_seq:06d}"
    q_cells = shlex.quote(f"{kernel.kernel_dir}/cells")

    # Clean stale tool-RPC requests from a previous cell before arming this
    # cell's poll loop, so a background thread the last cell leaked cannot
    # smuggle a call into this cell's authority window.
    q_rpc = shlex.quote(kernel.kernel_dir + '/rpc')
    try:
        kernel.sh(f"rm -f {q_rpc}/req_* {q_rpc}/res_*", timeout=10)
    except Exception:
        pass

    tool_call_log: list = []
    tool_call_counter = [0]
    stop_event = threading.Event()
    # Per-cell RPC thread carrying THIS call's approval/session context —
    # the remote analogue of CellAuthority: authority lives exactly as long
    # as the cell's poll loop.
    rpc_thread = threading.Thread(
        target=propagate_context_to_thread(_rpc_poll_loop),
        args=(
            env, f"{kernel.kernel_dir}/rpc", task_env_id,
            tool_call_log, tool_call_counter, max_tool_calls,
            sandbox_tools, stop_event, kernel.rpc_token,
        ),
        daemon=True,
    )
    rpc_thread.start()

    cell_status = "no-result"
    cell_payload: Dict[str, Any] = {}
    try:
        request = json.dumps({"id": seq, "code": code}, ensure_ascii=False)
        _ship_file_to_remote(
            env, f"{kernel.kernel_dir}/cells/cell_req_{seq}.json.tmp", request,
        )
        moved = env.execute(
            f"mv {q_cells}/cell_req_{seq}.json.tmp {q_cells}/cell_req_{seq}.json",
            cwd="/", timeout=10,
        )
        if is_interrupted() or moved.get("returncode") == 130:
            cell_status = "interrupted"
        else:
            deadline = time.monotonic() + timeout
            res_name = f"cell_res_{seq}.json"
            while time.monotonic() < deadline:
                if is_interrupted():
                    cell_status = "interrupted"
                    break
                try:
                    probe = env.execute(
                        f"cat {q_cells}/{shlex.quote(res_name)} 2>/dev/null",
                        cwd="/", timeout=20,
                    )
                except Exception:
                    if is_interrupted():
                        cell_status = "interrupted"
                        break
                    # One flaky round-trip is not kernel death; liveness decides.
                    time.sleep(_CELL_POLL_INTERVAL)
                    continue
                if probe.get("returncode") == 130 or is_interrupted():
                    cell_status = "interrupted"
                    break
                body = (probe.get("output", "") or "").strip()
                if body:
                    try:
                        cell_payload = json.loads(body)
                        cell_status = cell_payload.get("status", "error")
                    except ValueError:
                        cell_status = "protocol-error"
                    removed = env.execute(
                        f"rm -f {q_cells}/{shlex.quote(res_name)}",
                        cwd="/", timeout=10,
                    )
                    if removed.get("returncode") == 130 or is_interrupted():
                        cell_status = "interrupted"
                    break
                time.sleep(_CELL_POLL_INTERVAL)
            else:
                cell_status = "timeout"
    except Exception:
        if is_interrupted():
            cell_status = "interrupted"
        else:
            raise
    finally:
        stop_event.set()
        rpc_thread.join(timeout=5)

    if cell_status == "interrupted":
        _REGISTRY.discard(key, kernel)
        return _interrupted_result(
            reused=reused,
            tool_calls_made=tool_call_counter[0],
        )

    if cell_status in ("timeout", "protocol-error", "no-result"):
        # No safe way to interrupt one cell in place (same contract as
        # local): kill the kernel, report the loss, respawn next call.
        _REGISTRY.discard(key, kernel)
        return {
            "status": "timeout" if cell_status == "timeout" else "error",
            "stdout": "",
            "stderr": "",
            "traceback": "",
            "tool_calls_made": tool_call_counter[0],
            "kernel": {
                "reused": reused,
                "remote": True,
                "ended": True,
                "state_lost": True,
                "note": (
                    "Cell timed out; the remote session kernel was killed and "
                    "its state was lost. The next call starts a fresh kernel."
                    if cell_status == "timeout" else
                    "Remote kernel protocol failure; kernel killed, state lost."
                ),
            },
        }

    if cell_status == "exit":
        _REGISTRY.discard(key, kernel)

    kernel.execution_count = int(cell_payload.get("execution_count", 0) or 0)

    result: Dict[str, Any] = {
        "status": "success" if cell_status in ("ok", "exit") else "error",
        "stdout": cell_payload.get("stdout", ""),
        "stderr": cell_payload.get("stderr", ""),
        "traceback": cell_payload.get("traceback", ""),
        "stdout_clipped": bool(cell_payload.get("stdout_clipped")),
        "stderr_clipped": bool(cell_payload.get("stderr_clipped")),
        "stdout_bytes_total": int(cell_payload.get("stdout_bytes_total", 0) or 0),
        "stderr_bytes_total": int(cell_payload.get("stderr_bytes_total", 0) or 0),
        "tool_calls_made": tool_call_counter[0],
        "kernel": {
            "reused": reused,
            "remote": True,
            "execution_count": kernel.execution_count,
        },
    }
    if cell_status == "exit":
        result["kernel"]["ended"] = True
    if state_reset:
        result["kernel"]["state_reset"] = True
    if state_lost:
        result["kernel"]["state_lost"] = True
        result["kernel"]["note"] = (
            "The previous remote kernel was gone (transport drop, container "
            "restart, or idle self-exit); state from earlier calls was lost "
            "and a fresh kernel was started."
        )
    if cell_status == "error" and result["traceback"]:
        result["error"] = result["traceback"].strip().splitlines()[-1]
    return result


# ---- BEGIN PLUGIN-COMPAT (revert-scheduled; see COMPAT_MANIFEST.md) ----
# Names external plugins imported from this module before the Sep 2026 decomposition.
# Internal code MUST NOT use these (scripts/check_compat_pointers.py fails CI if it does).
# The whole block is removed by reverting the commit that added it.
import base64  # noqa: F401,E402
# ---- END PLUGIN-COMPAT ----

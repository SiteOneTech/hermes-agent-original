"""Regression tests for the Feishu adapter's owned SDK executor.

Blocking Feishu SDK calls used to run on asyncio's shared default executor.
When that executor was torn down (agent thread exit / loop cleanup), every
subsequent send failed permanently with "Executor shutdown has been called"
and the gateway became a zombie. The adapter now owns its own
ThreadPoolExecutor and recreates it on demand if it has been shut down.

Covers: #10849, #111020
"""

import asyncio
import concurrent.futures
import json

import pytest

from plugins.platforms.feishu.adapter import FeishuAdapter


def _bare_adapter() -> FeishuAdapter:
    """A FeishuAdapter with only the executor fields wired (no __init__)."""
    adapter = object.__new__(FeishuAdapter)
    import threading

    adapter._sdk_executor_lock = threading.Lock()
    adapter._sdk_executor = None
    adapter._sdk_executor_closing = False
    return adapter


def test_get_executor_creates_pool():
    adapter = _bare_adapter()
    executor = adapter._get_sdk_executor()
    assert isinstance(executor, concurrent.futures.ThreadPoolExecutor)
    # Same instance returned while alive.
    assert adapter._get_sdk_executor() is executor
    adapter._shutdown_sdk_executor()


def test_get_executor_recreates_after_shutdown():
    """A shut-down pool must be transparently replaced — the #10849 recovery."""
    adapter = _bare_adapter()
    first = adapter._get_sdk_executor()
    first.shutdown(wait=True)
    assert getattr(first, "_shutdown", False) is True

    second = adapter._get_sdk_executor()
    assert second is not first
    assert getattr(second, "_shutdown", False) is False
    adapter._shutdown_sdk_executor()


def test_shutdown_clears_reference():
    adapter = _bare_adapter()
    adapter._get_sdk_executor()
    adapter._shutdown_sdk_executor()
    assert adapter._sdk_executor is None
    # Idempotent.
    adapter._shutdown_sdk_executor()


@pytest.mark.asyncio
async def test_run_blocking_executes_on_owned_pool():
    adapter = _bare_adapter()
    captured = {}

    def _work(value):
        import threading

        captured["thread"] = threading.current_thread().name
        return value * 2

    result = await adapter._run_blocking(_work, 21)
    assert result == 42
    # Ran on the adapter-owned pool, not the default executor.
    assert captured["thread"].startswith("hermes-feishu-sdk")
    adapter._shutdown_sdk_executor()


@pytest.mark.asyncio
async def test_run_blocking_survives_pool_shutdown():
    """After the pool is shut down, _run_blocking transparently recovers."""
    adapter = _bare_adapter()
    assert await adapter._run_blocking(lambda: "first") == "first"

    adapter._shutdown_sdk_executor()

    # _shutdown set the closing flag, so this would now refuse — re-arm first
    # the way a reconnect does, then the next call rebuilds the pool.
    adapter._sdk_executor_closing = False
    assert await adapter._run_blocking(lambda: "second") == "second"
    adapter._shutdown_sdk_executor()


def test_closing_flag_refuses_resurrection():
    """A real disconnect/shutdown must NOT be resurrected by the recreate path."""
    adapter = _bare_adapter()
    adapter._get_sdk_executor()  # build a live pool
    adapter._shutdown_sdk_executor()  # real teardown sets _closing

    assert adapter._sdk_executor_closing is True
    with pytest.raises(RuntimeError, match="shutting down"):
        adapter._get_sdk_executor()


@pytest.mark.asyncio
async def test_reconnect_rearms_executor():
    """connect() clears the closing flag so a reconnect can use the pool again."""
    import threading

    adapter = object.__new__(FeishuAdapter)
    adapter._sdk_executor_lock = threading.Lock()
    adapter._sdk_executor = None
    adapter._sdk_executor_closing = True  # as if a prior disconnect ran

    # connect() bails early (no creds) but must still re-arm the executor.
    adapter._app_id = ""
    adapter._app_secret = ""
    ok = await adapter.connect()
    assert ok is False  # bailed on missing creds
    assert adapter._sdk_executor_closing is False
    # And now the executor is usable again.
    assert await adapter._run_blocking(lambda: "rearmed") == "rearmed"
    adapter._shutdown_sdk_executor()


@pytest.mark.asyncio
async def test_is_duplicate_flush_survives_default_executor_teardown(
    tmp_path, monkeypatch
):
    """The inbound dedup flush must not ride the loop's default executor.

    After the adapter's background event loop dies, its teardown shuts the
    default executor down; every subsequent inbound message was then dropped
    inside the dedup gate with a RuntimeError out of asyncio.to_thread
    (#111020). The flush now runs on the adapter-owned pool, mirroring the
    outbound SDK calls (#10849).
    """
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    from gateway.config import PlatformConfig

    adapter = FeishuAdapter(PlatformConfig())
    loop = asyncio.get_running_loop()
    # Save/restore via the private slot: set_default_executor() rejects None, but the
    # pristine state is exactly "no default executor set yet" (lazy creation on first use).
    original_executor = loop._default_executor
    try:
        torn_down = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        loop.set_default_executor(torn_down)
        torn_down.shutdown(wait=True)

        # Scenario premise: with the default executor torn down, to_thread fails.
        with pytest.raises(RuntimeError):
            await asyncio.to_thread(lambda: None)

        # The dedup gate must still admit the message and flush it to disk.
        assert await adapter._is_duplicate("om_after_executor_teardown") is False
        state = json.loads(
            (tmp_path / "feishu_seen_message_ids.json").read_text(encoding="utf-8")
        )
        assert "om_after_executor_teardown" in state["message_ids"]
    finally:
        loop._default_executor = original_executor
        adapter._shutdown_sdk_executor()


@pytest.mark.asyncio
async def test_run_blocking_propagates_caller_contextvars(tmp_path, monkeypatch):
    """Call sites moved off asyncio.to_thread must keep seeing the caller's context: a
    multiplexed profile's HERMES_HOME override is a contextvar, and a worker that lost it
    would flush dedup state / look up threads under the wrong profile."""
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    from gateway.config import PlatformConfig
    from hermes_constants import get_hermes_home_override, reset_hermes_home_override, set_hermes_home_override

    adapter = FeishuAdapter(PlatformConfig())
    token = set_hermes_home_override(str(tmp_path / "profiles" / "secondary"))
    try:
        assert await adapter._run_blocking(get_hermes_home_override) == str(tmp_path / "profiles" / "secondary")
    finally:
        reset_hermes_home_override(token)
        adapter._shutdown_sdk_executor()

"""Regression guard for #15000: --resume <id> after compression loses messages.

Context compression ends the current session and forks a new child session
(linked by ``parent_session_id``). The SQLite flush cursor is reset, so
only the latest descendant ends up with rows in the ``messages`` table:
the parent row has ``message_count = 0``. ``hermes --resume <parent_id>``
used to load zero rows and show a blank chat.

The backend's ``resolve_resume_session_id()`` walks the parent → child chain
and redirects to the first descendant that actually has messages. These
tests pin that behaviour.
"""
import time

import pytest

from persistence.sqlite.conversation._store.compression import get_compression_tip
from persistence.sqlite.conversation._store.messages import append_message, resolve_resume_session_id
from persistence.sqlite.conversation._store.sessions import create_session, end_session, list_sessions_rich


@pytest.fixture
def holder(backend, scope_a):
    return backend.open(scope_a).holder()


def _make_chain(holder, ids_with_parent):
    """Create sessions in order, forcing started_at so ordering is deterministic."""
    base = int(time.time()) - 10_000
    for i, (sid, parent) in enumerate(ids_with_parent):
        create_session(holder, sid, source="cli", parent_session_id=parent)
        holder._write_sql("UPDATE sessions SET started_at = ? WHERE id = ?", (base + i * 100, sid))


def test_redirects_from_empty_head_to_descendant_with_messages(holder):
    # Reproducer shape from #15000: 6 sessions, only the 5th holds messages.
    _make_chain(holder, [
        ("head",   None),
        ("mid1",   "head"),
        ("mid2",   "mid1"),
        ("mid3",   "mid2"),
        ("bulk",   "mid3"),    # has messages
        ("tail",   "bulk"),    # empty tail after another compression
    ])
    for i in range(5):
        append_message(holder, "bulk", role="user", content=f"msg {i}")

    assert resolve_resume_session_id(holder, "head") == "bulk"


def test_returns_self_when_only_parent_has_messages(holder):
    # When a session already has messages AND no descendant has messages,
    # it should still be returned.  The chain walk finds no better candidate.
    _make_chain(holder, [("root", None), ("child", "root")])
    append_message(holder, "root", role="user", content="hi")
    assert resolve_resume_session_id(holder, "root") == "root"


def test_returns_self_when_no_descendant_has_messages(holder):
    _make_chain(holder, [("root", None), ("child1", "root"), ("child2", "child1")])
    assert resolve_resume_session_id(holder, "root") == "root"


def test_returns_self_for_isolated_session(holder):
    create_session(holder, "isolated", source="cli")
    assert resolve_resume_session_id(holder, "isolated") == "isolated"


def test_returns_self_for_nonexistent_session(holder):
    assert resolve_resume_session_id(holder, "does_not_exist") == "does_not_exist"


def test_empty_session_id_passthrough(holder):
    assert resolve_resume_session_id(holder, "") == ""
    assert resolve_resume_session_id(holder, None) is None


def test_walks_from_middle_of_chain(holder):
    # If the user happens to know an intermediate ID, we still find the msg-bearing descendant.
    _make_chain(holder, [("a", None), ("b", "a"), ("c", "b"), ("d", "c")])
    append_message(holder, "d", role="user", content="x")
    assert resolve_resume_session_id(holder, "b") == "d"
    assert resolve_resume_session_id(holder, "c") == "d"


def test_follows_compression_tip_when_parent_retains_messages(holder):
    # The bug behind the desktop "I came back and the reply isn't there" report
    # on large sessions: auto-compression ends the live session and forks a
    # continuation child, but a long parent keeps its own flushed message rows.
    # The empty-head walk below never redirects a non-empty head, so resuming
    # the parent id reloaded the pre-compression transcript and the response
    # generated *after* compression (which lives in the continuation) was
    # missing. resolve_resume_session_id must follow the compression-tip chain
    # forward even when the parent still has messages.
    base = int(time.time()) - 10_000
    create_session(holder, "root", source="cli")
    append_message(holder, "root", role="user", content="pre-compression turn")
    end_session(holder, "root", "compression")
    create_session(holder, "cont", source="cli", parent_session_id="root")
    append_message(holder, "cont", role="assistant", content="post-compression reply")
    # Force deterministic ordering so the continuation's started_at is clearly
    # at/after the parent's ended_at (the get_compression_tip discriminator).
    holder._write_sql("UPDATE sessions SET started_at = ?, ended_at = ? WHERE id = 'root'", (base, base + 50))
    holder._write_sql("UPDATE sessions SET started_at = ? WHERE id = 'cont'", (base + 100,))

    assert resolve_resume_session_id(holder, "root") == "cont"


def test_compression_tip_not_confused_with_delegation_child(holder):
    # A delegation/branch child is created while the parent is still live (the
    # parent is NOT ended with end_reason='compression'), so resuming the
    # parent must stay on the parent, not get hijacked into the subagent branch.
    base = int(time.time()) - 10_000
    create_session(holder, "conv", source="cli")
    append_message(holder, "conv", role="user", content="parent turn")
    # Real delegate/subagent sessions carry the `_delegate_from` marker
    # (set in delegate_tool.py) — that marker, not timing, is what
    # distinguishes them from a compression continuation.
    create_session(
        holder,
        "subagent",
        source="subagent",
        parent_session_id="conv",
        model_config={"_delegate_from": "conv"},
    )
    append_message(holder, "subagent", role="assistant", content="delegated work")
    holder._write_sql("UPDATE sessions SET started_at = ? WHERE id = 'conv'", (base,))
    holder._write_sql("UPDATE sessions SET started_at = ? WHERE id = 'subagent'", (base + 100,))

    assert resolve_resume_session_id(holder, "conv") == "conv"


def test_prefers_most_recent_child_when_fork_exists(holder):
    # If a session was somehow forked (two children), pick the latest one.
    # In practice, compression only produces single-chain shape, but the helper
    # should degrade gracefully.
    _make_chain(holder, [
        ("parent", None),
        ("older_fork", "parent"),
        ("newer_fork", "parent"),
    ])
    append_message(holder, "newer_fork", role="user", content="x")
    assert resolve_resume_session_id(holder, "parent") == "newer_fork"


def test_redirects_from_message_bearing_parent_to_child(holder):
    """Fix for problem 2: parent has messages AND child also has messages.

    After context compression the parent holds old messages but the child
    is the active continuation session.  resolve_resume_session_id should
    prefer the latest descendant with messages, not short-circuit on the
    parent.
    """
    _make_chain(holder, [
        ("original", None),
        ("continued", "original"),
    ])
    # Both parent and child have messages
    append_message(holder, "original", role="user", content="old msg")
    append_message(holder, "original", role="assistant", content="old reply")
    append_message(holder, "continued", role="user", content="new msg")
    append_message(holder, "continued", role="assistant", content="new reply")

    assert resolve_resume_session_id(holder, "original") == "continued"


def test_compression_tip_handles_pre_ended_real_child_and_ws_orphan_sibling(holder):
    # Real desktop repro shape from a long GUI session:
    #
    #   root --compression--> real continuation --compression--> live tip
    #     \
    #      `-- stale websocket sibling ended by ws_orphan_reap
    #
    # The real continuation row can be inserted before root.ended_at is written,
    # so the old child.started_at >= parent.ended_at discriminator rejects it and
    # follows the stale websocket sibling instead. That makes the GUI look like
    # the latest conversation was lost. Resuming root must land on live_tip.
    base = int(time.time()) - 10_000
    create_session(holder, "root", source="tui")
    append_message(holder, "root", role="user", content="pre-compression")
    end_session(holder, "root", "compression")

    create_session(holder, "real_cont", source="tui", parent_session_id="root")
    append_message(holder, "real_cont", role="user", content="real continuation")
    end_session(holder, "real_cont", "compression")

    create_session(holder, "ws_orphan", source="tui", parent_session_id="root")
    append_message(holder, "ws_orphan", role="user", content="stale websocket")
    end_session(holder, "ws_orphan", "ws_orphan_reap")

    create_session(holder, "live_tip", source="tui", parent_session_id="real_cont")
    append_message(holder, "live_tip", role="user", content="latest real turn")

    holder._write_sql("UPDATE sessions SET started_at = ?, ended_at = ? WHERE id = 'root'", (base, base + 1000))
    # The real continuation starts before root.ended_at, exactly the race that
    # broke the old timestamp-based chain walk.
    holder._write_sql("UPDATE sessions SET started_at = ?, ended_at = ? WHERE id = 'real_cont'", (base + 500, base + 2000))
    holder._write_sql("UPDATE sessions SET started_at = ?, ended_at = ? WHERE id = 'ws_orphan'", (base + 1000, base + 3000))
    holder._write_sql("UPDATE sessions SET started_at = ? WHERE id = 'live_tip'", (base + 2000,))

    assert get_compression_tip(holder, "root") == "live_tip"
    assert resolve_resume_session_id(holder, "root") == "live_tip"

    listed = list_sessions_rich(holder, limit=10, order_by_last_active=True)
    ids = {row["id"] for row in listed}
    assert "live_tip" in ids
    assert "real_cont" not in ids
    assert "ws_orphan" not in ids

"""Characterization + unit tests for the `run_one_job` shared helper (Phase 4A).

`tick`'s per-job body (`_process_job`) is the execute → save → deliver → mark
sequence that fires ONE due job. Phase 4A extracts it into a module-level
`run_one_job(job, *, adapters=None, loop=None, verbose=False)` so the external
Chronos provider's `fire_due` can reuse the IDENTICAL body — no duplicated
correctness.

The first test characterizes the sequence as driven through `tick()` (proving
the extraction didn't change `tick`'s behavior); the rest unit-test the
extracted helper directly.
"""
import pytest

import cron.scheduler as s


def _patch_pipeline(monkeypatch, *, success=True, output="out", final="final response",
                    error=None, silent_marker_in=None):
    """Patch the job pipeline primitives and record the call order."""
    calls = []

    def fake_run_job(job, *, defer_agent_teardown=None, **kw):
        calls.append(("run_job", job["id"]))
        fr = final if silent_marker_in is None else silent_marker_in
        return (success, output, fr, error)

    def fake_save(jid, out):
        calls.append(("save", jid))
        return f"/tmp/{jid}.txt"

    def fake_deliver(job, content, adapters=None, loop=None, **kwargs):
        calls.append(("deliver", job["id"]))
        return None

    def fake_mark(jid, ok, err=None, delivery_error=None, **_kw):
        calls.append(("mark", jid, ok))

    monkeypatch.setattr(s, "run_job", fake_run_job)
    monkeypatch.setattr(s, "save_job_output", fake_save)
    monkeypatch.setattr(s, "_deliver_result", fake_deliver)
    monkeypatch.setattr(s, "mark_job_run", fake_mark)
    return calls


def test_tick_process_job_sequence(monkeypatch):
    """Characterization: a single due job driven through tick() runs the
    sequence run_job → save → deliver → mark, in that order."""
    calls = _patch_pipeline(monkeypatch)
    monkeypatch.setattr(s, "get_due_jobs", lambda: [{"id": "j1", "name": "t"}])
    monkeypatch.setattr(s, "claim_job_for_fire", lambda _job_id, **_kwargs: True)

    s.tick(verbose=False, sync=True)

    assert [c[0] for c in calls] == ["run_job", "save", "deliver", "mark"]
    assert calls[-1] == ("mark", "j1", True)


def test_tick_skips_job_when_durable_fire_claim_is_lost(monkeypatch):
    """A manual/external fire that wins the shared CAS must exclude ticker."""
    calls = _patch_pipeline(monkeypatch)
    monkeypatch.setattr(s, "get_due_jobs", lambda: [{"id": "j1", "name": "t"}])
    monkeypatch.setattr(s, "claim_job_for_fire", lambda _job_id: False)

    assert s.tick(verbose=False, sync=True) == 0
    assert calls == []


def test_run_one_job_success_sequence(monkeypatch):
    """The extracted helper runs the same execute→save→deliver→mark sequence
    for a successful job."""
    calls = _patch_pipeline(monkeypatch)

    ok = s.run_one_job({"id": "j2", "name": "t"})

    assert ok is True
    assert [c[0] for c in calls] == ["run_job", "save", "deliver", "mark"]
    assert calls[-1] == ("mark", "j2", True)


def test_run_one_job_agent_declared_failure_uses_failure_bookkeeping(monkeypatch):
    """A delegated-child failure reported by the agent is not a healthy cron run."""
    calls = _patch_pipeline(
        monkeypatch,
        final="[CRON_FAILURE]\nThe delegated child could not finish the report.",
    )

    ok = s.run_one_job({"id": "declared-failure", "name": "delegate", "deliver": "telegram"})

    assert ok is True
    assert [call[0] for call in calls] == ["run_job", "save", "deliver", "mark"]
    assert calls[-1] == ("mark", "declared-failure", False)


def test_run_one_job_agent_declared_failure_is_delivered_verbatim(monkeypatch):
    """The agent's own evidence reaches the operator as written, not re-diagnosed by the
    provider-error heuristics (a child that "timed out" is not a model-service timeout)."""
    delivered = []
    evidence = "The export subagent timed out after 30 minutes waiting on the database."
    _patch_pipeline(monkeypatch, final=f"[CRON_FAILURE]\n{evidence}")
    monkeypatch.setattr(
        s, "_deliver_result", lambda job, content, **kw: delivered.append(content))

    s.run_one_job({"id": "verbatim", "name": "nightly export", "deliver": "telegram"})

    assert len(delivered) == 1
    assert evidence.rstrip(".") in delivered[0]
    assert "model service" not in delivered[0]


def test_run_one_job_marker_mentioned_in_report_stays_successful(monkeypatch):
    """Only the exact first line is control text; quoted markers remain report content."""
    calls = _patch_pipeline(
        monkeypatch,
        final="The child documentation says [CRON_FAILURE], but this run recovered.",
    )

    s.run_one_job({"id": "quoted-marker", "name": "delegate", "deliver": "telegram"})

    assert calls[-1] == ("mark", "quoted-marker", True)


def test_run_one_job_exception_delivers_failure_alert(monkeypatch):
    """An exception escaping the run body must not become a silent error row."""
    delivered = []
    marked = []
    finished = []

    monkeypatch.setattr(
        s, "create_execution", lambda *_a, **_kw: {"id": "exec-j3"}
    )
    monkeypatch.setattr(s, "claim_dispatch", lambda _job_id: True)
    monkeypatch.setattr(s, "mark_execution_running", lambda _execution_id: {})
    monkeypatch.setattr(
        s,
        "run_job",
        lambda *_a, **_kw: (_ for _ in ()).throw(
            RuntimeError("Gemini HTTP 503 (UNAVAILABLE)")
        ),
    )
    monkeypatch.setattr(
        s,
        "_deliver_result",
        lambda job, content, **_kw: delivered.append((job["id"], content)) or None,
    )
    monkeypatch.setattr(
        s,
        "mark_job_run",
        lambda *args, **kwargs: marked.append((args, kwargs)),
    )
    monkeypatch.setattr(
        s,
        "finish_execution",
        lambda *args, **kwargs: finished.append((args, kwargs)),
    )

    ok = s.run_one_job({"id": "j3", "name": "morning", "deliver": "telegram"})

    assert ok is False
    assert len(delivered) == 1 and delivered[0][0] == "j3"
    # The notice carries the classifier verdict's gloss from the copy table (whatever its wording),
    # never the raw HTTP code as the lead, plus a retry command.
    from cron.scheduler_failure_copy import _provider_failure_cause, classify_cron_failure_reason
    gloss = _provider_failure_cause(classify_cron_failure_reason("Gemini HTTP 503 (UNAVAILABLE)"))
    assert gloss and gloss in delivered[0][1]
    assert not delivered[0][1].lstrip("⚠️ ").startswith("Gemini HTTP 503")
    assert "hermes cron run j3" in delivered[0][1]
    assert marked == [
        (("j3", False, "Gemini HTTP 503 (UNAVAILABLE)"), {"delivery_error": None})
    ]
    assert finished == [
        (
            ("exec-j3",),
            {
                "success": False,
                "error": "Gemini HTTP 503 (UNAVAILABLE)",
                "delivery_outcome": "delivered",
            },
        )
    ]


def test_run_one_job_exception_records_failure_alert_delivery_error(monkeypatch):
    """A failed fallback alert must populate last_delivery_error."""
    marked = []

    monkeypatch.setattr(
        s, "create_execution", lambda *_a, **_kw: {"id": "exec-j4"}
    )
    monkeypatch.setattr(s, "claim_dispatch", lambda _job_id: True)
    monkeypatch.setattr(s, "mark_execution_running", lambda _execution_id: {})
    monkeypatch.setattr(
        s,
        "run_job",
        lambda *_a, **_kw: (_ for _ in ()).throw(RuntimeError("provider failed")),
    )
    monkeypatch.setattr(s, "_deliver_result", lambda *_a, **_kw: "send failed: 502")
    monkeypatch.setattr(
        s,
        "mark_job_run",
        lambda *args, **kwargs: marked.append((args, kwargs)),
    )
    monkeypatch.setattr(s, "finish_execution", lambda *_a, **_kw: None)

    assert s.run_one_job({"id": "j4", "deliver": "telegram"}) is False
    assert marked == [
        (("j4", False, "provider failed"), {"delivery_error": "send failed: 502"})
    ]


def _patch_escaped_failure(monkeypatch, delivered, *, exec_id, err):
    """Make run_job raise, and capture what the escape handler delivers."""
    monkeypatch.setattr(s, "create_execution", lambda *_a, **_kw: {"id": exec_id})
    monkeypatch.setattr(s, "claim_dispatch", lambda _job_id: True)
    monkeypatch.setattr(s, "mark_execution_running", lambda _execution_id: {})
    monkeypatch.setattr(
        s,
        "run_job",
        lambda *_a, **_kw: (_ for _ in ()).throw(RuntimeError(err)),
    )
    monkeypatch.setattr(
        s,
        "_deliver_result",
        lambda job, content, **_kw: delivered.append(content) or None,
    )
    monkeypatch.setattr(s, "mark_job_run", lambda *_a, **_kw: None)
    monkeypatch.setattr(s, "finish_execution", lambda *_a, **_kw: None)
    # Deterministic threshold: default 3, independent of the host config.
    monkeypatch.setattr(s, "load_config", lambda: {})


def test_escaped_failure_delivery_carries_the_streak_nudge(monkeypatch):
    """A repeatedly-failing job must be nudged even when it fails at the
    scheduler layer (#88655).

    ``mark_job_run`` increments ``failure_streak`` for an escaped failure just
    as it does for an agent failure, so the counter climbs either way. But the
    nudge that spends it was only composed on the normal delivery path, so a
    job that raises before the run body on every tick - a bad import from a
    half-applied update, a provider client that cannot construct - alerts
    forever and is never told it should be reviewed or paused. Nothing else
    surfaces the streak in chat.
    """
    delivered = []
    _patch_escaped_failure(
        monkeypatch, delivered, exec_id="exec-j5", err="cannot import name X"
    )

    ok = s.run_one_job(
        {
            "id": "j5",
            "name": "scout",
            "deliver": "telegram",
            "schedule": {"kind": "interval"},
            "failure_streak": 2,  # + this run = 3 = default threshold
        }
    )

    assert ok is False
    assert len(delivered) == 1
    assert "cannot import name X" in delivered[0]
    assert "failed 3 runs in a row" in delivered[0]
    assert "hermes cron pause scout" in delivered[0]


def test_escaped_failure_delivery_stays_quiet_below_the_threshold(monkeypatch):
    """The nudge is appended, not always-on: a first failure reads as before."""
    delivered = []
    _patch_escaped_failure(
        monkeypatch, delivered, exec_id="exec-j6", err="provider failed"
    )

    ok = s.run_one_job(
        {
            "id": "j6",
            "name": "scout",
            "deliver": "telegram",
            "schedule": {"kind": "interval"},
            "failure_streak": 0,
        }
    )

    assert ok is False
    assert len(delivered) == 1
    assert delivered[0].startswith("⚠️ Cron 'scout' failed: provider failed")
    assert "hermes cron runs j6" in delivered[0]


def test_run_one_job_exception_after_delivery_does_not_redeliver(monkeypatch):
    """Once delivery has been attempted, the outer handler must not send again."""
    delivered = []
    mark_calls = []

    monkeypatch.setattr(
        s, "create_execution", lambda *_a, **_kw: {"id": "exec-j5"}
    )
    monkeypatch.setattr(s, "claim_dispatch", lambda _job_id: True)
    monkeypatch.setattr(s, "mark_execution_running", lambda _execution_id: {})
    monkeypatch.setattr(
        s,
        "run_job",
        lambda *_a, **_kw: (True, "out", "final response", None),
    )
    monkeypatch.setattr(s, "save_job_output", lambda jid, out: f"/tmp/{jid}.txt")
    monkeypatch.setattr(
        s,
        "_deliver_result",
        lambda job, content, **_kw: delivered.append((job["id"], content)) or None,
    )

    def fake_mark(*args, **kwargs):
        mark_calls.append((args, kwargs))
        if len(mark_calls) == 1:
            raise RuntimeError("bookkeeping boom")

    monkeypatch.setattr(s, "mark_job_run", fake_mark)
    monkeypatch.setattr(s, "finish_execution", lambda *_a, **_kw: None)

    ok = s.run_one_job({"id": "j5", "name": "once", "deliver": "telegram"})

    assert ok is False
    assert delivered == [("j5", "final response")]
    assert mark_calls[0] == (("j5", True, None), {"delivery_error": None})
    assert mark_calls[1] == (
        ("j5", False, "bookkeeping boom"),
        {"delivery_error": None},
    )


def test_run_one_job_keyboard_interrupt_skips_delivery_and_reraises(monkeypatch):
    """Hard interrupts must not attempt failure delivery; they re-raise."""
    delivered = []
    marked = []
    finished = []

    monkeypatch.setattr(
        s, "create_execution", lambda *_a, **_kw: {"id": "exec-j6"}
    )
    monkeypatch.setattr(s, "claim_dispatch", lambda _job_id: True)
    monkeypatch.setattr(s, "mark_execution_running", lambda _execution_id: {})
    monkeypatch.setattr(
        s,
        "run_job",
        lambda *_a, **_kw: (_ for _ in ()).throw(KeyboardInterrupt()),
    )
    monkeypatch.setattr(
        s,
        "_deliver_result",
        lambda job, content, **_kw: delivered.append((job["id"], content)) or None,
    )
    monkeypatch.setattr(
        s,
        "mark_job_run",
        lambda *args, **kwargs: marked.append((args, kwargs)),
    )
    monkeypatch.setattr(
        s,
        "finish_execution",
        lambda *args, **kwargs: finished.append((args, kwargs)),
    )

    with pytest.raises(KeyboardInterrupt):
        s.run_one_job({"id": "j6", "name": "interrupt", "deliver": "telegram"})

    assert delivered == []
    assert marked == [(("j6", False, "KeyboardInterrupt"), {})]
    assert finished == [
        (
            ("exec-j6",),
            {
                "success": False,
                "error": "KeyboardInterrupt",
                "delivery_outcome": "suppressed",
            },
        )
    ]


def test_run_one_job_installs_secret_scope_under_multiplex(monkeypatch, tmp_path):
    """Regression: under profile isolation (multiplex active), run_one_job must
    keep one profile secret scope active through execution and delivery so
    credential reads do not fail closed or fall through to another profile,
    then tear the scope down after the complete job lifecycle.

    Behavior contract: the same scope is present during run_job and
    _deliver_result, and no scope remains after run_one_job returns.
    """
    from agent import secret_scope as ss

    # Point cron's home resolution at a profile whose .env carries a secret.
    (tmp_path / ".env").write_text("OPENROUTER_BASE_URL=https://openrouter.ai/api/v1\n")
    monkeypatch.setattr(s, "_get_hermes_home", lambda: tmp_path)

    scope_during_run = {}
    scope_during_delivery = {}

    def fake_run_job(job, *, defer_agent_teardown=None, **kw):
        # This is where resolve_runtime_provider() would read a secret. Prove a
        # scope is installed and the profile's secret resolves without raising.
        scope_during_run["scope"] = ss.current_secret_scope()
        scope_during_run["base_url"] = ss.get_secret("OPENROUTER_BASE_URL")
        return (True, "out", "final", None)

    def fake_deliver(*args, **kwargs):
        scope_during_delivery["scope"] = ss.current_secret_scope()
        scope_during_delivery["base_url"] = ss.get_secret("OPENROUTER_BASE_URL")
        return None

    monkeypatch.setattr(s, "run_job", fake_run_job)
    monkeypatch.setattr(s, "save_job_output", lambda jid, out: f"/tmp/{jid}.txt")
    monkeypatch.setattr(s, "_deliver_result", fake_deliver)
    monkeypatch.setattr(s, "mark_job_run", lambda *a, **k: None)

    ss.set_multiplex_active(True)
    try:
        ok = s.run_one_job({"id": "j7", "name": "t"})
    finally:
        ss.set_multiplex_active(False)

    assert ok is True
    # The same profile scope covered both execution and delivery.
    assert scope_during_run["scope"] is not None
    assert scope_during_run["base_url"] == "https://openrouter.ai/api/v1"
    assert scope_during_delivery["scope"] == scope_during_run["scope"]
    assert scope_during_delivery["base_url"] == "https://openrouter.ai/api/v1"
    # And it was torn down after the full lifecycle returned (no leak).
    assert ss.current_secret_scope() is None


@pytest.mark.parametrize("multiplex_active", [False, True])
def test_run_one_job_refreshes_routed_profile_external_secret_scope_before_run(
    monkeypatch, tmp_path, multiplex_active
):
    """A routed profile must hydrate and isolate its secret snapshot before run+delivery.

    The outer scope wraps both execution and delivery.  A routed job therefore
    cannot defer hydration to ``run_job``: without multiplexing, an empty outer
    scope would otherwise fall through to the launch profile's process env.
    """
    import threading

    from agent import secret_scope as ss
    from agent.secret_sources import registry as secret_registry
    from agent.secret_sources.base import SECRET_SOURCE_API_VERSION, FetchResult, SecretSource
    from hermes_cli import env_loader

    class ProfileVault(SecretSource):
        api_version = SECRET_SOURCE_API_VERSION
        name = "profilevault"
        shape = "mapped"

        def fetch(self, cfg, home_path):
            return FetchResult(secrets={"PROFILE_ONLY_API_KEY": f"secret-for-{home_path.name}"})

    root = tmp_path / "launch"
    profile_home = root / "profiles" / "support"
    (root / "cron").mkdir(parents=True)
    profile_home.mkdir(parents=True)
    (profile_home / "config.yaml").write_text(
        "secrets:\n  profilevault:\n    enabled: true\n", encoding="utf-8"
    )

    monkeypatch.setenv("HERMES_HOME", str(root))
    # Simulate a deployment credential belonging to the launch profile.  It
    # must never satisfy a secret read for the routed support profile.
    monkeypatch.setenv("PROFILE_ONLY_API_KEY", "launch-profile-secret")
    monkeypatch.setenv("LAUNCH_ONLY_API_KEY", "must-not-leak-to-support")
    monkeypatch.setattr(s, "_get_hermes_home", lambda: root)
    monkeypatch.setattr(s, "save_job_output", lambda jid, out: f"/tmp/{jid}.txt")
    monkeypatch.setattr(s, "mark_job_run", lambda *a, **k: None)

    observed = {}

    def fake_run_job(job, *, defer_agent_teardown=None, **kw):
        observed["scope"] = dict(ss.current_secret_scope() or {})
        observed["secret"] = ss.get_secret("PROFILE_ONLY_API_KEY")
        observed["unrelated_launch_secret"] = ss.get_secret("LAUNCH_ONLY_API_KEY")
        return True, "out", "final", None

    def fake_deliver(*args, **kwargs):
        observed["delivery_scope"] = dict(ss.current_secret_scope() or {})
        observed["delivery_secret"] = ss.get_secret("PROFILE_ONLY_API_KEY")
        observed["delivery_unrelated_launch_secret"] = ss.get_secret("LAUNCH_ONLY_API_KEY")
        return None

    monkeypatch.setattr(s, "run_job", fake_run_job)
    monkeypatch.setattr(s, "_deliver_result", fake_deliver)

    secret_registry._reset_registry_for_tests()
    monkeypatch.setattr(secret_registry, "_ensure_builtin_sources", lambda: None)
    assert secret_registry.register_source(ProfileVault())

    # A concurrent job of this same profile can re-pull its sources.  Its
    # reset must remain blocked while this fire turns its fresh snapshot into
    # the mapping passed to set_secret_scope().
    build_started = threading.Event()
    reset_attempted = threading.Event()
    reset_completed = threading.Event()
    original_values = env_loader.get_secret_source_values

    def coordinated_values(home):
        if home == profile_home:
            build_started.set()
            assert reset_attempted.wait(timeout=1)
            assert not reset_completed.wait(timeout=0.1)
        return original_values(home)

    def concurrent_reset():
        if build_started.wait(timeout=1):
            reset_attempted.set()
            env_loader.reset_secret_source_cache(profile_home)
            reset_completed.set()

    monkeypatch.setattr(env_loader, "get_secret_source_values", coordinated_values)
    reset_thread = threading.Thread(target=concurrent_reset, daemon=True)
    reset_thread.start()

    previous_multiplex = ss.is_multiplex_active()
    ss.set_multiplex_active(multiplex_active)
    try:
        assert s.run_one_job({"id": "external-secret", "name": "t", "profile": "support"}) is True
    finally:
        ss.set_multiplex_active(previous_multiplex)
        build_started.set()
        reset_thread.join(timeout=1)
        secret_registry._reset_registry_for_tests()

    assert reset_completed.is_set()
    assert not reset_thread.is_alive()
    assert observed["secret"] == "secret-for-support"
    assert observed["unrelated_launch_secret"] is None
    assert observed["scope"] == {"PROFILE_ONLY_API_KEY": "secret-for-support"}
    assert observed["delivery_secret"] == "secret-for-support"
    assert observed["delivery_unrelated_launch_secret"] is None
    assert observed["delivery_scope"] == observed["scope"]
    assert s.os.environ["PROFILE_ONLY_API_KEY"] == "launch-profile-secret"


def test_run_one_job_explicit_self_profile_keeps_process_secret_fallback(monkeypatch, tmp_path):
    """An explicit ``profile: default`` is self-referential, not cross-profile routing.

    Its profile scope may not contain process-injected credentials (systemd or
    ``op run``), so a scoped miss must keep the single-profile fallback rather
    than treating the job as a secondary-profile run.
    """
    from agent import secret_scope as ss

    root = tmp_path / "launch"
    (root / "cron").mkdir(parents=True)
    monkeypatch.setenv("HERMES_HOME", str(root))
    monkeypatch.setenv("PROCESS_ONLY_API_KEY", "launch-process-secret")
    monkeypatch.setattr(s, "_get_hermes_home", lambda: root)
    monkeypatch.setattr(s, "create_execution", lambda *_a, **_k: {"id": "self-profile-exec"})
    monkeypatch.setattr(s, "claim_dispatch", lambda _job_id: True)
    monkeypatch.setattr(s, "mark_execution_running", lambda _execution_id: {})
    monkeypatch.setattr(s, "save_job_output", lambda jid, out: f"/tmp/{jid}.txt")
    monkeypatch.setattr(s, "_deliver_result", lambda *a, **k: None)
    monkeypatch.setattr(s, "mark_job_run", lambda *a, **k: None)
    monkeypatch.setattr(s, "finish_execution", lambda *a, **k: None)

    observed = {}

    def fake_run_job(job, *, defer_agent_teardown=None, **kw):
        observed["secret"] = ss.get_secret("PROCESS_ONLY_API_KEY")
        return True, "out", "final", None

    monkeypatch.setattr(s, "run_job", fake_run_job)
    previous_multiplex = ss.is_multiplex_active()
    ss.set_multiplex_active(False)
    try:
        assert s.run_one_job({"id": "self-profile", "name": "t", "profile": "default"}) is True
    finally:
        ss.set_multiplex_active(previous_multiplex)

    assert observed["secret"] == "launch-process-secret"
    assert ss.current_secret_scope() is None


def test_run_one_job_secondary_store_without_multiplexing_isolates_launch_secrets(
    monkeypatch, tmp_path
):
    """A secondary store is isolated even when its job has no explicit runtime profile.

    Gateway cron ticks every store on a host, including secondaries when adapter
    multiplexing is off. In that topology the store home differs from the
    process launch home, so it must hydrate its own external source and forbid
    an unset key from falling through to the launch process environment.
    """
    from agent import secret_scope as ss
    from agent.secret_sources import registry as secret_registry
    from agent.secret_sources.base import SECRET_SOURCE_API_VERSION, FetchResult, SecretSource
    from hermes_cli import env_loader

    class ProfileVault(SecretSource):
        api_version = SECRET_SOURCE_API_VERSION
        name = "profilevaultsecondary"
        shape = "mapped"

        def fetch(self, cfg, home_path):
            return FetchResult(secrets={"SECONDARY_ONLY_API_KEY": f"secret-for-{home_path.name}"})

    launch_home = tmp_path / "launch"
    secondary_home = launch_home / "profiles" / "secondary"
    (launch_home / "cron").mkdir(parents=True)
    (secondary_home / "cron").mkdir(parents=True)
    (secondary_home / "config.yaml").write_text(
        "secrets:\n  profilevaultsecondary:\n    enabled: true\n", encoding="utf-8"
    )
    monkeypatch.setenv("HERMES_HOME", str(launch_home))
    monkeypatch.setenv("SECONDARY_ONLY_API_KEY", "launch-secret-must-not-leak")
    monkeypatch.setenv("LAUNCH_ONLY_API_KEY", "launch-only-must-not-leak")
    monkeypatch.setattr(s, "_get_hermes_home", lambda: secondary_home)
    monkeypatch.setattr(s, "_launch_external_cron_worker", lambda _job: False)
    monkeypatch.setattr(s, "create_execution", lambda *_a, **_k: {"id": "secondary-store-exec"})
    monkeypatch.setattr(s, "claim_dispatch", lambda _job_id: True)
    monkeypatch.setattr(s, "mark_execution_running", lambda _execution_id: {})
    monkeypatch.setattr(s, "save_job_output", lambda jid, out: f"/tmp/{jid}.txt")
    monkeypatch.setattr(s, "_deliver_result", lambda *a, **k: None)
    monkeypatch.setattr(s, "mark_job_run", lambda *a, **k: None)
    monkeypatch.setattr(s, "finish_execution", lambda *a, **k: None)

    observed = {}

    def fake_run_job(job, *, defer_agent_teardown=None, **kw):
        observed["secret"] = ss.get_secret("SECONDARY_ONLY_API_KEY")
        observed["launch_only"] = ss.get_secret("LAUNCH_ONLY_API_KEY")
        observed["scope"] = dict(ss.current_secret_scope() or {})
        return True, "out", "final", None

    monkeypatch.setattr(s, "run_job", fake_run_job)
    secret_registry._reset_registry_for_tests()
    monkeypatch.setattr(secret_registry, "_ensure_builtin_sources", lambda: None)
    assert secret_registry.register_source(ProfileVault())
    previous_multiplex = ss.is_multiplex_active()
    ss.set_multiplex_active(False)
    try:
        assert s.run_one_job({"id": "secondary-store", "name": "t"}) is True
    finally:
        ss.set_multiplex_active(previous_multiplex)
        secret_registry._reset_registry_for_tests()
        env_loader.reset_secret_source_cache(secondary_home)

    assert observed == {
        "secret": "secret-for-secondary",
        "launch_only": None,
        "scope": {"SECONDARY_ONLY_API_KEY": "secret-for-secondary"},
    }

"""Canonical backend selection for SitioUno Software Factory state.

Agent Core PostgreSQL is the only production/runtime source of truth for the
Factory. SQLite is not a fallback and must not be selectable through CLI, env, or
scripts; legacy SQLite files are migration artifacts only and should be removed
after reconciliation.
"""
from __future__ import annotations

from types import ModuleType


class FactoryBackendUnavailable(RuntimeError):
    """Raised when the canonical Factory backend cannot be reached."""


def get_backend(*, explicit_sqlite_path: object = None) -> ModuleType:
    """Return the canonical Factory backend module.

    ``explicit_sqlite_path`` is accepted only as a backward-compatible call-site
    parameter so old imports fail with a clear error instead of silently routing
    work to a second source of truth.
    """

    try:
        from hermes_cli import factory_pg

        if factory_pg.available():
            return factory_pg
    except Exception as exc:
        raise FactoryBackendUnavailable(
            "Agent Core Postgres is the only canonical Factory backend and is unavailable. "
            "Start/fix the Agent Core DB; SQLite fallback is disabled."
        ) from exc

    raise FactoryBackendUnavailable(
        "Agent Core Postgres is the only canonical Factory backend and is unavailable. "
        "SQLite fallback is disabled."
    )


def backend_label(*, explicit_sqlite_path: object = None) -> str:
    get_backend(explicit_sqlite_path=explicit_sqlite_path)
    return "agent_core_postgres"

"""Every HTTP route the api_server registers must resolve to a real handler.

Regression guard for a class of bug that broke the platform silently for
months: `_http_route_table()` is built by touching `self._handle_*` while the
attribute is read, so a route whose handler method is missing raises
AttributeError during route construction — the adapter never starts, its port
never binds, and nothing in the route list is obviously wrong. The live symptom
was:

    [Api_Server] Failed to start API server:
    'APIServerAdapter' object has no attribute '_handle_skills'

Commit 1c3b9b389a dropped the _handle_skills and _handle_toolsets bodies but
left both rows in the table. Keeping the assertion on the TABLE (rather than on
a hand-written list of names) means a route can never be added without its
handler, and a handler can never be removed without its route.
"""

import inspect
import re

import pytest

from gateway.config import PlatformConfig
from gateway.platforms.api_server import APIServerAdapter


def _adapter() -> APIServerAdapter:
    return APIServerAdapter(PlatformConfig(enabled=True))


def test_route_table_builds_without_attribute_errors():
    """Building the table touches every handler; a missing one raises here."""
    routes = _adapter()._http_route_table()
    assert routes, "the api_server must register at least one route"


def test_every_route_handler_is_callable():
    adapter = _adapter()
    missing = []
    for method, path, handler in adapter._http_route_table():
        if not callable(handler):
            missing.append(f"{method} {path} -> {handler!r}")
    assert not missing, "routes without a callable handler:\n" + "\n".join(missing)


def test_every_handler_reference_in_the_table_source_resolves():
    """Static twin of the check above: catches a handler removed between the
    table being written and the class being assembled (mixin drift)."""
    source = inspect.getsource(APIServerAdapter._http_route_table)
    names = sorted(set(re.findall(r"self\.(_handle_[A-Za-z0-9_]+)", source)))
    assert names, "the route table should reference _handle_* methods"
    adapter = _adapter()
    unresolved = [name for name in names if not callable(getattr(adapter, name, None))]
    assert not unresolved, "route table references missing handlers: " + ", ".join(unresolved)


@pytest.mark.parametrize("name", ["_handle_skills", "_handle_toolsets"])
def test_capability_handlers_survive_the_fork_merge(name):
    """Both handlers were dropped by 1c3b9b389a; the fork must keep them."""
    assert callable(getattr(_adapter(), name, None)), f"{name} is missing from APIServerAdapter"

#!/usr/bin/env python3
"""Bootstrap SitioUno Software Factory Hermes profiles.

Compatibility entry point.  The canonical declarative spec now lives in
``scripts/factory/optimize_profiles.py`` because profile bootstrap must also
write role-specific SOUL.md, config.yaml, profile.yaml, and prune/copy the
profile-local skills allowlist.  Keeping this wrapper prevents the old clone-all
bootstrap path from reintroducing 120+ inherited skills per worker.
"""
from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.factory.optimize_profiles import main


if __name__ == "__main__":
    raise SystemExit(main())

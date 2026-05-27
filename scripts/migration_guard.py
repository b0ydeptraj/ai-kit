#!/usr/bin/env python3
"""Compatibility entrypoint for the Relay-kit naming guard.

The canonical implementation lives in `scripts/naming_guard.py`. This wrapper
keeps documented CI command names working while preserving the fail-closed
Relay-kit-only naming policy.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.naming_guard import main


if __name__ == "__main__":
    raise SystemExit(main())

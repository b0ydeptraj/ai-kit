#!/usr/bin/env python3
"""Compatibility shim for the renamed Relay-kit v3 entrypoint."""

from __future__ import annotations

import sys

from relay_kit import *  # noqa: F401,F403
from relay_kit import main as _relay_main


def _should_print_notice(argv: list[str]) -> bool:
    return len(argv) <= 1 or any(arg in {"-h", "--help", "--list-skills"} for arg in argv[1:])


def main() -> int:
    if _should_print_notice(sys.argv):
        print("Compatibility alias: prefer `relay_kit.py`; `python_kit.py` will be removed after one migration cycle.")
    return _relay_main(invoked_as="python_kit.py")


if __name__ == "__main__":
    raise SystemExit(main())

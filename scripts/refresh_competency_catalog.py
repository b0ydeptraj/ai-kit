#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from relay_kit_v3.competency_catalog import (
    CATALOG_SCHEMA_VERSION,
    build_competency_catalog,
    write_competency_profiles,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="refresh_competency_catalog.py",
        description="Refresh Relay-kit skill competency resource profiles.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON summary")
    args = parser.parse_args(argv)

    written = write_competency_profiles()
    catalog = build_competency_catalog()
    report = {
        "schema_version": CATALOG_SCHEMA_VERSION,
        "status": catalog["status"],
        "skill_count": catalog["skill_count"],
        "written_count": len(written),
        "files": [str(path.relative_to(ROOT).as_posix()) for path in written],
        "findings": catalog["findings"],
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(f"Refreshed {len(written)} competency profiles; status={catalog['status']}")
    return 0 if catalog["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())

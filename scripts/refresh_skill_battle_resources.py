from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.refresh_battle_resources import refresh_catalog, refresh_resources


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="refresh_skill_battle_resources.py",
        description="Rewrite Relay-kit skill resource packs from battle findings without raising public claims.",
    )
    parser.add_argument("--findings-file", default=None, help="Optional skill-battle or weakness JSON used as evidence input")
    parser.add_argument("--resources-only", action="store_true", help="Refresh resources without regenerating catalog")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable summary")
    args = parser.parse_args(argv)

    finding_count = 0
    if args.findings_file:
        path = Path(args.findings_file)
        if not path.is_absolute():
            path = ROOT / path
        payload = json.loads(path.read_text(encoding="utf-8"))
        finding_count = len(payload.get("findings", []))

    refresh_resources()
    if not args.resources_only:
        refresh_catalog()

    summary = {
        "schema_version": "relay-kit.skill-battle-resource-refresh.v1",
        "status": "pass",
        "finding_count": finding_count,
        "resources_refreshed": True,
        "catalog_refreshed": not args.resources_only,
        "claim_policy": "resources may describe battle-suite evidence, but max claims still require skill-battle 10/10.",
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=True, indent=2))
    else:
        print("Refreshed skill battle resources.")
        print(f"Findings consumed: {finding_count}")
        print(f"Catalog refreshed: {not args.resources_only}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

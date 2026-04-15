#!/usr/bin/env python3
"""Summarize change impact surface and suggest verification gates."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


AREA_RULES = [
    ("runtime-core", ("ai_kit_v3/", "relay_kit.py", "relay_kit_legacy.py", "relay_kit_compat.py")),
    ("adapter-surface", (".claude/skills/", ".agent/skills/", ".codex/skills/", ".relay-kit-prompts/")),
    ("artifacts-state", (".relay-kit/",)),
    ("templates", ("templates/skills/", "templates/agent/")),
    ("scripts-gates", ("scripts/",)),
    ("docs-public", ("docs/", "README.md", "README.vi.md", "CONTRIBUTING.md", "CHANGELOG.md")),
    ("packaging-cli", ("pyproject.toml", "relay_kit_public_cli.py")),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a compact blast-radius report for current changes.")
    parser.add_argument("project", nargs="?", default=".", help="Project root.")
    parser.add_argument("--base", help="Optional base ref for git diff.")
    parser.add_argument("--head", default="HEAD", help="Head ref for git diff (default: HEAD).")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser.parse_args()


def run(command: list[str], cwd: Path) -> str:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(command)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result.stdout.strip()


def changed_files(repo: Path, base: str | None, head: str) -> list[str]:
    if base:
        output = run(["git", "diff", "--name-only", f"{base}...{head}"], repo)
    else:
        output = run(["git", "status", "--porcelain"], repo)
        files: list[str] = []
        for line in output.splitlines():
            if not line.strip():
                continue
            path = line[3:].strip()
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            files.append(path)
        return sorted(set(files))
    return sorted({line.strip() for line in output.splitlines() if line.strip()})


def classify(path: str) -> set[str]:
    labels: set[str] = set()
    normalized = path.replace("\\", "/")
    for name, prefixes in AREA_RULES:
        if any(normalized.startswith(prefix) or normalized == prefix for prefix in prefixes):
            labels.add(name)
    if not labels:
        labels.add("other")
    return labels


def suggested_gates(areas: set[str]) -> list[str]:
    gates = [
        "py -3.12 scripts/validate_runtime.py",
        "py -3.12 scripts/skill_gauntlet.py . --strict",
    ]
    if {"runtime-core", "scripts-gates", "adapter-surface", "artifacts-state"} & areas:
        gates.append("py -3.12 scripts/migration_guard.py . --strict")
    if {"adapter-surface", "templates", "packaging-cli"} & areas:
        gates.extend(
            [
                "py -3.12 relay_kit_public_cli.py C:\\temp\\rk-codex --codex",
                "py -3.12 relay_kit_public_cli.py C:\\temp\\rk-claude --claude",
                "py -3.12 relay_kit_public_cli.py C:\\temp\\rk-antigravity --antigravity",
            ]
        )
    return gates


def risk_level(areas: set[str], file_count: int) -> str:
    if "runtime-core" in areas or "packaging-cli" in areas:
        return "high"
    if "adapter-surface" in areas or "scripts-gates" in areas or file_count > 30:
        return "medium"
    return "low"


def main() -> int:
    args = parse_args()
    repo = Path(args.project).resolve()
    files = changed_files(repo, args.base, args.head)
    area_map: dict[str, list[str]] = {}
    all_areas: set[str] = set()
    for file in files:
        areas = classify(file)
        all_areas |= areas
        for area in areas:
            area_map.setdefault(area, []).append(file)
    for values in area_map.values():
        values.sort()

    report = {
        "changed_files": len(files),
        "areas": sorted(all_areas),
        "risk_level": risk_level(all_areas, len(files)),
        "suggested_gates": suggested_gates(all_areas),
        "area_breakdown": area_map,
    }

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    print("Impact radar report")
    print(f"- changed files: {report['changed_files']}")
    print(f"- risk level: {report['risk_level']}")
    print(f"- areas: {', '.join(report['areas']) if report['areas'] else '-'}")
    print("- suggested gates:")
    for gate in report["suggested_gates"]:
        print(f"  - {gate}")
    print("- area breakdown:")
    for area in sorted(area_map):
        print(f"  - {area}: {len(area_map[area])} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
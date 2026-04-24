#!/usr/bin/env python3
"""Check runtime drift and adapter parity for Relay-kit surfaces."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from relay_kit_v3.registry.skills import ALL_V3_SKILLS


REQUIRED_DOCS = [
    ".relay-kit/docs/layer-model.md",
    ".relay-kit/docs/hub-mesh.md",
    ".relay-kit/docs/utility-provider-model.md",
    ".relay-kit/docs/parallelism-rules.md",
]

STATE_FILES = [
    ".relay-kit/state/workflow-state.md",
    ".relay-kit/state/team-board.md",
    ".relay-kit/state/lane-registry.md",
    ".relay-kit/state/handoff-log.md",
]

CONTRACTS_DIR = ".relay-kit/contracts"

ADAPTERS = [
    ".claude/skills",
    ".agent/skills",
    ".codex/skills",
]

# Optional legacy/native skills that can coexist with canonical v3 runtime skills.
ALLOWED_OPTIONAL_SKILLS = {
    "brainstorm",
    "build-it",
    "debug-systematically",
    "prove-it",
    "ready-check",
    "review-pr",
    "start-here",
    "write-steps",
    "aesthetic",
    "frontend-design",
    "ui-styling",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect runtime drift in Relay-kit surfaces.")
    parser.add_argument("project", nargs="?", default=".", help="Project root.")
    parser.add_argument(
        "--state-mode",
        choices=["template", "live"],
        default="template",
        help="Use template mode for repository templates, live mode for active project state checks.",
    )
    parser.add_argument("--strict", action="store_true", help="Return non-zero when findings exist.")
    return parser.parse_args()


def skill_set(root: Path, relative: str) -> set[str]:
    directory = root / relative
    if not directory.exists():
        return set()
    return {entry.name for entry in directory.iterdir() if entry.is_dir()}


def check_exists(root: Path, findings: list[str]) -> None:
    for rel in REQUIRED_DOCS + STATE_FILES:
        if not (root / rel).exists():
            findings.append(f"Missing required artifact: {rel}")


def check_adapter_parity(root: Path, findings: list[str]) -> None:
    expected = set(ALL_V3_SKILLS.keys())
    sets = {adapter: skill_set(root, adapter) for adapter in ADAPTERS}
    reference = sets[ADAPTERS[0]] - ALLOWED_OPTIONAL_SKILLS

    for adapter, current in sets.items():
        missing = sorted(expected - current)
        unexpected = sorted((current - expected) - ALLOWED_OPTIONAL_SKILLS)
        normalized = current - ALLOWED_OPTIONAL_SKILLS

        if missing:
            findings.append(f"{adapter} missing skills: {', '.join(missing)}")
        if unexpected:
            findings.append(f"{adapter} unexpected skills: {', '.join(unexpected)}")

        parity_missing = sorted(reference - normalized)
        parity_extra = sorted(normalized - reference)
        if parity_missing or parity_extra:
            findings.append(
                f"Adapter parity drift in {adapter}: "
                f"missing vs reference={parity_missing or '-'} extra vs reference={parity_extra or '-'}"
            )


def check_state_placeholders(root: Path, findings: list[str], mode: str) -> None:
    if mode != "live":
        return
    for rel in STATE_FILES:
        path = root / rel
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        if "TBD" in content:
            findings.append(f"Live state artifact still contains TBD markers: {rel}")


def check_contract_placeholders(root: Path, findings: list[str], mode: str) -> None:
    if mode != "live":
        return
    contracts_dir = root / CONTRACTS_DIR
    if not contracts_dir.exists():
        return
    for path in sorted(contracts_dir.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        if "TBD" in content:
            rel = path.relative_to(root).as_posix()
            findings.append(f"Live contract artifact still contains TBD markers: {rel}")


def main() -> int:
    args = parse_args()
    root = Path(args.project).resolve()
    findings: list[str] = []

    check_exists(root, findings)
    check_adapter_parity(root, findings)
    check_state_placeholders(root, findings, args.state_mode)
    check_contract_placeholders(root, findings, args.state_mode)

    print("Runtime doctor report")
    print(f"- state mode: {args.state_mode}")
    print(f"- findings: {len(findings)}")
    if findings:
        for finding in findings:
            print(f"  - {finding}")

    if args.strict and findings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

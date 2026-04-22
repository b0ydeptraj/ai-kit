#!/usr/bin/env python3
"""Check runtime drift and adapter parity for Relay-kit surfaces."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from relay_kit_v3.generator import BUNDLES, bundle_skill_names


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
    ".relay-kit/state/fidelity-policy.json",
]

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
    parser.add_argument(
        "--state-placeholder-mode",
        choices=["ignore", "warn", "strict"],
        default="warn",
        help="How to treat TBD placeholders when --state-mode live (default: warn).",
    )
    parser.add_argument(
        "--bundle",
        choices=["auto", *sorted(BUNDLES.keys())],
        default="auto",
        help="Expected bundle skill surface (default: auto detect from runtime).",
    )
    parser.add_argument(
        "--disallow-extra-skills",
        action="store_true",
        help="Treat extra skills outside expected bundle as findings.",
    )
    parser.add_argument("--strict", action="store_true", help="Return non-zero when findings exist.")
    return parser.parse_args()


def skill_set(root: Path, relative: str) -> set[str]:
    directory = root / relative
    if not directory.exists():
        return set()
    return {entry.name for entry in directory.iterdir() if entry.is_dir()}


def normalize(skills: set[str]) -> set[str]:
    return set(skills) - ALLOWED_OPTIONAL_SKILLS


def check_exists(root: Path, findings: list[str]) -> None:
    for rel in REQUIRED_DOCS + STATE_FILES:
        if not (root / rel).exists():
            findings.append(f"Missing required artifact: {rel}")


def detect_expected_bundle(
    reference: set[str],
    requested_bundle: str,
    warnings: list[str],
) -> tuple[str, set[str]]:
    if requested_bundle != "auto":
        return requested_bundle, set(bundle_skill_names(requested_bundle))

    if not reference:
        warnings.append("No adapter skills found; runtime bundle auto-detection is empty.")
        return "empty-surface", set()

    matches = sorted(
        bundle_name
        for bundle_name in BUNDLES
        if set(bundle_skill_names(bundle_name)) == reference
    )
    if len(matches) == 1:
        resolved = matches[0]
        return resolved, set(bundle_skill_names(resolved))

    if len(matches) > 1:
        resolved = matches[0]
        warnings.append(
            "Multiple bundles match current runtime surface "
            f"{matches}; using `{resolved}` as canonical reference."
        )
        return resolved, set(bundle_skill_names(resolved))

    warnings.append(
        "No known bundle exactly matches current runtime surface; "
        "using observed normalized adapter set as expected baseline."
    )
    return "observed-surface", set(reference)


def check_adapter_parity(
    root: Path,
    findings: list[str],
    warnings: list[str],
    requested_bundle: str,
    disallow_extra_skills: bool,
) -> tuple[str, set[str]]:
    raw_sets = {adapter: skill_set(root, adapter) for adapter in ADAPTERS}
    normalized_sets = {adapter: normalize(current) for adapter, current in raw_sets.items()}

    reference: set[str] = set()
    for adapter in ADAPTERS:
        if normalized_sets[adapter]:
            reference = set(normalized_sets[adapter])
            break

    resolved_bundle, expected = detect_expected_bundle(reference, requested_bundle, warnings)

    for adapter in ADAPTERS:
        current = normalized_sets[adapter]
        missing = sorted(expected - current)
        if missing:
            findings.append(f"{adapter} missing expected skills ({resolved_bundle}): {', '.join(missing)}")

        extra = sorted(current - expected)
        if extra:
            message = f"{adapter} extra skills beyond expected surface ({resolved_bundle}): {', '.join(extra)}"
            if disallow_extra_skills:
                findings.append(message)
            else:
                warnings.append(message)

    if expected:
        signature_mismatch = []
        for adapter in ADAPTERS:
            projection = sorted(normalized_sets[adapter] & expected)
            if projection != sorted(expected):
                signature_mismatch.append(adapter)
        if signature_mismatch:
            findings.append(
                "Adapter expected-surface parity drift detected in: " + ", ".join(signature_mismatch)
            )

    return resolved_bundle, expected


def check_state_placeholders(
    root: Path,
    findings: list[str],
    warnings: list[str],
    mode: str,
    placeholder_mode: str,
) -> None:
    if mode != "live" or placeholder_mode == "ignore":
        return

    for rel in STATE_FILES:
        path = root / rel
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        if "TBD" not in content:
            continue

        message = f"State artifact contains TBD placeholder markers: {rel}"
        if placeholder_mode == "strict":
            findings.append(message)
        else:
            warnings.append(message)


def main() -> int:
    args = parse_args()
    root = Path(args.project).resolve()
    findings: list[str] = []
    warnings: list[str] = []

    check_exists(root, findings)
    resolved_bundle, expected = check_adapter_parity(
        root,
        findings,
        warnings,
        args.bundle,
        args.disallow_extra_skills,
    )
    check_state_placeholders(root, findings, warnings, args.state_mode, args.state_placeholder_mode)

    print("Runtime doctor report")
    print(f"- state mode: {args.state_mode}")
    print(f"- state placeholder mode: {args.state_placeholder_mode}")
    print(f"- expected bundle: {resolved_bundle}")
    print(f"- expected skills: {len(expected)}")
    print(f"- findings: {len(findings)}")
    print(f"- warnings: {len(warnings)}")

    if findings:
        print("")
        print("Findings:")
        for finding in findings:
            print(f"- {finding}")

    if warnings:
        print("")
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")

    if args.strict and findings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


#!/usr/bin/env python3
"""Check runtime drift and adapter parity for Relay-kit surfaces."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from relay_kit_v3.registry.skills import ALL_V3_SKILLS
from relay_kit_v3.lane_audit import build_lane_audit
from relay_kit_v3.runtime_locale import inspect_runtime_locale


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

ADAPTERS = {
    "claude": ".claude/skills",
    "agent": ".agent/skills",
    "codex": ".codex/skills",
}

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
    parser.add_argument(
        "--adapters",
        nargs="+",
        choices=["all", *ADAPTERS],
        default=["all"],
        help="Adapter skill surfaces to inspect (default: all).",
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


def selected_adapters(adapter_names: list[str]) -> dict[str, str]:
    if "all" in adapter_names:
        return ADAPTERS
    return {name: ADAPTERS[name] for name in adapter_names}


def check_adapter_parity(root: Path, findings: list[str], adapters: dict[str, str]) -> None:
    expected = set(ALL_V3_SKILLS.keys())
    sets = {adapter: skill_set(root, relative) for adapter, relative in adapters.items()}
    reference_name = next(iter(adapters))
    reference = sets[reference_name] - ALLOWED_OPTIONAL_SKILLS

    for adapter, current in sets.items():
        relative = adapters[adapter]
        missing = sorted(expected - current)
        unexpected = sorted((current - expected) - ALLOWED_OPTIONAL_SKILLS)
        normalized = current - ALLOWED_OPTIONAL_SKILLS

        if missing:
            findings.append(f"{relative} missing skills: {', '.join(missing)}")
        if unexpected:
            findings.append(f"{relative} unexpected skills: {', '.join(unexpected)}")

        parity_missing = sorted(reference - normalized)
        parity_extra = sorted(normalized - reference)
        if parity_missing or parity_extra:
            findings.append(
                f"Adapter parity drift in {relative}: "
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
    for path in sorted(contracts_dir.rglob("*.md")):
        content = path.read_text(encoding="utf-8")
        if "TBD" in content:
            rel = path.relative_to(root).as_posix()
            findings.append(f"Live contract artifact still contains TBD markers: {rel}")


def current_git_branch(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def current_git_head(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def workflow_state_baseline(root: Path) -> str:
    path = root / ".relay-kit" / "state" / "workflow-state.md"
    if not path.exists():
        return ""
    match = re.search(r"Current main baseline[^`]*`([^`]+)`", path.read_text(encoding="utf-8"))
    return match.group(1).strip() if match else ""


def is_ancestor(root: Path, ancestor_sha: str, head_sha: str) -> bool | None:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor_sha, head_sha],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    return None


def check_stale_main_pointer(
    root: Path,
    findings: list[str],
    *,
    mode: str,
    current_branch: str | None = None,
    head_sha: str | None = None,
) -> None:
    if mode != "live":
        return
    branch = current_branch if current_branch is not None else current_git_branch(root)
    if branch != "main":
        return
    baseline = workflow_state_baseline(root)
    head = head_sha if head_sha is not None else current_git_head(root)
    if not baseline or not head:
        return
    if baseline == head or head.startswith(baseline):
        return
    if head_sha is None:
        ancestor_status = is_ancestor(root, baseline, head)
        if ancestor_status is not False:
            return
    findings.append(
        "workflow-state main baseline is stale: "
        f".relay-kit/state/workflow-state.md has {baseline}, current HEAD is {head}"
    )


def check_lane_audit(root: Path, findings: list[str], mode: str) -> None:
    if mode != "live":
        return
    report = build_lane_audit(root)
    if report["status"] == "pass":
        return
    for finding in report.get("findings", []):
        findings.append(f"Lane audit {finding.get('id', 'finding')}: {finding.get('summary', finding)}")


def check_runtime_locale(root: Path, findings: list[str], mode: str) -> None:
    if mode != "live":
        return
    report = inspect_runtime_locale(root)
    if report.get("status") == "pass":
        return
    for finding in report.get("findings", []):
        if isinstance(finding, dict):
            findings.append(f"Runtime locale {finding.get('id', 'finding')}: {finding.get('summary', finding)}")


def main() -> int:
    args = parse_args()
    root = Path(args.project).resolve()
    adapters = selected_adapters(args.adapters)
    findings: list[str] = []

    check_exists(root, findings)
    check_adapter_parity(root, findings, adapters)
    check_state_placeholders(root, findings, args.state_mode)
    check_contract_placeholders(root, findings, args.state_mode)
    check_stale_main_pointer(root, findings, mode=args.state_mode)
    check_lane_audit(root, findings, args.state_mode)
    check_runtime_locale(root, findings, args.state_mode)

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

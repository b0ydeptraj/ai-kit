#!/usr/bin/env python3
"""Accessibility gate utility for Relay-kit frontend readiness checks."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


CRITICAL_CHECKS: List[Tuple[str, str]] = [
    ("keyboard_navigation", "Keyboard-only navigation reaches all interactive controls"),
    ("focus_visible", "Visible focus indicator is present and not hidden"),
    ("semantic_structure", "Heading and landmark structure is semantically valid"),
    ("form_labels", "Inputs and controls have accessible labels and names"),
    ("color_contrast", "Text and control contrast meets minimum readability bar"),
]

SUPPORTING_CHECKS: List[Tuple[str, str]] = [
    ("status_states_announced", "Loading, empty, and error states are understandable to assistive tech"),
    ("dialog_a11y", "Dialogs and overlays trap focus and restore focus on close"),
    ("reduced_motion", "Reduced-motion preference is respected for non-essential animation"),
]


@dataclass(frozen=True)
class AccessibilityVerdict:
    passed: bool
    failed: List[str]
    missing: List[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate and evaluate an accessibility gate checklist for frontend changes.",
    )
    parser.add_argument("project_path", nargs="?", default=".", help="Target project root")
    parser.add_argument("--surface", default="frontend-surface", help="Screen, flow, or surface under review")
    parser.add_argument(
        "--report-file",
        help="Optional checklist evidence file (.json or markdown with - [x] key format)",
    )
    parser.add_argument("--output-file", help="Optional output path for generated report")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    return parser.parse_args()


def template_markdown(surface: str) -> str:
    lines = [
        "# accessibility-review",
        "",
        f"## Surface",
        f"- {surface}",
        "",
        "## Critical checks",
    ]
    for key, label in CRITICAL_CHECKS:
        lines.append(f"- [ ] `{key}` - {label}")
    lines.extend(["", "## Supporting checks"])
    for key, label in SUPPORTING_CHECKS:
        lines.append(f"- [ ] `{key}` - {label}")
    lines.extend(
        [
            "",
            "## Evidence links",
            "- screenshots:",
            "- browser snapshots:",
            "- keyboard walkthrough:",
            "",
            "## Verdict",
            "- pass|hold: TBD",
            "- notes:",
            "",
        ]
    )
    return "\n".join(lines)


def parse_markdown_report(content: str) -> Dict[str, bool]:
    status: Dict[str, bool] = {}
    pattern = re.compile(r"-\s*\[(?P<checked>[ xX])\]\s*`?(?P<key>[a-z0-9_\\-]+)`?")
    for line in content.splitlines():
        match = pattern.search(line)
        if match is None:
            continue
        status[match.group("key")] = match.group("checked").lower() == "x"
    return status


def load_report(path: Path) -> Dict[str, bool]:
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(payload, dict):
            raise ValueError("JSON report must be an object keyed by check id")
        return {str(key): bool(value) for key, value in payload.items()}
    return parse_markdown_report(path.read_text(encoding="utf-8"))


def evaluate(status: Dict[str, bool]) -> AccessibilityVerdict:
    failed: List[str] = []
    missing: List[str] = []
    for key, _label in CRITICAL_CHECKS:
        if key not in status:
            missing.append(key)
            continue
        if not status[key]:
            failed.append(key)
    return AccessibilityVerdict(passed=not failed and not missing, failed=failed, missing=missing)


def render_markdown(surface: str, verdict: AccessibilityVerdict | None) -> str:
    lines = [template_markdown(surface)]
    if verdict is None:
        lines.append("No report file provided. Checklist generated only.")
        return "\n".join(lines).rstrip() + "\n"
    lines.extend(
        [
            "## Evaluation",
            f"- verdict: {'PASS' if verdict.passed else 'HOLD'}",
            f"- failed critical checks: {', '.join(verdict.failed) if verdict.failed else '-'}",
            f"- missing critical checks: {', '.join(verdict.missing) if verdict.missing else '-'}",
            "",
        ]
    )
    return "\n".join(lines)


def render_json(surface: str, verdict: AccessibilityVerdict | None) -> str:
    payload = {
        "surface": surface,
        "critical_checks": [key for key, _ in CRITICAL_CHECKS],
        "supporting_checks": [key for key, _ in SUPPORTING_CHECKS],
        "result": None
        if verdict is None
        else {
            "passed": verdict.passed,
            "failed": verdict.failed,
            "missing": verdict.missing,
        },
    }
    return json.dumps(payload, ensure_ascii=True, indent=2)


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_path).resolve()
    verdict: AccessibilityVerdict | None = None

    if args.report_file:
        report_path = Path(args.report_file)
        if not report_path.is_absolute():
            report_path = project_root / report_path
        status = load_report(report_path)
        verdict = evaluate(status)

    if args.json:
        content = render_json(args.surface, verdict)
    else:
        content = render_markdown(args.surface, verdict)

    if args.output_file:
        output_path = Path(args.output_file)
        if not output_path.is_absolute():
            output_path = project_root / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        print(f"Wrote {output_path}")
    else:
        print(content, end="")

    if verdict is None:
        return 0
    return 0 if verdict.passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
